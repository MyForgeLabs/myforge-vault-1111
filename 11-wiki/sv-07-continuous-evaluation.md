---
name: SV-7 Continuous evaluation
type: wiki
tags: ["#type/wiki", "agi", "evaluation", "benchmark", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: done
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: d6e26ab3-3053-4eb8-a000-b3f53b83ebee
---

# SV-7 — Continuous evaluation

A 8-tengelyű szuperintelligens-vault evolúciós research hetedik cikke. **Kérdés:** hogyan kapjon minden session/projekt automatikus metrikákat — siker, tanulság-pontosság, stuck-detection — úgy, hogy a benchmark-trend láthatóvá tegye a vault és a benne dolgozó agentek fejlődését hónapról hónapra.

> **Status:** 7/7 kérdés válaszolva. NotebookLM-források: 35 (SWE-bench, AgentBench, HELM, MT-Bench, GAIA, tau-bench, AgentInstruct, OpenHands, Inspect AI, Braintrust, DSPy, Anthropic agents, Hamel Husain + Eugene Yan eval-blogok, MLPerf, plus 2 add-research bővítés). Audio overview generálandó (Phase A végén batch).

## 1. A tengely magja

Az LLM-agentek kontextusában a **continuous evaluation** egy átfogó paradigma, amely a modellek és agentek teljesítményének **szisztematikus, iteratív és a teljes életciklusra kiterjedő mérése** — a fejlesztői tesztkörnyezettől a CI/CD-automatizáción át egészen a produkciós monitoringig. A **"continuous"** szó arra utal, hogy a validáció nem egyszeri esemény, hanem soha véget nem érő körforgás: prompt- vagy kódváltozáskor azonnal lefutó automatikus tesztek, élő trace-megfigyelés, és szintetikus + valós adatokon alapuló iteratív hibajavítás. Az **"evaluation"** ezen belül a minőség és megbízhatóság objektív mérése — determinisztikus unit-testekkel, doménszakértői review-val vagy "LLM-as-a-judge" módszerekkel — a regressziók kiszűrése és az elvárt viselkedés garantálása érdekében.

A paradigma szervesen kapcsolódik a vezető benchmark-családokhoz:

- **SWE-bench** valós GitHub-issue-kat oldat meg, kódmegértés + szerkesztés + teszt-futtatás iteratív ciklusát követelve;
- **AgentBench** interaktív, többlépéses környezetekben mért érvelést és döntéshozatalt, ahol a környezeti visszacsatolás elengedhetetlen;
- **HELM** (Stanford) folyamatosan bővülő "living benchmark"-ként új scenario-kkal frissül;
- **Anthropic** az értékelést magába az agent-architektúrába emeli az ún. **"evaluator-optimizer"** workflow-val: egy második modell folyamatos feedback-loop-ban bírálja és javítja a fő agent kimenetét, plus a fejlesztők dedikált sandbox-okban tesztelnek.

> "Given a codebase along with a description of an issue to be resolved, a language model is tasked with editing the codebase to address the issue." — SWE-bench (Jimenez et al. 2023)

> "Strong LLM judges like GPT-4 can match both controlled and crowdsourced human preferences well, achieving over 80% agreement, the same level of agreement between humans." — MT-Bench (Zheng et al. 2023)

## 2. Kanonikus megközelítések (5 fő benchmark-család)

### SWE-bench (Jimenez et al. Princeton 2023; Verified 2024; Multimodal 2025)
- **Mit mér:** Az LLM képességét, hogy valós szoftverfejlesztési problémákat (GitHub-issue + kódbázis) oldjon meg.
- **Hogyan:** Konténerizált Docker-környezet, a modell egy patch-et generál, ami a kódot fixeli; a rendszer reprodukálható módon lefuttatja a teszteket.
- **Kulcs-újdonság:** Túllép az izolált kódgenerálási feladatokon — több függvényen, osztályon, fájlon átívelő változtatás + környezeti interakció + extrém hosszú kontextus.

### AgentBench (Liu et al. 2023)
- **Mit mér:** Az LLM mint autonóm agent (LLM-as-Agent) érvelési és döntéshozatali képességeit.
- **Hogyan:** 8 különböző interaktív környezet, multi-dimenziós keretrendszer; API-alapú és nyílt modellek tesztelése környezeti visszacsatolásra reagálás alapján.
- **Kulcs-újdonság:** Drasztikus szakadékot mutatott meg a kereskedelmi és a <70B nyílt modellek között; azonosította, hogy a long-horizon reasoning, döntéshozatal és instruction-following okozza a legtöbb hibát.

### HELM — Holistic Evaluation of Language Models (Liang et al. Stanford 2022, élő benchmark)
- **Mit mér:** A nyelvi modellek holisztikus minőségét — accuracy mellett kalibráció, robusztusság, fairness, bias, toxicitás és hatékonyság.
- **Hogyan:** Multi-metric framework, 87,5%-ban mind a 7 fő metrikát méri a 16 alap-scenario-n, plus 26 célzott scenario (reasoning, dezinformáció stb.).
- **Kulcs-újdonság:** Standardizált tesztkészlet nyílt és zárt modellekre, kompromisszumok (accuracy vs bias) explicit kimutatása. **"Living benchmark"** — folyamatosan új metrikákkal és feladatokkal bővül.

### LLM-as-a-judge: MT-Bench és G-Eval (Zheng et al. 2023; Liu et al. 2023)
- **Mit mér:** Csevegőasszisztensek és NLG-modellek válaszainak minőségét nyitott végű, többfordulós dialógusokban — emberi preferenciákkal való illeszkedés.
- **Hogyan:** Erős LLM (pl. GPT-4) mint bíró, chain-of-thought + form-filling logikával, előre megírt humán referencia nélkül.
- **Kulcs-újdonság:** Skálázható és magyarázható közelítése az emberi preferenciáknak — 80%+ egyetértés a humán értékelők közötti egyetértési szinttel. Felülmúlja a BLEU/ROUGE-szerű klasszikus metrikákat kreatív/diverz feladatoknál.

### WebArena (Zhou et al. CMU 2023)
- **Mit mér:** Autonóm web-agentek funkcionális helyességét valós webes feladatokon.
- **Hogyan:** Teljesen működőképes weboldalak (e-commerce, fórum, software-dev, CMS) reprodukálható, interaktív környezetben; az agenseknek térképek és szoftveres útmutatók segítségével kell emberi szintű feladatokat megoldaniuk.
- **Kulcs-újdonság:** Szigorúan valósághű, long-horizon mindennapi munkafolyamatok. Hatalmas szakadékot mutatott: emberek 78,24%, GPT-4-alapú agent 14,41% sikerráta.

> **Megjegyzés:** A NotebookLM **tau-bench**-et és **GAIA**-t a Q4-ben mint friss áttöréseket említi — lásd 4. szekció.

## 3. Tech-stack opciók 2026-ban

A continuous evaluation jelenleg **3 réteg**-et fed le, és minden réteghez 1-2 production-ready opció létezik:

### Off-the-shelf SaaS platform — gyors integráció

| Eszköz | Hatókör | Tradeoff |
|---|---|---|
| **Braintrust** | Teljes életciklus: dev-iteráció (Playground), CI/CD-eval per pull-request, online scoring (async produkciós log-pontozás) | SDK-alapú integráció, dobozos megoldás. Licencköltség, de a scorer-eket és prompt-okat testre kell szabni |
| **Inspect AI** (UK AISI) | Python open-source framework — Datasets + Solvers + Scorers összeláncolva, `@task` decorator, CLI + VS Code-extension, agent-sandbox Docker/Kubernetes | Ingyenes, 200+ beépített benchmark; futtatási infrastruktúra (Docker-env-fenntartás) a csapaté |

### Domain-specifikus LLM-as-a-judge — custom

| Eszköz | Hatókör | Tradeoff |
|---|---|---|
| **Hamel Husain / Eugene Yan-féle DIY pattern** | Egyedi data-viewer (Streamlit/FastHTML) a LangSmith-trace-eken, doménszakértő bináris (Pass/Fail) döntéseket + kritikákat ír → few-shot judge-prompt | Maximálisan testreszabott, elveti a megbízhatatlan 1-5-skálát. Alacsony szoftverköltség, magas humán-idő-ráfordítás. Cél: 90%+ ember-gép egyetértés |
| **DSPy** (Khattab et al. 2023) | Deklaratív self-improving pipeline; a fix prompt-template-eket modulokra cseréli, a "compiler" automatikusan optimalizál egy metrikát maximalizálva | Meredek tanulási görbe, magas refactor-költség meglévő projekten — cserébe automatizált prompt-engineering |

### Foundation-model és infrastructure benchmark — szabványos

| Eszköz | Hatókör | Tradeoff |
|---|---|---|
| **HELM** | Statikus CLI: foundation-model tesztelése 42+ scenario-n (accuracy, kalibráció, toxicitás, bias) | Ingyenes, de a futtatás compute-igényes. Az alkalmazás-specifikus üzleti logikát nem méri |
| **OpenHands eval suite** | Konténerizált környezet kód-író/böngésző agenteknek — SWE-bench és WebArena direkt-csatlakozással | MIT-licenc, szűk hatókör (kód + böngészés). Robusztus Docker-env-futtatás drága cloud-compute |
| **MLPerf Inference (Datacenter)** | DevOps-réteg: latency, throughput, energiafogyasztás szabványos load-generator-okkal | Drága, nehézkes hardware-setup. Csak rendszer-architektúra szintjén mér, nem agent-logikán |

### Anthropic paradigma (külön kiemelve)
Az Anthropic nem ad dedikált "continuous-eval Foundry" terméket, hanem **architekturális mintát** ajánl: az "evaluator-optimizer" workflow-t — a fő agent mellett egy második LLM feedback-loop-ban kritizál és javít. Értékelésnél kód-alapú (egzakt egyezés) vagy egyértelmű rubrikás LLM-as-judge pontozást preferálnak. A költség futásidőben magasabb (extra LLM-hívások).

> **NotebookLM-szintézis:** "Production-LLM-agent projekthez 2026-ban az optimális kombináció a **Hamel/Yan-féle DIY LLM-as-judge** módszertan az alapoknál, majd **Braintrust** felskálázásra a CI/CD + log-elemzéshez. Komplex tool-use/kódfuttatás méréséhez az **Inspect AI** a legmodernebb open-source standard."

## 4. Friss áttörések 2024-2026

A pre-2024 korszak statikus, vizsgaszerű QA-tesztjeit fundamentális paradigmaváltás követte. Fókusz: valós idejű, dinamikus, ellenőrzött (verified), és **uncontaminated** (titkos) tesztek.

### Leaderboard-hardening — contamination ellen
- **SWE-bench Verified** (2024-08, OpenAI Preparedness + SWE-bench team): 500 humán-validált GitHub-issue, ami emberek által megerősítetten egyértelműen megoldható. Kiszűrte a zajos, rosszul specifikált feladatokat.
- **SWE-bench Multimodal + privát tesztek** (2025-01): a teszt-split **teljesen titkos**, training-leakage-bypass; értékelés Modal-felhőn, szigorúan sandboxolt Docker-környezetben.

### Dinamikus interakciók és megbízhatóság
- **tau-bench** (2024): Tool-Agent-User-interakciók valós üzleti kontextusban (retail). Kulcs-újdonság a **pass^k metrika** — méri, hogy az agent **következetesen** megoldja-e a feladatot k egymást követő próbálkozás során. Kimutatta, hogy GPT-4o-szintű agentek is rendkívül inkonzisztensek (25% alatti pass^8 retail-en).
- **GAIA** (2023-vége, 2024-ben dominált): konceptuálisan egyszerű emberi feladatok, amikben az agentek hatalmas szakadékot mutatnak (humán 92% vs GPT-4-pluginnel 15%). Multi-modal + web-browsing + tool-use mix.

### Generative teaching — szintetikus adat
- **AgentInstruct** (Mitra et al. Microsoft 2024): ágens-vezérelt framework, automatikusan 25 millió diverz szintetikus tréning-pár nyers forrásokból. Nem csak értékel, hanem a *generative teaching* paradigmájával post-training-et hajt: Mistral-7b → Orca-3 akár 54%-os javulás reasoning-benchmark-okon.

### LLM-as-judge fejlődés — generikus pontozástól a critique-shadowingig
A 2023-as G-Eval és MT-Bench bizonyította a 80%-os humán-egyetértést, de a 2024-25-ös iparági gyakorlat **túlment** a megbízhatatlan 1-5-skálákon:
- **Bináris (Pass/Fail) döntés + részletes critique** — Hamel Husain, Eugene Yan iskolája.
- **Critique Shadowing** — doménszakértő (ügyvéd, orvos) "árnyékolja" a gép kritikáit, addig finomítva a prompt-ot, amíg az egyezés 90%+ nem lesz. Eugene Yan **AlignEval** eszköze pontosan ezt segíti.

> **Összegzés:** A 2024 előtti statikus vizsgaszerű QA-t felváltotta a konténerizált interaktív sandbox-eval (OpenHands, SWE-bench) + szintetikus adatgeneráció (AgentInstruct) + dinamikus user-szimuláció (tau-bench) + szigorúan kalibrált LLM-judge-ok kombinációja.

## 5. Failure-modes és limitációk

A continuous evaluation **nem csodaszer** — rosszul alkalmazva hamis biztonságérzetet ad. A 6 fő failure-mode:

### Goodhart-törvény és "tools trap"
Hamel Husain figyelmeztet: a csapatok elesnek a dashboardok és off-the-shelf metrikák varázsától, miközben a valós felhasználói hibákat nem nézik. *"Olyan, mintha a weboldal betöltési idejét optimalizálnád, miközben a fizetési folyamat rossz — a rossz dologban leszel egyre jobb."* Az 1-5-skálák zajosak, nem cselekvésre-ösztönzőek — bináris Pass/Fail az optimális.

### LLM-as-judge torzítások
- **Self-favoritism:** a G-Eval-tanulmány kimutatta, hogy az LLM-judge-ok elfogultak a saját maguk (vagy hasonló modell) által generált szövegekkel szemben.
- **Pozíciós + formázási bias:** a modellek megtéveszthetők a válaszlehetőségek sorrendjével vagy a prompt látszólag ártalmatlan formázási eltéréseivel.
- **Insensitivity:** Eugene Yan szerint a G-Eval gyakran alacsony recall-lel rendelkezik, finom tényszerű inkonzisztenciát nem ismer fel.
- **Over-trust:** az emberek hajlamosak túlságosan megbízni az AI önértékelésében (különösen amikor GPT-4 saját magát osztályozza).

### Criteria drift
Az AI-fejlesztés paradoxona: az értékelési szempontokat lehetetlen tökéletesen előre meghatározni anélkül, hogy ne látnánk rengeteg kimenetet. Ahogy a doménszakértők és felhasználók többet használják a rendszert, új edge-case-ek bukkannak fel, és újra-definiálják, mi a "jó" válasz. A statikus benchmarkok ezt nem követik le.

### Reprodukálhatóság hiánya
Az LLM-ek nem determinisztikusak — temperature + sampling folyamatos zajt visz. A tau-bench pass^8-metrikája megmutatta: GPT-4o-szintű agentek retail-feladatban 25% alatti megbízhatóságot mutatnak 8 ismétlésen át.

### Contamination / leakage
A publikus benchmarkokra (HumanEval, régi SWE-bench) optimalizálás klasszikus limitáció — a teszt-adat beszivárog a training-corpus-ba. A modern megoldás: titkos teszt-split (SWE-bench Multimodal 2025) + dedikált zárt eval-cloud (Modal).

### Cost & compute
- **Humán:** doménszakértői review a legpontosabb, de drága és lassú, hosszú távon fenntarthatatlan.
- **Gépi:** SWE-bench futtatása konténerenként akár 120 GB disk + 16 GB RAM + 8 CPU. Plus a long-horizon agent-trajektóriák több száz LLM-hívása.

> **Mit NEM old meg a continuous eval?** Nem ad megoldást a fundamentálisan hibás termék-/prompt-architektúrákra vagy az irreális elvárásokra (pl. "oldjon meg a chatbot mindent"). Nem pótolja a józan emberi iterációt: maga az LLM-bíró önmagában nem teremt értéket — *"egy drága LLM-eval-eszköztár megvétele gyakran csak egy trükk, hogy végre rávegyük a csapatot, valóban nézzen bele a saját adataiba"* (Hamel Husain).

## 6. Implementációs lépések a Peti-vault kontextusban

A vault adottságai:
- **240+ fájl**, Obsidian-Markdown
- **11.11 session-protokoll** — `08-Sessions/<slug>.md` fájlonként, kötelező `## Summary` / `## Learnings` / `## Next` szekciókkal
- **Heti vault-health-audit** — `06-Audits/System_Health.md` cron-generálva (vasárnap 04:00, `vault-cleanup` script)
- **280+ skill**, multi-agent setup (Claude/Codex/Gemini)
- **Auto-mode crystallization** session-záráskor — `## Propagation log`

A NotebookLM-szintézis szerint **3-szintű eval-pipeline** illeszkedik ehhez a struktúrához:

### Mit mérjünk

| Metrika | Definíció | Forrás |
|---|---|---|
| **Session-szintű siker** | Bináris Pass/Fail + critique (NEM 1-5 skála!) | LLM-judge a `## Summary` + `## Learnings` + `## Next` szekciókon |
| **Learnings-extraction pontosság** | Két dimenzió: (a) tényszerű konzisztencia — nem hallucinált-e ki a `## Learnings`-be olyat, ami a sessionben nem történt; (b) relevancia — a legfontosabbat emelte-e ki | NLI-alapú judge összeveti a Learnings-t a nyers trace-szel |
| **Agent stuck-detection** | Determinisztikus: ismétlődő tool-call-ok, context-window-betelés, hosszú eredmény-nélküli futás | Regex + counter a session-trace-en |
| **Vault-coherence-drift** | Az új `## Learnings` és `## Summary` szekciók mennyire ellentmondanak a korábbi sessionöknek vagy a 280 skill-szabályoknak | Semantic-similarity + LLM-judge |

### Implementációs sprintek

#### Sprint 1 — Level 1 unit-test (determinisztikus parser)
Gyors, olcsó, kód-alapú ellenőrzések minden új `08-Sessions/` fájl létrejöttekor.

**Script:** `scripts/eval_l1_parser.py`
- *Assert 1:* Tartalmazza-e a `## Summary`, `## Learnings`, `## Next` szekciókat
- *Assert 2 (stuck-detection):* Regex a nyers trace-en — ugyanaz a tool/skill-hívás vagy hibaüzenet ismétlődik-e ≥3-szor egymás után
- *Assert 3:* `## Learnings` szekció bullet-szám 0 < n < 20 (alsó és felső sanity-limit)

**Output:** `06-Audits/L1_Stuck_Alerts.csv` + `#review-needed` tag a hibás session-fájlon

#### Sprint 2 — Data viewer + emberi baseline
Mielőtt automatizálnánk, építsünk minimális UI-t a manuális review-ra.

**Script:** `scripts/vault_trace_viewer.py` (Python Streamlit vagy FastHTML)
- Egy képernyőn mutatja: aktuális `08-Sessions/<slug>.md`, behúzott skill-ek, system-kontextus
- **Pass / Fail gomb + 1-2 mondatos critique-mező**
- Heti 10-20 session manuális értékelés

**Output:** `06-Audits/Human_Ground_Truth.jsonl` — ez az LLM-judge betanítási alapja

#### Sprint 3 — LLM-as-judge "critique shadowing"
Amint van baseline (30-50 elemes minta), átadjuk a feladatot egy erős LLM-nek (GPT-4 / Claude Opus 4.7).

**Script:** `scripts/eval_l2_llm_judge.py` (aszinkron a friss `_archive/` session-eken)
- A judge prompt-ja **few-shot** példaként betölti a `Human_Ground_Truth.jsonl` legjobb kritikáit (ez a "critique shadowing")
- NLI-logika: `## Learnings` (hipotézis) vs nyers session-log (premissza) → ténybeli inkonzisztencia-flag
- **Cél:** 90%+ egyezés a manuális Pass/Fail-lel — addig finomítjuk a judge-prompt-ot

**Output:** új frontmatter-mezők a session-fájlokon:
```yaml
eval_score: Pass
eval_critique: "A kódot jól megírta, de a ## Next szekció hiányos."
hallucination_flag: false
```

#### Sprint 4 — Metrika-aggregálás a heti auditba
A meglévő `vault-cleanup` cron kiegészítése.

**Script:** `scripts/generate_system_health.py` (kiegészítve az L1/L2 outputtal)
**Output:** `06-Audits/System_Health.md` új szekciói:
- Hetes pass-rate trend (line-chart Mermaid)
- Top-5 leggyakoribb failure-pattern
- Hallucination-rate per agent (Claude/Codex/Gemini)
- Stuck-detection alerts az utolsó 7 napra

### Baseline + target

- **Baseline:** a Sprint 2-ben gyűjtött 30-50 elemes `Human_Ground_Truth.jsonl` — induló pass-rate + hallucination-arány
- **Alignment target:** LLM-judge ↔ humán Pass/Fail **≥ 90%** egyezés (iteratív judge-prompt-finomítás)
- **Rendszer-target (reális):**
  - Pass-rate rutin feladatokon: **>80%**
  - Pass-rate új/ismeretlen problémákon: **>60%**
  - Hallucination-rate (`## Learnings` ténybeli inkonzisztencia): **<10%**, ideális esetben <5% (2% alá vinni rendkívül nehéz)

### Kapcsolódás a meglévő struktúrához

| Vault-elem | Eval-szerep |
|---|---|
| `08-Sessions/<slug>.md` `## Summary` / `## Learnings` / `## Next` | A bináris Pass/Fail + critique forrása |
| `08-Sessions/_archive/` | Az L2 LLM-judge backfill-target-je (történelmi pass-rate) |
| `06-Audits/System_Health.md` (heti cron) | A 4-es sprint outputjának landing page-je — "Sikermetrikák" tábla a roadmap-ADR-ből |
| `## Propagation log` szekciók a session-fájlokban | Crystallization-velocity metrika forrása (SV-5 tengellyel közös) |
| `Frontmatter — eval_score / hallucination_flag` | Új YAML-séma kiegészítés a [[00-Meta/Frontmatter-schema]]-ben |

A roadmap-ADR-ben szereplő **"Sikermetrikák"** tábla (Phase C végén mérendő) direkt forrása ez a pipeline: a `Context-loading idő`, `Crystallization auto-rate`, `Recall`, `Knowledge crystallization velocity` mind az `eval_l1_parser.py` + `eval_l2_llm_judge.py` outputjából aggregálódik a `System_Health.md`-be.

## 7. Mit kell tovább kutatni?

A források alapján a következő 6-12 hónap kutatási irányai és a NotebookLM-ben felfedett open-kérdések:

### Meta-evaluation — ki értékeli az értékelőket?
Shreya Shankar et al. *"Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences"* (2024) — a **criteria drift** jelenség formális kezelése. Jelenleg nincs jó eszköz a validátorok minőségének automatikus ellenőrzésére, ez over-trust-hoz vezet. Phase B-re kötelező olvasmány.

### Agent-trajectory eval — több, mint a végeredmény
- **MT-Bench-101** — finomszemcsés multi-turn dialógus-eval
- **tau-bench pass^k metrika** — következetesség és reliability a teljes trajektórián
- Új kutatási kérdés: hogyan büntessük az agent-et a felesleges lépésekért (tool-call loops), és hogyan jutalmazzuk a hibákból való sikeres recovery-t?

### Self-improving pipeline-ok és RLHF-helyettesítők
- **DSPy** — automatikus prompt + súly-optimalizálás deklaratív gráf alapján
- **AgentInstruct** — generative teaching: erős agentek generálnak szintetikus oktató-adatot kisebb modellek post-training-jéhez. **Open kérdés:** *modell-összeomlás (model collapse)* elkerülése + szintetikus-adat kiterjedt automatizált értékelése

### World-model-grounded és execution-based eval
- **WebArena** funkcionális weboldalakkal, **OpenHands + SWE-bench** Docker-konténerekkel
- Várható kutatási fókusz: standardizált sandbox-környezetek, automatikus ground-truth-kiolvasás (pl. DB-állapot-ellenőrzés tau-bench-ben), multi-modal (vision-based) browsing-eval

### Living benchmarks és contamination
A HELM-paradigma + új SWE-bench-frissítések a **living benchmark** irány felé mutatnak — privát teszthalmaz, folyamatos cloud-bővítés (Modal). **Open kérdés:** hogyan publikálható egy benchmark anélkül, hogy gyorsan elavulna a contamination miatt?

### Olvasandó listák a Phase B-re

1. **Shreya Shankar et al. — *"Who Validates the Validators?"*** — criteria drift formális definíció és heti vault-audit-relevancia
2. **Eugene Yan — *AlignEval* és *"Task-Specific LLM Evals that Do & Don't Work"*** — NLI-alapú hallucination-mérés a `## Learnings` szekciókra
3. **Jason Liu — *Evaluating RAG & Data Literacy* írások** — a vault mint RAG knowledge-base értékelése külön a retrieval-pontosság és a generation-quality dimenziókban
4. **Yi Liu et al. — *"Enhancing LLM-As-A-Judge with Grading Notes"*** — empirikus bizonyíték a few-shot grading-notes drámai hatására az L2-judge-promptban
5. **Dosu / LangChain Case Study — dinamikus few-shot példák** — a judge-prompt-ba a *leghasonlóbb korábbi hibát* húzzuk be példaként a vault történetéből
6. **Eric Xiao (Arize) — *"Techniques for Self-Improving LLM Evals"*** — önjavító eval-loopok dedikált szoftver nélkül, log-alapon (passzol a `08-Sessions/` mappához)

## Phase A+ bővítés (2026-05-12 deep-research)

Phase A után (78 forrás) +4 deep-research kör futott le a NotebookLM-en (`d6e26ab3-3053-4eb8-a000-b3f53b83ebee`), forráspool **78 → 395** (+317). Témák: SWE-bench Verified 2026 leaderboard, agentic eval-frameworks (Promptfoo / Braintrust / Langfuse), LLM-judge bias/calibration, Hamel Husain + AlignEval + Eugene Yan production-patterns. Alább a 3 mély-kérdés szintézise — minden állítás a 395-forrásos pool-ból van idézve.

### 1. Mely 3 architektúra-elem KOMBINÁCIÓJA ad a legtöbb értéket — és milyen sorrendben?

A források szerint **NEM az automatizációval kell kezdeni**, hanem a saját adatok manuális nézegetésével — az AI-csapatok legnagyobb hibája, hogy nem nézik át a nyers logokat (Hamel Husain). Sorrend:

**Lépés 1 — Súrlódásmentes adatnézegető + Critique Shadowing baseline (Alapozás).** Bináris (Pass/Fail) döntéseket + részletes emberi kritikákat (critiques) gyűjts az `08-Sessions/` fájlokról, 1-5 skála helyett. **Tech-stack:** Braintrust (offline dataset + trace + dedikált manual-review felület), vagy egyedi pehelysúlyú Markdown-nézegető. **Vault-implementáció:** heti audit előtt 20-30 munkamenetet átnézel, rögzíted a `## Summary` és `## Learnings` Pass/Fail-jét + a "miért"-szöveges indoklást. Ez adja a manuális ground-truth-ot a későbbi judge-kalibrációhoz.

**Lépés 2 — LLM-Judge kalibráció + NLI tényellenőrzés (Automatizálás).** Eugene Yan kutatása alapján a `## Learnings` hallucináció-mentességére az **NLI (Natural Language Inference)** modellek a legcélravezetőbbek. **Tech-stack:** AlignEval (Eugene Yan tool — emberi vs gépi értékelés gyors összehangolása) + Claude Opus 4.6 vagy GPT-5.4 mint bíró-modell (Opus 4.6 = 80.8% SWE-bench Verified, 1M token kontextus). **Vault-implementáció:** a Lépés 1-ben gyűjtött kritikákat dinamikus few-shot példaként betáplálod a judge-promptba (= Hamel Husain "Critique Shadowing"). AlignEval-lel iterálod a promptot, amíg ≥90%-os egyezést el nem ér a te ítéleteiddel. Az NLI-réteg külön ellenőrzi: a `## Learnings`-ben nincs-e olyan állítás, ami a nyers session-logban nem szerepelt.

**Lépés 3 — Agentic scaffold + szemantikus keresés (Skálázás + rendszer-szintű audit).** A 2026-os SWE-bench Pro/Verified legfontosabb tanulsága: a modell-képesség önmagában kevés, a scaffold (harness, tool-use, context-retrieval) a pontszám **felét** teszi ki — ugyanaz a modell akár 22 pontot zuhanhat gyenge scaffold mellett. 240+ fájl koherencia-vizsgálatához a bírónak keresési-eszközei kellenek. **Tech-stack:** WarpGrep (vagy hasonló szemantikus AI-kereső subagent, párhuzamos eszközhívások, drasztikusan kisebb token-cost) + Braintrust Online Scoring (aszinkron pontozás élő trace-ekre). **Vault-implementáció:** a heti `System_Health.md` cron Braintrust online-scoring módban aktiválja az LLM-bírót az új session-fájlokon, WarpGrep végigpásztáz ~240 fájlon → "Vault-coherence-drift" ellenőrzés (az új tanulság nem mond-e ellent korábbi 280+ skill-definíciónak vagy ADR-nek).

**Összegzés:** Braintrust manual review → AlignEval-kalibrált Opus-bíró + NLI → WarpGrep + Braintrust online-scoring. Sorrend kötelező — ha rögtön L2-3-mal kezdesz, single-metric csőlátás lesz.

### 2. Production-ready vs akadémiai stádium (források alapján)

**Akadémiai / statikus benchmarkok** (modellszelekcióra jók, vault-produkcióra NEM):

- **SWE-bench Verified** — 2024-ben arany standard, 2026-ra **contaminated + saturated** (Claude Mythos Preview = 93.9% rekord). OpenAI nyilvánosan felhagyott vele, kiderült: modellek visszaöklendezik a tesztet az internetről. Iparág a **SWE-bench Pro** felé mozdult (kontamináció-védett).
- **GAIA** — General AI Assistants, mindennapi-logika tesztek. Tanulsága: **scaffold-függő** (Princeton HAL: Claude Opus 4 GAIA-pontszáma 57.6% és 64.9% között ugrál tisztán a keretrendszertől függően).
- **tau-bench** — dinamikus tool-agent-user szimuláció, `pass^k` metrika. Rávilágított: a legjobb agent-ek is inkonzisztensek (retail környezetben <25% konzisztencia).
- **AgentBench** — 2023-as klasszikus, 8 interaktív környezet, LLM-döntéshozó képesség.
- **HELM (Stanford)** — 42 forgatókönyv (Holistic Evaluation), statikus akadémiai keretrendszer, NEM CI/CD-eszköz.

**Production-ready** (Agent-Vault CI/CD-re alkalmas):

- **Braintrust** — teljes SaaS platform, CI/CD-be épül (offline eval) + Playground + **online scoring** (aszinkron pontozás éles trace-ekre, válaszidő-növelés nélkül). A 2026-os iparági fókusz erősen rajta van.
- **AlignEval (Eugene Yan)** — production-ready megoldás az LLM-as-a-judge legfőbb hibájára (emberi preferenciákkal összehangolás). Letisztult felület domén-szakértői bináris értékelésekhez + automatikus iteráció.
- **OpenHands** (ex-OpenDevin) — MIT-licenc, **konténerizált Docker-sandbox** kódoló-agent futtatáshoz + biztonságos kiértékeléshez (SWE-bench, WebArena futtatására is használják).
- **Anthropic Evaluator-Optimizer workflow** — nincs konkrét "Foundry" termék-név a 2026-os forrásokban, de hivatalos production-architektúraként ezt javasolják: külön bíró-LLM runtime-ban kritizálja és javíttatja a fő agent kimenetét.

**Promptfoo / Langfuse:** a 2026-os forrás-pool szövegszerűen nem említi őket nevesítve (a Braintrust dominálja a diskurzust), de a korábbi iparági kontextus alapján egyértelműen ugyanabba a production-ready CI/CD prompt-optimalizáció + observability kategóriába tartoznak.

**Legfőbb 2026-os konklúzió** (Uvik Software): *"A framework, ami megnyeri a saját benchmarkodat, az a framework, amit élesítened kell."* Public benchmarkra optimalizálás csapda. Vault-kontextusban a győztes kombó: **Braintrust + AlignEval + OpenHands-sandbox**.

### 3. Cost-sensitive budget-tier vágási stratégia

A források szerint LLM API + framework költségek autonóm agent-üzemeltetésben az opex **40-60%-át** is kitehetik — rossz eval-architektúra csendben megduplázza a kiadásokat.

**Tier 1 — $50/hó (költség-optimalizált):**
- **Megtart:** parser stuck-detection + cron-aggregálás (determinisztikus, kódalapú, **0 API-cost**). Streamlit Pass/Fail manuális review **kötelező** (a drága prémium-iterációkat ezzel váltjuk ki — humán review-idő-növelés a legolcsóbb tradeoff).
- **Levág:** benchmark feed teljes egészében. LLM-judge NLI-t le a drága modellekről (Opus, GPT-5.5).
- **Modell az NLI-bíróra:** havidíjas csomagok ($20-200) helyett tisztán token-alapú BYOK. "Nano" modellek (~$0.000006/hívás) vagy budget-frontier: DeepSeek V4-Flash ($0.14/$0.28 per 1M token), MiniMax M2.5 ($0.30/$1.20 per 1M).

**Tier 2 — $200/hó (kiegyensúlyozott hibrid):**
- **Megtart:** parser stuck-detection + cron-aggregálás. **Benchmark feed itt már beépíthető** az auditba költség nélkül.
- **Átalakít:** Streamlit Pass/Fail emberi munka csökkenthető, de nem hagyható el teljesen (kockázat). LLM-judge NLI stabilan bekerül — **80/20-as iparági szabály**: agent-forgalom és evaluation 60-80%-a olcsóbb/nyílt modellre, csak a nehezebb 20% eszkalál csúcsmodellre.
- **Modell az NLI-bíróra:** "workhorse" = Gemini 3.1 Pro ($2/$12 per 1M) vagy Claude Sonnet 4.6 ($3/$15 per 1M) — közel Opus-szintű pontosság **5×-ös cost-csökkentéssel**.

**Tier 3 — $500+/hó (frontier / teljes automatizáció):**
- **Megtart + bővít:** LLM-judge NLI itt teljesedik ki (legmélyebb context-alapú logikai tesztek). Cron + stuck-detection mellé **dedikált online scoring** + Braintrust "autoeval" + remote evals.
- **Levág:** Streamlit Pass/Fail manuális review drasztikus visszavágása. Prémium modellek >78% first-pass accuracy → humán review-ciklus rövidül → ellensúlyozza a magasabb token-költséget.
- **Modell az NLI-bíróra:** Claude Opus 4.7 ($5/$25 per 1M) vagy GPT-5.5 ($5/$30 per 1M), 1M-token kontextus garantálja a teljes Vault-coherence-eval-t. Claude Code Max eleve havi $200.

**Vault-applikáció (Peti kontextus, ~240 fájl, heti audit):** A Tier 2 ($200/hó) a sweet-spot — Sonnet 4.6 bíróval + heti review-rotációval, benchmark-feed havonta. Tier 1-en induljunk Sonnet helyett DeepSeek V4-Flash NLI-vel, és nézzük 1-2 hónapot, hogy a manuális Pass/Fail review-idő (Lépés 1 baseline) elviselhető-e — ha nem, lépés Tier 2-re.

### 4. Phase A+ → Phase B finomítás

A 3 új mély-szintézis **megerősíti és pontosítja** a Phase A action-pontokat:

- A `vault_trace_viewer.py` Streamlit (Phase B Sprint 2) helyett érdemes **Braintrust trial** kipróbálása először (offline dataset + manual-review UI ingyenes tier-ben) — ha beválik, kihagyja a custom Streamlit-fejlesztést.
- Az `eval_l2_llm_judge.py` (Phase B Sprint 3) prompt-pattern-je **explicit Critique Shadowing** legyen — Hamel Husain few-shot példa-beillesztés a Lépés 1 baseline-ból, nem generikus rubrika.
- A System_Health (Sprint 4) bővítése **"Vault-coherence-drift"** metrikával, amit a WarpGrep-szerű szemantikus scaffold mér — az új session-Learning ellentmond-e korábbi ADR-nek/skill-definíciónak.
- **Cost-tier döntés** előrehozva Sprint 1-re: induljunk Tier 1-en (DeepSeek V4-Flash), és csak ha 30 napos baseline alapján a review-burden tarthatatlan, akkor lépjünk Tier 2-re (Sonnet 4.6).
- **Új TODO:** OpenHands Docker-sandbox kiértékelése arra, hogy a self-improving eval-loopok (Eric Xiao mintája) hol futnak biztonságosan a vault-context-en kívül.

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható. Phase A végén batch-ben:

```bash
notebooklm generate audio -n d6e26ab3-3053-4eb8-a000-b3f53b83ebee
```

## Akció-pontok ehhez a tengelyhez

- [ ] **Phase B Sprint 1:** `scripts/eval_l1_parser.py` implementáció + integráció a `vault-cleanup` cron-ba
- [ ] **Phase B Sprint 2:** `scripts/vault_trace_viewer.py` (Streamlit) + heti 10-20 session manuális Pass/Fail review → `Human_Ground_Truth.jsonl` 30-50 elemig
- [ ] **Phase B Sprint 3:** `scripts/eval_l2_llm_judge.py` critique-shadowing few-shot prompt + alignment-iteráció ≥90%-ig
- [ ] **Phase B Sprint 4:** `06-Audits/System_Health.md` kiegészítés eval-metrikákkal (pass-rate trend, top-failure-pattern, hallucination-rate per agent)
- [ ] [[00-Meta/Frontmatter-schema]] kiegészítés: `eval_score`, `eval_critique`, `hallucination_flag` session-frontmatter-mezőkkel
- [ ] Olvasandó: Shankar et al. *"Who Validates the Validators?"* (criteria drift), Eugene Yan AlignEval + Yi Liu "Grading Notes" paper
- [ ] Audio overview generálás + letöltés
- [ ] Roadmap-ADR "Sikermetrikák" táblájának pontos baseline-számítása az első 30 historikus session-en (backfill az `_archive/`-ből)

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — Phase A → Phase B átmenet
- [[10-raw/2026-05-12 — Superintelligence research source pool]] — forrás-pool SV-7 szekció
- [[11-wiki/sv-05-crystallization-automation]] — testvér-tengely, közös pipeline-elem (Propagation-log → eval-input)
- [[11-wiki/Crystallization-protocol]] — a 11.11stop záró-protokoll, amit az eval-pipeline mér
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a vault alaprajza, amelynek koherenciáját az eval méri
- [[06-Audits/System_Health]] — a heti audit, ami az eval-output landing-page-je
- [[00-Meta/Frontmatter-schema]] — bővítendő `eval_*` mezőkkel

## NotebookLM-konverzáció

- **Notebook ID:** `d6e26ab3-3053-4eb8-a000-b3f53b83ebee`
- **Conversation ID:** `04f07598-16c9-46db-95ac-a4664a90ce4b`
- **Források:** 35 (33 statikus URL: arXiv-papers SWE-bench/AgentBench/HELM/MT-Bench/GAIA/tau-bench/AgentInstruct/OpenHands/HumanEval/MBPP/Spider/WebArena/LAB-Bench/G-Eval/DSPy + Hamel Husain és Eugene Yan eval-blogjai + Anthropic blog + Inspect AI + Braintrust + HELM + MLPerf + SWE-bench-Verified + OpenAI Anthropic Claude-Code best-practices + 2 add-research bővítés "agentic LLM evaluation framework 2026" és "continuous evaluation observability LLM apps")
- **Kérdések:** 7/7 válaszolva
- **Q-szövegek:** `/tmp/sv-research/sv7-q{1..7}-*.txt`
