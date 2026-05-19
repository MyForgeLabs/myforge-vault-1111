---
name: Vault restructure impact checklist
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/obsidian", "#topic/vault", "#topic/migration", "pattern/restructure", "evergreen", "lang/en"]
status: stable
lang: en
translated_from: vault-restructure-impact-checklist.md
session-evidence: 7
first-seen: 2026-W17
---

# Vault restructure impact checklist

> [!info] TL;DR
> Lessons from the 2026-04 Johnny-Decimal vault-prefix rename and the 2026-05-09 Mac-Obsidian-Git double-conflict cascade: a vault-wide `git mv` / mass-rename / folder reorganisation triggers **4 independent cascade breakages**, all of which fail silently (see [[silent-fail-family-taxonomy]] family 2). This wiki provides the pre-restructure checklist, incident-recovery protocol, and defensive flags.

## The 4 cascade breakages

### Breakage 1: Cron-script paths

**Symptom**: `vault-cleanup`, `vault-autosave`, `vault-ko-ingest` cron scripts contain hard-coded `/root/obsidian-vault/03-Hosts/...` paths. After folder rename they **silently** hit folder-not-found errors and **exit 0** (or write to stderr, which is lost without cron-mail). See [[cron-script-silent-fail-detection]] traps 2-3.

**Detection**:
```bash
grep -rnE "/root/obsidian-vault/[0-9]+-" /usr/local/bin/ /etc/cron.* 2>/dev/null
```

**Fix beforehand**: replace every hard-coded vault path with an env-var:
```bash
VAULT="${VAULT_ROOT:-/root/obsidian-vault}"
"$VAULT/03-Hosts/..."  # NOT hard-coded
```

### Breakage 2: Mac Obsidian-Git double-conflict

**Symptom**: server-side git-history modify (rebase / reset / mass-rename commit) **while** the Mac Obsidian-Git plugin's 5-minute auto-sync triggers → detached HEAD mid-rebase → after first conflict-resolve a **second conflict** (workspace-state modify). Result: server-side fix is **silent-reverted**, AUTO-GEN END marker disappears.

**Source**: `08-Sessions/2026-05-09-vault-maintenance.md`, `2026-05-13-sv-obsidian-coloring-fix.md`.

**Fix beforehand**:
```bash
# On Mac: Obsidian-Git plugin → Settings → "Disable auto-pull" temporarily
# or quit Obsidian for the restructure window
```

**Fix at git level** (both machines):
```bash
git config rebase.autoStash true
git config pull.rebase true
```

### Breakage 3: WordPress mu-plugins UpdraftPlus orphan

**Symptom**: if vault-restructure coincides with WordPress staging→prod transition, `UpdraftPlus`'s `wpcore.zip` will be empty (needs `wp core download --force --skip-content`). Vault path-rename alone doesn't affect this, **BUT** if the WP project file `02-Projects/<wp-project>.md` is renamed, attached scripts (deploy-foxxi.sh, kgc-deploy.sh) may reference hard-coded markdown paths.

**Detection**:
```bash
grep -rE "obsidian-vault.*\.md" /root/projects/ /usr/local/bin/ 2>/dev/null
```

### Breakage 4: Wikilinks mass-broken

**Symptom**: `[[02-Projects/teszt-eu]]` → if you rename `02-Projects/` to `20-Projects/`, **all** older wikilinks break. Obsidian graph empties. The `audit-md-self-referential-loop` (2026-05-18) further confuses: ~70% of the 1656 broken-link issues were self-loop noise.

**Detection** post-rename:
```bash
# broken-wikilink scanner (excluding self-references)
python3 /usr/local/bin/vault-broken-wikilink-audit.py --exclude-self
```

## Pre-restructure 10-point checklist

Before `git mv` or mass-rename:

1. **Backup** — `git tag pre-restructure-$(date +%F)` + `git push --tags`
2. **Quit Mac Obsidian** — or disable Obsidian-Git auto-pull
3. **Mac git-config check** — `rebase.autoStash=true`, `pull.rebase=true` on both machines
4. **Cron-script audit** — `grep -rnE "/root/obsidian-vault/[0-9]+-"` in `/usr/local/bin/` + `/etc/cron.*`
5. **Env-var migration first** — replace every hard-coded path with an env-var BEFORE restructure
6. **Wikilink-prefix bulk-replace dry-run** — `git grep -l "\[\[02-Projects/"` first (only grep, no sed)
7. **Scripts referencing `.md` paths** — `grep -rE "obsidian-vault.*\.md" /root/` (see Breakage 3)
8. **Symlinks AGENTS.md / CLAUDE.md / GEMINI.md** — these stay in the root → untouched by Johnny-Decimal prefix renames (DESIGN decision: root symlinks must never be renamed)
9. **Auto-save 10-min cron pause** — `crontab -e` → comment out `vault-autosave` for the restructure window
10. **Commit message convention** — `restructure: <from> → <to>` prefix so `vault-cleanup` audit-log identifies it

## Incident-recovery 4-step protocol

If something breaks mid-restructure:

### Step 1: Stop the bleeding

```bash
# Server: kill cron-autosave
sudo systemctl stop cron  # or comment-out vault-autosave

# Mac: quit Obsidian + disable Obsidian-Git auto-pull
```

### Step 2: Find the conflict state

```bash
cd /root/obsidian-vault
git status              # detached HEAD?
git log --oneline -20   # which commit are we on?
git diff HEAD@{1}       # what do we lose on forward-rebase?
```

### Step 3: Rebase resolution

```bash
# If mid-resolution rebase-conflict:
git rebase --abort                # back to known state
git checkout main                 # return to stable branch
git tag recovery-$(date +%s)      # safety tag
# Now retry the restructure cleanly
```

### Step 4: Validate

```bash
# Broken-wikilink count
python3 /usr/local/bin/vault-broken-wikilink-audit.py
# Cron-script smoketest
/usr/local/bin/vault-cleanup --dry-run
# Obsidian re-open + graph-view check
```

## Defensive flags (vault-config)

`~/.vault-config/restructure-safety.env`:

```bash
# Vault restructure-time safety flags
VAULT_AUTOSAVE_PAUSE=1               # Cron-autosave skips the run
VAULT_MAC_GIT_PAUSE=1                # Mac Obsidian-Git plugin looks for a marker
VAULT_BROKEN_WIKILINK_THRESHOLD=50  # above this → auto-revert
```

In the first line of `vault-autosave`:
```bash
[[ "${VAULT_AUTOSAVE_PAUSE:-0}" == "1" ]] && { echo "PAUSED $(date)"; exit 0; }
```

## Anti-patterns

| Pattern | Problem |
|---|---|
| Vault-batch `git mv` during active Mac session | detached HEAD, double-conflict |
| Hard-coded paths in cron script | silent fail after rename (Breakage 1) |
| Post-rename only Obsidian-graph audit | grep + broken-wikilink audit skipped (Breakage 4) |
| Renaming symlink AGENTS.md | root symlinks must never be renamed |
| Auto-pull active during restructure window | Mac-Obsidian-Git race condition |
| Mixing rename + content changes in 1 commit | git log opaque, recovery hard |

## Reusable rules

1. **Pre-restructure backup tag MANDATORY** — `git tag pre-restructure-<date>` + push.
2. **Pause Mac Obsidian-Git** for the restructure window — auto-pull race condition avoidance.
3. **Hard-coded path → env-var migration FIRST**, restructure AFTER.
4. **Root symlinks** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) immutable — Johnny-Decimal prefix rename is folder-only.
5. **Cron-autosave PAUSE flag** — env-var-controlled skip for the restructure window.
6. **Post-rename validation triple-check**: broken-wikilink audit + cron-smoke-test + Obsidian-graph re-open.
7. **Restructure commit separate** from content changes — git-log readability.
8. **Recovery tag** after every incident-recovery (`recovery-<epoch>`) — later forensics.

## Session evidence (7 sources)

| Week | Incident | Breakage families |
|---|---|---|
| W17 (2026-04) | Johnny-Decimal vault-prefix migration | 1 + 4 |
| W19 (2026-05-09) | Mac Obsidian-Git double-conflict | 2 |
| W19 (2026-05-13) | sv-obsidian-coloring-fix git-config | 2 |
| W20 (2026-05-18) | audit-md-self-referential-loop 1656 issues | 4 |
| W17 (2026-04-30) | crystallization workflow + autosave cron | 1 |
| W19 (2026-05-09) | vault-maintenance commit 4774a20 | 2 (AUTO-GEN END recovery) |
| W17 (2026-04-23) | Unified agent memory ADR (git-readiness) | 1 (design-time prevention) |

## Related

- [[silent-fail-family-taxonomy]] — family 2 (mutation-silent-revert) source
- [[cron-script-silent-fail-detection]] — Breakage 1 detail
- [[audit-md-self-referential-loop]] — Breakage 4 detail
- [[bmad-cross-machine-artifact-verification]] — Mac-server "event ≠ disk-state"
- [[Johnny-Decimal-prefix]] — why 00-, 01-, … prefix
- [[Karpathy-LLM-Wiki-pattern]] — background philosophy
- [[../06-Audits/System_Health]] — weekly health snapshot

## Hungarian original

[[vault-restructure-impact-checklist]]
