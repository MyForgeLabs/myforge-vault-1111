---
name: LangGraph durable-stateful agent-orchestration pattern
description: LangGraph low-level agent-orchestration mintázata - durable execution (perzisztens state, automatic resume) + human-in-the-loop interrupt (state-inspect+modify) + komplex memory (short-term working + long-term persistent) + Pregel/Apache-Beam-inspired graph-orchestration. Reusable séma stateful agentek építéséhez
type: wiki
created: 2026-05-18
updated: 2026-05-18
status: done
tags: ["#type/wiki", "agi", "multi-agent-orchestration", "stateful", "human-in-the-loop", "frontier-research", "sv-research"]
source: external-repo langchain-ai/langgraph (MIT)
source_path: 10-raw/external/langchain-ai_langgraph/
parent: [[11-wiki/sv-03-multi-agent-orchestration]]
---

# LangGraph durable-stateful agent-orchestration pattern

A **LangGraph** (LangChain Inc., 2024 óta) low-level orchestration-framework hosszan-futó, **stateful** agentekhez. Trusted by Klarna, Replit, Elastic. Inspirált a Google [Pregel](https://research.google/pubs/pub37252/) és Apache Beam graph-execution-modelljéből, a public-interface a NetworkX-ből. **Központi értékajánlata:** az agent NEM stateless-RPC, hanem **perzisztens state-graph**, automatikus failure-resume-mal, ember-felülbírálással, hosszú-távú memóriával.

## Frontier-context

- **Forrás:** [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph), [docs.langchain.com/oss/python/langgraph](https://docs.langchain.com/oss/python/langgraph)
- **Licenc:** MIT (LangChain Inc.)
- **Maintainers:** LangChain Inc., LangChain OSS team
- **Adoption:** Klarna, Replit, Elastic, production-scale
- **Higher-level:** `deepagents` Python package (plan + subagents + filesystem)

## Architektúra — 5 fő építőelem

### 1. Durable execution

A agent-graph execution **perzisztens state**-tel megy — minden node-kimenet checkpointolva. Crash / network-loss esetén **pontosan onnan** folytatódik, ahol elakadt. Hagyományos LLM-stack-eknél ez kézi retry+state-replay; LangGraph-ban beépített.

### 2. Human-in-the-loop (interrupt)

`interrupt()` mechanizmus: az agent **bármikor megáll**, az ember **inspect-elheti és módosíthatja a state-et**, majd folytat. Tipikus use-case-ek:
- Confirm-before-action (destruktív action engedélyezése)
- Slot-filling (ember adja meg a hiányzó paramétert)
- Diff-review (ember elfogadja vagy elutasítja az agent-by tervet)
- Tool-call-edit (agent tool-call paraméterét ember átírja előtte)

### 3. Comprehensive memory (két szint)

- **Short-term working memory** — folytatólagos reasoning context (per-graph-execution)
- **Long-term persistent memory** — sessions-on átívelő, deletable, queryable

### 4. LangSmith integration (eval + observability)

Trace-vizualizáció, state-transition capture, runtime-metrika. Külön termék (`LangSmith`), de "debugging poorly-performing LLM app runs" specifikusan ezen csinálható.

### 5. Production-ready deployment

`LangSmith Deployment` — visual-prototyping + scalable infra long-running stateful workflow-khoz.

## Mintázat (generic-reusable)

```python
# pseudocode-szintű
graph = StateGraph(MyState)

graph.add_node("planner", planner_node)
graph.add_node("worker", worker_node)
graph.add_node("critic", critic_node)
graph.add_node("human_review", interrupt_node)

graph.add_edge("planner", "worker")
graph.add_conditional_edge("worker", route_based_on_state, {
    "review": "human_review",
    "continue": "critic",
    "done": END,
})
graph.add_edge("human_review", "worker")
graph.add_edge("critic", "planner")

app = graph.compile(checkpointer=PostgresCheckpointer(...))
```

**Generic-reusable mintázat:**
- **State** mint központi entitás (NEM ad-hoc dict)
- **Nodes** = pure functions state → state
- **Edges** = conditional routing, lehet ciklus
- **Checkpointer** = perzisztencia-réteg (Postgres / SQLite / Memory)
- **Interrupts** = explicit human-control-points

Ez **Pregel/Beam-szintű** absztrakció az agent-flow-khoz.

## Hogyan releváns a vault-meta SV-nek

- **SV-3 Multi-agent orchestration** — a saját **subagent-fanout** mintázatunk (claude-code, 8× parallel general-purpose, $0 cost, ref: [[../11-wiki/claude-code-subagent-fanout]]) **stateless** és **one-shot**. LangGraph **stateful and durable**. **Konkrét gap:** a multi-fázisú feladatainkban (pl. vault-ko-ingest 2-phase pending pattern, vault-net-ingest with retry) **ad-hoc state-machine-eket** írunk, ami **épp az**, amit a LangGraph szabványosít. Érdemes a következő-generációs vault-stack-et LangGraph-szerű state-graph fölé tenni.
- **SV-1 Memory architecture** — a saját 3-rétegű working/episodic/semantic struktúránk **egyezik** a LangGraph "short-term + long-term" mintázattal magasabb-szinten.
- **Crystallization workflow (`11.11stop`)** — a propagation-loop **state-machine-szerű**: bullet-extract → score (G-Eval) → route → preview → confirm → propagate. **Most ad-hoc python script**. LangGraph-state-graph forma **lényegesen tisztább** lenne, különösen az interrupt-szemantika (human-in-the-loop a preview-ben).
- **Durable execution értékes a long-running ingest-pipeline-okra** — vault-net-ingest (firecrawl + retry + KO-extract + commit) **most NEM perzisztens** crash esetén; LangGraph-checkpointer megoldaná.
- **deepagents** (LangGraph-on built) — plan+subagents+filesystem, a saját MyForge Command-Centre-konceptünkkel **rokon**.

## Mintázat-buktatók

- **Vendor-lock-in moderate** — LangGraph maga MIT, de a LangSmith (debugging) **fizetős** és LangChain-stack-be huzz; "can be used without LangChain" ígéret, de a doc-és példa-ökoszisztéma erősen LangChain-féle
- **Boilerplate** — `StateGraph` + `add_node` + `add_edge` + `compile(checkpointer=...)` **mély boilerplate** egyszerű use-case-re; csak akkor éri meg ha tényleg long-running + stateful
- **Checkpointer-storage** — Postgres-checkpointer adatbázis-igényt hoz, ami egyszerű python-cron-job-hoz **overkill**
- **Pregel-paradigma vs. agent-loop** — a hagyományos ReAct-loop (`while True: think+act`) **mentálisan** egyszerűbb mint a Pregel-iteration. Stateful-agent-research-ben paradigma-shift kell
- **Hot-reloading state-graph** — production-on a state-graph **megváltoztatása mid-execution** veszélyes (existing checkpoint-okhoz nem matching node-ok); versioning-stratégia kell
- **NEM Pregel-szintű scale** — LangGraph "low-level orchestration", DE NEM Pregel-szintű (millió-node-os graphok), inkább 10-100 node-os agent-workflow-knak

## Kapcsolódó

- [[11-wiki/sv-03-multi-agent-orchestration]] — saját multi-agent-tengely
- [[11-wiki/claude-code-subagent-fanout]] — saját subagent-fanout (komplementer, NEM rivális)
- [[11-wiki/sv-01-memory-architecture]] — két-szintű memory parallel
- [[11-wiki/dspy-signatures-and-gepa-optimizer-pattern]] — DSPy a programming-réteg, LangGraph az orchestration-réteg (komplementer)
- [[10-raw/external/langchain-ai_langgraph/README]] — forrás
