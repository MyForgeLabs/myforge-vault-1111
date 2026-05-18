---
name: rollback-revert-strategy-tiers
type: wiki
lang: en
translated_from: rollback-revert-strategy-tiers
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#topic/operability", "#pattern/recovery"]
---

# Rollback / revert strategy tiers

## TL;DR

Every mutation level has a **different rollback strategy**: shell script (`.bak` copy), skill symlink (`rm`), git commit (`git revert`), threshold flip (hot-reload file), crystallization prop (`crystallize-revert <hash>`). The tier system is **explicit** — do NOT mix two mechanisms for one mutation.

## Background

- **Bash rollback:** `cp /usr/local/bin/myscript.bak /usr/local/bin/myscript`
- **Skill rollback:** `rm symlinks under ~/.agents/skills/`
- **Vault rollback:** `git revert <commit>` — matches the granularity of autosave 10-minute commits
- **Crystallize-revert script:** `crystallize-revert <bullet-hash>` for REAL-mode applies (Layer-5 with audit trail)
- **Threshold rollback (backout trigger):** if 7-day revert-rate >5% → `threshold +0.05 rollback` (just a hot-reload file flip)
- **Sprint Day 0 backout:** `<sprint>_MODE=disabled` ENV-flag-flip or `git revert`
- **Plugin rollback strategy:** for irreversible UI plugins, "plugin must not be uninstalled" requirement — otherwise non-revertible

## Pattern — Tier matrix

| Tier | Mutation type | Forward | Revert | Time |
|------|----------------|---------|--------|-----|
| T1 | Threshold flip (hot-reload) | `echo 0.85 > file` | `echo 1.0 > file` | <1s |
| T2 | ENV-flag toggle | `export VAULT_X=1` | `unset VAULT_X` | <1s |
| T3 | Skill symlink cherry-pick | `ln -s` | `rm symlink` | <1s |
| T4 | Shell-script update | `cp new file` | `cp file.bak file` | <1s |
| T5 | Crystallize auto-prop | atomic-write + commit | `crystallize-revert <hash>` | ~5s |
| T6 | Git commit (autosave) | `git commit` | `git revert <hash>` | <10s |
| T7 | DB mutation (RLS, schema) | Prisma `db push` | `git revert migration` + manual DBA | minutes |
| T8 | Plugin uninstall (WP) | UI/CLI | NOT revertible (data loss) | N/A |

## Architectural rules

1. **Before every mutation:** explicit tier decision — "this is T5, revert with `crystallize-revert <hash>`"
2. **`.bak` copy ALWAYS** before T4-mutation — even if it's in `git` (faster hot-restore)
3. **Audit-log entry MANDATORY** for T5-T7 mutations ([[audit-log-append-only-pattern]])
4. **Idempotency-key on every T5+ revertable operation** — revert must not produce a false-positive double-revert
5. **Pre-state backup** T5-T7: `git stash` or "pre-state commit"
6. **T8 (non-revertible) escalation flag** — Critic-review + user confirmation mandatory; never auto-mode

## Anti-patterns

- ❌ **`git reset --hard`** on autosave commits — can drop work between 10-minute commits
- ❌ **`rm -rf` directory revert** — never; use `git checkout HEAD~1 -- path`
- ❌ **DB-truncate "revert"** — not revert, destructive; restore from backup is required
- ❌ **Multi-tier compound revert** (T4+T6) — one tier per commit; separate commit per autosave

## Pitfalls

- ⚠️ **Vault rename + second editor sync** — batch `git mv` while another editor is active → detached HEAD; recovery + double-conflict cascade
- ⚠️ **`set -e` + command substitution exit-1** kills scripts; `2>/dev/null || true` is the fix
- ⚠️ **Autosave cron** every 10 minutes — if T5-revert + push collide with the cron → push conflict; always `git pull --rebase` first
- ⚠️ **Crystallize-revert + sandbox-branch** — revert on the sandbox, NOT on main; then `git merge sandbox` if clean

## Revert-rate monitoring

A weekly monitor — if **revert-rate >2% on the threshold, automatically threshold +0.05** (T1 hot-reload) and Critic-review trigger ([[crystallize-threshold-ramp]]).

## Related

- [[multi-layer-safety-gate]] — Layer 5 = revert/audit
- [[audit-log-append-only-pattern]] — every revert logged
- [[hot-reload-config-pattern]] — T1 threshold flip
- [[env-flag-default-disabled-gate]] — T2 flag toggle
- [[auto-propagation-confidence-gate]] — T5 crystallize revert
- [[sprint-day-0-skeleton-first]] — Day 0 backout
- [[crystallize-threshold-ramp]] — automatic threshold backout
