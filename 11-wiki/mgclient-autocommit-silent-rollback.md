---
name: mgclient autocommit silent-rollback pitfall
type: wiki
tags: ["#type/wiki", "memgraph", "python", "database", "driver-default", "silent-failure"]
created: 2026-05-18
updated: 2026-05-18
status: stable
---

# mgclient autocommit silent-rollback

A `pymgclient` (Memgraph hivatalos Python driver) `connect()` alap-default-ja **explicit-transaction-mode**. Ha `conn.autocommit = True` NEM kerül beállításra, akkor minden `SET`, `CREATE`, `MERGE`, `DELETE` statement **silent-rollback**-et szenved a `conn.close()` (vagy connection-drop) pillanatában — mintha semmi sem történt volna. **Hibát NEM dob.** A query-eredmény (`fetchall()`) jól néz ki, a count visszaadva, de a DB állapota érintetlen marad.

## TL;DR

- `conn = mgclient.connect(...)` után **első utasítás:** `conn.autocommit = True`
- VAGY minden write-batch végén explicit `conn.commit()` a `conn.close()` ELŐTT
- Tünet: a script "sikeres", de a `MATCH (n) RETURN count(n)` ugyanazt mutatja előtte/utána
- Detektálás: count-query előtte ÉS utána, diff-check kötelező
- Ez a pitfall NEM Memgraph-specifikus — `mariadb`, `cx_Oracle`, `psycopg2` (autocommit default-False) ugyanígy viselkedik

## Háttér — 2026-05-18 B-7 typing batch incidens

A vault B-7 axis (entity-tipizáltság) 2026-05-17-3 fázisban 14.87%-ra ért. A 2026-05-18 reggeli batch-fanout célja: ~8997 entity-ből minél többet `:Concept`, `:Decision`, `:Skill`, `:Pattern` címkével ellátni. A subagent-stack 7 batch-ben kiosztott classification-eket pumpált fel `vault-graph-retype` wrapper-en keresztül.

**Probléma:** az első 4 batch (összesen ~1262 classification call) lefutott, exit 0, log "OK", de a Memgraph `MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n)` query **0 változást mutatott**. Manuálisan újra-futtatva ugyanaz. Logikai hiba sehol, query helyes, paraméterek helyesek.

A root-cause: a `vault-graph-retype` wrapper a `mgclient.connect()`-et használta, de a `conn.autocommit = True` flag-et **nem állította be**. A driver alap-default-ja explicit-tx-mode, és a script `conn.commit()` nélkül zárta a kapcsolatot → minden SET statement rollback. A subagent jelentései szerint "1262 entity tipizálva", DB-szerint: 0.

A fix egysoros volt:

```python
conn = mgclient.connect(host="localhost", port=7687)
conn.autocommit = True   # ← KÖTELEZŐ, ENNYI
```

Második futás után 28.9% → 72.8% tipizáltság (1262 + extra batch-ek).

## A pattern

```python
import mgclient

def memgraph_write(query, params):
    conn = mgclient.connect(host="localhost", port=7687)
    conn.autocommit = True   # ← ELSŐ utasítás, NEM cursor előtt, NEM után
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        # Read result if needed
        return cur.fetchall()
    finally:
        conn.close()
```

VAGY explicit-tx mintán (ha tranzakciós csoportosítás kell):

```python
conn = mgclient.connect(host="localhost", port=7687)
# autocommit MARAD False, mert tx-csoport kell
try:
    cur = conn.cursor()
    for entity in batch:
        cur.execute("SET n:Concept WHERE n.name = $name", {"name": entity})
    conn.commit()   # ← explicit, mind-vagy-semmi
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

A KÉT minta közül **autocommit=True az alap**, és csak akkor explicit-tx ha:
- atomicitás kell több statement között
- rollback-szándék van hibára (különben részleges write marad)

## Anti-pattern: "majd commit lesz a close-ra"

```python
# ROSSZ
conn = mgclient.connect(...)
cur = conn.cursor()
for x in items:
    cur.execute("CREATE (n:X {id: $id})", {"id": x})
conn.close()   # ← SILENT ROLLBACK, 0 row created
```

A `conn.close()` **NEM** commit-ol. Connection-drop-pal a server rollback-eli a folyamatban lévő explicit tx-et. Ez NEM hiba, NEM warning, NEM exception — csak nem történt semmi.

Hasonló anti-pattern: `with mgclient.connect(...) as conn:` context-manager használata abban a hitben, hogy az `__exit__` commit-ol. **Nem** commit-ol — close-ol, ami szintén rollback.

## Detektálás (sanity-check pattern)

Minden write-batch elé/után count-query:

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

Ez bukásra állítja a scriptet ha silent-rollback történt, és lehetőséget ad a fix-elésre.

## Wider lesson: driver-default audit

A pitfall NEM csak `mgclient` — sok DB-driver-nek explicit-tx-mode az alap-default, ami silent-rollback-et okoz close-on. Audit-checklist új DB-integráció előtt:

| Driver | Autocommit default | Silent-rollback rizikó |
|---|---|---|
| `pymgclient` (Memgraph) | False | **MAGAS** |
| `neo4j` Python driver | implicit-tx auto-commit | Alacsony (driver szándékos) |
| `psycopg2` (Postgres) | False | **MAGAS** |
| `psycopg3` | False (de jobb error-handling) | Közepes |
| `mariadb` Python | False | **MAGAS** |
| `cx_Oracle` / `python-oracledb` | False | **MAGAS** |
| `sqlite3` stdlib | "deferred" (implicit-begin) | Közepes (commit kell) |
| `pyodbc` | False | **MAGAS** |
| `prisma` (Python via JSON-RPC) | True | Alacsony |
| `sqlalchemy` ORM | tranzakcionális (explicit `session.commit()`) | Magas ha felejtős |

**Reusable szabály:** új DB-driver első PoC-jában **mindig** count-before / write / count-after pattern, és csak akkor szabadulj fel a sanity-check alól, ha 3 független write 100%-ban perzisztens lett.

## Komplementer pattern-ek

- **Idempotens MERGE** — `MERGE (n:X {id: $id}) ON CREATE SET ... ON MATCH SET ...` ha többször futtatható a script
- **Health-check beforehand** — `MATCH (n) RETURN count(n) LIMIT 1` ping a write-batch előtt, hogy a connection él
- **Connection-pool** vs single-conn — pool esetén minden conn-on autocommit-set kell külön
- **Audit-log per batch** — sikeres apply → írj egy log-line-t a vault `06-Audits/`-ba a count-delta-val

## Kapcsolódó

- [[memgraph-ce-feature-limits]] — Memgraph CE feature-mátrix, ahol releváns
- [[vault-cleanup-multi-script-policy]] — script-ek közös pattern-jei
- [[../05-Memory/Infrastructure]] — Memgraph deploy-info (container, port)
- [[multi-layer-safety-gate]] — sanity-check mint védelmi réteg
