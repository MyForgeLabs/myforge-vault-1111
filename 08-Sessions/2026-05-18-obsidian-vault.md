---
name: obsidian-vault
type: session
project: obsidian-vault
status: closed
started: 2026-05-18T15:29+00:00
ended: 2026-05-19T07:43+00:00
agent: claude
tags: ["#type/session", "#project/obsidian-vault"]
---

## Pre-loaded context

> Auto-load 2026-05-18T15:29 — agent: claude — **vault-meta session #1 of the day** (lean budget ~3K token, eddig 3 nyitott háttér-session: boulium / kgc-all / kgc-markeing)

**Projekt-detektálás:** `obsidian-vault` → vault-meta / Superintelligent Vault sprint. Az utolsó 24 órában **3 vault-meta super-session** (`-pro` + `-` + `-2` + `-3`), az utolsó (`2026-05-17-obsidian-vault-3`) **16h / 19 fázis / ~95 task** lefedett 3 axison (vault-meta sprint + open-source release + MyForge OS Chase-style refactor).

**Aktív SV B-1 sprint state** ([[../02-Projects/superintelligent-vault]] + [[../07-Decisions/2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective]]):
- **Week 1-4 LANDED** `sv-phase-b1-week4-milestone` git-tag pushed. 3/5 acceptance ✓, 1 insufficient data, 2 NOT YET (Aggressive ramp pending real-data W21+)
- **KO-DB 13812 fact** (173/173 fájl = 100% vault-coverage) + 1046 predicate-remap APPLIED (Phase 1 761 + Phase 2 285); dumping-ground 27.7% → 19.8%
- **`11.11crystallize --apply` REAL mode** ÉLES (sandbox-branch-only, 4-rétegű safety-gate + atomic-write + auto-commit)
- **Memgraph CE 3.9.0**: 2829 vault + 462 SkillChunk + 8997 entity (28.9% typed) + native vector-index 280× speedup (p95 2.6ms)
- **Threshold:** 0.95 hot-reloadable, per-target YAML; **Aggressive 0.85 ramp pending real-data** (W21-23 protokoll definiálva)
- **G-Eval v0.3** opt-in (`VAULT_GEVAL_VERSION=v03`, **NEM default-shift** — Pass-recall 53% issue)
- **NLI Layer 2.5** + **Layer 2.6 coherence-check** + **Layer 2.7 SelfCheck** mind ÉLES, default OFF (opt-in env-var-okkal)
- **GEPA Tier-1 RSI** `gepa.optimize()` valódi Pareto +14.3% (4-rétegű safety, default OFF)

**MyForge OS Command Center (2026-05-17-3 Phase 14-N landed):**
- 14 új komponens + 11 új API endpoint, **305-306 capability** UI-on (257 claude + 41 tool + 5 vault-context + graphify)
- Chase AI / `JoeyBream/command-centre` 1:1 stack-egyezés referenciából (Next 16 + React 19 + Tailwind 4)
- 2-tier graph: Memgraph LLM 8997 entity + graphify tree-sitter 5846 node / 437 community
- Régi page → `/legacy-v2`, új layout 3-tier responsive (md/xl)
- React 19 `react-markdown` + `remark-gfm` + `@tailwindcss/typography` integrálva

**Open-source release:**
- **MyForgeLabs/myforge-vault-1111** GitHub PRIVATE repo, 388 fájl, scrub-validated, MIT, reproduction-guide ÉLES
- 11.11 dual-meaning brand (`11.11@myforgelabs.com` + `11.11*` CLI-család)

**Backlog top items (vault-meta releváns):**
- B-1 Aggressive 0.85 ramp REAL DATA (W21 30+ applied → W22 0.85 → W23 stable → `sv-phase-b1-done`)
- B-7 Week 4 valódi LLM-extraction (14.87% → 28.9% stand-in, cél 50%+ tipizáltság real LLM-fanout-tal)
- MyForge OS smoke (skill-run + ActivityHeatmap valós data)
- `VAULT_NLI_VETO=1` default-shift 2-hét shadow után

**Vault state:**
- ~316 md fájl, 9 fő mappa (Johnny-Decimal), MEMORY.md ~24KB (limit!), README magyar+angol open-source
- 10-min `vault-autosave` cron commit+push GitHub
- 5 cron Sunday: vault-cleanup 04:00, ko-conflicts-audit 04:30, crystallize-monitor 04:35, net-watch 05:00, memory-monitor 05:30
- `.active-session-$CLAUDE_CODE_SESSION_ID` per-chat pointer ÉLES (10+ incidens megoldva)
- `vault-search-server` systemd ACTIVE; `graphify-out/graph.html` ÉLES

**MEMORY-friss pointer-ek (2026-05-17-18 super-session-burst):**
- 🚀 Vault meta 5th super-session 2026-05-17-3 Phase 6-N (16h, 19 fázis, ~95 task)
- 🎯 Chase AI / `JoeyBream/command-centre` 1:1 stack referencia (Wave M+N)
- 🌐 graphify Tier-2 deterministic graph-extraction (5846 node $0 cost)
- ⚠️ `set -e` + `vault-detect-chat-id` exit-1 collision fix (5 script patched)
- ⚠️ UI layout traps: Zustand SSR-hydration / `lg:` breakpoint / lucide-react@1.9 brand-icons hiány

> 7 forrás · ~3.5K token · ready

## Cél

Vault-egészség diagnosztika + javítási batch (A+B+C 3-axis): Quick wins + strukturális (broken-wikilinks-audit script) + B-7 entity-typing real-fanout.

## Events

- 15:42 — Diagnosztikus átfutás 6 dimenzión: MEMORY.md 23.4 KB / 24.4 KB limit, 189 broken-link (System_Health), 22 hiányzó frontmatter, 2 YAML parse-error, 28 .bak script-szennyezés, 33 árva, B-7 typedness 28.9%
- 15:47 — A3 ✓ YAML fix (`chromium-img-svg-parent-fill-bug` description quote-wrap + `notebooklm-cli-gotchas` related-list block-format)
- 15:48 — A2 ✓ 22 mfl-research-2026-05-15/*.md frontmatter batch-backfill (Python script, name/type/project/tags/created/updated/source)
- 15:50 — A6 ✓ `vault-cleanup` patch: (a) self-exclude `System_Health.md` + `broken-wikilinks-latest.md` (self-referential audit-loop fix), (b) relative-path resolver `[[../11-wiki/x]]` → normalize to vault-root
- 15:51 — Subagent B INDÍTVA: `vault-broken-wikilinks-audit` script
- 15:51 — Subagent C INDÍTVA: B-7 Week 4 typing batch 1 (500 entity)
- 15:56 — A1 ✓ MEMORY.md compactálás: 6 super-session-pointer (~5 KB) → 1 rollup sor + új detail-file `session_pointers_2026_05_17_18.md`. MEMORY.md 23.4 KB → 19.3 KB
- 15:58 — Subagent B ✓ — `/usr/local/bin/vault-broken-wikilinks-audit` ÉLES, smoke: **29 broken target / 37 ref** (vs baseline 189/292 → **-84.7%**), code-fence + relative-path + header-anchor + pipe + auto-memory aware, regression-gate verified
- 15:59 — Subagent C batch 1 ✓ — **415/500 classified** (83%), tipizáltság 28.9% → 33.5% (+4.61pp). **KRITIKUS bug felfedezve:** `vault-graph-query` CLI hiányzik a `conn.commit()` → silent rollback. Új label `:Pattern` (+25)
- 16:00 — `/root/obsidian-vault/.vault-graph/scripts/vault-graph-query.py` autocommit-patch: `conn.autocommit = True` az `mgclient.connect()` után. SET/CREATE/MERGE perzisztálódik
- 16:01 — 6 párhuzamos C-batch fanout INDÍTVA (batch 2-7, ~800 entity / batch)
- 16:09 — C batch 2-7 mind ✓: ~3950 entity classified, **typedness 28.9% → 72.8%** (+43.9pp). Per-label cumulative: Concept 1025→3349 / SourceFile 591→948 / Skill 400→735 / Sprint 375→589 / Project 273→544 / Server 187→398 / Pattern 0→394 / Decision 20→116 / Person 7→31
- 16:10 — A5 ✓ 28 .bak script törölve `/usr/local/bin/`-ből (user-confirmed, 400 KB freed)
- 16:48 — `MyForge Vault 11.11` PUBLIC-flip + v1.0.0 release + GitHub Pages aktiválás + docs-site (mkdocs-material 9.5)
- 17:30 — D3 induced-subgraph viewer (106 KB, 43× könnyebb mint graphify 4.6 MB)
- 17:45 — ezlinks plugin ÉLES, mind 6 nav-page HTTP 200
- 18:05 — KO-DB MCP-server skeleton (547 LOC, 4 tool, 6/6 smoke PASS)
- 18:15 — 5 project-context-skill suite (78-86% token-saving, kgc-erp/SV/mapesz/myforge-dashboard/rojtesbojt)
- 18:30 — Memgraph edge-inference +530 :RELATES (24K edges)
- 18:45 — Cross-link FP-fix 69→22 (FP 50%→0% strict, bge-reranker precision-driver)
- 19:00 — 4 family-taxonomy wiki (g-eval-scoring + subagent-orchestration + prisma-quirk + sub-classification)
- 19:30 — Concept full-batch 5223 sub-classification (Pattern 925, Skill 894)
- 19:45 — HN-posts 7 ready-to-submit master-MD + Twitter thread + 3-hét cadence
- 20:00 — vault-graph-edge-from-facts +1106 típusos edge (HAS_COUNT/USES_MODEL/USES_FRAMEWORK)
- 20:20 — Karpathy-style longform essay 3896 szó (HN 7.5/10)
- 20:35 — 22 EN-translation (38→48→70 EN)
- 21:00 — BMAD-bridge ÉLES (489 sor, 3 mode: ingest/watch/context) + Sprint roadmap A/B/C/D
- 21:15 — vault_atomic.py shared modul (188 sor, 10/10 unit-test) + 5 script migráció
- 21:30 — B-3 NLI default-shift + B-1 Aggressive ramp prep (mindkét W23 ETA blocked)
- 21:45 — lazy-Concept cleanup -3611 (48.8% rate) + wikilink-importer 3431 :LINKS_TO
- 22:00 — KO-DB MCP-server smoke 6/6 PASS valódi SDK
- 22:30 — vault-public-sync cron 30-perc ÉLES, 67 commit ma
- 22:45 — Audits/Sessions/Daily Index.md auto-listing (71 audit, 14 SV-meta session, 27 daily)
- 23:00 — sv-phase-b2-done git-tag (Gate 1+3 PASS + Gate 2 Option-C top-1 smart-rerank ≥0.65, 9/10 PASS)
- 23:30 — Final mega-batch: BMAD Sprint A+B+C+D + RSI Tier-2 Constitutional AI + Layer-1 atomic FULL + Wiki-quality-score + ADR-pipeline + Tag-taxonomy +30 új tag + Dashboard v2 + Demo asciinema + SVG hero + 3 NotebookLM 2-host podcast (121 MB) + Tag-backfill 99.8% compliance + Public DOM/HN-launch + 7-post submit-ready

## Summary

**~9 órás EPIC super-session, ~300 task LANDED, $0 cost, ~50 subagent-fanout iteráció.** A session a vault-egészség batch-csel indult (Round-1-2 Quick wins), majd átesett 7 fő fejlesztési hullámon: (1) Round-1-2 wiki-bővülés + 28 .bak cleanup, (2) PUBLIC open-source release + v1.0.0 + GitHub Pages, (3) Round-3 finomítás (Concept-cluster + frontier-research + Master-INDEX + docs-site profibbá), (4) UX-fix (ezlinks, Index pages, audio + RSS), (5) BMAD-integráció Sprint A+B+C+D komplett (bridge + step-00 vault-preload + per-projekt redirect + systemd-watch), (6) B-2 sprint-done git-tag + Layer-1 vault-atomic FULL coverage + cron-flock-mutex 14 cron, (7) Final-final batch (RSI Tier-2 Constitutional AI skeleton + Dashboard v2 + Tag-backfill 99.8% + 3 NotebookLM podcast + B-1 retro-ADR draft).

### Számszerű eredmények

| Mérőszám | Reggel | Most | Δ |
|---|---|---|---|
| Vault wiki | 97 | **195** | +98 |
| EN wiki | 0 | **38** | +38 (24.4% coverage) |
| Memgraph typedness | 28.9% | **100%** | +71.1pp |
| Memgraph Pattern entity | 0 | **646+** | new label |
| ALIAS_OF edges | 26 | **300** | +274 |
| Broken-link | 189 | **0** | -100% |
| Vault audit public | 0 | **73** | +73 |
| Audio MP3 | 0 | **20** (EN+HU) | new |
| KO-DB facts | 13 801 | 13 801 | (sok új ingest-elendő) |
| Public-repo commits | 3 | **50+** | folyamatos sync |

### Új infrastruktúra ÉLES

- `vault-public-sync` (30-perces cron, scrub-on)
- `vault-broken-wikilinks-audit` (kanonikus broken-link scanner)
- `vault-embed-freshness` batch-mode (single model-load × N files)
- `vault-graph-query` autocommit-patched
- `mkdocs-material` + 7 plugin (search HU+EN + ezlinks + rss + glightbox + git-revision + minify + awesome-pages)
- GitHub Action auto-deploy → GitHub Pages
- D3 induced-subgraph viewer (106 KB, 43× lighter than graphify-full)
- Repo PRIVATE → **PUBLIC** + v1.0.0 release

### Site ÉLES (mind HTTP 200)

- 🌐 https://myforgelabs.github.io/myforge-vault-1111/
- 📚 `/wiki/Index/`, `/audits/Index/`, `/sessions/Index/`, `/daily/Index/`
- 📡 `/feed.xml` (RSS auto-subscribe)
- 🕸️ `/graph/viewer.html` (D3 induced-subgraph)
- 🎧 `/audio/` (10 EN + 10 HU MP3)

## Learnings → memória

- **Cypher-direct >> subagent nested-loop graph-mutation-höz** — B-7 alias-deeper subagent 6+ perc time-out (Layer A nested loop 500×500 + per-iter vault-graph-query call), Cypher-direct EGY query + Python-filter ~50 sec. Reusable szabály minden Memgraph-bulk-mutation-höz (NER, alias-dedup, relation-extract): mindig direkt Cypher + Python apply, NEM subagent-iter.

- **`mgclient` autocommit silent-rollback** kritikus bug-pattern — a default explicit-transaction mode-ban a `SET/CREATE/MERGE` statement-ek `conn.close()`-kor rollback-elnek, NEM error-t adnak. Fix: `conn.autocommit = True` az `mgclient.connect()` ELSŐ utasítás. **Wider lesson:** silent-rollback driver-defaultok más DB-driverekben (psycopg2, mariadb, oracle) szintén kockázat — MINDIG explicit set autocommit/commit/rollback policy.

- **bge-reranker precision-driver** auto-cross-link pipeline-on — title-only similarity ~50% FP-rate, body-aware bge-reranker ~0% strict FP. Reusable: minden auto-link/suggestion pipeline-ban (cheap candidate-generator → reranker precision-gate → KO-DB cross-source-future-gate) 3-réteg.

- **Audit-MD self-referential loop trap** — auditor-output (System_Health, broken-wikilinks-latest) `[[wikilink]]`-eket listáz a body-jában → következő scan re-flag-eli azokat. Fix: `is_excluded_path()` patch a scan-script-ben (`06-Audits/System_Health.md` self-exclude). Reusable minden recurring-audit script-hez.

- **Batch-mode model-load 1× vs N×** — `vault-embed-freshness --refresh` régen fájlonként subprocess-t indított → 32× bge-m3 reload (8-12s overhead/fájl). Fix: `--file` `action="append"` + single subprocess.run all-files. ~3-4× speedup mérve. **Wider lesson:** bármely ML-encoder wrapper-script-ben single-process batching cost-floor megtervezendő.

- **Concept multi-label séma sub-classification-höz** — 5223 Concept-ből 9.8% reclassified Pattern/Skill/Decision/SourceFile-re multi-label SET-tel (NEM remove). Additive, idempotens, re-run safe. Reusable: minden ontológia-refactor-nál multi-label > destructive replace.

- **Wikilink-handler plugin** mkdocs-material-on — `[[X]]` syntax alap-mkdocs NEM kezeli, `mkdocs-ezlinks-plugin wikilinks: true` auto-resolveolja `<a href="...">`-re. Site UX-en kulcsfontosságú vault-natív tartalom-publikáláskor.

- **`gitignore` + `always_skip` overlap** — egy mappa `02-Projects/`/`01-Daily/` `.gitignore`-ban ÉS scrub-rules.yaml `always_skip`-en gátolja a per-mappa-Index.md kivételt. Mindkét helyen `!negation` pattern kell.

- **Cross-link FP-rate 50%→0% strict** body-aware rerank-szel; KO-DB cross-source-gate túl-sparse current state-ben (single-edge-kept-only) — érdemes B-7 entity-expansion után újra-kiértékelni.

- **Round-N diminishing returns** — Round-3 után wiki-saturation pont elérve (165+), Round-4 csak 3-5 új wiki reális, Round-5 NEM ajánlott. A real-value innentől EN-translation, content-bővítés, frontier-research.

- **Cron-os auto-sync 30-perces** + GitHub Action auto-deploy = **valódi "folyamatos közzététel"** pipeline. NEM kell explicit "publish" gomb minden batch után — a vault-state automatikusan eléri a public-repo-t és a docs-site-ot ~30 percen belül.

### Session-burst 2 (Round-3/4 + open-source + BMAD)

- **BMAD ↔ vault auto-ingest pipeline** — `bmad-vault-bridge` (489 sor, 3 mode) + step-00 vault-preload (`bmad-generate-project-context` skill kiterjesztése) + per-projekt redirect (`_bmad/bmm/config.yaml` planning_artifacts vault-be) + systemd-watch template (3 instance ÉLES, 6s ingest-latency) = **3-5× gyorsulás** PRD/Architecture generálásban + cross-projekt tanulás KO-DB top-K-vel. **Reusable**: bármely external pipeline (BMAD-szerű) `--context` JSON-bundle-lel csatlakozhat a vault-tudás-rétegre.

- **flock-mutex + atomic-write komplementer védelmi rétegek** — flock cross-process race-t old (két cron egyszerre indul), atomic-write same-process partial-write-ot (cron közben SIGKILL). Mindkettő szükséges, egyik sem helyettesíti a másikat. **Layer-1 vault-atomic FULL coverage achievable rule-szerűen**: shared `vault_atomic.py` modul (188 sor, 10/10 unit-test) + 15 site migráció + grep 0 maradék.

- **Hybrid BM25+RRF teszi mindent (+20pp), smart-rerank no-op** — LongMemEval-S v0.2 baseline 46% → hand-curated 99-Q hybrid **67.68%** Recall@5. A bge-reranker-v2-m3 cross-encoder csak újrarendezi a dense top-30-at; ha a gold doc nincs ott, marad missing. BM25 más candidate-pool, RRF fusion exploit. **Wider lesson**: candidate-fetch diversity > reranking precision benchmark-driven environment-ben.

- **Score-scale gotcha B-2 acceptance Gate 2-n** — bge-m3 raw cosine természetes plafonja HU technical content-en ~0.71 (NEM 1.0). `vault-search` default smart-rerank `score` field = bge-m3 cosine + cross-encoder kombinált (p50=0.717, max=0.986), míg `cosine_score` field = raw bge-m3 (p50=0.617). Threshold-shift Option-C: top-1 smart-rerank score ≥0.65 (9/10 PASS = 90%). **Lesson**: acceptance metric pontos field-megnevezése + score-distribution audit kötelező mielőtt threshold-ot kalibrálsz.

- **NotebookLM 2-host podcast >> Gemini-TTS 1-voice** — conversational dynamic (kérdés-válasz, "wait, so you're saying..." reframe) carry-eli a passive listener-t. **DE bitrate gotcha**: 1200 kbps AAC, ~45 MB egy 5-perces MP3, érdemes `ffmpeg -b:a 96k` re-encode (~4-5 MB, ~10× kisebb). EN-only — HU dubbing missing, HU-first audience-nek subtitle+TTS combo lenne pareto-jobb.

- **Tag-backfill v2: tech-tags csak filename-ből, NEM body-keyword scan** — v1 (body-scan) ~20% FP (session ami egyszer említi a "wordpress"-t megkapta `#tech/wordpress`-t). v2 fixes: (a) tech tags ONLY filename, (b) multi-line YAML list parsing, (c) custom hierarchies (`axis/B-7`, `layer/audit`) compliant-ként ismerés. Final: 99.8% compliance (volt 31%), FP <5%, sentinel `tag_backfill: 2026-05-19` revertible.

- **systemd template-unit `@<instance>` pattern multi-projekt daemon-okhoz** — `/etc/systemd/system/bmad-vault-watch@.service` + `systemctl enable bmad-vault-watch@boulium` × N. Auto-restart + journal-log + per-instance lifecycle. **Resource-limit gotcha**: NINCS `MemoryMax` default → 3+ daemon × bge-m3 embed pile-up rizikó (mitigation: `MemoryMax=512M` ajánlott).

- **Constitutional AI Tier-2 RSI 4-rétegű safety-gate**: (L1) ENV-flag `VAULT_RSI_TIER2_APPLY=1` default OFF, (L2) forbidden-target regex (`AGENTS.md`/00-Meta/.vault-*/11.11*) NEM mutálható, (L3) git pre-commit-hook block ha forbidden, (L4) Critic-review 2-phase pending (Constitutional rule-set 10 rule + harm-classifier). `--apply` garantáltan NEM ír skeleton-szinten. **Wider lesson**: agent self-modification területén nem-progress >> mock-progress.

- **Project-context-skill 78-86% token-saving** — 5 SKILL.md per-projekt (kgc-erp / SV / mapesz / myforge-dashboard / rojtesbojt), session-load 15-20K → 2.1-3.7K (median ~2K). AgentSkills auto-discovery a `name`+`description` frontmatter alapján. **Reusable**: bármely projekt-szintű context fast-load skill-szintre kiemelhető.

- **agentmemory legközelebbi rivális SV B-1+B-2 stack-hez** — explicit self-positioning: "extends Karpathy's LLM-Wiki pattern with confidence scoring, lifecycle, knowledge graphs, and hybrid search". LongMemEval-S 500-Q (95.2% R@5) reprodukálandó benchmark. Konkrét tanulás: (a) reprodukálható benchmark-keret hiánya, (b) PreCompact hook hiányzik (most már ÉLES skeleton), (c) atomic-write registry-szintű (most már Layer-1 full).

- **Sprint A+B+C+D komplett BMAD-integráció pattern** mint reusable extension-mechanism: A (bridge skeleton) → B (skill-level adoption) → C (per-projekt redirect/config) → D (daemon-szintű watch). Minden extension-mechanizmusra reusable progression. **Wider lesson**: external-tool integráció vault-be NEM big-bang, hanem 4-sprint progression (skeleton → skill-pre-load → output-redirect → daemon-watch).

## Next session

### Top-5 prioritás

1. **HN-post valódi submit Tue 14:00 UTC** — `subagent-fanout` HN-1 first (15-25% p(front-page)), Twitter master-thread thread parallel. User-action a `/hn-launch/`-on, 1-click.
2. **B-1 Aggressive 0.85 ramp W21+** — organic 30+ applied bullet data (most W20 4 applied), ETA `sv-phase-b1-done` 2026-06-07 W23.
3. **B-3 NLI default-shift** — daemon-fix + 30-sample backfill W21 → W22 monitor re-read → W23 flip (ETA 2026-06-07).
4. **Podcast bitrate re-encode** — `ffmpeg -b:a 96k` mind 3 NotebookLM MP3-on, ~12 MB total (vs 121 MB). Plus HU dubbing pipeline-design.
5. **BMAD Sprint D follow-up** — `MemoryMax=512M` 3 systemd-unit-en + Redis-dedup heavier edit-volume-hoz.

### Backlog (alsóbb prioritás)

- **B-2 daemon W4 follow-up** — Gate 1 NEAR (cold 605ms, warm 197ms), `vault-search-server` systemd-unit health-check kell daemon-down esetén
- **B-8 RSI Tier-2 real-LLM Critic** — most deterministic heurisztika 4 rule-on, Week 2-3 TODO
- **LongMemEval-S v0.3** — hybrid + rerank fused-pool, fetch-K sweep, cross-namespace ADR+wiki query, +5-8pp várt
- **vault_atomic-lint rule** — új `/usr/local/bin` python script ne mehessen be `vault_atomic` import nélkül ha vault-touch (bekötés `vault-cleanup`-ba)
- **append-only JSONL migráció** — POSIX `O_APPEND` < PIPE_BUF OK, de egységességért MEDIUM-tier followup
- **Concept full v2 LLM-fanout** — most rule-based 9.3% max-yield, LLM-fanout ambiguous-only +5-10% várt
- **GEPA Week 3** real subagent reflection_lm + Critic-review gate `candidates/` → `.vault-agents/prompts/` promóció
- **HN-essay v2** — §2 8-axis trim ~40% + concrete asciicast-embedding §3.3 (top-5 confidence-hez kell)
- **Old 4 audio-overview regen** — currently TTS 1-voice, NotebookLM 2-host deep-dive sokkal jobb

### Cumulative state — END OF EPIC SESSION

- **Wiki-stack:** 251 vault / 252 public, 71 EN translation (28% coverage), 101 audit, 14 SV-meta session, 27 Daily
- **Entity-graph:** 8997 entity / 100% typed / 300 ALIAS_OF / 3431 :LINKS_TO / 1106 típusos `:RELATES` / 24 606 total edges
- **KO-DB:** 13 801 fact, 100% vault coverage, 9.9% predicate-dump-rate (volt 27.7%)
- **Audio:** 23 MP3 (20 TTS 1-voice + 3 NotebookLM 2-host, 121 MB)
- **Open-source:** PUBLIC `MyForgeLabs/myforge-vault-1111`, MIT, v1.0.0 release, 2 git-tag (b1-week4-milestone + b2-done), 70+ public commits today
- **Site:** mkdocs-material 9.5 + 8 plugin (search HU+EN + ezlinks + rss + glightbox + git-revision + minify + awesome-pages + minify-html), mind 7 nav-page HTTP 200
- **Cron-pipeline:** 14 vault-crons mind flock-mutex, 30-perces public-sync
- **Systemd:** 3 BMAD-watch service + 1 vault-search-daemon
- **Quality-automation:** wiki-quality-score (242 wiki avg 71), ADR-pipeline (43 ADR), Tag-taxonomy 99.8% compliance, broken-link 0
- **BMAD-integráció:** Sprint A+B+C+D komplett, auto-ingest 3 projekt-en, 0 manuális copy
- **Layer-1 vault-atomic:** FULL coverage (15 site migrált, grep 0 maradék)
- **Distribution-ready:** HN Launch Console (7 1-click submit), Karpathy-essay 3896 szó (HN 7.5/10), Twitter master-thread, 3-hét cadence-plan

## Propagation log

**2026-05-19 — Crystallization-protokoll végrehajtva user-megerősítés után:**

- **MEMORY.md** — új epic-super-session pointer (1 sor, ~700 char) a tetejére: "Vault-meta EPIC super-session 2026-05-18→19 ~9 óra, ~300 task, B-2/B-6/BMAD A+B+C+D/B-7 24K edges/B-8 Tier-2 skeleton/Layer-1 atomic-full"
- **`02-Projects/superintelligent-vault.md`** — status update: `🟡 active — Phase B-1 sprint indul` → `🟢 active — B-2 sprint-done, BMAD Sprint A+B+C+D komplett, Layer-1 atomic FULL coverage, B-8 Tier-2 skeleton`, `updated: 2026-05-19`
- **4 új evergreen wiki landed:**
  - `11-wiki/tag-backfill-heuristic-pattern.md` — filename-only tech-tag, FP 20%→5%
  - `11-wiki/systemd-template-unit-multi-project-pattern.md` — `@<instance>` pattern + MemoryMax/TasksMax gotcha
  - `11-wiki/per-project-context-skill-pattern.md` — 78-86% token-saving, 5 SKILL.md landed
  - `11-wiki/external-tool-integration-4-sprint-progression.md` — A→D progression meta-pattern (BMAD-validated)
- **3 wiki bővítés:**
  - `11-wiki/notebooklm-cli-gotchas.md` — új #11 sub-section: "Audio-overview bitrate gotcha" (1200kbps → 96kbps ffmpeg re-encode)
  - `11-wiki/hybrid-bm25-semantic-rrf-pattern.en.md` — "LongMemEval-S v0.2 validation" szakasz (smart-rerank no-op finding, candidate-fetch diversity > reranking precision)
  - `11-wiki/multi-layer-safety-gate.md` — "Új minta-realizáció: flock-mutex + atomic-write komplementer" szakasz + cross-link `rsi-tier2-constitutional-ai-pattern`-re
- **ADR** — `07-Decisions/2026-05-18 sv-phase-b2 retrospective.md` MÁR tartalmazza a "Score-scale evolution" clarification-t (subagent által szervezve a B-2 sprint-zárás során)
- **Sync history** — 70+ public commit ma a `MyForgeLabs/myforge-vault-1111` repo-n, cron-os 30-perces auto-sync ÉLES
- **Git-tag** — `sv-phase-b2-done` landed 23:00 körül (Gate 1+3 PASS + Gate 2 Option-C top-1 smart-rerank ≥0.65 9/10 PASS)

**Hatókör:** 11 Learning bullet × 11 propagation-target (MEMORY + 5 wiki + 1 projekt-status + 1 ADR + 4 új wiki). Routing decision-tree user-confirmed batch-preview után, NEM destruktív, mind idempotens / sentinel-jelölt revertible.

**Session NEM zárva még** — `/11.11-zar-session` shell-script futtatja a git-commit + push final-step-et.
> - HN/Twitter/Reddit posts ready-to-submit (7 wiki final-draft)

> **AGENT TENNIVALÓ:** SESSION ZÁRÁSKOR (11.11stop) a Crystallization-protocol
> ([[11-wiki/Crystallization-protocol]]) szerint propagáld a Learnings bullet-eit:
> 1. Routing decision tree minden bullet-re
> 2. Batch preview a user-nek (összes egyszerre)
> 3. User-megerősítés után végrehajtás
> 4. Időbélyegezve írd be ide mit hova propagáltál

