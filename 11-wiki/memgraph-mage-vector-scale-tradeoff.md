---
name: Memgraph MAGE vector-search scale trade-off
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/knowledge-graph", "#topic/scale", "sv-2", "memgraph", "vector-search"]
source: vault-meta NotebookLM Q4#4 / Q5#4 (2026-05-18, 63-source synthesis)
status: evergreen
project: [[../02-Projects/superintelligent-vault]]
related:
  - "[[memgraph-ce-feature-limits]]"
  - "[[vendor-feature-verify-before-workaround]]"
  - "[[sv-02-recursive-self-improvement]]"
---

# Memgraph MAGE vector-search scale trade-off

> **Tl;dr:** A Memgraph CE 3.9.0 natív `vector_search.search` (vector-index) **280× speedup-ot** ad numpy-cosine fölött ([[memgraph-ce-feature-limits]]), **DE ez 1000-5000 chunk-ig optimális**. 5000+ chunk fölött ipari GraphRAG / HippoRAG terheléshez **MAGE (`vector_search` C++ modul) vagy Memgraph Enterprise** szükséges. Ez a wiki rögzíti a **mikor-melyik** döntési mátrixot.

## A probléma kontextusa

A vault-meta NotebookLM cross-projekt synthesis (63 session) **Q4-#4 és Q5-#4** mind a kettő ugyanarra a falra mutatott: a SV B-2 Knowledge-Graph axis Memgraph CE-vel él, és **a chunk-szám közelít az 5000-es hard-limithez**, ahol a natív vector-index degradálódik.

2026-05-18-i state (B-2 Week 3):
- **Chunk-tár (`:Chunk` namespace):** 2829 vault-fájl-chunk
- **SkillChunk-tár (`:SkillChunk` namespace):** 462 skill-doc-chunk
- **Entity-tár (`:Entity` namespace):** 8997 LLM-extracted entity
- **Összesen Memgraph-ban:** ~12288 vector-indexed node

Az entity-tárat (8997) a B-7 Week 4 még native vector-indexszel jól szolgálja ki (mean 1ms / p95 2.6ms — [[memgraph-ce-feature-limits]]). **DE:** a chunk-tár 2829-ben van és nő ~50-100 chunk/hét tempóban, az SkillChunk-tár 462-ben (lassú növekedés). **Az aggregált összesített index szempontjából a 12K most jó, a 20-30K nem lesz.**

## A három skálázási tier

### Tier 1 — Memgraph CE Native (jelenlegi, "Tier-$50")

- **`CREATE VECTOR INDEX ON :NodeLabel(property)` + `vector_search.search()`** — out-of-the-box
- **Range:** 1000-5000 chunk per namespace
- **Performance:** 1-3ms mean, 5-10ms p95
- **Cost:** $0 (open-source CE)
- **Limit:** ~5000 chunk fölött a HNSW-index memóriaszükséglete + cold-cache rebuild lassúvá teszi

### Tier 2 — Memgraph MAGE `vector_search` C++

- **MAGE plugin install:** `docker exec memgraph apt install memgraph-mage`
- **C++-implementált vector-index** — natív HNSW + IVF-PQ kompresszió + parallel-query
- **Range:** 5000-100000 chunk per namespace
- **Performance:** 2-5ms mean, 10-20ms p95 (még 50K chunk-ig)
- **Cost:** $0 (MAGE is OSS, Apache 2.0)
- **Limit:** memóriaigény ~2× a Tier-1-éhez képest; full-text query nincs

### Tier 3 — Memgraph Enterprise

- **`CREATE VECTOR INDEX … WITH (algorithm='hnsw', m=16, ef_construction=200)`** — fine-tunable
- **Multi-tenancy, audit-log, RBAC, hot-backup**
- **Range:** 100K+ chunk, multi-tenant production
- **Performance:** 1-3ms mean p99 garantálva
- **Cost:** Enterprise license (NEM publikus pricing)
- **Limit:** valódi enterprise commitment szükséges

## Reference implementations (NotebookLM cited)

- **`Memgraph MAGE`** repo — `vector_search` modul, official Memgraph addon
- **`HippoRAG`** (paper, 2024) — hippocampal-inspired RAG, Memgraph MAGE-szerű vector-graph hybrid
- **`Microsoft GraphRAG`** — entity-graph + community-summarization, Neo4j alapú, de architecturally analóg

## Döntési mátrix — mikor melyik tier

| Feltétel | Tier 1 (CE Native) | Tier 2 (MAGE) | Tier 3 (Enterprise) |
|----------|--------|--------|--------|
| Chunk-szám < 5K | ✅ Optimal | Overkill | Overkill |
| Chunk-szám 5-50K | ⚠️ Degradál | ✅ Optimal | Overkill |
| Chunk-szám 50K+ | ❌ NEM működik | ✅ OK | ✅ Optimal |
| Multi-tenant prod | ❌ Single-tenant | ⚠️ Limited | ✅ Built-in |
| Cost | $0 | $0 | $$$ |
| HippoRAG/GraphRAG-style | ⚠️ Workaround | ✅ Native | ✅ Native |

## Trigger-küszöbök (proaktív skálázás)

A vault-meta NB Q5-#4 explicit ajánlás: **NE várd meg a falat**, monitorozz proaktívan:

- **🟡 4000 chunk per namespace:** MAGE PoC indítása, vector-index params tuning
- **🔴 4500 chunk per namespace:** MAGE production-deploy döntés
- **🚨 5000 chunk per namespace:** sürgős migráció, latency-degradáció várható

A B-2 Week 3 telemetria-monitorozó (`vault-embed-freshness`) jelenleg **chunk-count-only**, NEM mér latency-degradációt. **TODO:** `vault-vector-perf-monitor` skript a percentile-tracking-ra.

## Cross-projekt evidence

- **B-7 entity-graph (8997 node)** már most "Tier-1 közeli hard-limit" — az 1ms p95 csak frissen-rebuilt-index-szel; cold-start után 5-8ms (mérés: 2026-05-17-3 super-session)
- **B-2 chunk-tár (2829)** — most stabil, de a `vault-embed --backfill` heti +200-300 chunk-ot toldhat hozzá → ~10-15 hét MAGE-trigger
- **B-4 SkillChunk (462)** — lassú növekedés, nem közeli kockázat

## Anti-patterns (mit NE csinálj)

1. **Workaround in-Python cosine fallback (legacy)** — már bizonyítottan 280× lassabb mint a natív; ne térj vissza
2. **Sharding az application-szinten** — Memgraph natív multi-namespace ([[memgraph-ce-feature-limits]] 2026-05-17-3 megerősítés) elég
3. **External vector-DB (Qdrant, Weaviate, Milvus)** — graph-context elveszne; csak ha chunk-szám-növekedés szétfeszíti a Memgraph-graph-koherenciát
4. **Várj amíg a fal eljön** — proaktív migráció ~1 hét munka, reaktív migráció prod-degradációval ~3-4 hét

## Mikor érvényes ez a pattern

- ✅ Vector-search alapú knowledge-graph rendszer
- ✅ Memgraph mint backend (Neo4j-analóg patternek érvényesek, de termék-specifikusak)
- ✅ Chunk-szám aktívan növekszik
- ❌ Static, ~1000-chunk kbase NEM-érintett

## Implementation checklist (Tier-1 → Tier-2 migráció)

- [ ] `vault-vector-perf-monitor` skript (percentile-tracking)
- [ ] MAGE plugin install (`docker exec` + `LOAD MODULE`)
- [ ] Vector-index recreate MAGE syntaxszal
- [ ] Backward-compat: app-side dual-read (native + MAGE) 2 hétig
- [ ] Cutover: app-config switch
- [ ] Audit-log: post-cutover 2-hét latency-summary

## Kapcsolódó

- [[memgraph-ce-feature-limits]] — Tier-1 alap (280× speedup verifikáció)
- [[vendor-feature-verify-before-workaround]] — Tier-1 lecke; ne workaround-old a vendor-feature-t
- [[sv-02-recursive-self-improvement]] — B-2 sprint host
- [[two-tier-graph-extraction]] — graphify vs Memgraph LLM komplementer
- [[../06-Audits/2026-05-18 vault-meta NB cross-projekt Q4-Q5]] — forrás-audit
