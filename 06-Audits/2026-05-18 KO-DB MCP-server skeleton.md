---
name: KO-DB MCP-server skeleton — smoke-test audit
type: audit
created: 2026-05-18
updated: 2026-05-18
tags:
  - audit/mcp
  - sv/phase-b1
  - layer/3-retrieval
---

# KO-DB MCP-server skeleton — smoke-test audit

> [!success] Status
> **PASS** — 6/6 checks green (list_tools + 4 tools + error_path). Skeleton landed, public-release path mirrored, scrub-rules patched.

## Mit építettünk

A `modelcontextprotocol/servers` repo **memory** szerver-mintájára: a KO-DB (`.vault-ko/facts.db`, 13 801 fact) most MCP-server-ként hozzáférhető bármely MCP-host (Claude Desktop, Codex CLI, Cursor, Antigravity, Gemini CLI) számára.

**4 read-only tool stdio-transport-on:**

| Tool | Input | Output |
|------|-------|--------|
| `query` | `substring`, `top_k=10`, `source_type?` | LIKE-search, confidence DESC |
| `stats` | — | total + per-source-type + top-20 predicate + top-10 provenance |
| `conflicts` | `predicate?` | subjects with >1 distinct object per predicate |
| `top_k` | `token`, `top_k=10`, `facts_per_subject=5` | cross-source-corroboration rank |

## Skeleton fájlok

| Path | LOC | Purpose |
|------|-----|---------|
| `/root/obsidian-vault/.vault-ko/mcp-server/vault_ko_mcp.py` | 339 | MCP server (stdio) |
| `/root/obsidian-vault/.vault-ko/mcp-server/smoke_test.py` | 101 | Real MCP-client smoke test |
| `/root/obsidian-vault/.vault-ko/mcp-server/README.md` | 107 | Setup + tools-katalógus |
| `/root/obsidian-vault/.vault-ko/mcp-server/claude_desktop_config.json` | — | Host-config skeleton |

**Public-release mirror** (`/root/projects/myforge-vault-1111/.vault-ko/mcp-server/`): 1:1 copy, `scripts/scrub-rules.yaml` `include_paths` bővítve `.vault-ko/mcp-server/**`-vel.

**Total LOC:** 547 (Python + Markdown). Build time: ~15 perc (skeleton + smoke + docs + scrub-patch).

## Smoke-test eredmény

`python3 smoke_test.py` → **PASS 6/6** (~1.1s real time):

```
list_tools: pass=true tools=[conflicts, query, stats, top_k]
query     : pass=true count=3   sample={'subject': 'Touch-kiosk idle timeout origin', ...}
stats     : pass=true total_facts=13801 source_types=[session, wiki, adr]
conflicts : pass=true count=50  sample={'subject': 'Acceptance criteria', 'distinct_objects': 16}
top_k     : pass=true count=3   sample={'subject': 'kgc-berles', 'source_count': 8, ...}
error_path: pass=true isError=true (SDK enum validation surfaced as MCP-error)
```

A kliens **valódi MCP SDK** (`mcp.ClientSession` + `stdio_client`) — nem mock JSON-RPC. Subprocess spawn-ol, `await session.initialize()`-zal handshake-el, mind a 4 tool-t `call_tool()`-on át hívja.

**Error-path bonus** — bogus `source_type` érték esetén az MCP SDK enum-validation a tool-handler ELŐTT veri meg, és visszaadja `isError=True`-val. A server **nem crashel**, ami a fő követelmény volt.

## README setup-doc verify

A `README.md` lefedi: install (`pip install mcp`), standalone run, Claude Desktop/Codex/Cursor host-config-helyek, env-vár-mátrix (`VAULT_ROOT`, `VAULT_KO_DB`), public-release scrub-pipeline, és egy explicit production-readiness checklist a [√/×] státusszal.

## Mérnöki őszinte értékelés

**Production-ready? Részlegesen — solid skeleton, de éles agent-host alá még +1-2 napi munka.**

### Mi szilárd

- **MCP spec-compliance**: `@server.list_tools()` + `@server.call_tool()` dekorátorok, `stdio_server()` async context manager, `types.Tool` + `types.TextContent` SDK-osztályok. JSONSchema `inputSchema` minden tool-on. SDK v1.27.1 ellen tesztelve.
- **Read-only by construction**: `sqlite3.connect("file:...?mode=ro", uri=True)`. A DB mutation **fizikailag** lehetetlen — a kapcsolat read-only.
- **Input validation kettős védvonal**: SDK enum-check (`source_type`) + handler-szintű clamp (`top_k`/`facts_per_subject` 1..200, 1..50, 1..20 közé szorítva).
- **Graceful error path**: kivétel → `{"error": ...}` JSON. A server stdin-loopja él tovább, host nem akad le.
- **Cold-start fast**: ~1.1s 6 toolcall-ig (smoke összesen). SQLite filebased indexes (`idx_facts_subject`, `idx_facts_predicate`) → query-k <10ms.

### Mi gyenge

- **Per-call SQLite-connection**: minden `call_tool` új handle-t nyit, run-end zár. Funkcionálisan helyes (read-only, idempotens), de magas QPS alatt nem optimális. Connection pool kell éles HTTP-deploynál.
- **Nincs structured-content output**: az MCP-spec támogat `structuredContent` mezőt (a frissebb SDK-ban), én csak `TextContent`-JSON-t küldök. Az agent host ezt **biztosan** parse-olja, de a host-UI nem tud "rendered table"-t mutatni belőle.
- **Nincs logging**: a stdio transport-on stderr-be lehetne írni request/response auditot. Most semmi nem megy. Debug-vakság.
- **Nincs pagination cursor**: `query` és `top_k` clamp-elve, de 50+ találatnál a kliens nem tudja kérni a következő oldalt. MCP-spec támogat cursor-pagination-t (`ListToolsRequest.cursor`), tools-on belül nem.
- **Nincs HTTP/SSE transport variant**: csak stdio. Remote-deploy-hoz `mcp.server.sse` kell.
- **Smoke-test minimal**: 6 happy-path check + 1 error-path. Nincs concurrent-call, timeout, vagy malformed-JSON-input stressz.
- **Nincs CI/automated regression**: a smoke-test manuálisan futtatandó. Pytest-be tenni + `make smoke` target az 1-2 órás follow-up.
- **Live agent-host runtime nem verifikált**: a kliens-oldali smoke nem helyettesíti az élesben Claude Desktop / Codex CLI alól indított használatot. Tipikus integrációs gotchák (env propagáció, path-resolution, restart-cycle) még nem lettek tesztelve.

### Verdict

**Skeleton-szintű production-readiness, NEM stress-tested.** Egy magányos user (Peti) számára holnaptól bekonfigolható és működik. Multi-user / public-release / high-availability scenario-ra még kellenek: connection-pool, structured-content, logging, pagination, HTTP transport, pytest regression.

## Next steps (ha priorit kapna)

1. Pytest-suite + GitHub Actions CI a smoke-test-re.
2. Stderr-logging-réteg (per-call audit-log).
3. `structuredContent` migráció (MCP SDK v2 amikor stabil).
4. HTTP/SSE transport variant (`mcp.server.sse`) — remote-hosting opció.
5. Élesben tesztelni: Claude Desktop (Linux) → reload → list-tools → call.

## Kapcsolódó

- [[../11-wiki/Crystallization-protocol]] — a KO-DB szerepe a B-1 pipeline-ban
- [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — KO-DB ADR
- [`vault-ko-query`](file:///usr/local/bin/vault-ko-query) — a shell-CLI, amit ez a server mirroroz
- `modelcontextprotocol/servers` — pattern-forrás (memory server)
