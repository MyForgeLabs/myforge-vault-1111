---
name: metric-design-pivot-not-algorithm
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#project/sv", "metric-design", "evaluation"]
---

# Metric-design pivot, not algorithm

When a target metric doesn't move after multiple well-executed algorithm changes, suspect the **metric itself**, not the algorithm. A misformed metric is invisible until you stress-test it — every improvement looks like a failure.

## The pattern

You have a target metric **M** and a goal value **T**. You ship algorithm changes A1, A2, A3 — each one should structurally help. M stays roughly flat. The instinct is "we need A4 / better A3 / a tweak to A2." The honest move is often "**M is the wrong metric**."

Concrete signals that M is misformed:

- **Different domain-knowledgable extractors should agree on M** but they have low M-overlap by-design (different vocabularies, different resolutions).
- **A secondary axis is at ceiling already** (e.g. an XR or coverage axis = 1.0) while M is at the floor — the agreement signal is there, just not where M is looking.
- **The algorithm changes shrink the denominator without growing the numerator** in M's formula. Each "improvement" makes M technically worse via union-growth, even though the actual content quality improves.

## Worked example — Jaccard label-overlap (2026-05-19→20)

The `vault-graph-diff` between Memgraph Tier-1 (LLM-extracted narrative concepts) and graphify Tier-2 (markdown-section-paths) had a Phase-4 acceptance gate of **Jaccard ≥ 0.05**. Movement after 4 algorithm changes:

| Algorithm change | Jaccard before | Jaccard after | Delta |
|---|---:|---:|---:|
| Phase-1 Tier-A noise-cleanup (-791 entity) | 0.0070 | 0.0070 | +0 |
| Phase-2 Tier-C composite (-3074 entity) | 0.0070 | 0.0078 | +0.0008 |
| Phase-3 selective re-extract vocab v3 | 0.0078 | 0.0071 | -0.0007 |
| Option-B tree-sitter prepass (planned, +156 typed entities) | 0.0071 | **0.0068** (projected) | -0.0003 |

Four serious algorithm interventions, all empirically near-zero. The premise (Tier-1 and Tier-2 should share vocabulary) was **empirically false** — graphify-out inspection showed it parsed 367 .md + 2 .json + 1 .sh, zero Python source files. The "tree-sitter + Leiden" framing in graphify's README was about markdown parsing, NOT code-symbol extraction.

The pivot was metric-design, not algorithm: drop the Jaccard target, replace with **file-coverage agreement (FCA)** + **co-occurrence density (CD)** + **cross-reference rate (XR)**. Empirical effect after 171-file backfill:

| Metric | Baseline | Final | Status |
|---|---:|---:|---|
| Jaccard (old) | 0.0070 | ~0.0070 | flat (still misformed) |
| **FCA (new)** | 0.4676 | **0.9297** | ceiling reached |
| **XR_T1 (new)** | **1.0000** | **1.0000** | unchanged-truth — was always there |
| **XR_T2 (new)** | 0.4461 | **0.8965** | PASS |

The XR_T1 = 1.0 unchanged across baseline → all checkpoints → final is the giveaway: **every LLM-extracted concept has a graphify structural anchor**. That signal existed at baseline. Jaccard hid it under a structurally-wrong question ("do the labels match?") when the right question was ("do they cover the same files?").

## When to suspect the metric

| Signal | Likely interpretation |
|---|---|
| 3+ algorithm changes that "should" help, M stays flat | M's denominator is the wrong universe |
| Multi-axis metric set has 1 axis already at ceiling | That ceiling-axis is the real signal; M is hiding it |
| M is a label-overlap / set-intersection metric over disjoint-by-design vocabularies | Use file-overlap / source-overlap instead |
| M decreases as you add what should be valuable data (because union grows faster than intersection) | M is a ratio that punishes the numerator growth you want |

## Pattern reuse — when this applies beyond Jaccard

- **BLEU/ROUGE for paraphrase eval** — same family: lexical-overlap doesn't measure semantic equivalence, and a "better" paraphrase model often *reduces* BLEU. The fix is replacing with NLI-judge / semantic-similarity, not tuning more on BLEU.
- **Recall@K with K too small** — if recall@5 plateaus while recall@50 keeps growing, the gate is the K, not the retrieval algorithm.
- **Coverage-pct against an unstable denominator** — if you can shrink the denominator by exclusion-policy faster than you can grow the numerator by ingest, the metric is structurally unfair.

## When the metric is fine but the target is wrong (2026-05-21 addendum)

The Path-Z reframing (2026-05-20) replaced Jaccard with the FCA / CD / XR triple. By Sprint-3 cleanup (2026-05-21) **three of four metrics cleared their targets**, but **CD plateaued at 0.40** against a ≥0.50 target. This is a **distinct failure mode** from the original Jaccard story:

- Jaccard ≥0.05 case = **the metric was misformed** (measuring the wrong thing entirely)
- CD ≥0.50 case = **the metric is fine, the target value was misformed** (CD is a healthy mid-band metric; ≥0.50 implies vocabulary collapse)

Empirically, by-design two orthogonal extractors (Tier-1 narrative concepts vs Tier-2 markdown-section-paths) produce CD in a **healthy band of [0.35, 0.50]**. Above 0.50 = vocabulary collapse (extractors converging on the same layer = bug, not feature). Below 0.20 = measurement bug or extractor mis-config.

```
CD band reading:
  ≥ 0.50    🔴 vocabulary collapse — investigate
  0.35–0.50  🟢 healthy orthogonal complementarity
  0.20–0.35  🟡 strong asymmetry — extraction-density bug?
  < 0.20     🔴 measurement bug or mis-config
```

The CD target was revised ≥0.50 → ≥0.35 ([[../07-Decisions/2026-05-20 CD target revision — narrative-structural asymmetry|ADR]]). Current 0.40 = PASS in the healthy band.

**Goodhart-warning generalization:** when a metric has a **by-design bounded range** (not "higher always better"), a target that pushes the metric outside its design-band is the failure mode, not the metric. Before tuning the algorithm to hit the target, ask: *what's the design-band of this metric, and is my target inside it?*

Common metric-shapes with bounded design-bands (where this addendum applies):

| Metric family | Design-band reason |
|---|---|
| Complementarity / agreement between orthogonal extractors | Above ceiling = vocabulary collapse |
| Inter-rater κ (Cohen's kappa) in subjective domains | Above 0.85 often = annotators sharing systematic bias |
| LLM-as-judge agreement vs ground-truth | Above ~0.95 = judge-leakage or test-set overfit |
| Embedding-similarity for diverse-doc retrieval | Above ~0.85 = vocabulary-domain collapse, NOT semantic match |

In each case the question to ask first is "what's the healthy band?", not "how do I push higher?".

## Related

- [[../07-Decisions/2026-05-20 Two-tier complementarity over Jaccard label-overlap]] — the ADR this pattern is extracted from
- [[../06-Audits/2026-05-20 Option-B premise empirical refutation — graphify vocabulary is markdown not code]] — the diagnostic that triggered the pivot
- [[tuning-vs-production-recall-honest-reporting]] — sibling pattern (metric-honesty vs marketing-recall)
- [[../07-Decisions/2026-05-20 CD target revision — narrative-structural asymmetry]] — 2026-05-21 case-study (CD ≥0.50 → ≥0.35)
- [[engineering-honest-mid-sprint-postscript]] — companion writing-pattern for documenting metric pivots publicly
- [[vendor-feature-verify-before-workaround]] — sibling pattern (verify-the-data-not-the-tooling-metadata)
- [[two-tier-graph-extraction]] — the system this lesson came from
