---
name: 2026-05-18 B-1 Aggressive ramp data prep
type: audit
tags: ["#axis/sv-1", "#topic/crystallization", "#topic/threshold", "#topic/ramp-prep", "aggressive-ramp", "sv-1", "B-1", "milestone-tracking"]
created: 2026-05-18
updated: 2026-05-19
status: forecast
axis: B-1
session: 2026-05-19-obsidian-vault-pro
related:
  - 06-Audits/2026-05-17 B-1 Aggressive 0.85 ramp risk-assessment.md
  - 06-Audits/crystallize-health.json
  - 07-Decisions/2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective.md
  - 11-wiki/crystallize-threshold-ramp.md
---

# B-1 Aggressive ramp data prep — 30-applied-bullet milestone-tracking (2026-05-19)

> [!info] Cél
> A `sv-phase-b1-done` git-tag-hez **30+ applied bullet** szükséges Conservative-on (0.95), revert <2%, ≥2 hét stabilitás. Jelenleg **4 applied bullet** van rögzítve (mind W20-ban, 2026-05-17). Az audit forecast-olja a milestone-elérést, és értékeli a **synthetic ramp** opciót.

## 1. Current applied count + heti rate

### Audit-log forensics (`crystallize-log.jsonl`)

```
$ grep '"event": "apply_real"' crystallize-log.jsonl | wc -l
14

$ grep '"event": "apply_real"' crystallize-log.jsonl | grep -o '"executed": [a-z]*' | sort | uniq -c
     10 "executed": false   ← dry-run skeleton ("would-have-applied" audit-only)
      4 "executed": true    ← REAL writes (sandbox-branch realmode-smoketest)
```

Mind a 14 event ugyanazon a 2-perces ablakon belül íródott (2026-05-17 18:47:54 + 18:48:50), a `realmode-smoketest` branch-en. Tehát ez **NEM 4 organic apply**, hanem **1 smoke-test 7-bullet-en + 1 második 7-bullet** futás, amelyből a Critic 4 bullet-et `approve`-olt / `modify`-olt, 6-ot `discard`-olt. A monitor `applied_real: 4` ezt aggregálja `executed=true`-ra szűrve.

| Metrika | Érték |
|---|---:|
| `apply_real` events total | 14 |
| `executed: true` count | **4** |
| Critic `approve` | 3 |
| Critic `modify` | 1 |
| Critic `discard` | 6 |
| Distinct sessions | **1** (`2026-05-15-mfl-voice-sprint-1`) |
| Distinct weeks | **1** (W20) |
| Reverted | 0 (revert-rate: 0%) |

### "Heti rate" valós-becslés

Mivel a 4 applied **smoke-test artifact**, NEM organikus weekly-flow, a **valós heti rate jelenleg = 0** (W17-W21 között **0 production-`--apply` futás** történt, csak 1 manuális smoke W20-ban).

A `2026-05-17 B-1 Aggressive 0.85 ramp risk-assessment` 5-session dry-run-routing-aggregátuma viszont mutatja a **PRODUCT-PROXY HETI RATE-ET**: 5 session × 29 bullet × 62.1% auto-prop = **18 hipotetikus apply / hét**, ha a `VAULT_CRYSTALLIZE_APPLY=1 VAULT_CRYSTALLIZE_REAL=1` flag-ek bekapcsolnának minden zárásra. Ez **OPT-IN HIGH-RISK flag** marad (lásd `env-defaults.md` — `SOSEM default-shift`).

## 2. Forecast a 30-applied milestone-ra

### Forgatókönyv A — Organic flow (current trajectory)

| Hét | Apply trigger | Várt new applied | Cumulative | Milestone? |
|---|---|---:|---:|:---:|
| W20 (lezárt) | 1 smoke-test 4-bullet | 4 | **4** | — |
| W21 | 0 (Apply-flag default-OFF, manuális opt-in) | 0 | 4 | ❌ |
| W22 | 0 | 0 | 4 | ❌ |
| ... | ... | ... | ... | ❌ never |

**Konklúzió:** Organic-flow-ban **SOHA nem érünk el 30 applied bullet-et**, mert a `VAULT_CRYSTALLIZE_APPLY` HIGH-risk flag, default OFF, és senki nem futtatja manuálisan minden zárás után.

### Forgatókönyv B — Opt-in shadow-flow W21-től (recommended)

A user a következő 5 session-záráskor manuálisan futtatja:
```bash
export VAULT_CRYSTALLIZE_APPLY=1 VAULT_CRYSTALLIZE_REAL=1
11.11crystallize <slug> --scorer claude-code --with-context --apply
```

A `2026-05-17 risk-assessment` 5-session-átlaga: **3.6 auto-prop / session × Critic-pass-rate ~70%** → **~2.5 organic-apply / session**.

| Hét | Sessions × apply / session | New applied | Cumulative | Milestone? |
|---|---|---:|---:|:---:|
| W21 | 5 × 2.5 | ~13 | **17** | ❌ |
| W22 | 5 × 2.5 | ~13 | **30** | ✅ **REACHED** |
| W23 | 5 × 2.5 | ~13 | 43 | ✅ stabilization-week |

**Várt milestone-dátum:** **2026-05-31** (W22 zárása), feltéve hogy a user heti 5 zárást futtat `--apply`-jel + a Critic-discard-rate marad ~43% (6/14 a smoke-ban).

### Forgatókönyv C — Big-batch backfill (gyors, de NEM organikus)

Futtatható `11.11crystallize` minden lezárt session-en (08-Sessions/ × 18 session × ~7 bullet/session = 126 candidate). Becsült:

- ~126 × 62.1% auto-prop = ~78 candidate
- × ~70% Critic-pass = **~55 applied**
- Idő: ~2-3 óra subagent-fanout-tal (~$0)
- **Kockázat:** ⚠ NEM organic-flow, statistical-bias (csak retro-session), revert-rate-figyelési-érték kérdéses (a user már átolvasta a session-eket, "nem fog revert-elni" → biased low-revert-rate)

## 3. Synthetic ramp opció: érdemes-e most?

### Kandidátlista a synthetic-ramp-ben

A "synthetic" itt nem fiktív bullet-et jelent, hanem **retro-application sandbox-branch-en**: a lezárt session-eket re-futtatni `--apply`-jel.

| Pro | Contra |
|---|---|
| ✅ Gyorsan elérjük a 30-mark-ot (~3 óra) | ❌ **Critic-review-bias:** ugyanaz a Claude-instance ítél, mint ami a bullet-et eredetileg írta → confirmation-bias |
| ✅ $0 cost (subagent-fanout) | ❌ **Revert-bias:** retro-session-eknél a user már nem revert-el (lélektani sunk-cost), így a revert-rate-mérés meaningless |
| ✅ Idempotens (bullet_hash-dedup van) | ❌ **A B-1 acceptance-kritérium szellemét sérti:** "30+ applied **Conservative mode-ban**" — implicit organic-flow-szándék |
| ✅ Vault stable, 0 file-corruption-risk (sandbox-branch + atomic-write + Critic-review) | ❌ **Time-cost:** 3 óra non-trivial vs várj-1-hét organic-flow |

### Verdict: **❌ MOST NE futtassunk synthetic ramp-et**

**Indoklás:**

1. A `2026-05-17 risk-assessment` Opció A (PASS / Stay status quo) szerint **a 0.85 már de-facto él a 11-wiki/-en** a per-target YAML override-okon keresztül — a **forecast B** organikus pathway 2 héten belül elér a milestone-hez.
2. A synthetic-ramp-ben a **Critic-review confirmation-bias** csökkenti a kísérlet diagnostic-value-jét — a sprint-exit-criteria szellemét sérti.
3. **Daemon-prereq:** ahogy a [[2026-05-18 B-3 NLI default-shift mérés]] pár-audit megjegyzi, a `vault-nli.service` `inactive`, és a coherence-check is csak 4-sample. Ezeket előbb stabilizálni kell (W21 daemon-fix), azután organic-flow-ban gyűjteni shadow-data-t **mindhárom layer-re** párhuzamosan.

### Mit CSINÁLJUNK helyette W21-ben

| Lépés | Parancs / akció | Hatás |
|---|---|---|
| **(1) Daemon-fix** | `systemctl edit vault-nli.service` (Description URL fix) + `start` | Warm NLI socket |
| **(2) Coherence shadow ON** | `export VAULT_COHERENCE_CHECK=1` az `/etc/environment`-be | Layer 2.6 minden zárásra |
| **(3) NLI shadow ON** | `export VAULT_NLI_VETO=1` (shadow, NEM apply) | Layer 2.5 minden zárásra |
| **(4) Apply opt-in 2-3 valódi session-en** | Csak ahol a user meg-előzetes-olvasta a Learnings-t | ~5-7 new organic-applied |
| **(5) W21 záró audit** | `vault-crystallize-monitor --json` | Decision-point: stay vs adjust |

## 4. Mérnöki őszinte — mi kell még a `sv-phase-b1-done` git-tag-hez

A `2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective` szerint a sprint-exit kritérium:

> "W23: ha 0.85 stabil 2 héten át (revert <5%, auto >80%, pass >90%) → `sv-phase-b1-done` tag + retro."

### Acceptance-mátrix (current vs target)

| Kritérium | Target | Current | Gap | ETA |
|---|---|---|---|---|
| Applied bullet count | ≥30 (≥2 hét) | 4 (1 smoke-burst W20) | -26 | W22 zárása (organic) |
| Auto-rate | >80% | 37.5% W20 (de 62.1% a per-target YAML-on a dry-run audit szerint) | mérési-mód-tisztázás kell | W21 monitor re-read |
| Revert-rate | <5% | 0% (4/0) | ✅ MEET (zero-trial) | — |
| Pass-rate | >90% | n/a (manuál-eval nincs methodológia-doc) | dokumentáció-rés | W21 ADR-skeleton |
| Conservative stability | 2 hét | 1 hét (W20) | -1 hét | W21 vége |
| Aggressive ramp aktiválva | 0.85 default | de-facto YES (11-wiki/), de-jure NO (default=0.95) | semantika-rés (lásd risk-assessment) | W22 ADR-clarify |
| NLI-veto shadow | ≥10 sample / 2 hét | 7 / 1 hét | -3 sample / -1 hét | W21 (pair-audit) |
| Coherence-veto shadow | ≥10 sample / 2 session | 4 / 1 session | -6 sample / -1 session | W21 (pair-audit) |

### Még hiányzó deliverable-ek a sprint-exit-hez

1. **Pass-rate manual-eval methodology doku** — sehol nincs leírva, hogyan mérjük a "pass-rate >90%"-ot. Javaslat: 30-sample random apply → manuál-binárus accept/reject → percentage. ADR-skeleton kell.
2. **`crystallize-revert <bullet-hash>` script** — most kézi `git revert <commit-hash>`. A wiki ezt "későbbi sprint" megjegyzéssel hivatkozza, de a `sv-phase-b1-done` retro alapján az exit-kritérium MAJDNEM a revert-rate-mérésen áll, és a script hiánya **adatminőség-kockázat**.
3. **Auto-disable trigger implementation** — szintén "csak doku" a retro szerint.
4. **NLI + Coherence soft-veto default-shift** — pair-audit a [[2026-05-18 B-3 NLI default-shift mérés]]-ben, W22-W23 timeline.
5. **B-1 retrospective ADR** — `sv-phase-b1-done` tag után, NEM most.

### Realisztikus `sv-phase-b1-done` ETA

**2026-06-07 (W23 vége)** — feltéve hogy:
- W21: daemon-fix + shadow-ON + 2-3 organic-apply (~5 bullet)
- W22: 5-session organic-apply (~13 bullet) + monitor `default_shift_recommended` mindhárom layer-re flip → cumulative 17+ applied
- W23: stabilization-hét, 2 hét × 0% revert verifikálva, ADR-draft + tag

**Pessimistic ETA: 2026-06-21** (W25 vége) — ha a daemon-fix csúszik vagy a Critic-discard-rate emelkedik (>50%).

## 5. Mit NE csináljunk

- ❌ **`VAULT_CRYSTALLIZE_ALLOW_MAIN=1`** — sosem (env-defaults Risk: CRITICAL)
- ❌ **Synthetic-ramp 18 session retro-apply** — bias-csapda, lásd 3. szekció
- ❌ **Default 0.95 → 0.85 mozdítás most** — 0-bullet effect a per-target YAML miatt (risk-assessment Opció A)
- ❌ **Tag-elni `sv-phase-b1-done`-t a 4-applied-on** — explicit ≥30 kritérium

## Kapcsolódó

- [[2026-05-17 B-1 Aggressive 0.85 ramp risk-assessment]] — dry-run routing 29 bullet-en
- [[2026-05-18 B-3 NLI default-shift mérés]] — pair-audit (today, soft-veto layer)
- [[2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective]] — sprint exit-criteria forrás
- [[../11-wiki/crystallize-threshold-ramp]] — ramp-protocol playbook
- [[../11-wiki/multi-layer-safety-gate]] — 4-rétegű safety pattern
- [[../05-Memory/env-defaults]] — ENV-flag tracker
- [[../02-Projects/superintelligent-vault]] — szülő-projekt
