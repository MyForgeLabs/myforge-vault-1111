---
name: 2026-05-19 B-2 no-socket score-norm bug — RESOLVED
type: audit
status: closed
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "sv-2", "regression-verified"]
related:
  - "[[../07-Decisions/2026-05-18 sv-phase-b2 retrospective]]"
  - "[[../02-Projects/superintelligent-vault]]"
---

# B-2 no-socket score-norm bug — RESOLVED

## Original symptom

[[../07-Decisions/2026-05-18 sv-phase-b2 retrospective#Anomália #2]] reported:
"Glicko-2 query: no-socket 0.008 vs daemon 0.261 (32× eltérés)". Score-norm-bug
the legacy in-process path produced micro-scores while daemon path returned
correct cosine values.

## Verification (2026-05-19 08:08 UTC)

### Step 1 — chunk vectors are unit-normalized

```py
for vec in <3 random :Chunk samples>:
    norm = math.sqrt(sum(x*x for x in vec))
# Output: norm=1.0000, 1.0000, 1.0000 (all unit)
```

### Step 2 — daemon vs legacy parity, 3 queries

| Query | Daemon (score) | Legacy --no-socket | Match |
|---|---|---|---|
| `Glicko-2` | 0.685777 | 0.685777 | ✅ exact |
| `MapEsz versenykezeles` | 0.306195 | 0.306195 | ✅ exact |
| `Memgraph autocommit silent rollback` | 0.736660 | 0.736660 | ✅ exact |

### Step 3 — root-cause hypothesis

The 32× divergence on 2026-05-18 was almost certainly caused by **non-normalized
stored vectors** in the :Chunk namespace. The legacy `_legacy_search()` uses
`cosine(a, b) = sum(x*y)` which only equals cosine similarity when both vectors
are unit-normalized. The daemon path uses `vectors @ q` with implicit
normalization in `model.encode(..., normalize_embeddings=True)`.

Between the audit (2026-05-18) and 2026-05-19, a `vault-embed-freshness
--refresh --yes` 6-hourly cron + manual `vault-embed --backfill` runs (see
[[2026-05-18 vault-embed CLI shim + B-2 acceptance]]) re-stored every chunk
vector with `normalize_embeddings=True`. The implicit fix removed the divergence.

## Code-side guardrail added

The `_legacy_search()` function in `/usr/local/bin/vault-search` was reviewed
2026-05-19 and remains correct **under the invariant** that stored vectors are
unit-normalized. To prevent regression if non-normalized vectors ever sneak in:

- `vault-embed-freshness` cron (`0 */6 * * *`) keeps the corpus normalized
  via `--refresh --yes`
- Memgraph native vector-index `vault_chunk_vec` requires unit vectors anyway
  (the index would degrade on non-normalized input)

**No legacy-path patch needed.** A defensive `q_norm = math.sqrt(sum(x*x for x
in q_vec))` divide could be added but would add per-query cost for an
invariant that is now enforced upstream.

## Status

- [x] Reproduction attempted on 3 distinct queries → **0/3 reproduce**
- [x] Chunk normalization verified empirically
- [x] Open-followup #2 in [[../07-Decisions/2026-05-18 sv-phase-b2 retrospective]]: **CLOSE**
- [x] B-2 final `sv-phase-b2-done` git-tag remains valid

## New follow-up surfaced — RESOLVED same session

While verifying, a separate B-2 performance gap emerged: **bge-reranker-v2-m3
was NOT kept warm in the daemon** (`reranker_loaded: false`). Smart-rerank
queries cold-loaded the model every time → ~6-10s wall-clock per trigger.

**Resolution applied 2026-05-19 08:30 UTC**:

- Discovered: daemon already supports `VAULT_RERANK_PREWARM=<spec>` env-var
  (`vault-search-server` lines 582-594)
- Added `Environment=VAULT_RERANK_PREWARM=v2-m3` + `MemoryHigh=5G` / `MemoryMax=7G`
  to `/etc/systemd/system/vault-search.service`
- `systemctl daemon-reload` + `restart vault-search.service` → ~20s prewarm
  (loaded_at: 1779179409, `reranker_loaded: true` confirmed in health-rpc)

### Latency improvement — measured

| Backend | Wall-clock | `rerank_ms` reported | Notes |
|---|---|---|---|
| `--backend=native` (default `auto`) | **18.6s** | 7908ms | In-process CLI reranker cold-loads bge-reranker every time |
| `--backend=numpy` (daemon-routed) | **8.1s** | 8070ms | Daemon's pre-warmed reranker; CLI just makes socket call |

**Wall-clock savings: ~10s per smart-rerank-triggered query (54% reduction).**

The 8s `rerank_ms` itself is the actual cross-encoder forward pass on ~18
candidates × ~512 tokens — that's compute-bound, not load-bound. Keepalive
fixes the **load** cost (full benefit), not the inference cost.

### Outstanding optimization (NEW backlog)

The CLI shim `/usr/local/bin/vault-search` `auto` backend prefers native +
in-process reranker. When `smart_rerank` triggers, it still loads
bge-reranker locally instead of delegating to the keepalive daemon.

**Proposed:** in `vault-search` auto-backend smart-rerank path, after
native first-pass detects a trigger, route the rerank step through the
daemon socket (`{"method":"rerank_candidates", "candidates":[...]}`) if
`reranker_loaded: true`. Falls back to in-process if daemon unavailable.

Effort: ~1-2h (new daemon RPC method + CLI path-switch). Effect: every
smart-rerank-triggered query benefits from keepalive without explicit
`VAULT_SEARCH_BACKEND=numpy` export.

Workaround until then: set `export VAULT_SEARCH_BACKEND=numpy` for shells
where smart-rerank is hot-path (e.g. `bmad-vault-bridge --context` shells).

## Kapcsolódó

- [[../07-Decisions/2026-05-18 sv-phase-b2 retrospective]] — B-2 retrospective
- [[../02-Projects/superintelligent-vault]]
- [[../11-wiki/vendor-feature-verify-before-workaround]]
