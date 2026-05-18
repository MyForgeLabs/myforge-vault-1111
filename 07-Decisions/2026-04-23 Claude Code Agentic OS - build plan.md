---
name: Claude Code Agentic OS — build plan (videó alapján)
type: decision
status: in-progress
tags: [adr, agentic-os, youtube, vault-design]
date: 2026-04-23
source_video: "https://www.youtube.com/watch?v=pfPi04pIfaw"
source_title: "Claude Code Agentic OS = UNSTOPPABLE"
notebooklm_source_id: 4138583c-4faa-40fd-bcb2-8a77f9714607
---

# 2026-04-23 — Claude Code Agentic OS build plan

## A videó által bemutatott rendszer

Egy **"Agentic Operating System"** — ahol a Claude Code **motor**, egy Obsidian vault a **memória**, és CLI-integrációk + egy vizuális dashboard a **végrehajtás**. Lényege: nem csak chat, hanem **headless** módban lefutó skillek, üzleti funkciók szerint szervezve.

### A "Nagy Hármas" probléma amit megold

1. **Memória hiánya** — chat történetek elvesznek → Obsidian vault
2. **Konzisztencia hiánya** — AI outputja változik → struktúrált skillek
3. **Elérhetőségi gát** — terminál ijesztő nem-technikai embereknek → GUI dashboard

## Gap elemzés — videó vs. nálunk

| Elem | Videó | Nálunk |
|------|-------|--------|
| **Claude Code motorként** | ✓ | ✓ dev + prod + shared hosting |
| **Obsidian vault memória** | ✓ `raw/`, `wiki/`, `projects/` (Karpathy RAG) | ⚠️ `Projects/`, `Memory/`, `Decisions/`, etc. de **nincs `raw/` + `wiki/`** |
| **CLI integrációk** | GWS, Firecrawl, NotebookLM, GitHub | ✓ NotebookLM + gh; ❌ Firecrawl, GWS |
| **Always-on futtatási környezet** | Mac Mini | ✓ 2 VPS |
| **Skillek üzleti funkciók szerint** | Research / Content / Sales / Marketing / Admin | ⚠️ van `bmad-*`, `gds-*`, `obsidian:*` de **nem üzleti funkciók** szerint |
| **Skill Creator Skill meta** | ✓ saját | ✓ `skill-creator`, `bmad-agent-builder` |
| **Headless skill-futtatás** | ✓ dashboard gombokkal | ⚠️ `/11.11*` parancsok + cron (CLI-only, nincs GUI) |
| **Morning GitHub trending report** | ✓ remote task | ❌ |
| **Deep research flow** (Firecrawl + NotebookLM) | ✓ lokális task | ⚠️ NotebookLM megvan, Firecrawl hiányzik |
| **GUI dashboard** | ✓ custom, fizetős kurzusból | ❌ (nem is cél most) |
| **Vault cleanup automation** | ✓ headless Claude Code | ⚠️ részben: `11.11note`, autosave |

## Amit érdemes építeni ebből (és mit nem)

### ✓ Érdemes + kicsi (implementáljuk most)

1. **`raw/` + `wiki/` mappák** a vault-ban (Karpathy RAG pattern)
   - `raw/` = nyers input (kimásolt cikkek, videó-transzkriptek, ChatGPT beszélgetések)
   - `wiki/` = desztillált/szintetizált tudás (koncepciók, eljárások, playbook-ok)
   - `Projects/` már megvan

2. **Skillek üzleti funkciók szerinti csoportosítás** (csak mental model, nem fájl-reorganizáció)
   - Elég egy `Memory/Skill-map.md` ami csoportosítja a meglévő 300+ skillt

### ✓ Érdemes + közepes (betervezzük, de nem most)

3. **Firecrawl telepítés** — webscraping/reserach skillhez
   - Már most is van NotebookLM + defuddle (obsidian-skills-ből). Firecrawl plusz funkció.

4. **Morning GitHub trending skill**
   - Egy `Skills/github-trending-report.md` + cron — napi reggel automatikusan
   - Nem kell saját GUI: a Claude Code `/skill` parancs meghívható cron-ból is

5. **Headless skill-futtatás** kibővítés
   - Már megvan az `/11.11*` család — bővíteni lehet pl. `/11.11skill <name>` pattern-nel

### ⚠️ Érdemes de nagy — külön projekt

6. **GUI dashboard**
   - A videó fizetős kurzusból ad kódot. Mi vagy sajátot építünk (React/Electron/Tauri app CLI-wrapper) **vagy** használjuk meglévő open source alternatívákat (pl. Raycast, Alfred workflow-k Mac-en)
   - **Felvéve [[04-Tasks/Backlog]]-ba 🔽 long-term** — nem most, és nem szerveren, hanem Mac-en vagy webes UI-ként

### ❌ Nem szükséges nálunk

7. **GWS (Google Workspace) CLI** — nincs rá konkrét use case most
8. **Karmester-szerep Mac Mini-vel** — a 2 VPS ezt lefedi

## Terv — amit most megcsinálunk

1. **[[00-Meta/Tag-taxonomy]]** (TOP 3 #1 a NotebookLM research-ből)
2. **[[00-Meta/Frontmatter-schema]]** (TOP 3 #2)
3. **`raw/` + `wiki/` mappák** README-vel (videó #1)
4. **[[05-Memory/Skill-map.md]]** (videó #2 — üzleti funkció csoportosítás)
5. **AGENTS.md** bővítés: `raw/`, `wiki/`, tag-taxonomy, frontmatter-schema hivatkozások

## Amit később megcsinálunk (Backlog-ba)

- **Firecrawl skill** (`firecrawl` CLI + Claude slash command wrapper)
- **Morning GitHub trending report** skill + cron
- **GUI dashboard** — külön project (nem kell most)

## Kapcsolódó

- [[07-Decisions/2026-04-23 Vault design - NotebookLM research findings]] — általánosabb vault-best-practices
- [[06-Audits/2026-04-23 Teljes infra audit]]
- [[04-Tasks/Backlog]] — ide mennek a long-term elemek
- **Videó NotebookLM-ben:** [notebook 13a3bdbc](https://notebooklm.google.com/notebook/13a3bdbc-5618-4d13-b70c-b91b3ff17911), `-s 4138583c` a videó-only query-khez
