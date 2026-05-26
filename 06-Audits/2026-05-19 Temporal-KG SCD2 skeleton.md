---
name: 2026-05-19 Temporal-KG SCD2 skeleton
type: audit
status: skeleton-landed
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "#concept/temporal-kg", "skeleton-first"]
related:
  - "[[../11-wiki/temporal-kg-scd2-pattern]]"
  - "[[../00-Meta/migrations/2026-05-19-scd2-facts.sql]]"
  - "[[2026-05-19 SV new development ideas brainstorm]]"
---

# Temporal-KG SCD2 skeleton (audit)

Brainstorm ötlet **#9** (SV new dev ideas, 2026-05-19) skeleton-first scaffold-ja. A migration **NEM** futott le ma — minden írás synthetic in-memory SQLite ellen ment.

## Mi landolt

| Fájl | Bytes | Szerep |
|---|---:|---|
| `00-Meta/migrations/2026-05-19-scd2-facts.sql` | 6 230 | Transaction-wrapped, REVERSIBLE migration (2 oszlop + 3 index) |
| `.vault-ko/scd2.py` | 10 575 | Python module: 5 helper + 2 dataclass + RO/RW connection-pattern |
| `/usr/local/bin/vault-ko-temporal` | 5 489 | CLI: 5 subcommand (as-of/history/diff/insert/expire), `--json` |
| `.vault-ko/tests/test_scd2_skeleton.py` | 7 369 | 9 pytest case, synthetic DB, **NEM** érinti a prod facts.db-t |
| `11-wiki/temporal-kg-scd2-pattern.md` | 7 281 | Magyar wiki, T-GRAG/STAR-RAG/TG-RAG citation, playbook |
| `06-Audits/2026-05-19 Temporal-KG SCD2 skeleton.md` | (this) | Audit |
| **Total** | **~37 KB** | 6 fájl |

## Smoke-test verdict

```
$ pytest .vault-ko/tests/ -v
.vault-ko/tests/test_scd2_skeleton.py::test_facts_as_of_returns_historical_state PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_facts_as_of_far_future_returns_current PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_facts_as_of_far_past_returns_empty PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_fact_history_returns_all_versions_in_order PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_insert_with_version_closes_prior_live_row PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_insert_with_version_is_idempotent_for_same_triple PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_expire_fact_sets_valid_until PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_expire_fact_raises_when_no_live_row PASSED
.vault-ko/tests/test_scd2_skeleton.py::test_facts_changed_between_returns_correct_diff PASSED

9 passed in 0.14s
```

**Exit code: 0**. Mindegyik scenario zöld: as-of helyes történelmi snapshot, fact_history oldest-first sorrend, insert_with_version supersession + idempotency, expire_fact valid_until-set, diff window-helyesség.

## KO-DB age-distribution (read-only mérés)

```sql
SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM facts;
-- 2026-05-17T12:35:54+00:00 | 2026-05-17 17:55:31 | 13801
```

Per-óra bontás:

| Óra (UTC) | Fact count |
|---|---:|
| 2026-05-17 12 |    834 |
| 2026-05-17 13 |    508 |
| 2026-05-17 16 |  4 347 |
| 2026-05-17 17 |  8 112 |

> [!warning] Unexpected finding
> **A teljes 13 801 fact 4 órás ablakból származik** (2026-05-17 12:35 → 17:55). Ez egyetlen super-session burst eredménye (`vault-ko-ingest --backfill`), nem természetes time-series. Ennek két implikációja a temporal-layer-re:
> 1. A `facts_as_of("2026-05-15")` query üres set-et ad vissza a meglévő tudásra — a backfill `valid_from := created_at` döntés értelemszerűen a 2026-05-17 ablakot replikálja, NEM a megfigyelés tényleges idejét
> 2. A `valid_from`-ot opcionálisan **át lehetne állítani** a `provenance`-ből kinyerhető session-slug első datestamp-jére (pl. `session/2026-05-15-foo` → `2026-05-15`) — ez egy backfill-tuning lépés a migration `UPDATE`-jében. **Follow-up opció**, nem default

## Migration ETA

13 801 row + 3 új index. SQLite WAL módban, 5.9 MB DB. Becsült futási idő:

- `ALTER TABLE ADD COLUMN` × 2 → instant (metadata-only, ~ms)
- `UPDATE … SET valid_from = created_at` 13.8K row → ~200-500 ms
- `CREATE INDEX` × 3 → ~50-100 ms / index a row-számon

**Összesen: < 2 sec end-to-end**, jól belül a 30 sec budget-ben. A migration-block alig érzékelhető.

## Open follow-ups a tényleges migration-futás előtt

1. **UNIQUE(hash) constraint feloldása** — a jelenlegi schema egy hash-re egy row-t enged. SCD2 multi-version storage incompatible vele. A migration `0_scd2-facts.sql` ezt **nem** rendezi — Phase 2 cut-over (table-rebuild) szükséges, mielőtt `insert_with_version` éles lehetne. Skeleton-szinten OK, mert csak backfill történik
2. **`valid_from` semantic-tuning** — opt-in: ha a backfill-stratégia a `provenance`-ből parse-olja a session-datestamp-et, az age-distribution realisztikus időtengelyt kap (lásd unexpected finding fent). Külön ADR-t igényel
3. **`vault-ko-query` és `vault-ko-conflicts-audit` integráció** — mindkettő `LIKE` query-ket fut a `facts` táblán. Migration UTÁN automatikusan a live-only set-et lássák: `WHERE valid_until IS NULL` clause hozzáadása minden SELECT-hez. CLI-flag (`--at <ts>`) az időutazáshoz
4. **`crystallize` pipeline cut-over** — a `vault-ko-ingest` jelenleg `INSERT OR IGNORE` mintán fut. Mutation cut-over után `scd2.insert_with_version()`-re kell váltani — superseded fact-ek természetes lecsengést kapnak ahelyett, hogy silent-update-elnénk
5. **Memgraph mirror** — a B-2 layer entity-it időbélyegezni kell, ha a temporal-layer a graph-side-on is élesedik. Külön sprint; nem blokkolja az SQLite-only-t
6. **`vault-ko-temporal` CLI dogfood** — jelenleg `--help` smoke-test-en kívül nem érintette éles DB-t. A migration után érdemes egy quick-run sequence-cel verifikálni (`as-of` × ma + `history` × ismert subject + `diff` × elmúlt 24h)

## Verdict

Skeleton-first **kész**. Switch flip-eléséhez (a tényleges migration-futáshoz) a user explicit "go"-jára várunk. A 6 fájl együtt ~37 KB, plain-Python, $0 external dep (csak stdlib + pytest).

## Kapcsolódó

- [[../11-wiki/temporal-kg-scd2-pattern]]
- [[../00-Meta/migrations/2026-05-19-scd2-facts.sql]]
- [[2026-05-19 SV new development ideas brainstorm]]
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]]
