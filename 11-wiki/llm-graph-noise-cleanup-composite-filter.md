---
name: LLM graph-noise cleanup composite filter
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#project/sv", "extraction-quality", "graph-cleanup"]
---

# LLM graph-noise cleanup — composite filter pattern

A 2-phase composite filter for cleaning LLM-generated knowledge-graph noise: pattern-shape DELETE (Tier-A) + sc=1 ∧ multi-condition composite DELETE (Tier-C).

## Trigger

LLM-extracted entity-graphs accumulate noise at scale: quoted strings, hex colors, file paths, single-mention sentence fragments. A naive single-shape filter under-deletes; a too-aggressive count-only filter over-prunes legitimate single-mention concepts.

## Composite-filter structure

### Tier-A (hard-noise shape patterns)

Delete entities whose `name` matches any of:

```cypher
MATCH (n:Entity)
WHERE n.name =~ '^["''\\u201E].*'    // quoted-string-start
   OR n.name =~ '^#[0-9a-fA-F]{3,6}$' // hex-color
   OR n.name =~ '^https?://'          // URL-fragment
   OR n.name =~ '^[[:punct:]]'        // starts_with_punct
   OR n.name =~ '^[./]?(\\.\\.?/)*[a-zA-Z0-9_\\-./]+\\.(py|md|js|ts|json|yml|yaml|html|css|sh)$'  // looks_like_path
   OR (n.name CONTAINS '=' AND size(n.name) < 60)  // contains_equals_assign
   OR n.name CONTAINS '<' OR n.name CONTAINS '>'   // html-angle
DETACH DELETE n
```

Per-batch DELETE 500-1000 rows for transactional safety.

### Tier-C (composite: low source-count AND noise-shape OR length)

Delete entities that are:

```cypher
MATCH (n:Entity)
WHERE n.source_count = 1
  AND (
    size(split(n.name, ' ')) >= 3   // ≥3 tokens (sentence fragment)
    OR n.name =~ '^["''\\u201E].*'  // Tier-A residual
    OR ...                          // other Tier-A patterns
  )
DETACH DELETE n
```

## Defense rules (KEEP exclusions)

1. **`source_count = 0` typed-retype-injectees are KEPT.** These are entities introduced by the typed-classification pipeline (Person/Project/Concept/Alias) without a count, and are NOT noise.
2. **`max_confidence >= 0.8` exclusion** — even single-mention high-confidence entities are KEPT. Add to Tier-C predicate: `AND coalesce(n.max_confidence, 0.5) < 0.8`.
3. **Manually-tagged whitelist** — entities matching specific `slug` patterns (e.g. `kgc-*`, `mfl-*`) can be exempt via `WHERE NOT n.slug =~ '^(kgc|mfl|sv|boulium)-.*'`.

## Snapshot before DELETE

Non-negotiable. Five artifacts:
- Memgraph DUMP (cypherl format) — `docker exec vault-memgraph mgconsole --execute "DUMP DATABASE;"`
- facts.db backup (if KO-DB is sibling-system) — `cp facts.db facts.db.pre-cleanup-YYYY-MM-DD.bak`
- baseline-stats JSON — `vault-graph-diff --json > snapshots/baseline-graph-diff.json`
- sample-100 random entity dump — `MATCH (n:Entity) WITH n LIMIT 100 RETURN n.name, n.source_count`
- vault git-commit hash — `git rev-parse HEAD`

## Verification gate

Post-cleanup `vault-graph-diff --json | jq '.jaccard'` — for Phase-4 acceptance, Jaccard must reach ≥0.05.

**Empirical caveat (2026-05-19)**: Tier-A + Tier-C deletes alone shifted Jaccard from 0.0070 → 0.0078 (+0.0008). The two extraction stacks (LLM-narrative vs tree-sitter/Leiden) produce structurally orthogonal vocabularies, so noise-DELETE only shrinks the denominator. **Phase-3 selective re-extract with a tightened prompt is required to lift the numerator.**

## When to use this pattern

- LLM-extracted entity-graph hits >5k entities and Jaccard against any deterministic baseline is <0.02.
- Single-mention rate (`source_count = 1`) exceeds 40% of total entities.
- Tier-A shape pattern coverage (`grep` regex match) exceeds 5% of total entities.

## When NOT to use

- Single-source-only graphs (Jaccard not applicable).
- High-precision domain extractions where every entity was manually curated.

## Related

- [[two-tier-graph-extraction]] — the parent pattern (LLM Tier-1 ∩ deterministic Tier-2)
- [[vault-ko-ingest-prompt-tightening-2026-05-19]] — prevent-noise-at-source companion
- [[../06-Audits/2026-05-19 Memgraph entity-cleanup analysis]] — analysis that derived the 7 Tier-A rules
- [[../06-Audits/2026-05-19 Memgraph cleanup execution result]] — first execution audit
