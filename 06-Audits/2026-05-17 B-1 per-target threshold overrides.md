---
name: 2026-05-17 B-1 per-target threshold overrides
type: audit
tags: ["#axis/sv-1", "#topic/crystallization", "#topic/threshold", "sv-1", "crystallization", "threshold"]
created: 2026-05-17
updated: 2026-05-17
status: shipped
axis: B-1
session: 2026-05-17-obsidian-vault-2
---

# B-1 per-target threshold overrides — audit (2026-05-17)

> [!success]
> A `11.11crystallize` G-Eval routing **risk-aware** lett — minden auto-prop kandidát a *target-folder szerinti* threshold-on méretik, NEM egy globális 0.95-ön. Az Aggressive-ramp (1.0 → 0.85) most már nem all-or-nothing, hanem ADR-be 0.95 marad / Backlog-ba 0.75 csúszik.

## Mit szállítottunk

- Új YAML konfig `/root/.vault-config/crystallize-threshold.yaml`
- Új function `get_threshold_for_target(target_path)` — longest-prefix match
- Új function `load_threshold_config()` — cached YAML loader + legacy `.txt` fallback
- `process_session` + `run_apply_skeleton`: minden bullet `proposed_target`-jéhez kérik a threshold-ot
- Audit-log új mezők: `effective_threshold`, `threshold_key`, `target_file` (eddig `None` volt shadow-ban)
- Backward-compat: ha YAML hiányzik vagy `import yaml` fail → legacy `crystallize-threshold.txt` flat-érték
- Backup: `/usr/local/bin/11.11crystallize.bak.20260517`
- CLI override-szabály: `--threshold X` (ha != default + != global) felülírja a YAML lookup-ot, `threshold_key="cli-override"`-rel jelölve

## YAML séma

```yaml
default: 0.95
targets:
  "07-Decisions/": 0.95   # ADR-ek kritikus
  "00-Meta/": 1.00         # vault-szabályok readonly
  "MEMORY.md": 0.90
  "05-Memory/": 0.90
  "11-wiki/": 0.85
  "04-Tasks/Backlog.md": 0.75
```

## Lookup tesztek (unit)

| target | threshold | matched key |
|---|---:|---|
| `07-Decisions/foo.md` | 0.95 | `07-Decisions/` |
| `11-wiki/bar.md` | 0.85 | `11-wiki/` |
| `MEMORY.md` | 0.90 | `MEMORY.md` |
| `04-Tasks/Backlog.md` | 0.75 | `04-Tasks/Backlog.md` |
| `00-Meta/x.md` | 1.00 | `00-Meta/` |
| `05-Memory/User.md` | 0.90 | `05-Memory/` |
| `02-Projects/x.md` | 0.95 | `default` |
| `None` (ismeretlen) | 0.95 | `default` |

Longest-prefix győz (pl. `04-Tasks/Backlog.md` szigorúbb match mint `04-Tasks/`).

## E2E dry-run (mock scorer, `2026-05-17-obsidian-vault`)

8 Learning bullet, mind risk-aware routing-ot kapott:

```
[0] 🔴 conf=0.67 · t=0.90[MEMORY.md]
[1] 🔴 conf=0.67 · t=0.95[07-Decisions/]
[2] 🔴 conf=0.67 · t=0.90[MEMORY.md]
[3] 🟡 conf=0.73 · t=0.85[11-wiki/]      ← batch-preview
[4] 🟡 conf=0.73 · t=0.85[11-wiki/]      ← batch-preview
[5] 🔴 conf=0.67 · t=0.90[MEMORY.md]
[6] 🔴 conf=0.67 · t=0.90[MEMORY.md]
[7] 🟡 conf=0.73 · t=0.85[11-wiki/]      ← batch-preview
Summary: 🟢 0  🟡 3  🔴 5
```

Audit-log entry példa (utolsó bullet):

```json
{
  "scorer": "mock",
  "threshold": 0.95,
  "effective_threshold": 0.85,
  "threshold_key": "11-wiki/",
  "confidence": 0.7333,
  "route": "batch-preview",
  "target_file": "11-wiki/vscode-extension-popup-csak-name--et-mutat-nem.md"
}
```

## Next step — 1.00 → 0.85 ramp aktiválható per-target alapon

**Igen, aktiválható.** A korábbi globális Aggressive-ramp (1.0 → 0.85) blocking concern-je az volt, hogy ADR-be is 0.85-tel mehet be auto-prop. Az új YAML konfig megoldja:

- **07-Decisions/ marad 0.95** — kritikus / immutable / human-ratification-needed
- **00-Meta/ marad 1.00** — vault-governance readonly
- **MEMORY.md / 05-Memory/ 0.90** — közepes kockázat
- **11-wiki/ 0.85** — evergreen-pattern auto-draft elfogadható (Auto-DRAFT frontmatter-rel)
- **04-Tasks/Backlog.md 0.75** — alacsony kockázat, churn-friendly

**Aktiválási sorrend (javasolt):**

1. **Most (shadow-folytatás):** `VAULT_CRYSTALLIZE_APPLY=0`, csak audit-log gyűlik → 1 hét baseline
2. **+1 hét:** `VAULT_CRYSTALLIZE_APPLY=1` + sandbox-branch + `VAULT_CRYSTALLIZE_REAL=1` → 11-wiki kandidátok tesztelése izoláltan
3. **+2 hét:** ha `vault-crystallize-monitor` auto-rate < 0.5 / week és revert-rate == 0 → main-ra főleg 11-wiki + Backlog
4. **Tartós-shadow:** ADR / 00-Meta sose csúszik le 0.95/1.00 alól, akkor sem ha a többi rétegen csúszunk

A YAML hot-reloadable — config-szerkesztés azonnal él, daemon-restart nem kell.

## Kapcsolódó

- [[../11-wiki/crystallize-threshold-ramp]] — globális ramp-protokoll (eredeti)
- [[../11-wiki/multi-layer-safety-gate]] — 4-rétegű apply-gate, ezzel orthogonal
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — alaprács
- [[../02-Projects/superintelligent-vault]] — B-1 axis tracker
- Backup: `/usr/local/bin/11.11crystallize.bak.20260517`
- Config: `/root/.vault-config/crystallize-threshold.yaml`
