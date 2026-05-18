---
name: top-k-cross-source-corroboration
type: wiki
lang: en
translated_from: top-k-cross-source-corroboration
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/retrieval", "#topic/eval", "#pattern/ranking"]
---

# Top-K cross-source corroboration ranking

## TL;DR

Top-K ranking in a knowledge-fact store is NOT just frequency — **a subject appearing in many source files across multiple source-types (session/wiki/adr)** is a stronger signal of fact than a single high-confidence statement. This is the mechanism behind `ko-query --top-k N` style commands, and the basis of the cross-source-corroboration layer in [[layered-eval-cascading-pattern]].

## Background

- **Top-K subject ranking** uses a combination of `source_count` + `max_confidence` + `fact_count`, NOT just hits
- **KO-DB Top-K structured facts:** 13K+ facts, cross-source-corroboration ranking, instant SQLite — basis of a load-session-context skill
- **bge-m3 Top-K=3 retriever:** Top-K=3 is a common default for episodic memory
- **Tool Search Index Top-K=3:** in tool-routing
- **Karpathy LLM-wiki pattern:** Classical RAG = query embed → search top-k chunks → answer
- **Semantic bridge:** `ko-query --top-k N --semantic` → Memgraph bge-m3 → KO-DB LIKE bridge

## The pattern

```
query ─┬─> KO-DB LIKE pre-filter (substring on subject)
       ├─> group by subject
       ├─> compute score = source_count*10 + min(per_type_count)*5 + total_facts
       ├─> sort desc by score
       └─> return top-K subjects with N representative facts
```

**Architectural rules:**

1. **Cross-source first** — 1 fact in 3 sources > 5 facts in 1 source (less biased)
2. **Per-source-type bucket count** — `(s=3, w=3, a=3)` > `(s=9, w=0, a=0)` (type diversity)
3. **`max_confidence` as tie-breaker** — when source-count is equal
4. **Facts-per-subject default 3** — too many facts on the same subject is noise that eats into the top-K

## Anti-pattern: "session noise"

If a pattern only comes from `session/` sources, it is **NOT crystal-ready** — it may be a one-off observation. Auto-prop gate: at least 2 source_types (wiki+session or adr+session) — otherwise still a candidate, not evergreen.

```python
# decision rule example
def is_crystal_ready(subj):
    return (subj['types'] >= 2  # 2+ source_types
            and subj['source_count'] >= 3  # 3+ source files
            and subj['max_confidence'] >= 0.85)
```

## Pitfalls

- ⚠️ **Predicate dump** — a generic `has_value` predicate dominates the facts, top-K skews; fix per-predicate breakdown in audits
- ⚠️ **Substring-match false positives** — `"warm"` matches `warmstart`; fix with word-boundary regex or entity-id match
- ⚠️ **Chunk-count metric pitfall** — chunk-count ≠ vault-coverage; per-source-type breakdown is mandatory
- ⚠️ **Semantic-bridge fallback** — Memgraph down → automatic LIKE fallback, but recall decreases; monitor with embed-freshness tooling

## When to use

| Use case | Top-K strategy |
|----------|----------------|
| load-session-context | Top-K=20 subject + 3 facts/subject |
| Wiki-gap analysis | Top-K=30 per token, group by entity |
| Crystallization decision | Top-K=5 subject + cross-source-count gate |
| Tool routing | Top-K=3 (bge-m3 cosine) |
| Episodic memory recall | Top-K=3 (working + top-K) |

## Related

- [[Karpathy-LLM-Wiki-pattern]] — Classical RAG = Top-K retrieval
- [[layered-eval-cascading-pattern]] — Layer 2.6 coherence = cross-source check
- [[memgraph-ce-feature-limits]] — native vector-index Top-K backbone (1ms p95)
- [[hybrid-bm25-semantic-rrf-pattern]] — BM25+semantic fusion on Top-K
- [[sv-01-memory-architecture]] — Top-K=3 episodic memory
- [[Auto-context-loading]] — Top-K aggressive pre-load
