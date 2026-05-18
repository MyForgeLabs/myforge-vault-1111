---
name: GraphRAG community-summary pattern
description: Microsoft GraphRAG hierarchical knowledge-model pattern - LLM-extraction graph + Leiden community detection + per-community summary + global/local/drift-search query modes - global query-focused summarization for "what are the main themes" type questions, where vector-RAG conceptually fails
type: wiki
lang: en
translated_from: graphrag-community-summary-pattern
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "knowledge-graph", "graphrag", "community-detection", "frontier-research", "sv-research"]
source: external-repo microsoft/graphrag (MIT)
parent: [[11-wiki/sv-06-world-model-knowledge-graph]]
---

# GraphRAG community-summary pattern

**Microsoft GraphRAG** (research 2024, arXiv:2404.16130) is an industry-grade reference in the "narrative private data over LLM discovery" space. Core idea: an LLM extracts an entity-relation graph, the **Leiden algorithm** clusters it into hierarchical communities, an LLM-summary is **pre-generated** for every community, and at query time those summaries are synthesised into an answer. **This is unique: query-focused holistic summarization** — where chunk-similarity conceptually fails.

## Frontier context

- **Source:** [github.com/microsoft/graphrag](https://github.com/microsoft/graphrag), [microsoft.github.io/graphrag](https://microsoft.github.io/graphrag), [arXiv:2404.16130](https://arxiv.org/pdf/2404.16130)
- **License:** MIT (Microsoft Research)
- **Maintainers:** Microsoft Research, Darren Edge et al.
- **Note:** "demonstration, not officially supported offering"
- **Warning in docs:** "indexing can be an expensive operation, start small"

## Architecture — indexing pipeline

```
LoadDocuments → ChunkDocuments → {ExtractGraph, ExtractClaims, EmbedChunks}
ExtractGraph → {DetectCommunities, EmbedEntities}
DetectCommunities → GenerateReports → EmbedReports
```

**Knowledge Model** — output abstraction above the storage; pipeline:

1. **LoadDocuments → ChunkDocuments** — size-proportional chunking
2. **ExtractGraph** — LLM-extracted `(entity, relation, entity)` triplets + optionally **ExtractClaims** (statement-level claim store)
3. **DetectCommunities** — **Leiden algorithm** on the graph → hierarchical clusters (level-0, level-1, level-2 communities)
4. **GenerateReports** — for every community, an LLM pass: "write a summary of the theme represented by this community"
5. **EmbedChunks / EmbedEntities / EmbedReports** — three independent vector indices

## Three query modes

| Mode | What it does | Best for |
|---|---|---|
| **Global Search** | Synthesises top-level community summaries based on the query | **"What are the main themes?"**, holistic, sense-making |
| **Local Search** | Starts from a specific entity, fetches graph neighbourhood + chunks | Precise factoid: "what did X do?" |
| **Drift Search** | Hybrid — starts global, "drifts" toward local | Multi-hop with high-level grounding |

## Factory pattern (deep customisation)

GraphRAG's architecture is built on **factory patterns**, a reusable software-engineering pattern for any RAG stack:

- `completion_factory` — LLM provider swap (LiteLLM default, custom registrable)
- `cache_factory` — file / blob / CosmosDB
- `storage_factory` — output tables
- `vector_store_factory` — lancedb / Azure AI Search / CosmosDB
- `input_reader` — text / CSV / JSON / custom
- `workflows/factory` — full-pipeline override

**Reusable pattern:** string-name-based registration, override default, override per-instance.

## Pattern (generic-reusable)

```
[Corpus]
   ↓
[Chunk + LLM-extract entity/relation graph]
   ↓
[Leiden community detection — hierarchical]
   ↓
[LLM summary per community (offline batch)]
   ↓
[Vector-embed chunks, entities, reports]
   ↓
====== query-time ======
   ├── Global: community-summary fan-in → synthesis
   ├── Local: entity-anchor → neighborhood + chunks
   └── Drift: global → local progressive zoom
```

## Relevance to vault-style memory architectures

- **World-model / KG** — a B-7-style entity-graph (e.g. Memgraph, 8997 entity / 13812 relation) typically does NOT run Leiden community detection. **Concrete gap.** Memgraph MAGE has community detection available (Louvain/Leiden), worth trying on the vault. Estimated value: "what are the main themes of the vault" / "which projects belong together" meta-queries.
- **graphify Tier-2 already Leiden-based** — a graphify input **already** uses Leiden community detection (5846 node, 437 communities). **Partly built-in.** Missing: per-community LLM-summary layer (GraphRAG's main trick).
- **Indexing-cost warning** — Microsoft explicitly warns about high indexing cost. A `claude-code subagent-fanout` pattern ($0 cost) is **dramatically cheaper** than OpenAI-API-based GraphRAG indexing. This is a competitive advantage.
- **Factory pattern** — scripts in a typical vault stack (ko-ingest, search, crystallize-stack) are loosely structured; worth explicitly refactoring to a factory pattern for config stability.
- **Notebook-evaluation parallel** — a notebook as cognitive layer (axis SV-8) is **effectively** GraphRAG global-search-equivalent in a UI; an NB-deep-research pattern provides similar epistemic payoff at **lower cost**.

## Pattern pitfalls

- **Indexing cost** — large corpus + LLM entity-extraction + community-summary LLM pass + 3 vector indices = many USD ($100+ on typical datasets mentioned in docs)
- **Prompt tuning mandatory** — "out-of-the-box may not yield best results" (explicit in docs). Domain-specific prompt-tuning per `prompt_tuning/auto_prompt_tuning.md`
- **OpenAI-API lock-in** — original design heavily OpenAI-oriented; LiteLLM-wrapping mitigates, but NOT friction-free
- **Versioning frequency** — `graphrag init --root [path] --force` on every minor version bump; production deploys must monitor
- **Microsoft "demo, not supported"** — production-deploy at-your-own-risk; research codebase, not industrial stack
- **Community detection not always meaningful** — on small corpora (~100 doc), communities are forced; min ~1000-doc threshold recommended

## Related

- [[sv-06-world-model-knowledge-graph]] — KG axis
- [[two-tier-graph-extraction]] — 2-tier extraction (Tier-2 = graphify Leiden)
- [[sv-08-notebooklm-cognitive-layer]] — NB as cognitive layer, partly GraphRAG-equivalent
- [[memgraph-ce-feature-limits]] — Memgraph MAGE community detection
