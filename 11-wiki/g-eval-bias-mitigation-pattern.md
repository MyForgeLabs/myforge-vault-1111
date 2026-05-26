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

Same 10-bullet input (internal-voice-pilot-sprint-1 session-ből), v0.2 prompt vs v0.3-bias-mitigated:

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

## 2026-05-20 — Mining-classifier ground-truth-ceiling (B-8 100-bullet κ=0.708 finding)

A 2026-05-20-i B-8 RSI Critic 100-bullet production-flip-tesztelés feltárt egy **ground-truth-classifier-quality bottleneck**-et ami **mérhetően korlátozza a megfigyelhető κ-t**, függetlenül a Critic-prompt-kvalitásától.

### A finding

100-bullet clean baseline-on (60 pass-expected / 40 fail-expected, content-classifier ground-truth):
- Default-mode agreement: **86%**, Cohen's **κ = 0.708** ("substantial", Landis-Koch)
- Manual 10/10 false-accept inspection: **mind a 10 FA content-classifier mining-noise** (HH:MM regex over-trigger, "mai" magyar szó, IP-fragment-regex L0/L1/L2 architecture-parallel-bulleteken)
- **Effective FA rate ≈ 0%** post-relabeling
- **Revised effective κ ≈ 0.85+** post-noise-fix

### Wider lesson

A measurement-ground-truth-classifier önmaga zaj-szintje **hard-ceiling**-et szab a megfigyelhető κ-ra:
- Ha a ground-truth-classifier 10% misclassification-rate-tel dolgozik, akkor a maximum-observable κ ≈ 0.85
- Ha 5% → κ ≈ 0.90
- Ha 1% → κ ≈ 0.95

A **Critic-prompt-finomítás nem tudja átlépni** a ground-truth-classifier-zaj-szabta ceiling-et — csak a measurement-classifier-quality javítása oldja fel.

### Methodology-implication

A κ-mérések publikációja-előtt kötelező:
1. **Manual inspection a mismatch-cases-en** (különösen a false-accept oldalon)
2. **Ground-truth-classifier-noise-disclosure** a paper-ben
3. **Re-labeling estimate** mint sensitivity-analysis ("revised κ post-relabeling")

Anélkül a publikált κ alulbecsli a Critic-quality-jét és overrepresenti a measurement-classifier-noise-t.

### Empirikus eredmény

- 26-unique pilot (mock-scorer-labeled): κ=0.660 raw → ~0.74 post-noise-fix
- 100-clean pilot (content-classifier-labeled): κ=0.708 raw → ~0.85+ post-noise-fix
- Pattern: **a noise-fix +0.06-0.14 κ-lift-et adott**, ami a Critic-prompt-finomítás-szal NEM elérhető

Audit: [[../06-Audits/2026-05-20 B-8 Critic 100-bullet clean re-sample (kappa 0.708)]]

## Generalizes beyond G-Eval — tuning-recall ceiling pattern (2026-05-20)

A "measurement-classifier own noise sets observable-ceiling" finding **általánosul** minden olyan ML/IR evaluation-re ahol egy automated-classifier (ground-truth labeler / scorer / judge) szolgáltatja a labels-et és egy másik system-et mérünk ellene.

### Same dynamic, different domain — retrieval benchmark (RRF hybrid-fusion)

A 2026-05-20-i RRF-fusion benchmark **ugyanazt a pattern-t** mutatta:
- **Tuning-recall** (89-Q IDF-mined): 85.39% R@5
- **Held-out** (89-Q heading-mined): 69.66% R@5
- **Honest production-recall** (átlag): **77.5% R@5**

A 91% kezdő-szám (sőt a 85.39% tuning is) **a measurement-pipeline saját zaja**-t (path-mapping orphans + duplicate-ingest + query-distribution overfit) tükrözte, NEM a retrieval-system valós képességét. Az "honest reporting" akkor élesedik, ha a measurement-pipeline-t MIN. 2 methodology-val verifikáljuk és a delta-t auditáljuk.

**Wider lesson**: bármilyen automated-eval-loop önmagát kalibrálja a saját zajára. **Cross-validation különböző mérési-módszertannal kötelező** mielőtt egy single-number-t hivatkozási alapként marketingelünk.

Részletek: [[tuning-vs-production-recall-honest-reporting]] · [[benchmark-data-pipeline-fidelity-gotchas]] · [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]
