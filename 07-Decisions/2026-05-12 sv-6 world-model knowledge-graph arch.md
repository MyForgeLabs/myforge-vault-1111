---
name: SV-6 World-model / Knowledge graph — Phase B-7 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "knowledge-graph", "graphrag", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-06-world-model-knowledge-graph]]
sprint: B-7
priority: P2 (extension of B-2)
estimated_effort: 2-3 hét (de B-2 infrastruktúrával fél-sprintben befejezhető)
depends_on: B-2 (Memgraph foundation)
---

# ADR — Phase B-7: SV-6 World-model / Knowledge graph

## Kontextus

A B-2 sprint a Memgraph + LlamaIndex hibrid stack-et építi a memory-réteghez (vector + graph egy DB-ben). **DE** a graph-réteg eddig csak a **retrieval-augmentation** célt szolgálja — entity-extract + community-summary, mint kiegészítő.

**SV-6 Phase A+ insight (73 source):** A graph nem csak retrieval-réteg, hanem **explicit szemantikus világmodell** — Project + Server + Host + Task + Person + Document + Technology entitásokkal, és `DEPENDS_ON` / `WORKS_ON` / `PART_OF` / `MENTIONS` relációkkal. Ez **képessé teszi a multi-hop reasoning-ot** és **magyarázható következtetést** (vector = felszíni similarity, graph = explicit ok-okozat).

**A 3-rétegű világmodell-konvergens minta:**
- **GraphRAG** (Microsoft 2024) — Leiden community summaries, Global Search
- **H-JEPA** (Yann LeCun) — látens prediktív világmodell — *kísérleti fázis (Phase C+)*
- **HRM** (Sakana 2025) — két-szintű forward-pass reasoning — *kísérleti fázis (Phase C+)*

A Phase B-7 csak a **GraphRAG production-ready** részre fókuszál. JEPA + HRM Phase C+ idejére.

## Döntés

**Schema-driven entity-graph a B-2 Memgraph fölött**, 1-2 hetes inkrementális sprint (NEM 2-3 hét, mert a B-2 infrastruktúra már megvan).

### Schema-YAML (formális entity + reláció definíció)

A vault-konvenciók alapján 9 entitás-típus + 6 reláció-típus:

```yaml
# ~/obsidian-vault/00-Meta/graph-schema.yml

entities:
  Project:
    source: "02-Projects/*.md"
    fields: [name, status, repo_prod, repo_dev, last_touched]
    id_field: name
  Person:
    source: "manual + AGENTS.md + 05-Memory/User.md"
    fields: [name, email, role]
    id_field: name
  Server:
    source: "03-Hosts/*.md + 05-Memory/Infrastructure.md"
    fields: [hostname, ip, role, provider]
    id_field: hostname
  Host:
    source: "03-Hosts/*.md"
    fields: [name, port, service]
    id_field: name
  Task:
    source: "04-Tasks/Backlog.md"
    fields: [content, priority, status, due_date, tags]
    id_field: hash(content)
  Decision:
    source: "07-Decisions/*.md"
    fields: [name, status, sprint, date]
    id_field: filename
  Wiki_concept:
    source: "11-wiki/*.md"
    fields: [name, type, parent, related]
    id_field: filename
  Skill:
    source: "~/.agents/skills/*/SKILL.md"
    fields: [name, description, trigger_keywords]
    id_field: name
  Session:
    source: "08-Sessions/*.md"
    fields: [name, project, started, ended, status]
    id_field: filename

relations:
  DEPENDS_ON:
    from: [Project, Decision, Task]
    to: [Project, Decision, Server]
    example: "kgc-berles DEPENDS_ON kgc-postgres"
  WORKS_ON:
    from: [Person]
    to: [Project, Task]
    example: "Peti WORKS_ON kgc-berles"
  PART_OF:
    from: [Wiki_concept, Skill, Session]
    to: [Wiki_concept, Project, Decision]
    example: "sv-01-memory-architecture PART_OF superintelligent-vault-research"
  MENTIONS:
    from: [Session, Wiki_concept, Decision]
    to: [Project, Person, Server, Wiki_concept]
    example: "2026-05-12-obsidian-vaul MENTIONS Memgraph"
  DECIDED:
    from: [Decision]
    to: [Wiki_concept, Skill, Project]
    example: "ADR-sv-5 DECIDED G-Eval-threshold"
  AUTHORED:
    from: [Person, Session]
    to: [Decision, Wiki_concept]
    example: "Peti AUTHORED ADR-sv-5"
```

### Sprint-bontás (1-2 hét, B-2 infrastruktúra reuse)

**Hét 1: Schema + Extractor (5 nap)**
1. Schema-YAML draft + `00-Meta/graph-schema.yml` commit
2. `vault-graph-extract` script (LlamaIndex `SchemaLLMPathExtractor` config-jelölt) — Haiku-API entity+reláció kinyerés
3. **Egyszeri batch backfill:** 240 fájl + 280 skill → Memgraph entity-graph (kb. 30-60 perc)
4. Manual review az első 100 extracted entity-n (false-positive rate <5%)

**Hét 2: Query + UI (5 nap)**
1. **`vault-graph-query` CLI** — Cypher-prompt natural language-ből (LlamaIndex `GraphCypherQAChain` minta)
   - Példák: `"mely projektek függenek a kgc-postgres-től?"` → multi-hop graph-traversal
   - `"mit dolgoztam Robbal az elmúlt 30 napban?"` → temporal + person-filter
2. **Community-summary cron** (havi 1×) — Leiden algoritmussal entitás-klaszterek + LLM-summary-generálás minden klaszterre
3. **Obsidian-graph-view enhancement:** a Memgraph entity-graph **exportja Obsidian graph-view-be** (CSV / JSON-Canvas formátumban) — lokális Memgraph-ot Obsidian nem tud lekérdezni, de a manual snapshot a `02-Projects/Graph-snapshot.canvas` fájlba mehet

### Hybrid retrieval (vector + graph) — B-2 reuse

A B-2 sprint `vault-search`-jét **kibővíti** a graph-traversal-lal:

```python
def vault_search(query: str) -> List[Source]:
    # 1. Vector-search (B-2): top-3 semantic-similar chunk
    vector_results = memgraph_vector_search(query, top_k=3)

    # 2. Entity-extract a query-ből (B-7)
    query_entities = extract_entities(query)

    # 3. Graph-traversal: 2-hop expansion az entitásokból
    graph_results = memgraph_cypher(query_entities, max_hops=2)

    # 4. Hybrid rerank: vector-score + graph-distance weighted
    return hybrid_rerank(vector_results, graph_results)
```

## Acceptance criteria

- [ ] **Schema-YAML** commit + dokumentáció (9 entity + 6 reláció)
- [ ] **`vault-graph-extract`** működik, 240 fájl + 280 skill batch-extracted (>1000 entitás + >2000 reláció)
- [ ] **Manual review** az első 100 entity-n — false-positive <5%
- [ ] **`vault-graph-query`** működik, top-3 multi-hop reasoning query helyes válasszal
- [ ] **Community-summary** havi cron — generál >5 klaszter-summary az érett tartalmakra
- [ ] **Hybrid vector+graph rerank** mérve — single-axis vs hybrid összehasonlításban >20% relevance-javulás 30 query-n

## Alternatívák amiket ELUTASÍTOTTUNK

- **Neo4j AuraDB managed** — fizetős, Tier-$50/200-on nem fér bele; Memgraph self-hosted ingyenes
- **Pinecone hybrid** — vector + graph kombinált managed-service, de $200+/hó (Phase A+ Q3)
- **JEPA / HRM** — akadémiai fázis, no production API (Phase A+ Q2)
- **Manual entity-curation** — nem skálázható 240+ fájlra; LLM-extractor + manual review hibrid
- **Tisztán Obsidian-graph (file-link)** — nem fed le multi-hop és nem ad community-summary-t

## Konzekvenciák

**Pozitív:**
- **Multi-hop reasoning** explicit + magyarázható (vs vector black-box similarity)
- B-3 sprint (Eval) **direkt gazdagítja** — minden Learning entitás-szintű provenance-szel
- B-5 (NotebookLM) **konvergens-dual-bíró** — NotebookLM + Memgraph + G-Eval triple-validation
- **B-2 infrastruktúra reuse** → fél-sprint helyett 1.5 hét

**Negatív:**
- Schema-evolution overhead (új entity-típus → migration-script)
- LLM-extractor false-positive (~5%) → minden batch-extraction után audit
- Community-summary havi cron $2-5 token-cost (Haiku-API, Tier-$50 belül)

**Backout-plan:** A `vault-graph-query` opcionális — ENV-flag `GRAPH_QUERY=0` → csak B-2 vector-search. A schema-YAML és Memgraph entity-graph megmarad mint adat-pool, csak nem queryzzük.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| `SchemaLLMPathExtractor` schema-drift (új mezőre kinyerés) | Graph-zaj | Strict schema-YAML enforcement; nem-strict-fields → manual review |
| Cypher-query natural-language-translation hibás | Wrong reasoning | LlamaIndex `GraphCypherQAChain` validation: Cypher-szintax-check + dry-run |
| Community-summary hallucination | Wrong cluster-meaning | G-Eval (B-1) ellenőrzi a community-summary-output-ot |
| Cross-vault entity-conflict (Rob `Peti` vs vault `Peti`) | Entity-merge-ambiguity | Per-vault entity-namespace (URN-style: `peti-vault:Project:kgc-berles`) |

## Open questions

1. **Embedding-rerank threshold:** vector vs graph milyen súllyal? Phase B-7 második hetén 30-query benchmark.
2. **Time-decay reláció-staleness:** ha egy `MENTIONS` reláció 6+ hónapja nem újraerősített, low-confidence flag? Phase B-7 lezárása után döntés.
3. **Graph-explore UI:** Obsidian-graph-view extension vs Memgraph-Lab desktop-app vs web-UI? Phase C+ idejére.

## Kapcsolódó

- [[11-wiki/sv-06-world-model-knowledge-graph]] — research-cikk
- [[07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 sprint (Memgraph foundation reuse)
- [[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]] — B-3 sprint (entity-szintű provenance)
- [[07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch]] — B-5 sprint (dual-bíró konvergencia)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap
