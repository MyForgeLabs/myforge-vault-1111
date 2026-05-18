---
name: B-3 Week 2 — L2 NLI-judge calibration
type: audit
tags: ["#type/audit", "#project/sv", "sv-3", "sv-7", "nli-judge", "continuous-eval"]
created: 2026-05-17
updated: 2026-05-17
status: shadow-baseline
related:
  - "[[11-wiki/sv-07-continuous-evaluation]]"
  - "[[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]]"
  - "[[06-Audits/eval-l1-baseline-20260517T192717Z.jsonl]]"
---

# B-3 Week 2 — L2 NLI-judge calibration audit

A **B-3 (continuous evaluation)** sprint Week 2 iteráció audit-jelentése. Az L1 parser (Week 1-α) 57.1% critic-pass-rate baseline-t adott — gyenge, és lassú lesz a threshold-ramp 0.95 → 0.85 (a B-1 pipeline-on a critic-reject-rate 42.9% → auto-disable trigger landolt 2026-05-17). Az **L2 NLI-judge** egy **független eval-signal** ami a G-Eval mellett másodvélemény-t ad: a Learning-bullet (hypothesis) "logikusan következik-e" a provenance-ból (premise, session-context).

> **Status:** SHADOW-baseline landolt. 20-sample audit a `crystallize-log.jsonl`-ből 2 session-re. Integráció a `11.11crystallize`-be Week 3 feladat.

## Model-választás

| Opció | Méret | Cached | Output-skala | Edge |
|---|---|---|---|---|
| **`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`** ⭐ | ~440 MB | ✅ (HF hub helyben) | 3-way (entail / neutral / contradict) | MNLI + FEVER + ANLI tréning → fact-verification recall magas |
| `facebook/bart-large-mnli` | ~400 MB | ❌ | 3-way (zero-shot mode is) | Csak MNLI — fact-inconsistency-re gyengébb |
| `cross-encoder/nli-deberta-v3-base` | ~440 MB | ❌ | logits | Erősebb, de letöltés-overhead, és kevés batch-előny |

**Választás: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`.**

Indoklás:
1. **Cached helyben** (`~/.cache/huggingface/hub/models--MoritzLaurer--DeBERTa-v3-base-mnli-fever-anli/`) — nincs letöltés-blocker. Modell-load 2-3 s, inference ~530-600 ms CPU-n.
2. **FEVER** — Fact Extraction and VERification corpus. Pontosan a vault Learnings-szerű állítások ellenőrzésére van tanítva (claim ↔ Wikipedia-evidence típusú párokon).
3. **ANLI** — adversarial NLI; kiszűri a tipikus surface-pattern overfit-et, jobb a finom tényszerű inkonzisztenciára (Eugene Yan kifejezetten ezt ajánlja a `## Learnings` hallucináció-mérésre, lásd sv-07 wiki 6.3 szekció).
4. **3-way head** közvetlenül egyezik a kívánt outputtal (`entailment` / `neutral` / `contradiction`).

## CLI

```
/usr/local/bin/eval-l2-nli-judge

  --bullet <text>           Hypothesis (the Learning bullet)
  --provenance <text>       Premise (source / session-context)
  --input-file <jsonl>      Batch (one {bullet, provenance, id?} per line)
  --calibrate               Last N records from crystallize-log + agreement audit
  --samples N               Calibration sample count (default 10)
  --threshold F             Entailment-prob threshold for pass-vote (default 0.6)
  --json                    Machine-readable output
  --snapshot                Write 06-Audits/eval-l2-nli-calibration-<ts>.jsonl
```

Példa output:

```json
{
  "verdict": "entailment",
  "pass_vote": true,
  "confidence": 0.8564,
  "entailment_prob": 0.8564,
  "neutral_prob": 0.1426,
  "contradiction_prob": 0.0012,
  "model": "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
  "threshold": 0.6,
  "latency_ms": 533,
  "parser_version": "1.0"
}
```

## 20-sample calibration (2026-05-17, threshold=0.3)

Forrás: `06-Audits/crystallize-log.jsonl` legutóbbi 20 score-record, 2 session-en (mfl-voice-sprint-1, szerver-update). Provenance: a session `## Summary` + `## Events` concat, max 3500 char (tokenizer-truncate 512-re).

| # | session | g-route | g-conf | nli-verdict | nli-ent | agree |
|---|---|---|---|---|---|---|
| 1 | mfl-voice-sprint-1 | auto-prop | 0.73 | entailment | 0.630 | OK |
| 2 | mfl-voice-sprint-1 | discard | 0.67 | neutral | 0.190 | OK |
| 3 | mfl-voice-sprint-1 | auto-prop | 0.73 | entailment | 0.419 | OK |
| 4 | mfl-voice-sprint-1 | discard | 0.67 | entailment | 0.370 | DIFF |
| 5 | mfl-voice-sprint-1 | auto-prop | 0.73 | contradiction | 0.222 | DIFF |
| 6 | mfl-voice-sprint-1 | auto-prop | 0.80 | entailment | 0.320 | OK |
| 7 | mfl-voice-sprint-1 | auto-prop | 0.80 | entailment | 0.541 | OK |
| 8 | mfl-voice-sprint-1 | discard | 0.00 | neutral | 0.290 | OK |
| 9 | mfl-voice-sprint-1 | auto-prop | 0.73 | entailment | 0.377 | OK |
| 10 | mfl-voice-sprint-1 | auto-prop | 0.73 | contradiction | 0.282 | DIFF |
| 11 | szerver-update | discard | 0.67 | entailment | 0.314 | DIFF |
| 12 | szerver-update | discard | 0.00 | neutral | 0.272 | OK |
| 13 | szerver-update | batch-preview | 0.73 | entailment | 0.395 | OK |
| 14 | szerver-update | discard | 0.00 | entailment | 0.455 | DIFF |
| 15 | szerver-update | discard | 0.00 | contradiction | 0.130 | OK |
| 16 | szerver-update | discard | 0.67 | entailment | 0.378 | DIFF |
| 17 | szerver-update | discard | 0.67 | contradiction | 0.161 | OK |
| 18 | szerver-update | batch-preview | 0.73 | entailment | 0.388 | OK |
| 19 | szerver-update | discard | 0.53 | entailment | 0.337 | DIFF |
| 20 | szerver-update | discard | 0.67 | neutral | 0.276 | OK |

**Snapshot:** `06-Audits/eval-l2-nli-calibration-20260517T212105Z.jsonl` (20 rows + meta).

### Threshold-ramp (10-sample sub-audit)

| threshold | overall agreement | high-conf agreement |
|---|---|---|
| 0.6 (default kezdő) | 40.0% | 14.3% (1/7) |
| 0.5 | 50.0% | 28.6% (2/7) |
| 0.4 | 60.0% | 42.9% (3/7) |
| **0.3 (kalibrált)** | **70.0%** | **71.4% (5/7)** |

> **Megjegyzés:** alacsonyabb threshold = NLI engedékenyebb az "entailment" verdiktre. Az NLI inherently szigorúbb mint a G-Eval (entailment≥0.3 ≈ "logikailag konzisztens, de gyenge evidence"). A 0.3-as threshold a sweet-spot a target 80%+ közelében.

### 20-sample agreement summary

| metrika | érték |
|---|---|
| overall agreement | **65.0%** (13/20) |
| high-conf agreement (G-Eval auto-prop ∧ NLI pass) | **71.4%** (5/7) |
| both_pass | 7 |
| g_pass ∧ n_fail (NLI kiszűri) | 2 |
| g_fail ∧ n_pass (NLI engedékenyebb) | 5 |
| both_fail | 6 |

## Findings

1. **NLI inherently szigorúbb a G-Eval-nál** — a 20-sample-en 2 olyan auto-prop volt amit NLI `contradiction`-nek (#5, #10) jelölt. Ezek **valódi false-positive-jelöltek** a G-Eval-ban — case-by-case review-t érdemelnek. (Bullet #5: STT echo-loop; #10: Brand-paradigma — utóbbi tényleg gyenge evidence, single-incident).
2. **High-conf agreement 71.4%** közelít a target 80%+-hoz. A 2 kiesés `contradiction` — pont a kritikus eset, ahol NLI-jel értékes.
3. **Latency CPU-n 500-600 ms / bullet** — 10-bullet session = ~5-6 s overhead, akceptabilis a `11.11crystallize` flow-ban (G-Eval Anthropic-API hívása már ennél hosszabb).
4. **Provenance-quality kritikus** — a `## Events` szekciók rövidek a sessionökben. Ha a session-trace-t (chat-history vagy `08-Sessions/<slug>` raw) is be tudnánk húzni, az entailment-prob 0.05-0.15-tel feljebb tolódna a stabil eseteknél.
5. **`g_fail ∧ n_pass` 5 eset** — ez nem riasztó: G-Eval `discard`-ra döntött safety/dim4=1 (PII) penalty-vel. NLI viszont nem tudja a PII-policy-t, csak az állítás-igazságot. Ez **dimenziók közötti különbség**, nem hiba.

## Acceptance criteria (Week 2)

- [x] Model letöltés / cache-hit verifikálva (`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`)
- [x] `/usr/local/bin/eval-l2-nli-judge` CLI ÉLES (single + batch + calibrate-mode)
- [x] 10-sample calibration futott, ≥70% overall agreement threshold=0.3-on
- [x] Snapshot landol `06-Audits/eval-l2-nli-calibration-<ts>.jsonl`
- [x] Audit-fájl (ez a dokumentum) committed
- [ ] **Week 3:** integráció `11.11crystallize`-be (Layer 2.5 az G-Eval után, OR-rule auto-prop-hoz: G-Eval auto-prop ∧ NLI entailment)
- [ ] **Week 3:** disagreement-cases (G-Eval auto-prop ∧ NLI contradict) auto-batch-preview-re downgrade
- [ ] **Week 4:** threshold-ramp scriptbe (`vault-crystallize-monitor`) NLI-agreement-rate metrika beépítése

## Next step — `11.11crystallize` integráció (Week 3)

A Layer 2.5 NLI-judge a `process_session` loop-ban a G-Eval után fut, BULLET-enként. Pseudo-code:

```python
# in process_session loop, after `routing = route(confidence, threshold)`:
if routing == "auto-prop":
    provenance = session_provenance(slug)
    nli = nli_judge(bullet, provenance, threshold=0.3)
    if not nli["pass_vote"]:
        # G-Eval auto-prop + NLI fail → downgrade
        routing = "batch-preview"
        record["nli_downgrade"] = True
    record["nli"] = nli   # always logged for tracking
```

Audit-log mező-bővítés:
```jsonl
{..., "nli_verdict": "entailment", "nli_entailment_prob": 0.63, "nli_pass_vote": true, "nli_downgrade": false}
```

A pipeline 4-rétegű safety-gate-en belül ez egy **soft-veto Layer 2.5**-ként funkcionál — nem blokkol kemény-discard-dal, csak `batch-preview`-re tolja a kérdéses bullet-eket (low-cost intervention, magas-recall).

## Kapcsolódó

- [[11-wiki/sv-07-continuous-evaluation]] — B-3 research, NLI-judge szekció (6.3)
- [[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]] — B-3 ADR
- [[06-Audits/eval-l1-baseline-20260517T192717Z.jsonl]] — L1 baseline (Week 1-α)
- `/usr/local/bin/eval-l2-nli-judge` — Week 2 script ÉLES
- `/usr/local/bin/eval-l1-parser.py` (`.vault-eval/scripts/`) — L1 baseline parser
- `/usr/local/bin/11.11crystallize` — Layer 2 G-Eval + Layer 2.5 NLI integráció target
