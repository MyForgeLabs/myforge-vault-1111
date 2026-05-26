---
name: ENABLE_TOOL_SEARCH activation
type: audit
created: 2026-05-17
updated: 2026-05-19
tags: ["#type/audit"]
project: superintelligent-vault
axis: B-4
tag_backfill: 2026-05-19
---
# ENABLE_TOOL_SEARCH activation (SV B-4)

> [!info] Cél
> A Claude Code agent eager-load-olja az összes 462 SKILL.md skill-leírást és az MCP-tool-schemákat a context-window-ba. Az `ENABLE_TOOL_SEARCH=auto` env-var bekapcsolja a beépített dinamikus tool-search-et: csak a deferred tool-okat látja név szerint, a teljes JSONSchema-t a `ToolSearch` tool query-zi be on-demand → 10%+ token-savings + Lost-in-the-Middle hibák csökkenése.
> NotebookLM-mining (sv-04, 2026-05-17) HIGH-prioritású ajánlása.

## Settings update — diff

**File:** `/root/.claude/settings.json`
**Backup:** `/root/.claude/settings.json.bak.20260517` (33159 byte)

### Before (last 5 lines)

```json
  "theme": "dark-daltonized",
  "voiceEnabled": true,
  "agentPushNotifEnabled": true,
  "effortLevel": "xhigh"
}
```

### After

```json
  "theme": "dark-daltonized",
  "voiceEnabled": true,
  "agentPushNotifEnabled": true,
  "effortLevel": "xhigh",
  "env": {
    "ENABLE_TOOL_SEARCH": "auto"
  }
}
```

JSON-validáció: ✅ `python3 -m json.tool` passes.

`settings.local.json` érintetlen (csak `permissions.allow` listát tartalmaz; nincs `env` block szükség).

## MCP audit

A Claude Code MCP-szervereket két helyről kezeli:

1. **`~/.claude.json`** — lokális stdio MCP-k (`chrome-devtools`)
2. **Plugin marketplace** (`claude.ai`) — hosted HTTP MCP-k (Figma, Canva, Gmail, Drive, Calendar, Adobe, Higgins, WordPress)
3. **Enabled plugins** a `settings.json/enabledPlugins`-ben — `context7`, `playwright`, `ui-ux-pro-max`, stb.

> [!note] alwaysLoad flag
> A Claude Code (2026-05-17 állapot) **nem támogat** explicit `alwaysLoad` flag-et MCP-konfigben. Az `ENABLE_TOOL_SEARCH=auto` mód automatikusan elhalasztja a ritka tool schema-betöltését — a teljes tool-listát látja, de csak névszerint, a JSONSchema-t a `ToolSearch` tool húzza be.

### Élő MCP-szerverek (`claude mcp list`)

| Szerver | Típus | Kategória | ENABLE_TOOL_SEARCH viselkedés |
|---|---|---|---|
| `plugin:context7:context7` | stdio (npx) | **Kritikus** — dokumentáció lookup | Deferred-list, lazy-load |
| `plugin:playwright:playwright` | stdio (npx) | **Kritikus** — browser automation | Deferred-list, lazy-load |
| `chrome-devtools` | stdio (npx) | **Kritikus** — perf + console + Lighthouse | Deferred-list, lazy-load |
| `claude.ai Gmail` | HTTP | Gyakori (Peti workflow) | Deferred-list, lazy-load |
| `claude.ai Google Calendar` | HTTP | Gyakori | Deferred-list, lazy-load |
| `claude.ai Google Drive` | HTTP | Gyakori | Deferred-list, lazy-load |
| `claude.ai Figma` | HTTP | Ritka (csak design-tasknál) | Deferred-list, lazy-load |
| `claude.ai Canva` | HTTP | Ritka | Deferred-list, lazy-load |
| `claude.ai Adobe Marketing Agent` | HTTP | Ritka | Deferred-list, lazy-load |
| `claude.ai Adobe for creativity` | HTTP | Ritka | Deferred-list, lazy-load |
| `claude.ai higgins` | HTTP | Ritka | Deferred-list, lazy-load |
| `claude.ai WordPress.com` | HTTP | Ritka (csak WP-tasknál) | Deferred-list, lazy-load |
| `hostinger-mcp` | stdio (npx) | Ritka (DNS/VPS opszor) | Deferred-list, lazy-load |

### Ajánlott action (post-monitoring)

- **2 hét monitorozás** session-átlag context-méreten (mai baseline ~50K → target ≤45K)
- Ha NEM csökken észrevehetően: ellenőrizni hogy a Claude Code engine valóban honorálja-e az env-var-t (lehet, hogy belső flag, nem env)
- Ritka MCP-k (Adobe, Canva, higgins, WordPress.com) **disable** opció `claude mcp remove <name>` ha nem jön elő hetekig

### Konfigfájlok és backup-ok

| File | Backup |
|---|---|
| `/root/.claude/settings.json` | `.bak.20260517` (33159 byte) |
| `/root/.claude/settings.local.json` | `.bak.20260517` (érintetlen) |
| `/root/.claude.json` | `.bak.20260517` (érintetlen) |

A `~/.mcp.json` és `~/.claude/.mcp.json` **nem létezik** ezen a gépen — az MCP-konfiguráció `~/.claude.json` `mcpServers` blokkjában van.

## Várt token-savings

| Mérőszám | Baseline (eager) | Target (auto) | Megjegyzés |
|---|---|---|---|
| Skill-leírás token-fogyasztás | ~462 SKILL.md description × ~80 token = **~37K token** | ~3-5K | Csak a name-listát látja, description-t a Skill tool dinamikusan kéri |
| MCP-tool schema fogyasztás | ~250 tool × ~300 token = **~75K token** | ~5-8K | Deferred-list (név) + ToolSearch on-demand |
| **Teljes context-window mentés** | — | **~95-100K token** | NotebookLM-mining HIGH-prio finding |
| Lost-in-the-Middle hibák | Magas (long-context degradation) | Alacsony | Anthropic 2025 H2 paper |
| Session-start latency | ~3-5s eager-load | ~1-2s lazy | Mérendő |

## Next step

- **2026-05-17 délután** új session-t indítani (`/11.11-uj-session "tool-search-validation"`), mérni a session-start kontextus-méretét, összehasonlítani a baseline-nal
- Ha működik: **`crystallize`** a finding-ot `[[11-wiki/enable-tool-search-auto-pattern]]`-be (evergreen koncepció)
- B-4 Week 1 milestone: settings + MCP-audit committed, monitoring rendszerbe állítva

## Kapcsolódó

- [[02-Projects/superintelligent-vault]] — B-4 axis (Tool composition)
- [[../08-Sessions/2026-05-17-obsidian-vault-3]] — az ajánlás forrása
- [[11-wiki/claude-code-harness-blocks]] — settings.json patterns
- [[05-Memory/Agents-skill-suite]] — skill-katalog
