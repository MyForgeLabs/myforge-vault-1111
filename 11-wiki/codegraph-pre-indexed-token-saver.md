---
name: Pre-indexed code-knowledge-graph mint token-spóroló MCP-réteg
type: wiki
tags: ["#type/wiki", "knowledge-graph", "code-intelligence", "mcp", "tree-sitter", "token-economy"]
created: 2026-05-19
updated: 2026-05-19
source_repo: colbymchenry/codegraph
source_url: https://github.com/colbymchenry/codegraph
source_license: MIT
---

# Pre-indexed code-knowledge-graph mint token-spóroló MCP-réteg

A minta: ha egy coding-agent-nek **strukturált tudást** adunk a codebase-ről (symbol-graph, call-graph, framework-route map), akkor ahelyett, hogy `grep + Read + ls` cikluson keresztül szétszórja a tool-call-okat, **egy darab graph-query**-vel meg tudja válaszolni az exploration-szintű kérdéseket. A colbymchenry/codegraph konkrét számokon bizonyítja: **92% kevesebb tool-call · 71% gyorsabb** 6 real-world codebase-en (VS Code, Excalidraw, Claude Code Python+Rust, Claude Code Java, Alamofire, Swift Compiler).

## Az alapelv

A coding-agent két dolgot csinál exploration-során:

1. **Discovery** — "hol van X függvény / route / class?" — sok `grep` + `find` + `ls`
2. **Reading** — "milyen kód van benne / mit hív?" — sok `Read`

A discovery-fázist a `tree-sitter`-rel pre-index-elt SQLite-graph teljesen kiváltja, mert a kapcsolatok már explicit edge-ek. Az agent a `codegraph_explore` egyetlen tool-call-jával megkapja:

- Entry-pointokat (szimbólumok, ahol egy téma elkezdődik)
- Kapcsolódó szimbólumokat (callers, callees, references)
- Kód-snippet-eket (a graph-ből kapcsolt fájl-darabok)

A Swift Compiler benchmark a határeset: **25,874 fájl / 272,898 node, ~4 perc indexing, 6 explore-call / 35s / 0 file-read** egy komplex cross-cutting kérdésre. Ugyanez `grep + Read` kombinációval 37 tool-call / 2m 8s.

## Architektúra-rétegek

```
files
  -> ExtractionOrchestrator (tree-sitter, 19+ lang) -> DB (nodes/edges/files)
        -> ReferenceResolver (imports, name-matching, framework patterns)
              -> GraphQueryManager / GraphTraverser (callers, callees, impact)
                    -> ContextBuilder (markdown/JSON for AI consumption)
```

Hat alap-réteg, mind cserélhető. A storage `better-sqlite3` (native) ha elérhető, **transzparens fallback `node-sqlite3-wasm`-re** (wasm a slow path, de zero-native-dep deployment-en). A `codegraph status` parancs megmondja melyik él. Ez a fallback-pattern reusable minden olyan helyzetben, ahol egy native-binary-t opcionálisan akarunk + lassú-fallback-szeretnénk.

## Determinisztikus, nem-LLM extraction

A tudás-bázis nem LLM-summarized — minden `NodeKind` (file, class, function, method, route, …) és `EdgeKind` (contains, calls, imports, references, extends, decorates, …) a tree-sitter AST-ből deriválódik. Ez a két kulcs-property-t adja:

- **Reproducible** — ugyanaz a kód mindig ugyanazt a graph-et generálja
- **No hallucination** — a graph nem tudja kitalálni hogy egy függvény mit hív, csak amit szintaktikailag tényleg hív

Ez egy expicit duál a [[two-tier-graph-extraction]] mintánkban: **Tier-2 deterministic** szerep (mint a graphify tool a vault-on). Ami az LLM-extraction-nek megy (entity-disambig, semantic relation-naming), az **Tier-1**; ami szintaktikailag levezethető, az Tier-2 — és gyorsabb, olcsóbb, megbízhatóbb.

## Framework-aware route-detection

Speciális ötlet a `route` node-kind: 13 framework-pattern-t ismer (Django, Flask, FastAPI, Express, Laravel, Rails, Spring, Gin/chi/gorilla, Axum/actix/Rocket, ASP.NET, Vapor, React Router, SvelteKit, Vue/Nuxt). Egy `Route::get('/users', ...)` Laravel-hívás `route` node-ot generál, amit `references` edge köt a controller-method-hez. Így amikor az agent egy controller-action callers-eit kérdezi, **a graph megmondja az URL-pattern-t is**, ami binding-eli.

Ez nálunk a [[wp-rest-api]] / [[wordpress-router]] / [[wp-block-development]] kontextusban közvetlenül használható: WordPress REST-route → callback-handler kapcsolat is ugyanezzel a mintával extractálható (custom resolver).

## Multi-agent installer architektúra (átvehető minta)

A repo `src/installer/targets/` mintája — 4 agent-target (claude, cursor, codex, opencode) — egy mappa-szintű **plug-and-play registry**. Ötödik agent hozzáadása: **egy új fájl `targets/`-ben + egy entry `registry.ts`-ben**. Ami közös: `AgentTarget` interface, ami megmondja:

- Config-fájl-lokáció (per-OS)
- MCP-server JSON/TOML/JSONC írás (preserving meglévő tartalmat)
- Instructions-fájl path (`CLAUDE.md`, `.cursor/rules/codegraph.mdc`, `~/.codex/AGENTS.md`)

A `jsonc-parser`-rel surgical edit megőrzi a user komment-jeit és formatting-jét re-install/uninstall round-trip-eken keresztül. A `targets/toml.ts` hand-rolled TOML-serializer csak `[mcp_servers.codegraph]` scope-ra — nem dependency, és sibling-table-eket verbatim megőriz.

Ezt a mintát a SV-vault-on az agent-konfigurációk kezelésére (Claude/Codex/Gemini három agent) közvetlenül átvehetjük. Most symlink-alapú stack-ünk van; ha egyszer per-agent specifikus config-injection kell, ez a 4-target-registry-pattern a referencia.

## MCP server-instructions mint kontrakt

A `src/mcp/server-instructions.ts` az első üzenet, amit minden agent lát az MCP `initialize` response-ban. **Ez NEM ugyanaz a fájl, mint a per-agent instructions-template** — de **összhangban kell tartani** őket (`instructions-template.ts` + `.cursor/rules/codegraph.mdc` + `server-instructions.ts`). A repo CLAUDE.md house-rule-t fogalmaz erre: "amikor változtatod a tool-instrukciókat, mind a HÁRMAT update-eld".

Ez egy reusable governance-pattern minden olyan rendszerre, ahol **ugyanaz a tudás 2+ helyen replikálódik** kényszerből (technikai constraint miatt nem lehet single-source). Példák a SV-stack-ből: `~/.claude/CLAUDE.md` és `~/.codex/AGENTS.md` symlink, de a per-agent helyspecifikus instrukciók (pl. slash-command nevek vs shell CLI nevek) divergálnak — ezt a fajta tudást egy DOC közös szekciójában kell tartani.

## Always-fresh file-watcher

Native OS-events (FSEvents/inotify/RDCW) + debounced auto-sync. A graph friss marad a kód-változással. Ez kritikus, mert egy stale-graph hamis-confidence-t ad az agentnek. Az incremental update SHA-256 hash-alapú change-detection-en megy, NEM full re-index.

## Mit tanulhatunk a saját SV stack-ünkbe

Lásd "Őszinte rivalitás" lent. Konkrét átvehető-elemek:

- **Pre-indexed graph mint MCP-tool** — most a KO-DB-nk (13K+ fact) szöveges/structured triplet-szintű, NEM kód-szintű. Egy codegraph-szerű kód-graph integráció jelentős token-spórolás lenne minden kód-projekt-context-loading-nál (kgc-erp / client-c-app / stb.)
- **Tier-2 determinisztikus pillér explicit megnevezése** — most a graphify-t tartjuk Tier-2-nek, de a tree-sitter-extraction is ide tartozik, és kód-specifikusan jobb
- **Framework-route detection** — WordPress REST-route extraction reusable lenne FOXXI/Client-A/Client-C-app-on
- **Multi-target installer pattern** — ha valaha agent-specifikus injection kell

## Forrás-hivatkozások

- Repo: <https://github.com/colbymchenry/codegraph>
- npm: `@colbymchenry/codegraph` (MIT)
- Engine: tree-sitter + better-sqlite3 / node-sqlite3-wasm
- Raw-ingest: [[../10-raw/external/colbymchenry_codegraph/README]] + [[../10-raw/external/colbymchenry_codegraph/CLAUDE]]

## Kapcsolódó

- [[sv-04-tool-composition]] — agent-tool-stack, ahol egy ilyen graph-tool helyezkedik el
- [[sv-06-world-model-knowledge-graph]] — KG-tengely, kód-graph speciális esetre
- [[two-tier-graph-extraction]] — Tier-1 LLM / Tier-2 deterministic, codegraph Tier-2 referencia
- [[vault-knowledge-graph-overview]] — vault-saját KG, ami most NEM kód-szintű
- [[Karpathy-LLM-Wiki-pattern]] — a wiki/desztillátum-réteg analógja
