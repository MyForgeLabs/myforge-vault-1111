# MyForge Vault 11.11

> **8-tengelyű evolúciós módszer és working tooling egy személyes Obsidian-vault önfejlesztő tudásrendszerré alakítására.**
> Készítette: [MyForge Labs](mailto:11.11@myforgelabs.com). Augmented intelligence — NEM AGI, NEM hype. Magyar+angol dokumentáció, MIT.

[English version](./README.md) · [Roadmap](./07-Decisions/2026-05-12%20Superintelligent%20vault%20evolution%20roadmap.md) · [Cross-projekt synthesis](./06-Audits/2026-05-18%20vault-meta%20NotebookLM%20cross-projekt%20synthesis.md)

## Mi ez

A **MyForge Vault 11.11** (belső kódnév: SV — Superintelligent Vault) egy **8-tengelyű architektúra** + **35+ production-script** + **87+ evergreen wiki** + **28 ADR** ami egy klasszikus Obsidian-vault-ot **self-improving tudásrendszerré** alakít. Mérhető numerikus eredményekkel és nyílt forrású-publikálással egyértelmű scope-pal.

A **11.11** a névben két jelentést hordoz:
- 🏢 **MyForge Labs alapítási jel** — a `11.11@myforgelabs.com` email-cím a vault előtti
- 🔧 **Session-orchestration primitív** — minden workflow a `11.11*` CLI-családon (mint `11.11start`, `11.11stop`, `11.11crystallize`, `11.11worker`) — ez a "kötőszövet" ami a 8 tengelyt egy rendszerré teszi

A módszer kiindulópontja [Karpathy LLM-Wiki pattern](./11-wiki/Karpathy-LLM-Wiki-pattern.md)-je: a "raw input" (10-raw) → "desztillált tudás" (11-wiki) crystallization-workflow. A SV ezt evolúcióval bővíti 8 függetlenül fejleszthető tengellyel.

## 8 tengely

| # | Tengely | Cél | Konkrét eszközök |
|---|---|---|---|
| **B-1** | Crystallization automation | Session → wiki/MEMORY auto-propagáció | `11.11crystallize`, G-Eval prompt v0.3, threshold-ramp |
| **B-2** | Memory architecture | Lean ~5K context-load (vs 15-20K) | Memgraph CE 3.9.0 native vector + bge-m3 + RRF |
| **B-3** | Continuous evaluation | LLM-output quality-monitoring | G-Eval + NLI Layer 2.5 + Coherence Layer 2.6 cascade |
| **B-4** | Tool composition | Skill-pool discoverable | `vault-skill-search` 462 SKILL Memgraph native |
| **B-5** | NotebookLM cognitive layer | Cross-projekt synthesis | 63-source vault-meta NB + 3-query synthesis |
| **B-6** | Multi-agent orchestration | Worker + Critic + Summarizer | `11.11worker.sh` claude-code subprocess |
| **B-7** | World-model / knowledge graph | Typed entity-extraction | 8997 entity / 28.9% typed (Concept/Decision/Sprint/etc) |
| **B-8** | Recursive self-improvement | GEPA prompt-mutation | `gepa.optimize()` real loop, Pareto +14.3% |

## A 7 legfontosabb artifact (NotebookLM-recommended)

1. **[Subagent-fanout dispatcher](./11-wiki/claude-code-subagent-fanout.md)** — 174× párhuzamos LLM-task, $0 cost (Claude Code subscription)
2. **[load-session-context](./05-Memory/Skill-map.md)** — MemGPT-stílusú virtual context loader, 75% token-megtakarítás
3. **[vault-search-server](./06-Audits/2026-05-17%20vault-search-server%20systemd.md)** — Unix-socket daemon, 80× speedup (14s→165ms) + Memgraph 280× speedup
4. **[Bias-mitigated G-Eval](./11-wiki/g-eval-bias-mitigation-pattern.md)** — Claude-to-Claude self-enhancement debiasing, 96.7% kalibrációs egyezés
5. **[Smart-trigger NLI cascade](./11-wiki/smart-trigger-cost-pattern.md)** — gyors-baseline → drága-only-if-needed, 5-10× cost-savings
6. **[4-rétegű Safety-Gate](./11-wiki/multi-layer-safety-gate.md)** — ENV + script + git-hook + Critic review (RSI-guardrail)
7. **[Sprint Day-0 Skeleton-first](./11-wiki/sprint-day-0-skeleton-first.md)** — ~5× gyorsabb Week 1 implementáció

## Mérhető eredmények (2026-04-23 → 2026-05-18, 26 nap)

| Mutató | Érték |
|---|---|
| **Cost** | **$0** (Claude Code + NotebookLM subscription-keretben, NEM Anthropic-API) |
| Session-history | **76 closed session** indexelve, 73 frontmatter eval-mező |
| Knowledge-objects | **13890 fact** Memgraph-ban |
| Entity-graph | 8997 entity / 28.9% typed |
| Skill-pool | **462 SKILL.md** Memgraph native vector-index |
| Wiki | 87+ evergreen wiki |
| ADR | 28 Architecture Decision Record |
| Cross-projekt synthesis | 63-source NotebookLM + 3-query Q1+Q2+Q3 lefutott |
| Subagent-fanout iterations | 7 super-session (5 → 14 → 13 párh) |
| Memgraph vector-index speedup | **280× vs numpy-cosine** (sub-ms p95) |
| GEPA Pareto-improvement | **+14.3%** (baseline 0.541 → 0.619) |
| G-Eval bias-mitigation effect | conf 0.880 → 0.760 (-0.12) |

## Miben vagyunk MÁSOK (NEM verseny — kompozit)

| Funkció | Pocock/skills | obra/superpowers | tinyhumansai/openhuman | **MyForge Vault 11.11** |
|---|:---:|:---:|:---:|:---:|
| Skill-share | ✅ | ✅ | ✅ | ✅ + Memgraph vector |
| Cross-projekt synthesis | ❌ | ❌ | ❌ | ✅ NotebookLM 63 source |
| Auto-skill distillation | ❌ | ❌ | ❓ | ✅ vault-skill-distill |
| Persistent knowledge-graph | ❌ | ❌ | ❌ | ✅ Memgraph 8997 entity |
| LLM-eval cascade (3-layer) | ❌ | ❌ | ❓ | ✅ G-Eval+NLI+Coherence |
| RSI (GEPA Pareto) | ❌ | ❌ | ❌ | ✅ +14.3% verified |
| 8-axis ADR | ❌ | ❓ | ❓ | ✅ explicit per-axis |
| Multi-agent orchestration | ❌ | ❓ | ❌ | ✅ 11.11worker ÉLES |
| **11.11 session-orchestration** | ❌ | ❌ | ❌ | ✅ unique CLI-család |

## Quick start

```bash
# 1. Vault clone (ez a repo)
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

A teljes módszertan **architektúra-level reprodukálható** a [07-Decisions/](./07-Decisions/) ADR-ekkel + [11-wiki/](./11-wiki/) evergreen wiki-vel. Minden script idempotens, ENV-flag-gated, default-OFF safety pattern.

## Pozícionálás (transparent)

A MyForge Vault 11.11 **NEM** "Pocock-skills alternative" vagy "openhuman challenger". A módszer egy **8-tengelyű kompozit architektúra** mérhető eredményekkel, a MyForge Labs saját Obsidian-vault-ján használva, nyílt forráskóddal publikálva. Cél: ipari peer-feedback + bárki más reprodukálni tudja a saját vault-jában.

## Ki van mögötte

[**MyForge Labs**](mailto:11.11@myforgelabs.com) — kis magyar engineering-műhely ami agent-skill infrastruktúrát, multilingual webplatformokat és AI-augmented operatív tooling-ot épít. ~2026-02-26 alapítása óta a `11.11@myforgelabs.com` a céges essence.

## License

MIT — lásd [LICENSE](./LICENSE). Cherry-pick szabad, attribution-friendly.

## Kapcsolódó

- [Architecture decision records (28)](./07-Decisions/)
- [Evergreen wiki (87+)](./11-wiki/)
- [Cross-projekt synthesis audit](./06-Audits/2026-05-18%20vault-meta%20NotebookLM%20cross-projekt%20synthesis.md)
- [English README](./README.en.md)
