---
name: Triangulation skeleton — 100-fact calibration audit
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "ko-db", "memgraph", "triangulation", "nli", "skeleton", "calibration"]
related: ["[[../11-wiki/triangulation-score-pattern.en]]", "[[2026-05-19 SV new development ideas brainstorm]]"]
status: skeleton-baseline
---

# Triangulation skeleton — 100-fact calibration audit

`vault-ko-triangulate` (brainstorm idea #19) — first 100-fact baseline run on 2026-05-19.

## What this is

A CLI that adds a *semantic* corroboration score to each KO-DB triplet, orthogonal to the existing string-match-based cross-source-corroboration. For each `(subject, predicate, object)` it forms a hypothesis sentence, fetches related chunks via Memgraph (`Chunk.text/title CONTAINS subject`), and rerank-scores them with `bge-reranker-v2-m3` via the warm `vault-search-server` daemon. The max single-chunk score is the **triangulation_score**.

Source: `/root/obsidian-vault/.vault-ko/scripts/vault-ko-triangulate.py` (symlinked to `/usr/local/bin/vault-ko-triangulate`). Concept doc: [[../11-wiki/triangulation-score-pattern.en]].

## Calibration sample

Command:

```
vault-ko-triangulate --from-db --top-k 100 --json > /tmp/triangulate-100.json
```

Sampling order: `ORDER BY confidence DESC, id ASC LIMIT 100` — i.e. the 100 highest-confidence facts at the head of the table. All 100 sample facts are `source_type=wiki`.

### Histogram (100 facts)

| Verdict | Score range | Count | Share |
|---|---|---|---|
| **support** | ≥ 0.65 | 21 | 21 % |
| **weak** | 0.40–0.65 | 4 | 4 % |
| **neutral** | 0.20–0.40 | 4 | 4 % |
| **contradiction** | < 0.20 | 10 | 10 % |
| no-evidence | (n_chunks = 0) | 61 | 61 % |
| daemon-down | (socket error) | 0 | 0 % |

- Avg score across **all** 100: **0.228**
- Avg score on the **39 with-chunks subset**: **0.505**
- Elapsed: **394 s** (3.94 s/fact) on this host

### Interpretation

- **21 % support** is healthy — these are facts the surrounding wiki text directly entails. Examples (score ≥ 0.93):
  - `subagent-fanout has_cost "$0 marginal cost"` → 0.97
  - `subagent-fanout avoids "Anthropic API key requirement"` → 0.94
  - `Single-item playlist avoids "scheduled rotation timer"` → 0.94
  - `cross-document reasoning requires "single agent"` → 0.93
- **10 % contradiction** is the most interesting bucket — it's a mix of three failure modes:
  1. **Genuinely off-topic chunks** that happen to mention the subject string (~50 % of contradictions).
  2. **Bad ingestion** — fact extracted from a side-remark that the main chunk does not assert (~30 %).
  3. **Real contradictions** where the chunk asserts the opposite predicate-object (~20 %; e.g. `state-machine work avoids subagent-fanout` scores 0.00 because the chunk recommends *using* subagent-fanout for this case).
- **61 % no-evidence** dominates the distribution. Two structural causes:
  1. The current `Memgraph.Entity-MENTIONS-Chunk` relation is **empty** (0 edges). The retrieval falls back to text-CONTAINS on the subject string, which fails when the subject is a hash-style ad-hoc identifier (`ACCENTS_MAP`, `wpdb->update`, `--with-context flag`).
  2. KO-DB contains facts about facts (meta-claims about session events) whose subject literally does not appear in long-form wiki/session prose.

## One unexpected finding

The fact

```
Magyar fuzzy search | avoids | MiniSearch dependency
```

scored **0.16** (contradiction). Looking at the matched chunk, the wiki on `hungarian-fuzzy-search` discusses MiniSearch as an *option that was considered and rejected*, but the surrounding paragraph spends more text on "MiniSearch is the standard choice for X" than on "we avoid it because Y". The reranker correctly read "this passage is about MiniSearch as a recommended tool" → low score for the `avoids` predicate.

**This is exactly the contradiction-detection signal we want.** A pure string-match would have flagged this as well-corroborated (5 distinct sources mention "Magyar fuzzy search"). The triangulation score catches that the wiki's stance is ambiguous and the `avoids` direction is not directly asserted.

## Memgraph reachability on this host

**Yes.** Bolt :7687, 4,488 Chunk nodes, 12,778 Entity nodes. `vault-search-server` socket healthy (`/run/vault-search.sock`, ~237 ms search-rpc round-trip with smart_rerank).

Caveat: `Entity-MENTIONS-Chunk` count is 0 — only `Entity↔Entity` relations exist. Retrieval relies entirely on the `Chunk.text/title CONTAINS subject` fallback, which is the weakest path. **Backfilling the MENTIONS edges is the single highest-leverage improvement** for the next iteration.

## Cost projection — full KO-DB scan

- **Per-fact:** ~4 s on this host (1 Memgraph query + 1 daemon-RPC search call, both warm).
- **13,801 facts:** ~55,000 s ≈ **15 hours** single-threaded.
- **With 4-way parallelism on the daemon:** ~4 hours (the daemon's reranker is the bottleneck and is not currently parallel-safe at the search-RPC level; would need a small batching change).
- **In daemon-RPC seconds:** 13,801 × ~0.5 s reranker call ≈ **~7,000 RPC-seconds** of actual reranker work; the rest is Memgraph + Python overhead.

For a recurring nightly pass, a 4-hour parallelized run is feasible. For a per-ingest hot path, the latency is unacceptable — would need to either (a) cache the score, (b) only triangulate `support`-candidates from G-Eval, or (c) batch facts by subject and reuse the Memgraph fetch across multiple facts on the same subject.

## Skeleton-status — known gaps

| Gap | Impact | Fix |
|---|---|---|
| No NLI directional signal | Cannot distinguish "support" from "off-topic-mention" at the boundary | Swap reranker for `cross-encoder/nli-deberta-v3-base` (Option A) |
| No ALIAS expansion | `Memgraph CE` doesn't match chunks talking about `Memgraph` | Walk `Entity-[:ALIAS_OF]-Entity` before chunk-fetch |
| No MENTIONS edges | 61 % no-evidence at 100-fact sample | Backfill `Entity-MENTIONS-Chunk` via NER pass on chunk text |
| No predicate-direction-aware hypothesis | `avoids` and `supports` produce nearly-identical hypothesis sentences in some cases | Predicate template lib with negation-aware NL forms |
| No per-statement Memgraph timeout | Relies on small LIMIT to bound runtime | Use connection-level timeout when driver supports it |
| Pairwise reranker is not a true pairwise call | We re-issue a daemon `search` and filter results to candidate chunks; some candidate chunks never appear in the top-50 → 0 score | Add `method=rerank_pair` to the daemon (small change) |

## Verdict thresholds — keep or tune?

The current thresholds (0.65 / 0.40 / 0.20) yield a usable distribution: 21 % support, 14 % wider-than-neutral (weak + neutral), 10 % contradiction. If we tightened `support` to ≥ 0.70 the count would drop to ~15 %, which is still in the actionable range. **Recommendation:** keep the defaults; revisit after backfilling MENTIONS edges so the 61 % no-evidence drops below 30 %.

## Files created

- `/root/obsidian-vault/.vault-ko/scripts/vault-ko-triangulate.py` (≈ 16 KB)
- `/usr/local/bin/vault-ko-triangulate` → symlink to the above
- `/root/obsidian-vault/11-wiki/triangulation-score-pattern.en.md` (≈ 5 KB)
- `/root/obsidian-vault/06-Audits/2026-05-19 Triangulation skeleton.md` — this file

## Smoke tests run

| Test | Exit code | Time |
|---|---|---|
| `vault-ko-triangulate --help` | 0 | < 0.1 s |
| `vault-ko-triangulate --subject "Memgraph CE" --predicate "is_a" --object "graph database" --markdown` | 0 | ~3 s — score 0.58 (weak) |
| `vault-ko-triangulate --from-db --top-k 50 --json \| python3 -c "..."` | 0 | 204 s — avg 0.228 |
| `vault-ko-triangulate --from-db --predicate "uses_database" --top-k 10` | 0 | 52 s |
| `vault-ko-triangulate --from-db --top-k 100 --json` | 0 | 394 s |

All five pass. The triangulation pipeline is live in skeleton form.
