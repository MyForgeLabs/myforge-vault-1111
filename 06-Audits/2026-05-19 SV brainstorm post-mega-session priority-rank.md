---
name: 2026-05-19 SV brainstorm post-mega-session priority-rank
type: audit
status: planning
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "planning", "sprint-bontas"]
related:
  - "[[2026-05-19 SV new development ideas brainstorm]]"
  - "[[../08-Sessions/2026-05-19-obsidian-vault]]"
  - "[[../02-Projects/superintelligent-vault]]"
  - "[[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]]"
---

# SV brainstorm post-mega-session priority-rank

> **Kontextus:** 2026-05-19 mega-session 19/22 brainstorm-idea LANDED (86%) skeleton-szinten + 1 valódi data-mutation (SCD2 migration). Most a következő 3-réteg sprint-bontást kell megcsinálni: (a) mi futtatható az **idei héten** (Sprint-1), (b) **post-HN-launch** (Sprint-2), (c) **B-1 done + B-3 flip + ColBERT** ha kell (Sprint-3).
>
> **Forrás-aggregátor:** `06-Audits/2026-05-19 SV new development ideas brainstorm.md` (22 ötlet, 5 bucket, 11 source-cite) + `08-Sessions/2026-05-19-obsidian-vault.md` (358 sor, Round 1-10 + Propagation log).

---

## TL;DR

- **Sprint-1 (this week, 2026-05-19→05-26)**: 6 azonnali task — top: **#34 KO-DB hash refactor** (🔴 sürgős, 2-3h, blocking) + **HN-launch Tuesday** (user-action) + 3 skeleton-to-feature-complete prio (#5 sleep-consolidate real-LLM-Critic / #14 GitHub-bridge verify+ship / #11 entity-link batch).
- **Sprint-2 (next week, 2026-05-27→06-02)**: post-HN follow-up — viral-response readiness, contributors funnel, és skeleton-to-production a top-5 idea-CLI-on (RAGAS / Sleep / Vault-MCP / Browser-history / Triangulate).
- **Sprint-3 (~2026-06-03+)**: B-1 done git-tag W23, B-3 NLI default-flip, **#6 ColBERT** bekapcsolása **csak ha** retrieval-gap mérve, **#17 RSI Tier-3** csak Tier-2 real-LLM-Critic stabil után.

**Backlog-konszolidáció:** 6 task összevonható a Backlog 🔴 Sürgős és Vault-fejlesztések szekciókban (lásd 5. szekció).

---

## 1. ROI / Effort 2D matrix

### A) Maradék 3 nem-landolt brainstorm-idea

| # | Idea | Effort | Risk | ROI | State | Sprint |
|---|------|--------|------|-----|-------|--------|
| #6 | ColBERT late-interaction | M | mid | ⭐⭐⭐⭐ | skeleton ÉLES (`vault-colbert-fallback` 7KB), pylate+2GB model needed | **S3** (gap-mért-alapú) |
| #14 | GitHub commit-history bridge | L | low | ⭐⭐⭐ | **NEM landolt** (nincs `vault-gh-bridge`), session-záráskor agent még futott | **S1** (verify+ship) |
| #17 | RSI Tier-3 meta-policy | XL | high | ⭐⭐⭐⭐⭐ | deferred safety, Tier-2 stabilitás kell előbb | **S3+** (B-8 real-Critic után) |

### B) 19 landolt-de-skeleton-only — production-hardening priority-rank

Skeleton vs production-state matrix (skeleton = `dry-run` default + 1 use-case verifikálva; production = robusztus error-handling + dokumentáció + telepítés + monitoring + UX).

| # | CLI | Land state | Production-gap | Effort to harden | ROI of hardening | Sprint |
|---|-----|------------|----------------|------------------|------------------|--------|
| #1 | `vault-eval-regression` (RAGAS CI-gate) | **near-prod** — pytest 3/3 PASS, cron 02:45 daily | csak Recall@5, no Faithfulness/Precision | S (2-4h) | ⭐⭐⭐⭐⭐ | **S2** |
| #2 | `vault-explain` (retrieval-trace) | skeleton — Mermaid output | UI integration (mkdocs JS-injection), interactive | S-M | ⭐⭐⭐ | S3 |
| #3 | `vault-ko-decay` (predicate half-life) | skeleton — 38 predicate config | half-life-tuning per-predicate empirically | S | ⭐⭐⭐ | S2 |
| #4 | `vault-daily-rollup` (5-bullet) | skeleton — daily cron-able | template-aware merge (no duplicate-mention) | S | ⭐⭐⭐⭐ | **S1** quick-win |
| #5 | `vault-ko-anki` (1668 cloze cards) | skeleton — `.apkg` output | predicate-coverage tuning, .apkg deduplication | S | ⭐⭐ | S3 |
| #7 | `vault-entity-link` (HU↔EN annotation) | skeleton + audit only — 12 778 entity ID-listed | 3h subagent-fanout batch + Memgraph SET-pass | M | ⭐⭐⭐⭐ | **S1** (skeleton→batch) |
| #8 | `vault-entity-trace` (provenance) | skeleton — Cypher OK | mkdocs JS-injection hover-card UI | M | ⭐⭐⭐ | S3 |
| #9 | **Temporal-KG SCD2** | **PRODUCTION** — migráció EXECUTED 13 801 row, time-travel queries verified | `11.11crystallize` integration: új-conflict-on `valid_until` SET | S (1-2h) | ⭐⭐⭐⭐⭐ | **S1** |
| #10 | `vault-ko-schema-evolve` | skeleton + audit — 127 predicates listed, 87 orphans, top promote: prevents/fixes/defaults_to | 3-5 promote-decision + retro UPDATE | S-M | ⭐⭐⭐⭐ | **S1** |
| #11 | `vault-multi-hop` (HopRAG BFS) | skeleton — verified 1 query | benchmark-suite (5-10 multi-hop queries) | M | ⭐⭐⭐ | S2 |
| #12 | `vault-search-rewrite` (HyDE) | skeleton — +0.050 boost measured | trigger-tuning (when to rewrite), telepítés `vault-search`-be opt-in | S | ⭐⭐⭐ | S2 |
| #13 | `vault-browser-history-ingest` | skeleton + wiki — 0/0 smoke (no browser on sandbox) | real-Chrome SQLite teszt + NLI-filter calibration + Mac-dwell-time gather | L | ⭐⭐⭐⭐ | S2 |
| #15 | `vault-sleep-consolidate` | skeleton + 2-phase-pending — 60 session / 472 bullet / 1 SKIP | real-LLM-Critic (`VAULT_SLEEP_LLM_CRITIC=1`) production-flip + threshold-ramp | M | ⭐⭐⭐⭐⭐ | **S1** (skeleton→real-LLM) |
| #16 | `vault-core-memory` (Letta virtual-ctx) | skeleton — 996/2048 token budget, 80% savings simulated | `11.11start` touchpoint + 2-hét shadow-mode + flip | L | ⭐⭐⭐⭐⭐ | **S2** |
| #18 | `vault-graph-diff` (Jaccard) | **finding-only** — Jaccard 0.0070, 4439 vs 12 778 entity, LLM-noise signal | cleanup-action (extraction-prompt tighten + LLM-noise removal pass) | M | ⭐⭐⭐⭐ | **S1** |
| #19 | `vault-ko-triangulate` (NLI proxy) | skeleton — catches false-facts! | ingest-time-i hook integráció `vault-ko-ingest`-be | M | ⭐⭐⭐⭐ | S2 |
| #20 | `vault-mcp_server.py` | **near-prod** — 7 tools, smoke 7/7 PASS, .mcp.json wire-up done | Tailscale auth-layer, claude.ai web-UI testing, Codex/Gemini test | M | ⭐⭐⭐⭐ | **S2** |
| #21 | `vault-ko-belief` (Bayesian) | **finding-only** — 1115 contested, 0 confident-consensus → provenance-hash bug | **#34 hash-refactor BLOCKED erre** | M | ⭐⭐⭐⭐⭐ | **S1** (post #34) |
| #22 | `vault-nb-ingest` (NotebookLM-bridge) | skeleton — 6 reports detected | KO-DB extract-pass az 6 detected report-ra | S-M | ⭐⭐⭐ | S2 |

### C) 2D priority matrix (text-grid, ASCII)

```
                      Effort →
                  XS-S          M           L-XL
        ┌──────────────────────────────────────────────┐
ROI ⭐⭐⭐⭐⭐│ #9 SCD2-int   #15 sleep   #16 core-mem   │
        │ #1 RAGAS+     #21 belief* #17 RSI-T3     │
        │               #20 vault-MCP                │
        ├──────────────────────────────────────────────┤
ROI ⭐⭐⭐⭐│ #4 daily-roll #7 entity-l #13 browser-hist│
        │ #10 schema-ev #18 graph-d  #14 gh-bridge   │
        │               #19 triangu                 │
        ├──────────────────────────────────────────────┤
ROI ⭐⭐⭐ │ #3 decay      #2 explain                  │
        │ #12 HyDE      #8 ent-trace                 │
        │               #11 multi-hop                │
        │               #6 ColBERT                   │
        ├──────────────────────────────────────────────┤
ROI ⭐⭐  │ #5 anki                                    │
        └──────────────────────────────────────────────┘
                      ↑ blocked by #34 hash refactor
```

**Top-quadrant prio** (high-ROI × low-effort): **#9 SCD2-integration (S), #1 RAGAS expand (S), #4 daily-rollup, #10 schema-evolve, #21 belief post-#34**.

---

## 2. Sprint-bontás (3-réteg)

### Sprint-1 — This week (2026-05-19 → 2026-05-26)

**Tematika:** post-mega-session hardening + HN-launch-day prep + blocking-fix.

> [!warning] Kritikus blocker
> **#34 KO-DB hash refactor MOST.** Amíg `hash(s,p,o,provenance)` van, a Bayesian belief-update, a multi-source-corroboration és a triangulation mind dead. Egész S1 ettől függ.

**Main thread (most azonnal, 2-3h saved-up bandwidth):**

1. **#34 KO-DB ingest hash refactor** ([[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]]) — Option-C recommended. ETA 2-3h. Verification gate: `vault-ko-belief --all-contested --json` → ~30-50% `confident-consensus`. **Blocking** mindenre (#21 belief, #19 triangulate, multi-source confidence). 🔴 sürgős.
2. **#9 SCD2 integration `11.11crystallize`-ba** — most a migráció ÉLES, de a `vault-ko-ingest` még NEM állít `valid_until`-t a régi-conflict facts-en. ETA 1-2h. Closer the time-travel loop.
3. **#15 sleep-consolidate real-LLM-Critic flip** — most rule-gate-only. Aktiváld `VAULT_SLEEP_LLM_CRITIC=1` opt-in shadow-mode (audit-only, no apply). ETA ~1h env-config + 1 hét cron-figyelés. Threshold-tune Sprint-2-ben.

**Subagent-fanout (parallel, $0):**

4. **#14 GitHub commit-history bridge ship** — verify session-záráskor futó subagent state-ét; ha nem landolt, spawn-olj egy új general-purpose agent-et `gh-bridge.yaml` + per-projekt `git log --since=24h` parser-rel. ETA ~6 min subagent + 30 min main-thread integration. **Risk: low (read-only).**
5. **#10 schema-evolve top-3 promote** — `prevents` / `fixes` / `defaults_to` predicate-promote + retro UPDATE. ETA ~30 min. Skeleton + audit ÉLES, csak a SQL UPDATE-passing kell.
6. **#18 graph-diff cleanup action** — LLM-noise removal (quoted strings, hex colors) Memgraph `Entity` node-okról. Cypher `MATCH (e:Entity) WHERE e.name =~ '^[#"\\\\\'].*' DETACH DELETE e`. Audit-first, apply-later (gate). ETA ~2h.

**User-action:**

7. **Tuesday 2026-05-26 15:00 UTC HN-launch** — minden artifact ready (`06-Audits/2026-05-19 GitHub launch playbook.md` 3 angle + 11-tweet thread + 3 Reddit body). Only user can submit.

**Quick-wins (low-effort skeleton-hardening, fanout-friendly):**

8. **#4 daily-rollup deploy** — már skeleton ÉLES, daily cron 06:00 hozzáadás (most NINCS cron, csak CLI). ETA ~15 min.

**Sprint-1 exit-criteria:**
- #34 hash bug eliminated, post-migration ≥30% confident-consensus
- #9 SCD2 fact-versioning hot-path-on
- #15 sleep-consolidate real-Critic shadow-mode-ban
- #14 GitHub-bridge skeleton ship-elve (vagy explicit deferred)
- HN-submit happened (or explicit defer)

---

### Sprint-2 — Next week (2026-05-27 → 2026-06-02)

**Tematika:** post-HN response + skeleton-to-production push a top-5 idea-CLI-ra + B-1 W22 monitor.

**Viral-response readiness (HN-conditional):**

1. **If HN front-page (≥150 points):**
   - Ship-elhető top-3 demo: `vault-mcp` STDIO server (claude.ai web-UI integration showcase), `vault-search-rewrite` HyDE demo, sleep-consolidation example session.
   - PR-template + good-first-issue-label első hullám contributors-nek.
   - Star-history.com auto-update.
   - Twitter/X thread T+24h follow-up (with metrics: "1d after launch: X stars, Y forks").
2. **If HN flop (<50 points):**
   - Retry angle B (`06-Audits/2026-05-19 GitHub launch playbook.md` 3 angle ready) Lobsters → Reddit r/ObsidianMD.
   - SEO-pass: meta-descriptions, llms.txt verify, schema.org markup.
3. **If HN moderate (50-150 points):**
   - Targeted outreach: 3 newsletter-authors (Bens Bites, TLDR-AI), 1 Discord (Anthropic-community, Obsidian).

**Skeleton-to-production pushok (post-Sprint-1):**

4. **#16 `vault-core-memory` → `11.11start` migration** — `VAULT_CONTEXT_MODE=virtual` env-gate + per-session `--virtual` flag, 2-hét shadow-mode kezd. ETA 1-2 nap careful 11.11start touch + monitoring. **High-ROI** (80% token-savings simulated).
5. **#20 `vault-mcp` claude.ai web-UI integration** — Tailscale auth-layer + Codex/Gemini config-test. ETA 2-4h.
6. **#13 `vault-browser-history-ingest` real-Chrome test** — Mac-dwell-time data NEM elérhető szerverről, user-side teszt (Peti Chrome local SQLite-on). NLI-filter calibration 20-page random sample-en. ETA 3-4h cross-host.
7. **#19 `vault-ko-triangulate` ingest-time-hook** — `vault-ko-ingest` hookba, minden új triplet NLI-verdict-tel. ETA 2-3h. **post-#34 (Sprint-1)** dependency.
8. **#7 `vault-entity-link` batch** — 12 778 entity HU↔EN annotation, ~3h subagent-fanout-pass Memgraph SET-tel. Opt-in.

**B-1 sprint progress (time-gated):**

9. **B-1 W22 monitor** — `vault-crystallize-monitor --weeks 1 --json` weekly. Aggressive 0.85 ramp-decision data-collection (need 30+ applied bullet, revert-rate <5%).

**Sprint-2 exit-criteria:**
- Top-5 hardened (#16/#20/#13/#19/#7 production-ready vagy explicit-deferred)
- HN/Twitter response curve quantified
- B-1 W22 data: applied/total ratio + revert-count

---

### Sprint-3 — Week 3 (2026-06-03+)

**Tematika:** B-1 done git-tag, B-3 NLI flip, retrieval-gap-driven decision.

1. **B-1 W23 ramp-decision** — Aggressive 0.85 flip (if W22 gate passes) → `sv-phase-b1-done` git-tag + retrospective ADR `07-Decisions/2026-06-XX sv-phase-b1 retrospective.md`.
2. **B-3 NLI default-shift W23** — daemon-fix + 30-sample backfill W21 → W22 monitor re-read → W23 flip. **Time-gated**, NEM rohanható.
3. **#6 ColBERT bekapcsolás (conditional)** — **csak ha** retrieval-gap mérve (`vault-eval-regression`-ben + manual probe set < target). Pylate install + 2GB model + ~30 min index build. Az audit-skeleton már ÉLES, ha az időpont eljön minimal-effort.
4. **#8 entity-trace mkdocs UI** — hover-card injection. Provenance = trust pattern. ETA 4-6h frontend.
5. **#2 vault-explain UI integration** — mkdocs JS-injection. ETA 2-4h.
6. **#5 Anki .apkg dedup + first-export** — production-ready .apkg, weekly export. ETA 2-3h.
7. **#17 RSI Tier-3 design** — **csak ha** B-8 Tier-2 real-Critic stabil (~3-4 hét stable). Design-doc + GEPA-coupling-spec első, kód később. Cautious deferral.

**Sprint-3 exit-criteria:**
- `sv-phase-b1-done` git-tag
- B-3 NLI default flipped
- ColBERT decision (ship or defer based on retrieval-gap-mért)

---

## 3. Top-5 skeleton-to-production priority

A 19 landolt skeleton-ból a következő 5 a legmagasabb ROI a production-hardening-re. Multi-criteria pick: **user-facing impact × cross-feature unlock × maintenance-risk-reduction**.

### Top-5 hardening

1. **#9 Temporal-KG SCD2 integration** (S1) — már EXECUTED a migráció, de a hot-path (`11.11crystallize`) még nem állít `valid_until`-t. Bezárja a time-travel loop-ot, és ez a `#21 belief` + `#19 triangulate` post-#34-utáni real-value-jának előfeltétele. **ROI: ⭐⭐⭐⭐⭐, Effort: S.**
2. **#15 sleep-consolidate real-LLM-Critic flip** (S1→S2) — most rule-gate-only, a 2-phase-pending interface ÉLES. Aktiválás shadow-mode `VAULT_SLEEP_LLM_CRITIC=1`, threshold-ramp Sprint-2. Karpathy-pattern (REM-consolidation) production-érettsége, ami **autonóm wiki-bővítést** ad. **ROI: ⭐⭐⭐⭐⭐, Effort: M.**
3. **#16 `vault-core-memory` → `11.11start` migration** (S2) — 80% token-savings simulated, **minden agent-thread-en érződik**. Production-flip 2-hét shadow-mode-val. Cross-feature impact: minden `11.11*` script, minden 3 agent (Claude/Codex/Gemini). **ROI: ⭐⭐⭐⭐⭐, Effort: L.**
4. **#20 `vault-mcp` claude.ai web-UI** (S2) — most STDIO, smoke 7/7 PASS. Tailscale-auth + web-UI test → **a vault tudás mobilról és nem-CLI-felületről is hozzáférhető**. Distribution-impact (HN-bemutatható demo). **ROI: ⭐⭐⭐⭐, Effort: M.**
5. **#1 `vault-eval-regression` expansion** (S2) — most csak Recall@5. Bővítés Faithfulness + Context-Recall + Answer-Relevancy → teljes RAGAS-suite. CI-gate quality-floor → minden post-2026-05-19 retrieval-change automatikusan validált. **ROI: ⭐⭐⭐⭐⭐, Effort: S.**

### "Shovel-ready" — skeleton elég lehet permanens

Ezek "elég" skeleton-szinten, NEM kell tovább érlelni — vagy alacsony-priora future-feature, vagy "use-when-needed" tooling:

- **#2 vault-explain** — debug-tool, on-demand használat OK. Nem kell mkdocs-injection-re push-olni amíg nincs konkrét bug-debug-need.
- **#5 vault-ko-anki** — opt-in nice-to-have, user-pref-driven. Skeleton + heti cron már elég.
- **#6 ColBERT** — gap-driven decision. Skeleton önmagában értékes mint "ready-to-deploy if needed". NEM kell mostani investment.
- **#8 entity-trace** — UI-nice-to-have, NEM gating. CLI-only access most is OK.
- **#10 schema-evolve** — audit-only, kvázi-statikus. Heti vagy havi pass elég.
- **#18 graph-diff** — finding-only, Jaccard 0.0070 már megadta a signal-t. Csak akkor re-run ha Memgraph-extraction prompt változott.
- **#22 nb-ingest** — alacsony-volume (~6 report total), egy egyszeri batch elég.

---

## 4. Skeleton-to-production gap-typology

Kategorizálva, hogy a 14 skeleton-CLI **milyen gap-et** kell zárni production-szintre:

| Gap-típus | Érintett CLI-k | Default tipikus effort |
|-----------|----------------|------------------------|
| **Hook-integráció** (rule-only → ingest-time-hook) | #9 SCD2, #15 sleep, #19 triangulate, #16 core-memory | S-M |
| **Batch-pass execution** (audit-only → actual mutation) | #7 entity-link, #18 graph-diff, #10 schema-evolve | M (3-6h) |
| **UI-integráció** (CLI → mkdocs/web) | #2 explain, #8 entity-trace, #20 MCP-web | M-L |
| **Empirical-tuning** (skeleton-default → empirical threshold) | #3 decay-half-life, #12 HyDE-trigger, #1 RAGAS-suite | S |
| **Cross-host-testing** (sandbox-skeleton → real-environment) | #13 browser-history | L (cross-machine) |
| **Conditional-deploy** (gate-mért-alapú) | #6 ColBERT, #17 RSI-T3 | XL (when triggered) |

---

## 5. Backlog-konszolidációs javaslat

### Duplikáció / overlap-detect

A Backlog jelenleg ~6 SV-tagged item-et tartalmaz ami **átfed** a mega-session output-jával:

| Backlog-item | State | Javaslat |
|--------------|-------|----------|
| **#34 KO-DB hash key — drop provenance** | 🔴 ➕ 2026-05-19 | **Sprint-1 task #1** — már ott van a Backlog-on, S1-ben végrehajtandó. |
| **B-1 Week 1 — 3-modell benchmark** (Haiku/Sonnet/Qwen) | open | Még releváns? G-Eval Pass-recall 67.68% mérve, **scorer=claude-code subagent ÉLES** ($0), benchmark-célja most marginális. Javaslat: **defer S3+** vagy close as obsolete. |
| **B-1 Week 5-6 — Aggressive mode** | open | **S3 task** (W23 flip). Marad. |
| **B-2 Week 3 Day 5 — Acceptance gate** | open | **MÁR ZÁRT** — `sv-phase-b2-done` git-tag létezik (2026-05-18 session). Javaslat: **mark ✅**. |
| **B-2 Week 2 Day 4 — vault-search real impl** | open | **MÁR ZÁRT** — `vault-search-server` daemon ÉLES, smart-rerank ≥0.65, 9/10 PASS. Javaslat: **mark ✅**. |
| **B-2 Week 2 Day 3 — embedding-modell benchmark** | open | **Implicit zárt** — bge-m3 választás stabilizálódott, multilingual-coverage verified. Javaslat: **mark ✅ vagy defer S3+**. |
| **B-3 Week 2 Day 5 — Acceptance gate** | open | Maradék: 50+ humán-baseline. **S3 task** — NLI default-flip W23. Marad. |
| **B-3 Week 1 Day 3-5 — Critique-shadowing prompt + Streamlit UI** | open | Lower-priority, **S3+ vagy obsolete** (NLI Layer 2.5 alternatíva). |
| **B-4 Week 2-3 — Skill-embedding + MCP-server** | open | **#20 vault-MCP ÉLES**, ez **felülrótta** a B-4 W3 MCP-server taskot. Javaslat: **partial-merge**: B-4 W3 task close, helyette new task: "vault-MCP claude.ai web-UI + Tailscale auth" (S2). |
| **B-5 Week 2-3 — vault-nb-crystallize + heti commute-podcast** | open | Részben végrehajtva (3 podcast LANDED, 121MB→45MB re-encode). B-5 W3 cron még nincs. Defer S3 (low-pri). |
| **B-6 Week 1-3** — multi-agent E2E | open | **B-6 worker-triász + orchestrator E2E 45s** mégis landolt (2026-05-18 super-session). Javaslat: **mark ✅ Week 1**, W2-3 still open. |
| **B-8 PRECONDITION GATE + Week 1-3** | open | **Safety-gated**, S3+ tervezett. **#17 RSI Tier-3** itt csatlakozna mint W4+. |

### Új task-ok hozzáadása a Backlog-ba

Az S1+S2-ből 5 új task amit fel kell venni:

1. 🔴 **#9 SCD2 fact-versioning a `11.11crystallize`-ba** — `valid_until` SET old-conflict-on. ETA 1-2h.
2. 🔴 **#15 sleep-consolidate real-LLM-Critic shadow-flip** — `VAULT_SLEEP_LLM_CRITIC=1` opt-in shadow + cron-monitoring 1 hét.
3. 🟡 **#14 GitHub commit-history bridge ship** — verify subagent-state, ha nincs landolva, ship-eld.
4. 🟡 **#16 `vault-core-memory` → `11.11start` virtual-context migration** — S2 task, 2-hét shadow-mode.
5. 🟡 **#20 `vault-mcp` claude.ai web-UI + Tailscale auth** — S2 task, helyettesíti B-4 W3 MCP-task-ot.

### Closure / cleanup

3 task lezárandó-vagy-archive:

- **B-2 W3 D5 acceptance-gate** → ✅ (`sv-phase-b2-done` tag létezik)
- **B-2 W2 D4 vault-search real impl** → ✅ (daemon ÉLES)
- **B-2 W2 D3 embedding-benchmark** → ✅ vagy ➡️ defer-S3 (bge-m3 stabilized)

---

## 6. Risk-register

| Risk | Mitigation |
|------|------------|
| **#34 hash refactor delay** — 1115 contested pair sit waiting, Bayesian belief layer DEAD | S1-blocker, MAIN-THREAD-FIRST |
| **#15 sleep-consolidate LLM-noise** real-Critic false-promote → wiki-noise | shadow-flip-first, threshold-tune Sprint-2, revert-button ÉLES (`crystallize-revert`) |
| **#16 `11.11start` virtual-context regression** — context-eviction long-session-eken | 2-hét shadow-mode, opt-in env-gate, easy-rollback |
| **HN-launch flop** — single-shot exposure | 3-angle retry-tree ready (`launch-playbook.md`), Lobsters/Reddit fallback |
| **#6 ColBERT 2GB model + 30min index — wasted if gap-not-mért** | Conditional-S3 (gate-mért-alapú), NEM speculative install |
| **#17 RSI Tier-3 safety** — recursive self-mod risk | B-8 Tier-2 real-Critic stabilitás-előfeltétel (~3-4 hét stable), NEM rohanva |

---

## 7. Záró — Sprint-1 azonnali next-action

> [!todo] Most futtatható (saját bandwidth, no user-action needed)
> 1. **#34 KO-DB hash refactor** — Option-C migration plan végrehajtás. ADR-ben minden részlet kész.
> 2. **#9 SCD2 hook a `11.11crystallize`-ba** — 1-2h, conflict-on `valid_until` SET.
> 3. **#15 sleep-consolidate shadow-flip** — `VAULT_SLEEP_LLM_CRITIC=1` env + 1-hét cron-monitor.
> 4. **#10 schema-evolve top-3 promote** — `prevents`/`fixes`/`defaults_to` retro-UPDATE.
> 5. **#18 graph-diff LLM-noise cleanup** — Cypher DETACH DELETE pass (audit-first).
> 6. **#4 daily-rollup cron 06:00 add** — 15 min.
> 7. **Backlog cleanup** — 3 B-2 task close + 5 új task add.
>
> ETA összesen: ~6-9h main-thread work + 1-2 subagent-fanout pass + 1 user-action (HN-submit Tuesday).

---

## Kapcsolódó

- [[2026-05-19 SV new development ideas brainstorm]] — forrásdok (22 idea)
- [[../08-Sessions/2026-05-19-obsidian-vault]] — mega-session log
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — #34 ADR
- [[../02-Projects/superintelligent-vault]] — SV roadmap
- [[../04-Tasks/Backlog]] — task-tracking
- [[../06-Audits/2026-05-19 GitHub launch playbook]] — HN-launch action playbook
- [[../06-Audits/2026-05-19 mega-session summary]] — session-overview
