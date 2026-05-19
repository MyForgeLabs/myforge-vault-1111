---
name: NotebookLM deep-research output → KO-DB ingest pipeline
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#service/notebooklm", "#sv/b-1", "#tool/vault-nb-ingest"]
related: [notebooklm-deep-research-custom-report, vault-ko-ingest, crystallization-protocol]
---

# NotebookLM deep-research output → KO-DB ingest pipeline

`vault-nb-ingest` is the bridge between NotebookLM's "deep research" custom-report MD artifacts and the structured KO-DB fact-store. It mirrors the 2-phase pending pattern used by [[vault-ko-ingest]] / `11.11crystallize`, runs $0 (subagent-fanout extraction, no Anthropic API key), and defaults to dry-run with a two-layer apply gate.

## Why a separate ingestion path

Sessions, ADRs, and wikis are first-person *vault-internal* knowledge — they get crystallized via `11.11crystallize` after each `/11.11-zar-session` and their facts land in KO-DB with `source_type='session' | 'adr' | 'wiki'`.

NotebookLM deep-research outputs are different:

- **Multi-source synthesis** — each claim is backed by 50–161 citations the NotebookLM web/PDF retriever assembled. The fact-density-per-line is roughly 3–5× a session summary.
- **7-section structure** — custom reports come back with explicit numbered sections (Q1..Q7 + executive summary + references). Parsing needs a different heuristic than a session's `## Learnings` block.
- **No `/11.11-zar-session` hook fires** — the reports get downloaded by `notebooklm download report -a <id> <path>`, land under `10-raw/external/notebooklm/` or `06-Audits/`, and were previously invisible to the crystallization pipeline.

Result before this script: dense factual content sat in markdown files, but `vault-ko-query --top-k` cross-source corroboration ranking never saw it. `source_type='notebooklm'` rows in `facts.facts` were 0 (Q3 of vault-meta-NB 2026-05-18 confirmed: zero NotebookLM-cited facts in KO-DB despite 4 active NotebookLM-driven projects).

## The 7-section parsing heuristic

`parse_claim_blocks()` walks the markdown line-by-line tracking the most-recent `## ` (h2) heading. Each `### ` (h3) heading starts a new **claim block**, with the h3 title as the block's `section_title`. Code fences (` ``` `) are kept verbatim inside the block.

Fallback: if a file has *no* `### ` headings (some NotebookLM reports just dump prose under each `## Qn`), the parser splits on blank lines under each `## ` section instead. That covers both the `KGC-4 research-output Q1..Q7.md` style (60 h3-defined blocks) and the shorter `vault-meta synthesis.md` style (14 paragraph blocks under 6 h2 sections).

### Failure modes

- **Custom reports with TOC at top**: the table-of-contents block under the first `## ` ends up parsed as a claim block. Filtered out downstream by `pre_filter_block()` because it matches the URL-only or anchor-only heuristic.
- **Frontmatter overflow**: NotebookLM frontmatter occasionally includes long `sources-count:` arrays. `strip_frontmatter()` finds the *second* `---` delimiter to drop it cleanly.
- **Mixed-content reports** (combining NotebookLM citation with vault-author commentary, e.g. KGC-4 research-output): both are extracted. The provenance still points to the original MD file, which Phase-2 review can use to cross-check.

## Pre-filter rule set

After parsing, each claim block runs through `pre_filter_block()`. A block is **dropped** if any of these match:

| Rule | Drops blocks like |
| --- | --- |
| `reference-section` | h2/h3 titled "Felhasznált források", "References", "Kapcsolódó", "Tartalomjegyzék", "Következő action-item" |
| `url-only` | every non-blank line matches `^https?://...` |
| `anchor-only` | ≤2 lines and any line matches "as discussed", "lásd fent", "see section" |
| `question-only` | every non-blank line ends with `?` |
| `no-declarative-verb` | no `is/are/was/were/has/uses/runs/...` (HU+EN) anywhere |
| `too-short` | < 80 chars total |

In testing on the current vault (7 detected reports, 135 raw claim blocks): ~50% drop rate, 67 kept. The large drops are real — many h3 sections under NotebookLM reports are bullet-question lists or pure source-citation footers with no extractable facts.

## Idempotency contract

Three layers of "don't redo work":

1. **Phase-1 request idempotency**: `write_pending_batches()` skips a batch if either its `request.json` OR `response.json` already exists on disk.
2. **Phase-2 dedupe**: in-batch and across-batch dupes (by `sha256(subject|predicate|object)`) are removed before insertion.
3. **`--skip-existing`**: pre-checks `facts.hash` and skips triplets whose hash is already in KO-DB. Use this on cron runs to avoid double-confidence-bumping unchanged claims.

Re-running the script on the same file is therefore safe at every phase — it picks up fresh response.json files and never re-spawns work already pending.

## Two-layer apply gate

Default mode is **dry-run** — extracts, parses, validates, but writes *nothing* to KO-DB.

To write: `--apply` flag AND `VAULT_NB_INGEST_APPLY=1` env var. Either alone falls back to dry-run with a warning. This mirrors the `VAULT_CRYSTALLIZE_APPLY=1` + `VAULT_CRYSTALLIZE_REAL=1` two-layer gate from B-1, with the same "would-have-applied" audit pattern.

## Validation gate (per-triplet)

Each triplet returned by the extraction subagent is checked against:

- **Forbidden subject prefixes** (mirrors `vault-ko-remap-legacy` `FORBIDDEN_SUBJECT_PREFIXES`): `AGENTS.md`, `00-Meta/`, `11.11`, `MEMORY.md`. The KO-DB should never store facts *about* vault meta-files themselves.
- **PII patterns**: email-shape, JWT tokens, `ghp_*`, `AKIA*`, Bearer tokens, SSH private-key markers, `api_key=...`. Triplets where the subject OR object contains any of these are dropped.
- **Predicate vocabulary**: must be one of the 38 predicates from the canonical vocab (B-1 Week 4 `PREDICATE_VOCAB`). Out-of-vocab predicates are dropped, not silently mapped — this avoids polluting the typed-rate metric.
- **Length guards**: subject ≤ 200 chars, object ≤ 500 chars.

## Composition with `vault-ko-ingest`

`vault-nb-ingest` is **additive**, not a replacement.

| Surface | Owner | Source-type tag |
| --- | --- | --- |
| Session Learnings | `11.11crystallize` → `vault-ko-ingest` | `session` |
| ADR decisions | `vault-ko-ingest --file <ADR>` | `adr` |
| Evergreen wikis | `vault-ko-ingest --backfill 11-wiki/` | `wiki` |
| NotebookLM custom-reports | `vault-nb-ingest` | `notebooklm` |
| Manual `vault-ko-add` | direct SQL | `manual` |

All five paths share the same `facts.db` schema, the same 38-predicate vocab, the same `sha256(subject|predicate|object)` hash, the same `confidence` field. Cross-source corroboration via `vault-ko-query --top-k --semantic` (Memgraph bridge) automatically benefits from the new `notebooklm` rows — a fact appearing in both a session AND a NotebookLM-cited synthesis ranks higher than either alone, which is exactly the cross-source ranking signal B-1 Week 3 was designed to surface.

## Recommended cron cadence

Daily at 05:00, between `vault-net-watch` (which may surface fresh deep-research downloads under `10-raw/external/`) and the morning sync:

```
0 5 * * * VAULT_NB_INGEST_APPLY=1 /usr/local/bin/vault-cron-flock \
    vault-nb-ingest /usr/local/bin/vault-nb-ingest --apply \
    --days 1 --skip-existing >/dev/null 2>&1
```

The 24h window catches reports downloaded in the last day; `--skip-existing` keeps the cron idempotent across days. **DO NOT** install before a manual dry-run sweep validates the extraction yield against your current report inventory.

## Operational dashboard

Audit log at `06-Audits/vault-nb-ingest-log.jsonl` — one JSON line per file per run, with `parsed_blocks`, `filtered_blocks`, `triplets_collected`, `new_facts`, and skip-counters. Use it for the same "auto-rate / revert-rate" monitoring that `vault-crystallize-monitor` does for `11.11crystallize`.

## Related

- [[notebooklm-deep-research-custom-report]] — how to produce the source artifacts
- [[notebooklm-cli-gotchas]] — CLI quirks that affect filename conventions
- [[Crystallization-protocol]] — the wider B-1 crystallization pipeline this composes with
- [[sv-02-recursive-self-improvement]] — the GEPA loop that consumes KO-DB facts
