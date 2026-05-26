---
name: DSPy signatures + GEPA optimizer pattern
description: DSPy programmatic-LM-stack mintázata - signatures (input/output deklaráció), Modules (komponált pipeline-ok) és GEPA (reflective Pareto-front prompt-optimizer) - reusable kód-mint prompt-helyett és visszacsatoláson alapuló prompt-evolúciós keret
type: wiki
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "tool-composition", "self-improvement", "frontier-research", "sv-research"]
source: external-repo stanfordnlp/dspy (MIT)
source_path: 10-raw/external/stanfordnlp_dspy/
parent: [[11-wiki/sv-04-tool-composition]]
---

# DSPy signatures + GEPA optimizer pattern

A Stanford NLP labtól érkező **DSPy** keretrendszer (~2023 óta, 2025 H2-re ipari standard) abból a felismerésből indul, hogy a brittle, kézzel-pörgetett prompt-string-ek **NEM jó interfész** a foundation-modellekhez. Helyettük: **programozz, ne promptolj** — deklaratív Python-kód + automatikus optimalizáció.

## Frontier-context

- **Forrás:** [github.com/stanfordnlp/dspy](https://github.com/stanfordnlp/dspy), [dspy.ai](https://dspy.ai) (docs)
- **Licenc:** MIT (Stanford NLP, Omar Khattab et al.)
- **Maintainers:** Stanford NLP lab, Omar Khattab, Matei Zaharia, Chris Potts
- **Citation:** Khattab et al. 2024 ICLR ("DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines", arXiv:2310.03714)
- **GEPA paper:** Agrawal et al. 2025 ("GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning", arXiv:2507.19457)

## Architektúra — három fő primitív

### 1. Signature — deklaratív I/O kontraktus

```python
class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""
    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")
```

A signature **nem a prompt** — a signature az input/output sémája és a feladat magas-szintű leírása. A konkrét promptot az **Adapter** generálja runtime-ban (ChatAdapter / JSONAdapter / XMLAdapter / TwoStepAdapter). Ez a separation-of-concerns ahhoz hasonló, mint ahogy egy SQL-query nem a B-tree-bejárás.

### 2. Module — komponált pipeline-elem

A `dspy.Module` egy LLM-call-stack (ChainOfThought, ReAct, ProgramOfThought, BestOfN, Refine, MultiChainComparison). Modules **komponálhatóak** Python-koddal — egy RAG-pipeline három modul-hívás (retrieve → reason → answer).

### 3. Optimizer (teleprompter) — automatikus prompt+weights tanulás

A signature és modulok adottak; az optimizer kompilálja őket **konkrét promptokká, demo-példákká, esetleg fine-tuned súlyokká**. Kanonikus optimizerek:

- **BootstrapFewShot** — saját maga generál demo-példákat a trainsetből
- **BootstrapFinetune** — supervised fine-tune helyi vagy nagy modellen
- **MIPROv2** — Bayes-optimalizáció több modulon
- **COPRO / SIMBA** — koordinált prompt-evolution
- **GEPA** — Genetic-Pareto reflective evolution (alább részletesen)

## GEPA — a Pareto-front-os reflektív optimizer

GEPA (Genetic-Pareto, 2025) három mechanizmus köré épül:

1. **Reflective prompt mutation** — egy meta-LLM **strukturált execution-trace-ek** (input, output, hibás parse, constraint-violation) alapján **természetes-nyelvi feedback-et reflektál**, és új promptot javasol. NEM scalar-reward, hanem rich-textual-trace alapján.
2. **Pareto-frontier candidate selection** — nem a globális best-candidate-et mutálja (lokál-optimum csapda), hanem a Pareto-frontot tartja fenn: minden olyan kandidátot, ami **legalább egy eval-instance-en a legjobb**. Mutation-célnak a coverage szerinti súlyozással sample-el a frontról.
3. **Optional system-aware crossover** — különböző leszármazási vonalakból merge-eli a legjobban teljesítő modulokat.

**Eredmény:** néhány tíz rollout után outperforms RL-based prompt-tanulást.

## Mintázat (generic-reusable)

```
[Declarative I/O signature]  ←  ember írja, magas-szintű
        ↓
[Module composition Python-kóddal]  ←  ember írja, kontroll-flow
        ↓
[Adapter generál promptot]  ←  rendszer, swappable
        ↓
[Optimizer iteratív futtatja a pipelinet]  ←  AUTOMATIKUS
   - mintát hozzáad few-shot demo-ként
   - prompt-utasítást átfogalmaz
   - rich textual feedback → reflektív mutation (GEPA)
   - Pareto-front fenntart
        ↓
[Compiled program]  ←  perzisztens, deploy-olható
```

## Hogyan releváns a vault-meta SV-nek

- **SV-2 Recursive Self-Improvement (RSI)** — a Tier-1 RSI pillérünk **pontosan** GEPA-alapú (`gepa.optimize()` valós Pareto-front 0.541→0.619 +14.3%, ref: [[../11-wiki/sv-02-recursive-self-improvement]]). DSPy az ezt embeddelő keret — érdemes a custom GEPAAdapter+ClaudeCodeReflectionLM-et szabványosítani DSPy Signature/Module formára, akkor a többi DSPy-optimizer (MIPROv2, SIMBA) is **automatikusan elérhető**.
- **SV-4 Tool composition** — DSPy `ReAct` és `ProgramOfThought` module-ok pontosan a Toolformer/Voyager-vonal abstrakciós-rétegét adják; az MCP-skill-discovery-nk fölé jöhet egy DSPy-szintű komponáló réteg.
- **SV-5 Crystallization automation** — a G-Eval bullet-scoring kifejezetten illeszkedik a GEPA "feedback metric"-ben elvárt `dspy.Prediction(score=..., feedback=...)` formára. **Felmerült ötlet:** crystallize-bullet-scoring-ot DSPy `Module` + `Optimizer` formára átalakítani.
- **Eval cascade (Layer 1-2.5)** — a layered-eval kaszkádunk hierarchikus, **chained DSPy modules**-ban kifejezhető (`Layer1 → Layer2 → Layer3` mindegyik egy `dspy.Module`).

## Mintázat-buktatók

- **Signature ≠ prompt** — sokan a docstring-be akarják belerakni a "végső promptot"; nem, a docstring magas-szintű, az optimizer rakja össze a konkrétat
- **Trainset-quality > optimizer-choice** — 30-50 jó példa fontosabb mint a "legjobb" optimizer; a frontier-research konzisztens itt
- **GEPA feedback-quality** — `score=0.0/1.0` csak akkor működik jól, ha mellette rich textual `feedback="failed at step 3: regex no-match on `\\d{4}`"`-féle szöveg jön
- **Inference-time search vs train-time optimization** — GEPA `track_best_outputs=True` flag-gel test-time search-mechanizmus is, NEM csak train-time prompt-optimizer
- **DSPy ≠ LangChain** — DSPy a **programozási réteg** (signature+module), LangChain az **integrációs réteg** (vendor-bindings, retrievers). Komplementer, NEM rivális

## Kapcsolódó

- [[11-wiki/sv-02-recursive-self-improvement]] — saját Tier-1 RSI custom GEPAAdapter-rel
- [[11-wiki/sv-04-tool-composition]] — module-composition tengely
- [[11-wiki/g-eval-bias-mitigation-pattern]] — scorer-prompt-engineering, ami DSPy `Module` formán szabványosítható
- [[10-raw/external/stanfordnlp_dspy/README]] — forrás
