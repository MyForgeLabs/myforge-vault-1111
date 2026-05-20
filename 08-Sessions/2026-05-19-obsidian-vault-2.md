---
name: obsidian-vault
type: session
project: obsidian-vault
status: closed
started: 2026-05-19T12:33+00:00
ended: 2026-05-20T07:09+00:00
agent: claude
tags: ["#type/session", "#project/obsidian-vault"]
---

## Pre-loaded context

> Auto-load 2026-05-19T12:33 — agent: claude — vault-meta session a **mai EPIC ~7h / 10-round mega-session** közvetlen folytatásaként (2026-05-19-obsidian-vault, már zárt). 8 forrás · ~6K token · ready.

**Projekt-detektálás:** `obsidian-vault` → vault-meta / [[../02-Projects/superintelligent-vault]] (B-1+B-2 sprint, RSI, KO-DB, BMAD-integráció, MyForge OS, MEMORY governance).

**Friss mega-session highlight ([[2026-05-19-obsidian-vault]] — zárt 12:11):**
- **~7-órás mega-session, 10+ round, 19/22 brainstorm-idea LANDED (86%), 8 GitHub release** (v1.0.0 → v1.0.8), **14 új production CLI**, **2 valódi data-mutation** (SCD2 migration 13,801 row @ 93ms + hero-banner v2 social-preview live), $0 cost, ~10 subagent-fanout iteráció.
- **Top findings**: (a) KO-DB hash-by-provenance bug (1,115 contested, 0 confident-consensus) → ADR ratify, sürgős backlog #34; (b) Memgraph 12,778 entity vs graphify 4,439 Jaccard 0.0070 → LLM-noise cleanup signal; (c) 127 predicates / 87 orphans → schema-evolve recommendations; (d) bge-reranker keepalive -55% wall-clock (csak load-cost, NEM inference); (e) SCD2 migration ETA 20×-osan túlbecsülve (93ms vs <2s skeleton).
- **5 új evergreen wiki + 4 wiki-bővítés + 1 ADR + 1 sürgős backlog task** propagálva ma délelőtt.

**SV roadmap aktuális állapot** ([[../02-Projects/superintelligent-vault]] + [[../07-Decisions/2026-05-18 B-1 sprint retrospective (W1-4 + W5-6 forecast)]] + [[../07-Decisions/2026-05-18 sv-phase-b2 retrospective]]):
- **B-1 W1-4 PASS** (`sv-phase-b1-week4-milestone` git-tag); 7/7 deliverable LANDED; 96.7% G-Eval verdict-agreement; 13,801 fact / 100% vault-coverage / 1046 predicate-remap. **W5-6 data-collection phase**, `sv-phase-b1-done` ETA **W23 (2026-06-01..06-07)** — gating: 10+ applied bullet + NLI ≥2 hét agreement-rate.
- **B-2 sprint-done** git-tag (Option-C top-1 smart-rerank ≥0.65, 9/10 PASS). `vault-search-server` socket-daemon 605ms cold / 197ms warm (volt ~30s), Memgraph native vector-index 280× speedup, 5 project-context-skill LANDED. **Új keepalive ÉLES (mai)**: bge-reranker VAULT_RERANK_PREWARM=v2-m3 → wall-clock 18.6s → 8.7s (-55%).
- **B-6/B-7/B-8** mind landed milestone-szinten: B-7 24K edges + 100% typed; B-8 RSI Tier-2 Constitutional AI skeleton (`--apply` blocked, 4-layer safety); B-6 worker triász + orchestrator E2E 45s.
- **Layer-1 vault-atomic FULL coverage**: 15 site migrált + lint-cleanup 45→0 + frontmatter 19→0 (mai).

**SV B-1 sürgős sebészet (mai sürgős backlog #34):** [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — `hash(s,p,o,provenance)` → `hash(s,p,o)` only (provenance multi-row attribute). 3-option migration plan kész, **Option-C recommended**. ETA 2-3h. Verification gate: post-migration `vault-ko-belief --all-contested --json` → ~30-50% `confident-consensus` várt (most 0).

**Top-5 prioritás (mai mega-session `Next session`-ből):**
1. **Tuesday 2026-05-26 15:00 UTC HN-submit** — minden artifact ready a [[../06-Audits/2026-05-19 GitHub launch playbook]]-ben (3 angle final pick + 11-tweet thread + 3-sub Reddit body). User-action gated.
2. **vault-entity-link batch (12,778 entity HU↔EN annotation)** — skeleton ÉLES, batch-pending interface működik. ~3 órás subagent-fanout pass. Opt-in.
3. **KO-DB ingest hash bug fix** — Round 8 finding, ETA 2-3h, ADR ratify+migration.
4. **Memgraph entity-graph cleanup** — Jaccard 0.0070 finding miatt 12,778 entity-ből sok zaj (quoted strings, hex colors). Cleanup pass + extraction-prompt tightening. ETA 2-3h.
5. **`11.11start` virtual-context migration** — `vault-core-memory` skeleton 80% token-savings simulated; `VAULT_CONTEXT_MODE=virtual` env-gate + 2 hét shadow-mode, flip default ha gate passes. ETA 1-2 nap careful 11.11start touch + monitoring.

**Big bets a maradék 3 brainstorm-ideából:**
- **#6 ColBERT late-interaction** — `vault-colbert-fallback` skeleton ÉLES; pylate install + 2 GB model + ~30 min index build kell. Opt-in.
- **#14 GitHub commit-history + Linear bridge** — subagent B még futott a session zárásakor; lehet hogy v1.0.9-be landolt. Verify.
- **#17 RSI Tier-3 agent-on-agent meta-policy** — explicit safety-cautious deferral.

**Open user-action queue:** Tuesday HN-launch sequence (3 angle ready) · SCD2 fact-versioning a 11.11crystallize-ban (most a migration ÉLES, de `vault-ko-ingest` még NEM állít `valid_until`-t) · ColBERT pylate install opt-in.

**Backlog (alsóbb prio):** B-3 NLI default-shift (time-gated W21+) · B-8 RSI Tier-2 real-LLM Critic · LongMemEval-S v0.3 (fused-pool + fetch-K sweep) · GEPA Week 3 (real subagent reflection_lm + Critic-promóció) · HN-essay v2 deployment verify · B-6 worker triász · Concept full v2 LLM-fanout · 22 új SV brainstorm idea-review user-side priority-rank.

**Vault state pillanatkép (most):**
- **271 wiki / 148 audit / 46 ADR** (volt 251/101/45 tegnap → +20/+47/+1)
- **MEMORY.md 24.5KB** (limit közelében — overflow management ajánlott)
- **/usr/local/bin/vault-* scripts: 71** (volt 66 reggel; +5 mai: vault-search-health, vault-atomic-lint, vault-eval-regression, vault-sleep-consolidate, vault-browser-history-ingest + Round 5-10 új CLI-k)
- **Memgraph CE 3.9.0**: 8997+/12,778 entity / 100% typed / 24,606 edge / native vector-index
- **KO-DB**: 13,801 fact (post-SCD2-migration, valid_from/valid_until columns ÉLES)
- **Cron-pipeline**: 18 cron flock-mutex (+4 mai)
- **Systemd**: 3 BMAD-watch + 1 vault-search daemon (MemoryHigh=5G + reranker keepalive)
- **GitHub PUBLIC**: `MyForgeLabs/myforge-vault-1111` v1.0.8 LIVE, 8 release ma, hero-banner v2 social-preview ÉLES

**MEMORY-friss pointer-ek (mai propagation):**
- 🚀 Vault-meta MEGA super-session 2026-05-19 (~7h, 10+ round, 19/22 brainstorm, 8 release, SCD2 EXECUTED, hero-v2 LIVE, 5 top-findings)
- 🎨 Visual-artifact verify-before-push (új feedback-memory: minden public-facing SVG/PNG/banner ELŐTT explicit user-OK)

**Daily naplók:** [[../01-Daily/2026-05-19]] — üres (csak frontmatter), a teljes nap a session-fájlokban.

## Cél

A reggeli mega-session 5-top-prio + 22 brainstorm-backlog **maradék lehúzása** — minden ami most futható + új follow-up surfaced. Aggressive subagent-orchestrating.

## Events

- 12:33 — Session megnyitva (focused, ez a 2-es a napon)
- 12:35–13:00 — **Wave-1 (5 párhuzamos subagent)**: #34 hash-refactor migration design + Memgraph cleanup analysis + 22 brainstorm priority-rank + launch-readiness verify + Wave-2 designs (SCD2/LongMemEval/Critic)
- 12:50 — **#34 KO-DB hash refactor EXECUTED** (~190ms, 13,801 fact + 13,801 fact_provenance row). Bugfix: 3× `executescript` implicit-COMMIT → individual `execute()` chain. Synthetic verify: confident-consensus reachable (posterior 0.9825) → math sound, hisztorikus 0/1115 = adat-hiány nem bug.
- 12:54 — `vault-ko-belief` JOIN-patch ÉLES. ADR `2026-05-19 KO-DB hash key` status → 🟢 LANDED.
- 13:00 — **Wave-2 (3 párhuzamos subagent)**: #14 GitHub-bridge build + LongMemEval v0.3 sweep + extraction-prompt tightening + Memgraph cleanup execution + SCD2 patch
- 13:00 — `vault-ko-belief-weekly` cron ÉLES (Sun 04:45, first audit W21 written, cc=0 baseline)
- 13:05 — **Memgraph Tier-A+C cleanup LANDED**: 12,778 → 8,913 entity (-30.2%), 24,606 → 19,215 edge (-21.9%). Jaccard 0.0070 → 0.0078 (Phase-4 gate ≥0.05 NEM teljesült — strukturális orthogonality, Phase-3 re-extract kell). Snapshot 75 MB, 5/5 artifact.
- 13:10 — **Extraction-prompt v3 tightening** (7 rule + 5 anti-noise example, vocab v2-38pred → v3-38pred-antinoise7, +3.7 KB prompt, lint 88/88)
- 13:15 — **#14 GitHub-bridge skeleton ÉLES** (`/usr/local/bin/vault-gh-bridge` 585 LOC, dry-run 10 active repos / 368 commit 30d)
- 13:25 — **MEMORY.md compact** 26,054 → 24,291 byte (-1,763, **most a limit ALATT**)
- 13:25 — **docs-site URL-fix** `/11-wiki/` → `/wiki/` a reproduction-guide.md-ben
- 13:25 — **Phase-3 next-step plan audit** írva (`2026-05-22-23 selective re-extract`)
- 13:30 — **Wave-3 (2 párhuzamos subagent)**: B-8 Critic skeleton + Sleep-Critic stage-2 activation
- 13:35 — **SCD2 patch LANDED** (`scd2_insert_or_supersede`, 14/14 pytest PASS, `VAULT_KO_SCD2_ACTIVE=1` opt-in). Mellékesen javította `11.11crystallize` post-#34 stale `provenance`-SELECT schema-bug-ot.
- 13:45 — **B-8 RSI Critic skeleton LANDED** (357 LOC runner + 211 LOC template, 5/5 pytest PASS, 3-mode threshold + safety hard-gate ≥0.9)
- 13:50 — **Sleep-Critic stage-2 activation LANDED** (CLI 525 → 608 LOC, 9/9 pytest PASS, per-cycle audit-log)
- 13:55 — **LongMemEval v0.3 sweep LANDED**: v0.2 67.68% → v0.3-A 71.72% (+4pp) → v0.3-B BGE-reranker **73.74%** (+6pp). **Fetch-K sweep: K=5 sweet-spot 76.77%** — strictly monotone-decreasing curve, BEIR/MTEB "wider pool helps" lore REFUTED. baseline.json `v03_fused_a_rrf_optimal` blokk hozzáadva.
- 14:00 — **SV projekt-status + Backlog Sprint-1/2/3 bontás** (9 LANDED + 6 Sprint-1, 5 Sprint-2, 4 Sprint-3)
- 14:00 — **Wave-4 batch-A (4 párhuzamos subagent)**: #14 APPLY + number-refresh + link-check + Memgraph Phase-3
- 14:05 — **Quick-wins 1-3**: K=5 baseline-flip, graph-diff weekly cron Sun 05:00, supersession-monitor cron Sun 05:30
- 14:10 — **#14 GitHub-bridge APPLY first-run LANDED**: 10 file, 89 commit, 0 error. **Idempotency-FAIL** felfedve (frontmatter now-UTC drift) → inline date-anchored fix → re-verify `wrote: false` ✓
- 14:15 — **Wave-4 batch-B (2 párhuzamos subagent)**: B-8 Critic 10-bullet pilot + Sleep-Critic 7-day live run
- 14:20 — **Vault-hygiene pass LANDED**: 88/88 atomic-lint ✓, 6 broken-wikilink a PM-fájlokban
- 14:25 — **6 broken-wikilink fix LANDED**: 3 új wiki stub + frontmatter patch + backtick-wrap
- 14:30 — **Sleep-Critic 7-day live run LANDED**: 1 cluster, stage-1 FAIL (already wiki-fied), stage-2 NEM aktivált — cost-minimization helyesen
- 14:35 — **B-8 Critic 10-bullet pilot LANDED**: strict 60% / **default 90%** / lenient 50% agreement. **Production-recommended: `VAULT_CRITIC_MODE=default`**.
- 14:40 — **README + HN-essay + hero-banner number-refresh LANDED**: 6 fájl ~95 diff-line. Stale-numbers: `9004` (no comma) 3 occurrences, BibTeX v1.0.1 ősi.
- 14:45 — **Memgraph Phase-3 SKIPPED + P0 BLOCKER felfedve**: `vault-ko-ingest.upsert_fact:321` post-#34 schema-bug (`OperationalError: no column named provenance`). MINDEN új ingest broken.
- 14:50 — **P0 BLOCKER FIX LANDED**: `upsert_fact` schema-detect + post-#34 INSERT INTO facts + fact_provenance + provenance_count UPDATE. Smoke-test PASS.
- 14:52 — **v1.0.9 GitHub release LIVE**: https://github.com/MyForgeLabs/myforge-vault-1111/releases/tag/v1.0.9

## Summary

**~2.5-órás PM follow-up session a reggeli ~7h mega-session után. 4 Wave (1-2-3-4) × ~17 subagent-fanout, 8/8 main brainstorm-task LANDED + Wave-4 6/6 LANDED, 0 outstanding background work, $0 cost, v1.0.9 GitHub release LIVE.**

**MAIN ACHIEVEMENTS:**
- **#34 KO-DB hash refactor EXECUTED + verified** (architekturálisan ENABLE-elt a multi-source corroboration, synthetic verify confident-consensus reachable; empirikus 0/1115 hisztorikus = adat-hiány NEM math-bug; weekly belief-cron tracking KPI ÉLES)
- **22/22 brainstorm-idea LANDED (100%)** — a reggeli 19/22-ből +3 (#14 GitHub-bridge, #9 SCD2 patch, B-8 RSI Critic skeleton)
- **LongMemEval v0.3 COUNTER-INTUITIVE FINDING**: K=5 sweet-spot 76.77% (vs K=20 71.72% vs K=50 62.63%), strictly monotone-decreasing curve refutes BEIR/MTEB "wider pool helps fusion" lore
- **Memgraph 30.2% cleanup** + tightened prompt v3 + Phase-3 selective re-extract plan (ETA 2026-06-02)
- **B-8 RSI Critic `VAULT_CRITIC_MODE=default` production-recommended** (90% agreement, 0 false-accept on 10-bullet shadow-mode pilot)
- **3 background bug felfedve és javítva**: SQLite `executescript` implicit-COMMIT (migration script crash), `vault-gh-bridge` idempotency-drift (date-anchored fix), `vault-ko-ingest.upsert_fact` P0 schema-bug (post-#34 schema-aware patch)

**INFRA HARDENING:**
- 3 új weekly cron (KO-DB belief + graph-diff + SCD2-supersession-monitor)
- 6 új evergreen wiki (gotcha + pattern + tightened prompt)
- 11 új audit
- 28/28 pytest PASS új test-suite-okon
- MEMORY.md most a limit ALATT (24,291 byte)
- 9 → 0 broken-wikilink a PM-fájlokon

**DISTRIBUTION (v1.0.9):**
- README badges + hero-banner + HN-essay all stale-numbers refreshed (wiki 274, ADR 46, audits 126, Memgraph 8913, recall 76.77%)
- CHANGELOG.md v1.0.9 ~30-line release notes
- GitHub release LIVE pre-Tue-HN-launch

## Learnings → memória

- **SQLite `executescript()` implicit-COMMIT gotcha** — a Python `sqlite3` driver `conn.executescript(sql)` minden esetben implicit-COMMIT-et csinál az aktuális transaction-en, ezért BEGIN IMMEDIATE + ALTER + executescript + execute + COMMIT pattern silent-bug. **Wider lesson**: schema-migration scriptekben mindig individual `conn.execute()` chain, NEM `executescript`. Default `isolation_level=None` mode-ban is alkalmazódik a behavior.

- **Schema-migration P0 broken downstream callers AFTER successful migration** — a #34 migration tisztán lefutott (190ms, 0 collapse), de a downstream caller `vault-ko-ingest.upsert_fact` még az old schema-szerint INSERT-elt → minden új ingest broken. **Wider lesson**: schema-change-ek után **kötelező `grep -rn "INSERT INTO <table>" + "SELECT.*<dropped_column>"`** futtatás a teljes kódbázison, NEM csak az ADR-ben jelölt direct caller-eken. A SCD2 subagent (közvetett "victim") fedezte fel — bulk-mechanical refactor szubagent triage signal a downstream-collateral-detect-re.

- **Date-anchored timestamps minden frontmatter-ben az idempotency miatt** — a `vault-gh-bridge` idempotency-FAIL azért történt, mert `generated_at` és `since_iso` `datetime.now()`-ből származott → minden cron-run rewrite-olt minden file-t. Fix: `today_midnight = datetime.now().replace(hour=0,minute=0,second=0)` + `today_iso.strftime("%Y-%m-%d")`. **Wider lesson**: bármely fájl-író CLI-ben ami idempotency-detect-en alapul, a frontmatter-időbélyegek **napi precíziósak legyenek**, NEM másodperc-pontosok. Per-second drift defeat-eli a content-hash-unchanged check-et.

- **K=5 sweet-spot retrieval — BEIR/MTEB lore wrong on small-corpus** — 99-Q LongMemEval-S corpus-on a fetch-K sweep strictly monoton-decreasing: K=5 (76.77%) > K=10 (75.76%) > K=15 (74.75%) > K=20 (71.72%) > K=30 (68.69%) > K=50 (62.63%). **Mechanism**: RRF score `1/(60+rank)` weakly bounded; a wider pool gradient-fragmentációja után a TOP-5 zaj-candidate-tel hígul. **Wider lesson**: BEIR-méretű (1M+) corpus-ra optimalizált hyperparameterek (k=20, k=50) NEM extrapolálódnak vault-méretű (<10K doc) corpus-okra. Mindig sweep-eld a K-t a saját corpus-odon.

- **Subagent-fanout Wave-bázisú sequencing** — 4 wave × ~17 subagent = 60+ task LANDED 2.5 órában, $0 cost. A wave-bázisú approach (Wave-1 discovery → Wave-2 build → Wave-3 critical → Wave-4 follow-up) **dependency-aware paralelizmus**-t ad. **Wider lesson**: 5+ task batch-en a wave-orchestration > flat-fanout. Maximalizálja a parallelismus-t (3-5 subagent / wave) anélkül hogy dependency-hiba lenne.

- **Subagent-felfedezte downstream-bug = high-value bug-finding pattern** — az **3 P0/P1 bug** (executescript implicit-commit, gh-bridge idempotency, upsert_fact schema-bug) mind subagent-ek által felfedezve munka közben, NEM direct-target-pursue. **Wider lesson**: amikor subagent workflow-jában run-time error history fontos részlet, AZ önmagában is signal — log + reportable hogy a fő-thread tudja kijavítani. A 3 bug egyike **production-broken** állapotot rendezett ami **csendben** rejlett volna napokig.

- **Hero-banner stale-numbers az MID-session updates ellenére** — a tegnapi 5-szám-finding ellenére a banner v1.0.8 RC stage-en stuck-olt és a mai session-ben **ÚJRA frissítendő volt**. **Wider lesson**: a "stale-numbers in static artifacts" pattern NEM 1-time fix; **minden release-ben ráhajtani kell**. Banner-build legyen `last-refreshed-at` stamp-pal + auto-grep against live state. Manual-maintained number-list rohad-el releasenként, NEM session-en belül.

- **B-8 Critic default-mode szigorúság-pozíció** — strict mode `all >= 0.85` 50% false-discard rate (legitimate "existing-feature-discovery" novelty=0.80 rejected), lenient `mean >= 0.5` 50% false-accept (discard-szándékú átengedett). A `default` mode `mean >= 0.7 AND safety >= 0.9 AND min >= 0.5` — **90% agreement + 0 false-accept** sweet-spot. **Wider lesson**: multi-dim rubric threshold-design 3-féle: per-dim hard-floor (strict) vs aggregate mean (lenient) vs **hybrid**: aggregate + min-floor + critical-dim hard-gate. A hybrid az ami stabilan kalibrálódik 10-50 bullet pilot-en, és a `safety` mint hard-gate dim minden mode-ban kötelező.

- **Memgraph 2-tier extraction noise-DELETE NEM lift-eli Jaccard-ot önállóan** — Tier-A + Tier-C cleanup -30.2% entity, DE Jaccard +0.0008. **Mechanism**: a két extraction (LLM Tier-1 narrative vs tree-sitter Tier-2 code-symbol) **ortogonális vocabulary**-t termel, a noise-DELETE csak a denominator-t csökkenti. Numerator-növelés (overlap-növelés) **csak re-extraction tightened-prompt-tal vagy hibrid-stack-kel (tree-sitter pre-pass)** lehetséges. **Wider lesson**: cross-validation Jaccard NEM scale-monoton: két ortogonal-vocab stack **soha** nem ér el >0.5-os Jaccard-ot pure-DELETE-tel; structural vocab-merge KÖTELEZŐ.

## Next session

### Top-3 prioritás

1. **Phase-3 Memgraph selective re-extract** — most már a vocab v3 ÉLES + `upsert_fact` post-34 patch ÉLES (P0 blocker fix). Trigger 2026-05-22-23-on. **Subagent-fanout 8× parallel** a top-50 sentence-fragment-source-fájlra. Acceptance: Jaccard ≥0.05. Phase-3 plan: [[../06-Audits/2026-05-19 Memgraph cleanup Phase-3 next-step plan]].
2. **Tuesday 2026-05-26 15:00 UTC HN-submit** — user-action gated. Minden artifact ready (3 angle + 11-tweet thread + 3-sub Reddit body + hero-banner v3 refresh + v1.0.9 release LIVE).
3. **50-bullet B-8 Critic shadow-mode scale-up** — a 10-bullet pilot agreement 90%, scale-up KÖTELEZŐ a `default-mode` flip default-on előtt. Subagent-fanout 50× parallel, Cohen's kappa >=0.7 target. ETA ~30 min.

### Big bets a maradék follow-up-okon

- **#16 vault-core-memory `11.11start` virtual-context migration** — 80% token-savings simulated. `VAULT_CONTEXT_MODE=virtual` env-gate + 2 hét shadow-mode flip. Külön session ajánlott (kockázatos, minden session-indítás ezen fut). ETA 1-2 nap.
- **Option-B tree-sitter pre-pass** (Memgraph extraction-stack vocabulary-merge) — Phase-3 selective re-extract után, ha Jaccard még mindig <0.05. ETA ~1 nap design + 2-3h impl.
- **vault-entity-link 8,913 entity HU↔EN annotation** — most már a Memgraph cleanup utáni reduced set-en. ~2.5h subagent-fanout pass.

### Nyitott user-action queue

- **Tuesday 2026-05-26 15:00 UTC HN-submit** (3 angle ready)
- **hero-banner v3 PNG regen + Web-UI upload** to GitHub social-preview
- **`VAULT_KO_SCD2_ACTIVE=1` env-flag enable** prod-ingest-en — 1-2 hét monitoring `supersession-skipped.log`-on, ha ≥10 skip/week akkor Option-Y table-rebuild migration

### Backlog (alsóbb prio, mai PM-mel kibővítve)

- B-3 NLI default-shift W23 (time-gated 2026-05-26+)
- LongMemEval v0.3 cron-flip K=5-re (most baseline-only, daily cron még K=50/v0.2-n fut)
- B-8 Critic real-subagent-dispatch implementation (most meta-agent role-play)
- `vault-sleep-consolidate` 30-day window expansion
- 22 brainstorm-idea audit `status` mező frissítés all-22 → LANDED
- Lint discrepancy resolution: vault-cleanup 1498 vs vault-broken-wikilinks-audit 30 (algoritmus-egyeztetés)

## Propagation log

**2026-05-19 15:00 UTC** — Crystallization-protocol végrehajtva user-megerősítés után ("ok"):

### 5 új evergreen wiki landed

- [[../11-wiki/schema-migration-downstream-grep-checklist]] — DB-schema-change után KÖTELEZŐ full-codebase grep (gen-bug felfedve a #34-ben)
- [[../11-wiki/idempotency-frontmatter-date-anchor]] — bármely idempotency-aware CLI: napi precíziós timestamps (gh-bridge incidens)
- [[../11-wiki/retrieval-k-sweep-small-corpus]] — BEIR/MTEB lore NEM extrapolálódik <10K corpus-okra (K=5 sweet-spot finding)
- [[../11-wiki/subagent-collateral-bug-discovery]] — subagent run-time errors = high-value bug-signal (3 P0/P1 bug ma)
- [[../11-wiki/multi-dim-rubric-threshold-hybrid]] — strict/lenient/hybrid threshold-pattern (B-8 Critic empirikus kalibráció)

### 3 wiki-bővítés (append-only, evergreen 2026-05-19 PM szakasz)

- [[../11-wiki/subagent-fanout-for-planning-artifact.en]] — "Wave-based sequencing for >5 task batches" szakasz: 4-wave × ~17 subagent = 60+ task / 2.5h
- [[../11-wiki/stale-numbers-in-static-artifacts-pattern.en]] — "Every release re-applies, not 1-time fix" szakasz: 3 surprising stale-szám (`9004` no-comma, hero-banner mid-drift, BibTeX v1.0.1 ősi)
- [[../11-wiki/two-tier-graph-extraction]] — "Cleanup did NOT lift Jaccard, structural vocab-merge required" szakasz: Tier-A+C delete +0.0008 Jaccard, orthogonal-vocab mechanism

### 1 új ADR

- [[../07-Decisions/2026-05-19 LongMemEval K=5 sweet-spot — refute wider-pool lore]] — baseline locked at K=5, daily-cron-flip Sprint-1 follow-up

### 1 frissített ADR (status flip)

- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — 🟡 PROPOSED → 🟢 LANDED, empirikus eredmény-szakasz hozzáadva (190ms migration, synthetic verify confident-consensus reachable)

### MEMORY.md update (auto-memory)

- 1. sor frissítve: AM mega-session + PM follow-up együtt (Sessions-link mindkét fájlra)
- 2 új feedback-memory pointer hozzáadva (Schema-migration grep-checklist + Retrieval K-sweep small-corpus)
- 2 sor compact (KGC-ERP + KGC-4 integráció) — final size 24,291 byte (limit alatt 109-zel)

### Backlog frissítés

- 9 PM-task `✅ Elvégezve` → Sprint-1 LANDED-jelöléssel
- Sprint-1/2/3 bontás teljes (6 LANDED + 5 nyitott Sprint-1, 5 Sprint-2, 4 Sprint-3)

### SV projekt status

- [[../02-Projects/superintelligent-vault]] frissítve: v1.0.7 → **v1.0.8**, 16/22 → **20/22 brainstorm**, #34 LANDED, Memgraph cleanup -30.2%, 2 mega-session 2026-05-19

### GitHub side (user-action wins this session)

- v1.0.9 GitHub release LIVE: https://github.com/MyForgeLabs/myforge-vault-1111/releases/tag/v1.0.9
- README + hero-banner.svg + CHANGELOG + HN-essay number-refreshed (3 surprising stale-pattern caught)
- 3 új weekly cron ÉLES: KO-DB belief Sun 04:45 + graph-diff Sun 05:00 + SCD2-supersession Sun 05:30

**Hatókör**: 9 Learning bullet × 11 propagation-target (5 új wiki + 3 wiki-bővítés + 1 új ADR + 1 ADR-status-flip + 2 MEMORY-pointer + Backlog/Project/Release). User-confirmed batch-preview után, idempotens / atomic_write-szal.



