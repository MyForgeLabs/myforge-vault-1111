---
name: smart-trigger-cost-pattern
description: Két-fázisú pipeline minta - gyors+olcsó baseline futtatás, drága modell csak alacsony-confidence eseten - 5-10x cost-savings reusable LLM-judge/reranker/expensive-evaluator-okhoz
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "cost-optimization", "llm-pipeline", "performance"]
---

# Smart-trigger cost pattern

## A probléma

Sok eval/retrieval-pipeline-ben **drága második-pass modell** van (cross-encoder reranker, NLI-judge, multi-judge ensemble), amit minden query/bullet-ra futtatva 5-25× lassítást ad. **De: a queryk/bulletek többsége egyértelmű** — egyszerű cosine retrieval / G-Eval verdict elég.

## A pattern

**Két-fázisú pipeline:**

1. **Fast-baseline (cheap, fast)** mindig fut. Pl. cosine cosine top-K (165ms), single-pass G-Eval (200ms)
2. **Expensive-second-pass** csak akkor, ha a fast-baseline confidence < threshold. Pl. reranker, NLI-judge, multi-judge

A trigger-threshold tunable. Default ~0.65 a cosine score-on, ~0.85 a G-Eval-en.

## Élő példák (2026-05-17-obsidian-vault-2 session)

### Reranker smart-trigger (B-2)

- Cosine-only baseline: 154ms / query
- Pure reranker (bge-reranker-v2-m3): 13789ms / query (RAM-pressure)
- **Smart-rerank** (cosine + reranker csak ha max_score<0.65): **8333ms átlag** = 1.65× speedup vs pure
- Skipped queries (max>0.65) **89-106× speedup**
- 5-query bench: 2/5 skipped (session-pointer 0.668, nano-banana 0.726), 3/5 triggered

ENV: `RERANK_TRIGGER_THRESHOLD=0.65`

### NLI Layer 2.5 (B-1+B-3)

- G-Eval Layer-2 mindig fut (cheap, 200ms)
- NLI-judge (DeBERTa-v3, 530-600ms) **csak auto-prop kandidátra** (route="auto-prop" already), nem batch-preview vagy discard-ra
- Cost-savings: ~80% (NLI nem fut a discard-okra)

ENV: `VAULT_NLI_VETO=0` (default OFF, opt-in shadow-mode)

## A tunable threshold beállítása

- Empirikus: futtass 30-50 sample-t baseline-on, nézd meg a hisztogramot. A bimodális distribution alacsony-magas score-okra → a két mód közötti dip-pont = jó threshold
- Default ajánlott: cosine 0.65 (general retrieval), G-Eval 0.85 (high-confidence), NLI threshold 0.5 (entailment-prob)
- Adaptive: heti `vault-crystallize-monitor` cron loggolja az auto-rate-et / revert-rate-et, és ajánl threshold-finomítást

## Mikor érdemes alkalmazni

- ✅ Két-modellű pipeline (cheap baseline + expensive second-pass)
- ✅ Latency-sensitive workflow (interaktív, real-time)
- ✅ Cost-sensitive workflow (LLM-judge per-token)
- ✅ Imbalanced distribution (a többség "easy", kisebbség "hard")

## Élő ROI-tábla

| Pipeline | Cheap baseline | Expensive second-pass | Trigger | Cost-savings | Forrás |
|---|---|---|---|---|---|
| Vault-search rerank | cosine (sub-ms) | bge-reranker-v2-m3 cross-enc | max-cos < 0.65 | 1.65× (3/5 trigger 2/5 skip) | [[../06-Audits/2026-05-17 reranker smart-trigger]] |
| Crystallize Layer 2.5 | G-Eval verdict | NLI DeBERTa entailment | csak auto-prop kandidátra | 5-9× (5/9 discard skipped) | [[../06-Audits/2026-05-17 NLI Layer 2.5 integration]] |
| Crystallize Layer 2.6 | NLI verdict | vault-coherence-check NLI×5 neighbours | csak auto-prop post-NLI | 9× (5/9 discard + 0/4 NLI-veto skipped) | [[../06-Audits/2026-05-17 Layer 2.6 vault-coherence integration]] |
| **OmniRoute cascade (3-szintű)** | rule-based / cosine | claude-code subagent | confidence < threshold per-level | **36.4% auto vs deep-only** | [[../06-Audits/2026-05-17 OmniRoute cascade skeleton]] |
| **SelfCheckGPT N=3** | G-Eval single | 3× G-Eval re-run (Manakul 2023) | borderline-band 0.70-0.85 | **6× vs naiv-N=3-all** | [[../06-Audits/2026-05-17 SelfCheckGPT borderline-filter skeleton]] |

A 3-szintű cascade (fast / balanced / deep) + a borderline-band-trigger két új **alminta** a 2-fázisú alapra. Mindkettő reproducible $0 cost claude-code subagent-fanout-tal.

## Kapcsolódó

- [[g-eval-bias-mitigation-pattern]] — G-Eval bias-mitigation, ami önmagában csökkenti az auto-prop-ot, így a smart-trigger jobban érvényesül
- [[sv-01-memory-architecture]] — B-2 research
- [[multi-layer-safety-gate]] — kapcsolódó safety-pattern
- [[sprint-day-0-skeleton-first]] — kapcsolódó skeleton-pattern
- [[layered-eval-cascading-pattern]] — több-szintű cascading (G-Eval → NLI → Coherence)
