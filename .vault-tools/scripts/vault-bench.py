#!/root/.notebooklm-venv/bin/python3
"""
vault-bench — unified retrieval-quality + latency benchmark harness.

Runs a set of canonical queries against each available retrieval route and
emits a single comparable markdown report.

Routes tested (whichever are present on PATH):
  - vault-search           (Memgraph bge-m3 alone)
  - vault-search-fusion    (RRF hybrid of vault-search + agentmemory)
  - vault-ko-query --top-k (Layer-3, default route = --semantic-rrf)
  - vault-ko-query --semantic        (legacy compat)

Metric: mean latency over N queries (default 5). For LongMemEval-style
R@5, defer to vault-eval-regression --v03 (this is a quick health-bench,
not a recall-benchmark).

Usage:
  vault-bench                              # default 5 queries, all routes
  vault-bench --queries 10                 # 10 queries
  vault-bench --json                       # machine-readable
  vault-bench --output 06-Audits/<file>.md # write markdown audit
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_QUERIES = [
    "memgraph native vector index speedup",
    "RRF hybrid fusion retrieval pipeline",
    "subagent fanout zero cost LLM mutation",
    "schema migration downstream grep checklist",
    "G-Eval bias mitigation symmetric tightening",
    "Karpathy LLM wiki crystallization",
    "MEMORY.md overflow management",
    "B-7 typed entity classification",
    "vault-doctor health check axes",
    "Anki SRS confidence boost",
]


def run_query(cmd: list[str], timeout: int = 60) -> tuple[bool, float, int]:
    """Return (success, elapsed_s, n_results_or_0)."""
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        dt = time.time() - t0
        if r.returncode != 0:
            return False, dt, 0
        # Count results crudely (first valid JSON object's `results` or array len)
        try:
            stdout = r.stdout.strip()
            if stdout.startswith("["):
                data = json.loads(stdout)
                n = len(data) if isinstance(data, list) else 0
            else:
                data = json.loads(stdout)
                n = len(data.get("results", []) or data.get("groups", []))
        except Exception:
            n = 0
        return True, dt, n
    except Exception:
        return False, time.time() - t0, 0


def bench_route(name: str, cmd_template: list[str], queries: list[str]) -> dict:
    timings = []
    failures = 0
    for q in queries:
        cmd = [arg.format(q=q) if "{q}" in arg else arg for arg in cmd_template]
        cmd = [q if a == "{q_arg}" else a for a in cmd]
        ok, dt, n = run_query(cmd)
        if ok:
            timings.append(dt)
        else:
            failures += 1
    if not timings:
        return {"route": name, "status": "FAIL", "mean_s": None, "n_ok": 0, "n_fail": failures}
    return {
        "route": name,
        "status": "OK",
        "mean_s": round(sum(timings) / len(timings), 3),
        "min_s": round(min(timings), 3),
        "max_s": round(max(timings), 3),
        "n_ok": len(timings),
        "n_fail": failures,
    }


def discover_routes() -> list[tuple[str, list[str]]]:
    """Return [(label, command_template), ...] for routes available on PATH."""
    routes = []
    if shutil.which("vault-search"):
        routes.append(("vault-search (alone)", ["vault-search", "{q_arg}", "--top-k", "5", "--json"]))
    if shutil.which("vault-search-fusion"):
        routes.append(("vault-search-fusion (RRF)", ["vault-search-fusion", "{q_arg}", "--top-k", "5", "--json"]))
    if shutil.which("vault-ko-query"):
        routes.append(("vault-ko-query default (=rrf)", ["vault-ko-query", "{q_arg}", "--top-k", "3", "--json"]))
        routes.append(("vault-ko-query --hyde (rrf+HyDE)", ["vault-ko-query", "{q_arg}", "--top-k", "3", "--json", "--hyde"]))
        routes.append(("vault-ko-query --semantic (legacy)", ["vault-ko-query", "{q_arg}", "--top-k", "3", "--json", "--semantic"]))
        routes.append(("vault-ko-query --no-semantic", ["vault-ko-query", "{q_arg}", "--top-k", "3", "--json", "--no-semantic"]))
    return routes


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-bench")
    ap.add_argument("--queries", type=int, default=5,
                    help="Number of canonical queries (default 5, max 10)")
    ap.add_argument("--json", action="store_true",
                    help="JSON output to stdout")
    ap.add_argument("--output", type=Path,
                    help="Write markdown report to this file")
    args = ap.parse_args()

    queries = CANONICAL_QUERIES[: max(1, min(args.queries, len(CANONICAL_QUERIES)))]
    routes = discover_routes()
    if not routes:
        print("✗ no retrieval CLIs found on PATH", file=sys.stderr)
        return 2

    results = [bench_route(name, tmpl, queries) for name, tmpl in routes]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    if args.json:
        print(json.dumps({"ts": ts, "queries": queries, "routes": results}, indent=2))
        return 0

    # Markdown render
    lines = []
    lines.append(f"# vault-bench — retrieval-route latency comparison")
    lines.append(f"")
    lines.append(f"- Snapshot: {ts}")
    lines.append(f"- Queries: {len(queries)} canonical")
    lines.append(f"- Note: this is a QUICK latency comparison, NOT a recall benchmark. For R@5, see [`vault-eval-regression --v03`](../06-Audits/2026-05-25 v1.0.11 formal benchmark consolidated.md).")
    lines.append(f"")
    lines.append(f"## Latency comparison (mean over {len(queries)} queries)")
    lines.append(f"")
    lines.append(f"| route | mean (s) | min | max | ok | fail |")
    lines.append(f"|---|---:|---:|---:|---:|---:|")
    # Sort by mean_s ascending (fastest first)
    for r in sorted(results, key=lambda x: (x["mean_s"] is None, x["mean_s"] or 0)):
        if r["mean_s"] is None:
            lines.append(f"| `{r['route']}` | — | — | — | {r['n_ok']} | **{r['n_fail']}** |")
        else:
            lines.append(f"| `{r['route']}` | **{r['mean_s']}** | {r['min_s']} | {r['max_s']} | {r['n_ok']} | {r['n_fail']} |")
    lines.append("")
    lines.append("## Speedup vs slowest")
    slowest = max((r["mean_s"] for r in results if r["mean_s"] is not None), default=None)
    if slowest:
        lines.append("")
        lines.append(f"Reference (slowest): **{slowest:.3f}s**")
        lines.append("")
        for r in sorted(results, key=lambda x: x["mean_s"] or 1e9):
            if r["mean_s"] and r["mean_s"] > 0:
                speedup = slowest / r["mean_s"]
                lines.append(f"- `{r['route']}` — {speedup:.2f}× faster")
        lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```bash")
    lines.append("vault-bench --queries 5         # default")
    lines.append("vault-bench --queries 10 --json # full")
    lines.append("```")

    md = "\n".join(lines) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print(f"✓ wrote {args.output}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
