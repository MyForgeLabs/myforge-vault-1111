---
name: SV-4 Tool composition
type: wiki
tags: ["#type/wiki", "agi", "tool-use", "mcp", "skill-library", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: done
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: 90e132a1-3f58-4740-bdfc-8c9318571a6d
---

# SV-4 — Tool composition

A 8-tengelyű szuperintelligens-vault evolúciós research negyedik cikke. **Kérdés:** hogyan érhető el, hogy egy LLM-agent **maga fedezze fel, válassza ki és komponálja az új tool-okat** (functions, API-k, MCP-szerverek) ahelyett, hogy az ember előre telepítené őket — exponenciális tool-növekedést és önfejlesztő képességet eredményezve.

> **Status:** 7/7 kérdés válaszolva. NotebookLM-források: 31 (foundational papers — Toolformer, Gorilla, ToolGen, Voyager, ToolLLM; MCP-spec + Anthropic engineering blog-posztok; Cloudflare + Block/Goose + Simon Willison; YouTube MCP-explainer-ek; 2 web-research bővítés).

## 1. A tengely magja

A **„tool composition" (eszköz-kompozíció)** az agentikus AI egyik legfontosabb mozgatórugója, amely azt a **paradigmaváltást** jelöli, amikor egy LLM-alapú agent az ember által előre megírt, statikus munkafolyamatok és mereven bekötött eszközök helyett **teljesen önállóan képes felfedezni, kiválasztani és összekapcsolni a különböző külső funkciókat, API-kat és MCP-szervereket**. Ebben az autonóm működési modellben az agent **saját maga dönti el**, hogy egy feladat megoldásához mikor, hogyan és milyen eszközt hívjon meg (ahogy a Toolformer demonstrálta), és képes egy folyamatosan frissülő API-készletből is kikeresni a legrelevánsabbat (a Gorilla keresőalapú megközelítése vagy a ToolGen virtuális tokenekre épülő generatív integrációja révén). A kiválasztott eszközöket az agent komplex, **egymásra épülő cselekvési sorozatokká, kódokká fűzi** (mint a Voyager hoz létre egyszerűbb programokból összetett, újrafelhasználható készségeket egy önmagát építő könyvtárban), miközben a **Model Context Protocol (MCP)** specifikációi és központi regiszterei szabványosítják és kiterjesztik ezt az autonómiát; az agentek így **futásidőben, dinamikusan térképezhetik fel és emelhetik be a kontextusukba az új hálózati képességeket, ezáltal „önfejlesztővé" válva** anélkül, hogy a fejlesztőknek a rendszerek indulásakor előre ismerniük és telepíteniük kellene ezeket az eszközöket.

### Kulcs-dimenziók

| Dimenzió | Mit jelent | Példa-megoldás |
|---|---|---|
| **Tool discovery** | Hogyan találja meg az agent a megfelelő eszközt? | Gorilla retriever / ToolGen token / MCP Registry |
| **Tool selection** | Hogyan választ a sok jelölt közül? | Toolformer self-supervised / Constrained decoding |
| **Tool execution** | Hogyan hívja meg ténylegesen? | JSON-RPC (MCP) / kód-futtatás / direkt function-call |
| **Tool composition** | Hogyan láncol több tool-t? | Voyager skill-library / ReAct iteratív promptolás |
| **Tool creation** | Hogyan ír új tool-t magának? | CREATOR / LATM Python-függvény generálás |

## 2. Kanonikus megközelítések (5 fő minta)

### Toolformer (Schick et al. Meta 2023) — önfelügyelt tanulás

**Mechanizmus:** A nyelvi modell **önfelügyelt módon, saját maga által generált és a jövőbeli tokenek veszteségét (loss) csökkentő API-hívásokkal** finomhangolja önmagát. A modell **emberi demonstrációk nélkül** tanulja meg, mikor és hogyan hívjon meg eszközöket (pl. számológép, kereső).

**Kulcs-újdonság:** Az eszközhasználat statikusan, a finomhangolás során beépül a súlyokba — implicit tool-knowledge.

### Gorilla (Patil et al. UC Berkeley 2023) — retrieval-based

**Mechanizmus:** Visszakereséssel kiegészített (retrieval-aware) architektúra, amely **külső információkeresővel (BM25, GPT-Index) kéri le a legrelevánsabb és legfrissebb API-dokumentációkat** futásidőben.

**Kulcs-újdonság:** Csökkenti a hallucinációkat és **adaptálható az API-k változásaihoz újratanítás nélkül** — a tool-pool dinamikus marad.

### ToolGen (Wang et al. 2024) — virtuális tokenek

**Mechanizmus:** Az eszközök keresését és futtatását **egyetlen generatív feladattá olvasztja össze** azáltal, hogy **a szótár bővítésével minden eszközhöz egy egyedi virtuális tokent rendel** (atomic indexing). A modell a saját belső paramétereiből generálja a tool-hívásokat.

**Kulcs-újdonság:** Skálázható **47 000+ eszközre** külső kereső nélkül; **constrained decoding** teljesen kiküszöböli a hallucinált tool-call-okat.

### Voyager (Wang et al. NVIDIA 2023) — skill-library + iterative prompting

**Mechanizmus:** Folyamatosan tanuló, embodied agent, amely **bővülő, futtatható kódokból álló képesség-könyvtárat (skill library) épít fel**. Az agent környezeti visszacsatolások, futtatási hibák és **self-verification** révén iteratívan finomítja a programjait, amelyeket vektoros formában keres vissza új feladatokhoz.

**Kulcs-újdonság:** Az agent **maga írja a tool-t** kódként, és újrafelhasználható skill-ként eltárolja — lifelong learning.

### Model Context Protocol (Anthropic 2024-11) — szabványosított kliens-szerver

**Mechanizmus:** **Elvágja egymástól az AI-alkalmazást és az adatforrásokat/eszközöket**, lehetővé téve a szabványos, **JSON-RPC alapú** integrációt. Az agentek futásidőben kapcsolódnak külső MCP-szerverekhez, ahonnan strukturált módon erőforrásokat, prompt-okat és eszközöket kérhetnek le.

**Kulcs-újdonság:** **Composability** — egy agent egyszerre lehet kliens és szerver, így többrétegű autonóm hálózat építhető. Plus **MCP Registry** dinamikus felfedezésre.

### Tool-discovery-módszerek összehasonlítása

| Megközelítés | Discovery-módszer | Új tool hozzáadása |
|---|---|---|
| **Toolformer** | Súlyokba bekódolt (implicit) | Retraining szükséges |
| **Gorilla** | Külső kereső (BM25/dense) | Csak dokumentációt frissíteni |
| **ToolGen** | Next-token-prediction generative | Retraining szótár-bővítéssel |
| **Voyager** | Vektor-DB szemantikus keresés saját kódokon | Új skill kód-generálással |
| **MCP** | JSON-RPC `list_tools` + Registry API | Új szerver telepítése |

## 3. Tech-stack opciók 2026-ban

### MCP-szerver implementációk

| Eszköz | Tradeoff | Mire jó |
|---|---|---|
| **Anthropic referencia-szerverek + SDK** (Python, TypeScript) | Plug-and-play, stabil; az összetett üzleti logikát neked kell írni | Gyors integráció (GitHub, PostgreSQL, fájlrendszer) |
| **Cloudflare Code Mode** | Token-használat akár **98,7%-kal csökken** (kód-futtatás MCP-szerverekhez); sandbox és monitorozás kell | Nagy MCP-tool-pool, ahol a tool-szám > kontextus |
| **Block / Goose** | Open-source agent, MCP-szerverek mint „extensions"; flexibilis UI-integráció, de platform-specifikus nevek elrejtik a szabványos MCP-absztrakciót | Saját MCP-alapú agent-app, ahol a UI-réteg fontos |

### Tool-registries

| Megközelítés | Tradeoff |
|---|---|
| **ToolGen virtuális tokenek** | Constrained decoding → nincs hallucináció, nincs külső kereső; viszont **új tool = LLM retrain** (statikus) |
| **Gorilla retriever** | Folyamatos API-frissítés újratanítás nélkül; **keresési hibák továbbgyűrűznek** |
| **MCP Registry** | Szabványosított, dinamikus discovery → self-evolving agentek; **hálózati függőség + trust-ellenőrzés** kell |

### Agent-keretrendszerek tool-handling-je

| Keretrendszer | Tool-megoldás |
|---|---|
| **Claude Code** | **Tool Search** — eszközök csak akkor töltődnek a kontextusba, ha a feladat megkívánja (deferral); plus interaktív „elicitation" emberi jóváhagyáshoz |
| **LangGraph** | MCP-adapterek/connectors (nem saját protokoll); a keretrendszer maga a memory + control-loop |
| **AutoGPT** | ReAct-stílusú subgoal-decomposition; **hiányzik a self-verification** és a dinamikus skill-tárolás (Voyager-kiegészítés javasolt) |
| **Replit Agent** | MCP-architektúrába integrált; fejlesztői eszközök kiterjesztett, API-alapú elérése a kódoláshoz |

### Skill-library tárolási minták

| Minta | Tradeoff |
|---|---|
| **Fájl-alapú** (`SKILL.md` + script) | Token-hatékony (csak a betöltött fájl kontextusbe), könnyen verziókövethető (git); **szigorú sandbox + resource-limit kell** |
| **Vector-DB Voyager-style** | Szemantikus visszakeresés (top-5 leírás-embedding); folyamatos embedding-költség + retrieval-hibák lehetségesek |

## 4. Friss áttörések 2024-2026

**MCP — az ökoszisztéma alapja (Anthropic, 2024-11).** Nyílt szabvány, amely **megszünteti a fragmentált integrációkat**. 2026-ra a Cloudflare, Block, Replit, és számos enterprise vendor mind MCP-szerverekkel kínálja a hozzáférést a saját rendszerükhöz.

**Code-execution-with-MCP (Anthropic engineering, 2025).** Új univerzális tool-execution réteg: az agent nem direkt hívja az eszközöket egyenként, hanem **kódot ír** az MCP-szerverek eléréséhez — token-használat **98,7%-kal csökkenhet**. Az agent dinamikusan böngészi a fájlrendszert a szükséges eszközök után, és a futtatókörnyezetben szűri az adatokat.

**Claude Code skill-rendszer.** A sikeresen futtatott, agent által írt kódokat és eljárásokat egy `SKILL.md` fájlban tárolja a rendszer, így az agent idővel **magasabb szintű, újrafelhasználható képességekből álló eszköztárat épít fel magának**.

**ToolGen (2024) — virtuális tokenek.** Az eszközök az LLM **szótárába** integrálódnak egyedi tokenekként; a tool-discovery maga a next-token-prediction. **47 000+ eszközre** skálázható.

**Autonóm tool-creation (CREATOR, LATM).** Az LLM-ek maguk **hoznak létre új eszközöket** Python vagy SQL függvények formájában — kiterjesztve a saját képességeiket.

**„Compositional autonomy" / self-discovery trend.** A futásidőben, **emberi beavatkozás nélkül** történő tool-felfedezés trendje. Az MCP Registry teszi lehetővé, hogy ha egy feladathoz hiányzik egy eszköz, az agent **dinamikusan megkeresi és telepíti a hitelesített MCP-szervert**. Plus az MCP **láncolhatóság** (egy agent kliens ÉS szerver is) → többrétegű autonóm hálózatok.

**A pre-2024 vs post-2024 kontraszt:**
- Toolformer: csak ~5 előre definiált eszköz, statikus API-hívás → ToolGen 47k+ tool
- Gorilla: külső BM25 → kereső-hibák propagálódtak → MCP Code Mode univerzális absztrakció
- Statikus tool-pool → self-evolving Registry + autonóm tool-creation

## 5. Failure-modes és limitációk

### Klasszikus buktatók

**Tool-context-bloat.** Az elérhető eszközök számának növekedésével az **összes API-dokumentáció és séma előzetes betöltése felemészti a kontextusablakot**, ami lassítja a feldolgozást, növeli a költségeket, és extrém esetben működésképtelenné teszi a rendszert. *Mitigáció:* Claude Code Tool Search (deferral), Cloudflare Code Mode.

**Hallucinated tool-calls.** A modell **képzelt eszközöket, argumentumokat vagy nem létező paramétereket** próbál meghívni (pl. „rézkard" Minecraft-ban, fiktív GitHub repó). *Mitigáció:* ToolGen constrained decoding.

**Tool-selection-error.** Az agent **félreértelmezi a feladatot** (SQL-generátort hív matematikai problémához) vagy szuboptimálisan dönt komplex peremfeltételek közt.

**Compositional drift / compounding errors.** **Több lépésből álló cselekvéssorozatoknál egy korai hibás döntés dominóeffektusként gyűrűzik tovább** — végtelen hurok, korrigálási képtelenség. *Mitigáció:* Reflexion-stílusú self-verification, DFSDT-backtracking.

**Security / prompt-injection.** Külső eszközök (webes keresők, ellenőrizetlen adat) **prompt-injection támadásoknak teszik ki a modellt**; önkényes kód-végrehajtás + adatvédelem folyamatos explicit kontrollt és emberi jóváhagyást követel.

**Brittleness.** Egy API-spec változás (pl. Slack API) → mereven integrált rendszer azonnal **leáll**. *Mitigáció:* MCP-absztrakció + retrieval-alapú dokumentáció-lookup.

### Mit NEM oldanak meg a paradigmák

- **Toolformer** önállóan generál tool-hívásokat, de **képtelen láncolni** (egyik tool kimenete másik bemenete) és nem tud interaktívan böngészni.
- **Voyager** folyamatos tanulás ellenére **NEM oldja meg a hallucinációt** — gyakran érvénytelen blokkokat / nem létező primitíveket hív; a self-verification modul **tévesen jóváhagyhat kudarcot**.
- **MCP** egységesíti a hozzáférést, kód-futtatással csökkenti a kontextus-túlterhelést, de **NEM oldja meg a többrétegű compounding errors-t**, és **új biztonsági problémákat** teremt (nyílt hálózati képességek + prompt-injection + malicious clients).

## 6. Implementáció a Peti-vault kontextusban

A meglévő stack:
- **Obsidian-Markdown agent-vault** (~240 fájl, 11.11 session-protokoll)
- **Claude Code CLI** + ~280 skill pool a `~/.claude/skills/`-ben (plus `~/.agents/skills/` symlinkek Codex/Gemini felé)
- **Telepített MCP-szerverek:** `chrome-devtools`, `context7`, `playwright`, `hostinger-mcp` (lásd [[05-Memory/Infrastructure]])
- **External skill cherry-pick playbook:** [[11-wiki/external-skill-cherry-pick]] — már bevett gyakorlat a `ln -s` symlink-cherry-pick

### Konkrét fejlődési lépések

#### 1. Skill-discovery automatizálása (session-end skill-írás)

A Voyager **self-verification + memory-write** mechanizmusát beépíteni a 11.11stop-ba: ha az agent sikeresen megoldott egy problémát, a protokoll utasítsa a használt eszközhívások és kódblokkok összefoglalását + új skill létrehozását.

```bash
# Új skill bootstrap a session-end során
mkdir -p ~/.claude/skills/<new_task_slug>
cat > ~/.claude/skills/<new_task_slug>/script.py <<'EOF'
# Agent által generált kód
EOF
cat > ~/.claude/skills/<new_task_slug>/SKILL.md <<'EOF'
---
name: <new_task_slug>
description: <mit csinál, mikor hívja az agent>
---
# Cél / Használat / Példa
EOF
```

Integrálható a **[[11-wiki/Crystallization-protocol]]**-hoz — a Learnings bullet-ek között a „reusable skill" jelöltek automatikusan skill-né alakulhatnak.

#### 2. Voyager-style skill-library a vault-on belül

A Voyager **vektor-DB-ben tárolja a skill-eket leírás-embedding alapján**. A Peti-vault Obsidian-Markdown variánsa: minden `~/.claude/skills/<slug>/SKILL.md`-hez tartozzon egy **párhuzamos Markdown-index a vault-ban** YAML frontmatter-rel:

```yaml
---
skill_name: <slug>
type: skill-index
description: "<szemantikus kereséshez használt 1-2 mondat>"
path: "~/.claude/skills/<slug>/"
dependencies: []
last_used: 2026-05-12
success_rate: 0.92
---
```

Helye: új mappa `12-skills/<slug>.md` (vagy a meglévő `05-Memory/Skill-map.md` kibővítése). A Phase B-ben (sv-01 memory-architecture-rel együtt) embedding-index kapcsolódik hozzá — top-K szemantikus retrieval session-start-kor.

#### 3. MCP-server-pool autonóm bővítése

A meglévő MCP-szettet (`chrome-devtools`, `context7`, `playwright`, `hostinger-mcp`) az agent **maga bővítheti** futásidőben, ha egy feladathoz hiányzik a tool. Megerősítés-igényes lépés (security):

```bash
# Agent által, bash-tool-on keresztül, explicit user-confirm után:
npm install -g @modelcontextprotocol/server-postgres
claude mcp add --transport stdio postgres -- npx @modelcontextprotocol/server-postgres
# A szerver bekerül a ~/.claude.json-be vagy projekt-szintű .mcp.json-be
```

**Védelem-réteg:** új `~/.claude/skills/mcp-installer/SKILL.md` skill, amely **kötelezően dokumentálja** az `add-server` műveletet az ADR-formátumban (`07-Decisions/2026-XX-XX MCP server add <név>.md`), így audit-trail marad.

#### 4. Tool-registry indexálás + Tool Search aktiválás

A 280+ skill + N MCP-szerver mellett a **tool-context-bloat** valós kockázat. A Claude Code beépített **Tool Search** funkciója megoldja:

```bash
export ENABLE_TOOL_SEARCH=auto   # küszöbérték alatti tool-ok azonnal, többi keresésen át
```

A kritikus MCP-szerverek (pl. fájlrendszer, vault-olvasó) **azonnal-betöltődő** szettben maradnak az `.mcp.json`-ben:

```json
{
  "mcpServers": {
    "obsidian-reader": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp-server"],
      "alwaysLoad": true
    }
  }
}
```

A többi MCP-szerver **on-demand** töltődik, csak a `Tool Search` által kiválasztott releváns set kerül kontextusba.

#### 5. Cost-aware tool-routing (Phase C+)

A CATP-LLM keretrendszer mintájára: minden MCP-szerverhez/skill-hez kerüljön **cost-tag** (token-becslés, latency, $/hívás). A session-end metrika-pipeline (sv-07 continuous-evaluation) gyűjtse, és az agent a router-szakaszban válassza a legolcsóbb-elégséges tool-t.

### Fázis-ütemezés a meglévő roadmap-en (Phase C, hét 5-6)

A 8-tengelyű roadmap sorrendjében a **#4 tengely a hét 5-6** kerül sorra, **#1 memory + #7 eval előtt** már fut → az embedding-réteg és metric-pipeline készen áll a Voyager-style skill-library + cost-aware routing fedezésére.

## 7. Mit kell tovább kutatni?

### Open questions

1. **MCP-szerver marketplace + trust-protokoll.** Az Anthropic hivatalos MCP Registry API fejlesztés alatt; nyitott: **hogyan ellenőrizhető a szerverek megbízhatósága** nyílt hálózatokon (honnan tudja az agent, hogy adott Shopify MCP szerver hivatalos)? UI/UX, jogosultság-kezelés, felfedezési protokollok még tisztázatlanok.

2. **Tool-use Chain-of-Thought training + backtracking.** ReAct + CoT gyakran elbukik multi-tool feladatoknál (compounding errors). **ToolLLM DFSDT** (Depth-First Search-based Decision Tree) backtracking-et javasol; nyitott: hogyan tanítható natívan többágú, nem-szekvenciális tervezés úgy, hogy a keresési fa **NE emésszen fel irreálisan sok tokent**?

3. **Voyager-style skill-evolution production-ben.** A Voyager Minecraft-ban működik; **production szoftverkörnyezetben** és fizikai robotikában? Open: **skill-karbantartás** — hogyan felejti el / írja felül az elavult (API-change) skill-eket, hogyan kerüli a katasztrofális felejtést hosszú távon?

4. **Biztonság + sandboxing.** „Az eszközök tetszőleges kódvégrehajtást jelentenek." Hiányzik a **szabványosított védelem** prompt-injection, adat-exfiltráció, és malicious third-party tool-ok ellen. Új benchmarkok (**ToolEmu, ToolSword, InjecAgent**), de **gyakorlati védelmi mechanizmusok** kidolgozása várat magára.

5. **Cost-aware tool-routing.** A **CATP-LLM** (FaaS-pricing-alapú offline RL) elsőnek tanítja a modelleket teljesítmény vs. erőforrás-egyensúlyozásra. Open: **futásidejű** költség-visszacsatolás integráció + **párhuzamos, nem-szekvenciális** tool-végrehajtás.

### Hiányzó papírok (forrás-gap a következő iterációhoz)

- **ToolEmu** (Ruan et al. 2023) — LLM-emulált sandbox kockázat-elemzéshez
- **InjecAgent** (Zhan et al. 2024) — indirekt prompt-injection benchmark
- **ToolSword** (Ye et al. 2024) — tool-learning 3 szakaszának biztonsági problémái
- **SayCan / Do As I Can, Not As I Say** (Ahn et al. 2022) — LLM-affordance robotika
- **Code as Policies** (Liang et al. 2022) — kód-alapú cselekvésgenerálás robotikában
- **ReAct** (Yao et al. 2022) — kanonikus iteratív tool-promptolás alapja
- **Reflexion** (Shinn et al. 2023) — verbális RL self-verification
- **AutoGen** (Wu et al. 2023) — Microsoft multi-agent tool-orchestration
- **Generative Agents** (Park et al. 2023) — szociális kontextus tool-tervezés
- **API-Bank** (Li et al. 2023) — korai átfogó tool-augmented LLM benchmark
- **CATP-LLM** — cost-aware tool-routing keretrendszer (offline CAORL)

## Phase A+ bővítés (2026-05-12 deep-research)

A Phase A 31 forrásához **+890 új forrás** csatlakozott 4 `--mode deep --no-wait` web-search-szel (MCP ecosystem 2026, Voyager skill-library prod retrospektív, Toolformer/ToolGen prod, Claude Code skill-system code-execution-with-MCP). **921 forrás** a notebookban (571 ready / 321 error / 29 preparing — error-arány a 502/timeout import-pulse-ok miatt; a Q&A elegendő source-bázist érte el).

### Q1 — 3 architektúrális elem KOMBINÁCIÓJA + sorrend (Peti-vault implementáció)

A 240 fájlos vault + 280-skill pool + részben telepített MCP-szerverek (chrome-devtools, context7, playwright, hostinger) kontextusában a friss anyagok három elemet emelnek ki kombinációként:

**1. Helyi Obsidian MCP-szerver + "Code Execution" (Kód-futtatásos) réteg.** Dedikált Obsidian MCP-szerver desktop proxy tunnelen, ami a link-gráfot bejárja és specifikus Markdown-heading alatti szerkesztést tesz lehetővé full-file overwrite nélkül [Phase-A+ src 1]. A "code-execution with MCP" mintázat (Anthropic) lecseréli a több ezer soros raw-betöltést: az ágens Python-szűrőt ír a Playwright/Context7-output-ra és csak az aggregált eredményt küldi vissza a kontextusba [Phase-A+ src 2, 3].

**2. Dinamikus Tool Search + `SKILL.md` tokozás.** A 280-pool egyidejű prompt-betöltése "Lost in the Middle"-hibát okoz [Phase-A+ src 4, 5]. Minden skill önálló `SKILL.md`-vel (YAML name/description) [Phase-A+ src 6]. Két integrációs opció: (a) Claude Code beépített `ENABLE_TOOL_SEARCH=auto` (auto-késleltetés a kontextus 10% felett) [Phase-A+ src 7], vagy (b) saját sűrű retriever `bge-m3` + `bge-reranker-v2-m3` Top-K=3 [Phase-A+ src 8, 9]. Az ágens csak a metaadatokat látja, kódot meghíváskor olvas [Phase-A+ src 6].

**3. ReCreate-alapú TTE (Test-Time Tool Evolution) + CodeBERT deduplikáció.** A 11.11-protokoll automatizálva: `system_template / instance_template / memory_template / agent_tools/ / agent_memory/` ötfázisú struktúrával [Phase-A+ src 6, 10]. Sikeres trajektóriákból új skill, kudarcokból `agent_memory/` guardrail. CodeBERT cosine-similarity új skill ↔ meglévő pool között, ha $\tau > 0.8$ → eldobás [Phase-A+ src 8, 11].

**Beépítési sorrend:**
1. **MCP-réteg + code-execution alapozás** (infra-gerinc, e nélkül a 240 fájlon nem futhat tokenhatékony művelet) [src 1, 2].
2. **`SKILL.md` meta-réteg + dinamikus keresés** (a 280-pool átkonvertálása, context-tehermentesítés) [src 6, 7, 9].
3. **ReCreate evolúciós hurok + dedup** (a 11.11stop végére, ami önfejlesztővé teszi a vaultot) [src 6, 8, 11].

### Q2 — Production-ready vs akadémiai státusz (8 elem)

**Production-ready (industrial-validated, business case):**

- **MCP (Model Context Protocol)** — Enterprise Infrastructure 2026-ra. Oracle Fusion Agentic Applications + ServiceNow Build Agent governed-by-default éles deploymentben [Phase-A+ src 1, 2].
- **Claude Tool Use API / Claude Code** — Commercial Platform; ServiceNow Build Agent default modellje [Phase-A+ src 2, 3].

**Academic stage (paper-only / proof-of-concept):**

- **Toolformer** (Schick et al. 2023) — single-intent alapozó kutatás, papírban maradt [src 4].
- **Gorilla** — *Berkeley Function Calling Leaderboard* + retrieval-aware training, NeurIPS-keretrendszer, nem prod-platform [src 5-7].
- **ToolGen** (ICLR 2025) — virtuális token = tool, generatív retrieval. Publikáció + nyílt GitHub, prod-deployment-nincs [src 7-9].
- **Voyager skill-library** — Minecraft / gamified környezet, "rigor" hiánya valós tudományos/ipari folyamatokhoz [src 10, 11].
- **CREATOR** (ACL 2023) — abstract-vs-concrete reasoning szétválasztás, one-off tool-generation lépés gátolja az ipari adaptációt [src 12, 13].
- **LATM** (ICLR 2024) — closed-loop tool-maker, "decoupled paradigm" elválasztja a tool-creation-t az inferenciától, valós idejű prod-hoz nem alkalmas [src 7, 12].

### Q3 — Cost-sensitive 3-budget-tier (mit vágjunk le)

**$50/hó — "Bootstrapper":**
- *Levágva:* autonóm TTE (egy futtatás $300-600 [src 1]); Voyager skill-library (GPT-4 15× drágább a GPT-3.5-nél [src 2]); fizetős enterprise gateway-ek (TrueFoundry, Kong [src 3, 4]).
- *Megtartva:* Composio Free (havi 20.000 hívás [src 5]) **vagy** Cloudflare Workers $5 alap [src 6]. Helyi routing: Bifrost (free OSS [src 7]). Embedding helyett **BM25** (~$0.006/100q CPU-n) **vagy** ToolGen virtuális tokenek (~$0.005/100q) [src 8]. Cost-aware routing helyi Llama2-7B-vel CATP-LLM logika alapján [src 9, 10].

**$200/hó — "Professional":**
- *Levágva:* továbbra is a teljes TTE [src 1].
- *Megtartva/bővítve:* GPT-4-Voyager helyett **ReCreate** (36-82% költségcsökkentés ADAS-agent generálásban; domain-optimalizálás $7.41-$27.31 [src 11]). Composio Standard $29/hó, 200.000 hívás [src 5]. Embedding: BM25 → **ToolRetriever** (~$0.002/100q, jobb pontosság [src 8]). Adaptive Model Routing (**FrugalGPT, RouteLLM**) edge ↔ frontier átirányítás [src 12].
- 
**$500/hó — "Enterprise-Lite":**
- *Megtartva:* **TrueFoundry Pro MCP Gateway $499/hó** (RBAC + rate-limit + VPC [src 4]) **vagy** Composio Professional $229/hó 2M hívás [src 5]. **ReCreate** folyamatos tapasztalat-vezérelt optimalizálás [src 11]. Voyager GPT-4-skill-építés bevehető [src 2]. **IterFeedback** retrieval (~$0.055/100q, NDCG 89.51 [src 8]). CATP-LLM Quality-of-Plan + FaaS memória-modellezés [src 13, 14].
- *Levágva még itt is:* TTE ab-initio szintézis ($300-600/run kimerítené a havi keretet [src 1]).

### Mit ad ez konkrétan a Peti-vault-nek

- **Új ADR-kandidátus:** Obsidian MCP-szerver + `SKILL.md` re-tokozás a 280-pool-on (a Q1-3-elem sorrend formalizálása).
- **Phase B sprint-1:** `ENABLE_TOOL_SEARCH=auto` aktiválás dev-en (Q1 step-2 prereq), `bge-m3` benchmark a 280-skill metadata-index ellen.
- **Költség-döntés:** a jelenlegi tier elhelyezése a Q3 3-skálán → Bootstrapper-Professional határon (Anthropic API + Composio Free elég); Voyager-szerű evolúciós hurok bevezetése csak ReCreate-szel, NEM ab-initio TTE-vel.
- **Production-readiness audit:** Q2 alapján a Phase A "5 kanonikus minta" táblát meg kell jelölni production-ready vs paper-only flag-gel — csak a top-2 (MCP + Claude Code skills) megy éles infrába, a többi kísérleti.

## Audio overview

```bash
notebooklm generate audio -n 90e132a1-3f58-4740-bdfc-8c9318571a6d
```

10-15 perces podcast-szerű összefoglaló a 31 forrás szintéziséről — futtatható Phase A végén batch-ben az összes tengelyre.

## Akció-pontok ehhez a tengelyhez

- [ ] **Phase B sprint-tervezés:** SV-4 epic 3-4 sprintre bontva — (1) skill-discovery automatizálás 11.11stop-hoz, (2) skill-library index (`12-skills/` vault-mappa + embedding), (3) MCP-server-pool autonóm bővítés + ADR-audit-trail, (4) Tool Search aktiválás + cost-tag MVP
- [ ] **`ENABLE_TOOL_SEARCH=auto` aktiválása** dev-szinten — mérjük a context-token-megtakarítást a meglévő 280-skill-pool-on
- [ ] **`.mcp.json` audit** — `alwaysLoad: true` flag a kritikus szerverekre (chrome-devtools, context7), a többi on-demand
- [ ] **Voyager skill-template** kidolgozás: minden új skill `SKILL.md`-jébe egységes frontmatter (description, dependencies, last_used, success_rate)
- [ ] **Hiányzó papírok** beolvasása a következő research-iterációba (ToolEmu, ReAct, Reflexion, CATP-LLM) — biztonság + cost-aware tengely megerősítése
- [ ] **Audio overview** generálás + letöltés

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — ADR, 8-tengelyes roadmap
- [[10-raw/2026-05-12 — Superintelligence research source pool]] — source pool
- [[11-wiki/external-skill-cherry-pick]] — symlink-cherry-pick playbook (skill-library bázisa)
- [[11-wiki/sv-01-memory-architecture]] — embedding-réteg amire a Voyager skill-library épül
- [[11-wiki/Crystallization-protocol]] — a Learnings → skill auto-konverzió kapcsolata
- [[05-Memory/Skill-map]] — a meglévő 280-skill csoportosítás
- [[05-Memory/Infrastructure]] — telepített MCP-szerverek listája

## NotebookLM-konverzáció

- **Notebook ID:** `90e132a1-3f58-4740-bdfc-8c9318571a6d`
- **Conversation ID:** `4df77466-587b-4226-8dbc-e6a13f433f7f`
- **Források:** 31 (28 ready, 2 YouTube error, 1 add-research web-pool)
- **Kérdések:** 7/7 válaszolva
- **Válaszok mentve:** `/tmp/sv-research/sv4-q{1..7}-*.txt`
