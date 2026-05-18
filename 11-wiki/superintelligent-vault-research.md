---
name: Superintelligent vault research — master index
type: wiki
tags: ["#type/wiki", "agi", "agent-architecture", "research", "master-index"]
created: 2026-05-12
updated: 2026-05-12
status: phase-a-done
related: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
---

# Superintelligent vault research — master index

Phase A output a 8-tengelyű vault-evolúciós research-ből. Minden tengelyhez egy mély `sv-{n}` cikk, ami foundational paper-eket, friss áttöréseket, production tech-stack-eket, failure-mode-okat és **konkrét implementációs lépéseket** szintetizál.

## Hol tartunk

| # | Tengely | Phase A | Phase A+ | Wiki-cikk | NotebookLM (source-count) |
|---|---|---|---|---|---|
| 1 | Memory architecture | 🟢 | 🟢 done | [[11-wiki/sv-01-memory-architecture]] | `e2e31ae8...` (249) |
| 2 | Recursive self-improvement | 🟢 | 🟢 done | [[11-wiki/sv-02-recursive-self-improvement]] | `a2425bc7...` (1009) |
| 3 | Multi-agent orchestration | 🟢 | 🟢 done | [[11-wiki/sv-03-multi-agent-orchestration]] | `c7eba59a...` (737) |
| 4 | Tool composition | 🟢 | 🟢 done | [[11-wiki/sv-04-tool-composition]] | `90e132a1...` (921) |
| 5 | Crystallization automation | 🟢 | 🟢 done | [[11-wiki/sv-05-crystallization-automation]] | `a219107d...` (489) |
| 6 | World-model / knowledge graph | 🟢 | 🟢 done (Q3 retry ✓ 2026-05-12 20:35) | [[11-wiki/sv-06-world-model-knowledge-graph]] | `82e9046d...` (73) |
| 7 | Continuous evaluation | 🟢 | 🟢 done | [[11-wiki/sv-07-continuous-evaluation]] | `d6e26ab3...` (395) |
| 8 | NotebookLM as cognitive layer | 🟢 | 🟢 done | [[11-wiki/sv-08-notebooklm-cognitive-layer]] | `a60d993b...` (1200) |

**Phase A+ teljes — 8/8 tengely ✅** (2026-05-12 19:30 körül zárult).

**Összesített növekedés:** Phase A 200-250 forrás → Phase A+ után **~4800 forrás** a 8 notebookban (+19× bővülés). 24/24 mély-komplex kérdés válaszolva (5 közvetlen agent + 3 manuális). Master tudás-bázis méretrendekkel megnőtt.

### Phase A+ új cross-cutting insights (a 8 tengely érett szintézise)

**A. Konvergens minta: „Files-as-State + MCP + Skill-tokozás + Reflektív optimalizáló".** Az SV-2 (Skills+ReFlect+GEPA), SV-3 (Filesystem-as-State + Orchestrator+P2), SV-4 (SKILL.md+Tool-Search+MCP), SV-8 (Memory-Stack+MCP-bridge+DSPy/GEPA) **mind ugyanazt a 4-pilléres mintát** ajánlják különböző absztrakciós szinten — ez **az ipari 2026-os konszenzus** az agent-vault architektúrára. **Anthropic „simplicity over framework" + Claude Code paradigma a központi gravitációs pont**, nem a CrewAI / AutoGen / LangGraph framework-réteg.

**B. A Peti-vault MÁR Tier-$50 közeli (SV-8 self-referential insight).** A meglévő `02-Projects + 04-Tasks/Backlog + 07-Decisions + 08-Sessions` mappa-struktúra **lényegében már a 4-fájlos Karpathy working/episodic/semantic memory-stack gyakorlati megvalósítása**. Hiányzó elemek a Tier-$50 minimalista config-hoz: **(1) MCP-bridge** az Obsidian-vault fölött + **(2) 11.11stop crystallization-hook**. Mindkettő 1-2 hetes sprint Phase B-1-ben.

**C. Cost-architektúra konkrét számokkal (SV-5 + SV-7 + SV-8 keresztmetszete).**
- **In-context memory teljesen vágandó** minden tier-en: 1000 tény = $2.051/év, 5000 = $10.151, 7000 = $14.201 → KO-architektúra konstans **$56/év** (97-99% token-megtakarítás)
- **GraphRAG indexelés a legdrágább**: 50.000 token/globális-query (10× klasszikus RAG)
- **Multi-agent: +90% minőség / +15× token-cost** — SV-3 kategorikusan: P2P GroupChat zsákutca, **Orchestrator+isolated subagent+summary-only return** kell
- **MCP code-execution ~98.7% token-megtakarítás** vs prompt-tool-list (SV-4)

**D. RSI legutoljára: konvergens biztonság-konszenzus (SV-2 + SV-5 + SV-7 metszete).** Mind a 3 tengely **azonos sandbox+git-pre-commit+Pareto-szelekciós merge mintát** ajánl. **76-98% self-correction blind spot** (SV-2) + reward hacking (SV-5) + criteria-drift (SV-7) → **SV-2 (recursive self-improvement) csak a többi STABILIZÁLÓDÁSA UTÁN** engedhető. A Phase B sprint-sorrend megerősítve: SV-5 → SV-1+SV-7 → SV-4 → SV-8 → SV-3 → SV-6 → **SV-2 utolsó**.

**E. Production-ready vs akadémiai mérleg (8 tengely 2024-26 mainstream-szint).** 
- ✅ **Production-ready:** Memgraph, Neo4j, LlamaIndex GraphStore, MCP, Anthropic Agent Skills, GEPA, ReFlect, Knowledge Objects, Cost-Aware HITL, SWE-bench Verified, Microsoft GraphRAG (caveats), CrewAI, LangGraph, AutoGen
- ❌ **Akadémiai stage:** Yann LeCun JEPA-család (LeJEPA, V-JEPA 2, LLM-JEPA), Sakana HRM, Gödel Agent monkey-patching, Self-Rewarding LLM Self-Play, Model Collapse $\pi^2/6$ matematikai mitigáció, Cross-Layer Attention Probing, Context Equilibria, autonóm tool-creation ab-initio
- Konzekvencia: **Phase B Tier-$50/200 csak production-ready elemekből** építhető; akadémiai elemek **Phase C/C+ idejére** (12-18 hónap).

## Olvasási sorrend

- **Kezdő**: olvasd először az [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]-t, utána `sv-01` és `sv-05` (memory + crystallization — a leggyorsabban hasznosíthatók)
- **Mély-merülő**: ennek a fájlnak a 8 tengelyét sorrendben, és minden tengelynél a NotebookLM-audio-overview-t is hallgasd meg (~10-15 perc/tengely)
- **Implementátor**: ugorj a `sv-{n}` cikkek „Implementációs lépések egy meglévő agent-vaultban" szekciójára

## Kulcs-konklúziók — 8 tengelyű szintézis (Phase A done)

### Tengelyenkénti 1-bekezdéses esszencia

**SV-1 Memory architecture.** A memory-hierarchy (working/episodic/semantic) három komplementer minta szintézise: **MemGPT virtual context paging** (OS-mintára) + **GraphRAG entity-graph + community summaries** (1M-token-skálázható globális kérdésekhez) + **Generative Agents memory-stream + reflection-loop** (epizodikus → szemantikus konszolidáció). A failure-mode klasszikus retrieval-irrelevancy a 6-paper-pool-ban; cost / privacy / hallucination-amplification web-search-bővítést igényel Phase A+. Peti-vault implementáció: embedding-réteg `11-wiki/02-Projects/05-Memory`-re + entity-extraction script + community-summary cron + reflection a `08-Sessions/` → `05-Memory/`-ra.

**SV-2 Recursive self-improvement.** 4 dimenzió (prompt evolution / skill library growth / self-reflection / code self-modification), 2024-26 paradigmaváltás: szöveges reflexió → **determinisztikus harness-rendszerek** (ReFlect) + **dinamikus skill-library** (SAGE / SkillRL / Anthropic Agent Skills) + **Compound AI optimalizáció** (GEPA). Klasszikus failure: **76-98% self-correction blind spot**, sandbox + git-pre-commit + Pareto-szelekciós merge kötelező. 7-hetes sprint-bontás safety-harness-szel, SAGE-stílusú auto-skill-distillation a `/11.11stop`-ban, GEPA-prompt-mutator cron.

**SV-3 Multi-agent orchestration.** Lead-agent + subagent minta **+90% minőség 15× token-cost** mellett (Anthropic mérés). 3 framework-filozófia: graph-based **LangGraph** / role-based **CrewAI** / conversation-based **AutoGen** — de Anthropic kategorikusan: **„simplicity over framework"**, kompozábilis primitívek (workflow → autonomous agent) az ajánlott út. Peti-vault meglévő struktúrája (11.11 + párhuzamos session-ök + 280-skill + vault mint shared state) **direkt illeszkedik** az orchestrator-worker mintára. MVP 4-lépéses sprint.

**SV-4 Tool composition.** Az agent **futásidőben fedezi fel + láncolja** a tool-okat (Toolformer self-supervised, Gorilla retriever, ToolGen virtuális token, Voyager skill-library, MCP kliens-szerver). 2024 áttörés: **Code-execution-with-MCP pattern ~98,7% token-megtakarítás**; Claude Code skill-rendszer; ToolGen 47k+ tool atomic-indexing; autonóm tool-creation (CREATOR / LATM). Peti-vault: skill-discovery automatizálás 11.11stop-hoz, Voyager-stílusú `12-skills/` + embedding-index, MCP-server-pool autonóm bővítés, `ENABLE_TOOL_SEARCH=auto` + `alwaysLoad`.

**SV-5 Crystallization automation.** Karpathy LLM-Wiki + Constitutional AI/RLAIF + Self-Rewarding LLM minták szintézise. Konkrét javaslat: **G-Eval LLM-as-judge confidence-scoring 0.85 threshold** — a meglévő 11-lépéses routing decision tree változatlan, csak az output kerül auto-prop ágra (git-revert safeguard + audit log + hot-reload threshold) vagy klasszikus manual batch preview ágra. **4-6 hetes Reflexion-stílusú felfutás** Shadow 1.0 → Konzervatív 0.95 → Aggressive 0.85, célzott ~80% auto-rate. Failure-mode-ok (hallucination amplification, reward hacking, model collapse, lost oversight) → Guardrails + autonomy slider + ruthless prune.

**SV-6 World-model / knowledge graph.** 3 absztrakciós szint konvergens mintája: **Microsoft GraphRAG** (Leiden community summaries + Global Search) + **Yann LeCun H-JEPA** (látens prediktív világmodell) + **Sakana HRM** (két-szintű forward-pass reasoning CoT helyett). 2024 áttörés: automatikus LLM-vezérelt entity-extraction (`LLMGraphTransformer`, `SchemaLLMPathExtractor`), hibrid vector+graph RAG. Peti-vault: **LlamaIndex + Memgraph POC** a `02-Projects/` + `05-Memory/Infrastructure.md`-re (Project, Server, Host, Task, Person, Document, Technology entitások; DEPENDS_ON / WORKS_ON / PART_OF / MENTIONS relációk). **Komplementer az SV-1 vector-memory-vel** — vector = felszíni similarity, graph = multi-hop reasoning + magyarázhatóság.

**SV-7 Continuous evaluation.** 3 paradigmaváltás 2024-26-ban: (a) **leaderboard-hardening contamination ellen** (SWE-bench Verified + Multimodal privát teszt-split, Modal-felhő), (b) **dinamikus + reliability-fókuszú benchmark** (tau-bench `pass^k` metrika 8 ismétlésen mérve, GAIA multi-modal humán-vs-agent), (c) **LLM-as-judge érettség** — generikus 1-5-skála → bináris Pass/Fail + critique-shadowing (Hamel Husain, AlignEval), 90%+ humán-judge alignment. Peti-vault 3-szintű pipeline: `eval_l1_parser.py` (determinisztikus stuck-detection a `08-Sessions/`-on) → `vault_trace_viewer.py` Streamlit (humán Pass/Fail baseline) → `eval_l2_llm_judge.py` (NLI-alapú hallucination-flag a Learnings-en). Aggregálás a heti **System_Health.md cron-jába** + ADR sikermetrikák feed.

**SV-8 NotebookLM cognitive layer.** Steven Johnson „tools for thought" framing + Gemini 1.5 Pro 1.5M-szó context + **citation-grounded RAG**. 3 párhuzamos 2024-es áttörés: NotebookLM Audio Overview (09-11) + Claude Projects+Artifacts (06-25) + Anthropic Contextual Retrieval (09-19). **Self-referential bizonyíték: a teljes SV-1..SV-8 research ezzel készült.** Phase B 6-sprint: per-projekt notebook-pool, 11.11stop crystallization-hook a vault-meta notebookba (SV-5+SV-8 metszete), heti commute-podcast cron. Failure-mode-ok: csak angol audio, source-limit 50/300, Cloudflare/Turnstile headless-blokk (megoldott: cloakbrowser), RPC instabilitás 502 (retry pattern kötelező). Redundáns alternatíva: Anthropic Contextual Retrieval RAG-stack $1.02/1M token.

### Cross-cutting insights — 4 fő minta amit mind a 8 tengely megerősített

1. **Komplementaritás**, nem helyettesítés. SV-1 (vector) + SV-6 (graph), SV-2 (RSI prompt-evolution) + SV-5 (crystallization-distillation), SV-3 (multi-agent) + SV-4 (tool-composition) — minden tengely a többivel együtt teljes, izoláltan részleges. A Phase B-ben **kötelező interface-design** a tengelyek között (pl. SV-1 embedding-output → SV-6 entity-extractor input; SV-5 crystallization-output → SV-2 skill-library entry).

2. **Anthropic „simplicity over framework" konzisztens** SV-3 és SV-4-ben. Az MCP + Claude Code skill-rendszer egyszerű primitívekkel ad többet, mint a CrewAI / AutoGen / LangGraph összetettsége. **Phase B tech-stack-döntésnél megfontolandó**: saját kompozábilis primitívek a meglévő 11.11 + 280-skill fölött lehet hogy értelmesebb mint új framework-réteg.

3. **Failure-mode-ok és safety-harness mindenhol kritikus.** RSI (76-98% self-correction blind spot), Crystallization (hallucination amplification, reward hacking, model collapse), Multi-agent (15× token-cost-robban), Tool composition (autonóm tool-creation sandbox-szal), Eval (criteria-drift). Phase B kötelező sandbox + git-pre-commit + Pareto-szelekciós merge **minden tengelyhez**, nem csak a #2-höz.

4. **A meglévő Peti-vault már most jól pozicionált.** 11.11 session-protokoll = SV-2 reflexió alapja; párhuzamos session-ök = SV-3 multi-agent; 280-skill pool = SV-4 tool-composition; Crystallization-protocol = SV-5 alap; Obsidian-graph = SV-6 előfutára; 06-Audits = SV-7 alap; NotebookLM-skill = SV-8 alap. **A roadmap nem új rendszer, hanem rétegezett upgrade** a meglévő architektúrára.

### Phase A+ — hiányzó témák web-search-bővítéssel (1 napos finomítás)

- **SV-1:** Long-context Claude/Gemini vs RAG benchmarkok, Letta sleep-time-compute, 2026 H1 áttörések, cost-benchmark per vector-DB
- **SV-5:** Privacy / hallucination-amplification papers
- **SV-6:** Hybrid vector+graph cost-comparison (Pinecone vs Memgraph)
- **SV-8:** Self-improving DSPy + AgentInstruct meta-eval kombináció

### Phase B fókusz-pontok (előzetes priorizálás)

| Sprint | Tengely | Mit építünk | Becsült idő |
|---|---|---|---|
| **B-1** | SV-5 Crystallization | G-Eval LLM-as-judge integrálás a 11.11stop-ba, Shadow-mode 1.0 | 1-2 hét (low-risk, csak script) |
| **B-2** | SV-1 Memory | Embedding-pipeline (Chroma vagy Memgraph + vector), Working/Episodic/Semantic szint-mapping | 2-3 hét |
| **B-3** | SV-7 Continuous eval | `eval_l1_parser.py` stuck-detection + Streamlit Pass/Fail viewer | 1-2 hét párhuzamosan B-2-vel |
| **B-4** | SV-4 Tool composition | Voyager-stílusú `12-skills/` + skill-discovery 11.11stop-hoz, MCP-server-pool | 2-3 hét |
| **B-5** | SV-8 NotebookLM | Per-projekt notebook-pool automatizálás, 11.11stop crystallization-hook a vault-meta notebookba | 1-2 hét |
| **B-6** | SV-3 Multi-agent | Orchestrator-worker minta a meglévő 11.11 session-mechanikára, kompozábilis primitívek | 2-3 hét |
| **B-7** | SV-6 World-model | LlamaIndex + Memgraph POC entity-graph a 02-Projects + 05-Memory-re | 2-3 hét |
| **B-8** | SV-2 RSI | Csak a többi UTÁN — safety-harness, GEPA-prompt-mutator, sandbox-only kód-self-modification | 2-3 hét, **utolsó** |

**Indok az SV-2 (RSI) utolsóra:** a többi tengely stabilizálódása nélkül a recursive self-improvement **felerősíti a hibákat** (reward hacking, model collapse, lost oversight). Ha SV-5 (crystallization) + SV-7 (eval) + SV-4 (tool-sandbox) már él, **felügyelt** RSI-ról beszélhetünk. Ellenkező esetben kontrolálatlan rendszer.

**Teljes Phase B becsült futás:** **8-10 hét párhuzamos sprintekkel**. Phase C = inkrementális rollout + élesedés.

### Phase B részletes ADR-pool (8/8 ✅ 2026-05-12)

| Sprint | ADR | Tengely | Effort | Depends |
|---|---|---|---|---|
| **B-1** | [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] | SV-5 | 1-2 hét | — (low-risk start) |
| **B-2** | [[07-Decisions/2026-05-12 sv-1 memory architecture arch]] | SV-1 | 2-3 hét | B-1 (KO-DB) |
| **B-3** | [[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]] | SV-7 | 1-2 hét | B-1 (G-Eval), parallel B-2 |
| **B-4** | [[07-Decisions/2026-05-12 sv-4 tool composition arch]] | SV-4 | 2-3 hét | B-2 (Memgraph) |
| **B-5** | [[07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch]] | SV-8 | 1-2 hét | B-1 (G-Eval dual) |
| **B-6** | [[07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]] | SV-3 | 2-3 hét | B-4 (MCP), B-2, B-1 |
| **B-7** | [[07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch]] | SV-6 | 1-2 hét (B-2 reuse) | B-2 (Memgraph foundation) |
| **B-8** | [[07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]] | SV-2 | 2-3 hét | **B-1..B-7 mind STABIL** |

### Sprint-sorrend (függésekből levezetve)

```
Hét 1-2:  B-1 (Crystallization) ──────┐
Hét 3-4:  B-2 (Memory) + B-3 (Eval)   │parallel
Hét 5:    B-5 (NotebookLM)            │
Hét 5-6:  B-4 (Tool composition)      │
Hét 6-7:  B-7 (World-model)           │ (B-2 reuse)
Hét 7-9:  B-6 (Multi-agent)           │
Hét 10-12: B-8 (RSI — safety-gated)   │  ← csak B-1..B-7 stabil után
```

**Phase B fő dependency-pillérek:**
- **B-1 G-Eval** = foundation a B-3, B-5, B-6, B-8 confidence-routing-jához
- **B-2 Memgraph** = foundation a B-4 Tool Search Index-hez és B-7 entity-graph-hoz
- **B-4 MCP** = foundation a B-6 multi-agent RPC-kommunikációhoz
- **Mind a 7 stabil** = foundation a B-8 RSI biztonságos engedélyezéséhez

## Audio overviews

8 audio overview generálódik a NotebookLM-en (deep-dive long format, 10-15 perc/tengely). Letöltés Phase A zárásakor:

```bash
for nb in e2e31ae8 a2425bc7 c7eba59a 90e132a1 a219107d 82e9046d d6e26ab3 a60d993b; do
  notebooklm download audio -n "$nb" --out "~/vault-audio/sv-${nb:0:2}.mp3"
done
```

(A `notebooklm artifact poll` paranccsal ellenőrizhető a generálás státusza.)

## Források

- Source pool: [[10-raw/2026-05-12 — Superintelligence research source pool]]
- 8 NotebookLM-notebook (linkek a tábla harmadik oszlopában)
- ADR: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a kiinduló minta
- [[11-wiki/Crystallization-protocol]] — a #5 tengely jelenlegi alapja
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — a research-workflow alapja
- [[02-Projects/Index]] — Phase B-ben új projekt-bekötés
