#!/root/.notebooklm-venv/bin/python3
"""
eval-l3-aggregator — heti session-quality trend riport (B-3 Réteg 3).

ADR: 07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md
Sprint: B-3, Week 2 Day 3-4.

Beolvas: /tmp/vault-eval/eval-l1-*.jsonl (és l2/l2.5 ha vannak)
Kiír: 06-Audits/Eval_Trend.md (heti rolling-window)

Usage:
    eval-l3-aggregator                          # default: last 7 nap
    eval-l3-aggregator --days 14
    eval-l3-aggregator --write                  # write to 06-Audits/Eval_Trend.md (default: stdout)
    eval-l3-aggregator --json
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
EVAL_DIR = Path(os.environ.get("EVAL_OUTPUT_DIR", "/tmp/vault-eval"))
OUTPUT = VAULT_ROOT / "06-Audits" / "Eval_Trend.md"


def load_l1_results(days: int) -> list[dict]:
    """Aggregate l1 results from the last N days of JSONL files."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = []
    if not EVAL_DIR.exists():
        return results
    for f in sorted(EVAL_DIR.glob("eval-l1-*.jsonl")):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return results


def aggregate(results: list[dict]) -> dict:
    quality_dist = Counter()
    flag_counter = Counter()
    by_session = {}
    for r in results:
        q = r.get("quality", "skip")
        quality_dist[q] += 1
        for f in r.get("flags", []):
            flag_counter[f.split(":")[0]] += 1
        by_session[r.get("file", "?")] = r

    total_evaluated = sum(v for k, v in quality_dist.items() if k != "skip")
    pass_rate = (quality_dist.get("A", 0) + quality_dist.get("B", 0)) / max(total_evaluated, 1)

    return {
        "total_sessions_evaluated": total_evaluated,
        "skipped_open": quality_dist.get("skip", 0),
        "quality_distribution": dict(quality_dist),
        "pass_rate": round(pass_rate, 3),
        "flag_frequency": dict(flag_counter.most_common()),
        "quality_c_sessions": [r["file"] for r in results if r.get("quality") == "C"],
        "quality_b_sessions": [r["file"] for r in results if r.get("quality") == "B"],
    }


def render_markdown(agg: dict, days: int) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    lines = [
        "---",
        "name: Eval Trend — heti session-quality riport",
        "type: audit",
        "tags: [audit, eval, b-3, weekly]",
        f"updated: {now}",
        "author: eval-l3-aggregator",
        "---",
        "",
        f"# Eval Trend — last {days} days",
        "",
        f"Generálva: {now} UTC",
        "",
        "## Összefoglaló",
        "",
        f"- **Total evaluated:** {agg['total_sessions_evaluated']} closed session",
        f"- **Open (skipped):** {agg['skipped_open']}",
        f"- **Pass-rate (A+B / total):** {agg['pass_rate']*100:.1f}%",
        "",
        "## Quality distribution",
        "",
        "| Quality | Count |",
        "|---|---|",
    ]
    for q in ["A", "B", "C", "D", "skip"]:
        c = agg["quality_distribution"].get(q, 0)
        if c > 0:
            lines.append(f"| **{q}** | {c} |")

    lines.extend([
        "",
        "## Flag frequency",
        "",
    ])
    if agg["flag_frequency"]:
        lines.append("| Flag | Count |")
        lines.append("|---|---|")
        for flag, c in agg["flag_frequency"].items():
            lines.append(f"| {flag} | {c} |")
    else:
        lines.append("_Nincs flag (mind tiszta)_")

    if agg["quality_c_sessions"]:
        lines.extend(["", "## Quality C — human-review queue", ""])
        for s in agg["quality_c_sessions"]:
            lines.append(f"- [ ] [[{s.replace('.md', '')}]]")

    if agg["quality_b_sessions"]:
        lines.extend(["", "## Quality B — figyelni", ""])
        for s in agg["quality_b_sessions"]:
            lines.append(f"- [[{s.replace('.md', '')}]]")

    lines.extend([
        "",
        "## Kapcsolódó",
        "",
        "- [[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]] — ADR",
        "- [[02-Projects/superintelligent-vault]] — sprint host",
        "- [[06-Audits/System_Health]] — vault integritás",
        "",
        "<!-- AUTO-GEN END — manuális notes lent -->",
    ])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Eval Trend aggregator (B-3 Réteg 3)")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--write", action="store_true", help="Write to 06-Audits/Eval_Trend.md")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = load_l1_results(args.days)
    agg = aggregate(results)

    if args.json:
        print(json.dumps(agg, ensure_ascii=False, indent=2))
        return

    md = render_markdown(agg, args.days)

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        # Preserve manual content below AUTO-GEN END marker
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        manual_match = existing.find("<!-- AUTO-GEN END")
        manual_tail = existing[manual_match:] if manual_match >= 0 else ""
        if manual_tail and "\n" in manual_tail:
            # Keep just the user-edited part after the AUTO-GEN END line
            user_section = manual_tail.split("\n", 1)[1] if "\n" in manual_tail else ""
            md = md.rstrip() + "\n" + user_section
        OUTPUT.write_text(md, encoding="utf-8")
        print(f"[write] {OUTPUT}")
    else:
        print(md)


if __name__ == "__main__":
    main()
