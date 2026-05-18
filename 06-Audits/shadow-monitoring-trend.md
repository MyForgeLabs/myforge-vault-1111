---
name: shadow-monitoring-trend
type: audit
created: 2026-05-17
updated: 2026-05-18
tags: ["#sv/b-1", "#audit/shadow-window", "#crystallize/monitor"]
---

# Shadow-monitoring trend — NLI L2.5 + Coherence L2.6

Heti rolling-update a `vault-crystallize-monitor` shadow-window-extension-jából. A `default-shift` oszlopok azt jelzik, hogy egy adott layer (NLI / Coherence) megfelel-e az opt-out-default-shift kritériumainak — lásd `06-Audits/2026-05-17 B-1 NLI Layer 2.5 integration.md` és `06-Audits/2026-05-17 Layer 2.6 vault-coherence integration.md`.

## Heti összegzés

| ISO-week | NLI n | agreement | downgrade | NLI shift? | Coh n | FP | ERROR | p95 | Coh shift? |
|---|---:|---:|---:|:---:|---:|---:|---:|---:|:---:|
| 2026-W21 | 7 | 100.0% | 0.0% | ❌ | 4 | 0 | 0.0% | 60.6s | ❌ |

## Kritériumok

- **NLI**: agreement ≥75% AND downgrade <20%, ≥10 sample, ≥2 hét shadow-data
- **Coherence**: 0 FP across ≥2 session, p95 <90s, ERROR ≤5%, ≥10 sample

## Trend-data (machine-readable, idempotens upsert)

<!-- trend-data:start -->
```jsonl
{"iso_week": "2026-W21", "generated_at": "2026-05-18T06:01:05+00:00", "threshold": 0.95, "action": "hold", "nli_total": 7, "nli_agreement_rate": 1.0, "nli_downgrade_rate": 0.0, "nli_shift_ok": false, "coh_total": 4, "coh_fp_count": 0, "coh_error_rate": 0.0, "coh_p95_ms": 60552, "coh_shift_ok": false}
```
<!-- trend-data:end -->

## Kapcsolódó

- [[crystallize-health]] — friss JSON snapshot
- [[2026-05-17 B-1 NLI Layer 2.5 integration]]
- [[2026-05-17 Layer 2.6 vault-coherence integration]]
- [[2026-05-17 shadow-monitoring extension]] — architektúra + impl-jegyzet
