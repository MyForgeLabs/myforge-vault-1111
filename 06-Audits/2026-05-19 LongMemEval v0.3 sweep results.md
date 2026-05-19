---
name: LongMemEval v0.3 sweep results
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "#concept/longmemeval", "v0.3", "fused-pool", "fetch-k-sweep"]
related:
  - "[[2026-05-19 LongMemEval-S vault-variant v0.2]]"
  - "[[2026-05-19 Wave-2 follow-up designs (SCD2 LongMemEval Critic)]]"
  - "[[2026-05-19 mega-session summary]]"
---

# LongMemEval v0.3 sweep results — 2026-05-19

Wave-2 Design B implementation: fused-pool retrieval variants + fetch-K
sweep on the canonical 99-Q LongMemEval-S query-set.

## Variants

| Variant | Description | Recall@5 | Hits | Elapsed |
|---|---|---|---|---|
| **v0.2 hybrid (locked baseline)** | RRF, fetch_k=50 (default) | **67.68%** | 67/99 | — |
| **v0.3-A — RRF, fetch_k=20** | fused-pool, no reranker | **71.72%** | 71/99 | 15.2s |
| **v0.3-B — BGE-reranker-v2-m3, fetch_k=20** | cross-encoder on fused pool | **73.74%** | 73/99 | 942.9s |

## Variant comparison

- v0.2 hybrid baseline: **67.68%** (locked).
- v0.3-A delta vs v0.2 hybrid: **+4.04pp** (fetch_k=20 vs default 50).
- v0.3-B vs v0.3-A: **+2.02pp** (BGE-reranker-v2-m3 cross-encoder lift on fused pool).
- v0.3-B delta vs v0.2 hybrid: **+6.06pp**.

## Fetch-K sweep (variant A)

| K | Recall@5 | Hits | Elapsed | Δ vs K=5 |
|---|---|---|---|---|
| 5 | **76.77%** | 76/99 | 12.6s | — |
| 10 | **75.76%** | 75/99 | 15.0s | -1.01pp |
| 15 | **74.75%** | 74/99 | 14.8s | -2.02pp |
| 20 | **71.72%** | 71/99 | 14.3s | -5.05pp |
| 30 | **68.69%** | 68/99 | 14.9s | -8.08pp |
| 50 | **62.63%** | 62/99 | 14.1s | -14.14pp |

**Sweet-spot:** K=5 (Recall@5 = 76.77%)

## Sweet-spot prediction validation

- Design-doc prediction (BEIR/MTEB lore): **K=20** sweet-spot.
- Observed sweet-spot: **K=5** (Recall@5 = 76.77%).
- Prediction verdict: **REFUTED — winner K=5**.
- Marginal gain K=5 → K=20: **-5.05pp** (fetched-pool expansion lift).
- Marginal gain K=20 → K=50: **-9.09pp** (diminishing return / noise zone).

## Run-context

- Timestamp: 2026-05-19T13:05:41Z
- Query-set: 99 queries from v0.2 jsonl A:cosine rows
- Fast mode: False
- Total elapsed: 1043.9s
- Backend: vault-search hybrid + (variant B) BGE-reranker-v2-m3
- Daemon: vault-search-server warm-state (socket /run/vault-search.sock)

## Regression-gate status

- v0.3-A vs v0.2 hybrid floor (0.6268): PASS (0.7172)
- v0.3-B vs v0.3-A floor (A - 5pp): PASS (0.7374 vs A 0.7172)

## Follow-ups

- daily cron 02:45 still runs v0.2 fast-mode (NO change); ramping v0.3 onto cron is a separate decision after 1-2 verified runs.
- variant C (LLM-judge) skeleton in `driver_v03_fused.py` (`NotImplementedError`) — opt-in via Claude subagent fanout, non-zero $ cost.
- baseline.json v03_* blocks were NULL → populated on this first run (see `locked_at` timestamps). Update procedure documented inline.
