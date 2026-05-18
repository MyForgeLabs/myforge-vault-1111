---
name: SV-4 Tool composition — Phase B-4 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "tool-composition", "mcp", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-04-tool-composition]]
sprint: B-4
priority: P1 (skill-pool scale-out)
estimated_effort: 2-3 hét
depends_on: B-2 (Memgraph for skill-embedding-index)
---

# ADR — Phase B-4: SV-4 Tool composition

## Kontextus

A jelenlegi vault-toolpool **statikus + lapos**:
- ~280 skill a `~/.agents/skills/` mappában (Anthropic + BMAD + Azure + WDS + GDS + Microsoft skill-system)
- Mindegyik skill `SKILL.md` fájllal + esetleg külön script-ekkel
- A skillek **prompt-betöltéssel** kerülnek a Claude Code kontextusába → 280 skill × ~100 tokens metadata = **~28K token system-prompt** lenne, ha mind aktív
- A Claude `Skill` tool dinamikusan tölt be — de a 280 skill közül **csak ~10-20 használt heti szinten**
- Új skill telepítése **ember-által manuális**: clone → cp → symlink
- MCP-szerverek: 4-5 telepítve (chrome-devtools, context7, playwright, hostinger, plus pár saját) — **statikus** config

**SV-4 Phase A+ insight (921 source):** A 2026-os ipari konszenzus szerint a megfelelő minta **`SKILL.md`-tokozás + dinamikus Tool Search (`ENABLE_TOOL_SEARCH=auto` vagy `bge-m3` retriever Top-K=3) + Obsidian MCP-szerver code-execution-rétege**. **Voyager-szerű autonóm tool-creation csak ReCreate-szel** ($7-27/domain) éri meg, **NEM ab-initio TTE-vel** ($300-600/run).

## Döntés

**Hármas réteg-bevezetés Phase B-4 alatt, két-három hetes sprintben.**

### Réteg 1 — `SKILL.md` Progressive Disclosure (Anthropic Agent Skills minta)

A meglévő 280 skill **átszervezése** Anthropic Agent Skills standard-jára (SV-2 + SV-3 + SV-4 közös ajánlás).

**Tech-stack:**
- **Level-1 (Metadata, ~30 token):** A skill `SKILL.md` YAML frontmatter — `name`, `description`, `tags`, `trigger-keywords` (csak ennyi kerül a system-prompt-ba)
- **Level-2 (Instructions, 200-2000 token):** A Markdown törzs — csak trigger-keyword match-re tölt be (Claude `Skill` tool már így működik, csak a metadata-listát kell rendberakni)
- **Level-3 (Resources, csak explicit hívásra):** Külön `resources/` mappa per-skill, script-ek + assets

**Migration-script:** `/usr/local/bin/skill-canonicalize` — bejár minden `~/.agents/skills/*/SKILL.md`-t, normalizálja a frontmatter-t, kiegészíti hiányzó mezőkkel (`description`, `tags`, `trigger-keywords`). Plus audit-report a hibás formátumú skillekről.

### Réteg 2 — Tool Search Index (bge-m3 Top-K=3 retriever)

A `Skill` tool aktiváláskor **semantic search** a 280 skill között, NEM regex-keyword match.

**Tech-stack:**
- **bge-m3 lokális embedding** (B-2 sprint-tel közös) — minden `SKILL.md` Level-1+Level-2 szövege embedded
- **Memgraph vector-index** a skill-pool-ra (külön namespace a vault-tartalmaktól: `skills`)
- **Tool Search CLI:** `vault-skill-search "deploy a Next.js app"` → top-3 release skill + match-score
- **Auto-trigger:** a Claude Code `Skill` tool implicit-hív, ha a user-query embedding-similarity > threshold (0.7)

**ENABLE_TOOL_SEARCH=auto config** (Claude Code claude.json-ban): Top-K=3, threshold=0.7.

### Réteg 3 — Obsidian MCP-szerver (code-execution-réteg)

A Cloudflare Code Mode + Anthropic MCP minta (SV-4 Phase A+ kulcs-finding: **98.7% token-megtakarítás** vs. prompt-tool-list).

**Tech-stack:**
- **Custom MCP-szerver** `/opt/vault-mcp/` (Node.js / Python) — kibővítve a meglévő MCP-arsenálhoz
- **Tool-pool exposáltatás:** Memgraph-Cypher query, KO-DB SQL query, `vault-search` semantic-fetch, fájl-mutáció (`add_skill`, `update_wiki_section`, `add_decision`)
- **Code-execution sandbox** Python subprocess-szel — a tool-call NEM a Claude prompt-jában, hanem **JSON-RPC kódfutásként**, csak a result jön vissza a kontextusba
- **Skill-discovery hook:** új skill detect (új fájl `~/.agents/skills/` mappában) → auto-embedding + Memgraph-index update

### (Opcionális, Phase C+) Réteg 4 — Voyager-style ReCreate skill-evolution

A SV-4 Phase A+ Q3 alapján **NEM ab-initio TTE** (Tool-Tree-of-Thoughts, $300-600/run), hanem **ReCreate** ($7-27/domain) — meglévő skillt iteratívan finomít, NEM nulláról generál.

**Mit jelent:** ha a `11.11stop` Learning-jeiben azonos pattern 3+ session-ben → auto-trigger: új skill-draft a meglévő skill-template-ből (ReCreate-stílus), G-Eval-jóváhagyással (Phase B-1).

**Phase C+** mert: csak a B-1..B-3 stabilizálódása UTÁN biztonságos (recursive skill-creation reward-hacking-risk).

## Acceptance criteria

- [ ] **280 skill canonicalize-elve** Level-1+2+3 progressive disclosure formátumra (audit: 0 frontmatter-hiba)
- [ ] **`vault-skill-search`** működik, top-3 relevancia >0.85 (30 query benchmark)
- [ ] **Memgraph skill-namespace** embedded (10 perces backfill 280 skillre)
- [ ] **`/opt/vault-mcp/`** MCP-szerver fut, Claude Code-ban regisztrálva
- [ ] **`add_skill`, `update_wiki_section`, `add_decision`** MCP-tool-ok működnek
- [ ] **Skill-discovery hook** — új skill fájl 10 perc alatt indexelve és lekérhető
- [ ] **Code-execution token-megtakarítás** mérve: prompt-tool-list vs MCP-RPC összevetésében >80% csökkenés

## Alternatívák amiket ELUTASÍTOTTUNK

- **Ab-initio Voyager (TTE)** — $300-600/run, Tier-$50/200-ban nem fér bele; Phase A+ Q3 explicit ajánlja ReCreate-re
- **Toolformer súlyokba kódolt** — retrain szükséges új skillhez, Anthropic Claude API-val nem lehetséges
- **ToolGen 47k+ tool virtuális token** — retrain-szükséges, ugyanaz a probléma
- **MCP nélkül, csak prompt-tool-list** — 280 skill × metadata-tokens = 28K token system-prompt, nem fér bele
- **CrewAI / AutoGen / LangGraph framework új réteg** — Anthropic „simplicity over framework" konzisztens insight (SV-3 + SV-4 + SV-8 mind erre figyelmeztet)

## Konzekvenciák

**Pozitív:**
- **~98.7% token-megtakarítás** tool-execution-on (SV-4 Phase A+ kulcs-számadat)
- 280 skill **valóban használható** a Claude Code-ból semantic-discovery-vel
- MCP-szerver foundation a SV-3 (B-6) multi-agent sprintbe (orchestrator-worker MCP-n keresztül kommunikál)
- Új skill telepítése automatizált (drop-in + 10 perc embedding-index)

**Negatív:**
- Új MCP-szerver karbantartása (~/opt/vault-mcp/)
- 280 skill canonicalize-elés időigényes (~5-10 perc/skill = 24-46 óra; nagy részben scriptelhető)
- Tool Search threshold-tuning iteráció (false-positive vs false-negative trade-off)

**Backout-plan:** Az MCP-szerver leállítható (`launchctl unload`); Claude Code visszaesik a klasszikus `Skill` tool prompt-listára (rosszabb token-economy, de működik).

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| Skill-canonicalize false-positive (eltöri working skillt) | Skill-pool sérülés | Git-commit minden batch-canonicalize előtt; rollback `git revert` |
| MCP-szerver crash → tool-execution lehetetlen | Vault-funkció down | Launchd auto-restart; fallback prompt-tool-list (ENV-flag) |
| bge-m3 skill-similarity rosszul kalibrált | False match, rossz skill-trigger | Manual baseline 50 query-n, threshold-tuning |
| Cross-vault skill-share (Rob) | Skill-conflict | Per-vault skill-namespace a Memgraph-ban |

## Open questions

1. **MCP-szerver nyelv:** Python (gyors prototype) vagy Go/Node.js (gyorsabb runtime)? Phase B-4 első napon prototype mindkettőben, benchmark.
2. **Skill-versioning:** ha egy skill iteratívan frissül, hash-megőrzés vs overwrite? Git-history elég, vagy explicit `version: 2026-05-12` mezőre van szükség?
3. **Cross-tool composition:** ha az agent `Skill-A` + `Skill-B` chain-t akar futtatni, hogyan optimalizáljuk a token-economy-t? (Phase C+ ReCreate-pattern + composite-skill auto-draft).

## Kapcsolódó

- [[11-wiki/sv-04-tool-composition]] — research-cikk
- [[07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 sprint (Memgraph közös infra)
- [[07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]] — B-6 sprint (MCP-szerveren át kommunikál)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap
- [[05-Memory/Skill-map]] — meglévő skill-pool dokumentáció
