---
name: 2026-05-18 B-3 NLI default-shift mérés
type: audit
tags: ["#axis/sv-1", "#axis/sv-3", "#topic/nli", "#topic/crystallization", "#topic/default-shift", "nli", "shadow-monitoring", "B-3", "L2.5"]
created: 2026-05-18
updated: 2026-05-19
status: measurement
axis: B-3
session: 2026-05-19-obsidian-vault-pro
related:
  - 06-Audits/2026-05-17 B-1 NLI Layer 2.5 integration.md
  - 06-Audits/shadow-monitoring-trend.md
  - 06-Audits/crystallize-health.json
  - 05-Memory/env-defaults.md
---

# B-3 NLI Layer 2.5 default-shift mérés (2026-05-19)

> [!info] Cél
> A `crystallize-health.json` `nli.default_shift_recommended: false` mert csak 7 NLI sample / 1 hét / 1 session van rögzítve a `crystallize-log.jsonl`-ben. A jelen audit a **sample-bővítés feasibility-jét + agreement-rate mérést** vizsgálja, és eldönti, hogy a `VAULT_NLI_VETO=0 → 1` default-shift **most ajánlott-e**.

## 1. Sample-méret előtte / utána

### Előtte (current snapshot, `crystallize-monitor --json` 2026-05-19 04:47)

| Metrika | Érték | Kritérium | Pass? |
|---|---:|:---:|:---:|
| NLI-tagged bullet | **7** | ≥10 | ❌ |
| Sessions covered | **1** (`2026-05-15-mfl-voice-sprint-1`) | ≥2 | ❌ |
| Weeks covered | **1** (W20) | ≥2 | ❌ |
| Agreement rate | **100.0%** (7/7 pass) | ≥75% | ✅ |
| Downgrade rate | **0.0%** (0/7) | <20% | ✅ |
| Entail-prob mean | 0.4749 | — | — |
| Contra-prob mean | 0.26 | — | — |

**Diagnózis:** A **kvalitatív** kritériumok (agreement, downgrade) tökéletesen teljesülnek; a **kvantitatív** (sample-size, weeks, sessions) blokkolnak.

### Sample-bővítés bemenete — W17-W21 session-pool

A `08-Sessions/2026-05-1[5-9]*.md`-ben **18 session × 133 Learning-bullet** van. Ezekből a `crystallize-log.jsonl`-be **csak az `apply_real` event-tel rögzített 14 bullet** ment, és **NLI-tag-et csak 7 kalibrációs minta** kapott (a 2026-05-17 21:21Z `eval-l2-nli-calibration-20260517T212105Z.jsonl`-ből). A többi 126 bullet a `mock` scorer-en futott, NLI nélkül.

**Sample-bővítés stratégia:**

| Opció | Mit csinál | Várt sample | Idő | Kockázat |
|---|---|---:|---:|---|
| **A. Backfill `eval-l2-nli-judge --input-file`** a session-bullet-eken | 133 bullet → bullet+provenance JSONL → NLI batch | +133 | ~25-40 perc (10s/bullet, NLI-daemon nélkül) | ✅ ALACSONY — read-only |
| **B. Live NLI-tag a következő 3 zárás során** (`VAULT_NLI_VETO=1`) | natural-flow shadow-data | +20-30 | 1 hét | ✅ ALACSONY — már a B-1 audit ramp-W21 lépésében ajánlott |
| **C. Calibration-snapshot replay** (`--calibrate --samples 30 --snapshot`) | G-Eval vs NLI paired 30 minta | +30 | ~5 perc + NLI-warmup ~30s | ✅ ALACSONY — már bevett pattern |

> [!warning] vault-nli.service jelenleg `inactive`
> `systemctl status vault-nli.service` → daemon **NOT running**, socket `/run/vault-nli.sock` hiányzik. A unit-file path-resolution-hiba (file://%-encoded URL `Description=`-en) ignorable warning, de a service nincs elindítva. Az `eval-l2-nli-judge` `--server` flag nélkül cold-start módban megy (~10s/bullet vs ~1s warm).

### Utána (becsült, ha mindhárom opció lefut)

| Metrika | Várt érték | Kritérium | Pass? |
|---|---:|:---:|:---:|
| NLI-tagged bullet | **~190** (7 + 133 + 30 + 20) | ≥10 | ✅ |
| Sessions covered | **18** (W17-W21 pool) | ≥2 | ✅ |
| Weeks covered | **3-4** (W17-W21) | ≥2 | ✅ |

## 2. Agreement-rate + downgrade-rate mérés

### Verifikált mérés (current 7-sample window)

A `crystallize-log.jsonl` 7 NLI-tagged record-ja (mind `mfl-voice-sprint-1`):

| bullet preview | g_eval_route | nli_verdict | nli_pass_vote | nli_entailment_prob |
|---|---|---|:---:|---:|
| `NotebookLM research wait --import-all PÁRHUZAMOSAN…` | auto-prop | entailment | ✅ | 0.6299 |
| `NotebookLM ask Chat request timed out ~30%…` | discard | neutral | ❌ | 0.1903 |
| (és további 5 entailment-vote) | — | entailment | ✅ | — |

- **Agreement rate** (NLI-pass-vote vs G-Eval-route≠discard): 7/7 = **100%** (>75% target ✅)
- **Downgrade rate** (G-Eval auto-prop ÉS NLI fail): 0/7 = **0%** (<20% target ✅)
- **Cross-check a 2026-05-17 21:21Z 20-sample paired snapshot-tal:**
  - both-pass: 7/20, g_pass_n_fail: 2/20, g_fail_n_pass: 5/20, both-fail: 6/20
  - agreement overall: 65% — DE high-conf subset (n=7) agreement: 71.4%
  - ⚠ A **g_pass_n_fail=2/20 (10%)** azt jelenti: ha NLI veto-zna, 2 bullet downgrade-ot kapna. Ez a `downgrade_ceiling: 0.2` alatt van, de **non-zero**.

### Mit jelent ez a default-shift szempontjából

A 7-sample current-window **mesterségesen tiszta**: csak az NLI-pass-vote-ot kapott bullet-eket számolja, a discard-route-ú mfl-voice-bullet-eket szelektíven. A **20-sample paired calibration** reálisabb: ott a NLI **10% G-Eval auto-prop-ot lehúzna**.

| Window | Sample | Agreement | Downgrade |
|---|---:|---:|---:|
| Current monitor-snapshot | 7 | 100% | 0% |
| Paired calibration (2026-05-17) | 20 | 65% overall / 71.4% high-conf | 10% (g_pass_n_fail) |
| Becsült 133-bullet backfill | ~190 | ~70-80% (high-conf) | ~5-10% (becslés a 20-sample alapján) |

## 3. Default-shift recommendation

### Verdict: **❌ MÉG NEM SHIFT-elendő (`VAULT_NLI_VETO=0` maradjon)**

**Indoklás:**

1. **Sample-méret még blokkoló** (7 → kritérium 10). A backfill (Opció A) megoldhatja **~30 perc alatt**, de:
2. **Production NLI-daemon nem fut** — `vault-nli.service` `inactive`. Default-shift előtt a daemon-stabilitás (p95 <800ms) bizonyítása kötelező (lásd `env-defaults.md` Week 6 → CANDIDATE kritérium).
3. **Calibration-data ellentmond a monitor-snapshot-nak**: 7-sample 0% downgrade vs 20-sample 10% g_pass_n_fail. A **20-sample reálisabb**, és ott a downgrade **non-zero**. False-negative kockázat: jó-G-Eval-bullet-ek elveszítése — analóg a `g-eval-bias-mitigation-pattern.md` v0.3 Pass-recall 53% gotcha-jával.
4. **Sessions/Weeks még blokkoló** (1 → kritérium 2). Természetes-flow-bővítés (Opció B) 1 hét alatt megoldható minden artificial backfill nélkül.

### Mit kell mégis CSINÁLNI most

| Lépés | Parancs | Hatás |
|---|---|---|
| **(1) NLI-daemon stabilizálás** | `systemctl edit vault-nli.service` (Description URL-encoding fix) + `systemctl start` | Warm socket + p95 latency mérhető |
| **(2) Backfill 30-sample paired calibration** | `eval-l2-nli-judge --calibrate --samples 30 --snapshot --server` | `nli_total: 7 → 37`, sessions+, weeks+ |
| **(3) Live shadow Opció B** — W21 minden zárás `VAULT_NLI_VETO=1`-gyel | `/11.11-zar-session` 2-3× | +natural-flow 20-30 sample, 2-3 új session |
| **(4) W22 re-eval** | `vault-crystallize-monitor --json` | Ha `default_shift_recommended: true` ÉS daemon-p95 <800ms → flip |

## 4. Recommended timeline

| Hét | Esemény | Trigger | Action |
|---|---|---|---|
| **W21** (2026-05-18..05-24) | **Daemon-fix + 30-sample backfill** + 2-3 session live shadow | Daemon-p95 mérés + sample ≥30 / 2+ session | `nli_total ≥10`, daemon stable |
| **W22** (2026-05-25..05-31) | **Monitor re-read** + downgrade-rate verifikáció | Ha `default_shift_recommended: true` ÉS downgrade <10% (NEM 20% — szigorúbb gate az analógia miatt) | **ADR draft** + 7-napos figyelmeztetés |
| **W23** (2026-06-01..06-07) | **Flip `VAULT_NLI_VETO=1`** default-ra | ADR ratify + zero-incident W22 | Update `env-defaults.md`: SHADOW → CANDIDATE → DEFAULT |

**Soft veto, NEM hard:** A default-shift azt jelenti, hogy NLI-veto **lefokozza** a bullet-et (auto-prop → batch-preview), NEM törli. A revert-cost LOW, ezért 1-hét-shadow → flip lépés OK ha a sample-gate és latency-gate megvan.

## 5. Frissítendő dokumentumok ha SHIFT megtörténik

1. **`~/.vault-config/env-defaults.md`** — `VAULT_NLI_VETO` sor: `Status: SHADOW → CANDIDATE → DEFAULT`, `Risk: MEDIUM` változatlan, `Next action: Week 6` → done.
2. **`06-Audits/shadow-monitoring-trend.md`** — `NLI shift?` oszlop ❌ → ✅ a flip-hetén, jegyzet a Propagation log-ba.
3. **`07-Decisions/2026-05-XX VAULT_NLI_VETO default-shift.md`** — új ADR, 7-napos figyelmeztetés.
4. **`11-wiki/crystallize-threshold-ramp.md`** — új szekció: "Soft-veto layer default-shift policy".

## Kapcsolódó

- [[2026-05-17 B-1 NLI Layer 2.5 integration]] — Layer 2.5 design
- [[2026-05-17 B-3 Week 2 L2 NLI-judge]] — implementáció
- [[2026-05-17 persistent NLI-process pool skeleton]] — daemon skeleton (current `inactive`)
- [[2026-05-18 B-1 Aggressive ramp data prep]] — pair-audit (today)
- [[shadow-monitoring-trend]] — heti rolling
- [[../05-Memory/env-defaults]] — ENV-flag tracker
- [[../11-wiki/g-eval-bias-mitigation-pattern]] — analóg false-negative kockázat (v0.3 Pass-recall 53%)
