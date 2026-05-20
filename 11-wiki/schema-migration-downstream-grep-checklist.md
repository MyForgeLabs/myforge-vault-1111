---
name: Schema-migration downstream-grep checklist
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#concept/database", "#concept/refactor"]
---

# Schema-migration: downstream-grep checklist

After a successful schema-change migration (column dropped/renamed/replaced, table restructured), **the migration script's clean exit is NOT proof of system health**. Downstream callers that reference the old schema will silently break on next-write.

## The bug-pattern

1. Migration runs clean — `ALTER TABLE foo DROP COLUMN bar` succeeds.
2. The migration's own queries use the new schema → all tests pass.
3. Days later, an unrelated workflow tries to `INSERT INTO foo (..., bar, ...)` → `OperationalError: table foo has no column named bar`.
4. The bug is silent until a specific call-path triggers it.

## The mandatory checklist (run BEFORE declaring migration LANDED)

```bash
# 1. Find every INSERT/UPDATE/SELECT that references the changed table+column
grep -rn "INSERT INTO ${TABLE}\b" .              # all writers
grep -rn "\.${COLUMN}\b\|'${COLUMN}'\|\"${COLUMN}\"" .  # all readers/writers
grep -rn "FROM ${TABLE}\b" .                     # all readers

# 2. For each match, verify it works against the new schema:
#    - Open the file
#    - Trace the SQL string back to the active execution path
#    - Run a smoke-test (small INSERT or SELECT) against the migrated DB

# 3. If schema-detect logic is appropriate (back-compat), add it:
cur = conn.execute("PRAGMA table_info(target_table)")
cols = {row[1] for row in cur.fetchall()}
if "new_column" in cols:
    # post-migration path
else:
    # legacy path
```

## When it bit us (2026-05-19)

The KO-DB hash refactor (`migrate-hash-refactor-2026-05-19.py`) dropped `facts.provenance` and moved it to a `fact_provenance` side-table. The migration ran clean in ~190ms. The migration's own queries worked. The `vault-ko-belief` JOIN-patch was applied. **But `vault-ko-ingest.upsert_fact:321` still did `INSERT INTO facts (..., provenance, ...)` against the new schema** — `OperationalError: no column named provenance`. Every new ingest silently broken until a Memgraph Phase-3 subagent caught it.

The fix took 5 minutes once spotted: add schema-detect via `PRAGMA table_info` + branch to post-migration path. The detection took **hours of confusion** because the original migration's pytest passed.

## Why pytest didn't catch it

The migration had its own pytest (`test_scd2_ingest.py` 14/14 PASS), but it tested the **NEW path** (SCD2 supersession) and the **legacy-aware fallback path**. It did NOT test the **legacy non-SCD2 `upsert_fact`** path because that was assumed back-compat. The back-compat assumption was wrong — the legacy upsert still wrote the dropped column.

## Wider pattern

This is the **"collateral schema-bug"** pattern. The fix is procedural, not technical: **after any schema migration, run a full-codebase grep for the dropped/renamed identifier** and inspect every call-site, even ones the ADR's "affected callers" list doesn't enumerate.

## Related

- [[sqlite-executescript-implicit-commit]] — sibling SQLite gotcha from the same migration
- [[subagent-collateral-bug-discovery]] — subagent run-time errors as bug-finding signal
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — the migration that triggered this learning
