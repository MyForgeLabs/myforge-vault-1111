---
name: SV-8 NotebookLM as cognitive layer
type: wiki
tags: ["#type/wiki", "agi", "notebooklm", "cognitive-layer", "tools-for-thought", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: done
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: a60d993b-1926-40cc-b947-94b3ef663f00
---

# SV-8 — NotebookLM as cognitive layer

A 8-tengelyű szuperintelligens-vault evolúciós research nyolcadik (és egyben záró) cikke. **Kérdés:** a NotebookLM nem csak research-eszköz, hanem a vault-on belüli **source-grounded reasoning + convergent synthesis** réteg — automatikus audio-overview, multi-source-ütköztetés, hipotézis-tesztelés. Steven Johnson „tools for thought" minta.

> **Status:** Phase A 7/7 kérdés + Phase A+ 4 deep-research + 3 mély-Q válaszolva. NotebookLM-források: **1200** (Phase A: 30 → Phase A+: 1200). Phase B implementáció Q6 + Phase A+ konkluzió alapján indul.

> **Self-referential megjegyzés:** ez a wiki-cikk **a NotebookLM-mel készült a NotebookLM-mint-cognitive-layer pattern-ről**. A SV-1..SV-8 research-mind a NotebookLM-en fut — a tengely **maga is bizonyíték** a hipotézisre.

## 1. A tengely magja

A NotebookLM egy **„végfelhasználók számára testreszabható RAG (Retrieval-Augmented Generation) termék"**, amelynek célja, hogy a hagyományos jegyzetelést egy intelligens, AI-vezérelt folyamattá alakítsa. Ami megkülönbözteti a hagyományos chatbotoktól (ChatGPT) és a custom-RAG-stackektől: itt a nyelvi modell **kifejezetten a felhasználó saját forrásaiban van „lehorgonyozva" (grounded)**, ezáltal egy „személyre szabott AI"-t hozva létre, amely „jártas a felhasználó számára releváns információkban". Míg a **Claude Projects** is biztosít egy 200 000 tokenes kontextusablakot dokumentumok integrálására, a **NotebookLM a Gemini 1.5 Pro modell akár 1,5 millió szavas** (technikai trükkökkel 25 milliós) kapacitására épít — ami radikálisan átalakítja a gyakorlati hasznosságot: a teljes forrásanyag egyidejű, mély és kontextushű megértését teszi lehetővé chunkolás nélkül.

A NotebookLM működése azért írható le „source-grounded reasoning + convergent synthesis" kognitív rétegeként, mert „**virtuális kutatóasszisztensként**" működik, amely képes „tényeket összefoglalni, összetett ötleteket elmagyarázni és új összefüggéseket kitalálni" a feltöltött anyagok alapján. A **source-grounded reasoning** abban nyilvánul meg, hogy minden válasz a forrásokra alapszik, csökkentve a hallucinációkat, és az állítások eredeti idézetekkel (citation-pointerekkel) vannak alátámasztva. A **convergent synthesis** pedig a „tények és ötletek több forrásból történő szintetizálásának" időrabló kihívását oldja meg — a felhasználó dinamikusan generált javaslatokkal új strukturált dokumentumokat (vázlatokat, hírleveleket) vagy a forrásokat szintetizáló, két MI-műsorvezető által vezetett „Audio Overview" beszélgetéseket hoz létre.

Steven Johnson, a Google Labs szerkesztőségi igazgatója (a NotebookLM egyik atyja) ezt **„tools for thought"** (gondolkodást segítő eszközök) keretrendszerbe helyezi. A NotebookLM nem puszta információszervező alkalmazás, hanem egy **„személyre szabott AI munkatárs"**, amelynek célja, hogy a felhasználóknak „kihozni magukból a legjobb gondolkodást" segítsen — egy olyan tér, mint a konyhaasztal vagy egy séta, ahol „megszervezhetik gondolataikat, hogy üzeneteket fogalmazzanak meg, célokat érjenek el és kapcsolatokat teremtsenek". Johnson kiemeli: a 1,5 millió szavas kontextusbefogadó képesség **„az elmúlt két év leginkább alulértékelt AI-fejlesztése"**, amely valódi kognitív rétegként képes az emberi gondolkodást felerősíteni.

## 2. Kanonikus képességek (7 fő funkció)

### (1) Source-grounded generation citation-ökkel
A NotebookLM alapvető architekturális megközelítése: a nyelvi modellt szigorúan a feltöltött dokumentumokban „horgonyozza le", így minimalizálja a hallucinációkat. Minden állítást **kattintható hivatkozásokkal támasztja alá** — a felhasználó egy klikkel a citation-ből az eredeti forráskontextusra ugorhat. *„NotebookLM automatically shares citations from your sources whenever it answers a question. But now you can quickly jump from a citation to the source, letting you see the quote in its original context."* (Google blog)

### (2) Audio Overview ("podcast-magic")
A rendszer egykattintásos „deep dive" beszélgetést generál két AI-műsorvezetővel. Nem felolvasás, hanem **diszfluenciákkal** (szünetek, nevetés, töltelékszavak) tűzdelt, élethű dialógus. A 2024-09-i frissítéssel a felhasználó **instruálhatja is** a műsorvezetőket (fókuszálás konkrét témákra, szakértelmi szint módosítása). A háttértechnológia a Google Research **SoundStorm** projektje — 0,5 másodperc alatt 30 másodpercnyi audio. Saját hangok klónozása technikailag lehetséges (egy rövid „hang-prompt" elég), de termékben még nem elérhető.

### (3) Multi-source synthesis
A 1,5 millió szavas kontextusablakra építve a rendszer egyszerre elemez sok különböző formátumú forrást (Markdown, PDF, weboldalak, Google Docs, YouTube videók) — áthidalva a hagyományos kutatás legnagyobb akadályát, az adat-elszigeteltséget. *„One of the biggest challenges is synthesizing facts and ideas from multiple sources. You often have the sources you want, but it's time consuming to make the connections."* (Steven Johnson)

### (4) Artifact-generation
A források alapján a rendszer új strukturált tartalmakat generál: vázlatok (outlines), hírlevelek (newsletters), tanulmányi útmutatók (study guides), briefing dokumentumok. **A jelenleg dokumentált a források körében ezek + Audio Overview + jegyzetexport Google Docs-ba.** A NotebookLM CLI a tényleges 2026-os termékben ennél bővebb artifact-listát támogat (mind map, quiz, report, slide-deck, video, infographic, flashcards, data-table, cinematic-video) — ezeket a CLI `notebooklm generate` parancsa demonstrálja, de a forrásokban csak az alapfunkciók szerepelnek.

### (5) Sleep-time / async compute
Bár a források a „sleep-time" vagy „deep research mode" kifejezéseket nem használják explicit, a számításigényes műveletek (Audio Overview generálás) **aszinkron, háttérben futnak** — nagy notebookok esetén percekig dolgozik a rendszer. A CLI-szinten ez kifejezetten támogatott (`research wait --timeout`, `artifact poll`, `--no-wait` flag-ek).

### (6) Shared notebooks + collaboration
A NotebookLM elsődleges ígérete az adatvédelem (a feltöltött dokumentumokat nem használják fel az alapmodellek betanítására), de **támogatja a megosztást** is. A felhasználók megoszthatják a projekt-jegyzetfüzeteiket munkatársakkal — közös gondolkodás és szintézis ugyanazon tudásbázis felett. *„Your personal data is not used to train NotebookLM — so any private or sensitive information you have in your sources will stay private, unless you choose to share your sources with collaborators."*

### (7) CLI / API integráció (kontextuális kiegészítés)
**A forrásokban a CLI/API NEM dokumentált** — a Google a NotebookLM-et zárt, GUI-alapú végfelhasználói termékként pozícionálja. **A gyakorlatban viszont** közösségi `notebooklm-cli` (python wrapper) létezik, és a Peti-vault is erre épít (lásd #6 szekció). A 2025-26-ban bejelentett **NotebookLM Enterprise API** (Google Cloud) hivatalos REST-támogatást ad notebookok és sources kezeléséhez — ez a research-add-research által importált forrás (`docs.cloud.google.com`) megerősíti.

## 3. Tech-stack opciók 2026-ban (tradeoff-tábla)

| Megoldás | Kontextus | Költség / Ár | Fő erősség | Gyengeség |
|---|---|---|---|---|
| **NotebookLM Standard** (free) | 1,5M szó / Gemini 1.5 Pro | $0 (eddig) | Audio Overview, hatalmas out-of-the-box kontextus | Zárt GUI, hivatalos API csak Enterprise |
| **NotebookLM Plus** | 1,5M szó / Gemini 1.5 Pro | Forrásokban nincs explicit adat (~$20/hó körül kering közösségi adat) | Magasabb source-limit (300 vs 50), deep research mode | Csak USA/EU egyes piacokon |
| **NotebookLM Enterprise (API)** | 1,5M szó | Google Cloud pricing | Hivatalos REST-API, audit, VPC | Vállalati setup-overhead |
| **Claude Projects** | 200K token (~500 oldal) | Claude Pro/Team előfizetés | Artifacts UI (élő kód/dok-szerkesztés), MCP-integráció | Kisebb kontextusablak |
| **Anthropic Contextual Retrieval** (saját RAG) | Skálázható (vektor-DB) | $1,02 / 1M token feldolgozás | Teljes kontroll, **67%-kal csökkenti** a visszakeresési hibákat (5,7% → 1,9%), prompt caching 90% költségcsökkentés | Magas fejlesztési overhead (chunking, BM25, infra) |
| **ChatGPT Code Interpreter** | 100MB fájl | ChatGPT Plus | Autonóm kódírás, regressziós elemzés, vizualizáció | Nem optimális 1,5M szavas szintézisre |
| **Perplexity Spaces** | n/a (forrásokban nincs adat) | n/a | Nincs adat a forrásokban | Nincs adat a forrásokban |

### Konkrét integrációs minták (Peti-vault konzisztens)

A források a NotebookLM-mint-GUI-eszközt írják le; **automatizációs minták (cron, hook, Obsidian → notebook) hivatalosan nem dokumentáltak**. A Peti-vault gyakorlatban:

- **CLI:** `/root/.notebooklm-venv/bin/notebooklm` (python wrapper) — auth headless-FIFO patternen (lásd kapcsolódó wiki)
- **Source-add patterns:** `notebooklm source add <URL/file> -n <NB_ID>` Markdown vagy URL feltöltésre
- **Batch add-research:** `notebooklm source add-research "<kérdés>" -n <NB_ID> --import-all` web-bővítés
- **Async / scriptelt:** `notebooklm research wait --timeout 300 --import-all`, `notebooklm artifact poll`
- **Artifact generálás:** `notebooklm generate audio|mind-map|quiz|video|slide-deck|report|infographic`
- **Q&A scriptelhető:** `notebooklm ask "<kérdés>" -n <NB_ID> --json` — citation-okkal együtt JSON-output

## 4. Friss áttörések 2024-2026

A források alapján a **2024-es év vízválasztó** volt a source-grounded synthesis területén:

### 2024-09-11 — NotebookLM Audio Overview launch
Google a NotebookLM-be építette az **Audio Overview**-t — egykattintásos „deep dive" podcast-generálás. Háttér: **SoundStorm** (Google Research, 0,5 sec → 30 sec audio). A diszfluenciák („uh", „uhm", nevetés) bevezetése drasztikusan emelte a hihetőséget — *„we knew we couldn't have it sound like two robots talking"*. Hamel Husain, Simon Willison, Ethan Mollick mind a kísérleti élmény „erősen működő mágia" jellegét emelték ki.

### 2024-06-25 — Claude Projects + Artifacts
Az Anthropic párhuzamosan a NotebookLM-hez hasonló forrás-vezérelt szintetizálási igényre **Projects** funkciót vezetett be (200K context window, custom instructions). Mellé az **Artifacts** UI — dedikált ablak generált kód/dokumentum/vizualizáció élő szerkesztésére.

### 2024-09-19 — Anthropic Contextual Retrieval
Egy új RAG-keretrendszer a klasszikus chunking-veszteség kiküszöbölésére:
- **Contextual Embeddings** + **Contextual BM25** — minden chunkhoz hozzáfűzi az eredeti dokumentum-szintű kontextust
- **49%-os visszakeresési hibacsökkentés** alapból
- **67%-os hibacsökkentés** (5,7% → 1,9%) reranking-kel
- **Prompt caching** miatt költség: csak $1,02 / 1M token

### A mögöttes nagy áttörés: long context emergence
Steven Johnson (2022 nyár, NotebookLM-elődfejlesztés idején): „**a modellek mindössze ~1500 szót tudtak befogadni**". 2024-re ez **1,5 millió szó** lett (Gemini 1.5 Pro), trükkökkel 25 millió. Ez a kontextus-növekedés — kombinálva a prompt caching cost-reduktorral — tette lehetővé, hogy az AI túllépjen pontszerű kérdés-válaszon, és **a teljes személyes tudásbázist egyben kezelő, koherensen érvelő kognitív réteggé** váljon.

### Hiányzó / dokumentálatlan friss áttörések
A forrásokban **2024-09-i csúcsig** van adat. Az alábbiak (a kérdésben felvetett, de NotebookLM-output szerint forráson-kívüli) független verifikációt igényelnek:
- NotebookLM Plus tier launch (2024-12 körül, közösségi info)
- Video Overview / cinematic-video (2025)
- Deep research mode (2025-26)
- Multi-language audio (forrásokban: „az AI-műsorvezetők csak angolul")
- NotebookLM Enterprise API (add-research forrás megerősítette: `docs.cloud.google.com/gen-ai-app-builder/notebooklm-api`)

## 5. Failure-modes és limitációk

### Forrás-alapúak (dokumentált)

**(5a) Audio Overview pontatlanság** — A NotebookLM-output őszintén jelzi: az AI-műsorvezetők *„pontatlanságokat vihetnek a magyarázatokba"* (hallucináció), és a felhasználó **nem szakíthatja félbe** a generálást ha hibáznak. *Mitigáció:* fenntartásokkal kezelni, primer forrást ellenőrizni komplex tényadatoknál.

**(5b) Magyar / non-English audio-minőség** — A források szerint az AI-műsorvezetők **kizárólag angolul beszélnek**. A „podcast-magic" magyar forrásanyagokra nem alkalmazható (legalábbis 2024-09 állapot szerint). A szöveges Q&A működik magyarul (ezt a Peti-vault gyakorlat bizonyítja).

**(5c) Privacy — Google cloud hosting** — A Google ígérete: a feltöltött adatok nem kerülnek modell-tanításba, és más felhasználóknak nem láthatók. Viszont a fájlok **Google szervereire kerülnek** — szigorú on-premise / air-gapped vállalati előírásnak nem felel meg.

**(5d) Prompt injection / data exfiltration** — Simon Willison **2024-elején bemutatta**, hogy egy külső fájlba rejtett Markdown-kép URL képes volt **privát adatokat kiszivárogtatni** a query string-en keresztül. Google **2024 áprilisában javította**, de a precedens megmaradt — zárt rendszerek, API-hiányos termékek bizalmi auditra szorulnak.

### Forrásokon kívüli (Peti-vault gyakorlatban tapasztalt)

**(5e) Source-limit:** Standard 50, Plus 300 source/notebook (közösségi info, forrásban nincs)
**(5f) Cloudflare/Turnstile blokk:** Headless használatban gyakran kell `cloakbrowser` fingerprint-bypass — lásd [[cloakbrowser-fingerprint-bypass]]
**(5g) Auth-elveszés 2-4 hét után:** Heti keepalive cron-job kell (foxxi-NotebookLM kontextus)
**(5h) RPC instabilitás (502 Bad Gateway):** Az SV-8 research során is előfordult — `add-research` 502-vel hibázott egyszer, retry után OK. Retry pattern kötelező az automatizált workflow-knál.
**(5i) Citation-pointer félre-link:** A NotebookLM RAG-rendszerek hagyományos buktatója — ha a chunkok szövegszerűen hasonlítanak, a citation rossz dokumentumra mutathat.
**(5j) Streaming API hiány:** Az `ask` parancs blokkoló, nincs token-streaming. Vendor-lock-in csökkentő: Google Docs-export elérhető.

### Mikor szuboptimális választás?

A NotebookLM **nem** megfelelő:
1. **Air-gapped lokális** adatkörnyezet (forrásokat fel kell tölteni)
2. **Magyar nyelvű Audio Overview** (csak angol)
3. **Fejlesztői API-integráció kritikus** (Enterprise API setup-overhead-del jár; community CLI sérülékeny Google policy-változásra)
4. **100%-osan tény-alapú, megszakítható audio** kell

Ezekben az esetekben az **Anthropic Contextual Retrieval** + custom RAG, vagy a **Claude Projects + MCP** kombináció jobb választás.

## 6. Implementáció a Peti-vault kontextusban

> **Self-referential megjegyzés:** ez a teljes SV-1..SV-8 research **a NotebookLM-mel készült**. A workflow tehát **már most működik** — ez a szekció rögzíti a mintát szisztematikus skálázáshoz.

### Meglévő infrastruktúra (Peti-vault)

A NotebookLM-integráció **már él** a Peti-vaultban:
- **CLI telepítve:** `/root/.notebooklm-venv/bin/notebooklm` — python wrapper a notebooklm-CLI projekthez
- **Headless auth pattern:** [[11-wiki/notebooklm-headless-login-fifo]] — FIFO-stdin + VNC manuális login + heti keepalive cron (vasárnap 04:00)
- **Research pattern:** [[11-wiki/notebooklm-seo-competitor-research-pattern]] — 17×7 strukturált kérdés workflow, kipróbálva foxxi SEO-research projekten (~60-90 perc/research)
- **Az SV-8 research notebook:** `a60d993b-1926-40cc-b947-94b3ef663f00` — 30 source-szal (20 manuál + 10 add-research)

### Phase B sprintek (6 lépés)

**Sprint 1 — Per-projekt notebook-pool (1 hét)**
- Minden aktív projekthez egy NotebookLM-notebook: `<projekt>-context-<YYYY-MM-DD>`
- Source-pool a `02-Projects/<projekt>.md` + minden hivatkozott `11-wiki/*` + utolsó 10 session
- Manual seed-script: `/usr/local/bin/notebooklm-bootstrap-project <slug>` — átalakítja a Markdown-okat és batch source-add-eli
- **Cél:** minden projekthez egy aktív „brain" — kérdésekre konkrét, source-grounded választ ad a projekt-állapotról

**Sprint 2 — Auto-source-add változás-detektálással (1 hét)**
- `inotifywait -m -e modify,create /root/obsidian-vault/{11-wiki,02-Projects}` watcher
- Trigger: változott fájl → `notebooklm source refresh -n <NB_ID> -s <SOURCE_ID>` (CLI támogatja a refresh-t)
- **Tudatos korlát:** NotebookLM API hivatalosan nem támogatja a programozott add-et; community-CLI Google policy-change-re sérülékeny. Mitigáció: dual-write a vault-ba (canonical) + NotebookLM (cache).

**Sprint 3 — 11.11stop crystallization-hook (1 hét)**
- A `/11.11stop` flow Learnings-szekciója auto-küld egy közös **vault-meta** notebookba (egy notebook, ami minden tanulságot felhalmoz)
- Parancs: `notebooklm source add "<learnings-extract>" --type text --title "<session-slug>" -n <META_NB_ID>`
- A meta-notebookra futtatható: „Milyen tanulságok ismétlődnek 3+ projektben?" (cross-projekt synthesis)
- **Megfeleltetés a MemGPT pattern-nek:** a working memory (aktív session) → episodic (session-archív) → **semantic** (NotebookLM meta-notebook). A SV-8 a SV-1 (memory architecture) **semantic-réteg implementációja**.

**Sprint 4 — Heti commute-podcast (folyamatos, low-overhead)**
- Vasárnap esti cron: `notebooklm generate audio -n <WEEKLY_NB_ID>` egy „heti-vault-status" notebookra
- A heti-vault-status forrás-pool: aktív projekt-fájlok + a hét új ADR-jei + a top-5 Learning
- Output: MP3 letölthető, hétfő reggeli ingázáshoz
- **Korlát:** ahogy a források jelzik, az audio-overview NEM lehet cron-időzítve a Google-felületen — community-CLI-ből viszont **lehet** (`notebooklm generate audio` szkriptelhető)

**Sprint 5 — Cross-projekt synthesis kérdések (manuális, havi)**
- Havi 1× futtatás: a meta-notebookon (Sprint 3 output) 7 strukturált kérdés:
  1. „Mely tanulságok ismétlődnek 3+ projektben?"
  2. „Mely failure-mode-ok közösek?"
  3. „Mely tech-stack döntések ütköznek egymással?"
  4. „Mely user-preferenciák szilárdultak meg?"
  5. „Mely projekt-specifikus tudás lenne wiki-szintűvé emelhető?"
  6. „Mely tudás-területek alulkutatottak?"
  7. „Mely projektek hivatkoznak egymásra de nincs explicit link?"
- A válaszok új `11-wiki/cross-project-synthesis-<YYYY-MM>.md` cikkek

**Sprint 6 — Source-pool curation + tokenszám-menedzsment (folyamatos)**
- A 1,5M szavas kontextusablak miatt **a ~240 fájlos Peti-vault egyetlen notebookba beleférhet** — chunkolás nélkül
- A források szerint a NotebookLM Plus 300 source-limit szigorúbb mint a tokenszám
- Best practice: **forrás-prioritás** (⭐⭐⭐ foundational, ⭐⭐ konkrét, ⭐ háttér — [[10-raw/2026-05-12 — Superintelligence research source pool]] alapján) — minőség > mennyiség
- Biztonsági figyelmeztetés: a Markdown fájlok **ne tartalmazzanak external-resource Markdown képeket** (prompt injection vektor a Simon Willison 2024-eleji bemutató szerint)

### Kapcsolódó architektúra-minták a többi SV-tengelyhez

- **SV-1 (Memory):** a NotebookLM **a semantic-memory réteg implementációja** — a vault-meta notebook a Generative Agents reflection-loop megfelelője
- **SV-5 (Crystallization):** Sprint 3 (11.11stop hook) **integrálja** a SV-5-öt és a SV-8-at — a Karpathy „compilation" elv: külső tudás → notebook → audio → letöltött wiki-cikk pipeline
- **SV-6 (World-model / KG):** a multi-notebook cross-reasoning hiányát a **GraphRAG** entity-graph + community-summary pattern oldhatja meg — ez a SV-6 tárgya
- **SV-7 (Eval):** a „Don't Hallucinate, Abstain" (arXiv:2402.00367) Multi-LLM Collaboration framework a NotebookLM synthesis-minőségének auditálására (~19,3% javulás abstain-pontosságban)

## 7. Mit kell tovább kutatni?

### Open questions a NotebookLM-output szerint

1. **NotebookLM API stabilitása long-term** — Hivatalos REST-API csak Enterprise tier-en (Google Cloud), community-CLI policy-változásra sérülékeny. Long-term érdemes Anthropic Contextual Retrieval RAG-stackre épülni mint redundáns alternatíva.
2. **Self-hosted alternatíva tradeoff** — Anthropic Contextual Retrieval: $1,02 / 1M token, 67%-os hibacsökkentés, 90%-os prompt-caching cost-reduction. Skálázhatóbb és kontrollálhatóbb mint a NotebookLM, de magasabb fejlesztési overhead.
3. **Audio-overview personalizáció** — SoundStorm már technikailag képes saját hangokra („egy rövid hangminta promptként elég"), de termékben még nem elérhető. Várható 2026-27 körüli launch.
4. **Multi-notebook cross-reasoning** — Jelenleg notebook-szintű hatókör. A források a **GraphRAG (From Local to Global)** pattern-t adják meg: entity knowledge graph + community summaries → globális szintézis 1M+ token korpusz felett.
5. **Synthesis-minőség evaluation** — A **„Don't Hallucinate, Abstain"** (arXiv:2402.00367) **Multi-LLM Collaboration** framework — kooperatív/kompetitív „knowledge gap" tesztelés. 19,3%-os javulás az abstain-pontosságban.
6. **NotebookLM mint „compiler"** — A források szerint az Audio Overview generálási folyamat eleve compiler-szerű: AI vázlatot ír → átdolgozza → szkriptet ír → kritizálja → hozzáadja a diszfluenciákat. Ez **közvetlen analógia a Karpathy LLM-Wiki compilation pattern-hez** — külső tudás → notebook → audio + dokumentum.
7. **Friss kutatások amiket érdemes követni:**
   - `arXiv:2310.08560` MemGPT — operációs rendszer-szintű hierarchikus memóriakezelés (SV-1 alapanyaga)
   - `arXiv:2305.14283` Query Rewriting for RAG — „Rewrite-Retrieve-Read" framework (kisebb modell újraírja a query-t a feketedoboz LLM számára)
   - **Ethan Mollick** (One Useful Thing) — Agentic Era átmenet, ChatGPT Code Interpreter
   - **Simon Willison** (simonwillison.net) — prompt injection, NotebookLM nem-dokumentált funkciók („egzisztenciális krízis 2034-i dátummal" exploit)
   - **Steven Johnson** essays — „tools for thought" diskurzus, Google Labs editorial direction

### Független verifikációt igénylő (forrás-pool nem fedte le)

- NotebookLM Plus konkrét ár (2026-os)
- Video Overview / cinematic-video pontos launch-dátum és képességek
- Deep research mode 2025-26-os feature-set
- Multi-language audio (mikor lesz a magyar?)
- NotebookLM Enterprise API teljes endpoint-lista és quota
- Perplexity Spaces architektúra (versenytárs)

## Phase A+ bővítés (2026-05-12 deep-research)

> **Status:** 4 új `add-research --mode deep` + 3 mély kérdés a 4 új research-anyagra alapozva. Notebook-source-pool **30 → 1200** (40×). Phase A elsődleges hipotézisét **közvetlenül** validálja vagy felülírja, ahol kell.

A Phase A során 30 forrás (20 manual + 10 add-research import) adta a base-line-t. A Phase A+ négy célzott, mélyebb tématerületet hozott be:

- **R1 — DSPy + AgentInstruct + meta-evaluation (2026 production):** task `303a6340-afb5-480f-b660-c7074d85ac2c`
- **R2 — NotebookLM API Enterprise 2026 + third-party integration:** task `682951dd-fa6b-4d37-b907-13105a3583b1`
- **R3 — Claude Projects vs Anthropic Contextual Retrieval (production 2025-26):** task `06f72cf3-aaf6-4be6-846a-0fc512d21059`
- **R4 — Citation-grounded RAG (production patterns, source attribution accuracy):** task `deab30fa-133b-43c3-afc1-e22b047eae4f`

A 3 mély kérdés output-ja: `/tmp/sv-research/sv8-phase-a-plus-q{1,2,3}.txt`.

### Phase A+ — Q1: 3 architektúrális elem KOMBINÁCIÓJA + sorrend

A friss források alapján egy ~240 fájlos Obsidian-Markdown agent-vaultban a **vektor-DB-alapú „naiv" RAG mára elavult**. A Claude 4.6/4.7-es 1M tokenes ablak + a kiszivárgott Claude Code architektúra **bizonyítja**: a leghatékonyabb ágensek nem vektor-DB-t, hanem lemezen lévő Markdown-indexeket + lexikális keresést (grep) + okos tömörítést használnak. A NotebookLM-mint-cognitive-layer ebbe a paradigmába a következő 3 réteg KOMBINÁCIÓJA illeszkedik be — **a sorrend kötelező**:

**(1) Fájl-alapú „Memory Stack" + okos tömörítés** (Vector DB helyett) — **ELŐSZÖR EZ.** Négy fájlos memória-verem: `project-map.md` (struktúra + kritikus korlátok), `session-log.md` (döntéstörténet a 11.11 sessionökből), `state.md` (aktuális feladat pillanatképe), `known-issues.md` (hibatérkép). A 11.11-protokollba beépítve az ágens belépéskor a `session-log.md` + `project-map.md` beolvasásával azonnal kontextusba kerül, NEM próbál RAG-darabkákból (chunkokból) rekonstruálni. **A Peti-vaultban a `02-Projects/<projekt>.md` + `04-Tasks/Backlog.md` + `07-Decisions/*` + `08-Sessions/*` már LÉNYEGÉBEN EZ a 4-fájlos memória-verem** — csak nincs explicit named-up. Sprint-A+1: alias-fájlok / index-frissítés ennek tudatos kihasználására.

**(2) NotebookLM MCP-bridge** (kognitív szintézis) — **MÁSODSZOR.** A `notebooklm-mcp-cli` (2026) Model Context Protocol-on keresztül programozhatóvá teszi a NotebookLM-et. Claude Desktop / Cursor / Claude Code közvetlenül utasíthat: a 11.11stop a releváns Markdown-fájlokat batch-add-eli egy új projekt-NB-be, lefuttatja az Audio Overview-t, és visszatöltheti a citation-pointereket a vaultba. A SV-8 Phase B Sprint-2 ezt a réteget építi ki.

**(3) DSPy + GEPA meta-evaluációs réteg** (folyamatos önfejlesztés) — **HARMADSZOR.** Prompt-engineering helyett **Context Engineering**: az ágens-utasításokat DSPy „signature"-ként deklaráljuk, a 11.11-output-okra heurisztikus metrikákat alkalmazunk (hivatkozások megléte, struktúra-teljesség), és GEPA (Generalized Expectation-based Prompt Adaptation) a háttérben mutálja és optimalizálja a system-prompt-okat. Aszimmetrikus modell-orchestráció: olcsó generátor (GPT-5.4 Nano) + erős reflektor (Qwen3-Next-80B-Thinking vagy Opus 4.7). **GEPA megerősítéses tanuláshoz képest 35×-ös computational cost-reduction** a forrásokban.

> **Karpathy-kompatibilitás:** ez a 3-réteg = Karpathy `working ↔ episodic ↔ semantic` memória-stack-jének **gyakorlati megvalósítása** + auto-tuning. Az (1) a working/episodic (fájl-alapú), a (2) a semantic (NotebookLM szintézis), a (3) a meta-loop (Karpathy „compilation" pattern explicit auto-optimalizálással).

### Phase A+ — Q2: production-ready vs academic stage (2024-2026)

A 6 vizsgált komponens státusza a friss források alapján:

**PRODUCTION-READY (iparilag validált, éles használatban):**

- **NotebookLM + Audio Overview** — éles, ingyenes, ~50 source/notebook (Standard), 500k szó/notebook, click-to-podcast. „Source-grounding" mondatonkénti citation-okkal. Egyetlen ismert vektor a **prompt injection** (Simon Willison 2024-i bemutató).
- **Claude Projects** — $20/hó Claude Pro, 200K token (~150k szó), Claude Sonnet 4.5/4.6/4.7 + Artifacts. NotebookLM-mel ellentétben **rugalmas kiegészítő kontextusként** kezeli a forrásokat (nem kizárólagos tudásbázis), így komplexebb analitikai/kódolási feladatokra alkalmasabb.
- **Anthropic Contextual Retrieval** — kifejezetten enterprise nagy-volumen RAG-pipeline: 4-rétegű optimalizációs futószalag (contextual embeddings + contextual BM25 + reranking + prompt caching). 67%-os visszakeresési hibacsökkentés, $1.02/1M token.
- **DSPy + GEPA** — a manuális prompt-engineering 2026-ra ÉLES rendszerekben elavult. DSPy 2.x + GEPA az **ICLR 2026 Oral**-en kiemelt presentation. 10-40%-os minőségjavulás RAG-pipeline-okban. **2026 alapköve a professzionális AI-rendszereknek.**
- **Source-grounded / Agentic / Long-context RAG** — „naiv RAG" (chunk + cosine-similarity) **hivatalosan halott**. 2025-26 kontextusablak-forradalom (1-2M token direct processing) ↔ Agentic RAG (multi-step retrieval + reasoning) a két éles paradigma.

**ACADEMIC STAGE (kutatás / paper fázisú):**

- **AgentInstruct** — Microsoft Research, 2024 július, *„AgentInstruct: Toward Generative Teaching with Agentic Flows"*. Laborkörnyezetben szintetikus tanító-adat generálására (Orca-AgentInstruct keret), **NEM** end-user production komponens.

**Tanulság a Peti-vault tervezéshez:** a Phase B Sprint-2 (NotebookLM MCP) és Sprint-5 (cross-projekt synthesis) production-ready building-blokkokra épülhet — kockázat alacsony. A DSPy/GEPA Sprint-szerű bevezetése szintén production-ready, csak a budget kérdés (lásd Q3). Az AgentInstruct csak ihlet-forrás (synthetic-data-augmentation pattern), nem közvetlen tech-stack komponens.

### Phase A+ — Q3: 3 budget-tier ($50 / $200 / $500 / hó) — mit vágunk le

A ~240 fájlos vault **beleférne 1 db Plus-tier NotebookLM notebookba** (300 source-limit) → a teljes architektúra drasztikusan egyszerűsödik. A 3 budget-tier:

**Tier $50/hó — minimalista, ingyenes-stack:**
- **MEGTART:** NotebookLM per-projekt notebook-pool + commute-podcast (Audio Overview). Közösségi `notebooklm-py` CLI scripteli a source-add és audio-gen folyamatokat. Crystallization-hook a 11.11stop-nál ultra-budget API-val (GPT-5.4 Nano, $0.20/1M input token).
- **VÁG:** DSPy GEPA meta-eval (egyetlen futás $10-$200 iteratív tesztelés miatt). Contextual Retrieval backup (luxus, amíg NotebookLM ingyen elvégzi a dokumentum-Q&A-t). **Promptokat manuálisan írunk.**

**Tier $200/hó — hibrid / router-vezérelt:**
- **MEGTART Tier 1-ből:** NotebookLM CLI + napi notebook-management + podcast.
- **HOZZÁAD (kompromisszumokkal):**
    - **Contextual Retrieval csak cross-projekt szintézisre.** A NotebookLM legnagyobb hátránya a **notebook-izoláció** — szűk fókuszra kiváló, cross-corpus keresésre gyenge. Erre Claude Sonnet 4.6 + Prompt Caching (90% kedvezmény, $0.30/1M cached read, $1.02/1M context-chunk generation egyszer).
    - **Ritkított DSPy meta-eval** havonta 1-2 GEPA-ciklus aszimmetrikus modell-orchestrációval (olcsó generátor + okos reflektor) — futás-költség $1-2 alatt.

**Tier $500/hó — teljes agentic stack:**
- **MAXOL:** Full `notebooklm-mcp-cli` integráció (Claude Desktop / Cursor parancs-küldés). Folyamatos DSPy+GEPA a 11.11 crystallization-hook minden sprint-zárásnál. Premium Contextual Retrieval Claude Opus 4.7 ($5 input / $25 output / 1M token) cross-reasoning-re + OpenAI o3/o4-mini reasoning-modellek bekötése.

**Peti-vault konzisztens javaslat:** kezdjük **Tier $50** szinten — a vault még belefér 1 ingyenes notebookba, a NotebookLM CLI már él, a 11.11stop hook ultra-budget API-ra ráköthető. Cross-projekt synthesis havi 1× akkor amikor a $200/hó tier-be lépünk. A $500-os teljes stack csak akkor érdemes, ha a vault meghaladja az 1-notebook kapacitást (több projekt aktívan + bőséges audio-overview konzumálás).

### Phase A+ konkluzió — mit változtat a Phase B roadmap-en

A Phase A 6 Sprint-tervhez 3 új konkretizálás:

1. **Sprint 1 (per-projekt notebook-pool)** — VALIDÁLÓDOTT, Tier $50-ban már él. **Új tech-döntés:** ne csak a `notebooklm` CLI, hanem a **`notebooklm-mcp-cli`** legyen a stratégiai cél a Sprint 5-6 közben, mert MCP-bridge → Claude Code/Desktop közvetlen utasítás.
2. **Sprint 3 (11.11stop crystallization-hook)** — ÚJ explicit: a hook **NEM csak source-add**, hanem **DSPy signature-be deklarált learnings-extract** + opcionális GEPA meta-eval (havi 1-2 ciklus). A Karpathy crystallization + DSPy Context Engineering közös metszete.
3. **Sprint 6 (source-pool curation)** — ÚJ konkrét limit: **Plus-tier 300 source/notebook**, a ~240 fájlos vault NEM nőhet korlátlanul egy notebookban. Watching limit: **240 → 280** között proaktív partícionálás (per-projekt szubnotebook-ok). A foundational-prioritás (⭐⭐⭐/⭐⭐/⭐) marad érvényes minőség-stratégiaként.

**Új ADR-kandidátus:** „`notebooklm-mcp-cli` mint stratégiai bridge a Claude Code ↔ NotebookLM között + DSPy GEPA havi 1× meta-eval ciklus" — Tier $200 tier-átlépéskor írandó.

**Self-referential megjegyzés:** az SV-1..SV-8 research bizonyíték önmagában a tengely hipotézisére — a 8 NotebookLM-notebook + **~2700 forrás** + 56+ kérdés produktálta a 2300+ sornyi wiki-tartalmat 1 nap alatt. A Phase A+ source-burst (30 → 1200) **az 1,5M szavas kontextusablak gyakorlati skálázhatóságának** a saját bőrünkön tapasztalt validálása.

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható a SV-8 forrásokról. Phase A végén futtatandó:

```bash
notebooklm generate audio -n a60d993b-1926-40cc-b947-94b3ef663f00
```

## Akció-pontok ehhez a tengelyhez

- [ ] Audio overview generálás + letöltés (~15 perc compute, MP3 commute-podcast)
- [ ] Phase B Sprint 1: per-projekt NotebookLM bootstrap-script (`notebooklm-bootstrap-project`)
- [ ] Phase B Sprint 3: 11.11stop crystallization-hook NotebookLM-meta-notebookba (legmagasabb prioritás — a SV-5 + SV-8 közös metszete)
- [ ] Phase C: cross-projekt synthesis havi cron + új `11-wiki/cross-project-synthesis-*.md` template
- [ ] Független verifikáció: NotebookLM Plus konkrét ár 2026, Enterprise API endpoint-szettje
- [ ] Risk-mitigation ADR: ha Google policy-változás letiltja a community-CLI-t, fallback Anthropic Contextual Retrieval RAG-stackre

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — a 8-tengelyes roadmap
- [[10-raw/2026-05-12 — Superintelligence research source pool]] — a research forrás-pool
- [[11-wiki/notebooklm-headless-login-fifo]] — meglévő auth-pattern (Peti-vault)
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — meglévő 17×7 research-workflow (Peti-vault)
- [[11-wiki/sv-01-memory-architecture]] — a NotebookLM mint **semantic-memory réteg** a hierarchikus memory-pattern-ben
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a „compilation" elv amit a NotebookLM Audio Overview generálási folyamata közvetlen analógia
- [[11-wiki/Crystallization-protocol]] — a Sprint 3 (11.11stop hook) integrációs pontja
- [[11-wiki/cloakbrowser-fingerprint-bypass]] — fallback ha Cloudflare/Turnstile blokk
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[web-speech-api-continuous-stt]] (sem-rokon, score=0.56)
## NotebookLM-konverzáció

- **Notebook ID:** `a60d993b-1926-40cc-b947-94b3ef663f00`
- **Notebook cím:** `SV-8 NotebookLM cognitive layer`
- **Conversation ID:** `c82edbb5-cbab-42d5-bc0d-33a88f875a2f`
- **Források (Phase A):** 30 (20 manuál + 10 add-research)
- **Források (Phase A+):** **1200** (30 + 4× deep-research import ~1170 új forrás)
- **Kérdések:** Phase A 7/7 + Phase A+ 3/3 (10 összesen)
- **Q-output fájlok (tmp):** `/tmp/sv-research/sv8-q{1..7}-*.txt` (Phase A) + `/tmp/sv-research/sv8-phase-a-plus-q{1,2,3}.txt` (Phase A+)
- **Add-research Phase A:** R1 task `82ff3dc3-9263-4761-8897-b39b3cbd2efd` failed-to-start (retry pending); R2 task `7bd4d94b-...` 502-hibázott, retry után 10 source importálva
- **Add-research Phase A+:** R1 `303a6340-...` DSPy/AgentInstruct (~142 source); R2 `682951dd-...` NotebookLM API Enterprise (Phase A+ első batch); R3 `06f72cf3-...` Claude Projects vs Contextual Retrieval (~36 source); R4 `deab30fa-...` citation-grounded RAG. IMPORT_RESEARCH timeout-ok és 502-k retry-loop-ban kezelve, source-count 30 → 1200 (40×)
