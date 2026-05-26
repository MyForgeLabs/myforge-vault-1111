---
name: g-eval-bias-mitigation-pattern
description: G-Eval prompt template for when generator and judge are the same LLM family (Claude-Claude). 4 explicit bias blocks + calibration anchor + CoT bias-self-check, measurably reduces self-enhancement bias.
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "g-eval", "llm-evaluation", "bias-mitigation", "crystallization"]
lang: en
translated_from: g-eval-bias-mitigation-pattern.md
---

# G-Eval bias-mitigation pattern

> **TL;DR:** When the LLM that generated the content also judges it ("Claude scores Claude"), self-enhancement bias inflates scores by **~25%** in published measurements. Our 4-block bias-mitigation prompt cut auto-promotion from **10/10 → 6/10** on a 10-bullet paired sample, average confidence **0.880 → 0.760**. But a 30-sample paired calibration revealed an honest catch: bias-mitigation is **symmetric** (tightens both Pass AND Fail classes), causing **47% Pass-recall loss** (7/15 good bullets falsely discarded). Conclusion: **opt-in env-var, NOT default shift**. The asymmetry signal is the critical metric most evals don't measure.

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[g-eval-bias-mitigation-pattern]] (Hungarian version).

## What this is NOT

- **NOT a benchmark** — n=10 and n=30 paired samples are small. Treat numbers as directional signal, not statistical proof.
- **NOT a recommended default** — our own 30-sample calibration produced a CONDITIONAL PASS with **47% Pass-recall loss**, so we run v0.3 as opt-in only.
- **NOT a substitute for multi-judge ensemble** — if you can afford 3+ judges from different families, do that instead. This pattern is for cost-sensitive single-judge setups.
- **NOT magic prompt engineering** — the 4 bias blocks are textbook (self-enhancement, verbosity, position, halo). The contribution is the **measured asymmetry finding**, not the prompt itself.

## The problem

An LLM-as-judge setup (G-Eval, in-house subagent scorer) exhibits inherent bias when the generator and the judge come from the **same model family**:

- **Self-enhancement bias** — Claude scoring its own outputs (+~25% in published measurements)
- **Verbosity bias** — longer text scores better ("more = more thoughtful")
- **Position bias** — first/last option preferred
- **Halo / authority bias** — confident wording (`MUST`, `ALWAYS`, `kötelező`) scores higher

The Claude-Code subagent-scorer setup hits all of these, so it's the critical risk for any Claude-judges-Claude eval pipeline.

## The pattern

Embed **4 explicit bias blocks + calibration anchors + CoT bias-self-check** in the G-Eval prompt template:

```text
You are scoring a Learning bullet. Be aware of these biases:

1. **Self-enhancement bias** — assume the bullet was authored by a DIFFERENT agent (not yourself). Score the content, not familiarity.
2. **Verbosity bias** — length does NOT correlate with quality. Brevity is a feature. A 1-sentence Learning can outscore a 3-paragraph one.
3. **Position bias** — judge the substance, not the order.
4. **Halo/authority bias** — confident wording ("MUST", "always") does NOT make a Learning truer.

Calibration anchors:
- BAD-BUT-VERBOSE: "A well-considered brand narrative is an important part of any project..." → discard (platitude)
- GOOD-AND-TERSE: "Hostinger ICANN-redirect ignores Cache-Control headers" → auto-prop (specific, novel, actionable)

Before scoring, write one line:
"Bias-self-check: I detected the following biases in my draft scoring: [...]"

Then score the bullet on dim1-4 (1-5 scale).
```

## Live measurement (10-bullet paired sample)

Same 10-bullet input, v0.2 prompt vs v0.3 bias-mitigated:

| Metric | v0.2 | v0.3 | Δ |
|---|---|---|---|
| avg confidence | 0.880 | 0.760 | **-0.12** |
| auto-prop count | 10/10 | 6/10 | **-4 (40%)** |
| dim2 avg | 4.2 | 3.6 | -0.6 (verbosity de-bias) |
| dim3 avg | 3.8 | 3.2 | -0.6 (reusability de-bias) |

The 4 re-routed bullets were exactly the typical self-enhancement / verbosity targets (brand narrative, category enumeration, "well-articulated" psychological observation, single-tool fact).

## When it's worth applying

- ✅ Generator AND judge are the same LLM family (Claude-Claude, GPT-GPT, Gemini-Gemini)
- ✅ Cost-sensitive eval (multi-judge ensemble is expensive) — explicit bias mitigation yields 5%+ accuracy gain
- ✅ Borderline-confidence range (0.70-0.85), where bias can dominate the verdict

## Trade-off

- ⚠️ The v0.3 prompt uses **more tokens** (calibration anchor + bias-self-check CoT) — ~20% token overhead per scoring
- ⚠️ Initial measurement shows auto-prop count drops drastically (10→6) — so threshold ramps slow down
- ✅ In exchange: the scorer gives non-bias-shifted results → higher quality bar at the crystallize pipeline

## 30-sample paired calibration — symmetric tightening

A 30-sample paired calibration produced a **CONDITIONAL PASS** verdict — an important nuance to the simple "bias-debias → better verdict" narrative:

| Metric | v0.2 | v0.3 | Goal | Status |
|---|---:|---:|---:|---|
| 0 false-promotion (Fail → auto-prop) | 0/15 | 0/15 | 0 | ✅ both |
| Gold-agreement | 60% | 66.7% | +5% | ✅ +6.7% |
| Pass-set confidence drop | 0.916 | 0.773 | -0.10 | ✅ -0.142 |
| **Fail-set confidence drop (new metric)** | 0.502 | 0.271 | -0.10 | ✅ -0.231 (**~2× goal**) |
| Fail → Fail recall | 11/15 | 15/15 | 100% | ✅ 100% (v0.3) |
| **Pass-recall (v0.3 false-discard)** | 0/15 | **7/15** | 0% | ❌ **47% Pass-recall loss** |

**Lesson (new):** the bias-mitigation prompt is **NOT asymmetric tightening** (only on the Fail class) — it is **symmetric tightening on both classes**. The Pass-confidence drop 0.916→0.773 = 7/15 Pass bullets falsely discarded. **Precision goal** is met, but **production replacement with v0.3 is non-trivial** — opt-in env-var (`SCORER_VERSION=v03`) is recommended instead of default shift.

### Recommendation (3 options)

| Option | Threshold | Risk | Pass-recall | Use case |
|---|---|---|---|---|
| **A** (low risk, recommended) | v0.2 default + v0.3 opt-in env-var | LOW | 100% (v0.2) | precision-priority, minimum noise |
| B (medium) | v0.3 default + threshold 0.95→0.85 | MED | 53% (partial compensation) | balanced |
| C (NOT recommended) | v0.3 default, threshold unchanged | HIGH | 53% | pure precision focus |

**Reusable insight:** every bias-mitigation prompt evaluation must measure BOTH the Pass-set AND Fail-set confidence drop — the asymmetry is the critical signal.

## Audio overview

- EN narration (Charon voice): `[[.vault-nb/audio-overviews/g-eval-bias-mitigation-pattern.en.mp3]]`
- HU narration (Kore voice): `[[.vault-nb/audio-overviews/g-eval-bias-mitigation-pattern.hu.mp3]]`

Generated via Gemini 3.1 Flash TTS preview. ~1-2 minutes each. See [[gemini-3-1-flash-tts-pipeline]] for the pipeline.

## Related

- [[Crystallization-protocol]] — host protocol
- [[verification-step-before-claim]] — independent eval signal
- [[claude-code-subagent-fanout]] — fanout pattern that often pairs with G-Eval scoring
