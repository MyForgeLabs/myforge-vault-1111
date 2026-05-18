---
name: SV-5 Crystallization automation
type: wiki
tags: ["#type/wiki", "agi", "crystallization", "rlaif", "constitutional-ai", "self-rewarding", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: done
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: a219107d-e8fe-4ece-b721-ae6e3182bd45
---

# SV-5 — Crystallization automation

A 8-tengelyű szuperintelligens-vault evolúciós research ötödik cikke. **Kérdés:** hogyan automatizálható a `/11.11stop` user-confirmation-szakasza confidence-score alapján úgy, hogy a high-confidence Learnings auto-propagálódnak Memory / Wiki / Decisions felé, miközben a vault integritása megmarad és az emberi felügyelet kontrollálható szinten marad.

> **Status:** 7/7 kérdés válaszolva, 27 forrás (24 ready, 2 YouTube hibás, 1 add-research retry kihagyva). Phase A teljesítve. Phase B sprint-bontás következik (`02-Projects/superintelligent-vault.md`).

## 1. A tengely magja

A **kristályosítási automatizáció (crystallization automation)** egy LLM-ágens vault (tudás-trezor) kontextusában azt az önvezérelt folyamatot jelenti, amelynek során az ágens az aktív interakciókból, hibajavításokból és a környezet-felderítésből származó tapasztalatait **tömör, újrahasznosítható memóriafájlokká és strukturált szabályokká sűríti** anélkül, hogy a felhasználónak manuálisan kellene rögzítenie [Anthropic Claude Code memory]. A mechanizmus biztosítja, hogy az értékes felismerések — sikeres build parancsok, architektúra-minták, projekt-konvenciók — a jövőbeli munkamenetekben is elérhetők maradjanak egy perzisztens tudásrétegben (a Claude Code esetében ez a dinamikusan bővülő `MEMORY.md` + specifikus topik-fájlok).

### Három alapelv-pillér

| Alapelv | Forrás | Kapcsolat a crystallization-höz |
|---|---|---|
| **Karpathy LLM-Wiki / Compilation** | Karpathy Software 3.0 lecture, LLM-Wiki tweet thread | A nyers kontextust és a végtelen beszélgetéseket **LLM-barát "wiki" formátummá fordítja le** (compilation), amelyből az agent később hatékonyan olvas |
| **Constitutional AI / RLAIF** | Bai et al. 2022, Anthropic Collective CAI 2024 | Emberi címkézők helyett **magas szintű alapelvek + AI-feedback** értékeli a kimenet minőségét. A crystallization erre adaptálódik: az ágens maga ítéli meg, mi értékes a memóriába |
| **Self-Rewarding LLM** | Yuan et al. 2024 (arXiv 2401.10020) | Az LLM **a saját outputját értékeli ki** ("LLM-as-a-Judge"), így nemcsak generálni, hanem értékelni is egyre jobban tud. A kristályosítás ezt egy folyamatos önreflexiós hurokká szervezi |

### Knowledge crystallization vs. fine-tuning

A két megközelítés a tudás reprezentációjában és frissíthetőségében különbözik gyökeresen [Self-Rewarding LLM, Voyager, LIMA]:

- **Klasszikus fine-tuning:** a hálózat **belső súlyait** módosítja statikus adathalmazon. Lassú, számításigényes, katasztrofális felejtés és "alignment tax" rizikóval. A tudás "betonozódik".
- **Knowledge crystallization:** **nem módosítja a modell súlyait**. A tudást **független szöveges memóriapufferekbe, dinamikus szabályokba vagy futtatható kódkönyvtárakba** (Voyager skill library) menti. A modell ezt fekete dobozként, a kontextusablakán keresztül használja fel futásidőben — gyors, specifikus, drága újra-tanítás nélkül.

## 2. Kanonikus megközelítések (5 fő minta)

### Self-Rewarding LLM (Yuan et al. 2024, Meta)
- **Mechanizmus:** "LLM-as-a-Judge" prompttal a modell saját válaszait értékeli; iteratív DPO-tréning során **saját maga generálja a jutalmakat**, így nemcsak az instruktálható, hanem az ítélőképessége is fejlődik
- **Kulcs-újdonság:** Áttöri az emberi visszajelzések szűk keresztmetszetét — folyamatos önfejlesztés human-feedback nélkül
- **Forrás:** arXiv 2401.10020

### Constitutional AI / RLAIF (Anthropic 2022 + Collective CAI 2024)
- **Mechanizmus:** Egy előre megírt szabály- és alapelv-lista ("alkotmány") biztosítja a felügyeletet. A modell ezen elvek alapján **kritizálja és javítja a saját válaszait**. RLAIF: a költséges emberi preferencia-adatok helyett egy másik LLM generálja a feedback-et.
- **Kulcs-újdonság:** Az emberi felügyelet **a legmagasabb absztrakciós szintre tolódik** — az ember csak az alkotmányt írja meg, nem az egyes válaszokat címkézi
- **Forrás:** Bai et al. arXiv 2212.08073, Anthropic Collective CAI 2024

### Reflexion (Shinn et al. 2023)
- **Mechanizmus:** Az ágens a korábbi próbálkozásokból kapott visszajelzéseket (skaláris vagy szabad szöveg) **verbálisan reflektálva** értékeli, és a tanulságokat egy epizodikus memóriapufferben tárolja. Ez **pszeudó-gradient**: a modell a saját szavaival "finomhangolja" a következő lépéseit súlyfrissítés nélkül.
- **Kulcs-újdonság:** A trial-and-error tanulás súlyfrissítés nélkül; HumanEval-en példátlan ugrás
- **Forrás:** arXiv 2303.11366

### Karpathy LLM-Wiki / Compilation
- **Mechanizmus:** Kódbázisok és komplex környezetek automatikus elemzése és "lefordítása" **LLM-barát dokumentációs formátummá** ("Deep wiki"). Egy automata ágens a nyers fájlstruktúrát előemészti és optimalizált, kontextusba illeszthető tudásbázissá sűríti.
- **Kulcs-újdonság:** Magát a tudásbázis-építést is automatizálja — a "compilation" elv adaptálva markdown-vaultra
- **Forrás:** Karpathy Software 3.0 / Lex Fridman 2024, LLM-Wiki tweet thread

### Confidence-alapú thresholded auto-propagáció (architektúra-minta)
- **Mechanizmus:** Az ágens minden Learning bullet-hez **konfidencia-pontszámot** rendel (logprob-alapú, semantic consistency / SelfCheckGPT, vagy LLM-judge). Threshold (pl. 0.85) felett: csendes auto-propagáció. Threshold alatt: marad a klasszikus user-confirm batch preview.
- **Kulcs-újdonság:** Karpathy "autonomy slider" elv operacionalizálása — a user kontrollálja a threshold-ot, nem a per-item engedélyezést
- **Forrás:** szintézis (Self-Rewarding + Reflexion + G-Eval + Claude Code memory)

### Különbségek a confidence megállapításában

| Megközelítés | Confidence forrása | Emberi felügyelet |
|---|---|---|
| **Self-Rewarding / RLAIF** | Dedikált LLM-judge / AI-preferenciákra tanított reward model | Iktatva (futásidőben) |
| **Reflexion / STaR** | Külső környezeti **objektív siker** (kód lefutott? teszt zöld?) | Iktatva (futásidőben) |
| **Constitutional AI** | Modell magával szemben kritikai prompt + alkotmány-elvek | Csak az alkotmányt írja az ember |
| **Karpathy LLM-Wiki** | Az automata-agent saját kompresszió-minősége | Iktatva (compilation során) |

## 3. Tech-stack opciók 2026-ban

> A Peti-vault (Obsidian + Johnny-Decimal + 11.11 + 280 skill) **fájl-alapú markdown** — nem vector-store. A tech-stack ezt tükrözi: kevés runtime-infrastructure, sok prompt + script + git.

### (a) LLM-as-judge frameworks

| Eszköz | Tradeoff | Mire jó |
|---|---|---|
| **Anthropic Constitutional self-critique** | Magas setup-komplexitás (alkotmány tesztelése iteratív), dupla token, de **megbízható** | Production baseline a vault routing-judge szerepre |
| **G-Eval** (Liu et al. 2023) | Chain-of-Thought + űrlapkitöltés paradigma + logprob normalizálás. Position/verbosity/self-enhancement bias-mitigálás kell | Akadémiai-szintű kalibrált scoring |
| **OpenAI Evals / RAGAS** | Forrásokban csak általánosan említve. Külön package-ek, vault-integrácó nem out-of-box | Külső validáció, dataset-tesztelés |

**Költség:** Alacsony-Közepes (dupla token a judging miatt). **Bias-mitigáció kritikus:** Self-enhancement bias (Claude 25%-kal magasabb win-rate-et ad önmagának), Verbosity bias, Position bias.

### (b) Confidence scoring könyvtárak

| Módszer | Setup | Költség | Megbízhatóság |
|---|---|---|---|
| **Logprob-alapú** (G-Eval normalizálás) | Alacsony (közvetlen API-lekérdezés) | Ingyenes (one-call) | Olykor hamis magabiztosság — overconfidence |
| **Semantic consistency** (SelfCheckGPT — Manakul 2023) | Közepes (több generálás) | Drága (N-szeres token) | Nagyon megbízható hallucináció-detektálásra |
| **Ensemble agreement** | Közepes-Magas | Drága | Robusztus, de skálázási nehézség |

A **kombinált megoldás** ajánlott: logprob first-pass + semantic-consistency a borderline esetekre.

### (c) Automatikus knowledge-distillation pipelines

| Minta | Setup | Költség | Megjegyzés |
|---|---|---|---|
| **Claude Code auto-memory** | Magas (Anthropic-specifikus) | Magas | Production-szintű, `MEMORY.md` + topik-fájl auto-frissítés. **Direkt minta a Peti-vault crystallization-höz** |
| **MemGPT** | Magas (OS-szerű virtual memory) | Magas | Túl komplex pure-markdown vaultra; vector-store réteggel jönne be (SV-1) |
| **Voyager skill-library** | Magas | Magas | Code-skill specifikus; analógia: `00-Meta/skills/` futtatható mappa |

**Failure-mode:** A háttér-agentek olvasási/írási műveletei rengeteg tokent használnak. A modularitás kritikus (path-scoped szabályok, subagent-ek).

### (d) Git-hook + pre-commit validációk

| Eszköz | Setup | Költség | Megbízhatóság |
|---|---|---|---|
| **Non-interaktív Claude (`claude -p`)** | Közepes (script + hook config) | Közepes (LLM-hívás) | Magas (full content review) |
| **Guardrails AI** | Közepes (Pydantic séma) | Alacsony (determinisztikus) | Nagyon magas |
| **NeMo-Guardrails** | Magas (rule DSL) | Alacsony | Nagyon magas |

A **determinisztikus szintaktikai + szemantikai validáció elengedhetetlen** a vault-szennyezés ellen. Tipikus ellenőrzések: érvényes frontmatter, kötelező mezők (`name`, `type`, `created`, `updated`), tag-taxonomy compliance, wikilink-szintaxis, duplikátum-detekt.

### (e) DPO / RLAIF könyvtárak (fine-tuning útvonalon)

> **Csak akkor releváns,** ha a kristályosított tudást egy saját modell súlyaiba akarjuk sütni (SV-2 territory).

- **DPO (Direct Preference Optimization):** Egyszerű klasszifikációs veszteség, kikerüli a bonyolult reward model + RL hurok felépítését. Stabilabb mint PPO.
- **RLAIF:** Kész LLM generálja a preferencia-adatokat (emberi annotálás helyett).
- **QLoRA:** Kvantált architektúra, egyetlen GPU-n is elfér.

**Megbízhatóság kiváló**, de **most még overkill** — a Peti-vault prompt-alapú memóriájához nincs szükség weight-update-re; ez Phase C #2 (Recursive self-improvement) territory.

## 4. Friss áttörések 2024-2026

**(a) Self-Rewarding LLM (Yuan et al. 2024)** — áttörte az emberi visszajelzések teljesítménybeli szűk keresztmetszetét. Az iteratív DPO-tréning során a modell saját maga generálja a jutalmakat. Eredmény: nemcsak az utasítások követésében, hanem a saját **ítélőképességében** is folyamatos fejlődés [arXiv 2401.10020].

**(b) Collective Constitutional AI (Anthropic 2024)** — az eredeti zárt-ajtós CAI helyett ~1000 fős laikus amerikai csoport demokratikus szavazással alakította ki a "közösségi alkotmányt" (objektivitás, kiegyensúlyozottság, akadálymentesítés). Megvalósult a **skálázható alapelv-konszenzus** [Anthropic Collective CAI blog].

**(c) Reflexion + verbális RL** — drága súlyfrissítések nélkül lehetővé tette a trial-and-error tanulást. A szöveges reflexiók **pszeudó-gradiensként** szolgálnak; HumanEval-en példátlan ugrás. Hasonló elvre épít a **STaR** (Self-Taught Reasoner): helyes válaszokhoz vezető sikeres logikai levezetésekből bootstrappel [arXiv 2303.11366, 2203.14465].

**(d) Önmódosító kód-ágensek (Promptbreeder, Voyager)** — a *Promptbreeder* önreferenciális rendszer: az LLM nemcsak a feladatmegoldó promptokat mutálja, hanem **a mutációs promptokat is**. A *Voyager* (Minecraft) futtatható kódokból álló **képesség-könyvtárat** épít. Mindkettő bizonyítja: az ágensek **kristályosíthatnak komplex, hierarchikus szabályokat katasztrofális felejtés nélkül** [arXiv 2309.16797, 2305.16291].

**(e) Anthropic Claude Code memory pattern (2024-2026)** — éles production-szint! Claude **automatikusan figyeli a terminál munkamenetet** és emberi utasítás nélkül leírja a tanulságokat `.claude/projects/<repo>/memory/MEMORY.md` + topik-fájlokba (pl. `debugging.md`) [Anthropic Claude Code docs].

### Mit változtatott a research direction-ben?

A pre-2024 korszak az **RLHF**-re és klasszikus modell-súly frissítésekre fókuszált — az LLM "merev, rögzített tudásbázis" volt. Az új irány az **"LLMs as OS"** felfogás felé tolódott: kontextusablak = RAM, háttértár = autonóm módon frissülő **epizodikus és strukturált szöveges memória**. A fejlődés fő hajtóereje:

1. Modellszintű **önreflexió** (Reflexion)
2. Futásidejű **verbális memóriabővítés** (Self-Rewarding, RLAIF)
3. **AI-AI feedback** loop (Constitutional AI)
4. A tudás-**beégetés** helyett a dinamikusan bővülő, futtatható szabályokká történő **folyamatos, valós idejű kristályosítás**

## 5. Failure-modes és limitációk

### (a) Hallucination amplification
Ha az ágens automatikusan kristályosít egy téves megoldást vagy hibás következtetést, az **a memória részévé válik**. A Claude Code dokumentáció "konyhai mosogató" (kitchen sink) vagy "folyamatos javítgatás" hibaként azonosítja: ha a kontextusablak megtelik sikertelen próbálkozásokkal és a modell ezt sűríti be, **a rossz tudás bebetonozódik**.

### (b) Reward hacking + LLM-judge biasok (Self-Rewarding csapda)
Specifikus rendszerszintű torzítások:
- **Self-enhancement bias:** GPT-4 vagy Claude **részrehajló a saját outputja iránt** (Claude pl. 25%-kal magasabb win-rate-et ad önmagának)
- **Verbosity bias:** a modell a **hosszabb, bőbeszédűbb válaszokat** jutalmazza (még ha tömörebb minőségibb lenne)
- **Position bias:** az **elsőként bemutatott opciót** részesíti előnyben

A modell ezekre a biasokra optimalizál az objektív helyesség helyett — **jutalom-hekkelés**.

### (c) Confidence calibration hiánya
Karpathy: az LLM-eknek **nincs megfelelő belső önismereti modellje** (internal model of self-knowledge). Hajlamosak a **túlreagálásra**, ezért **nagy tétű döntéseknél** (10 000 soros kódmódosítás) az automatizáció túlzott magabiztossága **kritikus veszélyforrás**.

### (d) Compound errors / model collapse
Több munkamenet után a `CLAUDE.md` / `MEMORY.md` túlzsúfolttá (over-specified) válhat. Túl hosszú, egymásnak ellentmondó szabályokkal a modell **figyelmen kívül hagyja a fontos utasításokat** (zajban elvesznek) → konzisztencia és teljesítmény romlása.

### (e) Loss of human oversight
A user gyakran **nem látja, mi kerül a vaultba** — "nem tudom, mit mentett el az auto-memória" jelenség. Karpathy: az AI önállósodása ellenére **human-in-the-loop kötelező szűk keresztmetszet**.

### (f) Privacy / cross-session leak
Az LLM-ek **adatszivárgásra hajlamosak**. Az auto-memória legyen szigorúan **machine-local + git-repo-bound** (Claude Code mintára), ne osztódjon meg felhős környezetek között.

### Safeguards a forrásokból

| # | Védvonal | Forrás |
|---|---|---|
| 1 | **Szigorú verifikáció:** "Ha nem tudod verifikálni, ne shipeld" — tesztek, lintek, screenshot-compare | Claude Code docs |
| 2 | **Autonomy slider + leash:** Karpathy autonomy-csúszka — kis, ellenőrizhető lépésekben elengedni az AI kezét | Karpathy Software 3.0 |
| 3 | **Determinisztikus hookok + Guardrails:** NeMo-Guardrails, Guidance — szintaktikai/szemantikai validáció minden módosítás előtt | Eugene Yan, Claude Code hooks |
| 4 | **Agresszív memória-menedzsment:** rendszeres ruthless prune; `/memory` audit-parancs | Claude Code docs |
| 5 | **Classifier + sandboxing:** külön osztályozó model a háttérben + OS-level isolation | Self-Rewarding bias-mitigáció |

## 6. Implementáció a Peti-vault kontextusban

> **Kontextus:** A vault jelenleg már rendelkezik egy **félautomata Crystallization-protocol**-lal: a `/11.11stop` végén az agent batch preview-vel javaslatot tesz, a user OK-zik. A cél a >0.85 confidence tételek auto-propagálása. A meglévő fájlok és skill-ek:
> - **Routing decision tree:** [[11-wiki/Crystallization-protocol]] — 11-lépéses fa (ADR / vault-szabály / wiki / Glossary / Infrastructure / Skill-map / User / Dashboard / Projekt / Backlog / kérdez)
> - **Skill:** `00-Meta/skills/propagate-session/` — már létezik, ez a "manuális" workflow scriptelt verziója
> - **Session-fájl:** `08-Sessions/<slug>.md` — itt vannak a `## Learnings` bullet-ek
> - **Propagation log:** session-fájl alján `## Propagation log` — auditálható

### (1) Confidence-scoring mechanizmus per Learning bullet (LLM-as-a-Judge)

A `/11.11stop` lefutáskor egy **háttér-prompt** értékelő módba kapcsolja az ágenst. G-Eval-szerű Chain-of-Thought űrlap minden Learning bullet-re:

```
Bullet: "<text>"
Vizsgáld meg:
- factuality: 0.0-1.0 (a leírt tény ellenőrzött-e a session-history-ben?)
- novelty: 0.0-1.0 (nem szerepel-e már a vaultban?)
- routing_fit: 0.0-1.0 (a célmappa illeszkedik a tartalomhoz?)
- bias_check: ne legyen self-enhancement / verbosity / position bias

Output JSON:
{
  "bullet": "...",
  "target": "11-wiki/...",
  "rationale": "1-2 mondat",
  "confidence": 0.0-1.0
}
```

A confidence végső értéke a 3 sub-score harmonikus átlaga (a leggyengébb hozzájárul a legtöbbet — biztonságos becslés). **SelfCheckGPT-stílusú semantic consistency** opcionálisan a borderline (0.70-0.85) sávban: 3 független generálás, ha eltérnek → confidence levonva.

### (2) Decision tree routing — autonomy slider elv

Kibővített `Crystallization-protocol` routing:

```
Routing match (existing 11-step tree) →
JSON output (target, confidence) →
├── confidence ≥ THRESHOLD (default 0.85) → AUTO-PROPAGATE
│   ├── git commit pre-state ("auto-crystallization backup")
│   ├── append target file (Edit tool, scriptelt)
│   └── audit log entry
└── confidence < THRESHOLD → MANUAL BATCH PREVIEW (existing flow)
    └── user OK / módosít / skip
```

A meglévő [[11-wiki/Crystallization-protocol]] 11-lépéses fa változatlan; csak a **scoring + threshold-elágazás** új.

### (3) Git-revert safeguard

A "trust-then-verify gap" ellen:
- **Minden auto-propagáció előtt** automatikus `git commit -m "auto-crystallization pre-commit backup <session-slug>"`
- Pull-back: `git revert <hash>` vagy `/rewind <session-slug>` dedikált parancs
- A `vault-autosave` (10-percenkénti commit + push GitHub-ra) ezt erősíti — minden auto-prop hash-elt és recoverable

### (4) Audit log — transzparencia

Új fájl: `00-Meta/auto-crystallization-audit.md` (vagy a session-fájl `## Propagation log` szekciója szigorúbb formátumban):

```markdown
## Auto-crystallization audit log

| Dátum | Session | Bullet | Target | Confidence | Rationale |
|---|---|---|---|---|---|
| 2026-05-13T14:22 | sv5-research | "Self-Rewarding bias..." | [[11-wiki/sv-05]] | 0.92 | Új koncepció, vault-ban nincs |
| 2026-05-13T14:22 | sv5-research | "Reflexion pszeudo-gradient" | [[11-wiki/sv-05]] | 0.88 | Új evergreen wiki |
```

User hetente átnézi (vasárnap, a `vault-cleanup` cron mellett); ha valami nem stimmel, `git revert` + szabály-update.

### (5) Hot-reload threshold tuning

A `THRESHOLD` ne legyen hardcoded:
- Tárolás: `00-Meta/crystallization-config.yaml` (új fájl)
  ```yaml
  auto_threshold: 0.85
  judge_model: claude-opus-4-7
  bias_mitigation: true
  shadow_mode: false
  ```
- A `/11.11stop` futáskor hot-reload — user session közben is állíthatja
- Per-target-mappa override is lehetséges: `07-Decisions` (ADR) magasabb (0.95), `04-Tasks/Backlog` alacsonyabb (0.75)

### (6) Roadmap: Baseline → 80% auto-rate 4-6 hét alatt

Reflexion-stílusú folyamatos visszacsatolási hurokkal:

| Hét | Mód | Threshold | Cél |
|---|---|---|---|
| **1. Shadow mode** | 1.0 (semmi nem auto) | 1.0 | Baseline mérés: LLM-judge mennyiszer egyezik a user OK-zott javaslatokkal? |
| **2-3. Konzervatív auto** | 0.95 | 0.95 | A legbiztosabb tételek auto-prop. Reflexion-loop: ha user manuál-ágra került tételt máshova route-ol, ezt a hibát szövegesen visszatápláljuk a judge-promptba (`MEMORY.md` epizodikus rész). |
| **4-5. Agressive tuning** | 0.85 | 0.85 | A prompt már robusztus a Reflexion-javítások után. User az `audit.md`-t nézi, nem interaktív session-megszakítást. |
| **6. Stable state** | ~80% auto-rate | 0.85 | A tudás zöme megszakítás nélkül, láthatatlanul kristályosodik (Claude Code analog). User csak az edge-case 20%-kal találkozik. |

### Integráció a meglévő infrastruktúrával

- **Skill:** `00-Meta/skills/propagate-session/SKILL.md` bővítése a confidence-scoring lépéssel — a routing decision tree változatlan, csak a "batch preview" elágazik auto vs manual ágra
- **Cron:** A heti `vault-cleanup` (vasárnap 04:00) audit-log-ellenőrzést is futtat: ha az utolsó 7 nap auto-prop > N és user nem revertelte, threshold csökkenthető
- **Hook:** Pre-commit Guardrails-szerű validáció: frontmatter-schema, tag-taxonomy, wikilink-szintaxis, duplikátum-detekt — minden auto-prop ezen átmegy
- **MEMORY.md update:** A judge-prompt Reflexion-hibajavításai a `~/.claude/projects/-root/memory/MEMORY.md`-be kerülnek (mert ez az egész vault auto-memory entry-pointja)

## 7. Mit kell tovább kutatni?

### Open questions (6 nyitott kérdés)

1. **Cross-session tudáskonszolidáció + szemantikai deduplikáció:** Több tucat munkameneten átívelően hogyan **konszolidáljuk** a hasonló tanulságokat anélkül, hogy az új tapasztalatok felülírnák a régi érvényes szabályokat? Embedding-alapú dedup + contradiction-detection a következő lépés.
2. **Crystallization + fine-tuning hibrid (kritikus komplexitási küszöb):** Hol van a határ, amikor érdemes a prompt-alapú memóriát (`MEMORY.md`) **modell-súlyokba sütni** QLoRA-val? Ez kapcsolódik az SV-2 (recursive self-improvement) tengelyhez.
3. **Multi-agent vault — konfliktuskezelés:** Ha több párhuzamos agent (Claude / Codex / Gemini, plus subagentek) ír egy közös vault-ba, milyen konszenzus/conflict-resolution kell? (Generative Agents kutatás csak single-agent reflexiót old meg.)
4. **Konfidencia-kalibráció LLM-kimeneteknél:** Hogyan integráljuk a klasszikus kalibrációs módszereket (Platt scaling, isotonic regression) a generatív modellek confidence-output-jára? Karpathy szerint az LLM-eknek nincs jó belső self-knowledge modellje.
5. **Continuous-eval a vault-on:** Hogyan futtassunk háttérben aszinkron LLM-as-judge validációt a dinamikusan frissülő vault-on (Anthropic Foundry mintára)? Hetente egy "garbage collection + minőség-audit" agent-run.
6. **RLAIF / Self-Rewarding bias-mitigáció:** Hogyan akadályozzuk meg a reward-hacking és self-enhancement bias felerősödését, amikor a modell **saját maga dönti** mi kerüljön a tartós memóriába?

### További papers / blog-posts a következő research-iterációhoz

1. **SelfCheckGPT** (Manakul et al. 2023) — zero-resource black-box hallucination detection ensemble-szerű módszerrel. **Direkt használat:** cross-session konszolidáció + megbízhatóbb auto-crystallization confidence.
2. **HELM — Holistic Evaluation of Language Models** (Liang et al. 2022) — folyamatos kiértékelés (kalibráció, robusztusság, torzítás) többdimenziós keretrendszere. **Direkt használat:** vault-minőségbiztosítás guardrails.
3. **G-Eval** (Liu et al. 2023) — LLM-as-a-judge keretrendszer Chain-of-Thought + logprob normalizálással. **Direkt használat:** a (1) confidence-scoring mechanizmus implementációs alapja.
4. **InstructGPT** (Ouyang et al. 2022) — az "alignment tax" mélyen tárgyalt; kritikus a crystallization + súlymódosítás hibrid jövőjéhez.

## Phase A+ bővítés (2026-05-12 deep-research)

A Phase A 27 forrásához **+462 új** csatlakozott 4 `--mode deep --no-wait` web-search-szel (hallucination-amplification, RLAIF CAI 2 prod, privacy distillation, Self-Rewarding 2026). **489 forrás** a notebookban.

### Q1 — Optimális 3-elem kombináció (NotebookLM-szintézis)

A legújabb kutatások szerint a **tömörítésből (compaction) fakadó kontextus-romlás** a fő veszély — a puszta szöveges összefoglalások során a tények akár **60%-a elveszhet**. A 3 ajánlott elem:

**1. réteg — Knowledge Objects (KO) a markdown-összefoglalók helyett.** A klasszikus in-context memória + fájl-tömörítés helyett **hash-címzett `(subject, predicate, object, provenance)` tuple-ök** külső adatbázisban. **Tesztelt értékek:** 100% tény-visszakeresési pontosság, 78.9% multi-hop reasoning, konstans (alacsony) éves költség lineáris növekedés helyett. **Immunis a kontextus-romlásra** mert strukturálisan elválasztja a tárolást az LLM-feldolgozástól. **Tech-stack:** SQLite vagy PostgreSQL kulcs-érték tár a markdown fájlok mellé; kisebb modell (pl. Haiku) O(1) idő alatt kikeresi a hashelt tényeket, nagyobb modell (Sonnet) generálja a végleges választ.

**2. réteg — Checkpointed önreflexiós hurok („Knows-but-violates" ellen).** A modellek többkörös iterációkban hajlamosak elfelejteni vagy figyelmen kívül hagyni a korábbi instrukciókat, még akkor is, ha a belső reprezentáció szerint „tudják" a szabályt. **Megoldás:** 2. és 4. kör után **strukturált reflexiós checkpointok**. **Tech-stack:** `retrieve → generate → verify` munkafolyamat „autonomy slider" elvén, MCP-vel szabványosított külső-rendszer-csatlakozás.

**3. réteg — „Verification-Grade" KIP (Kritikus Intellektuális Tulajdon) + Provenance réteg.** A megbízhatóság és auditálhatóság kulcsa a **pontos forrásmegjelölés (provenance)** a tárolt tények mellett. Audit-naplók + hibanaplók + **near-miss logs** + kriptográfiai bizonyítékok. **Tech-stack:** „drift ops" + observability eszközök; minden output strukturált formátumban (JSON); span-szintű hivatkozások.

### Bevezetési sorrend
1. **KO Adatbázis** — kritikus strukturált tények migrálása SQLite/PostgreSQL-be → leállítja a kontextusablak-túlcsordulást
2. **MCP bevezetése** — stabil híd LLM ↔ fájlrendszer ↔ KO-DB
3. **Iteratív reflexiós pontok + provenance** — 11.11 session-be checkpoint-ok + verification-grade audit-réteg

### Q2 — Production-ready vs akadémiai (NotebookLM-szintézis)

**Production-ready (ipari szinten validált):**
- **„Software-as-Labor" + Szendvics-topológia (Sandwich Topology):** Az iparág túllépett a SaaS-en, **munkaerő-kiváltó eredményt** értékesít. Architektúra: emberi szándék (intent) → gépi végrehajtás (execution) → emberi verifikáció és felelősségvállalás (underwriting).
- **Liability-as-a-Service + Kriptográfiai Provenance:** A „Trójai Faló" externalitások miatt a marginális érték generálásról ellenőrzésre tevődött át. Az ipari moat ma a **kriptográfiailag igazolható adatszármazás** + magas-tétű kockázatok árazása (Liability-as-a-Service), verifikációs-szintű ground truth biztosítékként.
- **Knowledge Objects (KO) perzisztens memóriához:** A klasszikus context-compaction adatvesztése helyett a tények **„első osztályú objektumokká"** alakítása az elterjedt ipari sztenderd hosszú-távú memóriakezelésben.

**Akadémiai stage (paper-only, kísérleti):**
- **Model Collapse matematikai/statisztikai prevenció** — a jelenség (rekurzív szintetikus adatokon való „go MAD" devalváció) széles körben bizonyított, de a megoldó mechanizmusok (pl. $\pi^2/6$ matematikai pathway) csak kutatás-szinten.
- **Dinamikus Context Equilibria** — task-drift + kontextus-vesztés megállító elméleti keretek kísérleti fázisban.
- **Cross-Layer Attention Probing** — „Lookback lens" típusú belső attention-térkép-elemzés rendkívül aktív, de production-szinten túl drága.
- **Új generációs Reward Hacking mitigáció** — adverziális preferencia-optimalizáció (RM-LLM játékok), Energy Loss Phenomenon RLHF-modellezés — nyílt akadémiai benchmarkokon validálódnak.

### Q3 — Cost-sensitive trade-off (NotebookLM-szintézis)

**Univerzális döntés mindhárom tier-re:** A klasszikus „in-context" memóriát **TELJESEN le kell vágni**. 1000 tény → évi $2.051; 5000 tény → évi $10.151; 7000 tény → $14.201. A KO-architektúra ellenben **konstans évi $56** és **97-99% token-megtakarítás**.

| Tier | Mit megtartunk | Mit vágunk le |
|---|---|---|
| **$50/hó (mini)** | KO-DB ($56/év) + nulla-extra-hívás Prompt Engineering + decoding constraints + custom validáló scriptek (formátum, PII) | Post-gen verifiers / LLM-as-a-judge (+1 hívás), Agentic pipelines (+m hívás), Self-verification (+1 iter) |
| **$200/hó (hibrid)** | + Cost-Aware HITL (csak low-confidence / high-risk emberi ellenőrzés) + tier validation + caching + kisebb judge-modellek (GPT-4.1-mini, Lynx 2.0, Glider) | Drága Frontier modellek bíróként, általános OSS-modellek bíróként, minden válasz emberi ellenőrzése |
| **$500/hó (prémium)** | + Agentic pipelines + post-gen NLI claim-checkers + data flywheel user-feedback-ből | Feltétel nélküli RAG-lekérdezés (kapuzva risk-signal-lel), tisztán-RAG megközelítés (max-pontossághoz nem elég) |

**Konkrét számokkal:** A 2146 futásból álló benchmark **csak az API-hívásokra $450-t emészt fel** → még a $500/hó tier is feszített ha „minden kimenetet bírálatra teszünk".

## Audio overview

A NotebookLM beépített audio-overview funkciójával ~10-15 perces podcast-szerű összefoglaló generálható. Phase A végén futtatjuk:

```bash
notebooklm generate audio -n a219107d-e8fe-4ece-b721-ae6e3182bd45
```

## Akció-pontok ehhez a tengelyhez

- [ ] **Phase B sprint-bontás:** 4-6 sprint a 4-6 hetes roadmap-re (Shadow mode → Stable state)
- [ ] **Skill-bővítés:** `00-Meta/skills/propagate-session/SKILL.md` confidence-scoring step hozzáadása
- [ ] **Új fájl:** `00-Meta/crystallization-config.yaml` (auto_threshold + judge_model + bias_mitigation toggle)
- [ ] **Új fájl:** `00-Meta/auto-crystallization-audit.md` (időbélyegezett log)
- [ ] **Hook:** pre-commit Guardrails validation script (`/usr/local/bin/vault-frontmatter-validate`)
- [ ] **Audio overview** generálás + letöltés (referenciaként közlekedés közben)
- [ ] **Cross-link:** SV-2 (recursive self-improvement) — Phase C-ben a crystallization közvetlen elődje a self-improvement-nek

## Kapcsolódó

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — a 8-tengelyű ADR
- [[11-wiki/Crystallization-protocol]] — **a MEGLÉVŐ félautomata protokoll**, amit ez automatizál
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — az alapelv
- [[11-wiki/11.11-session-protokoll]] — a session-orchestration ahova ez beépül
- [[11-wiki/Auto-context-loading]] — a session-induló context-pre-load (a propagáció másik fele)
- [[10-raw/2026-05-12 — Superintelligence research source pool]] — a teljes source-pool
- [[11-wiki/sv-01-memory-architecture]] — kapcsolódó tengely (memory-réteg, amibe a kristályosított tudás kerül)

## NotebookLM-konverzáció

- **Notebook ID:** `a219107d-e8fe-4ece-b721-ae6e3182bd45`
- **Címe:** SV-5 Crystallization (Owner)
- **Conversation ID:** `146db45a-d9a2-462e-bed4-cb6aca58ea95`
- **Források:** 27 (24 ready, 2 YouTube error — Yannic Kilcher CAI + AI Explained Self-Rewarding; 1 add-research első próbálkozás failed, második retry sikeres)
- **Kérdések:** 7/7 válaszolva (`/tmp/sv-research/sv5-q{1..7}-*.txt`)
- **Audio overview:** TODO Phase A végén (`notebooklm generate audio`)
