---
name: Memgraph CE feature-limits + workarounds
type: wiki
tags: ["#type/wiki", "memgraph", "graph-db", "infrastructure", "gotchas"]
created: 2026-05-17
updated: 2026-05-17
status: stable

---

# Memgraph CE feature-limits + workarounds

A Memgraph **Community Edition** (jelen vault-build: `memgraph/memgraph:latest` → **3.9.0**, container `vault-memgraph`) több core feature-t **csendben elutasít** vagy explicit license-hibával eldob — production-bug-forrás, ha az ember Neo4j-mintára kódolja. Ez a doc a vault-projektben (`sv-06-world-model-knowledge-graph`) ténylegesen elcsapott limiteket és a working-workaround-okat gyűjti. Frissítendő ahogy újabb limit bejön.

## A 4 fő limit (vault-relevánsak)

| # | Feature | CE-viselkedés | Konkrét hibaüzenet / tünet |
|---|---|---|---|
| 1 | **DDL multicommand-transaction-ben** (`BEGIN; CREATE INDEX … ; COMMIT;`) | Hard-fail | `Index manipulation is not allowed in multicommand transactions. … please use an implicit transaction` |
| 2 | **Constraint-ek transaction-ben** | Hard-fail | `Constraint manipulation is not allowed in multicommand transactions.` |
| 3 | **Multi-database** (`CREATE DATABASE`, `SHOW DATABASES`, `USE DATABASE`) | Enterprise-only | `Your license has an invalid type. To use multi-tenancy you need to have an enterprise license.` |
| 4 | **MAGE algoritmus-procedúrák** (pagerank, community_detection, node2vec, betweenness, …) | Hiányoznak az alap-image-ből | `CALL pagerank.get()` → `there is no registered procedure with name 'pagerank.get'` (külön `memgraph/memgraph-mage` image kell) |

> [!success] Ami **MŰKÖDIK** CE 3.9.0-ban (korábbi B-2 sprint-tippünk elavult)
> - **Natív vector-index** működik: `CREATE VECTOR INDEX <name> ON :Label(prop) WITH CONFIG {"dimension": 1024, "capacity": 2048, "metric": "cos"}` + `CALL vector_search.search(...)`. 3.9.0-tól ingyenes a CE-ban. A korábbi numpy-cosine workaround már nem szükséges új projekteknél (lásd lent).
> - **Felhasználó-kezelés** (`CREATE USER … IDENTIFIED BY …`, `DROP USER`) — ingyenesen elérhető, de RBAC role-okhoz Enterprise kell.
> - **Replication** alap szinten (`SHOW REPLICATION ROLE`, `REGISTER REPLICA`) — működik CE-ban.

## Workaround playbook

### 1+2. DDL/Constraint transaction-ben → autocommit + MERGE-by-name

**Tilos:**
```python
with driver.session() as s:
    with s.begin_transaction() as tx:
        tx.run("CREATE INDEX ON :Entity(name)")  # ← BUMM
        tx.run("CREATE CONSTRAINT ON (e:Entity) ASSERT e.name IS UNIQUE")
```

**Helyes — két út:**

A) **mgconsole-on át, sor-szintű autocommit** (egyszer, indítás-időben):
```bash
docker exec vault-memgraph bash -c \
  "echo 'CREATE INDEX ON :Entity(name);' | mgconsole --use_ssl=false"
```

B) **Python driverben — `session.run` direkt, NEM `tx`-ben** (implicit transaction = autocommit):
```python
with driver.session() as s:
    s.run("CREATE INDEX ON :Entity(name)")  # ✅ autocommit
```

C) **Constraint helyett app-layer MERGE-dedup** (B-7 entity-graph-ban ezt használjuk):
```python
# Nincs UNIQUE constraint — helyette MERGE garantálja az 1-példányt name szerint
tx.run("""
  MERGE (e:Entity {name: $name})
  ON CREATE SET e.created_at = timestamp()
  ON MATCH  SET e.frequency = coalesce(e.frequency, 0) + 1
""", name=ent_name)
```

### 3. Multi-database → 1 instance / projekt + label-namespace

CE-ban nincs `DATABASE` koncepció — minden 1 alapértelmezett `memgraph` DB-ben él. Vault-megoldás: **label-prefix namespacing** (`:SV_Entity` vs `:Foxxi_Entity`), vagy külön Docker-container per projekt (`vault-memgraph`, `foxxi-memgraph`, eltérő portokon).

### 4. MAGE algoritmusok → image-csere

Cseréld a `memgraph/memgraph:latest`-t `memgraph/memgraph-mage:latest`-re a `docker-compose.yml`-ben. Drop-in, ugyanaz a data-volume kompatibilis. Plusz ~600MB image-méret, de jön a pagerank / community / node2vec / shortestpath / weakly_connected_components / 50+ algoritmus.

## Élő példa — B-7 entity-graph extract (2026-05-17)

A `sv-06-world-model` B-7 sprint a vault-corpus-ből entity-graph-ot extraktál egy LLM-pipeline-on át, és Memgraph CE-ba ír. Jelen állapot a `vault-memgraph` container-ben:

```
SHOW STORAGE INFO  →  vertex_count: 23964, edge_count: 13812, memory: 105 MiB
SHOW INDEX INFO    →  label+property index :Entity(name) (autocommit-tel létrejött)

MATCH (n) RETURN labels(n), count(*)
  ["Literal"]   12160
  ["Entity"]     8975
  ["Chunk"]      2829

MATCH ()-[r]->() RETURN type(r), count(*) ORDER BY count(*) DESC LIMIT 5
  HAS_VALUE   1921
  USES        1862
  PRODUCES    1718
  REQUIRES    1277
  APPLIES_TO   993
```

**Mit cseréltünk:** az eredeti loader `CREATE CONSTRAINT ... IS UNIQUE`-kal indult tranzakcióban → fail. Refactor: az indexet `mgconsole` autocommit-tal toltuk be migration-szerűen, és minden ingest-pass `MERGE (e:Entity {name: $name})`-rel megy. App-layer dedupot kapunk index-segítséggel (`MERGE` `:Entity(name)` indexen lookupol → O(log n)).

## Migráció Enterprise / MAGE-ra — mikor kell

| Kritérium | CE marad | MAGE image | Enterprise license |
|---|---|---|---|
| <50K node, <500K rel | ✅ | — | — |
| Algoritmus-igény (pagerank, community, shortestpath) | — | ✅ | — |
| >100K node + <1ms vector-latency | — | ✅ (HNSW tuning) | — |
| Multi-tenant (több izolált DB 1 instance-ban) | — | — | ✅ |
| RBAC role-ok, audit-log, fine-grained auth | — | — | ✅ |
| HA cluster (sync replication, automatic failover) | — | — | ✅ |

**B-7-re a CE+MAGE upgrade kandidát** — ha entity-cluster-detection (`community_detection.get`) vagy PageRank-ranking kerül a roadmapra, image-csere `memgraph/memgraph-mage:latest`-re, data-volume megmarad.

## Kapcsolódó

- [[sv-01-memory-architecture]] — vault memory-réteg arch.
- [[sv-06-world-model-knowledge-graph]] — KG schema + B-7 entity-graph design
- [[llm-daemon-warm-pattern]] — vault-search-server warm-model pattern (régi numpy-cosine workaround forrása)
- [[../05-Memory/Infrastructure#Memgraph]] — container deploy + port-mapping

## 2026-05-17 native vector-index VERIFIED LIVE

A Memgraph CE 3.9.0 **natívan támogat vector-index-et** — a 2026-05-17-obsidian-vault-2 session során élesben verifikálva.

- Syntax: `CREATE VECTOR INDEX vault_chunk_vec ON :Chunk(embedding) WITH CONFIG {"dimension": 1024, "metric": "cos", "capacity": 8192};`
- Query: `CALL vector_search.search('vault_chunk_vec', limit, query_vector) YIELD node, similarity`
- Benchmark: **pure search mean 1ms / p95 2.6ms** (280× speedup numpy-cosine workaround-hoz képest)
- Top-K result-egyezés numpy-val: 100% (3 query × k=3 byte-pontosan)

**Audit:** [[../06-Audits/2026-05-17 B-2 native vector-index migration]]

A `vault-search.py` `--backend=native|numpy|auto` fallback chain-nel él (native default, numpy fallback ha workaround-érek).

## 2026-05-17-3 multi-namespace vector-index konfirmáció

A B-4 Week 2 sprint kimutatta: **egy Memgraph DB-ben több, független label-prop vector-index él párhuzamosan, 0 mucking-around** (`SHOW INDEX INFO` egyszerre listázza). A vault state most:

```
label+property_vector  Chunk       vector     2829   (vault content)
label+property_vector  SkillChunk  embedding   462   (skill-pool)
label+property_vector  Entity      name       8997   (B-7 entity-graph)
```

- 3 különböző namespace (vault-content / skill-pool / entity-graph)
- 0 cross-namespace interferencia (külön index, külön cosine-space)
- Latency független: search 8-13ms a 462-skill-namespace-en, mean 1ms a 2829-vault-namespace-en
- `CREATE VECTOR INDEX <name> ON :<Label>(<prop>) WITH CONFIG ...` egy CQL-statement / namespace

**Reusable insight:** Memgraph CE multi-tenant vector-search **out-of-the-box** (NEM Neo4j-license-igényes), namespace per `:<Label>` triviálisan elválasztva.
