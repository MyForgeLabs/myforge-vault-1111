---
name: 11.11crystallize threshold-ramp protocol
type: wiki
tags: ["#type/wiki", "vault-ko", "crystallize", "threshold", "ramp", "safety"]
created: 2026-05-17
updated: 2026-05-17
status: stable
---

# 11.11crystallize threshold ramp protocol

A `11.11crystallize` auto-propagation a `~/.vault-config/crystallize-threshold.txt` hot-reloadable konfigurációval skálázódik. Cél: óvatosan emelkedni a Shadow (1.0) → Conservative (0.95) → Aggressive (0.85) szinten, közben revert-rate-et figyelni.

## A 3 üzemmód

| Mód | Threshold | Cél auto-rate | Revert-rate budget |
|---|---|---|---|
| **Shadow** | 1.0 | 0% (csak naplóz) | n/a |
| **Conservative** | 0.95 | 30%+ | <5% |
| **Aggressive** | 0.85 | 80% | <5% |

## Hot-reload threshold

```bash
echo "0.95" > /root/.vault-config/crystallize-threshold.txt
```

A script minden futtatáskor olvassa, nincs restart.

## A ramp-protocol

### 1. Shadow (1.0) — felmérés, no-op

- Cél: G-Eval-score eloszlás mérése. Semmi sem propagálódik (`route=auto-prop` 0 lesz).
- Kilépés: 50+ Learning bullet átment, score eloszlás látszik, `vault-crystallize-monitor` ad eligible-jelet.

### 2. Conservative (0.95) — top-5% bullet auto

- Cél: 30%+ auto-rate, >95% pass-rate.
- Cél (revert): <5% (azaz a user nem von vissza többet mint 5%-ot).
- Lépés bal-felé: ha 2 hét + 30+ apply, és revert <2%, és auto-rate <30% → 0.90-re mehet.
- Lépés jobbra: ha >5% revert → 1.0-ra (rollback) + root-cause-analysis a `vault-ko-conflicts-audit`-ban.

### 3. Aggressive (0.85) — 80% auto-rate cél

- Cél: 80% auto-rate, >90% pass-rate.
- **Backout-trigger:** >5% revert → bump `+0.05` automatikusan (kézzel a `crystallize-threshold.txt`-ben + ADR-be a root-cause).
- Sandbox-mode mindig: REAL flow csak `crystallize-sandbox-*` branchen indítható (nem main!), majd PR-rel megy fel.

## Monitoring eszközök

### vault-crystallize-monitor

```bash
vault-crystallize-monitor                 # text summary
vault-crystallize-monitor --weeks 12      # longer window
vault-crystallize-monitor --json          # for cron + alerting
```

Kimenet:
- Per-week scored / auto-prop / applied / revert
- Aggregált auto-rate és revert-rate
- **Threshold-ajánlás** (`raise`/`lower`/`hold`) a backout-rule szerint

Heti cron-osítható (a `vault-ko-conflicts-audit` mellé Sunday 04:35).

### Backout-trigger

Manuális revert egy bullet-re:
```bash
git log --oneline --grep "crystallize\[auto\]" | head -20    # listáz applied commit-okat
git revert <commit-hash>                                       # vissza, audit-logban event=apply_reverted lesz külön kezelve
```

A revert-rate számolás `apply_reverted` audit-event-ekből megy — ezeket a `vault-crystallize-revert` parancs (későbbi sprint) automatikusan írja.

## Mai státusz (2026-05-17 W20)

- **Threshold:** 0.95 (Conservative shadow → soft-on)
- **Auto-rate:** 38.1% (16/42 a héten)
- **Revert-rate:** 0% (4 applied, 0 visszavont — REAL mode aznap landolt)
- **Suggestion:** `hold` — insufficient applied volume (<10) ahhoz hogy a `0.85` ramp megalapozott legyen
- **Következő kapu:** W21-22 során 30+ applied bullet, ha revert <2% és auto >35% → **threshold 0.90-re mehet**
- **Aggressive (0.85)** földetérése a Week 5-6 céldátumon (W22-W23 körül) ha addig stabil

## Backout-plan a teljes apply-flow-ra

```bash
# Disable apply-mode azonnal (no env-var → no apply):
unset VAULT_CRYSTALLIZE_APPLY
unset VAULT_CRYSTALLIZE_REAL

# Threshold-ramp visszavonása:
echo "1.0" > /root/.vault-config/crystallize-threshold.txt

# Sandbox-branchek törlése:
git branch | grep crystallize-sandbox- | xargs -r git branch -D
```

A `~/.vault-config/crystallize-threshold.txt` file törlésével is működik — a script default 1.0-ra esik vissza.

## Kapcsolódó

- [[multi-layer-safety-gate]] — a 4 rétegű védelmi háló a REAL-mode körül
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — eredeti ADR (Backout szabályok)
- [[../02-Projects/superintelligent-vault]] — B-1 sprint host
- `/usr/local/bin/vault-crystallize-monitor` — health-checker
- `/usr/local/bin/11.11crystallize` — a propagation pipeline
- `/root/.vault-config/crystallize-threshold.txt` — hot-reloadable threshold
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[backout-trigger-pattern]] (sem-rokon, score=0.32)
- [[ufw-limit-rate-limit-pattern]] (sem-rokon, score=0.52)
