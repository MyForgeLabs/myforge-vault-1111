---
name: sandbox-branch-mutation-isolation
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#topic/git", "#pattern/isolation"]
---

# Sandbox-branch mutation isolation

## TL;DR

Magas-kockázatú **auto-mutation** (crystallize REAL, GEPA mutate, schema-migration, predicate-remap) **mindig `<feature>-sandbox-*` branchen fut**, sosem `main`-en. A `main` opt-in: `<FEATURE>_ALLOW_MAIN=1` ENV-flag mögött, audit-event-tel. Merge csak ha 7-napos sandbox-revert-rate <2%. Cross-source: 54+ fact, 3 source-type.

## Háttér (3+ source-evidence)

- **Crystallize REAL-mode sandbox-default:** `--apply` REAL futás csak `crystallize-sandbox-*` branchen; main-en csak `VAULT_CRYSTALLIZE_ALLOW_MAIN=1` (DANGER) ([CLAUDE.md SV B-1 pipeline](/root/.claude/CLAUDE.md))
- **B-1 Apply-mode 4-rétegű safety-gate:** sandbox-branch + ENV-flag + script-gate + Critic-review (multi-layer-safety-gate ráadás-réteg) ([sv-5 crystallization automation ADR](../07-Decisions/2026-05-12%20sv-5%20crystallization%20automation%20arch.md))
- **B-2 Memory architecture:** SV-1 sandbox-on először pilot-elve, hetekkel később merge main-be (`sv-phase-b1-week4-milestone` git-tag) ([CLAUDE.md tag history](/root/.claude/CLAUDE.md))
- **GEPA real `gepa.optimize()` loop:** Custom GEPAAdapter sandbox-szerű külön folyamat, $0 cost ([sv-02-recursive-self-improvement](sv-02-recursive-self-improvement.md))
- **Predicate-remap atomic-write:** 761 fact predicate-remap APPLIED — sandbox-on dry-run ELŐSZÖR, csak utána main-merge ([MEMORY 2nd super-session](/root/.claude/projects/-root/memory/MEMORY.md))
- **Hostinger UpdraftPlus staging migration:** staging-environment (saját sandbox-analógia) — production migration ELŐTT mindig staging ([hostinger-updraftplus-staging-migration](hostinger-updraftplus-staging-migration.md))

## Mintázat

```
Tervezett mutation ──> Új branch: <feature>-sandbox-YYYYMMDD
                                │
                                ├─> RUN mutation a sandbox-on
                                ├─> Audit-log + Critic-review
                                ├─> 7-napos megfigyelés (revert-rate)
                                │
                                ▼
                        Ha revert-rate < 2%
                                │
                                ▼
                        git merge main + git-tag <milestone>
```

## Architektúrális szabályok

1. **Branch-naming convention:** `<feature>-sandbox-<purpose>-YYYYMMDD` (pl. `crystallize-sandbox-week21-ramp`)
2. **Script-gate branch-prefix check:** Az apply-script `git rev-parse --abbrev-ref HEAD` outputot ellenőriz; ha NEM `*-sandbox-*` és NINCS `_ALLOW_MAIN=1` flag → exit 1
3. **Main-merge csak git-tag-gel** — `sv-phase-b1-week4-milestone` minta; pre-merge állapot tag-elve, hogy revert-elhető
4. **Audit-event sandbox-vs-main megkülönböztetve** — `branch_type: sandbox|main`
5. **Sandbox-cleanup periodikus** — 30-nap inaktív sandbox-branch törölhető (de NEM force-push)
6. **NE shared-state sandbox** — ha 2 sandbox ugyanazt a fájlt írja, merge-conflict garantált

## Sandbox-types tier-mátrix

| Sandbox típus | Életciklus | Merge gate | Revert |
|--------------|-----------|------------|--------|
| `crystallize-sandbox-week*` | 7-14 nap | revert-rate <2% | branch drop |
| `gepa-sandbox-iter-*` | 1-2 nap | Pareto-front improvement | branch drop |
| `predicate-remap-sandbox-*` | <1 nap | NLI confidence ≥0.9 | branch drop |
| `schema-migration-sandbox-*` | <1 óra | smoke-test pass | `prisma migrate reset` |
| `apt-upgrade-sandbox-*` | <2 óra | reboot-test pass | snapshot restore |

## Anti-pattern

- ❌ **Direct main mutation magas-kockázatra** — bypass-olja Critic-review-t és revert-trace-t
- ❌ **Sandbox-on `git pull --force main`** — törli a sandbox-state-et; csak `git rebase main` clean working-tree-vel
- ❌ **2 sandbox-branch cross-merge** — chain-revert lehetetlen; mindig main mint közvetítő
- ❌ **`--no-verify` commit sandbox-on** — Critic-review skip; sandbox is full-gate

## Buktatók

- ⚠️ **Auto-save cron** (10 perces) végigfut a sandbox-on is, de a `vault-autosave` script aktuális branchen commitál; ne futtass sandbox-on hosszú feldolgozást aktív cron mellett
- ⚠️ **Detached HEAD** vault-batch `git mv` aktív Mac-session közben — sandbox-on KEZDD, NE main-en ([MEMORY](/root/.claude/projects/-root/memory/MEMORY.md))
- ⚠️ **Branch-prefix mismatch** — `crystallizesandbox-X` (kötőjel hiányzik) NEM ismeri fel; regex `^<feature>-sandbox-` szigorúan
- ⚠️ **Sandbox-on env-flag elfelejtése** — script-gate átengedi sandbox-on de mutation nem fut → silent skeleton-only

## Implementációs sablon

```bash
# script-gate vázlat
BRANCH=$(git rev-parse --abbrev-ref HEAD)
ALLOW_MAIN=${MY_FEATURE_ALLOW_MAIN:-0}
case "$BRANCH" in
    my-feature-sandbox-*) ok=1 ;;
    main|master)
        if [ "$ALLOW_MAIN" = "1" ]; then
            ok=1
            audit_log "DANGER: running on main with explicit flag"
        else
            echo "ERR: not on sandbox branch, refusing"; exit 1
        fi ;;
    *) echo "ERR: unknown branch type"; exit 1 ;;
esac
```

## Kapcsolódó

- [[multi-layer-safety-gate]] — sandbox-branch mint Layer 2
- [[env-flag-default-disabled-gate]] — `_ALLOW_MAIN=1` flag-gating
- [[auto-propagation-confidence-gate]] — auto-prop sandbox-only default
- [[rollback-revert-strategy-tiers]] — T5-T6 revert sandbox-on legkönnyebb
- [[audit-log-append-only-pattern]] — branch-type field minden record-on
- [[verification-step-before-claim]] — sandbox-on smoke-verify ELŐTT main-merge
