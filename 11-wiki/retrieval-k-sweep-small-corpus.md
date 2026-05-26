---
name: Retrieval K-sweep on small corpora
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#concept/retrieval", "#concept/longmemeval", "#project/sv"]
---

# Retrieval K-sweep on small corpora — BEIR/MTEB lore doesn't transfer

BEIR and MTEB benchmarks recommend `fetch_k ∈ {20, 50, 100}` for RRF and reranker fusion. **On small corpora (<10K documents), these defaults often perform WORSE than `fetch_k = 5`.**

## The empirical refutation

LongMemEval-S vault-variant, 99 queries against ~3K vault-chunks (RRF fusion of BM25 + bge-m3 vector search):

| fetch_k | Recall@5 | Δ vs K=5 |
|---|---|---|
| 5 | **76.77%** | — |
| 10 | 75.76% | -1.01pp |
| 15 | 74.75% | -2.02pp |
| 20 | 71.72% | -5.05pp |
| 30 | 68.69% | -8.08pp |
| 50 | 62.63% | -14.14pp |

**Strictly monotone-decreasing.** No sweet-spot at K=20 (BEIR/MTEB-recommended). Each increase in K reduces Recall@5.

## Mechanism (hypothesis)

The RRF score `score(d) = sum( 1/(60 + rank_i(d)) ) for i in retrievers` is bounded above by `2/60 ≈ 0.033` (for a document ranked #1 by both retrievers). The discriminative range between rank-1 and rank-50 is `1/60 - 1/110 ≈ 0.0076` — tiny.

When `fetch_k = 50`, the noise candidates (rank 30-50) get tiny RRF scores that nonetheless can edge out a high-quality candidate ranked #6 by one retriever and not in the other's top-50. The top-5 output becomes diluted.

When `fetch_k = 5`, only the highest-confidence candidates compete, and the RRF top-5 is the intersection-or-union of two confident lists.

## On large corpora

BEIR has 1M+ document collections per dataset. There, the rank-50 candidates are still strong matches (the recall@50 for BM25 is often >0.9). Wider K helps because the "noise" at K=50 is still relevant. The dynamic flips.

## When this matters

- Personal knowledge-base RAG (vault, Obsidian, Roam) — typical 1K-10K notes
- Internal company wikis — usually <50K documents
- Codebase-search RAG — single project usually 1K-100K files
- Single-domain technical docs — focused but small

## When to use BEIR defaults

- Wikipedia-scale RAG (5M+ articles)
- Web-search-scale (1B+)
- General-knowledge LLM grounding with broad corpora

## Recommendation

**Always sweep K** on your own corpus. The sweet-spot is corpus-size-dependent. Empirical rule-of-thumb:
- corpus < 10K docs → K ∈ {5, 10}
- corpus 10K-100K → K ∈ {10, 20}
- corpus 100K-1M → K ∈ {20, 50}
- corpus > 1M → K ∈ {50, 100}

But these are starting points. Run the sweep, plot the curve, pick the empirical winner.

## When it bit us (2026-05-19)

LongMemEval-S v0.3 sweep was designed expecting K=20 sweet-spot (per BEIR/MTEB lore). The actual winner was K=5 by 5pp. The Wave-2 Design B prediction "K=20 sweet-spot, +3-5pp over baseline" turned out to be **REFUTED — winner K=5, +9pp over baseline (76.77% vs 67.68%)**.

The baseline.json now has a separate `v03_fused_a_rrf_optimal` entry locked at K=5 for the canonical production gate.

## Related

- [[../06-Audits/2026-05-19 LongMemEval v0.3 sweep results]] — the original sweep data
- [[reranker-cost-optimization-not-size]] — sibling retrieval-tuning pattern
- [[sv-01-memory-architecture]] — broader B-2 sprint context
