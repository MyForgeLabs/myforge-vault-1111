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

## 2026-05-18 — graphify-tool mint Tier-2 deterministic referencia VERIFIED

A korábban hipotetikus Tier-1 (regex/wikilink) + Tier-2 (LLM-extract) sémát most **gyakorlatban verifikáltuk** egy konkrét external-tool-lal: **`safishamsi/graphify`** (`uv tool install graphifyy 0.8.11`).

A graphify egy **pure-deterministic tree-sitter AST + Leiden clustering** pipeline ($0 cost, NEM-LLM), ami a vault-on:
- **5,846 node / 5,479 edge / 437 community** (content-filtered: 02-Projects + 07-Decisions + 11-wiki + 06-Audits + 08-Sessions + 05-Memory + 00-Meta)
- **graph.html 4.8 MB** (force-directed interactive viz)
- **GRAPH_REPORT.md 160 KB** ("Surprising connections" + community-list + god-nodes)

A meglevő Memgraph entity-graph (LLM-based `vault-graph-extract`, **8,997 entity / 28.9% typed**) és a graphify-output **két különböző csomóponti-modellt ad**:
- Memgraph: szemantikai entitások (Concept, Decision, Sprint, Project, Skill, Person, ...)
- Graphify: szintaktikai node-ok (function-call, import, file-reference, AST-leaf)

**Cross-validation use-case**: ha egy entity csak az LLM-graph-ban van DE a deterministic-graph-ban NINCS → hallucinációs gyanú; fordítva: ha csak a tree-sitter-ben → LLM nem ismerte fel a koncepciót.

**Az `eredeti` two-tier-pattern most már elérhető-egészen**: 
- Tier-1A (regex-wikilink) — `vault-graph-mentions-extract` ÉLES (1954 :MENTIONS edge)
- Tier-1B (tree-sitter AST) — **`graphify` ÉLES** (5,846 deterministic node)
- Tier-2 (LLM-extract) — `vault-graph-extract` + `vault-graph-retype` (8,997 typed entity)

## 2026-05-19 — Jaccard 0.0070 finding (LLM-noise signal)

A `vault-graph-diff` CLI (mega-session Round 8) lefuttatta a two-tier
cross-validation-t. Eredmény:

| Layer | Count | Both | Layer-only |
|---|---:|---:|---:|
| Tier-1 (Memgraph LLM) | **12,778 entity** | 119 | 12,512 |
| Tier-2 (graphify deterministic) | **4,439 node** | 119 | 4,320 |
| Jaccard agreement | — | **0.0070** | — |

A 0.7% agreement-rate **alacsony de értelmezhető**: a Tier-1 LLM-extraction
sok zajt fog (quoted strings mint `!busy && !mutedForTTS guard`, hex-color
értékek `#06b6d4-cyan`, code-snippet fragmentumokat) "entitásként", a Tier-2
graphify pedig structural code-symbol-okat fog amiket az LLM helyesen
**nem** promóvál entity-szintre.

**A használat**: a diff-output két szegmense actionable:

- **Tier-1 only** (`vault-graph-diff --tier-1-only`) — heurisztika-classifier `name-like`/`fragment`/`short-token` címkékkel → potential LLM-hallucination cleanup-list
- **Tier-2 only** (`vault-graph-diff --tier-2-only`) — `concept-like`/`file-ref`/`snake_case-ident` → potential coverage gap az LLM-extraction-ben

**Wider lesson**: ahol két ortogonális extraction-stack működik párhuzamosan,
a diff **maga** = signal a NOISE-ról. Ez reusable pattern bármely
"LLM + deterministic" hybrid stack-en, **NEM** csak graph-extraction-ra.
Ld. [[stale-numbers-in-static-artifacts-pattern.en]] hasonló cross-source-corroboration anti-rot disciplinát.

## 2026-05-19 PM — Cleanup did NOT lift Jaccard, structural vocab-merge required

Tier-A + Tier-C noise-DELETE (12,778 → 8,913 entity, -30.2%) + extraction-prompt
tightening (vocab v3, 7 anti-noise rule) — empirikus eredmény:

| Phase | Memgraph entities | graphify entities | Jaccard |
|---|---:|---:|---:|
| Pre-cleanup | 12,778 | 4,439 | 0.0070 |
| Post-cleanup | 8,913 | 4,439 | **0.0078** |

**Δ Jaccard = +0.0008.** A Phase-4 acceptance gate (≥0.05) **NEM teljesül**.

**Mechanism**: a két extraction-stack (LLM Tier-1 narrative vs tree-sitter
Tier-2 code-symbol) **ortogonális vocabulary**-t termel. A noise-DELETE
csak a denominator-t (Tier-1 ∪ Tier-2 méretét) csökkenti, a numerator-t
(Tier-1 ∩ Tier-2 méretét) nem növeli. A maradék 8,913 narrative-concept
és 4,439 code-symbol között **strukturálisan kevés** az átfedés.

**Wider lesson**: cross-validation Jaccard két ortogonális-vocab stack
között **soha** nem ér el >0.5-ös értéket pure-DELETE-tel; **structural
vocab-merge KÖTELEZŐ**. Két opció:

- **Option A (selective re-extract)** — tightened prompt → új extraction
  → LLM-output átsoroldódik code-symbol szintre is. ETA ~3-4h.
- **Option B (tree-sitter pre-pass)** — vault-ko-ingest hibrid-pass:
  tree-sitter tokenize → symbol-extract (LLM-output ∪ tree-sitter-output).
  Direct vocabulary-overlap-növelés. ETA 1 nap design + 2-3h impl.

**Recommended sequence**: Option-A először (gyorsabb ROI), aztán Option-B
ha Phase-4 gate még mindig nem teljesül. ETA acceptance: ~2026-06-02.

Részletek: [[../06-Audits/2026-05-19 Memgraph cleanup execution result]]
+ [[../06-Audits/2026-05-19 Memgraph cleanup Phase-3 next-step plan]]
+ [[llm-graph-noise-cleanup-composite-filter]] (filter-pattern wiki).

## Kapcsolódó

- [[sv-06-world-model-knowledge-graph]] — B-7 research
- [[memgraph-ce-feature-limits]] — Memgraph CE workaround-ok
- [[claude-code-subagent-fanout]] — Tier-2 LLM-extraction motorja
- [[vendor-feature-verify-before-workaround]] — kapcsolódó verifikációs lecke
- [[external-skill-cherry-pick]] — a graphify mint cherry-pick eredmény
- [[stale-numbers-in-static-artifacts-pattern.en]] — sibling cross-source-verification discipline
- [[llm-graph-noise-cleanup-composite-filter]] — Tier-A + Tier-C composite filter pattern
- [[vault-ko-ingest-prompt-tightening-2026-05-19]] — vocab v3 prompt-tightening
