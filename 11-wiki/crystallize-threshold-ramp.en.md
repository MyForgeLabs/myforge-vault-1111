---
name: 11.11crystallize threshold-ramp protocol
type: wiki
tags: ["#type/wiki", "vault-ko", "crystallize", "threshold", "ramp", "safety", "lang/en"]
created: 2026-05-17
updated: 2026-05-19
status: stable
lang: en
translated_from: crystallize-threshold-ramp.md
---

# 11.11crystallize threshold ramp protocol

The `11.11crystallize` auto-propagation scales via the `~/.vault-config/crystallize-threshold.txt` hot-reloadable config. Goal: cautiously ramp from Shadow (1.0) → Conservative (0.95) → Aggressive (0.85) while watching revert-rate.

## The 3 modes

| Mode | Threshold | Auto-rate target | Revert-rate budget |
|---|---|---|---|
| **Shadow** | 1.0 | 0% (log only) | n/a |
| **Conservative** | 0.95 | 30%+ | <5% |
| **Aggressive** | 0.85 | 80% | <5% |

## Hot-reload threshold

```bash
echo "0.95" > /root/.vault-config/crystallize-threshold.txt
```

The script reads it on every run — no restart needed.

## The ramp protocol

### 1. Shadow (1.0) — assessment, no-op

- Goal: measure G-Eval score distribution. Nothing propagates (`route=auto-prop` is 0).
- Exit: 50+ Learning bullets passed, distribution clear, `vault-crystallize-monitor` signals eligibility.

### 2. Conservative (0.95) — top-5% bullets auto

- Goal: 30%+ auto-rate, >95% pass-rate.
- Goal (revert): <5% (user reverts no more than 5%).
- Step left: if 2 weeks + 30+ apply, revert <2%, auto-rate <30% → move to 0.90.
- Step right: if >5% revert → 1.0 (rollback) + root-cause-analysis via `vault-ko-conflicts-audit`.

### 3. Aggressive (0.85) — 80% auto-rate target

- Goal: 80% auto-rate, >90% pass-rate.
- **Backout trigger:** >5% revert → bump `+0.05` automatically (manually in `crystallize-threshold.txt` + root-cause to ADR).
- Sandbox-mode always: REAL flow only runs on `crystallize-sandbox-*` branch (NOT main), then merges via PR.

## Monitoring tools

### vault-crystallize-monitor

```bash
vault-crystallize-monitor                 # text summary
vault-crystallize-monitor --weeks 12      # longer window
vault-crystallize-monitor --json          # for cron + alerting
```

Output:
- Per-week scored / auto-prop / applied / revert
- Aggregated auto-rate and revert-rate
- **Threshold recommendation** (`raise`/`lower`/`hold`) per backout-rule

Weekly-cron-able (alongside `vault-ko-conflicts-audit` Sunday 04:35).

### Backout trigger

Manual revert for a bullet:
```bash
git log --oneline --grep "crystallize\[auto\]" | head -20    # list applied commits
git revert <commit-hash>                                       # revert; audit-log event=apply_reverted handled separately
```

Revert-rate counting reads from `apply_reverted` audit-events — these are written by the `vault-crystallize-revert` command (later sprint).

## Current status (2026-05-17 W20)

- **Threshold:** 0.95 (Conservative shadow → soft-on)
- **Auto-rate:** 38.1% (16/42 this week)
- **Revert-rate:** 0% (4 applied, 0 reverted — REAL mode landed that day)
- **Suggestion:** `hold` — insufficient applied volume (<10) to justify the `0.85` ramp
- **Next gate:** during W21-22, 30+ applied bullets, if revert <2% and auto >35% → **threshold to 0.90**
- **Aggressive (0.85)** landing target: Week 5-6 (around W22-W23) if stable

## Full apply-flow backout plan

```bash
# Disable apply-mode immediately (no env-var → no apply):
unset VAULT_CRYSTALLIZE_APPLY
unset VAULT_CRYSTALLIZE_REAL

# Threshold-ramp rollback:
echo "1.0" > /root/.vault-config/crystallize-threshold.txt

# Delete sandbox branches:
git branch | grep crystallize-sandbox- | xargs -r git branch -D
```

Deleting `~/.vault-config/crystallize-threshold.txt` also works — script defaults to 1.0.

## Related

- [[multi-layer-safety-gate]] — the 4-layer protection net around REAL-mode
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — original ADR (backout rules)
- [[../02-Projects/superintelligent-vault]] — B-1 sprint host
- `/usr/local/bin/vault-crystallize-monitor` — health-checker
- `/usr/local/bin/11.11crystallize` — the propagation pipeline
- `/root/.vault-config/crystallize-threshold.txt` — hot-reloadable threshold
- [[backout-trigger-pattern]] (sem-related, score=0.32)

## Hungarian original

[[crystallize-threshold-ramp]]
