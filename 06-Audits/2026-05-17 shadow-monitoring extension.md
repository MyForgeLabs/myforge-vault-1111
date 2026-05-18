---
name: 2026-05-17 shadow-monitoring extension
type: audit
created: 2026-05-17
updated: 2026-05-18
tags: ["#sv/b-1", "#audit/shadow-window", "#crystallize/monitor", "#impl"]
---

# `vault-crystallize-monitor` shadow-window extension — impl + smoke

> [!success] B-1 Week 5-6 deliverable
> Az `11.11crystallize` audit-log most már Layer 2.5 (NLI) + Layer 2.6 (Coherence) shadow-mezőket loggolja, és a `vault-crystallize-monitor` heti cron-on méri az agreement-rate / FP-rate / latency / ERROR-rate adatokat. A default-shift döntés data-driven lesz, nem hunchből.

## Kontextus

A B-1 sprint korábbi rétegei (Layer 2.4 G-Eval v0.3 bias-mitigated + Layer 2.5 NLI cross-check + Layer 2.6 vault-coherence) shadow-mode-ban (default OFF, opt-in env-flag) loggolnak az `06-Audits/crystallize-log.jsonl`-be 14 új mezőt:

| Layer | Mezők |
|---|---|
| 2.5 NLI | `nli_verdict`, `nli_entailment_prob`, `nli_contradiction_prob`, `nli_pass_vote`, `nli_downgrade`, `nli_pre_route` |
| 2.6 Coherence | `coherence_status` (OK/FLAG/ERROR), `coherence_max_contra_prob`, `coherence_neighbour_count`, `coherence_downgrade`, `coherence_pre_route`, `coherence_latency_ms`, `coherence_conflicts`, `coherence_error` |

A default-shift (opt-out flag-flip, ENV-default 0→1) feltételei:

- **NLI**: agreement-rate ≥75% AND downgrade-rate <20%, legalább 10 NLI-tagged bullet ≥2 hét shadow-data
- **Coherence**: 0 false-positive ≥2 session-en keresztül, p95 latency <90s, ERROR-rate ≤5%, legalább 10 coherence-tagged bullet

A mérést a `vault-crystallize-monitor` script végzi heti cron-on (Sunday 04:35 → `crystallize-health.json`).

## Architektúra

### Adatfolyam

```
crystallize-log.jsonl   (append-only audit, 14 új mező / shadow-tagged bullet)
        │
        ▼
vault-crystallize-monitor (cron Sun 04:35)
        │
        ├──→ crystallize-health.json   (legutóbbi snapshot)
        │
        └──→ shadow-monitoring-trend.md  (heti rolling-update, idempotent JSONL block + table)
```

### Kódstruktúra

`/usr/local/bin/vault-crystallize-monitor` (Python 3, stdlib-only):

- `compute_stats()` — eredeti auto-rate / revert-rate / per-week buckets (változatlan)
- **`compute_shadow_stats()` (új)** — egy bejáráson kiszámolja:
  - NLI: `total`, `pass_vote`, `downgrade`, `agreement_rate`, `downgrade_rate`, per-week breakdown, entail/contra-prob means
  - Coherence: status-distribution, downgrade-rate, **FP-rate** (downgrade-flagged bullet kerül `apply_real executed=True` event-en keresztül applied set-be → user-override), p50/p95 latency, ERROR-rate, per-session FP breakdown
  - **Recommendation** (`default_shift_recommended: bool` + `reason: str`) — minden kritérium kiértékelve sorban, hiányzó adat is megjelenik
- **`upsert_trend_md()` (új)** — `shadow-monitoring-trend.md` idempotens upsert:
  - JSONL fenced block delimiterek között (`<!-- trend-data:start -->` / `<!-- trend-data:end -->`)
  - Egy sor / iso-hét, re-run overwrite-ol (NEM duplikál)
  - A human-readable markdown table minden futáson a JSONL-ből regenerálódik
- **`render()`** — text-mode kiterjesztve a shadow-window blokkal (`── Shadow-window (B-1 Week 5-6) ──` szekció)

### CLI flag-ek (új)

| Flag | Hatás |
|---|---|
| `--update-trend` | idempotens upsert `shadow-monitoring-trend.md`-be |
| `--dry-run` | NEM ír trend-MD-t (ad-hoc futtatás default-ja) |

A `--json` és `--weeks N` változatlan; a heti cron `--json --update-trend > crystallize-health.json` formában fog futni.

### Kritériumok kódolva (tunable)

```python
NLI_AGREEMENT_TARGET    = 0.75      # ≥ 75 %
NLI_DOWNGRADE_CEILING   = 0.20      # < 20 %
NLI_MIN_SAMPLES         = 10
NLI_MIN_WEEKS           = 2

COH_LATENCY_P95_CEILING_MS = 90_000  # 90 s
COH_ERROR_RATE_CEILING     = 0.05    # ≤ 5 %
COH_MIN_SAMPLES            = 10
COH_MIN_SESSIONS           = 2
```

A 06-Audits source-of-truth dokumentumok (`2026-05-17 B-1 NLI Layer 2.5 integration.md`, `2026-05-17 Layer 2.6 vault-coherence integration.md`) explicit küszöbei alapján.

## FP-detect heurisztika (Coherence)

A `coherence_downgrade=True` mellé jelenleg nincs explicit user-feedback mező. **Proxy:** ugyanaz a `bullet_hash` később megjelenik `apply_real` event-ben `executed=True`-val → ez user-override (a downgrade ellenére mégis applied lett).

> [!info] Limitáció
> Ez konzervatív heurisztika — az igazi FP-arányt csak explicit user-feedback mező (jövőbeli `user_override_route` mező a critic-decision-höz hasonlóan) tudná pontosan mérni. Addig is: 0 FP esetén a default-shift biztonságos; >0 FP esetén kötelező manual-eval a recommendation-kívül.

A `fp_by_session` mező a session-szintű FP-számot is exportálja, így könnyű kiszúrni hol gyűlt fel.

## Smoke-test eredmény (2026-05-18)

### Dry-run a teljes `crystallize-log.jsonl`-en (105 record)

```text
📊 11.11crystallize monitor — threshold currently 0.95

Week        scored   auto  batch  disc  applied  rev
2026-W20        88     33     17    38        4    0

Auto-rate (window): 37.5%  (33/88)
Revert-rate       : 0.00%  (0/4)
Critic discard    : 6 bullets rejected at Layer 4

⏸ Suggestion: **hold** threshold — insufficient data (4 applied bullets in window)

── Shadow-window (B-1 Week 5-6) ──────────────────────────
NLI L2.5      : 7 samples (1 sess, 1 wk)  agree 100.0%  downgrade 0.0%
              → default-shift ❌ NO — only 7 NLI-tagged bullets (need ≥10); only 1 weeks of NLI data (need ≥2)
Coherence L2.6: 4 samples (1 sess, 1 wk)  status {'OK': 4}  FP 0  p50 47.9s  p95 60.6s
              → default-shift ❌ NO — only 4 coherence-tagged bullets (need ≥10); only 1 session(s) (need ≥2)
```

### Verifikáció: új mezők perzisztáltak az audit-log-ban

| Mező | Előfordulás |
|---|---:|
| `nli_verdict` + 5 NLI mező | 7 / 105 record |
| `coherence_status` + 5 Coherence mező | 4 / 105 record |

Az utolsó 2 NLI sor (session `2026-05-15-mfl-voice-sprint-1`) mindkettő `entailment`, `pass_vote: true`, `downgrade: false` — agreement 100%, downgrade 0%, de a sample-szám nem éri el a 10-et, így **shift NO** (várt eredmény).

Az utolsó 4 Coherence sor (session `2026-05-17-obsidian-vault-2`) mindkettő `status: OK`, `downgrade: false`, latency 42.5-50.7s — minden zöld, de csak 1 session, így **shift NO** (várt eredmény).

### Recommendation output (várt: most még shadow-window túl rövid → false)

```json
"nli": {
  "default_shift_recommended": false,
  "reason": "only 7 NLI-tagged bullets (need ≥10); only 1 weeks of NLI data (need ≥2)"
},
"coherence": {
  "default_shift_recommended": false,
  "reason": "only 4 coherence-tagged bullets (need ≥10); only 1 session(s) (need ≥2)"
}
```

Megfelelően konzervatív — sem a NLI-, sem a Coherence-layer NEM kapja meg a default-shift-zöldet, amíg ki nem épült legalább 2 hét + 2 session shadow-data.

### Idempotency-test

- 1. futás → 1 jsonl-sor (W21) + 1 table-sor a markdown-ban
- 2. futás (azonnal) → még mindig 1 jsonl-sor (overwrite, NEM duplikál)
- 3. teszt: szintetikus W19 row injektálva manuálisan, 4. futás → 2 jsonl-sor sorted (W19, W21), 2 table-row → ✅ multi-week működik

## Heti cron integráció

A meglévő crontab-sor változatlan, csak a flag-set bővül:

```cron
35 4 * * 0 /usr/local/bin/vault-crystallize-monitor --json --update-trend > /root/obsidian-vault/06-Audits/crystallize-health.json 2>&1
```

> [!todo] Cron-flag-frissítés follow-up
> A `--update-trend` flag az új heti cron-on kell bekerüljön (`crontab -e`). A meglévő `--json` invocation továbbra is működik; a `--update-trend` opcionális.

## Default-shift checklist (mit kell még)

NLI:
- [ ] **≥10 NLI-tagged bullet** összesen (jelenleg 7) → kb. 2-3 session opt-in `VAULT_NLI_VETO=1`-zel
- [ ] **≥2 hét** shadow-data (jelenleg 1) → természetes idő múlása
- [ ] **agreement ≥75%** (jelenleg 100% — nagyon biztató, de kevés sample)
- [ ] **downgrade <20%** (jelenleg 0% — szintén kevés sample)

Coherence:
- [ ] **≥10 coherence-tagged bullet** (jelenleg 4)
- [ ] **≥2 session** lefedettség (jelenleg 1)
- [ ] **0 FP** (jelenleg 0 — clean)
- [ ] **p95 <90s** (jelenleg 60.6s — pass)
- [ ] **ERROR ≤5%** (jelenleg 0% — pass)

## Korlátozások

- A FP-detect heurisztika (downgrade-flagged hash → később applied) konzervatív — nem fedi a user-side rejection-eket (user soha nem futtatja az applied-step-et). Jövőbeli `user_override_route` mező pontosabbá tenné.
- A p95-számítás kevés sample-en (n=4) nem reprezentatív; csak 10+ sample-től érdemes komolyan venni.
- A shadow-monitoring-trend.md JSONL-blokkja `iso_week`-re key-elt — ha valaki kézzel írja át, a következő futás overwrite-olja a saját hét sorát (helyes viselkedés).

## Output fájlok

- `/usr/local/bin/vault-crystallize-monitor` — bővített monitor
- `/usr/local/bin/vault-crystallize-monitor.bak.20260517-shadow-monitor` — backup
- `/root/obsidian-vault/06-Audits/crystallize-health.json` — legutóbbi snapshot (heti cron output)
- `/root/obsidian-vault/06-Audits/shadow-monitoring-trend.md` — heti rolling-trend (table + JSONL)

## Kapcsolódó

- [[2026-05-17 B-1 NLI Layer 2.5 integration]]
- [[2026-05-17 Layer 2.6 vault-coherence integration]]
- [[2026-05-17 B-1 G-Eval bias-mitigation v0.3]]
- [[shadow-monitoring-trend]] — heti rolling-data
- [[../11-wiki/crystallize-threshold-ramp]] — backout-rule + ramp-protocol
- [[../11-wiki/Crystallization-protocol]]
