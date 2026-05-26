#!/usr/bin/env python3
"""vault-daily-rollup — prepend a 5-bullet `## Yesterday` rollup to a daily note.

Brainstorm idea #4 from `06-Audits/2026-05-19 SV new development ideas brainstorm.md`.

Why this exists
---------------
After ~50 SV-meta sessions, the `01-Daily/` notes are largely empty — the real
narrative lives in `08-Sessions/`. This script bridges that gap: every morning
(cron 06:00 UTC) it scans yesterday's session files and prepends a compact
5-bullet rollup to the matching daily note. The bullets are extracted
deterministically (rank by bold-prefix + concrete-number + `LANDED` markers),
so the default `extractive` mode is $0 and works without any LLM in the loop.

The `subagent` mode writes a 2-phase pending request that a calling harness
can pick up (mirrors the `vault-sleep-consolidate` / `crystallize` pattern):
the harness spawns a general-purpose subagent which writes `response.json`,
then re-runs this script to harvest.

Idempotency
-----------
Re-running on the same date REPLACES the existing `## Yesterday — <date>`
block (regex-bounded between the frontmatter and the next `## ` heading).
No duplicate blocks ever appear. All daily-note rewrites go through
`atomic_write` so a crash mid-write leaves the prior file intact.

Outputs
-------
- Rewrites `01-Daily/<today>.md` with the rollup block prepended (creates the
  daily-note skeleton if it doesn't exist yet).
- Appends a JSONL audit event to `06-Audits/vault-daily-rollup-log.jsonl`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
from vault_atomic import atomic_write, atomic_append_jsonl  # noqa: E402

VAULT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
SESSIONS_DIR = VAULT / "08-Sessions"
ARCHIVE_DIR = SESSIONS_DIR / "_archive"
DAILY_DIR = VAULT / "01-Daily"
AUDITS_DIR = VAULT / "06-Audits"
LOG_PATH = AUDITS_DIR / "vault-daily-rollup-log.jsonl"
PENDING_DIR = Path("/tmp/vault-daily-rollup-pending")

MAX_SESSIONS_PER_DAY = 10
MAX_BULLET_LEN = 120  # cap per bullet body (after the `**project** —` prefix)
TARGET_BULLETS = 5

# Words/markers that indicate "this LANDED" (rank-boost in extractive mode).
LANDED_MARKERS = (
    "LANDED", "ÉLES", "DONE", "✅", "RESOLVED", "PASS", "live", "LIVE",
)

# Regex for "concrete number" tokens (digits with units/quantifiers).
NUMBER_RE = re.compile(
    r"\b("
    r"\d+(?:[\.,]\d+)?\s*(?:%|x|×|ms|s|min|h|MB|KB|GB|LOC|sor|fájl|tok(?:en)?|pp|bullet|fact|entity|edge|node|chunk|event|session|commit)"
    r"|\$\d+(?:[\.,]\d+)?"
    r"|\d{2,}/\d{2,}"  # ratios like 5/5, 10/22
    r"|[+\-−]?\d+(?:[\.,]\d+)?\s*[%×x]"
    r")\b",
    re.IGNORECASE,
)

# Bold-prefixed bullet detection: `- **X** — ...` or `- **X**: ...`.
BOLD_PREFIX_RE = re.compile(r"^\s*-\s+\*\*([^*]+)\*\*\s*[—–\-:]\s*(.+)$")

# Section heading line.
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

# Daily-note frontmatter detection.
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

# Yesterday-block start: `## Yesterday — <date>`
YESTERDAY_BLOCK_START_RE = re.compile(
    r"^##\s+Yesterday\s+—\s+\d{4}-\d{2}-\d{2}\s*$", re.MULTILINE,
)


# ─── Session discovery & parsing ──────────────────────────────────────────────


def find_sessions_for_date(target: date) -> list[Path]:
    """Return up to MAX_SESSIONS_PER_DAY session files dated `target`."""
    prefix = target.isoformat() + "-"
    candidates: list[Path] = []
    if SESSIONS_DIR.exists():
        candidates.extend(p for p in SESSIONS_DIR.iterdir()
                          if p.is_file() and p.name.startswith(prefix)
                          and p.suffix == ".md")
    if ARCHIVE_DIR.exists():
        candidates.extend(p for p in ARCHIVE_DIR.iterdir()
                          if p.is_file() and p.name.startswith(prefix)
                          and p.suffix == ".md")
    candidates.sort(key=lambda p: p.name)
    return candidates[:MAX_SESSIONS_PER_DAY]


def extract_sections(text: str) -> dict[str, str]:
    """Split a session-file body into `{heading: body}` dict.

    Headings are level-2 (`## X`). Body is the text between this heading and
    the next level-2 heading (or EOF). Pre-frontmatter is dropped.
    """
    # Strip leading frontmatter so the first heading is found at column 0.
    body = FRONTMATTER_RE.sub("", text, count=1)
    sections: dict[str, str] = {}
    matches = list(SECTION_RE.finditer(body))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()
    return sections


def slug_from_filename(p: Path, target: date) -> str:
    """Pull the project-slug from `YYYY-MM-DD-<slug>.md`."""
    name = p.stem
    prefix = target.isoformat() + "-"
    if name.startswith(prefix):
        return name[len(prefix):]
    return name


def count_events(events_section: str) -> int:
    """Count bullet-style event lines in the `## Events` section."""
    if not events_section:
        return 0
    n = 0
    for line in events_section.splitlines():
        s = line.strip()
        if s.startswith("- ") or s.startswith("* "):
            n += 1
    return n


def detect_landed_in_propagation(prop_section: str) -> int:
    """Count LANDED-ish markers in the `## Propagation log` section."""
    if not prop_section:
        return 0
    score = 0
    for marker in ("LANDED", "✅"):
        score += prop_section.count(marker)
    return score


def parse_learning_bullets(learnings_section: str) -> list[tuple[str, str]]:
    """Return `[(prefix, body)]` for `- **prefix** — body` lines.

    The Karpathy-style learnings always use bold-prefix headers. Lines without
    the prefix are skipped — those are usually continuation paragraphs.
    """
    out: list[tuple[str, str]] = []
    for line in learnings_section.splitlines():
        m = BOLD_PREFIX_RE.match(line)
        if m:
            prefix = m.group(1).strip()
            body = m.group(2).strip()
            out.append((prefix, body))
    return out


def parse_summary_bullets(summary_section: str) -> list[str]:
    """Pull bullet-list items out of `## Summary` (also keep the leading
    bold-prefix style if present)."""
    out: list[str] = []
    for line in summary_section.splitlines():
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    if out:
        return out
    # If `## Summary` is one prose paragraph, return it whole (will be capped
    # in render).
    para = summary_section.strip()
    if para:
        return [para.split("\n\n", 1)[0].strip()]
    return []


# ─── Highlight scoring (extractive mode) ──────────────────────────────────────


def score_candidate(text: str, *, is_learning: bool = False) -> float:
    """Heuristic score: higher = better summary bullet.

    Ranks:
      +2.0  bullet was a `## Learnings` bold-prefix bullet (always strong)
      +1.0  per concrete-number match (capped at +3.0)
      +0.5  per LANDED-style marker (capped at +1.5)
      −0.4  per 100 chars past 200 (length penalty — we WANT punchy)
      −2.0  if shorter than 40 chars (no signal)
    """
    if not text:
        return -10.0
    s = 0.0
    if is_learning:
        s += 2.0
    num_count = len(NUMBER_RE.findall(text))
    s += min(num_count, 3) * 1.0
    landed_count = sum(text.count(m) for m in LANDED_MARKERS)
    s += min(landed_count, 3) * 0.5
    n = len(text)
    if n < 40:
        s -= 2.0
    elif n > 200:
        s -= ((n - 200) / 100.0) * 0.4
    return s


def truncate(text: str, limit: int = MAX_BULLET_LEN) -> str:
    """Shorten to <=limit chars at a word boundary, append ellipsis."""
    text = text.strip()
    # Strip wikilink-internal pipe noise like [[foo|bar]] → bar (read nicer).
    text = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", text)
    # Collapse multi-space.
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    # Try to break at last space within the last 20 chars.
    space = cut.rfind(" ", max(0, limit - 25))
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.- ") + "…"


# ─── Dedup against previous-day's rollup ──────────────────────────────────────


def previous_yesterday_block(today_iso: str) -> str:
    """Return the previous daily-note's `## Yesterday` body (for dedup),
    or empty string if none."""
    today_dt = date.fromisoformat(today_iso)
    prev = today_dt - timedelta(days=1)
    prev_path = DAILY_DIR / f"{prev.isoformat()}.md"
    if not prev_path.exists():
        return ""
    text = prev_path.read_text(encoding="utf-8")
    m = YESTERDAY_BLOCK_START_RE.search(text)
    if not m:
        return ""
    start = m.end()
    # End at next `## ` heading.
    nxt = SECTION_RE.search(text, pos=start)
    end = nxt.start() if nxt else len(text)
    return text[start:end]


def looks_like_duplicate(candidate: str, prev_block: str) -> bool:
    """Cheap fingerprint: if the first 8 alnum words of candidate appear
    in prev_block, treat as dup. Prevents the SAME bullet appearing two days
    in a row when sessions span multiple days."""
    if not prev_block:
        return False
    tokens = re.findall(r"\w{3,}", candidate.lower())
    if len(tokens) < 4:
        return False
    fingerprint = " ".join(tokens[:8])
    prev_norm = " ".join(re.findall(r"\w{3,}", prev_block.lower()))
    return fingerprint in prev_norm


# ─── Highlight extraction per session ─────────────────────────────────────────


def per_session_candidates(
    slug: str, sections: dict[str, str],
) -> list[dict]:
    """Yield `{score, project, text, source}` candidates from one session."""
    cands: list[dict] = []

    learnings = parse_learning_bullets(sections.get("Learnings → memória", ""))
    for prefix, body in learnings:
        full = f"{prefix}: {body}" if prefix else body
        sc = score_candidate(full, is_learning=True)
        cands.append({
            "score": sc, "project": slug, "text": full, "kind": "learning",
        })

    summary = parse_summary_bullets(sections.get("Summary", ""))
    for line in summary:
        # Strip leading bold prefix if present (we re-add project prefix).
        m = BOLD_PREFIX_RE.match(f"- {line}")
        body = m.group(2).strip() if m else line
        sc = score_candidate(body, is_learning=False)
        cands.append({
            "score": sc, "project": slug, "text": body, "kind": "summary",
        })

    return cands


# ─── Mode: extractive ─────────────────────────────────────────────────────────


def extractive_rollup(
    target: date, sessions: list[Path],
) -> tuple[list[dict], list[dict]]:
    """Return `(bullets, session_stats)` for the extractive render.

    bullets = list of {project, text} (after truncation, max TARGET_BULLETS)
    session_stats = list of {file, slug, events, learnings, landed}
    """
    all_cands: list[dict] = []
    session_stats: list[dict] = []

    for path in sessions:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        sections = extract_sections(text)
        slug = slug_from_filename(path, target)
        cands = per_session_candidates(slug, sections)
        all_cands.extend(cands)
        session_stats.append({
            "file": path.name,
            "path": str(path.relative_to(VAULT)),
            "slug": slug,
            "events": count_events(sections.get("Events", "")),
            "learnings": len(parse_learning_bullets(
                sections.get("Learnings → memória", ""))),
            "landed": detect_landed_in_propagation(
                sections.get("Propagation log", "")),
        })

    # Dedup against yesterday's rollup.
    today_iso = (target + timedelta(days=1)).isoformat()
    prev_block = previous_yesterday_block(today_iso)

    # Sort by score desc, take TARGET_BULLETS with diversity:
    #   - prefer at most 2 bullets per project (so a single mega-session can't
    #     monopolise the rollup).
    all_cands.sort(key=lambda c: c["score"], reverse=True)
    chosen: list[dict] = []
    per_project_count: dict[str, int] = {}
    seen_fingerprints: set[str] = set()

    for c in all_cands:
        if len(chosen) >= TARGET_BULLETS:
            break
        truncated = truncate(c["text"], MAX_BULLET_LEN)
        # Skip too-short or empty.
        if len(truncated) < 30:
            continue
        # Skip if this exact bullet already chosen (case-insensitive prefix).
        fp = " ".join(re.findall(r"\w{3,}", truncated.lower())[:6])
        if fp in seen_fingerprints:
            continue
        if looks_like_duplicate(truncated, prev_block):
            continue
        # Project diversity cap.
        proj = c["project"]
        if per_project_count.get(proj, 0) >= 2:
            continue
        chosen.append({
            "project": proj,
            "text": truncated,
            "score": round(c["score"], 2),
            "kind": c["kind"],
        })
        per_project_count[proj] = per_project_count.get(proj, 0) + 1
        seen_fingerprints.add(fp)

    return chosen, session_stats


# ─── Mode: subagent (2-phase pending) ─────────────────────────────────────────


def subagent_prepare_or_harvest(
    target: date, sessions: list[Path],
) -> tuple[list[dict] | None, list[dict], str]:
    """Try to harvest a previously-written response; if none, write the
    request file and return (None, stats, "pending")."""
    today_iso = target.isoformat()
    pdir = PENDING_DIR / today_iso
    pdir.mkdir(parents=True, exist_ok=True)
    req_path = pdir / "request.json"
    resp_path = pdir / "response.json"

    # Stats are always extractive (cheap).
    session_stats: list[dict] = []
    raw_bundle: list[dict] = []
    for path in sessions:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        sections = extract_sections(text)
        slug = slug_from_filename(path, target)
        session_stats.append({
            "file": path.name,
            "path": str(path.relative_to(VAULT)),
            "slug": slug,
            "events": count_events(sections.get("Events", "")),
            "learnings": len(parse_learning_bullets(
                sections.get("Learnings → memória", ""))),
            "landed": detect_landed_in_propagation(
                sections.get("Propagation log", "")),
        })
        raw_bundle.append({
            "slug": slug,
            "file": path.name,
            "summary": sections.get("Summary", "")[:2000],
            "learnings": sections.get("Learnings → memória", "")[:4000],
        })

    if resp_path.exists():
        try:
            resp = json.loads(resp_path.read_text(encoding="utf-8"))
            bullets = resp.get("bullets") or []
            cleaned: list[dict] = []
            for b in bullets[:TARGET_BULLETS]:
                if not isinstance(b, dict):
                    continue
                proj = (b.get("project") or "?").strip()
                txt = truncate((b.get("text") or "").strip(), MAX_BULLET_LEN)
                if not txt:
                    continue
                cleaned.append({"project": proj, "text": txt,
                                "kind": "subagent"})
            return cleaned, session_stats, "harvested"
        except Exception:
            pass  # fall through to re-issue request

    # No (valid) response yet — write the request, signal "pending".
    if not req_path.exists():
        payload = {
            "date": today_iso,
            "session_count": len(raw_bundle),
            "sessions": raw_bundle,
            "instructions": (
                "Synthesise EXACTLY 5 punchy 1-line bullets summarising the "
                "previous day's session work. Each bullet ≤120 chars. Mix "
                "across projects when sessions span multiple projects. Prefer "
                "concrete numbers, LANDED markers, and Karpathy-style "
                "learnings. Output JSON: {\"bullets\": [{\"project\": str, "
                "\"text\": str}, ...]}"
            ),
            "schema_version": "vault-daily-rollup-v1",
        }
        # /tmp scratch — atomic-lint exempt.
        req_path.write_text(  # vault-atomic-lint: ok — /tmp/ scratch pending-file
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return None, session_stats, "pending"


# ─── Render & write the daily-note ────────────────────────────────────────────


def render_block(
    target: date, bullets: list[dict], session_stats: list[dict],
    *, mode: str, elapsed_ms: int,
) -> str:
    """Build the markdown chunk to prepend (or splice into) the daily note."""
    n_sessions = len(session_stats)
    lines: list[str] = []
    lines.append(f"## Yesterday — {target.isoformat()}")
    lines.append("")
    lines.append(
        f"> [!summary] 5-bullet rollup from {n_sessions} session"
        f"{'s' if n_sessions != 1 else ''}"
    )
    lines.append(
        f"> _Auto-generated by `vault-daily-rollup` ({mode} mode, {elapsed_ms}ms)._"
    )
    lines.append("")
    if bullets:
        for b in bullets:
            lines.append(f"- **{b['project']}** — {b['text']}")
    else:
        lines.append("- _No bullets extracted — see session list below._")
    lines.append("")
    if session_stats:
        lines.append("<details>")
        lines.append(f"<summary>Sessions ({n_sessions})</summary>")
        lines.append("")
        for st in session_stats:
            wiki = f"[[../08-Sessions/{Path(st['file']).stem}|{st['slug']}]]"
            stats_bits = []
            if st["events"]:
                stats_bits.append(f"{st['events']} events")
            if st["learnings"]:
                stats_bits.append(f"{st['learnings']} learnings")
            if st["landed"]:
                stats_bits.append(f"{st['landed']} LANDED")
            tail = (" — " + ", ".join(stats_bits)) if stats_bits else ""
            lines.append(f"- {wiki}{tail}")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    return "\n".join(lines)


def minimal_daily_skeleton(today: date) -> str:
    iso = today.isoformat()
    return (
        f"---\n"
        f"name: {iso}\n"
        f"type: daily-note\n"
        f"created: {iso}\n"
        f"updated: {iso}\n"
        f"tags: [\"#type/daily\"]\n"
        f"---\n"
        f"\n"
        f"# {iso}\n"
        f"\n"
        f"## Today\n"
        f"\n"
        f"-\n"
        f"\n"
        f"## Notes\n"
        f"\n"
    )


def splice_yesterday_block(existing: str, block: str) -> str:
    """Insert `block` after the frontmatter, REPLACING any existing
    `## Yesterday — <date>` chunk (between that heading and the next `## `).
    """
    # 1) Drop any existing Yesterday block.
    m = YESTERDAY_BLOCK_START_RE.search(existing)
    if m:
        start = m.start()
        # Find next `## ` heading AFTER this one.
        nxt = SECTION_RE.search(existing, pos=m.end())
        end = nxt.start() if nxt else len(existing)
        # Also eat leading blank lines before the block (to avoid extra gaps).
        # Walk backwards to consume immediately-preceding blank lines.
        while start > 0 and existing[start - 1] == "\n":
            # keep at most one preceding newline (frontmatter terminator)
            if start >= 2 and existing[start - 2] == "\n":
                start -= 1
            else:
                break
        existing = existing[:start] + existing[end:]

    # 2) Splice the new block after the frontmatter (or at top if none).
    fm = FRONTMATTER_RE.match(existing)
    if fm:
        head = existing[:fm.end()]
        tail = existing[fm.end():]
        # Normalise to: <frontmatter>\n<block>\n<original-tail-without-leading-blank>
        tail = tail.lstrip("\n")
        return head + "\n" + block + "\n" + tail
    # No frontmatter — prepend.
    return block + "\n" + existing.lstrip("\n")


# ─── Audit log ────────────────────────────────────────────────────────────────


def emit_audit_event(
    target: date, sessions: list[Path], bullets: list[dict],
    *, mode: str, elapsed_ms: int, dry_run: bool, status: str,
) -> None:
    """Append a JSONL audit row. Best-effort; never raises."""
    try:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "date": target.isoformat(),
            "sessions": len(sessions),
            "bullets": len(bullets),
            "mode": mode,
            "ms": elapsed_ms,
            "dry_run": dry_run,
            "status": status,
        }
        atomic_append_jsonl(LOG_PATH, event)
    except Exception:
        pass  # audit is best-effort


# ─── CLI ──────────────────────────────────────────────────────────────────────


CRON_SUGGESTION = """\
# Suggested cron entry — daily rollup at 06:00 UTC:
# 0 6 * * * /usr/local/bin/vault-cron-flock vault-daily-rollup /usr/local/bin/vault-daily-rollup >/dev/null 2>&1
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    today = date.today()
    yesterday = today - timedelta(days=1)
    parser = argparse.ArgumentParser(
        prog="vault-daily-rollup",
        description=(
            "Prepend a 5-bullet `## Yesterday` rollup to today's daily note. "
            "Reads yesterday's `08-Sessions/*.md` files and ranks highlights."
        ),
        epilog=CRON_SUGGESTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--date", default=yesterday.isoformat(),
        help=(
            "Date to summarise (YYYY-MM-DD). Default: yesterday (UTC). "
            "The rollup writes into the FOLLOWING day's daily note "
            "(--date 2026-05-18 → 01-Daily/2026-05-19.md)."
        ),
    )
    parser.add_argument(
        "--mode", choices=("extractive", "subagent"), default="extractive",
        help="extractive (default, deterministic) | subagent (LLM via pending).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the would-be block to stdout, write nothing, exit 0.",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit a JSON summary to stdout instead of the markdown block.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    started = time.monotonic()

    try:
        target = date.fromisoformat(args.date)
    except ValueError:
        print(f"error: --date must be YYYY-MM-DD, got {args.date!r}",
              file=sys.stderr)
        return 2

    sessions = find_sessions_for_date(target)
    if not sessions:
        msg = f"no sessions found for {target.isoformat()}"
        if args.json:
            print(json.dumps({
                "date": target.isoformat(),
                "sessions": 0,
                "bullets": 0,
                "mode": args.mode,
                "status": "no-sessions",
            }))
        else:
            print(msg)
        emit_audit_event(
            target, sessions, [],
            mode=args.mode, elapsed_ms=int((time.monotonic() - started) * 1000),
            dry_run=args.dry_run, status="no-sessions",
        )
        return 0

    status = "ok"
    if args.mode == "subagent":
        bullets, session_stats, sub_status = subagent_prepare_or_harvest(
            target, sessions,
        )
        if bullets is None:
            # Falls back to extractive so the daily note still gets *something*
            # — the subagent response can land in a later re-run.
            bullets, session_stats = extractive_rollup(target, sessions)
            status = "subagent-pending+extractive-fallback"
        else:
            status = f"subagent-{sub_status}"
    else:
        bullets, session_stats = extractive_rollup(target, sessions)

    elapsed_ms = int((time.monotonic() - started) * 1000)
    block = render_block(
        target, bullets, session_stats,
        mode=args.mode, elapsed_ms=elapsed_ms,
    )

    today = target + timedelta(days=1)
    daily_path = DAILY_DIR / f"{today.isoformat()}.md"

    if args.dry_run:
        if args.json:
            print(json.dumps({
                "date": target.isoformat(),
                "daily_note": str(daily_path),
                "sessions": len(sessions),
                "bullets": len(bullets),
                "mode": args.mode,
                "status": status,
                "ms": elapsed_ms,
                "dry_run": True,
                "block": block,
            }, ensure_ascii=False, indent=2))
        else:
            print(block)
        emit_audit_event(
            target, sessions, bullets,
            mode=args.mode, elapsed_ms=elapsed_ms, dry_run=True, status=status,
        )
        return 0

    # Real write — create skeleton or splice.
    if daily_path.exists():
        existing = daily_path.read_text(encoding="utf-8")
    else:
        existing = minimal_daily_skeleton(today)

    new_content = splice_yesterday_block(existing, block)
    atomic_write(daily_path, new_content)

    if args.json:
        print(json.dumps({
            "date": target.isoformat(),
            "daily_note": str(daily_path),
            "sessions": len(sessions),
            "bullets": len(bullets),
            "mode": args.mode,
            "status": status,
            "ms": elapsed_ms,
            "dry_run": False,
        }, ensure_ascii=False, indent=2))
    else:
        print(
            f"vault-daily-rollup: wrote {daily_path} "
            f"({len(bullets)} bullets from {len(sessions)} sessions, "
            f"{elapsed_ms}ms, status={status})"
        )

    emit_audit_event(
        target, sessions, bullets,
        mode=args.mode, elapsed_ms=elapsed_ms, dry_run=False, status=status,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
