---
name: benchmark-data-pipeline-fidelity-gotchas
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#benchmark", "#methodology", "#evaluation"]
---

# Benchmark data-pipeline fidelity gotchas

> [!info] When to apply
> Building or running ANY benchmark where the test-pipeline ingests data, runs queries, and matches results against ground-truth labels. **The data-pipeline fidelity (mapping, dedup, schema consistency) is often a bigger source of measurement error than the algorithm being benchmarked.** Quantify the data-pipeline gotchas BEFORE you trust any aggregate number.

## A pattern

```
Test-pipeline failure surface:
  Ingest    → Index    → Query    → Result     → Match
   ↓           ↓           ↓          ↓           ↓
  dedup     schema-evol  fetch-K   path-resolve  ground-truth
  batches   path-rename  topK-bias mapping-drift label-noise
   ↓           ↓           ↓          ↓           ↓
  orphans   mismatch    truncation  filter-loss  inflated metric
```

**Failure mode**: a benchmark reports `91% R@5`, but the actual production-recall is `~78%`. The 13pp gap is caused by gotchas in the **data-pipeline**, not in the retrieval algorithm.

## Concrete case — RRF hybrid-fusion 91% → 78% (2026-05-20)

### Gotcha 1: Multi-batch ingest with duplicates → inflated RRF score

```
Ingest run 1: 89 sessions, title="Session"          → 89 obsIds
Ingest run 2: 573 docs (incl. same 89 sessions), title="VaultDoc" → 573 obsIds
                                                                       ↑
                                                          NOW: 89 docs have 2 obsIds each
```

**Symptom**: agentmemory's smart-search returns both copies for the same content. RRF score-aggregation **double-counts** the same document, inflating its rank.

**Detection**: query for a known doc; if the same `_path` appears twice in top-10, you have duplicates.

**Fix**: reset ingest state, re-ingest from clean (1 entry per file), maintain a persistent ID→path map for the production system. **6-10pp inflation removed**.

### Gotcha 2: ID→path mapping inconsistent across ingest batches

```
ingest-batch-1.json: {"obsId_A": "sessions/foo.md"}
ingest-batch-2.json: {"obsId_B": "sessions/foo.md"}    # same path, different ID!

benchmark uses ID_TO_PATH_MAP = ingest-batch-2.json
  → Returns obsId_A from search? PATH MISSING → counted as MISS
  → Returns obsId_B from search? PATH FOUND → counted as HIT
```

**Symptom**: same query returns inconsistent results depending on which batch's IDs the search engine prefers.

**Fix**: **single global ID→path map**, merged across all ingest batches (or rebuild from scratch).

### Gotcha 3: Title-leak via auto-title generation

Many storage systems (agentmemory, Pinecone, others) auto-generate a `title` field from the first N characters of content if not explicitly set. If your query-mining anchors on **headings** or **filenames** (which often appear in those first N chars), the index gets a free signal that inflates measured recall.

**Detection**: re-ingest with explicitly-generic title (`title="VaultDoc"`), measure delta.

**Concrete delta in our case**: 16pp inflation (92% with path-leak title → 76% with generic title on 89-session corpus).

**Fix**: explicit generic title, or post-hoc strip the auto-title from search matches before scoring.

### Gotcha 4: Corpus-size mismatch between systems being compared

```
System A indexes 89 docs.
System B indexes 573 docs.

Query Q matches doc-X in System A's top-5 (recall = 1.0).
Query Q matches doc-X in System B's top-5 (recall = 1.0).
                    ↑
Looks equal — but System A had 89-doc-pool, System B had 573-doc-pool.
System A's recall is INFLATED by ~6x lower difficulty.
```

**Fix**: enforce identical corpus boundaries (ingest the same N docs into both systems, or filter both to the same retrievable subset).

### Gotcha 5: Query-distribution overfit

If you mine queries via methodology M1, tune the system on those queries, and report recall measured on the same M1 queries — **you've overfit to M1's bias**.

**Detection**: build a 2nd query-set via a different methodology M2 (e.g., heading-mining vs IDF-mining). Measure the delta.

**Concrete delta in our case**: tuning 85.39% (IDF-mining) vs held-out 69.66% (heading-mining) = **16pp methodology-overfit**.

### Gotcha 6: Result-filtering after fetch

```
search.fetch(topK=5) → returns 5 IDs
filter for `id in valid_id_set` → 3 IDs remain (2 dropped as orphans)
take top-K=5 → only 3 results

# Methodology bug: the 2 dropped IDs may have been valid matches that we couldn't resolve
```

**Symptom**: top-K returned is smaller than requested; recall measurement is pessimistic but in a non-systematic way.

**Fix**: either (a) fetch more (topK=fetch_k > K) and filter, or (b) ensure valid_id_set is complete (no orphans).

## Detection checklist

Before publishing a benchmark number, run this checklist:

- [ ] **Index dedup**: query for a known-good doc; does it appear once or multiple times in top-N?
- [ ] **Mapping consistency**: each `id` in the search-result resolvable to exactly one `path`?
- [ ] **Title/metadata explicit**: did I set title/metadata explicitly, or is auto-generation injecting leak-signal?
- [ ] **Corpus parity**: do all systems being compared index the same N docs (boundary-tight)?
- [ ] **Query-distribution diversity**: are queries mined with ≥2 methodologies; is the recall similar on both?
- [ ] **Result-filtering loss**: is `len(top_K_returned)` consistently == K, or sometimes less?

## Generalizes to

- **Vector DB benchmarks** (Pinecone, Weaviate, Chroma, Milvus) — same dedup/mapping/title-leak gotchas
- **RAG eval frameworks** (RAGAS, TruLens, Phoenix) — same pipeline fidelity questions
- **MCP-tool benchmarks** — auto-generated metadata can leak signals
- **A/B test analysis** — corpus-size mismatch is the silent overfit-source in product experiments
- **ML training-set vs test-set hygiene** — same theme, different abstraction layer

## Source verified

- **RRF 91% → 78% finding**: [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]
- **Head-to-head TIE methodology**: [[../06-Audits/2026-05-20 agentmemory head-to-head LongMemEval-S R@5 — TIE 52.81 percent, 22pp ensemble-gain potential]]

## Kapcsolódó

- [[tuning-vs-production-recall-honest-reporting]]
- [[rrf-hybrid-fusion-retrieval-pattern]]
- [[g-eval-bias-mitigation-pattern]]
- [[../07-Decisions/2026-05-20 Production retrieval-stack v2 — RRF hybrid-fusion architecture]]
