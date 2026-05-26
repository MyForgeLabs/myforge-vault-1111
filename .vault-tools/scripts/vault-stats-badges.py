#!/root/.notebooklm-venv/bin/python3
"""
vault-stats-badges — generate static SVG badges for the public README.

Emits 4 shields-style SVG files into docs/badges/:
  - typed-coverage.svg     (Memgraph typed-coverage %)
  - longmemeval.svg        (LongMemEval-S R@5 %)
  - latency.svg            (Layer-3 default-route latency)
  - mutex.svg              (Cron mutex-coverage %)
  - cost.svg               (always "$0 marginal")
  - generated.svg          (timestamp)

Shields-style (flat): two-segment, dark label / colored value, 11pt sans-serif,
auto-sized. No external dependency (no shields.io request — pure local SVG).

Usage:
  vault-stats-badges                        # all 6 badges to default dir
  vault-stats-badges --output <dir>         # custom dir
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_OUT = Path("/root/projects/myforge-vault-1111/docs/badges")


def char_width_estimate(text: str) -> int:
    """Crude monospace-like estimate (11pt sans-serif). Pixels."""
    # Average ~6.5 px per char at 11pt Verdana. We over-estimate a bit for safety.
    return max(40, int(len(text) * 6.5) + 14)


def badge_svg(label: str, value: str, color: str = "#4c8eda") -> str:
    """Generate a shields-style two-segment SVG."""
    label_w = char_width_estimate(label)
    value_w = char_width_estimate(value)
    total_w = label_w + value_w
    h = 20

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{h}" role="img" aria-label="{label}: {value}">
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".25"/>
    <stop offset="1" stop-opacity=".25"/>
  </linearGradient>
  <mask id="m"><rect width="{total_w}" height="{h}" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{label_w}" height="{h}" fill="#444"/>
    <rect x="{label_w}" width="{value_w}" height="{h}" fill="{color}"/>
    <rect width="{total_w}" height="{h}" fill="url(#g)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,sans-serif" font-size="11">
    <text x="{label_w/2}" y="14" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_w/2}" y="13">{label}</text>
    <text x="{label_w + value_w/2}" y="14" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_w + value_w/2}" y="13">{value}</text>
  </g>
</svg>
"""


def collect_metrics() -> dict:
    out = {"typed_coverage_pct": None, "longmemeval_r5_pct": None,
           "latency_s": None, "cron_mutex_pct": None}
    try:
        r = subprocess.run(["vault-doctor", "--json"], capture_output=True, text=True, timeout=20)
        d = json.loads(r.stdout)
        c = d.get("checks", {})
        if "Memgraph" in c:
            out["typed_coverage_pct"] = c["Memgraph"].get("typed_pct")
        if "Cron" in c:
            out["cron_mutex_pct"] = c["Cron"].get("pct_protected")
    except Exception:
        pass
    try:
        baseline = Path("/root/obsidian-vault/.vault-eval/regression/baseline.json")
        if baseline.exists():
            b = json.loads(baseline.read_text())
            r5 = b.get("v03_fused_a_rrf_optimal", {}).get("recall_at_5")
            if r5 is not None:
                out["longmemeval_r5_pct"] = round(r5 * 100, 2)
    except Exception:
        pass
    try:
        ce = subprocess.run(["vault-continuous-eval", "--json"], capture_output=True, text=True, timeout=30)
        cd = json.loads(ce.stdout)
        for ax in cd.get("axes", []):
            if ax.get("axis") == "retrieval-latency":
                out["latency_s"] = ax.get("key_metrics", {}).get("mean_s")
                break
    except Exception:
        pass
    return out


def pct_color(pct: float, thresholds=(50, 75)) -> str:
    """Red/yellow/green by percentage threshold."""
    if pct >= thresholds[1]: return "#4c1"      # green
    if pct >= thresholds[0]: return "#dfb317"   # yellow
    return "#e05d44"                            # red


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-stats-badges")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT,
                    help=f"Output dir (default: {DEFAULT_OUT})")
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    m = collect_metrics()
    today = date.today().isoformat()

    badges = []
    if m["typed_coverage_pct"] is not None:
        v = m["typed_coverage_pct"]
        badges.append(("typed-coverage.svg",
                       badge_svg("typed-coverage", f"{v:.1f}%", pct_color(v))))
    if m["longmemeval_r5_pct"] is not None:
        v = m["longmemeval_r5_pct"]
        badges.append(("longmemeval-r5.svg",
                       badge_svg("LongMemEval R@5", f"{v:.1f}%", pct_color(v, (60, 70)))))
    if m["latency_s"] is not None:
        v = m["latency_s"]
        col = "#4c1" if v < 2 else "#dfb317" if v < 5 else "#e05d44"
        badges.append(("latency.svg", badge_svg("Layer-3 latency", f"{v:.2f}s", col)))
    if m["cron_mutex_pct"] is not None:
        v = m["cron_mutex_pct"]
        badges.append(("cron-mutex.svg",
                       badge_svg("cron-mutex", f"{v:.0f}%", pct_color(v, (75, 95)))))
    badges.append(("cost.svg", badge_svg("marginal cost", "$0", "#4c1")))
    badges.append(("generated.svg", badge_svg("snapshot", today, "#4c8eda")))

    for fname, svg in badges:
        (args.output / fname).write_text(svg, encoding="utf-8")
    print(f"[stats-badges] wrote {len(badges)} badges → {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
