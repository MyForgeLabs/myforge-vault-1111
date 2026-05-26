#!/usr/bin/env python3
"""
vault — unified umbrella CLI for the ~80 vault-* tools.

Day-0 skeleton: discoverability dispatcher with category-grouped help.
Wraps existing `/usr/local/bin/vault-*` binaries transparently.

Usage:
  vault                       List all categories
  vault <category>            List tools in a category
  vault <category> <name>     Run a specific tool (forwards all args)
  vault search "query"        Shortcut for `vault search "query"` → vault-search
  vault help <pattern>        Search tool descriptions for <pattern>
  vault stats                 Print quick health-rollup (continuous-eval --json)

Examples:
  vault audit                 # list audit-CLIs (conflicts, plugin-hooks, mcp, schema-migration, ...)
  vault audit conflicts       # → vault-ko-conflicts-audit
  vault graph                 # list graph tools
  vault graph extract --reset # → vault-graph-extract --reset
  vault help "broken"         # find anything matching "broken"

Wiki: 11-wiki/vault-umbrella-cli.md (to-be-written)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

BIN_DIR = Path("/usr/local/bin")
PREFIX = "vault-"

# ── Category map ────────────────────────────────────────────────────────────
# Each category maps to a list of (subcommand, full-tool-name, one-line-desc).
# Adding a new tool? Just add a vault-<name> binary; if you want it grouped,
# add a row here. Otherwise it lands in the auto-generated "other" category.
CATEGORIES: dict[str, list[tuple[str, str, str]]] = {
    "ko": [
        ("ingest",       "vault-ko-ingest",        "ingest facts from a session/file (subagent-fanout)"),
        ("query",        "vault-ko-query",         "search KO-DB by subject/predicate/object/provenance"),
        ("report",       "vault-ko-report",        "user-facing audit-log summary (last/week/session)"),
        ("anki",         "vault-ko-anki",          "export KO-DB facts to Anki flashcards"),
        ("belief",       "vault-ko-belief",        "Bayesian belief-update for facts (manual)"),
        ("belief-weekly","vault-ko-belief-weekly", "weekly belief-update cron entry"),
        ("conflicts",    "vault-ko-conflicts-audit","heat-classified cross-source contradictions"),
        ("decay",        "vault-ko-decay",         "confidence-decay sweep for stale facts"),
        ("normalize",    "vault-ko-normalize",     "predicate / object normalization sweeps"),
        ("pending",      "vault-ko-pending",       "2-phase pending-file process (idempotent)"),
        ("remap-legacy", "vault-ko-remap-legacy",  "legacy predicate remap (Phase 1/2 fanout)"),
        ("schema-evolve","vault-ko-schema-evolve", "schema-migration helper (post-#34 generation)"),
        ("temporal",     "vault-ko-temporal",      "temporal-axis queries (fact validity by date)"),
        ("triangulate",  "vault-ko-triangulate",   "cross-source triangulation for ambiguous facts"),
    ],
    "graph": [
        ("extract",        "vault-graph-extract",         "KO-DB → Memgraph entity/relation extract (subagent)"),
        ("query",          "vault-graph-query",           "Memgraph Cypher query helper"),
        ("retype",         "vault-graph-retype",          "typed-label classifier (concept/decision/sprint/...)"),
        ("diff",           "vault-graph-diff",            "Jaccard label-overlap (legacy, kept for reference)"),
        ("complementarity","vault-graph-complementarity", "FCA / CD / XR two-tier complementarity metrics"),
        ("edge-inference", "vault-graph-edge-inference",  "edge-inference from KO-DB facts"),
        ("edge-from-facts","vault-graph-edge-from-facts", "Memgraph edge-population from facts"),
        ("mentions",       "vault-graph-mentions-extract","wikilink → :MENTIONS edges (Tier-1B)"),
        ("lazy-cleanup",   "vault-graph-lazy-concept-cleanup", "lazy concept-cleanup sweep"),
    ],
    "search": [
        ("",         "vault-search",         "semantic search (Memgraph + bge-m3 hybrid)"),
        ("fusion",   "vault-search-fusion",  "RRF hybrid: vault-search + agentmemory (production-default)"),
        ("health",   "vault-search-health",  "search-pipeline health-check"),
        ("rewrite",  "vault-search-rewrite", "query-rewrite for ambiguous searches"),
        ("server",   "vault-search-server",  "HTTP server wrapper for vault-search"),
    ],
    "audit": [
        ("doctor",          "vault-doctor",                        "unified vault health-check dashboard (one-stop)"),
        ("bench",           "vault-bench",                         "5-route retrieval latency benchmark"),
        ("plugin-discover", "vault-plugin-discover",               "third-party vault-* binary discovery"),
        ("plugin-safety",   "vault-plugin-safety-scan",            "third-party vault-* binary static-grep safety scan"),
        ("plugin-hooks",    "vault-plugin-hooks-audit",            "marketplace plugin instruction-injection scan"),
        ("mcp",             "vault-mcp-audit",                     "MCP server registration safety scan"),
        ("schema-migration","vault-schema-migration-victim-audit", "post-#34 schema-migration downstream-grep"),
        ("conflicts",       "vault-ko-conflicts-audit",            "cross-source contradiction (alias of ko conflicts)"),
        ("continuous",      "vault-continuous-eval",               "weekly rollup of all per-axis audits"),
        ("orphan-wiki",     "vault-orphan-wiki",                   "find wiki files with no inbound links"),
        ("broken-wikilinks","vault-broken-wikilinks-audit",        "broken-wikilink scanner"),
        ("adr-aging",       "vault-adr-aging-watch",               "ADR drift / age tracker"),
        ("atomic-lint",     "vault-atomic-lint",                   "vault_atomic.atomic_write usage lint"),
        ("auto-disable",    "vault-auto-disable-check",            "auto-disable min-volume guard check"),
        ("coherence",       "vault-coherence-check",               "session-coherence Layer-2.6 audit"),
    ],
    "embed": [
        ("",             "vault-embed",            "bge-m3 multilingual embed backfill"),
        ("freshness",    "vault-embed-freshness",  "embed staleness audit"),
        ("entity-link",  "vault-entity-link",      "entity-link extraction"),
        ("entity-trace", "vault-entity-trace",     "entity provenance tracer"),
        ("colbert",      "vault-colbert-fallback", "ColBERT late-interaction fallback (deferred)"),
        ("bm25",         "vault-bm25-backfill",    "BM25 fallback index backfill"),
    ],
    "crystallize": [
        ("monitor",       "vault-crystallize-monitor",  "pipeline health + shadow-window monitoring"),
        ("supersede-mon", "vault-scd2-supersession-monitor", "SCD2 supersession tracker"),
    ],
    "session": [
        ("daily-rollup",        "vault-daily-rollup",        "daily-note extractive rollup (cron)"),
        ("eval-backfill",       "vault-session-eval-backfill","session-eval backfill"),
        ("eval-run",            "vault-session-eval-run",    "session-eval one-shot run"),
        ("memory-monitor",      "vault-memory-monitor",      "vault-memory subsystem health"),
        ("sleep-consolidate",   "vault-sleep-consolidate",   "sleep-consolidate (memory consolidation)"),
        ("stuck-detect",        "vault-stuck-detect",        "find stuck/blocked sessions"),
    ],
    "skill": [
        ("distill",  "vault-skill-distill", "skill-distillation pipeline"),
        ("search",   "vault-skill-search",  "skill-search index"),
    ],
    "wiki": [
        ("quality-score",     "vault-wiki-quality-score",     "wiki quality scoring"),
        ("orphan",            "vault-orphan-wiki",            "orphan-wiki detector (alias of audit orphan-wiki)"),
        ("broken-wikilinks",  "vault-broken-wikilinks-audit", "broken-wikilink scanner (alias)"),
        ("tag-backfill",      "vault-tag-backfill",           "tag-taxonomy backfill"),
        ("link-importer",     "vault-wikilink-importer",      "wikilink-importer (Tier-1A)"),
    ],
    "nb": [
        ("ingest",        "vault-nb-ingest",       "NotebookLM ingest"),
        ("crystallize",   "vault-nb-crystallize",  "NotebookLM crystallize"),
        ("meta-push",     "vault-nb-meta-push",    "NotebookLM metadata push"),
    ],
    "net": [
        ("ingest",  "vault-net-ingest", "external URL/repo ingest (firecrawl / gh clone)"),
        ("watch",   "vault-net-watch",  "watch external URLs for drift"),
    ],
    "infra": [
        ("autosave",            "vault-autosave",             "10-min auto-save cron (git commit + push)"),
        ("cleanup",             "vault-cleanup",              "weekly vault-cleanup (broken-links, lint, ...)"),
        ("public-sync",         "vault-public-sync",          "live-vault → public-repo sync"),
        ("cron-flock",          "vault-cron-flock",           "flock-mutex helper for cron entries"),
        ("detect-chat-id",      "vault-detect-chat-id",       "per-chat session-ID auto-detect"),
        ("core-memory",         "vault-core-memory",          "core-memory layer (B-2)"),
        ("stats-generator",     "vault-stats-generator",      "vault-stats.json generator"),
        ("vector-index-migrate","vault-vector-index-migrate", "Memgraph vector-index migration helper"),
        ("cost-rollup",         "vault-cost-rollup",          "LLM API-cost rollup"),
        ("route",               "vault-route",                "session-routing helper"),
        ("multi-hop",           "vault-multi-hop",            "multi-hop graph traversal"),
        ("selfcheck",           "vault-selfcheck",            "vault-toolkit self-check"),
        ("gh-bridge",           "vault-gh-bridge",            "GitHub bridge"),
        ("github-trending",     "vault-github-trending-recurrence", "GitHub trending recurrence detector"),
        ("browser-history",     "vault-browser-history-ingest","browser-history ingest"),
        ("image-batch",         "vault-image-batch",          "image batch-processing"),
        ("explain",             "vault-explain",              "explain a vault concept"),
        ("eval-regression",     "vault-eval-regression",      "LongMemEval-S regression gate"),
    ],
}


def list_categories() -> None:
    """Print all categories with tool count."""
    print("vault — unified umbrella for ~80 vault-* tools")
    print()
    print("Categories:")
    for cat, items in CATEGORIES.items():
        print(f"  {cat:<14}  {len(items):>3} tool(s)")
    print()
    auto = _auto_categorized()
    if auto:
        print(f"  (other)        {len(auto):>3} uncategorized — see `vault other`")
    print()
    print("Usage:")
    print("  vault <category>             list tools in a category")
    print("  vault <category> <sub>       run a tool (forwards args)")
    print("  vault help <pattern>         find tools matching a pattern")
    print("  vault stats                  weekly health snapshot")


def _auto_categorized() -> list[str]:
    """vault-* binaries on PATH that aren't in any category map."""
    known: set[str] = set()
    for items in CATEGORIES.values():
        for _, full, _ in items:
            known.add(full)
    found: list[str] = []
    if not BIN_DIR.exists():
        return found
    for f in BIN_DIR.iterdir():
        if f.name.startswith(PREFIX) and f.name not in known:
            # Skip our own dispatcher binary if installed
            if f.name == "vault":
                continue
            found.append(f.name)
    return sorted(found)


def list_category(cat: str) -> None:
    if cat == "other":
        items = _auto_categorized()
        print(f"vault other — {len(items)} uncategorized tool(s):")
        for f in items:
            print(f"  {f}")
        print()
        print("Add to CATEGORIES in vault.py to group them.")
        return
    if cat not in CATEGORIES:
        print(f"⚠ unknown category: {cat}", file=sys.stderr)
        print(f"  known: {', '.join(CATEGORIES)}", file=sys.stderr)
        sys.exit(2)
    items = CATEGORIES[cat]
    print(f"vault {cat} — {len(items)} tool(s):")
    print()
    for sub, full, desc in items:
        sub_disp = sub if sub else "(default)"
        print(f"  vault {cat:<10} {sub_disp:<22}  {desc}")
        print(f"  {'':<10} {'':<29} → {full}")
    print()
    print(f"Run any of them with: vault {cat} <sub> [args...]")


def dispatch(cat: str, sub: str, rest: list[str]) -> int:
    """Resolve `vault <cat> <sub>` to the full vault-* binary and exec it."""
    if cat not in CATEGORIES:
        # Fallback: maybe user meant `vault <cat>` with the cat being a tool-suffix
        # e.g. `vault search "query"` should map to vault-search.
        candidate = BIN_DIR / f"vault-{cat}"
        if candidate.is_file():
            args = [sub] + rest if sub else rest
            return subprocess.run([str(candidate)] + args).returncode
        print(f"⚠ unknown category: {cat}", file=sys.stderr)
        return 2
    items = CATEGORIES[cat]
    # Find by sub (exact match), or by full-name suffix match
    for s, full, _ in items:
        if s == sub:
            bin_path = BIN_DIR / full
            if not bin_path.is_file():
                print(f"⚠ binary not found: {bin_path}", file=sys.stderr)
                return 127
            return subprocess.run([str(bin_path)] + rest).returncode
    # If category has a "" default-entry AND `sub` isn't a known sub-command,
    # treat `sub` as the first arg to the default binary.
    for s, full, _ in items:
        if s == "":
            bin_path = BIN_DIR / full
            if bin_path.is_file():
                args = ([sub] if sub else []) + rest
                return subprocess.run([str(bin_path)] + args).returncode
    print(f"⚠ unknown sub-command: vault {cat} {sub}", file=sys.stderr)
    print(f"  available: {', '.join(s or '(default)' for s, _, _ in items)}", file=sys.stderr)
    return 2


def help_search(pattern: str) -> None:
    """Search all tool descriptions + names for a pattern."""
    pat = re.compile(pattern, re.IGNORECASE)
    hits: list[tuple[str, str, str]] = []
    for cat, items in CATEGORIES.items():
        for sub, full, desc in items:
            blob = f"{cat} {sub} {full} {desc}"
            if pat.search(blob):
                hits.append((cat, sub or "(default)", desc))
    auto = _auto_categorized()
    for full in auto:
        if pat.search(full):
            hits.append(("other", full.removeprefix(PREFIX), "(uncategorized)"))
    if not hits:
        print(f"no tools matched: /{pattern}/", file=sys.stderr)
        sys.exit(1)
    print(f"vault help — {len(hits)} match(es) for /{pattern}/:")
    print()
    for cat, sub, desc in hits:
        print(f"  vault {cat:<10} {sub:<22}  {desc}")


def stats() -> int:
    """Print a quick health snapshot (continuous-eval JSON, parsed)."""
    bin_path = BIN_DIR / "vault-continuous-eval"
    if not bin_path.is_file():
        print("⚠ vault-continuous-eval not on PATH", file=sys.stderr)
        return 127
    return subprocess.run([str(bin_path)]).returncode


def complete(args: list[str]) -> int:
    """Machine-readable output for bash-completion.

    `vault --complete categories`  → flat list of cat names + help, stats, other
    `vault --complete subs <cat>`  → flat list of sub-commands in <cat>
    """
    if not args:
        return 2
    mode = args[0]
    if mode == "categories":
        for cat in CATEGORIES:
            print(cat)
        print("help")
        print("stats")
        if _auto_categorized():
            print("other")
        return 0
    if mode == "subs" and len(args) >= 2:
        cat = args[1]
        if cat == "other":
            for f in _auto_categorized():
                print(f.removeprefix(PREFIX))
            return 0
        if cat not in CATEGORIES:
            return 2
        for sub, _full, _desc in CATEGORIES[cat]:
            if sub:
                print(sub)
        return 0
    return 2


def main() -> int:
    if len(sys.argv) == 1:
        list_categories()
        return 0
    cmd = sys.argv[1]
    if cmd == "--complete":
        return complete(sys.argv[2:])
    if cmd in ("-h", "--help", "help"):
        if len(sys.argv) > 2:
            help_search(sys.argv[2])
            return 0
        list_categories()
        return 0
    if cmd == "stats":
        return stats()
    if cmd in CATEGORIES or cmd == "other":
        if len(sys.argv) == 2:
            list_category(cmd)
            return 0
        sub = sys.argv[2]
        rest = sys.argv[3:]
        return dispatch(cmd, sub, rest)
    # Fallback to dispatch with empty sub (allows `vault search "query"`)
    rest = sys.argv[2:]
    return dispatch(cmd, "", rest)


if __name__ == "__main__":
    sys.exit(main())
