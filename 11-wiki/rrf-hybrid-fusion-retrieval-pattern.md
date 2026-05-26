---
name: rrf-hybrid-fusion-retrieval-pattern
type: wiki
created: 2026-05-20
updated: 2026-05-20
agent: claude
tags: ["#type/wiki", "#retrieval", "#rrf", "#hybrid-fusion", "#playbook"]
---

# RRF hybrid-fusion retrieval pattern

> [!info] When to apply
> Have two (or N) retrieval systems with **complementary errors** (e.g., 30% both-hit + 20% only-A + 20% only-B + 30% neither = union > each-alone)? **Reciprocal Rank Fusion** (RRF, Cormack et al. 2009) merges their ranked lists into one production-grade top-K. **Always worth piloting** when overlap < 60% and union-ceiling > each-alone-recall by 15pp+.

## A pattern

```
Query
 ├─→ System A  (top-N candidates ranked) ─┐
 ├─→ System B  (top-N candidates ranked) ─┤
 ├─→ (System C, D, ... optional)         ─┤
 │                                         ├─→ RRF merge → top-K
 │     score(d) = Σ_systems 1/(k_rrf + rank_in_system + 1)
 │                                         │
 └─→ Re-rank by score, return top-K       ─┘
```

**Default constants** (Cormack-style, validated 2026-05-20 on vault):
- `k_rrf = 60` (1-100 range insensitive on small corpus)
- `fetch_k = 20` per-system (sweet-spot — see "Fetch-K sweep" below)
- `top_k = 5` (display window)

## Why it works

Two retrieval-systems with **azonos recall** (e.g., 55-55%) but **különböző hibák** (28% both-hit + 22/22% only-one) compose: the union of their top-K lists covers ~72% of ground-truth, which RRF can extract because it **re-ranks by mutual agreement** (a doc in both lists scores higher than a doc in one).

## Concrete result — vault-search + agentmemory (2026-05-20)

| Configuration | Recall@5 |
|---|---|
| vault-search alone (BM25+bge-m3 hybrid) | 54.5% |
| agentmemory alone (smart-search noop) | 76.4% |
| **RRF fusion (k_rrf=60, fetch-k=20)** | **77.5%** average · **85.39%** best · **69.66%** worst |

**Lift vs vault-search alone**: +23pp average, +30pp best-case.
**Lift vs agentmemory alone**: +1pp (close — agentmemory the stronger single), +9pp best.

Methodology-sensitivity: RRF fusion magasabb a "tuning"-query-distribution-on, alacsonyabb a held-out methodology-n. **Production-recall realisztikus: 70-85% sávban** query-mix-től függően.

## Fetch-K sweep — monotone-decreasing pattern over 20

| fetch-K | RRF Recall@5 (n=89, clean setup) |
|---|---|
| 10 | 79.78% |
| **20** | **85.39%** ⭐ sweet-spot |
| 30 | 79.78% |
| 50 | 76.40% (= agentmemory alone, RRF nem nyer) |

Same monotone-decreasing pattern as the [[longmemeval-k5-sweet-spot]] finding (2026-05-19): **több candidate ≠ jobb**. A "wider pool helps fusion" BEIR/MTEB-lore **NEM áll** a vault-corpus-on. fetch-k=20 a sweet-spot.

## When NOT to use

| Anti-pattern | Why |
|---|---|
| Single retrieval-system available | RRF needs ≥2 ranked lists |
| Systems with HIGH overlap (>70% both-hit) | Marginal lift, latency-cost not worth it |
| Realtime-strict (<200ms) requirements | RRF adds the slower system's latency on top of the faster (parallel-call possible, sequential-call not) |
| Per-system tuning impossible | RRF doesn't help if both systems are equally bad on the query-distribution |
| Result-set size unknown / unbounded | RRF needs fetch-K — define it explicitly |

## Implementation

```python
from collections import defaultdict

def rrf_fuse(lists: list[list[str]], k_rrf: int = 60, top_k: int = 5) -> list[str]:
    """Reciprocal Rank Fusion (Cormack et al. 2009).

    Args:
      lists: list of ranked doc-id lists, one per retrieval-system
      k_rrf: fusion constant (Cormack default 60)
      top_k: result-window
    """
    scores = defaultdict(float)
    for L in lists:
        for rank, doc in enumerate(L):
            if doc:
                scores[doc] += 1.0 / (k_rrf + rank + 1)
    return sorted(scores.keys(), key=lambda d: -scores[d])[:top_k]
```

## Production deployment checklist

- [x] CLI wrapper for end-to-end orchestration (e.g., `vault-search-fusion`)
- [x] Graceful fallback to single-system if one is unreachable
- [x] Per-system fetch-K tunable (sweep before deploy)
- [x] systemd service for persistent ingest-storage (state-loss-recovery)
- [x] Mirror-cron for new content auto-ingest (10-15 min lag acceptable)
- [x] Persistent id→path map (mtime-cached, reload on change)
- [x] JSON output mode for downstream tools
- [x] Cross-validation on held-out methodology (NOT tuning-set)
- [x] Latency budget defined (<200ms strict / <600ms acceptable / >1s bad)

## Source verified

- **Implementation**: `/usr/local/bin/vault-search-fusion` (vault-search + agentmemory RRF wrapper)
- **Cron mirror**: `*/10 * * * * agentmemory-ingest --since-min 15`
- **systemd**: `/etc/systemd/system/agentmemory.service`
- **Benchmark**: 89-Q on vault sessions, 2026-05-20
- **Production audit**: [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]
- **Theoretical foundation**: Cormack, G., Clarke, C., Buettcher, S. (2009). "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods"

## Kapcsolódó

- [[longmemeval-k5-sweet-spot]] — analogue K-sweep monotone-decreasing
- [[hybrid-bm25-semantic-rrf-pattern]] — szűkebb scope (BM25+semantic egy rendszerben)
- [[../06-Audits/2026-05-20 RRF hybrid-fusion pilot — 91 percent R@5 (vault-search + agentmemory)]]
- [[../06-Audits/2026-05-20 agentmemory head-to-head LongMemEval-S R@5 — TIE 52.81 percent, 22pp ensemble-gain potential]]
- [[sv-01-memory-architecture]] — B-2 sprint retrieval-stack
