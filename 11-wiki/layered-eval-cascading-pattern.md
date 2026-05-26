---
name: layered-eval-cascading-pattern
description: Több-szintű eval-pipeline minta (G-Eval → NLI → Coherence → SelfCheck) cost-aware cascading-gel - minden következő layer csak az előző layer pozitívra fut, total cost-savings 5-30x reusable
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "llm-evaluation", "cost-optimization", "crystallization", "pipeline"]
status: stable
---

# Layered eval-cascading pattern

## A probléma

A B-1 Crystallization pipeline-ban szándékos a több-szintű quality-gate: **G-Eval (Layer 2) + NLI (Layer 2.5) + Coherence (Layer 2.6) + SelfCheckGPT (Layer 2.7)**. Naivan minden layer minden bullet-en fut → cost-explosion. Az SV B-1 mégis 0 latency-overhead-del fut shadow-on, mert minden következő layer **csak az előző layer pozitívra (auto-prop kandidátra) fut**.

## A pattern

```
                          ┌──────────────────────────────────┐
   Bullet ───► Layer 2 G-Eval (1×)                           │
                  │                                          │
                  ├── conf < 0.95 ──► batch-preview (STOP)   │
                  └── conf ≥ 0.95 (auto-prop kandidát)       │
                       │                                     │
                       ▼                                     │
                  Layer 2.5 NLI (1×) — csak ha pozitív       │
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
                            (csak borderline 0.70-0.85)
                                 │
                                 ├── disagreement ──► batch-preview
                                 └── agreement ──► AUTO-PROP ✓
```

**Kulcs-trükk:** minden layer cost = `prev_pass_count × layer_unit_cost`, NEM `total_bullet_count × layer_unit_cost`. Ha a pozitív-arány 30%, akkor Layer 2.5 cost 30%-a a naiv-mindenkin-futás-cost-jának. Ha mindegyik layer 30%-ot szűr, 4-layer pipeline cost ~30^3 = 2.7% (nem 100%).

## Élő SV B-1 cascade (2026-05-17 verified)

| Layer | Cost | Trigger | Output | Cost-savings vs naiv |
|---|---|---|---|---|
| Layer 2 G-Eval | 1× subagent | minden bullet | conf + verdict | (baseline) |
| Layer 2.5 NLI | 1× DeBERTa-440MB | csak auto-prop | entailment/contradiction | **5-9×** (5/9 discard skip) |
| Layer 2.6 Coherence | 5× NLI per bullet (neighbours) | csak auto-prop post-NLI | max_contra_prob | **9×** (5/9 discard + 0/4 NLI-veto skip) |
| Layer 2.7 SelfCheckGPT | 3× G-Eval | csak borderline 0.70-0.85 | variance/agreement | **6×** vs naiv-all-N=3 |

**Total cost ratio (B-1 W21 baseline):** ha 10 bullet, 4 auto-prop, 1 borderline → `10 + 4 + 4×5 + 1×3 = 37 unit` vs naiv `10 + 10 + 10×5 + 10×3 = 100 unit` = **2.7× cost-savings**.

## Tervezési alapelvek

1. **Cheapest layer first** — G-Eval olcsó (1× subagent, ~10s/bullet), NLI dráhg (5×~10s), Coherence dráhg (5×5 NLI), SelfCheck dráhg (3× G-Eval).
2. **Each layer must be discriminative** — ha 100% bullet átmegy, a layer felesleges. Cél: minden layer 20-50%-ot szűrjön.
3. **Fail-open default** — ha layer timeout/error, NE blokkold a pipeline-t; csak audit-log + opt-in re-run.
4. **Per-layer ENV-flag** — minden új layer `VAULT_<LAYER>=1` opt-in, default OFF; default-shift csak 2+ session 0-FP után.
5. **Audit-log konzisztencia** — minden layer 4-6 audit-mező a `crystallize-log.jsonl`-be (status, score, downgrade-flag, latency_ms).

## Mikor érdemes alkalmazni

- ✅ Multi-pass quality-gate ahol az utolsó pass dráhg (LLM-judge, NLI, cross-encoder)
- ✅ Imbalanced distribution (a többség "easy", kisebbség "hard" — kevés borderline)
- ✅ Production-pipeline ahol a Pass-recall + Pass-precision balance kritikus
- ❌ Ha minden bullet borderline (no distribution-skew) — cascading nem hoz savings-t

## Trade-off

- ⚠️ Komplexitás-növekedés: minden layer +500-1000 sor kód, +6 audit-mező, +1 ENV-flag
- ⚠️ Latency-additivity: ha 4 layer mind 2s, total = 8s (a baseline 2s helyett) — interaktív flow-hoz tiltott
- ✅ Cost-savings 3-30× a layer-count függvényében
- ✅ Risk-stratification: clear-Fail Layer 2-ben elkapva, edge-case Layer 2.6/2.7-ben

## Kapcsolódó

- [[smart-trigger-cost-pattern]] — 2-fázisú baseline-of-the-pattern
- [[multi-layer-safety-gate]] — kapcsolódó safety-aspect (DDD a write-side-en)
- [[g-eval-bias-mitigation-pattern]] — Layer 2 prompt-mitigation
- [[Crystallization-protocol]] — host protokoll
- [[sv-05-crystallization-automation]] — B-1 sprint research
- [[sv-07-continuous-evaluation]] — B-3 NLI Layer 2.5 forrás
