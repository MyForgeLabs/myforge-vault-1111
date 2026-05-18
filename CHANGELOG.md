# Changelog

All notable changes to MyForge Vault 11.11.

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
