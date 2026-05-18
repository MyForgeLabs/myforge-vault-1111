#!/root/.notebooklm-venv/bin/python3
"""
vault-nb-crystallize — NotebookLM cognitive crystallization (B-5 Réteg 2, Week 2).

ADR: 07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch.md
Sprint: B-5 Week 2 (real impl — per-bullet enrich + Layer 1.5 hook).

Two modes:

  1. Project-weekly crystallize (B-5 Week 2-α, default):
     For each project with a linked NotebookLM notebook (frontmatter `notebooklm:`),
     ask "what's new in this knowledge base?" and crystallize the answer to
     `10-raw/nb-crystallize/<slug>-<ISO-week>.md`. Then queue a KO-DB extraction
     request (same 2-phase pattern as vault-ko-ingest / vault-net-ingest).

  2. Per-bullet enrich (B-5 Week 2, Layer 1.5 hook for 11.11crystallize):
     For each Learning bullet in a session-fájl, ask the vault-meta NotebookLM
     (or per-project NB) whether it has 3+ supporting sources. Emits a JSON
     manifest the parent 11.11crystallize consumes BEFORE calling the G-Eval
     scorer (so the scorer sees `nb_support_count`, `nb_top_sources`,
     `nb_confidence` as context).

Robust to NotebookLM failures: print warning + continue with next bullet/project.

Usage:
    vault-nb-crystallize <slug>           # one project (weekly crystallize)
    vault-nb-crystallize --all            # all projects with NB linked (weekly)
    vault-nb-crystallize --dry-run        # don't query NB, just list targets
    vault-nb-crystallize --dry-run --all  # combine

    vault-nb-crystallize --bullet-enrich <session-slug>
                                          # Layer 1.5 enrich for 11.11crystallize.
                                          # Writes JSON to /tmp/vault-nb-pending/<slug>.bullet-enrich.json
                                          # Reads bullets from 08-Sessions/<slug>.md `## Learnings` section.
    vault-nb-crystallize --bullet-enrich <slug> --notebook <NB-ID>
                                          # Override notebook (default: vault-meta NB
                                          # at ~/.vault-config/vault-meta-notebook.id)
    vault-nb-crystallize --bullet-enrich <slug> --dry-run
                                          # No NotebookLM calls — placeholder result.
    vault-nb-crystallize --bullet-enrich <slug> --max-bullets N
                                          # Cap (default 50 = de facto unlimited).

Env:
    NOTEBOOKLM_CLI                override CLI path (default: /root/.notebooklm-venv/bin/notebooklm)
    NB_QUESTION                   override the fixed weekly-crystallize question
    VAULT_NB_BULLET_MIN_SUPPORT   threshold for "high" confidence (default 3)
    VAULT_NB_BULLET_TIMEOUT       per-bullet NotebookLM ask timeout (default 120)

Exit codes:
    0  ok (or per-bullet partial-fail — pending file always written if any bullets)
    1  bad input / session-fájl missing / no learnings
    2  notebooklm hard fail (e.g. CLI not found)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
PROJECTS_DIR = VAULT_ROOT / "02-Projects"
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
RAW_DIR = VAULT_ROOT / "10-raw" / "nb-crystallize"
KO_PENDING = Path("/tmp/vault-ko-pending")
NB_PENDING = Path("/tmp/vault-nb-pending")
NOTEBOOKLM = os.environ.get("NOTEBOOKLM_CLI", "/root/.notebooklm-venv/bin/notebooklm")
SKIP_PROJECTS = {"Index", "README"}
VAULT_META_NB_POINTER = Path(os.environ.get(
    "VAULT_META_NB_POINTER", "/root/.vault-config/vault-meta-notebook.id"
))

DEFAULT_QUESTION = os.environ.get(
    "NB_QUESTION",
    "Mi az új ebben a tudásbázisban az elmúlt időszakhoz képest? "
    "Sorold fel a 3-7 legfontosabb új vagy frissített témát, döntést, vagy mintát. "
    "Minden ponthoz adj forrás-citációt [N] formában, és tömör (1-2 mondat) magyarázatot."
)

MAX_ASK_TIMEOUT = 180  # seconds — notebooklm ask can be slow
BULLET_ASK_TIMEOUT = int(os.environ.get("VAULT_NB_BULLET_TIMEOUT", "120"))
BULLET_MIN_SUPPORT = int(os.environ.get("VAULT_NB_BULLET_MIN_SUPPORT", "3"))

# Same regex as 11.11crystallize for consistent Learnings extraction
LEARNINGS_HEADER = re.compile(r"^## Learnings", re.MULTILINE)
NEXT_SECTION = re.compile(r"^## (?!Learnings)", re.MULTILINE)
BULLET_PATTERN = re.compile(
    r"^[\s]*[-*]\s+(\*\*[^*]+\*\*[\s\-—:]*)?(.+?)(?=\n[\s]*[-*]\s|\n\n|\Z)",
    re.DOTALL | re.MULTILINE,
)


def parse_frontmatter(text: str) -> dict:
    """Same parse-style as vault-nb-sync.py (intentional consistency)."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        match = re.match(r"^([a-z_]+):\s*(.+)$", line)
        if match:
            fm[match.group(1)] = match.group(2).strip().strip('"')
    return fm


def get_notebook_id(project_path: Path) -> str | None:
    text = project_path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    return fm.get("notebooklm") or fm.get("notebook_id")


def get_vault_meta_nb_id() -> str | None:
    """Return the vault-meta NB ID from the pointer file (B-5 Week 2)."""
    if not VAULT_META_NB_POINTER.exists():
        return None
    nb_id = VAULT_META_NB_POINTER.read_text(encoding="utf-8").strip()
    return nb_id or None


def iso_week_tag(dt: datetime | None = None) -> str:
    """E.g. '2026-W20' (ISO week)."""
    dt = dt or datetime.utcnow()
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def list_linked_projects() -> list[tuple[Path, str]]:
    """Returns [(project_path, nb_id), ...] for every project with notebooklm frontmatter."""
    out = []
    for p in sorted(PROJECTS_DIR.glob("*.md")):
        if p.stem in SKIP_PROJECTS:
            continue
        if ".bak" in p.name:
            continue
        nb_id = get_notebook_id(p)
        if nb_id:
            out.append((p, nb_id))
    return out


def extract_learnings(text: str) -> list[str]:
    """Same algorithm as 11.11crystallize.extract_learnings — keep in sync."""
    m = LEARNINGS_HEADER.search(text)
    if not m:
        return []
    start = m.end()
    rest = text[start:]
    nxt = NEXT_SECTION.search(rest)
    section = rest[: nxt.start()] if nxt else rest
    bullets = []
    for match in BULLET_PATTERN.finditer(section):
        lead = (match.group(1) or "").strip()
        body = match.group(2).strip()
        full = f"{lead} — {body}" if lead else body
        full = re.sub(r"\*\*", "", full)
        full = re.sub(r"\s+", " ", full).strip()
        if len(full) >= 20:
            bullets.append(full)
    return bullets


def ask_notebook(nb_id: str, question: str, timeout: int = MAX_ASK_TIMEOUT,
                 use_json: bool = False) -> tuple[bool, str, dict]:
    """
    Invoke `notebooklm ask -n <NB_ID> "<question>"`.

    Returns (ok, answer_text, meta_dict). `meta_dict` carries references when
    use_json=True (else empty).
    On failure: (False, error_message, {}).
    """
    cmd = [NOTEBOOKLM, "ask", "-n", nb_id, question]
    if use_json:
        cmd.append("--json")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s", {}
    except FileNotFoundError:
        return False, f"notebooklm CLI not found at {NOTEBOOKLM}", {}

    if result.returncode != 0:
        return False, f"rc={result.returncode}: {result.stderr[:300]}", {}

    raw = result.stdout.strip()
    if len(raw) < 20:
        return False, f"suspiciously short answer ({len(raw)} chars): {raw!r}", {}

    if use_json:
        try:
            data = json.loads(raw)
            return True, data.get("answer", raw), data
        except json.JSONDecodeError:
            # Fall back to treating raw stdout as the answer (gotcha #1 fallback)
            return True, raw, {"_json_parse_failed": True, "raw_len": len(raw)}

    return True, raw, {}


# ───────────────────────── Mode 1: weekly project crystallize ─────────────────────────


def write_crystallize_raw(slug: str, nb_id: str, answer: str, week_tag: str) -> Path:
    """Write the NB answer to 10-raw/nb-crystallize/<slug>-<week>.md with frontmatter."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"{slug}-{week_tag}.md"

    today = datetime.utcnow().strftime("%Y-%m-%d")
    fm = [
        "---",
        f"type: raw",
        f"source: notebooklm-crystallize",
        f"source_nb_id: {nb_id}",
        f"source_project: {slug}",
        f"week: {week_tag}",
        f"created: {today}",
        f"updated: {today}",
        "---",
        "",
        f"# NB-crystallize · {slug} · {week_tag}",
        "",
        f"> NotebookLM cognitive crystallization for project `{slug}`.",
        f"> NB-ID: `{nb_id}`",
        f"> Generated: {today} UTC",
        "",
        "## Question",
        "",
        DEFAULT_QUESTION,
        "",
        "## Answer",
        "",
        answer,
        "",
    ]
    out_path.write_text("\n".join(fm), encoding="utf-8")
    return out_path


def queue_ko_extraction(path: Path, provenance: str, dry_run: bool = False) -> Path | None:
    """Mirror vault-net-ingest queue_ko_extraction — 2-phase subagent pattern."""
    if dry_run:
        return None
    KO_PENDING.mkdir(parents=True, exist_ok=True)
    safe = provenance.replace("/", "_").replace(" ", "_")
    req = KO_PENDING / f"{safe}.request.json"
    text = path.read_text(encoding="utf-8")
    req.write_text(json.dumps(
        {"provenance": provenance, "text": text, "source_type": "nb-crystallize"},
        ensure_ascii=False, indent=2,
    ))
    return req


def process_project(project_path: Path, nb_id: str, dry_run: bool) -> dict:
    slug = project_path.stem
    week_tag = iso_week_tag()
    result = {
        "slug": slug,
        "nb_id": nb_id,
        "week": week_tag,
    }

    if dry_run:
        result["status"] = "would_ask"
        result["raw_out"] = str(RAW_DIR / f"{slug}-{week_tag}.md")
        return result

    ok, answer, _meta = ask_notebook(nb_id, DEFAULT_QUESTION)
    if not ok:
        result["status"] = "ask_failed"
        result["error"] = answer
        return result

    out_path = write_crystallize_raw(slug, nb_id, answer, week_tag)
    provenance = str(out_path.relative_to(VAULT_ROOT))
    req_path = queue_ko_extraction(out_path, provenance, dry_run=False)

    result["status"] = "crystallized"
    result["raw_out"] = str(out_path)
    result["ko_request"] = str(req_path) if req_path else None
    result["answer_chars"] = len(answer)
    return result


# ───────────────── Mode 2: per-bullet enrich (Layer 1.5 hook for 11.11crystallize) ─────────────────


# Citation-count heuristic: count [N] markers in the answer. NB typically emits
# 1 citation per supporting source mentioned. We dedupe by N (so the *unique*
# count of distinct sources, not the total citation occurrences).
CITATION_RE = re.compile(r"\[(\d{1,3})\]")
NEGATIVE_RE = re.compile(
    r"(nem találtam|nincs (?:támogat|forrás|említ)|nem szerepel|"
    r"semmilyen forrás|nincsen erre|no supporting|no relevant|not found|"
    r"cannot find|i (?:cannot|can't|don'?t) find|nem fed le|i don't have|"
    r"there (?:is|are) no)",
    re.IGNORECASE,
)


def build_bullet_question(bullet: str) -> str:
    """Compose the per-bullet enrich question. Hungarian (vault default)."""
    # Trim bullet to a sane length for the prompt (NB tolerates ~1000+ chars,
    # but shorter prompts retrieve better)
    snippet = bullet.strip()
    if len(snippet) > 600:
        snippet = snippet[:600].rsplit(" ", 1)[0] + "…"
    return (
        "Az alábbi tanulság/megfigyelés szerepel egy session-naplóban. "
        "A te feladatod: keresd meg ennek a tanulságnak a TÁMOGATÓ FORRÁSAIT a notebook-ban. "
        f"\n\nTanulság: «{snippet}»\n\n"
        "Sorolj fel MINDEN olyan forrást, ami megerősíti, alátámasztja, vagy "
        "kiegészíti ezt a tanulságot. Minden forrás után tedd a [N] citation-jelölést. "
        "Ha nincs támogató forrás, írd: 'Nem találtam támogató forrást.' "
        "Ne találj ki forrásokat — csak a notebook-ban szereplőket idézd."
    )


def parse_support_signal(answer: str, meta: dict) -> tuple[int, list[str], str]:
    """
    Parse a NotebookLM answer into (support_count, top_sources, confidence_tier).

    Logic:
      - If `meta.references` is present (JSON mode), count unique source titles.
      - Else: count unique [N] tokens in plain stdout.
      - Negative-phrase check: if „nem találtam"/„no supporting" appears, force 0.
      - Confidence tier: high (>=3), mid (1-2), low (0).
    """
    # Negative-phrase short-circuit
    if NEGATIVE_RE.search(answer):
        return 0, [], "low"

    citation_ids: set[str] = set()
    sources: list[str] = []

    refs = meta.get("references") if meta else None
    if isinstance(refs, list) and refs:
        # JSON mode: references is list of {id, title, ...} or similar
        seen = set()
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            title = ref.get("title") or ref.get("source_id") or ref.get("id") or ""
            title = str(title).strip()
            if title and title not in seen:
                seen.add(title)
                sources.append(title)
        if sources:
            count = len(sources)
            tier = "high" if count >= BULLET_MIN_SUPPORT else ("mid" if count >= 1 else "low")
            return count, sources[:10], tier

    # Plain-stdout mode: count unique [N] tokens
    for m in CITATION_RE.finditer(answer):
        citation_ids.add(m.group(1))
    count = len(citation_ids)

    # Heuristic source-extract: lines starting with `- ` or `* ` (bullet lists
    # NB commonly emits when asked to list sources). Keep first 10.
    for line in answer.splitlines():
        line = line.strip()
        if line.startswith(("- ", "* ", "• ")):
            # Strip lead marker + trailing [N]
            src = re.sub(r"\[\d+\]", "", line.lstrip("-*• ").strip()).strip(" .;:")
            if src and len(src) <= 200 and src not in sources:
                sources.append(src)
                if len(sources) >= 10:
                    break

    tier = "high" if count >= BULLET_MIN_SUPPORT else ("mid" if count >= 1 else "low")
    return count, sources[:10], tier


def enrich_session_bullets(session_path: Path, nb_id: str, dry_run: bool,
                           max_bullets: int) -> dict:
    """
    For each Learning bullet in the session, ask NB about supporting sources.
    Returns the pending-enrich payload (also written to disk).
    """
    text = session_path.read_text(encoding="utf-8")
    bullets = extract_learnings(text)
    if not bullets:
        return {
            "session_slug": session_path.stem,
            "nb_id": nb_id,
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "bullets": [],
            "status": "no_bullets",
        }

    if max_bullets and len(bullets) > max_bullets:
        bullets = bullets[:max_bullets]

    results = []
    t_start = time.monotonic()
    for i, bullet in enumerate(bullets):
        preview = bullet[:80].replace("\n", " ")
        if dry_run:
            entry = {
                "index": i,
                "bullet_preview": preview,
                "nb_support_count": -1,
                "nb_top_sources": [],
                "nb_confidence": "dry-run",
                "nb_latency_ms": 0,
                "status": "dry-run",
            }
            results.append(entry)
            print(f"  [{i}] DRY  {preview}…")
            continue

        question = build_bullet_question(bullet)
        t0 = time.monotonic()
        ok, answer, meta = ask_notebook(
            nb_id, question, timeout=BULLET_ASK_TIMEOUT, use_json=True,
        )
        latency_ms = int((time.monotonic() - t0) * 1000)

        if not ok:
            entry = {
                "index": i,
                "bullet_preview": preview,
                "nb_support_count": 0,
                "nb_top_sources": [],
                "nb_confidence": "error",
                "nb_latency_ms": latency_ms,
                "status": "ask_failed",
                "error": answer[:200],
            }
            results.append(entry)
            print(f"  [{i}] ✗ {answer[:60]}  ({latency_ms} ms)")
            continue

        count, sources, tier = parse_support_signal(answer, meta)
        entry = {
            "index": i,
            "bullet_preview": preview,
            "nb_support_count": count,
            "nb_top_sources": sources,
            "nb_confidence": tier,
            "nb_latency_ms": latency_ms,
            "status": "ok",
            "answer_chars": len(answer),
        }
        results.append(entry)
        marker = {"high": "🟢", "mid": "🟡", "low": "🔴", "error": "✗"}.get(tier, "?")
        print(f"  [{i}] {marker} support={count} ({tier})  {latency_ms} ms  · {preview}…")

    total_ms = int((time.monotonic() - t_start) * 1000)
    payload = {
        "session_slug": session_path.stem,
        "session_path": str(session_path),
        "nb_id": nb_id,
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "total_bullets": len(bullets),
        "total_latency_ms": total_ms,
        "min_support_threshold": BULLET_MIN_SUPPORT,
        "bullets": results,
        "status": "ok",
    }
    return payload


def write_bullet_enrich_pending(slug: str, payload: dict) -> Path:
    NB_PENDING.mkdir(parents=True, exist_ok=True)
    out = NB_PENDING / f"{slug}.bullet-enrich.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def cmd_bullet_enrich(args) -> int:
    slug = args.bullet_enrich
    session_path = SESSIONS_DIR / f"{slug}.md"
    if not session_path.exists():
        print(f"✗ Session not found: {session_path}", file=sys.stderr)
        return 1

    nb_id = args.notebook or get_vault_meta_nb_id()
    if not nb_id:
        print(
            f"✗ No notebook ID. Pass --notebook <NB-ID> or write one to "
            f"{VAULT_META_NB_POINTER}",
            file=sys.stderr,
        )
        return 2

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"[{mode}] vault-nb-crystallize --bullet-enrich · {slug} · NB={nb_id[:8]}…")
    payload = enrich_session_bullets(
        session_path, nb_id, dry_run=args.dry_run, max_bullets=args.max_bullets,
    )

    if payload.get("status") == "no_bullets":
        print(f"⚠ No Learning bullets in {session_path.name}", file=sys.stderr)
        return 1

    out = write_bullet_enrich_pending(slug, payload)
    n = payload["total_bullets"]
    ms = payload.get("total_latency_ms", 0)
    high = sum(1 for b in payload["bullets"] if b.get("nb_confidence") == "high")
    mid  = sum(1 for b in payload["bullets"] if b.get("nb_confidence") == "mid")
    low  = sum(1 for b in payload["bullets"] if b.get("nb_confidence") == "low")
    err  = sum(1 for b in payload["bullets"] if b.get("nb_confidence") == "error")
    print(f"\n📝 Pending: {out}")
    print(f"   bullets={n}  🟢 high={high}  🟡 mid={mid}  🔴 low={low}  ✗ err={err}  · {ms/1000:.1f}s total")
    return 0


# ───────────────────────── CLI ─────────────────────────


def main():
    ap = argparse.ArgumentParser(description="NB crystallize (B-5 Réteg 2, Week 2)")
    ap.add_argument("slug", nargs="?", help="Project slug (or omit + use --all / --bullet-enrich)")
    ap.add_argument("--all", action="store_true", help="Process every project with linked NB")
    ap.add_argument("--dry-run", action="store_true", help="Don't query NB, just list targets")
    ap.add_argument("--bullet-enrich", metavar="SESSION_SLUG",
                    help="Per-bullet Layer 1.5 enrich for 11.11crystallize")
    ap.add_argument("--notebook", help="Override notebook ID (default: vault-meta NB)")
    ap.add_argument("--max-bullets", type=int, default=50,
                    help="Cap bullets per session (default 50 = effectively no cap)")
    args = ap.parse_args()

    if args.bullet_enrich:
        return sys.exit(cmd_bullet_enrich(args))

    if not args.slug and not args.all:
        ap.print_help()
        sys.exit(1)
    if args.slug and args.all:
        print("Use either <slug> OR --all, not both.", file=sys.stderr)
        sys.exit(2)

    if args.all:
        targets = list_linked_projects()
    else:
        p = PROJECTS_DIR / f"{args.slug}.md"
        if not p.exists():
            print(f"Project not found: {p}", file=sys.stderr)
            sys.exit(1)
        nb_id = get_notebook_id(p)
        if not nb_id:
            print(f"Project {args.slug} has no `notebooklm:` frontmatter — run vault-nb-sync first.",
                  file=sys.stderr)
            sys.exit(1)
        targets = [(p, nb_id)]

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"[{mode}] vault-nb-crystallize · {len(targets)} project(s) · week {iso_week_tag()}")
    print(f"{'STATUS':16} {'SLUG':30} {'NB':12} {'NOTES'}")

    results = []
    failures = 0
    for project_path, nb_id in targets:
        try:
            r = process_project(project_path, nb_id, args.dry_run)
        except Exception as e:
            r = {"slug": project_path.stem, "nb_id": nb_id, "status": "exception", "error": str(e)}
        results.append(r)
        notes = ""
        if r.get("status") == "ask_failed":
            notes = f"⚠ {r.get('error', '')[:60]}"
            failures += 1
        elif r.get("status") == "exception":
            notes = f"✗ {r.get('error', '')[:60]}"
            failures += 1
        elif r.get("status") == "would_ask":
            notes = f"→ {r['raw_out'].split('/')[-1]}"
        elif r.get("status") == "crystallized":
            notes = f"{r.get('answer_chars', 0)} chars → KO queued"
        print(f"{r['status']:16} {r['slug']:30} {nb_id[:8]:12} {notes}")

    if args.dry_run:
        print(f"\n[dry-run summary] {len(targets)} project(s) would be crystallized this run.")
    else:
        ok_count = sum(1 for r in results if r.get("status") == "crystallized")
        print(f"\n[summary] crystallized={ok_count} failed={failures} total={len(targets)}")

    sys.exit(1 if failures and not args.dry_run else 0)


if __name__ == "__main__":
    main()
