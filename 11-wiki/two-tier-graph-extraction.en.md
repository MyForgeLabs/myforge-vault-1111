---
name: two-tier-graph-extraction
description: Knowledge graph construction in two tiers - deterministic baseline (wikilinks/regex) + LLM enrichment - the baseline provides ground-truth for LLM eval and starts with zero cost
type: wiki
lang: en
translated_from: two-tier-graph-extraction
created: 2026-05-17
updated: 2026-05-18
tags: ["#type/wiki", "knowledge-graph", "memgraph", "extraction-pipeline"]
---

# Two-tier graph extraction

## The pattern

When building a knowledge graph (into Memgraph / Neo4j / Cypher store), **do NOT start with direct LLM-extraction**. Instead:

**Tier 1 (deterministic baseline)** — Zero-LLM, regex/parser-based:
- Wikilink importer: `\[\[([^\]|]+?)(\|[^\]]+)?\]\]` regex → `(:SourceFile)-[:MENTIONS]->(:WikiLink)` edges
- Frontmatter importer: `tags:` / `linked-to:` / `depends-on:` YAML fields → typed edges
- Filesystem importer: directory structure → `(:SourceFile)-[:LOCATED_IN]->(:Folder)` edges
- Cost: $0, latency: O(seconds), idempotent

**Tier 2 (LLM enrichment)** — using a subagent-fanout pattern:
- Implicit relations from markdown text (entity-pair → typed-relation)
- Cost: $0 (subscription) when run via subagent fanout, time O(minutes)
- Confidence-tagged: every LLM edge carries a `confidence: 0.0-1.0` field

**Eval:** Tier 1 is Tier 2's ground truth — if Tier 2 does NOT contain the edges produced by Tier 1, extraction recall is <100%.

## Live example

Ingesting a markdown knowledge base (sessions, projects, decisions, wiki) into Memgraph:

- **Tier 1 (Wikilink importer):** 556 `:SourceFile` + 562 `:WikiLink` + **1954 `:MENTIONS` edges** at zero cost, ~22s scan
- **Tier 2 (LLM-extracted via subagent fanout):** 8975 `:Entity` + 12160 `:Literal` + **13812 typed relations**
- **Overlap:** ~30% (common subjects found by both passes). The 70% LLM-only relations = implicit relations ("X uses Y" without explicit wikilink)

Top hubs in the deterministic baseline:
1. `Infrastructure` (67 inbound) — organisational knowledge hub
2. `Projects/Index` (38 inbound) — project catalogue
3. `Crystallization-protocol` (38 inbound) — protocol-reference magnet

## ROI of the two tiers

- **Tier 1 alone (no LLM):** O(s) build, O(s) update; few implicit relations, high precision, low recall
- **Tier 2 alone (LLM-only):** O(hours) build, higher recall but NO ground truth → schema-drift risk
- **Both tiers:** Tier 1 as regression test, Tier 2 as enrichment → optimum

## When to apply

- ✅ Any markdown knowledge base with graph-like queries (Obsidian vault, doc portal, wiki)
- ✅ Any graph-extraction pipeline where LLM-output verifiability matters
- ✅ Schema-versioning contexts — Tier 1 is stable, Tier 2 can evolve with LLM-prompt iterations

## graphify-tool as Tier-2 deterministic reference (verified)

The previously hypothetical Tier-1 (regex/wikilink) + Tier-2 (LLM-extract) scheme is now **practically verified** with a concrete external tool: **`graphify`** (a pure-deterministic tree-sitter AST + Leiden clustering pipeline, $0 cost, NOT LLM-based).

On a sample knowledge base:
- **5,846 nodes / 5,479 edges / 437 communities** (content-filtered)
- **graph.html 4.8 MB** (force-directed interactive viz)
- **GRAPH_REPORT.md 160 KB** ("Surprising connections" + community list + god-nodes)

The existing Memgraph entity graph (LLM-based, **8,997 entities / 28.9% typed**) and the graphify output **give two different node models**:
- Memgraph: semantic entities (Concept, Decision, Sprint, Project, Skill, Person, …)
- Graphify: syntactic nodes (function-call, import, file-reference, AST-leaf)

**Cross-validation use case:** if an entity is only in the LLM graph but NOT in the deterministic graph → hallucination suspicion; conversely: if only in the tree-sitter graph → LLM did not recognise the concept.

**The full two-tier pattern is now available end-to-end:**
- Tier-1A (regex-wikilink) — wikilink mention extractor (1954 :MENTIONS edges)
- Tier-1B (tree-sitter AST) — **graphify** (5,846 deterministic nodes)
- Tier-2 (LLM-extract) — subagent-fanout extractor (8,997 typed entities)

## Related

- [[sv-06-world-model-knowledge-graph]] — KG research axis
- [[memgraph-ce-feature-limits]] — Memgraph CE workarounds
- [[claude-code-subagent-fanout]] — Tier-2 LLM-extraction engine
- [[vendor-feature-verify-before-workaround]] — related verification lesson
- [[external-skill-cherry-pick]] — graphify as a cherry-pick result
