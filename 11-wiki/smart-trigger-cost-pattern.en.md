---
name: smart-trigger-cost-pattern
description: Two-phase pipeline pattern - cheap+fast baseline run, expensive model only on low-confidence cases - 5-10x cost-savings reusable for LLM-judges/rerankers/expensive-evaluators
type: wiki
lang: en
translated_from: smart-trigger-cost-pattern
created: 2026-05-17
updated: 2026-05-18
tags: ["#type/wiki", "cost-optimization", "llm-pipeline", "performance"]
---

# Smart-trigger cost pattern

## The problem

Many eval/retrieval pipelines have an **expensive second-pass model** (cross-encoder reranker, NLI-judge, multi-judge ensemble) which, run on every query/bullet, adds 5-25× slowdown. **But:** most queries/bullets are unambiguous — a single cosine retrieval / G-Eval verdict is enough.

## The pattern

**Two-phase pipeline:**

1. **Fast baseline (cheap, fast)** always runs. e.g. cosine top-K (165ms), single-pass G-Eval (200ms)
2. **Expensive second pass** runs only when the fast baseline's confidence < threshold. e.g. reranker, NLI-judge, multi-judge

The trigger threshold is tunable. Typical defaults: ~0.65 on cosine score, ~0.85 on G-Eval.

## Live examples

### Reranker smart-trigger

- Cosine-only baseline: 154ms / query
- Pure reranker (bge-reranker-v2-m3): 13789ms / query (RAM pressure)
- **Smart-rerank** (cosine + reranker only if max_score < 0.65): **8333ms average** = 1.65× speedup vs pure
- Skipped queries (max > 0.65) get **89-106× speedup**
- 5-query bench: 2/5 skipped, 3/5 triggered

ENV: `RERANK_TRIGGER_THRESHOLD=0.65`

### NLI Layer 2.5

- G-Eval Layer-2 always runs (cheap, 200ms)
- NLI-judge (DeBERTa-v3, 530-600ms) **only on auto-prop candidates** (route="auto-prop"), not on batch-preview or discard
- Cost savings: ~80% (NLI does not run on discards)

ENV: `VAULT_NLI_VETO=0` (default OFF, opt-in shadow-mode)

## Tuning the threshold

- Empirical: run 30-50 samples through the baseline, look at the histogram. A bimodal distribution (low-high scores) → the dip-point between the two modes is a good threshold
- Recommended defaults: cosine 0.65 (general retrieval), G-Eval 0.85 (high-confidence), NLI threshold 0.5 (entailment-prob)
- Adaptive: a weekly monitor cron logs the auto-rate / revert-rate and recommends threshold tuning

## When to apply

- ✅ Two-model pipelines (cheap baseline + expensive second-pass)
- ✅ Latency-sensitive workflows (interactive, real-time)
- ✅ Cost-sensitive workflows (LLM-judge per-token)
- ✅ Imbalanced distribution (majority "easy", minority "hard")

## Live ROI table

| Pipeline | Cheap baseline | Expensive second-pass | Trigger | Cost savings |
|---|---|---|---|---|
| Vault-search rerank | cosine (sub-ms) | bge-reranker-v2-m3 cross-enc | max-cos < 0.65 | 1.65× (3/5 trigger 2/5 skip) |
| Crystallize Layer 2.5 | G-Eval verdict | NLI DeBERTa entailment | only on auto-prop candidate | 5-9× (5/9 discards skipped) |
| Crystallize Layer 2.6 | NLI verdict | coherence NLI×5 neighbours | only on auto-prop post-NLI | 9× (5/9 discards + 0/4 NLI-veto skipped) |
| **OmniRoute cascade (3-tier)** | rule-based / cosine | claude-code subagent | confidence < threshold per-level | **36.4% auto vs deep-only** |
| **SelfCheckGPT N=3** | G-Eval single | 3× G-Eval re-run (Manakul 2023) | borderline-band 0.70-0.85 | **6× vs naive-N=3-all** |

The 3-tier cascade (fast / balanced / deep) and the borderline-band trigger are two **sub-patterns** on top of the 2-phase base. Both reproducible at $0 cost with claude-code subagent fanout.

## Related

- [[g-eval-bias-mitigation-pattern]] — G-Eval bias mitigation reduces auto-prop, making smart-trigger more effective
- [[sv-01-memory-architecture]] — search architecture research
- [[multi-layer-safety-gate]] — related safety pattern
- [[sprint-day-0-skeleton-first]] — related skeleton pattern
- [[layered-eval-cascading-pattern]] — multi-tier cascading (G-Eval → NLI → Coherence)
