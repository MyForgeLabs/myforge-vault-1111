---
name: Vault design — NotebookLM research findings
type: research-summary
tags: [adr, vault-design, notebooklm, research]
date: 2026-04-23
sources_count: 483
notebooklm_notebook_id: 13a3bdbc-5618-4d13-b70c-b91b3ff17911
---

# 2026-04-23 — Vault design: NotebookLM kutatás eredmények

NotebookLM 3 párhuzamos deep-research lefutott (vault-struktúra infrára, AI-agent workflow-k, multi-device sync), **483 forrás** (Obsidian forum, Steph Ango/Kepano blog, johnnydecimal.com, Obsidian Dataview docs, PKM-blogok). Ez a fájl a kulcs-ajánlásokat gyűjti, priorizálva.

## TL;DR — Top 10 fejlesztés, hatás szerint

1. **Johnny Decimal számozás** a mappákon → determinisztikus útvonalak AI-agentnek
2. **Szigorú YAML frontmatter séma** (ISO dátumok, egységes mezők) → adatbázis-szerű lekérdezések
3. **System_Health.md automata audit** (bad YAML, dangling links) → vault-romlás észlelés
4. **MOC-k (Map of Content) mint dashboardok** domainenként → nem folder-drill-down
5. **Mermaid diagrams-as-code** → AI jól ír Mermaidet, natívan renderelődik
6. **Időbélyeges fájlnevek** dinamikus logokra → Git-konfliktus elkerülése
7. **Inline Dataview metaadatok** (`Key:: Value`) logoláshoz → nem YAML-módosítás
8. **Bases / Database Folder plugin** → Notion-szerű tábla-szerkesztés emberi validáláshoz
9. **Canvas RCA-hoz** → vizuális hibakeresés, migration planning
10. **Tag taxonómia + Auto Note Mover** → agent-konzisztencia (`#prod` vs `#production`)

## Részletesen — mindegyik ajánláshoz konkrét akció

### 1. Johnny Decimal mappa-számozás

> **Miért:** AI agentek hajlamosak rossz helyre menteni, vagy eltévedni a struktúrában. A JD-rendszer "permanens címeket" ad a funkcionális tartományoknak.

**Akció:**
```
Átnevezés:
  AGENTS.md      →  (root marad)
  Projects/      →  20-Projects/
  Hosts/         →  30-Hosts/
  Tasks/         →  40-Tasks/
  Sessions/     →  50-Sessions/
  Memory/        →  60-Memory/
  Decisions/     →  70-Decisions/
  Audits/        →  80-Audits/

Belsejében: 31-Prod-Servers/, 32-Dev-Servers/ ha bővül
```

**Ellen-érv:** nálunk elég kicsi a struktúra (8 mappa), szó szerinti JD overkill. De a **számozási logika** a subfolderekben (pl. `Hosts/10-VPS/`, `Hosts/20-Shared-Hosting/`) hasznos lesz amikor bővül.

### 2. YAML frontmatter szigorú séma

**Akció:** [[AGENTS]]-be írni pontos sémát per-típus:
```yaml
# Hosts/
---
type: host
hostname: srvXXXX
ipv4: "..."
ipv6: "..."
role: [dev|prod|shared|cdn]  # vagy enum
status: active|archived
created: 2026-04-23   # ISO-8601 ONLY
updated: 2026-04-23
tags: ["#host", "#env/prod"]   # mindig array
---
```
Key insight: **többes szám minden tag/list mezőre** (`tags:`, `servers:`), ISO dátumok kizárólag.

### 3. System_Health.md automata audit

**Akció:** `Audits/System_Health.md` — Dataview DQL:
```dataview
TABLE file.mtime as Modified, status
FROM "Hosts" OR "Projects"
WHERE status = null OR updated = null
SORT file.mtime DESC
```
Ez mutatja az üres status-t, hiányzó frontmattert. Heti 1× ránézni.

### 4. MOC-k (Map of Content) dashboard-ok

**Most van:** [[02-Projects/Index]], [[03-Hosts/Index]], [[04-Tasks/Dashboard]] — **jó úton vagyunk**.
**Hiányzó:** `Incident_MOC.md` (RCA-k), `Pipeline_MOC.md` (CI/CD), `Inventory_MOC.md` (egyesített hardver + DB + domain lista).

### 5. Mermaid diagramok architektúra-ábrákhoz

**Akció:** `Hosts/Network-topology.md` — network mermaid diagram (dev Caddy → prod nginx proxy láncok). AI-agenteket instruálni: architektúra-döntésben mindig adjon mermaid-et.

### 6. Időbélyeges fájlnevek

**Most:** Sessions/ `YYYY-MM-DD-slug.md` — egyetlen session naponta. Ha 2 agent ugyanazt akarja indítani, ütköznek.
**Akció:** `YYYY-MM-DD-HHMM-slug.md` — óra-perc is. A `11.11start` scriptet frissíteni.

### 7. Inline Dataview metaadat logokhoz

**Akció:** `11.11note` append-elt sorok a `## Events`-be már `- 18:33 — ...` formában vannak. Ez Dataview-kompat lesz ha rákérdezünk **`- time:: 18:33 — content`** formára. Opcionális, csak ha lekérdezni akarunk.

### 8. Bases plugin vs Dataview

**Status:** `Tasks/Backlog.md` már Tasks plugin-nel megy. Bases/Database Folder plugin **további** lehetőség lenne a Hosts/ vagy Projects/ mappákra, Notion-szerű táblanézettel.

**Akció:** Próbáljuk ki a **Bases**-t (Obsidian natív feature újabb verziókban) egy Hosts-base-szel.

### 9. Canvas RCA-hoz

**Most van:** `Projects/KGC-ALL Architektura.canvas` (legacy).
**Akció:** Bug/incident esetén csinálni egy `Audits/<incident>.canvas`-t — húzni rá a log-részleteket, linkelt Host + Project fájlokat, screenshotokat.

### 10. Tag taxonómia

**Most:** az agent-ek különböző tag-eket használnak (pl. `#prod`, `#production`, `#éles`).
**Akció:** új fájl `Memory/Tag-taxonomy.md` — kötelező tag-lista + hierarchia (`#env/prod`, `#env/dev`, `#type/host`, `#type/project`, stb.). [[AGENTS]] hivatkozik rá: "ha tag-et használsz, ezek közül válassz".

## Plusz technikai javaslatok a kutatásból

- **"File over App" filozófia** — vault ne függjön egyetlen eszköztől (már ezt követjük Git-szinken)
- **`Local Images Plus` / `Attachment Management` plugin** — csatolmányokat dedikált mappába
- **`Janitor` plugin** — árva fájlok (nincs link rájuk) havi takarítása
- **`Auto Note Mover` plugin** — ha agent rossz helyre ment valamit, tag-alapon odaviszi helyesen
- **`Random Note`** rutinszerű régi-doksi átnézés

## Mit mondanak a specifikus "Obsidian for AI agents" források

- **AGENTS.md konvenció** (amit már használunk) iparági **de facto standard** (lásd Kepano, Claude Code, Cursor)
- **Prompt engineering vault-ban:** a vault-struktúra maga része a promptnak — az agent ne „találjon ki" konvenciókat, minden explicit a tartalomban
- **Hallucination-védelem:** szigorú séma + `Dataview WHERE` + validáló Dataview query = agent output ellenőrzés

## Források (NotebookLM notebook)

A teljes 483 forrás elérhető: [NotebookLM notebook](https://notebooklm.google.com/notebook/13a3bdbc-5618-4d13-b70c-b91b3ff17911) — Q&A-t is továbbcsinálhatunk ott.

Key-forrás-listából emlékezetes:
- **Steph Ango (Kepano) — How I use Obsidian:** https://stephango.com/vault — az egyszerűség + "File over App" filozófia atyja
- **Johnny Decimal:** https://johnnydecimal.com
- **Obsidian Dataview:** https://github.com/blacksmithgu/obsidian-dataview
- **Obsidian forum — MOC:** https://forum.obsidian.md/t/a-case-for-mocs
- **Obsidian forum — Engineering Project Management:** https://forum.obsidian.md/t/engineering-project-management

## Mi a következő

A Top-10 pontokból érdemes [[04-Tasks/Backlog]]-ba írni a konkrét tennivalókat:
- YAML séma definiálás + meglévő fájlok ellenőrzése
- `Memory/Tag-taxonomy.md` létrehozása
- System_Health.md Audits/-ben
- Sessions fájl-nevekben óra-perc hozzáadása a `11.11start`-hoz
- Bases/Database Folder plugin kipróbálása Hosts/-on

## Kapcsolódó

- [[06-Audits/2026-04-23 Teljes infra audit]] — infra snapshot
- [[AGENTS]] — közös agent-utasítás (ahová a tag-taxonomy + YAML séma megy)
- [[04-Tasks/Backlog]] — ide mennek az akciók
