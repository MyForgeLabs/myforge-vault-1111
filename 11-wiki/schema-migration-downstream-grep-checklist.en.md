---
name: Schema-migration downstream-grep checklist
type: wiki
created: 2026-05-19
updated: 2026-05-20
tags: ["#type/wiki", "#concept/database", "#concept/refactor", "#lang/en"]
---

# Schema-migration: downstream-grep checklist

After a successful schema-change migration (column dropped/renamed/replaced, table restructured), **the migration script's clean exit is NOT proof of system health**. Downstream callers that still reference the old schema will silently break on the next write.

## The bug-pattern

1. The migration runs clean — `ALTER TABLE foo DROP COLUMN bar` succeeds.
2. The migration's own queries use the new schema, so all of its tests pass.
3. Days later, an unrelated workflow tries to `INSERT INTO foo (..., bar, ...)` and crashes with `OperationalError: table foo has no column named bar`.
4. The bug stays silent until a specific call-path triggers it.

## The mandatory checklist (run BEFORE declaring a migration LANDED)

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

The KO-DB hash refactor (`migrate-hash-refactor-2026-05-19.py`) dropped `facts.provenance` and moved it into a `fact_provenance` side-table. The migration ran clean in ~190ms. The migration's own queries worked. The `vault-ko-belief` JOIN-patch was applied. **But `vault-ko-ingest.upsert_fact:321` was still doing `INSERT INTO facts (..., provenance, ...)` against the new schema** — `OperationalError: no column named provenance`. Every new ingest silently broke until a Memgraph Phase-3 subagent caught it.

The fix took five minutes once spotted: add schema-detect via `PRAGMA table_info` and branch into the post-migration path. The detection itself took **hours of confusion** because the original migration's pytest passed.

## Why pytest didn't catch it

The migration shipped with its own pytest (`test_scd2_ingest.py`, 14/14 PASS), but it exercised the **NEW path** (SCD2 supersession) and the **legacy-aware fallback path**. It did NOT exercise the **legacy non-SCD2 `upsert_fact`** path because that was assumed to be back-compat. The back-compat assumption was wrong — the legacy upsert was still writing the dropped column.

## Wider pattern

This is the **"collateral schema-bug"** pattern. The fix is procedural, not technical: **after any schema migration, run a full-codebase grep for the dropped/renamed identifier** and inspect every call-site, even the ones the ADR's "affected callers" list doesn't enumerate.

## 2026-05-20 — 15-victim case study + automation

The 2026-05-19 incident was only the tip of the iceberg. The 2026-05-20 Wave-A systemic downstream-grep uncovered the rest:

| Victim type | Count | Examples |
|---|---:|---|
| Patched READER | 12 | `vault-ko-query`, `vault-ko-anki`, `vault-ko-conflicts-audit`, `vault-ko-decay`, `vault-ko-schema-evolve`, `vault-ko-report`, `vault-entity-trace`, `vault-graph-edge-inference`, `vault-graph-edge-from-facts`, `vault-ko-triangulate`, `vault-explain`, 2× MCP-tool |
| Patched WRITER | 1 | `vault-nb-ingest.upsert_fact` |
| Pre-patched (skip) | 4 | `vault-ko-ingest`, `vault-graph-extract`, `scd2.py`, `vault-ko-belief` |
| Test fixtures (skip) | 2 | `test_scd2_skeleton`, `test_scd2_ingest` |
| **Total silent victims** | **15** | (2 pre-found + 13 latent until the Wave-A subagent-fanout) |

**MCP-tools were broken too** — `vault_ko_mcp.tool_query`, `tool_top_k`, `tool_stats`, and `tool_conflicts` all silently returned errors or empty results on the user-thread. **A silent JSON-error-fallback masked the regression**.

## Automation (post-2026-05-20)

### Tool — `vault-schema-migration-victim-audit`

```
/usr/local/bin/vault-schema-migration-victim-audit [--json] [--quiet] [--print-cron] [--week YYYY-WWNN]
```

- Scans `07-Decisions/` for ADRs whose frontmatter has `migration: true` OR for content-triggers (`DROP COLUMN`, `## Schema change/delta`, "Dropped \`x\` column").
- For each, it extracts the dropped columns and greps the codebase using **qualified-reference matching** (`<table>.<col>` or `<alias>.<col>` via an SQL-alias map).
- Classifies each hit: READER / WRITER / TEST / COMMENT / ALREADY-PATCHED.
- Outputs `06-Audits/schema-migration-victim-audit-YYYY-WWNN.md`.
- Exit 0 = GREEN, exit 2 = RED (any unpatched READER/WRITER).

### Weekly cron (Mon 05:00 UTC)

```
0 5 * * 1 flock -n /tmp/vault-schema-migration-audit.lock vault-schema-migration-victim-audit --quiet \
    || vault-schema-migration-victim-audit > /tmp/audit-fail-mail.txt
```

Deployed 2026-05-20.

### Git pre-commit hook chain

`.git/hooks/pre-commit-schema-migration-watch.sh` — chained from the main `pre-commit` (Layer 3a, before Layer 3 forbidden-targets). It only triggers when an ADR or a `migrate-*.py` file is staged, and it blocks the commit if the audit comes back RED.

### Frontmatter convention

For unambiguous detection, future migration ADRs should include:

```yaml
---
name: ...
type: decision
migration: true
---
```

## Why qualified-classification matters

The first-pass heuristic (bare-word match + 5-line window) returned **46 false-positive READERs** — almost all of them were `scd2.py`-style parameter-passing of a `provenance` variable that legitimately now lives on the new side-table. The fix: **qualified-reference matching only** (`<alias>.<col>` via the SQL-alias map). Final result: 0 false-positives.

The general lesson for schema-migration grep tools: **bare-word grep is too noisy; require SQL-context anchoring**.

## Related

- [[sqlite-executescript-implicit-commit]] — sibling SQLite gotcha from the same migration
- [[subagent-collateral-bug-discovery]] — subagent run-time errors as a bug-finding signal
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — the migration that triggered this learning
- [[../06-Audits/2026-05-20 Wave-A schema-migration-victim sweep (13 silent victims patched)]] — the 2026-05-20 15-victim audit
- [[../06-Audits/schema-migration-victim-audit-2026-W21]] — first weekly audit (GREEN)
