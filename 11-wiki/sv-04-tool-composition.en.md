---
name: SV-4 Tool composition
type: wiki
lang: en
translated_from: sv-04-tool-composition.md
tags: ["#type/wiki", "agi", "tool-use", "mcp", "skill-library", "sv-research"]
created: 2026-05-12
updated: 2026-05-19
status: done
parent: [[11-wiki/superintelligent-vault-research]]
---

# SV-4 — Tool composition

Fourth article of the 8-axis SV research. **Question:** how can an LLM agent **discover, select, and compose new tools** (functions, APIs, MCP servers) on its own — exponential tool growth and self-improving capability without humans pre-installing everything.

## 1. The axis core

**Tool composition** is the paradigm shift where an LLM agent — instead of using pre-wired, static workflows — **autonomously discovers, selects, and composes external functions, APIs, and MCP servers**. The agent decides when, how, and which tool to invoke (Toolformer demonstrated this); finds the most relevant from a growing API set (Gorilla retriever, ToolGen virtual tokens); and chains tools into complex action sequences (Voyager skill library). The **Model Context Protocol (MCP)** specifies and standardizes this autonomy — agents **dynamically map and absorb new network capabilities at runtime**.

### Key dimensions

| Dimension | What it means | Example |
|---|---|---|
| **Tool discovery** | How does the agent find the right tool? | Gorilla retriever / ToolGen token / MCP Registry |
| **Tool selection** | How to pick among candidates? | Toolformer self-supervised / Constrained decoding |
| **Tool execution** | Actual invocation | JSON-RPC (MCP) / code execution / direct function call |
| **Tool composition** | Chaining multiple tools | Voyager skill library / ReAct iterative prompting |
| **Tool creation** | Writing new tools for itself | CREATOR / LATM Python function generation |

## 2. Canonical approaches

### Toolformer (Meta 2023) — self-supervised
Self-fine-tunes via self-generated API calls that reduce future-token loss. Learns when/how to call tools (calculator, search) without human demos. Tool use baked into weights.

### Gorilla (UC Berkeley 2023) — retrieval-based
Retrieval-aware architecture; external retriever (BM25, GPT-Index) fetches most relevant API docs at runtime. Reduces hallucination; adapts to API changes without retraining.

### ToolGen (2024) — virtual tokens
Folds tool discovery and execution into a **single generative task**: each tool gets a virtual token in the vocabulary. Scales to **47,000+ tools** without external retrieval; **constrained decoding** eliminates hallucinated tool calls.

### Voyager (NVIDIA 2023) — skill library + iterative prompting
Lifelong-learning embodied agent builds a **library of executable code skills**. Environmental feedback, runtime errors, and self-verification iteratively refine skills. The agent **writes its own tools** as reusable code.

### Model Context Protocol (Anthropic 2024-11) — standardized client-server
**Decouples AI applications from data sources**, enabling **JSON-RPC-based** integration. Agents connect to external MCP servers at runtime, fetching resources/prompts/tools. **Composability** — one agent can be both client and server. Plus an **MCP Registry** for dynamic discovery.

### Discovery method comparison

| Approach | Discovery method | Adding new tool |
|---|---|---|
| **Toolformer** | Baked into weights (implicit) | Retraining |
| **Gorilla** | External retriever (BM25/dense) | Update docs |
| **ToolGen** | Next-token prediction generative | Retrain with vocab extension |
| **Voyager** | Vector-DB semantic search over own code | Code generation |
| **MCP** | JSON-RPC `list_tools` + Registry API | Install new server |

## 3. Tech stack 2026

### MCP server implementations

| Tool | Tradeoff | Use case |
|---|---|---|
| **Anthropic reference servers + SDK** | Plug-and-play, stable; bring your own business logic | Fast integration (GitHub, Postgres, FS) |
| **Cloudflare Code Mode** | Token use drops **up to 98.7%** (code execution for MCP); needs sandbox + monitoring | Large MCP pool where tool count > context |
| **Block / Goose** | Open-source agent with MCP "extensions"; UI-flexible but platform-specific | Custom MCP-based apps with UI focus |

### Tool registries

| Approach | Tradeoff |
|---|---|
| **ToolGen virtual tokens** | Constrained decoding (no hallucination, no retriever); new tool = retrain |
| **Gorilla retriever** | Continuous API refresh without retraining; retrieval errors propagate |
| **MCP Registry** | Standardized, dynamic discovery → self-evolving agents; network + trust required |

### Agent framework tool handling

| Framework | Approach |
|---|---|
| **Claude Code** | **Tool Search** — tools loaded into context only when needed (deferral) + interactive elicitation |
| **LangGraph** | MCP adapters/connectors; framework provides memory + control loop |
| **AutoGPT** | ReAct subgoal decomposition; lacks self-verification and dynamic skill storage |
| **Replit Agent** | MCP-integrated; extended API access for coding |

### Skill library storage patterns

| Pattern | Tradeoff |
|---|---|
| **File-based** (`SKILL.md` + script) | Token-efficient (only loaded file enters context), git-versionable; needs strict sandbox |
| **Vector-DB Voyager-style** | Semantic retrieval over descriptions; ongoing embedding cost, retrieval errors |

## 4. Breakthroughs 2024-2026

**MCP — ecosystem foundation (Anthropic 2024-11).** Open standard ending fragmented integrations. By 2026 Cloudflare, Block, Replit, and many enterprise vendors expose access via MCP servers.

**Code-execution-with-MCP (Anthropic 2025).** Universal tool-execution layer: agent **writes code** to access MCP servers instead of directly calling them — **up to 98.7% token reduction**.

**Claude Code skill system.** Successfully-executed agent code stored in `SKILL.md` — the agent builds **a personal toolkit of higher-level reusable capabilities** over time.

**ToolGen (2024) — virtual tokens.** Tools integrate into the LLM **vocabulary** as unique tokens; discovery = next-token prediction. Scales to **47,000+ tools**.

**Autonomous tool creation (CREATOR, LATM).** LLMs **create new tools** as Python or SQL functions — expanding their own capabilities.

**Compositional autonomy / self-discovery.** Runtime, **no-human-loop** tool discovery. If a task lacks a tool, the agent **dynamically finds and installs a vetted MCP server**.

## 5. Failure modes

**Tool-context bloat.** Pre-loading all API docs/schemas blows the context window. *Mitigation:* Claude Code Tool Search (deferral), Cloudflare Code Mode.

**Hallucinated tool calls.** Model invents fictional tools, args, or non-existent parameters. *Mitigation:* ToolGen constrained decoding.

**Tool selection error.** Agent **misinterprets task** (SQL generator for a math problem) or chooses suboptimally under complex constraints.

**Compositional drift / compounding errors.** **One early bad decision dominoes** through a multi-step chain. *Mitigation:* Reflexion-style self-verification, DFSDT backtracking.

**Security / prompt injection.** External tools (web searches, unverified data) expose the model to **prompt-injection attacks**; arbitrary code execution + data privacy demand explicit oversight.

**Brittleness.** API spec change (e.g. Slack API) → rigid integration breaks. *Mitigation:* MCP abstraction + retrieval-based doc lookup.

### What the paradigms do NOT solve

- **Toolformer** generates calls but **cannot chain** (output of one tool as input of next) and lacks interactive browsing.
- **Voyager** lifelong learning **doesn't solve hallucination** — invalid blocks / nonexistent primitives still called; self-verification can erroneously approve failure.
- **MCP** unifies access, reduces context with code execution, but **doesn't solve multi-step compounding errors** and creates **new security problems** (open network capabilities + prompt injection + malicious clients).

## 6. Implementation in a personal vault

Existing stack:
- Markdown vault + session protocol + ~280 skill pool in `~/.claude/skills/`
- Installed MCP servers: chrome-devtools, context7, playwright, hostinger-mcp
- External-skill cherry-pick playbook: symlinking from external repos

### Concrete steps

#### 1. Automate skill discovery (session-end skill writing)

Bake Voyager **self-verification + memory-write** into session close: if the agent solved a novel problem, the protocol creates a new skill from used tool calls and code blocks.

#### 2. Voyager-style skill library inside the vault

Voyager stores skills in a vector DB by description embedding. Vault adaptation: each `~/.claude/skills/<slug>/SKILL.md` paired with a vault Markdown index (`12-skills/<slug>.md`) holding `skill_name`, `description`, `path`, `dependencies`, `last_used`, `success_rate`. Phase B couples this to the SV-1 embedding index for top-K retrieval at session start.

#### 3. Autonomous MCP-server-pool growth

The agent can **add new MCP servers** at runtime with explicit user-confirm (security):

```bash
npm install -g @modelcontextprotocol/server-postgres
claude mcp add --transport stdio postgres -- npx @modelcontextprotocol/server-postgres
```

**Protection layer:** new `mcp-installer` skill **mandatorily documents** each add as an ADR (`07-Decisions/...`) — full audit trail.

#### 4. Tool-registry indexing + Tool Search activation

With 280+ skills + N MCP servers, **tool-context bloat** is real. Claude Code's built-in **Tool Search** solves it: `ENABLE_TOOL_SEARCH=auto`. Critical MCP servers (FS, vault-reader) stay always-loaded via `.mcp.json` `alwaysLoad: true`. Others load on-demand.

#### 5. Cost-aware tool routing (Phase C+)

Per CATP-LLM framework: tag each MCP server/skill with **cost-tag** (token estimate, latency, $/call). The continuous-eval pipeline (SV-7) collects these; the router picks the cheapest sufficient tool.

## 7. Open research

1. **MCP server marketplace + trust protocol.** Anthropic official MCP Registry under development; **how to verify server trustworthiness** on open networks is open.
2. **Tool-use CoT training + backtracking.** ReAct + CoT fails on multi-tool tasks (compounding errors). ToolLLM DFSDT proposes backtracking; how to natively train multi-branch non-sequential planning without massive token use is open.
3. **Voyager-style skill evolution in production.** Works in Minecraft; what about software environments and physical robotics? **Skill maintenance** — how to forget/overwrite outdated (API-changed) skills.
4. **Security + sandboxing.** "Tools mean arbitrary code execution." Standardized defense against prompt injection, data exfiltration, malicious third-party tools is missing.
5. **Cost-aware tool routing.** CATP-LLM is first to train models for performance vs cost balance; runtime feedback integration + parallel non-sequential tool execution still open.

## Phase A+ summary

3 architectural elements for a markdown vault:
1. **Local Obsidian MCP server + code-execution layer** — Python filter on Playwright/Context7 output, only aggregated result enters context
2. **Dynamic Tool Search + `SKILL.md` encapsulation** — Built-in `ENABLE_TOOL_SEARCH=auto` OR custom dense retriever `bge-m3` + `bge-reranker-v2-m3` Top-K=3
3. **ReCreate-based TTE (Test-Time Tool Evolution) + CodeBERT deduplication** — Successful trajectories → new skills, failures → guardrails; cosine-similarity prevents skill bloat

**Order:** MCP layer first → SKILL.md meta + dynamic search → ReCreate evolution loop.

**Production-ready:** MCP, Claude Code/Tool Use API. **Academic:** Toolformer, Gorilla, ToolGen, Voyager, CREATOR, LATM (all paper-only as of 2026).

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[11-wiki/external-skill-cherry-pick]] — symlink-based skill curation
- [[11-wiki/sv-01-memory-architecture]] — embedding layer Voyager builds on
- [[11-wiki/Crystallization-protocol]] — Learnings → skill auto-conversion
