---
name: Letta-style virtual-context pattern (skeleton)
type: wiki
tags: ["#type/wiki", "memory-architecture", "letta", "memgpt", "virtual-context", "agi", "agents"]
created: 2026-05-19
updated: 2026-05-19
related:
  - "[[00-Meta/core-memory-schema]]"
  - "[[11-wiki/sv-01-memory-architecture]]"
  - "[[06-Audits/2026-05-19 Letta virtual-context skeleton]]"
---

# Letta-style virtual-context pattern for the vault

> **TL;DR.** The vault used to do ~15–20 K tokens of aggressive pre-load at every
> session start. Letta (formerly MemGPT) formalises a better split: a tiny
> "core memory" (~2 K tokens) is **always loaded**; everything else is
> **archival memory**, fetched on demand via `vault-search` (semantic) or
> `vault-ko-query` (structured facts). We already have the archival primitives;
> this skill plus `vault-core-memory` adds the **core** half.

## Why aggressive pre-load doesn't scale

The original `load-session-context` skill cat-jeled five files at session
start: the project doc, the last five sessions, recent ADRs, the
Infrastructure note, and a filtered Backlog slice. Sum: 15–20 K tokens before
the user typed a single message.

That worked when sessions were short (5–15 turns) and Claude was the only
agent. By spring 2026 the vault hosts 40-turn sessions across Claude / Codex /
Gemini, sometimes interleaved. Three problems compounded:

1. **Cost per turn.** A 17 K head, repeated across 40 turns = 680 K tokens of
   redundant context per session. Most of it is never consulted.
2. **Stale cache.** Pre-loaded content is *frozen at session-start*. A Backlog
   update mid-session doesn't reach the agent until the next session — leading
   to silent off-by-one tasking.
3. **Saturation.** Aggressive pre-load makes the working window smaller for
   the actual conversation. A 200 K context with a 20 K head leaves
   180 K — fine. A 1 M context with a 20 K head still leaves 980 K, but the
   *attention* the agent pays to those head tokens decays. Letta-paper
   §5.1 calls this "context dilution".

## The Letta split

```
┌─────────────────────────────────────────────────────────┐
│                  LLM Context Window                      │
│                                                          │
│  ┌──────────────────────────────────────────────┐       │
│  │  CORE MEMORY (~2 K tokens, always loaded)    │       │
│  │  ┌─ user_profile     ─┐                       │       │
│  │  ├─ active_project   │                        │       │
│  │  ├─ open_tasks       │  6 fixed blocks        │       │
│  │  ├─ glossary         │  budget_tokens: 2048   │       │
│  │  ├─ infra_pins       │                        │       │
│  │  └─ recent_decisions ─┘                       │       │
│  └──────────────────────────────────────────────┘       │
│                       ▲                                  │
│              page-fault│                                 │
│                       │                                  │
│  ┌──────────────────────────────────────────────┐       │
│  │  ARCHIVAL MEMORY (unlimited, on-demand)      │       │
│  │     vault-search    "<semantic query>"        │       │
│  │     vault-ko-query  "<structured pattern>"   │       │
│  │   → top-K chunks injected this turn only      │       │
│  └──────────────────────────────────────────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

`vault-search` is **already the archival primitive.** It runs as a daemon,
indexes the whole vault into Memgraph's native vector index (bge-m3 multilingual),
and answers in ~1 ms p95. `vault-ko-query` is the *structured* archival:
13 K facts in SQLite, queryable by subject / predicate / object.

What was missing is the **core**. That's what the new `00-Meta/core-memory.yaml`
file + `vault-core-memory` CLI provide.

## The 6-block core schema (and why these six)

| Block | Why it's in core |
|---|---|
| `user_profile` | The agent needs Peti's language preference, terseness, and "destructive ops require confirmation" rule on every turn. ~150 tokens of pure house rules. |
| `active_project` | Without it the agent has to guess what the session is about. ~110 tokens of project state. |
| `open_tasks` | The 3–5 burning items — *not* the 460-line Backlog. Lets the agent answer "what's next?" without paging anything. |
| `glossary` | 14 acronyms (KGC / MFL / SV / KO-DB / …) used reflexively. Cheaper than letting the agent re-derive each one. |
| `infra_pins` | Prod VPS IP, KGC Postgres port, Memgraph port, VNC display. Recurring questions; cheap to pin. |
| `recent_decisions` | Last 5 ADR titles + 1-line `why`. Prevents the agent from contradicting yesterday's decision without first asking. |

Full spec: [[00-Meta/core-memory-schema]]. Budget is **2 K tokens soft / 3 K
hard**; today's initialized core sits at ~1 K tokens, leaving room for growth.

## How to migrate `11.11start` (the planned step)

Today, `11.11start` invokes the `load-session-context` skill which does the
aggressive pre-load. The migration is **NOT done today** — this wiki page
describes the recipe so a future session can execute it under user
supervision.

### Step 1. Add a flag to `load-session-context`

```bash
export VAULT_CONTEXT_MODE=virtual   # vs. "aggressive" (current default)
```

The skill checks the env-var. In `virtual` mode it skips the cat-jel and
instead emits a single prompt like:

```
You have core memory loaded. If you need details, call:
  vault-search "<query>" --top-k 5
  vault-ko-query "<pattern>" --top-k 8

<inline-core-memory>
{{contents of 00-Meta/core-memory.yaml `blocks.*.content`}}
</inline-core-memory>
```

### Step 2. Wire `11.11start` to refresh `active_project` + `open_tasks`

When a session opens, run automatically:

```bash
vault-core-memory update active_project "<slug>: <one-line goal>"
vault-core-memory update open_tasks "$(grep -A5 '^- \[ \]' 04-Tasks/Backlog.md | head -5)"
```

Idempotent — re-running gives the same result.

### Step 3. Wire ADR creation to refresh `recent_decisions`

A post-commit hook in `vault-autosave` checks if a new file landed in
`07-Decisions/` and prepends it to the block, trimming to 5.

### Step 4. Shadow-mode acceptance gate

Run both modes in parallel for two weeks (env-flag flip per session). Compare:

- Token cost per session (target: 75 % reduction)
- "Forgot X" complaints (must not increase)
- Time-to-first-useful-answer (target: ≤ 10 s vs current ~30 s pre-load)

If acceptance gate passes, flip the default to `virtual`. The aggressive mode
stays available as a backout for one release cycle.

## When to update core (mutable) vs leave archival alone (immutable)

| Trigger | Core block | Archival? |
|---|---|---|
| User says "from now on do X" | `user_profile` ✅ | No |
| `11.11focus` switch | `active_project` ✅ | No |
| Backlog item changes 🔺 priority | `open_tasks` ✅ | No |
| New ADR written | `recent_decisions` ✅ | Yes (full ADR in archival) |
| Wiki page added | (none) | ✅ Indexed by `vault-embed` |
| Daily journal entry | (none) | ✅ Indexed by `vault-embed` |
| New acronym appears | `glossary` ✅ if active | Yes (in 00-Meta/Glossary.md) |

**Rule of thumb:** core is for things the agent should *reflexively know*.
Archival is for things the agent should *be able to retrieve*. If you'd be
annoyed having to remind the agent every session, it belongs in core.

## Comparison with adjacent patterns

- **mem0 hierarchical memory.** mem0 splits into User / Session / Agent
  scopes with TTLs. Letta's core/archival is orthogonal: mem0's *User* scope
  maps roughly to our `user_profile`; the *Session* scope to our
  `active_project` + `open_tasks`. mem0 stores both in a single vector store
  and ranks by recency × scope; Letta separates the **always-loaded** head
  from the **retrievable** body. Our vault adopts the Letta split because the
  archival side is already richer (Memgraph + KO-DB + reranker) than mem0's
  single-store would justify.
- **Cognee memory-bus.** Cognee runs a pub-sub bus between cognitive modules
  (extractor, summariser, retriever). Our model is simpler: agents call
  `vault-search` / `vault-ko-query` directly. Cognee shines when many agents
  cooperate on a shared write-stream; our vault is read-heavy and the agents
  are mostly serial. We may revisit if multi-agent fan-out (sprint B-6) grows
  beyond ~5 concurrent agents.
- **OpenAI Memories.** OpenAI's hosted "memory" feature is conceptually
  Letta's user_profile block, but vendor-locked and opaque. We get the same
  benefit with a local, auditable YAML file.

## Open questions (for the migration session)

1. Should `glossary` be project-scoped? Today it's a single shared block; a
   bigger vault might want `glossary.kgc`, `glossary.sv`, etc.
2. How does core round-trip across the three agents? Claude / Codex / Gemini
   all read it because `00-Meta/` is in the shared vault — but should the
   write path (`update`) be agent-scoped to avoid race conditions?
3. Is 2 K the right budget? A 1 K core would force more page-faults; a 4 K
   core wastes head-bytes. The acceptance gate above will measure.

## Related

- [[00-Meta/core-memory-schema]] — formal spec of the file format
- [[11-wiki/sv-01-memory-architecture]] — the B-2 sprint that birthed this
- [[06-Audits/2026-05-19 Letta virtual-context skeleton]] — birth-audit
- [[05-Memory/README]] — the *de facto* core memory today
- Letta paper: <https://arxiv.org/abs/2310.08560> (MemGPT)
- mem0: <https://github.com/mem0ai/mem0>
- Cognee: <https://github.com/topoteretes/cognee>
