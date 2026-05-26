---
name: SV-2 Recursive self-improvement
type: wiki
tags: ["#type/wiki", "agi", "recursive-self-improvement", "prompt-evolution", "skill-library", "sv-research"]
created: 2026-05-12
updated: 2026-05-17
status: done-phase-a-plus
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: a2425bc7-4786-46f4-9fe8-00fa9510177e
---

# SV-2 — Recursive self-improvement

A 8-tengelyű szuperintelligens-vault evolúciós research második cikke. **Kérdés:** hogyan lehet egy LLM-agent rendszert úgy felépíteni, hogy ne csak a feladatokat oldja meg, hanem **saját magát is fejlessze** — a promptját, a skill-jeit, akár a kódját — minden interakcióból tanulva, nem csak a Crystallization manuális confirmációs ciklusán keresztül.

> **Status:** 7/7 kérdés válaszolva (Phase A) + 3/3 mély-komplex kérdés válaszolva (Phase A+). NotebookLM-források: 55 → **1009 ready** a 4× `--mode deep` research után. Audio overview generálás elindítva. Phase A+ kész.

## 1. A tengely magja

A **rekurzív önfejlesztés** (recursive self-improvement, RSI) az LLM-agentek kontextusában az a képesség, amellyel a rendszer **autonóm módon elemzi és tökéletesíti saját működési logikáját, architektúráját és tanulási folyamatait**, minden iterációval egyre hatékonyabbá válva a további önfejlesztési ciklusokban. Túllép az ember által tervezett, fix meta-tanulási rutinokon: az agent nemcsak a feladatok kimenetét generálja, hanem a saját működését vezérlő belső struktúrákat is dinamikusan megváltoztatja a környezeti visszacsatolások és a hibák elemzése alapján.

### A 4 fő dimenzió

| Dimenzió | Mit változtat | Példa-architektúra |
|---|---|---|
| **Prompt evolution** | A feladat-promptokat és magukat a "mutációs promptokat" iteratívan finomítja evolúciós elveken | Promptbreeder, GEPA |
| **Skill library growth** | A sikeres interakciókat újrahasználható skillekké (kódokká, leírásokká) desztillálja egy dinamikus könyvtárba | Voyager, SAGE/SkillRL, Anthropic Agent Skills |
| **Self-reflection** | A modell visszamenőleg értékeli teljesítményét, nyelvi visszacsatolást generál a jövő javítására | Reflexion, Self-Refine, RISE |
| **Code self-modification** | Az agent futásidőben átírja a saját forráskódját, beleértve az önmódosításért felelős részeket is | Gödel Agent (monkey patching) |

### Az autonómia spektruma

A 4 dimenzió **autonómia-spektrumot** jelöl: a prompt-evolution a legenyhébb (statikus súlyokkal, csak szöveg-szinten változik), a code-self-modification a legradikálisabb (futásidejű kódbeavatkozás, "nincsenek mesterséges emberi korlátok"). A Gödel Agent paradigmatikusan demonstrálja a felső véget: dinamikus memóriamanipulációval (monkey patching) elemzi és írja át a saját kódját, beleértve **azokat a kódrészeket is, amelyek a saját elemzéséért és önmódosításáért felelősek**.

## 2. Kanonikus megközelítések

### STaR — Self-Taught Reasoner (Zelikman et al. 2022, Stanford)
- **Mechanizmus:** Kis chain-of-thought példakészletből indulva a modell válaszokat + indoklásokat generál rengeteg kérdésre; ha hibázik, a helyes válasz ismeretében újra próbálkozik; a sikeres indoklásokon finomhangolja magát.
- **Kulcs-újdonság:** Kiküszöböli a hatalmas, emberek által írt indoklás-adathalmazok szükségességét — a modell **saját sikeres levezetéseiből bootstrappel**.
- **Eredmény:** A CommonsenseQA-n egy 30-szor nagyobb csúcs-LLM teljesítményét elérte.

### Reflexion (Shinn et al. 2023)
- **Mechanizmus:** A nyelvi agent a környezeti visszajelzések alapján **verbálisan reflektál** a hibáira, és a reflexiót egy **epizodikus memóriapufferben** tárolja a jövőbeli próbálkozásokhoz.
- **Kulcs-újdonság:** A "verbális megerősítéses tanulás" — döntéshozatali stratégiák módosítása **súlyfrissítés nélkül**.
- **Eredmény:** HumanEval-en 91% pontosság, felülmúlva az akkori GPT-4 80%-os alaperedményét.

### Voyager (Wang et al. 2023, NVIDIA)
- **Mechanizmus:** Minecraft-ban open-ended agent: automatikus tananyag (curriculum) maximalizálja a felfedezést, a sikeres akciókat **futtatható kódként egy folyamatosan bővülő skill library-ba** menti.
- **Kulcs-újdonság:** Paraméter-finomhangolás helyett blackbox LLM-lekérdezés + **kompozicionális, újrahasználható skillek** → gyors tudás-felhalmozás, katasztrofális felejtés elkerülése.
- **Eredmény:** 3,3× több egyedi tárgy, 2,3× távolabbi utazás, 15,3× gyorsabb mérföldkő-feloldás a korábbi SOTA-hoz képest.

### Promptbreeder (Fernando et al. 2023, DeepMind)
- **Mechanizmus:** LLM-vezérelt evolúciós folyamat: feladat-promptok populációját mutálja és értékeli.
- **Kulcs-újdonság:** **Önreferenciális** — nemcsak a feladat-promptokat fejleszti, hanem **azokat a "mutációs promptokat" is, amelyek magát az evolúciós folyamatot irányítják**.
- **Eredmény:** Matematikai és common-sense benchmarkokon felülmúlta a kézzel tervezett CoT és Plan-and-Solve stratégiákat.

### Self-Rewarding Language Models (Yuan et al. 2024, Meta)
- **Mechanizmus:** Iteratív DPO (Direct Preference Optimization) tréning, amely során **a modell "LLM-as-a-Judge" technikával saját maga generál jutalmakat** a kimeneteire, és ezeket visszacsatolja a saját képzésébe.
- **Kulcs-újdonság:** Az előre rögzített, frozen reward-modellek kiiktatása → szuperhumán képességek elméleti lehetősége.
- **Eredmény:** Llama 2 70B három iteráció után az AlpacaEval 2.0-on lepipálta a Claude 2-t, Gemini Pro-t, GPT-4 0613-at.

### Gödel Agent (2025)
- **Mechanizmus:** A "Gödel-gépéből" inspirált architektúra **dinamikus memóriamanipulációval (monkey patching) futásidőben elemzi és írja át a saját kódját**, magas szintű promptolt célok vezérlésével.
- **Kulcs-újdonság:** **Teljes önreferencia és korlátlanság** — mentes az előre tervezett fix meta-tanulási rutinoktól, az agent a teljes tervezési teret bejárhatja, az önmódosításáért felelős algoritmust is kicserélheti.
- **Eredmény:** Matematikai és komplex érvelési teszteken folyamatos önfejlesztő képességet mutatott, teljesítményben és flexibilitásban felülmúlta a hagyományos kézzel tervezett architektúrákat.

## 3. Tech-stack opciók 2026-ban

### Production-ready stack-ek

| Stack | Mire jó | Tradeoff |
|---|---|---|
| **Anthropic Claude Code + Agent Skills + MCP** | Egyszálú, fegyelmezett master-loop + dinamikus `SKILL.md` betöltés + MCP külső kapcsolatok | Kiemelkedően stabil, auditálható, jogosultsági szintekkel — DE az egyszálú lapos dizájn miatt nem használja ki a multi-agent párhuzamosítást |
| **GEPA / DSPy / TextGrad** (prompt-optimizer) | Nyelvi reflexión alapuló prompt-mutáció, zárt API-modelleknél is működik | Súlyfrissítés nélküli minőségjavulás — DE **compile-time** folyamat egy adathalmazon, NEM futásidejű önkorrekció a feladat közben |
| **AutoGen / LangGraph / CrewAI** (orchestration) | Multi-agent szerepkör-delegálás, kollaboratív feladatmegoldás | Jól menedzseli rögzített munkafolyamatokat — DE az ágens-közti protokollok (ACP, ANP) kiforratlanok, korlátozhatják a nyílt végű önfejlesztést |
| **ReFlect Harness** (vLLM / Temporal backend) | Determinisztikus, hibadetektáló burok az LLM körül; shape-based validátorok (pl. SWE-bench diff, ALFRED) | Drasztikusan megbízhatóbb és token-hatékonyabb a tisztán LLM-judged self-correction-nél — DE megköveteli, hogy minden feladattípushoz előre leprogramozzák a determinisztikus validátort |

### A 3 stack-paradigma elhatárolása

A 4 dimenzió közül a top 3 implementáció-szintű paradigma **eltérő infrastruktúrát** igényel:

- **Prompt-evolution stack** — Az utasítások iteratív, evolúciós csiszolása. A modell-paraméterek **nem változnak**. A futásidejű állapot maga a felgenerált prompt-szöveg, a javítás Pareto-front szelekcióval és nyelvi összegzéssel történik. *(GEPA, DSPy, Promptbreeder)*
- **Skill-library-growth stack** — Az ügynök memóriáját **kívülről** elmentett képességek tára jelenti. A működést **progressive disclosure** vezérli: az agent fájlrendszerből / DB-ből olvas be eljárási modulokat új feladat előtt. Az LLM belső működése változatlan. *(SAGE/SkillRL, Anthropic Agent Skills, Voyager)*
- **Code-self-modification stack** — A "valódi" rekurzió: az agent **monkey patching** módszerrel fér hozzá a saját belső működéséhez, futásidőben átírja a memóriában lévő forráskódot. Kritikus a robusztus hibakezelés, hogy a hibás kód ne omlasszon. *(Gödel Agent)*

## 4. Friss áttörések 2024-2026

A 2024 előtti paradigmák (Reflexion, Self-Refine, Promptbreeder) jellemzően **egyetlen monolitikus promptot** optimalizáltak vagy a modell **saját, megbízhatatlan szöveges önkritikájára** támaszkodtak. A 2024-26-os paradigmaváltás lényege: az önfejlesztés **átlépett a puszta szöveges csiszoláson** — futásidejű kód-újraírás, dinamikus skill library-k, Compound AI System evolúció és **determinisztikus külső harness**-ek felé mozdult.

### 1. Teljes önreferencia és futásidejű kódmódosítás (Gödel Agent)
Az első olyan agent, ami **monkey patching**-gel a saját futásidejű logikáját képes felülírni — beleértve az önmódosításért felelős algoritmusokat is. Nincsenek beégetett emberi korlátok, a teljes agent-tervezési teret bejárhatja.

### 2. "Skill Engineering" kora — dinamikus képességtárak
A prompt tervezés (2022-23) és egyszeri eszközhasználat (2023-24) után 2025-26-ot a "Skill Engineering" dominálja. Az Anthropic szabványosította az ágens eljárási tudását `SKILL.md` + MCP-vel. A modell már nem mindenttudó súlyokból dolgozik, hanem **dinamikusan tölt be többlépéses instrukciókat, kódokat és munkafolyamatokat**, finomhangolás nélkül. A **SAGE** (Skill Augmented GRPO) és **SEAgent** algoritmikusan desztillálják nyers tapasztalatokat skillekké, RL-lel validálva.

### 3. Algoritmusok és teljes kódbázisok evolúciója (AlphaEvolve, DeepMind 2025)
A korábbi kódgeneráló ágensek csak izolált függvényeket alkottak. Az **AlphaEvolve** az LLM-kreativitást automatizált értékelőkkel kombinálva **komplex algoritmusokat és teljes kódbázisokat evolúciósan fejleszt**, és olyan nyitott matematikai problémákon ért el új eredményeket, mint a "kissing number problem".

### 4. Összetett rendszerek prompt-evolúciója (GEPA, 2026)
A Promptbreeder még csak egylépéses LLM-hívások promptjait fejlesztette. A **GEPA (Genetic-Pareto Reflective Prompt Evolution)** túllép: **Compound AI rendszereket** (több modul + prompt interakcióban) optimalizál. Futásidejű trajectory-kat természetes nyelvi reflexióval elemzi, új generációkat Pareto-fronton őriz meg. **35× kevesebb próbálkozással** felülmúlta a drága RL-módszereket (GRPO).

### 5. Test-time evolúció külső verifikáló nélkül (Recursive Self-Aggregation, RSA)
A 2025-26-os **RSA** új hibrid paradigma: nem külső verifikálót használ, hanem evolúciósan fenntartja a **reasoning chains populációját**, iteratívan rekurzívan aggregálja, kicseréli a részlegesen helyes lépéseket szálak között. Ezzel egy 4B paraméteres modell (Qwen3-4B) képes a DeepSeek-R1 szintjét elérni.

### 6. A megbízhatóság áthelyezése a promptból a burokba (ReFlect Harness)
A "self-correction blind spot" felismerése: hosszú távú feladatoknál a modell szöveges önkritikája **az esetek 76-98%-ában fals-pozitív**. A **ReFlect** kiveszi a hibadetektálást és recovery-t a modellből, és egy determinisztikus futtatókörnyezetbe helyezi. **Shape-based validátorok** + kódolt retry. Az LLM csak cselekszik, a burok ellenőriz.

## 5. Failure-modes és limitációk

### 1. Self-correction blind spot
Huang et al. (2023, "Large Language Models Cannot Self-Correct Reasoning Yet") rávilágít: külső, objektív visszajelzés hiányában az LLM-ek **szinte képtelenek kijavítani a saját logikai hibáikat** — sőt, az önkorrekciós próbálkozás **rontja** a teljesítményt. Auditok: 100 reflexiós blokkból 90 semmilyen hibát nem jelez, a valódi irányváltás aránya ~1,7%. **Az esetek 76%-ában a modell tévesen elfogadja a hibás választ is.** A hallucinációk csendben halmozódnak.

### 2. Degenerált ismétlődési hurkok és költségrobbanás
Strukturális korlátok nélkül a modellek **végtelen "ismétlődési hurokba"** esnek: folyamatosan megkérdezik maguktól "helyes-e a válasz?", újragenerálják ugyanazt a hibás kimenetet. Bizonyos teszteken **7-23%-os gyakoriság**. Token-budget kimerülés, számítási költségrobbanás megoldás-közeledés nélkül.

### 3. Katasztrofális felejtés és mode collapse
A dinamikus skill-betöltés és folyamatos finomhangolás során az új folyamatok **akaratlanul felülírhatják** a modell hasznos default viselkedéseit. Evolúciós megközelítéseknél (rekurzív aggregáció) **diverzitásvesztés**: a rendszer ugyanazokat a sikeres mintákat reciklálja → mode collapse, distribution drift.

### 4. Biztonsági kockázatok — a hibakezelés "felülírása"
A teljesen önreferenciális (Gödel Agent-szerű) architektúrák legnagyobb kockázata: ha az agent reward-hacking gyanánt vagy tévedésből **felülírja az őt védő hibakezelő rutint**, a rendszer összeomlik, és minden további önoptimalizálás lehetetlenné válik. **Sandboxed végrehajtás kötelező.**

### 5. Yampolskiy-limit (intelligencia szűk keresztmetszete)
Elméleti és gyakorlati korlát: ahogy az agent komplexebbé válik, **saját kódjának megértése és továbbfejlesztése exponenciálisan nagyobb intelligenciát követelne**. A kezdetben önmódosításra képes rendszer egy idő után "túlnő" saját értelmezési képességein és megakad.

### Amit az RSI önmagában NEM old meg

> A rekurzív önfejlesztés **nem képes külső igazságot (ground truth) generálni abból, ami nincs benne a modell tudásában vagy a környezetben**.

A tisztán "LLM-judged" önkorrekció **elméleti plafonba ütközik**: a nyelvi modellek túl rosszak a determinisztikus verifikációban. A szuboptimális futás megakadályozására az önfejlesztést kötelezően **harness rendszerekkel** (linter, math engine, állapottér-követő) kell kiegészíteni — az LLM csak javasol, a verifikáció nem-LLM mechanizmusnál marad.

## 6. Implementáció a Peti-vault kontextusban

A meglévő `[[AGENTS.md]]` + Karpathy LLM-Wiki + Johnny-Decimal struktúrájú vault + 11.11 session-protokoll + [[11-wiki/Crystallization-protocol]] + 280-skill pool **kiváló alapot** ad a recursive self-improvement bevezetésére. A `/11.11stop` záráskor már most ki vannak nyerve a Learnings, de **passzív** — a következő evolúciós lépés ezek átalakítása **végrehajtható eljárásokká** és magának az agent-config-nak (AGENTS.md, skill-fájlok) az autonóm fejlesztésévé.

### 1. Safety-harness ELŐSZÖR — sandbox + git-hook + rollback

> **⚠️ Sorrend kritikus.** A `[[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]` is rögzíti: a #2 tengely (RSI) **a többi szabályozott pályára állítása után, utolsóként** engedélyezhető. Az alábbi safety-mechanizmusok ELŐFELTÉTELEK.

- **Sandbox-mappa** — pl. `00-Meta/Sandbox/` Johnny-Decimal logikával. Az agent minden önmódosítás-javaslata először ide kerül `#sandbox` taggel, `unvetted` jogosultsági szinttel
- **Git-commit-pre-hook** — determinisztikus Python-szkript (formátum-validátor, frontmatter-séma, link-konzisztencia) teszteli az új fájlt. **Az LLM csak javasol, a futtatás joga a teszté.** ReFlect-mintájú "G3 Behavioral Sandbox" gate
- **Revert-able változások** — minden önmódosítás ELŐTT git checkpoint (commit-tag `pre-self-mod-<timestamp>`). Ha az új AGENTS.md hibát dob a teszten → automatikus `git reset` a tag-re. A jelenlegi 10-perces `vault-autosave` cron jó alapot ad
- **Confidence-threshold** — a Crystallization-protocol [[11-wiki/Crystallization-protocol#Routing decision tree]] mintájára: csak `confidence >= 0.85` és **legalább 2 független session** Learning-jeit lehet auto-propagálni. Lower-confidence → továbbra is user-confirm marad

### 2. Automatikus skill-desztilláció a session history-ból (SAGE / SkillRL mintára)

A `/11.11stop` futásakor egy szintetizáló folyamat induljon, ami a chat-history-t SAGE-mintára eljárás-skillekké desztillálja:

- **Trigger:** Ha a session sikeresen oldott meg **újszerű** feladatot (nincs matching skill a `~/.claude/skills/` pool-ban), induljon a desztilláció
- **Reflexiós LLM-hívás:** Egy dedikált haiku-szintű hívás kivonja a sikeres lépéssorozatot a session events-ből + diff-ekből
- **SKILL.md generálás progressive disclosure-rel:**
  - **Level 1 (metadata)** — YAML frontmatter (név, leírás, trigger-feltételek), ami **fixen az agent kontextusába kerül** session-induláskor
  - **Level 2 (instructions)** — A session-ből desztillált, lépéses utasítások (a fájl törzse), amit az agent **on-demand** tölt be
- **Tárolás** — `~/.claude/skills/auto-distilled/<slug>/SKILL.md` mappa, `auto-distilled` tag a Skill-map-ben → később manual review-zható

> **Karpathy "compilation" párhuzam:** Ez a folyamat pontosan a `[[11-wiki/Karpathy-LLM-Wiki-pattern]]` "lassú → gyors" desztillációja. A "Heavy Thinking" (Tree of Thoughts, rekurzív aggregáció) eredményeit átfordítja **azonnal futtatható skillekké** — a nyitott kutatási kérdést (open issue Q7) a Peti-vault egy konkrét implementációval címzi.

### 3. AGENTS.md és skill-fájlok autonóm finomítása (Gödel Agent + GEPA hibrid)

**Self-update tool:** `EditTool` + `self_update` akció — beolvashatja és felülírhatja a `~/.claude/CLAUDE.md`-t és a skill-fájlokat **DE csak a Sandbox-mappában** (`00-Meta/Sandbox/CLAUDE.md.proposal`).

**Diagnózis és kiváltó ok (ReFlect INSPECT operátor mintára):** Ha a rendszer elakad (stalled progress detektálva — pl. session-en belül `>=3` retry ugyanarra a hibára), strukturáltan diagnosztizálja:
- Hiányzó skill? → új skill-jelölt generálása
- Rossz prompt-részlet az AGENTS.md-ben? → patch-javaslat
- Hibás routing-szabály a Crystallization-protocol-ban? → szabály-finomítás

**Promptok evolúciós optimalizálása (GEPA):**
- **Mutáció** — minden 10. session után egy háttérfolyamat összegyűjti a sikertelen + sikeres trajektóriákat, és 3-5 új mutációt javasol a CLAUDE.md / skill-fájlok utasításaihoz
- **Minibatch tesztelés** — az új prompt-jelölteket korábbi session-feladatok mintáján futtatja, pontszámokat gyűjt
- **Pareto-szelekció** — csak azok élesednek, amik **javítanak új feladaton anélkül hogy lerontanák a régieket** → ez akadályozza meg, hogy a CLAUDE.md "kezelhetetlenül hosszú, felesleges szabályokkal teli fájllá hízzon"
- **System-Aware Merge** — a változtatások interfész-kompatibilisek a 11.11 session-protokollal és a Crystallization-flow-val

### 4. Konkrét sprint-bontás (Phase B-be be)

| Sprint | Feladat | Függés |
|---|---|---|
| **W1** | Sandbox-mappa + git-pre-commit-hook + rollback-script (`pre-self-mod-<ts>` tag) | — |
| **W2** | Confidence-score a Crystallization-protocol-hoz; auto-propagáló kritérium definiálva | Sprint 1 |
| **W3-4** | SKILL-desztilláló a `/11.11stop`-ba (Level-1+2 generálás, `~/.claude/skills/auto-distilled/`) | Sprint 1-2 |
| **W5-6** | GEPA-stílusú prompt-mutator + minibatch-tesztelő (background cron) | Sprint 1-4 |
| **W7+** | Self-update tool integrálása — agent ír AGENTS.md-patch-eket sandboxba, user-confirm után élesedik | Sprint 1-6 |

> **Megjegyzés:** A Gödel Agent stílusú **valós futásidejű kódmódosítás** (Python file rewrite a futó folyamatban) **kihagyható** ebben az iterációban — túl magas attack-surface, és a vault nem egy futó Python-folyamat. A "code self-modification" itt **a markdown-config (AGENTS.md, SKILL.md) önmódosításra** korlátozódik, ami biztonságosabb és minden git-revertálható.

## 7. Mit kell tovább kutatni?

### 1. Meta-learning vs. in-context tanulás
A jelenlegi keretrendszerek (Promptbreeder, GEPA) in-context prompt-evolúcióra vagy fix meta-tanulási algoritmusokra épülnek. Az **STOP (Self-Taught Optimizer)** kutatás "meta-meta" szintű optimalizációt javasol: maga a meta-tanulásért felelős algoritmus is önfejlesztés célpontjává válik. Nyitott: in-context aggregáció (RSA) és RL mélyebb integrációja — több-lépéses RL ami a modell-súlyokba égeti a stratégiákat. Új irány a **"meta-harness optimalizáció"**: a keretrendszer (eszközválasztás, leállási kritérium, formátum-küszöbök) **kódobjektumként folyamatosan keresett** — nem ember által tervezett.

### 2. Multi-agent self-improvement
**Mixture-of-Agents** paradigma: több LLM kollaborációjával generálnak és aggregálnak javított megoldásokat. Gödel Agent továbbfejlesztése: **kollektív intelligencia + játékelmélet** integrációja — teljesen autonóm, magukat módosító ágensek a többit a környezet részeként kezelik, kompetícióban / kooperációban fejlesztik a logikájukat. Hivatkozott open probléma: **skill compilation fázisátmenet** — egy multi-agent hálózat sikeres stratégiái át-"fordíthatók" egyetlen agent skill-libráriájába; DE **kritikus pont** ahol a könyvtár-növekedéssel a skill-választási pontosság hirtelen összeomlik. Ez egyenesen az [[02-Projects/Index]] tervezett SV-3 multi-agent tengelyéhez kapcsolódik.

### 3. Fine-tuning + RAG kombináció learning-konszolidációra
A hagyományos RAG passzív, nem adaptál dinamikusan eljárást. **Self-RAG** (egyetlen LLM finomhangolva speciális reflexiós tokenekre — futásidőben dönt mikor kell külső tudás, kritikusan értékeli a visszakeresett információt és a saját generálását) ezt címzi. Nyitott: **continual learning catastrophic forgetting nélkül** — **ön-desztilláció (self-distillation)** mint módszer arra, hogy a dinamikusan betöltött új képességek konszolidálódjanak a modellben anélkül hogy felülírnák a hasznos alap-viselkedéseket. Direkt kapcsolódik az SV-5 Crystallization-tengelyhez.

### 4. Safety-kutatások
Megdöbbentő adat: a közösség által fejlesztett ágens-skillek **több mint 26%-a sebezhetőséget tartalmaz**. Jövőbeli safety-fókusz: a hagyományos szoftvertesztelésen túl **formális verifikáció** + **képességalapú finomszemcsés jogosultsági modellek (capability-based permission models)**. Önmódosító rendszereknél (Gödel Agent) szigorú **sandboxed execution** + önmódosítások **hatókör-korlátozása** — nehogy egy rosszul sikerült mutáció a biztonsági fékeket tegye tönkre.

### 5. Karpathy 'compilation' (LLM-Wiki) — direkt kapcsolat a self-improvement-hez
A tudományos irodalom Karpathy víziójának ("LLM Wiki", "Vibe Coding → Agentic Engineering") tudományos megfelelőjét **"compilation" / desztilláció** néven ismeri (DSPy deklaratív hívások önfejlesztő pipeline-okká kompilálása, "skill compilation" kutatások). A self-improvement-ben ez **a lassú "Heavy Thinking" (Tree of Thoughts, RSA) eredményeinek átfordítása letisztult, azonnal futtatható skillekké vagy LLM-Wiki szócikkekké**. **A nyitott kérdés:** hogyan építhető olyan infrastruktúra (MCP-protokollokon át), ami **automatikusan, emberi beavatkozás nélkül tartja karban és frissíti** ezt a növekvő LLM-Wiki tudástárat — és **kerüli el a túl sok információ okozta teljesítményromlást**? Pontosan ez a Peti-vault saját implementációs frontvonala.

## Phase A+ bővítés (2026-05-12 deep-research)

A Phase A 7/7 kérdése után a tengelyt 4 párhuzamos `--mode deep` NotebookLM-research-csel bővítettem (~3-4 órás web-crawl), majd 3 mély-komplex kérdést tettem fel az így gazdagított forrásbázisra. **A source-pool 55 → 1009 readyre nőtt** (a deep-research a teljes citation-gráfot beszippantotta — sok átfedés a 4 tengely között, de mind ready és kereshető).

### Új források (4× deep-research)

| Query | Találatok | Kulcs-anyagok |
|---|---|---|
| "recursive self improvement LLM agent 2026 production case study real deployment" | 212 source | "The State of RSI in LLM Agents 2026" Report; ICLR 2026 RSI Workshop OpenReview; SkillRL OpenReview; Self-Evolving Agents (EvoAI Labs); "The Ungovernable Machine" (Stanford Law) |
| "GEPA optimizer Compound AI production results 2025 2026 industry benchmark" | ~46+ source | "Architectural Convergence of Genetic-Pareto Optimization and Compound AI Systems" Report; VentureBeat GEPA coverage |
| "ICLR 2026 RSI workshop recursive self improvement papers latest" | (lefedi az 1) | ICLR 2026 Recursive Self-Improvement workshop accepted papers, OpenReview poszter-bundle |
| "Anthropic Agent Skills compositional learning production case study Gödel Agent ReFlect" | + | Anthropic Skills `SKILL.md` progressive-disclosure dokumentáció; Gödel Agent ACL 2025; ReFlect 2026 benchmarkok |

### Q1 — Optimális 3 architektúra-kombináció és sorrend

> A NotebookLM válasz **NEM a Gödel Agent monkey-patching megközelítését** javasolja, hanem egy strukturáltabb **Compound AI System három-pilléres** építését. A Peti-vault esetében (240 fájl, 280-skill pool) ez **csavarja meg a Phase A "code self-modification" felső véget**: a kockázat nem éri meg a hasznot.

**1. lépés — Tudásbázis-strukturálás: Anthropic Agent Skills (Progressive Disclosure)** [Anthropic Skills doc + ECC plugin source]
- *Mechanizmus:* 3 szint — **Level 1 (Metadata):** YAML frontmatter, mindig a kontextusablakban; **Level 2 (Instructions):** Markdown-törzs, csak on-demand betöltve a skill-hívásnál; **Level 3 (Resources):** Külső szkriptek (`.py`/`.sh`), csak L2-parancs hatására futnak.
- *Tech-stack döntés a vaultra:* az `SKILL.md` fájlok már YAML-frontmatter szerkezetűek (`name`, `description`) — Level 1 a globális promptba kerül, a fájltörzs (Level 2) és a `~/.claude/skills/<slug>/scripts/` (Level 3) dinamikus loader-en át. **Drasztikusan csökkenti a kontextus-fogyasztást a 280-skill pool mellett.**

**2. lépés — Biztonságos végrehajtás: ReFlect Harness (Level-3 determinisztikus burok)** [ReFlect 2026 benchmark, Skill RL OpenReview]
- *Mechanizmus:* "LLM-judged" önkritika **nem működik** komplex feladatoknál ("Level 2" szint korlátja). A ReFlect a hiba-észlelést és recovery-t **kiszervezi az LLM-ből** egy determinisztikus Python-harness-be: shape-routed format-validátorok + retry-as-code.
- *Tech-stack döntés a vaultra:* az Obsidian vault köré Python-executor (a meglévő `vault-cleanup` cron-keretrendszer természetes hely). Amikor az agent skill-módosítást vagy AGENTS.md-patch-et javasol, a shape-routed kód ellenőrzi a JSON/Markdown-struktúrát (frontmatter-séma, link-konzisztencia). **A javasolt önmódosítás csak akkor megy élesbe, ha ezen átmegy** — ez ki is köszöni a Phase A failure-mode #1-jét (self-correction blind spot).

**3. lépés — Iteratív evolúció: GEPA (Reflective Prompt Evolution)** [GEPA 2026 industry report, gepa-ai/gepa Python lib]
- *Mechanizmus:* Pontszámok helyett **természetes nyelvi reflexió** a futási trace-ekből + hibákból + Pareto-front fenntartás. **35× kevesebb rollout** mint a klasszikus RL (GRPO).
- *Tech-stack döntés a vaultra:* a `/11.11stop` session-lezárásakor keletkező Learnings + chat-trace-eket a `gepa-ai/gepa` Python-libbe táplálni. A GEPA időszakosan (pl. 10 session-enként) elemzi a sikereket+kudarcokat, automatikusan javasol patch-et a `SKILL.md`-kre és az `AGENTS.md`-re — **a teljes Compound AI System folyamatosan, autonóm módon evolválódik**, de a ReFlect-harness-en át.

**Kulcs-tanulság a sorrendre:** Skills → ReFlect → GEPA. A biztonsági burok ELŐBB kell mint a evolúciós motor — a Phase A "safety first" sprintbontás (W1-W7) ezt már lefedi, csak most konkrét tech-stack-döntésekkel.

### Q2 — Production-ready vs akadémiai

> **Kemény üzenet:** A 10 felsorolt RSI-irány közül **egyetlen `production-ready` áttörés a GEPA**. A többi mind akadémiai stádium — kutatási mérföldkő, nincs business case.

| Megközelítés | Státusz | Forrás-idézet |
|---|---|---|
| **GEPA** | ✅ **Production-ready** | "2026 közepére a GEPA vált az összetett AI rendszerek ipari szintű optimalizálásának domináns keretrendszerévé"; GRPO-t 20% pontosságban felülmúl, 35× kevesebb rollouttal; prompt-cachingel kombinálva ipari standard [GEPA Industry Report] |
| **Promptbreeder** | 📚 Akadémiai | "Hatalmas számítási költségek és algoritmikus komplexitás miatt nem elég praktikus" — a cégek GEPA-ra váltottak |
| **Voyager** | 📚 Akadémiai / alapkutatás | Az első élethosszig tanuló (lifelong learning) LLM-agent, **skill library koncepció úttörője**, de maga a Voyager technológiai demó |
| **STaR** | 📚 Akadémiai | Bootstrapping reasoning alapozó cikk (2022), számos mai siker alapja, de a STaR önmagában csak papíron |
| **Reflexion** | 📚 Akadémiai | A 2026-os ReFlect-paper kifejezetten **a Reflexion ipari limitjeire reagál**: "az esetek legalább 76%-ában a modell hibásan elfogadja a rossz megoldást" |
| **Self-Rewarding LMs** | 📚 Akadémiai | "Tiszta alapkutatás az RL továbbfejlesztésére" |
| **Gödel Agent** | 📚 Akadémiai (ACL 2025) | Az önreferenciális monkey-patching csak akadémiai értekezésekben létezik |
| **ReFlect** | 📚 Akadémiai (de 2026!) | "Kiváló eredmények SWE-bench-en, de ipari termékesítése még várat magára" |
| **SAGE** | 📚 Akadémiai (ICLR 2026 RSI poszter) | Self-play Adversarial Games — versengő agentek logikai képességre |
| **SkillRL** | 📚 Akadémiai (2026-02) | Hierarchikus skill-library RL-lel — friss, Reflexion-továbbfejlesztés |

**Üzleti kitörés a 2026-os képben:** RSI az **egyértelmű, bináris siker/kudarc kritériumú** ("verifiable reward") területeken — kódolás, gyógyszerkutatás — termel milliókat. **Példa: Meta Ranking Engineer Agent (REA)** — production, teljesen autonóm módon iterál és optimalizál ML-modelleket [Industry Report].

### Q3 — Cost-tier vágási térkép (3 budget)

> A NotebookLM keményen kvantifikálja: prompt-opt futás $10-200, SFT $15-500, RL $200-5000 / iteráció. Egy 1-fejlesztős set-up szigorú metszést igényel.

#### Tier 1 — **$50/hó (Ultra-Budget / Bootstrap)**
- **LEVÁGNI:**
  - Nyelvi alapú **Reflexion** (Level-2 önkritika) — $10.26 / 100 helyes válasz + 76%-os hibás-elfogadás
  - **GEPA + Pareto-merge** — $10-200 / kör azonnal kimerít
  - **Skill-distill (SFT/RL)** — RL min $200/iter
- **MEGTARTANI:**
  - **Progressive Disclosure** (Level 1 metadata + on-demand Level 2 body) — a 280-skill pool token-fogyasztását drasztikusan csökkenti
  - **ReFlect-burok + git-precommit** — "Full ReFlect" $0.36 / 100 helyes futás (!)
  - **Prompt caching** — 60-90% input-költség csökkentés
  - **Ultra-budget modellek:** GPT-5 Nano ($0.05/$0.40 per 1M token) vagy DeepSeek V3.2 ($0.14/$0.28) napi futtatásokra

#### Tier 2 — **$200/hó (Mid-range)**
- **LEVÁGNI:**
  - **Teljes validációs rollout-ok** a GEPA-ban — a teszthalmaz drága kiértékelése
  - **Folyamatos Frontier-modell-használat** a mutációhoz
- **MEGTARTANI / BEÉPÍTENI:**
  - **Proxy benchmark GEPA** — kisebb `D_proxy` halmaz, rangsorolási szignál megőrződik
  - **LEVI-féle role-aware routing** — a mutációk **90%-át olcsó open-modell** (pl. Qwen3-30B) végzi, 10% drágább reflektor (pl. Gemini Flash 3) szerkezeti paradigmaváltásokhoz
  - **Frontier reflektor — TILOS ezen spórolni**: a reflexió a GEPA-költségek csak 5-10%-a, de gyenge reflektor → nem tanul a rendszer (elpazarolt rollout-ok)
  - **`/ratchet` éjszakai hurok** (kayba-ai inspirált) — autonóm improve→eval→keep-or-revert ciklus sandboxban

#### Tier 3 — **$500/hó (High-end)**
- **LEVÁGNI:**
  - **Korlátozatlan GEPA mutációk** length-regularization nélkül — különben "prompt bloat" 5000-karakteres méreggdrága monolitikus promptokat generál
- **MEGTARTANI / BEÉPÍTENI:**
  - **Rendszeres Pareto-merge GEPA** szabályozott prompt-hosszal
  - **Skill-distill (SFT)** — havonta a Pareto-optimális promptokat és trace-eket $15-500 közötti finomhangolással **égessük be egy kisebb open-modellbe** (formátum-fix a súlyokba)
  - **Modell-kaszkád routing** — alapból olcsó finomhangolt modell, ReFlect parse-failure-detect esetén **eszkaláció a prémium modellhez** (Opus 4.6) — átlagosan **58% költségmegtakarítás** vs folyamatos frontier-használat

**Peti-vault konkrét pozicionálás:** A jelenlegi $50-100/hó Anthropic-API tényleges használat (becsült) Tier-1-be esik → **Skills + ReFlect + prompt caching az ELSŐ 3 hónapra**. A GEPA-evolúciós motor csak Tier-2-től racionális.

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható. Elindítva:

```bash
notebooklm generate audio -n a2425bc7-4786-46f4-9fe8-00fa9510177e
# Task: 18f27b6c-623f-4030-b59e-de415fe2c1e8
```

Letöltés (Phase A végén):

```bash
notebooklm download audio -n a2425bc7-4786-46f4-9fe8-00fa9510177e
```

## GEPA verified-live 2026-05-17

A `gepa-ai/gepa==0.1.1` Python-library **pip-installable + smoke-test-green** 2026-05-17-én verifikálva. A Phase A+ idején még arXiv-paper-szintű volt; ma production-ready.

- Install: `pip install gepa` (< 1 perc, transformers + torch dependencies)
- API: `gepa.optimize(seed_prompt, train_data, valid_data, ...)` + `gepa.GEPAAdapter` subclass
- Strategies: `Pareto`, `current_best`, `epsilon_greedy`, `top_k_pareto`, `stop_callbacks`

**SV B-8 Week 1 skeleton ÉLES (`/root/obsidian-vault/.vault-rsi/`):** 2 script (`gepa-prompt-eval.py`, `gepa-prompt-mutate.py`), 3 baseline prompt, 8-sample gold-set, 4-rétegű safety-gate (ENV `VAULT_RSI_APPLY=0` default OFF, candidates-only write, forbidden-targets `AGENTS.md`/`00-Meta/`/`.vault-ko/safety/`/`11.11*`, Week 1 0 apply). Részletek: [[../06-Audits/2026-05-17 B-8 GEPA prompt-mutator skeleton]].

**Tanulság a SV-roadmap-hez:** [[vendor-feature-verify-before-workaround]] — minden 6+ hónapos roadmap-elem érdemes újra-verifikálni release-cycle-ben; ami "research-only" volt 4 hónapja, ma `pip install`.

### Week 2 real `gepa.optimize()` loop verifikálva (2026-05-17-3)

A B-8 Week 2 subagent élesítette a **valós Pareto-improvement loopot** (audit: `06-Audits/2026-05-17 GEPA Week 2 real-loop.md`):

- Custom `GEPAAdapter` + `ClaudeCodeReflectionLM` (~810 sor kód) — `evaluate()` írja a phase-1 scoring-request fájlokat (`.vault-rsi/scoring-pending/`), `make_reflective_dataset()` per-sample feedback-et ad a reflection_lm-nek
- Smoke (budget=32, iter=3, 8-sample gold-set): **baseline 0.541 → concise 0.593 → actionable 0.619 = +14.3% Pareto-front**
- 3 candidate variant materializálva `.vault-rsi/prompts/candidates/g-eval-v0.3.{0,1,2}/` (detect-only header `<!-- CANDIDATE — NOT LIVE -->`)
- 2-phase pending UUIDv5 idempotency (`sha256(candidate, sample, component)`)
- 4-rétegű safety mind ✓: Layer-1 ENV-gate, Layer-2 forbidden-target 6/7 BLOCKED (csak `candidates/` OK), Layer-3 Pareto-cap, Layer-4 detect-only header

**Mérnöki ROI:** $0 cost (claude-code parent + subagent-pattern), <2 perc wall-clock smoke. Reusable bárhol ahol prompt-pareto-front kell + gold-sample-ek vannak.

**Week 3 follow-up:** `mode='auto-fill'` (deterministic mutator) → `mode='subagent'` (real reflection-LLM-fanout) + Critic-review gate `candidates/<id>` → `.vault-agents/prompts/` promóció ELŐTT.

## 2026-05-19 — Real-LLM Critic skeleton landed

A 4-rétegű safety-gate Layer 4 Critic mostantól **real-LLM** is lehet a `VAULT_CRITIC_ACTIVE=1` opt-in env-flag mögött. Részletes architektúra + activation: [[sv-rsi-tier2-real-critic]].

- **Pattern:** 2-phase pending (request.json → Claude subagent → response.json), `crystallize-pending` skill mintáján
- **Rubric:** 5-dim (`factuality`, `novelty`, `durability`, `vault_fit`, `safety`), 0.0-1.0 float
- **Threshold:** 3 mode (`strict` default / `default` / `lenient`), `safety >= 0.9` mindig hard-gate
- **Cost:** $0 (subagent-fanout), nincs Anthropic API-key
- **Files:** `.vault-ko/safety/critic-review.py` + `.vault-ko/prompts/critic-review-template.md` (5-dim rubric + 5 anchor) + `.vault-ko/safety/git-pre-commit-hook.sh` (Layer 4 integráció) + `.vault-ko/tests/test_critic_review.py` (5 pytest test, mind PASS)
- **Audit-log:** `06-Audits/critic-review-log.jsonl` (JSONL, mode=stub/strict/default/lenient)
- **Back-compat:** `VAULT_CRITIC_ACTIVE` nem set → marad a deterministic 4-rule Critic-stub

## Akció-pontok ehhez a tengelyhez

- [x] **W1 sprint:** Sandbox-mappa + git-pre-commit-hook + rollback-script ✓ ([[../06-Audits/2026-05-17 B-8 GEPA prompt-mutator skeleton]])
- [x] **W2 sprint:** Confidence-score modell a Crystallization-protocol-hoz ✓ (G-Eval kalibrációs 96.7% + v0.3-bias-mitigated)
- [x] **W3-4 sprint:** SKILL-desztilláló skeleton a `/11.11stop`-ba ✓ ([[../06-Audits/2026-05-17 B-4 auto-skill distillation skeleton]])
- [x] **W5-6 sprint:** GEPA-stílusú prompt-mutator skeleton ✓ ([[../06-Audits/2026-05-17 B-8 GEPA prompt-mutator skeleton]]) — REAL loop Week 2
- [ ] **W7+ sprint:** Self-update tool integrálása sandbox-mode-ban (NEM élesben)
- [ ] Audio overview letöltése és meghallgatása
- [ ] SV-3 (multi-agent) cikk megírásakor: vissza-referencia a "skill compilation phase transition" open problémára
- [ ] SV-5 (Crystallization automation) cikk megírásakor: vissza-referencia a "Self-RAG + continual learning" open kérdésre

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
- [[10-raw/2026-05-12 — Superintelligence research source pool]]
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a "compilation" elv kiindulópontja, közvetlenül a SV-2-höz kapcsolódik (Q7)
- [[11-wiki/Crystallization-protocol]] — a jelenlegi manuális tudás-propagáció; ennek auto-bővítése az SV-2 magja
- [[11-wiki/11.11-session-protokoll]] — a session-lifecycle, ahova az auto-skill-desztilláció bekerül
- [[11-wiki/external-skill-cherry-pick]] — skill-pool gyarapítási minta, párhuzamos az auto-desztilláció filozófiájával
- [[11-wiki/sv-01-memory-architecture]] — az előző tengely
## NotebookLM-konverzáció

- **Notebook ID:** `a2425bc7-4786-46f4-9fe8-00fa9510177e`
- **Conversation ID:** `4743590e-4973-43ba-b0d2-7c026412c300`
- **Források:** 53 ready (5 arXiv + 5 arXiv + 5 Anthropic/DeepMind/arXiv + 5 arXiv + 2 add-research × ~10 import × részben dupla) + 2 YouTube error
- **Kérdések:** 7/7 válaszolva, mind ~5KB-os strukturált válasz
- **Audio overview task:** `18f27b6c-623f-4030-b59e-de415fe2c1e8` (generálás folyamatban)
