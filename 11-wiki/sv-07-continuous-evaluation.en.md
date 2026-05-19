---
name: SV-7 Continuous evaluation
type: wiki
tags: ["#type/wiki", "agi", "evaluation", "benchmark", "sv-research", "lang/en"]
created: 2026-05-12
updated: 2026-05-19
status: done
lang: en
translated_from: sv-07-continuous-evaluation.md
parent: [[11-wiki/superintelligent-vault-research]]
notebooklm: d6e26ab3-3053-4eb8-a000-b3f53b83ebee
---

# SV-7 — Continuous evaluation

The seventh axis of the 8-axis superintelligent-vault research. **Question:** how can every session/project receive automatic metrics — success, learning-extraction accuracy, stuck-detection — such that benchmark trends visualize the vault's and its agents' month-over-month improvement?

> **Status:** 7/7 questions answered. NotebookLM sources: 35 (SWE-bench, AgentBench, HELM, MT-Bench, GAIA, tau-bench, AgentInstruct, OpenHands, Inspect AI, Braintrust, DSPy, Anthropic, Hamel Husain + Eugene Yan eval-blogs, MLPerf, plus 2 add-research expansions).

## 1. Axis core

In the LLM-agent context, **continuous evaluation** is a comprehensive paradigm — **systematic, iterative, full-lifecycle measurement** of model and agent performance — from dev-sandbox through CI/CD automation to production monitoring. The **"continuous"** part means validation is not a one-time event but an endless loop: tests run instantly on prompt/code change, live trace-observation, iterative bug-fixing on synthetic + real data. The **"evaluation"** part means objective measurement of quality and reliability — deterministic unit tests, domain-expert review, or "LLM-as-a-judge" methods — to catch regressions and guarantee expected behaviour.

The paradigm connects directly to leading benchmark families:

- **SWE-bench** has the model solve real GitHub issues, requiring code understanding + editing + test-execution in iterative cycles;
- **AgentBench** measures reasoning and decision-making in interactive, multi-step environments where environment-feedback is essential;
- **HELM** (Stanford) is a continuously-expanding "living benchmark" updated with new scenarios;
- **Anthropic** embeds evaluation in the agent architecture via the **"evaluator-optimizer"** workflow: a second model critiques and improves the main agent's output in a feedback loop, plus developers test in dedicated sandboxes.

## 2. Canonical approaches (5 main benchmark families)

### SWE-bench (Jimenez et al. Princeton 2023; Verified 2024; Multimodal 2025)
- **What it measures:** LLM ability to solve real software-engineering problems (GitHub issue + codebase).
- **How:** Containerized Docker env; model generates a patch; the system reproducibly runs tests.
- **Novelty:** Goes beyond isolated code-generation — multi-function/class/file changes + environment interaction + extreme-long context.

### AgentBench (Liu et al. 2023)
- **What it measures:** LLM-as-Agent reasoning and decision-making.
- **How:** 8 different interactive environments, multi-dimensional framework; tests API-based and open models on environment-feedback response.
- **Novelty:** Showed dramatic gap between commercial and <70B open models; identified long-horizon reasoning, decision-making and instruction-following as the main failure modes.

### HELM — Holistic Evaluation of Language Models (Liang et al. Stanford 2022, living benchmark)
- **What it measures:** Holistic LM quality — alongside accuracy: calibration, robustness, fairness, bias, toxicity, efficiency.
- **How:** Multi-metric framework; 87.5% of the 7 main metrics measured across 16 base-scenarios + 26 targeted scenarios.
- **Novelty:** Standardized test-suite for open and closed models; explicit trade-off visibility (accuracy vs bias). **"Living benchmark"** continuously expanding.

### LLM-as-a-judge: MT-Bench and G-Eval (Zheng et al. 2023; Liu et al. 2023)
- **What it measures:** Quality of chat-assistant and NLG responses in open-ended, multi-turn dialogues — alignment with human preferences.
- **How:** A strong LLM (e.g. GPT-4) judges with chain-of-thought + form-filling logic, no pre-written human reference required.
- **Novelty:** Scalable and explainable approximation of human preference — 80%+ agreement with human inter-rater agreement. Outperforms BLEU/ROUGE-style classic metrics on creative/diverse tasks.

### WebArena (Zhou et al. CMU 2023)
- **What it measures:** Functional correctness of autonomous web-agents on real web tasks.
- **How:** Fully-functional websites (e-commerce, forum, dev, CMS) in reproducible interactive env; agents solve human-level tasks with maps and software-guidance.
- **Novelty:** Strictly realistic long-horizon everyday workflows. Massive gap: humans 78.24%, GPT-4 agent 14.41%.

## 3. Tech-stack options in 2026

Continuous evaluation currently covers **3 layers**, with 1-2 production-ready options each:

### Off-the-shelf SaaS platform — fast integration

| Tool | Scope | Trade-off |
|---|---|---|
| **Braintrust** | Full lifecycle: dev-iteration (Playground), CI/CD-eval per PR, online scoring (async production-log scoring) | SDK-integration, turn-key. License cost; scorers and prompts still need tuning |
| **Inspect AI** (UK AISI) | Python open-source — Datasets + Solvers + Scorers chained, `@task` decorator, CLI + VS Code-extension, agent-sandbox Docker/Kubernetes | Free, 200+ built-in benchmarks; runtime infra (Docker-env maintenance) on the team |

### Domain-specific LLM-as-a-judge — custom

| Tool | Scope | Trade-off |
|---|---|---|
| **Hamel Husain / Eugene Yan DIY pattern** | Custom data-viewer (Streamlit/FastHTML) on LangSmith traces; domain expert writes binary (Pass/Fail) + critique → few-shot judge prompt | Maximally tailored, rejects unreliable 1-5 scale. Low software cost, high human-time cost. Goal: 90%+ human-machine agreement |
| **DSPy** (Khattab et al. 2023) | Declarative self-improving pipeline; replaces fixed prompt-templates with modules, "compiler" optimizes a metric automatically | Steep learning curve, high refactor cost on existing project — in return: automated prompt-engineering |

### Foundation-model and infrastructure benchmark — standardized

| Tool | Scope | Trade-off |
|---|---|---|
| **HELM** | Static CLI: foundation-model testing on 42+ scenarios (accuracy, calibration, toxicity, bias) | Free, but compute-intensive. Doesn't measure app-specific business logic |
| **OpenHands eval suite** | Containerized env for code-writing/browsing agents — SWE-bench and WebArena direct integration | MIT-licensed, narrow scope (code + browsing). Robust Docker-env-run expensive cloud-compute |
| **MLPerf Inference (Datacenter)** | DevOps layer: latency, throughput, energy via standardized load generators | Expensive, complex hardware setup. Only system-architecture level, not agent-logic |

### Anthropic paradigm (separately highlighted)
Anthropic doesn't ship a dedicated "continuous-eval Foundry" product but recommends an **architectural pattern**: the "evaluator-optimizer" workflow — alongside the main agent, a second LLM critiques and improves in a feedback loop. Prefers code-based (exact match) or unambiguous rubric-based LLM-as-judge scoring. Higher runtime cost (extra LLM calls).

## 4. Recent breakthroughs 2024-2026

The pre-2024 static, exam-style QA was followed by a fundamental paradigm shift. Focus: real-time, dynamic, verified, and **uncontaminated** (secret) tests.

### Leaderboard-hardening — anti-contamination
- **SWE-bench Verified** (2024-08, OpenAI Preparedness + SWE-bench team): 500 human-validated GitHub issues unambiguously solvable. Filtered out noisy/ill-specified tasks.
- **SWE-bench Multimodal + private tests** (2025-01): test-split **fully secret**, training-leakage-bypass; evaluation on Modal cloud, strictly sandboxed Docker.

### Dynamic interaction and reliability
- **tau-bench** (2024): Tool-Agent-User interaction in real business context (retail). Key novelty: **pass^k metric** — measures whether the agent solves the task **consistently** across k attempts. Showed GPT-4o-level agents extremely inconsistent (under 25% pass^8 in retail).
- **GAIA** (late-2023, dominant in 2024): conceptually-simple human tasks where agents show huge gap (human 92% vs GPT-4-plugin 15%). Multi-modal + web-browsing + tool-use mix.

### Generative teaching — synthetic data
- **AgentInstruct** (Mitra et al. Microsoft 2024): agent-driven framework, automatically 25M diverse synthetic training pairs from raw sources. Not just evaluating but post-training via *generative teaching*: Mistral-7b → Orca-3 up to 54% improvement on reasoning benchmarks.

### LLM-as-judge evolution — from generic scoring to critique-shadowing
The 2023 G-Eval and MT-Bench proved 80% human-agreement, but 2024-25 industry practice **moved beyond** unreliable 1-5 scales:
- **Binary (Pass/Fail) decision + detailed critique** — Hamel Husain, Eugene Yan school.
- **Critique Shadowing** — domain expert (lawyer, doctor) "shadows" the machine's critiques, refining the prompt until ≥90% agreement. Eugene Yan's **AlignEval** tool helps exactly this.

> **Summary:** Pre-2024 static exam-style QA was replaced by containerized interactive sandbox-eval (OpenHands, SWE-bench) + synthetic data generation (AgentInstruct) + dynamic user-simulation (tau-bench) + strictly-calibrated LLM-judges.

## 5. Failure modes and limitations

Continuous evaluation is **not a silver bullet** — misapplied, it gives false security. 6 main failure modes:

### Goodhart's law and the "tools trap"
Hamel Husain warns: teams fall for dashboards and off-the-shelf metrics while ignoring real user failures. *"It's like optimizing website load time while the payment flow is broken — you get better at the wrong thing."* 1-5 scales are noisy, not actionable — binary Pass/Fail is optimal.

### LLM-as-judge biases
- **Self-favoritism:** G-Eval study showed LLM-judges biased toward text generated by themselves (or similar models).
- **Position + format bias:** Models deceived by answer-order or innocuous-looking format differences.
- **Insensitivity:** Per Eugene Yan, G-Eval often has low recall, missing fine-grained factual inconsistency.
- **Over-trust:** Humans over-trust AI self-evaluation (especially when GPT-4 grades itself).

### Criteria drift
The AI-dev paradox: eval criteria can't be defined perfectly upfront without seeing many outputs. As domain experts and users use the system more, new edge cases appear, redefining what's "good". Static benchmarks don't follow this.

### Lack of reproducibility
LLMs aren't deterministic — temperature + sampling adds continuous noise. tau-bench's pass^8 metric showed: GPT-4o-level agents under 25% reliability over 8 retail repeats.

### Contamination / leakage
Optimizing to public benchmarks (HumanEval, old SWE-bench) is a classic limitation — test data leaks into training corpus. Modern fix: secret test-split (SWE-bench Multimodal 2025) + dedicated closed eval-cloud (Modal).

### Cost & compute
- **Human:** domain-expert review most accurate but expensive and slow, unsustainable long-term.
- **Machine:** SWE-bench runs may need 120 GB disk + 16 GB RAM + 8 CPU per container. Plus long-horizon agent-trajectory hundreds of LLM calls.

> **What continuous eval does NOT solve:** Fundamentally-broken product/prompt architecture or unrealistic expectations ("chatbot solve everything"). Doesn't replace honest human iteration: the LLM judge alone creates no value — *"buying an expensive LLM-eval toolkit is often just a trick to finally get the team to actually look at their own data"* (Hamel Husain).

## 6. Implementation steps in the Peti-vault context

Vault setup:
- **240+ files**, Obsidian-Markdown
- **11.11 session protocol** — one file in `08-Sessions/<slug>.md`, mandatory `## Summary` / `## Learnings` / `## Next`
- **Weekly vault-health-audit** — `06-Audits/System_Health.md` cron-generated
- **280+ skills**, multi-agent setup (Claude/Codex/Gemini)
- **Auto-mode crystallization** on session-close — `## Propagation log`

The NotebookLM synthesis identifies a **3-level eval-pipeline** fitting this structure:

### What to measure

| Metric | Definition | Source |
|---|---|---|
| **Session-level success** | Binary Pass/Fail + critique (NOT 1-5 scale!) | LLM-judge on `## Summary` + `## Learnings` + `## Next` |
| **Learnings-extraction accuracy** | Two dimensions: (a) factual consistency — no hallucinated entries in `## Learnings`; (b) relevance — picked the most important things | NLI-based judge compares Learnings to raw trace |
| **Agent stuck-detection** | Deterministic: repeating tool-calls, context-window full, long no-result runs | Regex + counter on session trace |
| **Vault-coherence drift** | Whether new `## Learnings` and `## Summary` contradict earlier sessions or the 280 skill-rules | Semantic similarity + LLM-judge |

### Implementation sprints

#### Sprint 1 — Level 1 unit-test (deterministic parser)
Fast, cheap, code-based checks on every new `08-Sessions/` file.

**Script:** `scripts/eval_l1_parser.py`
- *Assert 1:* Contains `## Summary`, `## Learnings`, `## Next`
- *Assert 2 (stuck-detection):* Regex on raw trace — same tool/skill-call or error repeating ≥3× consecutively
- *Assert 3:* `## Learnings` bullet-count 0 < n < 20 (lower and upper sanity limit)

**Output:** `06-Audits/L1_Stuck_Alerts.csv` + `#review-needed` tag

#### Sprint 2 — Data viewer + human baseline
Before automating, build a minimal manual-review UI.

**Script:** `scripts/vault_trace_viewer.py` (Python Streamlit or FastHTML)
- One screen: current `08-Sessions/<slug>.md`, attached skills, system-context
- **Pass / Fail button + 1-2 sentence critique field**
- Weekly 10-20 sessions manual evaluation

**Output:** `06-Audits/Human_Ground_Truth.jsonl` — basis for LLM-judge training

#### Sprint 3 — LLM-as-judge "critique shadowing"
Once baseline (30-50 examples) exists, delegate to a strong LLM (GPT-4 / Claude Opus 4.7).

**Script:** `scripts/eval_l2_llm_judge.py` (async on freshly-`_archive/`d sessions)
- Judge prompt **few-shot**-loads best critiques from `Human_Ground_Truth.jsonl` (this is "critique shadowing")
- NLI logic: `## Learnings` (hypothesis) vs raw session log (premise) → factual-inconsistency flag
- **Goal:** 90%+ agreement with manual Pass/Fail — iterate judge prompt until reached

**Output:** new frontmatter on session files:
```yaml
eval_score: Pass
eval_critique: "Code well-written but ## Next section incomplete."
hallucination_flag: false
```

#### Sprint 4 — Metric aggregation into weekly audit
Extend the existing `vault-cleanup` cron.

**Output:** new `06-Audits/System_Health.md` sections:
- Weekly pass-rate trend (line-chart Mermaid)
- Top-5 failure patterns
- Hallucination-rate per agent (Claude/Codex/Gemini)
- Stuck-detection alerts for the last 7 days

### Baseline + target

- **Baseline:** Sprint 2's 30-50-element `Human_Ground_Truth.jsonl` — starting pass-rate + hallucination-rate
- **Alignment target:** LLM-judge ↔ human Pass/Fail **≥ 90%** agreement
- **System target (realistic):**
  - Pass-rate on routine tasks: **>80%**
  - Pass-rate on new/unknown problems: **>60%**
  - Hallucination-rate: **<10%**, ideally <5%

## 7. Further research

### Meta-evaluation — who validates the validators?
Shreya Shankar et al. *"Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences"* (2024) — formal treatment of **criteria drift**. No good tool currently for auto-validating validator quality, leading to over-trust. Mandatory reading for Phase B.

### Agent-trajectory eval — more than just outcome
- **MT-Bench-101** — fine-grained multi-turn dialogue eval
- **tau-bench pass^k metric** — consistency and reliability across the trajectory
- New question: how to penalize unnecessary steps (tool-call loops) and reward successful recovery from errors?

### Self-improving pipelines and RLHF-substitutes
- **DSPy** — automatic prompt + weight optimization on declarative graph
- **AgentInstruct** — generative teaching: strong agents generate synthetic training data for smaller models post-training. **Open question:** *model collapse* avoidance + extensive automated eval of synthetic data

### World-model-grounded and execution-based eval
- **WebArena** functional websites, **OpenHands + SWE-bench** Docker containers
- Expected research focus: standardized sandbox envs, automatic ground-truth (e.g. DB-state check in tau-bench), multi-modal (vision-based) browsing eval

### Living benchmarks and contamination
HELM-paradigm + new SWE-bench updates point toward **living benchmark** — private test set, continuous cloud-expansion (Modal). **Open question:** how to publish a benchmark without rapid obsolescence from contamination?

## Phase A+ expansion (2026-05-12 deep research)

After Phase A (78 sources), +4 deep-research rounds on NotebookLM (`d6e26ab3-3053-4eb8-a000-b3f53b83ebee`), source pool **78 → 395** (+317). Topics: SWE-bench Verified 2026 leaderboard, agentic eval-frameworks (Promptfoo / Braintrust / Langfuse), LLM-judge bias/calibration, Hamel Husain + AlignEval + Eugene Yan production patterns.

### 1. Which 3 architecture elements together deliver most value — and in what order?

Sources say **DON'T start with automation** — start with manually reviewing your own data. The biggest mistake of AI teams: not reading the raw logs (Hamel Husain). Order:

**Step 1 — Frictionless data viewer + Critique Shadowing baseline (Foundation).** Collect binary (Pass/Fail) decisions + detailed human critiques on `08-Sessions/` files, instead of 1-5 scale. **Tech-stack:** Braintrust (offline dataset + trace + manual-review UI) or custom lightweight Markdown viewer.

**Step 2 — LLM-Judge calibration + NLI fact-check (Automation).** Per Eugene Yan, **NLI (Natural Language Inference)** models work best for `## Learnings` hallucination-checking. **Tech-stack:** AlignEval (Eugene Yan tool — fast human-vs-machine alignment) + Claude Opus 4.6 or GPT-5.4 as judge.

**Step 3 — Agentic scaffold + semantic search (Scaling).** 2026's SWE-bench Pro/Verified lesson: model capability alone is insufficient, scaffold (harness, tool-use, context-retrieval) is **half** the score — same model can drop 22 points on weak scaffold. **Tech-stack:** WarpGrep (semantic AI-search subagent, parallel tool-calls, drastic token-cost reduction) + Braintrust Online Scoring.

**Order is mandatory** — if you start with L2-3, you get single-metric tunnel vision.

### 2. Production-ready vs academic stage

**Academic / static benchmarks** (good for model-selection, NOT vault-production):
- SWE-bench Verified — 2024 gold-standard, by 2026 **contaminated + saturated** (Claude Mythos Preview = 93.9% record). OpenAI publicly abandoned it. Industry moved to **SWE-bench Pro**.
- GAIA — General AI Assistants. Lesson: **scaffold-dependent** (Princeton HAL: Claude Opus 4 GAIA-score 57.6%-64.9% depending purely on framework).
- tau-bench — dynamic tool-agent-user, `pass^k` metric.
- AgentBench — 2023 classic, 8 interactive envs.
- HELM (Stanford) — 42 scenarios, static, NOT a CI/CD tool.

**Production-ready** (Agent-Vault CI/CD-suitable):
- Braintrust — full SaaS, CI/CD-integrated (offline eval) + Playground + **online scoring**.
- AlignEval (Eugene Yan) — production-ready answer to LLM-as-a-judge alignment.
- OpenHands (ex-OpenDevin) — MIT, **containerized Docker-sandbox** for code-agents + safe evaluation.
- Anthropic Evaluator-Optimizer workflow — no specific "Foundry" product, but official production architecture.

**Main 2026 conclusion:** *"The framework that wins your own benchmark is the framework you should ship."* Public-benchmark optimization is a trap. Vault-context winning combo: **Braintrust + AlignEval + OpenHands-sandbox**.

### 3. Cost-sensitive budget-tier cut strategy

LLM API + framework costs can be **40-60% of opex** in autonomous agent operations — bad eval architecture silently doubles costs.

**Tier 1 — $50/month (cost-optimized):**
- Keep: parser stuck-detection + cron-aggregation (deterministic, **$0 API**). Streamlit Pass/Fail manual review **mandatory**.
- Cut: benchmark feed entirely. LLM-judge NLI off the expensive models (Opus, GPT-5.5).
- NLI judge model: token-based BYOK only — "Nano" models (~$0.000006/call) or budget-frontier (DeepSeek V4-Flash $0.14/$0.28 per 1M; MiniMax M2.5 $0.30/$1.20 per 1M).

**Tier 2 — $200/month (balanced hybrid):**
- Keep: parser stuck-detection + cron-aggregation. **Benchmark feed integratable** here.
- Adjust: Streamlit Pass/Fail can be reduced, not eliminated. LLM-judge NLI stably in — **80/20 industry rule**: 60-80% of agent-traffic and eval on cheaper/open models, only the harder 20% escalates to top models.
- NLI judge model: "workhorse" = Gemini 3.1 Pro ($2/$12 per 1M) or Claude Sonnet 4.6 ($3/$15 per 1M) — near-Opus accuracy at **5× cost reduction**.

**Tier 3 — $500+/month (frontier / full automation):**
- Keep + extend: LLM-judge NLI fully blooms (deepest context-based logic tests). Cron + stuck-detection + dedicated online scoring + Braintrust "autoeval" + remote evals.
- Cut: drastic reduction of Streamlit Pass/Fail manual review.
- NLI judge model: Claude Opus 4.7 ($5/$25 per 1M) or GPT-5.5 ($5/$30 per 1M), 1M-token context guarantees full Vault-coherence eval.

**Vault application (Peti context, ~240 files, weekly audit):** **Tier 2 ($200/month) is the sweet spot** — Sonnet 4.6 judge + weekly review-rotation, monthly benchmark-feed.

### 4. Phase A+ → Phase B refinement

The 3 new deep syntheses **confirm and refine** Phase A action items:
- The `vault_trace_viewer.py` Streamlit (Phase B Sprint 2): worth trialing **Braintrust** first (free tier offline dataset + manual-review UI) — may skip custom Streamlit dev.
- The `eval_l2_llm_judge.py` (Phase B Sprint 3) prompt-pattern should be **explicit Critique Shadowing** — Hamel Husain few-shot example-injection from Step 1 baseline, not generic rubric.
- System_Health (Sprint 4) extended with **"Vault-coherence-drift"** metric via WarpGrep-style semantic scaffold.
- **Cost-tier decision** pulled forward to Sprint 1: start Tier 1 (DeepSeek V4-Flash), move to Tier 2 only if 30-day baseline review-burden unsustainable.
- **New TODO:** OpenHands Docker-sandbox evaluation for self-improving eval loops outside vault-context.

## Action items for this axis

- [ ] **Phase B Sprint 1:** `scripts/eval_l1_parser.py` + integration into `vault-cleanup` cron
- [ ] **Phase B Sprint 2:** `scripts/vault_trace_viewer.py` (Streamlit) + weekly 10-20 session manual Pass/Fail → `Human_Ground_Truth.jsonl` 30-50 elements
- [ ] **Phase B Sprint 3:** `scripts/eval_l2_llm_judge.py` critique-shadowing few-shot prompt + alignment-iteration ≥90%
- [ ] **Phase B Sprint 4:** `06-Audits/System_Health.md` extension with eval metrics
- [ ] [[00-Meta/Frontmatter-schema]] extension: `eval_score`, `eval_critique`, `hallucination_flag`
- [ ] Reading: Shankar et al. *"Who Validates the Validators?"*, Eugene Yan AlignEval + Yi Liu "Grading Notes"

## Related

- [[11-wiki/superintelligent-vault-research]] — master index
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — Phase A → Phase B transition
- [[11-wiki/sv-05-crystallization-automation]] — sibling axis, shared pipeline element
- [[11-wiki/Crystallization-protocol]] — the 11.11stop close protocol the eval pipeline measures
- [[06-Audits/System_Health]] — weekly audit, eval-output landing page

## Hungarian original

[[sv-07-continuous-evaluation]]
