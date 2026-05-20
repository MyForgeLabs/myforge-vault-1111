---
name: LongMemEval K=5 sweet-spot — refute wider-pool lore
type: decision
status: 🟢 LANDED 2026-05-19 (baseline locked, v0.3-A optimal block added)
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/decision", "#project/sv", "sv-3", "evaluation", "retrieval", "longmemeval"]
related:
  - "[[../11-wiki/retrieval-k-sweep-small-corpus]]"
  - "[[../06-Audits/2026-05-19 LongMemEval v0.3 sweep results]]"
  - "[[2026-05-12 sv-7 continuous evaluation arch]]"
---

# LongMemEval K=5 sweet-spot — refute "wider pool helps fusion" lore

## Context

The SV B-7 continuous-evaluation sprint locked a LongMemEval-S vault-variant baseline at **67.68% Recall@5** using RRF fusion over BM25 + bge-m3 vector-search with `fetch_k = 50` (BEIR/MTEB default). This was used as the production regression-gate from 2026-05-13 onward.

Brainstorm idea #1 (RAGAS) was wired into a daily cron at 02:45 against this baseline.

## The decision (and the surprising finding)

2026-05-19 PM session ran a v0.3 fetch-K sweep over the same 99-query LongMemEval-S corpus. The expected result (per Wave-2 Design B) was a sweet-spot at K=20, +3-5pp over baseline.

The actual result:

| fetch_k | Recall@5 | Hits | Δ vs K=5 |
|---|---|---|---|
| **5** | **76.77%** | 76/99 | — |
| 10 | 75.76% | 75/99 | -1.01pp |
| 15 | 74.75% | 74/99 | -2.02pp |
| 20 | 71.72% | 71/99 | -5.05pp |
| 30 | 68.69% | 68/99 | -8.08pp |
| 50 | 62.63% | 62/99 | -14.14pp |

**Strictly monotone-decreasing.** The BEIR/MTEB lore "wider candidate pool helps fusion" is **refuted on this corpus**.

## Why (mechanism)

RRF score `1/(60 + rank)` is bounded above by `2/60 ≈ 0.033` (rank-1 by both retrievers) and the discriminative range between rank-1 and rank-50 is `≈ 0.0076` — very narrow. With `fetch_k = 50`, noise candidates (rank 30-50) accumulate small but nonzero RRF scores that can edge out a high-quality candidate ranked #6 by one retriever and not present in the other's top-50.

On large corpora (1M+ docs as in BEIR), the rank-50 candidates are still strong (recall@50 for BM25 is often >0.9), so wider K helps. On small corpora (~3K vault-chunks), rank-50 includes irrelevant material → top-5 dilution.

## Decision

1. **Lock K=5 as the production-default optimal** for the SV `v0.3-A` retrieval path.
2. Keep v0.2 hybrid baseline (`fetch_k = 50`, 67.68%) for back-compat in the daily 02:45 regression cron — NO breaking change to existing cron-gates.
3. **New baseline block added to `.vault-eval/regression/baseline.json`**:
   ```json
   "v03_fused_a_rrf_optimal": {
       "fetch_k": 5,
       "recall_at_5": 0.7677,
       "min_recall": 0.7177,
       "n_hits": 76,
       "n_total": 99,
       "tolerance_pct": 5,
       "locked_at": "2026-05-19T14:00:00Z"
   }
   ```
4. Future retrieval-changes must keep Recall@5 ≥ 0.7177 at fetch_k=5 (sweet-spot baseline minus 5pp tolerance).
5. Add a follow-up task: flip the daily cron from `--v02 K=50` to `--v03 K=5` after 1 week of stability monitoring (a v0.3-A K=5 result is ~15x faster than v0.3-B reranker; cost-neutral to flip).

## Counter-cases (when NOT to use K=5)

- Corpora >100K documents — the rank-30 to rank-50 range starts to contain genuinely useful candidates again.
- Multi-modal RAG where the fusion combines diverse retriever types (graph + vector + lexical) — wider pool may help cross-retriever consensus.
- High-recall-tolerance applications (e.g. exploratory research) — K=20 may give better recall@20 even at the cost of recall@5.

## Generalization

The wider lesson (now in [[../11-wiki/retrieval-k-sweep-small-corpus]]): **always sweep K on your own corpus before adopting BEIR/MTEB defaults**. Corpus size matters more than algorithmic family. Recommended starting points:

- corpus < 10K docs → K ∈ {5, 10}
- corpus 10K-100K → K ∈ {10, 20}
- corpus 100K-1M → K ∈ {20, 50}
- corpus > 1M → K ∈ {50, 100}

## Status

🟢 **LANDED.** baseline.json updated, audit-trail in [[../06-Audits/2026-05-19 LongMemEval v0.3 sweep results]], wiki published, daily-cron-flip queued as Sprint-1 follow-up.

## Related

- [[../11-wiki/retrieval-k-sweep-small-corpus]] — generalized wiki
- [[../06-Audits/2026-05-19 LongMemEval v0.3 sweep results]] — empirical data + driver code
- [[2026-05-12 sv-7 continuous evaluation arch]] — SV B-3 sprint context
- [[../11-wiki/reranker-cost-optimization-not-size]] — sibling retrieval-tuning lesson
