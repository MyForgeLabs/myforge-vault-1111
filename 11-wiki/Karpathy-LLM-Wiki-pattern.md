---
name: Karpathy LLM Wiki pattern
type: wiki
tags: ["#type/reference", "rag", "vault-design", "agents"]
created: 2026-04-30
updated: 2026-04-30
source:
  - "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f"
  - "https://github.com/Ar9av/obsidian-wiki"
  - "[[10-raw/2026-04-23 — NotebookLM briefing - Obsidian vault AI agent infra]]"
---

# Karpathy LLM Wiki pattern

Andrej Karpathy 2026 áprilisában publikált minimal RAG-mintája. **Központi gondolat:** a klasszikus retrieval (vektor-DB, embedding, runtime keresés) helyett az LLM **inkrementálisan compile-olja** a tudást egy strukturált wikibe, ami időben felhalmozódik (compounds).

## A három réteg

| Réteg | Mire való | Példa nálunk |
|-------|-----------|--------------|
| **raw/** | Immutable forrás — cikkek, transzkriptek, chat-dump-ok, screenshot-olvasatok. Az LLM **olvassa**, de soha **nem módosítja**. | [[10-raw/]] |
| **wiki/** | Desztillált, saját szavakkal átírt tudás. Az LLM ide ír — koncepciók, playbookok, glosszárium. Linkelt entries, konzisztens struktúra. | [[11-wiki/]] |
| **agent munkavault** | Spekulatív vázlatok, rendezetlen drag-drop. Itt nem-validált tartalom is lehet. | (most még nincs külön — a 08-Sessions/ tölti be ezt a szerepet) |

## Compilation > Retrieval

A klasszikus RAG: query → embed → keresés → top-k chunks → válasz.

Karpathy: query → **olvasd a wiki-index.md-t** → drill into wiki-page-ek → válasz.

Vector DB nincs. Embedding nincs. **Index.md a térkép, a szemantikus struktúra a wiki-fájlokban.**

## Crystallization workflow

Egy munkamenet (research thread, debug session, analysis) végén az LLM:
1. Az érintett `08-Sessions/` fájlt **átolvassa**
2. Készít egy `11-wiki/` digestet ami a tartós tanulságokat tartalmazza
3. Ha új koncepció került elő, külön wiki-bejegyzés
4. A `08-Sessions/` raw marad — referenciának

A nálunk lévő `/11.11stop` parancs ezt félig már csinálja: **Summary + Learnings + Next session** szekciók a session-ben. A teljes Karpathy-pattern szerint a Learnings bullet-jeit külön `11-wiki/` bejegyzésekbe is propagáljuk.

## Operatív komponensek (Karpathy minimum-stackje)

- **CLAUDE.md / AGENTS.md** = a "schema-brain" — entity-types, page-formátumok, workflow-szabályok. Az LLM első dolga olvasni.
- **index.md** = a "térkép" — minden mappához (Projects/Index.md, Hosts/Index.md, wiki/Index.md). Az LLM ezzel navigál a kérdés feltevése után.
- Vector DB nincs — index + drill-down megoldja "hundreds of pages"-ig (~200-300 fájl).

## Mit veszünk át, mit nem

| Karpathy mintája | Nálunk |
|------------------|--------|
| `raw/` mint immutable forrás | ✅ [[10-raw/]] létezik |
| `wiki/` mint desztillátum | ✅ [[11-wiki/]] létezik (most fejlesztjük) |
| Agent-munkavault külön | 🟡 Részben — `08-Sessions/` betölti, de tisztán nem szétválasztva |
| index.md per mappa | 🟡 [[02-Projects/Index]], [[03-Hosts/Index]], [[06-Audits/Index]], [[10-raw/Index]], [[11-wiki/Index]] van — bővítve |
| Crystallization workflow | 🟡 `/11.11stop` félig — bővíthető wiki-propagációval |
| CLAUDE.md schema-brain | ✅ [[AGENTS]] |

## Production validation — GenericAgent L0-L4 párhuzam (2026-05-11)

Egy 10.7k★ kínai self-evolving agent framework, [`lsdefine/GenericAgent`](https://github.com/lsdefine/GenericAgent) (arXiv 2604.17091), ugyanazt a 5-rétegű Karpathy-mintát választotta production-szintre — két különböző projekt egymástól függetlenül erre konvergált:

| GenericAgent | Saját vault |
|---|---|
| **L0 — Meta Rules** (alap-viselkedés + system constraints) | [[00-Meta/]] (Tag-taxonomy, Frontmatter-schema, AGENTS.md) |
| **L1 — Insight Index** (minimális index, gyors routing/recall) | [[02-Projects/Index]], `MEMORY.md` |
| **L2 — Global Facts** (long-term stabil tudás) | [[05-Memory/User]], [[05-Memory/Infrastructure]] |
| **L3 — Task Skills / SOPs** (reusable workflow-ok) | [[11-wiki/]] evergreen playbookok |
| **L4 — Session Archive** (kész taskok desztillált rekordjai) | [[08-Sessions/]] |

**9 atomic tool ≈ saját stack:**

- `code_run`, `file_read/write/patch` ≈ Bash, Read, Write, Edit
- `web_scan`, `web_execute_js` ≈ WebFetch, WebSearch
- `ask_user` ≈ AskUserQuestion
- `update_working_checkpoint`, `start_long_term_update` ≈ `11.11note`, `11.11stop` crystallization

**Kulcskülönbség: autonómia-szint.** GenericAgent autonomous-skill-growth (minden task után auto-crystallize), saját rendszerünk human-in-the-loop (batch preview + user approval `/11.11stop`-nál). A memory-struktúra ugyanaz, az autonómia-szint különbözik.

**Takeaway:** ha valamikor PaaS-szerű agent-rendszert építünk (pl. MyForge OS részeként), a 9-atomic-tool + L0-L4-réteg minta jó starting skeleton.

## Kapcsolódó

- [[11-wiki/Johnny-Decimal-prefix]]
- [[11-wiki/11.11-session-protokoll]]
- [[11-wiki/Kepano-File-over-App-filozofia]]
- [[07-Decisions/2026-04-23 Vault design - NotebookLM research findings]]
- [[07-Decisions/2026-04-23 Claude Code Agentic OS - build plan]]
- [[08-Sessions/2026-05-11-github-repo]] — GenericAgent README elemzés + L0-L4 párhuzam felfedezés
- [[10-raw/2026-04-23 — NotebookLM briefing - Obsidian vault AI agent infra]]
