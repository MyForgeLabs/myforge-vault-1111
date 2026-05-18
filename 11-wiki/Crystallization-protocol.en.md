---
name: Crystallization protocol — session-stop propagation
type: wiki
tags: ["#type/reference", "agents", "11.11", "crystallization", "sv-b1"]
created: 2026-04-30
updated: 2026-05-16
lang: en
translated_from: Crystallization-protocol.md
source:
  - "[[Karpathy-LLM-Wiki-pattern]]"
  - "[[11.11-session-protokoll]]"
---

# Crystallization protocol

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[Crystallization-protocol.md]] (Hungarian version).

When a session closes (`/11.11stop`), the agent **must** transform learnings into long-term knowledge: every `## Learnings` bullet is propagated into the appropriate persistent layer. **This is not optional.** The vault only "compounds" (in the Karpathy sense) if knowledge is carried into the persistent layers at every session close.

## Protocol overview (manual mode — original)

```
session close → agent collects learnings → classifies them
              → BATCH PREVIEW: shows them all to the user at once
              → user OKs / modifies / skips
              → agent executes
              → propagation log appended to the session file
```

## Auto-mode addition (G-Eval scoring layer)

In addition to the manual protocol, an automatic scoring layer can be added that computes a 4-dimensional G-Eval confidence for every Learning bullet. The routing decision tree is unchanged — scoring appears as a **signal**, NOT as a replacement for human decision at conservative (0.95) and aggressive (0.85) thresholds.

```
session close → crystallize <slug> --scorer claude-code --with-context  (opt-in)
              → Phase 1: pending request file
              → general-purpose Agent scores using G-Eval prompt (4 dim × 5 scale, with corpus context)
              → Phase 2: response file → confidence router → audit log
              → routing decision tree (unchanged)
              → batch preview to user (now with confidence color coding)
              → user OK → propagation → propagation log
```

**Confidence routing:**

| Confidence | Route | Threshold rules |
|---|---|---|
| ≥ threshold | `auto-prop` | Shadow (1.0): audit-log only · Conservative (0.95): 1-shot user confirm · Aggressive (0.85): no confirm |
| 0.70 — threshold | `batch-preview` | To user per decision-tree routing |
| < 0.70 | `discard` | Audit log only, NOT propagated |

**Threshold config:** held in a hot-reloadable file. Default 1.0 (shadow); use 0.95 (conservative) once a calibration benchmark shows verdict agreement > target (e.g., 96.7% vs 90% goal).

**Cost:** $0 (claude-code scorer via subagent-fanout, see [[claude-code-subagent-fanout]]).

## Routing decision tree

For each Learning bullet, the agent walks through this list; **first match wins**:

1. **Architecture-level decision** ("we choose X over Y because…", with reasoning + alternatives) → new ADR document
2. **Vault convention / rule** (new tag, new frontmatter field, new folder rule) → tag taxonomy or frontmatter schema
3. **New evergreen concept / playbook** (a pattern, a recipe, a process) → new wiki entry
4. **New abbreviation / slug / codename** → glossary
5. **Server / port / cron / DB / service knowledge** → infrastructure memory
6. **Skill description (agent skill / capability)** → skill map
7. **User preference** (style rule, "always use X in section Y") → user preferences memory
8. **Dashboard / access rule** → access control memory
9. **Project-specific knowledge** (status change, gotcha, port value, deploy recipe for one project) → project file
10. **New TODO / task** → backlog (correct priority section)
11. **Else** → ask the user

## Batch preview UX

The user wants to see all suggestions at once, NOT bullet-by-bullet:

```
🧠 N learnings to propagate — I suggest:

[1] "<bullet 1 quote>"
    → infrastructure-memory ▸ "Next.js gotchas" section (new subsection)
    → preview: <first 2 lines of the text to be inserted>

[2] "<bullet 2 quote>"
    → user-memory ▸ "UI/UX preferences"
    → preview: ...

[3] "<bullet 3 quote>"
    → new ADR: <YYYY-MM-DD topic>.md
    → status: accepted, affects: <project>
    → preview: ...

[4] "<bullet 4 quote>"
    → new evergreen: wiki/<topic>.md
    → preview: ...

OK? You can reply briefly:
- "OK" → all executed
- "1-3 OK, 4 to project-X.md" → 1-3 fine, route 4 elsewhere
- "skip 2" → drop 2, keep the rest
- "stop" → nothing
```

## Propagation log

A `## Propagation log` section is appended to the session file, time-stamped:

```markdown
## Propagation log

- 2026-04-30T12:34 — [1] → infrastructure-memory (new gotcha)
- 2026-04-30T12:34 — [2] → user-memory (UI/UX prefs added)
- 2026-04-30T12:34 — [3] → new ADR <YYYY-MM-DD topic>.md
- 2026-04-30T12:34 — [4] → new wiki/<topic>.md
- 2026-04-30T12:35 — Backlog updated (3 new TODOs #project/<slug>)
```

This is **auditable later**: you can trace "where did this learning come from" → the propagation log points back to the source session.

## What NOT to propagate

- **Transient state** that will be irrelevant in 1 day ("the build was running on the server just now")
- **Bug info we already fixed** (the fix is in the code, no document pollution needed)
- **Implementation steps** that were only interesting during the session ("I tried X, it didn't work")
- **Duplicate knowledge** already documented elsewhere (then just link)

If unsure → keep it in `## Learnings` (lives in the session file as raw) but DO NOT propagate to persistent layers.

## Edge cases

| Situation | What to do |
|-----------|------------|
| A bullet fits in two places | Pick one, or duplicate with a **short link** (put the source in the ADR/wiki, only `→ see [[…]]` elsewhere) |
| No bullet is propagation-worthy | OK, just write "## Propagation log\n\n- (no propagation-worthy learnings)" |
| User says "stop" | Respect it, just record "user skipped" in the propagation log |
| User changes the target | Override the suggestion, propagate per the user's redirection |
| New ADR/wiki needed, but user is offline | Leave in the session `## Learnings` with a flag: `<!-- TODO-PROPAGATE: new ADR or infra memory -->` — handle next time |

## Combined with aggressive context loading

If you have already preloaded the project file + last 5 sessions + ADRs at session start (per the context-loading protocol), then propagation is **faster**: the agent knows which section the new knowledge fits into and won't duplicate.

## Related

- [[Karpathy-LLM-Wiki-pattern]] — the meta-principle behind this
- [[Auto-context-loading]] — the start-time counterpart
- [[claude-code-subagent-fanout]] — how to scale the scoring layer at $0
- [[g-eval-bias-mitigation-pattern]] — the scorer's bias-mitigation prompt
