---
name: LongMemEval-S vault-variant v0.2
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit"]
tag_backfill: 2026-05-19
---
# LongMemEval-S vault-variant — v0.2

Benchmark-driven optimization sprint following v0.1 baseline (R@5=46%).

## Configurations

| Label | Mode | Hybrid | Subset | Recall@5 | Hits | Elapsed |
|---|---|---|---|---|---|---|
| A:cosine | `cosine-only` | no | full | **31.31%** | 31/99 | 17.9s |
| C:hybrid | `hybrid` | yes | full | **67.68%** | 67/99 | 50.2s |
| B:smart-rerank | `smart-rerank` | no | subset | **40.00%** | 8/20 | 415.6s |

## Setup

- Corpus: `08-Sessions/` (80 sessions)
- Queries: **99** (50 IDF-mined + 49 hand-curated cross-session-distinct)
- Seed: 42 (IDF), 43 (curated)
- top-K: 5
- Backend: `vault-search` (Memgraph native vector-index, bge-m3)

## v0.1 vs v0.2 delta

- **v0.1 baseline (50-Q IDF, cosine-only):** R@5 = 46.00%
- **v0.2 cosine-only (100-Q):** R@5 = 31.31% (31/99)
  - IDF-only segment (50-Q): 46.00%
  - Hand-curated segment (49-Q): 16.33%
- **v0.2 hybrid (RRF, BM25+semantic, 100-Q):** R@5 = 67.68% (67/99)
  - IDF-only segment (50-Q): 68.00%
  - Hand-curated segment (49-Q): 67.35%
- **v0.2 smart-rerank (subset 20-Q):** R@5 = 40.00% (8/20)

## Spot-check (5 representative)

| # | Query | Expected | Cosine top-5 hit? | Hybrid top-5 hit? |
|---|---|---|---|---|
| 1 | `propagate-session bash-patch` | `08-Sessions/2026-04-30-deploy-smoke-teszt.md` | ✗ | ✓ |
| 2 | `sv-meta sessions` | `08-Sessions/Index.md` | ✗ | ✗ |
| 3 | `domi litespeed-szabályok` | `08-Sessions/2026-05-10-foxxi-weboldal-2.md` | ✗ | ✗ |
| 4 | `25-30 ütemmel` | `08-Sessions/2026-05-13-sv-day0-cascade.md` | ✗ | ✓ |
| 5 | `ai-képek ízléses` | `08-Sessions/2026-05-08-foxxi-rebrand-iteracio2.md` | ✗ | ✓ |

## Per-fix contribution (apples-to-apples on first-20-Q subset)

| Config | R@5 on same 20-Q | Delta vs cosine-only |
|---|---|---|
| A: cosine-only | 40.0% (8/20) | — |
| B: smart-rerank | 40.0% (8/20) | **+0 pp** |
| C: hybrid (BM25+RRF) | 60.0% (12/20) | **+20 pp** |

Hybrid alone delivers the entire optimization win; smart-rerank is a no-op
on this query distribution. Mechanism: rerank operates on the dense top-30
fetched first-pass, so if the gold doc is not in that pool, rerank cannot
recover it. BM25 lexical scoring fetches a *different* pool, so the RRF
fusion adds genuinely new candidates.

## Headline result (full 100-Q)

| | v0.1 | v0.2 |
|---|---|---|
| Recall@5 | 46.00% (50-Q, IDF-only, cosine) | **67.68%** (99-Q, mixed mining, hybrid) |
| Target | — | 70%+ |
| Status | baseline | **misses target by 2.3 pp** |

## Interpretation

- **Hybrid RRF is the entire delta.** BM25 + semantic fused via RRF
  (latency ~0.5 s/query, no GPU) closes the gap from 31% (cosine-only on
  the harder 99-Q set) to 67.68%. The hand-curated cross-session-distinct
  segment in particular jumps from 16.33% → 67.35%, validating that the
  v0.1 result was inflated by lexical-coincidence in IDF pairs.
- **Smart-rerank failed to help here.** On the first-20-Q subset it scored
  identically to cosine-only (8/20). The cross-encoder reorders the dense
  first-pass top-30 but cannot insert candidates that aren't already in
  that pool — which is exactly the failure mode that hybrid fixes.
- **The hand-curated mining strategy** (anchors with df≤3 across the
  corpus, paired with rare tokens from the same heading) is meaningfully
  harder than v0.1's same-line IDF pairs. Same retriever (cosine-only)
  drops from 46% → 16% on this segment.
- **vs agentmemory 95.2%:** not apples-to-apples (their queries are
  hand-curated long-context QA with model-graded answers; ours is
  mined-from-source path-recall), but the gap is ~27 pp at v0.2.
  Closing it requires either (a) a more discriminative retriever
  (e.g. ColBERT-style late-interaction), (b) wider first-pass (dense
  top-100 → rerank), or (c) easier queries (LongMemEval-S itself
  has ground-truth lifted from sessions, ours has nothing curated).

## Honest verdict

- **Target 70% not hit, but the engineering call is fair: 67.68% is
  within 2.3 pp of target on a strictly harder query-set than v0.1.**
- A trivial path to ≥70%: keep the IDF-only segment (which scored 68%
  alone) and drop the most pathological 5-10% of hand-curated stubs.
  Doing so would be benchmark-gaming; we don't.
- A real path to ≥70%: hybrid-fetch-K bump from 50 → 100 + reranker
  on the fused pool (v0.3 below). Estimated +3-5 pp.

## v0.3 roadmap

1. **Hybrid + rerank fusion pool** (priority): pull top-50 dense + top-50
   BM25, RRF-fuse to 100, then cross-encoder top-K — pulls in rerank
   benefit on candidates BM25 surfaces. Est +3-5 pp.
2. **Hybrid-fetch-K sweep**: try k=100/150 to see if simple recall-bump
   matches reranker gain at lower latency.
3. **Mine cross-source-type queries**: ADR + wiki + session triplets,
   exercise multi-namespace vector-index (Chunk/SkillChunk/Entity)
   instead of session-only.
4. **Answerable-QA evaluator (LLM-judge)**: closer to LongMemEval-S
   methodology — LLM answers from top-5 snippets, compare to gold.
   Eliminates the "expected source path" proxy.
5. **Stuck-detector cron integration**: weekly trend MD with 4-week
   recall-history; alarms on >5pp regression.
6. **Bench-isolate by mining type**: split IDF / heading-derived /
   filename-derived metrics so regressions in one pipeline are visible.
