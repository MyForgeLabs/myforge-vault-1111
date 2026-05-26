#!/usr/bin/env python3
"""
vault-graph-complementarity — measure two-tier extractor agreement via
complementarity metrics (NOT Jaccard label-overlap).

ADR (proposed): 07-Decisions/2026-05-20 Two-tier complementarity over Jaccard.md
Audit: 06-Audits/2026-05-20 Option-B premise empirical refutation ...md

The two-tier extraction stack:
  - Tier-1 (KO-DB → Memgraph): LLM-extracted narrative concepts, with
    per-fact provenance (fact_provenance.provenance = vault-relative path).
  - Tier-2 (graphify-out/graph.json): tree-sitter + Leiden over markdown
    files, with per-node source_file (absolute /tmp/vault-content/... path).

The two vocabularies are by-design ORTHOGONAL (LLM concepts vs markdown-
section-paths). Jaccard label-overlap is a misformed proxy for "agreement"
between them. This CLI computes three honest complementarity metrics:

  1. FCA — File-Coverage Agreement
     % of files in the vault corpus that have ≥1 Tier-1 entity AND
     ≥1 Tier-2 node. Both systems "agree the file matters."

  2. CD — Co-occurrence Density
     For each file F:  min(t1_count[F], t2_count[F]) / max(t1_count[F], t2_count[F])
     Aggregated as mean over files where BOTH systems extract.

  3. XR — Cross-Reference Rate
     % of Tier-1 entities whose provenance file is also surfaced by Tier-2
     as ≥1 node (i.e. graphify "anchored" that file structurally).
     The mirror metric: % of Tier-2 source-files where Tier-1 extracted
     at least one entity ("file-pinning rate").

Usage:
  vault-graph-complementarity                  # markdown report
  vault-graph-complementarity --json
  vault-graph-complementarity --per-file       # file-by-file table
  vault-graph-complementarity --write-audit    # save to 06-Audits/
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
try:
    from vault_atomic import atomic_write  # noqa: E402
except ImportError:
    def atomic_write(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

VAULT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
KO_DB = VAULT / ".vault-ko" / "facts.db"
GRAPHIFY_JSON = VAULT / "graphify-out" / "graph.json"
GRAPHIFY_CONTENT_PREFIX = "/tmp/vault-content/"   # graphify's input dir
AUDITS_DIR = VAULT / "06-Audits"

# Default corpus-normalization rules. KO-DB ingest is markdown-only and
# explicitly skips vault-meta directories per AGENTS.md policy; the
# complementarity metric must measure both extractors over the SAME corpus.
DEFAULT_EXCLUDE_DIRS = ("00-Meta", "05-Memory")
DEFAULT_INCLUDE_SUFFIXES = (".md",)


def _is_excluded(rel_path: str, exclude_dirs: tuple[str, ...],
                 include_suffixes: tuple[str, ...]) -> bool:
    """Return True if rel_path should be dropped from the corpus."""
    for d in exclude_dirs:
        if rel_path.startswith(f"{d}/") or rel_path == d:
            return True
    if include_suffixes and not rel_path.endswith(include_suffixes):
        return True
    return False


# ── Loaders ────────────────────────────────────────────────────────────────


def load_tier1_per_file(exclude_dirs: tuple[str, ...] = DEFAULT_EXCLUDE_DIRS,
                        include_suffixes: tuple[str, ...] = DEFAULT_INCLUDE_SUFFIXES,
                        ) -> dict[str, set[str]]:
    """Return {provenance: set(subject)} from KO-DB.

    Each Tier-1 'entity' is a unique fact-subject. A subject may have many
    provenances; we count it once per provenance file. Vault-meta dirs and
    non-markdown files are excluded for corpus parity with Tier-2.
    """
    out: dict[str, set[str]] = {}
    conn = sqlite3.connect(KO_DB)
    cur = conn.execute(
        """
        SELECT fp.provenance, f.subject
        FROM   fact_provenance fp
        JOIN   facts f ON f.hash = fp.fact_hash
        """
    )
    for prov, subj in cur:
        if not prov or not subj:
            continue
        if _is_excluded(prov, exclude_dirs, include_suffixes):
            continue
        out.setdefault(prov, set()).add(subj)
    conn.close()
    return out


def load_tier2_per_file(exclude_dirs: tuple[str, ...] = DEFAULT_EXCLUDE_DIRS,
                        include_suffixes: tuple[str, ...] = DEFAULT_INCLUDE_SUFFIXES,
                        ) -> dict[str, set[str]]:
    """Return {vault_relative_path: set(label)} from graphify graph.json.

    graphify source_file paths are absolute (e.g. /tmp/vault-content/11-wiki/foo.md).
    We strip the GRAPHIFY_CONTENT_PREFIX to get vault-relative paths that match
    KO-DB's provenance format, then apply the same corpus filter as Tier-1.
    """
    if not GRAPHIFY_JSON.exists():
        return {}
    g = json.loads(GRAPHIFY_JSON.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}
    for n in g.get("nodes", []):
        sf = n.get("source_file")
        label = n.get("label") or n.get("norm_label")
        if not sf or not label:
            continue
        if sf.startswith(GRAPHIFY_CONTENT_PREFIX):
            sf = sf[len(GRAPHIFY_CONTENT_PREFIX):]
        if _is_excluded(sf, exclude_dirs, include_suffixes):
            continue
        out.setdefault(sf, set()).add(label)
    return out


# ── Metrics ────────────────────────────────────────────────────────────────


def compute_metrics(t1: dict[str, set[str]], t2: dict[str, set[str]]) -> dict:
    t1_files = set(t1)
    t2_files = set(t2)
    union_files = t1_files | t2_files
    both_files = t1_files & t2_files
    t1_only = t1_files - t2_files
    t2_only = t2_files - t1_files

    # Metric 1: File-Coverage Agreement
    fca = len(both_files) / max(1, len(union_files))

    # Metric 2: Co-occurrence Density (per-file proportion, averaged over BOTH)
    if both_files:
        ratios = []
        for f in both_files:
            n1 = len(t1[f])
            n2 = len(t2[f])
            if n1 == 0 or n2 == 0:
                continue
            ratios.append(min(n1, n2) / max(n1, n2))
        cd = sum(ratios) / len(ratios) if ratios else 0.0
    else:
        cd = 0.0

    # Metric 3: Cross-Reference Rate
    # Forward: % of Tier-1 entities whose provenance file is also in Tier-2
    t1_entities_anchored = 0
    t1_entities_total = 0
    for f, entities in t1.items():
        t1_entities_total += len(entities)
        if f in t2:
            t1_entities_anchored += len(entities)
    xr_t1 = t1_entities_anchored / max(1, t1_entities_total)

    # Mirror: % of Tier-2 nodes whose source file has ≥1 Tier-1 entity
    t2_nodes_pinned = 0
    t2_nodes_total = 0
    for f, nodes in t2.items():
        t2_nodes_total += len(nodes)
        if f in t1:
            t2_nodes_pinned += len(nodes)
    xr_t2 = t2_nodes_pinned / max(1, t2_nodes_total)

    return {
        "tier1_files": len(t1_files),
        "tier2_files": len(t2_files),
        "both_files": len(both_files),
        "tier1_only_files": len(t1_only),
        "tier2_only_files": len(t2_only),
        "union_files": len(union_files),
        "fca": round(fca, 4),
        "cd": round(cd, 4),
        "xr_t1": round(xr_t1, 4),
        "xr_t2": round(xr_t2, 4),
        "tier1_entities_total": sum(len(s) for s in t1.values()),
        "tier2_nodes_total": sum(len(s) for s in t2.values()),
        "tier1_entities_anchored": t1_entities_anchored,
        "tier2_nodes_pinned": t2_nodes_pinned,
    }


def per_file_table(t1: dict[str, set[str]], t2: dict[str, set[str]],
                   limit: int = 50) -> list[tuple[str, int, int, float]]:
    """Per-file (path, t1_count, t2_count, density)."""
    files = sorted(set(t1) | set(t2))
    rows = []
    for f in files:
        n1 = len(t1.get(f, set()))
        n2 = len(t2.get(f, set()))
        if n1 == 0 or n2 == 0:
            density = 0.0
        else:
            density = min(n1, n2) / max(n1, n2)
        rows.append((f, n1, n2, density))
    # Sort by total then density
    rows.sort(key=lambda r: (-(r[1] + r[2]), -r[3]))
    return rows[:limit]


# ── Rendering ──────────────────────────────────────────────────────────────


def render_markdown(metrics: dict, per_file: list, jaccard: float | None,
                    exclude_dirs: tuple[str, ...] = (),
                    include_suffixes: tuple[str, ...] = ()) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    lines = [
        "---",
        f"name: graph-complementarity {now.strftime('%Y-%m-%d')}",
        "type: audit",
        f"created: {now.strftime('%Y-%m-%d')}",
        f"updated: {now.strftime('%Y-%m-%d')}",
        'tags: ["#type/audit", "#project/sv", "two-tier-graph", "complementarity"]',
        "---",
        "",
        f"# Two-tier complementarity — {now.strftime('%Y-%m-%d %H:%M')} UTC",
        "",
        "Honest cross-validation between KO-DB Tier-1 (LLM-extracted narrative "
        "concepts) and graphify Tier-2 (markdown-section-path nodes). Jaccard "
        "label-overlap is a misformed proxy for orthogonal-vocabulary extractors; "
        "this report uses three complementarity metrics instead.",
        "",
        "## Corpus normalization",
        "",
        ("Both extractors are measured over the SAME file corpus. "
         "Files filtered uniformly from BOTH Tier-1 and Tier-2 before metrics:"),
        "",
        f"- excluded dirs: `{', '.join(exclude_dirs) if exclude_dirs else '(none)'}`",
        f"- included suffixes: `{', '.join(include_suffixes) if include_suffixes else '(any)'}`",
        "",
        "## Aggregate",
        "",
        "| Metric | Value | Interpretation |",
        "|---|---:|---|",
        f"| Tier-1 files (KO-DB provenance) | {metrics['tier1_files']:,} | files with ≥1 LLM entity |",
        f"| Tier-2 files (graphify source) | {metrics['tier2_files']:,} | files with ≥1 graphify node |",
        f"| Both | {metrics['both_files']:,} | files BOTH systems extracted from |",
        f"| Union | {metrics['union_files']:,} | files EITHER touched |",
        f"| **FCA** (file-coverage agreement) | **{metrics['fca']:.4f}** | both / union |",
        f"| **CD** (co-occurrence density) | **{metrics['cd']:.4f}** | mean min/max per file |",
        f"| **XR_T1** (cross-reference rate, forward) | **{metrics['xr_t1']:.4f}** | % of Tier-1 entities whose provenance file is also in Tier-2 |",
        f"| **XR_T2** (file-pinning rate, mirror) | **{metrics['xr_t2']:.4f}** | % of Tier-2 nodes whose source file is also in Tier-1 |",
        f"| Tier-1 total entities | {metrics['tier1_entities_total']:,} | sum across all files |",
        f"| Tier-2 total nodes | {metrics['tier2_nodes_total']:,} | sum across all files |",
    ]
    if jaccard is not None:
        lines.append(f"| Jaccard label-overlap (for context, *not* a target) | {jaccard:.4f} | misformed, see audit |")

    lines.extend([
        "",
        "## Reading guide",
        "",
        "- **FCA → 1.0** = both systems agree on which files matter. **FCA → 0** = "
        "they pick disjoint corpora (e.g. one indexes wikis, the other indexes "
        "sessions). Mid-range = partial overlap with structural reasons (one "
        "system skips certain dirs).",
        "- **CD → 1.0** = when both extract from a file, they produce similar "
        "entity-counts (proportional information density). **CD → 0** = one "
        "system extracts heavily where the other extracts lightly.",
        "- **XR_T1 → 1.0** = every LLM-extracted concept lives in a file that "
        "graphify also surfaces structurally (the LLM-extracted concept has a "
        "structural anchor). **XR_T2 → 1.0** = the reverse — graphify never "
        "indexes a file the LLM didn't also touch.",
        "",
        "Acceptance criteria (Sprint-2): FCA ≥ 0.50, CD ≥ 0.30, XR_T1 ≥ 0.80, "
        "XR_T2 ≥ 0.80. See ADR.",
        "",
        "## Top-50 per-file table",
        "",
        "| File | Tier-1 entities | Tier-2 nodes | Density |",
        "|---|---:|---:|---:|",
    ])
    for path, n1, n2, density in per_file:
        lines.append(f"| `{path}` | {n1} | {n2} | {density:.2f} |")

    lines.extend([
        "",
        "## Related",
        "",
        "- [[../07-Decisions/2026-05-20 Option-B tree-sitter pre-pass for Memgraph extraction]] — superseded",
        "- [[2026-05-20 Option-B premise empirical refutation — graphify vocabulary is markdown not code]] — empirical refutation",
        "- [[../11-wiki/two-tier-graph-extraction]] — pattern wiki",
        "",
    ])
    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Two-tier complementarity metrics for KO-DB ↔ graphify"
    )
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--per-file", action="store_true",
                    help="show per-file count table")
    ap.add_argument("--limit", type=int, default=50,
                    help="rows in per-file table (default 50)")
    ap.add_argument("--write-audit", action="store_true",
                    help="save markdown to 06-Audits/")
    ap.add_argument("--exclude-dir", action="append", default=None,
                    help=f"vault-relative dir to drop from BOTH corpora "
                         f"(repeatable; default: {', '.join(DEFAULT_EXCLUDE_DIRS)})")
    ap.add_argument("--include-suffix", action="append", default=None,
                    help=f"file suffix to keep in BOTH corpora "
                         f"(repeatable; default: {', '.join(DEFAULT_INCLUDE_SUFFIXES)}; "
                         f"pass empty string '' to disable suffix filter)")
    ap.add_argument("--no-corpus-normalize", action="store_true",
                    help="disable all corpus-normalization filters "
                         "(legacy baseline mode; FCA will reflect raw graphify output)")
    args = ap.parse_args()

    if args.no_corpus_normalize:
        exclude_dirs: tuple[str, ...] = ()
        include_suffixes: tuple[str, ...] = ()
    else:
        exclude_dirs = tuple(args.exclude_dir) if args.exclude_dir is not None else DEFAULT_EXCLUDE_DIRS
        if args.include_suffix is None:
            include_suffixes = DEFAULT_INCLUDE_SUFFIXES
        else:
            include_suffixes = tuple(s for s in args.include_suffix if s)

    t1 = load_tier1_per_file(exclude_dirs, include_suffixes)
    t2 = load_tier2_per_file(exclude_dirs, include_suffixes)
    if not t1:
        print("⚠ KO-DB has no fact_provenance rows", file=sys.stderr)
        return 1
    if not t2:
        print("⚠ graphify graph.json missing or empty", file=sys.stderr)
        return 1

    metrics = compute_metrics(t1, t2)
    rows = per_file_table(t1, t2, args.limit) if args.per_file or args.write_audit else []

    if args.json:
        out = dict(metrics)
        if rows:
            out["per_file_top"] = [
                {"file": r[0], "tier1": r[1], "tier2": r[2], "density": r[3]}
                for r in rows
            ]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    md = render_markdown(metrics, rows, None, exclude_dirs, include_suffixes)
    if args.write_audit:
        AUDITS_DIR.mkdir(parents=True, exist_ok=True)
        today = dt.date.today().isoformat()
        out_path = AUDITS_DIR / f"{today} two-tier complementarity baseline.md"
        atomic_write(out_path, md)
        print(f"✓ wrote {out_path}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
