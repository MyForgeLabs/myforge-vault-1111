---
name: multi-axis-metric-flat-axis-signal
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#project/sv", "metric-design", "evaluation"]
---

# Multi-axis metric: the flat axis is often the real signal

When you design a metric set with 3-5 axes and one of them sits at ceiling (or floor) **unchanged across every measurement**, that flat axis is usually telling you the actual truth — not noise to ignore.

## The pattern

You build a multi-axis metric (FCA, CD, XR_T1, XR_T2) to capture "agreement" between two systems. Three axes move with your sprint. One axis is stuck at 1.0 (or 0.0) from day one. The instinct is "axis-N is degenerate, drop it." The right read is often "axis-N is the **unchanged-truth** — the agreement signal that was always there, just invisible because the wrong gate-metric was hiding it."

## Worked example — XR_T1 across the Path-Z reframing (2026-05-19→20)

Built three complementarity metrics to replace the misformed Jaccard target:

| Metric | Definition | Baseline | Post-50 | Post-66 | Final (171) |
|---|---|---:|---:|---:|---:|
| FCA | files both systems extract from / files either system extracts from | 0.4676 | 0.6027 | 0.6459 | 0.9297 |
| CD | mean min/max entity-count per shared file | 0.2717 | 0.3331 | 0.3494 | 0.3967 |
| **XR_T1** | % of Tier-1 entities whose provenance file is also in Tier-2 | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| XR_T2 | % of Tier-2 nodes whose source file is also in Tier-1 | 0.4461 | 0.5788 | 0.6259 | 0.8965 |

**XR_T1 stays at 1.0 across every checkpoint.** Initial reaction: "useless axis, drop it." Real interpretation:

> Every single LLM-extracted concept is sourced from a file that graphify also indexes structurally. The "do these two systems agree on what's important?" question has a flat-out yes answer — the agreement was at 100% from day one. The Jaccard metric was hiding this because it was measuring **labels**, not **sources**.

The 1.0 was not noise; it was the truth. Jaccard 0.0069 was telling a false story.

## Why this happens

Multi-axis metric sets are designed to triangulate a phenomenon from multiple angles. Often **only one of the angles is structurally aligned with the underlying truth**, and the others measure noise, marketing, or misformed proxies. The one that sits at a flat extreme (ceiling or floor) is the one that snapped to truth and stays there.

Concrete predictors that a flat axis is the real signal:

- The flat axis has the **simplest definition** (one set-cardinality ratio, not a derived weighted score)
- The flat axis is **monotone-in-truth** (every actual improvement *should* push it; if it's already at extreme, the truth is at extreme)
- The non-flat axes are **artifact-laden** (penalize for union growth, depend on density, weighted by hyperparameter)

## Pattern reuse

| Domain | Flat axis | What it usually means |
|---|---|---|
| Retrieval eval | `recall@all = 1.0` | The correct answer is in the corpus — the failure is the ranker, not the index |
| Multi-judge LLM eval | `inter-judge-agreement = constant_high` | The disagreement-source is the *question*, not the model |
| Code-coverage | `executable-statement-coverage = 100%` but `branch-coverage = 60%` | The test-suite passes through, but doesn't explore |
| Graph-cross-validation | `XR-forward = 1.0` (this case) | The narrative-side is fully anchored to the structural-side |

## When NOT to apply this pattern

A flat axis is **not** the real signal if:

- It's flat at an **incongruous extreme** (e.g. accuracy = 100% on a hard task — likely a measurement bug)
- The flatness is **by construction trivial** (e.g. `precision_at_K=1 = 1.0` always when K=1 and you return one item)
- The axis is **degenerate over the test set** (no variation in inputs)

Verify the flat axis is meaningful before treating it as truth.

## Related

- [[metric-design-pivot-not-algorithm]] — sibling pattern (pivot the metric, not the algorithm)
- [[../07-Decisions/2026-05-20 Two-tier complementarity over Jaccard label-overlap]] — the ADR where this flat-axis revelation became the case for keeping XR_T1
- [[tuning-vs-production-recall-honest-reporting]] — honest-reporting sibling
- [[../06-Audits/2026-05-20 Tier-1 backfill COMPLETE 171-171 — FCA 0.93 (ceiling reached)]] — final measurement showing XR_T1 stayed 1.0 across all 11 batches
