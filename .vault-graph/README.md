---
name: .vault-graph
type: infra-layer
created: 2026-05-17
updated: 2026-05-17
tags: [layer/world-model, sprint/B-7, infra/memgraph]
---

# .vault-graph — World-model Knowledge Graph (SV B-7)

Memgraph-backed entity-graph built on top of the KO-DB triplet store
(`.vault-ko/facts.db`). This is the **entity-relation layer** of the
Superintelligent Vault — the structured world-model that complements the
KO-DB (atomic facts) and the wiki (evergreen prose).

- **Schema:** [[../00-Meta/graph-schema.yml]] (9 entity-types + 6 relations, draft v0.1)
- **ADR:** [[../07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch]]
- **Wiki:** [[../11-wiki/sv-06-world-model-knowledge-graph]]
- **Source:** [[../.vault-ko/facts.db]] (~14K triplets)
- **Backend:** Memgraph container `vault-memgraph`, port 7687 (shared with B-2)

## Status

- **Phase:** Week 1-α (Day 0 → first extraction, 2026-05-17)
- **Schema:** Loose extraction — subject/object become nodes, predicate becomes
  edge type. No schema-typed entities yet (Project/Person/Server/…) — that
  is Week 2 work using SchemaLLMPathExtractor.

## Layout

```
.vault-graph/
├── README.md                        # this file
├── schema/
│   └── entity-graph-schema.cypher   # indexes + constraints
└── scripts/
    ├── vault-graph-extract.py       # KO-DB → Memgraph nodes/edges
    └── vault-graph-query.py         # thin Cypher wrapper
```

## Quickstart

```bash
# preview without writing
vault-graph-extract --dry-run

# full extraction (idempotent — uses MERGE)
vault-graph-extract

# wipe & rebuild
vault-graph-extract --reset

# query
vault-graph-query "MATCH (e:Entity) RETURN e.name ORDER BY e.source_count DESC LIMIT 5"
```

## Namespace convention

The Memgraph container is shared with B-2 (vault-memory). To stay isolated:

- All nodes here carry label **`:Entity`** or **`:Literal`**.
- Other B-2 nodes use different labels (e.g. `:VaultDoc`, `:Session`).
- Relations get the **uppercased snake-case predicate** as edge type
  (e.g. `has_minimum` → `:HAS_MINIMUM`).

A subject in KO-DB → `:Entity`. An object is `:Entity` iff it appears as a
subject somewhere; otherwise `:Literal`.

## Node properties

| Label    | Properties                                         |
|----------|----------------------------------------------------|
| Entity   | `name`, `source_count`, `max_confidence`           |
| Literal  | `value`                                            |

Edges carry: `confidence`, `provenance`, `source_type`, `fact_hash`.

## Roadmap

- **Week 1 (now):** loose extraction; smoke-query the top entities.
- **Week 2:** SchemaLLMPathExtractor over the wiki/ADR corpus, typed nodes.
- **Week 3:** cross-link entity-graph nodes back to KO-DB rows + wiki files.
- **Week 4:** false-positive review-loop, then `validation.strict_mode=true`.

## Related

- [[../11-wiki/sv-06-world-model-knowledge-graph]] — research
- [[../07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch]] — ADR
- [[../02-Projects/superintelligent-vault]] — roadmap
- [[../.vault-ko]] — KO-DB triplet store (source of truth)
