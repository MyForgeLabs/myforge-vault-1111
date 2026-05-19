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

## Kapcsolódó

- [[Crystallization-protocol]] — itt lesz `scd2.insert_with_version` a write-path, ha a B-9 follow-up zöld
- [[append-only-event-log-undo-prune]] — alternatív minta (event-sourcing) ami szintén megfontolásra került
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — eredeti KO-DB schema-döntés
- [[../06-Audits/2026-05-19 Temporal-KG SCD2 skeleton]] — eredeti skeleton-audit (Round 5)
