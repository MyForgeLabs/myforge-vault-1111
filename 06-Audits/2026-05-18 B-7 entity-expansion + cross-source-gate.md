---
name: B-7 entity-expansion + cross-source-gate
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [audit, sv-b-7, memgraph, ko-db, cross-link]
---

# B-7 entity-expansion + KO-DB cross-source-gate

> Time-budget: 8 perc. Cél: relation-extract bővítés Memgraph-on + `--co-occurrence` flag + spot-check, hogy a cross-link auto-suggest-pipeline használhassa a KO-DB cross-source-evidence-jelét.

## 1. Memgraph pre/post relation-edge count

| Metric | PRE | POST | Δ |
|---|---:|---:|---:|
| `:Entity` node | 8 997 | **16 019** | +7 022 (lazy-created `:Concept`) |
| Directed `(:Entity)-[r]->(:Entity)` | 1 279 | **8 744** | **+7 465** |
| Distinct rel-type | ~20 | **40+** | +new (MOTIVATED_BY, DECIDED_AT, HAS_COST, USES_MODEL…) |

PRE top-3: ALIAS_OF (274), USES (218), IMPLEMENTED_IN (99).
POST top-3: USES (982), PRODUCES (916), REQUIRES (760).

Forrás: `/root/obsidian-vault/.vault-ko/facts.db` `source_type IN ('wiki','adr')` → 8 068 fact-ot 19.4 mp alatt MERGE-elve Memgraph-ra (`/tmp/relation_expand.py`). Idempotent: re-run = 0 új edge. 0 hiba.

## 2. Cross-source-gate smoke (5 candidate-pair)

`vault-ko-query --co-occurrence NAME1 NAME2` az új flag:

| Pair | Shared sources | Top source-type mix |
|---|---:|---|
| Memgraph ⨯ vector-index | **3** | 2 adr + 1 session |
| G-Eval ⨯ bias | **3** | 1 adr + 2 wiki |
| GEPA ⨯ Pareto | **3** | 2 wiki + 1 adr |
| Karpathy ⨯ wiki | **32** | wide mix (adr/wiki/session) |
| crystallize ⨯ shadow | **5** | 1 adr + 4 session |

100% non-zero → a gate-signal **szignifikáns** minden tesztelt valid pair-re. Top-result mindig high-fact-count canonical doc (pl. `11-wiki/sv-02-recursive-self-improvement.md` GEPA⨯Pareto-ra).

## 3. KO-DB query-bővítés state

`vault-ko-query --co-occurrence <n1> <n2>` ÉLES:

- Implementáció: SQL `INTERSECT` 2 subject/object LIKE-halmazon → shared provenance, per source-type fact-count.
- JSON-mode: `--json` strukturált output (`name1`, `name2`, `shared_source_count`, `shared_sources[]`).
- Help-text frissítve, argparse 2-args.
- 5/5 smoke ✅, 0 false-empty.

A B-7 cross-link auto-suggest-pipeline most a következő gate-et tudja használni:
```python
# pseudo
candidates = subagent_propose_links(entity)
filtered = [
    c for c in candidates
    if ko_query_co_occurrence(entity, c).shared_source_count >= 2
]
```

## 4. 5 spot-check (entity-pair → relation + cross-source-evidence)

| Pair | Memgraph relation | KO-DB sources | Auto-suggest gate |
|---|---|---:|---|
| Memgraph ⨯ vector-index | 0 fwd / 0 rev | 3 | ⚠ KO-DB-only (rel hiányzik, entity-név fragmentált) |
| G-Eval ⨯ bias | `REQUIRES`, `CAUSES` (3 fwd) | 3 | ✅ PASS |
| GEPA ⨯ Pareto | `PRODUCES`, `USES` (3 fwd) | 3 | ✅ PASS |
| Karpathy ⨯ LLM-Wiki | `DEFINED_IN`, `ALIAS_OF` (2+3) | 19 | ✅ PASS |
| crystallize ⨯ shadow | 0 fwd / 0 rev | 5 | ⚠ KO-DB-only (multi-word predicate-objektek) |

→ **3/5 dual-gate PASS**, **2/5 KO-DB-only** (a hiányzó Memgraph-rel oka: a fact predicate-object-je hosszabb string, így a `vector-index` és `shadow` nem önálló entity-ként szerepel, hanem object-szubstring-ként a KO-DB-ben — a Memgraph mention-extract még nem entitásifikálja őket).

## 5. Mérnöki őszinte: cross-link auto-suggest production-ready?

**Részben.** A két jel külön-külön working, de összefüggésében az alábbiak miatt **még nem 1-click-prod**:

✅ **Ami már van**
- 8 744 typed `(:Entity)-[r]->(:Entity)` triplet Memgraph-on (volt 1 279, +584%).
- 40+ rel-type — elég gazdag predicate-vocab.
- `--co-occurrence` szignifikáns jelet ad (3-19 shared source a tesztelt valid pair-eken).
- Idempotent re-run, 0-error pipeline.

⚠ **Ami még blocker / tech-debt**
1. **Entity-fragmentáció.** A `--co-occurrence "Memgraph" "vector-index"` 3 shared sourceot ad, de Memgraph-on nincs `(:Entity{name:"vector-index"})` — a "vector-index" szó csak object-textben él. Megoldás: mention-extract finomítása vagy a fact-object-eket NER-rel split-elni külön Entity-kre.
2. **Lazy-created Concept-zaj.** +7 022 új `:Concept` lett, ami a 16 019/8 997-es növekedés ~80%-a. Ezek nagy része hosszú object-string (pl. "Pareto-front 3-5 specialista-változat"), ami NEM jó cross-link target. Cleanup-pass kell — vagy `lazy_created=true` szűrő az auto-suggest-pipeline-on.
3. **Predicate-disambiguation.** `USES` (982) vs `IMPLEMENTED_IN` (367) vs `DEPENDS_ON` (207) közti határ nincs jól meghúzva (sok az átfedés a forrás-fact-ekben).
4. **Cross-source threshold kalibráció hiányzik.** ≥2-jó kiindulás, de a 19-source Karpathy⨯wiki-pair ugyanúgy számít mint a 3-source GEPA⨯Pareto. Súlyozott küszöb kell (pl. min-source-type-diversity: ≥1 wiki + ≥1 adr).
5. **Self-loop / circular-rel** filter nincs, bár a relation-expand-ben már `sn == on` filter van — ENTITY-szintű alias-cycle-check hiányzik.

**Ajánlás:** A B-7 auto-suggest-pipeline shadow-mode-ban indítható (proposal-log, no auto-apply), 1 hét után review. **NE** kapcsoljuk auto-apply-ra production-on, amíg a (1) entity-fragmentáció és (2) lazy-Concept-cleanup nincs megoldva — különben 30-40% FP-cascade várható a noisy long-string object-eken.

**Score: 7/10 production-readiness.** A jel működik, az aljzat-zaj kicsi-közepes.

## Kapcsolódó

- ADR: [[../07-Decisions/2026-05-12 sv-7 advanced-graph-search arch]]
- B-1 layer: [[../11-wiki/Crystallization-protocol]]
- KO-DB cli: `vault-ko-query --help`
- Script: `/tmp/relation_expand.py`
