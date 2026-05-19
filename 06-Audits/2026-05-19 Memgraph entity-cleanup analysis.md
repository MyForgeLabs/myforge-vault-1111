---
name: 2026-05-19 Memgraph entity-cleanup analysis
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/superintelligent-vault", "memgraph", "knowledge-graph", "cleanup"]
related:
  - "[[../11-wiki/two-tier-graph-extraction]]"
  - "[[../08-Sessions/2026-05-19-obsidian-vault]]"
  - "`00-Meta/graph-schema.yml`"
  - "[[../11-wiki/mgclient-autocommit-silent-rollback]]"
status: draft — read-only, no mutations executed
---

# Memgraph entity-cleanup analysis (2026-05-19)

> [!info] Scope
> Read-only analysis of `Entity` nodes in Memgraph (`vault-memgraph` container, CE 3.9.0, localhost:7687). Triggered by mega-session Round 8 finding (`vault-graph-diff` Jaccard 0.0070). NO mutations executed. Source data captured at 2026-05-19.

## Baseline

| Counter | Value |
|---|---:|
| `:Entity` total | **12,778** |
| `:Literal` total | 12,160 |
| Edges total | 24,606 |
| `:Entity` with `source_count=0/NULL` (typed-only, retype-injected) | 3,803 |
| `:Entity` with `source_count>=1` (KO-DB-rooted) | 8,975 |
| `:Entity` with `source_count=1` (single-mention) | **6,537 (51%)** |
| `:Entity` with `source_count>=3` (multi-evidence) | 1,085 (8.5%) |
| `:Entity` with `source_count>=5` | 428 (3.3%) |
| Predicate vocabulary in use | LINKS_TO 3,431 · HAS_VALUE 2,340 · USES 2,318 · PRODUCES 2,135 · MENTIONS 1,954 · REQUIRES 1,615 · APPLIES_TO 1,337 · ... 127 total |
| No-outgoing-edges entities | 3,803 |
| No-incoming-edges entities | 7,898 |

> [!warning] sc=0 ≠ noise
> The 3,803 `source_count=0/NULL` entities are **typed-retype injectees** (`:Person`, `:Project`, `:Concept`, `:Alias`, `:WikiFile`, `:SourceFile`, `:SkillChunk`). They are NOT extraction noise; they come from `vault-graph-retype` enrichment. Examples: `user@example.com`, `Andrej Karpathy`, `MyForge Labs`, `Kisgépcentrum`. **Do not include these in cleanup.**

## Noise-pattern catalog

### Tier-A — Hard-noise (unambiguous, ~1% of graph)

| Pattern | Count | Representative samples |
|---|---:|---|
| `quoted_string_start` (starts with `"`, `'`, or backtick) | 3 | `"3 minutes"`, `"60 seconds"`, `"10 seconds" auto-timeout` |
| `hex_color` (`#RRGGBB` or `#xxx-name`) | 32 | `#f5f1ea`, `#2d3e2f`, `#3b82f6-blue` |
| `url_fragment` (starts with `http`/`https`/`www`) | 9 | `https://stephango.com/vault`, `http://localhost:8202` |
| `too_short` (`size(name) < 3`) | 21 | `Q1`, `Q2`, `Q3` |
| `starts_with_punct` (leading punctuation/operator) | 347 | `!busy && !mutedForTTS guard`, `!empty ternary`, `#!/usr/bin/env python3` |
| `looks_like_path` (filepath ending in code-extension) | 183 | `06-Audits/System_Health.md`, `00-Meta/graph-schema.yml` |
| `number_only` (`^-?[0-9]+(\.[0-9]+)?$`) | 19 | `0`, `0.00`, `0.001` |
| `contains_quote_inside` | 15 | `regex /root/[^ )\`]+\.md`, `<g id="g34">` |
| `contains_html_angle` (`<...>`) | 48 | `Record<string, unknown>`, `<g id="g34">` |
| `md_link_or_wikilink` | 1 | `long 'Details: [[X]]' explanation` |
| `contains_double_colon` | 3 | `Key:: Value syntax`, `Comparator::compare_all method` |
| `contains_arrow` (`->` / `=>`) | 8 | `wpdb->update`, `wpdb->update direct SQL` |
| `contains_pipe` (shell-pipe) | 4 | `sshd -T \| grep passwordauthentication` |
| `contains_equals_assign` (with `=` but not `==`) | 117 | `video preload=metadata on 200+ items`, `humanize=True option` |
| **Hard-noise union (deduped)** | **~797** (6.2% of total) | — |

### Tier-B — Soft-noise (sentence-fragments, much bigger)

| Pattern | Count | Representative samples |
|---|---:|---|
| Phrase-like, `>=3 tokens` | 5,524 | (44% of all entities — many are sentences) |
| Phrase-like, `>=4 tokens` | 1,354 | `Touch-kiosk idle timeout origin`, `Idle timeout above 5 minutes` |
| Phrase-like, `>=5 tokens` | 394 | `setTimeout reset on every state change`, `Dataset larger than 3000 elements` |
| Phrase-like, `>=9 tokens` | 4 | (paragraph-fragments) |
| `snake_or_camel_ident_only` (likely code var/field) | 205 | `_auto_resume_orphans`, `_bricks_editor_mode`, `_bricks_page_content_2` |
| `env_var_like` (`^[A-Z][A-Z0-9_]{2,}$`) | 83 | `ACCENTS_MAP`, `ADMIN_PASSWORD`, `ANTHROPIC_API_KEY` |
| `contains_dollar` (shell var / monetary) | 100 | `global $post variable`, `$50/month tier` |
| `looks_like_filepath_general` (any `/`-separated) | 669 | `06-Audits/System_Health.md`, etc. |

### Tier-C — Composite cleanup-candidate (single-mention + noise-shape)

| Filter | Count |
|---|---:|
| `source_count=1` AND (`>=3 tokens` OR Tier-A shape) | **3,310** |
| `source_count=1` alone (loose) | 6,537 |

> [!success] Recommended cleanup target
> **Tier-C composite (~3,310 entities, 26% of graph)** — high-precision because dual-condition (low evidence AND noise-shape). Trade-offs against pure Tier-A (high precision, low recall ~1%) and pure sc=1 loose (high recall, high false-positive risk on legitimate single-mention concepts).

## Prompt-tightening rules (5–7 actionable)

Insert into `EXTRACTION_PROMPT_TEMPLATE` in `/root/obsidian-vault/.vault-ko/scripts/vault-ko-ingest.py` (lines 64-128), under a new `MUST NOT EXTRACT AS SUBJECT/OBJECT` section. **Important:** these guard the **`subject` and `object` fields** of triples — they do NOT remove value-bearing literals (we want `has_color → #f5f1ea`, just not `:Entity {name: "#f5f1ea"}`).

| # | Rule (verbatim, prompt-ready) |
|---|---|
| 1 | **NEVER emit a `subject` that starts with a quote character (`"`, `'`, backtick).** Quoted phrases are values, not entities — re-frame as `(real-subject, has_string_value, "the quote")`. |
| 2 | **NEVER emit a `subject` that is a hex-color, URL, port number, raw filesystem path, or numeric-only token.** These belong on the right side as `has_color` / `has_url` / `has_port` / `has_path` / `has_count` literals — never as a `:Entity` subject. |
| 3 | **NEVER emit a `subject` whose surface form is a code keyword, operator-laden expression, or shell-pipeline.** Examples to reject: `wpdb->update`, `sshd -T | grep ...`, `!busy && !mutedForTTS guard`, `Record<string, unknown>`. If the concept is real (e.g. "the wpdb update path"), rephrase to a noun-phrase entity. |
| 4 | **NEVER emit a `subject` or `object` longer than 60 characters or containing more than 4 word-tokens.** Long phrases are descriptions/sentences, not entities. Either pick a shorter noun-phrase head, or skip the triple entirely. |
| 5 | **NEVER emit env-var-like ALL_CAPS_IDENT or `_leading_snake_case` tokens as `:Entity` subjects.** Use `has_credential` / `has_flag` / `has_path` with the var-name as literal object instead. |
| 6 | **NEVER invent entities from incidental code-snippets in the markdown.** If the markdown shows `def foo():` or `<div class="x">`, do NOT create `:Entity` nodes for `def`, `foo`, `class`, or HTML tags. Code blocks contribute only when they reveal a named concept. |
| 7 | **PREFER multi-mention concepts.** If a candidate subject appears only once in the document and has no clear referent in vault index files (Projects/Index, Memory, wiki), output `confidence ≤ 0.5` so downstream filters can drop it. |

> [!info] Calibration
> After deploying rules 1-7, target = single-mention entity-rate drops from 51% (current) to <25%, hard-noise union <0.5%, Jaccard with graphify rises from 0.0070 to ≥0.05 on next `vault-graph-diff` run.

## Cleanup-strategy options

### Option A — Bulk-DELETE in Memgraph (no re-extraction)

- **Target set:** Tier-C composite (~3,310 entities) + Tier-A hard-noise union (~797). Total ~3,500-4,000 entity DETACH DELETE.
- **Edge fallout:** ~9,000 edges dropped (proxy from `sc=1` impact: 8,733 edges) — mostly low-confidence sc=1-rooted HAS_VALUE / USES / MENTIONS.
- **Idempotent?** YES — re-runs are no-ops because Cypher WHERE filters target the same shape.
- **Reversible?** Only via snapshot restore (Memgraph DUMP).
- **ETA:** ~5 min Cypher batch (DETACH DELETE in chunks of 500). Plus 5 min snapshot.
- **Risk:** Low — read-only filters are precise; sc=0 typed-entities are skipped by predicate. **BUT:** does not fix KO-DB facts.db — next `vault-graph-extract --reset` re-ingests the same noise.

### Option B — Re-extraction with tightened prompt (no bulk DELETE)

- **Target:** Patch `EXTRACTION_PROMPT_TEMPLATE` with rules 1-7, then `vault-graph-extract --reset` from a re-ingested `facts.db`.
- **Pre-req:** Re-ingest the source files via `vault-ko-ingest --backfill` (subagent-fanout) — the **expensive part**. The vault has ~556 source files; subagent-fanout is $0 (subscription) but takes ~2-3h wall-clock for the ~556 files.
- **Reversible?** YES — facts.db has SCD2 versioning (`scd2.py`); old rows can be revived.
- **ETA:** 30 min prompt-patch + dry-run, 2-3h re-ingest, 5 min graph-extract. **Total 3-4h.**
- **Risk:** Medium — depends on prompt-rule recall (could over-prune valid edge-case entities). MUST run dry-run + sample-review before commit.

### Option C — Hybrid (recommended)

1. **Now (15 min):** Snapshot Memgraph + facts.db. Patch prompt with rules 1-7.
2. **Phase 1 (10 min):** Bulk-DELETE Tier-A hard-noise (~797 entities) — these are unambiguously wrong regardless of provenance. Low risk.
3. **Phase 2 (5 min):** Bulk-DELETE Tier-C composite **only where `source_count=1` AND `max_confidence < 0.8`** — adds confidence-gate to avoid pruning legitimate single-mention concepts. Expected drop: ~2,500-2,800 entities.
4. **Phase 3 (background, 2-3h):** Schedule `vault-ko-ingest --backfill` re-extraction with tightened prompt for **only the noisy-domain files** (08-Sessions/ and any file with `>=5 sc=1 noise-shape entities`). NOT a full re-ingest.
5. **Phase 4 (5 min):** Re-run `vault-graph-diff` to verify Jaccard ≥0.05 improvement.

- **ETA total:** ~3h (most async).
- **Risk:** Lowest — bounded, reversible at every step, prompt-tightening prevents recurrence.

## Snapshot recommendation (mandatory before ANY DELETE)

| Artifact | Command | Output location | Notes |
|---|---|---|---|
| Memgraph full DUMP | `docker exec vault-memgraph bash -c "echo 'DUMP DATABASE;' \| mgconsole" > /root/obsidian-vault/.vault-memory/snapshots/memgraph-2026-05-19-pre-cleanup.cypherl` | `.vault-memory/snapshots/` | Restores entire graph state. Big file (~50-100MB est.). |
| KO-DB facts.db | `cp /root/obsidian-vault/.vault-ko/facts.db /root/obsidian-vault/.vault-ko/snapshots/facts-2026-05-19-pre-cleanup.db` | `.vault-ko/snapshots/` | Source-of-truth for entity-graph. **Critical.** |
| Git commit | `git -C /root/obsidian-vault add -A && git commit -m "snapshot: pre-Memgraph-cleanup 2026-05-19"` | upstream | Provides revert anchor for `.vault-ko/`, `.vault-memory/`, all md files. |
| Entity-stats baseline | `python3 /tmp/memgraph-cleanup-analysis.py > /root/obsidian-vault/.vault-memory/snapshots/baseline-stats-2026-05-19.txt` | `.vault-memory/snapshots/` | Numeric before/after diff anchor. |
| Sample-100 random entities | `MATCH (n:Entity) WITH n, rand() AS r ORDER BY r LIMIT 100 RETURN n.name, n.source_count, n.max_confidence` saved as JSON | `.vault-memory/snapshots/sample-100-pre-cleanup.json` | Sanity-check: post-cleanup the same entities should either still exist (good) or be in the deletion-set (expected). |

> [!warning] `mgclient` autocommit gotcha
> Cleanup scripts will be **write-mode** — remember `conn.autocommit = True` per [[../11-wiki/mgclient-autocommit-silent-rollback]], otherwise DETACH DELETE silently rolls back at close. This analysis was read-only so the gotcha did not apply, but the cleanup script MUST set it.

## Recommendations summary

1. **Adopt Option C (hybrid)** — minimal blast-radius, maximum learning.
2. **Patch the extraction prompt FIRST** (rules 1-7) so any re-ingest produces clean output. This is the lasting fix; bulk-DELETE is the temporary one-shot.
3. **Snapshot is non-negotiable.** Five-step backup above takes 10 min and is fully reversible.
4. **Hold ADR** until Phase 4 metric: if `vault-graph-diff` Jaccard improves from 0.0070 to ≥0.05 (target) or ≥0.10 (stretch), ratify the prompt-rules into `00-Meta/graph-schema.yml` validation block. If improvement <0.03, escalate to NotebookLM deep-research on entity-typing best-practices before broader rollout.
5. **Wider lesson worth wiki-promotion:** "single-mention + shape-noise composite" is a reusable cleanup-filter for any LLM-extracted graph. Promote to `[[../11-wiki/llm-graph-noise-cleanup-composite-filter]]` after Phase 4.

## Source data

- Read-only analysis scripts: `/tmp/memgraph-cleanup-analysis.py`, `/tmp/memgraph-deeper.py`, `/tmp/memgraph-noisepct.py`, `/tmp/memgraph-sc0.py`
- Raw JSON: `/tmp/memgraph-noise-results.json`
- Extraction code reviewed: `/root/obsidian-vault/.vault-graph/scripts/vault-graph-extract.py` (lines 1-247, downstream of KO-DB)
- Extraction prompt reviewed: `/root/obsidian-vault/.vault-ko/scripts/vault-ko-ingest.py` (lines 64-128, `EXTRACTION_PROMPT_TEMPLATE`)
- Schema: `/root/obsidian-vault/00-Meta/graph-schema.yml`
