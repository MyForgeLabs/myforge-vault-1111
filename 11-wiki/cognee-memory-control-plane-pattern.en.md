---
name: Cognee memory control-plane pattern
description: Cognee unified memory-control-plane pattern - remember/recall/forget/improve API + embedding+graph+session-cache + lifecycle-hooks (SessionStart, PostToolUse, PreCompact, SessionEnd) - reusable scheme for agent-memory extension
type: wiki
lang: en
translated_from: cognee-memory-control-plane-pattern
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "memory", "knowledge-graph", "agent-lifecycle", "frontier-research", "sv-research"]
source: external-repo topoteretes/cognee (Apache-2.0)
parent: [[11-wiki/sv-01-memory-architecture]]
---

# Cognee memory control-plane pattern

**Cognee** (topoteretes, since 2024) is an open-source "memory control plane" for AI agents. The naming is deliberate: NOT a "memory database", NOT a "vector store", but a **control plane** — sitting on top of multi-tier persistent stores (vector + graph + session-cache + ontology) and exposing a **uniform 4-operation API** to agents.

## Frontier context

- **Source:** [github.com/topoteretes/cognee](https://github.com/topoteretes/cognee), [docs.cognee.ai](https://docs.cognee.ai), [cognee.ai](https://cognee.ai)
- **License:** Apache-2.0
- **Maintainers:** Vasilije Markovic et al. (topoteretes)
- **Citation:** Markovic et al. 2025 ("Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning", arXiv:2505.24478)
- **Trend:** Trendshift 2024/13955 (top-trending agent-memory framework)

## Architecture — 4 operations, multi-layer storage

The surface is minimal: `remember`, `recall`, `forget`, `improve`. Beneath it, a hybrid stack:

- **Vector embeddings** — embedder + vector store (classic RAG base)
- **Knowledge graph** — entity+relation extraction (LLM-driven), Neo4j/Memgraph/Kuzu optional
- **Session memory** — fast cache, async-syncing to permanent graph
- **Ontology grounding** — optional (typed domain ontology)
- **Multimodal** — any format (PDF, HTML, audio transcript)

```python
await cognee.remember("Cognee turns documents into AI memory.")  # → add+cognify+improve pipeline
await cognee.remember("User prefers detailed explanations.", session_id="chat_1")  # session-scope
results = await cognee.recall("What does Cognee do?")  # auto-routes (vector vs graph vs session)
await cognee.forget(dataset="main_dataset")  # GDPR-friendly
```

## The "cognify" pipeline — under the hood

`remember()` runs:
1. **Add** — raw document ingest (chunking, normalisation)
2. **Cognify** — entity+relation extraction with LLM → graph + vector embedding in parallel
3. **Improve** — feedback loop that refines the graph during use

## Pattern (generic-reusable) — agent-lifecycle hooks

Cognee's Claude Code integration produces a reusable lifecycle pattern for any agent platform:

| Hook | Function |
|------|----------|
| **SessionStart** | Initialises memory context (top-K relevant memories loaded) |
| **PostToolUse** | Captures every tool call to session memory (async) |
| **UserPromptSubmit** | Injects relevant context into the prompt (RAG-level) |
| **PreCompact** | Saves the "critical facts" before context compression |
| **SessionEnd** | Bridges session memory into the permanent graph (cognify pass) |

This is an **OS-level pattern**: memory is NOT part of the agent code, but provided by the **runtime platform** automatically; the code only consumes.

## Relevance to vault-style memory architectures

- **Memory architecture** — a 3-tier working/episodic/semantic memory (~5K token lean-context) is **conceptually equivalent** to Cognee's session-memory + permanent-graph. The `remember/recall` semantics map directly onto search and KO-query commands.
- **World-model / KG** — Cognee uses Neo4j/Memgraph underneath; a custom entity-graph implementation (8997 entity / 13812 relation in Memgraph) is **effectively a custom Cognee implementation** — worth studying the interface (remember/recall/forget/improve) as a standardisable layer.
- **Lifecycle-hook pattern** — session-protocol scripts already do this (start ≈ SessionStart, stop ≈ SessionEnd), BUT a `UserPromptSubmit`-level per-prompt context injection is often missing. This is a **gap**. (Note: a global static context like `~/.claude/CLAUDE.md` is static — Cognee adds **dynamic** RAG-style per-prompt context on top.)
- **`session_id`-scoped cache** — a per-chat session-isolation pattern (`$CLAUDE_CODE_SESSION_ID`) **matches** Cognee's `session_id="chat_1"` pattern.

## Pattern pitfalls

- **"Cognify" cost** — LLM entity-extraction is pricey on large corpora; offline batch vs online trade-off (HippoRAG handles this better, see separate wiki)
- **Auto-routing recall** — "picks best search strategy automatically" is tempting, but **opaque** for debugging; in production prefer explicit routing
- **Ontology grounding is optional** — not mandatory out-of-the-box, but **dramatically improves precision on large data** (~30% F1 in some measurements)
- **Vendor lock-in moderate** — `cognee.remember()` is a unified API but the vendor (OpenAI default) is **there** underneath; swappable
- **NOT a rival to Memgraph** — complementary (Cognee is a higher-level API on top of Memgraph), NOT a reimplementation

## Related

- [[sv-01-memory-architecture]] — multi-tier memory axis
- [[sv-06-world-model-knowledge-graph]] — Memgraph KG layer
- [[two-tier-graph-extraction]] — Tier-1 baseline + Tier-2 LLM-enrichment
- [[cli-session-id-env-var-matrix]] — per-chat session-isolation pattern
