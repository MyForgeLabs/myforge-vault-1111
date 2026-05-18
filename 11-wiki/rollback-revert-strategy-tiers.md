---
name: rollback-revert-strategy-tiers
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#topic/operability", "#pattern/recovery"]
---

# Rollback / revert stratégia tier-ek

## TL;DR

Minden mutation-szintnek **különböző rollback-stratégiája** van: shell-script (`.bak` copy), skill-symlink (`rm`), git-commit (`git revert`), threshold-flip (hot-reload fájl), crystallization-prop (`crystallize-revert <hash>`). A tier-rendszer **explicit** — ne keverj 2 mechanizmust egy mutation-re. Cross-source: 32+ fact, 3 source-type.

## Háttér (3+ source-evidence)

- **Bash rollback:** `cp /usr/local/bin/11.11start.bak /usr/local/bin/11.11start` ([2026-04-30 Crystallization workflow ADR](../07-Decisions/2026-04-30%20Crystallization%20workflow%20+%20auto-context.md))
- **Skill rollback:** `rm symlinks under /root/.agents/skills/` ([2026-04-30 ADR](../07-Decisions/2026-04-30%20Crystallization%20workflow%20+%20auto-context.md))
- **Vault rollback:** `git revert <commit>` — vault-autosave 10 perces commit-jaihoz illeszkedő granularitás (auto-save cron)
- **Crystallize-revert script:** `crystallize-revert <bullet-hash>` REAL-mode apply-okhoz (Layer 5 audit-trail-lel) ([CLAUDE.md SV B-1 pipeline](/root/.claude/CLAUDE.md))
- **Threshold-rollback (Backout-trigger):** Ha 7-napos revert-rate >5% → `threshold +0.05 rollback` (csak hot-reload fájl flip) ([sv-5 crystallization automation ADR](../07-Decisions/2026-05-12%20sv-5%20crystallization%20automation%20arch.md))
- **Sprint Day 0 backout:** `<sprint>_MODE=disabled` ENV-flag-flip vagy `git revert` ([sprint-day-0-skeleton-first](sprint-day-0-skeleton-first.md))
- **Elementor PRO rollback strategy:** "Elementor PRO not deleted" requirement — mert nem-revertible ha plugin törölve ([2026-05-08 Rojt és Bojt — Bricks Builder migration](../07-Decisions/2026-05-08%20Rojt%20és%20Bojt%20—%20Bricks%20Builder%20migration.md))

## Mintázat — Tier-mátrix

| Tier | Mutation típus | Forward | Revert | Idő |
|------|----------------|---------|--------|-----|
| T1 | Threshold-flip (hot-reload) | `echo 0.85 > file` | `echo 1.0 > file` | <1s |
| T2 | ENV-flag toggle | `export VAULT_X=1` | `unset VAULT_X` | <1s |
| T3 | Skill symlink-cherry-pick | `ln -s` | `rm symlink` | <1s |
| T4 | Shell-script update | `cp new file` | `cp file.bak file` | <1s |
| T5 | Crystallize auto-prop | atomic-write + commit | `crystallize-revert <hash>` | ~5s |
| T6 | Git-commit (auto-save) | `git commit` | `git revert <hash>` | <10s |
| T7 | DB-mutation (RLS, schema) | Prisma `db push` | `git revert migration` + manual DBA | percek |
| T8 | Plugin-uninstall (WP) | UI/CLI | NEM revertible (data-loss) | N/A |

## Architektúrális szabályok

1. **Minden mutation előtt:** Tier-eldöntés explicit — "ez T5, revert `crystallize-revert <hash>`"
2. **`.bak` copy MINDIG** T4-mutáció előtt — még ha `git`-ben is van (gyorsabb hot-restore)
3. **Audit-log entry KÖTELEZŐ** T5-T7 mutation-höz ([audit-log-append-only-pattern]])
4. **Idempotency-key minden T5+ révert-elhető operation-ben** — revert ne csináljon false-positive double-revert-et
5. **Pre-state backup** T5-T7: `git stash` vagy "pre-state commit" ([sv-05-crystallization-automation](sv-05-crystallization-automation.md))
6. **T8 (NEM-revertible) eskalációs flag** — Critic-review + user-konfirmáció kötelező; sosem auto-mode

## Anti-pattern

- ❌ **`git reset --hard`** auto-save-re — 10-perces commit-ok közt drop-elhet munkát
- ❌ **`rm -rf` directory revert** — sosem; `git checkout HEAD~1 -- path` használj
- ❌ **DB-truncate "revert"** — nem revert, hanem destructive; restore from backup szükséges
- ❌ **Multi-tier compound revert** (T4+T6) — egy commit-ban egy tier; külön commit auto-save-en

## Buktatók

- ⚠️ **Vault rename + Mac Obsidian-Git sync** — vault-batch `git mv` aktív Mac-session közben → detached HEAD; recovery + double-conflict cascade ([MEMORY](/root/.claude/projects/-root/memory/MEMORY.md))
- ⚠️ **`set -e` + command-substitution exit-1** öl `2>/dev/null || true` fix (5 11.11* script 2026-05-18 patcholt)
- ⚠️ **Auto-save cron** 10 percenként — ha T5-revert + push collide a cron-nal → push-conflict; mindig `git pull --rebase` előbb
- ⚠️ **Crystallize-revert + sandbox-branch** — sandbox-on revertelj, NE main; majd `git merge sandbox` ha clean

## Revert-rate monitoring

`vault-crystallize-monitor` heti riport — ha **revert-rate >2% threshold-on, automatikusan threshold +0.05** (T1 hot-reload) és Critic-review trigger ([crystallize-threshold-ramp]]).

## Kapcsolódó

- [[multi-layer-safety-gate]] — Layer 5 = revert/audit
- [[audit-log-append-only-pattern]] — minden revert audit-loggal
- [[hot-reload-config-pattern]] — T1 threshold-flip
- [[env-flag-default-disabled-gate]] — T2 flag-toggle
- [[auto-propagation-confidence-gate]] — T5 crystallize revert
- [[sprint-day-0-skeleton-first]] — Day 0 backout
- [[crystallize-threshold-ramp]] — automatikus threshold-backout
