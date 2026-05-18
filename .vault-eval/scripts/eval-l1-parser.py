#!/usr/bin/env python3
"""
eval-l1-parser — determinisztikus L1 metrika-aggregátor a crystallize-pipeline
audit-log-jából (`06-Audits/crystallize-log.jsonl`).

ADR: 07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md
Wiki: 11-wiki/sv-07-continuous-evaluation.md
Sprint: B-3, Réteg 1 (kód-alapú, $0 API-cost) — Week 1-α (2026-05-17).

Status: LIVE. A crystallize-log.jsonl-ből per-session aggregált metrikákat termel,
amelyek az L2 (LLM-judge) és L3 (aggregator) bemenetét adják.

Eredeti session-fájl heurisztika (Day 0 skeleton) elérhető `--mode sessions`-szel.

Usage:
    eval-l1-parser                              # default: crystallize-log mód, table-output
    eval-l1-parser --json                       # JSON-output (machine-readable)
    eval-l1-parser --snapshot                   # write baseline snapshot 06-Audits/
    eval-l1-parser --log <path>                 # alternative log-file
    eval-l1-parser --mode sessions --backfill   # eredeti session-quality heuristic
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
AUDITS_DIR = VAULT_ROOT / "06-Audits"
DEFAULT_LOG = AUDITS_DIR / "crystallize-log.jsonl"
LEGACY_OUTPUT_DIR = Path("/tmp/vault-eval")

# Threshold-routing rules (ADR Réteg 1, legacy session-mode)
RULES = {
    "events_time_gap_hours": 2,
    "summary_min_chars": 100,
    "retry_pending_max": 5,
    "session_max_hours": 6,
}


# ---------------------------------------------------------------------------
# CRYSTALLIZE-LOG MODE (default, Week 1-α — LIVE)
# ---------------------------------------------------------------------------

def classify_record(rec: dict) -> str:
    """Return record-type discriminator."""
    if "event" in rec:
        return f"event:{rec['event']}"
    if "route" in rec and "scores" in rec:
        return "score"
    if "critic_decision" in rec:
        return "critic"
    if "apply_status" in rec:
        return "apply"
    return "other"


def load_log(path: Path) -> list[dict]:
    """Read JSONL log, skip malformed lines."""
    records = []
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[warn] {path}:{ln}: {e}", file=sys.stderr)
    return records


def aggregate_by_session(records: list[dict]) -> dict[str, dict]:
    """
    Per-session aggregated metrics.

    Returns:
        {session_slug: {
            "n_records": int,
            "n_bullets_scored": int,
            "n_auto_prop": int, "n_batch_preview": int, "n_discard": int,
            "auto_rate_pct": float,
            "n_applied_real": int,
            "n_critic_approve": int, "n_critic_modify": int, "n_critic_discard": int,
            "critic_pass_rate_pct": float,
            "n_apply_written": int, "n_apply_skipped": int, "n_apply_idempotent": int,
            "route_distribution": {route: count},
            "scorers": {scorer: count},
            "first_ts": iso, "last_ts": iso,
        }}
    """
    sessions: dict[str, dict] = defaultdict(lambda: {
        "n_records": 0,
        "n_bullets_scored": 0,
        "n_auto_prop": 0,
        "n_batch_preview": 0,
        "n_discard": 0,
        "n_applied_real": 0,
        "n_critic_approve": 0,
        "n_critic_modify": 0,
        "n_critic_discard": 0,
        "n_apply_written": 0,
        "n_apply_skipped": 0,
        "n_apply_idempotent": 0,
        "route_distribution": Counter(),
        "scorers": Counter(),
        "_timestamps": [],
    })

    for rec in records:
        slug = rec.get("session_slug")
        if not slug:
            continue  # global events (e.g. auto_disabled) skipped per-session
        s = sessions[slug]
        s["n_records"] += 1
        if (ts := rec.get("ts")):
            s["_timestamps"].append(ts)

        kind = classify_record(rec)
        if kind == "score":
            s["n_bullets_scored"] += 1
            route = rec.get("route", "unknown")
            s["route_distribution"][route] += 1
            if route == "auto-prop":
                s["n_auto_prop"] += 1
            elif route == "batch-preview":
                s["n_batch_preview"] += 1
            elif route == "discard":
                s["n_discard"] += 1
            if (scorer := rec.get("scorer")):
                s["scorers"][scorer] += 1
        elif kind == "event:apply_real":
            s["n_applied_real"] += 1
            decision = rec.get("critic_decision")
            if decision == "approve":
                s["n_critic_approve"] += 1
            elif decision == "modify":
                s["n_critic_modify"] += 1
            elif decision == "discard":
                s["n_critic_discard"] += 1
            status = rec.get("apply_status")
            if status == "written":
                s["n_apply_written"] += 1
            elif status == "skipped":
                s["n_apply_skipped"] += 1
            elif status == "idempotent-skip":
                s["n_apply_idempotent"] += 1

    # Derived rates + finalize
    out: dict[str, dict] = {}
    for slug, s in sessions.items():
        scored = s["n_bullets_scored"]
        critic_total = s["n_critic_approve"] + s["n_critic_modify"] + s["n_critic_discard"]
        auto_rate = (s["n_auto_prop"] / scored * 100.0) if scored else 0.0
        # "Pass" = approve or modify (modify still results in apply); discard = fail.
        critic_pass = s["n_critic_approve"] + s["n_critic_modify"]
        pass_rate = (critic_pass / critic_total * 100.0) if critic_total else 0.0
        ts_list = sorted(s.pop("_timestamps"))
        out[slug] = {
            "session_slug": slug,
            "n_records": s["n_records"],
            "n_bullets_scored": scored,
            "n_auto_prop": s["n_auto_prop"],
            "n_batch_preview": s["n_batch_preview"],
            "n_discard": s["n_discard"],
            "auto_rate_pct": round(auto_rate, 2),
            "n_applied_real": s["n_applied_real"],
            "n_critic_approve": s["n_critic_approve"],
            "n_critic_modify": s["n_critic_modify"],
            "n_critic_discard": s["n_critic_discard"],
            "critic_pass_rate_pct": round(pass_rate, 2),
            "n_apply_written": s["n_apply_written"],
            "n_apply_skipped": s["n_apply_skipped"],
            "n_apply_idempotent": s["n_apply_idempotent"],
            "route_distribution": dict(s["route_distribution"]),
            "scorers": dict(s["scorers"]),
            "first_ts": ts_list[0] if ts_list else None,
            "last_ts": ts_list[-1] if ts_list else None,
        }
    return out


def render_table(by_session: dict[str, dict]) -> str:
    """Compact text-table summary."""
    if not by_session:
        return "(no sessions found in log)"
    rows = sorted(by_session.values(), key=lambda r: r["session_slug"])
    lines = []
    header = (
        f"{'session_slug':<40} {'scored':>6} {'auto':>5} {'btch':>5} {'disc':>5} "
        f"{'auto%':>6} {'applR':>6} {'apv':>4} {'mod':>4} {'dsc':>4} {'pass%':>6} {'wrtn':>5}"
    )
    lines.append(header)
    lines.append("-" * len(header))
    totals = Counter()
    for r in rows:
        lines.append(
            f"{r['session_slug']:<40} "
            f"{r['n_bullets_scored']:>6} {r['n_auto_prop']:>5} {r['n_batch_preview']:>5} {r['n_discard']:>5} "
            f"{r['auto_rate_pct']:>6.1f} {r['n_applied_real']:>6} "
            f"{r['n_critic_approve']:>4} {r['n_critic_modify']:>4} {r['n_critic_discard']:>4} "
            f"{r['critic_pass_rate_pct']:>6.1f} {r['n_apply_written']:>5}"
        )
        for k in ("n_bullets_scored", "n_auto_prop", "n_batch_preview", "n_discard",
                 "n_applied_real", "n_critic_approve", "n_critic_modify",
                 "n_critic_discard", "n_apply_written"):
            totals[k] += r[k]
    lines.append("-" * len(header))
    lines.append(
        f"{'TOTAL ({} sessions)'.format(len(rows)):<40} "
        f"{totals['n_bullets_scored']:>6} {totals['n_auto_prop']:>5} "
        f"{totals['n_batch_preview']:>5} {totals['n_discard']:>5} "
        f"{'-':>6} {totals['n_applied_real']:>6} "
        f"{totals['n_critic_approve']:>4} {totals['n_critic_modify']:>4} "
        f"{totals['n_critic_discard']:>4} {'-':>6} {totals['n_apply_written']:>5}"
    )
    return "\n".join(lines)


def write_snapshot(by_session: dict[str, dict], out_dir: Path) -> Path:
    """Write per-session baseline JSONL (one line per session)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"eval-l1-baseline-{ts}.jsonl"
    snapshot_ts = datetime.utcnow().isoformat() + "Z"
    with path.open("w", encoding="utf-8") as f:
        for slug in sorted(by_session):
            rec = dict(by_session[slug])
            rec["_snapshot_ts"] = snapshot_ts
            rec["_layer"] = "L1"
            rec["_parser_version"] = "1.0"
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


def readiness_summary(by_session: dict[str, dict]) -> str:
    n_sessions = len(by_session)
    n_bullets = sum(r["n_bullets_scored"] for r in by_session.values())
    n_auto = sum(r["n_auto_prop"] for r in by_session.values())
    n_applied = sum(r["n_apply_written"] for r in by_session.values())
    return (
        f"L1 parser baseline: {n_sessions} sessions, {n_bullets} total bullets scored, "
        f"{n_auto} route=auto-prop, {n_applied} apply_written (real-mode). "
        f"Ready for L2 LLM-judge addition next iteration."
    )


def run_log_mode(args) -> int:
    log_path = Path(args.log) if args.log else DEFAULT_LOG
    records = load_log(log_path)
    by_session = aggregate_by_session(records)

    if args.json:
        print(json.dumps({
            "log": str(log_path),
            "n_records": len(records),
            "n_sessions": len(by_session),
            "sessions": by_session,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"# L1 baseline — source: {log_path} ({len(records)} records)")
        print(render_table(by_session))
        print()
        print(readiness_summary(by_session))

    if args.snapshot:
        out = write_snapshot(by_session, AUDITS_DIR)
        print(f"[snapshot] {out}", file=sys.stderr)

    return 0


# ---------------------------------------------------------------------------
# LEGACY SESSION-FILE MODE (Day 0 skeleton — retained for backward-compat)
# ---------------------------------------------------------------------------

def parse_session(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    flags = []

    fm_match = re.search(r"^status:\s*(\w+)", text, re.MULTILINE)
    if not fm_match or fm_match.group(1) != "closed":
        return {"file": str(path.relative_to(VAULT_ROOT)), "skip": "not-closed"}

    summary_match = re.search(r"## Summary\s*\n+(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not summary_match or len(summary_match.group(1).strip()) < RULES["summary_min_chars"]:
        flags.append("incomplete-summary")

    learnings_match = re.search(r"## Learnings.*?\n+(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not learnings_match or len(learnings_match.group(1).strip()) < 50:
        flags.append("no-learning-extracted")

    next_match = re.search(r"## Next session\s*\n+(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not next_match or len(next_match.group(1).strip()) < 30:
        flags.append("no-handoff")

    retry_count = len(re.findall(r"retry[\s-]pending", text, re.IGNORECASE))
    if retry_count > RULES["retry_pending_max"]:
        flags.append(f"high-retry-rate:{retry_count}")

    if not flags:
        quality = "A"
    elif len(flags) <= 2:
        quality = "B"
    else:
        quality = "C"

    return {
        "file": str(path.relative_to(VAULT_ROOT)),
        "quality": quality,
        "flags": flags,
        "retry_count": retry_count,
        "evaluated_at": datetime.utcnow().isoformat(),
    }


def run_session_mode(args) -> int:
    if not (args.since or args.session or args.backfill):
        print("[error] session-mode requires --since/--session/--backfill", file=sys.stderr)
        return 1

    files = []
    if args.session:
        p = SESSIONS_DIR / f"{args.session}.md"
        if p.exists():
            files.append(p)
    else:
        for p in sorted(SESSIONS_DIR.glob("*.md")):
            if args.since:
                try:
                    cutoff = datetime.fromisoformat(args.since)
                    if datetime.fromtimestamp(p.stat().st_mtime) < cutoff:
                        continue
                except ValueError:
                    pass
            files.append(p)

    if not args.dry_run:
        LEGACY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = [parse_session(f) for f in files]

    if args.dry_run:
        for r in results[:10]:
            print(json.dumps(r, ensure_ascii=False))
        print(f"[dry-run] {len(results)} sessions evaluated")
    else:
        out_path = LEGACY_OUTPUT_DIR / f"eval-l1-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
        with out_path.open("a") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[write] {len(results)} → {out_path}")

    dist = {}
    for r in results:
        q = r.get("quality", "skip")
        dist[q] = dist.get(q, 0) + 1
    print(f"  Quality distribution: {dist}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="L1 eval parser (B-3, sv-7)")
    ap.add_argument("--mode", choices=["log", "sessions"], default="log",
                    help="log = crystallize-log aggregation (default); "
                         "sessions = legacy session-file quality heuristic")
    # log-mode flags
    ap.add_argument("--log", help="path to crystallize-log.jsonl (default: 06-Audits/)")
    ap.add_argument("--json", action="store_true", help="JSON output (log-mode)")
    ap.add_argument("--snapshot", action="store_true",
                    help="write 06-Audits/eval-l1-baseline-<ts>.jsonl")
    # legacy session-mode flags
    ap.add_argument("--since", help="ISO date — closed sessions since (sessions-mode)")
    ap.add_argument("--session", help="single session slug (sessions-mode)")
    ap.add_argument("--backfill", action="store_true", help="ALL sessions (sessions-mode)")
    ap.add_argument("--dry-run", action="store_true", help="preview, no JSONL write")
    args = ap.parse_args()

    if args.mode == "log":
        sys.exit(run_log_mode(args))
    else:
        sys.exit(run_session_mode(args))


if __name__ == "__main__":
    main()
