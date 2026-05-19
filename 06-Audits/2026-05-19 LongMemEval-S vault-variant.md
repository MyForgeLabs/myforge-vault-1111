---
name: LongMemEval-S vault-variant baseline
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [audit, eval, longmemeval, recall, sv-b-2]
---

# LongMemEval-S vault-variant baseline

Recall@5 **46.00%** (23/50)

Inspired by the `agentmemory` LongMemEval-S benchmark (500-Q, 95.2% R@5).
This is a smaller, fully-local variant: questions are deterministically mined
from session-MD files; expected source = the session the query was mined from.

## Setup

- Corpus: `08-Sessions/` (80 sessions)
- Sample: 50 random sessions (seed=42)
- Queries per session: 1
- Total queries: 50
- Search backend: `vault-search --mode cosine-only --top-k 5` (Memgraph native vector-index, bge-m3)
- Query mining: top-IDF unigram + nearest co-occurring non-stopword on the same line

## Result

| Metric | Value |
|---|---|
| Recall@5 | **46.00%** |
| Hits | 23 / 50 |
| `agentmemory` LongMemEval-S R@5 reference | 95.2% |
| Gap to reference | +49.2 pp |

## Per-query trace

Full JSONL: `06-Audits/2026-05-19 LongMemEval-S vault-variant.jsonl`

### Sample (first 10)

| # | Query | Expected | Hit | Top-1 cos |
|---|---|---|---|---|
| 1 | `propagate-session bash-patch` | `08-Sessions/2026-04-30-deploy-smoke-teszt.md` | ✗ | 0.575 |
| 2 | `skills skills-count` | `08-Sessions/2026-04-23-obsidian-vault-rendbetetele.md` | ✗ | 0.590 |
| 3 | `zoli akcionálható-e` | `08-Sessions/2026-05-10-kgc-weboldal.md` | ✗ | 0.493 |
| 4 | `rebase retroaktív` | `08-Sessions/2026-05-09-vault-maintenance.md` | ✓ | 0.549 |
| 5 | `balance atti` | `08-Sessions/2026-05-08-kinda-project-folytasa.md` | ✓ | 0.610 |
| 6 | `elementor theme-foxy` | `08-Sessions/2026-05-02-foxxi-weboldal.md` | ✓ | 0.667 |
| 7 | `atti helyreállítása` | `08-Sessions/2026-04-29-wellbeing.md` | ✓ | 0.574 |
| 8 | `uses predicate-vocab` | `08-Sessions/2026-05-17-obsidian-vault-2.md` | ✗ | 0.484 |
| 9 | `player screen-id` | `08-Sessions/2026-04-27-kgc-marketing-kivetitok.md` | ✗ | 0.571 |
| 10 | `memgraph emelünk` | `08-Sessions/2026-05-13-sv-functional-payoff.md` | ✗ | 0.620 |

## Interpretation

- This benchmark sits at the easier end of the difficulty spectrum:
  the expected source is by construction the document the query
  was mined from, so it always exists in the index. R@5 measures
  whether the retriever surfaces *that exact source* in the top-5,
  not whether it can answer an unseen question.
- `agentmemory`'s 95.2% R@5 is over LongMemEval-S, a hand-curated
  long-context QA set; direct comparison is not apples-to-apples.
  We report it as a north-star, not a target.
- Failures usually fall into three buckets: (a) the mined query is
  too generic (high-DF token slipped through stopword filter),
  (b) the same phrase appears in another doc that is more central
  to the index, (c) the session is a stub with <6 salient tokens.

## Next

- Re-run after enabling `--mode smart-rerank` (default) — expected
  +5–10 pp on the failures whose top-1 cosine was 0.55–0.70.
- Wire the script into `vault-session-eval-run`'s weekly cron
  alongside the L1 stuck-detector for trend-tracking.
- Consider a second tier of queries mined from ADR/wiki for
  cross-source-type recall.
