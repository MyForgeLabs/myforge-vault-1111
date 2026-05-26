---
name: vault-explain pattern
type: wiki
tags: ["#type/pattern", "rag", "retrieval", "introspection", "graphrag", "vault-design"]
created: 2026-05-19
updated: 2026-05-19
source:
  - "[[../06-Audits/2026-05-19 SV new development ideas brainstorm#Idea 2 vault-explain]]"
  - "[[../.vault-memory/scripts/vault-explain.py]]"
---

# vault-explain pattern

`vault-explain` is a retrieval-introspection CLI for the Superintelligent Vault stack. Where `vault-search` answers _"what are the top-K matches?"_, `vault-explain` answers _"**why** are these the top-K, and how confident should I be?"_ — a runtime trace of every signal that contributed to a ranking decision.

## Why retrieval introspection matters

The 2026 GraphRAG consensus is that retrieval *traceability* — being able to point at the chunks, edges, and facts that drove a ranking — is no longer optional for production RAG. Two reasons:

1. **Debuggability.** When a RAG answer is wrong, "the retrieval returned bad chunks" is not actionable. You need to know whether the failure was cosine drift, missing wiki-edges, off-topic KO-DB corroboration, or simply a query that's off-vocabulary.
2. **Trust calibration.** A top-K with `cosine=0.48` and zero corroboration should not feel the same as one with `cosine=0.85 + 5 distinct KO-DB sources + 3 entity-graph hops`. Without per-result trace data, downstream agents can't distinguish high-confidence retrievals from coincidental matches.

The frontier framing here borrows from interpretability research: an LLM's retrieval step is itself a "model" with internal state, and we want a probe that exposes it.

## The four trace dimensions

`vault-explain` reports four orthogonal signals per top-K result:

| Dimension | What it tells you | Source |
|---|---|---|
| **Cosine similarity** | Semantic match strength — does the bge-m3 embedding agree the chunk is on-topic? | vault-search daemon (native vector_search or numpy fallback) |
| **Token overlap** | Lexical match — does the chunk share surface tokens with the query? Catches "semantic-only" misses (synonym storms) | In-process tokenizer matching `vault-bm25-backfill` |
| **KO-DB cross-source corroboration** | How many distinct sources independently mention this chunk's subject? A 1-source hit is weaker than a 5-source consensus, even at identical cosine | SQLite read-only against `.vault-ko/facts.db` |
| **Entity-graph neighbourhood** | Does the chunk's WikiFile node link out to entities detected in the query? Promotes results that sit in the right semantic neighbourhood, not just the right vector cluster | Memgraph read-only (`:WikiFile`-[:LINKS_TO]→, `:Entity` lookup) |

A high-confidence verdict requires ≥3 of these signals to align. The verdict heuristic also considers the cosine score gap between top-1 and top-2 (a small gap means multiple plausible interpretations).

## When to use `vault-explain` vs `vault-search --json`

- **`vault-search --json`** — production read path. You want results fast; you don't care _why_.
- **`vault-explain`** — debugging, prompt-engineering, and trust calibration. You want a self-explaining retrieval report. Run it when:
  - A downstream agent is producing surprising answers and you suspect retrieval is upstream.
  - You're tuning the smart-rerank trigger threshold and want to see when it fires.
  - You're authoring evals and want a ground-truth trace per query.
  - You're explaining the SV stack to a new collaborator.

`vault-explain` adds ~100ms of overhead on top of search (one KO-DB query per result + a few Memgraph reads), so it is not the right tool for hot-path production retrieval.

## The Mermaid diagram convention

`vault-explain` emits a `flowchart LR` that visualizes the trace:

- **Solid arrows** are the retrieval pipeline (Q → bge-m3 → top-K chunks). Edge labels carry the cosine score.
- **Dotted arrows with `src` count** are KO-DB corroboration links (chunk subject ↔ KO-DB facts).
- **Dotted `detect` arrows** from Q are detected entities (Memgraph Entity-node lookups).
- **Solid `:LINKS_TO` arrows** between chunks and neighbour-wiki-files surface relevant graph-locality.

The diagram is intentionally information-dense over pretty — its job is to make 4-dimensional rank reasoning visually scannable.

## Graceful fallback (skeleton-first)

All three external dependencies — vault-search daemon, KO-DB, Memgraph — fail open. If the daemon is down, the trace returns an empty result list with a clear error note. If KO-DB is missing, the corroboration column is just zeroed. If Memgraph is unreachable, the entity-graph section is replaced by a one-line warning. The CLI never crashes; downstream agents can rely on the JSON schema being stable.

## Comparison with mem0 / Letta

Most agent-memory frameworks expose retrieval as a black box: you call `memory.search(query)` and get a result list with no traceability. mem0 and Letta both fall into this category — their public APIs return chunks and scores, but no structured "why this ranked here" data.

`vault-explain` is the structured-output version of what an agent's introspection prompt would otherwise have to do at runtime (and pay for in tokens). By computing the trace dimensions deterministically against the same indices the retrieval used, we get free, reproducible, and cheap retrieval introspection — and it composes with the rest of the SV stack (Memgraph, KO-DB, daemon) without any extra infrastructure.

## Related

- [[Karpathy-LLM-Wiki-pattern]] — the compounding-knowledge philosophy this retrieval stack serves
- [[memgraph-ce-feature-limits]] — native vector_search backing the cosine layer
- [[../06-Audits/2026-05-19 SV new development ideas brainstorm]] — brainstorm origin (idea #2)
- `/usr/local/bin/vault-search` — the retrieval CLI this introspects
- `/root/obsidian-vault/.vault-memory/scripts/vault-explain.py` — implementation
