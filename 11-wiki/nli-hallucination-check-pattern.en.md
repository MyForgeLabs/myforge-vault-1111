---
name: nli-hallucination-check-pattern
type: wiki
lang: en
translated_from: nli-hallucination-check-pattern
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/eval", "#topic/llm-as-judge", "#topic/hallucination", "#topic/rag"]
---

# NLI-based hallucination check (Learnings ↔ session-trace)

## TL;DR

**Natural Language Inference (NLI)** as a separate layer in the LLM-as-judge pipeline: it checks the factual consistency of a generated summary / Learnings / answer (hypothesis) against the source trace (premise). Cheap (nano-model + classifier head), deterministic output (`entailment | neutral | contradiction`), high precision on subtle inconsistencies that a plain G-Eval rubric is insensitive to.

## Background

- A continuous-evaluation axis often includes a "NLI judge compares Learnings to raw trace" Layer 2.5 implementation
- A crystallization automation axis uses NLI-based anti-hallucination gates between propagated bullets and target wiki content
- A cognitive-layer / NotebookLM-style axis can use NLI as the hallucination-measurement status per Eugene Yan AlignEval and "Task-Specific LLM Evals"
- NLI as an orthogonal check layer next to G-Eval self-favouritism bias, calibrated on a paired sample set

## Pattern

NLI is 3-class classification (entailment / neutral / contradiction), non-generative (logits, NOT free text), so 10-100× cheaper than an LLM judge and reproducible. The vault pipeline applies it to `## Learnings` sections: every bullet → "hypothesis", a session-trace window → "premise", and the NLI model returns the 3-class probabilities. If P(contradiction) > P(entailment), the bullet gets a "hallucinated" flag.

Architecturally, NLI is a **second-pass filter** after a generative judge (NOT instead of it): the G-Eval/LLM-judge opens classification (relevant? valuable?), NLI closes the factual gate. This is the "cascading eval" pattern (see [[layered-eval-cascading-pattern]]) — the expensive layer only runs if the cheap NLI did not rule it out.

Code: `microsoft/deberta-v3-large-mnli` or `cross-encoder/nli-deberta-v3-base` — CPU 50-200ms/pair, barely measurable on GPU. The L2.5 implementation runs as a batch-job script.

## Anti-patterns

- **Replacing NLI with a generative LLM "Pass/Fail?" prompt.** Latency is 100×, cost 1000×, and generative bias returns — exactly what NLI was supposed to avoid.
- **Using only NLI, without a generative judge.** NLI does not measure relevance, only factuality — a true-but-irrelevant Learnings will get entailment, but is still useless.
- **Running NLI on a long premise.** Above the 512-token cap, deberta-MNLI degrades — build a sliding-window premise or retrieve only the top-3 most relevant chunks.
- **Calling cross-encoder NLI a bi-encoder embedding.** Different technique, different use — bi-encoder is similarity, NOT logical inference.

## Reusable rules

1. **NLI for hallucination-gate only**, NOT for content evaluation. The "is this Learnings relevant?" question is for a generative judge / human.
2. **Cascading**: cheap NLI first, expensive LLM judge only on the survivors. Typical measurement: 53-80% bullet filtering by NLI, expensive judge cost reduced proportionally.
3. **Hypothesis = max 256 tokens**, premise = sliding-window 512-token chunk. Longer hypothesis (multi-bullet) → accuracy loss.
4. **Threshold per target**: wiki-bullet stricter (P(contradiction) > 0.40), session-note looser (>0.55). YAML config, hot-reloadable.
5. **Per-target threshold measurement**: 30-100 sample paired calibration mandatory; "global 0.50 everywhere" = false-negative cascade.
6. **Avoid NLI input completeness trap**: the premise must contain the full evidence block, NOT just the immediately-matching sentence — see [[nli-eval-input-completeness-trap]].

## Pitfalls

- **Language mismatch**: English-trained NLI on non-English bullets — accuracy plummets. Solution: multilingual NLI (XLM-R-MNLI) or LLM translation at premise level.
- **Negation flip**: deberta-MNLI is sensitive to "not" — if the generative judge rewrote the Learnings from "X is not stable" to "X is stable", NLI catches it, **but** only if the premise chunk contains the negated form.
- **Empty premise**: if retrieval finds no relevant chunk, do NOT return neutral; emit a "no-evidence" flag — otherwise the hypothesis "passes" all checks.
- **Domain shift**: on medical or legal domains, deberta-MNLI accuracy drops ~10-20pp vs general news text. Domain fine-tuning or a specific model (BioBERT-MNLI) recommended.
- **Multi-claim bullet trap**: a bullet contains multiple claims ("X is stable AND Y improves") — the NLI model entails or contradicts the whole, NOT per-claim. Atomic-claim decomposition preprocessing is mandatory.
- **Smart-threshold over-tuning**: calibrating per-target P(contradiction) on N=30 will scale poorly. Validation set N≥100, weekly drift monitoring required.

## When to use / when NOT to use

| Use case | NLI recommended? | Why |
|---|---|---|
| Session Learnings → wiki propagation | YES | Bullet-level factual inconsistency gate |
| Search-result relevance ranking | NO | Reranker / cross-encoder bi-encoder is better (semantic similarity, NOT logical) |
| RAG-grounded answer audit | YES | Whether the generated answer actually comes from the retrieved context |
| Long-document summary audit | PARTIAL | Sliding-window required, plus multi-claim decomposition |
| Subjective / creative output (story, design) | NO | NLI focuses on factuality, does not evaluate creative quality |

## Related

- [[layered-eval-cascading-pattern]] — NLI as L2.5 cheap layer
- [[g-eval-bias-mitigation-pattern]] — complementary eval-strictness
- [[nli-eval-input-completeness-trap]] — premise-building gotcha
- [[sv-07-continuous-evaluation]] — full eval architecture
- [[reranker-cost-optimization-not-size]] — similar cost arch (cheap-first, expensive-only-if-needed)
- [[auto-propagation-confidence-gate]] — NLI output as propagation input
