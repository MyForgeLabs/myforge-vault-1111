---
name: G-Eval scoring-protokoll család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "g-eval", "llm-evaluation", "scoring", "taxonomy", "evergreen", "crystallization"]
---

# G-Eval scoring-protokoll család taxonomy

> [!info] TL;DR
> A vault-ban **13 Concept + 27 wiki-említés** beszél „G-Eval"-ról, de a tényleges használatban a G-Eval **egy scoring-protokoll-család keret-neve**, NEM egy konkrét prompt. A család **5 réteg** + **3 verzió-evolúció** (v0.1 → v0.2 → v0.3) + **2 borderline-resolver** (NLI Layer 2.5, SelfCheckGPT Layer 2.6 coherence-check) keveredik egymás mellett. Ez a wiki disambiguálja melyik réteg mit csinál, mit NEM, és hogyan stack-eljük production-ban.

## Cluster-members (vault Concept-corpus)

| Concept | Réteg / verzió | Forrás |
|---|---|---|
| G-Eval | meta / keret | wiki/sv-05-crystallization-automation |
| G-Eval threshold-routing | Layer 2 routing | wiki/sprint-day-0-skeleton-first |
| G-Eval Chain-of-Thought | scoring-mechanizmus | wiki/sv-05 |
| G-Eval logprob normalization | scoring-mechanizmus | wiki/sv-05 |
| G-Eval factuality sub-score | dimenzió | wiki/sv-05 |
| G-Eval novelty sub-score | dimenzió | wiki/sv-05 |
| G-Eval routing_fit sub-score | dimenzió | wiki/sv-05 |
| G-Eval bias_check | bias-mitigation | wiki/g-eval-bias-mitigation-pattern |
| G-Eval JSON output | output-szerződés | wiki/sv-05 |
| G-Eval v0.3 bias-mitigated | verzió | MEMORY.md + wiki/g-eval-bias-mitigation-pattern |
| KO-DB confidence field | output-mező | ADR/2026-05-12 sv-5 |
| Layer 2 = G-Eval confidence-scoring | architektúra-szint | ADR/2026-05-12 sv-5 |
| SelfCheckGPT semantic consistency | borderline-resolver | wiki/sv-05 |
| NLI tényellenőrzés | borderline-resolver | ADR/2026-05-12 sv-7 |
| Tier-2 Sonnet 4.6 NLI-bíró | borderline-resolver | ADR/2026-05-12 sv-7 |
| Layer 2.5 NLI | borderline-resolver | wiki/nli-hallucination-check-pattern |
| Layer 2.6 coherence-check | borderline-resolver | session/2026-05-17-3 |
| reranker smart-trigger | smart-trigger | MEMORY.md |
| auto-propagation-confidence-gate | downstream | wiki/auto-propagation-confidence-gate |

## A scoring-család 5 rétege

```
Bullet → Layer 0 (filter) → Layer 1 (rule-based) → Layer 2 (G-Eval) → Layer 2.5 (NLI) → Layer 2.6 (coherence) → Layer 3 (auto-prop gate)
```

### Layer 0 — Pre-filter (NEM G-Eval)
- **Mit:** stop-words, min-length, tag-blacklist
- **Cost:** $0 (regex)
- **Output:** drop / pass-through

### Layer 1 — Rule-based scorer (mock G-Eval)
- **Mit:** Python-rule alapján conf-becslés (pl. backtick-density, link-density, named-entity-count)
- **Cost:** $0 (CPU)
- **Output:** conf 0.0–1.0, gyors baseline
- **Production:** `VAULT_CRYSTALLIZE_SCORER=mock` (fallback ha LLM-down)

### Layer 2 — G-Eval LLM-as-judge (a tulajdonképpeni G-Eval)
- **Mit:** Chain-of-Thought form-filling + logprob normalization (lásd [[sv-05-crystallization-automation]])
- **Output:** 3-dimenziós sub-score (factuality / novelty / routing_fit) + bias_check + JSON `{bullet, target, rationale, confidence}`
- **Implementáció:** subagent-fanout (`VAULT_CRYSTALLIZE_SCORER=claude-code`, $0 cost) vagy API (`anthropic`, key-igényes)
- **Bias-mitigation kötelező:** [[g-eval-bias-mitigation-pattern]]

### Layer 2.5 — NLI claim-checker (borderline-resolver)
- **Mit:** DeBERTa-v3-base-mnli-fever-anli entailment-check (bullet ↔ forrás-szöveg)
- **Cost:** $0 CPU (GPU-mentes), 19–80× speedup process-pool-lal
- **Trigger:** conf 0.70–0.90 borderline band-en (NEM minden bullet-re)
- **Részletek:** [[nli-hallucination-check-pattern]] + [[nli-eval-input-completeness-trap]]

### Layer 2.6 — Coherence-check (cross-bullet)
- **Mit:** ugyanabban a sessionben több bullet együttes konzisztenciája (NEM csak per-bullet)
- **Cost:** $0 (small NLI batch)
- **Trigger:** ha 2+ bullet ugyanazon subject-re tesz állítást → konfliktus-flag
- **Status:** 2026-05-17-3 0 FP smoke-teszten

### Layer 2.7 — SelfCheckGPT (drága borderline-resolver)
- **Mit:** 3 független generálás → szemantikus konzisztencia (LLM-divergencia = hallucination-jel)
- **Cost:** 6× G-Eval (N=3 generálás × scoring)
- **Trigger:** csak borderline 0.70–0.85 band-en, opt-in (smart-trigger pattern → [[smart-trigger-cost-pattern]])

## G-Eval verzió-evolúció (v0.1 → v0.3)

| Verzió | Bias-prompt | Pass-recall | Auto-prop arány | Production status |
|---|---|---|---|---|
| **v0.1** (2026-05-12) | nincs | ~100% (over-pass) | 10/10 | deprecated |
| **v0.2** (2026-05-14) | 1 bias-blokk + kalibrációs horgony | ~80% | 8/10 | stable, default |
| **v0.3** (2026-05-17) | 4 bias-blokk + CoT bias-self-check + szimmetrikus szigorítás | 53% (false-discard 7/15) | 6/10 | **opt-in only** `VAULT_GEVAL_VERSION=v03` |

**Mérnöki finding:** v0.3 NEM aszimmetrikus szigorítás (csak Fail-osztály), hanem **mindkét osztályon** csökkenti a conf-et. 30-sample paired kalibráció: Pass-recall **53%** → default-shift NEM ajánlott, csak Fail-precision-kritikus szakaszokban (pl. main-branch propagation). Részletek: [[g-eval-bias-mitigation-pattern#30-sample paired kalibráció]]

## 3 sub-score dimenzió

A G-Eval kimenete **3 független 0.0–1.0** sub-score, NEM egy aggregát:

1. **Factuality** — a bullet állítása ténybeli-e (NLI-jellegű ellenőrzés a forrásra)
2. **Novelty** — új-e a vault-ban? (KO-DB top-k corroboration → [[top-k-cross-source-corroboration]])
3. **Routing-fit** — a target-réteg (wiki / ADR / Memory / Glossary) konzisztens-e a bullet-tartalommal?

**Aggregálás:** súlyozott átlag (default `0.4 × fact + 0.3 × nov + 0.3 × routing`), de a `auto-prop`-gate az **összes 3 sub-score**-t külön ellenőrzi (`min(sub) >= 0.7`) — ez a Pocock-szerű multi-arm védelem.

## Mintázat — hogyan stack-eld production-ban

```
default-pipeline (Shadow / threshold=1.0):
  Layer 0 → Layer 1 → Layer 2 (G-Eval v0.2) → audit-log (NO write)

conservative-ramp (threshold=0.95):
  Layer 0 → Layer 1 → Layer 2 v0.2 → Layer 2.5 NLI (borderline 0.70-0.90) → Layer 3 auto-prop

aggressive (threshold=0.85, csak sandbox-branch):
  + Layer 2.6 coherence-check + Layer 2.7 SelfCheckGPT smart-trigger
```

**Threshold-config:** `~/.vault-config/crystallize-threshold.txt` (hot-reload, [[hot-reload-config-pattern]]). Ramp-protokoll: [[crystallize-threshold-ramp]].

## Anti-pattern

- ❌ **„G-Eval = egy prompt"** — nem, ez egy 5-rétegű család. Ne hivatkozz egyetlen prompt-fájlra mint „a G-Eval".
- ❌ **„Csak Layer 2 elég"** — borderline 0.70–0.90 band-en Layer 2.5 NLI NÉLKÜL false-discard 30%+.
- ❌ **„v0.3 mindig jobb mert szigorúbb"** — Pass-recall 53% miatt false-discard 7/15, only-opt-in.
- ❌ **„SelfCheckGPT olcsó"** — 6× token cost, csak borderline-band-en érdemes triggerelni.
- ❌ **„Same-LLM judge no bias"** — Claude-Claude self-enhancement +25% mérve, bias-mitigation [[g-eval-bias-mitigation-pattern]] kötelező.
- ❌ **„Aggregát score elég"** — `min(sub)` kell, nem `mean(sub)`; egyetlen <0.7 sub-score borítja a Pass-t.

## Reusable döntés-szabály

| Helyzet | Stack |
|---|---|
| Shadow / new pipeline | Layer 0 + 1 + 2 (v0.2), threshold 1.0, NO write |
| Production main-branch | Layer 0..2.5, threshold 0.95, opt-in v0.3 |
| Sandbox-branch (4-réteg safety-gate) | Layer 0..2.7, threshold 0.85 |
| Borderline-only deep-check | Layer 2.7 SelfCheckGPT smart-trigger, 6× cost OK |
| Cross-bullet konfliktus-gyanú | Layer 2.6 coherence-check |
| Same-LLM judge (Claude-Claude) | bias-mitigation prompt KÖTELEZŐ |
| Multi-bullet session-záráskor | Layer 2.5 NLI + Layer 2.6 coherence-check, NEM csak per-bullet G-Eval |

## Kapcsolódó

- [[g-eval-bias-mitigation-pattern]] — alfa-pattern: Layer 2 bias-prompt
- [[nli-hallucination-check-pattern]] — alfa-pattern: Layer 2.5
- [[nli-eval-input-completeness-trap]] — gotcha: NLI-bemenet hiányos kontextus
- [[layered-eval-cascading-pattern]] — meta: layered-eval cascade
- [[smart-trigger-cost-pattern]] — Layer 2.7 cost-control
- [[top-k-cross-source-corroboration]] — Novelty sub-score forrás
- [[crystallize-threshold-ramp]] — threshold-ramp protokoll
- [[auto-propagation-confidence-gate]] — Layer 3 downstream-gate
- [[llm-as-judge-evaluation-pattern]] — meta: LLM-as-judge család
- [[sv-05-crystallization-automation]] — architektúra-szint (B-1 sprint)
- [[sv-07-continuous-evaluation]] — Tier-2 NLI-bíró integráció
- [[hot-reload-config-pattern]] — threshold-config hot-reload
- [[reranker-cost-optimization-not-size]] — reranker smart-trigger analóg minta

## Forrás

- Memory bullet (2026-05-17-3): G-Eval v0.3 30-sample paired kalibráció Pass-recall 53%
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]]
- [[../07-Decisions/2026-05-12 sv-7 continuous evaluation arch]]
- KO-DB facts 212, 213, 1248–1256, 1259–1265, 1311, 5359, 5365–5368, 6436, 6440, 6470–6478
- Session 2026-05-17-3: Layer 2.6 coherence-check 0 FP smoke
