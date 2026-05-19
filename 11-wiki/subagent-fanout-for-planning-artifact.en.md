---
name: Subagent-fanout for the planning artifact
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
lang: en
tags: ["#type/wiki", "subagent", "planning", "mega-session", "karpathy-llm-wiki"]
related:
  - "[[claude-code-subagent-fanout]]"
  - "[[sprint-day-0-skeleton-first]]"
---

# Subagent-fanout for the planning artifact

When a user is in "keep going" mode for hours, the highest-leverage move is to **subagent-fanout the PLANNING artifact at session-start**, not just the execution.

## The pattern

Most agent sessions burn the subagent budget on execution (parallel file edits, parallel research, parallel test runs). But the rate-limiting step in a long open-ended session isn't execution capacity — it's *knowing what to do next*. When the user says "menjen tovább szuper", the agent's working memory of follow-up ideas runs out by round 3-4.

The fix: at session start, spawn a research subagent whose job is to produce a **structured planning artifact** the main thread can iterate against for the rest of the session.

```
Session start
  │
  ├── Subagent A (background, $0): brainstorm 15-25 new dev ideas
  │     against the current state, with effort/risk/ROI per idea
  │     [writes a markdown audit at /06-Audits/ ~3000 words]
  │
  └── Main thread: continues with the user's stated top-5 priorities
        ↓
   Round 2-N: pick 3-4 ideas from the brainstorm audit per round,
              skeleton-first, ship as CLIs/wikis/scaffolds
```

## Validation — 2026-05-19 SV mega-session

- Round 1: spawned a 22-idea brainstorm research subagent (~6 min, ~85K tokens, $0)
- Rounds 2–10: 19 of 22 ideas LANDED as skeleton-first production CLIs
- Without the brainstorm artifact: estimated 0 brainstorm-idea ships (only stated top-5 would have happened)
- Cumulative session: ~7 hours wall-clock, 8 GitHub releases, $0 marginal cost

## When this works

- **Open-ended "keep going" sessions** (3+ hours, user-trigger-driven, no fixed scope)
- **Brainstorm domains** with measurable per-idea ROI (every idea has effort + risk + dependency on existing layer)
- **Skeleton-friendly targets** — each idea must be implementable as a 200-700 LOC CLI in an hour, not a multi-day system

## When it doesn't

- Short sessions (<1 hour) — overhead of the brainstorm-subagent eats the budget
- Tight scope (user has a specific 1-2 things to do) — no planning ambiguity
- High-coupling ideas — if implementations are interdependent, parallel skeletons collide

## Comparison with sequential planning

A naive sequential pattern: agent finishes current task → asks user "what's next?" → user picks → repeat. Latency-bound by user response time, and the user has to maintain the project mental model.

The fanout-planning pattern shifts the *planning* itself to the background, so the main thread is always doing work AND has a list of next things to pick from without user-prompt-latency.

## Composability

This pattern composes cleanly with the [[sprint-day-0-skeleton-first]] discipline: each idea picked from the brainstorm gets a Day-0 skeleton (CLI + tests + wiki), and Day-N filling-in happens in a follow-up session.

## Related

- [[claude-code-subagent-fanout]] — the underlying $0-cost subagent-fanout primitive
- [[sprint-day-0-skeleton-first]] — the skeleton-first discipline applied to each idea
- [[Karpathy-LLM-Wiki-pattern]] — the wider pattern of "compile knowledge incrementally"
- `06-Audits/2026-05-19 mega-session summary.md` — the empirical validation
