---
name: Memgraph MAGE vector-search scale trade-off
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/knowledge-graph", "#topic/scale", "sv-2", "memgraph", "vector-search", "lang/en"]
source: vault-meta NotebookLM Q4#4 / Q5#4 (2026-05-18, 63-source synthesis)
status: evergreen
lang: en
translated_from: memgraph-mage-vector-scale-tradeoff.md
project: [[../02-Projects/superintelligent-vault]]
related: [[memgraph-ce-feature-limits]], [[vendor-feature-verify-before-workaround]], [[sv-02-recursive-self-improvement]]
---

# Memgraph MAGE vector-search scale trade-off

> **TL;DR:** Memgraph CE 3.9.0's native `vector_search.search` (vector index) gives a **280× speedup** over numpy-cosine ([[memgraph-ce-feature-limits]]), **BUT this is optimal up to 1000-5000 chunks**. Above 5000 chunks, industrial GraphRAG / HippoRAG workloads need **MAGE (`vector_search` C++ module) or Memgraph Enterprise**. This wiki encodes the **when-which** decision matrix.

## Problem context

The vault-meta NotebookLM cross-project synthesis (63 sessions) — **Q4-#4 and Q5-#4** both pointed at the same wall: SV B-2 Knowledge-Graph axis runs on Memgraph CE, and **chunk-count is approaching the 5000 hard limit** where the native vector index degrades.

State on 2026-05-18 (B-2 Week 3):
- **Chunk store (`:Chunk` namespace):** 2829 vault-file chunks
- **SkillChunk store (`:SkillChunk` namespace):** 462 skill-doc chunks
- **Entity store (`:Entity` namespace):** 8997 LLM-extracted entities
- **Total in Memgraph:** ~12288 vector-indexed nodes

The entity store (8997) is still served well by the native vector index per B-7 Week 4 (mean 1ms / p95 2.6ms — [[memgraph-ce-feature-limits]]). **BUT:** the chunk store is at 2829 and growing at ~50-100 chunks/week, SkillChunk at 462 (slow growth). **In aggregate, 12K is fine now; 20-30K won't be.**

## The three scale tiers

### Tier 1 — Memgraph CE Native (current, "Tier-$50")

- **`CREATE VECTOR INDEX ON :NodeLabel(property)` + `vector_search.search()`** — out of the box
- **Range:** 1000-5000 chunks per namespace
- **Performance:** 1-3ms mean, 5-10ms p95
- **Cost:** $0 (open-source CE)
- **Limit:** above ~5000 chunks the HNSW-index memory footprint + cold-cache rebuild slows it down

### Tier 2 — Memgraph MAGE `vector_search` C++

- **MAGE plugin install:** `docker exec memgraph apt install memgraph-mage`
- **C++-implemented vector index** — native HNSW + IVF-PQ compression + parallel query
- **Range:** 5000-100000 chunks per namespace
- **Performance:** 2-5ms mean, 10-20ms p95 (up to 50K chunks)
- **Cost:** $0 (MAGE is OSS, Apache 2.0)
- **Limit:** memory footprint ~2× Tier-1; no full-text query

### Tier 3 — Memgraph Enterprise

- **`CREATE VECTOR INDEX … WITH (algorithm='hnsw', m=16, ef_construction=200)`** — fine-tunable
- **Multi-tenancy, audit log, RBAC, hot backup**
- **Range:** 100K+ chunks, multi-tenant production
- **Performance:** 1-3ms mean p99 guaranteed
- **Cost:** Enterprise license (no public pricing)
- **Limit:** real enterprise commitment required

## Reference implementations (NotebookLM cited)

- **`Memgraph MAGE`** repo — `vector_search` module, official Memgraph addon
- **`HippoRAG`** (paper, 2024) — hippocampal-inspired RAG, MAGE-like vector-graph hybrid
- **`Microsoft GraphRAG`** — entity-graph + community summarization, Neo4j-based but architecturally analogous

## Decision matrix — when which tier

| Condition | Tier 1 (CE Native) | Tier 2 (MAGE) | Tier 3 (Enterprise) |
|----------|--------|--------|--------|
| Chunks < 5K | ✅ Optimal | Overkill | Overkill |
| Chunks 5-50K | ⚠️ Degrades | ✅ Optimal | Overkill |
| Chunks 50K+ | ❌ Doesn't work | ✅ OK | ✅ Optimal |
| Multi-tenant prod | ❌ Single-tenant | ⚠️ Limited | ✅ Built-in |
| Cost | $0 | $0 | $$$ |
| HippoRAG/GraphRAG-style | ⚠️ Workaround | ✅ Native | ✅ Native |

## Trigger thresholds (proactive scaling)

The vault-meta NB Q5-#4 explicit recommendation: **do NOT wait for the wall**, monitor proactively:

- **🟡 4000 chunks per namespace:** start MAGE PoC, tune vector-index params
- **🔴 4500 chunks per namespace:** MAGE production-deploy decision
- **🚨 5000 chunks per namespace:** urgent migration, latency degradation expected

The B-2 Week 3 telemetry monitor (`vault-embed-freshness`) is currently **chunk-count-only**, NOT measuring latency degradation. **TODO:** `vault-vector-perf-monitor` script for percentile tracking.

## Cross-project evidence

- **B-7 entity-graph (8997 nodes)** already at "near Tier-1 hard limit" — the 1ms p95 only on freshly-rebuilt index; cold-start 5-8ms (2026-05-17-3 super-session)
- **B-2 chunk store (2829)** — currently stable, but `vault-embed --backfill` may add 200-300 chunks/week → ~10-15 weeks until MAGE trigger
- **B-4 SkillChunk (462)** — slow growth, no near-term risk

## Anti-patterns (what NOT to do)

1. **In-Python cosine fallback (legacy)** — already proven 280× slower than native; don't go back
2. **Application-level sharding** — Memgraph native multi-namespace ([[memgraph-ce-feature-limits]] 2026-05-17-3 confirmed) is enough
3. **External vector DB (Qdrant, Weaviate, Milvus)** — graph context lost; only if chunk-count growth bursts Memgraph graph coherence
4. **Wait until the wall** — proactive migration is ~1 week work, reactive migration with prod degradation is ~3-4 weeks

## When this pattern applies

- ✅ Vector-search-based knowledge-graph system
- ✅ Memgraph as backend (Neo4j-analog patterns also apply, but product-specific)
- ✅ Chunk count is actively growing
- ❌ Static ~1000-chunk knowledge base NOT affected

## Implementation checklist (Tier-1 → Tier-2 migration)

- [ ] `vault-vector-perf-monitor` script (percentile tracking)
- [ ] MAGE plugin install (`docker exec` + `LOAD MODULE`)
- [ ] Vector index recreate with MAGE syntax
- [ ] Backward-compat: app-side dual-read (native + MAGE) for 2 weeks
- [ ] Cutover: app-config switch
- [ ] Audit log: post-cutover 2-week latency summary

## Related

- [[memgraph-ce-feature-limits]] — Tier-1 baseline (280× speedup verification)
- [[vendor-feature-verify-before-workaround]] — Tier-1 lesson; don't work around a vendor feature
- [[sv-02-recursive-self-improvement]] — B-2 sprint host
- [[two-tier-graph-extraction]] — graphify vs Memgraph LLM complementary
- [[../06-Audits/2026-05-18 vault-meta NB cross-projekt Q4-Q5]] — source audit

## Hungarian original

[[memgraph-mage-vector-scale-tradeoff]]
