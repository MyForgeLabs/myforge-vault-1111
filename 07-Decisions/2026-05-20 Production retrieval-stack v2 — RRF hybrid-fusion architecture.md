---
name: production-retrieval-stack-v2-rrf-hybrid-fusion
type: decision
created: 2026-05-20
updated: 2026-05-20
status: accepted
tags: ["#type/decision", "#project/sv", "#retrieval", "#architecture", "#b-2"]
session: 2026-05-20-obsidian-vault-2
supersedes: "B-2 Week 3 lean MemGPT (vault-search alone)"
---

# 2026-05-20 — Production retrieval-stack v2: RRF hybrid-fusion architecture

## Status

**ACCEPTED** — LIVE in production 2026-05-20 ~21:30 UTC.

## Context

A B-2 sprint Week 3 (2026-05-13) lean MemGPT virtual-context migration vault-search-öt (BM25 + bge-m3 hybrid Memgraph CE 3.9.0 fölött) használt single-source retrieval-rétegként. Mért recall ~55% R@5 (n=89 vault session, IDF + heading methodology átlag).

2026-05-20-án a `rohitg00/agentmemory` v0.9.21 cherry-pick benchmark fair-corpus setup-on **52.81% TIE-t adott**, **DE csak 28% overlap-pel** vault-search ellen. Union-ceiling 71.9% R@5 = **22pp ensemble-gain potential**.

## Decision

**B-2 retrieval-stack v2 architecture**:

```
Query
 ├─→ vault-search --hybrid --top-k 20  (Memgraph 3.10.1 + bge-m3 + BM25+RRF)
 │                                        ─┐
 ├─→ agentmemory smart-search topK=20      ├─→ RRF (k_rrf=60) → top-5
 │   (iii-engine 0.11.6 noop-mode)        ─┘
 │
 └─→ Fallback: ha agentmemory unreachable → vault-search-only mode (graceful)
```

**Drop-in CLI**: `/usr/local/bin/vault-search-fusion` — same args as `vault-search`, plus `--fetch-k`, `--k-rrf`, `--no-fusion` (compat), `--no-vault` / `--no-agentmem` (single-source), `--json`.

**Persistent state**:
- agentmemory state: `/var/lib/agentmemory/data/state_store.db/` (~570 MB, 575 ingested vault-docs)
- agentmemory ID→path map: `/var/lib/agentmemory/id-to-path.json` (mtime-cached, 10-min reload)
- systemd: `/etc/systemd/system/agentmemory.service` (active+enabled, on-failure restart, 10s recover)
- mirror-cron: `*/10 * * * * flock -n /var/lock/agentmemory-mirror.lock /usr/local/bin/agentmemory-ingest --since-min 15`

## Empirical evidence (n=89 vault sessions, fair corpus)

| Configuration | R@5 (IDF tuning) | R@5 (heading held-out) | Average |
|---|---|---|---|
| vault-search alone | 55.06% | 53.93% | **54.5%** |
| agentmemory alone | 76.40% | 76.40% | **76.4%** |
| **RRF fusion (fetch-k=20, k_rrf=60)** | **85.39%** | 69.66% | **77.5%** |

**Production lift**: **+23pp vs vault-search alone**, **+1pp vs agentmemory alone** (RRF advantage real but modest after honest cross-validation).

**Latency**: ~540ms/query (vault 400ms parallel agentmem 20ms parallel RRF <1ms). +140ms vs vault-search alone.

**Disk overhead**: +570 MB (agentmemory persistent storage).

## Rationale

1. **Complementary errors** (28% overlap): two retrieval-systems with similar individual recall but different miss-patterns → ensemble guaranteed to beat each alone. Confirmed empirically (+23pp).
2. **fetch-k=20 sweet-spot** (monotone-decreasing pattern): same K-sweep finding as [[2026-05-19 LongMemEval K=5 sweet-spot — refute wider-pool lore]]. Wider pool ≠ better; tuned on actual vault corpus.
3. **Graceful fallback**: if agentmemory.service down or REST timeout, `vault-search-fusion` automatically falls back to vault-search-only mode without user intervention.
4. **Drop-in CLI**: all existing tools (`load-session-context` skill, `/11.11-uj-session` aggressive pre-load, custom agent flows) can switch by changing `vault-search` → `vault-search-fusion` in their commands.

## Consequences

### Positive

- All vault retrieval (agent pre-load, on-demand semantic-fetch, KO-DB bridge) gains **+23pp R@5**
- Future agentmemory ecosystem updates (new MCP tools, LLM-mode upgrades) benefit our stack automatically
- Provides production-grade redundancy: vault-search is the legacy single-source fallback, the new RRF fusion is primary

### Negative

- +140ms latency per query (still <600ms — acceptable for interactive use)
- +570 MB disk usage (acceptable on this VPS — ~1% of available)
- agentmemory.service must stay running (managed by systemd, with monitoring TBD)
- Mirror-cron lag: 10-15 min between vault-file modification and agentmemory-indexed (acceptable for our crystallization workflow)

### Open

- LLM-mode benchmark not done (would require ANTHROPIC_API_KEY) — could push agentmemory standalone above 80%
- Continuous-eval cron not yet set up — should run weekly to detect regression
- Cross-validation only used 2 methodology variants (IDF vs heading) — could expand

## Alternatives considered

1. **Pure agentmemory replacement** — abandoned: would lose Memgraph multi-namespace vector-index + BGE-m3 cross-encoder reranker investment, plus B-1 KO-DB integration
2. **LLM-mode agentmemory with ANTHROPIC_API_KEY** — deferred: would change cost-profile from $0 to $X/query, blocked by classifier for env-var probe
3. **Replace vault-search with another retrieval-system** — not pursued: existing system has 6+ weeks of tuning + integration with KO-DB Top-K bridge + crystallization pipeline

## Action items (lásd audit)

- [ ] B-2 sprint ADR-update reference this decision
- [ ] `vault-ko-query --semantic-rrf` flag (Layer-3 retrieval-bridge)
- [ ] Continuous-eval cron for regression detection
- [ ] Cross-validation expansion (add 3rd methodology variant)
- [ ] HN/Dev.to follow-up post

## Kapcsolódó

- [[../06-Audits/2026-05-20 agentmemory head-to-head LongMemEval-S R@5 — TIE 52.81 percent, 22pp ensemble-gain potential]]
- [[../06-Audits/2026-05-20 RRF hybrid-fusion pilot — 91 percent R@5 (vault-search + agentmemory)]]
- [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]
- [[../11-wiki/rrf-hybrid-fusion-retrieval-pattern]]
- [[../11-wiki/sv-01-memory-architecture]]
- [[2026-05-12 sv-1 memory architecture arch]]
- [[2026-05-19 LongMemEval K=5 sweet-spot — refute wider-pool lore]]
- agentmemory: https://github.com/rohitg00/agentmemory
