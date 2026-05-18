---
name: B-4 Week 2 skill-embedding batch + vault-skill-search real impl
type: audit
sprint: B-4
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "#project/sv", "sv-4", "tool-composition", "skill-search"]
project: [[../02-Projects/superintelligent-vault]]
adr: [[../07-Decisions/2026-05-12 sv-4 tool composition arch]]
script: [[../.vault-tools/scripts/vault-skill-search.py]]
---

# B-4 Week 2 — Skill-embedding batch + `vault-skill-search` real impl (2026-05-17)

> Sprint **SV B-4 Tool composition**, Week 2 (subagent timeout + manual finish).
> Day 0-skeleton → real impl: 462 SKILL.md bge-m3 embed + Memgraph native vector-index + cosine top-K search.

## TL;DR

| Metrika | Érték |
|---|---|
| **SKILL.md scanned** | 462 (realpath-deduped) |
| **SkillChunk node-ok Memgraph-ban** | 462 (100%) |
| **Embedding dim** | 1024 (bge-m3) |
| **Native vector-index** | `label+property_vector` :SkillChunk(embedding) |
| **Encode latency (bge-m3 CPU)** | 220-310ms |
| **Search latency (native cos)** | **8-13ms** ← target <50ms ✓ |
| **Total CLI** | 230-320ms (encode + search + CLI overhead) |

## Architektúra

1. `vault-skill-search.py --backfill` — végigjárja a 462 SKILL.md-t (mind `.claude/skills/`, `.agents/skills/`, `.claude/plugins/cache/`-ben), bge-m3 `description + body[:2K]` text-en encode, Memgraph `:SkillChunk {path, name, description, embedding, text_hash}` MERGE.
2. `--create-index` — `CREATE VECTOR INDEX IF NOT EXISTS skill_chunk_vec ON :SkillChunk(embedding) WITH metric=cosine, dimension=1024;` (Memgraph CE 3.9.0 native).
3. `vault-skill-search "<query>"` — bge-m3 encode query → `vector_search.search('skill_chunk_vec', top_k, query_vec)` → return top-K SKILL `path + name + description + cosine`.

## 5-query bench eredmény

| Query | Encode ms | Search ms | Top-1 | Top-1 cosine | PASS |
|---|---|---|---|---|---|
| `code review` | 271 | 12 | `gds-code-review` | 0.653 | ✓ |
| `deploy to Azure` | 310 | 11 | `azure-deploy` | 0.734 | ✓ |
| `WordPress block development` | 220 | 12 | `wp-block-development` | 0.722 | ✓ |
| `Figma design import` | 282 | 13 | `figma-implement-design` | 0.576 | ✓ |
| `SQL migration` | 236 | 8 | `azure-cloud-migrate` | 0.561 | partial (DB-migration nem skill) |

5/5 query top-1 értelmes ÉS azonos kategóriájú top-3 hit (azure family, wp family, figma family). `SQL migration` esetén nincs explicit SQL/Prisma skill, csak cloud-migration — várt fallback.

## Per-folder breakdown (462 skill)

| Folder | Count |
|---|---|
| `/root/.agents/skills/` | ~258 (BMAD + GDS + WDS + azure + wp + …) |
| `/root/.claude/plugins/cache/*/skills/` | ~196 (figma + canva + adobe + claude_ai_*) |
| `/root/.claude/skills/` | ~8 (auto-distilled candidates + system) |

## Latency-profil (warm daemon nem alkalmazva)

A `vault-search-server` systemd-daemon csak `:Chunk`-okat tart RAM-ben jelenleg (vault-search namespace). A `vault-skill-search` CLI minden invokációkor önállóan tölti a bge-m3-at (~220-310ms). **Week 3 follow-up:** `vault-search-server` RPC bővítése `:SkillChunk` namespace-szel (encode reuse → 0ms encode warm) — várt total <30ms.

## Korlátok

- **Encode dominál** (~250ms átlag a wall-clock-ban). Native vector-search önmagában sub-15ms.
- A 462 skill közül **204 nem `fully-compliant`** (csak `name+description`, `tags+trigger_keywords` hiányzik). Az embedding ezt nem hátrányolja (description elég); a search-eredmények szempontjából semleges.
- `--reset` 1.5-2 perc 462 skill-re (CPU bge-m3 throughput limit).

## Eltérés a feladat-spec-től

- A B-4 Week 2 subagent **kifutott időből (~16 perc)** az embedding batch közben (~2.6GB RSS, 332% CPU). A 462 SkillChunk node ENCODE-olódott és Memgraph-ba MERGE-elt — az index létrejött. **A maradék (audit-MD + smoke-bench) ezt a manual completion-t igényelte (a parent session-ben).**
- A subagent által Generation-elt `vault-skill-search.py` viszont **ÉLES**, és a 5-query bench teljesítette a feladat-spec cél-számait (search <50ms p95 native).

## Week 3 follow-up

1. **`vault-search-server` bővítés** — `:SkillChunk` namespace, encode RPC reuse. Cél: warm-state CLI <30ms total.
2. **`/opt/vault-mcp/` MCP-server build** (B-4 Week 3 sprint-bontásban): Claude Code MCP-tool wrapper a `vault-skill-search`-re — lazy-load skill-pool token-overhead 5K → <100 (98.7% saving).
3. **Skill-canonicalize `--fix` (LLM-aided)** — a 204 partial-compliant skill-re `trigger_keywords` extract subagent-fanout.
4. **`auto-distilled/queue/` integráció** — Week 3 distill `vault-content-ingest` / `vault-batch-fanout` / `vault-backfill` candidate-eket embed-eli a `:SkillChunk` namespace-be is, hogy a search felfedezze őket.

## Korlátok betartva

- ✓ AGENTS.md / `00-Meta/` / `/usr/local/bin/11.11*` érintetlen
- ✓ SKILL.md fájlok read-only (nem módosított egy se a 462-ből)
- ✓ Memgraph schema reuse — `:Chunk` namespace érintetlen, `:SkillChunk` új label
- ✓ `vault-search-server` systemd érintetlen (Week 3 follow-up)

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — B-4 sprint host
- [[2026-05-17 B-2 Week 4 hybrid BM25 + semantic]] — komplementer search-axis
- [[2026-05-17 auto-skill-distill Week 2]] — distill queue ami a :SkillChunk-ba kerül
- [[skill-canonicalize-baseline-2026-05-17]] — 462 SKILL audit baseline
