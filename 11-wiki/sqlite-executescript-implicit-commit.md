---
name: SQLite executescript implicit-commit gotcha
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#concept/sqlite", "#concept/python"]
---

# SQLite `executescript()` implicit-commit gotcha

A Python `sqlite3` driver `conn.executescript(sql)` **always issues a COMMIT first** regardless of the connection's `isolation_level` or any in-flight explicit transaction (`BEGIN IMMEDIATE`).

## Symptom

```python
conn = sqlite3.connect(db_path, isolation_level=None)
conn.execute("BEGIN IMMEDIATE")
try:
    conn.execute("ALTER TABLE foo ADD COLUMN bar INTEGER")  # OK, in txn
    conn.executescript("""
        CREATE TABLE baz (...);
        CREATE INDEX idx_baz ON baz(...);
    """)  # ← implicit COMMIT here, transaction ends
    conn.execute("UPDATE foo SET bar = 1 WHERE ...")  # OK, but no txn now
    conn.execute("COMMIT")  # ← sqlite3.OperationalError: cannot commit - no transaction is active
except Exception:
    conn.execute("ROLLBACK")  # ← cannot rollback either
    raise
```

## Why

[Python docs](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.executescript): "Execute the SQL statements in `sql_script`. **If the autocommit is LEGACY_TRANSACTION_CONTROL and there is a pending transaction, an implicit `COMMIT` statement is executed first.**"

This applies even with `isolation_level=None` (manual transaction mode), because `executescript` was designed for schema-bootstrap scripts where atomic per-statement commits are wanted.

## Fix

Replace `executescript` with individual `execute()` calls inside the transaction:

```python
conn.execute("BEGIN IMMEDIATE")
try:
    conn.execute("CREATE TABLE baz (...)")
    conn.execute("CREATE INDEX idx_baz ON baz(...)")
    conn.execute("UPDATE foo SET bar = 1 WHERE ...")
    conn.execute("COMMIT")
except Exception:
    conn.execute("ROLLBACK")
    raise
```

## When it bit us

2026-05-19 — `migrate-hash-refactor-2026-05-19.py` (KO-DB Option-C migration) had 3 `executescript()` calls. First APPLY-run failed with `cannot commit - no transaction is active`. Replaced all 3 with `execute()` chains. Migration re-ran clean in ~190ms.

Sibling gotchas:
- DDL statements like `CREATE TABLE` / `ALTER TABLE` are transactional in SQLite (unlike older MySQL).
- `conn.execute("PRAGMA …")` for some PRAGMAs (e.g. `journal_mode`) also implicit-commits — check the [PRAGMA list](https://www.sqlite.org/pragma.html).
- The Python sqlite3 module's `isolation_level=None` is correctly called "autocommit" mode, but is distinct from the SQLite C API's autocommit — the Python wrapper still adds implicit-commit-before-DDL behavior on `executescript`.

## Related

- [[mgclient-autocommit-silent-rollback]] — similar but inverse pattern in Memgraph Python driver
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — original incident
