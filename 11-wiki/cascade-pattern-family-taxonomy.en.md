---
name: Cascade-pattern family taxonomy
type: wiki
lang: en
translated_from: cascade-pattern-family-taxonomy
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/cascade, taxonomy, evergreen, orchestration]
---

# Cascade-pattern family taxonomy

> [!info] TL;DR
> Many distinct concepts use the word "cascade", but they really represent **4 different meaning layers** under one word: (a) **sprint-orchestration cascade** (skeleton-first Day 0), (b) **agent-fanout cascade** (subagent tree), (c) **CSS-fill cascade** (DOM inheritance), (d) **eval/scoring cascade** (multi-layer auto-prop gate). This wiki disambiguates and gives reusable decision rules.

## Cluster members (representative)

| Concept | Layer |
|---|---|
| cascade phase | Sprint-orchestration |
| cascade sprint Day 0 | Sprint-orchestration |
| Day 0 cascade pattern | Sprint-orchestration |
| Trial then 8-parallel cascade | Sprint-orchestration |
| cascade agents | Agent-fanout |
| cascade prompt-template | Agent-fanout |
| Subagent cascade pattern | Agent-fanout |
| agent-tree cascade failure | Agent-fanout |
| text-group fill cascade | CSS-DOM |
| fill cascade inheritance | CSS-DOM |
| Chromium img-svg parent-fill cascade bug | CSS-DOM |
| SV B-4 cascade | Eval/scoring |
| Model cascade routing | Eval/scoring |

## The 4 cascade families

### 1. Sprint-orchestration cascade (Day 0 skeleton-first)

**Pattern:** N sprints start **in parallel**, all committed on the same Day 0, so downstream sprints don't block each other.

- **Trigger:** launching multiple research axes simultaneously (e.g. B-1..B-5)
- **Mechanism:** Day 0 = scaffold + skeleton, ZERO functional code (exception: <20 LOC)
- **Examples:** SV B-1..B-7 cascade, multi-sprint cascades

**Reusable rule:** if 3+ sprints must start independently, **commit a Day 0 skeleton for each** — this is what "cascade" means, NOT serialized execution.

→ [[sprint-day-0-skeleton-first]]

### 2. Agent-fanout cascade (subagent tree)

**Pattern:** lead-agent spawns N subagents **in parallel**, each with clean context, results flow back to the lead (map-reduce).

- **Trigger:** 5+ identical-type tasks (bulk-mutation, batch-research)
- **Mechanism:** Task-tool / Agent-tool fanout, NOT sequential
- **Failure tolerance:** `agent-tree cascade failure` = if 1 subagent fails, the others continue (lead-aggregator decides)

**Reusable rule:** for subagent-fanout, MIN 5 tasks, MAX 10 (rate-limit) per batch. Lead-context budget must not exhaust — clean-context handoff [[clean-context-subagent-handoff]].

→ [[claude-code-subagent-fanout]]

### 3. CSS-DOM fill cascade (Chromium bug)

**Pattern:** SVG `<text>` fill property inherits from parent, but Chromium has a bug in the `<img>` parent ↔ inline-SVG relationship.

- **Trigger:** WP/Elementor icon field with SVG, source-level `<img src="...svg">`
- **Mechanism:** Chromium `fill` cascade does NOT cross img-parent boundary, Firefox/Safari does
- **Workaround:** inline SVG or `<object>` tag

→ [[chromium-img-svg-parent-fill-bug]]

**Reusable rule:** SVG fill is cross-browser inconsistent — print assets should be direct-vector, web assets should be inline-`<svg>`.

### 4. Eval/scoring cascade (layered safety)

**Pattern:** expensive ML eval (LLM judge) preceded by a cheap rule-based layer → if that filters, the expensive layer does not run.

- **Trigger:** auto-propagation gate, model-cascade routing
- **Layers:** rule-based → coherence check (local NLI) → G-Eval (LLM judge, expensive)
- **Example:** crystallize cascade Layer 1 ENV-gate → 2 source-type → 2.5 NLI → 2.6 coherence → 3 G-Eval

**Reusable rule:** in evaluation pipelines, **cheap-first, expensive-last**. If hot-path is <10ms, expensive layer only runs when cheap layers pass.

→ [[layered-eval-cascading-pattern]] · [[g-eval-bias-mitigation-pattern]]

## "Cascade" word disambiguation rule

When using "cascade" in a session, **mark the layer**:

| Word | Meaning |
|---|---|
| "sprint-cascade" | Day 0 parallel sprint launch |
| "agent-cascade" / "subagent-cascade" | fanout spawn |
| "CSS-cascade" / "fill-cascade" | DOM inheritance |
| "eval-cascade" / "scoring-cascade" | layered ML judge |
| bare "cascade" | forbidden, ambiguous |

## Anti-patterns

| Pattern | Problem |
|---|---|
| 5-sprint cascade with Day 0 SKIPPED | sequential, NOT cascade |
| Agent-fanout AND sequential subagent mixed | rate-limit + race condition |
| Eval-cascade in reverse order (expensive-first) | cost explodes |
| CSS-cascade Chromium-specific condition | cross-browser break |

## Reusable rules

1. **Cascade ≠ sequential**: if order is bound → it's a pipeline. "Cascade" = parallel / layered
2. **In layered cascade**: cheap-first, telemetry to measure which layer filters how much
3. **In Day 0 cascade**: scaffold-only commits, functional code Day 1+
4. **In agent-fanout cascade**: clean-context, NOT shared-memory; lead-aggregator decides

## Related

- [[sprint-day-0-skeleton-first]]
- [[claude-code-subagent-fanout]]
- [[chromium-img-svg-parent-fill-bug]]
- [[layered-eval-cascading-pattern]]
- [[clean-context-subagent-handoff]]
- [[g-eval-bias-mitigation-pattern]]
