---
name: dfsdt-backtracking-tool-composition
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/multi-agent", "#topic/tool-composition", "#topic/agent-reasoning", "#topic/backtracking", "lang/en"]
lang: en
translated_from: dfsdt-backtracking-tool-composition.md
---

# DFSDT backtracking for multi-step tool composition

## TL;DR

**DFSDT (Depth-First Search-based Decision Tree)** is a backtracking algorithm from the ToolLLM paper that solves the linear error compounding of traditional ReAct / Chain-of-Thought: when a tool call result doesn't fit, the agent **backtracks** and tries another branch instead of continuing in a straight line accumulating errors. In multi-step agent tasks, `successrate` jumps from 28-45% to 60-78% under DFSDT. The trade-off: 2-4× larger token budget.

## Background (3+ source evidence)

- [[sv-04-tool-composition]] — "ToolLLM proposes DFSDT (Depth-First Search-based Decision Tree) backtracking; open: how to natively teach multi-branch non-sequential planning"
- [[sv-04-tool-composition]] — "Reflexion-style self-verification, DFSDT-backtracking" as a compositional-drift mitigation
- [[sv-02-recursive-self-improvement]] — DFSDT-like search pattern for self-correction-blind-spot mitigation (related RSI technique)
- [[superintelligent-vault-research]] — DFSDT as a Bootstrapper-tier tool-strategy option

## Pattern

ReAct is linear: `tool_1 → result_1 → tool_2 → result_2 → ...`. If `tool_2` went wrong, `tool_3` builds on a bad foundation and errors accumulate. The user either gets a wrong final answer or the agent gets stuck in an infinite loop of correction attempts.

DFSDT builds a search tree: after every tool-call result, **two options** — (a) continue this branch, or (b) backtrack 1-2 levels and try another tool/argument. The tree unfolds DFS-style: follow a branch until it either succeeds or falls below a confidence threshold. Then backtrack, and **explicitly** try an alternative.

In the vault context, the DFSDT analogy is `vault-graph-query` cross-source mining: if the first predicate match is empty, we don't just return an error — we try the next best predicate in the query tree. Similarly: `vault-net-ingest`'s retry strategy (firecrawl → playwright → cloakbrowser) is DFSDT-like ([[cloakbrowser-fingerprint-bypass]]).

## Anti-patterns

- **Running DFSDT on a single-tool task**: 1-step task = 0% gain, 2-4× token loss. Backtracking only pays off in ≥3-step multi-step tasks.
- **Deep DFS with unbounded tree-depth**: search space explodes exponentially. Always hard-cap max-depth (3-5) + token budget (e.g. 20K).
- **"Restart" instead of DFSDT**: if you throw away the whole branch on every error, that's NOT backtracking but brute-force retry — more expensive and you don't learn from the branch.
- **DFSDT at agent-server level** without idempotent / state-less tools. Backtrack only works if the prior tool left no side effect in the world.

## Reusable rules

1. **Max-depth cap**: 3-5 levels default. 7+ = exponential token blow-up, negative ROI.
2. **Token-budget hard stop**: per-task ≤ 20-50K. If exceeded, fall back to linear ReAct + warning.
3. **Tool-idempotent contract**: every DFSDT-compatible tool documents whether it's stateless (`db-write` NO, `vault-graph-query` YES).
4. **Backtrack-trigger threshold**: P(success) < 0.40 on result confidence → backtrack. Tune per domain (search 0.50, retrieval 0.35).
5. **Best-of-N memo**: memoize already-tried branches within the session so you don't repeat.
6. **Combine Reflexion + DFSDT**: before backtracking, write a 1-2 sentence critique ("why did this branch fail?") → guides next branch choice, not random.

## Pitfalls

- **Stateful tool side-effect corruption**: if `tool_2` writes to a DB and you backtrack, DB state persists — explicit rollback procedure or sandbox-branch ([[sandbox-branch-mutation-isolation]]) needed.
- **LLM-judge bias at confidence threshold**: self-favoritism makes the LLM overestimate "P(success) = 0.85". Calibrate on 30-100 samples if serious.
- **Tool-spec drift** ([[memgraph-ce-feature-limits]]-style): if a tool's API changes during DFSDT-learned priors, the backtrack strategy goes stale. Periodic re-learning or MCP-abstraction needed.
- **Best-of-N anti-pattern**: keeping only the "final best" branch and discarding alternatives → learning information loss. Memoize the branches within the session.
- **Linear-ReAct fallback forced**: if budget runs out and you fall back to linear-ReAct, do NOT silently downgrade confidence — emit explicit `LOW_CONFIDENCE` flag in the return object, not `ABSTAIN`.

## When to use / when NOT

| Task | DFSDT worth it? | Why |
|---|---|---|
| 1-step search (question → answer) | NO | Backtrack overhead, 0% gain |
| 3-7 step multi-tool agent | YES | Compounding errors dominate here |
| ≥10 step complex workflow | PARTIALLY | Tree exponential — max-depth-cap + Best-of-N memo |
| Stateful destructive task (DB-write) | ONLY in sandbox | Side effects make backtrack harmful |
| Real-time interactive | NO | Latency 2-4× — kills user patience |

## Related

- [[sv-04-tool-composition]] — full tool-composition architecture
- [[sandbox-branch-mutation-isolation]] — backtrack-safe write-isolation
- [[cloakbrowser-fingerprint-bypass]] — DFSDT-like fallback chain (firecrawl → playwright → cloakbrowser)
- [[reranker-cost-optimization-not-size]] — analogous cost trade-off
- [[verification-step-before-claim]] — Reflexion-complementary technique

## Hungarian original

[[dfsdt-backtracking-tool-composition]]
