---
name: vault-core-memory integration roadmap
type: wiki
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/wiki", "#concept/memgpt", "#concept/virtual-context", "sv-1", "memory-architecture", "roadmap"]
related:
  - "[[../07-Decisions/2026-05-25 vault-core-memory MemGPT integration sprint plan]]"
  - "[[letta-virtual-context-pattern.en]]"
  - "[[../00-Meta/core-memory-schema]]"
  - "[[sv-01-memory-architecture]]"
---

# vault-core-memory integration roadmap

Week-by-week execution plan for the Letta/MemGPT virtual-context migration. Built on the 2026-05-19 foundation (`vault-core-memory` CLI + 6-block schema + simulate). The sprint adds the runtime integration with `11.11*` scripts and the session-start flow.

> [!info] Status snapshot (Day 0, 2026-05-25)
> Foundation: **DONE** · `page-in` runtime: **DONE today** · Auto-update hooks: **W1-3** · A/B measurement: **W4** · Default flip: **W5**

## Architecture in one diagram

```
┌──────────────────────────────────────────────────────────┐
│  Agent context (per turn)                                │
│                                                          │
│  ┌────────────────────┐    ┌─────────────────────────┐   │
│  │ Core memory ~2 KB  │    │ Page-in result (~2 KB)  │   │
│  │ (always loaded)    │ +  │ (on-demand, optional)   │   │
│  │ - user_profile     │    │                         │   │
│  │ - active_project   │    │ via vault-core-memory   │   │
│  │ - open_tasks       │    │     page-in "<query>"   │   │
│  │ - glossary         │    │                         │   │
│  │ - infra_pins       │    │ which calls             │   │
│  │ - recent_decisions │    │   vault-search --hybrid │   │
│  └────────────────────┘    │   + Memgraph chunk fetch│   │
│                            └─────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                  ↑                          ↑
                  │                          │
       ┌──────────┴──────┐         ┌─────────┴──────────┐
       │ /11.11-uj-      │         │ Archival           │
       │ session writes  │         │ (full vault)       │
       │ this from       │         │ - 11-wiki/         │
       │ core-memory.yaml│         │ - 08-Sessions/     │
       │                 │         │ - 06-Audits/       │
       │                 │         │ - 07-Decisions/    │
       └─────────────────┘         │ - 02-Projects/     │
                                   └────────────────────┘
                                   Indexed in Memgraph
                                   chunks via bge-m3
```

## Week-by-week plan

### Day 0 — 2026-05-25 (LANDED today)

- [x] **`page-in` subcommand** — `vault-core-memory page-in "<query>"` retrieves real Memgraph chunk text (not just titles), formats as agent-paste-ready markdown.
- [x] **ADR** — [[../07-Decisions/2026-05-25 vault-core-memory MemGPT integration sprint plan]]
- [x] **This roadmap wiki**
- [x] **AGENTS.md preview section** — when to use core-memory + page-in (doc-only, no behavior change)

**Acceptance:** `vault-core-memory page-in "memgraph"` returns a markdown block ≤4000 chars with real chunk-text from the top-5 hybrid hits. Verified.

### Week 1 — `11.11focus` auto-updates active_project block

- [ ] Add an `AGENT=claude /usr/local/bin/vault-core-memory update active_project "<auto-built block>"` call inside `11.11focus`
- [ ] Gate behind `VAULT_CORE_MEMORY_AUTO=1` (default OFF for the entire week)
- [ ] Auto-build content: project slug + current phase + 3 most-recent session bullet points (idempotent — same input → same output)
- [ ] Smoke-test: `11.11focus <slug>` then `vault-core-memory size` confirms active_project block was rewritten
- [ ] Rollback: `unset VAULT_CORE_MEMORY_AUTO` — `11.11focus` skips the call

**Acceptance:** with `VAULT_CORE_MEMORY_AUTO=1`, switching focus rewrites `active_project` in <500ms, never exceeds 600 tokens for the block, leaves the other 5 blocks untouched.

### Week 2 — `/11.11-uj-session` writes lean Pre-loaded context

- [ ] Add a `vault-core-memory show > /tmp/core.md` step to the session template
- [ ] When `VAULT_CORE_MEMORY_AUTO=1`, the agent's session-start workflow uses the 4-block core dump + writes `## Pre-loaded context` as ~4 lines + offers `vault-core-memory page-in` recommendations for likely first questions
- [ ] When `VAULT_CORE_MEMORY_AUTO` unset, the current aggressive pre-load remains
- [ ] Update the `bmad-load-session-context` skill (if it exists in user-installed skills) to prefer the lean path

**Acceptance:** A new session under `VAULT_CORE_MEMORY_AUTO=1` writes ≤500 chars of `Pre-loaded context` (vs ~5000 today), total session-start tool-uses ≤3 (vs ~8 today).

### Week 3 — Auto-update hooks for open_tasks + recent_decisions

- [ ] **open_tasks hook:** new file watcher (cron @ */15 min) on `04-Tasks/Backlog.md`. When `## 🔴 Sürgős` section changes, regenerate `open_tasks` block with the 3-5 highest-priority items.
- [ ] **recent_decisions hook:** new file watcher on `07-Decisions/`. When a new ADR is written, prepend title + 1-line "why" to `recent_decisions` block, truncate to keep ≤5 entries.
- [ ] Both hooks behind `VAULT_CORE_MEMORY_AUTO=1`. Each writes only one block (atomic via `vault-core-memory update`).
- [ ] flock-mutex on both (already 100% coverage policy).
- [ ] Rollback: comment out the cron lines.

**Acceptance:** after 7 days of cron-driven updates, `core-memory.yaml` size remains under 3000 tokens, no drift in unrelated blocks, no crash logs in `06-Audits/`.

### Week 4 — A/B measurement on real sessions

- [ ] Pick 10 real sessions (mix of project types). 5 with `VAULT_CORE_MEMORY_AUTO=1`, 5 without (control).
- [ ] Per session, record: token cost (transcript size + tool-uses), wall-clock to first-useful-answer, subjective context-quality (user-rated 1-5).
- [ ] Aggregate. Write audit MD `06-Audits/<date> vault-core-memory A/B measurement.md`.
- [ ] If virtual-context wins on ≥7/10 sessions for both cost AND quality, proceed to Week 5.

**Acceptance:** measurement is a read-only experiment; no rollback needed. Audit lands regardless of which side wins.

### Week 5 — Flip default (gated on A/B result)

- [ ] If Week 4 audit positive: set `VAULT_CORE_MEMORY_AUTO=1` as default in `~/.bashrc` / shell-init for the agent contexts
- [ ] Keep the aggressive pre-load as a fallback (`VAULT_CORE_MEMORY_AUTO=0`) for 4 weeks
- [ ] After 4 weeks of green operation, sunset the aggressive path

**Acceptance:** explicit user sign-off required after seeing Week 4 audit. No automatic flip.

## Open design questions (deferred)

1. **Multi-project sessions** — schema has `active_project: single`. Client-A ecosystem sessions touch 5-6 projects. Options: (a) rotate as user pivots, (b) widen schema to `active_projects: list[max 3]`, (c) introduce a higher-level "ecosystem" concept.
2. **NotebookLM cross-link** — `notebooklm:` ID in project frontmatter is high-signal. Should it be in `active_project` block automatically?
3. **B-7 typed-entity priority** — when page-faulting, should the agent prefer chunks whose linked entities (`Project`, `Sprint`) match the current `active_project`? Couples B-1 + B-7.
4. **Page-fault budget per session** — cap at 20 page-ins, flag mis-sized core if exceeded?

## Why this matters (compounding effects)

- **80% token-saving per session** is the headline (17K → 3.5K). At 40 turns/day across all sessions, that's ~500K tokens/day saved.
- **Context coherence** — the always-loaded core means the agent never "forgets" the user profile mid-session or contradicts a recent decision. Hard to measure in numbers but qualitatively visible.
- **Foundation for B-6 cross-agent handoff** — core-memory.yaml is portable: Codex / Gemini can load the same file and the handoff is trivial. Multi-agent task continuity without re-loading the world.
- **Future: agent-driven memory writes** — once core-memory is the runtime norm, the agent can `vault-core-memory update open_tasks "..."` mid-session as new tasks emerge. That's the Letta-style self-modifying memory primitive in production.

## See also

- [[../07-Decisions/2026-05-25 vault-core-memory MemGPT integration sprint plan]] — the binding ADR
- [[../00-Meta/core-memory-schema]] — the 6-block schema contract
- [[letta-virtual-context-pattern.en]] — pattern background
- [[sv-01-memory-architecture]] — original 5-layer research that motivated this
- [[claude-code-subagent-fanout]] — the sister "no-LLM-cost" primitive
