---
name: env-flag-default-disabled-gate
type: wiki
lang: en
translated_from: env-flag-default-disabled-gate
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#pattern/opt-in", "#topic/rollout"]
---

# ENV-flag default-disabled activation gate

## TL;DR

A high-risk **new feature / pipeline step / auto-mutation** ships **default-DISABLED**, with an explicit `ENV_FLAG=1` required for activation. This is Layer-1 in [[multi-layer-safety-gate]]. Rollback = `unset ENV_FLAG` (NOT a code revert).

## Background

- **REAL-mode application:** typically requires `<FEATURE>_APPLY=1` + `<FEATURE>_REAL=1` — without them, only a skeleton "would-have-applied" audit log runs, no mutation
- **Sprint Day 0 backout:** new sprint features launch with `<sprint>_MODE=disabled` env var; activate via explicit flag-flip
- **Multi-layer safety-gate Layer 1:** "ENV-flag default-disabled" is the first layer of the 4-tier gate
- **Eval-version opt-in:** e.g. `VAULT_GEVAL_VERSION=v03` — a stricter version may not become default, opt-in ENV-flag instead based on honest calibration findings
- **Auto-process gates:** every new automation lives behind its own ENV-flag tracked in an `env-defaults.md` registry

## The pattern

```
            ┌─ default behaviour: DISABLED, skeleton-only / shadow / dry-run
ENV_FLAG ───┤
            └─ EXPLICIT =1: enable + audit-log + Critic-review hook
```

**Layer-stacking** combined with other gates:

| Layer | Example | Mechanism |
|-------|---------|-----------|
| 1 ENV-flag | `VAULT_CRYSTALLIZE_APPLY=1` | shell env, opt-in |
| 2 script-gate | branch-check `crystallize-sandbox-*` | git-branch prefix required |
| 3 git-hook | pre-commit: lint + Critic | hook execution required |
| 4 review | Critic-review subagent | adversarial-review skill runs |

## Rollout protocol

1. **Week 1 (shadow):** ENV-flag exists, default OFF, audit-log fills with dry-runs
2. **Week 2 (opt-in):** ENV-flag documented in `env-defaults.md`, a few sessions manually ON
3. **Week 3 (ramp):** if 7-day revert-rate <2% → threshold-ramp + flag default-on candidate
4. **Week 4 (default-on candidate):** separate ADR + audit trend → flag becomes default-on
5. **Never:** hard-coded ON via code merge without an ENV-flag

## Pitfalls

- ⚠️ **Env-var typos** — `VAULT_CRYSTALIZE_APPLY` ≠ `VAULT_CRYSTALLIZE_APPLY`; always use `env-defaults.md` as reference
- ⚠️ **Flag explosion** — 15+ flags → audit becomes hard; only add a new flag for Tier-S risk features
- ⚠️ **`set -e` + `${VAR:-$(cmd)}` parameter expansion** kills flag-detect command-substitution on exit-1 — fix with `2>/dev/null || true`
- ⚠️ **Persistent shell export must NOT live in `~/.bashrc`** — that is a "hidden default-on"; only register in `~/.vault-config/env-defaults.md`

## Implementation template

```bash
# script.sh head
APPLY=${MY_FEATURE_APPLY:-0}
if [ "$APPLY" != "1" ]; then
  echo "[skeleton] would-have-done X (set MY_FEATURE_APPLY=1 to enable)"
  exit 0
fi
# REAL mutation here, AFTER all gates passed
```

## Related

- [[multi-layer-safety-gate]] — 4-tier gate; ENV-flag = Layer 1
- [[sprint-day-0-skeleton-first]] — Day 0 backout = ENV-flag-flip
- [[crystallize-threshold-ramp]] — ENV-flag-flip in the ramp protocol steps
- [[audit-log-append-only-pattern]] — flag state logged on every mutation
- [[g-eval-bias-mitigation-pattern]] — opt-in ENV gate for stricter version
