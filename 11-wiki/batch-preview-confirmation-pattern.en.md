---
name: Batch-preview confirmation pattern
type: wiki
lang: en
translated_from: batch-preview-confirmation-pattern
created: 2026-05-18
updated: 2026-05-18
tags: [pattern, ux, ai-agent, propagation, safety]
---

# Batch-preview confirmation pattern

> [!info] What it solves
> Any **multi-target write** (file-modifying propagation, multiple commits, multiple email sends, bulk DB mutation) where the user **wants control** but **does not want to be asked 5-10× one-by-one**. The batch-preview shows the whole package at once — a single `OK` (or partial selection) approves or modifies it.

## The core idea

Naive automation oscillates between two extremes: either **ask at every step** (UX fatigue, 10 turns) or **just announce afterwards** what was done (irreversible, trap-like). The batch-preview is a middle layer:

1. **Agent computes** all proposed operations (N items)
2. **Single summary block** presents them: numbered, `quote / source → target + preview`
3. **One user answer** decides the entire batch — `yes` / `1-3 OK, 4 use X instead` / `skip 2` / `stop`
4. **Only after confirmation** does it run the writes — atomically, with audit log

## When to use

| Situation | Batch-preview suitable |
|---|---|
| Session-end crystallization (5-20 Learning bullets to propagate) | ✅ canonical |
| Bulk-rename (50 files with new convention) | ✅ |
| Multi-project brand update (logo replacement in 4 project files) | ✅ |
| Single high-stakes operation (DB-drop, force-push) | ❌ use a hard-confirm modal instead |
| Real-time interactive editing (human at the keyboard) | ❌ inline preview is enough |

## Anatomy

A typical crystallization protocol uses this:

```
🧠 Propagating N learnings — proposal:
[1] "<bullet quote>" → 11-wiki/<slug>.md (new section "## Pattern X")
[2] "<bullet quote>" → 07-Decisions/2026-MM-DD <topic>.md (new ADR)
[3] "<bullet quote>" → 05-Memory/Infrastructure.md (new row in the "Ports" table)
[4] "<bullet quote>" → DISCARD (low-confidence, generic)
...
OK? (yes / "1-3 OK, 4 use X" / "skip 2" / "stop")
```

User-answer format is 4-pronged:
- **`yes`** — every proposal applied
- **partial selection** (`1-3 OK, 4 use X`) — agent re-plans #4, the rest proceed
- **`skip N`** — N excluded, rest proceed
- **`stop`** — nothing is propagated, the session file stays in raw form

## Why it works

- **Cognitive load**: O(1) decision for the user instead of O(N) — reviewing 8 bullets in 30s vs 8 turns over 5 minutes
- **Auditability**: the preview block itself is a log record (chat-history captures what the agent proposed and what the user accepted)
- **Reversibility**: on `stop`, nothing is written — contrasted with the "let me just do it too" anti-pattern
- **Trust building**: the more often the user sees the preview was accurate, the more they say `yes`

## Anti-patterns

| Anti-pattern | Problem | Correct form |
|---|---|---|
| **One-by-one prompt** | 10 turns, user exhausted → blindly says `yes` to everything | Single preview block |
| **Silent batch-apply** | Agent writes, then tells what it did | Always preview FIRST |
| **No-number preview** | "I propose this + this + this" — user cannot do partial selection | `[N]` numbering MANDATORY |
| **No target in preview** | "I'll propagate the learnings" — does not say WHICH files | Target path MANDATORY in every row |
| **Hiding confidence info** | High-confidence and weak proposals lumped together | `🟢 high / 🟡 mid / 🔴 low` markers in preview |

## Extension: G-Eval / confidence injection in the preview

A crystallization layer can embed G-Eval scoring into every preview row:

```
[1] 🟢 0.94 — "<quote>" → 11-wiki/<slug>.md
[2] 🟡 0.78 — "<quote>" → 07-Decisions/...
[3] 🔴 0.42 — "<quote>" → DISCARD-CANDIDATE (low conf)
```

Users filter Pass vs borderline **faster**. See [[auto-propagation-confidence-gate]] for the threshold mechanism.

## Implementation checklist

- [ ] All N proposals **in a single message** (not fragmented)
- [ ] Every row: `[N] source → target + 1-sentence preview`
- [ ] Numbering 1.. **monotonically increasing** (for partial selection)
- [ ] Target path **absolute or wikilink form** (no ambiguity)
- [ ] User-prompt clear option list (`yes / partial / skip / stop`)
- [ ] Operations executed **atomically** after user OK (not half-done)
- [ ] Propagation log written after every applied change (`## Propagation log` section in the session file)

## Related

- [[Crystallization-protocol]] — the vault session-closing protocol
- [[auto-propagation-confidence-gate]] — G-Eval threshold (when to preview vs auto-prop)
- [[destructive-action-hard-confirm-ux]] — single-action high-stakes (modal + Cancel autofocus)
- [[multi-layer-safety-gate]] — high-risk feature ENV+script+hook+critic
- [[rollback-revert-strategy-tiers]] — if rollback is needed after batch-apply
