---
name: Filesystem-as-state pattern
type: wiki
lang: en
translated_from: filesystem-as-state-pattern
created: 2026-05-18
updated: 2026-05-18
tags: [pattern, agent-architecture, anthropic, ssot, durability]
---

# Filesystem-as-state pattern

> [!info] What it solves
> Writes the **agent's state** (memory, decision-trail, work-in-progress) into **filesystem files** at every step, not in-memory objects. The consequence: the chat-history can rebuild the entire state, multi-agent handoff works without secrets, and the git log is the session log.

## The core idea

A classic chat-agent keeps state in memory (the context window). Problem: if the agent dies, if the context overflows, if another subagent has to continue → data loss. **Filesystem-as-state** inverts this:

1. **Every component is a file** — session log, decision log, todo list, memory, agent config
2. **The agent reads/writes files** — does NOT pass object-state through functions
3. **"Context loading"** = `cat` the relevant files at the start of the conversation
4. **"Context saving"** = `Write` / `Edit` the relevant files at the end

The pattern is recommended in [Anthropic's "Code Execution with MCP"](https://www.anthropic.com/engineering/code-execution-with-mcp) and the canonical basis of the [Karpathy LLM-Wiki pattern](Karpathy-LLM-Wiki-pattern.md).

## Concrete implementation (vault)

A Johnny-Decimal-style markdown vault is a filesystem-as-state implementation for multi-agent setups:

| Component | File location | What it stores |
|---|---|---|
| **Agent config** | `AGENTS.md` (symlinked to per-tool locations) | Shared agent instructions |
| **Session state** | `08-Sessions/<slug>.md` | Current conversation timeline + events |
| **Decision trail** | `07-Decisions/YYYY-MM-DD <topic>.md` | ADR-style decision log |
| **Long-term memory** | `05-Memory/*.md` (User, Infrastructure, Skill-map) | Persistent profile + infra facts |
| **Project state** | `02-Projects/<slug>.md` | One-project-one-file, status + history |
| **Todo state** | `04-Tasks/Backlog.md` | Obsidian Tasks emoji syntax (`✅` / `🔴` / `🟡`) |
| **Crystallized knowledge** | `11-wiki/<slug>.md` | Evergreen knowledge in own words |
| **Raw input** | `10-raw/YYYY-MM-DD — <source>.md` | Articles, transcripts in immutable form |

## Why files, not a DB

| Aspect | File-based | DB-based |
|---|---|---|
| **Version control** | git out-of-the-box | DB-dump cron or WAL |
| **Multi-agent handoff** | another agent `cat` + Read tool | API + auth + schema agreement |
| **Audit trail** | git log = step-by-step | trigger-table or event-sourcing |
| **Diff-ability** | `git diff` native | DB-specific tooling |
| **Offline editing** | any editor + git-pull sync | online connection required |
| **Search** | grep / ripgrep / Obsidian | SQL / full-text-index |
| **Privacy** | local-only until push | always server-side |
| **Large-scale performance** | ~10K files OK, then slow | scales |

Vault philosophy: **filesystem-first** as long as possible, indexing layers **only mirror this** (Memgraph vector-index, KO-DB SQLite triplet store, embedding cache). The file remains the Source of Truth.

## Karpathy's layer scheme

The LLM-Wiki essay defines 3 layers:
- **Raw layer** (`10-raw/`) — immutable, as received (article, transcript)
- **Wiki layer** (`11-wiki/`) — evergreen, distilled in own words
- **Glossary layer** (`00-Meta/Glossary.md`) — slug-resolution index

Under this pattern, "raw" is never edited, only ingested. Only **distilled** knowledge goes into the wiki layer — the session log is the temporary buffer.

## Anti-patterns

| Anti-pattern | Problem | Correct form |
|---|---|---|
| **In-memory + cron snapshot** | Crash = lost state between two snapshots | Inline write at every step |
| **Single-mega-file** | `everything.md` 50MB → grep slows down, git-diff useless | Per-concept file + index |
| **DB + symlink trick** | DB is the truth, file is just an export → drift | File is truth, DB is only an index |
| **No frontmatter** | Missing YAML → Obsidian Dataview cannot read type/status fields | Every file gets `type:` + `created:` + `updated:` frontmatter |
| **No wikilink** | "see the .../something.md file" as a string → linter cannot validate | `[[02-Projects/<slug>]]` with folder prefix |

## Extension: indexing layers on top

Filesystem-as-state does not exclude indices:
- **Memgraph** (`bolt://localhost:7687`) — entity-graph + native vector-search
- **KO-DB** (`.vault-ko/facts.db`) — triplet store SQLite
- **Embed cache** — sentence-transformers chunks
- **Obsidian Dataview / Bases** — UI layer

These are **always regenerable from files** (idempotent backfill). The file remains canonical.

## Implementation checklist

- [ ] Every agent-state component has a dedicated file location
- [ ] Frontmatter on every file (`type`, `created`, `updated` minimum)
- [ ] Wikilink for every cross-reference instead of path-string
- [ ] Git commit after every agent session (autosave + session-stop)
- [ ] Index layers **regenerable** from files (idempotent backfill script)
- [ ] Multi-agent: shared AGENTS.md symlink, NOT per-agent copies
- [ ] Session-end ritual: every temporary state committed or moved to `08-Sessions/_archive/`

## Related

- [[Karpathy-LLM-Wiki-pattern]] — raw + wiki + glossary scheme
- [[Kepano-File-over-App-filozofia]] — Obsidian Kepano philosophy
- [[Johnny-Decimal-prefix]] — why 00-, 01-, 02- prefix
- [[Auto-context-loading]] — file-state loading at session start
- [[sv-01-memory-architecture]] — multi-tier memory on this file base
- [[audit-log-append-only-pattern]] — special filesystem-as-state where writes are append-only
