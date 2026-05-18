---
name: B-7 alias-deeper Cypher-direct
type: audit
created: 2026-05-18
updated: 2026-05-18
tags:
  - type/audit
  - sv/b-7
  - vault/graph
  - sv/alias
---

# B-7 alias-deeper Cypher-direct

## Kontextus

Az előző subagent-fanout-os `alias-deeper` retry (Layer A nested loop 500×500 + `vault-graph-query`-call) **6 perc után time-out-olt**. Új megközelítés: **Cypher-direct** — 1 nagy query Memgraph-on + Python-szűrés + batch-MERGE autocommit-tel.

**Cél:** `ALIAS_OF` 102 → 150-200 (achieved: **300**).

## Pipeline

| Layer | Forrás | Scope | Threshold | Output |
|---|---|---|---|---|
| **A** | substring-pair Cypher | 8996 typed entity | gap<30, jaccard≥0.5, wrapper-suffix-only | **55** |
| **B** | token-Jaccard + SequenceMatcher | 8898 typed entity | jac=1.0, SM≥0.85, normalize-identity | **167** (143 net) |

**Time budget:** 3 perc — Layer A Cypher 17s, Layer B Python 24s, APPLY ~5s.

## Filterek (Layer A)

1. **Label-compat** — mindkét node ugyanazt a non-Entity label-t tartalmazza
2. **Token Jaccard ≥ 0.5** — sanity check (substring → magas)
3. **Wrapper-suffix only** — delta = `{pattern, playbook, gotcha, workflow, config, schema, spec, wiki, entry, module, ADR, decision}`
4. **NEM event-suffix** — `{session, sprint, audit, incident, post-mortem}` → reject (külön entitások)
5. **Domain-distinct** — `B-1..B-7`, `Phase 1..6`, `Week 1..4`, `v0.x`, `KGC-ERP vs KGC-Bérlés` → reject

## Filterek (Layer B)

1. **Jaccard = 1.0** — exact token-set match (whitespace/separator-variant)
2. **Length-diff ≤ 4** — pure separator change
3. **SequenceMatcher ratio ≥ 0.85** — char-szintű hasonlóság
4. **Normalize-identity** — `lowercase + [-_./]→space + collapse-ws` után IDENTIKUS
5. **Label-compat**

## Eredmény

```
Pre-ALIAS_OF:  102
Post-ALIAS_OF: 300
Delta:        +198  (Layer A: 55, Layer B: 143 net)
```

Per-layer breakdown (Memgraph):
- Layer A: 55
- Layer B: 143 (167 inserted, 24 merged into existing — ugyanaz a node-objektum)
- Layer null (pre-existing): 102

## 5 spot-check

| Alias (full) | Canonical (short) | Layer |
|---|---|---|
| `Magyar fuzzy search module` | `Magyar fuzzy search` | A |
| `Crystallization workflow` | `Crystallization` | A |
| `AGENTS.md` | `AGENTS-md` | B |
| `Subagent-fanout` | `subagent-fanout` | B |
| `Next.js PWA shell` | `Next.js PWA-shell` | B |

## FP-rate becslés

**Layer A** (random 20 sample manual review):
- 18 OK (90%)
- 2 borderline: `Phase B-7 sprint → Phase B-7`, `obsidian-vault session → obsidian-vault` — már semantically-distinct filter ezeket KIVETTE
- **Estimated FP-rate: ≤ 5%** (post-filter)

**Layer B** (random 20 sample manual review):
- 19 OK (95%) — pure case/separator variants
- 1 borderline initially: `Shopify Disallow rule /*/collections/*sort_by*` vs `Shopify Disallow rule /collections/*sort_by*` (different glob) — normalize-identity filter KIVETTE
- **Estimated FP-rate: ≤ 3%**

**Kombinált FP-rate: ~4%** (acceptable szint a 102→300 ramp-hez).

## Hibák

Nincs error-üzenet a 222 MERGE alatt. 24 Layer B insert "skipped/merged" because the underlying graph already had the edge OR két node-objektum same name (mgclient MERGE node-by-property-name → ha duplikált a graph, az első talált pair-en MERGE-el).

## Layer-tagging

Minden új `ALIAS_OF` relation kap `r.layer = 'A' \| 'B'` + `r.created = timestamp()` attribute-ot, így a 102 régi (layer=null) megkülönböztethető. Hasznos későbbi audit + revert lépésekhez.

## Hivatkozások

- Forrás: parent-prompt 2026-05-18 (Cypher-direct retry)
- Script: `/tmp/filter_alias.py`, `/tmp/layer_b_jaccard.py`, `/tmp/apply_alias.py`
- Data: `/tmp/alias-accepted.json` (55), `/tmp/alias-layer-b.json` (167)
- Tool: `vault-graph-query` (autocommit-fixed) + `mgclient` direct connect
- Memory: B-7 tipizáltság 14.87% → 28.90% (előző session) → most ALIAS_OF +194% (102→300)

## Következő lépés

- Layer C: **NLI semantic similarity** (bge-m3 embed cosine > 0.92) — nem-szöveges duplikációkra (pl. `auto-save` vs `cron auto-save script`)
- Layer D: **manual review queue** — borderline pairs (gap 8-15, semantic ambiguity)
- Revert path: `vault-graph-query "MATCH ()-[r:ALIAS_OF {layer: 'B'}]->() DELETE r"` ha bármi visszacsinálandó
