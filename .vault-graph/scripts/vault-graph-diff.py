#!/usr/bin/env python3
"""vault-graph-diff — two-tier graph cross-validation: graphify (Tier-2) ↔ Memgraph (Tier-1).

Brainstorm idea #18 from `06-Audits/2026-05-19 SV new development ideas brainstorm.md`.

The vault maintains TWO graph extractions:
  - **Tier-1 (LLM-extracted)** — Memgraph 12.7K `Entity` nodes from
    subagent-fanout extraction over vault content. Captures semantic
    entities ("MAPESZ", "Karpathy LLM-Wiki pattern", "G-Eval scorer").
  - **Tier-2 (deterministic)** — graphify 5.8K nodes via tree-sitter +
    Leiden community detection. Captures syntactic / structural entities
    (function names, file references, code-symbols).

These should LARGELY agree on the "things that matter". A diff between
them yields three signals:

  - **Tier-1 only**: LLM-detected entity that no deterministic parse
    matches. Could be: (a) a real semantic concept above the syntax layer
    (legitimate), (b) an LLM hallucination (review needed).
  - **Tier-2 only**: structural node not promoted to a semantic entity.
    Could be: (a) low-level technical detail (correct exclusion), (b)
    coverage gap in the LLM extraction (worth ingesting).
  - **Both**: high-confidence "real" entities.

Two-tier cross-validation is a 2026 emerging pattern from the GraphRAG
literature (Microsoft + Graphwise blog posts). This CLI makes the diff
audit-able weekly.

Usage:
  vault-graph-diff                         # full report (markdown)
  vault-graph-diff --json
  vault-graph-diff --tier-1-only --top 50  # potential LLM hallucinations
  vault-graph-diff --tier-2-only --top 50  # coverage gaps
  vault-graph-diff --write-audit           # save to 06-Audits/
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
from vault_atomic import atomic_write  # noqa: E402

VAULT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
GRAPHIFY_JSON = VAULT / "graphify-out" / "graph.json"
AUDITS_DIR = VAULT / "06-Audits"
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))


def normalize(name: str) -> str:
    """Lowercase + collapse whitespace + strip punctuation for comparison."""
    s = name.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s.-]", "", s)
    return s


# ── Loaders ────────────────────────────────────────────────────────────────


def load_tier2() -> dict[str, set[str]]:
    """Return {normalized_label: set(original labels)} from graphify."""
    if not GRAPHIFY_JSON.exists():
        return {}
    g = json.loads(GRAPHIFY_JSON.read_text(encoding="utf-8"))
    nodes = g.get("nodes") or []
    out: dict[str, set[str]] = {}
    for n in nodes:
        label = n.get("label") or n.get("norm_label")
        if not label:
            continue
        norm = normalize(label)
        if not norm:
            continue
        out.setdefault(norm, set()).add(label)
    return out


def load_tier1() -> dict[str, set[str]]:
    """Return {normalized_name: set(original entity names)} from Memgraph."""
    try:
        import mgclient
        conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    except Exception as e:
        print(f"  ⚠ Memgraph unreachable: {e}", file=sys.stderr)
        return {}
    cur = conn.cursor()
    try:
        cur.execute("MATCH (e:Entity) RETURN e.name")
        rows = cur.fetchall()
    finally:
        conn.close()
    out: dict[str, set[str]] = {}
    for (name,) in rows:
        if not name:
            continue
        norm = normalize(name)
        if not norm:
            continue
        out.setdefault(norm, set()).add(name)
    return out


# ── Diff ───────────────────────────────────────────────────────────────────


def compute_diff(t1: dict, t2: dict) -> dict:
    t1_keys = set(t1)
    t2_keys = set(t2)
    both = t1_keys & t2_keys
    t1_only = t1_keys - t2_keys
    t2_only = t2_keys - t1_keys
    return {
        "tier1_total": len(t1_keys),
        "tier2_total": len(t2_keys),
        "both": len(both),
        "tier1_only": len(t1_only),
        "tier2_only": len(t2_only),
        "agreement_rate": (
            round(len(both) / max(1, len(t1_keys | t2_keys)), 4)
        ),
        "tier1_only_labels": sorted(
            {next(iter(t1[k])) for k in t1_only}
        )[:200],
        "tier2_only_labels": sorted(
            {next(iter(t2[k])) for k in t2_only}
        )[:200],
        "both_labels_sample": sorted(
            {next(iter(t1[k])) for k in both}
        )[:30],
    }


# ── Heuristic classifier for the "diff" rows ──────────────────────────────


def classify_tier1_only(label: str) -> str:
    """Best-guess: legitimate-semantic vs LLM-hallucination."""
    low = label.lower()
    if len(label) < 4:
        return "short-token"  # likely noise
    if any(t in low for t in ("?", "...", "etc", "stb")):
        return "fragment"
    if low.count(" ") >= 4:
        return "phrase-like"  # multi-word — typical LLM concept
    return "name-like"


def classify_tier2_only(label: str) -> str:
    """Best-guess: structural detail vs missed-concept."""
    low = label.lower()
    if any(low.endswith(ext) for ext in (".py", ".js", ".ts", ".md", ".sh", ".json")):
        return "file-ref"
    if "/" in label or "\\" in label:
        return "path-ref"
    if any(low.startswith(p) for p in ("def ", "class ", "function ")):
        return "code-symbol"
    if low.count("_") >= 2 and " " not in label:
        return "snake_case-ident"
    return "concept-like"


# ── Report ─────────────────────────────────────────────────────────────────


def render_markdown(diff: dict, t1: dict, t2: dict) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    lines = [
        f"---",
        f"name: graph-diff {now.strftime('%Y-%m-%d')}",
        f"type: audit",
        f"created: {now.strftime('%Y-%m-%d')}",
        f"updated: {now.strftime('%Y-%m-%d')}",
        f"tags: [\"#type/audit\", \"#project/sv\", \"two-tier-graph\"]",
        f"---",
        f"",
        f"# graphify × Memgraph diff — {now.strftime('%Y-%m-%d %H:%M')} UTC",
        f"",
        f"Two-tier graph cross-validation: deterministic graphify (tree-sitter +",
        f"Leiden) vs LLM-extracted Memgraph entity-graph.",
        f"",
        f"## Aggregate",
        f"",
        f"| | Count |",
        f"|---|---:|",
        f"| Tier-1 (Memgraph LLM) | **{diff['tier1_total']:,}** unique entities |",
        f"| Tier-2 (graphify deterministic) | **{diff['tier2_total']:,}** unique nodes |",
        f"| Agreement (both) | **{diff['both']:,}** |",
        f"| Tier-1 only | **{diff['tier1_only']:,}** |",
        f"| Tier-2 only | **{diff['tier2_only']:,}** |",
        f"| Jaccard agreement | **{diff['agreement_rate']:.4f}** |",
        f"",
        f"## Tier-1 only (potential LLM signals — semantic concepts above syntax)",
        f"",
        f"_These appear in the LLM-extracted graph but NOT in the deterministic",
        f"parse. Most are legitimate semantic-level concepts; some may be",
        f"hallucinated. Review pattern: high-noise = `fragment` / `short-token`._",
        f"",
    ]
    # Classify Tier-1-only
    t1_by_class: dict[str, list[str]] = {}
    for label in diff["tier1_only_labels"]:
        cls = classify_tier1_only(label)
        t1_by_class.setdefault(cls, []).append(label)
    for cls in ("phrase-like", "name-like", "short-token", "fragment"):
        items = t1_by_class.get(cls, [])
        if not items:
            continue
        lines.append(f"### `{cls}` ({len(items)})")
        lines.append("")
        for it in items[:30]:
            lines.append(f"- `{it}`")
        if len(items) > 30:
            lines.append(f"- _({len(items) - 30} more)_")
        lines.append("")

    lines.append("## Tier-2 only (coverage gaps — structural nodes not yet semantic)")
    lines.append("")
    lines.append("_These are deterministic structural nodes — file paths, code")
    lines.append("symbols, snake_case identifiers — that the LLM extraction")
    lines.append("excluded. Pattern: `concept-like` may warrant promotion._")
    lines.append("")
    t2_by_class: dict[str, list[str]] = {}
    for label in diff["tier2_only_labels"]:
        cls = classify_tier2_only(label)
        t2_by_class.setdefault(cls, []).append(label)
    for cls in ("concept-like", "file-ref", "snake_case-ident", "path-ref", "code-symbol"):
        items = t2_by_class.get(cls, [])
        if not items:
            continue
        lines.append(f"### `{cls}` ({len(items)})")
        lines.append("")
        for it in items[:30]:
            lines.append(f"- `{it}`")
        if len(items) > 30:
            lines.append(f"- _({len(items) - 30} more)_")
        lines.append("")

    lines.append("## Both (high-confidence cross-validated)")
    lines.append("")
    for it in diff["both_labels_sample"][:30]:
        lines.append(f"- `{it}`")
    lines.append("")
    lines.append(f"_Sample of {len(diff['both_labels_sample'])}/{diff['both']} agreement entities._")
    return "\n".join(lines) + "\n"


# ── Main ───────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(
        prog="vault-graph-diff",
        description="Two-tier graphify × Memgraph cross-validation diff.",
    )
    ap.add_argument("--tier-1-only", action="store_true",
                    help="show only Memgraph-only entities (LLM signals)")
    ap.add_argument("--tier-2-only", action="store_true",
                    help="show only graphify-only nodes (coverage gaps)")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-audit", action="store_true",
                    help="save markdown report to 06-Audits/")
    ap.add_argument("--complementarity", action="store_true",
                    help="run vault-graph-complementarity instead (file-level "
                         "FCA/CD/XR metrics — the principled replacement for "
                         "Jaccard label-overlap, ADR 2026-05-20)")
    args = ap.parse_args()

    if args.complementarity:
        # Delegate to the complementarity CLI — pass through --json/--write-audit
        import subprocess
        cmd = ["/usr/local/bin/vault-graph-complementarity"]
        if args.json:
            cmd.append("--json")
        if args.write_audit:
            cmd.append("--write-audit")
        sys.exit(subprocess.call(cmd))

    t1 = load_tier1()
    t2 = load_tier2()

    if not t1 and not t2:
        print("Both graphs empty — Memgraph unreachable AND graphify-out missing.",
              file=sys.stderr)
        return 1

    diff = compute_diff(t1, t2)

    if args.tier_1_only:
        labels = diff["tier1_only_labels"][:args.top]
        if args.json:
            print(json.dumps({"tier_1_only": labels,
                              "total": diff["tier1_only"]}, indent=2,
                             ensure_ascii=False))
        else:
            print(f"\nTier-1 only ({diff['tier1_only']:,}, "
                  f"showing top {args.top}):\n")
            for it in labels:
                cls = classify_tier1_only(it)
                print(f"  [{cls:<14s}] {it}")
        return 0

    if args.tier_2_only:
        labels = diff["tier2_only_labels"][:args.top]
        if args.json:
            print(json.dumps({"tier_2_only": labels,
                              "total": diff["tier2_only"]}, indent=2,
                             ensure_ascii=False))
        else:
            print(f"\nTier-2 only ({diff['tier2_only']:,}, "
                  f"showing top {args.top}):\n")
            for it in labels:
                cls = classify_tier2_only(it)
                print(f"  [{cls:<14s}] {it}")
        return 0

    if args.json:
        print(json.dumps(diff, indent=2, ensure_ascii=False))
        return 0

    md = render_markdown(diff, t1, t2)
    if args.write_audit:
        out_path = AUDITS_DIR / f"graph-diff-{dt.date.today().isoformat()}.md"
        atomic_write(out_path, md)
        print(f"wrote {out_path.relative_to(VAULT)}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
