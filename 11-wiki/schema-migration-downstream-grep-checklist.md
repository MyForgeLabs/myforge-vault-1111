---
name: Schema-migration downstream-grep checklist
type: wiki
created: 2026-05-19
updated: 2026-05-20
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

## 2026-05-20 — 15-victim case study + automation

A 2026-05-19 incidens csak a JÉGHEGY-csúcsa volt. A 2026-05-20-i Wave-A systemic downstream-grep felfedte:

| Victim type | Count | Examples |
|---|---:|---|
| Patcholt READER | 12 | `vault-ko-query`, `vault-ko-anki`, `vault-ko-conflicts-audit`, `vault-ko-decay`, `vault-ko-schema-evolve`, `vault-ko-report`, `vault-entity-trace`, `vault-graph-edge-inference`, `vault-graph-edge-from-facts`, `vault-ko-triangulate`, `vault-explain`, 2× MCP-tool |
| Patcholt WRITER | 1 | `vault-nb-ingest.upsert_fact` |
| Pre-patched (skip) | 4 | `vault-ko-ingest`, `vault-graph-extract`, `scd2.py`, `vault-ko-belief` |
| Test fixtures (skip) | 2 | `test_scd2_skeleton`, `test_scd2_ingest` |
| **Total silent victims** | **15** | (2 pre-found + 13 latent until Wave-A subagent-fanout) |

**MCP-tools were broken too** — `vault_ko_mcp.tool_query`, `tool_top_k`, `tool_stats`, `tool_conflicts` mind silently returned errors/empty results on the user-thread. **Silent JSON-error-fallback masked the regression**.

## Automation (post-2026-05-20)

### Tool — `vault-schema-migration-victim-audit`

```
/usr/local/bin/vault-schema-migration-victim-audit [--json] [--quiet] [--print-cron] [--week YYYY-WWNN]
```

- Scans `07-Decisions/` for ADRs with frontmatter `migration: true` OR content-triggers (`DROP COLUMN`, `## Schema change/delta`, "Dropped \`x\` column").
- For each, extracts dropped columns + greps the codebase using **qualified-reference matching** (`<table>.<col>` or `<alias>.<col>` via SQL-alias map).
- Classifies hits: READER / WRITER / TEST / COMMENT / ALREADY-PATCHED.
- Outputs `06-Audits/schema-migration-victim-audit-YYYY-WWNN.md`.
- Exit 0 = GREEN, exit 2 = RED (any unpatched READER/WRITER).

### Weekly cron (Mon 05:00 UTC)

```
0 5 * * 1 flock -n /tmp/vault-schema-migration-audit.lock vault-schema-migration-victim-audit --quiet \
    || vault-schema-migration-victim-audit > /tmp/audit-fail-mail.txt
```

Telepítve 2026-05-20.

### Git pre-commit hook chain

`.git/hooks/pre-commit-schema-migration-watch.sh` — chained from the main `pre-commit` (Layer 3a, before Layer 3 forbidden-targets). Triggers only when an ADR or `migrate-*.py` is staged. Blocks commit if RED.

### Frontmatter convention

For unambiguous detection, future migration ADRs should have:

```yaml
---
name: ...
type: decision
migration: true
---
```

## Why fixed-classification matters

The first-pass heuristic (bare-word + 5-line window) returned **46 false-positive READERs** — almost all `scd2.py`-style parameter-passing of a `provenance` variable that's now legitimately on the new side-table. The fix: **qualified-reference matching only** (`<alias>.<col>` via SQL-alias map). Final: 0 false-positives.

This is a general lesson for schema-migration grep tools: **bare-word grep is too noisy; require SQL-context anchoring**.

## Related

- [[sqlite-executescript-implicit-commit]] — sibling SQLite gotcha from the same migration
- [[subagent-collateral-bug-discovery]] — subagent run-time errors as bug-finding signal
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — the migration that triggered this learning
- [[../06-Audits/2026-05-20 Wave-A schema-migration-victim sweep (13 silent victims patched)]] — 2026-05-20-i 15-victim audit
- [[../06-Audits/schema-migration-victim-audit-2026-W21]] — first weekly audit (GREEN)
