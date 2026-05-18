---
name: SV-1 Memory architecture
type: wiki
tags: ["#type/wiki", "agi", "memory", "rag", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: phase-a-plus-done
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: e2e31ae8-fa81-4775-9cd7-2cc43b441d69
---

# SV-1 — Memory architecture

A 8-tengelyű szuperintelligens-vault evolúciós research első cikke. **Kérdés:** hogyan lehet egy LLM-agent memóriáját úgy strukturálni, hogy ne legyen lapos fájl-keresés, hanem hierarchikus, asszociatív, és a használat során tanuljon-fejlődjön.

> **Status:** Phase A teljes — 7/7 kérdés válaszolva. NotebookLM-források: 6 + 1 add-research-bővítés (YouTube). Audio overview és tech-stack-deep-dive Phase A+ folytatáskor.

## 1. A tengely magja

Az LLM-agentek kontextusában a **memóriarchitektúra** egy olyan átfogó rendszer, amely kiterjeszti a nyelvi modellek korlátozott kontextusablakát, lehetővé téve számukra az információk hosszú távú tárolását, dinamikus visszakeresését és a múltbeli eseményekből való tanulást. A Mem0 „univerzális, önfejlesztő memóriarétegként" írja le ezt a rendszert, míg a Letta egy „**memory-first**" (állapottartó) agentként határozza meg, amely a tapasztalataiból tanulva folyamatosan fejlődik. A Generative Agents kutatás rávilágít, hogy egy ilyen architektúra a természetes nyelven rögzített tapasztalatok teljes tárházát jelenti, amelyből az agent képes a múltbeli eseményekre támaszkodva megtervezni a jövőbeli viselkedését.

### Kulcs-architektúra-szintek

A fejlett memória-architektúrák különböző szintekre bontják az információkezelést:

| Szint | Mit tárol | Példa-implementáció |
|---|---|---|
| **Working memory** | Aktív kontextus, aktuális task | MemGPT virtual context (aktív szint) |
| **Episodic memory** | Nyers események, megfigyelések, dialógusok | Generative Agents memory-stream |
| **Semantic memory** | Magas-szintű reflexiók, absztrakciók, ok-okozat | Generative Agents reflection, RAPTOR fa-csomópontok, GraphRAG entity-graph |

### A memory-hierarchia szerepe

A **memory-hierarchy** kritikus szerepe az erőforrások hatékony optimalizálása és a kontextus intelligens áramoltatása. A **MemGPT** a hagyományos operációs rendszerek hierarchikus memóriakezeléséből merítve bevezeti a „**virtuális kontextuskezelés**" (virtual context management) fogalmát, amely az adatokat az aktív (gyors) és a háttérben lévő (lassú) memóriaszintek között mozgatja. Ez a hierarchikus irányítás teszi lehetővé, hogy az agent intelligensen menedzselje a különböző memóriarétegeket az LLM korlátozott kontextusablakán belül.

## 2. Kanonikus megközelítések (5 fő minta)

### Generative Agents (Park et al. 2023, Stanford)
- **Mechanizmus:** Természetes nyelven rögzíti az összes megfigyelést mint **memory-stream**; idővel a nyers emlékeket **magasabb szintű reflexiókká** szintetizálja; dinamikusan visszakeresi a tervezéshez.
- **Kulcs-újdonság:** A reflection-loop — automatikusan időről időre az agent „elgondolkodik" a memóriáin és absztrakciókat ír.

### MemGPT (Packer et al. 2023, Berkeley)
- **Mechanizmus:** OS-szerű virtuális memory-hierarchia (fast=context-window, slow=archival storage), **interrupts** a kontroll-flow-hoz. Az agent maga dönti el mit page-eljen be/ki.
- **Kulcs-újdonság:** Az LLM mint OS-kernel mintázat — paging primitívek a prompt-kontextusra.

### RAPTOR (Sarthi et al. 2024, Stanford)
- **Mechanizmus:** **Recursive abstractive processing** — alulról építkezve rekurzív klaszterezés + összefoglalás, **fa-struktúrájú memory**. Az agent inference során a fa különböző szintjeiről kér adatot.
- **Kulcs-újdonság:** Multi-resolution retrieval — egyszerre lehet részlet és nagy-kép.

### GraphRAG (Edge et al. 2024, Microsoft Research)
- **Mechanizmus:** LLM kivonja az **entitásokat + relációkat** a forrásdokumentumokból → entity knowledge graph + **community summaries** (klaszter-szintű összefoglalók). Kérdés esetén részválaszok → globális szintézis.
- **Kulcs-újdonság:** Skálázhatóság 1M-token korpuszra; „globális kérdések" (pl. „mik a fő témák az adathalmazban?") amit a klasszikus RAG nem old meg.

### Mem0 (open-source, 2024)
- **Mechanizmus:** **Self-improving memory layer** — API/CLI réteg fölött menedzseli a memóriát; integrálódik LangChain/CrewAI keretrendszerekkel. Cloud és self-hosted variáns is van.
- **Kulcs-újdonság:** Plug-and-play memory szolgáltatás, nem kell saját architektúrát építeni.

### Letta (Berkeley, MemGPT-spinoff)
- **Mechanizmus:** **Memory-first agent** keretrendszer — sleep-time-compute (az agent inaktív periódusban tanul-frissít), perzisztens állapotok kódoló agentekhez, autonóm asszisztensekhez.
- **Kulcs-újdonság:** A memory-first design alapelve — az architektúra az állapotból indul, nem a prompt-templatesből.

## 3. Tech-stack opciók 2026-ban

> **⚠️ Forrás-korlátozás:** A 6 forrás (MemGPT, GraphRAG, Generative Agents, RAPTOR, Letta, Mem0) **nem fedi le** a tech-stack-tradeoff-okat (Chroma, Qdrant, Weaviate, Pinecone, Neo4j stb.). Ehhez a Q3 válaszban a NotebookLM **web-search-bővítést ajánlott fel** — ezt a következő session-ben aktiváljuk a `notebooklm source add-research` paranccsal. Az alábbi az eddigi források alapján:

### Managed memory-szolgáltatások (forrás-szintű)

| Eszköz | Tradeoff | Mire jó |
|---|---|---|
| **Mem0 Cloud** | Production-scale infra, percek alatt üzembe helyezhető, alacsony setup-komplexitás. Konkrét árazás/latency NEM a forrásban. | Gyors integráció saját infra nélkül; „univerzális, önfejlesztő memóriaréteg" mintára |
| **Letta Cloud** | Desktop/CLI + cloud deploy. Skálázhatóság/ár nincs konkrét adatban. | Personalized memory-first agentek, kódoló asszisztensek, autonóm digitális alkalmazottak, AI társak |
| **Microsoft GraphRAG** | Kétlépcsős setup (graph-build + query) magasabb komplexitás. Skálázhatóság: 1M-token korpusz. | Globális, átfogó kérdések teljes korpuszra; nem pont-keresés |

### Lokális vector-store-ok és graph-store-ok

> Hiányzó forrás-fedettség — a következő research-iterációban a `notebooklm source add-research` web-search-szel kiegészítjük:
> - **Lokális vector-store:** Chroma, Qdrant, Weaviate, FAISS, pgvector
> - **Managed vector:** Pinecone, MongoDB Atlas Vector
> - **Graph-store:** Neo4j, Memgraph
> - **Hybrid:** ElasticSearch + vector-plugin, PostgreSQL + pgvector + Apache AGE

Ezekre a Phase A folytatásban frissítem a táblát.

## 4. Friss áttörések 2024-2026

A 6 forrás alapján 3 megkérdőjelezhetetlen mérföldkő, időtengelyen sorrendben:

### 2023. október — MemGPT és a virtuális kontextus
A 2023-10-12-én publikált MemGPT bevezette a **virtual context management** koncepcióját. A hagyományos operációs rendszerek hierarchikus memóriájából inspirálódva az adatokat a gyors (context-window) és lassú (archival) memóriaszintek között mozgatja. Ez nyitotta meg az utat olyan multi-session konverzációs agentekhez, amelyek hosszú távú interakciók során képesek emlékezni, reflektálni és dinamikusan fejlődni.

### 2024. január — RAPTOR és a többszintű visszakeresés
A 2024-01-31-én publikált RAPTOR rekurzív megközelítéssel meghaladta a korábbi RAG módszereket, amik csak rövid, összefüggő chunk-okat tudtak visszakeresni. A rendszer alulról építkezve fa-struktúrát épít — szövegdarabokat embedding-eli, klaszterezi és összefoglalja. Inference közben **különböző absztrakciós szintekről** képes adatot visszakeresni → holisztikus megértés, kimagasló eredmény több-lépéses érvelést igénylő feladatokon.

### 2024. április — GraphRAG és a community summaries skálázhatósága
A 2024-04-24-én bemutatott GraphRAG a **globális kérdésekre** (pl. „Mik a fő témák az adathalmazban?") adott forradalmi megoldást — amit a korábbi RAG rendszerek nem tudtak kezelni. A modell entitás-tudásgráfot épít, majd előre **community summaries**-t generál szorosan kapcsolódó entitáscsoportokhoz. Bizonyítottan skálázható **1M-token nagyságrendű** adathalmazokra is, érdemben felülmúlva a klasszikus RAG-ot átfogóságban és diverzitásban.

> **NB:** A 6 forrásból a Claude/Gemini long-context vs RAG benchmarkok, a Letta sleep-time-compute mechanikája, és a 2026 H1 áttörések **kifejezetten kimaradtak**. Ezekhez Phase A+ web-search-bővítés szükséges (a `notebooklm source add-research` futtatva, egy YouTube találattal — *Markdown Memory? Outgrow It Faster*).

## 5. Failure-modes és limitációk

A 6 forrás **csak korlátozottan** tárgyalja a failure-mode-okat — a hallucináció-amplifikáció, költség, privacy/leakage, cold-start és stale memory mint **dedikált** problémák kifejezetten kimaradtak. A források explicit foglalkozta-tárgyalta egyetlen failure-mode-ja:

### Retrieval-irrelevancy (a klasszikus, dokumentált failure-mode)

- **GraphRAG diagnózisa:** A hagyományos RAG-rendszerek **kifejezetten elbuknak** globális kérdéseknél (egy teljes szövegkorpuszra vonatkozó kérdésnél). A klasszikus visszakeresés szuboptimális, mert a felhasználói szándék valójában **query-focused summarization**, nem konkrét tények explicit visszakeresése. A GraphRAG az entitás-tudásgráfokkal hídalja át.
- **RAPTOR diagnózisa:** A legtöbb létező visszakeresési módszer **kizárólag rövid, összefüggő chunk-okat** emel ki — ez korlátozza a dokumentum átfogó kontextusának holisztikus megértését.
- **MemGPT diagnózisa:** A modern LLM-ek korlátozott kontextusablaka **súlyosan hátráltatja** a teljesítményt multi-session csevegéseknél és hosszú-dokumentum-elemzésnél → szükségszerű a memória-szintek intelligens, hierarchikus kezelése.

### Érintőlegesen említett

- **Stale memory:** A RAPTOR megjegyzi, hogy a retrieval-augmented modellek általánosságban jobban alkalmazkodnak a „világ állapotának változásaihoz" mint a statikus tudású alap-modellek — de dedikált failure-mode-ként nem tárgyalja.
- **Privacy:** A Letta dokumentációja megemlíti a Permissions és Secrets menedzsmentjét, de a leakage / cross-user buktatókat nem fejti ki.

**Phase A insight:** A teljes failure-mode-kép összerakásához **web-search-bővítés szükséges** Phase A+-ban (privacy papers, cost-benchmarks, hallucination-RLAIF tanulmányok).

## 6. Implementációs lépések a Peti-vault kontextusban

> **NotebookLM-megjegyzés:** A 6 forrás egyike sem tartalmazza az Obsidian-Markdown-Johnny-Decimal-vault integrációs lépéseit, kódolási útmutatókat, vagy mappa-szintű vector-store-elhelyezést. Az alábbi roadmap **szigorúan a forrásokban szereplő elméleti mechanizmusokra támaszkodva** illeszti rá a MemGPT + GraphRAG + Generative-Agents architektúrát a Peti-vault-struktúrára.

### 6-lépéses elméleti roadmap

**1. lépés — Nyers megfigyelések (Observations) rögzítése.**
- *Forrás:* A Generative Agents minden tapasztalatot természetes nyelven, „teljes történetként" rögzít.
- *Vault-implementáció:* Minden új user-interakció, parancs, session-protokoll-esemény **immutable** raw-ként kerüljön a `10-raw/` és `08-Sessions/` mappákba.

**2. lépés — Entitás-tudásgráf generálása a statikus tudásból.**
- *Forrás:* GraphRAG első lépése: LLM-mel entitás-tudásgráf-derivatúm a forrásdokumentumokból.
- *Vault-implementáció:* Indexelő script feldolgozza az evergreen tartalmakat (`11-wiki/`) és az alap-szabályokat (`00-Meta/`); kinyeri az entitásokat és kapcsolatokat. *(A háttér-DB-elhelyezést a forrás nem részletezi — Phase B-ben dönteni.)*

**3. lépés — Community summaries előgenerálása.**
- *Forrás:* GraphRAG: a gráf felépülése után előre legenerált klaszter-összefoglalók szorosan kapcsolódó entitáscsoportokhoz.
- *Vault-implementáció:* Periodikusan futtatott job az érett tudásbázison (`11-wiki/`, `02-Projects/`). A magas-szintű tematikus összefoglalók (pl. „Mik a projekt fő kihívásai?") indexbe bekötve → drasztikusan javított globális-lekérdezési pontosság.

**4. lépés — Reflection-loop futtatása a memórián.**
- *Forrás:* Generative Agents: az idővel a nyers emlékek „magasabb-szintű reflexiókká" szintetizálódnak, ezek vezérlik a viselkedéstervezést.
- *Vault-implementáció:* Aszinkron folyamat elemzi a `08-Sessions/` és `10-raw/` tartalmát, összefüggéseket keres a múltbeli munkamenetekből. A reflexiók a `05-Memory/` vagy `07-Decisions/` mappába íródnak.

**5. lépés — Virtual context kezelés és interrupts.**
- *Forrás:* MemGPT: gyors-lassú memóriaszintek közötti adatmozgatás + interrupts a control flow-hoz; Mem0/Letta CLI-toolokat ad hozzá.
- *Vault-implementáció:* Az agent promptjában elkülönített „gyors" memória (aktuális `08-Sessions/`) és „lassú" memória (`11-wiki/` + `05-Memory/` reflexiók). Köztes control-flow kód (Letta API/CLI-mintára) tölti be a megfelelő adatelemeket on-demand, vagy megszakítja a folyamatot frissítéshez.

**6. lépés — Dinamikus visszakeresés aktív munkamenetben.**
- *Forrás:* Generative Agents: dinamikus retrieval kérdésre; GraphRAG: globális kérdéshez community summaries → részválaszok → végső szintézis.
- *Vault-implementáció:* Ha a kérdés átfogó (pl. `02-Projects/` állapot-összesítő), a 3. lépés community-summaries-jét hívja be. Ha specifikus döntés/viselkedés, az 1+4 lépés nyers emlékeit és reflexióit keresi vissza.

**Részletes sprint-bontás Phase B-ben** — tech-stack-döntés (Chroma vs Qdrant vs pgvector), kód-skeleton, acceptance criteria.

## 7. Mit kell tovább kutatni?

A 6 forrás átfogó képet ad a retrieval-alapú (RAG/in-context) és agent-szintű (szöveges) memóriakezelésről, de a haladó kutatási irányok **teljesen kimaradtak** — ezek a Phase A+ keretében külön research-iterációt igényelnek:

### 1. Memory fine-tuning vs in-context + LoRA-adapterek
A bemutatott architektúrák (RAPTOR fa, GraphRAG entity-graph, Mem0 réteg, MemGPT hierarchia) **mind kizárólag in-context (prompt-alapú) memóriabővítésre épülnek**. A modell-súly-frissítés (memory-fine-tuning), és a paraméter-hatékony módszerek (memóriaspecifikus LoRA-adapterek) nem szerepelnek. A tudás súlyokba kódolt és dinamikus visszakeresett fúziója nyitott kérdés.

### 2. Multi-modal memory
A források szigorúan szöveges adatokra koncentrálnak — a Generative Agents kifejezetten hangsúlyozza a „természetes nyelvű" tárolást. A vizuális, hangalapú vagy térbeli memóriák rögzítése-szintetizálása-visszakeresése (multi-modal memory) **egyetlen forrásban sem jelenik meg**.

### 3. Federated memory és elosztott adatvédelem
A Mem0 saját-hosztolás-támogatása és a Letta Permissions/Secrets-menedzsmentje csak az adatok feletti kontrollt érinti. A **federated memory** (több agent / user között megosztott memória, kriptográfiailag vagy federated-learning-gel védett privacy-vel) nem szerepel.

### 4. Hardver-szintű optimalizációk (KV cache, prefill caching)
A MemGPT csak szoftver-architekturális szinten mozgatja a tokeneket. A hosszú-kontextus költség-hatékony futtatáshoz elengedhetetlen **KV cache optimalizáció** és **prefill caching** nem szerepel.

### 5. Memory + Reasoning mélyebb kombinációja
A források érintik a komplex feladatokat (RAPTOR multi-step QA, Generative Agents reflexió-tervezés), de a **modern aktív következtetési** technikák (chain-of-thought közben iteratív + belső memory-hívás hipotézis-teszteléshez, anélkül hogy csak külső kontextusként kapná) **mélyebb mechanizmusait nem részletezik**.

### Phase A+ priorizálás
Ezekhez a Phase A+ web-search-bővítés (`notebooklm source add-research`) ÉS célzott YouTube-cherry-pick (Yannic Kilcher LoRA-papers, AI Explained federated-learning, Karpathy hardware-talks) szükséges. Phase B-ben a Memory-implementációs-sprint csak a #1-3 témákra reaktív (a #4 hardware és #5 reasoning-mély-kombináció a Phase C-be).

## Phase A+ bővítés (2026-05-12 deep-research)

A Phase A 6 forrását kiegészítettük 4 célzott deep-research-iterációval, amelyek a Phase A-ban explicit hiányzó témákat fedik le: long-context vs RAG production benchmark, Letta sleep-time-compute mechanika, 2026-os vektor-DB pénzügyi-skálázási benchmark, valamint privacy-leakage és hallucination amplification a perzisztens memóriában.

### Új források betöltve

A 4 deep-research-task **243 új forrás-URL-t** hozott be (kezdeti 6 → 249 összesen). A 4 témakör eloszlása nagyjából egyenletes:

- **Long-context vs RAG** (Sonnet 4 / Gemini 1M-2M token vs hibrid RAG production benchmarkok)
- **Letta sleep-time-compute** (subconscious agent, async memory-consolidation, out-of-band processing)
- **Vector DB 2026** (Chroma / Qdrant / Weaviate / Pinecone / Memgraph / pgvector / Milvus / Turso-sqlite-vec / Turbopuffer pénzügyi és skálázási adatok)
- **Privacy / hallucination** (cross-session poisoning, embedding-leakage, hibrid keresés mint zaj-szűrő)

A források között szerepel a Letta saját dokumentációja, a Mem0 LOCOMO-benchmark publikációja, a Qdrant pgvector-tradeoff blogposztja, vektor-DB pricing-oldalak (Pinecone, Weaviate, Turbopuffer), és több arXiv-paper a memóriarendszerek biztonságáról.

### Q1 — Optimális 3-elem kombináció

A források alapján a meglévő Obsidian-Markdown agent-vault esetén **3 architekturális elem kombinációja** ad a legtöbb értéket, sorrendben építve:

**1. elem — A kanonikus Markdown-tár és a származtatott vektor-index szigorú szétválasztása.** A vektor-adatbázis sosem lehet az "igazság forrása" (truth layer), csupán egy újraépíthető "gyorsítóréteg" (materialized view) [1-3]. A `08-Sessions/` és `10-raw/` a nyers event-log, a `11-wiki/` + `02-Projects/` + `05-Memory/` a strukturált tudásbázis, a vektor-index pedig egy content-hash-elt, *teljesen újragenerálható* másolat. Ha a vektor-DB korrumpálódik, törölhető és újraépíthető — a primer tudás megmarad Markdown-ban (provenance + git-history) [2, 3].

**2. elem — Lokális, beágyazott (embedded) vektor-adatbázis + hibrid keresés.** A tech-stack gerince a **Chroma** embedded módban, ideális "local-first" fejlesztéshez minimális infra-igénnyel [4, 5]. Alternatíva: **Turso / sqlite-vec** per-user izolációra és edge-deployra [6, 7]. A RAG-hallucinációk és az embedding-poisoning ellen *kötelező* a **hibrid keresés** (BM25 lexikális + szemantikus vektor együtt) — drasztikusan szűri az irreleváns vagy manipulatív kontextust ("switch to hybrid this quarter" [8, 9]). Opcionálisan **VOTE-RAG** generálás előtt: több független lekérdezés-aggregálás torzítás-csökkentésre [16, 17].

**3. elem — Aszinkron "tudatalatti" memory-consolidation (Letta-stílusú async ágens).** A 11.11 session-protokoll teljes szövegét NEM zsúfoljuk egy hosszú kontextusba; helyette egy háttér-script éjszaka vagy session-zárás után olvassa be a `08-Sessions/` új fájljait, LLM-mel kivonja a tartós tudást (tények, döntések, preferenciák), és **emberi promotion-gating** után írja be a megfelelő `11-wiki/` vagy `05-Memory/` Markdown fájlba [10-13]. NEM teljes-chat-vektorizálás (ez "architectural drift"-hez vezet [18]) — szelektív LLM-szintézis.

**Implementációs sorrend:** 1. fázis (adat-réteg-szeparáció + content-hash), 2. fázis (Chroma embedded + BM25 hibrid retrieval), 3. fázis (Letta-mintájú async promotion-pipeline). Az 1. → 2. → 3. sorrend a kritikus, mert a 3. nem működik a 2. nélkül, a 2. pedig értelmetlen a kanonikus-source-separation hiányában.

### Q2 — Production-ready vs akadémiai

A források éles határvonalat húznak a production-ready és academic stage között:

| Technológia | Kategória | Forrás-bizonyíték |
|---|---|---|
| **Letta** | Production-ready | "Ugyanezeknél a produkciós rendszereknél figyelhetők meg, mint a Claude Code, a Cursor, a Letta, az AWS AgentCore" [1]; subconscious agent out-of-band memory-frissítéssel [2] |
| **Mem0** | Production-ready | "Production-scale infrastructure" [3]; konkrét metrika: "91%-os késleltetés-csökkenés és 90%+ token-cost savings a LOCOMO benchmarkon" [4] |
| **Pinecone** | Production-ready | "Battle-tested in production" [5]; pricing: 100k vektorig ingyenes, $70/hó alacsony serverless, $500-2500/hó közepes, $10k+/hó nagy production [6] |
| **Qdrant** | Production-ready | 10M-1B vektor production-ready [7]; Rust-engine + quantization "4x memóriacsökkentés" [8]; 100M+ vektornál self-hosted "5-10x gazdaságosabb" mint managed [6] |
| **RAPTOR** | Akadémiai | Csak arXiv:2401.18059, kontrollált kísérletek QuALITY benchmarkon "20% abszolút pontosságnövekedés" — nincs production-metrika [9] |
| **MemGPT** | Akadémiai (Letta-ban folytatódik) | arXiv:2310.08560, "képességek és hatékonyság — nem irányítás — elsődleges céljával tervezve" [4, 10]; production-utódja a Letta |
| **GraphRAG** | Akadémiai | Microsoft-paper "From Local to Global", UltraDomain benchmark — nincs $/performance metrika [11, 12] |
| **Chroma** | MVP / prototyping | "Leggyorsabb út az ötlettől a prototípusig", "nem termelési léptékre tervezve", "10M vektor alatt prototípusra" — csapatok Qdrant/Milvusra váltanak skálázáskor [13, 14] |
| **Memgraph** | Nincs forrásban | A források NEM fedik le — kérés benne volt, de NotebookLM explicit jelezte hogy "Memgraph egyáltalán nem szerepel a forrásokban" |

A különbség lényege: a production-ready kategória rendelkezik konkrét $/performance metrikákkal és működő business case-ekkel (LOCOMO-benchmark, pricing-tier-ek, deployed-by-Claude-Code-and-Cursor referenciák), míg az akadémiai stage csak kontrollált benchmark-kísérleteket mutat fel (QuALITY, UltraDomain) production-deployment nélkül.

### Q3 — Cost-sensitive trade-off

A források alapján 1 fejlesztős, költségérzékeny környezetben az alábbi vágások szükségesek:

**Tier 1 — $50/hó (ultra-cost / prototípus).** Stack: **ChromaDB embedded** (ingyenes) [1, 2] vagy **Qdrant 1GB free-forever** [3, 4] vagy **Turso/sqlite-vec** $5/hó per-user izolációval [5, 6]. **Levágva:** (a) a Letta-stílusú async memory-consolidation — túl sok LLM-tokent égetne [7, 8]; (b) menedzselt cloud vektor-DB-k (Pinecone serverless ~$70/hó, Weaviate $25/hó-tól indul [9-11]). **Kompromisszum:** Chromán nincs natív hibrid keresés (csak experimental [14, 15]), aszinkron consolidation nélkül a rendszer hajlamos "context drift"-re (felhalmozódás → drágább inferencia + romló pontosság) [16, 17]. Skálázási plafon ~10M vektor [18, 19].

**Tier 2 — $200/hó (közepes skála).** Stack: **Turbopuffer** $64/hó-tól [20, 21] vagy **Qdrant Cloud** $25-100/hó [22, 23] vagy **Pinecone Serverless** ~$70/hó [9, 24]. **Levágva:** (a) dedikált multi-pod infra (Weaviate Cloud / Pinecone-pod $150-400/hó [22, 23]); (b) "enterprise" skála (Zilliz Cloud [25, 26]). **Kompromisszum:** az async memory-consolidation **bekapcsolható**, de szigorú **layer-based token-budget** kell [27, 28] — a memory-promotion *naponta egyszer batch*-ben fut (NEM session-zárásonként), hogy a $130-170 maradék fedezze az LLM-API-t. Pinecone esetén vendor-lock-in kockázat [29, 30].

**Tier 3 — $500/hó (production / teljes funkcionalitás 1 fejlesztőnek).** Stack: **Weaviate Cloud** $150-300/hó natív hibrid kereséssel [22, 31] vagy **Pinecone dedikált pod-ok** $200-400/hó "zero ops"-szal [22, 32, 33]. **Levágva:** **Milvus self-hosted** — bár 100M+ vektoron 5-10x olcsóbb [34-36], a Kubernetes-alapú DevOps-overhead 1 fejlesztőnek túl sok [34, 37, 38]. **Kompromisszum:** lemondunk az infra-feletti teljes kontrollról és az extrém költséghatékonyságról a fejlesztői-idő-megtakarításért [39, 40]. A maradék $200-300 elegendő a teljes Letta-stílusú async-szintézisre, GraphRAG entitás-gráf-frissítésre és BM25+vektor hibrid keresésre lassulás nélkül [31, 41, 42].

A Peti-vault jelenlegi mérete (~240 fájl) bőven a Tier 1 sweet-spotjában van — a Chroma embedded + napi-egyszer batch-promotion realisztikus kiindulás, Tier 2-re csak akkor lépünk, ha a Letta-stílusú folyamatos async-consolidation reálisan szükséges lesz.

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható. Phase A végén futtatjuk:

```bash
notebooklm generate audio -n e2e31ae8-fa81-4775-9cd7-2cc43b441d69
```

## Akció-pontok ehhez a tengelyhez

- [ ] Phase A Q4-Q7 lefuttatása (NotebookLM, ~30-45 perc)
- [ ] `notebooklm source add-research` futtatás a tech-stack-bővítéshez (Chroma/Pinecone/Neo4j konkrét adatok)
- [ ] Audio overview generálás + letöltés
- [ ] Phase B sprint-bontás: 4-5 sprint a memory-upgrade-re a vault-ban

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
- [[10-raw/2026-05-12 — Superintelligence research source pool]]
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a vault jelenlegi memory-struktúrájának háttere
- [[11-wiki/Crystallization-protocol]] — a #5 tengely (auto-crystallization) kapcsolata

## NotebookLM-konverzáció

- **Notebook ID:** `e2e31ae8-fa81-4775-9cd7-2cc43b441d69`
- **Conversation ID:** `25fabc06-18b9-4df5-910e-1196b6ff04b7`
- **Források:** 6 (5 ready, 1 retry — Letta)
- **Kérdések:** 3/7 válaszolva
