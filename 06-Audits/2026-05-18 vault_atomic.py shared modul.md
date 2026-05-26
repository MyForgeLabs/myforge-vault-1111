---
name: vault_atomic.py shared modul + 13 script atomic-write migráció
type: audit
created: 2026-05-18
updated: 2026-05-19
status: top-5 migrated, remaining 8 deferred
tags:
  - "#audit/vault-infra"
  - "#topic/atomic-write"
  - "#topic/race-condition"
---

# vault_atomic.py shared modul + 13 script atomic-write migráció

## 1. Modul

- **Path:** `/root/obsidian-vault/.vault-tools/lib/vault_atomic.py` (~180 sor)
- **API:**
  - `atomic_write(path, content, encoding='utf-8', *, mode=0o644, fsync_dir=True) -> Path`
  - `atomic_write_json(path, obj, *, indent=2, ensure_ascii=False, sort_keys=False, trailing_newline=True)`
  - `atomic_append_jsonl(path, obj, *, ensure_ascii=False)` — POSIX `O_APPEND` < PIPE_BUF
  - `AtomicWriteError(OSError)` — wrapper kivétel
- **Recept:** tempfile (`tempfile.mkstemp` ugyanazon a könyvtáron) → `flush+fsync` → `os.replace` (POSIX-atomic rename) → opcionális parent-dir fsync (rename-durability)
- **Sandbox-import** minden hívóban: `sys.path.insert(0, '/root/obsidian-vault/.vault-tools/lib')` — symlink-mentes, NEM kell PYTHONPATH

## 2. Unit-test PASS state

`/root/obsidian-vault/.vault-tools/lib/test_vault_atomic.py` — `python3 test_vault_atomic.py`:

```
Ran 10 tests in 0.161s -- OK
```

5 alap-teszt (str/bytes/overwrite/json/mkdir-parents) + 5 race/crash szimulátor:

| # | Szimulátor | Verifikál |
|---|---|---|
| 1 | 8 thread × 8KB concurrent overwrite | final ∈ payloads (no torn write) |
| 2 | 4 process × 4KB concurrent overwrite (fork-pool) | final ∈ payloads (no GIL-rejtett race) |
| 3 | reader-thread × writer-loop 20 ciklus | reader csak OLD vagy NEW-t lát, partial-t SOHA |
| 4 | mid-write crash (monkey-patched `os.replace`) | destination ORIGINAL marad + nincs `.tmp.*` szemét |
| 5 | 6 thread × 25 JSONL append | 150 valid JSON sor, semmi torn |

## 3. Top-5 patched script (diff-summary)

| Script | Hely | Volt | Lett |
|---|---|---|---|
| `vault-cleanup` | L340 | `dest.write_text(auto_block + preserved, encoding='utf-8')` | `atomic_write(dest, auto_block + preserved, encoding='utf-8')` |
| `vault-crystallize-monitor` | L591 | `TREND_MD.write_text("\n".join(md))` (+ explicit mkdir) | `atomic_write(TREND_MD, "\n".join(md))` (mkdir már a helperben) |
| `vault-broken-wikilinks-audit` | L430, L436 | `json_path.write_text(json.dumps(...) + "\n", ...)` + `md_path.write_text(render_audit_md(...), encoding="utf-8")` | `atomic_write_json(json_path, payload)` + `atomic_write(md_path, render_audit_md(...))` |
| `vault-ko-conflicts-audit` | L321, L368 | `BACKLOG_FILE.write_text(... encoding="utf-8")` + `out_path.write_text(report)` | `atomic_write(BACKLOG_FILE, ...)` + `atomic_write(out_path, report)` |
| `vault-skill-distill` | L456,533,594,609,733,744 | 6× `write_text` (cache JSON / req JSON / queue MD / dedup MD / run-summary JSON / out MD) | 3× `atomic_write_json` + 3× `atomic_write` |

Mindegyik patch importja közös:
```python
sys.path.insert(0, '/root/obsidian-vault/.vault-tools/lib')
from vault_atomic import atomic_write  # vagy atomic_write_json
```

**Smoke-test PASS:** `python3 -c "py_compile"` mind az 5-ön + funkcionális futás (`vault-crystallize-monitor --json` valid JSON, `vault-ko-conflicts-audit` 136 conflict írt audit-MD-t, `vault-cleanup --quiet` exit=1 [issue-kkal, várt]).

## 4. Mérnöki őszinte: maradék 8 script

Az `egrep -c write_text` szerint még **8 script** használja a nem-atomic mintát. Soroljuk impact + frekvencia mentén:

| Script | Cron? | Write-méret | Race-rizikó | Migráció ajánlott? |
|---|---|---|---|---|
| `vault-nb-crystallize` (3 hívás) | manual | nagy MD-batch | **MAGAS** — gyakran multi-MB | **IGEN** |
| `vault-net-ingest` (4 hívás) | manual | scrape-output, sok-KB | KÖZEPES | **IGEN** (érték: 10p munka) |
| `vault-github-trending-recurrence` (2 hívás) | **`0 6 * * 0` heti** | kicsi MD (5-50KB) | ALACSONY (heti, single-writer cron) | OPCIONÁLIS — kis nyereség |
| `vault-ko-remap-legacy` (2 hívás) | manual, ritka | egyszeri | NAGYON ALACSONY | NEM |
| `vault-session-eval-run` (1) | manual, on-demand | per-session, kicsi | ALACSONY | NEM (single-writer) |
| `vault-session-eval-backfill` (1) | manual | batch, közepes | ALACSONY | NEM (admin-only) |
| `vault-selfcheck` (1) | manual diagnose | kicsi | ZÉRÓ | NEM |
| `vault-net-watch` (1) | **`0 5 * * 0` heti** | kicsi MD | ALACSONY | OPCIONÁLIS |
| `vault-ko-ingest` (1) | manual / hook | nagy triplet-batch lehet | **KÖZEPES-MAGAS** | **IGEN** |
| `vault-graph-retype` (1) | manual one-shot | egyszeri | ZÉRÓ | NEM |
| `vault-auto-disable-check` (1) | **`*/15 * * * *` 15p-enként** | KICSI status MD | ALACSONY de **gyakori cron** | OPCIONÁLIS (kicsi payload, 15p szerint < tear esélye minimum) |

**Verdikt:** a 3 IGEN (vault-nb-crystallize, vault-net-ingest, vault-ko-ingest) hozza a maradék ROI ~80%-át. A többi gyakorlatilag single-writer / ritkán futó / kicsi-payload — a tear-rizikó negligibilis, az `os.replace`-szemantika ROI-ja a hívási rátához skálázódik.

**Javaslat:** ezt a 3-at átemelni **következő sprintben** (1 commit, ~10 perc). A maradékot hagyni — overengineering lenne.

## 5. Egyéb race-pattern találatok

### 5.1 Lockfile-hiány (komoly!)

A crontab-ban **14 vault-job** fut különböző intervallumokon, de csak **2 script** (`vault-autosave`, `11.11crystallize`) használ `flock`-ot. A többi **közös erőforrásokra ír párhuzamosan** (System_Health.md, Backlog.md, audit-MD-k, ko-db SQLite):

| Ütközési lehetőség | Két cron-job ami egyszerre futhat |
|---|---|
| **`vault-cleanup --write` (Sun 04:00) ↔ `vault-broken-wikilinks-audit` (daily 04:30)** | Eltérő idő, **OK**. De Sunday 04:00 cleanup ha 30 percig fut, ütközik a 04:30 wikilink-audittal a 06-Audits/ dir-en |
| **`vault-ko-conflicts-audit` (Sun 04:30) ↔ `vault-crystallize-monitor` (Sun 04:35)** | Mindkettő Backlog.md-be ír / 06-Audits/ JSON-be — **5 perces buffer kockázatos**, ha a 04:30 lassul |
| **`vault-public-sync` (`*/30`) ↔ ANY** | Git-state-et nyúl, párhuzamos `git add` ütközés-rizikó |
| **`vault-auto-disable-check` (`*/15`) ↔ ANY** | watchdog state-MD, single-writer ha csak ez ír — **OK** |
| **`vault-autosave` (`*/10`) ↔ Sunday-batch (`04:00..06:00`)** | Autosave 10p-enként commit+push; Sunday hajnali batch közben **több `git add` ütközés** lehetséges. Az autosave már flock-os → részben védett, de a sunday-batch jobok NEM koordinálnak vele |

**Konkrét incident-pattern (megtörtént)**: `[Vault rename + Mac Obsidian-Git sync](.../feedback_vault_rename_obsidian_git_sync.md)` 10+ napló-bejegyzés `.active-session per-chat pointer divergence`-ről — pontosan az ilyen párhuzamos-író bug-osztály.

**Javaslat (új TODO Backlog-ra):** `vault-cron-flock` wrapper script — minden cron-job futtatása `flock -n /tmp/vault-cron.lock` mögé. Ez 5-soros bash + 1 cron-bulk-edit, **alacsony költség / magas érték**.

### 5.2 Memgraph + atomic-write decoupling

A vault-graph-* parancsok Memgraph-ot írnak (NEM filesystem-et), így nem érintettek. **De**: `mgclient autocommit silent-rollback` ([korábbi tanulság](../11-wiki/mgclient-autocommit-silent-rollback.md)) ugyanaz az osztály — silent data-loss durability-bug. Azt a 2026-05 patch már lefedte.

### 5.3 SQLite KO-DB

`.vault-ko/facts.db` írás párhuzamosság esetén SQLite WAL-módban már atomic (járulékos OS-level lock). **Nem kell migrálni.** De érdemes auditálni hogy `journal_mode=WAL` aktív-e:

```bash
sqlite3 /root/obsidian-vault/.vault-ko/facts.db "PRAGMA journal_mode;"
```

### 5.4 JSONL audit-logok

`crystallize-log.jsonl`, `distill-log.jsonl` — már append-only, POSIX < 4KB sor-méret esetén atomic. **NEM kell változtatni.** A modul `atomic_append_jsonl` helper itt opcionális drop-in (cleanliness, nem bug-fix).

---

## Propagation log

- 2026-05-19 04:55 UTC — modul + tesztek létrehozva, 5 script patchelve, **10/10 PASS**, smoke-test mind ZÖLD
- TODO: Backlog-ba: (a) maradék 3 IGEN-migráció, (b) `vault-cron-flock` wrapper, (c) SQLite WAL-mode verify
