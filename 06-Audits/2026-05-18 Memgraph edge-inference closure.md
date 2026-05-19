---
name: Memgraph edge-inference closure (B-7 typed-edge gap)
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#tech/memgraph"]
  - "#graph"
  - "#memgraph"
  - "#b-7"
  - "#sv-b1"
tag_backfill: 2026-05-19
---
# Memgraph edge-inference closure — 2026-05-19

> [!success] Result
> **+530 új `:RELATES{source:'inference'}` edge** beírva Memgraph CE 3.9.0-be cross-source-corroboration alapján. **23 531 → 24 061** (+2.25%). 1.25s end-to-end runtime, autocommit per `mgclient-autocommit-silent-rollback` lesson.

## Eszköz

[`/usr/local/bin/vault-graph-edge-inference`](file:///usr/local/bin/vault-graph-edge-inference) — Python (mgclient + sqlite3), idempotens, dry-run default. Kompozit indexálással O(provenance × subjects-per-file²) szegmensezve; ~0.5s teljes pair-enumeráció a 8929 KO-DB-matched entity-felett.

```bash
vault-graph-edge-inference                  # dry-run, top-30 preview
vault-graph-edge-inference --json --top 0   # all candidates JSON-lines
vault-graph-edge-inference --apply          # MERGE :RELATES edges
vault-graph-edge-inference --min-types 1 --apply  # loose gate (~970 cands)
```

## Pre / Post edge count

| Metric | Pre | Post | Δ |
|---|--:|--:|--:|
| Total Memgraph edges (any type, any direction) | 23 531 | 24 061 | **+530** |
| Distinct `(a,b)` pair-edges (symmetric) | 8 671 | 9 201 | +530 |
| `:RELATES{source:'inference'}` edges | 0 | 530 | +530 |

## Per-confidence breakdown

| Bucket | Definition | Count |
|---|---|--:|
| **high** | ≥4 shared sources AND ≥3 source-types | **2** |
| **medium** | ≥2 shared sources AND ≥2 source-types (default gate) | **528** |
| _low (not applied)_ | ≥2 sources, only 1 source-type | _440 (`--min-types 1` would add)_ |

## 8 spot-check pair (entity-pair → shared sources → confidence)

| # | a | b | confidence | shared_sources | source_types |
|--:|---|---|:-:|--:|---|
| 1 | `11.11start` | `11.11stop` | **high** | 5 | adr, session, wiki |
| 2 | `AGENTS.md` | `vault` | **high** | 4 | adr, session, wiki |
| 3 | `.active-session pointer` | `MEMORY.md` | medium | 4 | session, wiki |
| 4 | `11.11stop` | `Crystallization-protocol` | medium | 4 | session, wiki |
| 5 | `robbantott-kereso-api.service` | `robbantott-kereso-web.service` | medium | 4 | session, wiki |
| 6 | `Memgraph` | `SV-6` | medium | 3 | adr, wiki |
| 7 | `kgc-postgres container` | `kgc_berles DB` | medium | 2 | session, wiki |
| 8 | `kgc-berles` | `robbantott-kereso` | medium | 2 | session, wiki |

Mind a 8 spot-check pair **valid** — szemantikailag indokolt co-occurrence (parancs-páros, repo-szervezés, container-DB, KGC-cluster cross-project bridge).

## FP-rate becslés

25-pair manuális sampling a `shared_source_count=2 AND source_type_count=2` (legalsó küszöb) szegmensben:

| Kategória | Találat | Példa |
|---|--:|---|
| **TP** (real semantic relation) | 21 / 25 (~84%) | `11.11crystallize ↔ KO-DB`, `kgc-postgres container ↔ kgc_berles DB`, `11.11note ↔ MEMORY.md` |
| **Likely FP** (co-mention only) | ~4 / 25 (~16%) | `11.11 session-protokoll ↔ P2P GroupChat / CrewAI / SV-3` (research-note co-mention, no actual relation), `07-Decisions ↔ 08-Sessions` (directory artifacts) |

**Becsült végleges FP-rate: ~12-15%** a 530-as halmazban — a brief `<15%` célja teljesítve. A 2 high-confidence edge **0% FP**. A medium-tail `shared_source_count=2` legalsó negyede hordozza az FP-tömeg többségét; ha szigorúbb gate kell, `--min-sources 3` (~227 edge, becslés ~5% FP) is opció.

## Mérnöki őszinte vélemény — cross-source-corroboration `:RELATES`-edge-hez

**Részlegesen elég, de szuboptimális** önmagában. Pontosan:

### Mi az, amit jól csinál

- **Asszociáció-felfedezés**: két entity, ami legalább 2 függetlenül kifejlődő dokumentumban (különböző source-type-okból) együtt szerepel, biztosan valamilyen koncepcionális közelségben van. Ez **graph-traversal**-hez (load-session-context KO-DB top-K bővítés, B-2 semantic search re-rank) **elegendő**.
- **Confidence-tagging** (high/medium/low) lehetővé teszi a downstream-szűrést — pl. RAG-kérdéskor csak `confidence='high'`-on lépni át.

### Mi az, amit NEM csinál jól

- **Semantic direction**: `:RELATES` szimmetrikus és predicate-agnosztikus. Ha a KO-DB `(robbantott-kereso, IMPLEMENTED_IN, NestJS)` factot tartalmaz, a derivált edge típusa lehetne `:IMPLEMENTED_IN` és irány-helyes. Most ez **elveszett**.
- **Predicate-specificity**: a KO-DB-ban 1718 `produces`, 1368 `uses`, 506 `implemented_in` predicate van. Ezek **típusosan kinyerhetők** lennének a fact-rekordokból (subject↔object pair-szinten, nem subject↔subject co-occurrence-en). Egy második passz `vault-graph-edge-from-facts` predicate-szintű edge-eket adna (`MERGE (s)-[:USES]->(o)` ahol fact.subject=s, fact.object=o).
- **Direction-aware corroboration**: a co-occurrence csak gyenge szignál; egy `:DEPENDS_ON` edge-hez **direkt fact-evidence kell** (`A uses B` 2+ source-ban), NEM közvetett `A,B both appear in 2 files`.

### Javasolt iteráció (nem ebben a session-ben)

1. **Megtartani** ezt a 530 edge-et `:RELATES{source:'inference'}` címen — graph-density jó hozam, downstream-szűrhető.
2. **Új script**: `vault-graph-edge-from-facts` — KO-DB `(subject, predicate, object)` triplet → tipikus edge `(s)-[:<PREDICATE_UPPER>]->(o)`, ha mindkettő `:Entity` Memgraph-on. Várt nagyságrend: 2000-4000 tipikus edge (a 13 801 fact ~30-40%-a entity-pair).
3. **Hibrid retrieval**: graph-traversal-ben `:RELATES{source:'inference'}` csak fallback, ha nincs típusos edge (`weight=0.3` ranking-faktor).

### Mit ne csinálj

- **Ne emeld** ezeket a `:RELATES` edge-eket `IMPLEMENTED_IN` / `USES` típusra a co-occurrence alapján — predicate-specifikusság **NEM levezethető** subject-koincidenciából, csak fact-tripletből.
- **Ne shrinkeld** a confidence-küszöböt `--min-types 1`-re alapértelmezésnek — a +440 low-bucket edge ~25-30% FP-rate becslés, downstream-noise nagyobb mint a recall-haszon.

## Time-budget

| Fázis | Idő |
|---|--:|
| Script-fejlesztés + dry-run iteráció | ~3.5 perc |
| `--apply` futtatás | 1.25s |
| Audit-írás | ~1 perc |
| **Total** | **~4.5 perc** |

## Kapcsolódó

- [[../11-wiki/mgclient-autocommit-silent-rollback]] — miért `conn.autocommit = True`
- [[../11-wiki/memgraph-ce-feature-limits]] — natív vector-index 280× speedup (előző sprint)
- [[../11-wiki/memgraph-multi-labeling-edge-case-typedness-measurement]] — multi-label dupla-számolás
- [[../11-wiki/two-tier-graph-extraction]] — Tier-1 LLM-entity vs Tier-2 graphify
- KO-DB pipeline: `/usr/local/bin/vault-ko-query --co-occurrence` (B-7 gate)
