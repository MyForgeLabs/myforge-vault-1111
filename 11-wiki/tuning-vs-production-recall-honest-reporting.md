---
name: tuning-vs-production-recall-honest-reporting
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#evaluation", "#methodology", "#benchmark", "#integrity"]
---

# Tuning vs production-recall — honest reporting

> [!info] When to apply
> Before publishing a single-number benchmark result (R@K, accuracy, F1, recall, etc.) — **cross-validate on at least 2 methodology-distinct query/test sets**. The "tuning-recall" (measured on the set you iterated against) is **always inflated** relative to the "production-recall" (measured on unseen workloads). Quantify the gap. Publish the average, not the best.

## A pattern

```
Build tuning-set T (methodology M1)
Build held-out-set H (methodology M2, same domain, NO overlap in tuning iterations)

Tuning recall = recall(system, T)        # the number you optimized
Held-out recall = recall(system, H)      # the number you should report

Production recall ≈ (tuning + held-out) / 2  (often a fair estimate)
                 ≈ min(tuning, held-out) (pessimistic but safer for users)
```

**Never publish only the tuning number.** It misleads downstream users about what they'll actually experience.

## Concrete example — RRF hybrid-fusion (2026-05-20 finding)

We built `vault-search-fusion` (RRF hybrid of vault-search + agentmemory) and tuned `fetch-k`, `k_rrf` on a 89-Q LongMemEval-style query set mined via IDF (rare-term 2-gram from session body).

| Step | What we measured | Result |
|---|---|---|
| 1. Initial benchmark (with duplicates) | IDF-mined, mixed-state agentmemory | **91.01% R@5** |
| 2. Clean re-setup (575 unique docs) | Same IDF-mined queries (TUNING) | **85.39% R@5** |
| 3. Cross-validation (heading-mined queries, HELD-OUT) | Same RRF system, different query-mining | **69.66% R@5** |
| 4. Honest average | (85.39 + 69.66) / 2 | **77.5% R@5** |

**A 91% lett volna a marketing-szám.** Egy 6pp duplicate-artifact + 8pp tuning-overfit, **total 13pp inflation** valós production-recall-hoz képest. Publikáláskor 77.5% volt a helyes (vagy a pesszimista 69.66%).

## Hidden inflation sources

| Source | Tipikus inflation | Detection |
|---|---|---|
| **Data duplicates** (multiple ingest-batches, near-duplicate content) | 3-10pp | Re-ingest from clean state, verify single entry per source |
| **Title-leak / metadata-leak** (target tokens appear in indexed metadata) | 5-20pp | Use generic title/metadata, measure delta |
| **Query-distribution overfit** (test queries mined the same way as tuning queries) | 5-15pp | Use a different query-mining method on held-out |
| **Corpus-size mismatch** (one system indexes more than another) | 5-30pp | Enforce identical corpus boundaries |
| **Reranker over-tuned to test-set** (cross-encoder seeing tuning queries) | 3-10pp | Hold out 30% of queries from any cross-encoder fine-tuning |

## When honest-reporting matters most

- **OSS project benchmark in README** (users will quote it) → publish honest cross-val
- **HN/Reddit launch posts** (community will fact-check) → publish honest cross-val + methodology
- **Internal vs external recall claims** (sales-deck vs engineering-doc) → same number both places, no double-standard
- **Marketing pages** (claims become commitment) → use the **pessimistic** number (min of tuning/held-out), not average

## When tuning-recall is OK to cite

- **Internal optimization decision** ("which knob to turn next") — tuning recall is the right signal for direction
- **Ablation studies** ("removing component X drops tuning by Y") — relative deltas hold across methodologies
- **Engineering changelog / sprint-retro** (clearly labeled as "on tuning set X")

## Implementation tips

1. **Always have ≥2 query-mining methodologies** for the same domain. Build them up-front, before any tuning iteration. E.g., for retrieval: IDF-mined, heading-mined, hand-curated, NL-paraphrase (LLM-generated, on held-out content).
2. **Label benchmark output clearly**: `R@5 (tuning, n=89, IDF)`, `R@5 (held-out, n=89, heading)`, `R@5 (average)`. Don't hide which is which.
3. **Document the duplication-state of the index** in every benchmark: "fresh re-ingest", "incremental updates", "with X duplicates of Y files". Duplicates are the most common 3-10pp inflation source and are easy to overlook.
4. **Re-publish corrected numbers** when you find inflation. Don't suppress. The community respects honesty more than precision.

## Generalizes to

- **G-Eval / LLM-as-judge ground-truth ceiling** ([[g-eval-bias-mitigation-pattern]]) — measurement-classifier own noise sets observable-agreement ceiling
- **A/B test reporting** — winning condition on training-cohort ≠ winning condition on new-cohort
- **Model-card publication** — fine-tuned model "achieves X%" usually inflated 5-15pp vs production
- **OSS retrieval benchmarks** — BEIR/MTEB leaderboards have known overfit dynamics (researcher iterates against the public test-set)

## Source verified

- **RRF hybrid-fusion finding**: [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]
- **G-Eval ceiling analogue**: [[g-eval-bias-mitigation-pattern]] "Mining-classifier ground-truth-ceiling (B-8 100-bullet κ=0.708 finding)"
- **BEIR/MTEB known overfit**: industry consensus, no single-cite

## Kapcsolódó

- [[rrf-hybrid-fusion-retrieval-pattern]]
- [[g-eval-bias-mitigation-pattern]]
- [[longmemeval-vault-variant-pattern]]
- [[../07-Decisions/2026-05-19 LongMemEval K=5 sweet-spot — refute wider-pool lore]]
- [[../07-Decisions/2026-05-20 Production retrieval-stack v2 — RRF hybrid-fusion architecture]]
