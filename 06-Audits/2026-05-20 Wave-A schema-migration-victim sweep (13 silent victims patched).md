---
name: Wave-A schema-migration-victim sweep — 13 silent #34 victims patched
type: audit
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/audit", "#project/sv", "schema-migration", "downstream-victims", "p0-fix", "wave-a"]
status: 13 silent downstream-victims patched + verified, 0 broken remaining in scope
---

# Wave-A schema-migration-victim sweep — 13 silent #34 victims patched

## TL;DR

Subagent-fanout `grep`-pass a #34 KO-DB hash-refactor (2026-05-19) **csendes downstream-victim**-jeire fókuszálva. Eredmény: a 2 előzetes-patcholt fájl (`vault-ko-ingest`, `vault-graph-extract`) mellett **további 13 fájl is csendben broken volt** — 12 READER + 1 WRITER. Mind javítva a canonical post-#34 schema-detect + `GROUP_CONCAT(fp.provenance, '||')` JOIN pattern-nel. **16 smoke-test PASS**, 0 broken downstream-caller marad. **Wider lesson**: a 2026-05-19-i [[../11-wiki/schema-migration-downstream-grep-checklist]] wiki HETI cron-ra való kiterjesztése kötelező.

## Audit-scope

Scanned: ~70 fájl 9 directory-ban:
- `.vault-ko/` (KO-DB scripts)
- `.vault-graph/` (graph extraction)
- `.vault-memory/` (memory layer)
- `.vault-eval/` (eval scripts)
- `.vault-nb/` (NotebookLM integration)
- `.vault-mcp/` (MCP server)
- `.vault-tools/`
- `.vault-selfcheck/`
- `/usr/local/bin/vault-*` (CLI symlinks, followed)
- `/root/.claude/skills/` (skill-shipped scripts)

Patterns grep-elve:
- `provenance FROM facts`
- `SELECT.*provenance.*facts`
- `INSERT INTO facts.*provenance`
- `facts.provenance` (column reference)
- `r["provenance"]`, `row["provenance"]`, `fact["provenance"]` (row-dict reads)

References found: **24 line 14 distinct fájlban**.

## Patched READERs (12, verified ✓)

| File | Path | Functions patched | Smoke-test |
|---|---|---|---|
| `vault-ko-query` | `/usr/local/bin/` | `query_facts`, `stats`, `top_k_subjects`, `co_occurrence`, `find_conflicts` (5 functions) | PASS (15835 facts, 173 sources) |
| `vault-ko-anki` | `/usr/local/bin/` | `fetch_candidates` (JOIN + correlated subquery) | PASS (2 cards) |
| `vault-ko-conflicts-audit` | `/usr/local/bin/` | `fetch_high_density_subjects`, `find_conflicts_exact` | PASS (170 conflicts) |
| `vault-ko-decay` | `/usr/local/bin/` | `top_k_decayed` (JOIN + GROUP_CONCAT) | PASS |
| `vault-ko-schema-evolve` | `/usr/local/bin/` | `predicate_frequencies` | PASS (138 predicates) |
| `vault-ko-report` | `/usr/local/bin/` | `kodb_summary` | PASS (kodb_summary fixed) |
| `vault-entity-trace` | `/usr/local/bin/` | `ko_db_trace` (one row per fact-prov pair) | PASS (150 facts) |
| `vault-graph-edge-inference` | `/usr/local/bin/` | `load_ko_subject_sources` | PASS (718 candidates) |
| `vault-graph-edge-from-facts` | `/usr/local/bin/` | `fetch_candidate_facts` | PASS |
| `vault-ko-triangulate.py` | `.vault-ko/scripts/` | `fetch_facts`, `string_corroboration_count` (+`_is_post34()` helper) | PASS (score 0.67) |
| `vault-explain.py` | `.vault-memory/scripts/` | `ko_corroboration_for_subject` | PASS (trace) |
| `vault_ko_mcp.py` | `.vault-ko/mcp-server/` | `tool_query`, `tool_stats`, `tool_conflicts`, `tool_top_k` (4 tools) | PASS in-process |
| `vault_mcp_server.py` | `.vault-mcp/` | `tool_ko_query`, `tool_ko_top_k` (2 tools) | PASS in-process |

## Patched WRITER (1, verified ✓)

| File | Function | Pattern |
|---|---|---|
| `vault-nb-ingest.py` (`.vault-nb/scripts/`) | `upsert_fact:642` | INSERT facts (no provenance) + INSERT OR IGNORE fact_provenance + UPDATE provenance_count |

## Already-patched (skipped)

- `vault-ko-ingest.py:upsert_fact` (2026-05-19 PM, by SCD2 subagent)
- `vault-graph-extract.py:load_facts` (2026-05-20 AM)
- `vault-ko/scd2.py` (built-in schema-detect)
- `vault-ko-belief.py:fetch_pair_facts` (originally JOIN-aware)

## Flagged (NOT patched per rules)

- `tests/test_scd2_skeleton.py:82` — test fixture explicitly creates legacy schema
- `tests/test_scd2_ingest.py:89` — test fixture queries pre-migration shape
- `migrate-hash-refactor-2026-05-19.py` — explicitly targets schema versions (DO-NOT-TOUCH)
- `vault-ko-report --last` — **pre-existing** `KeyError: 'session_slug'` (NEM provenance-related, separate bug)

## Canonical patch pattern

```python
# Schema-detect: post-#34 (2026-05-19) drops `facts.provenance`; provenance
# lives in side-table `fact_provenance`. GROUP_CONCAT keeps 1 row per fact
# with `||`-joined provenance string.
cols = {r[1] for r in conn.execute("PRAGMA table_info(facts)").fetchall()}
has_pv_table = bool(conn.execute(
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fact_provenance'"
).fetchone())
post34 = "provenance" not in cols and has_pv_table

if post34:
    cur.execute(
        """SELECT f.hash, f.subject, f.predicate, f.object, f.confidence,
                  COALESCE(GROUP_CONCAT(fp.provenance, '||'), '') AS provenance,
                  f.source_type
           FROM facts f
           LEFT JOIN fact_provenance fp ON fp.fact_hash = f.hash
           GROUP BY f.hash"""
    )
else:
    cur.execute("<original-legacy-query>")
```

**Top-K corroboration optimization**: ahol nincs szükség a teljes provenance-listára, használjuk `MAX(provenance_count)` denormalizált oszlopot a `facts`-on (gyorsabb mint a GROUP_CONCAT).

## Surprising findings

1. **15 silent victim összesen a #34 után** — 2 + 13 — ezekből 11 vault-CLI a vault napi rutinos working flow-jának része (`vault-ko-query`, `vault-explain`, `vault-entity-trace`, MCP-tool-ok, stb.). A `vault-ko-query --stats` is broken volt, ami **a vault-meta dashboard-jának fő-számára számít**. A felhasználó NEM észlelhette napokig (silent SQLite OperationalError egyes ritkán futtatott CLI-ken).

2. **A `2026-05-19` Phase-3 result audit `vault-ko-ingest.upsert_fact` finding-ja csak a JÉGHEGY-csúcsa volt** — a wider grep-pass 14× több victim-et fedezett fel. **Wider lesson**: schema-migration audit-ban NEM elég megnevezni 1-2 direct caller-t — heti automatikus grep-pass kötelező.

3. **MCP-tool-ok is broken voltak** — `vault_ko_mcp.tool_query`, `tool_top_k`, `tool_stats`, `tool_conflicts` mind broken. Ezeken keresztül a user-facing Claude Code agent érte el a KO-DB-t, és ezek **csendben hibáztak** a #34 óta. **Risk**: a user-thread NEM kapott explicit error-feedback-et, csak `{"results": [], "error": "..."}`-stílust.

4. **Single subagent ~13 min wall-clock** 13 fájl bulk-patch-elésére, 16 smoke-test futtatásával. $0 cost. **Wave-based subagent-fanout NEM kell ennyihez** — single thorough subagent is elég volt.

## Wider lessons (propagation candidates)

### Lesson 1: heti cron `vault-schema-migration-victim-audit`

```bash
# Új CLI proposal:
vault-schema-migration-victim-audit
# - Reads all ADRs from 07-Decisions/ with `migration:` or `schema-change:` frontmatter
# - For each, extracts dropped/renamed columns
# - Greps the entire codebase for SELECT/INSERT references
# - Reports broken files + suggested patch pattern
```

Cron entry:
```
0 5 * * 1 flock -n /tmp/vault-schema-migration-audit.lock vault-schema-migration-victim-audit --weekly
```

### Lesson 2: git pre-commit hook

Ha `.vault-ko/scripts/migrate-*.py` vagy `.vault-ko/schema.sql` változik, a hook **automatikusan** futtassa a downstream-grep-et és vegye blokkoló-listára a commit-ot, amíg minden grep-hit explicit `# post-XX: schema-aware` annotation-tel nem rendelkezik.

### Lesson 3: schema-migration-checklist wiki expansion

Az [[../11-wiki/schema-migration-downstream-grep-checklist]] wiki update-elendő:
- Hozzáadni a **15-broken-victim case study**-t mint empirical evidence
- Hozzáadni az **MCP-tool-blind-spot** finding-et (silent JSON-error-fallback)
- Hozzáadni az **automated cron audit + pre-commit hook** ajánlást

## Status

🟢 **LANDED** — 13 fájl patcholva, 16 smoke-test PASS, 0 broken downstream-caller marad a scope-ban.

## Related

- [[2026-05-19 KO-DB hash key — drop provenance from hash]] — #34 ADR (regression-source)
- [[2026-05-19 Memgraph Phase-3 re-extract result]] — `upsert_fact` #1 P0-fix (előzetes lökés)
- [[2026-05-20 Phase-3 re-extract execution + downstream P0 patch]] — `vault-graph-extract` #2 P0-fix
- [[../11-wiki/schema-migration-downstream-grep-checklist]] — wider-lesson wiki (heti cron + pre-commit hook expansion)
- [[../11-wiki/subagent-collateral-bug-discovery]] — subagent-run-time error pattern (egyetlen subagent fedte fel az 13 csendes victim-et)
