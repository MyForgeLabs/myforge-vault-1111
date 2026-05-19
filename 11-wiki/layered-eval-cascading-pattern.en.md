---
name: layered-eval-cascading-pattern
description: Multi-tier eval-pipeline pattern (G-Eval → NLI → Coherence → SelfCheck) with cost-aware cascading - each subsequent layer only runs on positives from the previous layer, total cost-savings 5-30x reusable
type: wiki
lang: en
translated_from: layered-eval-cascading-pattern
created: 2026-05-17
updated: 2026-05-18
tags: ["#type/wiki", "llm-evaluation", "cost-optimization", "crystallization", "pipeline"]
status: stable
---

# Layered eval-cascading pattern

## 🎧 Audio overview

- **Deep-dive podcast** (NotebookLM 2-host, ~5 min, EN): [layered-eval-cascading-pattern.en-podcast.mp3](../.vault-nb/audio-overviews/layered-eval-cascading-pattern.en-podcast.mp3) (38 MB) — *"Slash AI evaluation costs with layered cascades"*

## The problem

A robust crystallization or quality-gate pipeline often stacks multiple LLM-based evaluators: **G-Eval (Layer 2) + NLI (Layer 2.5) + Coherence (Layer 2.6) + SelfCheckGPT (Layer 2.7)**. Running every layer on every input bullet leads to cost explosion. In our production deployment, however, the pipeline runs with near-zero latency overhead because **each subsequent layer only fires on the previous layer's positive (auto-prop candidate)**.

## The pattern

```
                          ┌──────────────────────────────────┐
   Bullet ───► Layer 2 G-Eval (1×)                           │
                  │                                          │
                  ├── conf < 0.95 ──► batch-preview (STOP)   │
                  └── conf ≥ 0.95 (auto-prop candidate)      │
                       │                                     │
                       ▼                                     │
                  Layer 2.5 NLI (1×) — only if positive      │
                       │                                     │
                       ├── contradiction ──► batch-preview   │
                       └── entail/neutral                    │
                            │                                │
                            ▼                                │
                       Layer 2.6 Coherence (NLI×N neighbours)│
                            │                                │
                            ├── conflict ──► batch-preview   │
                            └── OK                           │
                                 │                           │
                                 ▼                           │
                            Layer 2.7 SelfCheckGPT (3×) ─────┘
                            (only borderline 0.70-0.85)
                                 │
                                 ├── disagreement ──► batch-preview
                                 └── agreement ──► AUTO-PROP ✓
```

**Key insight:** each layer's cost = `prev_pass_count × layer_unit_cost`, NOT `total_bullet_count × layer_unit_cost`. If the positive rate is 30%, Layer 2.5 costs 30% of the naive-every-bullet baseline. If every layer filters 30%, a 4-layer pipeline costs ~30^3 = 2.7% (not 100%).

## Live cascade (verified 2026-05-17)

| Layer | Cost | Trigger | Output | Cost savings vs naive |
|---|---|---|---|---|
| Layer 2 G-Eval | 1× subagent | every bullet | conf + verdict | (baseline) |
| Layer 2.5 NLI | 1× DeBERTa-440MB | only auto-prop | entailment/contradiction | **5-9×** (5/9 discards skipped) |
| Layer 2.6 Coherence | 5× NLI per bullet (neighbours) | only auto-prop post-NLI | max_contra_prob | **9×** (5/9 discards + 0/4 NLI-veto skipped) |
| Layer 2.7 SelfCheckGPT | 3× G-Eval | only borderline 0.70-0.85 | variance/agreement | **6×** vs naive-all-N=3 |

**Total cost ratio (baseline):** for 10 bullets, 4 auto-prop, 1 borderline → `10 + 4 + 4×5 + 1×3 = 37 units` vs naive `10 + 10 + 10×5 + 10×3 = 100 units` = **2.7× cost savings**.

## Design principles

1. **Cheapest layer first** — G-Eval is cheap (1× subagent, ~10s/bullet), NLI is expensive (5× ~10s), Coherence is more expensive (5×5 NLI), SelfCheck is most expensive (3× G-Eval).
2. **Each layer must be discriminative** — if 100% of inputs pass, the layer is useless. Aim for 20-50% filtering per layer.
3. **Fail-open default** — if a layer times out or errors, do NOT block the pipeline; just audit-log and offer opt-in re-run.
4. **Per-layer ENV-flag** — every new layer ships behind `VAULT_<LAYER>=1` opt-in, default OFF; flip default only after 2+ runs with 0 false-positives.
5. **Audit-log consistency** — each layer writes 4-6 audit fields to a structured log (status, score, downgrade-flag, latency_ms).

## When to apply

- ✅ Multi-pass quality-gate where the final pass is expensive (LLM-judge, NLI, cross-encoder)
- ✅ Imbalanced distribution (majority "easy", minority "hard" — few borderline)
- ✅ Production pipelines where Pass-recall + Pass-precision balance is critical
- ❌ If every input is borderline (no distribution skew) — cascading produces no savings

## Trade-offs

- ⚠️ Complexity increase: each layer adds 500-1000 LOC, +6 audit fields, +1 ENV-flag
- ⚠️ Latency additivity: 4 layers at 2s each = 8s total (vs 2s baseline) — forbidden for interactive flows
- ✅ Cost savings 3-30× depending on layer count
- ✅ Risk stratification: clear-Fail caught at Layer 2, edge cases caught at Layer 2.6/2.7

## Related

- [[smart-trigger-cost-pattern]] — 2-phase baseline of this pattern
- [[multi-layer-safety-gate]] — related safety aspect (defense-in-depth on the write side)
- [[g-eval-bias-mitigation-pattern]] — Layer 2 prompt-mitigation
- [[Crystallization-protocol]] — host protocol
- [[sv-05-crystallization-automation]] — crystallization research axis
- [[sv-07-continuous-evaluation]] — NLI Layer 2.5 source
