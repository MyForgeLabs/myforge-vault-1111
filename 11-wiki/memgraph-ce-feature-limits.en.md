---
name: Memgraph CE feature-limits + workarounds
type: wiki
tags: ["#type/wiki", "memgraph", "graph-db", "infrastructure", "gotchas"]
created: 2026-05-17
updated: 2026-05-17
status: stable
lang: en
translated_from: memgraph-ce-feature-limits.md
---

# Memgraph CE feature-limits + workarounds

> **TL;DR:** Memgraph **Community Edition** silently breaks on 4 features Neo4j users assume work: (1) DDL inside multi-statement transactions, (2) constraints inside transactions, (3) multi-database, (4) MAGE algorithms. The win: **native vector-index is FREE in CE 3.9.0** — measured **1ms mean / 2.6ms p95 search latency**, **280× speedup** over our previous numpy-cosine workaround. Multi-namespace vector-index (3 namespaces × 2829/462/8997 nodes) works **out-of-the-box, zero Enterprise license needed**.

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[memgraph-ce-feature-limits.md]] (Hungarian version).

The Memgraph **Community Edition** (current build: `memgraph/memgraph:latest` → **3.9.0**) silently rejects or hard-errors on several core features — a production-bug source if you code against it as if it were Neo4j. This doc collects limits actually hit in production and the working workarounds. Update as new limits surface.

## What this is NOT

- **NOT a Memgraph-vs-Neo4j shootout** — this is a pragmatic CE feature-list, not a benchmark. We chose Memgraph for the in-memory vector-index; your call may differ.
- **NOT exhaustive** — only limits hit in our production. Other CE limits (HA cluster, audit-log, RBAC) are listed in the migration table but we have NOT independently verified them.
- **NOT static** — Memgraph ships fast. The "WORKS in CE 3.9.0" callout flipped from earlier docs. Re-verify before relying on it.
- **NOT a recommendation against Enterprise** — if you need multi-tenancy or HA, pay for Enterprise. The point is CE goes much further than the 2023-era docs suggested.

## The 4 main limits

| # | Feature | CE behavior | Concrete error / symptom |
|---|---|---|---|
| 1 | **DDL inside multicommand-transactions** (`BEGIN; CREATE INDEX … ; COMMIT;`) | Hard-fail | `Index manipulation is not allowed in multicommand transactions. … please use an implicit transaction` |
| 2 | **Constraints inside transactions** | Hard-fail | `Constraint manipulation is not allowed in multicommand transactions.` |
| 3 | **Multi-database** (`CREATE DATABASE`, `SHOW DATABASES`, `USE DATABASE`) | Enterprise-only | `Your license has an invalid type. To use multi-tenancy you need to have an enterprise license.` |
| 4 | **MAGE algorithm procedures** (pagerank, community_detection, node2vec, betweenness, …) | Missing from base image | `CALL pagerank.get()` → `there is no registered procedure with name 'pagerank.get'` (need separate `memgraph/memgraph-mage` image) |

> [!success] What **WORKS** in CE 3.9.0 (earlier tips are stale)
> - **Native vector index** works: `CREATE VECTOR INDEX <name> ON :Label(prop) WITH CONFIG {"dimension": 1024, "capacity": 2048, "metric": "cos"}` + `CALL vector_search.search(...)`. Free in CE from 3.9.0. The earlier numpy-cosine workaround is no longer needed for new projects (see below).
> - **User management** (`CREATE USER … IDENTIFIED BY …`, `DROP USER`) — free, but RBAC roles need Enterprise.
> - **Replication** basics (`SHOW REPLICATION ROLE`, `REGISTER REPLICA`) — work in CE.

## Workaround playbook

### 1+2. DDL/Constraint in transactions → autocommit + MERGE-by-name

**Forbidden:**
```python
with driver.session() as s:
    with s.begin_transaction() as tx:
        tx.run("CREATE INDEX ON :Entity(name)")  # ← BOOM
        tx.run("CREATE CONSTRAINT ON (e:Entity) ASSERT e.name IS UNIQUE")
```

**Correct — two paths:**

A) **Via mgconsole, row-level autocommit** (once, at startup):
```bash
docker exec my-memgraph bash -c \
  "echo 'CREATE INDEX ON :Entity(name);' | mgconsole --use_ssl=false"
```

B) **In the Python driver — `session.run` directly, NOT in a `tx`** (implicit transaction = autocommit):
```python
with driver.session() as s:
    s.run("CREATE INDEX ON :Entity(name)")  # ✅ autocommit
```

C) **App-layer MERGE-dedup instead of constraints:**
```python
# No UNIQUE constraint — instead MERGE guarantees one instance per name
tx.run("""
  MERGE (e:Entity {name: $name})
  ON CREATE SET e.created_at = timestamp()
  ON MATCH  SET e.frequency = coalesce(e.frequency, 0) + 1
""", name=ent_name)
```

### 3. Multi-database → 1 instance per project + label namespace

CE has no `DATABASE` concept — everything lives in the default `memgraph` DB. Workaround: **label-prefix namespacing** (`:ProjectA_Entity` vs `:ProjectB_Entity`), or a separate Docker container per project on different ports.

### 4. MAGE algorithms → image swap

Replace `memgraph/memgraph:latest` with `memgraph/memgraph-mage:latest` in `docker-compose.yml`. Drop-in, same data volume is compatible. Adds ~600MB image size, but you get pagerank / community / node2vec / shortestpath / weakly_connected_components / 50+ algorithms.

## Live example — entity-graph extract

A live entity-graph extracted from a corpus via an LLM pipeline, written to Memgraph CE:

```
SHOW STORAGE INFO  →  vertex_count: 23964, edge_count: 13812, memory: 105 MiB
SHOW INDEX INFO    →  label+property index :Entity(name) (created via autocommit)

MATCH (n) RETURN labels(n), count(*)
  ["Literal"]   12160
  ["Entity"]     8975
  ["Chunk"]      2829
```

**What we swapped:** the original loader started a `CREATE CONSTRAINT ... IS UNIQUE` inside a transaction → fail. Refactor: push the index migration-style via `mgconsole` autocommit, and every ingest pass uses `MERGE (e:Entity {name: $name})`. We get app-layer dedup with index assistance (`MERGE` looks up via `:Entity(name)` index → O(log n)).

## Migration to Enterprise / MAGE — when

| Criterion | Stay on CE | MAGE image | Enterprise license |
|---|---|---|---|
| <50K nodes, <500K relationships | ✅ | — | — |
| Algorithm needs (pagerank, community, shortestpath) | — | ✅ | — |
| >100K nodes + <1ms vector latency | — | ✅ (HNSW tuning) | — |
| Multi-tenant (multiple isolated DBs in 1 instance) | — | — | ✅ |
| RBAC roles, audit log, fine-grained auth | — | — | ✅ |
| HA cluster (sync replication, automatic failover) | — | — | ✅ |

## Native vector-index VERIFIED LIVE

Memgraph CE 3.9.0 **natively supports vector indexes** — verified in production.

- Syntax: `CREATE VECTOR INDEX vault_chunk_vec ON :Chunk(embedding) WITH CONFIG {"dimension": 1024, "metric": "cos", "capacity": 8192};`
- Query: `CALL vector_search.search('vault_chunk_vec', limit, query_vector) YIELD node, similarity`
- Benchmark: **pure search mean 1ms / p95 2.6ms** (280× speedup vs numpy-cosine workaround)
- Top-K result agreement with numpy: 100% (3 queries × k=3 byte-exact)

## Multi-namespace vector-index confirmation

One Memgraph DB can host multiple independent label-prop vector indexes in parallel — 0 mucking-around (`SHOW INDEX INFO` lists them together). Example:

```
label+property_vector  Chunk       embedding  2829   (vault content)
label+property_vector  SkillChunk  embedding   462   (skill pool)
label+property_vector  Entity      embedding  8997   (entity-graph)
```

- 3 different namespaces (content / skill-pool / entity-graph)
- 0 cross-namespace interference (separate index, separate cosine space)
- Latency independent: search 8-13ms on the 462-skill namespace, mean 1ms on the 2829-content namespace
- `CREATE VECTOR INDEX <name> ON :<Label>(<prop>) WITH CONFIG ...` is one CQL statement per namespace

**Reusable insight:** Memgraph CE multi-tenant vector-search **out-of-the-box** (no Neo4j-style license requirement), namespace per `:<Label>` trivially separated.

## Related

- [[mgclient-autocommit-silent-rollback]] — the related Python driver pitfall
- [[verification-step-before-claim]] — verify vendor features before implementing workarounds
