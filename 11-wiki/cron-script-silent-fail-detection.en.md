---
name: Cron-script silent-fail detection
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/cron", "#topic/observability", "#topic/reliability", "pattern/silent-fail", "evergreen", "lang/en"]
status: stable
lang: en
translated_from: cron-script-silent-fail-detection.md
session-evidence: 8
first-seen: 2026-W17
---

# Cron-script silent-fail detection

> [!info] TL;DR
> `dev backup cron` was silent for 3 months; `vault-detect-chat-id` with `set -e` returned `exit 1` inside a parameter expansion and silently killed the chain (5 scripts had to be patched 2026-05-18); `wp db export` on Hostinger shared produced a 20-byte gzip header with `exit 0`. All the same generic problem: **cron + bash + set -e + no-monitoring = invisible failure**. This wiki gives the defensive script pattern.

## The 4 cron-silent-fail modes

### 1. Bash `set -e` + parameter-expansion collision

**Problem**: `${VAR:-$(cmd 2>/dev/null)}` — inside parameter expansion, `cmd`'s `exit 1` with `set -e` **kills the entire script** mid-line, no error message (the `2>/dev/null` also eats stderr).

**Source**: 2026-05-18 vault — `vault-detect-chat-id` exit-1 collision in 11.11 family; 5 scripts (`11.11start`, `11.11stop`, `11.11note`, `11.11focus`, `11.11ls`) patched.

**Fix:**
```bash
# BAD — set -e kills the chain if `vault-detect-chat-id` exits 1
CHAT_ID="${CHAT_ID:-$(vault-detect-chat-id 2>/dev/null)}"

# GOOD — explicit `|| true` guarantees no propagated exit code
CHAT_ID="${CHAT_ID:-$(vault-detect-chat-id 2>/dev/null || true)}"
```

**General rule**: every command-substitution inside parameter expansion should end with `|| true` when `set -e` is active and the failure is non-fatal.

### 2. Truncated cron PATH

**Problem**: cron `PATH=/usr/bin:/bin` (truncated), tools alive in session PATH (`vault-ko-query`, `pnpm`, `wp`, `gh`) are **not found**. Bash silently says "command not found" → without `set -e` it exits 0 as if it ran. Cron mails stderr, but on most VPSes mail aliases aren't configured → **silently lost**.

**Fix:**
```bash
#!/usr/bin/env bash
set -euo pipefail
# Explicit PATH extension in EVERY cron script
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Or use absolute paths
/usr/local/bin/vault-ko-query "..." > /var/log/myscript.log 2>&1
```

### 3. Exit-0 + 20-byte indicator

**Problem**: command returns `exit 0` but output is empty / header-only. `wp db export` on Hostinger shared produces a **20-byte gzip header** — `$?==0` but the backup is worthless.

**Detection**: every cron-generated file gets a **size-floor check**:

```bash
output="/var/backups/site-$(date +%F).sql.gz"
wp db export - | gzip > "$output"
size=$(stat -c%s "$output")
if [[ $size -lt 1024 ]]; then
  echo "ERROR: backup file only $size bytes — likely silent fail" >&2
  # Fallback to direct mysqldump
  mysqldump --defaults-file=$HOME/.my.cnf db | gzip > "$output"
  exit 1
fi
```

### 4. MIN_VOLUME watchdog missing

**Problem**: cron script runs normally, but **volume** drops (e.g. `vault-ko-ingest` finds 0 new facts for 7 days straight). No error, just silent loss of added value. (See `auto-disable-min-volume-guard`.)

**Fix**: weekly audit job watches `wc -l $LOG`; if 7 days without a new line → alert OR auto-disable.

```bash
# weekly-audit.sh
recent_lines=$(find /var/log/myscript.log -mtime -7 -exec cat {} \; | wc -l)
if [[ $recent_lines -lt 5 ]]; then
  echo "ALERT: myscript produced only $recent_lines lines in past 7 days" \
    | mail -s "Watchdog: low volume" admin@example.com
fi
```

## Defensive cron-script template

```bash
#!/usr/bin/env bash
set -euo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

LOG="/var/log/$(basename "$0").log"
exec > >(tee -a "$LOG") 2>&1

echo "=== $(date -Iseconds) START $0 ==="

# ... script body ...

echo "=== $(date -Iseconds) DONE $0 ==="
# Sanity marker — weekly audit job tail-1 checks it
echo "# CRON_OK $(date -Iseconds)" >> "$LOG"
```

The `# CRON_OK <iso>` line is the sanity marker. Weekly audit:

```bash
last_ok=$(grep "^# CRON_OK" /var/log/myscript.log | tail -1 | awk '{print $3}')
last_ok_epoch=$(date -d "$last_ok" +%s)
now=$(date +%s)
age=$(( (now - last_ok_epoch) / 86400 ))
if [[ $age -gt 2 ]]; then
  echo "ALERT: myscript last successful $age days ago" | mail -s "Cron stale" admin@...
fi
```

## Reusable rules

1. **`set -euo pipefail`** always — but know that command-substitution + `set -e` inside parameter expansion needs `|| true`.
2. **Explicit PATH** in first lines of every cron script — never assume interactive shell PATH is live.
3. **`tee` + `LOG`** on every output — cron mail can be lost, log file is the source.
4. **Sanity marker** `# CRON_OK <iso>` at the end of every successful run.
5. **Size-floor check** on every generated artifact (see [[silent-fail-family-taxonomy]] family 1).
6. **MIN_VOLUME watchdog** — if 7 days produce 0 new lines / 0 new facts → alert or auto-disable.
7. **Audit-log append-only** — never `>` (overwrite), always `>>` (append), else run history vanishes.
8. **Independent monitoring**: don't let the cron script report its own health (circular); separate weekly audit job.

## Anti-patterns

| Pattern | Problem |
|---|---|
| `set -e` + `${VAR:-$(cmd)}` without `\|\| true` | parameter-expansion exit-1 kills the chain |
| Cron script inherits session PATH | cron context has different PATH, command not found |
| `> output.sql` without size check | 20-byte silent fail unnoticed |
| Cron mail as the only signal | mail alias missing → lost |
| Script reports its own health | circular: if it dies, no signal |
| `exit 0` after `if grep ...; then` | grep no-match exit-1 → `set -e` kills, or invisible |

## Session evidence (8 sources)

| Project | Week | Trap type |
|---|---|---|
| frankpanama.com wp db export | W17 | 3 (20-byte) |
| dev backup cron 3-month silent | W20 | 4 (MIN_VOLUME) |
| 11.11 family vault-detect-chat-id | W20 | 1 (set -e + parameter expansion) |
| vault-autosave 10-min cron | W17 | template reference |
| crystallize weekly audit job | W19 | template reference |
| Hostinger shared wp db export | W20 | 3 (Hostinger-specific) |
| mailbox auto-disable | W19 | 4 (volume watchdog) |
| vault-cleanup weekly cron | W20 | 7 (append-only audit) |

## Related

- [[silent-fail-family-taxonomy]] — family taxonomy (1. exit-0 subgroup)
- [[wp-cli-shared-db-export-fallback]] — Hostinger-specific incident
- [[auto-disable-min-volume-guard]] — watchdog pattern
- [[audit-log-append-only-pattern]] — append-only audit trail
- [[memory-md-overflow-management]] — analogous silent-truncation

## Hungarian original

[[cron-script-silent-fail-detection]]
