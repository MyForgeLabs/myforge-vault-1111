---
name: HippoRAG PageRank-mediated retrieval pattern
description: HippoRAG 2 neurobiológiailag-ihletett retrieval-mintázata - OpenIE entity-extraction + Personalized PageRank a graphon a query-entity-kkel mint forrással - associativity (multi-hop) és sense-making (long-context) jobb, miközben olcsóbb mint GraphRAG/RAPTOR/LightRAG
type: wiki
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "memory", "retrieval", "knowledge-graph", "pagerank", "frontier-research", "sv-research"]
source: external-repo OSU-NLP-Group/HippoRAG (MIT)
source_path: 10-raw/external/OSU-NLP-Group_HippoRAG/
parent: [[11-wiki/sv-01-memory-architecture]]
---

# HippoRAG PageRank-mediated retrieval pattern

A **HippoRAG 2** (OSU NLP Group, ICML 2025, arXiv:2502.14802) az emberi hippocampus-szerű long-term-memory neurobiológiai elveire épülő RAG-keret. **Központi újdonság:** a klasszikus vector-similarity helyett **Personalized PageRank**-et futtat a tudás-graphon, a query-ből kinyert entity-ket "personalization vector"-ként használva — multi-hop reasoning és sense-making lényegesen jobb, miközben **kevesebb LLM-hívás** kell mint GraphRAG/RAPTOR/LightRAG-ban.

## Frontier-context

- **Forrás:** [github.com/OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG), [arXiv:2502.14802](https://arxiv.org/abs/2502.14802)
- **Licenc:** MIT (OSU NLP Group)
- **Maintainers:** Bernal Jiménez Gutiérrez et al., Ohio State University
- **Paper-history:** HippoRAG 1 (NeurIPS 2024, arXiv:2405.14831), HippoRAG 2 (ICML 2025, arXiv:2502.14802)

## Architektúra — két fázis

### Offline indexing (NagyOnce)

1. **OpenIE-extraction** — minden chunkon LLM-mel kinyer `(subject, predicate, object)` triplet-et
2. **Knowledge graph** — entity-ket node-ként, predikátumokat edge-ként importál
3. **Embedding** — entity-onként és chunk-onként embedding (NV-Embed-v2, GritLM, Contriever)

### Online query (kis-cost-ú)

1. **Query → entity-extraction** — LLM (vagy egyszerű NER) kinyeri a query-ben szereplő entitásokat
2. **Personalization-vektor** — a kinyert entity-knek 1.0 súly, mindenki másnak 0
3. **Personalized PageRank** futás a graphon (NEM uniform — a query-entity-ből indul)
4. **Top-K node** kiválasztás → a node-okat tartalmazó chunkok → LLM-feedbe

## Miért jobb mint chunk-vector-similarity

| Feladat-típus | Vector-RAG | HippoRAG |
|---|---|---|
| **Single-hop QA** (NaturalQuestions, PopQA) | Erős | Konkurens (NEM gyengébb) |
| **Multi-hop QA** (MuSiQue, HotpotQA, 2Wiki) | Gyenge — chunk-similarity NEM tudja összekötni a pontokat | **Erős** — PageRank a graphon multi-hop |
| **Sense-making** (NarrativeQA, LV-Eval) | Gyenge | **Erős** — global graph-struktúra figyelembe |
| **Indexing-cost** | Olcsó (csak embedding) | **Olcsóbb mint GraphRAG/RAPTOR** (csak OpenIE, NEM hierarchikus summary) |
| **Query-latency** | ~ms | ~ms+PageRank (jól skálázódik) |

## Mintázat (generic-reusable)

```
[Document chunks]
    ↓ (offline, once)
[OpenIE LLM extraction]  ← triplet-tár
    ↓
[Knowledge graph: entity-node, predicate-edge]
[+ entity-embedding + chunk-embedding]
    ↓
======== online query ========
[Query] → [Query-entity-extraction (LLM/NER)]
    ↓
[Personalization vector: 1.0 a query-entity-kre]
    ↓
[Personalized PageRank a graph-on]
    ↓
[Top-K node → chunks tartalmazva]
    ↓
[LLM-feed → answer]
```

## Hogyan releváns a vault-meta SV-nek

- **SV-1 Memory architecture, "associativity" pillér** — a saját 3-rétegű (working/episodic/semantic) memóriánk **most NEM csinál PageRank-stílusú associative-retrieval-t**, csak top-K cosine. **Ez konkrét gap.** A saját Memgraph-graphunkban (8997 entity, 13812 relation) **közvetlenül futtatható** Personalized PageRank a `MAGE` Memgraph-pluginnal vagy NetworkX-hidd. Becsült improvement multi-hop kérdésekre: jelentős.
- **SV-6 World-model / KG** — a HippoRAG **azonos hipotézis-családba** tartozik mint a saját B-7 entity-graph-réteg. **Különbség:** a mi rétegünk most főleg passzív (search-céllal lookup-olt), HippoRAG **aktívan retrieval-mediator**.
- **Indexing-cost előny** — GraphRAG-szerű hierarchikus community-summary drága; HippoRAG csak OpenIE-t kér. A mi entity-extraction-pipelinetink **már OpenIE-szerű** (subagent-fanout pattern, 2-phase pending) — **kompatibilis**.
- **Continual learning property** — HippoRAG explicit "non-parametric continual learning" — új doc add-elésekor **NEM kell re-indexelni** mindent, csak az új triplet-eket add a graphba. A mi vault-ko-ingest pipeline-unk **pontosan ezt** csinálja.

## Mintázat-buktatók

- **OpenIE-quality kritikus** — ha a triplet-extraction zajos (rossz entity-linking, hallucinated relation), a PageRank szétpermutálja a noise-t. **Mitigation:** cross-source corroboration (egyezzen 2+ chunkban a triplet előtti elfogadás)
- **Entity-resolution / deduplication** — `"Barack Obama" vs "Obama" vs "President Obama"` — ha NEM egyesülnek a graph-on, a PageRank szétoszlik. **Mitigation:** canonical-entity-resolver (LLM-mel vagy embedding-clustering-gel)
- **PageRank-paraméterek** — damping-factor (0.5 default), top-K, iteration-count nyitottak; **datasethez kell hangolni**
- **Embedding-model fontos** — NV-Embed-v2 / GritLM / Contriever ajánlott, OpenAI ada-002 gyengébb
- **Long-tail entitás-probléma** — ritkán-előforduló entity-knek alacsony connectivity → PageRank kevés súlyt ad → hibás retrieval. **Mitigation:** vector-search fallback hybrid-módban

## Kapcsolódó

- [[11-wiki/sv-01-memory-architecture]] — saját memory-architektúra
- [[11-wiki/sv-06-world-model-knowledge-graph]] — saját KG-réteg
- [[11-wiki/two-tier-graph-extraction]] — saját 2-tier extraction (~HippoRAG OpenIE)
- [[11-wiki/hybrid-bm25-semantic-rrf-pattern]] — saját hybrid-retrieval, PageRank ide is bevezethető
- [[11-wiki/memgraph-ce-feature-limits]] — Memgraph MAGE-ben elérhető PageRank
- [[10-raw/external/OSU-NLP-Group_HippoRAG/README]] — forrás
