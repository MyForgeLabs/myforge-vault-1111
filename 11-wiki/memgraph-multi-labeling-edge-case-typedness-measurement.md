---
name: Memgraph multi-labeling — tipizáltság-mérőszám edge-case
type: wiki
tags: ["#type/wiki", "memgraph", "graph-metrics", "labels", "measurement", "double-counting"]
created: 2026-05-18
updated: 2026-05-18
status: stable
---

# Memgraph multi-labeling tipizáltság-mérőszám

Memgraph (és Neo4j, és általában Cypher-graph-DB) entity-jei **több címkét** kaphatnak (`SET n:Concept; SET n:Pattern;`). Tipizáltság-mérőszámok (typed-rate, label-distribution, multi-label-overlap) **double-counting hibára** vezetnek, ha a script naivan `count(:Label1) + count(:Label2) + ...` SUM-ot csinál — az így kapott szám **NAGYOBB lehet az entity-count-nál**, ami félrevezető riport-output.

## TL;DR

- Memgraph entity: `MATCH (n:Entity) SET n:Concept` után `n` címkéi = `{Entity, Concept}`. `SET n:Pattern` után = `{Entity, Concept, Pattern}`.
- **Rossz:** `MATCH (n:Concept) RETURN count(n) AS c1` + `MATCH (n:Pattern) RETURN count(n) AS c2` → `c1+c2 > total_entities` (mert dupla-számolódik a `{Concept, Pattern}` overlap)
- **Jó:** `MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n) AS typed` (a `:Entity` az alap-label, plusz minden további típus-jelölő)
- Multi-label-érték: feltérképezhető, de **DISTINCT entity-count** kell, NEM label-instance-count

## Háttér — 2026-05-18 B-7 fanout typed-rate report-incidens

A B-7 7-batch fanout után az audit-script azt jelentette: "tipizáltság 88.4%". Ez gyanúsan magas volt, mert csak ~1262 entity-re futott le explicit re-type call az autocommit-fix után. Manuális vizsgálat:

```cypher
// audit-script logika (ROSSZ)
MATCH (n:Concept) RETURN count(n);  // 3349
MATCH (n:Decision) RETURN count(n); //   20
MATCH (n:Pattern) RETURN count(n);  //  948
MATCH (n:Skill) RETURN count(n);    // 2480
MATCH (n:Project) RETURN count(n);  //  220
MATCH (n:Tool) RETURN count(n);     //  733
// Sum = 7750. Entity-total = 8997. Typed-rate = 7750/8997 = 86.1%. BUT...
```

A **valódi** tipizáltság mérve `size(labels) > 1`:

```cypher
MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n);
// = 6547. Tipizáltság = 6547/8997 = 72.8%.
```

A 7750 - 6547 = **1203 "extra" label-instance** olyan entity-kből származott, amik **2-3 címkét** kaptak (pl. egy GEPA-szerű entity lehet `:Skill` + `:Pattern` egyszerre, vagy egy szakkifejezés `:Concept` + `:Tool`). A SUM-alapú riport ezeket dupla-háromszor számolta, és ~12pp-vel felfújta a "tipizáltság" számot.

## A pattern

### Helyes mérőszámok set

```cypher
-- 1. Total entity count (denominator)
MATCH (n:Entity) RETURN count(n) AS total;

-- 2. Tipizált = van legalább 1 további label az alap :Entity-n túl
MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n) AS typed;

-- 3. Generic-only (csak :Entity, nincs más)
MATCH (n:Entity) WHERE size(labels(n)) = 1 RETURN count(n) AS generic_only;

-- 4. Multi-label (2+ típus-címke az :Entity mellett)
MATCH (n:Entity) WHERE size(labels(n)) > 2 RETURN count(n) AS multi_typed;

-- 5. Label-distribution DISTINCT entity-szám szerint (helyes pie-chart)
MATCH (n:Entity)
UNWIND labels(n) AS lbl
WITH lbl, count(DISTINCT n) AS cnt
WHERE lbl <> 'Entity'
RETURN lbl, cnt ORDER BY cnt DESC;
```

A 5. query is "duplán számol" abban az értelemben, hogy ha egy entity `:Concept` ÉS `:Pattern`, akkor mind a két sor inkrementálódik 1-gyel — de ez **szándékos** egy distribution-bontásnál (mindkét label-nek 1 entity-tagja van). A SUM ezen oszlopon NEM értelmezhető tipizáltságként.

### Multi-label arány (mennyire átfedők a címkék)

```cypher
MATCH (n:Entity)
RETURN size(labels(n)) AS label_count, count(n) AS entities
ORDER BY label_count;
-- Eredmény pl:
-- 1 → 2450 (generic-only)
-- 2 → 5344 (1 típus-címke)
-- 3 → 1100 (2 típus-címke)
-- 4 →  103 (3 típus-címke, ritka)
```

Ez adja a tényleges multi-label-átfedés-eloszlást, ami a SUM ↔ DISTINCT delta-t magyarázza.

## Anti-pattern: SUM-of-counts mint typed-rate

```cypher
-- ROSSZ pattern, double-counts multi-label entity-ket
MATCH (n) WHERE n:Concept OR n:Pattern OR n:Skill ... RETURN count(n);
```

Ez a query is helytelen, mert `OR` látszólag "DISTINCT-el", de az `n` változó minden találatra egyszer számolódik **a label-megelégedésig** — viszont ha 3 label-konstrukció kifejezetten SUM-előállítást vár (különálló queryben + Python-oldali +=), akkor a Python-script double-count.

Másik anti-pattern: **`labels(n)[1]` mint "az első nem-Entity label"**. Ez label-sorrendet feltételez, ami Memgraph-ban NEM garantált — két azonos-tag-szettű entity különböző sorrendű array-t adhat vissza (storage-belső sorrend). Helyette explicit filter: `[l IN labels(n) WHERE l <> 'Entity'][0]`.

## Reusable szabályok

1. **Alap-label konvenció:** minden entity-nek legyen 1 alap-label (pl. `:Entity`), amit a tipizálás SOSEM ad/vesz el. A tipizálás pluszban címkéz: `:Entity:Concept`, `:Entity:Pattern`, stb. Ezzel a `size(labels) > 1` típus-detektor stabil.
2. **Tipizáltság := DISTINCT(typed)/DISTINCT(total)** — sose SUM-instance-alapú.
3. **Label-distribution riportban tüntesd fel az "X% multi-label" sort** — különben a stake-holder feltételezi, hogy a barchart-oszlopok diszjunktak.
4. **Audit-script `count(DISTINCT n)`-t használjon** mindig, amikor entity-ket számol, NEM `count(n)`-t többszörös label-collect után.
5. **Schema-konstans-list:** definiálj egy `LABEL_HIERARCHY` constants-listát (pl. `["Concept", "Pattern", "Decision", "Skill", "Project", "Tool", "Person", "Event"]`) és minden audit script ebből iteráljon — NE hardkódolj cypher-stringben.

## Hatás más graph-metrikákra

A multi-label edge-case nem csak tipizáltságot érint, hanem:

- **Hub-detection** — degree-számolás OK (edge-based), de label-szűrt-degree (`MATCH (n:Concept)-[r]->()`) szintén dupla-count-olhat, ha relations is multi-typed
- **Community-membership** — Leiden / Louvain community-detection node-szinten egyértelmű, de "label-szerinti community-distribution" overlap-tárgyat tartalmaz
- **PageRank label-szűrt projekción** — `MATCH (n:Concept) WHERE n IN nodes_in_subgraph` nézi label-tagságot, multi-label node-ok többször vesznek részt
- **Vector-search label-filter:** `WHERE node.label = 'Concept'` Cypher-pattern NEM működik label-ekre, label-tagság-vizsgálat kell (`'Concept' IN labels(n)`)

## Komplementer pattern-ek

- **Schema-validáció** — startup-time-on script ellenőrzi, hogy minden entity-nek `:Entity` címkéje van. Ha nincs, error-flag
- **Label-lifecycle** — explicit `REMOVE n:OldLabel` parancs label-deprekációra, NEM hagyod hogy maradjon és piszkítsa a metrikát
- **Tipizáltság-target** = entity-szintű DISTINCT-rate, NEM label-instance density
- **Tag-cleanup ritka labels-re** — ha egy label <10 entity-n él, vagy beolvad nagyobb taxonómiába, vagy kerül `:OtherSpecific`-be
- **Test-script multi-label-overlap-on** — unit-test, ami szándékosan multi-label entity-t hoz létre, futtatja a metrika-querykt, és asserts a "tipizáltság < instance-sum"-ot

## Élő alkalmazás — vault audit-szkript-fix (Next session)

> [!todo] TODO
> - `/usr/local/bin/vault-typedness-report` query-csere SUM-ról `size(labels(n)) > 1`-re
> - Backfill: 2026-05-17-3 → 2026-05-18 közötti tipizáltság-mérések újraszámolása (manual riport correction)
> - Label-distribution barchart kapjon "multi-label X%" footnote-ot
> - Schema-validate cron — heti `MATCH (n) WHERE NOT n:Entity RETURN count(n)`, ha > 0, alert

## Kapcsolódó

- [[memgraph-ce-feature-limits]] — Memgraph CE feature-mátrix
- [[mgclient-autocommit-silent-rollback]] — másik B-7 fanout során felfedett pitfall
- [[subagent-fanout-context-aware-classification]] — a tipizálási flow felépítése
- [[two-tier-graph-extraction]] — graphify (deterministic) komplementer Memgraph LLM-tipizáláshoz
- [[../02-Projects/superintelligent-vault]] — B-7 axis project
