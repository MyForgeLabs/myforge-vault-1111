---
name: SV-1 Memory architecture — Phase B-2 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "memory", "rag", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-01-memory-architecture]]
sprint: B-2
priority: P1 (core infrastructure)
estimated_effort: 2-3 hét (B-3-mal parallel)
depends_on: B-1 (KO-DB foundation)
---

# ADR — Phase B-2: SV-1 Memory architecture

## Kontextus

A jelenlegi vault-memory **lapos fájl-szintű olvasás** alapú:
- Session-induláskor a `load-session-context` skill 15-20K tokent olvas be (projekt-fájl + 5 utolsó session + ADR-ek + Memory + Backlog + Daily)
- Lineáris keresés (`grep`/`Read`), nincs semantic-similarity
- A 240 fájl skálázódásával ez nem fenntartható: 500+ fájl mellett a context-load >60K token / >30 sec

**SV-1 Phase A+ insight:** A 249 source-os deep-research szerint a **3-rétegű hibrid memory-architektúra** a 2026-os ipari konszenzus: MemGPT virtual context (working) + GraphRAG entity-graph + Generative Agents reflection-loop (semantic). **Magnyalat:** vector-RAG + graph-RAG **komplementer**, nem helyettesítő.

## Döntés

**Hibrid Memgraph + LlamaIndex stack** a Memory-rétegre, hierarchikus mappa-szint-mapping-gel, hét-szintű sprintben.

### Tech-stack döntés (SV-1 + SV-6 Q1 insight alapján)

**Vector + Graph hibrid: Memgraph + LlamaIndex** — vs Chroma/Qdrant tisztán-vector vagy Neo4j tisztán-graph.

**Indok:**
- **Memgraph** in-memory + natív Neo4j-kompatibilitás + **beépített vector-search** (egyetlen DB két retrieval-paradigmára)
- **LlamaIndex `SchemaLLMPathExtractor`** automatikus entity+reláció kinyerés az Obsidian-Markdown fájlokból
- **240-fájlos vault** méreténél a GraphRAG-indexelési költség **elhanyagolható** (Phase A+ Q1 megerősítése)
- **SV-1 + SV-6 közös infrastruktúra** — két tengely egy DB-vel, 2 sprint helyett 1.5

### Hierarchikus memory-szint mapping

A meglévő vault-mappa-struktúra **direkten illeszthető** a 3 memory-szintre (lásd SV-8 Phase A+ self-referential insight):

| Memory-szint | Vault-mappa | Retrieval-stratégia |
|---|---|---|
| **Working** | `08-Sessions/<focused>.md` (aktív session) | Direct file-read, mindig context-ben |
| **Episodic** | `01-Daily/` + `08-Sessions/_archive/` + `10-raw/` | Time-windowed retrieval (last 7-14 days), vector-similarity |
| **Semantic** | `11-wiki/` + `07-Decisions/` + `05-Memory/` + `02-Projects/` | Graph-traversal (Memgraph) + entity-mention retrieval |

### Sprint-bontás (2-3 hét, B-3-mal parallel)

**Hét 1: Infrastruktúra (5 nap)**
1. Memgraph Docker-konténer telepítése `~/obsidian-vault/.memgraph/` mappába (port 7687)
2. LlamaIndex Python-csomag + `SchemaLLMPathExtractor` config az Obsidian-Markdown-ra
3. Schema-YAML draft: 9 entity-type (Project, Person, Server, Host, Task, Decision, Wiki-concept, Skill, Session) + 6 relation-type (DEPENDS_ON, WORKS_ON, PART_OF, MENTIONS, DECIDED, AUTHORED)
4. KO-DB → Memgraph bridge (a B-1 sprint SQLite-DB tartalma mint kiinduló triplet-pool)

**Hét 2: Embedding-pipeline (5 nap)**
1. `bge-m3` lokális embedding-model (free, GPU-mentes) — SV-4 Q1-ban ajánlott Top-K=3 retriever-re
2. **Egyszeri batch backfill:** összes `11-wiki/*` + `02-Projects/*` + `05-Memory/*` embedding → Memgraph vector-index
3. **File-watch hook:** új vagy módosított fájl → auto-embedding update (cron 10 percenként, `vault-autosave` mellé)
4. `vault-search` CLI parancs — semantic search egyszerű prompt-tal

**Hét 3: MemGPT-szerű virtual context + reflection-loop (5-10 nap)**
1. **Session-induláskor:** csak working+top-K (=3) episodic kerül a context-be, semantic on-demand `vault-search` hívással
2. **MemGPT-stílusú interrupt:** ha az LLM `vault-search` tool-t hív, az on-demand kerül a kontextusba
3. **Reflection-loop:** heti cron a `08-Sessions/` tartalmán — GraphRAG-stílusú community-summary generálás → új wiki-cikkek vagy `05-Memory/Feedback-*.md` automatikus draftolás (G-Eval-jóváhagyással Phase B-1 routing-jából)
4. **`11.11start` integráció:** az aggressive context-load NEM 15-20K, hanem **<5K token semantic-fetch** + on-demand expand

## Acceptance criteria

- [ ] **Memgraph + LlamaIndex** működik (`vault-search "milyen projektjei vannak Petinek"` <500 ms)
- [ ] **240 fájl embedded** és graph-extracted (10 perces backfill)
- [ ] **Auto-update hook** működik (új fájl 10 perc alatt indexelve)
- [ ] ~~**`vault-search` top-5 relevancia** >0.85~~ → **AMENDED 2026-05-17:** `top-5 cosine >0.45` (bge-m3 multilingual technical-Hungarian-tartalmra ~0.4-0.6 közt produkál even on highly relevant matches; >0.85 unrealistic). Lásd [[../06-Audits/2026-05-17 B-2 Week 3 acceptance gate readout]]
- [ ] **Session context-load idő** 30 sec → **<10 sec** — JELENLEG ~14s (bge-m3 cold-boot + in-Python cosine). **Megoldás Week 4:** `vault-search-server` daemon (model warm-on-disk, Unix-socket API) → cél ~2-3s.
- [ ] **Context-tokens session-induláskor** 15-20K → **<5K** (75% csökkenés) — JELENLEG ~5.4K kombinálva; **megoldás:** KO-DB text-mode default a `load-session-context` skill-ben (kész 2026-05-17) → ~4.6K.
- [ ] **Reflection-loop weekly** működik, >= 3 új wiki-cikk-draft/hét

## Alternatívák amiket ELUTASÍTOTTUNK

- **Tisztán Chroma vagy Qdrant (csak vector)** — multi-hop reasoning hiányzik (SV-6 Phase A+ Q1: „vector = felszíni similarity, graph = magyarázhatóság")
- **Tisztán Neo4j (csak graph)** — nincs natív vector-search; külön Pinecone/Chroma kellene → komplexebb
- **Pinecone managed hybrid** — Phase A+ Q3: drága (Tier-$200/500), self-hosted Memgraph ingyenes Tier-$50-ben
- **In-context long-context (Claude 1M token)** — Phase A+ univerzális insight: $2k-14k/év vs $56/év KO + $0/hó Memgraph
- **Mem0 vagy Letta cloud** — vendor-lock-in, fizetős, Phase A+ Q2 csak az **alsó 2 réteg** ajánlása

## Konzekvenciák

**Pozitív:**
- ~3× gyorsabb session-induláskor context-load
- 75% token-megtakarítás a Claude API hívásokon (Tier-$50-tartható)
- SV-6 (World-model) sprint **fél-sprintben befejezhető** (közös infrastruktúra)
- Foundation a SV-2 (RSI) sprintbe: a Voyager-szerű skill-library is Memgraph-ban tárolható

**Negatív:**
- Memgraph Docker-konténer mindig fut (~200 MB RAM)
- Vault-méret nő (~/obsidian-vault/.memgraph/ ~50-200 MB)
- Új tech-stack komponens (LlamaIndex Python-dep)
- Új failure-mode: Memgraph crash → vault működik, de search lassú (file-grep fallback)

**Backout-plan:** A klasszikus `load-session-context` skill megmarad mint fallback. ENV-flag `VAULT_SEARCH_MODE=grep` visszaesik a régi módra.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| LlamaIndex `SchemaLLMPathExtractor` hibás entity-kinyerés | Rossz graph | Schema-YAML konzervatív, manual-review az első 20 entity-extraction-en |
| bge-m3 embedding magyar nyelvre szuboptimális | Rossz semantic-search HU-ra | Phase B-2 közbenső benchmark: bge-m3 vs multilingual-e5 vs LaBSE 50 magyar query-n |
| Memgraph Docker startup-fail (reboot után) | vault-search nem megy | systemd-szerű launchd-job a `vault-autosave` mintára |
| Embedding-pipeline lassú (240 fájl batch >30 perc) | Onboarding-friction | Incremental backfill (parallelizálás, async batch) |

## Open questions

1. **Embedding-frissítés gyakorisága:** 10 perc cron (a `vault-autosave` mellé) vagy real-time file-watch? Compromise lehet: file-watch trigger + 30 sec debounce.
2. **Reflection-loop output-formátum:** új `11-wiki/<topic>.md` (auto-draft G-Eval-jóváhagyással) vagy `05-Memory/Auto-reflections/<date>.md` (separate folder, manuális promóció a wiki-be)?
3. **Cross-vault embedding-pool:** ha Rob vaultja is integrálódik, közös embedding-DB vagy per-vault separated?

## Kapcsolódó

- [[11-wiki/sv-01-memory-architecture]] — research-cikk
- [[11-wiki/sv-06-world-model-knowledge-graph]] — közös infrastruktúra (Memgraph)
- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — B-1 sprint (KO-DB foundation)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a meglévő vault-architektúra háttere
