---
name: Vault Knowledge Graph — Overview
type: wiki
lang: en
translated_from: vault-knowledge-graph-overview.md
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/reference", "#tech/memgraph"]
  - memgraph
  - graphify
  - viz
  - karpathy-llm-wiki
tag_backfill: 2026-05-19
---
# Vault Knowledge Graph — Overview

> [!info] Two complementary extraction layers
> The vault knowledge graph is **2-tier**: (1) **Memgraph LLM-extraction** (semantic entity-relation, 8997 entities / 6722 typed) and (2) **graphify deterministic tree-sitter + Leiden** (5846 nodes / 437 communities, content-filtered). The two layers validate each other — see [[two-tier-graph-extraction]].

## Live state (2026-05-18)

### Memgraph entity graph (Tier-1, LLM-extracted)

| Metric | Value |
|---|---|
| **Total entities** | 8,997 |
| **Typed entities** (≥1 label beyond `Entity`) | 6,722 (74.7%) |
| **Untyped** (only `Entity`) | 2,275 (25.3%) |
| **Alias edges** (`ALIAS_OF`) | 102 |
| **Top relation types** | `MENTIONS` 1,954 · `HAS_VALUE` 1,921 · `USES` 1,862 · `PRODUCES` 1,718 · `REQUIRES` 1,277 · `APPLIES_TO` 993 · `CAUSES` 688 |

### Label distribution (top-9 typed)

Concept 3,292 · SourceFile 663 · Skill 649 · Sprint 568 · Project 395 · Server 383 · Pattern 349 · Decision 105 · Person 31

> [!note] Multi-label combos
> 224 entities have 2-3 labels (e.g. `Skill+Project` 107, `Concept+Pattern` 52, `Sprint+Pattern` 17). The `labels(n)` set reflects domain overlap.

### graphify deterministic (Tier-2, tree-sitter + Leiden)

| Metric | Value |
|---|---|
| **Node count** (content-filtered) | 5,846 |
| **Edge count** | 5,479 |
| **Communities** (Leiden) | 437 |
| **Extraction time** | ~12 min · $0 cost |
| **Output** | `graphify-out/graph.html` (4.6 MB) + `graph.json` (4.3 MB) |

Graphify was content-filtered because the full vault (including `.obsidian/plugins/` and `10-raw/`) produced 18,102 nodes — an unreadable hairball.

## Top-10 hub entities (Memgraph degree rank)

| # | Name | Label(s) | Degree | Note |
|---:|---|---|---:|---|
| 1 | `extracted-search` | Project | 39 | PDF→search project |
| 2 | `rental-portal` | Project | 38 | Rental portal |
| 3 | `Phase B-8` | Sprint | 32 | Vault entity-graph cleanup |
| 4 | `11-wiki/Index.md` | SourceFile | 30 | Karpathy-wiki entry point |
| 5 | `SV-3` | Sprint | 28 | Subagent-fanout RSI sprint |
| 6 | `NotebookLM` | Skill | 26 | Deep-research toolchain |
| 7 | `subagent-fanout` | Concept | 24 | $0-cost bulk LLM-mutation pattern |
| 8 | `SV-8` | Sprint | 23 | Recursive self-improvement sprint |
| 9 | `Memgraph` | Server | 22 | Graph DB :7687 |
| 10 | `vault` | Entity | 22 | Untyped meta-hub (cleanup candidate) |

## Visualization forms

### A. Lightweight overview SVG
- Top-60 hubs + induced subgraph (11 internal edges — hub-and-spoke nature means most edges go to low-degree leaves)
- Fruchterman-Reingold force-directed layout, 250 iterations
- 14.6 KB total
- Label-colored by entity type; node size = `4 + 8 × √(deg / max_deg)`
- Labels only on top-30 hubs

### B. Interactive full graph (graphify-out reuse)
- `graph/index.html` (4.6 MB) reused directly
- 5,846 nodes + 5,479 edges + 437 color-coded communities
- UX: zoom, pan, node-search, community-isolate
- Load: ~10s first-load CDN-less, ~3-5s gzipped

### C. D3.js induced-subgraph viewer (Phase 2 — LIVE 2026-05-18)
- `viewer.html` 12.8 KB + `top200.json` 13.0 KB
- Top-200 Memgraph hubs + intra-edges (39 deduplicated)
- D3 v7 jsDelivr CDN (~80 KB browser-cached)
- **Total first-load: ~106 KB — ~43× smaller** than Phase-1 4.6 MB
- Features: force-directed + zoom (0.2×-4×), per-label colors, filter checkboxes, click-to-expand neighbor highlight, hover tooltip, name-substring search, drag-to-fix node positions
- Mobile UX: 200 KB first-load → ~2-3s on 3G, <1s on 4G

### D. Mkdocs nav integration
Top-level `Knowledge Graph` tab with: Overview wiki, Interactive viewer (~106 KB Phase 2), Full graph (4.6 MB Phase 1).

## 2-tier extraction — what does each tell us?

| Layer | Strength | Weakness |
|---|---|---|
| **Memgraph LLM** | Semantic precision (`USES`, `CAUSES`, `BLOCKS` relation types), context-sensitive, evolves via subagent-fanout | Token cost per run, prompt drift, non-deterministic |
| **graphify tree-sitter + Leiden** | Deterministic, $0 cost, code-symbol precise, reproducible, community-aware | Only syntactic structure (NOT semantic edges), language-agnostic parsing limits |

**Verdict:** Memgraph is the "semantic graph", graphify is the "structural graph". Production vault-search uses Memgraph (vector index + cypher), graphify provides the **deterministic anchor** (CI-runnable regression check). See [[two-tier-graph-extraction]].

## Engineering-honest finding (candid audit)

> [!warning] Utility of the 4.6 MB interactive graph on public docs
> 4.6 MB is **significant** for a static asset on a GH Pages docs site. Mobile load slow; 3G users 30-60s. Two alternatives:
>
> 1. **Keep** — flagged with `[!warning] 4.6 MB, slow on mobile` callout, as a reference deep-dive (5846-node interactive Leiden-community viz is rare in open-source vaults)
> 2. **Replace with D3 induced subgraph** — top-200 hubs + intra-edges, ~150 KB inline d3.js + JSON, zoom + click-to-expand, much faster
>
> Recommendation: **Phase 1 — paste it in now** (zero effort, already built), **Phase 2 — build D3 induced subgraph** when time allows (~1 dev day, high ROI). Current commit is Phase 1.
>
> **Phase 2 update (2026-05-18):** LIVE — see section C. `viewer.html` 12.8 KB + `top200.json` 13.0 KB + D3 v7 CDN ~80 KB ≈ 106 KB first-load (43× smaller).

## Related

- [[two-tier-graph-extraction]] — why two extraction layers
- [[memgraph-ce-feature-limits]] — vector index + multi-namespace
- [[sv-06-world-model-knowledge-graph]] (semantically related)

## Regeneration

```bash
# A. SVG overview
python3 /tmp/build_svg.py

# B. Interactive (Phase 1 — full graphify)
cd /root/obsidian-vault && graphify scan . --output graphify-out/ \
    --exclude '.obsidian/plugins/*' --exclude '10-raw/*'

# C. D3 induced-subgraph viewer (Phase 2 — top-200 + intra-edges)
python3 /tmp/extract_top200.py

# D. Wiki stats refresh
vault-graph-query "MATCH (n:Entity) RETURN count(n)" --json
```
