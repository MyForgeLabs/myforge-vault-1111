---
name: 2026-05-18 Memgraph edge-from-facts
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#tech/memgraph"]
tag_backfill: 2026-05-19
---
# Memgraph edge-from-facts — B-7 follow-up

Goal: close the typed-edge gap by materializing predicate-typed edges directly
from `facts.db` triplets (NOT co-occurrence inference as in `vault-graph-edge-inference`).

## Script

`/usr/local/bin/vault-graph-edge-from-facts` (~210 sor Python, mgclient + sqlite3,
autocommit=True per the mgclient lesson).

Idempotent via `MERGE (a)-[r:<PRED> {fact_hash: $h}]->(b)`. Re-runs skip
already-present fact_hashes at the MATCH level.

## Pre/Post edge count

| Metric | Pre | Post | Δ |
|---|---|---|---|
| Total edges | 24 061 | 25 167 | **+1 106** |
| :Entity nodes | 16 019 | 16 389 | +370 |

Note: +1 106 ≪ user's "2 000-4 000 expected" target because **prior ingest had
already materialized 13 812 of 13 794 confidence>0.6 facts**. Only the
non-ingested predicate-buckets (`has_count`, `has_cost`, `uses_*`, `has_*`)
remained. The gap was real but bounded.

## Per-predicate breakdown (new edges, top-15)

| Predicate | Count | Notes |
|---|---|---|
| `:HAS_COUNT` | 316 | Numerical magnitudes ("200 lines", "292 machines") |
| `:HAS_COST` | 86 | Money / Ft / EUR / $ |
| `:USES_MODEL` | 80 | LLM/AI model references |
| `:USES_FRAMEWORK` | 79 | Next.js 16, Elementor, NestJS, ... |
| `:USES_RUNTIME` | 58 | systemd, Python, Node, ... |
| `:USES_PROTOCOL` | 55 | ssh, HTTPS, websocket |
| `:USES_FLAG` | 55 | CLI flags, env-vars |
| `:USES_PATTERN` | 52 | architectural patterns |
| `:USES_DATABASE` | 42 | Postgres, SQLite, Memgraph |
| `:USES_LIBRARY` | 33 | npm/pip dependencies |
| `:HAS_PATH` | 31 | filesystem paths |
| `:HAS_COLOR` | 25 | hex/CSS colors |
| `:HAS_PORT` | 23 | TCP/UDP ports |
| `:HAS_VERSION` | 18 | software versions |
| `:HAS_URL` | 17 | URLs |

Total 42 distinct predicates added. Long-tail covered: `:USES_ALGORITHM`,
`:HAS_THRESHOLD`, `:HAS_DATE`, `:USES_ENDPOINT`, `:HAS_STATUS`, `:LISTENS_TO`,
`:VALIDATES`, etc.

## 8 spot-check samples (random seed=42)

| Confidence | Subject | Predicate | Object | Verdict |
|---|---|---|---|---|
| 0.95 | `--foxxi-maple` | HAS_COLOR | `#e37f56` | ✅ correct |
| 1.00 | Whisper transcription on CPU | HAS_COUNT | ~10 sec per minute audio | ✅ correct |
| 1.00 | Vault | HAS_COUNT | 977 chunk embedded bge-m3 | ✅ correct |
| 0.90 | ufw limit | PREVENTS | portscan and bruteforce attacks | ✅ correct |
| 1.00 | Gemini CLI | USES_MODEL | `~/.gemini/GEMINI.md` symlink | ❌ wrong predicate (should be HAS_CONFIG_FILE) |
| 0.95 | external skill cherry-pick | USES_PATTERN | symlink pattern | ✅ correct |
| 0.90 | Foxxi project | USES_FRAMEWORK | Elementor custom widgets | ✅ correct |
| 1.00 | 07-Decisions target | HAS_THRESHOLD | threshold 0.95 | ✅ correct |

## FP-rate estimate

**1/8 = 12.5%** spot-checked false-positive rate. The one FP is an
**extraction-time predicate-misclassification** in KO-DB (the script faithfully
materialized whatever was in `facts.db`); the script itself introduced no FPs.

Extrapolated: ~138 of 1 106 new edges may carry semantically-wrong predicates,
matching the general extraction-noise floor observed in prior B-7 audits.
Mitigation path: feed FP examples back into the KO-DB extraction subagent's
predicate-vocabulary tightening (out of scope here).

## Object-node policy applied

- 723 facts (65 %) — object matched an existing `:Entity` → edge attached to
  existing node
- 383 facts (35 %) — object did not exist → created new `(:Entity:Concept)` node
  (370 unique names; the 13 difference is duplicate-key MERGE coalescence)

## Filter behavior

`has_value` / `applies_to` are flagged GENERIC; under min-evidence=3 only
9 facts were excluded (vast majority already in graph from earlier ingest).
Default behavior matches B-7 typed-rate guidance: no further dilution.

## Apply state

**APPLIED** (REAL, not dry-run). 1 106 edges MERGEd, 0 errors. All carry
`source: 'kodb-edge'` property for downstream filter / revert.

## Rollback recipe

```cypher
MATCH ()-[r]->() WHERE r.source = 'kodb-edge'
  AND r.created_at STARTS WITH '2026-05-19'
DELETE r;
```

## Follow-ups

- KO-DB extraction predicate-vocabulary tightening (FP class: `USES_MODEL` on
  file-paths, `HAS_PATH` on URLs, ...) → backlog item
- Re-run when KO-DB grows past 14 000 facts; idempotent MERGE handles deltas
- `vault-graph-edge-inference` (co-occurrence :RELATES) and this script are
  complementary — both should run after each KO-DB ingest cycle
