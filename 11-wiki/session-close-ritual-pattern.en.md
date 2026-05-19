---
name: session-close-ritual-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/agent-workflow", "#topic/session-management", "#topic/crystallization", "#topic/11.11", "lang/en"]
lang: en
translated_from: session-close-ritual-pattern.md
---

# Session-close ritual — agent-output validation + crystallization trigger

## TL;DR

**Session close** is NOT just "commit + push", but a structured ritual: the agent (1) writes Summary + Learnings + Next sections from chat history, (2) **VERIFIES** every referenced artifact path on disk-state ("event-log claim ≠ real disk state"), (3) launches the crystallization flow, (4) commits + pushes. Skipping any of the 4 steps causes silent divergence inside the vault.

## Background (3+ source evidence)

- [[bmad-cross-machine-artifact-verification]] — "session-close ritual requires: ls verification of all referenced /root/...md paths; produces: MISSING-on-server diagnostics"
- [[11.11-session-protokoll]] — canonical 11.11* CLI workflow + slash-command mapping
- [[Crystallization-protocol]] — post-close propagation decision tree
- [[claude-code-session-id-per-chat-isolation]] — per-chat pointer file (`.active-session-$CHAT_ID`) so session-close is NOT cross-chat-corruptible
- [[verification-step-before-claim]] — base principle: claimed ≠ verified

## Pattern

The `11.11stop` (or `/11.11-zar-session`) trigger runs 4 steps in mandatory order:

**1. Write Summary + Learnings + Next** (agent's task). Into `08-Sessions/<slug>.md` from chat history:
- `## Summary` — 5-15 sentences, what we did
- `## Learnings` — N learnings as bullets (evergreen-worthy!)
- `## Next` — backlog + concrete next action

**2. Artifact verification** ([[bmad-cross-machine-artifact-verification]]):
- For every `/root/.../...md` path mentioned in the session → `ls` check
- If MISSING → insert `MISSING-on-server: <path>` audit-line into the session file
- Cross-machine context: file referenced on Mac that isn't yet synced to the server → DETECT, NOT silent pass

**3. Crystallization flow** (opt-in, `VAULT_CRYSTALLIZE_AUTO=1`):
- `11.11crystallize <slug> --scorer claude-code --with-context`
- G-Eval scoring (4 dim × 5 scale) on every Learning bullet
- Routing decision tree ([[Crystallization-protocol]]): ADR / wiki / glossary / infra / skill / user-pref / task
- Batch-preview to user, propagation after confirmation

**4. Git commit + push** (script's task):
- `commit -m "session: <slug> + AGENT=<claude|codex|gemini>"`
- Auto-push to GitHub (`vault-autosave` also runs every 10 min, but session-close is the atomic state)
- Session file gets a `closed: true` frontmatter flag

## Anti-patterns

- **Only Summary, no Learnings**: 6 months later the session isn't searchable — no evergreen section to propagate into the wiki.
- **Referenced paths not verified**: Mac-Obsidian session writes `[[02-Projects/X]]`, but file isn't synced to server yet — silent broken link. `ls` check is mandatory.
- **Crystallization NEVER fires**: if session stays open (visible in `11.11ls`) but never closes, Learnings never propagate. Weekly `vault-stuck-detect` audit.
- **Skipping the commit**: silent disk-state divergence — local changes lost or git-conflict on next `11.11start`.
- **"Event log = truth"**: `11.11note "done"` ≠ file existing on disk. Event log is event log, NOT authoritative state.

## Reusable rules

1. **Agent finishes the session**, NOT the user. Agent owns the 4-step ritual.
2. **3 structured sections mandatory**: Summary, Learnings, Next. Incomplete session = stuck flag.
3. **Verify-before-propagate**: every referenced artifact `ls`-checked, MISSING-line in the session.
4. **Crystallization opt-in but default-encouraged**: `VAULT_CRYSTALLIZE_AUTO=1` env-var, NOT hard-coded.
5. **Idempotency**: if `11.11stop` accidentally runs twice, do NOT create duplicate summary. Frontmatter `closed: true` flag filter.
6. **Atomic state**: either all 4 steps succeed or none. On failure, rollback-able.
7. **Audit log**: every close (`<ts>, <session>, <agent>, <verify-result>, <crystallize-result>`) append-only.

## Pitfalls

- **Concurrent close from 2 chats**: per-chat session-id isolation ([[claude-code-session-id-per-chat-isolation]]) solves this, BUT the bash `set -e` + `vault-detect-chat-id` exit-1 collision pattern (MEMORY) gotcha — `2>/dev/null || true` patched.
- **Vault-autosave during session-close**: 10-minute cron commit may precede the session-close commit → forked history. Autosave skips open session files.
- **Mac-server double-conflict cascade**: session file mutated on Mac and server both → 2 conflicts + opposite saves. `11.11focus`-style single-source-of-truth mandatory during the session.
- **Crystallization failure blocks commit**: if G-Eval fails or times out, session-close still goes — propagation is a separate retry batch.

## Related

- [[11.11-session-protokoll]] — full 11.11 workflow
- [[Crystallization-protocol]] — propagation decision tree
- [[bmad-cross-machine-artifact-verification]] — verify-step detail
- [[claude-code-session-id-per-chat-isolation]] — per-chat pointer file
- [[verification-step-before-claim]] — base principle
- [[audit-log-append-only-pattern]] — log rule
- [[Karpathy-LLM-Wiki-pattern]] — background philosophy (raw → distilled)

## Hungarian original

[[session-close-ritual-pattern]]
