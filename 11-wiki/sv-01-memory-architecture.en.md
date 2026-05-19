---
name: SV-1 Memory architecture
type: wiki
lang: en
translated_from: sv-01-memory-architecture.md
tags: ["#type/wiki", "agi", "memory", "rag", "sv-research"]
created: 2026-05-12
updated: 2026-05-19
status: phase-a-plus-done
parent: [[11-wiki/superintelligent-vault-research]]
---

# SV-1 — Memory architecture

First article of the 8-axis superintelligent-vault research. **Question:** how to structure an LLM agent's memory so it isn't flat file-search but hierarchical, associative, and learns through use.

## 1. The axis core

In the LLM-agent context, **memory architecture** is a system that extends the model's limited context window — enabling long-term storage, dynamic retrieval, and learning from past events. Mem0 calls it a "universal, self-improving memory layer"; Letta defines a "memory-first" stateful agent; the Generative Agents paper describes an experiential store recorded in natural language.

### Key architectural levels

| Level | Stores | Example |
|---|---|---|
| **Working memory** | Active context, current task | MemGPT virtual context (fast tier) |
| **Episodic memory** | Raw events, observations, dialogues | Generative Agents memory-stream |
| **Semantic memory** | High-level reflections, abstractions, causality | Generative Agents reflection, RAPTOR tree, GraphRAG entity-graph |

The **memory hierarchy** matters because it lets the agent move data between fast (active) and slow (archival) tiers — MemGPT calls this **virtual context management** (borrowed from OS theory).

## 2. Canonical approaches

### Generative Agents (Park et al. 2023, Stanford)
- **Mechanism:** Records observations as a **memory stream** in natural language; periodically synthesizes raw memories into **higher-level reflections**; dynamically retrieves for planning.
- **Novelty:** The reflection loop — the agent automatically "thinks about" its memories.

### MemGPT (Packer et al. 2023, Berkeley)
- **Mechanism:** OS-like virtual memory hierarchy (fast=context-window, slow=archival), **interrupts** for control flow. The agent decides what to page in/out.
- **Novelty:** "LLM as OS kernel" — paging primitives for prompt context.

### RAPTOR (Sarthi et al. 2024, Stanford)
- **Mechanism:** **Recursive abstractive processing** — bottom-up recursive clustering + summarization, **tree-structured memory**. Retrieves from multiple tree levels.
- **Novelty:** Multi-resolution retrieval — both detail and big-picture.

### GraphRAG (Edge et al. 2024, Microsoft Research)
- **Mechanism:** LLM extracts **entities + relations** from source docs → entity knowledge graph + **community summaries**. For queries, partial answers → global synthesis.
- **Novelty:** Scales to 1M-token corpora; solves "global questions" that classical RAG cannot.

### Mem0 (open-source, 2024)
- **Mechanism:** **Self-improving memory layer** as an API/CLI service; integrates with LangChain/CrewAI.
- **Novelty:** Plug-and-play memory service.

### Letta (Berkeley, MemGPT-spinoff)
- **Mechanism:** **Memory-first agent** framework — sleep-time-compute (learning during idle), persistent state.
- **Novelty:** Memory-first design principle — architecture starts from state, not prompt templates.

## 3. Tech-stack options 2026

### Managed memory services

| Tool | Tradeoff | Use case |
|---|---|---|
| **Mem0 Cloud** | Production-scale infra, fast to deploy | Quick integration; "universal self-improving memory" pattern |
| **Letta Cloud** | Desktop/CLI + cloud | Personalized memory-first agents, coding assistants, AI companions |
| **Microsoft GraphRAG** | Two-stage setup (graph-build + query), higher complexity. Scales to 1M tokens | Global, holistic questions over full corpora |

### Local vector / graph stores

- **Local vector:** Chroma, Qdrant, Weaviate, FAISS, pgvector
- **Managed vector:** Pinecone, MongoDB Atlas Vector
- **Graph store:** Neo4j, Memgraph
- **Hybrid:** ElasticSearch + vector plugin, PostgreSQL + pgvector + Apache AGE

## 4. Breakthroughs 2024-2026

### Oct 2023 — MemGPT and virtual context
Introduced **virtual context management** modeled on hierarchical OS memory. Enabled multi-session agents that remember, reflect, and evolve over long-running interactions.

### Jan 2024 — RAPTOR and multi-level retrieval
Recursive tree-building over text chunks: embed → cluster → summarize. Retrieves from **different abstraction levels** at inference, delivering holistic understanding for multi-hop reasoning.

### April 2024 — GraphRAG and community summaries at scale
Solved **global questions** ("what are the main themes?") that prior RAG couldn't handle. Builds entity knowledge graph + pre-generated **community summaries**. Scales to 1M-token corpora.

## 5. Failure modes

### Retrieval-irrelevancy (the documented classic)
- **GraphRAG diagnosis:** Classic RAG **fails on global questions**. User intent is really **query-focused summarization**, not exact-fact retrieval.
- **RAPTOR diagnosis:** Most retrieval extracts **only short, contiguous chunks** — limits holistic context understanding.
- **MemGPT diagnosis:** Limited context windows **severely hurt** multi-session chat and long-document analysis.

### Briefly noted
- **Stale memory:** Retrieval-augmented models adapt better to a changing world than static-knowledge base models (RAPTOR), but failure-mode coverage is thin.
- **Privacy:** Letta mentions Permissions/Secrets management but doesn't elaborate on leakage / cross-user pitfalls.

## 6. Implementation in a personal markdown vault

### 6-step theoretical roadmap

1. **Record raw observations** — every user interaction, command, session event lands as **immutable** raw in `10-raw/` and `08-Sessions/`.
2. **Generate entity knowledge graph from static knowledge** — indexing script processes evergreen content (`11-wiki/`) and rules (`00-Meta/`).
3. **Pre-generate community summaries** — periodic job over mature knowledge (`11-wiki/`, `02-Projects/`); enables global queries like "what are the main project challenges?".
4. **Run reflection loop over memory** — async process analyzes `08-Sessions/` and `10-raw/`, finds cross-session connections, writes reflections to `05-Memory/` or `07-Decisions/`.
5. **Virtual context management + interrupts** — separated "fast" memory (current `08-Sessions/`) and "slow" memory (`11-wiki/` + `05-Memory/`) in the agent's prompt; control-flow code loads elements on demand.
6. **Dynamic retrieval in active session** — broad queries hit community summaries; specific decisions hit raw memories and reflections.

## 7. Open research questions

1. **Memory fine-tuning vs in-context + LoRA adapters** — current architectures all rely on in-context expansion; weight-update memory fusion is open.
2. **Multi-modal memory** — sources focus strictly on text; visual/audio/spatial memory is absent.
3. **Federated memory and distributed privacy** — sharing memory across agents/users with cryptographic or FL-based privacy isn't covered.
4. **Hardware-level optimizations** — KV cache, prefill caching for cost-effective long-context.
5. **Memory + reasoning deeper combination** — iterative reasoning with internal memory calls for hypothesis testing.

## Phase A+ expansion (2026-05-12 deep-research)

Source pool grew 6 → 249. Key finding: **strict separation of canonical Markdown source from derived vector index** (the vector DB is a rebuildable cached view, never the source of truth). For a $50-100/mo cost-sensitive setup, **Chroma embedded + BM25 hybrid retrieval** is the sweet spot; async memory-consolidation (Letta-style) only at $200/mo+ tier.

### Production-ready vs academic

| Technology | Category |
|---|---|
| **Letta** | Production-ready |
| **Mem0** | Production-ready (LOCOMO benchmark: 91% latency reduction, 90%+ token savings) |
| **Pinecone** | Production-ready (~$70/mo serverless) |
| **Qdrant** | Production-ready (10M-1B vectors, Rust engine + quantization) |
| **RAPTOR** | Academic (QuALITY benchmark only) |
| **MemGPT** | Academic (continued in Letta) |
| **GraphRAG** | Academic |
| **Chroma** | MVP / prototyping (under 10M vectors) |

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — background for the vault's current memory structure
- [[11-wiki/Crystallization-protocol]] — connection to axis 5 (auto-crystallization)
