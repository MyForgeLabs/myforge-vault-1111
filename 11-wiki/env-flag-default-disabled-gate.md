---
name: env-flag-default-disabled-gate
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#pattern/opt-in", "#topic/rollout"]
---

# ENV-flag default-disabled activation gate

## TL;DR

Magas-kockázatú **új feature / pipeline-step / auto-mutation** **default-DISABLED**-del megy ki, **explicit `ENV_FLAG=1`** kell az aktiváláshoz. Layer-1 a [[multi-layer-safety-gate]]-ben. Rollback = `unset ENV_FLAG` (NEM kód-revert). Cross-source: 22+ fact, 3 source-type.

## Háttér (3+ source-evidence)

- **Crystallize REAL-mode:** `VAULT_CRYSTALLIZE_APPLY=1` + `VAULT_CRYSTALLIZE_REAL=1` — NÉLKÜLE csak skeleton "would-have-applied" audit, mutation NEM történik ([CLAUDE.md SV B-1 pipeline](/root/.claude/CLAUDE.md))
- **Sprint Day 0 backout:** Új sprint-feature `<sprint>_MODE=disabled` env-var-ral indul; activate explicit flag-flip-pel ([sprint-day-0-skeleton-first](sprint-day-0-skeleton-first.md))
- **Multi-layer safety-gate Layer 1:** "ENV-flag default-disabled" az első réteg a 4-rétegű gate-ben ([multi-layer-safety-gate](multi-layer-safety-gate.md))
- **G-Eval v0.3 opt-in:** `VAULT_GEVAL_VERSION=v03` — v0.3 nem default-shift (53% Pass-recall), opt-in ENV-flag mögé tette mérnöki őszinte finding alapján ([g-eval-bias-mitigation-pattern](g-eval-bias-mitigation-pattern.md))
- **B-7 entity-tipizáltság ramp:** `VAULT_CRYSTALLIZE_AUTO=1`, `VAULT_CRYSTALLIZE_ALLOW_MAIN=1` — minden új automatizmus külön ENV-flag mögé kerül (env-defaults tracker `/root/.vault-config/env-defaults.md`)

## Mintázat

```
            ┌─ default behaviour: DISABLED, skeleton-only / shadow / dry-run
ENV_FLAG ───┤
            └─ EXPLICIT =1: enable + audit-log + Critic-review hook
```

**Layer-stacking** kombinálva más gate-ekkel:

| Layer | Példa | Mechanizmus |
|-------|-------|-------------|
| 1 ENV-flag | `VAULT_CRYSTALLIZE_APPLY=1` | shell env, opt-in |
| 2 script-gate | branch-check `crystallize-sandbox-*` | git-branch prefix kötelező |
| 3 git-hook | pre-commit: lint + Critic | hook futás kötelező |
| 4 review | Critic-review subagent | adversarial-review-skill futtat |

## Rollout-protokoll

1. **Week 1 (shadow):** ENV-flag létezik, default OFF, audit-log feltöltődik dry-run-rekkel
2. **Week 2 (opt-in):** ENV-flag dokumentálva `env-defaults.md`-ben, néhány session manuálisan ON
3. **Week 3 (ramp):** Ha 7-napos revert-rate <2% → threshold-ramp + flag default-on jelölt
4. **Week 4 (default-on jelölt):** Külön ADR + audit-trend → flag default-on
5. **Sosem:** Hard-coded ON kód-mergével ENV-flag nélkül

## Buktatók

- ⚠️ **Env-var typo** — `VAULT_CRYSTALIZE_APPLY` ≠ `VAULT_CRYSTALLIZE_APPLY`; mindig használj `env-defaults.md`-t referenciaként
- ⚠️ **Flag-explosion** — 15+ flag → audit nehéz; csak Tier-S kockázatú feature-höz adj új flag-et
- ⚠️ **`set -e` + `${VAR:-$(cmd)}` parameter-expansion** öl flag-detect command-substitution exit-1-re — fix `2>/dev/null || true` (5 11.11* script patcholt 2026-05-18)
- ⚠️ **Persistent-shell-export ne legyen `~/.bashrc`-ben** — ez "rejtett default-on"; csak `~/.vault-config/env-defaults.md`-be regisztrálj

## Implementációs sablon

```bash
# script.sh fej
APPLY=${MY_FEATURE_APPLY:-0}
if [ "$APPLY" != "1" ]; then
  echo "[skeleton] would-have-done X (set MY_FEATURE_APPLY=1 to enable)"
  exit 0
fi
# REAL mutation here, AFTER all gates passed
```

## Kapcsolódó

- [[multi-layer-safety-gate]] — 4-rétegű gate; ENV-flag = Layer 1
- [[sprint-day-0-skeleton-first]] — Day 0 backout = ENV-flag-flip
- [[crystallize-threshold-ramp]] — ENV-flag-flip a ramp-protokoll lépéseiben
- [[audit-log-append-only-pattern]] — flag-state minden mutationben loggolva
- [[g-eval-bias-mitigation-pattern]] — opt-in ENV gate v0.3-ra
