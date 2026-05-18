---
name: Superintelligent vault evolution roadmap
type: decision
tags: ["#type/decision", "vault-architecture", "agi", "research", "long-term"]
created: 2026-05-12
updated: 2026-05-12
status: research-phase
---

# ADR — Superintelligent vault evolution roadmap

## Kontextus

A jelenlegi `~/obsidian-vault` egy első-generációs agent-vault (Karpathy LLM-Wiki minta + Johnny-Decimal + 11.11 session-protokoll + 280-skill pool). Működik, de **lineáris**: a context-loading fájl-szintű, a tudás-propagáció félautomata, az agentek egy-by-one futnak, a tools statikusak, a memory-réteg laposan strukturált.

A „szuperintelligencia" itt **nem AGI**, hanem a **te-meg-Claude páros együttes képessége**, amit a 2025-26-os szakirodalom „augmented intelligence" / „cognitive architecture" néven hivatkozik. Az ambíció: a vault legyen olyan agent-rendszer, ami **maga is fejleszti magát**, **strukturáltan tanul minden interakcióból**, és **multi-agent orchestration**-nel olyan komplex feladatokat is megold, amik egyetlen sessionben nem férnek el.

## Döntés — 8-tengelyes evolúciós roadmap

Ez egy **multi-fázisú döntés**: a 8 tengely közül **mind a 8 megy be**, de fázisokban — minden fázis önállóan futtatható és értékes.

### A 8 tengely

| # | Tengely | Hipotézis | Fő téma |
|---|---|---|---|
| **1** | **Memory architecture** | Vektor-embedding + hierarchikus memory (working/episodic/semantic) sokszorosan gyorsabb context-loading mint a jelenlegi fájl-szintű olvasás | MemGPT, Letta, Mem0, GraphRAG, long-context vs RAG benchmarks |
| **2** | **Recursive self-improvement** | Az agent maga írja át a saját AGENTS.md-t, skill-eket, prompt-okat — minden sessionből tanul, nem csak Crystallization-en | Promptbreeder (DeepMind), Voyager (NVIDIA), AlphaEvolve, STaR, Reflexion |
| **3** | **Multi-agent orchestration** | Több párhuzamos agent (planner / executor / critic / summarizer / red-team) szignifikánsan jobb minőséget ad mint single-agent | CrewAI, AutoGen, ChatDev, Generative Agents (Stanford Smallville), Devin/Manus arch |
| **4** | **Tool composition** | Az agent maga fedez fel és komponál új MCP-tool-okat, nem várja hogy ember telepítse — exponenciális tool-növekedés | Toolformer, ToolGen, Anthropic MCP, Voyager skill-library pattern, AGENT-E |
| **5** | **Crystallization automation** | A 11.11stop user-confirmation-szakasz automatizálható confidence-score alapján; high-confidence Learnings auto-propagálódnak | Karpathy LLM-Wiki eredeti elv, Anthropic continuous-eval, Constitutional AI, RLHF-replacement methods |
| **6** | **World-model / knowledge graph** | Explicit semantic graph (entitások + relációk + ok-okozat) + hierarchikus reasoning engine fölötte > Obsidian fájl-link-graph | Microsoft GraphRAG, Neo4j+LLM, KG-RAG, mental-models |
| **7** | **Continuous evaluation** | Minden session/projekt **automatikus metrikákat** kap (mit végeztünk, mi a tanulság, hol akadt el az agent) → benchmark-trend láthatóvá teszi a fejlődést | Anthropic continuous-eval Foundry, AgentBench, OpenHands eval, SWE-bench |
| **8** | **NotebookLM mint cognitive layer** | A NotebookLM nem csak research-eszköz, hanem a vault-on belüli **convergent reasoning + source-grounded synthesis** réteg — automatikus audio-overview, multi-source-ütköztetés, hipotézis-tesztelés | NotebookLM API/CLI, source-grounded LLM, RAG-systems comparison |

## Fázisok

### Phase A — Deep research (2026-05-12 .. 05-16, ~3-4 nap)

**Cél:** 8 tengelyhez 8 részletes `11-wiki/` cikk, tudományos hivatkozásokkal, konkrét recept + 3 alternatíva trade-off-fal + Peti-vault-specifikus „mit csináljak először" akció-pont.

**Output:**
- `11-wiki/superintelligent-vault-research.md` (master index)
- `11-wiki/sv-01-memory-architecture.md`
- `11-wiki/sv-02-recursive-self-improvement.md`
- `11-wiki/sv-03-multi-agent-orchestration.md`
- `11-wiki/sv-04-tool-composition.md`
- `11-wiki/sv-05-crystallization-automation.md`
- `11-wiki/sv-06-world-model-knowledge-graph.md`
- `11-wiki/sv-07-continuous-evaluation.md`
- `11-wiki/sv-08-notebooklm-cognitive-layer.md`
- `10-raw/2026-05-12 — Superintelligence research source pool.md` (50+ forrás)

**Eszközök:**
- NotebookLM (8 notebook, 1/tengely, ~30-50 forrás összesen)
- Tudományos sources: arXiv papers 2024-2026
- YouTube: Lex Fridman, Karpathy lectures, Yannic Kilcher, AI Explained, Two Minute Papers
- Blogok: Simon Willison, Hamel Husain, Eugene Yan, Latent Space, Anthropic engineering, OpenAI blog
- Conferences: NeurIPS/ICLR/ICML/NeurIPS 2025-2026

### Phase B — Implementation roadmap (2026-05-17 .. 05-19, ~2-3 nap)

**Cél:** A research alapján **konkrét epic-sprint-task tree** összeállítása. Minden tengelyhez:
- Architektúra-diagram
- Tech-stack döntés (mit használunk: lokális FAISS vs Pinecone, MCP server config, agent-framework: CrewAI/AutoGen/saját)
- Sprint-bontás (~1-2 hetes ütemekben)
- Acceptance criteria (mit jelent „kész")
- Risk-register (mi mehet rosszul, hogyan mérsékelhető)

**Output:**
- `02-Projects/superintelligent-vault.md` (új projekt, 8 epic alatta)
- `04-Tasks/Backlog.md` szekció `#project/sv` taggel
- 8 db `07-Decisions/2026-05-{17..19} sv-{1..8} <tengely> arch.md` ADR

### Phase C — Incremental rollout (2026-05-20 .. ~07-15, ~8-9 hét)

**Cél:** A Phase B sprintjeit végrehajtjuk, **inkrementálisan**, hogy a vault közben **használható maradjon**.

**Sorrend (függés-irányítva, low-risk → high-risk):**

```
Week 1-2:  #5 Crystallization automation  (csak script, nincs külső függés)
Week 3-4:  #1 Memory (vektor-store)         + #7 Eval (metric-pipeline)
Week 5-6:  #4 Tool composition (MCP)        + #8 NotebookLM cognitive
Week 7-8:  #3 Multi-agent orchestration     (követi #4-et)
Week 9:    #6 World-model graph             (követi #1-et)
Week 10+:  #2 Recursive self-improvement    (a többi szabályozott pályán fut → biztonságos engedélyezni)
```

**Acceptance gate** minden fázis után: ha az aktuális vault **regresszió-tesztet** elbukik (régi session-flow tört), rollback + root-cause.

## Alternatívák amiket ELUTASÍTOTTUNK

- **Egyetlen csomag minden fázist egyszerre** → túl nagy attack-surface, regresszió-rizikó, nincs measurable progress, demoralizáló
- **Csak egy tengely** (#1 vagy #2) → szuboptimális; a tengelyek **egymást erősítik**, izoláltan kevesebbet adnak
- **AGI-vibes „önműködő agent"** → nem realisztikus mai modellekkel, plus security/cost-risk; az „augmented intelligence" framing kontrollálható és measurable

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| **Phase A blokkolás** ha NotebookLM-keepalive lejár vagy CloudFlare blokk | Research-leállás | [[11-wiki/notebooklm-headless-login-fifo]] heti keepalive cron; fallback [[11-wiki/cloakbrowser-fingerprint-bypass]] |
| **Tudományos overload** — 100+ paper, nincs idő szintetizálni | Stagnálás | NotebookLM/tengely max 7 source; 7 strukturált kérdés/tengely (17×7 minta) |
| **Implementation drift** — a research absztrakt, a vault konkrét | Phase B kudarc | Phase B output mindig kapcsolódjon konkrét vault-fájlhoz / scripthez |
| **Recursive self-improvement security** — agent rosszul írja át az AGENTS.md-t | Vault-corruption | #2 csak a végén, sandbox-tag-ek a változásokra (git-commit-pre-hook), revert-able |
| **Cost** — NotebookLM ingyenes, de vector-store / multi-agent prod-API hív → token-bill | Pénz | Phase C-ben per-tengely cost-budget; lokális modellek (llama.cpp, ollama) ahol lehet |
| **Vault-explosion** — 240 → 500+ fájl, navigációs káosz | UX | Phase B-ben **Tag/Index audit** kötelező; minden új fájlnak Frontmatter + Index-bekötés |

## Sikermetrikák (Phase C végén mérendő)

> **Phase A+ update (2026-05-12):** A Phase A+ deep-research konkrét cost-számokat hozott amik a Target-oszlop quantifikálását élesítik. Forrás: [[11-wiki/superintelligent-vault-research#Phase A+ új cross-cutting insights]] + SV-4/5/8 deep-research output-ok.

| Metrika | Baseline (most) | Target (10 hét múlva) | Phase A+ konkrét szám |
|---|---|---|---|
| **Context-loading idő** (új session indulás) | ~15-20K token, ~30 sec olvasás | ~5K token releváns kontextus, <10 sec semantic-fetch | **30s → <10s** (3× gyorsulás Memgraph in-memory + KO-DB indexed lookup-pal, SV-1+SV-6) |
| **Crystallization auto-rate** | 0% (manuális user-confirm) | 60-80% (high-confidence auto-propagál) | **0% → 80%** Aggressive mode (B-1 Week 5-6, threshold 0.85, G-Eval CoT scoring) |
| **Crystallization cost** | $0 (manuális, csak user-time) | KO-DB stack | **$2k-14k/év in-context-memory → $56/év KO-DB** (97-99% saving, SV-5+SV-8 cross-cutting insight) |
| **Tool-pool token-overhead** | Static 280 skill, prompt-tool-list minden hívásra | MCP code-exec lazy-load | **MCP code-exec 98.7% token-saving** vs prompt-tool-list (SV-4 deep-research) |
| **Multi-agent task completion** | 0 (nincs multi-agent) | 70%+ a SWE-bench-szerű benchmark-on | +90% minőség / **15× token-cost** (Anthropic Claude Code release-paper mérés, SV-3) |
| **Tool-pool növekedés** | statikus 280 | önfedező MCP-tool + 50-100 új skill/hó | Voyager skill-library minta + Anthropic "simplicity over framework" (SV-4) |
| **Recall** (régi tudás visszahívása új kontextusban) | manuális grep | top-5 relevancia >0.9 semantic search-en | LlamaIndex hybrid retriever (vector + graph) — false-positive <5% gate (B-7 acceptance) |
| **„Knowledge crystallization velocity"** | ~5-10 wiki-cikk / hó | 20-30 / hó (auto-distillation a session-history-ból) | KO-DB ingest backfill batch: 240 fájl + 280 skill → 30-60 perc (B-7 sprint Week 1) |
| **Tier-cost positioning** | $0 baseline (csak manuális) | Tier-$50/hó target (NotebookLM ingyenes + Haiku-API) | **Peti-vault MÁR Tier-$50 közeli** — csak MCP-bridge + 11.11stop hook hiányzik (SV-8 self-referential insight) |

## Konzekvenciák

**Pozitív:**
- A vault valódi „compounding intelligence" — minden használat növeli az értékét, nem csak hozzáad
- Multi-agent munkagép → komplexebb feladatok (full-stack feature, end-to-end PR) egyetlen session-rángatás nélkül
- A te idődet csökken: amit ma 1 órát adsz át kontextusban, az 10 perc lesz

**Negatív:**
- 10 hét tényleges munka, közben kevesebb projekt-fejlesztés
- Új tech-stack komponensek (vector-store, MCP-servers, agent-framework) → új failure-modes
- A vault többé nem „naiv Markdown-mappa" — Obsidian-only-olvasó nem lesz teljes értékű (a graph + semantic-fetch CLI-szintű marad)

**Backout-plan:** Minden fázis-end-pointon git-tag (`sv-phase-a-done`, `sv-phase-b-done`, stb.) — visszaverhetők. A jelenlegi vault-funkcionalitás (11.11 + AGENTS.md + Obsidian) **soha nem törhet meg** a roadmap során.

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a kiinduló minta
- [[11-wiki/Crystallization-protocol]] — a #5 tengely jelenlegi alapja
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — a Phase A 17×7 minta forrása
- [[02-Projects/Index]] — Phase B-ben új sor: `superintelligent-vault`
- [[08-Sessions/2026-05-12-obsidian-vaul]] — a research-session ami ezt indította

## Open questions

1. **Lokális vs cloud agent-runtime** — futtassuk-e az agenteket a saját szerveren (privacy, költség-kontroll, latency)? Phase B-ben kell eldönteni.
2. **Mely vector-store** — Chroma, Qdrant, Weaviate, Pinecone, pgvector? Phase A #1 dönti el.
3. **Mely agent-framework** — CrewAI vs AutoGen vs LangGraph vs saját? Phase A #3 dönti el.
4. **NotebookLM API stabilitása** — még ingyenes, de Google API-policyt változtathat; alternatíva mint backup?
