# MyForge Vault 11.11

> **An open-source 8-axis methodology + working tooling for evolving a personal Obsidian-vault into a self-improving knowledge-system.**
> Made by [MyForge Labs](mailto:11.11@myforgelabs.com). Augmented intelligence — NOT AGI, NOT hype. Hungarian+English docs, MIT.

[Magyar verzió](./README.hu.md) · [Roadmap](./07-Decisions/2026-05-12%20Superintelligent%20vault%20evolution%20roadmap.md) · [Cross-project synthesis](./06-Audits/2026-05-18%20vault-meta%20NotebookLM%20cross-projekt%20synthesis.md)

## What is this

**MyForge Vault 11.11** (internal codename: SV) is an **8-axis architecture** + **35+ production scripts** + **87+ evergreen wiki pages** + **28 ADRs** that turns a classic Obsidian-vault into a **self-improving knowledge-system**. With measurable numeric results and clear open-source publishing scope.

The **11.11** in the name carries two meanings:
- 🏢 **MyForge Labs founding signal** — the company's `11.11@myforgelabs.com` email predates this vault
- 🔧 **Session-orchestration primitive** — every workflow runs through the `11.11*` CLI family (`11.11start`, `11.11stop`, `11.11note`, `11.11focus`, `11.11ls`, `11.11crystallize`, `11.11worker`) — the connective tissue that makes the 8 axes work as one system

The methodology starts from [Karpathy's LLM-Wiki pattern](./11-wiki/Karpathy-LLM-Wiki-pattern.md): the "raw input" (10-raw) → "distilled knowledge" (11-wiki) crystallization workflow. SV extends this through evolution along 8 independently developable axes.

## The 8 axes

| # | Axis | Goal | Concrete tooling |
|---|---|---|---|
| **B-1** | Crystallization automation | Session → wiki/MEMORY auto-propagation | `11.11crystallize`, G-Eval prompt v0.3, threshold-ramp |
| **B-2** | Memory architecture | Lean ~5K context-load (vs 15-20K) | Memgraph CE 3.9.0 native vector + bge-m3 + RRF |
| **B-3** | Continuous evaluation | LLM-output quality monitoring | G-Eval + NLI Layer 2.5 + Coherence Layer 2.6 cascade |
| **B-4** | Tool composition | Discoverable skill-pool | `vault-skill-search` 462 SKILL Memgraph native |
| **B-5** | NotebookLM cognitive layer | Cross-project synthesis | 63-source vault-meta NB + 3-query synthesis |
| **B-6** | Multi-agent orchestration | Worker + Critic + Summarizer | `11.11worker.sh` claude-code subprocess |
| **B-7** | World-model / knowledge graph | Typed entity-extraction | 8997 entities / 28.9% typed (Concept/Decision/Sprint/etc) |
| **B-8** | Recursive self-improvement | GEPA prompt mutation | `gepa.optimize()` real loop, Pareto +14.3% |

## The 7 most important artifacts (NotebookLM-recommended)

1. **[Subagent-fanout dispatcher](./11-wiki/claude-code-subagent-fanout.md)** — 174× parallel LLM-task, $0 cost (Claude Code subscription)
2. **[load-session-context](./05-Memory/Skill-map.md)** — MemGPT-style virtual context loader, 75% token savings
3. **[vault-search-server](./06-Audits/2026-05-17%20vault-search-server%20systemd.md)** — Unix-socket daemon, 80× speedup (14s→165ms) + Memgraph 280× speedup
4. **[Bias-mitigated G-Eval](./11-wiki/g-eval-bias-mitigation-pattern.md)** — Claude-to-Claude self-enhancement debiasing, 96.7% calibration agreement
5. **[Smart-trigger NLI cascade](./11-wiki/smart-trigger-cost-pattern.md)** — fast-baseline → expensive-only-if-needed, 5-10× cost-savings
6. **[4-layer Safety-Gate](./11-wiki/multi-layer-safety-gate.md)** — ENV + script + git-hook + Critic review (RSI guardrail)
7. **[Sprint Day-0 Skeleton-first](./11-wiki/sprint-day-0-skeleton-first.md)** — ~5× faster Week 1 implementation

## Measured results (2026-04-23 → 2026-05-18, 26 days)

| Metric | Value |
|---|---|
| **Cost** | **$0** (Claude Code + NotebookLM subscription, NOT Anthropic API) |
| Session history | **76 closed sessions** indexed, 73 frontmatter eval-fields |
| Knowledge objects | **13890 facts** in Memgraph |
| Entity graph | 8997 entities / 28.9% typed |
| Skill pool | **462 SKILL.md** Memgraph native vector-index |
| Wiki | 87+ evergreen wikis |
| ADR | 28 Architecture Decision Records |
| Cross-project synthesis | 63-source NotebookLM + 3-query Q1+Q2+Q3 executed |
| Subagent-fanout iterations | 7 super-sessions (5 → 14 → 13 parallel) |
| Memgraph vector-index speedup | **280× vs numpy-cosine** (sub-ms p95) |
| GEPA Pareto improvement | **+14.3%** (baseline 0.541 → 0.619) |
| G-Eval bias-mitigation effect | conf 0.880 → 0.760 (-0.12) |

## What's DIFFERENT (NOT competition — composite)

| Feature | Pocock/skills | obra/superpowers | tinyhumansai/openhuman | **MyForge Vault 11.11** |
|---|:---:|:---:|:---:|:---:|
| Skill share | ✅ | ✅ | ✅ | ✅ + Memgraph vector |
| Cross-project synthesis | ❌ | ❌ | ❌ | ✅ NotebookLM 63 source |
| Auto-skill distillation | ❌ | ❌ | ❓ | ✅ vault-skill-distill |
| Persistent knowledge-graph | ❌ | ❌ | ❌ | ✅ Memgraph 8997 entities |
| LLM-eval cascade (3-layer) | ❌ | ❌ | ❓ | ✅ G-Eval+NLI+Coherence |
| RSI (GEPA Pareto) | ❌ | ❌ | ❌ | ✅ +14.3% verified |
| 8-axis ADR | ❌ | ❓ | ❓ | ✅ explicit per-axis |
| Multi-agent orchestration | ❌ | ❓ | ❌ | ✅ 11.11worker LIVE |
| **11.11 session orchestration** | ❌ | ❌ | ❌ | ✅ unique CLI family |

## Quick start

```bash
# 1. Vault clone (this repo)
git clone https://github.com/<owner>/superintelligent-vault.git
cd superintelligent-vault

# 2. Memgraph CE (Docker)
docker run -d --name memgraph -p 7687:7687 memgraph/memgraph:latest

# 3. Python venv + bge-m3
python3 -m venv .notebooklm-venv
.notebooklm-venv/bin/pip install sentence-transformers transformers mgclient pymgclient

# 4. Embed vault
./scripts/vault-embed.py --backfill 11-wiki/

# 5. Search
./scripts/vault-search "G-Eval bias mitigation"
```

## Reproducibility

The full methodology is **architecture-level reproducible** through the [07-Decisions/](./07-Decisions/) ADRs + [11-wiki/](./11-wiki/) evergreen wikis. Every script is idempotent, ENV-flag-gated, default-OFF safety pattern.

## Positioning (transparent)

MyForge Vault 11.11 is **NOT** a "Pocock-skills alternative" or "openhuman challenger". The methodology is an **8-axis composite architecture with measurable results**, used on MyForge Labs' own Obsidian-vault, published as open source. Goal: industry peer feedback + anyone else reproduces it on their own vault.

## Who's behind it

[**MyForge Labs**](mailto:11.11@myforgelabs.com) — small Hungarian engineering shop building agent-skill infrastructure, multilingual web platforms, and AI-augmented operational tooling. Founded around 11.11.

## License

MIT — see [LICENSE](./LICENSE). Cherry-pick freely, attribution-friendly.

## Related

- [Architecture decision records (28)](./07-Decisions/)
- [Evergreen wikis (87+)](./11-wiki/)
- [Cross-project synthesis audit](./06-Audits/2026-05-18%20vault-meta%20NotebookLM%20cross-projekt%20synthesis.md)
- [Hungarian README](./README.hu.md)
