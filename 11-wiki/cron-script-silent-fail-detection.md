---
name: Cron-script silent-fail detection
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/cron", "#topic/observability", "#topic/reliability", "pattern/silent-fail", "evergreen"]
status: stable
session-evidence: 8
first-seen: 2026-W17
---

# Cron-script silent-fail detection

> [!info] TL;DR
> A `dev backup cron` 3 hónapig néma volt; a `vault-detect-chat-id` `set -e`-vel `exit 1`-et adott egy parameter-expansion-ben és csendben ölte a chain-t (5 script-et kellett patchelni 2026-05-18-án); a `wp db export` Hostinger shared-en `exit 0`-val 20-byte gzip-headert produkált. Mind ugyanaz a generikus probléma: **cron + bash + set -e + no-monitoring = láthatatlan kudarc**. Ez a wiki adja a defenzív szkript-pattern-t.

## A 4 cron-silent-fail mód

### 1. Bash `set -e` + parameter-expansion collision

**Probléma**: `${VAR:-$(cmd 2>/dev/null)}` parameter-expansion-ben a `cmd` exit-1-je `set -e`-vel **megöli a teljes scriptet** mid-line, hibaüzenet nélkül (a `2>/dev/null` elnyeli a stderr-t is).

**Forrás**: 2026-05-18 vault — `vault-detect-chat-id` exit-1 collision a 11.11 family-ben; 5 script (`11.11start`, `11.11stop`, `11.11note`, `11.11focus`, `11.11ls`) patcholva (MEMORY 2026-05-18).

**Fix:**
```bash
# ROSSZ — set -e öli a chain-t ha `vault-detect-chat-id` exit 1
CHAT_ID="${CHAT_ID:-$(vault-detect-chat-id 2>/dev/null)}"

# JÓ — explicit `|| true` ensure-eli, hogy nem ürögtet exit-code-ot
CHAT_ID="${CHAT_ID:-$(vault-detect-chat-id 2>/dev/null || true)}"
```

**Általánosabb szabály**: minden command-substitution-t parameter-expansion-ben `|| true`-val zárj, ha `set -e` aktív és a hiba nem fatális.

### 2. Cron PATH-csonka

**Probléma**: cron `PATH=/usr/bin:/bin` (csonka), session-PATH-ban élő tool-ok (`vault-ko-query`, `pnpm`, `wp`, `gh`) **nem találhatók**. Bash csendben "command not found"-ot ad → `set -e` nélkül exit 0, mintha lefutott volna. Cron stderr-t mail-eli, de a legtöbb VPS-en a mail-aliasok nincsenek konfigolva → **csendben elveszik**.

**Fix:**
```bash
#!/usr/bin/env bash
set -euo pipefail
# Cron-PATH explicit kiegészítése MINDEN cron-scriptben
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Vagy abszolút path-ekkel hivatkozz
/usr/local/bin/vault-ko-query "..." > /var/log/myscript.log 2>&1
```

### 3. Exit-0 + 20-byte indikátor

**Probléma**: parancs `exit 0`-val tér vissza, de a kimenete üres / fejléc-only. A `wp db export` Hostinger shared-en **20-byte gzip-header** (KO-DB [4940], [4973], [13614]) — `$?==0`, de a backup értéktelen.

**Detektálás**: minden cron-által generált fájlra **size-floor check**:

```bash
output="/var/backups/site-$(date +%F).sql.gz"
wp db export - | gzip > "$output"
size=$(stat -c%s "$output")
if [[ $size -lt 1024 ]]; then
  echo "ERROR: backup file only $size bytes — likely silent fail" >&2
  # Fallback to mysqldump direct (KO-DB [4948])
  mysqldump --defaults-file=$HOME/.my.cnf db | gzip > "$output"
  exit 1
fi
```

### 4. MIN_VOLUME watchdog hiánya

**Probléma**: cron-script normál módon fut, de a **mennyiség** leesik (pl. `vault-ko-ingest` 0 új fact-et talál 7 napig egymás után). Nincs error, csak csendben elveszik a hozzáadott érték. (Lásd `auto-disable-min-volume-guard` wiki.)

**Fix**: heti audit-job ami `wc -l $LOG`-ot néz, és ha 7 napig nincs új sor → riaszt VAGY auto-disable.

```bash
# weekly-audit.sh
recent_lines=$(find /var/log/myscript.log -mtime -7 -exec cat {} \; | wc -l)
if [[ $recent_lines -lt 5 ]]; then
  echo "ALERT: myscript produced only $recent_lines lines in past 7 days" \
    | mail -s "Watchdog: low volume" admin@example.com
fi
```

## Defenzív cron-script template

```bash
#!/usr/bin/env bash
set -euo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

LOG="/var/log/$(basename "$0").log"
exec > >(tee -a "$LOG") 2>&1

echo "=== $(date -Iseconds) START $0 ==="

# ... script-body ...

echo "=== $(date -Iseconds) DONE $0 ==="
# Sanity-marker — heti audit-job tail-1-gyel ellenőrzi
echo "# CRON_OK $(date -Iseconds)" >> "$LOG"
```

A `# CRON_OK <iso>` line a sanity-marker. A heti audit:

```bash
last_ok=$(grep "^# CRON_OK" /var/log/myscript.log | tail -1 | awk '{print $3}')
last_ok_epoch=$(date -d "$last_ok" +%s)
now=$(date +%s)
age=$(( (now - last_ok_epoch) / 86400 ))
if [[ $age -gt 2 ]]; then
  echo "ALERT: myscript last successful $age days ago" | mail -s "Cron stale" admin@...
fi
```

## Reusable szabályok

1. **`set -euo pipefail`** mindig — de tudd, hogy command-substitution + `set -e` parameter-expansion-ben → `|| true` kell.
2. **Explicit PATH** minden cron-script első soraiban — sose feltételezd, hogy az interaktív shell PATH-ja él.
3. **`tee` + `LOG`** minden output-ra — cron-mail elveszhet, log-fájl a forrás.
4. **Sanity-marker** `# CRON_OK <iso>` minden sikeres futás végén.
5. **Size-floor check** minden generált artefaktumra (lásd [[silent-fail-family-taxonomy]] 1. család).
6. **MIN_VOLUME watchdog** — ha 7 napig 0 új sor / 0 új fact → riaszt vagy auto-disable.
7. **Audit-log append-only** — sose `>` (overwrite), mindig `>>` (append), különben a futás-történet eltűnik.
8. **Független monitoring**: ne a cron-script jelezze a saját egészségét (kör), külön audit-job heti riportja.

## Anti-pattern

| Pattern | Probléma |
|---|---|
| `set -e` + `${VAR:-$(cmd)}` `\|\| true` nélkül | parameter-expansion exit-1 öli a chain-t |
| Cron-script PATH-ot örökli a saját session-ből | cron-context másik PATH, command not found |
| `> output.sql` size-check nélkül | 20-byte silent-fail észrevétlen |
| Cron-mail egyetlen jelzés | mail-alias hiányában elveszik |
| Saját script jelzi a saját egészségét | körkörös, ha a script meghal, nincs jelzés |
| `exit 0` `if grep ...; then` után | grep no-match exit-1 → `set -e` öl, vagy láthatatlan |

## Session-evidence (8 forrás)

| Project | Hét | Trap-típus |
|---|---|---|
| frankpanama.com wp db export | W17 | 3 (20-byte) |
| dev backup cron 3 hónap silent | W20 | 4 (MIN_VOLUME) |
| 11.11 family vault-detect-chat-id | W20 | 1 (set -e + parameter-expansion) |
| vault-autosave 10-min cron | W17 | template-referencia |
| crystallize weekly audit-job | W19 | template-referencia |
| Hostinger shared wp db export | W20 | 3 (Hostinger-specific) |
| mailbox auto-disable | W19 | 4 (volume-watchdog) |
| vault-cleanup heti cron | W20 | 7 (append-only audit) |

## Kapcsolódó

- [[silent-fail-family-taxonomy]] — családi taxonomy (1. exit-0 alcsoport)
- [[wp-cli-shared-db-export-fallback]] — Hostinger-specific incidens
- [[auto-disable-min-volume-guard]] — watchdog-pattern
- [[audit-log-append-only-pattern]] — append-only audit-trail
- [[memory-md-overflow-management]] — analóg silent-truncation
