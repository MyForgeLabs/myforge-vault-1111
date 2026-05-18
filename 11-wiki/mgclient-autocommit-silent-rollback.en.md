---
name: mgclient autocommit silent-rollback pitfall
type: wiki
tags: ["#type/wiki", "memgraph", "python", "database", "driver-default", "silent-failure"]
created: 2026-05-18
updated: 2026-05-18
status: stable
lang: en
translated_from: mgclient-autocommit-silent-rollback.md
---

# mgclient autocommit silent-rollback

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[mgclient-autocommit-silent-rollback.md]] (Hungarian version).

The `pymgclient` (the official Memgraph Python driver) `connect()` default is **explicit-transaction-mode**. If `conn.autocommit = True` is NOT set, then every `SET`, `CREATE`, `MERGE`, `DELETE` statement gets **silently rolled back** when `conn.close()` runs (or the connection drops) — as if nothing had happened. **No error is raised.** The query result (`fetchall()`) looks fine, the row count is returned, but the DB state is untouched.

## TL;DR

- After `conn = mgclient.connect(...)`, **first statement:** `conn.autocommit = True`
- OR explicitly `conn.commit()` at the end of every write batch, BEFORE `conn.close()`
- Symptom: script reports "success", but `MATCH (n) RETURN count(n)` shows the same value before/after
- Detection: count query before AND after, diff-check mandatory
- This pitfall is NOT Memgraph-specific — `mariadb`, `cx_Oracle`, `psycopg2` (autocommit default false) behave the same way

## Background — a bulk-typing batch incident

During a graph entity-typing batch (~8997 entities → label with `:Concept`, `:Decision`, `:Skill`, `:Pattern`), a subagent stack pushed classifications via a `vault-graph-retype` wrapper.

**Problem:** the first 4 batches (~1262 classification calls total) ran, exit 0, log "OK", but a Memgraph `MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n)` query showed **0 changes**. Re-running manually: same. No logic error, query correct, parameters correct.

Root cause: the wrapper used `mgclient.connect()` but did NOT set `conn.autocommit = True`. The driver's default is explicit-tx-mode, and the script closed the connection without `conn.commit()` → every SET statement rolled back. The subagent reports said "1262 entities typed", but per the DB: 0.

The fix was one line:

```python
conn = mgclient.connect(host="localhost", port=7687)
conn.autocommit = True   # ← MANDATORY, that's it
```

After the second run: typing coverage 28.9% → 72.8% (1262 + extra batches).

## The pattern

```python
import mgclient

def memgraph_write(query, params):
    conn = mgclient.connect(host="localhost", port=7687)
    conn.autocommit = True   # ← FIRST statement, NOT before/after cursor
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()
```

OR explicit-tx pattern (when transactional grouping is needed):

```python
conn = mgclient.connect(host="localhost", port=7687)
# autocommit STAYS False, because tx grouping is required
try:
    cur = conn.cursor()
    for entity in batch:
        cur.execute("SET n:Concept WHERE n.name = $name", {"name": entity})
    conn.commit()   # ← explicit, all-or-nothing
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

Of the two patterns, **autocommit=True is the default**, and explicit-tx is only required if:
- atomicity is needed across multiple statements
- you want rollback intent on error (otherwise a partial write remains)

## Anti-pattern: "commit will happen on close"

```python
# WRONG
conn = mgclient.connect(...)
cur = conn.cursor()
for x in items:
    cur.execute("CREATE (n:X {id: $id})", {"id": x})
conn.close()   # ← SILENT ROLLBACK, 0 rows created
```

`conn.close()` does **NOT** commit. On connection drop, the server rolls back the in-flight explicit tx. This is NOT an error, NOT a warning, NOT an exception — nothing simply happens.

Related anti-pattern: `with mgclient.connect(...) as conn:` context-manager use, hoping that `__exit__` commits. It does **NOT** commit — it closes, which is also rollback.

## Detection (sanity-check pattern)

Before/after every write batch, run a count query:

```python
def safe_batch_write(write_fn, batch_name="batch"):
    before = query_count("MATCH (n) RETURN count(n) AS c")
    write_fn()
    after = query_count("MATCH (n) RETURN count(n) AS c")
    delta = after - before
    if delta == 0 and len(batch) > 0:
        raise RuntimeError(f"{batch_name}: 0 delta despite {len(batch)} ops — autocommit pitfall?")
    log.info(f"{batch_name}: {delta} new nodes (expected ~{len(batch)})")
```

This makes the script fail loudly on silent rollback, and gives an opportunity to fix it.

## Wider lesson: driver-default audit

The pitfall is NOT exclusive to `mgclient` — many DB drivers default to explicit-tx-mode, causing silent rollback on close. Audit checklist before any new DB integration:

| Driver | Autocommit default | Silent-rollback risk |
|---|---|---|
| `pymgclient` (Memgraph) | False | **HIGH** |
| `neo4j` Python driver | implicit-tx auto-commit | Low (driver intentional) |
| `psycopg2` (Postgres) | False | **HIGH** |
| `psycopg3` | False (but better error handling) | Medium |
| `mariadb` Python | False | **HIGH** |
| `cx_Oracle` / `python-oracledb` | False | **HIGH** |
| `sqlite3` stdlib | "deferred" (implicit-begin) | Medium (commit required) |
| `pyodbc` | False | **HIGH** |
| `prisma` (Python via JSON-RPC) | True | Low |
| `sqlalchemy` ORM | transactional (explicit `session.commit()`) | High if forgotten |

**Reusable rule:** in the first PoC of any new DB driver, **always** use count-before / write / count-after pattern, and only stop sanity-checking once 3 independent writes have been 100% persistent.

## Complementary patterns

- **Idempotent MERGE** — `MERGE (n:X {id: $id}) ON CREATE SET ... ON MATCH SET ...` if the script may run repeatedly
- **Health-check beforehand** — `MATCH (n) RETURN count(n) LIMIT 1` ping before the write batch to ensure the connection is alive
- **Connection-pool** vs single-conn — with a pool, every conn needs autocommit set separately
- **Audit-log per batch** — successful apply → write a log line with the count-delta

## Related

- [[memgraph-ce-feature-limits]] — Memgraph CE feature matrix
- [[multi-layer-safety-gate]] — sanity-check as a defense layer
- [[verification-step-before-claim]] — verify before claiming success
