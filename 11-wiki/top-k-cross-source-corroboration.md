---
name: top-k-cross-source-corroboration
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/retrieval", "#topic/eval", "#pattern/ranking"]
---

# Top-K cross-source corroboration ranking

## TL;DR

A KO-DB Top-K ranking NEM csak frekvencia — **több source-on át (session/wiki/adr) több source_file-ban szerepelő** subject pontosabb jel a tényre, mint egyetlen high-confidence állítás. Ez a `vault-ko-query --top-k N` mögötti mechanizmus, és a [[layered-eval-cascading-pattern]] cross-source-corroboration layer-jének alapja. Cross-source: 20+ fact, 3 source-type.

## Háttér (3+ source-evidence)

- **vault-ko-query --top-k implementation:** Top-K subject ranking `source_count` + `max_confidence` + `fact_count` kombináción, NEM csak hits ([vault-ko-query --help output](/usr/local/bin/vault-ko-query))
- **B-1 Week 3-4 KO-DB Top-K structured facts:** 13K+ fact, cross-source-corroboration ranking, instant SQLite — a load-session-context skill alapja ([CLAUDE.md, SV B-1 pipeline](/root/.claude/CLAUDE.md))
- **bge-m3 Top-K=3 retriever:** SV-1 memory architecture-ben Top-K=3 az episodic memory default ([sv-1 memory architecture ADR](../07-Decisions/2026-05-12%20sv-1%20memory%20architecture%20arch.md))
- **Tool Search Index Top-K=3:** SV-4 tool composition-ben tool-routing-ra Top-K=3 ([sv-4 tool composition ADR](../07-Decisions/2026-05-12%20sv-4%20tool%20composition%20arch.md))
- **Karpathy LLM-wiki minta:** Classical RAG = query embed → search top-k chunks → answer ([Karpathy-LLM-Wiki-pattern](Karpathy-LLM-Wiki-pattern.md))
- **Semantic bridge:** `vault-ko-query --top-k N --semantic` → Memgraph bge-m3 → KO-DB LIKE bridge ([SV B-2 pipeline CLAUDE.md](/root/.claude/CLAUDE.md))

## Mintázat

```
query ─┬─> KO-DB LIKE pre-filter (substring on subject)
       ├─> group by subject
       ├─> compute score = source_count*10 + min(per_type_count)*5 + total_facts
       ├─> sort desc by score
       └─> return top-K subjects with N representative facts
```

**Architektúrális szabályok:**

1. **Cross-source first** — 1 fact 3 source-on > 5 fact 1 source-on (kevésbé bias-elt)
2. **Per-source-type bucket-count** — `(s=3, w=3, a=3)` > `(s=9, w=0, a=0)` (típus-diverzitás)
3. **`max_confidence` mint tie-breaker** — egyenlő source-count esetén
4. **Facts-per-subject default 3** — túl sok fact ugyanarra a subject-re zaj-növelő, top-K-t felzabálja

## Anti-pattern: "session-noise"

Ha csak `session/` source-okból jön egy pattern, az **NEM crystal**-ready — lehet egy-két session-specifikus megfigyelés. Auto-prop küszöb: legalább 2 source_type (wiki+session vagy adr+session) — különben még kandidát, nem evergreen.

```python
# decision rule example
def is_crystal_ready(subj):
    return (subj['types'] >= 2  # 2+ source_type
            and subj['source_count'] >= 3  # 3+ source_file
            and subj['max_confidence'] >= 0.85)
```

## Buktatók

- ⚠️ **Predicate-dump (19.8%)** — generikus `has_value` predicate dominálja a fact-okat, top-K elferdül; fix [[../06-Audits/2026-05-17 B-2 Week 3 acceptance gate readout]] szerint per-predicate bontás
- ⚠️ **Substring-match false-positive** — `"warm"` matchel `warmstart`-ra is; fix word-boundary regex vagy entity-id match
- ⚠️ **Chunk-count metric pitfall** — chunk-szám ≠ vault-coverage; per-source-type bontás kötelező ([MEMORY chunk-count metric pitfall](/root/.claude/projects/-root/memory/MEMORY.md))
- ⚠️ **Semantic bridge fallback** — Memgraph down → LIKE-fallback automatikus, de a recall csökken; monitor `vault-embed-freshness`-szel

## Mikor használd

| Use case | Top-K strategy |
|----------|----------------|
| load-session-context | Top-K=20 subject + 3 fact/subject |
| Wiki-gap analysis (jelen feladat) | Top-K=30 per-token, group by entity |
| Crystallization decision | Top-K=5 subject + cross-source-count gate |
| Tool-routing | Top-K=3 (bge-m3 cosine) |
| Episodic memory recall | Top-K=3 (working+top-K) |

## Kapcsolódó

- [[Karpathy-LLM-Wiki-pattern]] — Classical RAG = Top-K retrieval
- [[layered-eval-cascading-pattern]] — Layer 2.6 coherence = cross-source-check
- [[memgraph-ce-feature-limits]] — native vector-index Top-K backbone (1ms p95)
- [[hybrid-bm25-semantic-rrf-pattern]] — BM25+semantic fúzió Top-K-ra
- [[sv-01-memory-architecture]] — Top-K=3 episodic memory
- [[Auto-context-loading]] — Top-K aggressive pre-load
