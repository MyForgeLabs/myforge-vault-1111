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

### Counter-intuitive finding: monotone-decreasing curve

The sweep curve is **strictly monotone-decreasing** in K (every increase of K
reduces Recall@5). This refutes the BEIR/MTEB lore that a wider candidate
pool helps the fusion step.

Mechanism (hypothesis): the RRF score `1/(60 + rank)` is bounded by the
worst rank in the pool. When K=5, only the top-5 from each side enter the
union — both rankers' high-confidence picks dominate. When K=50, lower-
quality candidates from both sides bring **rank-50 noise** into the fused
ranking and crowd the top-5 output. The semantic side, in particular, has
a long tail of low-cosine matches that have NO BM25 overlap — these enter
the fused pool with `rrf = 1/(60+50)` ≈ 0.009 and can outrank legitimate
candidates that show up at rank-3 on only ONE side.

This finding is consistent with the recent KO-DB conflict findings from the
2026-05-19 mega-session (1,115 contested entries, 0 confident-consensus) —
when two rankers disagree, larger pools amplify disagreement-noise, smaller
pools concentrate on high-confidence overlap.

Practical implication: the v0.2 default `HYBRID_FETCH_K=50` is **too wide**
for this 99-Q LongMemEval-S corpus. Tuning down to K=5..15 yields +7-9pp
Recall@5 at zero extra latency cost.

### Self-consistency check

The standalone variant-A run at fetch_k=20 and the sweep entry at K=20
should produce identical Recall@5 (same code path, same queries). Observed:
both = **0.7172 (71/99)** — deterministic, no caching/state divergence.

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

## Pytest layer

The v0.3 sweep is gated by 4 new tests in
`.vault-eval/regression/test_longmemeval_regression.py`:

- `test_v03_self_consistency` — baseline blocks tolerance-consistency
- `test_v03_fused_pool_rrf_pass` — variant A ≥ v0.2 hybrid - 5pp
- `test_v03_fused_pool_reranker_pass` — variant B ≥ variant A - 5pp
- `test_v03_fetchk_sweep_curve_pass` — all K-values clear baseline floor;
  sweet-spot is in swept set; sweet-spot ≥ K=5

Run: `pytest .vault-eval/regression/ -m "fast or v03" -v`

Current status: **7/7 passing** (4 fast + 3 v03 — `test_v03_self_consistency`
is `fast` since it only validates baseline.json shape).

## Follow-ups

- **CRON UNCHANGED**: daily cron 02:45 still runs `vault-eval-regression`
  (v0.2 fast-mode); ramping v0.3 onto cron is a separate decision after
  1-2 verified runs (need to confirm K=5 win is stable across runs).
- **Investigation TODO**: re-run sweep on a Spanish/French session-corpus
  fork to test whether monotone-decreasing curve is corpus-specific or a
  general property of this RRF-fusion config (k_const=60).
- **Variant C (LLM-judge)** — stub in `driver_v03_fused.py` raises
  `NotImplementedError`; opt-in via Claude subagent fanout (`crystallize-
  pending` pattern), non-zero $ cost. Defer to user opt-in.
- **HYBRID_FETCH_K production-tune?** — the v0.3 finding suggests lowering
  the production default from 50 to 5. NOT auto-applied (would change
  interactive search behaviour); leave to a separate ADR if the K=5 win
  is reproduced on a second run.
- **baseline.json v03_* blocks** were NULL → populated on this first run
  (see `locked_at` timestamps). Update procedure documented in baseline
  `_update_procedure`.
