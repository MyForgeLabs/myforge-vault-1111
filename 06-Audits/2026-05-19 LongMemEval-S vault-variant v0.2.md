---
name: LongMemEval-S vault-variant v0.2
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [audit, eval, longmemeval, recall, sv-b-2, v0.2]
---

# LongMemEval-S vault-variant — v0.2

Benchmark-driven optimization sprint following v0.1 baseline (R@5=46%).

## Configurations

| Label | Mode | Hybrid | Subset | Recall@5 | Hits | Elapsed |
|---|---|---|---|---|---|---|
| A:cosine | `cosine-only` | no | full | **31.31%** | 31/99 | 35.6s |
| C:hybrid | `hybrid` | yes | full | **67.68%** | 67/99 | 58.4s |

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

## Spot-check (5 representative)

| # | Query | Expected | Cosine top-5 hit? | Hybrid top-5 hit? |
|---|---|---|---|---|
| 1 | `propagate-session bash-patch` | `08-Sessions/2026-04-30-deploy-smoke-teszt.md` | ✗ | ✓ |
| 2 | `sv-meta sessions` | `08-Sessions/Index.md` | ✗ | ✗ |
| 3 | `domi litespeed-szabályok` | `08-Sessions/2026-05-10-foxxi-weboldal-2.md` | ✗ | ✗ |
| 4 | `25-30 ütemmel` | `08-Sessions/2026-05-13-sv-day0-cascade.md` | ✗ | ✓ |
| 5 | `ai-képek ízléses` | `08-Sessions/2026-05-08-foxxi-rebrand-iteracio2.md` | ✗ | ✓ |

## Interpretation

- The hand-curated mining strategy (cross-session-distinct anchor +
  heading-derived 2nd token) is intentionally harder than v0.1's same-line
  IDF pairs — it picks sessions whose anchors appear ONLY in that doc,
  testing pure semantic recall rather than lexical coincidence.
- Hybrid RRF (BM25 + semantic) is the cheapest delta — same latency
  envelope as pure cosine (~0.5s/query), no GPU spin-up.
- Smart-rerank is the most expensive (~18s/query for cross-encoder
  BAAI/bge-reranker-v2-m3 on CPU) — only run as 20-Q subset within
  this audit's 6-min budget; full 100-Q rerank-pass deferred to v0.3.
- The agentmemory 95.2% reference is not directly comparable: their
  benchmark uses hand-curated long-context QA with model-graded
  answers, ours uses mined-from-source path-recall. Treat as a star,
  not a target.

## v0.3 roadmap

- Full 100-Q smart-rerank pass (background, ~30 min wallclock).
- 4th config: hybrid + rerank top-50 (RRF fuse → cross-encoder),
  expected +5-10pp on lexical-light queries.
- Mine cross-source-type queries: ADR+wiki+session triplets to test
  the multi-namespace vector-index (Chunk/SkillChunk/Entity).
- Add answerable-QA evaluator: LLM judge answers the question from
  top-5 snippets, compare to expected — closer to LongMemEval-S
  methodology.
- Stuck-detector integration: weekly cron writes a 4-week trend table.
