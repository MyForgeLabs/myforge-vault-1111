---
name: HippoRAG PageRank-mediated retrieval pattern
description: HippoRAG 2 neurobiologically-inspired retrieval pattern - OpenIE entity-extraction + Personalized PageRank on the graph using query-entities as the source - better associativity (multi-hop) and sense-making (long-context), while cheaper than GraphRAG/RAPTOR/LightRAG
type: wiki
lang: en
translated_from: hipporag-pagerank-mediated-retrieval-pattern
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "memory", "retrieval", "knowledge-graph", "pagerank", "frontier-research", "sv-research"]
source: external-repo OSU-NLP-Group/HippoRAG (MIT)
parent: [[11-wiki/sv-01-memory-architecture]]
---

# HippoRAG PageRank-mediated retrieval pattern

**HippoRAG 2** (OSU NLP Group, ICML 2025, arXiv:2502.14802) is a RAG framework inspired by neurobiological principles of the human hippocampus and long-term memory. **Central novelty:** instead of classical vector similarity, it runs **Personalized PageRank** on the knowledge graph, using the entities extracted from the query as the "personalization vector" — multi-hop reasoning and sense-making are substantially better, while **requiring fewer LLM calls** than GraphRAG/RAPTOR/LightRAG.

## Frontier context

- **Source:** [github.com/OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG), [arXiv:2502.14802](https://arxiv.org/abs/2502.14802)
- **License:** MIT (OSU NLP Group)
- **Maintainers:** Bernal Jiménez Gutiérrez et al., Ohio State University
- **Paper history:** HippoRAG 1 (NeurIPS 2024, arXiv:2405.14831), HippoRAG 2 (ICML 2025, arXiv:2502.14802)

## Architecture — two phases

### Offline indexing (one-time, large)

1. **OpenIE extraction** — for every chunk, extract `(subject, predicate, object)` triplets with an LLM
2. **Knowledge graph** — import entities as nodes, predicates as edges
3. **Embedding** — per-entity and per-chunk embeddings (NV-Embed-v2, GritLM, Contriever)

### Online query (low-cost)

1. **Query → entity extraction** — LLM (or simple NER) extracts entities present in the query
2. **Personalization vector** — extracted entities get weight 1.0, everyone else 0
3. **Personalized PageRank** runs on the graph (NOT uniform — starts from the query entities)
4. **Top-K node** selection → chunks containing those nodes → fed to the LLM

## Why this beats chunk-vector similarity

| Task type | Vector RAG | HippoRAG |
|---|---|---|
| **Single-hop QA** (NaturalQuestions, PopQA) | Strong | Competitive (NOT weaker) |
| **Multi-hop QA** (MuSiQue, HotpotQA, 2Wiki) | Weak — chunk-similarity cannot connect dots | **Strong** — PageRank on the graph multi-hops naturally |
| **Sense-making** (NarrativeQA, LV-Eval) | Weak | **Strong** — global graph structure considered |
| **Indexing cost** | Cheap (just embedding) | **Cheaper than GraphRAG/RAPTOR** (only OpenIE, NO hierarchical summary) |
| **Query latency** | ~ms | ~ms + PageRank (scales well) |

## Pattern (generic-reusable)

```
[Document chunks]
    ↓ (offline, once)
[OpenIE LLM extraction]  ← triplet store
    ↓
[Knowledge graph: entity-node, predicate-edge]
[+ entity-embedding + chunk-embedding]
    ↓
======== online query ========
[Query] → [Query-entity extraction (LLM/NER)]
    ↓
[Personalization vector: 1.0 on query entities]
    ↓
[Personalized PageRank on the graph]
    ↓
[Top-K node → containing chunks]
    ↓
[LLM-feed → answer]
```

## Relevance to vault-style memory architectures

- **Memory architecture, "associativity" pillar** — a 3-tier (working/episodic/semantic) memory typically does NOT do PageRank-style associative retrieval, only top-K cosine. **Concrete gap.** On a Memgraph-based knowledge graph (e.g. 8997 entities, 13812 relations), Personalized PageRank can be **directly run** with the `MAGE` plugin or a NetworkX bridge. Estimated improvement on multi-hop questions: significant.
- **World-model / KG** — HippoRAG belongs to the **same hypothesis family** as a B-7-style entity-graph layer. **Difference:** a passive layer (lookup-only) is now mostly passive, HippoRAG **actively mediates retrieval**.
- **Indexing-cost advantage** — GraphRAG-style hierarchical community summary is expensive; HippoRAG asks only for OpenIE. A `claude-code subagent-fanout` pattern ($0 cost) is **dramatically cheaper** than OpenAI-API-based GraphRAG indexing.
- **Continual learning property** — HippoRAG explicitly supports "non-parametric continual learning" — when a new doc is added, you do **NOT need to re-index** everything, just add new triplets to the graph. An ingest pipeline can do **exactly this**.

## Pattern pitfalls

- **OpenIE quality is critical** — if triplet-extraction is noisy (bad entity linking, hallucinated relation), PageRank will spread the noise. **Mitigation:** cross-source corroboration (require 2+ chunks to agree before accepting a triplet)
- **Entity resolution / deduplication** — `"Barack Obama" vs "Obama" vs "President Obama"` — if not unified on the graph, PageRank dilutes. **Mitigation:** canonical-entity resolver (LLM-based or embedding-clustering)
- **PageRank parameters** — damping factor (0.5 default), top-K, iteration count are open; **dataset-tunable**
- **Embedding model matters** — NV-Embed-v2 / GritLM / Contriever recommended, OpenAI ada-002 is weaker
- **Long-tail entity problem** — rarely-occurring entities have low connectivity → PageRank gives them little weight → poor retrieval. **Mitigation:** vector-search fallback in hybrid mode

## Related

- [[sv-01-memory-architecture]] — memory architecture
- [[sv-06-world-model-knowledge-graph]] — KG layer
- [[two-tier-graph-extraction]] — 2-tier extraction (~HippoRAG OpenIE)
- [[hybrid-bm25-semantic-rrf-pattern]] — hybrid retrieval (PageRank can extend here)
- [[memgraph-ce-feature-limits]] — Memgraph MAGE PageRank availability
