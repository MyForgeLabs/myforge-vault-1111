---
name: SV-2 Recursive self-improvement
type: wiki
lang: en
translated_from: sv-02-recursive-self-improvement.md
tags: ["#type/wiki", "agi", "recursive-self-improvement", "prompt-evolution", "skill-library", "sv-research"]
created: 2026-05-12
updated: 2026-05-19
status: done-phase-a-plus
parent: [[11-wiki/superintelligent-vault-research]]
---

# SV-2 — Recursive self-improvement

Second article of the 8-axis SV research. **Question:** how to build an LLM agent system that doesn't just solve tasks but **improves itself** — its prompts, skills, even its code — learning from every interaction, beyond the manual crystallization confirmation loop.

## 1. The axis core

**Recursive self-improvement (RSI)** is the ability of an LLM agent to **autonomously analyze and improve its own operating logic, architecture, and learning processes**, becoming more efficient with each iteration. It transcends hand-designed fixed meta-learning routines: the agent dynamically alters the internal structures controlling its own behavior, based on environmental feedback and error analysis.

### The 4 main dimensions

| Dimension | What changes | Example architecture |
|---|---|---|
| **Prompt evolution** | Task prompts and "mutation prompts" iteratively refined via evolutionary principles | Promptbreeder, GEPA |
| **Skill library growth** | Successful interactions distilled into reusable skills (code, descriptions) in a dynamic library | Voyager, SAGE/SkillRL, Anthropic Agent Skills |
| **Self-reflection** | The model retrospectively evaluates performance, generates verbal feedback for future improvement | Reflexion, Self-Refine, RISE |
| **Code self-modification** | The agent rewrites its own source code at runtime, including the parts responsible for self-modification | Gödel Agent (monkey patching) |

## 2. Canonical approaches

### STaR — Self-Taught Reasoner (Zelikman et al. 2022)
Bootstraps from a small CoT seed: generates answers + rationales, retries on errors, fine-tunes on successful derivations. Matched 30× larger LLMs on CommonsenseQA.

### Reflexion (Shinn et al. 2023)
Verbal reflection on errors stored in an **episodic memory buffer**. Decision-strategy update **without weight changes**. 91% on HumanEval (vs GPT-4 baseline 80%).

### Voyager (Wang et al. 2023, NVIDIA)
Open-ended Minecraft agent with automatic curriculum; successful actions saved as **executable code in a growing skill library**. 3.3× more unique items, 15.3× faster milestone unlocks vs SOTA.

### Promptbreeder (Fernando et al. 2023, DeepMind)
LLM-driven evolutionary process mutating prompt populations. **Self-referential** — evolves the "mutation prompts" themselves. Beat hand-designed CoT and Plan-and-Solve on math and common-sense benchmarks.

### Self-Rewarding LMs (Yuan et al. 2024, Meta)
Iterative DPO where the model **generates its own rewards** via "LLM-as-a-Judge". Eliminates frozen reward models. Llama 2 70B after three iterations beat Claude 2, Gemini Pro, GPT-4 0613 on AlpacaEval 2.0.

### Gödel Agent (2025)
Inspired by Gödel machines. **Dynamic memory manipulation (monkey patching)** at runtime to analyze and rewrite its own code — including the algorithm responsible for self-modification. **Full self-reference, no built-in limits.**

## 3. Tech-stack options 2026

| Stack | Use case | Tradeoff |
|---|---|---|
| **Anthropic Claude Code + Agent Skills + MCP** | Single-thread disciplined master-loop + dynamic `SKILL.md` + external MCP | Exceptionally stable, auditable — but flat single-thread design misses multi-agent parallelism |
| **GEPA / DSPy / TextGrad** (prompt optimizer) | Reflection-based prompt mutation, works with closed APIs | Weight-free quality improvement — but **compile-time** on a dataset, NOT runtime self-correction |
| **AutoGen / LangGraph / CrewAI** (orchestration) | Multi-agent role delegation | Handles fixed workflows well — agent-protocol immaturity (ACP, ANP) can limit open-ended self-improvement |
| **ReFlect Harness** | Deterministic, error-detecting wrapper around the LLM; shape-based validators | Massively more reliable + token-efficient than pure LLM-judged self-correction — needs pre-coded validator per task type |

### Three stack paradigms

- **Prompt-evolution stack** — iterative refinement of instructions. Model weights unchanged. Pareto-front selection + verbal summarization. *(GEPA, DSPy, Promptbreeder)*
- **Skill-library-growth stack** — externally stored capability library. **Progressive disclosure** loads procedural modules per task. *(SAGE/SkillRL, Anthropic Agent Skills, Voyager)*
- **Code-self-modification stack** — true recursion: **monkey patching** of own code at runtime. Requires robust error handling. *(Gödel Agent)*

## 4. Breakthroughs 2024-2026

### 1. Full self-reference + runtime code rewriting (Gödel Agent)
First agent capable of overwriting its own runtime logic via monkey-patching — including the algorithms responsible for self-modification.

### 2. "Skill Engineering" era — dynamic capability libraries
2025-26 dominated by **Skill Engineering**. Anthropic standardized agent procedural knowledge with `SKILL.md` + MCP. The model dynamically loads multi-step instructions, code, workflows — no fine-tuning. **SAGE** and **SEAgent** algorithmically distill raw experience into skills, RL-validated.

### 3. Algorithm and full-codebase evolution (AlphaEvolve, DeepMind 2025)
Combines LLM creativity with automated evaluators to **evolve complex algorithms and entire codebases**. Cracked open math problems like the "kissing number problem".

### 4. Compound AI System prompt evolution (GEPA, 2026)
**GEPA (Genetic-Pareto Reflective Prompt Evolution)** optimizes **Compound AI systems** (many modules + prompts). Uses natural-language reflection on runtime trajectories, maintains generations on a Pareto front. **35× fewer trials** to beat RL methods (GRPO).

### 5. Test-time evolution without external verifiers (RSA)
**Recursive Self-Aggregation** maintains a **population of reasoning chains**, iteratively aggregating partially-correct steps. A 4B model (Qwen3-4B) reaches DeepSeek-R1 levels.

### 6. Reliability moves from prompt to wrapper (ReFlect Harness)
"Self-correction blind spot": for long tasks, text self-critique is **false-positive in 76-98% of cases**. ReFlect moves error detection and recovery OUT of the model into a deterministic runtime with shape-based validators and coded retries.

## 5. Failure modes

### 1. Self-correction blind spot
Huang et al. 2023: without external objective feedback, LLMs **almost cannot fix their own logic errors** — self-correction attempts **degrade** performance. **In 76% of cases the model accepts the wrong answer.** Hallucinations silently accumulate.

### 2. Degenerate repetition loops and cost explosion
Without structural limits, models fall into **infinite "repetition loops"**. **7-23% occurrence** in tests. Token-budget exhaustion, compute cost explosion without convergence.

### 3. Catastrophic forgetting and mode collapse
Dynamic skill loading can **inadvertently overwrite** useful defaults. Evolutionary methods → **diversity loss**: same successful patterns recycled → mode collapse, distribution drift.

### 4. Safety risks — overwriting the safety net
The biggest risk of fully self-referential (Gödel-Agent-like) architectures: if the agent **overwrites the protective error handler** via reward hacking or accident, the system collapses. **Sandboxed execution is mandatory.**

### 5. Yampolskiy limit (intelligence bottleneck)
As the agent grows complex, **understanding and improving its own code requires exponentially more intelligence**. Initially-self-modifying systems eventually "outgrow" their own interpretive capacity.

### What RSI alone does NOT solve

> Recursive self-improvement **cannot generate external ground truth** beyond what is in the model or environment.

Pure "LLM-judged" self-correction hits a **theoretical ceiling**: language models are too weak at deterministic verification. Self-improvement must be wrapped by non-LLM **harness systems** (linter, math engine, state-tracker) — the LLM proposes, deterministic verification disposes.

## 6. Implementation in a personal vault

### 1. Safety harness FIRST — sandbox + git-hook + rollback

> **Order is critical.** RSI is the LAST axis to enable, after the others are tracked.

- **Sandbox folder** — `00-Meta/Sandbox/`. All self-modification proposals land here first with `#sandbox` tag, `unvetted` permission.
- **Git pre-commit hook** — deterministic Python script (format validator, frontmatter schema, link consistency). **LLM proposes, tests dispose.** ReFlect-style "G3 Behavioral Sandbox" gate.
- **Revertable changes** — git checkpoint (`pre-self-mod-<timestamp>`) BEFORE every self-mod. Failed test → automatic `git reset`. The existing 10-min vault-autosave cron is the foundation.
- **Confidence threshold** — only `confidence >= 0.85` and **at least 2 independent sessions** auto-propagate. Lower → manual user-confirm.

### 2. Auto skill distillation from session history (SAGE/SkillRL pattern)

At `/11.11stop`, a synthesis process distills chat history into procedural skills:
- **Trigger:** the session solved a **novel** task (no matching skill in pool)
- **Reflection LLM call:** haiku-level call extracts successful step sequence from session events + diffs
- **`SKILL.md` generation with progressive disclosure:**
  - **Level 1 (metadata)** — YAML frontmatter (name, description, trigger), always in agent context
  - **Level 2 (instructions)** — distilled step-by-step body, loaded on-demand
- **Storage** — `~/.claude/skills/auto-distilled/<slug>/` with manual-review tag

### 3. Autonomous refinement of agent config (Gödel + GEPA hybrid)

**Self-update tool:** `EditTool` + `self_update` action — reads and overwrites the agent config **only in Sandbox** (`00-Meta/Sandbox/CLAUDE.md.proposal`).

**Prompt mutation (GEPA):**
- **Mutate** — every 10 sessions, a background process collects successful + failed trajectories, proposes 3-5 mutations
- **Minibatch test** — score candidates against historical session tasks
- **Pareto selection** — only keep mutations that **improve new tasks without harming old ones**
- **System-aware merge** — changes stay interface-compatible with session protocol and crystallization flow

### Sprint breakdown

| Sprint | Task |
|---|---|
| **W1** | Sandbox folder + git-pre-commit-hook + rollback script |
| **W2** | Confidence score for crystallization protocol |
| **W3-4** | SKILL distillation in `/11.11stop` (Level-1+2 gen) |
| **W5-6** | GEPA-style prompt mutator + minibatch tester (background cron) |
| **W7+** | Self-update tool integration — agent writes patches to sandbox, user-confirms before live |

## 7. Open research questions

1. **Meta-learning vs in-context learning** — STOP (Self-Taught Optimizer) targets "meta-meta" optimization. Open: deeper RL integration with in-context aggregation.
2. **Multi-agent self-improvement** — Mixture-of-Agents + game theory. Open problem: **skill compilation phase transition** — at some library size, skill-selection accuracy collapses.
3. **Fine-tuning + RAG for learning consolidation** — Self-RAG, self-distillation for continual learning without catastrophic forgetting.
4. **Safety** — **over 26% of community-developed agent skills contain vulnerabilities**. Future: formal verification + capability-based fine-grained permissions.
5. **Karpathy "compilation" / LLM-Wiki** — automating maintenance of growing skill libraries without performance degradation from information bloat.

## GEPA verified-live 2026-05-17

`gepa-ai/gepa==0.1.1` — pip-installable + smoke-test-green. Custom `GEPAAdapter` + reflection LLM (~810 LOC), smoke (8-sample gold-set): **baseline 0.541 → actionable 0.619 = +14.3% Pareto front**, $0 cost (claude-code parent + subagent pattern).

**Lesson for any 6+ month roadmap:** re-verify research-only entries every release cycle; what was "research-only" 4 months ago is `pip install` today.

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — "compilation" foundation
- [[11-wiki/Crystallization-protocol]] — manual knowledge propagation that this axis automates
- [[11-wiki/sv-01-memory-architecture]] — previous axis
