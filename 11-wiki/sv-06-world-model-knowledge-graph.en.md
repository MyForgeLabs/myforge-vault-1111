---
name: SV-6 World model / knowledge graph
type: wiki
lang: en
translated_from: sv-06-world-model-knowledge-graph.md
tags: ["#type/wiki", "agi", "knowledge-graph", "graphrag", "world-model", "sv-research"]
created: 2026-05-12
updated: 2026-05-19
status: done
parent: [[11-wiki/superintelligent-vault-research]]
---

# SV-6 — World model / knowledge graph

Sixth article of the 8-axis SV research. **Question:** how to organize an LLM agent's knowledge into an explicit semantic graph (entities + relations + causation), and what hierarchical reasoning engine could sit on top to deliver significantly better results than classic vector RAG or a flat file-link graph.

## 1. The axis core

The "world model" / "knowledge graph" approach builds a **structured, relational, hierarchical internal representation** that goes beyond pattern recognition — enabling **deeper logical understanding, predictive inference, and complex multi-timescale planning**.

Three abstraction levels of the same idea:

- **Yann LeCun H-JEPA** (Hierarchical Joint Embedding Predictive Architecture) — latent-variable energy-based model predicting high-level abstract representations. Goal: autonomous machine intelligence ("Level 5") with reliable world models.
- **HRM** (Hierarchical Reasoning Model, Sakana 2025) — biologically-inspired 2-level recurrent architecture: slow abstract planner + fast detail computer in a **single forward pass**, no explicit CoT supervision.
- **GraphRAG** (Microsoft 2024) — LLM-extracted entity graph + hierarchical community summaries build a "world model" for the corpus; query-time global synthesis where chunk-level vector RAG fails.

> **Contrast with classic vector RAG:** vector RAG searches isolated unstructured chunks via **surface semantic similarity** — fails conceptually at "connecting the dots" (multi-hop reasoning), aggregation, and global corpus-wide questions. Knowledge-graph reasoning replaces the black-box similarity search with a **structured, explainable, reasoning-capable architecture**.

## 2. Canonical patterns

### Microsoft GraphRAG (hierarchical community summaries + global search)
LLM extracts entities and relations into a knowledge graph; **Leiden algorithm** clusters into hierarchical communities; each community gets a pre-generated summary. At query time, global search synthesizes hierarchical summaries. Enables **whole-corpus sensemaking and "connecting dots"** — impossible for vector RAG.

### LeCun H-JEPA (predictive latent world models)
Energy-based latent-variable model predicting **high-level abstract representations** (not pixels/tokens). Enables reliable internal world models, logical reasoning, complex multi-timescale planning.

### HRM (Sakana 2025, arXiv 2506.21734)
2-level recurrent network: slow abstract planning + fast detail computation, single forward pass, **no CoT supervision**. **27M parameters and 1000 training samples** suffice for AGI-class tasks (Sudoku, ARC, mazes).

### LLM-driven knowledge graph extraction (Neo4j + LangChain)
LangChain `LLMGraphTransformer`, LlamaIndex `SchemaLLMPathExtractor` — auto-identify entities and exact relations from text. Eliminates the hardest bottleneck of graph building: manual ontology design.

### Hybrid Vector + Graph RAG
Vector search combined with graph traversal (Cypher queries on the neighborhood). Combines **semantic flexibility of vectors with precise logical aggregation and traceability of graphs**. Answers complex relational questions (exact counts, indirect dependencies) where chunk-similarity inevitably fails.

## 3. Tech stack 2026

| Tech | Use case | Setup | Scale | LLM integration |
|---|---|---|---|---|
| **Neo4j** | Industrial standard, hybrid (vector + graph) RAG production-ready | Med/High — dedicated DB, Cypher needed | Excellent | Strong — deep LangChain/LlamaIndex, own MCP server |
| **Memgraph** | Extremely fast in-memory graph, realtime high-throughput RAG | Medium — Bolt-compatible, fast Docker | Excellent — perf-optimized | Strong — built-in LangChain toolkit, LlamaIndex, Mem0, LightRAG |
| **Microsoft GraphRAG** | Hierarchical + holistic query-focused summarization (Global Search) | High — CLI pipeline, manual prompt tuning, OpenAI-API-bound | Limited/expensive | Built-in, closed orchestration |
| **LangChain Knowledge Graph** | Fast app dev, auto graph-extraction, LLM-generated Cypher | Low/Med — Python API, backend DB needed | DB-bound | Maximum |
| **LlamaIndex Property Graphs** | Data-first framework, flexible ingestion | Low | DB-bound | Very good — Memgraph vector-search backed |

### Recommendation for a ~240-file markdown vault

**Holistic "big picture" / sensemaking → Microsoft GraphRAG** — indexing is expensive but at this size affordable. Best for "what are the top 5 themes in my notes?".

**Interactive dynamic Q&A + fast build → LlamaIndex + Memgraph (or Neo4j Desktop)** — Memgraph locally in Docker, LlamaIndex `SchemaLLMPathExtractor` over Markdown, hybrid retriever vector + graph. Much cheaper than GraphRAG.

## 4. Breakthroughs 2024-2026

1. **Microsoft GraphRAG (2024)** — global understanding breakthrough. LLM-extracted entity graph + Leiden community summaries + Global Search. Enables whole-corpus query-focused summarization, impossible for vector RAG.
2. **Hierarchical Reasoning Model (HRM, 2025-06)** — single forward pass, no CoT supervision, 27M params + 1000 samples for AGI-class tasks.
3. **Property graph integrations (LlamaIndex + LangChain)** — auto-ontology design, hybrid vector+graph search built-in.
4. **JEPA family expansion (H-JEPA, V-JEPA, LLM-JEPA, LeJEPA)** — latent abstract prediction enables autonomous action planning.
5. **Verification and Agentic RAG** — independent **evaluator agents** score context+answer; **Agentic GraphRAG** (LangGraph) — agent autonomously chooses vector search vs Cypher.

## 5. Failure modes

1. **Extreme cold-start cost** — Building graph from scratch requires LLM to process every sentence. Microsoft explicitly warns: GraphRAG indexing is **extremely expensive** — "start small". Unsustainable on huge real-time-updating data.
2. **High latency** — GraphRAG-query (especially Global Search or LLM-generated Cypher) slower than vector RAG. Tests: vector ~8 sec, GraphRAG ~71 sec + many tokens.
3. **Entity-extraction errors and "baked-in" hallucinations** — Graph quality = LLM extraction quality. Misunderstood context or hallucinated relations enter the graph as facts — **"structural hallucination"** is much harder to detect than plain text hallucination.
4. **Schema drift and rigidity** — Auto-ontology drifts long-term. Without explicit schema control it gradually decays.

### When NOT to use GraphRAG
Simple fact lookup ("which file contains X?"). Vector DB is faster, cheaper, more effective.

### What graphs do NOT solve
- **Don't replace semantic search** — graphs handle precise structured logic, weak at fuzzy unstructured text similarity. Need **hybrid (vector + graph)**.
- **Don't guarantee zero hallucination** — graph gives exact facts but final LLM answer can still hallucinate if context doesn't cover the question. Graph only helps with **traceability**.

## 6. Implementation in a personal vault

A ~240-file markdown vault (Johnny-Decimal prefix + Karpathy LLM-Wiki pattern) is **ideal substrate** for hybrid (vector + graph) RAG — the structure is already semi-entity:

- `02-Projects/<project>.md` = **Project entity**
- `05-Memory/Infrastructure.md` = **Infrastructure/Server entity graph**
- `03-Hosts/<host>.md` = **Host entity**
- `07-Decisions/<date>.md` = **Decision entity** (ADR-like)
- `[[wikilink]]`s = **explicit `MENTIONS` relations**

### Implementation steps

**1. Load existing structure (explicit graph)** — Fixed metadata (folder prefix → entity type, frontmatter `name` + `type`) and wikilinks import as default nodes + edges. **Code-only, deterministic**, no LLM.

**2. LLM-driven entity + relation extraction (implicit graph)** — `SchemaLLMPathExtractor` (LlamaIndex) or `LLMGraphTransformer` (LangChain) with predefined schema:
- **Entity types:** Project, Infrastructure, Server, Host, Task, Person, Document, Technology, Concept
- **Relations:** MENTIONS, LINKS_TO (from wikilinks), DEPENDS_ON, WORKS_ON, PART_OF, RELATES_TO

**3. Vector indexes inside the graph (complements SV-1)** — Embeddings from node properties stored as graph-DB vector index. **Hybrid retriever** — vector + Cypher simultaneously.

**4. Optional community hierarchy** — For holistic queries ("main themes I worked on this year?"), Leiden clustering + community summary (Microsoft GraphRAG pattern).

### Complement to SV-1 memory layer

| What vector memory (SV-1) does | What graph layer (SV-6) adds |
|---|---|
| Surface semantic search ("how did I configure nginx cache last time?") | Multi-hop reasoning ("which projects break if the DB-server in Infrastructure.md goes down?") |
| Fast cold-start (embedding batch only) | Structured aggregation, exact counts |
| Cheaper per-query | Explainable, source-traceable answers |
| Stale-friendly | Explicit dependencies / causation |

**Ideal architecture:** SV-1 vector + SV-6 graph + **LangGraph agent** autonomously routing between them (Agentic GraphRAG).

## 7. Open research

1. **Dynamic graph update (session-based entities)** — How to integrate session-flow (note → graph update). Mem0 and Cognee building this; long-term schema-drift consistency is open.
2. **Multimodal knowledge graph (image, code, audio)** — Janus (arXiv 2410.13848); "Bridging Visualization and Optimization" (2501.11968).
3. **Federated graph + permissions (cross-vault, multi-user)** — Memgraph Zero, Federated GQL.
4. **Graph + reasoning (CoT + Cypher)** — `GraphCypherQAChain` NL→Cypher hallucinates. Future: **Agentic GraphRAG** + maybe **HRM + graph**.
5. **JEPA + markdown vault integration** — Open: how to bridge **continuous latent JEPA memory space** with **discrete symbolic graph nodes**?

## Phase A+ summary

**3-layer recommendation, bottom-up:**
1. **Hybrid vector + knowledge-graph base** (infrastructure) — Memgraph + LlamaIndex. ~240 files = negligible GraphRAG indexing cost. Multi-hop infra reasoning at this level.
2. **Epistemic world model + global workspace** (orchestration) — Mem0 or Cognee natively supports Memgraph; agent does meta-cognitive self-check via global workspace.
3. **Hierarchical reasoning + predictive planning** (intelligence) — HRM + JEPA principles. **LLM-JEPA** fine-tunes in embedding space. "What if" cascading impact simulation.

**Production-ready:** Neo4j, Memgraph, LangChain Graph, LlamaIndex GraphStore, Pinecone hybrid. Microsoft GraphRAG production-with-caveats.
**Academic:** JEPA family (LeJEPA, V-JEPA 2, LLM-JEPA), HRM, World Models in general.

### Cost tiers
- **$50/mo (lean hybrid):** Memgraph Docker local, LlamaIndex `SchemaLLMPathExtractor`, hybrid RAG. **CUT:** Microsoft GraphRAG (50k tokens/query, $71-second per query), JEPA family, World Models.
- **$200/mo (Agentic OS + filtered GraphRAG):** Neo4j AuraDB, partial GraphRAG (Local Search + DRIFT Search, not Global), Mem0/Knowlee autonomous concept extraction.
- **$500/mo (production world-model max):** Full 4-layer cognitive architecture (Knowledge/Memory/Wisdom/Intelligence), Pinecone Hybrid, daily GraphRAG cron, LLM-JEPA fine-tune.

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[11-wiki/sv-01-memory-architecture]] — companion (vector memory layer)
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — background of the vault's semi-entity structure
- [[11-wiki/Crystallization-protocol]] — graph-update hook for session close
- [[vault-knowledge-graph-overview]] — live state of the vault graph
