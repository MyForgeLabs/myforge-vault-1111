---
name: SV-5 Crystallization automation
type: wiki
lang: en
translated_from: sv-05-crystallization-automation.md
tags: ["#type/wiki", "agi", "crystallization", "rlaif", "constitutional-ai", "self-rewarding", "sv-research"]
created: 2026-05-12
updated: 2026-05-19
status: done
parent: [[11-wiki/superintelligent-vault-research]]
---

# SV-5 — Crystallization automation

Fifth article of the 8-axis SV research. **Question:** how to automate the user-confirmation step of session close via confidence score — so high-confidence Learnings auto-propagate to Memory / Wiki / Decisions while vault integrity holds and human oversight stays controllable.

## 1. The axis core

**Crystallization automation** is the self-driven process where an LLM agent, in a knowledge vault context, **condenses experiences from active interactions, bug fixes, and environment exploration into compact reusable memory files and structured rules** — without the user manually recording them. The mechanism keeps valuable insights (successful build commands, architecture patterns, project conventions) available in a persistent knowledge layer across future sessions.

### Three principle pillars

| Principle | Source | Connection to crystallization |
|---|---|---|
| **Karpathy LLM-Wiki / Compilation** | Karpathy Software 3.0 lecture | Translates raw context and endless conversations into an **LLM-friendly "wiki" format** for efficient future reading |
| **Constitutional AI / RLAIF** | Bai et al. 2022, Anthropic Collective CAI 2024 | High-level principles + AI-feedback replace human labels. Adapted: the agent itself decides what's memorable |
| **Self-Rewarding LLM** | Yuan et al. 2024 | LLM **evaluates its own output** ("LLM-as-a-Judge") — becomes better at both generation and judgment |

### Knowledge crystallization vs fine-tuning

- **Classic fine-tuning:** modifies model **weights** on a static dataset. Slow, compute-heavy, risks catastrophic forgetting + "alignment tax". Knowledge gets "cemented".
- **Knowledge crystallization:** **doesn't modify weights**. Knowledge saved to text memory buffers, dynamic rules, or executable code libraries (Voyager). Model uses it via context window — fast, specific, no expensive retraining.

## 2. Canonical approaches

### Self-Rewarding LLM (Yuan 2024, Meta)
"LLM-as-a-Judge" prompt where the model scores its own outputs; iterative DPO with **self-generated rewards**. Continuous improvement without human feedback bottleneck.

### Constitutional AI / RLAIF (Anthropic)
A "constitution" of principles provides oversight. Model critiques and corrects its own answers per the constitution. RLAIF: another LLM provides the feedback. Human oversight moves to the **highest abstraction level** — write the constitution, not the labels.

### Reflexion (Shinn 2023)
Verbal reflection on past failures in an episodic memory buffer. **Pseudo-gradient**: model "fine-tunes" its next steps in its own words, no weight update.

### Karpathy LLM-Wiki / Compilation
Automatic analysis of codebases/environments translated into **LLM-friendly documentation** ("deep wiki"). An automated agent pre-digests raw file structure into context-fit knowledge.

### Confidence-threshold auto-propagation (architecture pattern)
Each Learning gets a **confidence score** (logprob, semantic consistency / SelfCheckGPT, or LLM-judge). Above threshold (e.g. 0.85): silent auto-propagation. Below: classic user-confirm batch preview.

## 3. Tech-stack 2026

### LLM-as-judge frameworks

| Tool | Tradeoff |
|---|---|
| **Anthropic Constitutional self-critique** | High setup cost, double-token, but **reliable** baseline |
| **G-Eval** (Liu 2023) | CoT + form-filling + logprob normalization; needs position/verbosity/self-enhancement bias mitigation |
| **OpenAI Evals / RAGAS** | External validation, dataset testing |

**Bias mitigation critical:** Self-enhancement bias (Claude gives itself 25% higher win-rate), Verbosity bias, Position bias.

### Confidence scoring

| Method | Setup | Cost | Reliability |
|---|---|---|---|
| **Logprob-based** | Low | Free | Sometimes overconfident |
| **Semantic consistency** (SelfCheckGPT) | Medium | High (N× tokens) | Very reliable for hallucination detection |
| **Ensemble agreement** | Med-High | High | Robust |

Combined approach: logprob first-pass + semantic-consistency for borderline cases.

### Auto knowledge-distillation pipelines

| Pattern | Notes |
|---|---|
| **Claude Code auto-memory** | Production-grade `MEMORY.md` + topic-files auto-update — direct model for vault crystallization |
| **MemGPT** | OS-style virtual memory; too complex for pure markdown vault |
| **Voyager skill library** | Code-skill specific |

### Git-hook + pre-commit validation

| Tool | Setup | Reliability |
|---|---|---|
| **Non-interactive Claude (`claude -p`)** | Medium | High (full review) |
| **Guardrails AI** | Medium (Pydantic schema) | Very high |
| **NeMo-Guardrails** | High (rule DSL) | Very high |

## 4. Breakthroughs 2024-2026

- **Self-Rewarding LLM (Yuan 2024)** — broke the human-feedback bottleneck. Self-generated rewards in iterative DPO.
- **Collective Constitutional AI (Anthropic 2024)** — ~1000 lay-person democratic vote to shape the "community constitution".
- **Reflexion + verbal RL** — trial-and-error learning without expensive weight updates; verbal reflections as **pseudo-gradients**.
- **Self-modifying code agents (Promptbreeder, Voyager)** — Promptbreeder mutates **mutation prompts**; Voyager builds executable code skill library.
- **Anthropic Claude Code memory pattern (2024-2026)** — production scale! Claude **auto-watches terminal sessions** and writes lessons to `.claude/projects/<repo>/memory/MEMORY.md` + topic-files without explicit instruction.

## 5. Failure modes

### (a) Hallucination amplification
Auto-crystallizing a wrong answer **becomes part of memory**. Claude Code calls this "kitchen sink" — failed attempts get summarized in, **cementing bad knowledge**.

### (b) Reward hacking + LLM-judge biases
- **Self-enhancement bias** — Claude gives its own outputs 25% higher win-rate
- **Verbosity bias** — model rewards **longer** answers
- **Position bias** — favors the **first** option

The model optimizes for these biases instead of objective correctness.

### (c) Confidence calibration absent
Karpathy: LLMs **lack a proper internal model of self-knowledge**. They over-react; in high-stakes decisions (10,000-line code changes) automation's overconfidence is critical risk.

### (d) Compound errors / model collapse
Over multiple sessions, `MEMORY.md` becomes over-specified. Long, contradictory rules → the model **ignores important instructions** (lost in noise).

### (e) Loss of human oversight
User often **doesn't see what enters the vault** — "I don't know what auto-memory saved" phenomenon. Karpathy: human-in-the-loop remains a mandatory bottleneck.

### (f) Privacy / cross-session leak
LLMs leak data. Auto-memory must be strictly **machine-local + git-repo-bound** (Claude Code pattern), not shared across cloud environments.

### Safeguards

| # | Defense | Source |
|---|---|---|
| 1 | **Strict verification:** "If you can't verify it, don't ship it" — tests, lints, screenshot-compare | Claude Code docs |
| 2 | **Autonomy slider + leash:** Karpathy — let AI off the leash in small verifiable steps | Karpathy |
| 3 | **Deterministic hooks + Guardrails:** NeMo-Guardrails, Guidance — syntactic/semantic validation before every change | Eugene Yan |
| 4 | **Aggressive memory management:** regular ruthless prune; `/memory` audit | Claude Code |
| 5 | **Classifier + sandboxing:** separate background classifier model + OS-level isolation | Self-Rewarding bias mitigation |

## 6. Implementation in a personal vault

### (1) Confidence-scoring per Learning bullet (LLM-as-a-Judge)

At session close, a background prompt evaluates each Learning with G-Eval-style CoT:

```
Bullet: "<text>"
Score: factuality, novelty, routing_fit, bias_check (0.0-1.0 each)
Output JSON: {bullet, target, rationale, confidence}
```

Final confidence is the harmonic mean of sub-scores (weakest dominates — safe estimate). SelfCheckGPT-style semantic consistency for the 0.70-0.85 borderline band.

### (2) Decision-tree routing — autonomy slider

```
Routing match (existing 11-step tree) →
JSON output (target, confidence) →
├── confidence ≥ THRESHOLD (default 0.85) → AUTO-PROPAGATE
│   ├── git commit pre-state ("auto-crystallization backup")
│   ├── append target file (Edit tool, scripted)
│   └── audit log entry
└── confidence < THRESHOLD → MANUAL BATCH PREVIEW
    └── user OK / edit / skip
```

### (3) Git-revert safeguard
- Auto `git commit -m "auto-crystallization pre-commit backup <session-slug>"`
- Pull-back: `git revert <hash>` or `/rewind <session-slug>`
- The 10-min vault-autosave cron strengthens this — every auto-prop hash-tracked and recoverable

### (4) Audit log — transparency

New file `00-Meta/auto-crystallization-audit.md` with timestamped entries (date, session, bullet, target, confidence, rationale). User reviews weekly; if something's off, `git revert` + rule update.

### (5) Hot-reload threshold tuning

`00-Meta/crystallization-config.yaml`:
```yaml
auto_threshold: 0.85
judge_model: claude-opus-4-7
bias_mitigation: true
shadow_mode: false
```

Per-target-folder override (ADR higher 0.95, Backlog lower 0.75).

### (6) Roadmap: baseline → 80% auto-rate in 4-6 weeks

| Week | Mode | Threshold | Goal |
|---|---|---|---|
| **1. Shadow** | 1.0 | 1.0 | Baseline: how often does judge match user OK? |
| **2-3. Conservative** | 0.95 | 0.95 | Safest items auto-prop |
| **4-5. Aggressive** | 0.85 | 0.85 | Prompt robust after Reflexion fixes |
| **6. Stable** | ~80% auto | 0.85 | Most knowledge crystallizes invisibly |

## 7. Open research

1. **Cross-session consolidation + semantic dedup** — Embedding-based dedup + contradiction-detection.
2. **Crystallization + fine-tuning hybrid** — When does prompt-memory deserve QLoRA weights?
3. **Multi-agent vault — conflict resolution** — When multiple parallel agents write a shared vault.
4. **Confidence calibration for LLM output** — Integrate Platt scaling, isotonic regression with generative confidence.
5. **Continuous eval on the vault** — Async background LLM-as-judge validation (Anthropic Foundry pattern).
6. **RLAIF / Self-Rewarding bias mitigation** — Prevent reward-hacking and self-enhancement when the model chooses what enters memory.

### Recommended next papers
- **SelfCheckGPT** — black-box hallucination detection
- **HELM** — Holistic Evaluation framework
- **G-Eval** — judge framework (CoT + logprob normalization)
- **InstructGPT** — "alignment tax" discussion

## Phase A+ takeaways

**3 architectural elements:**
1. **Knowledge Objects (KO)** — hash-addressed `(subject, predicate, object, provenance)` tuples in SQLite/Postgres. 100% fact-recall, 78.9% multi-hop. Constant low yearly cost (vs $2k-14k for context-only).
2. **Checkpointed self-reflection loop** — "Knows-but-violates" mitigation via reflection checkpoints every 2-4 rounds; `retrieve → generate → verify` workflow.
3. **"Verification-grade" KIP + Provenance layer** — exact source attribution, audit logs, near-miss logs, cryptographic evidence.

**Order:** KO database → MCP integration → reflection checkpoints + provenance.

**Universal cost lesson:** Cut classical in-context memory entirely. 1000 facts = $2,051/year; KO architecture = constant $56/year with 97-99% token savings.

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[11-wiki/Crystallization-protocol]] — **the existing semi-automated protocol** this automates
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — foundational principle
- [[11-wiki/sv-01-memory-architecture]] — companion axis (memory layer receiving crystallized knowledge)
