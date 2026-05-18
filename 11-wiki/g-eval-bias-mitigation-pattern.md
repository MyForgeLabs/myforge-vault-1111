---
name: g-eval-bias-mitigation-pattern
description: G-Eval prompt-template ha a generator és judge ugyanaz az LLM-család (Claude-Claude) - 4 explicit bias-blokk + kalibrációs horgony + CoT bias-self-check, mérhetően csökkenti self-enhancement-et
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "g-eval", "llm-evaluation", "bias-mitigation", "crystallization"]
---

# G-Eval bias-mitigation pattern

## A probléma

LLM-as-judge setup (G-Eval, claude-code subagent-scorer) eredendő bias-t mutat ha a generator és a judge UGYANAZ a model-család:

- **Self-enhancement bias** — Claude scoring saját outputjának (+~25% irodalmi mérések)
- **Verbosity bias** — hosszabb-szöveg jobban scorel ("több = jobban átgondolt")
- **Position bias** — első/utolsó option preferált
- **Halo / authority bias** — confident wording (`MUST`, `ALWAYS`, `kötelező`) jobban scorel

A SV `claude-code` subagent-scorer pont ilyen setup, ezért a B-1 sprint kritikus pontja.

## A pattern

A G-Eval prompt-template-be **4 explicit bias-blokk + kalibrációs horgony + CoT bias-self-check** beillesztve:

```text
You are scoring a Learning bullet. Be aware of these biases:

1. **Self-enhancement bias** — assume the bullet was authored by a DIFFERENT agent (not yourself). Score the content, not familiarity.
2. **Verbosity bias** — length does NOT correlate with quality. Brevity is a feature. A 1-sentence Learning can outscore a 3-paragraph one.
3. **Position bias** — judge the substance, not the order.
4. **Halo/authority bias** — confident wording ("MUST", "kötelező") does NOT make a Learning truer.

Calibration anchors:
- BAD-BUT-VERBOSE: "A jól-átgondolt brand-narratíva fontos része egy projektnek..." → discard (platitude)
- GOOD-AND-TERSE: "Hostinger ICANN-redirect ignores Cache-Control headers" → auto-prop (specific, novel, actionable)

Before scoring, write one line:
"Bias-self-check: I detected the following biases in my draft scoring: [...]"

Then score the bullet on dim1-4 (1-5 scale).
```

## Élő mérés (2026-05-17-obsidian-vault-2 session)

Same 10-bullet input (mfl-voice-sprint-1 session-ből), v0.2 prompt vs v0.3-bias-mitigated:

| Metric | v0.2 | v0.3 | Δ |
|---|---|---|---|
| avg confidence | 0.880 | 0.760 | **-0.12** |
| auto-prop count | 10/10 | 6/10 | **-4 (40%)** |
| dim2 avg | 4.2 | 3.6 | -0.6 (verbosity debias) |
| dim3 avg | 3.8 | 3.2 | -0.6 (reusability debias) |

A 4 re-routalt bullet pont a tipikus self-enhancement/verbosity-targets (brand-narratíva, kategória-felsorolás, "jól-fogalmazott" pszichológiai megfigyelés, single-tool fact). Részletek: [[../06-Audits/2026-05-17 B-1 G-Eval bias-mitigation v0.3]].

## Mikor érdemes alkalmazni

- ✅ Generator ÉS judge ugyanaz a LLM-család (Claude-Claude, GPT-GPT, Gemini-Gemini)
- ✅ Cost-sensitive eval (drága a multi-judge ensemble) — explicit bias-mitigation 5%+ accuracy-gain
- ✅ Borderline-confidence range (0.70-0.85), ahol a bias dominánsan ronthatja a verdict-et

## Trade-off

- ⚠️ A v0.3-prompt **több token** (kalibrációs horgony + bias-self-check CoT) — ~20% token-overhead per scoring
- ⚠️ Initial mérés szerint az auto-prop count drasztikusan csökken (10→6) — emiatt a threshold-ramp (B-1 Aggressive 0.85) lassabb lesz
- ✅ Cserébe: a `claude-code` scorer NEM bias-eltolt eredményt ad → a crystallize-pipeline minőségi határa magasabb

## 30-sample paired kalibráció (2026-05-17-3) — szimmetrikus szigorítás

A B-1 Week 5 subagent-fanout 30-sample paired kalibráció (`06-Audits/2026-05-17 G-Eval v0.3 30-sample paired kalibráció.md`) **CONDITIONAL PASS** verdikt-tel zárt — fontos finomítás a fenti egyszerű "bias-debias ⇒ jobb verdict" narratívához:

| Metrika | v0.2 | v0.3 | Cél | Status |
|---|---:|---:|---:|---|
| 0 false-promotion (Fail → auto-prop) | 0/15 | 0/15 | 0 | ✅ mindkettő |
| Gold-agreement | 60% | 66.7% | +5% | ✅ +6.7% |
| Pass-set conf csökkenés | 0.916 | 0.773 | -0.10 | ✅ -0.142 |
| **Fail-set conf csökkenés (új mérés)** | 0.502 | 0.271 | -0.10 | ✅ -0.231 (**~2× cél**) |
| Fail → Fail recall | 11/15 | 15/15 | 100% | ✅ 100% (v0.3) |
| **Pass-recall (v0.3 false-discard)** | 0/15 | **7/15** | 0% | ❌ **47% Pass-recall veszteség** |

**Tanulság (új):** a bias-mitigation prompt **NEM aszimmetrikus szigorítás** (csak Fail-osztály), hanem **szimmetrikus szigorítás mindkét osztályon**. A Pass-confidence 0.916→0.773 csökkenése = 7/15 Pass-bullet false-discard. **Precision-cél** (B-1) elérve, de **production-replace v0.3-ra NEM trivialis** — opt-in env-var (`VAULT_GEVAL_VERSION=v03`) ajánlott default-shift helyett.

### Recommendation (3 opció)

| Opció | Threshold | Kockázat | Pass-recall | Use-case |
|---|---|---|---|---|
| **A** (alacsony kockázat, ajánlott) | v0.2 default + v0.3 opt-in env-var | LOW | 100% (v0.2) | precision-prioritás minimum-noise |
| B (közepes) | v0.3 default + threshold 0.95→0.85 | MED | 53% (kompenzáció részleges) | balanced |
| C (NEM ajánlott) | v0.3 default threshold-változatlan | HIGH | 53% | tisztán precision-fókusz |

**Reusable insight:** minden bias-mitigation prompt-evaluation MIND a Pass-set ÉS Fail-set conf-csökkenést mérje — az aszimmetria a kritikus jel.

## Kapcsolódó

- [[Crystallization-protocol]] — host protokoll
- [[sv-05-crystallization-automation]] — B-1 research
- [[sv-07-continuous-evaluation]] — független eval-signal (B-3 L2 NLI)
- [[smart-trigger-cost-pattern]] — kapcsolódó cost-savings pattern
