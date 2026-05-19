---
name: obsidian-vault
type: session
project: obsidian-vault
status: open
started: 2026-05-19T07:48+00:00
ended:
agent: claude
tags: ["#type/session", "#project/obsidian-vault"]
---

## Pre-loaded context

> Auto-load 2026-05-19T07:48 — agent: claude — vault-meta session a tegnapi **EPIC ~9h / ~300-task super-session** után. 5 forrás · ~3K token · ready.

**Projekt-detektálás:** `obsidian-vault` → vault-meta / [[../02-Projects/superintelligent-vault]] (B-1 + B-2 sprint, BMAD-integráció, MyForge OS, MEMORY governance). Az utóbbi 2 napban (2026-05-17→19) **6 vault-meta super-session** zárult, **70+ public commit** ment ki a `MyForgeLabs/myforge-vault-1111` PUBLIC repóra.

**SV roadmap aktuális állapot** ([[../02-Projects/superintelligent-vault]] + [[../07-Decisions/2026-05-18 B-1 sprint retrospective (W1-4 + W5-6 forecast)]] + [[../07-Decisions/2026-05-18 sv-phase-b2 retrospective]]):
- **B-1 W1-4 PASS** (`sv-phase-b1-week4-milestone` git-tag); 7/7 deliverable LANDED; 96.7% G-Eval verdict-agreement; 13 801 fact / 100% vault-coverage / 1046 predicate-remap. **W5-6 data-collection phase**, `sv-phase-b1-done` ETA **W23 (2026-06-01..06-07)** — gating: 10+ applied bullet + NLI ≥2 hét agreement-rate.
- **B-2 sprint-done** git-tag (Option-C top-1 smart-rerank ≥0.65, 9/10 PASS). `vault-search-server` socket-daemon **605ms cold / 197ms warm** (volt ~30s), Memgraph native vector-index **280× speedup**, 5 project-context-skill LANDED (token-cost 15-20K → ~2K, **8-10× lemegy**). Open: no-socket score-norm bug (post-B-2), `bmad-vault-bridge --context` shim-használat verify.
- **B-6/B-7/B-8** mind landed milestone-szinten: B-7 **24K edges + 100% typed** (volt 14.87% → 28.9% → 72.8% → 100%) + 300 ALIAS_OF + 3431 :LINKS_TO + lazy-Concept cleanup -3611; B-8 **RSI Tier-2 Constitutional AI skeleton** (319 sor, 10 rule, 4-layer safety, `--apply` blokkolt); B-6 worker-triász + orchestrator E2E 45s.
- **G-Eval v0.3** szimmetrikus bias-mitigation **NEM default**: paired kalibráció Pass-recall **53%** (false-discard 7/15) → opt-in env-var `VAULT_GEVAL_VERSION=v03`.
- **Layer-1 vault-atomic FULL coverage**: 15 site migrált, shared `vault_atomic.py` (188 sor, 10/10 unit-test), 14 cron flock-mutex.

**Tegnapi super-session highlight-ok** ([[2026-05-18-obsidian-vault]]):
- **Wiki 97 → 251** (+154), **EN 0 → 71** (28% coverage), **Audit 0 → 101**
- **Broken-link 189 → 0** (-100%) — új `vault-broken-wikilinks-audit` script, self-loop fix
- **Karpathy-style longform essay 3896 szó** (HN 7.5/10) + **3 NotebookLM 2-host podcast** (121 MB, EN) + **HN Launch Console** (7 1-click submit)
- **BMAD ↔ vault auto-ingest pipeline** Sprint A+B+C+D komplett (bridge 489 sor + step-00 vault-preload + per-projekt redirect + 3 systemd-watch, **3-5× gyorsulás** PRD/Arch)
- **Open-source release** PUBLIC: MIT, v1.0.0, mkdocs-material 9.5 site ÉLES (`https://myforgelabs.github.io/myforge-vault-1111/`)
- **vault-quality** 99.8% tag-compliance (filename-only tech-tag, FP 20%→5%)
- **LongMemEval-S** 46% → **67.68%** Recall@5 hybrid BM25+RRF (smart-rerank no-op finding)

**Top-5 prioritás a tegnapi `Next session`-ből:**
1. **HN-post valódi submit Tue 14:00 UTC** — `subagent-fanout` HN-1 first (15-25% p(front-page)), Twitter master-thread parallel
2. **B-1 Aggressive 0.85 ramp W21+** — organic 30+ applied bullet data; ETA `sv-phase-b1-done` 2026-06-07
3. **B-3 NLI default-shift** — daemon-fix + 30-sample backfill W21 → W22 monitor re-read → W23 flip
4. **Podcast bitrate re-encode** — `ffmpeg -b:a 96k` mind 3 MP3-on (~12 MB total vs 121 MB) + HU dubbing pipeline-design
5. **BMAD Sprint D follow-up** — `MemoryMax=512M` 3 systemd-unit-en + Redis-dedup heavier edit-volume-hoz

**Backlog (alsóbb prio):** B-2 daemon W4 follow-up (vault-search-server health-check), B-8 RSI Tier-2 real-LLM Critic (most deterministic 4-rule heurisztika), LongMemEval-S v0.3 (fused-pool, fetch-K sweep), `vault_atomic-lint` rule, append-only JSONL migration, Concept full v2 LLM-fanout, GEPA Week 3 (real subagent reflection_lm + Critic-review promóció), HN-essay v2 §2 trim, 4 régi audio-overview NotebookLM regen.

**Vault state pillanatkép:**
- **316+ md fájl** / 9 fő mappa (Johnny-Decimal) / MEMORY.md ~24 KB (limit közelében!)
- **Memgraph CE 3.9.0**: 8997 entity / 100% typed / 24 606 edge / native vector-index
- **KO-DB**: 13 801 fact / SQLite / 9.9% predicate-dump-rate (volt 27.7%)
- **Cron-pipeline**: 14 cron flock-mutex; 30-perces `vault-public-sync` → GitHub Pages auto-deploy
- **Systemd**: 3 BMAD-watch + 1 `vault-search-server` daemon
- **`.active-session-$CLAUDE_CODE_SESSION_ID`** per-chat pointer ÉLES (10+ incidens megoldva)

**MEMORY-friss pointer-ek (2026-05-18→19 EPIC):**
- 🚀 Vault-meta EPIC super-session 2026-05-18→19 (~9h, ~300 task, $0 cost)
- 🏆 Boulium Phase 1+Phase 2 P1 + prod-deploy `boulium.com` (12 feature ÉLES)
- 🏗️ KGC-4 ↔ publikus weboldal integráció architektúra v1 (Strapi 5 + NextAuth + SimplePay)
- 🐘 `mgclient` autocommit silent-rollback (kritikus bug-pattern, wider risk psycopg2/mariadb/oracle)
- 🛡️ Constitutional AI Tier-2 RSI 4-rétegű safety-gate (ENV + forbidden-target + git-hook + Critic)

**01-Daily/2026-05-18.md:** üres (csak frontmatter) — a teljes nap a session-fájlokban.

## Cél

A tegnapi EPIC super-session **5-prio + backlog batch** lehúzása — minden ami most futható (a W21+ adat-gated és HN-user-submitten kívül) + **új fejlesztési ötletek research**.

## Events

- 07:48 — Pre-load + 3 párhuzamos task-csoport indítva (state-map, podcast re-encode background, research agent background)
- 07:54 — **Podcast re-encode DONE**: 3 NotebookLM MP3 (121 MB total, 1200kbps) → 96k AAC (45 MB, **62% reduction**). Originálok `originals-1200k/` mappába, új MP3-ek a primary slot-ban.
- 07:55 — **BMAD systemd MemoryMax=512M LANDED**: template `bmad-vault-watch@.service` patched (`MemoryMax=512M` + `MemoryHigh=384M` + `TasksMax=128`), 3 instance (boulium/kgc-berles/mapesz) reload + restart + verify ActiveState=active.
- 07:57 — **vault-search-health script ÉLES** (`/usr/local/bin/vault-search-health`, 5-step probe: socket / systemd / health-rpc / search-rpc / skill-ns, JSON+md output). Smoke 5/5 OK.
- 07:58 — vault-cleanup patched: új `daemon_health` analyzer, 🩺 section a System_Health.md report top-ján. Smoke: 0 issue (healthy).
- 07:59 — **30-min cron entry** vault-search-health-re (`*/30 * * * *` → `06-Audits/vault-search-health.json`). First write OK.
- 08:00 — **bmad-vault-bridge --context shim usage CONFIRMED**: `backend: native`, smart-rerank triggered, 21s wall-clock. **Új follow-up surfaced**: bge-reranker NEM warm a daemon-ban (`reranker_loaded: false`), 6.2s rerank-ms cold-load minden trigger-en.
- 08:01 — **22 új SV dev idea BRAINSTORM landed** (background research agent, `06-Audits/2026-05-19 SV new development ideas brainstorm.md`, ~2,936 szó, 5 bucket, 11 source-cite). Top-5: Temporal-KG SCD2 / RAGAS CI-gate / Sleep-consolidation cron / Browser-history bridge / Vault-MCP server.
- 08:04 — **vault-atomic-lint rule ÉLES** (`/usr/local/bin/vault-atomic-lint`, AST-scan + whitelist comment-tag). Initial scan: 5 violations across 5 scripts.
- 08:05–08:07 — **5 violation triaged**: 3 vault-touching refactored (vault-tag-backfill: write_text→atomic_write; vault-cost-rollup: local atomic_write deleted, use shared module; selfcheck/disable-check/stats-generator: 4 whitelist-comments for /tmp + /root/.vault-config + PUBLIC_REPO state-files). Final lint: **0 violations / 66 scripts compliant**.
- 08:06 — **Daily cron 02:30 vault-atomic-lint** added → `06-Audits/vault-atomic-lint.json` (regression-gate).
- 08:08 — **B-2 no-socket score-norm bug RESOLVED**: 0/3 repro on `Glicko-2` / `MapEsz versenykezeles` / `Memgraph autocommit silent rollback` — daemon and legacy scores match exactly (0.685777, 0.306195, 0.736660). Audit `06-Audits/2026-05-19 B-2 no-socket score-norm bug — RESOLVED.md` landed; root-cause: implicit fix via yesterday's `vault-embed-freshness --refresh` re-normalized stored vectors.
- 08:13 — **HN-essay v2 trim+embed**: §2 8-axis bullets → compact table (373 → 255 words, -31.6%); §3.3 asciicast embed + concrete fanout-transcript code-block hozzáadva. Essay total 3909 szó.
- 08:18–08:20 — **Append-only JSONL migration kickoff**: 17 sites detected, 2 migrated (`vault-tag-backfill` + `bmad-vault-bridge` audit() → `atomic_append_jsonl`), 2 whitelisted, 13 tracked-todo. **Playbook wiki** landed.
- 08:21 — SV-projekt status updated, session Summary írás.
- 08:25 — **Round 2 — user: "nem menjünk csináljuk ami kell"**. Új 6-task batch indítva.
- 08:26 — **JSONL migration agent** (general-purpose, background) spawned a hátralévő 13 site-ra.
- 08:30 — **B-2 reranker-keepalive ÉLES** — felfedezve hogy a daemon-kód már támogatja `VAULT_RERANK_PREWARM=<spec>` env-vart. Systemd-unit patch: `Environment=VAULT_RERANK_PREWARM=v2-m3` + `MemoryHigh=5G` / `MemoryMax=7G`. Daemon-reload + restart, ~20s prewarm után `reranker_loaded: true`. **Wall-clock latency 18.6s → 8.1s (-54%)** verifikálva `--backend=numpy` route-on. **Új followup surfaced**: CLI `auto` backend in-process reranker-t használ smart-rerank trigger-en → kerülő (`VAULT_SEARCH_BACKEND=numpy` export) vagy fix (daemon-delegáció patch).
- 08:33 — B-2 RESOLVED audit kibővítve: keepalive resolution + measured latency table + new backlog item.
- 08:37 — **Vault-MCP umbrella server skeleton landed** (idea #20 a brainstormbol). `/root/obsidian-vault/.vault-mcp/vault_mcp_server.py` (~17KB, 7 tools, read-only): `search_vault` / `search_skills` / `ko_query` / `ko_top_k` / `memgraph_cypher` (mutáció-keyword reject) / `read_project` (prefix-match slug) / `list_recent_sessions`. README + .mcp.json wire-up doc. Smoke 7/7 PASS (a `ko_query` schema-fix után — `source_file` oszlop nem létezett, helyette `provenance`).
- 08:40 — **JSONL migration agent return**: **10 site migrated** (vault-route, vault-skill-distill/search, vault-nb-meta-push, 11.11critic/summarizer/worker, 11.11orchestrator×3, 11.11crystallize×1), **2 manual-review-marked** (vault-ko-remap-legacy ×2 — SQL transaction-scoped file-handle reuse), **2 false-positives correctly refused** (11.11crystallize L370/L390 markdown content append-ek, NEM JSONL). Lint exit 0. Playbook wiki kibővítve subagent-findings szakasszal.
- 08:43 — **RAGAS CI-gate ÉLES** (idea #1): `/root/obsidian-vault/.vault-eval/regression/` (baseline.json + test_longmemeval_regression.py + conftest.py) + `/usr/local/bin/vault-eval-regression` CLI + cron 02:45 daily. 3 pytest fast-mode test PASS. **Self-consistency test fogott egy valós baseline-bug-ot**: `tolerance_pct` vs `min_recall` gap mismatch — javítva inline (cosine `min_recall: 0.2131 / tolerance_pct: 10`, hybrid `min_recall: 0.6268 / tolerance_pct: 5`).
- 08:46 — **Sleep-consolidation cron skeleton ÉLES** (idea #15): `/usr/local/bin/vault-sleep-consolidate` (~14.7KB) — 7-napos session-scan, TF-IDF Jaccard 0.30-threshold clustering, 4-rétegű mock Constitutional Critic (min/max length + recurrence + novelty vs 11-wiki/), audit-only output (`VAULT_SLEEP_APPLY=1 VAULT_SLEEP_REAL=1` env-flag-pár locked). **First run: 60 sessions / 472 bullet / 1 recurrence / 1 SKIP-decision** (Next.js 16 systemctl restart pattern recurred 2 sessions, helyesen elutasítva mert az `pnpm-build-systemctl-restart-deploy-ritual.md` 0.632 token-overlap-pel már létezik). Cron 03:30 daily.
- 08:48 — Round 2 final verify-pass: lint 0 / health 5/5 / regression green / all 4 new cron-ok aktívak.
- 08:55 — **Round 3 indul — user: "mindent csináljunk meg.. meg hogy lehet beröpíteni a köztudatba githubrepon ezt az egészet mert nagy dolgot csinálunk"**. 2 párhuzamos subagent spawn-olva (Browser-history bridge + GitHub launch playbook), main thread medium-tasks-szel folytat.
- 08:58 — **CLI rerank-daemon-delegation patch ÉLES** — `vault-search` auto-backend smart-rerank trigger most a daemon-ot hívja ha `reranker_loaded: true` (új `_daemon_has_reranker_loaded` helper + delegate-block az `_apply_smart_rerank_local`-ban + `VAULT_NO_DAEMON_RERANK=1` fallback). **18.6s → 8.7s wall-clock (-55%)** Glicko-XP benchmark-on (user-time 52s → 0.04s — daemon-socket-call only). Eliminálja a `VAULT_SEARCH_BACKEND=numpy` workaround-ot.
- 09:00 — **Vault-MCP wire-up ÉLES** — `/root/obsidian-vault/.mcp.json` vault-szintű registration (Claude Code auto-loads) + `.vault-mcp/mcp.json.sample` (Codex / Gemini / Claude Desktop config templates).
- 09:02 — **Browser-history bridge subagent return**: `/usr/local/bin/vault-browser-history-ingest` (661 LOC, 25KB) + `11-wiki/browser-history-ingest-pattern.md` (8KB). Chrome/Chromium/Brave SQLite History → `10-raw/external/browser/`, NLI pre-filter (3-tier rule-based), `--dry-run` default + `VAULT_BROWSER_INGEST_APPLY=1` opt-in. Smoke 0/0 (no browser on sandbox, expected). Chrome epoch handling, EXCLUDE_DOMAINS, KO-DB dedup verified with synthetic 7-row test DB.
- 09:04 — **Sleep-consolidation real-LLM-Critic 2-phase pending interface ÉLES** — stage-1 rule-gate (length / recurrence / novelty, always runs) + stage-2 LLM-Critic (opt-in `VAULT_SLEEP_LLM_CRITIC=1`, subagent-fanout pending-file pattern). 5-dimensional rubric prompt: factuality / novelty / durability / vault_fit / safety. Stage-1 fail blocks stage-2 invocation. Verified with current week's 1 detected cluster (Next.js restart): stage-1 fail (novelty 0.632 > 0.45 threshold) → LLM-Critic correctly NOT invoked.
- 09:05 — **GitHub launch playbook subagent return**: `06-Audits/2026-05-19 GitHub launch playbook.md` 7,060 szó, 7 szekció, **3 direct competitor identified** (`swarmclawai/swarmvault` 3 hete launch-olt, `Ar9av/obsidian-wiki`, `obra/knowledge-graph`). **Defensible wedge**: 3-CLI-agent bridge + GEPA RSI + NotebookLM podcast layer (no competitor ships these). **Single highest-leverage action**: Tuesday 2026-05-26 15:00 UTC HN Angle A submit + 11-tweet X thread T+30 min. Cite-list: Show-HN survival study (asof.app/research) + llms.txt spec + GitHub social-preview docs.
- 09:06 — **GitHub repo polish — 6 új artifact a public-repo-ban**: `SECURITY.md` (vuln disclosure policy) + `CITATION.cff` (Zenodo DOI-mintable) + `llms.txt` (agentic-browsing per llmstxt.org spec) + `.github/FUNDING.yml` (Sponsors) + `.github/ISSUE_TEMPLATE/vault_pattern.md` ("Share your vault" community template) + `.github/ISSUE_TEMPLATE/config.yml` (route blank-issue → Discussions). + **CHANGELOG.md v1.0.1 release notes** (Added/Changed/Fixed/Internal/Numbers, ~80 sor).
- 09:08 — `vault-public-sync` triggered → commit `7ad30a2` pushed to `MyForgeLabs/myforge-vault-1111@main` (HEAD == origin/main, 0 commits ahead).
- 09:09 — **v1.0.1 GitHub release LIVE**: https://github.com/MyForgeLabs/myforge-vault-1111/releases/tag/v1.0.1
- 09:15 — **Round 4 indul — user: "mi az amivel tudjuk javítani... contributornak :D meg a repot is nézzük át alaposan"**. 2 párhuzamos subagent spawn (repo-audit + CI-workflow scaffold), main thread on tangibles (PR template / Mermaid arch / FAQ / contributors).
- 09:18 — Repo-improvement audit kezdő-state mapping (258 wiki / 71 EN / 45 ADR / 104 audit / 16 SV-meta session) + CODEOWNERS added.
- 09:20 — **Mermaid architecture wiki ÉLES** (`11-wiki/architecture-overview.en.md`) — full 7-subgraph diagram (Input / Crystallize / Memory / Distilled / Tooling / Eval+RSI / Cognitive) + per-axis ADR+wiki deep-link table + footprint stats.
- 09:21 — **FAQ wiki ÉLES** (`11-wiki/faq.en.md`) — 13 launch-FAQ kérdés ("What is this", "Should I use", "Is this AGI", "How much costs", "Why three CLI agents", "Why Memgraph", "Is AI-aided disclosed", "Discord", "Can I contribute", "Hungarian-first weird", "What's NOT in yet"). Each opinionated, specific, NOT generic.
- 09:22 — **README hero rewrite**: counts frissítve (87 → **258** wiki, 28 → **45** ADR, fokozók: Cost ✓ / KO-DB 13.8K / Memgraph 8997+100% typed / hybrid R@5 67.68% / lint 66/66). 5 új badge (Release / Audits / Star-history). Quick-start link ✓ (placeholder `<owner>/superintelligent-vault.git` már nem volt, audit caught).
- 09:23 — **vs mem0/Letta/GraphRAG/agentmemory competitor table** added — direct memory-OSS comparison (13 dimension), "Where SV is NOT the right pick" honest section, "Where SV IS" 4 use-case. Skill-agent comparison kept as separate table (different category).
- 09:24 — **Contributors section ÉLES** — Vault User + Claude Code + Codex + Gemini + NotebookLM mind named co-collaborator (NEM tool). `AGENT=` commit-trailer pattern documented. Acknowledgements blokk (Karpathy / Memgraph / BAAI / agent-vendors / Obsidian community).
- 09:25 — **Repo-audit subagent return**: 3,250£ audit landed. **1 stop-the-launch caught** (`<owner>/superintelligent-vault.git` placeholder) — already fixed in README edit a percekkel korábban. 5 highest-leverage fix-rank: (1) quickstart URL placeholder, (2) social-preview upload, (3) hero rewrite, (4) stale counters, (5) mem0/GraphRAG/Letta table. Mind a 5 LANDED + competitor-table v0. Audit-benchmarks: mem0 (4-row numbers table → second H2), qdrant (1-line docker run quickstart), lancedb (`<details>⭐` star reveal).
- 09:25 — **Repo topics: 12 → 20** (+8 új: ai-agents, rag, vector-search, embedding, llm-eval, personal-knowledge-management, local-first, bge-m3). Maxed out at 20.
- 09:26 — **`docs/assets/hero-banner.png` 420KB** generated from SVG (1280×640, ImageMagick `convert -density 300 -resize 1280x640`). **User-action remaining**: manual upload via Settings → Options → Social preview (REST API doesn't expose this, only Web UI).
- 09:27 — **Star-history reveal + Built-with + Cite-this-work** collapsible `<details>` blocks added to README footer (lancedb-style pattern).
- 09:27 — **HN Launch Console hidden from mkdocs nav** (optics risk — launch-internal artifact shouldn't be on the public docs site pre-launch).
- 09:28 — **Codespaces devcontainer ÉLES** — `.devcontainer/{devcontainer.json,post-create.sh}` — Python 3.12 + Docker-in-Docker (auto-Memgraph) + 8 IDE extensions (Python/Pylance/Ruff/Markdown/MarkdownLint/TOML/YAML/Claude-Code) + port-forward (7687 silent / 8000 openPreview) + post-create banner. "Try it in Codespaces" button-ready.
- 09:29 — **CI-workflow subagent return**: 4 új workflow YAML (`ci.yml` 5.9KB / `pr-labeler.yml` / `stale.yml` / `link-check.yml`) + `.github/labeler.yml` + 2 helper scripts (`lint_frontmatter.py` budget=25, `broken_wikilinks_check.py` budget=250) + `Makefile` (7 targets: help/install/lint/test/docs/build-docs/clean) + `requirements-dev.txt`. **YAML parse 5/5**. Budget-tunable (MAX_FRONTMATTER_ISSUES env + BROKEN_REF_BUDGET env) — CI passes today, ratchet-down later. Note: existing `docs.yml` (GitHub Pages deploy) untouched.
- 09:30 — **Commit `be26485` + push to PUBLIC main** (5 changed files + 196 insertions). v1.0.2 release LIVE: https://github.com/MyForgeLabs/myforge-vault-1111/releases/tag/v1.0.2 — title: "launch-readiness polish (CI + devcontainer + competitor table + Mermaid arch + FAQ)".

## Summary

**Három round, ~80-min wall-clock, ~30 task LANDED, $0 cost, 4 subagent-fanout iteration.** Round 1 (07:48–08:21): tegnapi top-5 prio + backlog batch lehúzva. Round 2 (08:25–08:48, user: "csináljuk ami kell"): 4 új brainstorm-idea ÉLES skeleton-szinten + JSONL migration finished. **Round 3 (08:55–09:09, user: "mindent csináljunk meg.. meg hogy lehet beröpíteni a köztudatba")**: 4 nagy task lehúzva — CLI rerank-daemon-delegation + Vault-MCP wire-up + Sleep-consolidation real-LLM-Critic + Browser-history bridge (subagent) — **PLUS launch-distribution playbook 7,060 szó** + **GitHub repo polish (6 új artifact)** + **v1.0.1 release LIVE**.

A 22-idea brainstorm 4 idea-ja ÉLES (#1 RAGAS / #13 Browser-history / #15 Sleep-consolidation / #20 Vault-MCP), 18 backlog. Temporal-KG SCD2 #9 a következő session-re.

**Distribution-szempontból (a kérdésre "hogy lehet beröpíteni a köztudatba"):** a `06-Audits/2026-05-19 GitHub launch playbook.md` egy konkrét, paste-ready 7-csatornás playbook (HN ×3 angle / Twitter 11-tweet thread / Reddit ×3 sub / Dev.to / Lobsters / LinkedIn / Mastodon) + SEO + cadence + retry tree. **Single highest-leverage action**: Tuesday 2026-05-26 15:00 UTC HN "Show HN" Angle A submit + X thread T+30 min. **Kritikus finding**: 3 competitor már létezik (swarmclawai/swarmvault, Ar9av/obsidian-wiki, obra/knowledge-graph) — wedge: 3-CLI-agent bridge + GEPA RSI + NotebookLM podcast layer.

### Számszerű eredmények (Round 1 + Round 2 + Round 3 cumulative)

| Kategória | Δ |
|---|---|
| Új /usr/local/bin script | **+5** (vault-search-health, vault-atomic-lint, vault-eval-regression, vault-sleep-consolidate, vault-browser-history-ingest) |
| Új scaffolds (dirs) | **+2** (.vault-mcp/, .vault-eval/regression/) |
| Új cron entry | **+4** (30-min health, daily 02:30/02:45/03:30) |
| Új wiki | **+2** (append-only-jsonl-migration, browser-history-ingest-pattern) |
| Új audit | **+4** (SV dev ideas brainstorm + B-2 RESOLVED + sleep-consolidate + **GitHub launch playbook 7060£**) |
| Refactored vault scripts | **5** (atomic-write compliance) |
| Migrated JSONL append-sites | **12** of 17 (4 whitelist + 2 manual-review SQL-tx, 2 false-positive markdown-content) |
| Systemd hardening | BMAD MemoryMax=512M × 3 + vault-search MemoryHigh=5G/Max=7G + VAULT_RERANK_PREWARM=v2-m3 |
| MP3 footprint | **121 MB → 45 MB** (-62%) |
| Reranker latency | **18.6s → 8.7s** (-55%) wall-clock — Round 3 CLI delegate patch |
| Brainstorm ideas landed (of 22) | **4** (#1 RAGAS / #13 Browser-history / #15 Sleep-consolidation / #20 Vault-MCP) |
| **Public repo polish (Round 3)** | SECURITY.md + CITATION.cff + llms.txt + FUNDING.yml + vault_pattern issue-template + issue-config + CHANGELOG v1.0.1 |
| **Public commits today** | 7ad30a2 + autosaves (~9 commits in this Round 3 alone) |
| **GitHub releases** | v1.0.0 → v1.0.1 → **v1.0.2 LIVE** (releases/tag/v1.0.2) |
| **Launch playbook channels covered** | HN×3 / Twitter / Reddit×3 / Dev.to / Lobsters / LinkedIn / Mastodon |
| Lint compliance | **66/66 scripts ✓** |
| Pytest regression-gate | **3/3 PASS** |
| Daemon health | **5/5 ✓** |

### Round 4 extra (launch-readiness)

| Kategória | Δ |
|---|---|
| Új GitHub workflows | **+4** (ci.yml + pr-labeler.yml + stale.yml + link-check.yml) |
| CI helper scripts | **+2** (lint_frontmatter.py + broken_wikilinks_check.py) + .github/labeler.yml |
| Repo dev-tooling | Makefile (7 targets) + requirements-dev.txt + .devcontainer/ |
| Új wiki (vault-side) | **+2** (architecture-overview.en.md + faq.en.md) |
| Új audit | **+2** (repo improvement audit 3,250£ + GitHub launch playbook 7,060£) |
| Új public-repo file | CODEOWNERS + hero-banner.png + 5 nagyobb README rewrite |
| Repo topics | 12 → **20** (8 új) |
| Stop-the-launch findings caught | **1** (quickstart URL placeholder — fixed) |
| Competitor wedge | mem0 / Letta / GraphRAG / agentmemory comparison table (13 dim) |
| Contributors section | AI agents as named co-collaborators (Claude / Codex / Gemini / NotebookLM) honestly listed |

### Új infrastruktúra ÉLES

**Round 1 (07:48–08:21):**
- `/usr/local/bin/vault-search-health` — 5-step daemon probe (socket/systemd/health-rpc/search-rpc/skill-ns)
- `/usr/local/bin/vault-atomic-lint` — AST-scan for forbidden direct writes
- vault-cleanup `🩺 Daemon health` section a System_Health.md tetején
- BMAD systemd template `MemoryMax=512M` resource-cap

**Round 2 (08:25–08:48):**
- `/usr/local/bin/vault-eval-regression` — LongMemEval-S Pytest CI-gate (idea #1)
- `/usr/local/bin/vault-sleep-consolidate` — REM-style cross-session consolidator (idea #15)
- `/root/obsidian-vault/.vault-mcp/vault_mcp_server.py` — umbrella STDIO MCP, 7 read-only tools (idea #20)
- `/root/obsidian-vault/.vault-eval/regression/` — baseline.json + 3 pytest + conftest
- `vault-search.service` patched: `VAULT_RERANK_PREWARM=v2-m3` + MemoryHigh=5G/MemoryMax=7G → **bge-reranker keepalive ÉLES** (10s wall-clock savings)

**4 new daily/30-min cron entries (mind flock-mutex):**
- `*/30 * * * *` vault-search-health → `06-Audits/vault-search-health.json`
- `30 2 * * *` vault-atomic-lint → `06-Audits/vault-atomic-lint.json`
- `45 2 * * *` vault-eval-regression → `06-Audits/vault-eval-regression.json`
- `30 3 * * *` vault-sleep-consolidate → `06-Audits/sleep-consolidate-<date>.md`

## Learnings → memória

- **Implicit fix via background-cron pattern** — A B-2 no-socket score-norm bug (32× divergencia 2026-05-18-án) ma 0/3 repro: a `vault-embed-freshness --refresh --yes` 6-órás cron közben re-normalizálta a stored chunk-vektorokat (`norm=1.0000` empirikusan). **Wider lesson**: cron-os auto-refresh pipeline-ok **csendben oldhatnak meg bug-ot** ha az alapja invariáns-restore. Verify-before-patch: 3-query smoke test megelőzte a felesleges code-patch-et.

- **Daemon-warm encoder vs daemon-warm reranker** — `vault-search-server` keepalive-ben tartja bge-m3-at (encoder), de NEM tartja warm a bge-reranker-v2-m3-at (cross-encoder). Smart-rerank-triggered query → 6.2s cold-load minden trigger-en. **Wider lesson**: keepalive daemon design szelektív kell, NEM "tartsd warm az összes ML-modellt" (RAM-fragmentáció), de a HOT-path reranker-t igen, ha smart-trigger feltétel rendszeresen tüzel.

- **vault-atomic-lint AST-scan + whitelist-comment pattern** — 5 violation találva 66 script-ben, 5 perc alatt classified + fixed. Pattern: AST-walk forbidden patterns, vault-touching heurisztika `VAULT_TOKENS` consts-szal, `# vault-atomic-lint: ok` line-comment whitelist. **Wider lesson**: regression-gate-eket inline-comment-whitelist-tel **per-call-site reasoning** lehetséges, nem fájl-level `# noqa`. AST + comment-aware lint közös pattern bármely codebase-szintű invariáns kikényszerítésére.

- **systemd template-unit MemoryMax retrofit zero-downtime** — `bmad-vault-watch@.service` template patch → `daemon-reload` + `systemctl restart` per-instance ~0.5s — minden 3-instance ActiveState=active maradt < 2s alatt. **Wider lesson**: template-unit (`@<instance>`) refactor a multi-projekt daemon-stack-en bulk-applicable, NEM per-unit edit.

- **Subagent-fanout brainstorm sweet-spot** — research agent ~6 min, 16 tool-use, 22 ötlet × 11 source-cite, ~85K token. **$0 cost** + parallel-with-main-work. **Wider lesson**: bulk-creative tasks (brainstorm, content-survey, paper-roundup) ideal for fanout-of-1 dedicated agent + main thread continues — NEM blocking. Háttér-research-agentet érdemes spawnolni minden session-elején ha van >5-task batch lehúzandó.

- **Per-file 3-tier refactor classification**: vault-touching (refactor) vs state-file (whitelist) vs append-only-JSONL (atomic_append_jsonl migration) — egy szabálykészletbe vegyítve confused. Külön sections per-rule + külön whitelist-criteria-block playbook-ban tisztább. Pattern reusable bármely codebase-szintű invariáns 3-fajta call-site klasszifikációra.

- **Word-count target ≠ vacuum** — §2 trim cél 40% (373→225), aktuális 31.6% (373→255), mert table-format konstrukció pad-eli a per-bullet-min-szöveget. **Wider lesson**: prose→table refactor jó kompresszió, de van fizikai padló — table-cell magyarázat ≥ 8-10 szó hogy olvasható maradjon, bullet-list ≥ 5-7. 100% trim-target table-formattal nem teljesíthető — érdemes átdefiniálni a tighter table → még tömörebb table-of-contents pattern.

### Round 2 új tanulságok

- **Existing-feature discovery > new-feature build** — A B-2 reranker-keepalive task-on a daemon-kódban már létezett `VAULT_RERANK_PREWARM=<spec>` env-var (lines 582-594), implementáció ÉLES, csak nem konfigurálva. 5-perces grep + 1-soros systemd-edit megspórolt 1-2 óra new-feature impl-t. **Wider lesson**: minden "új feature kell" task ELSŐ lépése a `grep -nE "<feature>"` az érintett kódbázison — gyakran az implementáció már ott, csak nincs engedélyezve.

- **Self-consistency-test caught real bug** — A RAGAS CI-gate `test_baseline_self_consistent` `tolerance_pct` mismatch-et talált a sajat `baseline.json`-emben (declared 10pp, actual 3.31pp). Pytest fail 0.05s alatt fogta el a bug-ot mielőtt commitba ment volna. **Wider lesson**: regression-gate-eknek ne csak külső gate-funkciója legyen, hanem **self-validation** is — a baseline-fájl maga is integrity-checked. Catch problems in your own config, not just in production data.

- **Subagent triage > blind mechanical refactor** — A JSONL migration agent 13/13 callsite-on **2 false-positive-t kifogott** (markdown content append-ek `MEMORY.md`-re és wiki-be) és **2 manual-review-marked-et** (SQL transaction-flow). Naive mechanical regex-find-replace 4-féle bugot okozott volna (JSON-encoded prose + lost transaction atomicity). **Wider lesson**: bulk-mechanical refactor task-okat alkalmas agent-re bízni, AKI tud judgment-call-okat hozni (és vissza-jelezni amit nem konvertál). Pure regex script-tel ez 4 silent bug lett volna.

- **Skeleton-first → finding the finding** — A Sleep-consolidation első futása **NEM talált új promotion-candidate-et** — egyetlen detected recurrence (Next.js restart pattern) helyesen elutasítva mert már wiki-fied. **Wider lesson**: skeleton-first NEM "low-value placeholder" — even a SKIP-decision is information. A vault már jól crystallized; a sleep-consolidate igazi értéke a *jövőbeli* divergencia-detektálás, NEM az aktuális batch.

- **Reranker keepalive: load vs inference cost decomposition** — A 6-10s rerank-cost-ból a daemon-keepalive a load-portion-t eliminálja (~10s wall), de a tényleges cross-encoder forward-pass (~8s on 18 candidates) compute-bound marad. **Wider lesson**: model-warm optimizations szigorúan a *boot-time* (model-load + import) megspórolásáról szólnak, NEM az inference-throughput-ról. GPU vagy quantization kell a inference-bottleneck-hez.

- **Brainstorm → idea-realization tempó: 4/22 ÉLES skeleton egy session-ben** — RAGAS, Sleep-consolidation, Vault-MCP, Browser-history. **Wider lesson**: brainstorm-output ROI akkor mérhető, ha rögtön skeleton-first-tel landol — különben paper-only marad.

### Round 3 új tanulságok

- **3 competitor finding > 22-idea brainstorm** — A launch-playbook subagent kiderítette hogy 3 direct competitor már létezik (swarmclawai/swarmvault 3 hete launch-olt, Ar9av/obsidian-wiki, obra/knowledge-graph). Single most-valuable insight a 7,060-szavas dok-ból. **Wider lesson**: minden OSS launch FIRST step a competitor-discovery (gh search-repos + WebSearch), NEM a polish + post-drafts. A wedge-thinking csak akkor érvényes ha pontosan tudod ki van már ott. A SV stack 3-CLI-bridge + GEPA + NotebookLM trió ad differentiation-t, NEM a vault-pattern maga.

- **Existing-feature discovery (Round 2) → existing-config discovery (Round 3)** — a CLI rerank-daemon-delegation alaposan jól hangzó "nagy patch" volt, de a daemon-kód már támogatta a delegáció primitívjét: a `_try_socket_search()` accept-elte a `smart_rerank: true` flag-et és a daemon-side smart-rerank-logic ÉLES volt. A patch csak a CLI auto-backend ágat hard-wire-elte hozzá. **Wider lesson**: "új feature" task-on a teljes kódbázis grep-je MIELŐTT design-olnál — már ott lehet 80%-ban.

- **Subagent-spawn ordering: Browser-history és Launch-playbook ELLENTÉTES domain** — egyik kódot ír, másik szöveget. Párhuzamos spawn $0-cost wall-clock-savings nélkül (~6 + ~9 min). **Wider lesson**: subagent-parallelizmus akkor reálértékű, ha a task-ok ortogonálisak (egyik nem támaszkodik a másikra) ÉS a wall-clock-uk hasonló nagyságrendű. Itt mindkét feltétel teljesült — pure win.

- **2-phase pending-file pattern transferable extension-point** — A Sleep-consolidation real-LLM-Critic stage-2 ugyanazt a `crystallize` 2-phase pending-file pattern-t használja (request.json → subagent → response.json → re-read). Reusable interface bármely "agent-callable async scoring" feature-höz. **Wider lesson**: a Phase-1/Phase-2 pending-file pattern egy general-purpose "agent-pluggable hook-point" — egy script "kéri" a verdict-et, az agent (claude-code / codex) spawn-olja a subagent-et később, a script idempotensan re-reads. 4. helyen használjuk most (crystallize, selfcheck, vault-ko-ingest, sleep-consolidate).

- **Distribution = engineering** — A launch-playbook NEM marketing-fluff — konkrét HN-title-engineering (Show-HN survival study data alapján), llms.txt szövegezés (per llmstxt.org spec), retry-tree-decision (HN bomb → új angle, NEM ismétlés), competitor-aware wedge framing. **Wider lesson**: open-source distribution **engineering-discipline**, nem charisma-driven. Mérhető (HN points, GitHub stars, mkdocs analytics), retry-able (3 HN angles készen állnak ha 1 bomb-ol), és reusable (a cadence-tree következő projektre is alkalmazható).

## Next session

### Top-5 prioritás (frissítve a Round 2 után — sokat lerövidült)

1. **HN-post valódi submit Tue 14:00 UTC** — még mindig **user-action gated**. Nem futtatható ma.
2. **Vault-MCP wire-up + cloudflared tunnel** — a skeleton ÉLES, most kell .mcp.json-be regisztrálni a Claude Code-on, és Tailscale-funnel/`cloudflared` bridge a claude.ai web/mobile számára. ETA: 1-2h.
3. **Sleep-consolidation real Constitutional Critic** — most mock-rule-based gate, idea-rep promotion-decision rule-by-LLM verifikációs csere. ETA: 2-3h, opt-in `VAULT_SLEEP_REAL=1` után.
4. **vault-ko-remap-legacy 2 manual-review-marked site refactor** — `transaction-aware atomic_append_jsonl` variant kell (`BEGIN ... ROLLBACK` atomicity preserve). ETA: 1-2h.
5. **CLI rerank-daemon-delegation** — `vault-search auto`-backend smart-rerank trigger → daemon socket route ha `reranker_loaded`. Eliminate `VAULT_SEARCH_BACKEND=numpy` workaround. ETA: 1-2h.

### Big bets a 22-ötlet brainstormból (még nem startolt)

- **#9 Temporal-KG SCD2 layer** — `valid_from/valid_until` KO-DB fact-eken, time-travel query ("what did I know on date X"). Highest-confidence reasoner-feature, T-GRAG/STAR-RAG 2026 papers.
- **#13 Browser-history bridge** — Chrome History SQLite → 10-raw NLI pre-filter. Passive ingest, zero-friction, high cross-source-corroboration win.
- **Temporal-KG + Sleep-consolidation kombináció** — a két idea ortogonálisan kombinálható: SCD2 fact-versioning + REM-style cross-session promotion → real time-aware semantic memory.

### Backlog (alsóbb prio, ma kibővítve)

- **22 új dev idea brainstorm review** — `06-Audits/2026-05-19 SV new development ideas brainstorm.md` user-review után priority-rank, top-3 sprint-bontás. Megjegyzés: ötletek között Temporal-KG SCD2, RAGAS CI-gate, Sleep-consolidation cron, Browser-history bridge a legmagasabb-ROI.
- **B-3 NLI default-shift** — daemon-fix + 30-sample backfill W21 → W22 monitor re-read → W23 flip. **Time-gated**.
- **B-8 RSI Tier-2 real-LLM Critic** — most deterministic 4-rule heurisztika, Week 2-3 TODO
- **LongMemEval-S v0.3** — hybrid + rerank fused-pool, fetch-K sweep
- **GEPA Week 3** — real subagent reflection_lm + Critic-review promóció
- **HN-essay v2 verify deployment** — public-repo `11-wiki/what-i-learned-building-self-improving-vault.en.md` 30-min auto-sync után docs-site-on (`https://myforgelabs.github.io/myforge-vault-1111/`) ellenőrizni a §2 table + §3.3 asciicast-link render-t
- **B-6 worker triász** és **Concept full v2 LLM-fanout** — backlog continues

### Cumulative state — END OF SESSION (Round 1 + Round 2)

- **Wiki-stack:** 252 vault / 252 public (+1 ma: `append-only-jsonl-migration.md`), 71 EN translation
- **Audit:** 104 (+3 ma: SV new dev ideas brainstorm + B-2 RESOLVED + sleep-consolidate-2026-05-19)
- **/usr/local/bin scripts:** 69 (+4 ma), 66/66 atomic-write-compliant
- **Cron-pipeline:** 18 (+4 ma) flock-mutex
- **Systemd hardening:** BMAD MemoryMax=512M × 3 + vault-search MemoryHigh=5G/Max=7G + VAULT_RERANK_PREWARM=v2-m3
- **MP3 footprint:** 45 MB (was 121 MB)
- **Reranker latency:** 18.6s → 8.1s wall (-54%)
- **Brainstorm ideas landed (22 total):** 3 ÉLES skeleton (RAGAS / Sleep-consolidation / Vault-MCP), 1 deferred (Browser-history), 18 backlog
- **Open follow-ups closed:** B-2 retro #2 ✅, B-2 reranker-keepalive ✅ (surfaced AND resolved same session)
- **New follow-ups surfaced:** CLI rerank-daemon-delegation, vault-ko-remap-legacy transaction-aware append, Sleep-consolidation real-Critic
- **No regressions:** all 4 new daily-cron-ok ÉLES, all checks green

## Propagation log

> **AGENT TENNIVALÓ:** SESSION ZÁRÁSKOR (11.11stop) a Crystallization-protocol
> ([[11-wiki/Crystallization-protocol]]) szerint propagáld a Learnings bullet-eit:
> 1. Routing decision tree minden bullet-re
> 2. Batch preview a user-nek (összes egyszerre)
> 3. User-megerősítés után végrehajtás
> 4. Időbélyegezve írd be ide mit hova propagáltál

