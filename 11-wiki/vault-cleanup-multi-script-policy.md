---
name: Vault-cleanup multi-script policy
type: wiki
tags: ["#type/wiki", "vault", "cron", "scripts", "ops", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Vault-cleanup multi-script policy

## TL;DR

A vault egészségét ~10+ `vault-*` script tartja karban (autosave, cleanup, audit, conflict-detection, stuck-detection, coherence-check). Közös pattern-jeik: **idempotent overwrite, threshold-alert exit-code, JSON+MD dual-output, cron-friendly env-var override, auto-disable min-volume guard**. Ütemezés override-protected (Sun 04:00 vault-cleanup → 04:45 broken-wikilinks → 04:50 ko-conflicts → 05:00 crystallize-health). A scriptek **egymásra építenek** (post-cleanup audit-scripteket futtat), így a sorrendisége nem véletlen.

## Háttér

A B-3 (vault-coherence) és B-7 (entity-graph) sprintek bevezetése előtt a vault-karbantartás 1 script-tel ment: `vault-cleanup` heti vasárnap. Ahogy a vault növekedett (~3K MD-fájl, 13K+ KO-DB fact, 9K Memgraph entity), a single-script-pattern nem skálázott:

- A `vault-cleanup` 30+ perces futás-időt vett fel
- Different concerns (broken-links, conflict-audit, stuck-detection) eltérő rate-en kell futtatni
- Failure-cascade — ha egy lépés elhasal, a többi blokkolódik

Megoldás: **script-családra bontás + cron-orchestration**. Mind külön logolnak, mind külön failik (no-cascade), és az output-jukat ugyanaz a `06-Audits/System_Health.md` aggregálja.

## Cron-mátrix (ratify-ed 2026-05-17)

| Script | Frequency | Time (HU) | Layer |
|---|---|---|---|
| `vault-autosave` | 10 perc | continuous | persist |
| `vault-stuck-detect` | daily | 03:00 | health |
| `vault-coherence-check` | daily | 03:30 | health |
| `vault-cleanup` | weekly | Sun 04:00 | structural |
| `vault-broken-wikilinks-audit --audit-md` | weekly | Sun 04:45 | integrity |
| `vault-ko-conflicts-audit` | weekly | Sun 04:50 | KO-DB |
| `vault-crystallize-monitor` | weekly | Sun 05:00 | crystallize |
| `vault-orphan-wiki` | weekly | Sun 05:10 | integrity |
| `vault-graph-extract` | weekly | Sun 05:20 | B-7 entity-graph |
| `vault-embed-freshness` | weekly | Sun 05:30 | B-2 semantic |

## Közös pattern-ek

### 1. Idempotent overwrite

Minden script `06-Audits/<topic>-YYYY-MM-DD.json` + `<topic>-latest.md` outputot ír. Same-day re-run **felülír**, nem duplikál. Multi-day archívum a JSON-okban marad.

### 2. Threshold-alert exit-code

```bash
# inside script
if (( delta_broken_targets > 20 )); then
  echo "REGRESSION: +$delta_broken_targets broken targets"
  exit 1
fi
```

Cron-email-elhető: ha exit 1 → MTA delivery to user → manual review. Exit 0 = "all clear, no action needed".

### 3. JSON + MD dual-output

- **JSON** — machine-readable, downstream automation (System_Health aggregátor)
- **MD** — human-readable, Obsidian-rendelhető, frontmatter + táblázat

### 4. Cron-friendly env-var override

```
VAULT_ROOT=/root/obsidian-vault SCORER=claude-code vault-crystallize-monitor --weeks 4
```

NEM hardcoded path-ok, NEM hardcoded scorer — minden override-elhető. Defaults sensible.

### 5. Auto-disable min-volume guard

Smoketest-noise → false-positive cascade védelem. Példa: ha total facts < 1000 → SKIP (`vault-ko-conflicts-audit`). Részletek: [[auto-disable-min-volume-guard]].

### 6. Audit-event log

Minden script `/root/.vault-config/audit-log.jsonl` JSON-line-ba ír: timestamp, script-name, exit-code, output-path. Debug-céllal cross-script timeline reconstruál-ható.

## Anti-pattern

- **Single mega-script** — failure-cascade, hard-to-debug, slow
- **Cron-overlap** — két script ugyanabban a percben írja az SQLite-ot → lock-contention
- **Hardcoded path** — minden vault-rename / restructure tönkreteszi a scriptet
- **No idempotency** — re-run duplicate-content vagy reset-old
- **Silent failure** — exit 0 mindig, így a cron-email-monitoring vakká válik
- **No audit-event** — debugger nem tudja rekonstruálni mi-mikor futott

## Reusable szabályok

1. **Cron-rend mindig +5-10 perc gap** — overlap-kerülés
2. **Idempotent overwrite default** — `<topic>-latest.{json,md}` symlink frissül
3. **Threshold-alert delta-based** — NEM absolute count, hanem prev-vs-current delta
4. **Audit-event minden script-ben** — `audit-log.jsonl` append
5. **Env-var override + sensible default** — `VAULT_ROOT`, `SCORER`, `WEEKS`, stb.
6. **Min-volume guard** — corruption/restart utáni false-positive elkerülése
7. **System_Health.md aggregátor** — minden script-output egy helyen összegezve, heti regenerálás
8. **Failure NEM kaszkádolódik** — script B nem függ A success-én, csak A outputjának létezésén

## Buktatók

- A `vault-autosave` cron continuous (10 perc) — git lock-contention ha vault-cleanup is fut → cleanup szerezzen acquire-lock-ot ELŐSZÖR
- Memgraph-cluster restart utáni `vault-graph-*` scriptek false-empty-result-tal exit 1-elnek; `--allow-empty` flag kell ramp-up alatt
- A `vault-stuck-detect` daily run dump-olja az "elfelejtett" session-eket; ha hosszú multi-day session fut, false-positive lesz → exclude-list configolható
- Cron-time-zone — szerver UTC vagy CET? Mindig explicit `TZ=Europe/Budapest` a crontab-on

## Kapcsolódó

- [[auto-disable-min-volume-guard]] — false-positive guard
- [[mgclient-autocommit-silent-rollback]] — Memgraph quirks
- [[../05-Memory/Infrastructure]] — script-listák, host-info
- [[../06-Audits/System_Health]] — aggregátor
- [[wikilink-importer-pattern]] — broken-link sub-audit
- [[vault-ko-conflicts-audit-design]] — conflict sub-audit
- [[crystallize-health]] — crystallize-monitor output
- [[vault-corruption-detection-pattern]] — szélesebb integritás
