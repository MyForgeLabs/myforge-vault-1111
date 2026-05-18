---
name: two-tier-graph-extraction
description: Knowledge-graph építés két rétegben - determinisztikus baseline (wikilinks/regex) + LLM-enrichment - a baseline ground-truth-ot ad az LLM eval-hoz, és zero-cost-tal indul
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "knowledge-graph", "memgraph", "extraction-pipeline"]
---

# Two-tier graph extraction

## A pattern

Knowledge-graph építéskor (Memgraph / Neo4j / Cypher-store-ba) **NE indulj direkt LLM-extraction-nel**. Helyette:

**Tier 1 (deterministic baseline)** — Zero-LLM, regex/parser-based:
- Wikilink-importer: `\[\[([^\]|]+?)(\|[^\]]+)?\]\]` regex → `(:SourceFile)-[:MENTIONS]->(:WikiLink)` edges
- Frontmatter-importer: `tags:`/`linked-to:`/`depends-on:` YAML mezők → typed edges
- Filesystem-importer: directory-structure → `(:SourceFile)-[:LOCATED_IN]->(:Folder)` edges
- Cost: $0, latency: O(seconds), idempotens

**Tier 2 (LLM-enrichment)** — Subagent-fanout-pattern-rel:
- Implicit relations a markdown-szöveg-ből (entity-pair → typed-relation)
- Cost: $0 (subscription) ha claude-code subagent-fanout, idő O(perc)
- Confidence-tagged: minden LLM-edge `confidence: 0.0-1.0` mezővel

**Eval:** A Tier-1 a Tier-2 ground-truth-ja — ha a Tier-2 NEM tartalmazza a Tier-1-ben szereplő edge-eket, akkor extraction-recall < 100%.

## Élő példa (2026-05-17-obsidian-vault-2)

A vault `08-Sessions/`, `02-Projects/`, `07-Decisions/`, `11-wiki/` mappáit Memgraph-ba ingest-elve:

- **Tier 1 (Wikilink-importer):** 556 :SourceFile + 562 :WikiLink + **1954 :MENTIONS edges** zero-cost-tal, ~22s scan
- **Tier 2 (LLM-extracted, Week 1-α):** 8975 :Entity + 12160 :Literal + **13812 typed-relations** subagent-fanout-pattern-rel
- **Overlap:** ~30% (a sokak közös subject-eken mind a baseline mind az LLM-pass találja). A 70% LLM-only relations = implicit relation-ok (pl. "X uses Y" without explicit wikilink)

Top hubok a deterministic baseline-ben:
1. `05-Memory/Infrastructure` (67 inbound) — szervezeti tudás-központ
2. `02-Projects/Index` (38 inbound) — projekt-katalógus
3. `11-wiki/Crystallization-protocol` (38 inbound) — protokoll-hivatkozás-magnet

## A kétréteg ROI-ja

- **Tier 1 alone (no LLM):** O(s) build, O(s) update; kevés implicit relation, magas precision, alacsony recall
- **Tier 2 alone (LLM-only):** O(óra) build, magasabb recall, de NO ground-truth → schema-drift risk
- **Both tiers:** Tier 1 mint regression-test, Tier 2 enrichment → optimum

## Mikor érdemes alkalmazni

- ✅ Bármilyen markdown-knowledge-base graph-szerű query-vel (Obsidian-vault, doc-portál, wiki)
- ✅ Bármilyen graph-extraction-pipeline, ahol az LLM-eredmény ellenőrizhetőség fontos
- ✅ Schema-versioning kontextusban — a Tier-1 stabil, Tier-2 LLM-prompt-evolúcióval változhat

## Kapcsolódó

- [[sv-06-world-model-knowledge-graph]] — B-7 research
- [[memgraph-ce-feature-limits]] — Memgraph CE workaround-ok
- [[claude-code-subagent-fanout]] — Tier-2 LLM-extraction motorja
- [[vendor-feature-verify-before-workaround]] — kapcsolódó verifikációs lecke
