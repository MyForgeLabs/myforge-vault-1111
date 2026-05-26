---
name: hybrid-bm25-semantic-rrf-pattern
description: BM25 + semantic top-K RRF (Reciprocal Rank Fusion) hybrid retrieval pattern - +8ms latency overhead, marginal win on rare-token queries, neutral on common-token queries, recall improvement mainly on evergreen-conceptual chunks
type: wiki
lang: en
translated_from: hybrid-bm25-semantic-rrf-pattern
created: 2026-05-17
updated: 2026-05-18
tags: ["#type/wiki", "retrieval", "search", "bm25", "semantic-search", "rrf"]
status: stable
---

# Hybrid BM25 + semantic RRF pattern

## The problem

Pure **semantic search (cosine over a multilingual embedding like bge-m3)** loses **rare-token queries** — terms like "G-Eval bias mitigation" or "subagent fanout" drown in noise when the embedding pool is large and the surface form is unusual. Pure-BM25, on the other hand, loses **paraphrase recall** (acronym ↔ full-name, synonyms). A hybrid pipeline lands hits on both axes and **fuses by rank**.

## The pattern (RRF — Reciprocal Rank Fusion)

```
query ──► BM25 corpus (in-RAM)  ──► top-K_bm25 (3-12ms)
      └─► semantic vector-index ──► top-K_sem (1-300ms)

                          │
                          ▼
   per-document: score_RRF = (1/(k+rank_bm25)) + (1/(k+rank_semantic))
   (k=60 default, smooths the 1/rank distribution)
                          │
                          ▼
                  top-K_hybrid (sub-ms fusion)
```

**Cost:** +5-12ms BM25 in-RAM + sub-ms fusion = **+8ms average overhead**. The semantic encode (~270ms warm) remains dominant, so hybrid's relative overhead is ~3%.

## 5-query benchmark result

| Query | Pure-semantic top-5 | Hybrid top-5 | Overlap | New hits |
|---|---|---|---|---|
| pdf parsing pipeline | 5 hits | 5 hits | 3/5 | 2 session-summaries BM25 #1 |
| Memgraph native vector index | 5 hits | 5 hits | 4/5 | 1 "Next session" planning |
| subagent fanout pattern | 5 hits | 5 hits | 3/5 | 2 wiki-intro chunks BM25 #1 |
| G-Eval bias mitigation | 5 hits | 5 hits | 2/5 | 3 wiki-explainer chunks |
| nano-banana CLI gotchas | 5 hits | 5 hits | 5/5 | 0 (only re-ordering) |

**Aggregate:** 17/25 overlap, **8/25 new hits** (32% recall improvement on rare-token queries). Manual judgement: 0 false-positives among new hits (all genuinely relevant).

## When to apply

- ✅ Rare-token / acronym-heavy domain (jargon like G-Eval, NLI, subagent, RRF)
- ✅ Code-token search (function names, flag names, library IDs)
- ✅ Multilingual mixed-tech domains where the embedding model's coverage of the secondary language is weaker than English
- ❌ Common-token natural-language queries (all queries hit 5/5 overlap, +8ms wasted)
- ❌ Mixed-language domain where encoding dominates (latency cap)

## Design principles

1. **Hybrid flag DEFAULT OFF** — backward compat + savings if no rare-token queries
2. **BM25 index in-RAM JSON-serialized** — many CLI security hooks block binary formats; JSON rehydration of `BM25Okapi.__dict__` is primitive-only and safe
3. **Accent-fold + lowercase + ≥2 char tokenizer** for non-English languages — Snowball stemming is a follow-up, not critical at first
4. **RRF k=60** — Cormack et al. 2009 empirical default; smooths the 1/rank distribution
5. **JSON output `{bm25_rank, semantic_rank, rrf_score}`** — debuggable, NOT black-box

## Trade-offs

- ⚠️ BM25 index disk size ~2.5× larger in JSON form
- ⚠️ Missing stemming means morphological variants tokenize separately (Snowball follow-up fixes this)
- ✅ Marginal win on rare-token queries, neutral on common-token queries
- ✅ $0 implementation cost (rank-bm25 pip + existing semantic infra)

## Related

- [[memgraph-ce-feature-limits]] — native vector-index (fast search half)
- [[sv-01-memory-architecture]] — retrieval architecture research
- [[smart-trigger-cost-pattern]] — related retrieval pipeline pattern

## LongMemEval-S v0.2 validation (2026-05-19)

A `vault-search` 3-mode head-to-head, 20-Q first-batch, same gold set:

| Mode | Recall@5 | Δ vs cosine-only |
|---|---:|---:|
| cosine-only baseline | 40.0% (8/20) | – |
| smart-rerank (bge-reranker-v2-m3) | 40.0% (8/20) | **+0 pp** |
| **hybrid (BM25+RRF)** | **60.0% (12/20)** | **+20 pp** |

**Mechanism:** smart-rerank reorders the dense-cosine top-30. If gold isn't in that initial pool, reranking can't recover it. BM25 fetches a different candidate pool (lexical-match driven), RRF fusion combines both ranked lists. **Candidate-fetch diversity > reranking precision** — inverts the conventional "rerank for precision" narrative.

**Default-shift:** `longmemeval-vault-variant.py` default mode `cosine-only` → `hybrid`. 99-Q hand-curated benchmark: **67.68% Recall@5** (2.3pp short of 70% target, but on a strictly harder dataset than v0.1's 50-Q).
