---
name: clean-context-subagent-handoff
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/multi-agent", "#topic/orchestration", "#topic/context-management", "#topic/subagent", "lang/en"]
lang: en
translated_from: clean-context-subagent-handoff.md
---

# Clean-context subagent handoff — multi-agent context-isolation primitive

## TL;DR

The orchestrator agent **never passes its own full context window** to the subagent; instead it writes a **lean, targeted prompt** containing ONLY the info needed for the task. The subagent runs and returns **only the task result (summary-only)**. Goals: (a) context-window overflow avoidance, (b) compound-error mitigation, (c) parallelism (8+ subagents simultaneously, no $0-cost compromise).

## Background (3+ source evidence)

- [[sv-03-multi-agent-orchestration]] — "clean-context subagent handoff, prevents: context window overflow"
- [[sv-03-multi-agent-orchestration]] — "Orchestrator + isolated subagent + summary-only return" as canonical pattern
- [[claude-code-subagent-fanout]] — vault 19+ super-sessions with 8× parallel fanout, $0
- [[sv-03-multi-agent-orchestration]] — "stateful long-running agents causes compounding errors" — counter-pattern
- Anthropic Multi-Agent Research blog (2024-25) — "Building Effective Agents" core principle

## Pattern

Orchestrator (master agent) steps:

1. **Task decomposition**: split complex task into N independently-solvable parts
2. **Per-task prompt engineering**: tailored prompt for each subagent — input + rules + return-format. Does NOT pass its own context window, but a **synthesized lean input**
3. **Spawn N subagents in parallel**: each starts with its own **fresh** context window (does NOT see master history)
4. **Wait + collect**: subagents return `summary-only` output (NOT their full internal trace)
5. **Aggregate**: orchestrator reads only the summaries into its own context — not the subagent tokens
6. **Audit**: every subagent call logged (what it got, what it returned)

Vault examples:

- **`vault-ko-ingest` triplet-extraction**: 8 parallel subagents, each gets N raw docs, returns a triplet list
- **`11.11crystallize claude-code-scorer`**: 4 dim × 5 scale G-Eval, subagent-fanout pending pattern
- **Wiki-roundtable (round-2 axis A)**: 5-8 wikis at once, 1 subagent per axis

## Anti-patterns

- **Master passes own context window to subagent**: token cost ×2 and the subagent gets distracted by master noise. **CRITICAL anti-pattern.**
- **Stateful long-running subagent**: if subagent state persists across calls, compound errors accumulate. Every call starts with clean context.
- **Subagent "rich return"**: subagent returns full internal trace → orchestrator context window explodes. Only `summary-only` (200-2000 tokens).
- **Subagent → subagent recursion without limit**: subagent spawns subagent, which spawns more → token bomb. Max-depth-cap (default 1, rarely 2).
- **Race condition on shared state**: 8 parallel subagents write to the same file → corruption. Per-subagent dedicated output path (`/tmp/<uuid>.json`) + post-aggregate.

## Reusable rules

1. **Subagent prompt ≤ 4-8K tokens**: anything larger is either over-task or noise. Refactor.
2. **Summary-only return ≤ 2K tokens**: enforce with structured output (JSON schema, return-format example).
3. **Per-subagent dedicated output file** `/tmp/<task-id>-<subagent-id>.json` — race-condition-free.
4. **Max depth = 1** (default): orchestrator → subagent → result. Deeper nesting only in special cases.
5. **Idempotency key per task** — replay-safe.
6. **Audit log append-only** ([[audit-log-append-only-pattern]]): `(task-id, subagent-id, input-hash, output-hash, ts)`.
7. **Timeout per subagent** (20-60s), defensive — one slow subagent shouldn't block the orchestrator.

## Pitfalls

- **Token amplification**: aggregate-sum plus N×subagent-cost can rapidly become expensive. Per-batch token budget hard-cap.
- **Coherence drift**: 8 subagents on the same question return 8 different answers — orchestrator-level consensus / synthesis or ABSTAIN ([[dont-hallucinate-abstain-pattern]]).
- **Lost-context bug**: master forgets what it asked the subagent, and the return summary alone isn't interpretable. Always log prompt + return together.
- **Hallucinated subagent output**: subagent fabricates a fact — NLI gate ([[nli-hallucination-check-pattern]]) at aggregate level.

## Related

- [[sv-03-multi-agent-orchestration]] — full multi-agent architecture
- [[claude-code-subagent-fanout]] — vault-applied concrete implementation
- [[audit-log-append-only-pattern]] — log rule
- [[dont-hallucinate-abstain-pattern]] — multi-subagent disagreement handling
- [[nli-hallucination-check-pattern]] — output gate
- [[skill-metadata-catalog-pattern]] — complementary "what to load" strategy

## Hungarian original

[[clean-context-subagent-handoff]]
