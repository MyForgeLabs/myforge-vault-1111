#!/root/.notebooklm-venv/bin/python3
"""
vault-metrics-append — append today's metric snapshot to timeline.json.

Used by `vault-public-sync` after each release to auto-grow the per-release
line-chart. Idempotent: if today's date + version already exists, skip.

Inputs:
  --version <X.Y.Z>     CHANGELOG version to record (default: parse from CHANGELOG)
  --date <YYYY-MM-DD>   Date (default: today UTC)
  --timeline <path>     timeline.json (default: public-repo/docs/metrics/timeline.json)

Sources for each metric (must succeed or value falls back to last-known):
  typed_coverage_pct  → vault-doctor --json → checks.Memgraph.typed_pct
  retrieval_latency_s → vault-doctor --json → checks.retrieval-latency (if added) or vault-bench
  cron_mutex_pct      → vault-doctor --json → checks.Cron.pct_protected
  longmemeval_r5_pct  → .vault-eval/regression/baseline.json → v03_fused_a_rrf_optimal.recall_at_5

Usage:
  vault-metrics-append --version 1.0.15
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from datetime import date as _date, datetime, timezone
from pathlib import Path

DEFAULT_TIMELINE = Path("/root/projects/myforge-vault-1111/docs/metrics/timeline.json")
DEFAULT_BASELINE = Path("/root/obsidian-vault/.vault-eval/regression/baseline.json")


def parse_latest_version_from_changelog() -> str | None:
    p = Path("/root/projects/myforge-vault-1111/CHANGELOG.md")
    if not p.exists():
        return None
    for ln in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## \[(\d+\.\d+\.\d+)\]", ln)
        if m:
            return m.group(1)
    return None


def collect_metrics() -> dict:
    out = {}
    # vault-doctor
    try:
        r = subprocess.run(["vault-doctor", "--json"], capture_output=True, text=True, timeout=20)
        if r.stdout:
            d = json.loads(r.stdout)
            checks = d.get("checks", {})
            if "Memgraph" in checks:
                out["typed_coverage_pct"] = checks["Memgraph"].get("typed_pct")
            if "Cron" in checks:
                out["cron_mutex_pct"] = checks["Cron"].get("pct_protected")
    except Exception:
        pass

    # LongMemEval baseline
    try:
        if DEFAULT_BASELINE.exists():
            b = json.loads(DEFAULT_BASELINE.read_text())
            r5 = b.get("v03_fused_a_rrf_optimal", {}).get("recall_at_5")
            if r5 is not None:
                out["longmemeval_r5_pct"] = round(r5 * 100, 2)
    except Exception:
        pass

    # vault-bench (only if very recent JSON snapshot exists; else fall back)
    # Try to read continuous-eval's retrieval-latency reading instead — already cached
    try:
        r = subprocess.run(["vault-doctor", "--json"], capture_output=True, text=True, timeout=20)
        # vault-doctor doesn't carry retrieval-latency yet; use continuous-eval if --json available
        ce = subprocess.run(["vault-continuous-eval", "--json"], capture_output=True, text=True, timeout=30)
        if ce.stdout:
            cd = json.loads(ce.stdout)
            for ax in cd.get("axes", []):
                if ax.get("axis") == "retrieval-latency":
                    out["retrieval_latency_s"] = ax.get("key_metrics", {}).get("mean_s")
                    break
    except Exception:
        pass

    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-metrics-append")
    ap.add_argument("--version", help="CHANGELOG version (default: parse latest)")
    ap.add_argument("--date", default=_date.today().isoformat(),
                    help="ISO date (default: today UTC)")
    ap.add_argument("--timeline", type=Path, default=DEFAULT_TIMELINE,
                    help=f"Path to timeline.json (default: {DEFAULT_TIMELINE})")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print would-be entry, write nothing")
    args = ap.parse_args()

    version = args.version or parse_latest_version_from_changelog()
    if not version:
        print("✗ no --version given and could not parse CHANGELOG", file=sys.stderr)
        return 2

    if not args.timeline.exists():
        print(f"✗ {args.timeline} missing", file=sys.stderr)
        return 2

    data = json.loads(args.timeline.read_text(encoding="utf-8"))
    releases = data.setdefault("releases", [])

    # Idempotency: skip if today's (version, date) tuple already exists
    for r in releases:
        if r.get("version") == version and r.get("date") == args.date:
            print(f"[metrics-append] {version} @ {args.date} already in timeline — skip", file=sys.stderr)
            return 0

    metrics = collect_metrics()
    new_entry = {"version": version, "date": args.date}
    new_entry.update({k: v for k, v in metrics.items() if v is not None})

    if args.dry_run:
        print(json.dumps(new_entry, indent=2))
        return 0

    releases.append(new_entry)
    args.timeline.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    print(f"[metrics-append] appended v{version} @ {args.date}: {metrics}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
