---
name: SV-6 World-model / knowledge graph
type: wiki
tags: ["#type/wiki", "agi", "knowledge-graph", "graphrag", "world-model", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: done
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: 82e9046d-a60f-4a6e-9165-dedadc8fd591
---

# SV-6 — World-model / knowledge graph

A 8-tengelyű szuperintelligens-vault evolúciós research hatodik cikke. **Kérdés:** hogyan lehet egy LLM-agent ismereteit explicit szemantikus graphba szervezni (entitások + relációk + ok-okozat), és milyen hierarchikus reasoning-engine épülhet fölé, hogy szignifikánsan jobb eredményt adjon mint a klasszikus vector-RAG vagy az Obsidian fájl-link-graph.

> **Status:** 7/7 kérdés válaszolva, 17 NotebookLM-forrás (GraphRAG paper + JEPA + HRM + Neo4j/Memgraph docs + Pinecone hybrid + LangChain blog + 2× web-research). Phase A SV-6 ✅ done.

## 1. A tengely magja

Az LLM-agentek kontextusában a "world model" / "knowledge graph" megközelítés magja egy **strukturált, relációs és hierarchikus belső reprezentáció** felépítése, amely az adatok puszta felismerésén túlmutatva lehetővé teszi a rendszer számára a **mélyebb logikai összefüggések megértését, a prediktív következtetést, valamint a több időléptékű, komplex tervezést**.

Három különböző absztrakciós szinten jelenik meg ugyanaz az alapelv:

- **Yann LeCun H-JEPA** (Hierarchical Joint Embedding Predictive Architecture) — látens változós, energia-alapú modell, ami magas szintű absztrakt reprezentációkat jósol, nem token-szintű részleteket. Célja autonóm gépi intelligencia ("Level 5") megbízható belső világmodellekkel.
- **HRM** (Hierarchical Reasoning Model, Sakana 2025) — biológiai ihletésű kétszintű rekurrens architektúra: lassú, absztrakt tervező modul + gyors, részletes számoló modul, **egyetlen forward pass-ban**, explicit CoT-felügyelet nélkül.
- **GraphRAG** (Microsoft 2024) — LLM-mel kinyert entitás-graphból + hierarchikus community-summary-ből épít "világmodellt" az adott korpuszra; lekérdezéskor globális szintézist ad ott, ahol a chunk-szintű vector-RAG koncepcionálisan elbukik.

> **A kontraszt klasszikus vector-RAG-gal:** a vector-RAG csupán **felszíni szemantikai hasonlóság** alapján keres izolált, strukturálatlan chunkokat egy magas dimenziójú térből — ezért **konceptuálisan kudarcot vall** a "pontok összekötésében" (multi-hop reasoning), az aggregációban és a globális, teljes-korpuszt-átfogó kérdésekben. A world-model/knowledge-graph tengely a fekete dobozként működő hasonlóság-keresést egy **strukturált, magyarázható (explainable) és tudatos érvelésre képes architektúrával** váltja fel.

## 2. Kanonikus megközelítések (5 fő minta)

### Microsoft GraphRAG (hierarchikus community summaries + global search)
- **Mechanizmus:** LLM az unstructured korpuszból entitásokat és relációkat von ki egy knowledge-graphba; **Leiden-algoritmus** klaszterezi a graphot hierarchikus communities-be; minden community-re előre legenerál egy summary-t. Query-kor a globális search ezeket a hierarchikus összefoglalókat szintetizálja válaszként.
- **Kulcs-újdonság:** Képessé teszi az LLM-et **teljes adathalmazt átfogó, globális értelemalkotásra és "a pontok összekötésére"** (query-focused summarization) — pont arra, ami a vector-RAG-nak konceptuálisan lehetetlen ("Melyek a fő témák a korpuszomban?").

### LeCun H-JEPA (prediktív, látens világmodellek)
- **Mechanizmus:** Energiaalapú, látens változós modell — ahelyett, hogy pixel/token szinten predikálna, **magas szintű absztrakt reprezentációkat jósol** egy látens térben.
- **Kulcs-újdonság:** Lehetővé teszi a megbízható belső világmodellek elsajátítását, **a logikai érvelést és a komplex, több időléptékű akciósorozatok előretekintő tervezését**. LeCun szerint ez az emberhez hasonló, autonóm gépi intelligencia kritikus alapköve.

### Hierarchical Reasoning Model (HRM, Sakana 2025, arXiv 2506.21734)
- **Mechanizmus:** Kétszintű rekurrens hálózat: **lassú, absztrakt tervező magas-szintű modul** + **gyors, részletes alacsony-szintű modul**, egyetlen forward pass-ban, **CoT explicit felügyelete nélkül**.
- **Kulcs-újdonság:** Biológiai ihletésű, több időskálájú feldolgozás, ami rendkívüli számítási mélységet ér el a CoT törékenysége és extrém adatigénye nélkül. **Mindössze 27M paraméter és 1000 tanítási minta** elég AGI-szintű feladatokra (Sudoku, ARC, labirintus).

### LLM-vezérelt knowledge graph extrakció (Neo4j + LangChain)
- **Mechanizmus:** Az LLM mély kontextuális megértésével (LangChain `LLMGraphTransformer`, LlamaIndex `SchemaLLMPathExtractor`) automatikusan azonosítja a szövegben szereplő **entitásokat és pontos kapcsolataikat**, majd ezeket Neo4j/Memgraph-ba importálja.
- **Kulcs-újdonság:** Kiküszöböli a graph-építés legnehezebb szűk keresztmetszetét — a manuális ontológia-tervezést és adatkinyerést. Strukturált, magyarázható memóriahálózat **automatikusan**, fekete-doboz szövegekből.

### Hibrid Vector + Graph RAG (strukturált + szemantikus lekérdezés)
- **Mechanizmus:** A magas-dimenziós vector-keresést kombinálja explicit, network-alapú graph-bejárással (entitás-detekció után Cypher-query a szomszédság lekérésére).
- **Kulcs-újdonság:** **Tökéletesen ötvözi a vector-keresés szemantikai rugalmasságát a graph precíz, logikai aggregációs képességeivel és nyomon-követhetőségével**. Az agent meg tud válaszolni komplex relációs kérdéseket (pontos darabszámok, közvetett függőségek), ahol a chunk-similarity elkerülhetetlenül elbukik.

## 3. Tech-stack opciók 2026-ban

| Technológia | Mire jó | Setup-komplexitás | Skálázás | LLM-integráció |
|---|---|---|---|---|
| **Neo4j** | Ipari standard, perzisztens, hibrid (vector + graph) RAG production-kész | Közepes/Magas — dedikált DB-instance (Desktop/AuraDB), Cypher-tudás kell | Kiváló — enterprise scale | Erős — mély LangChain/LlamaIndex integráció, saját MCP-server |
| **Memgraph** | Extrém gyors in-memory graph-elemzés, valós-idejű high-throughput RAG | Közepes — Bolt-kompatibilis, gyors Docker-indítás, memória-limit figyelni | Kiváló — performance-optimalizált, natív C/C++/Python (MAGE) | Erős — beépített LangChain toolkit, LlamaIndex, Mem0, LightRAG |
| **Microsoft GraphRAG** | Hierarchikus graph + holisztikus query-focused summarization (Global Search) | Magas — CLI-pipeline, manuális prompt-tuning, erősen OpenAI-API-függő | Korlátozott/Költséges — LLM-indexelés drága és időigényes nagy korpuszra | Beépített, zártabb orchestration; zseniális global-summary-re |
| **LangChain Knowledge Graph** | Gyors app-fejlesztés, auto graph-extraction (`LLMGraphTransformer`), LLM-generálta Cypher (`GraphCypherQAChain`) | Alacsony/Közepes — Python-API, de háttér-DB kell (Neo4j/Memgraph) | DB-függő | Maximális — láncolható tool-okkal, beépített RAG-pipeline-ok |
| **LlamaIndex Property Graphs** | Data-first framework, rugalmas ingestion, `SchemaLLMPathExtractor`, hibrid retriever | Alacsony — tiszta Python-integráció, DB-háttér kell | DB-függő | Nagyon jó — Memgraph vector-search a háttérben |

### Recommendáció ~240 fájlos markdown-vault-ra

A NotebookLM-output **két forgatókönyvet** ajánl:

**1. Holisztikus "Big Picture" / sensemaking → Microsoft GraphRAG**
- Bár az indexing-fázis drága, 240 fájlnál a költség még elfogadható.
- Akkor válaszd, ha **"melyek a top 5 fő téma a jegyzeteimben?"** vagy **"milyen összefüggések vannak a projektjeim között?"** típusú átfogó kérdéseket akarsz feltenni. A Leiden-algoritmusos community-hierarchia és Global Search messze a legjobb minőségű holisztikus összefoglalókat adja.

**2. Interaktív, dinamikus Q&A + gyors építkezés → LlamaIndex + Memgraph (vagy Neo4j Desktop)**
- Memgraph lokálisan, Docker-konténerben, in-memory-villámgyors.
- LlamaIndex `SchemaLLMPathExtractor` végigmegy a Markdown-on és kinyeri az entitásokat; beépített hibrid retriever vector + graph search-szel.
- Lényegesen olcsóbb és kevesebb prompt-tuning, mint MS GraphRAG.

## 4. Friss áttörések 2024-2026

A 2024-2026 időszak alapvetően átformálta a knowledge-graph + LLM kombinációkat. Míg **2023-ban a klasszikus baseline RAG** dominált (vector-similarity, izolált chunkok, elbukva a multi-hopon és a globális kérdéseken), addig az új áttörések a **strukturált memóriát, hierarchikus absztrakciót és tervezést** helyezték a középpontba. A graph-építés, ami korábban manuális volt, mára teljesen automatizálttá vált.

1. **Microsoft GraphRAG (2024)** — globális megértés áttörése. LLM-kinyerte entitás-graph + Leiden-community-summaries + Global Search. **Új 2023-hoz képest:** lehetővé tette a teljes-korpuszt-átfogó query-focused summarization-t, amire a vector-RAG koncepcionálisan képtelen.
2. **Hierarchical Reasoning Model (HRM, 2025-06)** — biológiai ihletésű 2-szintű rekurrens architektúra. **Új:** egyetlen forward pass, explicit CoT-felügyelet nélkül, 27M paraméter + 1000 sample is elég AGI-szintű feladatokra (Sudoku, ARC).
3. **Property-graph integrációk (LlamaIndex + LangChain)** — `LLMGraphTransformer`, `SchemaLLMPathExtractor`. **Új:** auto-ontology-design, hibrid vector + graph search beépítve, nem kell ontológia-tervezés.
4. **JEPA-családbővülés és megbízható világmodellek (H-JEPA)** — látens változós, energia-alapú modellek. **Új:** absztrakt látens predikció token/pixel helyett → autonóm akciósorozatok tervezhetők. (A research-output a VJEPA, Causal-JEPA és HIT-JEPA modellekről explicit jelzi: a forrásokban nincs részletes leírás, ezek **független ellenőrzést igényelnek**.)
5. **Verifikációs és Agentic RAG** — független **evaluator agentek** verifikációs pontszámot adnak a kinyert kontextusra + válaszra (hallucináció-csökkentés). **Agentic GraphRAG** (LangGraph): az agent autonóm dönt, mikor használ vector-keresést és mikor Cypher-query-t a graphon.

## 5. Failure-modes és limitációk

A GraphRAG és knowledge-graph megközelítés **nem csodafegyver**:

1. **Extrém cold-start költség** — graph-építés nulláról azt igényli, hogy LLM végigmenjen az adathalmaz minden mondatán entity-extraction-ért. A Microsoft explicit figyelmeztet: a GraphRAG indexing **rendkívül drága**, "start small". Hatalmas, real-time-frissülő adatokra **fenntarthatatlan költség**.
2. **Magas latency** — GraphRAG-query (különösen Global Search vagy LLM-generálta Cypher) lassabb mint vector-RAG. Tesztben **vector-search ~8 sec, GraphRAG ~71 sec és sokszor több token** egy átfogó válaszra. Plus LLM-call-ok önmagukban late­ncy-t hoznak.
3. **Entity-extraction-hibák és "beégetett" hallucinációk** — a graph minősége teljes mértékben az LLM extraction-képességén múlik. Ha az LLM félreért egy kontextust vagy nem létező relációt hallucinál, ezek **strukturált formában bekerülnek a graphba**, és a rendszer tényként kezeli őket. Ez "**strukturális hallucináció**" — sokkal nehezebben detektálható mint a sima text-hallucination. Részben csak independent verifier agentekkel enyhíthető.
4. **Schema-drift és rugalmatlanság** — auto-ontológia long-term schema-driftre érzékeny. Új típusú dokumentumok jönnek → az auto-ontology inkonzisztenssé válik (ugyanaz a fogalom más entity-type-ként). Explicit schema-kontroll nélkül **fokozatosan elzajosodhat**.

**Mikor szuboptimális a GraphRAG?**
- Ha a query egyszerű ténykeresés ("melyik fájl tartalmazza X-et?"). Vector-DB gyorsabb, olcsóbb, hatékonyabb.

**Mit NEM old meg a graph-réteg?**
- **Nem helyettesíti a szemantikus keresést** — gráf precíz strukturált logikára jó, de gyenge laza, strukturálatlan szöveges hasonlóságra. Ezért kell **hibrid (vector + graph) RAG**.
- **Nem garantálja zero hallucinációt** — a graph pontos tényeket ad át, de az LLM a végső válaszgeneráláskor hallucinálhat, ha a context nem fedi le a kérdést. A graph csak abban segít, hogy a válaszok **visszakövethetők (explainable)** az eredeti forrásig.

## 6. Implementáció a Peti-vault kontextusban

A jelenlegi `/root/obsidian-vault` (~240 fájl, Johnny-Decimal prefix, Karpathy LLM-Wiki minta) **ideális alapanyag** egy hibrid (vector + graph) RAG-architektúrához — a meglévő struktúra már félig entity-szerű:

- `02-Projects/<projekt>.md` = **Project entity** (egy fájl = egy entitás már most)
- `05-Memory/Infrastructure.md` = **Infrastructure/Server entity-graph** (host-portok, szolgáltatások, függőségek)
- `03-Hosts/<host>.md` = **Host entity**
- `07-Decisions/<date>.md` = **Decision entity** (ADR-szerű)
- A `[[wikilink]]`-ek a fájlok között már **explicit `MENTIONS` relációk** (Obsidian graph-view ezt vizualizálja)

### Implementációs lépések

**1. lépés — meglévő struktúra betöltése (explicit graph)**
Az Obsidian fájlokból a fix metaadatok (mappa-prefix → entity-type, frontmatter `name` + `type`) és a wikilinkek **alapértelmezett node-okként + élekként** importálódnak a graph-DB-be (Memgraph/Neo4j). Ez adja a strukturális gerincet — **kódolatlan, determinisztikus**, nem kell LLM-hez.

**2. lépés — LLM-vezérelt entity + relation extraction (implicit graph)**
A folyószövegre `SchemaLLMPathExtractor` (LlamaIndex) vagy `LLMGraphTransformer` (LangChain). **Előre definiált schemával** csökkentett zaj:
- **Entity-types:** `Project`, `Infrastructure`, `Server`, `Host`, `Task`, `Person`, `Document`, `Technology`, `Concept`
- **Relációk:** `MENTIONS`, `LINKS_TO` (wikilink-ből), `DEPENDS_ON` (projekt-szerver-DB függés), `WORKS_ON` (Peti → projekt), `PART_OF` (task → projekt), `RELATES_TO` (general)

**3. lépés — vector-indexek a graph-ban (komplementer SV-1-gyel)**
A graph-node-ok tulajdonságaiból (description, content snippet) embeddingek; ezeket a graph-DB-ben tároljuk vector-indexként. **Hibrid retriever** — egyszerre vector + Cypher.

**4. lépés — opcionális community-hierarchy**
Ha holisztikus query-k kellenek ("milyen fő témákon dolgoztam idén?"), Leiden-clustering + community-summary (Microsoft GraphRAG-minta). 240 fájlnál a költség elfogadható.

### Komplementer az SV-1 memory-rétegre

Ez a tengely **nem helyettesíti** az SV-1 vector-memory-réteget, hanem **fölé épül és kiegészíti**:

| Mit a vector-memory tud (SV-1) | Mit a graph-réteg ad (SV-6) |
|---|---|
| Felszínes szemantikai keresés ("Hogyan konfiguráltam a múltkor az Nginx cache-t?") | Multi-hop reasoning ("Mely projektek dőlnek be ha a `05-Memory/Infrastructure.md`-ben leírt DB-szerver leáll?") |
| Cold-start gyors (csak embedding-batch) | Strukturált aggregáció, pontos darabszámok |
| Olcsóbb per-query | Magyarázható, source-traceable válaszok |
| Stale-friendly (embedding-update könnyű) | Explicit dependencies / causation |

Az ideális architektúra: **SV-1 vector-réteg + SV-6 graph-réteg + LangGraph-agent**, ami autonóm dönti el melyik tool-t használja (Agentic GraphRAG). Ez a kombináció **magyarázható, tudatos logikai hálózatot húz a vector-similarity fekete-dobozra**.

### Phase B-be vihető akció-pontok

1. **POC**: Memgraph Docker + LlamaIndex `SchemaLLMPathExtractor` a `02-Projects/`-re — kinyerni a Project entitásokat + `DEPENDS_ON` relációkat az `05-Memory/Infrastructure.md`-vel. Cél: 1 napos POC.
2. **Schema-design**: explicit YAML-schema a 9 entity-type-ra + 6 reláció-type-ra (lásd lentebb). Verzionálni a `00-Meta/`-ban.
3. **Wikilink-importer**: deterministic script ami az összes `[[link]]`-et begyűjti és `MENTIONS` éleket épít — **nem kell LLM**.
4. **Hibrid retriever**: LlamaIndex query-engine vector + graph hibrid, integrálni az SV-1 memory-réteggel.
5. **Phase C-ben**: Microsoft GraphRAG külön notebook-szerű use-case ("milyen fő témákon dolgoztam Q1-Q2-ben?") quarterly retrospektívra.

## 7. Mit kell tovább kutatni?

### Open questions a forrásokból

1. **Dinamikus graph-frissítés (session-alapú entitások)** — hogyan integrálódjon a session-flow-ba (11.11note → graph-update). **Mem0 és Cognee** építik ezt; konzisztencia long-term schema-drift ellen még open.
2. **Multimodális knowledge graph (kép, kód, audio)** — két friss paper:
   - **Janus (arXiv 2410.13848)** — multimodális megértést és generálást egyesít a vizuális encoder szétválasztásával.
   - **"Bridging Visualization and Optimization" (arXiv 2501.11968)** — gráfokat képekké alakít, hogy MLLM-ek a térbeli intelligenciájukat használhassák graph-strukturált optimalizációra.
3. **Federated graph + jogosultságkezelés (cross-vault, több user)** — **Memgraph Zero** koncepciója: Federated GQL + Public-Private Data + multi-tenancy + LBAC.
4. **Graph + reasoning (CoT + Cypher)** — `GraphCypherQAChain` NL→Cypher, de **hallucinál** Cypher-szinten. Jövő: **Agentic GraphRAG** + esetleg **HRM + graph** (forward-pass reasoning Cypher-keresés helyett — még spekulatív).
5. **JEPA + Markdown-vault integráció** — open question: hogyan híd a **látens, folytonos JEPA-memóriatér** és a **diszkrét, szimbolikus graph-csomópontok** között? Ha az agent JEPA-val tudná predikálni a markdown-fájlok közötti rejtett dinamikákat, új kutatási irányokat / hiányzó tudáselemeket javasolhatna.

### Hivatkozott, de még nem kifejtett papers / projektek

- **Janus** (2410.13848) — multimodális unified architecture decoupled visual encoder-rel
- **Bridging Visualization and Optimization** (2501.11968) — graph → image transformation MLLM-ek számára
- **Mem0, Cognee, LightRAG** — újgenerációs RAG / AI-memory keretrendszerek folyamatos dinamikus graph-tanulásra
- **DRIFT Search** (MS GraphRAG) — harmadik query-method, lokális szomszédság fan-out + community-info
- **Agentic MCP-server-platformok** — Databricks Agent Bricks, Google Gemini Enterprise, Salesforce Agentforce — graph-DB-ket sztenderdizált external memory-tool-ként kötik be agentekhez

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható:

```bash
notebooklm generate audio -n 82e9046d-a60f-4a6e-9165-dedadc8fd591
```

## Phase A+ bővítés (2026-05-12 deep-research)

A Phase A 17 forrásához **+56 új forrás** csatlakozott 4 db `--mode deep --no-wait` web-search-szel (hybrid-cost benchmark, Memgraph/Neo4j prod case-studies, JEPA 2025-26, HRM prod). Összesen **73 forrás** a notebookban. Új 3 mély-komplex kérdés lefuttatva a teljes kibővült tudás-bázis alapján.

### Új források betöltve
- **Hybrid vector+graph RAG cost-benchmark:** Pinecone-Memgraph-Neo4j ár/teljesítmény összehasonlítók
- **Memgraph/Neo4j enterprise integráció:** LlamaIndex GraphStore, LangChain `LLMGraphTransformer`, `SchemaLLMPathExtractor`, `GraphCypherQAChain` production case-studies
- **JEPA 2025-26 fejlemények:** Yann LeCun AMI Labs $1.03B seed (2026), V-JEPA 2.1 (2026-03), LLM-JEPA, LeJEPA
- **HRM Sakana 2025-26:** arXiv 2506.21734 + hierarchikus reasoning POC-ok

### Q1 — Optimális 3-elem kombináció (a Peti-vault-ra)

A NotebookLM **3-rétegű architektúrát** ajánl alulról-felfelé sorrenddel.

**1. réteg — Hibrid vektor + tudásgráf alapréteg (infrastruktúra).** A meglévő `02-Projects/` + `05-Memory/` gráfba emelése és vektoros kereséssel ötvözése. Konkrét stack: **Memgraph + LlamaIndex**. A Memgraph in-memory + natív Neo4j-kompatibilitás + beépített vector-search; a LlamaIndex `SchemaLLMPathExtractor` automatikusan kinyeri entitásokat és relációkat az Obsidian fájlokból. **~240 fájlos vault méreténél a GraphRAG indexelési költség elhanyagolható.** Multi-hop infrastrukturális összefüggések megválaszolása már ezen a szinten.

**2. réteg — Episztemikus világmodell + globális munkaterület (orkesztráció).** A statikus DB → folyamatosan tanuló rendszer. „**Epistemic World Models**" — a gráf a „világként" funkcionál, az agent egy **Global Workspace**-en keresztül végez meta-kognitív önellenőrzést. Konkrét stack: **Mem0 vagy Cognee** — natívan támogatja a Memgraph-ot háttértárként, valós időben menti vissza a session-koncepciókat a gráfba. Megoldja a folyamatos tanulás + sémadrift problémáját a teljes újraindexelés nélkül.

**3. réteg — Hierarchikus következtetés + prediktív tervezés (intelligencia).** A Chain-of-Thought-ot leváltó architektúrák: **HRM** (magas-szintű lassú + alacsony-szintű gyors modul, egyetlen forward-pass) + **JEPA** elvek (absztrakt látens-térben jövőbeli állapot-predikció). A közelmúltban bemutatott **LLM-JEPA** a finomhangolást embedding-térben végzi. „Mi lenne ha"-szimulációk: szerver-módosítás kaszkádhatása azonnal, CoT-adatigény + latency nélkül.

**Bevezetési sorrend:** Memgraph + LlamaIndex → Mem0/Cognee → HRM/JEPA (felülre).

### Q2 — Production-ready vs akadémiai (2024-2026)

| Technológia | Stage | Megjegyzés |
|---|---|---|
| **Neo4j** | ✅ Production | Ipari standard, AuraDB managed, natív vector-keresés |
| **Memgraph** | ✅ Production | In-memory, high-throughput; cybersec / fraud-detection optimalizált |
| **LangChain Graph + LlamaIndex GraphStore** | ✅ Production | `LLMGraphTransformer`, `SchemaLLMPathExtractor`, `GraphCypherQAChain` rutinszerűen használva |
| **Pinecone hybrid (vector + graph)** | ✅ Production | „Legmegbízhatóbb éles RAG megközelítés" — szemantikai + gráf-aggregáció + explainability |
| **Microsoft GraphRAG** | 🟡 Prod-with-caveats | v3.0.9 (2026), megbízható globális kereséshez, **DE drága LLM-indexelési fázis** |
| **JEPA-család** (LeJEPA, V-JEPA 2, LLM-JEPA) | ❌ Academic | AMI Labs $1.03B seed (2026), **„nincs még kiadott termék"**, „évekbe telhet a kereskedelmi alkalmazás" — AMI CEO |
| **HRM (Hierarchical Reasoning)** | ❌ Academic | arXiv 2506.21734, proof-of-concept, **nem integrálva enterprise frameworkbe** |
| **World Models (general)** | ❌ Frontier | „Kutatási frontvonal; gyakorlati telepítés bizonytalan hatókör" |

**Konklúzió:** Az alsó 2 réteg azonnal építhető production tech-stack-kel. A **3. réteg (HRM/JEPA) Phase C+ idejére** marad, amíg production API-k nem érkeznek.

### Q3 — Cost-sensitive trade-off (3 budget-tier)

> **Status:** retry sikeres (2026-05-12 20:35), 126 sor, magyar nyelvű részletes 3-tier bontás. Forrás: `/tmp/sv-research/sv6-phase-a-plus-q3-retry.txt`. Az eredeti marker-fallback csonkolt 600-char-output frissítve.

Egy 240-fájlos jól strukturált Obsidian-vault (~100k-200k token nyers szöveg) ideális kiindulópont. A DB-inicializálás nem csillagászati költségű, de a fejlett "összképet" vizsgáló (sensemaking) lekérdezések + folyamatos gráf-frissítés gyorsan elfogyaszthatják a keretet. A három budget-tier:

#### Tier 1: $50/hó — "Lean" Hibrid Alap (Bootstrap)

A teljes keret API-hívásokra megy (főleg GPT-4o-mini, ritkán GPT-4o / Claude Sonnet), infrastruktúra ingyenes/lokális/open-source.

**MIT ÉPÍTÜNK:**
- **Memgraph Docker lokálisan** — extrém gyors in-memory gráf-DB, beépített vector-index, költségmentes [1, 2]
- **LlamaIndex `SchemaLLMPathExtractor`** — előre definiált entitások (Projekt, Szerver, Session, stb.) kinyerése az Obsidian-fájlokból [3]
- **Hibrid RAG**: szöveges embeddingek + gráf-bejárás ugyanabban a Memgraph-ban (Pinecone helyett lokális szemantikai keresés + 1-2 ugrásos multi-hop gráf-traversál) [4]

**MIT VÁGUNK LE:**
- **Microsoft GraphRAG** + hierarchikus közösségi összefoglalók (Leiden) — egyetlen globális query akár **50.000 token + 71 mp** [5], pillanatok alatt lenullázná a $50-os keretet
- **JEPA család** (V-JEPA, LLM-JEPA) + World Models — túl számítás-igényes, túl kutatási fázisban [6, 7, 8]

**Forrás-citáció:** [1-8]

#### Tier 2: $200/hó — "Agentic OS" + szűrt GraphRAG

~$30-50 menedzselt felhős infrastruktúra (Neo4j AuraDB / erős VPS) + ~$150 intelligensebb LLM-API.

**MIT ÉPÍTÜNK:**
- **Neo4j AuraDB** — perzisztens, robusztus gráf-tárolás [9]
- **Microsoft GraphRAG részlegesen**: Leiden-közösségek építése a vault-entitásokra, de a drága *Global Search* helyett **Local Search** (entitás körüli szomszédos koncepciók) + **DRIFT Search** [11, 12]
- **Agentic OS memória-réteg** Mem0 / Knowlee mintájára — autonóm strukturált koncepció-kinyerés a 11.11 sessionökből, valós időben vissza a gráf-DB-be [13, 14, 15]
- **3-rétegű "Knowledge" tárolás** supersession-nel + felülírással [16]

**MIT VÁGUNK LE:**
- Teljes 4-rétegű (Intelligence / Knowledge / Memory / Wisdom) szétválasztott kognitív modell — Google AOMA mintájú folyamatos DreamCycle (30 percenként offline LLM memória-konszolidáció) gyorsan túllépné a $150 API-keretet [16, 17]
- Natív HRM (Hierarchical Reasoning Model) + H-JEPA prediktív látens-tervezés — nulláról-betanítás kívül esik a büdzsén [18, 19]

**Forrás-citáció:** [9-19]

#### Tier 3: $500/hó — Produkciós "World-Model" Maxolás

Dedikált ügynök-ökoszisztéma, proaktív/okfejtő, megkülönbözteti a memóriatípusokat. Fedezi a jelentős API-költségeket, dedikált (esetleg GPU-gyorsított) VPS-t, legfejlettebb vektor+gráf stack-et.

**MIT MAXOLUNK KI:**
- **Teljes 4-rétegű Kognitív Architektúra** — perzisztens tények (Knowledge, supersession + provenance) + efemer élmény-memória (Memory, Ebbinghaus felejtési görbe) + viselkedési szabályok (Wisdom, szigorú revíziós kapuk) [16, 20]
- **Pinecone Hybrid RAG** — sűrű + ritka vektor kombináció maximális precizitásért (vector-search kiszervezve a Memgraph-ról)
- **Microsoft GraphRAG napi cron-on** — offline közösségi-összefoglalók frissítése [11]
- **LLM-JEPA finomhangolás** — bizonyítottan felülmúlja a standard input-space LLM-tanítást prediktív teljesítményben; absztrakt látens-térben (világmodell) előrejelez Obsidian-projekt logikai kimeneteleket, nyers szöveggenerálás hallucinációi nélkül [7, 21, 22]

**MIT MARADHAT KI (még $500-ból sem):**
- Natív multimodális fizikai világmodellek (V-JEPA 2 eredeti, NVIDIA Cosmos) — petabájtnyi videó-adat + több ezer GPU + millió-dolláros beruházás kell fizikai-valóság szimulációra / AGI-ra [8, 23, 24]
- Markdown-alapú agent-vault-ban a video-alapú "jóslások" (kinematika, vizuális fizika) feleslegesek és megfizethetetlenek — csak a JEPA elveinek **szöveges/kognitív adaptációjánál** (LLM-JEPA, 4-rétegű memória) maradunk

**Forrás-citáció:** [7, 8, 11, 16, 20-24]

#### Áttekintő tábla

| Tier | DB-réteg | Memory-Architektúra | GraphRAG | JEPA/World-Model |
|---|---|---|---|---|
| **$50/hó** | Memgraph Docker (lokális) | egyrétegű, embedding+gráf | ❌ kihagyva (50k token/query túl drága) | ❌ |
| **$200/hó** | Neo4j AuraDB (cloud) | Mem0/Knowlee autonóm extract + Knowledge-réteg | 🟡 részleges (Leiden + Local/DRIFT search) | ❌ HRM/H-JEPA nem |
| **$500/hó** | Neo4j + Pinecone Hybrid | teljes 4-réteg (K/M/W/I) + Ebbinghaus felejtés | ✅ teljes napi cron | 🟡 LLM-JEPA finetune ✓, V-JEPA 2 multimodális ❌ |

## Akció-pontok ehhez a tengelyhez

- [ ] Phase B sprint-bontás: 4-5 sprint a graph-réteg beépítésére (POC → schema → wikilink-importer → hybrid-retriever → GraphRAG-quarterly)
- [ ] Audio overview generálás + letöltés
- [ ] Schema-YAML draft a 9 entity-type + 6 relation-type-ra (`00-Meta/graph-schema.md`)
- [ ] POC Memgraph Docker-konténer + LlamaIndex extraction a `02-Projects/`-re (1 nap)
- [ ] Integrációs döntés SV-1 (vector-memory) ↔ SV-6 (graph): LlamaIndex hybrid retriever vs külön LangGraph agent-router

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
- [[10-raw/2026-05-12 — Superintelligence research source pool]]
- [[11-wiki/sv-01-memory-architecture]] — komplementer (vector-memory réteg)
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a vault jelenlegi (semi-)entity-struktúrájának háttere
- [[11-wiki/Crystallization-protocol]] — graph-update hook a session-záráshoz

## NotebookLM-konverzáció

- **Notebook ID:** `82e9046d-a60f-4a6e-9165-dedadc8fd591`
- **Conversation ID:** `352f63e1-1c39-45c3-9a23-3f6f0b43e0bd`
- **Források:** 17 (15 ready + 2 error: 4 YouTube + 1 paywall — backup arXiv-pdf-fel pótolva)
- **Kérdések:** 7/7 + 3 Phase A+ + 1 retry (Q3 2026-05-12 20:35, finomított hosszú-formátum prompt)
- **Forrásszintű idézet-támogatás:** minden szekció direkt forrás-citáció a NotebookLM-output szerint (lásd `/tmp/sv-research/sv6-q*.txt` + `sv6-phase-a-plus-q3-retry.txt` raw output-ok)
