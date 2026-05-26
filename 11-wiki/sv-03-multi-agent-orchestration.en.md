---
name: SV-3 Multi-agent orchestration
type: wiki
lang: en
translated_from: sv-03-multi-agent-orchestration.md
tags: ["#type/wiki", "agi", "multi-agent", "orchestration", "agent-architecture", "sv-research"]
created: 2026-05-12
updated: 2026-05-19
status: done
parent: [[11-wiki/superintelligent-vault-research]]
---

# SV-3 — Multi-agent orchestration

Third article of the 8-axis SV research. **Question:** do multiple parallel, specialized agents (planner / executor / critic / summarizer / red-team) deliver significantly higher quality than a single-agent system — and if so, what architectural patterns fit a session-based vault + skill-pool?

## 1. The axis core

**Multi-agent orchestration** is a control/architecture paradigm where several **specialized autonomous agents** (LLMs, tools, humans) communicate via **structured network or hierarchical patterns** to solve complex tasks. Its core is **"conversation programming"** and **state management** — task solving emerges from **iterative agent collaboration** (plan → feedback → execute), not a single monolithic step.

### Single-agent vs multi-agent

Single-agent systems overload at **5-10 tools**: context window saturates, decisions degrade. Multi-agent systems split work to **specialized agents** (researcher, coder, mathematician, critic) with their own prompts and tools, collaborating via **dedicated interaction patterns** (e.g. orchestrator-worker).

### Why parallel agents are meaningfully better

| Mechanism | Result | Source |
|---|---|---|
| **Focused context + token scaling** | Anthropic: **~80% of performance variance explained by token usage**; subagents work in their own context | Anthropic multi-agent research system |
| **Divergent thinking + critic loop** | AutoGen Writer+Safeguard generates **8-35% more safe code**; ChatDev "communicative dehallucination" massively improves code runnability | AutoGen, ChatDev |
| **Long-horizon coherence** | Generative Agents ablation: multi-agent dynamics **essential** for believable long-term social behavior | Park et al. 2023 |

Anthropic measured up to **90.2% better performance** in complex research tasks — at **~15× the token cost**.

## 2. Canonical patterns

### Generative Agents (Park 2023, Stanford)
Natural-language memory stream + dynamic retrieval + reflection loop + planning. Long-horizon coherence without hardcoded rules; emergent social behavior in Smallville.

### ChatDev (Qian 2023)
Waterfall (plan/code/test) via specialized agents in a **chat chain**; paired instructor + assistant. **"Communicative dehallucination"** — coder and tester debate until bugs surface.

### AutoGen (Microsoft 2023)
**"Conversation programming"** — flexible messaging, shared chats or hierarchical structures; LLM/tool/human mix. Built-in `GroupChatManager`.

### CrewAI
**Flows** (deterministic, event-driven) + **Crews** (autonomous role-playing agent teams). Separates autonomy from control.

### LangGraph (LangChain)
**Directed graph** (DAG) + state machine, shared-state objects. **"Durable execution"** — time travel, streaming, memory, human-in-the-loop, custom cognitive architectures.

### Anthropic Claude Agent SDK
**Composable / simplicity-first** — augmented LLM + workflows + autonomous agents. Production systems **rarely use complex frameworks**. **Orchestrator-worker pattern** — lead researcher delegates to parallel search subagents.

## 3. Tech-stack options 2026

| Tool | Philosophy | DX | Tradeoff | Typical use |
|---|---|---|---|---|
| **LangGraph** | Graph | Higher learning curve | Most robust durable execution; time travel + streaming + memory | Async enterprise workflows, HITL, multi-day processes |
| **CrewAI** | Role | Low | Production-ready Flows+Crews, less low-level control | Complex content gen, API backends |
| **AutoGen** | Conversation | Medium | Token-overshoot risk in open chats | Software dev, math, dynamic debate |
| **Claude Agent SDK** | Composable | Lowest | "Build effective agents" — autonomy only when needed | Open-ended research, orchestrator-worker |
| **OpenHands** | Turnkey | Plug-and-play | MIT open-source, SDK+CLI+GUI+enterprise VPC; thousands of parallel cloud agents | Coding agent farms, enterprise deployment |
| **Devin** | Turnkey closed-source | SaaS | Built-in sandbox: shell + editor + browser | "Autonomous AI software engineer" |
| **Manus** | Turnkey generalist | UI-level | "Less structure, more intelligence" — desktop + browser + Slack + email | Non-developer users |

### The "less framework" lesson

Anthropic engineering: **production systems rarely use complex frameworks**. Recommended pattern: simple composable primitives, climb the complexity ladder only when truly needed.

## 4. Breakthroughs 2024-2026

### Anthropic multi-agent research system (lead + subagents)
Complex async Claude system: **parallel discovery + synthesis**. ~15× token use vs single chat, **up to 90.2% better performance**.

### Devin — first autonomous AI software engineer
**Built-in sandbox compute environment**: shell + editor + browser. Thousands of decisions, in-flight learning and bug-fixing.

### OpenHands — open-source alternative
SDK + CLI + local GUI + enterprise VPC. **Code-based agent definition**, thousands of parallel cloud agents.

### Manus — generalist browser operator
"Less structure, more intelligence" — desktop app, browser, Slack, email. Builds presentations/sites/designs for non-developer users.

### Lead-agent + subagent pattern (orchestrator-worker)

1. **Lead agent** receives complex request, builds strategy, decomposes
2. **Specialized subagents** work **in parallel** in their own context
3. Subagents act as **intelligent filters** — return distilled essence
4. Lead **synthesizes** final answer

### Parallel tool use vs sequential

Modern parallel: (1) Lead launches **3-5 subagents** simultaneously, (2) subagents run **3+ tools** in parallel. **Up to 90% shorter research time.**

### Context rot and mitigations

- **Intelligent compression + external memory**
- **Clean-context subagents** with cautious handoff
- **Direct filesystem output** — subagent writes files, returns reference (avoids "telephone game")

## 5. Failure modes

### 5.1 Token cost explosion
One agent 4× a chat; multi-agent research system **~15× cost**. Smallville: 25 agents × 2 days = thousands of dollars.

### 5.2 Error propagation
In long-running stateful agents, errors **compound**. One bad tool pick → catastrophic divergence.

### 5.3 Debugging hell
Same prompt, different runs. Small code change → domino effect. Without tracing, devs see "unintelligible chatter".

### 5.4 Hallucination amplification + role-flipping
Poorly structured communication amplifies errors: role-flipping, instruction repetition, fabricated answers, **memory bias** (agent "embellishes" past events).

### 5.5 Coordination overhead + race conditions
Early systems: 50 subagents wandering the web for a simple question. Sync → bottleneck; async → state-consistency problems.

### 5.6 Context rot — see 4.

### 5.7 Security holes
**Prompt injection** from external data; **memory hacking** (manipulated chat convinces agent of a fabricated past event); risky autonomous code execution without a Safeguard.

### When NOT to use multi-agent

| Situation | Why not |
|---|---|
| Simple, well-defined task | Wasted latency + cost |
| Tightly-coupled shared-context work | LLM agents in 2026 still poor at real-time coordination |
| Weak task definition | System can't fill the spec gap |

## 6. Implementation in a personal vault

### 6.1 Framework choice: LangGraph or own Anthropic-SDK

Two realistic options:
- **LangGraph** — graph-based, durable execution, shared state (the vault IS the shared state), HITL, time travel
- **Own Anthropic-SDK** — simple composable primitives, orchestrator-worker as default

Anthropic's lesson — **production rarely uses complex frameworks** — suggests: **start with own SDK**, switch to LangGraph only when true state-graph complexity emerges.

### 6.2 Role split for vault tasks

| Role | Responsibility |
|---|---|
| **Planner / Orchestrator** | Receives prompt, builds strategy, picks skills from pool, decomposes |
| **Executor / Subagent (Researcher)** | Modifies specific Markdown files in isolated context |
| **Critic / Safeguard** | Validates Executor output (format + content hallucination); gate before commit |
| **Summarizer / Citation** | Stitches backlinks, generates session-close report |

### 6.3 Direct-to-filesystem pattern (context-rot prevention)

Subagents **don't** return full content to the Planner — they **write Markdown directly**, returning a lightweight reference (path, short summary). Perfect fit for the vault paradigm — **the vault IS the shared state space**.

### 6.4 MVP first sprint

| Step | Build |
|---|---|
| 1 | Orchestrator-Worker workflow — central LLM Planner receives task, picks subagent |
| 2 | 2-3 async Executors, **direct-to-filesystem** writes, status-only return |
| 3 | Critic (Reviewer) — simple evaluator-optimizer loop before file finalize |
| 4 | JSONL log per agent decision — debug non-determinism |

## 7. Open research areas

### 7.1 End-state benchmarks
Turn-by-turn evaluation assumes fixed step counts; multi-agent reaches **identical results via different valid paths**. End-state quality evaluation methodology needed.

### 7.2 Safety: memory hacking + cascading failures
Carefully-crafted conversation convinces the agent of a fabricated past event. Fail-safes for cascading errors, reward hacking, runaway control are missing.

### 7.3 Async A2A coordination + state consistency
Current systems mostly sync (bottleneck). Async would speed things up but **distributed state-consistency + error-containment** is unsolved.

### 7.4 Cost optimization + optimal topologies
No "one fits all" — agent count, roles, interaction patterns are workload-dependent. Smaller dedicated models trained for multi-agent architectures emerging.

### 7.5 Hybrid orchestration + self-improving agents
Perfect human-in-the-loop balance. Andrew Ng's open question: when does a single truly general-purpose agent supersede task-specific frameworks?

## Phase A+ key takeaway

2026 industry mainstream consensus: multi-agent ≠ many-agent chat-net (GroupChat dead-end), but **hard "Orchestrator + isolated subagent + summary-only return + filesystem-as-state"** + cost-aware **OmniRoute model-mix**. A markdown-vault paradigm (Markdown = single source of truth, session-protocol = orchestrator-protocol, skill pool = `SKILL.md` library) **fits structurally**.

### Production-ready vs academic

| Framework | Status |
|---|---|
| **LangGraph (LangChain)** | Enterprise leader |
| **CrewAI** | Production, >60% of Fortune 500 prototypes |
| **AutoGen (Microsoft Agent Framework 1.0)** | Productized; graph orchestration + middleware + MCP |
| **Anthropic Multi-Agent / Managed Agents** | "Cattle not pets" — 15× tokens, TTFT 60-90% faster via session replay |
| **OpenHands** | 67k+ stars, MLSys 2026 architecture |
| **Devin** | Closed-source turnkey SWE — Otterlink hypervisor + SWE-1.x models |
| **Manus** | Production browser operator for non-devs |
| **ChatDev + traditional GroupChat** | Academic — pushed out of production |

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[11-wiki/sv-01-memory-architecture]] — links to context-rot solutions
- [[11-wiki/Crystallization-protocol]] — summarizer-agent role base
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — base pattern scaling to multi-parallel agent runtime
