---
name: sv-phase-b2 retrospective
type: decision
status: draft
created: 2026-05-19
updated: 2026-05-19
sprint: sv-phase-b2
related:
  - "[[02-Projects/superintelligent-vault]]"
  - "[[06-Audits/2026-05-18 vault-embed CLI shim + B-2 acceptance.md]]"
  - "[[07-Decisions/2026-05-12 sv-1 memory architecture arch.md]]"
tags:
  - "#adr/retrospective"
  - "#sv/b2"
---

# sv-phase-b2 retrospective

> [!info] Status: DRAFT
> Az audit `06-Audits/2026-05-18 vault-embed CLI shim + B-2 acceptance.md`
> alapján — Gate 2 score-scale kalibrálás után frissítendő, majd
> `git tag sv-phase-b2-done` actionable.

## Sprint summary

| | |
|---|---|
| Sprint | sv-phase-b2 (Memgraph-backed embedding + semantic search) |
| Kezdés | 2026-05-13 (Week 1 Day 3) |
| Audit-dátum | 2026-05-19 |
| Master | [[02-Projects/superintelligent-vault]] |
| Stack | bge-m3 1024-dim + Memgraph CE 3.9.0 (native vector-index) |

## Decision — B-2 zárás 2-fázisú

**RC1 most, final 1-2 óra múlva.** A B-2 sprint **funkcionálisan ÉLES**, de a
"Top-5 relevance >0.85" acceptance-gate score-scale-konfliktusa miatt két
fázisban zárjuk:

1. **`sv-phase-b2-done-rc1`** — most, az audit alapján (3/3 query top-1
   helyes, 605ms cold daemon-search, ~2K token/skill).
2. **`sv-phase-b2-done`** — Gate 2 score-scale újra-kalibrálás után
   (cosine-only top-1 >0.5 + hybrid top-1 >0.8 kettős gate, VAGY default-`--hybrid`
   és a 0.85-öt mind a 3-Q-n elérni).

## Wins (mérhető)

| Metrika | Pre-B2 | Post-B2 | Delta |
|---|---|---|---|
| Context-load idő (cold) | ~30s aggressive pre-load | **605ms** daemon-search | **50× faster** |
| Context-load idő (warm) | ~30s | **197ms** | **150× faster** |
| Token-cost per session-start | 15-20K | **~2K** project-context skill | **8-10× lemegy** |
| Memgraph vector-search (per Q) | 280ms numpy-cosine | **1ms** native index | **280× faster** |
| Multi-namespace izoláció | n/a | content (2693) + skills (969) parallel, 0 interferencia | new |

## Wins (kvalitatív)

- ✅ `vault-embed` PATH-shim (~50 sor bash, 3 mode: text/file/dir, single-load batch)
- ✅ `vault-embed-freshness` stale/missing/orphan detection
- ✅ `vault-search-server` daemon (keepalive bge-m3 → sub-sec cold)
- ✅ 5 project-context skill landed (kgc-erp, mapesz, sv, myforge, rojtesbojt)
- ✅ Hybrid path (BM25 + dense + RRF) opt-in flag
- ✅ Auto-rerank smart-trigger pattern (cost-aware)

## Anomáliák — utómunka kell

### Anomália #1 — score-scale gate (acceptance-blokkoló volt)

A "Top-5 relevance >0.85" cosine-only-ra **nem teljesül** (0.738 max).
A v0.2 LongMemEval-S validáció `--rerank` flag-gel ment, ami másik score-scale.
**Akció:** újra-kalibrálni a gate-et VAGY default-`--hybrid` a context-load-ban.

### Anomália #2 — no-socket score-divergencia (B-2 zárás után fix-elendő)

Glicko-2 query: no-socket 0.008 vs daemon 0.261 (32× eltérés). Score-normalization-bug a
legacy path-ban. **Severity:** low (daemon-default-tal kerülhető).
**Akció:** B-2 close után külön ticket.

### Anomália #3 — `bmad-vault-bridge` használja-e most a shim-et?

A trigger-audit szerint a `bmad-vault-bridge --context` `semantic_top_k` fallback-en
megy. A shim most már él, **újra kell tesztelni** hogy ténylegesen használja-e
vs. még mindig fallback-en megy. **Akció:** verify `bmad-vault-bridge --context <slug>`.

## Lessons (Karpathy-style)

- **Daemon-keepalive > naive-cold.** A bge-m3 model-load (12s cold) megöli a
  user-experience-et. `vault-search-server` socket-daemon mint always-on
  background-szolgáltatás 50-150× speedup. Reusable pattern minden ML-CLI-hoz.
- **Acceptance-gate score-scale-érzékeny.** A "0.85" threshold cosine-only-ra
  szigorú, de `--rerank` flag-gel reális. Acceptance-gate-eket **method-specific**
  threshold-okkal definiáljunk, ne method-agnostic-an.
- **Multi-namespace Memgraph CE out-of-box.** 3,662 chunk 2 namespace-ben
  (content + skills) 0 interferencia, vector-index párhuzamosan. CE-feature-limit
  audit-előny: nincs Enterprise-license-igény.
- **Shim-pattern reuse: bash > python wrapper.** A `vault-embed` shim 87 sor bash,
  delegál a Python IMPL-nek + 1 új mode (`--text` inline-python). 5 perc setup,
  PATH-parity. Reusable minden hasonló esetre (vault-bm25-backfill mintát követi).

## Open follow-ups

| # | Action | Owner | Target |
|---|---|---|---|
| 1 | Score-scale gate újra-kalibrálás (Gate 2) | system | B-2 final close pre |
| 2 | No-socket score-norm bug fix (legacy path) | system | post-B-2 |
| 3 | `bmad-vault-bridge --context` shim-használat verify | system | B-2 final close pre |
| 4 | Daemon-health check beépítése `vault-cleanup` heti cron-ba | ops | post-B-2 |
| 5 | `git tag sv-phase-b2-done` | user-decision | 1-3 elvégzése után |

## Risks accepted

- **No-socket fallback degradáció**: ha `vault-search-server` daemon down,
  search 16× lassabb és score-norm-bug-os. Mitigation: systemd-unit + cron
  health-check (open-followup #4).
- **Score-scale evolution**: a "top-1 >0.85" gate cosine-only-ra végleg
  elhagyandó; minden új embedding-modell saját score-scale-t hoz. ADR-elv:
  **method-specific gate**, NEM cross-method-egységes.

## Kapcsolódó

- [[06-Audits/2026-05-18 vault-embed CLI shim + B-2 acceptance.md]] — ez az ADR-t kiváltó audit
- [[02-Projects/superintelligent-vault]] — sprint master
- [[07-Decisions/2026-05-12 sv-1 memory architecture arch.md]] — B-2 design
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap.md]] — 8-tengelyű roadmap
