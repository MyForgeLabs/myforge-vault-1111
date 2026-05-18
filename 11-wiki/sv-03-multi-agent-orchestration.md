---
name: SV-3 Multi-agent orchestration
type: wiki
tags: ["#type/wiki", "agi", "multi-agent", "orchestration", "agent-architecture", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: done
phase: A+
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: c7eba59a-a42b-4bf4-8fb2-30c13806eb64
---

# SV-3 — Multi-agent orchestration

A 8-tengelyű szuperintelligens-vault evolúciós research harmadik cikke. **Kérdés:** ad-e szignifikánsan jobb minőséget több párhuzamos, specializált agent (planner / executor / critic / summarizer / red-team), mint egy single-agent rendszer — és ha igen, milyen architektúra-mintákkal építsük be a meglévő 11.11-protokoll + 280-skill-pool vault-ba?

> **Status:** 7/7 kérdés válaszolva + Phase A+ 3 deep-question válaszolva. NotebookLM-források: **737** (Phase A 14 → +723 deep-research bővítés, 589 ready / 14 error / többi pending). Audio-overview generálás folyamatban.

## 1. A tengely magja

A **multi-agent orchestráció** az LLM-alapú rendszerek kontextusában egy vezérlési és architekturális paradigma, amelyben több, **specializált szerepkörrel** felruházott autonóm ágens (LLM-ek, eszközök, emberek) **strukturált hálózati vagy hierarchikus mintázatok** mentén kommunikál egymással komplex feladatok megoldása céljából. Az orchestráció magját a **„beszélgetés-központú programozás" (conversation programming)** és az **állapotkezelés (state management)** adja: a vezérlési folyamatot az ágensek közötti üzenetváltások és interakciós szabályok határozzák meg, így a feladatmegoldás nem egyetlen monolitikus modelllépésből, hanem az ágensek **iteratív együttműködéséből** (tervezés → visszacsatolás → végrehajtás) áll össze.

### Single-agent vs multi-agent

A single-agent rendszerekben egyetlen LLM kísérli meg megérteni a teljes kontextust, kiválasztani az eszközöket, megtervezni a lépéseket és végrehajtani azokat. A tapasztalatok szerint **5-10 eszköznél több** esetén az egyetlen ágens kontextusablaka **túlterhelődik**, és egyre rosszabb döntéseket hoz. A multi-agent rendszerek a feladatokat **specializált ágensekre bontják** — minden ágens csak a saját felelősségi körére fókuszál (kutató, kódoló, matematikus, kritikus), saját promptokkal és eszközökkel, és **dedikált interakciós minták** (pl. orchestrator-worker) szerint dolgozik össze.

### Miért szignifikánsan jobb több párhuzamos agent?

A vezető kutatások három fő mechanizmust azonosítanak:

| Mechanizmus | Eredmény | Forrás |
|---|---|---|
| **Fókuszált kontextusablakok + token-skálázás** | Anthropic mérés szerint a teljesítmény-variancia **~80%-át a tokenhasználat magyarázza**; al-ágensek saját kontextusukban dolgoznak, megsokszorozzák a párhuzamos érvelési kapacitást | Anthropic multi-agent research system |
| **Divergens gondolkodás + critic-loop** | AutoGen Writer+Safeguard pár **8-35%-kal több biztonságos kódot** generál; ChatDev „kommunikatív dehallucináció" drasztikusan javítja a kód-futtathatóságot | AutoGen (arXiv 2308.08155), ChatDev (arXiv 2307.07924) |
| **Hosszútávú koherencia (emergens viselkedés)** | Generative Agents ablation: a multi-agent dinamika **elengedhetetlen a hiteles** (believable) hosszútávú társas viselkedéshez (önálló információterjesztés, koordináció) | Generative Agents (Park et al. 2023, arXiv 2304.03442) |

Az Anthropic számszerű mérés szerint a multi-agent research system **akár 90,2%-kal jobb teljesítményt** nyújt komplex kutatásokban egyetlen modellhez képest — cserébe **~15× több tokent** éget el (lásd #5 failure-modes).

## 2. Kanonikus megközelítések (6 fő minta)

### Generative Agents (Park et al. 2023, Stanford)
- **Mechanizmus:** Természetes nyelvű **memory-stream** + dinamikus retrieval + **reflection-loop** (időről időre az ágens absztrakciókká szintetizálja a nyers emlékeit) + tervezés
- **Kulcs-újdonság:** Hossztávú koherencia kódolt szabályok nélkül; emergens társas viselkedés
- **Use-case:** Smallville-szimuláció — egyetlen kezdeti gondolatból (pl. „akarjon valaki Valentin-napi bulit") az ágensek önállóan terjesztik az információt, egyeztetnek időpontokat, megjelennek az eseményen

### ChatDev (Qian et al. 2023)
- **Mechanizmus:** Vízesés-modell (tervezés/kódolás/tesztelés) → specializált ágensek **chat-lánca** (chat chain); párokba rendezett instruktor + asszisztens
- **Kulcs-újdonság:** **„Kommunikatív dehallucináció"** — a kódoló és tesztelő addig vitáznak, amíg a kódolási hibákat (hallucinációkat) ki nem szűrik
- **Use-case:** Teljes szoftver (pl. Gomoku) generálása egyetlen laikus parancsból — CEO → CTO → programozó → tesztelő lánc

### AutoGen (Microsoft 2023)
- **Mechanizmus:** **„Conversation programming"** — rugalmas üzenetváltások, közös chatek vagy hierarchikus struktúrák; LLM/eszköz/ember-mix
- **Kulcs-újdonság:** Kódolási és természetes-nyelvi vezérlés ötvözése; beépített **GroupChatManager**
- **Use-case:** OptiGuide — Commander + Writer + Safeguard pár iteratívan generál, validál, futtat biztonságos kódot

### CrewAI
- **Mechanizmus:** **Flows** (determinisztikus, eseményvezérelt) + **Crews** (autonóm, szerepjátszó ágenscsapatok)
- **Kulcs-újdonság:** Autonómia és kontroll szétválasztása — kiszámítható állapotkezelés, miközben kihasználja a specializált ágensek non-determinisztikus problémamegoldó képességét
- **Use-case:** API-háttérrendszerek — Flow kezeli az állapotot + DB-mentést, a tartalom-generálást delegálja egy Crew-nak

### LangGraph (LangChain)
- **Mechanizmus:** **Irányított gráf** (DAG) + állapotgép, shared-state objektumok (pl. közös üzenetlista), szigorú paraméterátadás
- **Kulcs-újdonság:** **„Durable execution"** futtatókörnyezet — időutazás (time travel), streaming, memory, human-in-the-loop, custom kognitív architektúrák
- **Use-case:** Hierarchikus / supervisor-hálózatok komplex kutatási folyamatokhoz (fő ágens → specializált al-ágensek); aszinkron enterprise workflow-k

### Anthropic Claude Agent SDK
- **Mechanizmus:** **Kompozábilis / egyszerűség-vezérelt** — augmented LLM + workflows + autonomous agents minták; sikeres prod-rendszerek **ritkán használnak komplex frameworköt**
- **Kulcs-újdonság:** Komplexitást csak nyílt-végű feladatokra; mindenre mást **determinisztikus kódutak**; külső memória + retry logic az állapotvesztés ellen
- **Use-case:** **Orchestrator-worker minta** — egy vezető kutató delegál párhuzamosan kereső al-ágenseknek (lásd `https://www.anthropic.com/engineering/multi-agent-research-system`)

## 3. Tech-stack opciók 2026-ban

A 2026-os piac **három filozófia** mentén kristályosodott ki:

| Filozófia | Példa | Kommunikáció |
|---|---|---|
| **Graph-based** | LangGraph | Shared state / paraméterátadás, DAG-szerű flow |
| **Role-based** | CrewAI | Hierarchikus „crew" + determinisztikus „flow" |
| **Conversation-based** | AutoGen | Természetes nyelvi üzenetváltás + auto-reply |

### Részletes összehasonlítás

| Eszköz | Filozófia | DX (tanulási görbe) | Trade-off | Tipikus use-case |
|---|---|---|---|---|
| **LangGraph** | Graph | Magasabb — manuálisan kell node-okat/edge-eket összekötni | Legrobusztusabb „durable execution"; idő-utazás + streaming + memory + custom kognitív arch. | Aszinkron enterprise workflow-k, human-in-the-loop, hosszan futó folyamatok |
| **CrewAI** | Role | Alacsony — gyorsan tanulható | Termelés-kész struktúra Flows+Crews-szel, kevesebb low-level kontroll a gondolkodási folyamatok felett | Komplex tartalomgenerálás, API-háttér, multi-agent kutatás (Andrew Ng kiemeli) |
| **AutoGen** | Conversation | Közepes — rugalmas, de hajlamos a token-overshoot-ra | Nyílt-végű chatek a tokenlimit kimerítésére hajlamosak; nehezebb robust production deploy | Szoftverfejlesztés, matematikai problémák, dinamikus viták |
| **Claude Agent SDK** | Kompozábilis | Legalacsonyabb — egyszerű primitívek | „Build effective agents" filozófia: csak akkor autonóm ágens, ha tényleg kell; kevesebb dobozos absztrakció | Nyílt-végű webes kutatás, orchestrator-worker minta |
| **OpenHands** | Turnkey | Plug-and-play | Nyílt forráskódú (MIT) AI-driven development ökoszisztéma — SDK + CLI + GUI + enterprise VPC; akár több ezer ágens egyszerre felhőben | Kódolási agent farmok, vállalati telepítés |
| **Devin** | Turnkey, zárt | Plug-and-play (SaaS) | Beépített sandbox: shell + szerkesztő + böngésző; hossztávú tervezés és önjavítás | „Autonóm AI szoftvermérnök" — több ezer döntés, menet közbeni hibajavítás |
| **Manus** | Turnkey, generalist | UI-szintű használat | „Less structure, more intelligence" — asztali alkalmazásokon + böngészőn + Slack-en + emailen mozog | Laikus felhasználók: prezentáció, weboldal, dizájn-elem készítése |

### A „kevesebb framework" tanulság

Az Anthropic engineering blog kategorikus: **a sikeres production rendszerek ritkán használnak komplex frameworköt**. Az ajánlott minta: egyszerű, kompozábilis primitívek (augmented LLM → workflow → autonomous agent), és csak akkor lépj feljebb a komplexitás-létrán, ha az adott feladat valóban indokolja. (A LangChain mérnökei is megerősítik: enterprise rendszerekben szinte mindig **„teljesen egyedi kognitív architektúrákra"** van szükség off-the-shelf hierarchiák helyett.)

## 4. Friss áttörések 2024-2026

A 2024-2026 korszak túllépett a pre-2024 statikus, törékeny iterációkon. Négy fő áttörés:

### 4.1 Anthropic multi-agent research system (lead-agent + subagents)
Egy komplex, aszinkron kutatási rendszer Claude-ágensekkel: **párhuzamos felderítés + szintézis**. A tokenhasználat ~15× nőtt egy chat-hez képest, de **a teljesítmény akár 90,2%-kal jobb** komplex kutatásokban. Az „orchestrator-worker" minta egy központi vezető ágenst (planner) és specializált al-ágenseket (subagents) használ.

### 4.2 Devin — első autonóm AI szoftvermérnök
A kulcs-újdonság: **beépített sandbox-számítási környezet** — shell + kódszerkesztő + böngésző. Ez engedi, hogy a modell több ezer döntést hozzon, **menet közben tanuljon és javítson hibákat**, hossztávú terveken dolgozzon.

### 4.3 OpenHands — nyílt-forráskódú alternatíva
SDK + CLI + lokális GUI + enterprise VPC. **Kód-alapú agent-definíció**, és akár **több ezer ágens egyidejű felhő-futtatása**. Rugalmas open-source ellenpólusa a zárt SaaS-rendszereknek.

### 4.4 Manus — generalist „browser operator"
„Less structure, more intelligence" filozófia. Nem szakosodott kódoló agent, hanem **általános UI-operátor**: asztali app, böngésző, Slack, email — laikus felhasználóknak készít prezentációt / weboldalt / dizájnt.

### Lead-agent + subagent minta (orchestrator-worker)

A korszak **mester-mintája**:

1. **Lead agent** fogadja a komplex kérést, stratégiát épít, részfeladatokra bontja
2. **Specializált subagents** (kutató, kódoló stb.) **párhuzamosan**, saját kontextusukban dolgoznak
3. Subagent-ek **intelligens szűrőként** működnek — a kinyert esszenciát küldik vissza
4. Lead agent **szintetizál** végső választ

### Parallel-tool-use vs sequential

A korai ágensek szekvenciálisan futtatták az eszközöket (lassú). A modern parallel-megközelítés **kétszintű**:
- (1) Lead agent egyszerre indít **3-5 subagentet**
- (2) Maguk a subagentek **3+ tool**-t futtatnak párhuzamosan

Eredmény: akár **90%-kal rövidebb kutatási idő** — percek óra helyett.

### Context-rot és megoldásai

A **context-rot** = a hosszú beszélgetés / sok lépés meghaladja a model kontextusablakát → koherenciavesztés. Három modern megoldás:

1. **Intelligens tömörítés + külső memória** — befejezett fázisok összefoglalása, esszenciális info kimentése
2. **Tiszta kontextusú al-ágensek** — kontextuslimit közelében új, üres-kontextusú subagent + óvatos „handoff"
3. **Közvetlen fájlrendszer-kimenet („telefonjáték" elkerülése)** — a subagent nem visszaadja a teljes kódot/jelentést, hanem **közvetlenül fájlba** ír, csak egy referenciát ad a lead-nek

## 5. Failure-modes és limitációk

A multi-agent rendszerek **nem csodaszerek**. Hét fő failure-mode:

### 5.1 Token-költség robbanás („unbounded token use")
- Egy agent **4× több** tokent használ chat-nél
- Multi-agent research system **~15× több** tokent éget el
- Generative Agents Smallville: **25 ágens × 2 nap = dollárezrek**, napokig tartó futás
- Laza kommunikációs topológia → korlátlan LLM-hívások → megbízhatatlan, drága

### 5.2 Hibapropagáció (compounding errors)
Hosszan futó stateful ágensek esetén a hibák **halmozódnak**. Egyetlen rossz eszközválasztás vagy félreértett részfeladat **teljesen eltérő útvonalra** viheti az ágenseket → katasztrofális kimenetel.

### 5.3 Debugging-pokol (non-determinisztikus viselkedés)
Azonos prompttal is **eltérő futás**. Apró kódváltoztatás **dominóeffektust** indít. Tracing nélkül a fejlesztők csak „érthetetlen fecsegést" (unintelligible chatter) látnak.

### 5.4 Hallucináció-amplifikáció és role-flipping
Rosszul strukturált kommunikációnál a hibák **felerősödnek**. Tipikus tünetek: szerepcserélődés (role flipping), instrukciók végtelen ismételgetése, hamis válaszok. **Memory-bias**: az ágens „kiszínezi" (embellishes) a múltbeli eseményeit — valósághű, de kitalált memória.

### 5.5 Koordinációs overhead + race conditions
- Korai rendszerek: 50 subagent egy egyszerű kérdéshez (weben bolyongtak)
- Szinkron végrehajtás → bottleneck (lead vár a workereknek)
- Aszinkron végrehajtás → új probléma: állapot-konzisztencia, elosztott hibakezelés
- **„Game of telephone"** — agentek hosszú kimeneteket passzolgatnak → token-keret gyors elégetése

### 5.6 Context-rot
A 4.4 fejezet részletezi. A hosszú workflow / sok eszköz **kontextusablak-túlterhelést** okoz, ha nincs intelligens memória-tömörítés.

### 5.7 Biztonsági rések
- **Prompt-injection** külső adatból (weboldal-rejtett prompt)
- **Memory hacking** — manipulált beszélgetés meggyőzi az ágenst egy sosem-volt eseményről
- Autonóm kódvégrehajtás + API-hívás veszélyes, ha hiányzik a Safeguard (lásd AutoGen)

### Mikor szuboptimális a multi-agent?

| Helyzet | Miért nem jó |
|---|---|
| Egyszerű, jól definiált feladat | Felesleges latency + költség; egy jól promptolt RAG-LLM is elég |
| Szorosan csatolt, közös kontextust igénylő folyamat | Az LLM-ágensek 2026-ban **még nem elég jók valós-idejű koordinációban** |
| Gyenge task definition (homályos elvárások) | A rendszer nem pótolja a hiányzó specifikációt — alacsony információsűrűségű, felszínes megoldás (pl. „túl alapvető Snake játék") |

## 6. Implementáció a Peti-vault kontextusban

A meglévő struktúra (`AGENTS.md` + 11.11 session-protokoll + 280-skill pool + **több párhuzamos session lehet nyitva**, már most 8 párhuzamos research-agent fut) **kiválóan illeszkedik** az orchestrator-worker mintára. Több kulcsmegfigyelés a NotebookLM-syntézisből:

### 6.1 Framework-választás: LangGraph vagy saját Anthropic SDK
A források szerint **két reális opció**:
- **LangGraph** — graph-based, „durable execution", shared state (= az Obsidian vault maga lehet a shared state), human-in-the-loop, time travel
- **Saját Anthropic-mintájú SDK** — egyszerű kompozábilis primitívek, „orchestrator-worker workflow" mint default, csak ott autonomy ahol indokolt

Az Anthropic engineering tanulság (**„a sikeres prod-rendszerek ritkán használnak komplex frameworköt"**) erősen sugallja: **kezdj saját Anthropic SDK-val**, és csak akkor lépj LangGraph-ra, ha tényleg state-graph komplexitás van.

> Az AutoGen kódolási vitákra erős, de a token-overshoot egy Markdown-vault iteratív szerkesztésénél felesleges drag. CrewAI gyors-tanulható, de a low-level kontroll hiánya korlátozhatja a 11.11-protokollal való integrációt.

### 6.2 Role-felosztás vault-fejlesztési feladatokra

A meglévő több-párhuzamos-session-modell már **félautomata multi-agent** — a NotebookLM válasza alapján a klasszikus szoftverfejlesztő (ChatDev) szerepköröket **adaptáljuk kutatási + tartalomgenerálási mintákra**:

| Szerep | Felelősség | Vault-specifikus konkrétum |
|---|---|---|
| **Planner / Commander** (Orchestrator) | Fogadja a 11.11-promptot, stratégiát alkot, kiválasztja a 280-skill pool releváns elemeit, részfeladatokra bont | A `/11.11start` által indított „lead session" |
| **Executor / Subagent** (Writer / Kutató) | Specifikus Markdown-fájlokat módosít, vagy kutatási feladatot végez **saját elszigetelt kontextusban** | A jelenlegi párhuzamos research-agentek mintáját követi |
| **Critic / Safeguard** (Red-team) | Validálja az Executor kimenetét (formai + tartalmi hallucináció); csak az ő jóváhagyásával kerül a vaultba | Új skill: `multi-agent-vault-critic` — ChatDev „kommunikatív dehallucinációja" minta |
| **Summarizer / Citation** | Backlinkeket fűz össze a vault-ban, session-záró jelentést generál | Részlegesen már a `crystallization-protocol` szerepe — kiegészíthető |

### 6.3 Illeszkedés a 11.11-protokollhoz és a többsessionhöz

A NotebookLM-syntézis **„Supervisor with tools"** architektúrát javasol: az Orchestrator a 8 meglévő research-agentet **eszközként (tool) hívja meg**, nem peer-agentként. **Kulcs-mintában**:

- **„Direct to filesystem" (context-rot megelőzés)** — az Executor / Research subagentek **NEM** küldik vissza a teljes generált tartalmat a Plannernek, hanem **közvetlenül a Markdown-fájlokba** írnak, és csak egy könnyű referenciát (fájlnév, rövid summary) adnak vissza. **Ez tökéletesen illeszkedik az Obsidian-vault paradigmához** — a vault maga a megosztott állapottér.
- **Aszinkron végrehajtás** — a párhuzamos session-ök már ezt az elvet követik (lásd `[[../05-Memory/Infrastructure]]#11.11 session-protokoll`)
- **Tracing** — minden subagent-akció commitba kerül (vault-autosave), az `AGENT=claude|codex|gemini` env-var a commit-üzenetbe is — ez **már most a minimum-tracing**

### 6.4 MVP első sprint (4 lépés)

Az Anthropic alapelve: **„Tartsd meg az ágensek dizájnjának egyszerűségét"** — az MVP NE legyen azonnal 5-ágenses autonóm hálózat.

| Lépés | Mit építünk | Hivatkozás |
|---|---|---|
| **1. Alap Workflow** | **Orchestrator-Worker workflow** — fix kódút, központi LLM (Planner) fogadja a 11.11-session indítását, eldönti melyik subagentet indítsa | Anthropic „Building Effective Agents" — workflow szint |
| **2. Parallelizáció + filesystem** | Aszinkron 2-3 Executor a 280-skill pool egy-egy elemével; **„direct to filesystem"** írás, csak status-jelentés vissza | A meglévő több-párhuzamos-session-modell formalizálása |
| **3. Evaluator-Optimizer** | Critic (Reviewer) ágens hozzáadása — egyszerű evaluator-optimizer hurok; Markdown-fájl véglegesítés ELŐTT formai + tartalmi check | ChatDev kommunikatív dehallucináció minta |
| **4. Transzparencia + Traceability** | LangSmith vagy egyszerű JSONL log per-agent-decision; **nem-determinisztikus iterációk** debug-olhatósága | Anthropic engineering: „tracing without observability is gambling" |

### 6.5 Mit hozhat a meglévő infrastruktúrából

- **Skill-pool (280 elem)** = subagent capability-katalógus
- **`AGENTS.md` (közös instrukciós réteg)** = system prompt all agents
- **11.11 session-protokoll** = orchestrator-worker control flow primitívja
- **Crystallization-protocol** = summarizer-agent template
- **Vault-autosave (10 perces git-commit)** = audit trail / time-travel alap

## 7. Mit kell tovább kutatni

A források öt kritikus, alig-érintett területet azonosítanak:

### 7.1 Dinamikus értékelés és end-state benchmarkok
A jelenlegi turn-by-turn értékelések feltételezik a fix lépésszámot — de multi-agent rendszerek **azonos bemenetből különböző érvényes utakon** jutnak el. **End-state evaluation** módszertanok kellenek, amik a végállapot minőségét mérik, nem a lépéseket.

### 7.2 Biztonság: memory hacking + kaszkádoló hibák
Új sebezhetőség: **memory hacking** — gondosan felépített beszélgetés meggyőzi az ágenst egy sosem-volt múltbeli eseményről. Fail-safe mechanizmusok hiányoznak a kaszkádoló hibákra, reward hacking-re, kontrollálatlanná válásra.

### 7.3 Aszinkron A2A-koordináció + state consistency
A jelen rendszerek többnyire **szinkronok** (bottleneck). Az aszinkron A2A koordináció növelné a sebességet, de a **rendszerszintű állapot-konzisztencia + hibatovaterjedés-megállítás** jelenleg megoldatlan.

### 7.4 Költségoptimalizáció + optimális topológiák
Nincs „one-fits-all" válasz: hány ágens, milyen szerepelosztás, milyen interakciós minta optimális egy adott feladatra. Felmerül **kifejezetten multi-agent-architektúrához hangolt kisebb / olcsóbb modellek** képzésének igénye.

### 7.5 Hibrid orchestráció + önfejlesztő ágensek
**Tökéletes human-in-the-loop egyensúly** keresése. A statikus szerepek helyett **új készségek önálló felfedezése** (skill discovery). Andrew Ng nyitott kérdése: mikor lesz **egyetlen valóban általános célú ágens** a specifikus-feladatra-épített frameworkok helyett?

## Phase A+ bővítés (2026-05-12 deep-research)

A Phase A 14 forrásához **+723 új** csatlakozott 4 `--mode deep --no-wait` web-search-szel (Devin/Cognition, Manus, Anthropic agent cookbook, OpenHands). **737 forrás** a notebookban (589 ready, 14 error, többi pending).

### Q1 — Optimális 3-elem kombináció (NotebookLM-szintézis)

A 2025-26 ipari konszenzus: a **„peer-to-peer csoportos csevegés" zsákutca** — átlagosan **15× tokenköltség + masszív kontextus-degradáció**. 3 elem kombinációja:

**1. réteg — Orchestrator + Isolated Subagents („P2 prompt pattern").** Központi Planner/Orchestrator vezérli a fő 11.11 session-protokollt + teljes kontextust; rész­feladatokhoz **ephemerális isolated subagent**-eket indít tiszta kontextus­ablakban, saját system-prompttal. **Kulcs P2 szabály:** a subagent SOHA nem küldi vissza a teljes levezetést, csak egy magasan tömörített **summary return**-t. → Megakadályozza hogy a 8 párhuzamos research-agent kutatási adatai túlcsordítsák az Orchestrator kontextusablakát. Az Anthropic mérései szerint a tokenfelhasználás skálázásával radikálisan növeli a párhuzamos végrehajtás sikerességét.

**2. réteg — Progressive Disclosure of Skills (AgentSkills Standard).** A 280-skill 1 system-promptba sűrítése = fókuszvesztés + token-pazarlás. **OpenHands V1 minta:** skillenként `SKILL.md`; a fő agent system-promptban csak ~100 karakteres metadata-címtárat lát a 280 skillről. Csak amikor egy kulcsszó felmerül, vagy az agent explicit `invoke_skill()`-et hív → teljes instrukció betöltése. Külön fájlokba szervezhető a 11.11 protokoll adott szakasza, a Markdown-formázási szabályok, vagy a kutatási irányelvek — az agent csak akkor olvassa be, ha azon a fázison dolgozik.

**3. réteg — Filesystem-as-State & Context-Mode MCP (event-driven állapot).** Az agent state-jét **ki kell emelni** az LLM-kontextusából; a fájlrendszer (Obsidian vault) = **single source of truth**. **Microsoft Azure SRE bizonyíték:** natív „bash-szerű" fájlrendszer-hozzáférés (`read_file`, `grep`, `find`) **jobb mint testreszabott API-eszközök**. **OpenHands event-driven arch:** stateless agentek, közvetlen Markdown-írás, append-only `EventLog`. „Think in code" paradigma + nagy fájlokhoz **BM25-alapú „context-mode MCP" szerver**, amely strukturált keresést biztosít anélkül, hogy a teljes fájltartalmat folyamatosan az LLM-nek küldené.

#### Konkrét Tech-Stack (2026)
- **Orchestráció:** **LangGraph 2.0** — durable runtime + Checkpointer multi-session suspend/resume; type-safe streaming és checkpoint-resume több napig futó feladatokhoz
- **Tooling:** **MCP (Model Context Protocol)** dedikált lokális szerverrel az Obsidian-vault fölött (`codebase-memory-mcp` minta) — strukturált grep + fájl-írás/olvasás minden agentnek
- **Modell-routing:** **OmniRoute** paradigma — Planner: Claude 4.5 Opus/Sonnet érvelő; parallel workers: olcsóbb dedikált modellek (40-60% tokenköltség-csökkentés)

#### Bevezetési sprintek (sorrendben)
1. **Sprint 1: AgentSkills + MCP infra** — 280 skill konszolidálása trigger-alapú `SKILL.md` fájlokká + lokális MCP-szerver az egyetlen agentnek (előbb a single-agent környezetet rendbe tenni)
2. **Sprint 2: Orchestrator + Isolated Subagents (P2)** — LangGraph Planner (Claude 4.5 Sonnet érvelővel) + friss memóriájú Worker subagent + MCP-vel írás a vaultba + summary-only return
3. **Sprint 3: Párhuzamosítás + Stuck Detection** — 8 párhuzamos fan-out LangGraph parallel node-okkal vagy OpenHands ThreadPoolExecutor-ral; Stuck Detection (hibás ciklus → auto-halt); Critic safeguard Markdown-link integritás-ellenőrzéssel session-záráskor

### Q2 — Production-ready vs akadémiai (per-framework, forrás-idézetekkel)

Az iparági konszenzus (Anthropic, OpenAI, FlowHunt) egyértelműen elmozdult a szabadon csevegő, „peer-to-peer" ágenshálózatoktól egy szigorúbb, determinisztikus „P2 prompt pattern" struktúra felé (központi Orchestrator + izolált subagentek + summary return).

**Production-Ready (ipari sztenderdek, working business case):**

| Framework | Státusz | Validáció |
|---|---|---|
| **LangGraph (LangChain)** | Piacvezető enterprise orchestrációs réteg komplex Python munkafolyamatokhoz | Legszélesebb körben adaptált production framework. 2026 LangGraph 2.0: type-safe streaming + checkpoint-resume több napig futó ágenses feladatokhoz |
| **CrewAI** | Production, gyorsan skálázódó | Fortune 500 >60%-a használja prototípusra + role-based workflow-ra. 2026 kétszintű orchestráció: eseményvezérelt „Flow" + autonóm „Crew" delegáció hibridje |
| **AutoGen (Microsoft Agent Framework 1.0)** | Kutatásból enterprise productba érett | 2026 áprilisában beolvadt a **Microsoft Agent Framework 1.0**-ba (Semantic Kernel-lel együtt). Elhagyta a „GroupChat" koncepciót; gráf-alapú orchestráció + middleware hook + DevUI + natív MCP integráció |
| **Anthropic Multi-Agent (Managed Agents / Agent SDK)** | „Cattle not pets" ipari architektúra | A multi-agent rendszerek 15× tokenköltséget használnak, a teljesítmény-variancia 80%-át a tokenek száma magyarázza. „Managed Agents" leválasztja az „agyat" (Claude) a „kezekről" (homokozók); session replay → TTFT 60-90%-kal gyorsabb |
| **OpenHands (All Hands AI)** | Production, open-source (67k+ csillag) | Teljes ökoszisztéma, Seed funding. SDK + event-driven state + sandbox-execution + context condensation. MLSys 2026-on publikált architektúra |
| **Devin (Cognition Labs)** | Zárt forrás, legelőrehaladottabb „turnkey" autonóm SWE | Dedikált **Otterlink hypervisor** + custom **SWE-1.x** modellek. Devin 2.2: böngészős workspace + Jira/Linear integráció + ütemezett futtatás + Slack-csapatkommunikáció = teljes digitális munkatárs |
| **Manus** | Production, general-purpose browser operator | Fejlesztő-fókuszú Devin/OpenHands ellentéte: laikus felhasználóknak prezentáció/weblap/dizájn. Validált business case |

**Academic / Kutatási stage:**

- **ChatDev + a hagyományos „GroupChat" architektúrák** — akadémiai, **productból kiszorult**. A 2023-as peer-to-peer „CEO ↔ programozó ↔ tesztelő közös chat" modell a 2026-os benchmarkokon és költségelemzéseken **hatalmas context-bleed-et és kezelhetetlen token-költséget** mutatott. A modern ipari platformok (új AutoGen, Anthropic SDK) ezt teljesen elvetették az „Orchestrator + izolált némán dolgozó subagent" modell javára. Kutatási papírokon hasznos (szoftverfejlesztési szimuláció), dollár/teljesítmény alapon szuboptimális.

### Q3 — Cost-sensitive trade-off (3 budget-tier)

A multi-agent rendszerek átlagosan **15× több token**-t használnak mint a single-agent chat. Egyetlen fejlesztőre, költség­érzékeny környezetben a teljes elméleti architektúra (Planner + Executor + Critic + Summarizer + Red-team + Enterprise framework) fenntarthatatlan.

**Tier 1: Ultra-Low Budget ($50 / hónap)** — Cline (open-source), Sculptor (free, konténerizált), Windsurf ($15-30/hó), „zero markup" API-billing.

*Mit vágunk le:*
- **Teljes multi-agent delegáció (subagentek)** — OpenHands útmutató: az első verziókban kihagyni; egy ágens jó kontextus-sűrítővel (condenser) is meglepően hosszú feladatot kezel
- **Critic / Red-team** — duplázza a tokenhasználatot
- **Frontier modellek** — helyettük open-weights pl. **MiniMax M2.5** (Claude Sonnet teljesítmény ~tizedáron)
- **LLM Summarizer** — helyette **truncate** condenser (csak prompt + legutóbbi lépések)

**Tier 2: Mid-Tier Budget ($200 / hónap)** — Cursor Ultra, Claude Code Max, Intent Max (450k kredit).

*Mit vágunk le:*
- **Peer-to-peer / GroupChat** — szigorúan kerülni, csak akkor bevezetni ha az esetek >5%-ában tényleg kell
- **Folyamatos csúcsmodell-használat** — **Multi-Provider LLM Gateway** (OmniRoute) bevezetése = 40-60% tokenköltség-csökkentés (rutinra olcsó, tervezésre frontier)

*Megtartjuk:*
- **P2 minta (Orchestrator + Subagent)** — Planner felbontja, Executor subagentek elszigetelten futnak, csak **summary string** vissza (NEM transzkript)

**Tier 3: High-Tier Budget ($500 / hónap)** — Devin Team ($500/hó, 250 ACU). Teljes architektúra megengedhető (Coordinator + Specialist + Verifier).

*Mit vágunk le:*
- **Strukturálatlan rajok** — egymással egyezkedő ágensek = figyelemelterelés és pazarlás (Cognition explicit megállapítása)
- **Több szálon futó write actions** — Planner/Executor/Critic párhuzamos olvasás OK, **írást szigorúan egyszálúsítani** (architektúra-fragmentálódás elkerülése)

#### Mikor maradj inkább SINGLE-AGENT?

A 2026-os akadémiai kutatások (Tran & Kiela, OneFlow) bizonyították: **azonos token-budget mellett a single-agent rendszerek információ-hatékonyabbak**, gyakran elérik vagy verik a multi-agent rendszereket multi-hop reasoning-ben. **Kötelező single-agent:**

1. **Szekvenciális feladatok** — „csináld ezt, majd az eredmény alapján a következőt" → a delegáció csak overhead; jobb kontextus-engineering kell
2. **Közös állapot (shared state)** — folyamatosan ugyanazt a megosztott memóriát érintő feladatra a multi-agent többet árt
3. **Szoros költségkeretek (fixed reasoning-token budget)** — a teljesítmény-variancia 80%-át a tokenek száma magyarázza; szűkös keretnél a jól-promptolt, nagyobb iterációszámú single-agent verheti a multi-agent láncot

**Multi-agent CSAK akkor indokolt, ha:** jól párhuzamosítható + olvasás-intenzív munka (parallelizable read-heavy), VAGY különböző eszközök/adatbázisok biztonsági izolációja szükséges (disjoint tool domains), VAGY single-agent plafont ért egy long-horizon feladatban (akkor pl. CAID-szerű delegációra váltani).

### Phase A+ fő tanulság

A 2026 ipari mainstream **megegyezik** abban hogy a multi-agent világ NEM a sok-ágenses chatháló (GroupChat zsákutca) hanem **kemény „Orchestrator + isolated subagent + summary-only return + filesystem-as-state"** + cost-aware **OmniRoute modell-mix**. Az Obsidian-vault paradigmánk (Markdown = single source of truth, 11.11 = orchestrator-protocol, 280-skill = `SKILL.md` library) **strukturálisan illeszkedik** erre — az MVP útja: Sprint 1 AgentSkills+MCP-vel a single-agent rendberakása, Sprint 2 LangGraph 2.0 P2 minta + summary-return, Sprint 3 párhuzamos fan-out + Stuck Detection + Critic safeguard.

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható:

```bash
notebooklm generate audio -n c7eba59a-a42b-4bf4-8fb2-30c13806eb64
```

> A generálás indítva ennek a cikknek a megírásakor — háttérben fut.

## Akció-pontok ehhez a tengelyhez

- [ ] Audio overview generálás befejezése + letöltés
- [ ] Phase B sprint-bontás: 4 sprint a MVP-re (workflow → parallelizáció → critic → tracing)
- [ ] Framework-döntés: saját Anthropic SDK vs LangGraph — POC mindkettővel egy egyszerű vault-szerkesztési feladaton (pl. „2 párhuzamos research-subagent + critic")
- [ ] `multi-agent-vault-critic` skill-prototípus
- [ ] „Direct to filesystem" minta dokumentálása + bekötése a meglévő 11.11-protokollba (formalizált handoff)
- [ ] Token-budget per-multi-agent-session bevezetése (5.1 robbanás-megelőzés)
- [ ] A 2 YouTube-source error vizsgálata + alternatív források beszerzése (retry pending)

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
- [[10-raw/2026-05-12 — Superintelligence research source pool]]
- [[11-wiki/sv-01-memory-architecture]] — kapcsolódik a context-rot megoldásokhoz (külső memória)
- [[11-wiki/Crystallization-protocol]] — a summarizer-agent szerepköre épülhet rá
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — alapminta, ami a több-párhuzamos-agent-runtime irányába skálázódik
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[langgraph-durable-stateful-agent-orchestration-pattern]] (sem-rokon, score=0.62)
- [[agent-vault-setup-playbook]] (sem-rokon, score=0.59)
## NotebookLM-konverzáció

- **Notebook ID:** `c7eba59a-a42b-4bf4-8fb2-30c13806eb64`
- **Conversation ID:** `a6bf8cf5-01ea-4914-8b5c-c28161b2c812`
- **Források:** **737** (Phase A 14 → Phase A+ +723 deep-research bővítéssel, 589 ready / 14 error / többi pending)
- **Kérdések:** 7/7 Phase A + 3/3 Phase A+ deep-research (validation + cost-tier)
- **Audio overview:** generálás folyamatban (háttér-task)

### Forrás-pool

**Foundational arXiv:**
- `2304.03442` — Generative Agents: Interactive Simulacra of Human Behavior (Park et al. 2023, Stanford)
- `2307.07924` — ChatDev: Communicative Agents for Software Development (Qian et al. 2023)
- `2308.08155` — AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation (Microsoft 2023)

**Framework docs:**
- CrewAI introduction (docs.crewai.com)
- AutoGen (microsoft.github.io/autogen)
- LangGraph (langchain-ai.github.io/langgraph) + blog
- OpenHands (github.com/All-Hands-AI/OpenHands)

**Production breakdowns:**
- Anthropic: Building Effective Agents
- Anthropic: How we built our multi-agent research system
- Cognition: Introducing Devin
- Manus: hands-on AI

**YouTube:**
- Andrew Ng — AI Agentic Workflows And Their Potential For Driving AI Progress
- LangChain — Conceptual Guide: Multi Agent Architectures

**Add-research bővítések (web):**
- „multi-agent LLM orchestration framework 2026 production patterns" — 10 source (Beam.ai, InfoQ Google patterns, towardsagenticai, gurusup Best Frameworks 2026, AutoGen vs CrewAI vs LangGraph comparison, Indium state persistence, Braintrust observability, Okta security stb.)
- „Devin Manus OpenHands agentic coding architecture deep dive 2025" — 10 source (LocalAIMaster CrewAI setup, MCP context-enhancing, BAMAS budget-aware, efficient LLM serving stb.)
