---
name: vault-handoff cross-CLI bundle Day-0
type: adr
status: proposed
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/adr", "#project/sv", "b-6", "multi-agent", "cross-cli", "handoff"]
related:
  - "[[2026-05-12 sv-3 multi-agent orchestration arch]]"
  - "[[../11-wiki/sv-03-multi-agent-orchestration]]"
  - "[[2026-05-25 vault-core-memory MemGPT integration sprint plan]]"
  - "[[../11-wiki/cli-session-id-env-var-matrix]]"
---

# vault-handoff cross-CLI bundle Day-0

The first executable primitive of the B-6 Multi-agent sprint, scoped down from the full Orchestrator/Worker/Critic/Summarizer architecture to the smaller, sooner-useful piece: **moving a working session from one CLI to another** (Claude → Codex → Gemini, in any direction).

## Context

The vault already supports three CLIs via shared `AGENTS.md` (symlinked) and the `11.11*` session protocol. What hasn't existed: **a way to take a session-in-progress on Claude and resume it on Codex** (or vice-versa) without re-loading everything by hand. Today the user does this implicitly — opens a fresh CLI, runs `/11.11-uj-session` or `11.11focus`, then describes the context manually.

The full B-6 sprint (orchestrator + worker spawning + critic + summarizer) is 2-3 weeks. The handoff primitive is a single CLI plus an ADR — landable in one session, immediately useful.

## Decision

Land `vault-handoff` Day-0 today with three subcommands:

- **`vault-handoff export [--session SLUG] [--format json|markdown]`** — bundles the focused (or named) session state into a self-describing markdown or JSON. Includes: session metadata, full 6-block core-memory snapshot, top-5 open tasks for the project, last 3 ADRs touching the project, KO-DB top-5 facts on the project subject, last 5 timestamped `## Events` notes.
- **`vault-handoff import <bundle-file>`** — parses a bundle (JSON or markdown) and prints it. Day-0: print-only, NO state mutation. Subsequent weeks: opt-in `--apply` that creates the receiving session-file + writes pointer.
- **`vault-handoff list [--format text|json]`** — lists all open sessions with CLI affinity (which agent started each), highlights the current `CLAUDE_CODE_SESSION_ID` / `CODEX_*` / `GEMINI_SESSION_ID` chat's focused session.

Built on the existing primitives:

- **CLI session-isolation** ([[../11-wiki/cli-session-id-env-var-matrix]]) — per-chat pointers via `.active-session-<chat-id>`, with `vault-detect-chat-id` Codex-rollout fallback
- **Core memory** (today's Day-0 #1 deliverable) — the bundle's "always-loaded" half travels with the handoff verbatim
- **KO-DB** (`vault-ko-query`) — structured facts on the project subject add ~5 high-signal triplets for the receiving agent
- **AGENTS.md** (symlinked) — receiving agent already has the protocol; bundle just provides the state

## What Day-0 lands today

1. `/usr/local/bin/vault-handoff` (symlink to `.vault-tools/scripts/vault-handoff.py`, ~340 LOC)
2. `vault-handoff export` produces working markdown bundles end-to-end (tested on the focused superintelligent-vault session)
3. `vault-handoff list` correctly resolves per-chat focused session via `CLAUDE_CODE_SESSION_ID`
4. `vault-handoff import` is a printer (the receiving agent reads the markdown and paste-into-context)
5. This ADR + handoff-pattern wiki ([[../11-wiki/cross-cli-handoff-pattern]])

## What Day-0 does NOT do

- Receive-side state mutation. `import --apply` (create session-file + set pointer on the receiving CLI) is Week 1.
- Real-time sync between two simultaneous CLIs on the same session. That's "shared session" not "handoff" — different problem.
- Authentication / signature on the bundle. The vault is single-user; trust comes from same-user same-vault. If we ever support remote handoff (across machines), signing kicks in (out of scope today).
- Critic/Summarizer/Orchestrator agents (the wider B-6 ADR scope).

## Acceptance criteria (handoff primitive)

- [x] `vault-handoff export` on the focused Claude session produces a markdown bundle that a fresh Codex or Gemini agent can read without external context to know: which project, which file, what's open, what was just discussed
- [x] `vault-handoff list` shows the right "focused" indicator per `CLAUDE_CODE_SESSION_ID`
- [ ] **Week 1:** real cross-CLI test — same session paused on Claude, resumed on Codex via `vault-handoff export | scp | vault-handoff import` (or local pipe). Acceptance: Codex's first turn does NOT need any human-supplied context to continue.
- [ ] **Week 2:** `vault-handoff import --apply` writes a receiving session-file and sets the receiving CLI's `.active-session-<chat-id>` pointer.

## Why this slice first

- **Smallest landable piece** of the B-6 sprint that's useful day-1.
- **Reuses everything we already built** (core-memory, KO-DB, per-chat pointers, AGENTS.md).
- **No new agent spawning** — handoff is fundamentally human-controlled (user picks when to pause Claude and start Codex). The harder Worker-spawning primitive (`11.11worker`) stays deferred to the full B-6 sprint.
- **Tests the bundle shape** end-to-end before we wire it into the full Orchestrator/Worker flow.

## Open questions for later weeks

- **Bundle size cap.** A core-memory dump (~2KB) + 5 notes + 5 tasks + 3 ADRs + 5 facts ≈ ~5-8KB markdown. Should there be a hard cap to keep the receiving agent's paste-into-context cost predictable?
- **`--apply` safety.** When `import --apply` writes a session-file on the receiving CLI, what if the same session-slug already exists locally with newer content? Conflict resolution: refuse / pick-newer / interactive.
- **Codex/Gemini parity.** Codex specific behaviors (`~/.codex/AGENTS.md`, rollout-file format) and Gemini specific behaviors (`~/.gemini/.current-session-id` hook) need real cross-CLI smoke-tests in W1. Today's testing is Claude-only.
- **Bundle versioning.** `schema_version: 1` is in the bundle today. When we add fields in W2+, the receiving agent should not break — design the parser to ignore unknown keys.

## Rollback

`vault-handoff` is a read-only CLI today (`import` is print-only). Nothing to roll back. If the tool turns out wrong, `rm /usr/local/bin/vault-handoff` and the rest of the vault keeps working.

## References

- [[2026-05-12 sv-3 multi-agent orchestration arch]] — the full B-6 ADR (this is a subset)
- [[2026-05-25 vault-core-memory MemGPT integration sprint plan]] — the sister Day-0 #1
- [[../11-wiki/cli-session-id-env-var-matrix]] — the per-chat pointer system this builds on
- [[../11-wiki/cross-cli-handoff-pattern]] — usage walkthrough
