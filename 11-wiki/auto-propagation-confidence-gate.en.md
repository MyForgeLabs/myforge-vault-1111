---
name: auto-propagation-confidence-gate
type: wiki
lang: en
translated_from: auto-propagation-confidence-gate
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/automation", "#topic/safety", "#pattern/gating"]
---

# Auto-propagation confidence-gate pattern

## TL;DR

A crystallization pipeline does **NOT propagate every Learning bullet automatically** — a confidence-threshold decision (`shadow=1.0` / `conservative=0.95` / `aggressive=0.85`) decides between auto-prop, batch-preview (manual), or discard. The gate is asymmetric: false-positive (bad propagation) >> false-negative (manual review).

## Background

- **Crystallization automation:** `threshold >= 0.85 → auto-prop`, `0.70-0.85 → manual batch-preview`, `<0.70 → discard`
- **Auto-propagation pipeline:** routing match → JSON output (target, confidence) → threshold branch
- **Threshold ramp protocol:** Shadow (1.0, 100% manual) → Conservative (0.95, small auto) → Aggressive (0.85, ramp-up). Only steps if 7-day revert-rate <2%
- **Dry-run risk assessment:** e.g. 29 bullets / 62.1% auto-prop / 100% wiki auto-rate → PASS-with-Wait
- **Pre-state backup mandatory:** auto-propagation requires git commit pre-state backup and audit log entry
- **Bias-mitigated scoring:** confidence-score self-enhancement bias mitigated by stricter prompt (e.g. 0.880→0.760)

## Pattern

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

**Asymmetric risk budget:**

| Failure mode | Cost | Mitigation |
|--------------|------|-----------|
| False-positive auto-prop (bad fact enters evergreen wiki) | HIGH | High threshold + Critic-review + revertable |
| False-negative manual-review (good fact goes to user) | LOW | User OKs with 1 click |

## Architectural rules

1. **Layered eval cascade** precedes the confidence calculation ([[layered-eval-cascading-pattern]])
2. **Bias-mitigated G-Eval prompt** (opt-in) — self-enhancement bias control
3. **Threshold hot-reloadable** — `~/.vault-config/crystallize-threshold.txt` ([[hot-reload-config-pattern]])
4. **Audit-log append-only** on every decision ([[audit-log-append-only-pattern]])
5. **REAL-mode behind a separate ENV-flag** — `VAULT_CRYSTALLIZE_APPLY=1 VAULT_CRYSTALLIZE_REAL=1` ([[env-flag-default-disabled-gate]])
6. **Sandbox-branch default** — `crystallize-sandbox-*` branch may run REAL, main only with `VAULT_CRYSTALLIZE_ALLOW_MAIN=1`
7. **Revert-rate monitor** mandatory — weekly report

## Ramp protocol measurement

```
Week N → Auto-rate (%)  → Revert-rate (%)  → Threshold step
W21    → ~50%           → <2%               → 1.0 → 0.95 OK
W22-23 → ~62%           → <2%               → 0.95 → 0.90 OK
W24+   → ramp up        → ongoing           → 0.90 → 0.85 ramp
```

## Pitfalls

- ⚠️ **Confidence bias** — without self-enhancement bias mitigation, the threshold is de-facto 0.05 lower; bias-mitigated prompt mandatory for auto-prop
- ⚠️ **MIN_VOLUME guard** — small batches (≤3 bullets) must NOT ramp; smoke-test noise → false-positive cascade
- ⚠️ **Predicate dump** must be fixed first (generic `has_value` predicates skew confidence)
- ⚠️ **Per-target threshold** — wiki target lenient, ADR target stricter (PR significance)

## Related

- [[crystallize-threshold-ramp]] — ramp protocol
- [[g-eval-bias-mitigation-pattern]] — bias-mitigated scoring
- [[layered-eval-cascading-pattern]] — multi-layer eval before confidence
- [[multi-layer-safety-gate]] — auto-prop as high-risk mutation
- [[hot-reload-config-pattern]] — threshold hot-reload
- [[env-flag-default-disabled-gate]] — REAL-mode flag gating
- [[audit-log-append-only-pattern]] — decision trace
- [[sv-05-crystallization-automation]] — implementation ADR
