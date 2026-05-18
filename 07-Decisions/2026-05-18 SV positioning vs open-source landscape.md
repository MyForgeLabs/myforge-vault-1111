---
name: SV positioning vs open-source agent-skill landscape (2026-Q2)
type: decision
sprint: SV-meta
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/decision", "#project/sv", "positioning", "open-source", "strategic"]
status: 🟡 active
context-source: [[../06-Audits/2026-05-18 GitHub trending recurrence + top-10 ingest]]
---

# Superintelligent Vault — pozicionálás (2026-Q2)

## Háttér

A 2026-04-23 → 2026-05-18 időszak `github-trending` recurrence-elemzése azt mutatja: az **agent-skill / framework** kategória 17 repo / 80 megjelenéssel **legdominánsabb** a GitHub-trending-on. Ipari konszenzus: 2026-Q2-ben az AI-agent + skill-ecosystem szektorvezető. A vault-meta sprint (B-1..B-8) pontosan ezen frontier-on dolgozik.

**A kérdés NEM**: melyik repo "győz". **A kérdés**: hogyan pozícionáljuk a SV-rendszert úgy, hogy érték-add és láthatóság maximális legyen, miközben nem head-to-head-verseny.

## A 3 legrelevánsabb peer (recurring trending-en)

### 1. `mattpocock/skills` (12×, top recurrent)
- TypeScript-influencer publikus `.claude/` skill-directory
- **Pattern**: egy ember single-use personal skill-share
- **Strength**: ismert, jó branding
- **Weakness**: nincs cross-projekt orchestration, nincs auto-learning, nincs memory-architecture

### 2. `obra/superpowers` (7×, methodology framework)
- "Agentic skills framework + dev methodology"
- **Pattern**: top-down framework + opinionated structure
- **Strength**: clear methodology, jó docs
- **Weakness**: NEM self-improving, NEM cross-projekt synthesis, NEM perzisztens KO-DB

### 3. `tinyhumansai/openhuman` (7×, **DIREKT konkurens NAME-pattern**)
- "Your Personal AI super intelligence. Private, Simple and extremely powerful."
- **Pattern**: end-user-facing "AI superintelligence" branding
- **Strength**: marketing-language match, app-szerű distribution
- **Weakness**: closed-architecture (mit csinál belül NEM publik), single-user tooling

## Mit csinálunk MI MÁSKÉPP (KONKRÉT diff)

A vault-meta sprint **8-tengelyű evolúciós roadmap-je** kínál olyat amit a fenti 3 peer NEM:

| Funkció | Pocock | Superpowers | OpenHuman | **SV (mi)** |
|---|:---:|:---:|:---:|:---:|
| Skill-share | ✅ | ✅ | ✅ | ✅ + Memgraph vector-search |
| Cross-projekt synthesis | ❌ | ❌ | ❌ | ✅ B-5 NotebookLM 63 source |
| Auto-skill distillation | ❌ | ❌ | ❓ | ✅ B-4 `vault-skill-distill` |
| Persistent knowledge-graph | ❌ | ❌ | ❌ | ✅ B-7 Memgraph 8997 entity |
| Cascaded LLM-eval (G-Eval+NLI+Coherence) | ❌ | ❌ | ❓ | ✅ B-1 3-layer cascade |
| Recursive self-improvement (GEPA) | ❌ | ❌ | ❌ | ✅ B-8 verified-live Pareto +14.3% |
| **8-tengelyű roadmap** | ❌ | ❓ | ❓ | ✅ explicit ADR per axis |
| Open architecture (ADR-doku) | ❌ | ✅ | ❌ | ✅✅ (vault-szintű) |
| **Multi-agent orchestration** | ❌ | ❓ | ❌ | ✅ B-6 worker.sh ÉLES |
| 462 skill production-vector | ❌ (~50?) | ❓ | ❌ | ✅ Memgraph native vector |
| Crystallization auto-prop | ❌ | ❌ | ❌ | ✅ B-1 ramp-protocol |

A SV **uniquely 6 funkciót** kínál (Cross-projekt synthesis, Auto-distillation, KG, LLM-eval cascade, RSI Pareto, Crystallization).

## Pozicionálási decision

### NEM verseny — pozitív-sum

A SV-rendszer pozicionálása **NEM** "Pocock-skills alternative" vagy "openhuman challenger" — hanem:

> **"An open-source 8-axis methodology + working tooling for evolving a personal Obsidian-vault into a self-improving knowledge-system."**

A peer-repo-k mindegyike (Pocock/Superpowers/OpenHuman) **dominánsan single-axis** — mi 8-axis paradigm-ot kínálunk **production-ready scriptekkel + ADR-doku-val + verifikált metrikákkal**.

### Mi az "értékadás" amit kínálunk

1. **8-tengelyű kompozit architektúra ADR-szinten** (`07-Decisions/2026-05-12 *`)
2. **35+ production-script** ($0 cost claude-code subagent-fanout pattern)
3. **Mérhető numerikus eredmények** (G-Eval 96.7%, Memgraph 280× speedup, GEPA +14.3% Pareto, 28.9% typed entity)
4. **Cross-platform reuse** (`AGENTS.md` ↔ `~/.claude/CLAUDE.md` ↔ `~/.codex/AGENTS.md` ↔ `~/.gemini/GEMINI.md`)
5. **Karpathy LLM-Wiki pattern** mint kiinduló minta + saját evolúciója

## Open-source release decision (jelen ADR fő döntése)

🟢 **PUBLISH**: a SV-rendszer **mint open-source repo + publikus dokumentáció** release-elésre alkalmas. Konkrét lépések:

### Tartalmi scope

- ✅ `AGENTS.md` (jelenlegi shared agent-guideline) — public-ready, **ahogy van**
- ✅ `00-Meta/` (vault-szabályok, frontmatter-schema, glossary) — public-ready, generic
- ✅ `11-wiki/` (87+ evergreen wiki) — public-ready, **technical-knowledge**
- ✅ `07-Decisions/` (ADR-ek) — public-ready, **architecture-rationale**
- ⚠️ `02-Projects/` — **SCRUB** (ügyfél-specifikus, NEM publish)
- ⚠️ `08-Sessions/` — **SCRUB** + selective (ügyfél-tartalom NEM, vault-meta session-ek igen)
- ⚠️ `05-Memory/User.md` — **NEM publish** (user-pref private)
- ✅ `05-Memory/Infrastructure.md` — selective publish (host-pattern OK, IP-port NEM)
- ✅ `.vault-ko/`, `.vault-memory/`, `.vault-eval/`, `.vault-tools/`, `.vault-nb/`, `.vault-agents/`, `.vault-rsi/` skeleton-okkal mind public
- ✅ `/usr/local/bin/11.11*`, `vault-*` scriptek — public OS-tooling

### License decision

**MIT** — alacsony-friction, közmegegyezés a 2026 agent-skill ecosystem-ben (Pocock MIT, browserbase MIT, addyosmani MIT).

### Repo-struktúra (javasolt)

```
superintelligent-vault/
├── README.md                # 5-axis intro + Quick-start (HU + EN)
├── README.hu.md             # magyar verzió
├── README.en.md             # angol verzió (vagy default README.md)
├── LICENSE                  # MIT
├── AGENTS.md                # közös agent-guideline (Claude/Codex/Gemini)
├── docs/
│   ├── 8-axis-roadmap.md    # 07-Decisions/2026-05-12-evolution-roadmap szerinti
│   ├── crystallization.md   # 11-wiki/Crystallization-protocol
│   ├── memory-architecture.md
│   └── ...
├── wiki/                    # → 11-wiki/ kópia (filtered)
├── decisions/               # → 07-Decisions/ kópia (filtered)
├── scripts/                 # → /usr/local/bin/* + .vault-*/*.py
└── .github/
    ├── workflows/cron-trending.yml
    └── ISSUE_TEMPLATE/...
```

### Marketing decision (LOW-key, NEM hype)

- **NE használj** "AI superintelligence", "AGI", "consciousness" kifejezéseket — ezek hype-jelek, és pontosan az a réteg amit el akarunk kerülni (vs. openhuman)
- **HASZNÁLD**: "augmented intelligence", "self-improving knowledge-system", "personal Obsidian-vault evolution", "open methodology"
- **Honnan számítsd a top-10-be**: heti `github-trending` cron monitor, ha agent-skill kategóriában nem jelenünk meg ≥1× / hónap → változtatás kell

### Timing

- **Soft-launch**: 1-2 hét belül, ha a B-1 Aggressive ramp stabil + 10+ wiki publish-ready
- **Hard-launch**: blog-post + HN/Reddit submission, miután 3+ peer-feedback van (DM, issue)
- **Sustained**: heti commit-cadence (vault-autosave amúgy 10-perces commit)

## Risk-elemzés

| Risk | Mitigation |
|---|---|
| Ügyfél-tartalom-leak (foxxi/KGC szótár) | `02-Projects` + `08-Sessions` SCRUB-script + git-history-filter |
| "Versenytárs-kvalifikáció" elvárás | low-key marketing, ADR-driven, NEM hype |
| Fork-megj (kis MIT-projektek nyomás) | NEM fókusz, csak ha rendszerese feedback (Issue/PR) |
| Time-cost a maintenance-en | weekly cron + autosave, max 1-2h/hét |
| Failed launch (0 trending) | nem hiba — a használati érték önmagunknak megmarad |

## Acceptance criteria

A pozicionálás akkor sikeres, ha:

- ✅ Public repo + README HU+EN létezik (NEM kell external traction)
- ✅ A 11-wiki/ + 07-Decisions/ alapján bárki reprodukálni tudja a 8-tengelyű vault-architektúrát
- ✅ `github-trending`-en agent-skill kategóriában ≥1× felbukkanunk havonta (top-100 elég, NEM top-10)
- ✅ A SV-rendszer SAJÁT projektjeinkben mérhető idő-megtakarítást ad (lásd cross-projekt synthesis)

## Konkrét következő lépés

1. **`README.md` magyar + angol** — public landing-doku skeleton (ez a session Phase 9.5)
2. **`scripts/scrub-public.py`** — automatikus filter `02-Projects` + `08-Sessions` ügyfél-tartalomra (Week 6)
3. **GitHub repo create** (private először, public-ready státusz után public-flip)
4. **`.github/workflows/cron-trending.yml`** — heti GitHub-trending recurrence (a vault-cron mintát követve)

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — host project
- [[../06-Audits/2026-05-18 GitHub trending recurrence + top-10 ingest]] — context-source
- [[2026-05-12 Superintelligent vault evolution roadmap]] — 8-axis roadmap forrás
- [[../11-wiki/external-skill-cherry-pick]] — cherry-pick metodológia
- [[../11-wiki/Karpathy-LLM-Wiki-pattern]] — kiinduló minta
