---
name: Subagent-fanout context-aware classification pattern
type: wiki
tags: ["#type/wiki", "subagent-fanout", "classification", "ner", "entity-typing", "quality"]
created: 2026-05-18
updated: 2026-05-18
status: stable
lang: en
translated_from: subagent-fanout-context-aware-classification.md
---

# Subagent-fanout context-aware classification

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[subagent-fanout-context-aware-classification.md]] (Hungarian version).

The subagent-fanout pattern ([[claude-code-subagent-fanout]]) scales well for bulk LLM mutation ($0 cost in Claude Code), but **classification tasks** (entity typing, label injection, summary tagging, NER) have quality that varies drastically based on whether the subagent receives context for the item being classified. A **blind classifier** (item name only) typically yields ~5% false-positive rate and low recall; a **context-aware classifier** (subagent reads the source documents where the entity is mentioned) has FP-rate <2%, with recall +20-40pp higher.

## TL;DR

- **Blind fanout** = subagent INPUT is only `entity_name` → fast, cheap, but FP ~5%, low recall
- **Context-aware fanout** = subagent INPUT is `entity_name + 1-2 source excerpts` → slower (~2-3× the time), but FP <2%, recall +20-40pp
- **Hybrid strategy:** blind fanout in iteration 1 → keep high-confidence items → re-run ambiguous ones via context-aware in iteration 2
- **Reusable:** applies to every classification task (entity typing, doc categorization, sentiment, intent detection)

## Background — entity-typing pipeline evolution

An entity-typing project for a graph with 8,997 entities went through three iterations:

| Iteration | Pattern | Coverage | FP-rate (sample) |
|---|---|---|---|
| 1 | stand-in classifier (rule-based, entity-name regex only) | 14.87% | ~8% (manual sample, 4 wrong out of 50) |
| 2 | **blind subagent-fanout** (7 batches, entity-name only) | 28.9% → 72.8%* | ~5% |
| 3 | **context-aware subagent-fanout** (entity + source excerpt) | >90% target | <2% target |

*The 28.9% → 72.8% jump was the fanout COMBINED with the `mgclient.autocommit` fix — see [[mgclient-autocommit-silent-rollback]]. The increase attributable purely to fanout was significant, but the autocommit bug masked its real magnitude in the first 4 batches.

The blind iteration produced 2 primary error types:
1. **Homonym entities** — e.g. `"Cache"` can be an HTTP cache pattern, a character name in a game-design GDD, or a React `useMemo` cache. Without context, the subagent picks the most common meaning → wrong label for a specific vault segment.
2. **Domain-specific meanings** — e.g. `"Pocock"` in the context of Sequential Validity statistical methods, NOT the British political historian — a general-knowledge subagent can't tell. The context-aware iteration would resolve this from an excerpt of `Pocock-design-monitoring-statistics.md`.

## The pattern

### Blind iteration (Phase 1)

```python
# Fast, cheap, ~80% accuracy
def blind_classify(entity_name):
    prompt = f"""Classify this vault entity into one of:
    Concept, Decision, Pattern, Skill, Project, Person, Tool, Other.

    Entity name: {entity_name}

    Reply with ONLY the label, no explanation."""
    return subagent.run(prompt)
```

### Context-aware iteration (Phase 2)

```python
# Slower, more expensive, ~95-98% accuracy
def context_aware_classify(entity_name, source_mds):
    """source_mds: list of (path, excerpt) where entity is mentioned"""
    context = "\n\n".join(
        f"### {p}\n{e[:500]}" for p, e in source_mds[:3]
    )
    prompt = f"""Classify this vault entity based on actual usage context:

    Entity name: {entity_name}

    Context from documents where it appears:
    {context}

    Choose ONE label: Concept, Decision, Pattern, Skill, Project, Person, Tool, Other.

    Reasoning (1 sentence) then label on last line."""
    return subagent.run(prompt)
```

### Hybrid (production-grade)

```python
def hybrid_classify(entities):
    # Round 1: blind, high-throughput
    round1 = {e: blind_classify(e) for e in entities}

    # Confidence filter: concrete label, NOT "Other", NOT null
    confident = {e: l for e, l in round1.items() if l != "Other"}
    ambiguous = [e for e in entities if e not in confident]

    # Round 2: context-aware ONLY for ambiguous
    for e in ambiguous:
        sources = find_mentions(e, vault)
        round1[e] = context_aware_classify(e, sources)

    return round1
```

This handles 60-80% of items via the cheap blind path and spends the expensive context-aware budget on the rest. Vault-scale ROI is ~3-5× more significant than pure context-aware.

## When blind, when context-aware

| Task | Blind enough | Context-aware mandatory |
|---|---|---|
| Unique global proper noun (person name, brand) | ✓ | rarely |
| General concept without polysemy (HTTP, REST) | ✓ | only <2% domain-specific |
| Domain-specific code-word / internal project name | ✗ | MANDATORY |
| Polysemous entity (Cache, Pipeline, Worker) | ✗ | MANDATORY |
| Newly coined slug / freshly minted convention | ✗ | MANDATORY |
| Spec-violation detection | ✗ | MANDATORY (the spec is the context) |

**Rule of thumb:** if your corpus contains domain-specific jargon (and every serious long-form corpus does), the minimum is 2 iterations.

## Anti-pattern: "blind-only" big-bang

Do NOT run a large entity set (>5,000) with **blind only** classification and accept the result. The 5% FP inflates the typing coverage metric (false-positives look "typed"), but downstream features (search rerank by label, label-filtered graph traversal) train on noise. The FP-rate cascades into the **next layer's** quality, which is **harder to measure**.

Another anti-pattern: **skipping manual sampling**. Whether after a blind or context-aware iteration — a 50-100-item random sample for manual verify is mandatory. A high-confidence subagent report does NOT guarantee that the label is actually correct. LLM self-evaluation bias mitigation ([[g-eval-bias-mitigation-pattern]]) tells us that the LLM tends to overstate its own confidence.

## Reusable rules

| Task type | Recommended pattern |
|---|---|
| Entity typing (graph matrix) | Hybrid: blind → ambiguous context-aware |
| Doc categorization (markdown → folder) | Blind enough if taxonomy is stable |
| Tag suggestion | Context-aware mandatory (project conventions) |
| Sentiment analysis | Blind, except ironic/sarcastic domains |
| Intent detection (chat) | Context-aware (last 2-3 turns injected) |
| NER (general) | Blind (specialized model is materially better than LLM-fanout) |
| Spec-violation detection | Context-aware (the spec is the context) |

## Cost model

Subagent-fanout in Claude Code is $0 ($0 / agent call), but there's a **time cost**:
- Blind: ~2-3 sec/entity (simple prompt)
- Context-aware: ~6-10 sec/entity (3-5 MD excerpts read + classification)
- Hybrid 80/20: ~4 sec/entity average

For 8,997 entities, hybrid is ~10 agent-hours (parallel 8 subagents → ~1.25 hours wall clock). For production bulk tasks this is acceptable.

## Complementary patterns

- **Self-verification** — every subagent output is verified by ANOTHER subagent (two-phase quorum). More expensive but FP drops below 1%.
- **Ensemble** — 3 subagents classify independently, majority vote → even lower FP
- **Active-learning loop** — errors found in manual samples are added to the few-shot prompt for the next iteration
- **Source-quality weight** — `wiki/` sources outweigh `raw/` sources, context-injection priority
- **Confidence-threshold escalation** — blind output includes "confidence 0-1"; <0.7 → context-aware re-run

## Related

- [[claude-code-subagent-fanout]] — base pattern that this extends
- [[g-eval-bias-mitigation-pattern]] — LLM self-evaluation bias, which affects confidence scoring
- [[mgclient-autocommit-silent-rollback]] — a related pitfall discovered during the typing batch
- [[verification-step-before-claim]] — manual sampling as verification
