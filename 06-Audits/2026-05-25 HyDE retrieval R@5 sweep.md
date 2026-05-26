---
name: HyDE retrieval R@5 sweep
type: audit
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/audit", "#project/sv", "#concept/hyde", "#concept/longmemeval", "retrieval-quality", "negative-result"]
related:
  - "[[11-wiki/hyde-query-rewrite-skeleton]]"
  - "[[2026-05-19 LongMemEval-S vault-variant v0.2]]"
  - "[[2026-05-19 LongMemEval v0.3 sweep results]]"
---

# HyDE retrieval R@5 sweep — 2026-05-25

R@5 measurement of Variant A (RRF fused-pool, `fetch_k=5` v0.3 sweet-spot) with vs without HyDE query rewriting, on the canonical LongMemEval-S 29-Q set.

> [!warning] Negative result
> **Both HyDE modes regress on this query class.** The vault retrieval-stack does NOT need HyDE today — the SV queries are already keyword-dense slug-style ("kgc-berles kisgépcentrum", "hash hash-by-provenance"), and any HyDE-expansion adds noise that hurts precision.

## Modes

| Mode | Description | Recall@5 | Hits | Elapsed | Δ vs baseline |
|---|---|---:|---:|---:|---:|
| **baseline** | no HyDE rewrite | **75.86%** | 22/29 | 4.3s | — |
| **hyde-fast** | keyword-expand fast-path (no LLM) | 44.83% | 13/29 | 4.3s | **−31.03pp** |
| **hyde-llm** | subagent-fanout LLM rewrite (Claude general-purpose, 4 batches × 7-8 queries) | 68.97% | 20/29 | 18.8s | **−6.90pp** |

## Verdict

- **hyde-fast** is a **31-point regression**. The keyword-expand-fallback path appends generic vault vocabulary (`session wiki audit ADR vault sprint`) when no topic-bank match exists. On 25/29 queries the fallback triggers; the generic tokens dilute the bge-m3 embedding so concrete-slug retrieval breaks.
- **hyde-llm** is a **7-point regression** AND **4.4× slower** (18.8s vs 4.3s). The Claude-generated hypothetical documents are domain-correct but introduce extra terminology that hurts the RRF rank-fusion on keyword-dense queries.
- **Recommendation:** keep HyDE OUT of the default retrieval path. The `--hyde` flag stays opt-in for experimental use; do not ship it to `vault-ko-query` defaults.

## Why HyDE hurts here (analysis)

HyDE's hypothesis: an embedding of a hypothetical *answer document* is closer to real answer documents than the *raw query* is. This is true when queries are under-specified natural-language questions ("how does X scale", "why did we choose Y over Z"). The LongMemEval-S canonical set we ported is the opposite shape — short keyword bundles that already contain unique vault-slug fragments:

| Query | Type | HyDE expected to help? |
|---|---|---|
| "kgc-berles kisgépcentrum" | slug + brand | NO — slug already matches one file exactly |
| "hash hash-by-provenance" | technical slug | NO — KO-DB term already unique |
| "balance wellbeing" | concept slug | NO — already maps to one project |
| "memgraph 1-re" | system + cardinality | MAYBE — sparse query |
| "auto-gen felismerés" | feature + adjective | YES — naturally vague |

Of the 29 queries only ~5-7 are vague enough for HyDE to plausibly help; on the other 22-24 HyDE adds noise. Net: regression.

## Run-context

- Timestamp: 2026-05-25T20:53:14Z
- Query-set: 29 canonical LongMemEval-S v0.2 A:cosine rows (loaded by `load_canonical_queries()`)
- fetch_k: 5 (v0.3 sweet-spot — see [[2026-05-19 LongMemEval-S K=5 sweet-spot — refute wider-pool lore]])
- Backend: vault-search hybrid (BM25 + bge-m3 cosine, RRF fusion), Memgraph warm daemon at `/run/vault-search.sock`
- HyDE script: `.vault-tools/scripts/vault-hyde-rewrite.py` (keyword-expand fast-path)
- LLM subagents: 4 parallel general-purpose agents, 29 hypothetical-doc requests total, $0 cost via Claude Code subagent fanout, ~3 min wall-clock
- Pending request dir: `/tmp/hyde-pending/` (kept on disk for reproducibility)

## Reproduce

```bash
# 1. Emit pending requests (29 JSONs)
vault-eval-hyde --emit-pending /tmp/hyde-pending

# 2. Fan out subagents (4 parallel general-purpose agents, one per batch)
ls /tmp/hyde-pending/hyde-*.json | grep -v MANIFEST | sort > /tmp/hyde-pending/files.txt
split -n l/4 -d /tmp/hyde-pending/files.txt /tmp/hyde-pending/batch-
# spawn one Agent per batch-XX file (see this session's prompt log)

# 3. Run the 3-mode comparison
vault-eval-hyde --mode all --consume /tmp/hyde-pending
```

## Follow-ups

- **NEGATIVE-RESULT MEMORY:** record in `11-wiki/hyde-not-warranted-on-slug-queries.md` so this is not retried unprompted.
- **Query-shape dependence:** if a future query-set is more natural-language (e.g. LongMemEval-M longer questions), re-measure — HyDE may flip positive there.
- **Reranker still helps:** the v0.3-B BGE-reranker variant gave +1.4pp on a similar query set. Reranker > HyDE for this corpus.
- **Cron schedule:** do NOT add `vault-eval-hyde` to cron. It's a one-shot diagnostic; re-run only if `vault-hyde-rewrite` script changes meaningfully.
