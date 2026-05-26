---
name: HyDE query-rewrite skeleton
description: Hypothetical Document Embedding (HyDE) query-rewrite pattern as implemented by vault-hyde-rewrite + wired into vault-ko-query --hyde. Why HyDE helps under-specified queries; the fast keyword-expand path vs the 2-phase subagent-fanout path; integration with the RRF default-route.
type: wiki
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/wiki", "retrieval", "hyde", "sv-1"]
---

# HyDE query-rewrite skeleton

## What HyDE is (and why it helps)

**HyDE = Hypothetical Document Embedding** (Gao et al., 2022). Instead of embedding the raw query, you ask an LLM to write a hypothetical answer-document, then embed THAT for retrieval. The expanded text has more semantic surface that overlaps with real documents — particularly useful for under-specified queries like "how does it scale?" where the raw query has too few concept-tokens to match anything good.

Concrete example from the vault stack:

| query | what raw embedding sees | what HyDE-expanded embedding sees |
|---|---|---|
| `"how does the typed graph work"` | 6 generic tokens | adds: typed-entity, Memgraph, Cypher, labels, B-7 — concrete vault terms |
| `"retrieval"` | 1 token | adds: bge-m3, RRF fusion, Memgraph vector-index, top-K, Recall@5 |

The expanded query then drives the same downstream pipeline (embed → cosine top-K → RRF fusion → KO-DB subject lookup).

## Implementation (vault v1.0.16)

Two paths, same I/O contract:

### Fast path — `vault-hyde-rewrite` keyword-expand

`~5ms`, no LLM call. Matches the query against a hand-curated 10-topic domain hint bank (`DOMAIN_HINTS` dict in `vault-hyde-rewrite.py`). Each matched topic contributes 3-5 concrete keywords. Caps at 8 expansion-keywords total.

Use case: production default. Cheap, deterministic, no API calls, predictable latency.

### Real path — 2-phase subagent-fanout

Same 2-phase pending-file pattern as `b7-ctx-pass` / `vault-ko-ingest`:

```
$ vault-hyde-rewrite "how does the typed graph work" --emit-pending /tmp/hyde/
{"batch_id": "hyde-20260525T191500", "pending_file": "/tmp/hyde/hyde-20260525T191500.json"}

# subagent reads pending file, writes hypothetical_documents to *.response.json

$ vault-hyde-rewrite "how does the typed graph work" --consume /tmp/hyde/
# reads newest response, merges hypothetical sentences into merged_for_embedding
```

Use case: research, A/B experiments, batch jobs where LLM cost is OK.

## How `vault-ko-query --hyde` wires it together

`vault-ko-query --top-k <N> --hyde "<query>"` does:

1. **Pre-pass**: call `vault-hyde-rewrite "<query>" --json`, take `merged_for_embedding`. ~5ms.
2. **Retrieval**: pass the EXPANDED query to `vault-search-fusion` (the production default route). Same RRF hybrid as without --hyde.
3. **KO-DB join**: extract titles+keywords from top chunks, top-K subjects by cross-source corroboration. Same as default route.

Graceful fallback: if `vault-hyde-rewrite` fails (missing on PATH, timeout, invalid JSON), uses the raw query unchanged. So `--hyde` is always safe to add.

## Observed effect

Side-by-side example (query: `"memgraph native vector"`):

- **Default route**: top-1 subject is `Heartbeat 90s threshold` (low-quality match, raw query too short)
- **`--hyde` route**: top-1 subject is `sv-06-world-model-knowledge-graph` (correct wiki for the topic)

`vault-bench` 5-query latency comparison (v1.0.16):

| route | mean (s) |
|---|---:|
| `--no-semantic` (KO-DB LIKE) | 0.07 |
| `vault-search-fusion (RRF, raw)` | 0.77 |
| `vault-ko-query --hyde (rrf+HyDE)` | **1.10** |
| `vault-ko-query default (=rrf)` | 1.33 |
| `vault-search (alone)` | 5.02 |
| `vault-ko-query --semantic (legacy)` | 5.38 |

Note: HyDE route is FASTER than the default RRF route in this snapshot. Likely because the expanded query matches cached embeddings better and the fusion has fewer ambiguous matches to merge. Could be noise — needs n>5 to confirm.

## Open follow-ups

- **Wire into `vault-search-fusion` directly** (not only KO-DB top-K) — would give plain `vault-search-fusion --hyde` users the same benefit.
- **Recall@5 measurement**: integrate `--hyde` into `vault-eval-regression --v03` for a hard number against LongMemEval-S 99-Q.
- **Expand DOMAIN_HINTS** as new vault subsystems appear (currently 10 topics; could grow to 20+ as the vault adds plugin / agent / hardware axes).
- **Real-LLM A/B**: 99-query subagent-fanout to compare keyword-expand vs LLM-rewritten HyDE, R@5 delta.

## Related

- [[vault-bench-harness]] — latency comparison framework (5 routes default)
- [[claude-code-subagent-fanout]] — the 2-phase pattern HyDE's real path uses
- [[memgraph-ce-feature-limits]] — the bge-m3 embed layer below HyDE
