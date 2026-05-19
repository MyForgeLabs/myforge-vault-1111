---
name: Memgraph multi-labeling — typedness metric edge case
type: wiki
lang: en
translated_from: memgraph-multi-labeling-edge-case-typedness-measurement
tags: ["#type/wiki", "memgraph", "graph-metrics", "labels", "measurement", "double-counting"]
created: 2026-05-18
updated: 2026-05-18
status: stable
---

# Memgraph multi-labeling typedness metric

## 🎧 Audio overview

- **Deep-dive podcast** (NotebookLM 2-host, ~5 min, EN): [memgraph-multi-labeling-edge-case-typedness-measurement.en-podcast.mp3](../.vault-nb/audio-overviews/memgraph-multi-labeling-edge-case-typedness-measurement.en-podcast.mp3) (44 MB) — *"The 88.4 Percent Data Illusion"*

Memgraph entities (and Neo4j, and Cypher graph-DBs generally) can carry **multiple labels** (`SET n:Concept; SET n:Pattern;`). Typedness metrics (typed-rate, label-distribution, multi-label-overlap) suffer from a **double-counting bug** if the script naively does `count(:Label1) + count(:Label2) + ...` SUM — the resulting number **can exceed the entity count**, which is misleading in reports.

## TL;DR

- Memgraph entity: `MATCH (n:Entity) SET n:Concept` results in `n`'s labels = `{Entity, Concept}`. `SET n:Pattern` results in `{Entity, Concept, Pattern}`.
- **Wrong:** `MATCH (n:Concept) RETURN count(n) AS c1` + `MATCH (n:Pattern) RETURN count(n) AS c2` → `c1+c2 > total_entities` (because the `{Concept, Pattern}` overlap is double-counted)
- **Right:** `MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n) AS typed` (`:Entity` is the base label, plus every additional type marker)
- Multi-label coverage can be measured, but **DISTINCT entity count** is required, NOT label-instance count

## Background — fanout typed-rate report incident

After a 7-batch fanout, the audit script reported "typedness 88.4%". This was suspiciously high because only ~1262 entities had explicit re-type calls after the autocommit-fix. Manual investigation:

```cypher
// audit-script logic (WRONG)
MATCH (n:Concept) RETURN count(n);  // 3349
MATCH (n:Decision) RETURN count(n); //   20
MATCH (n:Pattern) RETURN count(n);  //  948
MATCH (n:Skill) RETURN count(n);    // 2480
MATCH (n:Project) RETURN count(n);  //  220
MATCH (n:Tool) RETURN count(n);     //  733
// Sum = 7750. Entity-total = 8997. Typed-rate = 7750/8997 = 86.1%. BUT...
```

The **actual** typedness measured by `size(labels) > 1`:

```cypher
MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n);
// = 6547. Typedness = 6547/8997 = 72.8%.
```

The 7750 - 6547 = **1203 "extra" label instances** came from entities with **2-3 labels** (e.g. a GEPA-like entity may be both `:Skill` and `:Pattern`, or a term may be `:Concept` and `:Tool`). The SUM-based report double- or triple-counted these and inflated the "typedness" number by ~12pp.

## The pattern

### Correct metrics set

```cypher
-- 1. Total entity count (denominator)
MATCH (n:Entity) RETURN count(n) AS total;

-- 2. Typed = at least 1 additional label beyond base :Entity
MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n) AS typed;

-- 3. Generic-only (only :Entity, nothing else)
MATCH (n:Entity) WHERE size(labels(n)) = 1 RETURN count(n) AS generic_only;

-- 4. Multi-label (2+ type labels alongside :Entity)
MATCH (n:Entity) WHERE size(labels(n)) > 2 RETURN count(n) AS multi_typed;

-- 5. Label distribution by DISTINCT entity count (correct pie chart)
MATCH (n:Entity)
UNWIND labels(n) AS lbl
WITH lbl, count(DISTINCT n) AS cnt
WHERE lbl <> 'Entity'
RETURN lbl, cnt ORDER BY cnt DESC;
```

Query 5 also "double-counts" in the sense that if an entity is `:Concept` AND `:Pattern`, both rows get +1 — but that is **intentional** for a distribution breakdown (both labels have 1 entity member). The SUM over this column does NOT make sense as typedness.

### Multi-label ratio (how overlapping labels are)

```cypher
MATCH (n:Entity)
RETURN size(labels(n)) AS label_count, count(n) AS entities
ORDER BY label_count;
-- Result e.g.:
-- 1 → 2450 (generic-only)
-- 2 → 5344 (1 type label)
-- 3 → 1100 (2 type labels)
-- 4 →  103 (3 type labels, rare)
```

This gives the actual multi-label overlap distribution, which explains the SUM ↔ DISTINCT delta.

## Anti-pattern: SUM-of-counts as typed-rate

```cypher
-- WRONG pattern, double-counts multi-label entities
MATCH (n) WHERE n:Concept OR n:Pattern OR n:Skill ... RETURN count(n);
```

This query is also incorrect — `OR` appears to "DISTINCT", but the `n` variable counts once per match **up to label satisfaction**; if 3 label constructions explicitly expect SUM production (separate queries + Python-side +=), the Python script double-counts.

Another anti-pattern: **`labels(n)[1]` as "the first non-Entity label"**. This assumes label ordering, which is NOT guaranteed in Memgraph — two entities with the same tag set may return arrays in different orders (storage-internal order). Use explicit filter instead: `[l IN labels(n) WHERE l <> 'Entity'][0]`.

## Reusable rules

1. **Base-label convention:** every entity has 1 base label (e.g. `:Entity`) that typing NEVER adds/removes. Typing adds extra labels: `:Entity:Concept`, `:Entity:Pattern`, etc. This makes the `size(labels) > 1` type detector stable.
2. **Typedness := DISTINCT(typed)/DISTINCT(total)** — never SUM-instance-based.
3. **In label-distribution reports show an "X% multi-label" row** — otherwise stakeholders assume bar-chart columns are disjoint.
4. **Audit scripts use `count(DISTINCT n)`** whenever counting entities, NOT `count(n)` after a multi-label collect.
5. **Schema constants list:** define a `LABEL_HIERARCHY` constants list (e.g. `["Concept", "Pattern", "Decision", "Skill", "Project", "Tool", "Person", "Event"]`) and iterate from there in every audit script — DO NOT hardcode in cypher strings.

## Impact on other graph metrics

The multi-label edge case affects not only typedness:

- **Hub detection** — degree counting is fine (edge-based), but label-filtered degree (`MATCH (n:Concept)-[r]->()`) can also double-count if relations are multi-typed
- **Community membership** — Leiden / Louvain community detection is unambiguous at node level, but "label-wise community distribution" contains overlap
- **PageRank on label-filtered projections** — `MATCH (n:Concept) WHERE n IN nodes_in_subgraph` checks label membership, multi-label nodes participate multiple times
- **Vector-search label-filter:** `WHERE node.label = 'Concept'` cypher pattern does NOT work on labels, label-membership check needed (`'Concept' IN labels(n)`)

## Complementary patterns

- **Schema validation** — startup-time script verifies every entity has the `:Entity` label. If missing, error-flag
- **Label lifecycle** — explicit `REMOVE n:OldLabel` for label deprecation, do NOT leave it to dirty the metrics
- **Typedness target** = entity-level DISTINCT rate, NOT label-instance density
- **Tag cleanup for rare labels** — if a label lives on <10 entities, either merge into a larger taxonomy or move to `:OtherSpecific`
- **Test script on multi-label overlap** — unit test that intentionally creates a multi-label entity, runs the metric queries, and asserts that "typedness < instance-sum"

## Related

- [[memgraph-ce-feature-limits]] — Memgraph CE feature matrix
- [[mgclient-autocommit-silent-rollback]] — another pitfall discovered during fanout
- [[subagent-fanout-context-aware-classification]] — the typing flow architecture
- [[two-tier-graph-extraction]] — graphify (deterministic) as complement to Memgraph LLM typing
