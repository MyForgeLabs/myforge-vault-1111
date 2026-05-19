---
name: Multi-agent pointer ownership lock pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/orchestration", "#topic/concurrency", "sv-3", "multi-agent", "lang/en"]
source: vault-meta NotebookLM Q4#5 / Q5#3 (2026-05-18, 63-source synthesis)
status: evergreen
lang: en
translated_from: multi-agent-pointer-ownership-lock.md
project: [[../02-Projects/superintelligent-vault]]
related: [[claude-code-session-id-per-chat-isolation]], [[cli-session-id-env-var-matrix]], [[sv-03-multi-agent-orchestration]]
---

# Multi-agent pointer ownership lock pattern

> **TL;DR:** A global mutable pointer (e.g. `.active-session`, `current.txt`) causes a **race condition** between parallel agent processes. The classic "one-pointer, one-agent" assumption collapses in multi-agent fanout. The solution is **NOT** a retry loop, but **per-agent ownership** (env-var, file-lock, or both).

## The problem

A vault-meta NotebookLM cross-project synthesis (63 sessions, 2026-05-18) counted **13+ documented incidents** where the `~/.claude/projects/<X>/.active-session` pointer file diverged — a background agent overwrote the focus pointer, and the next `11.11note` wrote into **a different project's session file**.

This is **not a configuration bug** — it's an **architectural gap**:

1. The global pointer is mutable shared state
2. Subagent fanout (8-174 parallel) writes this state **concurrently**
3. No locking, no ownership verification
4. Idempotency missing (the "overwrite" is silent, NOT a merge)

## Why the session-id env-var alone isn't enough

The [[claude-code-session-id-per-chat-isolation|2026-05-17 fix]] (`$CLAUDE_CODE_SESSION_ID` UUID in 5 `11.11*` scripts) **reduces but does NOT solve** the problem:

- ✅ Different-session-ID parallel Claude Code chats do NOT write each other's `.active-session`
- ❌ BUT: if **the same** chat spawns 8 subagent-fanout, they all inherit the same `CLAUDE_CODE_SESSION_ID` → race condition is back
- ❌ Codex/Gemini cross-CLI agents sharing `.active-session` → still vulnerable

## The solution: per-agent ownership lock

### Layer 1 — env-var-driven session targeting

```bash
# 11.11note implementation skeleton
SESSION_FILE="${SESSION_FILE:-$(cat ~/.claude/projects/$PROJ/.active-session)}"
# SESSION_FILE explicit env-var is fixed targeting, ALWAYS overrides the pointer file
echo "$(date -Iseconds) | $NOTE" >> "$SESSION_FILE"
```

**Pro:** the agent spawner knows exactly which session file to write to.
**Con:** must be passed on every subagent call.

### Layer 2 — Advisory file-lock (`flock`)

```bash
# 11.11focus implementation
flock -x ~/.claude/projects/$PROJ/.active-session.lock -c "echo $SLUG > ~/.claude/projects/$PROJ/.active-session"
```

**Pro:** OS-level serialization, atomic `read-modify-write`.
**Con:** stuck lock (crashed agent) → manual cleanup.

### Layer 3 — Per-agent UUID-prefixed pointer

```
~/.claude/projects/<proj>/.active-session              # legacy (backward-compat)
~/.claude/projects/<proj>/.active-session-<UUID>       # per-Claude-chat
~/.claude/projects/<proj>/.active-session-<UUID>-<N>   # per-subagent (UUID + worker-N)
```

`11.11note` first tries the UUID-N pointer, falls back to UUID, then legacy.

## Reference implementations

- **`rohitg00/agentmemory`** (NotebookLM source) — MCP-based isolated memory architecture; every agent instance has its own namespace + lock-controlled write
- **`MemGPT`** (Berkeley) — virtual context-management event system; every agent instance has its own episodic memory namespace
- **`GenericAgent`** L0-L4 architecture — per-agent context shard, no shared mutable pointer

## Why it matters for the Superintelligent Vault

The B-3 (Multi-agent Orchestration) sprint runs **8-174 parallel subagent fanout** (vault-skill-distill, ko-extract, gepa-mutate, eval-l2-nli-judge). They **all write** some form of vault state. The current 13+ pointer-divergence incidents only concerned `.active-session`; **many other shared pointers also exist** (`/root/.vault-config/env-defaults.md`, `~/.notebooklm-data/conversations/`, `/var/lib/vault-ko-db/audit.log`).

The ownership-lock pattern is **architecturally required** in B-3 Week 2-3, otherwise every new subagent-fanout feature is a new race-condition surface.

## Anti-patterns (what NOT to do)

1. **Retry loop for pointer-conflict detection** — silent overwrite is undetectable because there's no version stamp
2. **Sleep-loop before write** — luck, not synchronization
3. **Global mutex inside a chat** — the parent agent doesn't know how many subagent spawns will exist dynamically
4. **Ignoring "only happens rarely"** — 13+ documented incidents is not rare

## Cross-project evidence

The vault-meta NB Q5 cited:
- **6 different sessions** mention the `.active-session` divergence incident (kgc-kivetit, foxxi, kinda-project, boulium, obsidian-vault, sv-week1)
- **Same root cause:** global mutable pointer + parallel write
- **Same band-aid fix:** `11.11focus <slug>` explicit redirect — BUT that's NOT the root solution, just focus-recover

## Implementation roadmap

| Phase | Work | Result |
|-------|------|--------|
| 1 | `SESSION_FILE=` env-var support in the 5 `11.11*` scripts | Explicit targeting opt-in |
| 2 | `flock` wrapper on `.active-session` read/write | Advisory locking |
| 3 | Per-subagent UUID-N namespace pattern | Full per-agent isolation |
| 4 | Audit log for every pointer write (timestamp + agent UUID) | Incident forensics |

## When this pattern applies

- ✅ Multi-agent system holds global mutable shared state
- ✅ Subagent fanout (>2 parallel) is present
- ✅ Cross-CLI (Claude / Codex / Gemini) access the same state
- ❌ Inside a single-agent CLI session this is **not needed**

## Related

- [[claude-code-session-id-per-chat-isolation]] — 2026-05-17 first-layer fix (env-var only)
- [[cli-session-id-env-var-matrix]] — Claude / Codex / Gemini session-ID source of truth
- [[sv-03-multi-agent-orchestration]] — B-3 sprint host
- [[sandbox-branch-mutation-isolation]] — analogous pattern at git level
- [[../06-Audits/2026-05-18 vault-meta NB cross-projekt Q4-Q5]] — source audit

## Hungarian original

[[multi-agent-pointer-ownership-lock]]
