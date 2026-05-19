# Changelog

All notable changes to MyForge Vault 11.11.

## [1.0.2] — 2026-05-19 (later)

Repo-audit-driven launch-readiness pass. No code-behaviour changes; everything below is OSS infrastructure, documentation, or distribution polish.

### Added

- **`.github/workflows/ci.yml`** — main CI pipeline: ruff lint + markdown lint (lax) + frontmatter lint + broken-wikilink scan + pytest regression + mkdocs strict build (6 parallel jobs, 10-min timeout each)
- **`.github/workflows/pr-labeler.yml`** + **`.github/labeler.yml`** — auto-label PRs by area (wiki / adr / audit / cli / docs / i18n / breaking-change)
- **`.github/workflows/stale.yml`** — gentle 60/30-day stale-marker on issues / PRs, with `pinned`/`roadmap`/`community-pattern` exemptions
- **`.github/workflows/link-check.yml`** — weekly external-link check via `lycheeverse/lychee-action`, auto-files issue on 404s
- **`.github/scripts/lint_frontmatter.py`** + **`broken_wikilinks_check.py`** — CI-helper scripts, locally runnable, budget-tunable
- **`Makefile`** — `make {help,install,lint,test,docs,build-docs,clean}` developer-friendly targets
- **`requirements-dev.txt`** — `pytest`, `pyyaml`, `ruff`
- **`.devcontainer/`** — GitHub Codespaces / VS Code dev-container: Python 3.12 + Docker-in-Docker + auto-Memgraph + 8 IDE extensions pre-configured + post-create banner
- **`.github/CODEOWNERS`** — single-maintainer signal
- **`docs/assets/hero-banner.png`** — 1280×640 PNG rasterized from the SVG, ready for GitHub social-preview upload (Settings → Options → Social preview)
- **`11-wiki/architecture-overview.en.md`** — full Mermaid architecture diagram + the 8 axes mapped end-to-end + per-axis deep-dive links
- **`11-wiki/faq.en.md`** — 13 launch-FAQ questions answered up front
- **`06-Audits/2026-05-19 repo improvement audit.md`** — ~3,250-word benchmark vs mem0/lancedb/qdrant/microsoft-graphrag/agno/crewai/langfuse/litellm
- **`06-Audits/2026-05-19 GitHub launch playbook.md`** — ~7,060-word channel-by-channel playbook (HN×3 / Twitter / Reddit×3 / Dev.to / Lobsters / LinkedIn / Mastodon) with paste-ready post drafts

### Changed

- **README rewrite** — corrected stale counts (87 → **258** wikis, 28 → **45** ADRs, 76 → ~80 sessions), fixed broken quickstart URL (`<owner>/superintelligent-vault.git` → `MyForgeLabs/myforge-vault-1111.git` — caught by the audit as a stop-the-launch finding), added memory-OSS competitor comparison table (mem0 / Letta / GraphRAG / agentmemory), added Contributors section honestly listing AI agents as named co-collaborators, added Architecture diagram block, added Star History + Built-with + Cite-this-work collapsible sections, added FAQ + architecture-overview links
- **Repo topics** added 8 new (now 20 total): `ai-agents`, `rag`, `vector-search`, `embedding`, `llm-eval`, `personal-knowledge-management`, `local-first`, `bge-m3`
- **`mkdocs.yml`** — hid `HN Launch Console` from public nav (it's launch-internal, optics risk)

### Fixed

- **Stop-the-launch:** README quickstart had a `<owner>/superintelligent-vault.git` placeholder URL pointing at the legacy repo name. Fixed pre-Tuesday launch.

### User-action remaining

- **Social-preview PNG upload** — `docs/assets/hero-banner.png` is ready in the repo; upload via Settings → Options → Social preview (no REST API for this; must use web UI)

## [1.0.1] — 2026-05-19

Two days of post-launch polish on top of v1.0.0. No breaking changes.

### Added

- **`SECURITY.md`** — vulnerability disclosure policy
- **`CITATION.cff`** — academic citation metadata (Zenodo-compatible DOI mintable)
- **`llms.txt`** at repo root — agentic-browsing discovery per [llmstxt.org](https://llmstxt.org)
- **`.github/FUNDING.yml`** — GitHub Sponsors registration
- **`.github/ISSUE_TEMPLATE/vault_pattern.md`** — "Share your vault pattern" community thread template
- **`.github/ISSUE_TEMPLATE/config.yml`** — routes blank issues to Discussions instead
- **`.vault-mcp/vault_mcp_server.py`** — umbrella STDIO MCP server (7 read-only tools: `search_vault`, `search_skills`, `ko_query`, `ko_top_k`, `memgraph_cypher`, `read_project`, `list_recent_sessions`); local-first, no auth, mutation keywords rejected in Cypher
- **`.vault-mcp/mcp.json.sample`** — wire-up config for Claude Code / Claude Desktop / Codex / Gemini
- **`.vault-eval/regression/`** — LongMemEval-S retrieval-quality CI gate (Pytest fast + slow modes, daily cron)
- **`/usr/local/bin/vault-search-health`** — 5-step daemon probe (socket / systemd / health-rpc / search-rpc / skill-ns)
- **`/usr/local/bin/vault-atomic-lint`** — AST-scan + whitelist-comment lint for atomic-write compliance
- **`/usr/local/bin/vault-eval-regression`** — CLI wrapper for the LongMemEval-S regression gate
- **`/usr/local/bin/vault-sleep-consolidate`** — REM-style cross-session learning consolidator (stage-1 rule gate + stage-2 LLM-Critic via subagent-fanout pending pattern, audit-only by default)
- **`/usr/local/bin/vault-browser-history-ingest`** — Chrome/Chromium/Brave History → `10-raw/external/browser/` with NLI pre-filter, dry-run default, `VAULT_BROWSER_INGEST_APPLY=1` gate
- **`11-wiki/append-only-jsonl-migration.md`** — 17-site migration playbook + subagent triage finding
- **`11-wiki/browser-history-ingest-pattern.md`** — passive-ingest pipeline doc
- **3 NotebookLM podcasts re-encoded** from 1200 kbps to 96 kbps: **121 MB → 45 MB** (-62%)

### Changed

- **`bmad-vault-watch@.service`** systemd template hardened: `MemoryMax=512M`, `MemoryHigh=384M`, `TasksMax=128`
- **`vault-search.service`** patched: `VAULT_RERANK_PREWARM=v2-m3`, `MemoryHigh=5G`, `MemoryMax=7G`; bge-reranker now warm at daemon start
- **`vault-search` CLI** auto-backend smart-rerank now **delegates to the daemon** when `reranker_loaded: true` — wall-clock **18.6 s → 8.7 s (-55%)**
- **12 JSONL append-sites** migrated to the centralised `vault_atomic.atomic_append_jsonl` helper
- **B-7 entity typing**: 28.9% → **72.8% (+43.9pp)** in one parallel subagent classification pass

### Fixed

- **B-2 no-socket score-norm bug RESOLVED** — daemon-vs-legacy score divergence eliminated by implicit chunk-vector re-normalization
- **`mgclient` autocommit silent-rollback** — `conn.autocommit = True` enforced in all Memgraph writers
- **`set -e` + `vault-detect-chat-id` exit-1 collision** in 5 of the `11.11*` family scripts
- **Audit-MD self-referential loop** in the broken-wikilink scanner (~70% noise reduction)

### Internal

- **Layer-1 vault-atomic FULL coverage** across 15 sites + flock-mutex in 14+ cron jobs
- **B-7 graph**: 24,606 typed edges, 100% typed, 3,431 `:LINKS_TO`, 300 `:ALIAS_OF`
- **B-8 RSI Tier-2 Constitutional AI skeleton** (319 LOC, 10 rules, 4-layer safety, `--apply` blocked by default)
- **4 new daily cron jobs** (all flock-mutex): vault-search-health 30-min, vault-atomic-lint 02:30, vault-eval-regression 02:45, vault-sleep-consolidate 03:30

### Numbers (post-1.0.1)

- 252 wikis (was 219), 71 EN translations
- 13,800+ KO-DB facts, 8,997 entity-graph nodes / 24,606 edges / 100% typed
- 67/99 Recall@5 hybrid (LongMemEval-S vault-variant v0.2)
- 0 atomic-write violations (66 scripts lint-compliant)
- 18.6s → 8.7s smart-rerank wall-clock (-55%)
- 121 MB → 45 MB podcast footprint (-62%)

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.0...v1.0.1

## [1.0.0] — 2026-05-18

**Initial public release.** Repository flipped from PRIVATE to PUBLIC, MIT license, docs site live at <https://myforgelabs.github.io/myforge-vault-1111/>.

### Knowledge base
- **140 evergreen wikis** in `11-wiki/` (Hungarian primary, English translations for top-10 in progress)
- **41 ADRs** in `07-Decisions/`
- **67+ audit reports** in `06-Audits/`
- **13 SV-meta sessions** in `08-Sessions/` (scrub-validated for public)
- Master-INDEX with 10 topic-clusters (`11-wiki/Index.md`, 330 lines)

### 8-axis architecture (B-1 .. B-8) — Phase B foundation landed

- **B-1 Crystallization automation** — `11.11crystallize` script, G-Eval v0.3 paired-calibration, 4-layer safety-gate, Layer 2.5 NLI + Layer 2.6 coherence-check cascade
- **B-2 Memory architecture** — Memgraph CE 3.9.0 native vector-index (280× speedup, p95 2.6 ms), bge-m3 multilingual encoder, RRF hybrid BM25+semantic
- **B-3 Continuous evaluation** — G-Eval prompt, NLI Layer 2.5, coherence-check Layer 2.6, SelfCheckGPT borderline filter
- **B-4 Tool composition** — `vault-skill-search`, 462 SkillChunk Memgraph-embedded
- **B-5 NotebookLM cognitive layer** — 63-source vault-meta NB, cross-project synthesis (Q1–Q5)
- **B-6 Multi-agent orchestration** — `11.11worker.sh` claude-code subprocess pattern
- **B-7 World-model / knowledge graph** — 8997 entities, **74.7% typed** (Concept/Skill/Project/Sprint/Server/Person/Decision/SourceFile/Pattern/Alias), 102 ALIAS_OF edges
- **B-8 Recursive self-improvement** — GEPA `gepa.optimize()` real loop, Pareto +14.3% (custom GEPAAdapter + ClaudeCodeReflectionLM)

### Tooling

- `11.11*` session-orchestration CLI family (start/stop/note/focus/ls/crystallize/worker)
- `vault-public-sync` — idempotent scrub + commit + push pipeline, 30-min cron
- `vault-broken-wikilinks-audit` — code-fence + relative-path + auto-memory aware
- `vault-graph-query` — Memgraph CLI wrapper (autocommit-patched 2026-05-18)
- `vault-search` + `vault-search-server` — semantic search daemon (warm bge-m3 + Memgraph vector-index)
- `vault-ko-query` — KO-DB top-K cross-source corroboration
- `vault-cleanup` — weekly vault-integrity scan with self-exclusion fix
- 35+ additional scripts in `.vault-*/scripts/`

### Open-source release

- **Scrub pipeline:** paranoid YAML rules + glob-aware regex + 94 replacements + 0 forbidden-violations
- **Docs site:** mkdocs-material with Hungarian UI, dark-mode default, search, navigation tabs, git-revision-date footer, glightbox image zoom
- **GitHub Action:** auto-deploy on push to `main` (Pages, ~3 min build time)
- **License:** MIT, attribution to MyForge Labs

### Quality metrics (session of 2026-05-18)

- KO-DB facts: **13 801** (100% vault coverage: 76 wikis + 28 ADRs + 69 sessions)
- Predicate-dump rate: 19.8% → **9.9%** (via 1 046 fact predicate-remap)
- Memgraph entity-typedness: 28.9% → **74.7%** (+45.8 pp via 7-batch context-aware classification fanout)
- ALIAS_OF edges: 26 → **102** (separator/suffix/case normalization)
- Memgraph wiki chunk coverage: 0 → **100% (97/97)**
- Crystallization predicate dump: 27.7% → 9.9%

### Bug-fixes shipped

- `vault-graph-query` autocommit-bug — silent rollback on SET/CREATE/MERGE statements (Memgraph mgclient default explicit-transaction mode)
- `vault-cleanup` self-referential audit-loop — System_Health.md and broken-wikilinks-latest.md now self-excluded
- `vault-cleanup` relative-path resolution — `[[../11-wiki/x]]` now resolves correctly
- `11.11*` family `set -e` + `vault-detect-chat-id` exit-1 collision fix (5 scripts patched)

## Pre-1.0 history

See `08-Sessions/` for the 6 super-sessions between 2026-05-17 and 2026-05-18 that produced the initial public release. Earlier internal development (since 2026-02-05) remains private.
