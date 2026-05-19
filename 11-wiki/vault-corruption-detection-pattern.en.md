---
name: Vault-corruption detection pattern (EN)
type: wiki
lang: en
translated_from: vault-corruption-detection-pattern.md
tags: ["#type/wiki", "vault", "integrity", "monitoring", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Vault-corruption detection pattern

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[vault-corruption-detection-pattern.md]] (Hungarian version).

## TL;DR

A 3000+ markdown / 13K+ KO-DB-fact / 9K Memgraph-entity vault can corrupt silently in many ways (broken-link creep, encoding bug, escape-strip, frontmatter drift, self-referential loop, orphan wiki). The **vault-corruption detection pattern** measures this on **5 detection axes**, each with its own script, JSON+MD output, and weekly cron. The 5 axes are complementary — none replaces another.

## Background

As the vault structure grew (Karpathy LLM-Wiki + Johnny-Decimal + B-1..B-8 SV pipeline), "corruption" stopped being visible via `git status`. Concrete incidents led to the detection-axis matrix:

- **Backslash-strip on Unicode escapes** in editor JSON exports → `é` rendered as `u00e9` (silent, only visible on render)
- **Cron-script hardcoded paths** broke after vault rename → daily scan crashed weeks before noticed
- **Audit-MD self-referential loop** — System_Health output listed broken `[[wikilink]]` literals → next scan re-flagged itself
- **mgclient autocommit silent rollback** — 1262 graph mutations vanished without error
- **Lazy-Concept node noise** — 7022 noisy `:Concept` entities from raw-fact-fragments

Each is "silent" in a different layer (file content / cron infra / audit output / DB transaction / graph topology). One axis cannot catch them all.

## The 5 detection axes

### 1. Frontmatter + YAML parse (`vault-cleanup`)

- Scans every `.md` for valid YAML frontmatter
- Reports missing `type:`, malformed dates, broken `[[wikilink]]` targets
- Weekly cron Sunday 04:00, output `06-Audits/System_Health.md`
- **Catches:** structural drift, schema violations, broken refs

### 2. Broken-wikilinks deep scan (`vault-broken-wikilinks-audit`)

- Code-fence aware, relative-path aware, header-anchor aware
- Distinct from `vault-cleanup` — orthogonal heuristics
- Daily cron 04:30, output `06-Audits/broken-wikilinks-latest.md`
- **Catches:** wikilink rot after renames, escape-strip artifacts, false-positive cascades

### 3. KO-DB cross-source contradictions (`vault-ko-conflicts-audit`)

- For every predicate, finds entities where different sources give contradicting values
- Heat-classifier (HIGH/MID/LOW)
- Weekly cron Sunday 04:30, output `06-Audits/cross-source-conflicts-*.md`
- **Catches:** factual drift, stale claims, predicate ambiguity

### 4. Memgraph orphan/lazy node detect (`vault-graph-lazy-concept-cleanup`)

- `:Concept` nodes with `source_count IS NULL` and no cross-source corroboration → candidate noise
- Wordy/long-name / unit-pattern / path-pattern heuristics
- On-demand, output JSON + audit-MD
- **Catches:** raw-fact-fragment noise, lazy-created entities from auto-ingestion

### 5. Vault-coherence drift check (`vault-coherence-check`)

- Compares newly-applied facts against historical KO-DB
- Flags contradictions, novelty-vs-noise
- Used by `11.11crystallize` Layer 2.6 (cascading eval)
- **Catches:** semantic drift, propagation errors

## Reusable rules

1. **Multi-axis is required** — single-axis detection misses 60-80% of real corruptions (each axis sees a different surface).
2. **Detection ≠ correction** — keep them separate scripts. Detection runs cheap+often; correction runs gated+rare.
3. **Self-exclude audit outputs** — auditor-MD that lists `[[broken-link]]` literals must add itself to `always_skip` (see [[audit-md-self-referential-loop]]).
4. **JSON + MD dual-output** — JSON for diff/trend, MD for human review. Both go to `06-Audits/`.
5. **Weekly cadence default**, daily for fast-changing layers (wikilinks).
6. **Threshold-trigger alerts** — if `broken_targets > prev_week * 1.2` → flag regression.
7. **Idempotent + dry-run default** — every detection script must be safely re-runnable.

## Anti-pattern

- **"git status passes, so we're fine"** — corruption lives below the file-level diff.
- **Single-script "vault-health"** — one script can't see all 5 axes; you get false confidence.
- **No baseline measurement** — without a `prev_week` to compare, regressions are invisible.
- **Auto-fix without human review** — corruptions often look like noise but encode real history.

## Pitfalls

- The `vault-cleanup` script ran weekly used to re-flag its own audit output (self-referential loop) until `is_excluded_path()` patched in `06-Audits/System_Health.md` + `broken-wikilinks-latest.md`.
- Cron-script hardcoded paths broke silently for 3 weeks after a vault rename — recommended `VAULT_ROOT` env-var + `grep` audit after any restructure.
- Memgraph's mgclient driver silently rolls back uncommitted SET/CREATE/MERGE on `conn.close()` unless `autocommit = True` — measured 1262 lost writes, see [[mgclient-autocommit-silent-rollback]].

## Related

- [[audit-md-self-referential-loop]] — Auditor-output self-loop trap
- [[mgclient-autocommit-silent-rollback]] — DB driver silent-rollback
- [[silent-fail-family-taxonomy]] — Cross-stack silent-fail taxonomy
- [[vault-restructure-impact-checklist]] — Pre-restructure 10-point checklist
- [[cron-script-silent-fail-detection]] — Cron-specific detection patterns
