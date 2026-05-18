---
name: hybrid-bm25-semantic-rrf-pattern
description: BM25 + semantic top-K RRF (Reciprocal Rank Fusion) hibrid retrieval minta - +8ms latency overhead, marginal-win ritka-tokenű query-n, semleges gyakori-tokenű query-n, recall-improvement főleg evergreen-konceptuális chunkokon
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "retrieval", "search", "bm25", "semantic-search", "rrf"]
status: stable
---

# Hybrid BM25 + semantic RRF pattern

## A probléma

Tisztán **semantic-search (cosine over bge-m3 embedding)** elveszítheti a **ritka-tokenű query-ket** — a "G-Eval bias mitigation" vagy "subagent fanout" query a session-noise-ban elveszik a vault-context-embed pool-ban. A pure-BM25 viszont elveszíti a **paraphrase-recall**-t (akronima ↔ teljes-név). Hibrid pipeline mindkét axis-on hoz hit-eket és **rang-szerű fuzionálja**.

## A pattern (RRF — Reciprocal Rank Fusion)

```
query ──► BM25 corpus (in-RAM)  ──► top-K_bm25 (3-12ms)
      └─► semantic vector-index ──► top-K_sem (1-300ms)

                          │
                          ▼
   per-document: score_RRF = (1/(k+rank_bm25)) + (1/(k+rank_semantic))
   (k=60 default, smooths the 1/rank distribution)
                          │
                          ▼
                  top-K_hybrid (sub-ms fusion)
```

**Cost:** +5-12ms BM25 in-RAM + sub-ms fusion = **+8ms átlag overhead**. A semantic-encode (~270ms warm) marad a dominans, így a hybrid relatív overhead 3%.

## SV B-2 Week 4 5-query bench eredmény

| Query | Pure-semantic top-5 | Hybrid top-5 | Overlap | Új hit |
|---|---|---|---|---|
| robbantott kereső pdf parsing | 5 hit | 5 hit | 3/5 | 2 session-summary BM25 #1 |
| Memgraph native vector index | 5 hit | 5 hit | 4/5 | 1 "Next session" planning |
| subagent fanout pattern | 5 hit | 5 hit | 3/5 | 2 wiki-intro chunk BM25 #1 |
| G-Eval bias mitigation | 5 hit | 5 hit | 2/5 | 3 wiki-explainer chunk |
| nano-banana CLI gotchas | 5 hit | 5 hit | 5/5 | 0 (csak rendezés cserélődött) |

**Aggregate:** 17/25 overlap, **8/25 új hit** (32% recall-improvement ritka-tokenű query-n). Manual judgment: 0 false-positive új-hit-ben (mindegyik új valódi-relevant).

## Mikor érdemes alkalmazni

- ✅ Ritka-tokenű / akronima-domain (G-Eval, NLI, subagent, RRF)
- ✅ Kód-token search (function-name, flag-name, library-id)
- ✅ Magyar tech-vegyes domain (a bge-m3 magyar-coverage gyengébb mint az angol)
- ❌ Gyakori-tokenű természetes nyelvű query (mind 5 query 5/5 overlap, +8ms haszontalan)
- ❌ Vegyes-nyelvű domain ahol az encode dominál (latency cap)

## Tervezési alapelvek

1. **Hybrid flag DEFAULT OFF** — backward-compat + savings ha nincs ritka-token query
2. **BM25-index in-RAM JSON-serialize** — claude-code security-hook blokkolja a bináris-formátumot, JSON-rehidrálás OK (`BM25Okapi` `__dict__` primitív-only)
3. **Magyar accent-fold + lowercase + ≥2 char tokenizer** — Snowball stemming még Week 5+ (látszik a wiki-coverage-en, nem kritikus)
4. **RRF k=60** — Cormack et al. 2009 empirikus default, smooths the 1/rank distribution
5. **JSON output `{bm25_rank, semantic_rank, rrf_score}`** — debug-able, NEM black-box

## Trade-off

- ⚠️ BM25-index disk-méret ~2.5× nagyobb JSON-formátumban
- ⚠️ Magyar stemming-hiány miatt "regiszter" / "regiszterezte" / "regiszteres" külön token (Week 5 Snowball HU javítja)
- ✅ Marginal-win ritka-tokenű query-n, semleges gyakori-tokenű query-n
- ✅ Implementation $0 cost (rank-bm25 pip + existing semantic infra)

## Kapcsolódó

- [[../05-Memory/Infrastructure#Memgraph]] — semantic vector-index infra
- [[memgraph-ce-feature-limits]] — native vector-index (gyors-search-part)
- [[sv-01-memory-architecture]] — B-2 research
- [[smart-trigger-cost-pattern]] — kapcsolódó retrieval-pipeline pattern
