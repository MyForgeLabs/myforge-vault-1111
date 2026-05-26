---
name: bulk-fanout-context-budget-checkpoint
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#project/sv", "subagent-fanout", "context-management"]
---

# Bulk-fanout context-budget checkpoint placement

Subagent-fanout-tal vault-bulk-work közben a **parent-context fogyás-rátája** ~30-35K token per 16-agent batch (launch + completion notifications). 11-12 batch-en túli single-session bulk-művelet megközelíti a 400K parent-context, ami komoly compaction-veszélyt jelent. **Strategically placed user-decision-checkpoint-ok** mind ROI-feedback-mechanism (continue/stop/revert), mind context-safety-mechanism.

## A pattern

| Fázis | Mit csinálsz | Context-kihatás |
|---|---|---|
| Pre-batch generate | `vault-ko-ingest --file F` minden fájlra → request.json | ~50 byte / fájl (negligible) |
| Per-batch launch (16 agents) | 16× Agent tool call | ~16K (launch boilerplate) |
| Per-batch completion | 16× system-notification | ~12-15K (agent reports) |
| Per-batch process | `vault-ko-pending --process-ready` | ~1K (single tool result) |
| Per-batch re-measure | `vault-graph-complementarity --json` | ~1K (single tool result) |
| **Per-batch total** | | **~30-35K context** |

Vault-szintű bulk-művelet (171 fájl, ~11 batch) → ~330-385K parent-context. A Claude Code parent-session context limit ~200K (with caching, ~500K total accessible), de a 200K alatti zónát kell tartani, mert compaction lefojthatja az agent-tool-akciókat.

## Checkpoint placement playbook

**Default cadence**: minden 20-30% progress után. 171-fájl-es vault-backfill esetén ~50-fájl-szintű checkpoint optimális (29.2%).

**Min 2 explicit user-decision** kell: 30% és 60% szinten. A 30% checkpoint a "smart-stop" döntés (linear projection alapján "do I really need to run all of it?"). A 60% checkpoint a "context-safety" döntés (mennyi parent-context maradt?).

**Per-checkpoint output to user**:

1. **Progress számok**: `X / Y processed, +N facts, +M provs`
2. **Metric delta**: `FCA: 0.47 → 0.60 (Δ+0.13, projected 0.0027/file)`
3. **Linear projection**: `final = current + (remaining × per-file-rate) = X.XX`
4. **Decision option**: continue / stop-here / pivot-direction

## Worked example — Tier-1 backfill 2026-05-20

| Checkpoint | Files | FCA | Per-file rate | Projection | User decision |
|---|---:|---:|---:|---:|---|
| Pre-batch | 0 | 0.4676 | — | — | "go" |
| Post-50 (29.2%) | 50 | 0.6027 | **0.00270** | 0.93 | continue |
| Post-66 (38.6%) | 66 | 0.6459 | 0.00270 | 0.93 | continue (Option A) |
| Final (100%) | 171 | **0.9297** | 0.00270 | **0.9297** ✓ | merge to main |

A 50-checkpoint linear projection-ja (0.93) **EXACTLY** reprodukálódott a final-mérésen — a backfill teljes futása ezt csak konfirmálta, nem új információt adott. **Insight**: a final-decision (FCA ≥0.95 ceiling, vault-meta exclusions) MÁR a 50-checkpointnál látszott. A "continue all 171" döntés ÉRTELMES VOLT, de NEM "új információ alapon", hanem "data-completeness reason".

## Decision-tree az explicit checkpoint-on

```
30% checkpoint elérve.
Project linear? ──┬── YES ──┬── Final-projection acceptable? ──┬── YES → STOP-HERE (LinExtrapolate OK)
                  │         │                                   └── NO → CONTINUE + pivot
                  │         └── Final-projection ceiling? ───── YES → CONTINUE (data-completeness)
                  └── NO ───┬── Diminishing returns? ───────── YES → STOP-HERE
                            └── Increasing returns? ────────── YES → CONTINUE (positive curve)
```

Ha a project NEM lineáris (azaz minden új fájl változó hatást fejt ki — early/late files different), a 30%-checkpoint NEM elég, kell 60% checkpoint is.

## Context-budget hard-stop

Ha a parent-context 200K-hoz közelít (~85% used) MIELŐTT a következő batch befejeződne, **mandatory stop** + offer "résume in next session". A bulk-work folytatható: a `/tmp/vault-ko-pending/` állomány tartalmazza a már generált request-fájlokat, és minden batch idempotent.

## Pattern reuse

Ez a playbook nem csak vault-bulk-ingestre kell. Bármely bulk-fanout-művelet ami:

- ≥5 batch (~80-100 agent call)
- ~30K context / batch (par-batch overhead)
- linear-projection szempontjából értelmezhető (per-unit progress measurable)

→ használja a 30%/60% checkpoint-pattern-t. Példák: skill-batch-ingest, web-scrape-batch, code-refactor-batch, knowledge-distill-batch.

## Kapcsolódó

- [[claude-code-subagent-fanout]] — alap-pattern + scale-verified 2026-05-20
- [[sprint-day-0-skeleton-first]] — linear-extrapolation playbook
- [[memory-md-overflow-management]] — komplementer context-management pattern
- [[multi-layer-safety-gate]] — sandbox-branch + per-batch checkpoint sibling
- [[../06-Audits/2026-05-20 Tier-1 backfill 50-file partial — FCA +0.135 empirical]] — élő példa (50-checkpoint)
