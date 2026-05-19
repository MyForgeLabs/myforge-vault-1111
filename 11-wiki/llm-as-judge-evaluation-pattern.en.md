---
name: LLM-as-judge evaluation pattern
type: wiki
lang: en
translated_from: llm-as-judge-evaluation-pattern
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/reference"]
tag_backfill: 2026-05-19
---
# LLM-as-judge evaluation pattern

> [!info] What it solves
> Where **scalable quality judgement** is needed for many outputs but **human reviewers are expensive/slow**. LLM-as-judge has a second LLM rate the first LLM's output against a rubric. Classic use case: auto-gating of agent-generated content by a confidence threshold.

## The core idea

Naive pipeline: `Generator-LLM → Output → Human review`. Bottleneck at scale: a human reviewer handles ~10-50 outputs / day / person. LLM-as-judge takes over the reviewer role:

1. **Generator-LLM** produces an output (text, code, decision)
2. **Judge-LLM** (typically a different prompt, sometimes a different model) **evaluates with a rubric prompt**
3. **Rubric** is structured — score 0-1 + Pass/Fail + justification
4. **Threshold gate** decides: auto-accept if score > threshold, manual-review otherwise

## Variants

| Variant | Characteristic | When |
|---|---|---|
| **G-Eval** (naive LLM-as-judge) | 1 LLM call, CoT prompt + score output | Quick gate, low-stakes |
| **Critique Shadowing** | Judge-LLM **few-shot calibrated** against 20-50 human-labelled examples | Mid-stakes, better recall |
| **Self-RAG** | Generator evaluates itself at token level + retrieval | Real-time generation steering |
| **NLI-based** | Natural Language Inference judge (logical entailment) → more robust than scoring | Hallucination detection |
| **Multi-judge ensemble** | 3-5 judges vote, majority rule | High-stakes (medical, legal) |
| **Pairwise comparison** | Judge sees two outputs and picks A/B | Preference-dataset building |

## Pitfalls

### 1. Position bias

The judge statistically prefers the **earlier-listed** output. Mitigation: randomised order + bidirectional comparison.

### 2. Verbosity bias

The judge rates **longer** output as better. Mitigation: explicit "conciseness is a value" in the rubric.

### 3. Self-enhancement bias

The judge rates **its own model family's** output as better (GPT-4 prefers GPT-4 over Claude). Mitigation: cross-family judge + bias-correction prompt ([[g-eval-bias-mitigation-pattern]]).

### 4. False-Pass overconfidence

The judge often **passes everything** (lazy bias). Mitigation: calibration set, threshold adjustment, force-distribution.

### 5. Input-completeness blind spot

The judge does not notice when the input context is **incomplete** (e.g. the Generator was given fewer sources than needed). Mitigation: a separate NLI layer ([[nli-eval-input-completeness-trap]]).

## Concrete implementation (vault)

A crystallization layer uses this:

```
Generator: Session-end agent proposes propagation targets (5-15 bullets)
   ↓
Judge: G-Eval LLM-as-judge subagent (claude-code fanout, $0 cost)
   ↓ rubric: routing-pertinence + evidence-strength + non-duplication
Output: per-bullet score (0-1) + Pass/Fail + brief justification
   ↓
Threshold gate:
   • score >= 0.95 → auto-prop (Conservative mode)
   • 0.85 ≤ score < 0.95 → preview (default Shadow mode)
   • score < 0.85 → discard-candidate
```

Confidence threshold: hot-reloadable config file. Production-ramp protocol: shadow → conservative → aggressive ([[crystallize-threshold-ramp]]).

## The 4-layer quality gate

Instead of a single-judge, a cascading 4-layer eval is preferred:

| Layer | What it checks | Cost | Eliminates |
|---|---|---|---|
| **L1: Rule-based** | Format, frontmatter existence, wikilink validity | $0 | ~30% trivial-Fail |
| **L2: G-Eval scoring** | Routing-pertinence + evidence + relevance | $0 (subagent fanout) | ~40% borderline |
| **L2.5: NLI-judge** | Logical entailment between bullet and target | $0 (local model) | ~10% subtle mismatch |
| **L2.6: Coherence check** | Cross-bullet contradiction detection | $0 (KO-DB query) | ~5% contradiction |

Cascading advantage: an expensive L3 (manual review) only fires on ~15%, the L1-L2.6 layers filter the cleanly-decidable cases. Details: [[layered-eval-cascading-pattern]].

## Bias-mitigation prompt template

A G-Eval bias-mitigation prompt (measured: conf 0.880→0.760, auto-prop 10/10→6/10) uses 4 bias blocks + a calibration anchor:

```
You are a STRICT judge. These are the biases you CONSCIOUSLY avoid:
- Self-enhancement: NOT preferring your own model family's style
- Verbosity: short and concise output can also score 1.0
- Position: order is irrelevant
- Lazy-pass: do not Pass everything; if unsure, Fail

Calibration anchor: a 1.0 score means "real example, evidence-grounded,
non-duplicate, correct target". 0.5 means "acceptable but borderline".

Bias self-check (CoT): before scoring, answer in 1 sentence:
"Which bias should I be most careful about for this bullet?"
```

See [[g-eval-bias-mitigation-pattern]] for the full template.

## When NOT to use LLM-as-judge

- **High-stakes, irreversible operations** (medical diagnosis, legal decision) — humans required
- **Definitional truth** (mathematical proof, code correctness) — use unit-test / formal-prover
- **Creative judgement without consensus** — use user-preference A/B test
- **Adversarial input** — the judge prompt can be manipulated via prompt-injection if input is untrusted

## Related

- [[sv-07-continuous-evaluation]] — continuous-eval research axis
- [[g-eval-bias-mitigation-pattern]] — bias-block prompt template
- [[layered-eval-cascading-pattern]] — L1-L2-L2.5-L2.6 cascading
- [[nli-eval-input-completeness-trap]] — NLI layer for input-completeness
- [[auto-propagation-confidence-gate]] — threshold gate before propagation
- [[crystallize-threshold-ramp]] — shadow → conservative → aggressive ramp protocol
- [[reranker-cost-optimization-not-size]] — judge size is not always directly proportional to quality
