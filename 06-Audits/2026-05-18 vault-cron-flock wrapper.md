---
name: vault-cron-flock wrapper
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#topic/vault-ops", "#topic/race-condition"]
---

# vault-cron-flock wrapper

> Concurrency-guard wrapper minden vault-cron-hoz. flock-alapú lock-acquire,
> non-blocking, contention esetén skip + log + exit 0.

## Háttér

A vault_atomic.py subagent audit (2026-05-18) szerint **14 vault-cron, csak 2 használ flock-ot**. Race-rizikók (azonos 5-perces ablakon belül futó job-párok):

| Job A | Job B | Ütközés |
|---|---|---|
| vault-ko-conflicts-audit (Sun 04:30) | vault-broken-wikilinks-audit (daily 04:30) | közös 06-Audits/ + Backlog.md |
| vault-crystallize-monitor (Sun 04:35) | vault-ko-conflicts-audit (Sun 04:30) | overlap ha 1. tovább fut |
| vault-public-sync (*/30) | vault-autosave (*/10) | git-state mutáció (commit/push race) |
| vault-cleanup (Sun 04:00) | vault-net-watch (Sun 05:00) | overlap ha vault-cleanup tovább tart 1h-nál |

## Implementáció

`/usr/local/bin/vault-cron-flock` — 51 sor bash. Konvenció:

```
vault-cron-flock <lockname> <command...>
```

- **flock -n** (non-blocking): contention esetén nem vár, exit 0 + log
- **flock -E 99**: contention exit-code megkülönböztethető az inner cmd-tól
- **Log:** `/var/log/vault-cron-flock.log` (append-only, timestamp + lockname + cmd)
- **Lockdir:** `/var/run/vault-locks/` (vagy `/tmp/vault-locks/` fallback)

## Lockname-mátrix

| Lockname | Cron-okat lefedi | Megjegyzés |
|---|---|---|
| `git-state` | vault-autosave (*/10), vault-public-sync (*/30) | **Shared lock** — git-mutation szériába rendezve |
| `vault-cleanup` | vault-cleanup | own lock |
| `vault-ko-conflicts-audit` | vault-ko-conflicts-audit | own lock |
| `vault-crystallize-monitor` | vault-crystallize-monitor | own lock |
| `vault-memory-monitor` | vault-memory-monitor | own lock |
| `vault-net-watch` | vault-net-watch | own lock |
| `vault-github-trending-recurrence` | vault-github-trending-recurrence | own lock |
| `vault-broken-wikilinks-audit` | vault-broken-wikilinks-audit | own lock |
| `vault-embed-freshness` | vault-embed-freshness | own lock |
| `vault-coherence-check` | vault-coherence-check | own lock |
| `vault-orphan-wiki` | vault-orphan-wiki | own lock |
| `vault-auto-disable-check` | vault-auto-disable-check (*/15) | own lock, leginkább önmagával raceelhet |
| `vault-cost-rollup` | vault-cost-rollup | own lock |

**Nem-vault cron-ok érintetlen:** `github-trending-report`, `notebooklm list`, `backup.sh`, `boulium notify-events` — saját scope-juk van, nem írnak a vault-ba.

## Smoke

3 párhuzamos cron-spawn ugyanazzal a lockname-mel (`race-test`):

```
PID1 rc=0  ← winner (sleep 2 normál lefutása)
PID2 rc=0  ← contention-skip
PID3 rc=0  ← contention-skip
```

Contention log:

```
[2026-05-19T05:43:45Z] LOCK CONTENTION on 'race-test' (cmd=/bin/sleep 2), skipped
[2026-05-19T05:43:45Z] LOCK CONTENTION on 'race-test' (cmd=/bin/sleep 2), skipped
```

Cron-context-ben az exit-0 a helyes — a skipped job a next-tick-en majd lefut, és NEM tölti meg a cron-mail-t fals-pozitív hiba-leveléklel.

## Rollback

```bash
crontab /tmp/crontab.backup-YYYYMMDD-HHMMSS
```

(Backup automatikusan készül az install-script futása előtt.)

## Kapcsolódó

- `/root/obsidian-vault/.vault-tools/lib/vault_atomic.py` — atomic-write helper, ami a same-fs race-eket kezeli (a flock-wrapper meg a cross-process race-t)
- [[vault-cleanup]] — az egyik legnagyobb-rizikójú job, 100+ MB-os audit-output, lock-megelőzi a System_Health.md half-write-ot
