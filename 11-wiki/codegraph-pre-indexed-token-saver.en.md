---
name: Pre-indexed code-knowledge-graph as token-saving MCP layer
type: wiki
tags: ["#type/wiki", "knowledge-graph", "code-intelligence", "mcp", "tree-sitter", "token-economy", "lang/en"]
created: 2026-05-19
updated: 2026-05-19
lang: en
translated_from: codegraph-pre-indexed-token-saver.md
source_repo: colbymchenry/codegraph
source_url: https://github.com/colbymchenry/codegraph
source_license: MIT
---

# Pre-indexed code-knowledge-graph as token-saving MCP layer

The pattern: if you give a coding-agent **structured knowledge** about the codebase (symbol graph, call graph, framework-route map), then instead of scattering `grep + Read + ls` tool calls in cycles, **a single graph query** can answer exploration-level questions. colbymchenry/codegraph proves it with concrete numbers: **92% fewer tool calls · 71% faster** on 6 real-world codebases (VS Code, Excalidraw, Claude Code Python+Rust, Claude Code Java, Alamofire, Swift Compiler).

## The principle

A coding agent does two things during exploration:

1. **Discovery** — "where is function/route/class X?" — lots of `grep` + `find` + `ls`
2. **Reading** — "what code is in it / what does it call?" — lots of `Read`

Discovery is fully replaced by a `tree-sitter` pre-indexed SQLite graph because the relations are already explicit edges. With a single `codegraph_explore` tool call the agent gets:

- Entry points (symbols where a topic starts)
- Related symbols (callers, callees, references)
- Code snippets (file pieces attached via the graph)

The Swift Compiler benchmark is the edge case: **25,874 files / 272,898 nodes, ~4 min indexing, 6 explore-calls / 35s / 0 file reads** for a complex cross-cutting question. The same with `grep + Read` takes 37 tool calls / 2m 8s.

## Architecture layers

```
files
  -> ExtractionOrchestrator (tree-sitter, 19+ langs) -> DB (nodes/edges/files)
        -> ReferenceResolver (imports, name-matching, framework patterns)
              -> GraphQueryManager / GraphTraverser (callers, callees, impact)
                    -> ContextBuilder (markdown/JSON for AI consumption)
```

Six base layers, all swappable. Storage is `better-sqlite3` (native) if available, with a **transparent fallback to `node-sqlite3-wasm`** (wasm is the slow path but zero-native-dep deployment). The `codegraph status` command tells you which is live. This fallback pattern is reusable wherever you want a native binary optional + slow-fallback.

## Deterministic, non-LLM extraction

The knowledge base is not LLM-summarized — every `NodeKind` (file, class, function, method, route, …) and `EdgeKind` (contains, calls, imports, references, extends, decorates, …) is derived from the tree-sitter AST. This yields two key properties:

- **Reproducible** — the same code always generates the same graph
- **No hallucination** — the graph can't invent what a function calls, only what it syntactically actually calls

This is an explicit dual to our [[two-tier-graph-extraction]] pattern: **Tier-2 deterministic** role (like the graphify tool on the vault). What goes to LLM extraction (entity disambiguation, semantic relation naming) is **Tier-1**; what's syntactically derivable is Tier-2 — and faster, cheaper, more reliable.

## Framework-aware route detection

Special idea: the `route` NodeKind. It recognizes 13 framework patterns (Django, Flask, FastAPI, Express, Laravel, Rails, Spring, Gin/chi/gorilla, Axum/actix/Rocket, ASP.NET, Vapor, React Router, SvelteKit, Vue/Nuxt). A `Route::get('/users', ...)` Laravel call produces a `route` node, with a `references` edge to the controller method. So when the agent asks for callers of a controller action, **the graph also returns the URL pattern** that binds it.

For us, this is directly usable in the [[wp-rest-api]] / [[wordpress-router]] / [[wp-block-development]] context: WordPress REST route → callback handler relation is extractable with the same pattern (custom resolver).

## Multi-agent installer architecture (reusable pattern)

The `src/installer/targets/` pattern — 4 agent targets (claude, cursor, codex, opencode) — is a folder-level **plug-and-play registry**. Adding a fifth agent: **one new file in `targets/` + one entry in `registry.ts`**. The common interface `AgentTarget` says:

- Config file location (per OS)
- MCP-server JSON/TOML/JSONC write (preserving existing content)
- Instructions file path (`CLAUDE.md`, `.cursor/rules/codegraph.mdc`, `~/.codex/AGENTS.md`)

`jsonc-parser` does surgical edits preserving user comments and formatting across re-install/uninstall round-trips. The hand-rolled `targets/toml.ts` TOML serializer is scoped only to `[mcp_servers.codegraph]` — not a dependency, and preserves sibling tables verbatim.

We can adopt this pattern in the SV vault for agent-config management (Claude/Codex/Gemini three agents). Currently it's symlink-based; if per-agent specific config injection is ever needed, this 4-target registry pattern is the reference.

## MCP server-instructions as contract

`src/mcp/server-instructions.ts` is the first message every agent sees in the MCP `initialize` response. **It is NOT the same file as the per-agent instructions template** — but **they must be kept in sync** (`instructions-template.ts` + `.cursor/rules/codegraph.mdc` + `server-instructions.ts`). The repo's CLAUDE.md has a house rule for it: "when you change tool instructions, update ALL THREE".

A reusable governance pattern for any system where **the same knowledge is replicated in 2+ places by necessity** (technical constraint, no single source possible). Example from the SV stack: `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` are symlinked, but per-agent host-specific instructions (e.g. slash-command names vs shell CLI names) diverge — this kind of knowledge has to live in a shared section of a doc.

## Always-fresh file-watcher

Native OS events (FSEvents/inotify/RDCW) + debounced auto-sync. The graph stays fresh with code changes. Critical because a stale graph gives the agent false confidence. Incremental update uses SHA-256 change detection, NOT full re-index.

## What we can adopt for our SV stack

Concrete adoptables:

- **Pre-indexed graph as MCP tool** — our KO-DB (13K+ facts) is text / structured-triplet level, NOT code level. A codegraph-like code-graph integration would meaningfully save tokens on every code project context-loading (kgc-erp / boulium / etc.).
- **Explicit naming of the Tier-2 deterministic pillar** — we currently treat graphify as Tier-2, but tree-sitter extraction also belongs there and is code-specifically better.
- **Framework-route detection** — WordPress REST-route extraction would be reusable for FOXXI/KGC/Boulium.
- **Multi-target installer pattern** — if agent-specific injection is ever needed.

## Source references

- Repo: <https://github.com/colbymchenry/codegraph>
- npm: `@colbymchenry/codegraph` (MIT)
- Engine: tree-sitter + better-sqlite3 / node-sqlite3-wasm
- Raw ingest: [[../10-raw/external/colbymchenry_codegraph/README]] + [[../10-raw/external/colbymchenry_codegraph/CLAUDE]]

## Related

- [[sv-04-tool-composition]] — agent tool stack where such a graph tool sits
- [[sv-06-world-model-knowledge-graph]] — KG axis, code graph as a special case
- [[two-tier-graph-extraction]] — Tier-1 LLM / Tier-2 deterministic, codegraph Tier-2 reference
- [[vault-knowledge-graph-overview]] — vault's own KG, currently NOT code level
- [[Karpathy-LLM-Wiki-pattern]] — analog to the wiki/distillate layer

## Hungarian original

[[codegraph-pre-indexed-token-saver]]
