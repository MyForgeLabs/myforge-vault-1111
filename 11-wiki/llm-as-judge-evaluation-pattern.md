---
name: LLM-as-judge evaluation pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern, evaluation, llm, g-eval, quality-gate, critique-shadowing]
---

# LLM-as-judge evaluation pattern

> [!info] Mit hív életre
> Ahol **scale-elhető minőség-elbírálás** kell sok output-ra, de **emberi reviewer drága/lassú**. Az LLM-as-judge egy második LLM-mel értékelteti az első LLM-output-ot rubrika-szerinti score-ral. A klasszikus alkalmazás: agent-generálta tartalom auto-gate-elése bizonyossági küszöbbel.

## A pattern lényege

A naiv pipeline: `Generator-LLM → Output → Human-review`. Skálázódásnál szűk: emberi reviewer ~10-50 output / nap / fő. Az LLM-as-judge átveszi a reviewer szerepét:

1. **Generator-LLM** előállít egy output-ot (text, code, decision)
2. **Judge-LLM** (általában másik prompt, esetenként másik modell) **rubrika-prompt-tal** értékeli az output-ot
3. **Rubrika** strukturált — pontszám 0-1 + Pass/Fail + indoklás
4. **Threshold-gate** dönt: auto-accept ha score > threshold, manual-review ha alatta

## Variánsok

| Variáns | Mi jellemzi | Mikor |
|---|---|---|
| **G-Eval** (Naive LLM-as-judge) | 1 LLM-call, CoT-prompt + score-output | Gyors gate, low-stakes |
| **Critique Shadowing** | Judge-LLM **few-shot kalibrációval**, ahol az emberi reviewer 20-50 példán pre-jelölt | Mid-stakes, jobb-recall kell |
| **Self-RAG** | Generator önmagát értékeli token-szinten + retrieval-rel | Real-time generation steering |
| **NLI-based** | Natural Language Inference judge (logical-entailment) → robusztusabb mint scoring | Hallucination-detection |
| **Multi-judge ensemble** | 3-5 judge szavaz, többségi-vote | High-stakes (medical, legal) |
| **Pairwise comparison** | Judge két output-ot kap és A/B-t mond | Preference-dataset building |

## Buktatók

### 1. Position bias

A judge a **listán előrébb-szereplő** output-ot preferálja statisztikailag. Mitigation: randomizált sorrend + két irányú comparison.

### 2. Verbosity bias

A judge a **hosszabb** output-ot jobbnak ítéli. Mitigation: rubrikába explicit "tömörség is érték".

### 3. Self-enhancement bias

A judge a **saját modell-családja** output-ját jobbnak ítéli (GPT-4 jobbnak látja a GPT-4-et mint Claude-ot). Mitigation: cross-family judge + bias-correction prompt ([[g-eval-bias-mitigation-pattern]]).

### 4. False-Pass overconfidence

A judge sokszor **mindent Pass-nak** ítél (lazy bias). Mitigation: kalibrációs-set, threshold-adjustment, force-distribution.

### 5. Input-completeness blind spot

A judge nem veszi észre ha az input-context **hiányos** (pl. a Generator-nek nem adtak meg minden source-t). Mitigation: NLI-réteg külön ([[nli-eval-input-completeness-trap]]).

## A vault konkrét megvalósulása

A vault SV B-1 layer (crystallization) használja:

```
Generator: Session-záró agent javasol propagation-target-eket (5-15 bullet)
   ↓
Judge: G-Eval LLM-as-judge subagent (Claude Code fanout, $0 cost)
   ↓ rubrika: routing-pertinence + evidence-strength + non-duplication
Output: per-bullet score (0-1) + Pass/Fail + brief justification
   ↓
Threshold-gate:
   • score >= 0.95 → auto-prop (Conservative mode)
   • 0.85 ≤ score < 0.95 → preview-be (default Shadow mode)
   • score < 0.85 → discard-candidate
```

Confidence-threshold: `~/.vault-config/crystallize-threshold.txt` (hot-reload). Production-ramp protokoll: shadow → conservative → aggressive ([[crystallize-threshold-ramp]]).

## A 4-rétegű quality-gate (vault implementáció)

A vault SV B-1 a single-judge helyett **cascading 4-layer eval-t** használ:

| Layer | Mit ellenőriz | Cost | Eliminálja |
|---|---|---|---|
| **L1: Rule-based** | Formátum, frontmatter-egzistencia, wikilink-validity | $0 | ~30% trivial-Fail |
| **L2: G-Eval scoring** | Routing-pertinence + evidence + relevance | $0 (subagent-fanout) | ~40% borderline |
| **L2.5: NLI-judge** | Logical-entailment a bullet és target közt | $0 (helyi modell) | ~10% subtle-mismatch |
| **L2.6: Coherence-check** | Cross-bullet contradiction-detection | $0 (KO-DB query) | ~5% contradiction |

A cascading-pattern előnye: drága L3-réteg (manual-review) csak ~15%-ra fut, az L1-L2.6 átszűri a tisztán gondolható eseteket. Részletek: [[layered-eval-cascading-pattern]].

## Bias-mitigation prompt-template

A G-Eval bias-mitigation v0.3 (mért: conf 0.880→0.760, auto-prop 10/10→6/10) 4 bias-blokk + kalibrációs horgony:

```
Te egy SZIGORÚ judge vagy. Ezek a torzítások amelyeket TUDATOSAN kerülsz:
- Self-enhancement: NEM preferálod a saját modell-családod stílusát
- Verbosity: rövid és tömör output is lehet 1.0
- Position: a sorrend irreleváns
- Lazy-pass: nem mindent Pass-olsz; ha bizonytalan vagy, Fail

Kalibrációs horgony: az 1.0 score azt jelenti "valós példa, evidence-grounded, 
non-duplikált, helyes target". 0.5 az "elfogadható de határeset". 

Bias-self-check (CoT): mielőtt scorolnál, 1 mondatban válaszolj:
"Melyik bias-t kellene most legjobban kerülnöm ennél a bullet-nél?"
```

Lásd [[g-eval-bias-mitigation-pattern]] a teljes prompt-template-ért.

## Mikor NE használj LLM-as-judge

- **High-stakes, irreverzibilis műveletek** (orvosi diagnózis, jogi döntés) — itt ember kell
- **Definíció-szerinti igazság** (matematikai bizonyítás, kód-correctness) — itt unit-test / formal-prover
- **Kreatív értékítélet ahol nincs konszenzus** — itt user-preferencia A/B teszt
- **Adversarial input** — a judge prompt-injection-nel manipulálható, ha input untrusted

## Source-evidence (KO-DB)

- `LLM-as-judge` token: 5 distinct subject, 10 fact, **3 source-type** (adr + session + wiki)
- `Critique Shadowing` token: 6 subject, 15 fact, 2 source-type (adr + wiki) — kalibrációs variáns
- `G-Eval LLM-as-judge` token: 1 subject, 3 fact, 2 source-type — vault-specifikus implementáció
- Top-source: `07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md` + `11-wiki/sv-07-continuous-evaluation.md`

## Kapcsolódó

- [[sv-07-continuous-evaluation]] — a vault SV-7 axis részletes terve
- [[g-eval-bias-mitigation-pattern]] — bias-blokk prompt-template
- [[layered-eval-cascading-pattern]] — L1-L2-L2.5-L2.6 cascading
- [[nli-eval-input-completeness-trap]] — NLI-réteg az input-completeness-re
- [[auto-propagation-confidence-gate]] — threshold-gate a propagáció előtt
- [[crystallize-threshold-ramp]] — shadow → conservative → aggressive ramp protokoll
- [[reranker-cost-optimization-not-size]] — judge-méret nem mindig egyenes arányos a quality-vel
