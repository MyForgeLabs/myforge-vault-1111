---
name: 2026-05-19 vault-gh-bridge first APPLY run
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#topic/sv-b-1", "#bridge/gh", "#status/findings"]
---

# vault-gh-bridge — első APPLY-futtatás audit (2026-05-19)

> [!info] Context
> SV `#14 vault-gh-bridge` CLI első APPLY-futtatása `--days 1` window-ban.
> CLI: `/usr/local/bin/vault-gh-bridge` (21KB, 585 LOC)
> Pattern wiki: [[../11-wiki/github-commit-history-ingest-pattern]]

## TL;DR

- **Pre-flight (dry-run):** 10 active repo, 89 commit várt 1-napos window-ban
- **APPLY result:** 10 file írva, 89 commit, 0 error
- **State-file:** `~/.vault-config/gh-bridge-state.json` ÉLES, 1993 byte, 10 entry — content_hash truncated (16 char)
- **Idempotency-test: ⚠️ FAIL** — re-run-onként újraírja a fájlokat mert `generated_at`+`since_iso` minden run-on now-UTC (frontmatter-drift bug)
- **KO-DB ingest:** opt-out (`--ingest-kodb` flag NEM használva) — fájl-only

## Pre-flight check

```
$ gh auth status
✓ Logged in to github.com account PetykaMaki — scopes: repo, workflow, gist, read:org

$ ls /root/obsidian-vault/10-raw/external/github/
(dir nem létezett, CLI létrehozta)

$ vault-gh-bridge --dry-run --days 1
[DRY-RUN] 10 repos, 89 commits (window 1d)
```

## APPLY-run result

| Repo | Commits | File | Status |
|---|---|---|---|
| `PetykaMaki/obsidian-vault` | 86 | `commits-2026-05-19.md` | wrote |
| `PetykaMaki/boulium-web` | 3 | `commits-2026-05-19.md` | wrote |
| `PetykaMaki/agents-skills` | 0 | `commits-2026-05-19.md` | wrote (empty table) |
| `PetykaMaki/obsidian-vault-starter` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| `PetykaMaki/kgc-berles` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| `PetykaMaki/PetykaMaki.github.io` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| `PetykaMaki/kgcshop` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| `PetykaMaki/koko-chatbot` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| `PetykaMaki/MyforgeCore` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| `PetykaMaki/petanque-app` | 0 | `commits-2026-05-19.md` | wrote (empty) |
| **TOTAL** | **89** | **10 files** | 0 errors |

**Inaktív repo-k 1-day window-ban (8):** agents-skills, obsidian-vault-starter, kgc-berles, PetykaMaki.github.io, kgcshop, koko-chatbot, MyforgeCore, petanque-app.

Megjegyzés: az inaktív repo-k is kapnak file-t üres tábla-val (frontmatter `commit_count: 0`). 30-napos backfill-ben több repo lesz aktív (pl. `kgc-berles` 54 commit `--days 30`-ban).

## Output sample (boulium-web)

```yaml
---
name: PetykaMaki__boulium-web-commits-2026-05-19
type: raw
source: github-commits
repo: PetykaMaki/boulium-web
window_days: 1
since_iso: 2026-05-18T17:45:52Z
commit_count: 3
generated_at: 2026-05-19T17:45:52+00:00
created: 2026-05-19
tags: ["#type/raw", "#source/github", "#bridge/gh"]
---
```

| sha7 | author | date | message |
|---|---|---|---|
| `4216ca1` | root | 2026-05-18T19:43:33Z | Match replay UI + avatar mobile-Safari fixes |
| `76ca7ec` | root | 2026-05-18T19:37:28Z | Recurring events 24h push-notif |
| `5319a43` | root | 2026-05-18T19:17:31Z | Friends-MVP foundation + backfill scripts |

Format clean, markdown table valid, frontmatter parse-able.

## State-file

- Path: `/root/.vault-config/gh-bridge-state.json`
- Size: 1993 bytes
- Struktúra: `{"files": {<rel-path>: {"commits": N, "content_hash": "<16char>", "written_at": "<iso>"}}}`
- 10/10 entry consistent a tényleges file SHA-256-prefix-szel közvetlenül a write után.

## Idempotency-test — ⚠️ FAIL

**Várt:** második `--apply` run `[SKIP] file unchanged` minden file-ra.
**Tényleges:** második run minden file-t újraírt, mtime változott, state-file `written_at` minden entry-ben frissült, `content_hash` is változott (`afb5dfd6` → `3b00595b` boulium-web-en).

**Root cause:** `since_iso` és `generated_at` mezők frontmatter-ben **now-UTC** minden run-on, NEM date-anchored (pl. `2026-05-19T00:00:00Z`). Így a render mindig új bytes-ot termel, content-hash mindig új, `unchanged` mindig False.

**JSON proof:**
```json
{"files_written": 10, "files_unchanged": 0, "errors": 0}
```

A `files_unchanged` counter LÉTEZIK a CLI-ben — csak sosem trigger-elődik a fenti drift miatt.

**Javasolt fix (külön task):** `since_iso` és `generated_at` mezőket date-anchored timestamp-pé alakítani (pl. `since_iso = today_utc.replace(hour=0,minute=0,second=0)`, `generated_at = today_utc.date()`). Vagy: idempotency-check kihagyja a frontmatter-t és csak a table-body-t hash-eli.

## Anomáliák

1. **Idempotency-drift (HIGH)** — fent leírva, nem-blokkoló (a tartalom jó), de cron-on minden run-on commit-noise-t fog generálni a vault-autosave-en keresztül. Fix kell `--days 30` backfill előtt.
2. **Üres-window file-write** — 0-commit repo-k is kapnak file-t üres táblával. Nem feltétlen bug (timeline-stabil), de noise. Opcionális flag: `--skip-empty`.

## Next-steps

1. **Idempotency-fix** (külön task) — date-anchored timestamp vagy hash-skip-frontmatter, MIELŐTT `--days 30` backfill-t futtatunk.
2. **`--days 30` backfill** — fix után. Várt volume ~368 commit (dry-run alapján 30 nap).
3. **`--ingest-kodb` opt-in** — Layer 2 KO-DB ingest a fix UTÁN, hogy elkerüljük a 10×/day duplikált triplet-extract-et.
4. **Cron telepítés** — fix után. Suggested line:
   ```
   45 6 * * * VAULT_GH_BRIDGE_APPLY=1 /usr/local/bin/vault-gh-bridge --apply --days 1 --json >> /var/log/vault-gh-bridge.log 2>&1
   ```

## Kapcsolódó

- CLI: `/usr/local/bin/vault-gh-bridge`
- Pattern: [[../11-wiki/github-commit-history-ingest-pattern]]
- Log: `/tmp/vault-gh-bridge-first-run.log`
- State: `/root/.vault-config/gh-bridge-state.json`
