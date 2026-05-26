---
name: HyDE not warranted on slug/keyword queries
type: wiki
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/wiki", "#concept/hyde", "#concept/retrieval", "negative-result"]
related:
  - "[[hyde-query-rewrite-skeleton]]"
  - "[[../06-Audits/2026-05-25 HyDE retrieval R@5 sweep]]"
  - "[[../06-Audits/2026-05-19 LongMemEval-S K=5 sweet-spot — refute wider-pool lore]]"
---

# HyDE not warranted on slug / keyword-dense queries

**Verdict** (measured 2026-05-25, LongMemEval-S 29-Q canonical set): HyDE (Hypothetical Document Embeddings) **regresses** retrieval quality when queries are short keyword-bundles or slug-style fragments. Do NOT enable `--hyde` by default in `vault-ko-query` or `vault-search`.

## The numbers

| Mode | R@5 | Δ vs baseline | Latency |
|---|---:|---:|---:|
| baseline (RRF fused-pool, K=5) | 75.86% | — | 4.3s |
| `--hyde` fast (keyword-expand) | 44.83% | **−31.03pp** | 4.3s |
| `--hyde` LLM (subagent-fanout) | 68.97% | **−6.90pp** | 18.8s |

Both HyDE variants degrade. The LLM variant also costs 4.4× latency.

## Why HyDE assumes the wrong query shape

The original HyDE paper (Gao et al. 2022) targets under-specified natural-language questions where the raw query embedding is far from any answer document. The rewrite generates a hypothetical answer and embeds *that*, which lands closer to the real document cluster.

Our vault queries are the opposite shape:

- `kgc-berles kisgépcentrum` — slug + brand (unique to one file)
- `hash hash-by-provenance` — KO-DB technical term (unique to KO-DB context)
- `2026-05-13-sv-week2-extend` — literal session-slug
- `balance wellbeing` — project concept

Of 29 canonical queries, ~22-24 already contain a vault-unique token. HyDE expansion adds *more* terms, which dilutes the precise match in RRF rank-fusion and pulls in semantically-adjacent but wrong-file chunks.

## When HyDE WOULD help (rule of thumb)

Re-test HyDE if the query distribution shifts to any of:

- **Long-form natural-language questions** ("how does the vault handle stale memory?") — no unique slug, embedding starts far from documents
- **Conceptual queries without vault-specific vocabulary** ("what's the difference between RRF and reciprocal rank fusion?")
- **Multi-document synthesis queries** ("compare B-1 and B-7 sprint approaches")

A LongMemEval-M or LongMemEval-L corpus (longer queries) would be the right re-test gate.

## What helps INSTEAD on this corpus

The 2026-05-19 K-sweep audit established the actual sweet-spots for this query class:

| Lever | Baseline | Tuned | Lift |
|---|---:|---:|---:|
| fetch_k (RRF pool) | 50 | 5 | **+5.05pp** (76.77%) |
| BGE-reranker on K=20 pool | 71.72% | 73.74% | +2.02pp |
| HyDE rewrite | 75.86% | 68.97% | **−6.90pp** |

The dominant lever is `fetch_k`, then reranker. HyDE is below noise — skip it.

## The opt-in still exists

The `--hyde` flag remains in `vault-ko-query` and the eval driver supports `hyde_mode={None, "fast", "consume"}`. We keep them because:

1. The next query corpus shift (LongMemEval-M, agentic chat queries) may flip this
2. The 2-phase emit/consume pattern is the same one used by B-7 ctx-pass — keeping it exercised is cheap
3. The negative-result audit is itself useful research; ad-hoc re-measurement should stay easy

## Reproduce in one shell

```bash
vault-eval-hyde --emit-pending /tmp/hyde-pending
# spawn 4 parallel general-purpose subagents (one per batch file)
vault-eval-hyde --mode all --consume /tmp/hyde-pending
# audit MD lands at 06-Audits/<today> HyDE retrieval R@5 sweep.md
```

## See also

- [[hyde-query-rewrite-skeleton]] — what the rewriter does + 2-phase pending pattern
- [[../06-Audits/2026-05-25 HyDE retrieval R@5 sweep]] — full negative-result audit
- [[../06-Audits/2026-05-19 LongMemEval-S K=5 sweet-spot — refute wider-pool lore]] — sister negative-result on `fetch_k` lore
