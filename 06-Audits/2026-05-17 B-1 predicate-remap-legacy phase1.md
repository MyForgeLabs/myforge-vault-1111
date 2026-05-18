---
name: B-1 predicate-remap-legacy Phase 1 (regex)
type: audit
tags: ["#type/audit", "#project/sv", "sv-1", "predicate-vocab", "remap"]
created: 2026-05-17
updated: 2026-05-17
status: dry-run
generated_by: vault-ko-remap-legacy
---

# B-1 predicate-remap-legacy Phase 1 (regex) audit

> Phase 2.3 (predicate-vocab 21 → 38) follow-up. Re-maps the legacy
> dumping-ground `has_value` + `uses` predicate-facts to the typed
> alternatives via deterministic regex/substring rules.

## Mode

- **DRY-RUN (no DB write)**
- Phase: regex (Phase 1)
- DB: `/root/obsidian-vault/.vault-ko/facts.db`

## Scanned

- Total facts scanned: **3822**
- `has_value` facts: **1938**
- `uses` facts: **1884**

## has_value remap distribution

Remapped: **373** / 1938 = **19.2%**
Stayed `has_value` (miss): **1565** (80.8%)

  - `has_count` → **149** (7.7%)
  - `has_cost` → **88** (4.5%)
  - `has_color` → **25** (1.3%)
  - `has_port` → **23** (1.2%)
  - `has_path` → **18** (0.9%)
  - `has_version` → **18** (0.9%)
  - `has_url` → **17** (0.9%)
  - `has_date` → **15** (0.8%)
  - `has_threshold` → **12** (0.6%)
  - `has_status` → **5** (0.3%)
  - `has_string_value` → **3** (0.2%)

## uses remap distribution

Remapped: **388** / 1884 = **20.6%**
Stayed `uses` (miss): **1496** (79.4%)

  - `uses_model` → **77** (4.1%)
  - `uses_framework` → **58** (3.1%)
  - `uses_flag` → **56** (3.0%)
  - `uses_protocol` → **55** (2.9%)
  - `uses_runtime` → **54** (2.9%)
  - `uses_database` → **34** (1.8%)
  - `uses_library` → **24** (1.3%)
  - `uses_algorithm` → **17** (0.9%)
  - `uses_endpoint` → **13** (0.7%)

## Overall

- **Phase 1 deterministic remap-rate: 19.9%** of dumping-ground facts.
- Remaining for Phase 2 LLM-fanout: **3061** facts.

## Phase 2 fanout-plan (skeleton, NOT executed)

- Remaining facts: **3061**
- Batch-size: 300 facts/subagent
- Parallelism: 8× concurrent subagents
- Total batches: **11**
- Waves (batches / parallelism): **2**
- Estimated runtime: **~16 min**
- Estimated API cost: **$0** (subagent-fanout via parent agent)

Trigger when scheduled: a future session manually invokes the
Claude Code subagent-fanout protocol (see `11-wiki/claude-code-subagent-fanout.md`).

## Sample remap decisions (first 15)

| fact_id | subject | old_pred | new_pred | object |
|---|---|---|---|---|
| 3 | Touch-kiosk idle timeout | `has_value` | `has_string_value` | "3 * 60 * 1000 ms" |
| 8 | Confirmed state screen | `has_value` | `has_string_value` | "10 seconds" auto-timeout |
| 13 | Touch-kiosk idle timeout origi | `uses` | `uses_runtime` | KGC-Bérlés Tizen Samsung 1080x1920 totems |
| 15 | Magyar fuzzy search | `uses` | `uses_algorithm` | per-token Levenshtein distance |
| 18 | Magyar fuzzy search | `has_value` | `has_count` | 200 lines of TypeScript |
| 21 | KGC dataset | `has_value` | `has_count` | 292 machines |
| 22 | Fuzzy search per-query perform | `has_value` | `has_count` | ~1ms per query per element |
| 27 | Levenshtein implementation | `uses` | `uses_algorithm` | two-row DP optimization |
| 35 | Levenshtein matching max dista | `has_value` | `has_count` | 2 |
| 46 | Magyar fuzzy search | `uses` | `uses_algorithm` | 3 exports (normalize, levenshtein, scoreMatch) |
| 84 | error event fallback | `has_value` | `has_count` | 2000ms duration |
| 90 | subagent-fanout | `has_value` | `has_cost` | $0 marginal cost |
| 105 | batch size 50 files | `has_value` | `has_count` | ~3 min per-agent duration |
| 127 | direct Haiku 4.5 API | `has_value` | `has_cost` | ~$0.0001-0.0002 per file |
| 128 | direct Haiku 4.5 API for 267 f | `has_value` | `has_cost` | ~$0.05-0.10 total |

## Sample misses → Phase 2 fanout candidates (first 15)

| fact_id | subject | predicate | object |
|---|---|---|---|
| 14 | Magyar fuzzy search | `uses` | accent-strip map normalization |
| 24 | ACCENTS_MAP | `uses` | static character map for Hungarian accents |
| 28 | Exact word-prefix match | `has_value` | score 0 |
| 29 | Exact mid-word substring match | `has_value` | score 1 |
| 30 | Levenshtein distance 1 match | `has_value` | score 5 |
| 31 | Levenshtein distance 2 match | `has_value` | score 12 |
| 36 | Tie-breaker | `uses` | target length / 100 (max 0.5) |
| 47 | Tokenization | `uses` | whitespace split with empty-filter |
| 48 | Exact substring start-of-word  | `uses` | preceding char is space or hyphen |
| 57 | video loop reliability | `uses` | belt-and-suspenders pattern (v.loop=true + ended-listener) |
| 58 | ended-listener loop fallback | `uses` | v.currentTime=0 + v.play() |
| 63 | mixed-content diagnosis | `uses` | F12 Console Mixed Content warning |
| 64 | Multer array uploader | `has_value` | default count limit 50 |
| 69 | frontend batch upload | `has_value` | BATCH_SIZE 50 |
| 71 | browser connection-pool | `has_value` | ~6 parallel connections |

## Next steps

1. Review this dry-run output.
2. If acceptable, re-run with `--apply` to commit the **761** regex-remap.
3. Schedule Phase 2 fanout (separate session): 3061 facts × 8× parallel × 300/batch.
4. After both phases: re-run `vault-ko-conflicts-audit` to verify `LOW` rate dropped and `HIGH` rate rose on real drift.

## Kapcsolódó

- [[06-Audits/2026-05-17 predicate-vocab expansion 21 to 35-40]] — Phase 2.3 audit (parent)
- [[11-wiki/claude-code-subagent-fanout]] — fanout protocol for Phase 2
- [[02-Projects/superintelligent-vault]] — B-1 axis
- audit-log JSONL: `.vault-ko/remap-log.jsonl`
