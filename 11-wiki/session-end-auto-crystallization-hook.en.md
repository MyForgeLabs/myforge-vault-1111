---
name: Session-end auto-crystallization hook pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/memory-architecture", "#topic/crystallization", "sv-1", "sv-5", "memgpt-style", "lang/en"]
source: vault-meta NotebookLM Q4#1 / Q5#2 (2026-05-18, 63-source synthesis)
status: evergreen
lang: en
translated_from: session-end-auto-crystallization-hook.md
project: [[../02-Projects/superintelligent-vault]]
related: [[Crystallization-protocol]], [[Karpathy-LLM-Wiki-pattern]], [[sv-05-crystallization-automation]], [[crystallize-threshold-ramp]]
---

# Session-end auto-crystallization hook pattern

> **TL;DR:** The Karpathy LLM-wiki `working → episodic → semantic` memory structure works in production only if **the episodic→semantic transition is automated** — manual crystallization drop-off in practice is 60-80%. The solution is a **session-end hook** (embedded into `11.11stop`) that auto-propagates bullets passing the G-Eval cascade to the appropriate persistence layer.

## The problem

The vault-meta NotebookLM cross-project synthesis (63 sessions, 2026-05-18) — both **Q4-#1 and Q5-#2** pointed at this: the Karpathy memory structure is **structurally ready** in the vault (`08-Sessions/` episodic, `11-wiki/` semantic, `05-Memory/` working), **BUT automatic distillation is missing**.

Concrete quote from NB Q5-#2:
> "Automatic distillation and finalization of episodic knowledge (session logs) embedded in the `11.11stop` flow is currently explicitly a missing feature."

Manual crystallization fallout (own measurement, early 2026-05):
- **42 closed sessions** of which **only 18** had a manual `## Propagation log` filled
- **24 sessions** (57%) received **NO** semantic-layer update
- The "learning vanishes" anti-pattern → the vault degrades

## The MemGPT-style solution

MemGPT (Berkeley, Packer et al. 2024) and `GenericAgent` (Chinese L0-L4 architecture) **both** implement the same pattern: **event-driven session-end hook** that automatically:

1. **Extract:** session log → Learning-bullet list (LLM extraction)
2. **Score:** G-Eval cascade (Layer 1 syntax + Layer 2 NLI + Layer 2.5 reranker + Layer 3 cross-source)
3. **Route:** decision tree → target layer (wiki / ADR / MEMORY / glossary / projects / tasks)
4. **Apply:** auto-prop (high-confidence) or batch-preview (medium-confidence)
5. **Audit:** propagation log mandatory write-back into the session md

## The SV B-1 + B-5 implementation

### Current state (2026-05-18)

| Step | Implementation | Status |
|------|---------------|--------|
| 1. Extract | Manual (agent writes the `## Learnings` section) | ✅ LIVE |
| 2. Score | `11.11crystallize <slug> --scorer claude-code --with-context` (G-Eval cascade) | ✅ LIVE (B-1 Week 4) |
| 3. Route | `Crystallization-protocol` decision tree | ⚠️ Manual ratify |
| 4. Apply | `VAULT_CRYSTALLIZE_APPLY=1 + REAL=1` | ⚠️ Opt-in, default OFF |
| 5. Audit | `crystallize-revert <hash>` rollback | ✅ LIVE |

### What's missing (Q4-#1 / Q5-#2)

The **automatic chain between `11.11stop` and `11.11crystallize`**. Currently:
- User manually writes the Learning bullets → 11.11stop → manually runs crystallize → manually approves the batch-preview
- **Hook is missing** — no `pre-stop` and `post-stop` event triggers
- **MCP bridge missing** — Claude Code's session-end event doesn't talk to the vault pipeline

### The proposed hook architecture

```
11.11stop "<slug>"
  ├── pre-stop hook (Claude Code SessionEnd event)
  │     └── auto-LLM-extract Learning bullets from chat history
  │
  ├── core: 11.11stop script (commit + push + close)
  │
  └── post-stop hook (MCP-bridge → vault-pipeline)
        ├── (a) 11.11crystallize <slug> --scorer claude-code --with-context (G-Eval)
        ├── (b) Layer-3 cross-source validation (NLI + reranker smart-trigger)
        ├── (c) batch-preview to user (5-bullet limit) AND/OR
        │       auto-prop (threshold ≥0.95 → REAL mode) if env-flag LIVE
        ├── (d) audit log to the session md `## Propagation log` (idempotent)
        └── (e) if ANY bullet REVERTed → notification ✕
```

## Reference implementations

- **MemGPT** (Berkeley, Packer 2024) — virtual context management, `Heartbeat`/`Sleep` event-trigger, recall-memory persistence
- **GenericAgent** L0-L4 — automated memory hooks, atomic-tool-parallel ([[Karpathy-LLM-Wiki-pattern]])
- **Letta** (MemGPT successor, 2025) — Agent OS, MCP-server-as-memory-broker

## Why it's NOT trivial

### Problem 1: G-Eval bias

Self-evaluation bias (Claude scoring Claude output) is **systematic confidence inflation** ([[g-eval-bias-mitigation-pattern]]). The 2026-05-17-3 30-sample paired calibration shows v0.3 bias-mitigation tightens symmetrically, **Pass-recall drops to 53%**. In an auto-prop system this means **57% false-discard** = lost learning.

**Solution:** Layered cascade ([[layered-eval-cascading-pattern]]) — fast G-Eval is only the first filter, NLI Layer 2.5 is the deciding one.

### Problem 2: Idempotency

If the hook runs twice (e.g. crash + retry), it must not duplicate the wiki merge. **Hash-based idempotency** required (bullet-content-hash → log entry).

### Problem 3: User-trust cliff

"Fully autonomous auto-prop" with 0% human review **can't be reached at once**. Threshold-ramp protocol ([[crystallize-threshold-ramp]]) required:
- **W1 shadow** (threshold=1.0, audit only)
- **W2-3 conservative** (threshold=0.95, opt-in user-flag)
- **W4-5 production** (threshold=0.85, default-on for the wiki-target layer)

### Problem 4: Cross-target routing

Not every Learning goes to the same place:
- Architecture-level → ADR (`07-Decisions/`)
- Reusable pattern → wiki (`11-wiki/`)
- Project-specific → `02-Projects/<slug>.md`
- User-pref → `05-Memory/User.md`
- Infra-fact → `05-Memory/Infrastructure.md`

**Routing accuracy ≥85%** required, else wrong-target noise > value.

## Cross-project evidence

In the 63-source NB synthesis:
- **Foxxi**, **kgc-berles**, **kinda-project** sessions: Learning bullets **stayed in chat history**, never reached `11-wiki/` → 6-8 months later **unfindable knowledge**
- **MyForge-dashboard**, **sv-week1**: manual crystallization ran **disciplined** → **measurable wiki evolution**
- **Correlation:** projects with manual crystallization show **3-5× lower** "déjà vu re-solving" rate

## Anti-patterns

1. **Auto-prop default-ON threshold=0.5 without threshold-ramp** — user-trust cliff instantly
2. **G-Eval-only scoring without NLI cascade** — bias inflation (53% Pass-recall confirmed)
3. **No hash-idempotency** — duplicated wiki merge if hook crashes + retries
4. **Manual-ratify-default forever** — 60-80% drop-off (Karpathy pattern useless)

## When this pattern applies

- ✅ Karpathy-style vault architecture (`working / episodic / semantic` layers)
- ✅ Session-close as a discrete event (NOT continuous stream)
- ✅ G-Eval (or similar LLM-judge) available for scoring
- ❌ Purely human-curated knowledge base (no LLM in the loop)

## Implementation roadmap (B-1 Week 2 + B-5 Week 1)

| Phase | Work | Est. time |
|-------|------|-----------|
| 1 | `pre-stop` Claude Code SessionEnd hook (MCP-bridge skeleton) | 1-2 days |
| 2 | Auto-Learning-extraction LLM subagent | 1 day |
| 3 | `post-stop` chain: extract → score → route → preview | 2-3 days |
| 4 | Threshold-ramp config + audit-log idempotent | 1-2 days |
| 5 | Cross-target routing accuracy validation (>85%) | 2-3 days |
| **Total** | | **7-11 days** (1.5-2 weeks) |

## Related

- [[Crystallization-protocol]] — manual crystallization protocol (foundation)
- [[Karpathy-LLM-Wiki-pattern]] — background architecture
- [[sv-05-crystallization-automation]] — B-5 sprint host
- [[crystallize-threshold-ramp]] — threshold management
- [[g-eval-bias-mitigation-pattern]] — G-Eval bias mitigation
- [[layered-eval-cascading-pattern]] — G-Eval + NLI cascade
- [[../06-Audits/2026-05-18 vault-meta NB cross-projekt Q4-Q5]] — source audit

## Hungarian original

[[session-end-auto-crystallization-hook]]
