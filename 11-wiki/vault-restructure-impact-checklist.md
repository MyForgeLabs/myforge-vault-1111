---
name: Vault restructure impact checklist
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/obsidian", "#topic/vault", "#topic/migration", "pattern/restructure", "evergreen"]
status: stable
session-evidence: 7
first-seen: 2026-W17
---

# Vault restructure impact checklist

> [!info] TL;DR
> A 2026-04 Johnny-Decimal vault-prefix-rename és a 2026-05-09 Mac-Obsidian-Git double-conflict cascade tanítása: vault-szintű `git mv` / mass-rename / mappa-átszervezés **4 független cascade-breakage-et** indít, amiknek mindegyik szilenten-fail (lásd [[silent-fail-family-taxonomy]] 2. család). Ez a wiki adja a pre-restructure checklistet, az incident-recovery protokollt, és a defenzív-flagek listáját.

## A 4 cascade-breakage

### Breakage 1: Cron-script path-ok

**Tünet**: `vault-cleanup`, `vault-autosave`, `vault-ko-ingest` cron-scriptek hard-coded `/root/obsidian-vault/03-Hosts/...` path-ot tartalmaznak. Mappa-rename után **csendben** mappát-nem-talál hibára futnak, **exit 0**-val tér vissza (vagy stderr-be ír, ami cron-mail nélkül elveszik). Lásd [[cron-script-silent-fail-detection]] 2-3 trap.

**Detektálás**:
```bash
grep -rnE "/root/obsidian-vault/[0-9]+-" /usr/local/bin/ /etc/cron.* 2>/dev/null
```

**Fix előtte**: minden hard-coded vault-path-ot env-var-ra cserélj:
```bash
VAULT="${VAULT_ROOT:-/root/obsidian-vault}"
"$VAULT/03-Hosts/..."  # NEM hard-coded
```

### Breakage 2: Mac Obsidian-Git double-conflict

**Tünet** (KO-DB [11130], [11131], [13070], [13071], [1238], [11128], [11136]): server-side git-history modify (rebase / reset / mass-rename commit) **közben** a Mac Obsidian-Git plugin 5-perces auto-sync triggerelődik → detached HEAD mid-rebase → első conflict-resolve után **második conflict** (workspace-state modify). Eredmény: server-side fix **silent-revert**, AUTO-GEN END marker eltűnik.

**Forrás**: `08-Sessions/2026-05-09-vault-maintenance.md`, `2026-05-13-sv-obsidian-coloring-fix.md`.

**Fix előtte**:
```bash
# Mac-en: Obsidian-Git plugin → Settings → "Disable auto-pull" temporarily
# vagy quit Obsidian a restructure-időablakra
```

**Fix git-szinten** (mindkét gépen):
```bash
git config rebase.autoStash true      # KO-DB [11139]
git config pull.rebase true            # KO-DB [11140]
```

### Breakage 3: WordPress mu-plugins UpdraftPlus orphan

**Tünet**: ha a vault-restructure mellett WordPress staging→prod átállás történik, az `UpdraftPlus` `wpcore.zip` üres lesz (MEMORY: `wp core download --force --skip-content` kell). A vault path-rename ide önmagában nem érint, **DE** ha a WP-projekt-fájl `02-Projects/<wp-projekt>.md`-je rename-elve, a hozzá kapcsolódó scriptek (deploy-client-b.sh, kgc-deploy.sh) hard-coded markdown-path-okra hivatkozhatnak.

**Detektálás**:
```bash
grep -rE "obsidian-vault.*\.md" /root/projektjeim/ /usr/local/bin/ 2>/dev/null
```

### Breakage 4: Wikilink mass-broken

**Tünet**: `[[02-Projects/teszt-eu]]` → ha a `02-Projects/` átnevezed `20-Projects/`-re, az **összes** régebbi wikilink eltörik. Obsidian-graph üres. A `audit-md-self-referential-loop` (MEMORY 2026-05-18) tovább zavar: 1656 broken-link issue ~70%-a self-loop-noise volt.

**Detektálás** post-rename:
```bash
# broken-wikilink scanner (excluding self-references)
python3 /usr/local/bin/vault-broken-wikilink-audit.py --exclude-self
```

## Pre-restructure 10-pontos checklist

Mielőtt `git mv` vagy mass-rename:

1. **Backup** — `git tag pre-restructure-$(date +%F)` + `git push --tags`
2. **Mac Obsidian quit** — vagy Obsidian-Git plugin auto-pull disable
3. **Mac git-config check** — `rebase.autoStash=true`, `pull.rebase=true` mindkét gépen
4. **Cron-script audit** — `grep -rnE "/root/obsidian-vault/[0-9]+-"` a `/usr/local/bin/`-ben + `/etc/cron.*`-ban
5. **Env-var migráció előbb** — minden hard-coded path-ot env-var-ra cserélj a restructure ELŐTT
6. **Wikilink-prefix bulk-replace dry-run** — `git grep -l "\[\[02-Projects/" | xargs sed -i.bak 's|\[\[02-Projects/|[[20-Projects/|g'` ELŐTT `--dry-run` equivalent (csak `git grep`)
7. **Scripts referencing `.md` paths** — `grep -rE "obsidian-vault.*\.md" /root/` (lásd Breakage 3)
8. **Symlinks AGENTS.md / CLAUDE.md / GEMINI.md** — ezek a gyökérben maradnak → érintetlenek a Johnny-Decimal-prefix rename-ekben (DESIGN-decision: gyökér-szimlinkek soha ne rename-elődjenek)
9. **Auto-save 10-min cron pause** — `crontab -e` → comment-out `vault-autosave` a restructure-időablakra
10. **Commit message konvenció** — `restructure: <from> → <to>` prefix, hogy a `vault-cleanup` audit-log azonosítsa

## Incident-recovery 4-step protokol

Ha restructure közben break-elt valami:

### Step 1: Stop the bleeding

```bash
# Server: cron-autosave kill
sudo systemctl stop cron  # vagy comment-out vault-autosave

# Mac: Obsidian quit + Obsidian-Git auto-pull disable
```

### Step 2: Find the conflict-state

```bash
cd /root/obsidian-vault
git status              # detached HEAD?
git log --oneline -20   # melyik commit-on vagyunk?
git diff HEAD@{1}       # mit veszítünk, ha forward-rebase-elünk?
```

### Step 3: Rebase resolution

```bash
# Ha rebase-conflict mid-resolution:
git rebase --abort                # back to known state
git checkout main                 # vissza a stable branch-re
git tag recovery-$(date +%s)      # safety-tag
# Most retry a restructure-t cleanly
```

### Step 4: Validate

```bash
# Broken-wikilink count
python3 /usr/local/bin/vault-broken-wikilink-audit.py
# Cron-script smoketest
/usr/local/bin/vault-cleanup --dry-run
# Obsidian re-open + graph-view check
```

## Defenzív flag-ek (vault-config)

`~/.vault-config/restructure-safety.env`:

```bash
# Vault restructure-time safety flags
VAULT_AUTOSAVE_PAUSE=1           # Cron-autosave skip-eli a futást
VAULT_MAC_GIT_PAUSE=1            # Mac Obsidian-Git plugin egy markert keres ehhez
VAULT_BROKEN_WIKILINK_THRESHOLD=50  # ennyi felett auto-revert
```

A `vault-autosave` script első sorában:
```bash
[[ "${VAULT_AUTOSAVE_PAUSE:-0}" == "1" ]] && { echo "PAUSED $(date)"; exit 0; }
```

## Anti-pattern

| Pattern | Probléma |
|---|---|
| Vault-batch `git mv` aktív Mac-session közben | detached HEAD, double-conflict (KO-DB [11130]) |
| Hard-coded path-ok cron-scriptben | rename után silent-fail (Breakage 1) |
| Post-rename csak Obsidian-graph audit | grep + broken-wikilink audit kihagyva (Breakage 4) |
| Symlink AGENTS.md rename-elés | gyökér-szimlinkek soha ne rename-elődjenek |
| Auto-pull aktív restructure-időablakra | Mac-Obsidian-Git race-condition |
| 1 commit-ban átnevezés + tartalmi módosítás | git log-átláthatatlan, recovery nehéz |

## Reusable szabályok

1. **Pre-restructure backup-tag KÖTELEZŐ** — `git tag pre-restructure-<date>` + push.
2. **Mac Obsidian-Git pause** restructure-időablakra — auto-pull race condition elkerülése.
3. **Hard-coded path → env-var migráció ELŐSZÖR**, restructure UTÁN.
4. **Symlinks gyökérben** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) immutable — Johnny-Decimal prefix-rename mappákra korlátozódik.
5. **Cron-autosave PAUSE-flag** — env-var-controlled skip a restructure-időablakra.
6. **Post-rename validation triple-check**: broken-wikilink audit + cron-smoke-test + Obsidian-graph re-open.
7. **Restructure commit külön** a tartalmi módosításoktól — git log átláthatóság.
8. **Recovery-tag** minden incident-recovery után (`recovery-<epoch>`) — későbbi forensics.

## Session-evidence (7 forrás)

| Hét | Incident | Breakage-családok |
|---|---|---|
| W17 (2026-04) | Johnny-Decimal vault-prefix migráció | 1 + 4 |
| W19 (2026-05-09) | Mac Obsidian-Git double-conflict | 2 |
| W19 (2026-05-13) | sv-obsidian-coloring-fix git-config | 2 |
| W20 (2026-05-18) | audit-md-self-referential-loop 1656 issue | 4 |
| W17 (2026-04-30) | crystallization workflow + autosave cron | 1 |
| W19 (2026-05-09) | vault-maintenance commit 4774a20 | 2 (AUTO-GEN END recovery) |
| W17 (2026-04-23) | Unified agent memory ADR (git-readiness) | 1 (design-time prevention) |

## Kapcsolódó

- [[silent-fail-family-taxonomy]] — 2. (mutation-silent-revert) család forrása
- [[cron-script-silent-fail-detection]] — Breakage 1 detail
- [[audit-md-self-referential-loop]] — Breakage 4 detail
- [[bmad-cross-machine-artifact-verification]] — Mac-server „event ≠ disk-state"
- [[Johnny-Decimal-prefix]] — miért 00-, 01-, … prefix
- [[Karpathy-LLM-Wiki-pattern]] — háttér-filozófia
- [[../06-Audits/System_Health]] — heti egészség-snapshot
