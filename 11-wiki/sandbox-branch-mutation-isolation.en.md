---
name: sandbox-branch-mutation-isolation
type: wiki
lang: en
translated_from: sandbox-branch-mutation-isolation
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#topic/git", "#pattern/isolation"]
---

# Sandbox-branch mutation isolation

## TL;DR

High-risk **auto-mutations** (apply-mode propagation, GEPA mutate, schema-migration, predicate-remap) **always run on a `<feature>-sandbox-*` branch**, never on `main`. Running on `main` is opt-in via a `<FEATURE>_ALLOW_MAIN=1` ENV-flag with an audit event. Merge only when 7-day sandbox-revert-rate < 2%.

## Background

- **REAL-mode sandbox default:** `--apply` REAL execution only on `<feature>-sandbox-*` branches; main only with `VAULT_<FEATURE>_ALLOW_MAIN=1` (DANGER)
- **Apply-mode 4-tier safety-gate:** sandbox-branch + ENV-flag + script-gate + Critic-review (multi-layer-safety-gate as an additional layer)
- **Memory architecture rollouts:** SV features piloted on sandbox first, merged into main weeks later (`<feature>-week<N>-milestone` git-tag)
- **GEPA real `gepa.optimize()` loop:** custom GEPAAdapter runs as a sandbox-like separate process, $0 cost
- **Predicate-remap atomic write:** large-scale fact predicate-remap APPLIED — sandbox dry-run FIRST, only then main-merge
- **Staging analogy:** any staging environment is the same idea — production migration NEVER without staging first

## The pattern

```
Planned mutation ──> New branch: <feature>-sandbox-YYYYMMDD
                              │
                              ├─> RUN mutation on the sandbox
                              ├─> Audit-log + Critic-review
                              ├─> 7-day observation (revert-rate)
                              │
                              ▼
                      If revert-rate < 2%
                              │
                              ▼
                      git merge main + git-tag <milestone>
```

## Architectural rules

1. **Branch-naming convention:** `<feature>-sandbox-<purpose>-YYYYMMDD` (e.g. `crystallize-sandbox-week21-ramp`)
2. **Script-gate branch-prefix check:** the apply script checks `git rev-parse --abbrev-ref HEAD`; if NOT `*-sandbox-*` and NO `_ALLOW_MAIN=1` flag → exit 1
3. **Main-merge only via git-tag** — `<feature>-week<N>-milestone` pattern; pre-merge state tagged so it can be reverted
4. **Audit event distinguishes sandbox vs main** — `branch_type: sandbox|main`
5. **Periodic sandbox cleanup** — 30-day inactive sandbox-branches can be deleted (but NOT force-pushed)
6. **NO shared-state sandboxes** — if two sandboxes write the same file, merge conflict guaranteed

## Sandbox-type tier matrix

| Sandbox type | Lifecycle | Merge gate | Revert |
|--------------|-----------|------------|--------|
| `crystallize-sandbox-week*` | 7-14 days | revert-rate <2% | branch drop |
| `gepa-sandbox-iter-*` | 1-2 days | Pareto-front improvement | branch drop |
| `predicate-remap-sandbox-*` | <1 day | NLI confidence ≥0.9 | branch drop |
| `schema-migration-sandbox-*` | <1 hour | smoke-test pass | `prisma migrate reset` |
| `apt-upgrade-sandbox-*` | <2 hours | reboot-test pass | snapshot restore |

## Anti-patterns

- ❌ **Direct main mutation for high-risk changes** — bypasses Critic-review and revert-trace
- ❌ **`git pull --force main` on sandbox** — destroys sandbox state; only `git rebase main` with clean working tree
- ❌ **Cross-merging two sandbox branches** — chain-revert becomes impossible; always go through main as intermediary
- ❌ **`--no-verify` commit on sandbox** — skips Critic-review; sandbox is also full-gated

## Pitfalls

- ⚠️ **Autosave cron** (e.g. every 10 minutes) runs on the sandbox too, and commits on the current branch; do not run long-running sandbox processing with an active autosave
- ⚠️ **Detached HEAD** during batch `git mv` with an active second editor — START on a sandbox branch, NOT main
- ⚠️ **Branch-prefix mismatch** — `crystallizesandbox-X` (missing hyphen) is NOT recognised; regex `^<feature>-sandbox-` strictly
- ⚠️ **Forgetting the env-flag on sandbox** — script-gate lets it through on sandbox, but mutation does not run → silent skeleton-only

## Implementation template

```bash
# script-gate skeleton
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

## Related

- [[multi-layer-safety-gate]] — sandbox-branch as Layer 2
- [[env-flag-default-disabled-gate]] — `_ALLOW_MAIN=1` flag-gating
- [[auto-propagation-confidence-gate]] — auto-prop sandbox-only default
- [[rollback-revert-strategy-tiers]] — tiered revert easiest on sandbox
- [[audit-log-append-only-pattern]] — branch-type field on every record
- [[verification-step-before-claim]] — sandbox smoke-verify BEFORE main-merge
