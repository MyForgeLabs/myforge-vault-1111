---
name: temporal-kg-scd2-pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#project/sv", "#concept/knowledge-graph", "#concept/temporal-rag"]
related:
  - "[[../00-Meta/migrations/2026-05-19-scd2-facts.sql]]"
  - "[[../06-Audits/2026-05-19 Temporal-KG SCD2 skeleton]]"
  - "[[../06-Audits/2026-05-19 SV new development ideas brainstorm]]"
---

# Temporal-KG SCD2 minta

A KO-DB (`/root/obsidian-vault/.vault-ko/facts.db`) jelenleg point-in-time tudást tárol: minden fact "most" igaz vagy nincs sehol. Ez a minta a klasszikus data warehouse SCD2-t (Slowly Changing Dimensions Type 2) adoptálja, hogy a vault tudása **időben követhető** legyen — például *"mit tudtam a Memgraph keepalive-ról 2026-05-15-én?"*.

## Mi a Type 2

SCD2 ≈ a fact-soron két extra oszlop:

- `valid_from` — mikor lett először megfigyelve (UTC ISO-8601)
- `valid_until` — mikor lett "lecserélve". `NULL` = jelenleg érvényes

Update-elés helyett a régi sor `valid_until = NOW`-ra zár, az új tartalom egy frissen beszúrt sor `valid_from = NOW, valid_until = NULL`-lal. Két query-shape:

```sql
-- "Most élő" tudás (hot path)
WHERE valid_until IS NULL

-- "Mi volt a tudás :ts időben"
WHERE valid_from <= :ts AND (valid_until IS NULL OR valid_until > :ts)
```

## Miért SCD2, és miért nem valami más

| Alternatíva | Mikor jobb | Miért NEM most |
|---|---|---|
| **Bitemporal** (valid + transaction time, két idő-tengely) | Audit-szigorú rendszerek, "mit tudtunk akkor és most" külön kérdés | Overkill — két idő-tengely 4 timestamp + sok kombinatorikus query. A vault csak `observation time`-ot tárol, a `transaction time` ≈ `valid_from` |
| **Append-only event-log** (immutable insert + materialized view) | Eseményvezérelt rendszerek, replay-igény | Nincs natív "live state" view — minden olvasáshoz aggregáció kell. Nálunk 13.8K fact-on most még olcsó, de a KO-DB-t kis SQLite-on tartjuk |
| **Snapshot isolation** (timestamped full table-copy) | Ritka, batch-elt frissítés | Storage-pazarló. Heti 1500-2000 új fact = heti teljes másolat |
| **Event-sourcing** (CRUD → log + projection) | Üzleti tranzakciók, undo/redo | Komplex projektor-réteg. SCD2 a "minimum viable temporal" |

A 2026-os RAG-irodalom (T-GRAG, STAR-RAG, TG-RAG) ugyanezt csinálja, csak gráf-szinten: timestamped relations + temporal query decomposition. Nálunk most az egyszerű relational SCD2 elég — a Memgraph-réteg külön kezeli a graph-temporality-t később (B-8 RSI Tier-3 follow-up).

## A 2-oszlopos schema

```sql
ALTER TABLE facts ADD COLUMN valid_from  TIMESTAMP;
ALTER TABLE facts ADD COLUMN valid_until TIMESTAMP;

-- Hot path: live-only query-k a vault-ko-query/conflicts-audit-ból
CREATE INDEX idx_facts_valid_current
    ON facts(subject, predicate) WHERE valid_until IS NULL;

-- Range scan: as-of és diff query-k
CREATE INDEX idx_facts_valid_range
    ON facts(valid_from, valid_until);

-- Subject + as-of: "mit tudtam X-ről akkor"
CREATE INDEX idx_facts_subject_valid_from
    ON facts(subject, valid_from);
```

A migration script: [[../00-Meta/migrations/2026-05-19-scd2-facts.sql]]. Tranzakció-wrappelt, REVERSIBLE (SQLite 3.35+ DROP COLUMN-nal).

## Három fő query-alak

### 1. As-of (időpont)

```py
from scd2 import facts_as_of
rows = facts_as_of("2026-05-15T12:00:00Z", subject="Memgraph")
```

Visszaadja azt a fact-state-et, ami `2026-05-15T12:00Z`-kor élt. Akkor is, ha azóta superseded.

### 2. History (subject + predicate idővonal)

```py
from scd2 import fact_history
versions = fact_history("Memgraph", "supports")
# [cypher-only (2026-05-10 → 2026-05-12),
#  vector-search-numpy (2026-05-12 → 2026-05-17),
#  native-vector-index (2026-05-17 → NULL)]
```

Minden verzió oldest-first. A live row az utolsó, ahol `valid_until IS NULL`.

### 3. Diff (időablak)

```py
from scd2 import facts_changed_between
diff = facts_changed_between("2026-05-15T00:00Z", "2026-05-17T00:00Z")
# diff.added   — valid_from a window-ban
# diff.expired — valid_until a window-ban
```

Tipikus use case: heti retrospektív, "mi változott a vault-tudásban az elmúlt 7 napban".

## Migration playbook

A skeleton (2026-05-19) **NEM futtatja** a migrationt — az csak akkor megy le, ha kifejezetten kérve. A go-live checklist:

1. **Backup:** `cp facts.db facts.db.bak-$(date +%Y%m%d-%H%M)` — 5.9 MB, < 1 sec
2. **Dry-run a backup-on:** `sqlite3 facts.db.bak ".read 00-Meta/migrations/2026-05-19-scd2-facts.sql"` → verify schema + row-counts
3. **UNIQUE(hash) constraint-et el kell engedni** a `facts` táblán, mielőtt élesben SCD2-zünk — multi-version storage ütközik vele. Ez egy table-rebuild lépés (CREATE NEW → INSERT SELECT → DROP OLD → RENAME). A migration script ezt **nem** tartalmazza, mert a backfill önmagában safe; a constraint-drop a Phase 2 mutation cut-over része
4. **Élesben futtatás:** ugyanazzal a `.read` paranccsal, becsült ETA < 30 sec 13.8K row-n
5. **Verifikáció:** `PRAGMA table_info(facts)` és `SELECT COUNT(*) FROM facts WHERE valid_until IS NULL` (= total row-count) és `.indexes facts` (= 7 index)
6. **Roll back ha kell:** lásd a SQL fájl alján a `ROLLBACK` szekciót

A `vault-ko-ingest` és `crystallize` pipeline-ok mostani `INSERT OR IGNORE` viselkedését **NEM töri** a migration — a backfill miatt minden meglévő row `valid_until IS NULL`-ra esik, és a régi kód csak ezeket látja. A `scd2.insert_with_version()` opt-in path, később váltunk át rá.

## Limitációk

- **Schema-szintű időutazás van, semantic-szintű nincs.** Ha egy predikátum jelentése változik időben (pl. `supports` előbb "elv" most "implementált"), a fact literal-string-je nem reflektálja. T-GRAG erre temporal-aware predicate-canonicalization-t használ; nálunk Phase B-9 follow-up
- **`UNIQUE(hash)` ütközés.** A jelenlegi schema egy hash-re egy row-t enged, ami SCD2-ben tilos (több version = több row ugyanazzal a `(subject,predicate,object)`-tel csak akkor lehet, ha legalább egy attribútum eltér — pl. `confidence`). A go-live előtt a constraint-et drop-olni kell vagy a hash-be bele kell venni a `valid_from`-ot
- **Időzónák.** Minden timestamp UTC. Lokális idő-konverzió a CLI/UI rétegben történjen
- **Nincs cascade-delete a propagation_log-ból.** Ha SCD2-vel "expire"-elünk egy fact-et, a `propagation_log` rekordok megmaradnak — ez szándékos (audit-trail), de a downstream consumerek kell hogy stale-aware-ek legyenek

## Hivatkozások

- **T-GRAG** (Dynamic GraphRAG for temporal conflicts) — [arxiv:2508.01680](https://arxiv.org/abs/2508.01680)
- **STAR-RAG** (Temporal RAG via Graph Summarization) — [arxiv:2510.16715](https://arxiv.org/abs/2510.16715)
- **TG-RAG** (Time-Sensitive RAG, Temporal Graphs) — [arxiv:2510.13590](https://arxiv.org/abs/2510.13590)
- Kimball: *The Data Warehouse Toolkit* — SCD Type 2 az alap

## 2026-05-19 — migráció EXECUTED on real `facts.db`

A skeleton-first ETA "<2 sec" konzervatív volt **20×-osan**. A tényleges futás:

```
$ time sqlite3 -bail /root/obsidian-vault/.vault-ko/facts.db \
    < /root/obsidian-vault/00-Meta/migrations/2026-05-19-scd2-facts.sql
real    0m0.093s
user    0m0.032s
sys     0m0.048s
Exit: 0
```

**93 milliszekundum** mindössze a következőkre:

1. `ALTER TABLE ADD COLUMN valid_from` (metadata-only, ~ms)
2. `ALTER TABLE ADD COLUMN valid_until` (metadata-only, ~ms)
3. `UPDATE facts SET valid_from = created_at WHERE valid_from IS NULL` (13,801 rows)
4. Sanity-check temp-table + CHECK constraint
5. 3 `CREATE INDEX`: compound `(valid_from, valid_until)` + partial `WHERE valid_until IS NULL` + composite `(subject, valid_from)`

**Wider lesson**: SQLite schema-evolution **nem rate-limit a normál-méretű KO-DB-knél**. 13,801 row + 2 column + 3 index < 100ms. Ne becsüld túl a migration-időt single-digit-K row-szám esetén. A "skeleton-first ETA <2s" konzervatív tervezés volt — a valódi cost ~20×-osan kisebb. Production-grade gyorsság.

Post-migration verification (`vault-ko-temporal as-of`):

```
$ vault-ko-temporal as-of "2026-05-19T11:03:13Z" --subject "Memgraph"
Facts valid as of 2026-05-19T11:03:13Z:
  · #13588  Memgraph | has_count | 977 chunks  from=2026-05-17T17:32:54  until=—
  · #12804  Memgraph | produces | beépített vector-search  from=2026-05-17T17:30:44  until=—
  ...

$ vault-ko-temporal as-of "2026-05-15T00:00:00Z" --subject "Memgraph"
Facts valid as of 2026-05-15T00:00:00Z:
  (no rows)
```

A pre-ingest dátum **helyesen üres** → time-travel queries ÉLES.

## 2026-05-19 EXECUTED — `_scd2_insert_or_supersede` integration

A skeleton-szintű `scd2.insert_with_version` MELLETT most már él egy ingest-path entry-point is, a **brainstorm idea #9** szerinti 3-osztályú konfliktus-kezeléssel:

```py
from scd2 import scd2_insert_or_supersede

result = scd2_insert_or_supersede(
    "Memgraph", "uses_algorithm", "native-vector-index",
    provenance="11-wiki/memgraph-ce-feature-limits.md",
    source_type="wiki",
    confidence=0.95,
)
# result.action ∈ {"insert", "supersede", "noop", "skip"}
```

### Patched fájlok (2026-05-19)

| Fájl | LOC delta | Mit változott |
|---|---|---|
| `/root/obsidian-vault/.vault-ko/scd2.py` | +~270 | `SupersessionResult` dataclass + `scd2_insert_or_supersede` + `_insert_provenance_row` + `_insert_new_fact_row` + schema-feature detect + log-skipped helper |
| `/root/obsidian-vault/.vault-ko/scripts/vault-ko-ingest.py` | +~75 | `VAULT_KO_SCD2_ACTIVE` env-gate + `_scd2_insert_or_supersede(fact)` wrapper + `ingest_file` SCD2-aware counter logic |
| `/usr/local/bin/11.11crystallize` | +30 / -10 | `lookup_kodb_context` schema-agnostic read (post-#34 `fact_provenance` table támogatás) + docstring note hogy ITT nincs fact-INSERT, csak read |
| `/root/obsidian-vault/.vault-ko/tests/test_scd2_ingest.py` | új, ~230 sor | 5 új pytest (insert / noop / supersede / skip / wrapper) |

### Conflict-osztályozás (3+1 osztály)

A `scd2_insert_or_supersede` minden új `(s, p, o)` tripletre 4 ágra fut:

1. **Identical no-op** (`action="noop"`). Live `(s, p, o)` row létezik (`hash` match + `valid_until IS NULL`). Action: **NEM** új facts-row; CSAK `fact_provenance` insert új (`provenance`, `source_type`)-pal. Ez a **cross-source corroboration** path — több source ugyanazt mondja, mindegyik bekerül a provenance-táblába, és a `provenance_count` ennek tükre lesz a `vault-ko-query --top-k` ranking-ben.
2. **Supersession close-and-replace** (`action="supersede"`). Live `(s, p)` row létezik, de `o` eltér. Action: `UPDATE old SET valid_until = NOW` ÉS `INSERT new row valid_from = NOW, valid_until = NULL`. Ez a klasszikus SCD2-pattern — a `fact_history(s, p)` többé NEM 1-elemű.
3. **New insert** (`action="insert"`). Nincs live `(s, p)` match. Action: standard insert + provenance-row.
4. **Hash-collision skip** (`action="skip"`). A live `UNIQUE(hash)` constraint blokkolja a supersession-t flip-flop esetben (A → B → A). Action: **NO-OP a DB-n** + JSON-line log a `$VAULT_KO_SCD2_LOG_DIR/supersession-skipped.log`-ba (default `/tmp/vault-ko-scd2/`).

### A `UNIQUE(hash)` ütközés és a "Option-X draft-mode"

A migration-prerequisite szakasz (fentebb) **deferred** marad: a `facts.hash` még mindig `UNIQUE NOT NULL`. Ez **csak a flip-flop A → B → A** esetén jelentkezik — a "B" supersedeli az "A"-t, az "A"-row most `valid_until = NOW`, és ha újra "A"-t akarunk insertálni, az `INSERT INTO facts` az ugyanazon hash-en `IntegrityError`-ra fut.

A kód **detektálja előre** (`SELECT id FROM facts WHERE hash = ?`) és **skip-eli** (Option-X). A skip-log production-mode-ban heti-szinten reviewable; ha 10+ skip / hét, az a jel hogy az **Option-Y migration** (UNIQUE(hash) drop + partial-index `WHERE valid_until IS NULL`) érdemes elvégezni.

### Env-flag aktiválás

```bash
# Per-shell, opt-in:
export VAULT_KO_SCD2_ACTIVE=1

# vagy CLI-szintű:
VAULT_KO_SCD2_ACTIVE=1 vault-ko-ingest --backfill 11-wiki/

# Opcionális log-dir override:
export VAULT_KO_SCD2_LOG_DIR=/root/obsidian-vault/06-Audits/scd2-skipped
```

A default `OFF`: existing 13,801-row ingest-flow változatlan, amíg explicit nincs flag.

### Test státusz

```
$ pytest .vault-ko/tests/ -x -v
========== 14 passed in 0.46s ==========
  · 5 ÚJ:  test_scd2_ingest.py
  · 9 LEGACY: test_scd2_skeleton.py — regression-zero
```

### Critical edge-case-ek (3+1)

1. **`fact_provenance` PK duplicate** — ugyanaz a `(fact_hash, provenance)` második-ingest nem hiba: a `_insert_provenance_row` `IntegrityError`-t fog és `False`-t ad vissza. Caller-szempontból `provenance_added=False` jelzi.
2. **Race a precheck és insert között** — két párhuzamos ingest ugyanazt a `(s, p, o)`-t küldené supersession-be ÉS éppen történik egy másik writer. Defensive: az `INSERT INTO facts` `try/except IntegrityError` ágában rollback-eljük a `valid_until` close-t és skip-elünk. Production-kockázat alacsony (SQLite egy-író modell), de tesztben nem kötelező.
3. **`UNIQUE(hash)` collision flip-flop** — fent tárgyalt; `action="skip"`. **Több, mint 10 / hét** = Option-Y migration ETA ~1h (table-rebuild SQLite-on, ~150 ms 13.8K row-n).
4. **Legacy schema (with `provenance` column)** — a `scd2.py` és `lookup_kodb_context` is schema-agnostic; ha `provenance` column létezik (régi DB), azt írja; ha nem (post-#34), a `fact_provenance` side-table-t használja.

### Következő lépés-javaslat

- **Most**: `VAULT_KO_SCD2_ACTIVE=1` a következő live ingest előtt, monitorozni a `supersession-skipped.log`-ot 1-2 hétig.
- **Ha skip-rate < 5 / hét**: maradhat Option-X. Az ad-hoc skip-ek nem érintenek kritikus knowledge-okat.
- **Ha skip-rate ≥ 10 / hét**: Option-Y migration (`migrate-unique-hash-drop-2026-XX-XX.sql`), table-rebuild ~150 ms, partial-index `WHERE valid_until IS NULL` átveszi a uniqueness-garantálást.

## Kapcsolódó

- [[Crystallization-protocol]] — itt lesz `scd2.insert_with_version` a write-path, ha a B-9 follow-up zöld
- [[append-only-event-log-undo-prune]] — alternatív minta (event-sourcing) ami szintén megfontolásra került
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — eredeti KO-DB schema-döntés
- [[../06-Audits/2026-05-19 Temporal-KG SCD2 skeleton]] — eredeti skeleton-audit (Round 5)
- [[../06-Audits/2026-05-19 Wave-2 follow-up designs (SCD2 LongMemEval Critic)]] — Design A SCD2 patch ETA + 3-class conflict-table
