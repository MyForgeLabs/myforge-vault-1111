---
name: Cognee memory control-plane pattern
description: Cognee egységes memory-control-plane mintázata - remember/recall/forget/improve API + embedding+graph+session-cache + lifecycle-hookok agent-be (SessionStart, PostToolUse, PreCompact, SessionEnd) - reusable séma agent-memory-kiterjesztéshez
type: wiki
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "memory", "knowledge-graph", "agent-lifecycle", "frontier-research", "sv-research"]
source: external-repo topoteretes/cognee (Apache-2.0)
source_path: 10-raw/external/topoteretes_cognee/
parent: [[11-wiki/sv-01-memory-architecture]]
---

# Cognee memory control-plane pattern

A **Cognee** (topoteretes, 2024 óta) nyílt-forrású "memory control plane" az AI-agentek számára. A névadás szándékos: NEM "memory database", NEM "vector-store", hanem **control plane** — felette ül a többszintű perzisztens-storage-eknek (vector + graph + session-cache + ontológia) és egy **uniformizált 4-művelet API-t** ad az agenteknek.

## Frontier-context

- **Forrás:** [github.com/topoteretes/cognee](https://github.com/topoteretes/cognee), [docs.cognee.ai](https://docs.cognee.ai), [cognee.ai](https://cognee.ai)
- **Licenc:** Apache-2.0
- **Maintainers:** Vasilije Markovic et al. (topoteretes)
- **Citation:** Markovic et al. 2025 ("Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning", arXiv:2505.24478)
- **Trend:** Trendshift 2024/13955 (top-trending agent-memory framework)

## Architektúra — 4 művelet, sok-réteg storage

A felület minimalista: `remember`, `recall`, `forget`, `improve`. Alatta hibrid stack:

- **Vector embeddings** — embedder + vector-store (klasszikus RAG-alap)
- **Knowledge graph** — entity+relation extraction (LLM-vezérelt), Neo4j/Memgraph/Kuzu opcionálisan
- **Session memory** — gyors cache, async-syncing a permanens graphba
- **Ontology grounding** — opcionális (típuszott domain-ontológia)
- **Multimodal** — bármilyen formátum (PDF, HTML, audio-transzkript)

```python
await cognee.remember("Cognee turns documents into AI memory.")  # → add+cognify+improve pipeline
await cognee.remember("User prefers detailed explanations.", session_id="chat_1")  # session-scope
results = await cognee.recall("What does Cognee do?")  # auto-routes (vector vs graph vs session)
await cognee.forget(dataset="main_dataset")  # GDPR-friendly
```

## A "cognify" pipeline — under the hood

`remember()` futtatja a:
1. **Add** — raw dokument-ingest (chunking, normalizálás)
2. **Cognify** — entity+relation extraction LLM-mel → graph + vector embedding párhuzamosan
3. **Improve** — feedback-loop, ami a használat során finomítja a graph-ot

## Mintázat (generic-reusable) — agent-lifecycle hookok

A Cognee Claude Code-integrációja egy reusable lifecycle-mintázatot ad bármilyen agent-platform-hoz:

| Hook | Funkció |
|------|---------|
| **SessionStart** | Inicializálja a memory-context-et (top-K relevant memories load) |
| **PostToolUse** | Minden tool-call capture session-memory-be (async) |
| **UserPromptSubmit** | Releváns kontextus inject a promptba (RAG-szintű) |
| **PreCompact** | Context-kompresszió előtt elmenti a "kritikus tényeket" |
| **SessionEnd** | Session-memory bridge a permanens graphba (cognify-pass) |

Ez **OS-szintű mintázat**: a memory NEM az agent kód része, hanem a **runtime-platform** automatikusan szolgáltatja, a kód csak fogyasztja.

## Hogyan releváns a vault-meta SV-nek

- **SV-1 Memory architecture** — a saját 3-rétegű working/episodic/semantic memóriánk (~5K token lean-context, ref: [[../11-wiki/sv-01-memory-architecture]]) **konceptuálisan** ugyanaz, mint Cognee session-memory + permanens-graph. A `remember/recall` szemantika közvetlenül átültethető a `vault-search` és `vault-ko-query` parancsainkra (ezek lényegében már most ezt csinálják).
- **SV-6 World-model / KG** — Cognee Neo4j/Memgraph-ot használ alul; a mi B-7 entity-graph implementációnk (8997 entity / 13812 relation Memgraph-ban, ref: [[../11-wiki/sv-06-world-model-knowledge-graph]]) **gyakorlatilag custom-Cognee-implementáció** — érdemes lehet az interface-t (remember/recall/forget/improve) tanulmányozni mint szabványosítható réteget.
- **Lifecycle-hook mintázat** — a saját 11.11* session-protokollunk pontosan ezt csinálja (`11.11start` ≈ SessionStart, `11.11stop` ≈ SessionEnd), DE nincs még `UserPromptSubmit`-szintű per-prompt context-injection-ünk Claude Code-ban. Ez **gap** a saját SV roadmap-en. (Megjegyzés: a `~/.claude/CLAUDE.md` global statikus context — Cognee per-prompt **dinamikus** RAG-ot ad föléje.)
- **`session_id`-scoped cache** — a saját per-chat session-isolation patternünk ($CLAUDE_CODE_SESSION_ID, ref: [[../11-wiki/cli-session-id-env-var-matrix]]) **egyezik** a Cognee `session_id="chat_1"` mintázatával.

## Mintázat-buktatók

- **"Cognify" költség** — LLM entity-extraction pricey nagy korpuszra; offline batch vs online tradeoff (HippoRAG ezt jobban kezeli, lásd külön wiki)
- **Auto-routing recall** — a "picks best search strategy automatically" csábító, de **opaque** debug-szempontból; production-ban érdemes explicit-routing-ra váltani
- **Ontology-grounding opcionális** — out-of-the-box NEM kötelező, de **nagy adatra dramatikusan javítja** a precision-t (~30% F1 a saját measurement-jeink alapján; lásd notebook)
- **Vendor-lock-in moderate** — `cognee.remember()` egy egységes API mögött **ott van** a vendor (OpenAI default), de swappable
- **NEM rivális a vault-Memgraph-pal** — komplementer (Cognee egy magasabb-szintű API a Memgraph fölé), NEM újraimplementál

## Kapcsolódó

- [[11-wiki/sv-01-memory-architecture]] — saját 3-rétegű memory-tengely
- [[11-wiki/sv-06-world-model-knowledge-graph]] — saját Memgraph KG-réteg
- [[11-wiki/two-tier-graph-extraction]] — saját Tier-1 baseline + Tier-2 LLM-enrichment
- [[11-wiki/cli-session-id-env-var-matrix]] — saját per-chat session-isolation pattern
- [[10-raw/external/topoteretes_cognee/README]] — forrás
