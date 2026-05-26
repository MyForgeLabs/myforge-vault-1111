#!/usr/bin/env python3
"""
vault-continuous-eval — weekly rollup of all per-axis audit outputs.

Aggregates the latest results from each individual audit CLI into one
unified health-summary with week-over-week drift detection:

  - vault-eval-regression       (LongMemEval-S R@5 retrieval baseline)
  - vault-graph-complementarity (FCA / CD / XR two-tier metrics)
  - vault-graph-diff            (Jaccard label-overlap, legacy reference)
  - vault-ko-conflicts-audit    (cross-source contradictions)
  - vault-ko-belief-weekly      (Bayesian belief-update health)
  - vault-plugin-hooks-audit    (marketplace plugin instruction-injection)
  - vault-crystallize-monitor   (crystallize pipeline + shadow-window)

Output: 06-Audits/continuous-eval-YYYY-WNN.md

Run weekly via cron (Sunday 06:00 UTC, AFTER the per-axis cron jobs at
02:45/05:00/05:30). Exit code 0 always — this is a passive rollup.
Strict mode (--strict) exits 1 if any axis crossed an alert-threshold,
for use in CI/notification pipelines.

Wiki: 11-wiki/sv-07-continuous-evaluation.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
try:
    from vault_atomic import atomic_write  # noqa: E402
except ImportError:
    def atomic_write(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
AUDITS_DIR = VAULT_ROOT / "06-Audits"


# ── Per-axis readers ────────────────────────────────────────────────────────
# Each reader returns a dict with at least {status, summary, key_metrics, source}.
# status ∈ {"ok", "warn", "alert", "stale", "missing"}.


def _file_age_days(path: Path) -> float | None:
    if not path.exists():
        return None
    return (datetime.now().timestamp() - path.stat().st_mtime) / 86400.0


def read_eval_regression() -> dict:
    """Reads vault-eval-regression.json. Tolerates JSON-followed-by-plain-text
    (the CLI writes a JSON object then a trailing confirmation line)."""
    f = AUDITS_DIR / "vault-eval-regression.json"
    if not f.exists():
        return {"axis": "retrieval (LongMemEval-S)", "status": "missing", "source": str(f)}
    age = _file_age_days(f)
    raw = f.read_text(encoding="utf-8")
    # Strip trailing non-JSON content (CLI appends a plain-text status line)
    data = None
    decoder = json.JSONDecoder()
    try:
        data, _ = decoder.raw_decode(raw)
    except Exception as e:
        return {"axis": "retrieval (LongMemEval-S)", "status": "alert",
                "summary": f"parse error: {e}", "source": str(f)}

    # Accept multiple shape conventions:
    #   - {status: "green"|"red", passed, failed, mode, ts}
    #   - {exit_code: 0|1, results: [...]}
    status_field = (data.get("status") or "").lower()
    exit_code = data.get("exit_code", data.get("returncode"))
    passed = data.get("passed")
    failed = data.get("failed")

    if status_field in ("green", "ok", "pass"):
        status = "ok"
    elif status_field in ("red", "fail", "alert"):
        status = "alert"
    elif exit_code is not None:
        status = "ok" if exit_code == 0 else "alert"
    elif failed is not None and failed > 0:
        status = "alert"
    elif passed is not None and passed > 0:
        status = "ok"
    else:
        status = "warn"

    if age and age > 3:
        status = "stale" if status == "ok" else status

    metrics = {}
    if passed is not None:
        metrics["passed"] = passed
    if failed is not None:
        metrics["failed"] = failed
    if "mode" in data:
        metrics["mode"] = data["mode"]
    for r in data.get("results", []):
        cfg = r.get("config") or r.get("name", "?")
        if "recall" in r:
            metrics[f"R@5[{cfg}]"] = r["recall"]

    summary_bits = []
    if "mode" in data: summary_bits.append(f"mode={data['mode']}")
    if age: summary_bits.append(f"age={age:.1f}d")
    return {
        "axis": "retrieval (LongMemEval-S)",
        "status": status,
        "summary": ", ".join(summary_bits) if summary_bits else "—",
        "key_metrics": metrics,
        "source": str(f),
    }


def read_complementarity() -> dict:
    """Reads the latest 'two-tier complementarity baseline.md' audit."""
    matches = sorted(AUDITS_DIR.glob("*two-tier complementarity baseline.md"))
    if not matches:
        return {"axis": "two-tier graph", "status": "missing"}
    latest = matches[-1]
    age = _file_age_days(latest)
    text = latest.read_text(encoding="utf-8")
    fca = re.search(r"FCA[^|]*\|\s*\*\*([\d.]+)\*\*", text)
    cd = re.search(r"CD.*co-occurrence[^|]*\|\s*\*\*([\d.]+)\*\*", text)
    xr1 = re.search(r"XR_T1[^|]*\|\s*\*\*([\d.]+)\*\*", text)
    xr2 = re.search(r"XR_T2[^|]*\|\s*\*\*([\d.]+)\*\*", text)
    metrics = {}
    if fca: metrics["FCA"] = float(fca.group(1))
    if cd:  metrics["CD"]  = float(cd.group(1))
    if xr1: metrics["XR_T1"] = float(xr1.group(1))
    if xr2: metrics["XR_T2"] = float(xr2.group(1))
    status = "ok"
    if metrics.get("FCA", 1.0) < 0.95: status = "warn"
    if metrics.get("CD", 0.5) < 0.35: status = "alert"
    if metrics.get("XR_T1", 1.0) < 0.95: status = "warn"
    if metrics.get("XR_T2", 1.0) < 0.80: status = "warn"
    if age and age > 14: status = "stale"
    return {
        "axis": "two-tier graph complementarity",
        "status": status,
        "summary": f"audit age={age:.1f}d" if age else "no age",
        "key_metrics": metrics,
        "source": str(latest),
    }


def read_conflicts() -> dict:
    matches = sorted(AUDITS_DIR.glob("cross-source-conflicts-*.md"))
    if not matches:
        return {"axis": "ko-conflicts", "status": "missing"}
    latest = matches[-1]
    age = _file_age_days(latest)
    text = latest.read_text(encoding="utf-8")
    high = re.search(r"🔴\s*(\d+)\s*HIGH", text)
    mid  = re.search(r"🟡\s*(\d+)\s*MID",  text)
    low  = re.search(r"🟢\s*(\d+)\s*LOW",  text)
    total = re.search(r"\*\*(\d+)\*\*\s*total\s+conflict", text)
    metrics = {}
    if total: metrics["total"] = int(total.group(1))
    if high:  metrics["HIGH"]  = int(high.group(1))
    if mid:   metrics["MID"]   = int(mid.group(1))
    if low:   metrics["LOW"]   = int(low.group(1))
    status = "ok"
    if metrics.get("HIGH", 0) >= 30: status = "alert"
    elif metrics.get("HIGH", 0) >= 15: status = "warn"
    if age and age > 14: status = "stale"
    return {
        "axis": "ko-conflicts (cross-source)",
        "status": status,
        "summary": f"audit age={age:.1f}d" if age else "no age",
        "key_metrics": metrics,
        "source": str(latest),
    }


def read_belief() -> dict:
    matches = sorted(AUDITS_DIR.glob("ko-belief-weekly-*.md"))
    if not matches:
        return {"axis": "ko-belief", "status": "missing"}
    latest = matches[-1]
    age = _file_age_days(latest)
    return {
        "axis": "ko-belief (Bayesian update)",
        "status": "stale" if age and age > 14 else "ok",
        "summary": f"audit age={age:.1f}d" if age else "no age",
        "source": str(latest),
    }


def read_plugin_hooks() -> dict:
    matches = sorted(AUDITS_DIR.glob("plugin-hooks-audit-*.md"))
    if not matches:
        return {"axis": "plugin-hooks", "status": "missing"}
    latest = matches[-1]
    age = _file_age_days(latest)
    text = latest.read_text(encoding="utf-8")
    high = re.search(r"🔴\s*\*\*(\d+)\s+HIGH-heat", text)
    mid  = re.search(r"🟡\s*\*\*(\d+)\s+MID-heat",  text)
    metrics = {}
    if high: metrics["HIGH"] = int(high.group(1))
    if mid:  metrics["MID"]  = int(mid.group(1))
    status = "ok"
    if metrics.get("HIGH", 0) > 0: status = "alert"
    elif metrics.get("MID", 0) > 0: status = "warn"
    if age and age > 14: status = "stale"
    return {
        "axis": "plugin-hooks (instruction-injection)",
        "status": status,
        "summary": f"audit age={age:.1f}d" if age else "no age",
        "key_metrics": metrics,
        "source": str(latest),
    }


def read_crystallize_health() -> dict:
    """Reads crystallize-health.json produced by vault-crystallize-monitor."""
    f = AUDITS_DIR / "crystallize-health.json"
    if not f.exists():
        return {"axis": "crystallize-pipeline", "status": "missing"}
    age = _file_age_days(f)
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        return {"axis": "crystallize-pipeline", "status": "alert",
                "summary": f"parse error: {e}"}
    metrics = {}
    for k in ("auto_rate", "revert_rate", "threshold", "weeks_analyzed"):
        if k in data:
            metrics[k] = data[k]
    status = "ok"
    if metrics.get("revert_rate", 0) > 0.05: status = "warn"
    if age and age > 14: status = "stale"
    return {
        "axis": "crystallize-pipeline + shadow-monitoring",
        "status": status,
        "summary": f"health-json age={age:.1f}d" if age else "no age",
        "key_metrics": metrics,
        "source": str(f),
    }


def read_typed_coverage() -> dict:
    """Memgraph typed-entity coverage % (B-7 typed-graph axis, 2026-05-25)."""
    try:
        import mgclient
    except ImportError:
        return {
            "axis": "typed-coverage", "status": "missing",
            "summary": "mgclient not installed",
            "key_metrics": {}, "source": "memgraph://127.0.0.1:7687",
        }
    try:
        conn = mgclient.connect(host="127.0.0.1", port=7687)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("MATCH (n:Entity) RETURN count(n)")
        total = cur.fetchone()[0]
        cur.execute("MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n)")
        typed = cur.fetchone()[0]
        pct = (typed / total * 100) if total else 0
        if total == 0:
            status, msg = "alert", "0 entities (Memgraph empty)"
        elif pct < 10:
            status, msg = "alert", f"{pct:.1f}% — far below target"
        elif pct < 50:
            status, msg = "warn", f"{pct:.1f}% — below 50% target"
        else:
            status, msg = "ok", f"{pct:.1f}% ({typed}/{total} entities)"
        return {
            "axis": "typed-coverage", "status": status, "summary": msg,
            "key_metrics": {
                "total": total, "typed": typed, "typed_pct": round(pct, 1),
            },
            "source": "memgraph://127.0.0.1:7687",
        }
    except Exception as e:
        return {
            "axis": "typed-coverage", "status": "missing",
            "summary": f"connect failed: {str(e)[:60]}",
            "key_metrics": {}, "source": "memgraph://127.0.0.1:7687",
        }


def read_retrieval_latency() -> dict:
    """Layer-3 retrieval latency benchmark (3-query mean, default route = --semantic-rrf, 2026-05-25)."""
    import subprocess, time
    QUERIES = [
        "memgraph native vector index",
        "RRF hybrid fusion retrieval",
        "subagent fanout pattern",
    ]
    timings = []
    for q in QUERIES:
        t0 = time.time()
        try:
            r = subprocess.run(
                ["vault-ko-query", q, "--top-k", "3", "--json"],
                capture_output=True, timeout=30, text=True,
            )
            if r.returncode == 0:
                timings.append(time.time() - t0)
        except Exception:
            pass
    if not timings:
        return {
            "axis": "retrieval-latency", "status": "missing",
            "summary": "vault-ko-query unreachable",
            "key_metrics": {}, "source": "vault-ko-query --top-k --json",
        }
    mean_s = sum(timings) / len(timings)
    if mean_s > 5.0:
        status, msg = "alert", f"{mean_s:.2f}s mean (>5s — slow)"
    elif mean_s > 2.0:
        status, msg = "warn", f"{mean_s:.2f}s mean (>2s — drift)"
    else:
        status, msg = "ok", f"{mean_s:.2f}s mean ({len(timings)} queries)"
    return {
        "axis": "retrieval-latency", "status": status, "summary": msg,
        "key_metrics": {
            "mean_s": round(mean_s, 2),
            "queries": len(timings),
            "min_s": round(min(timings), 2),
            "max_s": round(max(timings), 2),
        },
        "source": "vault-ko-query --top-k --json (default = --semantic-rrf)",
    }


def read_broken_wikilinks() -> dict:
    """Broken wikilink targets count (vault-broken-wikilinks-audit JSON snapshot)."""
    import glob
    # Latest snapshot wins
    candidates = sorted(glob.glob(str(AUDITS_DIR / "broken-wikilinks-*.json")))
    if not candidates:
        return {
            "axis": "broken-wikilinks", "status": "missing",
            "summary": "no broken-wikilinks-*.json found",
            "key_metrics": {}, "source": "06-Audits/broken-wikilinks-*.json",
        }
    latest = Path(candidates[-1])
    try:
        d = json.loads(latest.read_text())
        targets = d.get("broken_targets", 0)
        refs = d.get("broken_references", 0)
        if targets > 100:
            status, msg = "alert", f"{targets} broken targets ({refs} refs) — drift"
        elif targets > 50:
            status, msg = "warn", f"{targets} broken targets ({refs} refs) — above soft-cap 50"
        else:
            status, msg = "ok", f"{targets} broken targets ({refs} refs)"
        return {
            "axis": "broken-wikilinks", "status": status, "summary": msg,
            "key_metrics": {"targets": targets, "refs": refs},
            "source": str(latest),
        }
    except Exception as e:
        return {
            "axis": "broken-wikilinks", "status": "missing",
            "summary": f"parse failed: {str(e)[:60]}",
            "key_metrics": {}, "source": str(latest),
        }


READERS = [
    read_eval_regression,
    read_complementarity,
    read_conflicts,
    read_belief,
    read_plugin_hooks,
    read_crystallize_health,
    read_typed_coverage,
    read_retrieval_latency,
    read_broken_wikilinks,
]


# ── Week-over-week diff ─────────────────────────────────────────────────────


def find_prior_rollup() -> Path | None:
    """Find the prior weekly rollup file, if any."""
    matches = sorted(AUDITS_DIR.glob("continuous-eval-*.md"))
    # ignore the one we might be writing this run; just return the latest
    # one that's older than now-24h (prior weekly run)
    cutoff = datetime.now().timestamp() - 24 * 3600
    for m in reversed(matches):
        if m.stat().st_mtime < cutoff:
            return m
    return None


def parse_prior_metrics(path: Path) -> dict:
    """Parse a prior rollup's per-axis metrics from JSON block."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    m = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


def compute_deltas(now_axes: list[dict], prior: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    prior_axes = {a["axis"]: a for a in prior.get("axes", []) if "axis" in a}
    for ax in now_axes:
        name = ax["axis"]
        prior_ax = prior_axes.get(name)
        if not prior_ax:
            continue
        prior_metrics = prior_ax.get("key_metrics", {}) or {}
        now_metrics = ax.get("key_metrics", {}) or {}
        for k, v in now_metrics.items():
            if k in prior_metrics:
                try:
                    delta = float(v) - float(prior_metrics[k])
                    out.setdefault(name, {})[k] = delta
                except (TypeError, ValueError):
                    pass
    return out


# ── Rendering ───────────────────────────────────────────────────────────────


STATUS_ICON = {
    "ok":      "🟢",
    "warn":    "🟡",
    "alert":   "🔴",
    "stale":   "⏳",
    "missing": "⚪",
}


def render_markdown(axes: list[dict], deltas: dict, prior_path: Path | None,
                    iso_week: str) -> str:
    now = datetime.now(timezone.utc)
    lines: list[str] = []
    lines.append("---")
    lines.append(f"name: Continuous-eval rollup {iso_week}")
    lines.append("type: audit")
    lines.append(f"created: {now.strftime('%Y-%m-%dT%H:%M:%S%z')}")
    lines.append('tags: ["#type/audit", "#project/sv", "continuous-eval", "weekly-rollup"]')
    lines.append("generated_by: vault-continuous-eval")
    lines.append("---")
    lines.append("")
    lines.append(f"# Continuous-eval rollup {iso_week}")
    lines.append("")
    lines.append(
        f"> Weekly health snapshot across **{len(axes)} eval axes**. Auto-generated by "
        f"`vault-continuous-eval` at {now.strftime('%Y-%m-%dT%H:%M:%S%z')}."
    )
    lines.append("")

    # Headline status
    counts = {}
    for ax in axes:
        s = ax["status"]
        counts[s] = counts.get(s, 0) + 1
    headline_bits = []
    for status in ("alert", "warn", "stale", "ok", "missing"):
        n = counts.get(status, 0)
        if n:
            headline_bits.append(f"{STATUS_ICON[status]} {n} {status}")
    lines.append("## Health summary")
    lines.append("")
    lines.append(" · ".join(headline_bits))
    lines.append("")

    # Per-axis table
    lines.append("| Status | Axis | Key metrics | Δ vs prior | Source |")
    lines.append("|---|---|---|---|---|")
    for ax in axes:
        icon = STATUS_ICON.get(ax["status"], "?")
        name = ax["axis"]
        metrics = ax.get("key_metrics") or {}
        metric_strs = []
        for k, v in metrics.items():
            if isinstance(v, float):
                metric_strs.append(f"`{k}`: **{v:.4f}**" if abs(v) < 10
                                   else f"`{k}`: **{v:.2f}**")
            else:
                metric_strs.append(f"`{k}`: **{v}**")
        metric_disp = "<br>".join(metric_strs) if metric_strs else "—"

        d = deltas.get(name, {})
        if d:
            delta_bits = []
            for k, v in d.items():
                sign = "+" if v > 0 else ""
                if abs(v) < 0.001:
                    delta_bits.append(f"`{k}`: ≈0")
                elif abs(v) < 10:
                    delta_bits.append(f"`{k}`: {sign}{v:.4f}")
                else:
                    delta_bits.append(f"`{k}`: {sign}{v:.2f}")
            delta_disp = "<br>".join(delta_bits)
        else:
            delta_disp = "—"

        src = ax.get("source", "")
        if src:
            try:
                src_rel = Path(src).relative_to(VAULT_ROOT)
                src_disp = f"`{src_rel}`"
            except (ValueError, TypeError):
                src_disp = f"`{src}`"
        else:
            src_disp = "—"

        lines.append(f"| {icon} | {name} | {metric_disp} | {delta_disp} | {src_disp} |")
    lines.append("")

    # Status legend
    lines.append("**Legend:** "
                 "🟢 ok · 🟡 warn (mild drift / threshold near) · "
                 "🔴 alert (threshold crossed / investigation needed) · "
                 "⏳ stale (audit data >14d old) · ⚪ missing (no audit found)")
    lines.append("")

    # Prior reference
    if prior_path:
        try:
            prior_rel = prior_path.relative_to(VAULT_ROOT)
            lines.append(f"_Δ computed vs prior rollup `{prior_rel}`._")
        except ValueError:
            lines.append(f"_Δ computed vs prior rollup `{prior_path}`._")
        lines.append("")

    # Drift findings (anything moved beyond threshold)
    lines.append("## Drift detection")
    lines.append("")
    drift_rows = []
    for axis_name, ds in deltas.items():
        for metric, delta in ds.items():
            # Heuristic threshold: 5% absolute for fractional metrics, 10% for counts
            if abs(delta) < 0.001:
                continue
            row_type = "🟢"
            if abs(delta) >= 0.05 and "rate" in metric.lower():
                row_type = "🟡"
            if abs(delta) >= 0.10 and metric not in ("CD",):
                row_type = "🔴"
            if metric.startswith("HIGH") and delta > 0:
                row_type = "🔴"
            drift_rows.append((row_type, axis_name, metric, delta))
    if drift_rows:
        lines.append("| Heat | Axis | Metric | Δ |")
        lines.append("|---|---|---|---:|")
        for r in drift_rows:
            sign = "+" if r[3] > 0 else ""
            lines.append(f"| {r[0]} | {r[1]} | `{r[2]}` | {sign}{r[3]:.4f} |")
    else:
        lines.append("_No drift detected (no metric moved beyond noise threshold)._")
    lines.append("")

    # Machine-readable snapshot
    lines.append("## Machine-readable snapshot")
    lines.append("")
    lines.append("```json")
    snapshot = {
        "generated_at": now.isoformat(),
        "iso_week": iso_week,
        "axes": axes,
        "counts": counts,
    }
    lines.append(json.dumps(snapshot, indent=2, default=str, ensure_ascii=False))
    lines.append("```")
    lines.append("")

    lines.append("## Related")
    lines.append("")
    lines.append("- [[../11-wiki/sv-07-continuous-evaluation]] — B-3 axis (continuous evaluation)")
    lines.append("- [[../11-wiki/auto-disable-min-volume-guard]] — alert-threshold-design")
    lines.append("- [[plugin-hooks-audit-" + iso_week + "]] — companion (run via separate cron)")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Weekly rollup of all per-axis eval audits"
    )
    ap.add_argument("--json", action="store_true",
                    help="emit JSON snapshot to stdout instead of writing the audit")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any axis is in 'alert' status")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress stdout summary line")
    args = ap.parse_args()

    axes = [reader() for reader in READERS]

    now = datetime.now(timezone.utc)
    iso_week = now.strftime("%G-W%V")

    prior_path = find_prior_rollup()
    prior = parse_prior_metrics(prior_path) if prior_path else {}
    deltas = compute_deltas(axes, prior)

    if args.json:
        print(json.dumps({
            "iso_week": iso_week,
            "axes": axes,
            "deltas": deltas,
        }, indent=2, default=str, ensure_ascii=False))
    else:
        md = render_markdown(axes, deltas, prior_path, iso_week)
        out_path = AUDITS_DIR / f"continuous-eval-{iso_week}.md"
        atomic_write(out_path, md)
        if not args.quiet:
            counts = {}
            for ax in axes:
                counts[ax["status"]] = counts.get(ax["status"], 0) + 1
            bits = [f"{STATUS_ICON[s]} {n}" for s, n in counts.items()]
            print("  " + " · ".join(bits))
            print(f"✓ Rollup written: {out_path}")

    if args.strict:
        if any(ax["status"] == "alert" for ax in axes):
            print("⚠ STRICT mode: at least one axis in alert state", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
