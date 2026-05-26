---
name: DSPy signatures + GEPA optimizer pattern
description: DSPy programmatic-LM-stack pattern - signatures (input/output declaration), Modules (composed pipelines) and GEPA (reflective Pareto-front prompt optimizer) - reusable code-instead-of-prompt and feedback-based prompt-evolution framework
type: wiki
lang: en
translated_from: dspy-signatures-and-gepa-optimizer-pattern
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "tool-composition", "self-improvement", "frontier-research", "sv-research"]
source: external-repo stanfordnlp/dspy (MIT)
parent: [[11-wiki/sv-04-tool-composition]]
---

# DSPy signatures + GEPA optimizer pattern

The **DSPy** framework from Stanford NLP lab (since ~2023, becoming an industry standard by 2025 H2) starts from the realisation that brittle, hand-tuned prompt strings are NOT a good interface to foundation models. Instead: **program, don't prompt** — declarative Python code + automatic optimisation.

## Frontier context

- **Source:** [github.com/stanfordnlp/dspy](https://github.com/stanfordnlp/dspy), [dspy.ai](https://dspy.ai) (docs)
- **License:** MIT (Stanford NLP, Omar Khattab et al.)
- **Maintainers:** Stanford NLP lab, Omar Khattab, Matei Zaharia, Chris Potts
- **Citation:** Khattab et al. 2024 ICLR ("DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines", arXiv:2310.03714)
- **GEPA paper:** Agrawal et al. 2025 ("GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning", arXiv:2507.19457)

## Architecture — three primitives

### 1. Signature — declarative I/O contract

```python
class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""
    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")
```

The signature is **NOT the prompt** — the signature is the I/O schema and a high-level task description. The actual prompt is generated at runtime by an **Adapter** (ChatAdapter / JSONAdapter / XMLAdapter / TwoStepAdapter). This separation of concerns is analogous to how a SQL query is not the B-tree traversal.

### 2. Module — composed pipeline element

A `dspy.Module` is an LLM-call stack (ChainOfThought, ReAct, ProgramOfThought, BestOfN, Refine, MultiChainComparison). Modules are **composable** in Python — a RAG pipeline is three module calls (retrieve → reason → answer).

### 3. Optimizer (teleprompter) — automatic prompt+weights learning

Signatures and modules are given; the optimizer compiles them into **concrete prompts, demo examples, possibly fine-tuned weights**. Canonical optimizers:

- **BootstrapFewShot** — auto-generates demo examples from the trainset
- **BootstrapFinetune** — supervised fine-tune on a local or large model
- **MIPROv2** — Bayesian optimisation across multiple modules
- **COPRO / SIMBA** — coordinated prompt evolution
- **GEPA** — Genetic-Pareto reflective evolution (detailed below)

## GEPA — the Pareto-front reflective optimizer

GEPA (Genetic-Pareto, 2025) is built around three mechanisms:

1. **Reflective prompt mutation** — a meta-LLM **reflects natural-language feedback** based on **structured execution traces** (input, output, failed parse, constraint violation) and proposes a new prompt. NOT scalar-reward, but rich-textual-trace based.
2. **Pareto-frontier candidate selection** — does not mutate the global best candidate (local-optimum trap), but maintains a Pareto front: every candidate that is **best on at least one eval instance**. Mutation samples from the front by coverage-weighting.
3. **Optional system-aware crossover** — merges the best-performing modules across different lineages.

**Result:** after a few tens of rollouts, outperforms RL-based prompt learning.

## Pattern (generic-reusable)

```
[Declarative I/O signature]  ←  human writes, high-level
        ↓
[Module composition in Python]  ←  human writes, control flow
        ↓
[Adapter generates prompt]  ←  system, swappable
        ↓
[Optimizer iteratively runs the pipeline]  ←  AUTOMATIC
   - adds samples as few-shot demos
   - rewrites prompt instructions
   - rich textual feedback → reflective mutation (GEPA)
   - maintains Pareto front
        ↓
[Compiled program]  ←  persistent, deployable
```

## Pattern pitfalls

- **Signature ≠ prompt** — many try to cram the "final prompt" into the docstring; no, the docstring is high-level, the optimizer assembles the concrete prompt
- **Trainset quality > optimizer choice** — 30-50 good examples matter more than the "best" optimizer; frontier research is consistent on this
- **GEPA feedback quality** — `score=0.0/1.0` only works well when accompanied by rich textual `feedback="failed at step 3: regex no-match on `\\d{4}`"`-style text
- **Inference-time search vs train-time optimisation** — GEPA with `track_best_outputs=True` becomes a test-time search mechanism, NOT just a train-time prompt optimizer
- **DSPy ≠ LangChain** — DSPy is the **programming layer** (signature+module), LangChain is the **integration layer** (vendor bindings, retrievers). Complementary, NOT rivals

## Relevance to self-improving agent stacks

- **Recursive Self-Improvement** — a Tier-1 RSI pillar can be **exactly** GEPA-based (verified `gepa.optimize()` real Pareto-front 0.541→0.619 +14.3%). DSPy is the embedding framework — worth standardising a custom GEPAAdapter+ReflectionLM on DSPy Signature/Module form, so the other DSPy optimizers (MIPROv2, SIMBA) become **automatically available**.
- **Tool composition** — DSPy `ReAct` and `ProgramOfThought` modules give exactly the Toolformer/Voyager-line abstraction layer; an MCP-skill-discovery layer can sit underneath a DSPy composition layer.
- **Crystallization automation** — a bullet-scoring evaluator fits cleanly into the GEPA "feedback metric" expectation of `dspy.Prediction(score=..., feedback=...)`. A standard pattern: convert bullet-scoring to a DSPy `Module` + `Optimizer`.
- **Eval cascade** — a layered-eval cascade is hierarchical, **expressible as chained DSPy modules** (`Layer1 → Layer2 → Layer3`, each a `dspy.Module`).

## Related

- [[sv-02-recursive-self-improvement]] — custom GEPAAdapter integration
- [[sv-04-tool-composition]] — module-composition axis
- [[g-eval-bias-mitigation-pattern]] — scorer-prompt-engineering standardisable as DSPy `Module`
