# vault-ko-mcp-server

MCP server exposing the **KO-DB** (`.vault-ko/facts.db`) as a Model Context Protocol tool surface for any compatible agent host (Claude Desktop, Codex CLI, Cursor, Gemini CLI, Antigravity, etc.).

Pattern reference: [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) — the official `memory` server, which exposes a JSON knowledge-graph over stdio. This server applies the same pattern to our SQLite-backed knowledge-objects DB (~13K facts, B-1 sprint Week 1–4).

## Why

The KO-DB already powers `vault-ko-query`, `vault-ko-report`, `load-session-context`, and the crystallization scorer's `--with-context` flag. MCP exposure gives **every** agent (not just our wrapper scripts) direct tool-call access to the same vault-confirmed knowledge — no shell escapes, no copy-paste, no token-burning context dumps.

## Tools

| Tool | Args | Returns |
|------|------|---------|
| `query` | `substring`, `top_k=10`, `source_type=null` | Up to `top_k` facts (id/subject/predicate/object/provenance/confidence/source_type), ordered by confidence DESC. Optional `source_type` filter: `session\|wiki\|adr\|notebooklm\|manual`. |
| `stats` | — | `{ total_facts, by_source_type, top_predicates (20), top_provenance (10) }`. |
| `conflicts` | `predicate=null` | Subjects with multiple distinct objects per predicate. Optional `predicate` LIKE filter. |
| `top_k` | `token`, `top_k=10`, `facts_per_subject=5` | Top-K subjects ranked by `(distinct_provenance DESC, max_confidence DESC, fact_count DESC)` — the cross-source-corroboration rank used by `load-session-context`. |

All tools are **read-only** — the server opens SQLite with `mode=ro` URI; mutation is impossible by construction.

## Install

```bash
pip install mcp           # MCP Python SDK (>=1.27, installs pydantic+starlette)
```

The script is self-contained — no other deps beyond stdlib + `mcp`.

## Run (standalone, stdio transport)

```bash
python3 /root/obsidian-vault/.vault-ko/mcp-server/vault_ko_mcp.py
```

The process speaks the MCP JSON-RPC protocol on stdin/stdout. It will appear idle to a human; that's correct — it's waiting for an MCP host to attach.

## Wire into an agent host

### Claude Desktop / Codex CLI

Copy the `mcpServers.vault-ko` entry from [`claude_desktop_config.json`](./claude_desktop_config.json) into your host's MCP config:

- **Claude Desktop (Linux):** `~/.config/Claude/claude_desktop_config.json`
- **Claude Desktop (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Codex CLI:** `~/.codex/config.json` (under `mcp.servers` — check your Codex version)
- **Cursor:** `~/.cursor/mcp.json`
- **Antigravity:** project `.antigravity/mcp.json`

Restart the host. The four tools appear as `vault-ko/query`, `vault-ko/stats`, etc.

### Claude Code (this CLI)

Add via the existing project MCP config (e.g. `~/.claude/mcp.json` or per-project `.mcp.json`):

```json
{
  "mcpServers": {
    "vault-ko": {
      "command": "python3",
      "args": ["/root/obsidian-vault/.vault-ko/mcp-server/vault_ko_mcp.py"],
      "env": { "VAULT_ROOT": "/root/obsidian-vault" }
    }
  }
}
```

## Env vars

| Var | Default | Purpose |
|-----|---------|---------|
| `VAULT_ROOT` | `/root/obsidian-vault` | Vault root path. |
| `VAULT_KO_DB` | `$VAULT_ROOT/.vault-ko/facts.db` | Override DB location entirely. |

## Public release (myforge-vault-1111)

A clean copy lives at `/root/projects/myforge-vault-1111/.vault-ko/mcp-server/`. Before each release, run the scrub pipeline against the bundled `facts.db` snapshot:

```bash
python3 /root/projects/myforge-vault-1111/scripts/scrub-public.py \
    --rules /root/projects/myforge-vault-1111/scripts/scrub-rules.yaml \
    --db /root/projects/myforge-vault-1111/.vault-ko/facts.db
```

If new PII-shaped predicates leak into the source vault, extend `scrub-rules.yaml` accordingly.

## Status

**Skeleton** (2026-05-18). Smoke-tested with a mock MCP client (all 4 tools PASS). Not yet exercised under a live agent host in production. Production-readiness checklist below.

### Production-readiness checklist

- [x] Read-only enforcement (SQLite `mode=ro` URI).
- [x] Input validation: `source_type` enum check, `top_k` clamped to safe range.
- [x] Error path: exceptions surface as JSON `{"error": ...}` instead of killing the server.
- [x] MCP SDK v1 spec compliance (`@server.list_tools` / `@server.call_tool` decorators, `stdio_server` context manager).
- [ ] Logging to stderr (currently silent — fine for stdio transport but blind for debugging).
- [ ] Connection pooling — currently opens a new SQLite handle per call (cheap, but not optimal).
- [ ] Pagination cursor — `query` and `top_k` are clamped; large result sets truncated.
- [ ] Auth — none (MCP stdio assumes a trusted local host process).
- [ ] HTTP / SSE transport variant — only stdio implemented.

## See also

- [`vault-ko-query`](../../../../usr/local/bin/vault-ko-query) — the shell CLI this server mirrors.
- ADR: `07-Decisions/2026-05-12 sv-5 crystallization automation arch.md`.
- Smoke-test report: `06-Audits/2026-05-18 KO-DB MCP-server skeleton.md`.
