---
name: auto-propagation-confidence-gate
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/automation", "#topic/safety", "#pattern/gating"]
---

# Auto-propagation confidence-gate mintázat

## TL;DR

A crystallization-pipeline **NEM minden Learning bullet-et propagál automatikusan** — confidence-threshold döntés (`shadow=1.0` / `conservative=0.95` / `aggressive=0.85`) eldönti, hogy auto-prop, batch-preview (manual), vagy discard. Cross-source: 19+ fact, 3 source-type. A gate aszimmetrikus: false-positive (rossz propagáció) >> false-negative (manual-review-be esik).

## Háttér (3+ source-evidence)

- **B-1 SV-5 crystallization automation:** `Threshold >= 0.85 → auto-prop`, `0.70-0.85 → manual batch-preview`, `<0.70 → discard` ([sv-5 crystallization automation ADR](../07-Decisions/2026-05-12%20sv-5%20crystallization%20automation%20arch.md))
- **Auto-propagation pipeline:** Routing match → JSON output (target, confidence) → threshold branch — implementáció az [[sv-05-crystallization-automation]]-ben
- **Threshold-ramp protokoll:** Shadow (1.0, 100% manual) → Conservative (0.95, kis auto) → Aggressive (0.85, ramp-up). Csak akkor lép, ha 7-napos revert-rate <2% ([crystallize-threshold-ramp](crystallize-threshold-ramp.md))
- **B-1 ramp dry-run risk-assessment:** 29 bullet / 62.1% auto-prop / 11-wiki 100% auto-rate → PASS-with-Wait W21-23 ([MEMORY 4th super-session Phase 5 bullet](/root/.claude/projects/-root/memory/MEMORY.md))
- **Pre-state backup kötelező:** `Auto-propagation requires git commit pre-state backup` és `audit log entry` ([sv-05-crystallization-automation](sv-05-crystallization-automation.md))
- **G-Eval bias-mitigation:** Confidence-score self-enhancement-bias miatt v0.3-ban szimmetrikusan szigorítva (0.880→0.760) ([g-eval-bias-mitigation-pattern](g-eval-bias-mitigation-pattern.md))

## Mintázat

```
Learning bullet ──> G-Eval scoring (LLM-as-judge)
                                │
                ┌───────────────┴───────────────┐
                │                                │
        confidence >= threshold        confidence < threshold
                │                                │
                ▼                                ▼
        ┌───────────────┐               ┌──────────────────┐
        │ pre-state git │               │ batch-preview to │
        │ commit + audit│               │ user / discard   │
        │ + atomic write│               │  (Layer 1 hard   │
        │ + Critic-rev. │               │   stop)          │
        └───────────────┘               └──────────────────┘
```

**Aszimmetrikus risk-budget:**

| Failure mode | Cost | Mitigáció |
|--------------|------|-----------|
| False-positive auto-prop (rossz tény bekerül evergreen wiki-be) | HIGH | Threshold magas + Critic-review + revert-able |
| False-negative manual-review (jó tény user-elé kerül) | LOW | User 1 kattintással OK-ézi |

## Architektúrális szabályok

1. **Layered eval cascade** előzze meg a confidence-számolást ([layered-eval-cascading-pattern]])
2. **Bias-mitigated G-Eval** prompt (v0.3, opt-in) — self-enhancement bias-kontroll
3. **Threshold hot-reloadable** — `~/.vault-config/crystallize-threshold.txt` ([hot-reload-config-pattern]])
4. **Audit-log append-only** minden döntésre ([audit-log-append-only-pattern]])
5. **REAL-mode külön ENV-flag** — `VAULT_CRYSTALLIZE_APPLY=1 VAULT_CRYSTALLIZE_REAL=1` ([env-flag-default-disabled-gate]])
6. **Sandbox-branch default** — `crystallize-sandbox-*` branchen futhat REAL, main-en csak `VAULT_CRYSTALLIZE_ALLOW_MAIN=1` ([CLAUDE.md](/root/.claude/CLAUDE.md))
7. **Revert-rate monitor** kötelező — `vault-crystallize-monitor` heti riport

## Ramp-protokoll mérés

```
Week N → Auto-rate (%)  → Revert-rate (%)  → Threshold-lépés
W21    → ~50%           → <2%               → 1.0 → 0.95 OK
W22-23 → ~62%           → <2%               → 0.95 → 0.90 OK
W24+   → ramp up        → folyamatos        → 0.90 → 0.85 ramp
```

## Buktatók

- ⚠️ **Confidence-bias** — Self-enhancement bias nélkül a threshold de-facto 0.05-tel alacsonyabb; v0.3 bias-mitigated prompt kötelező auto-prop-hoz
- ⚠️ **MIN_VOLUME guard** — kis batch (≤3 bullet) NE ramp-eljen; smoketest-noise → false-positive cascade ([auto-disable-min-volume-guard](auto-disable-min-volume-guard.md))
- ⚠️ **Predicate-dump** előbb fix-eld (19.8% generikus `has_value`) — confidence-score-okat torzítja
- ⚠️ **Per-target threshold** — wiki-target lazább, ADR-target szigorúbb (PR-fontosság szerint)

## Kapcsolódó

- [[crystallize-threshold-ramp]] — ramp-protokoll
- [[g-eval-bias-mitigation-pattern]] — bias-mitigated scoring v0.3
- [[layered-eval-cascading-pattern]] — multi-layer eval before confidence
- [[multi-layer-safety-gate]] — auto-prop mint magas-kockázatú mutation
- [[hot-reload-config-pattern]] — threshold hot-reload
- [[env-flag-default-disabled-gate]] — REAL-mode flag-gating
- [[audit-log-append-only-pattern]] — döntés-trace
- [[sv-05-crystallization-automation]] — implementációs ADR
