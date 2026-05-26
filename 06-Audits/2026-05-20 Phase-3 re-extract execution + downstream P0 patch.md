---
name: Phase-3 re-extract execution + downstream P0 patch
type: audit
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/audit", "#project/sv", "memgraph", "extraction-quality", "phase-3", "p0-fix"]
status: Phase-3 fanout LANDED + KO-DB ingest LANDED + vault-graph-extract P0 fix LANDED. Jaccard gate ≥0.05 NEM teljesült (orthogonal-vocab structural limit).
---

# Phase-3 re-extract execution + downstream P0 patch

## TL;DR

**Phase-3 selective re-extract subagent-fanout (8× parallel) LANDED**: 68 v3-vocab response.json írva, KO-DB +2,034 fact (13,801 → 15,835). Közben **vault-graph-extract** felfedte a #34 hash-refactor MÁSODIK downstream regresszióját (`SELECT ... provenance FROM facts` → schema-error). Patch ÉLES (post-#34 schema-detect + GROUP_CONCAT). Memgraph re-extract után **Jaccard 0.0078 → 0.0070** — Acceptance gate ≥0.05 **NEM teljesült**, megerősíti a 2026-05-19 Phase-3-result audit predikcióját: orthogonal-vocab structural limit, Option-B tree-sitter pre-pass szükséges.

## Subagent-fanout execution

| Batch | Files | Triples | Wall-clock |
|---|---|---|---|
| 0 | 9 | 300 | ~12 min |
| 1 | 9 | 254 | ~12 min |
| 2 | 9 | 223 | ~13 min |
| 3 | 9 | 243 | ~12 min |
| 4 | 8 | 217 | ~11 min |
| 5 | 8 | 187 | ~11 min |
| 6 | 8 | 240 | ~11 min |
| 7 | 8 | 244 | ~11 min |
| **Total** | **68** | **1,908** | parallel ~13 min |

**Vocab-v3 (anti-noise-7) compliance**: ≤60 char / ≤4 token subject cap, no quoted-string subjects, no port/URL/hex/path as subject, single-mention confidence ≤0.5 honored, typed-predicates preferred over `has_value`/`uses` fallbacks throughout.

## KO-DB ingest

```
vault-ko-pending --process-ready --yes
Done: 151/151 processed, ~0 new facts logged, 0 failure(s).
Real time: 11.7 s
```

| Metric | Pre | Post | Δ |
|---|---:|---:|---|
| `facts` row count | 13,801 | 15,835 | **+2,034** |
| `fact_provenance` row count | 13,801 | 15,957 | **+2,156** |
| Multi-provenance facts | 0 | 122 | +122 |

A "~0 new facts logged" stdout-üzenet **misleading** — a `vault-ko-pending.py --process-ready` aggregálja a `vault-ko-ingest` per-file kimeneteket egy single message-be, de a tényleges DB-mutáció +2,034 sor.

## Downstream P0 BUG #2: `vault-graph-extract`

A #34 hash-refactor MÁSODIK csendes downstream regresszióját **fedeztük fel** (az első a `vault-ko-ingest.upsert_fact:321` volt, 2026-05-19 délutáni P0-fix).

### Symptom

```
$ vault-graph-extract --dry-run
Traceback (most recent call last):
  File "/usr/local/bin/vault-graph-extract", line 247, in <module>
    main()
  ...
  File "/usr/local/bin/vault-graph-extract", line 72, in load_facts
    cur.execute(
sqlite3.OperationalError: no such column: provenance
```

### Root cause

A `load_facts()` SELECT-je `SELECT ... provenance FROM facts`-szel hivatkozott a #34-után eltávolított `provenance` oszlopra. **3 helyen volt provenance-referencia** a scriptben (sorok 19, 73, 183, 190), de csak a SELECT crash-elte azonnal — a setter (`r["provenance"]`) is broken volt downstream.

### Fix

```python
# Schema-detect: post-#34 (2026-05-19) drops `facts.provenance`; provenance
# lives in side-table `fact_provenance`. GROUP_CONCAT keeps 1 edge per fact
# with `||`-joined provenance string (parseable downstream).
cols = {r[1] for r in conn.execute("PRAGMA table_info(facts)").fetchall()}
has_pv_table = bool(conn.execute(
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fact_provenance'"
).fetchone())
post34 = "provenance" not in cols and has_pv_table

if post34:
    cur.execute(
        """SELECT f.hash, f.subject, f.predicate, f.object, f.confidence,
                  COALESCE(GROUP_CONCAT(fp.provenance, '||'), '') AS provenance,
                  f.source_type
           FROM facts f
           LEFT JOIN fact_provenance fp ON fp.fact_hash = f.hash
           GROUP BY f.hash"""
    )
else:
    cur.execute("SELECT hash, ... provenance ... FROM facts")  # legacy
```

**Design choice**: GROUP_CONCAT `||`-joined provenance preserves 1 edge per fact-hash (Memgraph MERGE-key egységesség). Downstream callers parse-olhatják `provenance.split("||")`-vel.

### Verification

```
$ vault-graph-extract --dry-run
[stats] KO-DB rows:            15,835
[stats] unique entities:        9,517
[stats] unique literals:       13,115
[stats] unique predicates:        138
```

Patch path: `/root/obsidian-vault/.vault-graph/scripts/vault-graph-extract.py:66-93`. CLI: `/usr/local/bin/vault-graph-extract` (symlink).

## Memgraph re-extract result

| Metric | Pre (post-Phase1+2) | Post-Phase3 | Δ |
|---|---:|---:|---|
| Entity | 8,913 | **13,051** | **+4,138** |
| Edge | 19,215 | **25,518** | **+6,303** |
| Literal | — | 13,141 | — |

**Surprising finding**: Memgraph entity count NÖTT a Phase-3 re-extract után, NEM csökkent. Magyarázat: a `vault-graph-extract` MERGE-pattern új entitásokat HOZZÁAD, de a Phase-1+2 cleanup-pal **eltávolított Tier-A+C zaj-entitásokat ÚJRA megjeleníti** a KO-DB `facts.subject` mezőjéből (mert a #34 előtti hash-elt facts továbbra is ott vannak a DB-ben, csak más source-type-pal).

A 9,517 unique-entity stat (vault-graph-extract dry-run) vs 13,051 Memgraph-state Δ = 3,534 — **ennyi régi zaj-entitás éledt fel** a re-merge során.

## Jaccard re-measure

| Metric | 2026-05-19 post-Phase1+2 | 2026-05-20 post-Phase3 | Δ |
|---|---:|---:|---|
| tier1_total (Memgraph) | 8,806 | 12,881 | +4,075 |
| tier2_total (graphify) | 4,439 | 4,439 | 0 |
| both (intersect) | 102 | 121 | +19 |
| **agreement_rate (Jaccard)** | **0.0078** | **0.0070** | **-0.0008** |

**Acceptance gate ≥0.05: NEM teljesült.** Re-confirms a 2026-05-19 Phase-3-result audit predikcióját: a két extraction-stack **ortogonális vocabulary-t** termel, és pure prompt-tightening önmagában NEM lift-eli a Jaccard-ot.

## Lessons learned

1. **Schema-migration downstream-grep CHECKLIST: 3 hét helyett 3 nap mire mindegyik felfedezésre kerül** — 2026-05-19 délután fedezte fel a `vault-ko-ingest.upsert_fact` regressziót, 2026-05-20 reggel a `vault-graph-extract`-ot. **Wider lesson**: schema-change után a `grep -rn "INSERT INTO <table>" + "SELECT.*<dropped_column>"` futtatás a teljes kódbázison KÖTELEZŐ — NEM elég csak az ADR-ben jelölt direct caller-ek vizsgálata. Ez a 2026-05-19-i [[../11-wiki/schema-migration-downstream-grep-checklist]] wiki ECHOJA.

2. **MERGE-pattern re-merges previously-deleted noise entities** — a vault-graph-extract MERGE-DEFAULT-pattern új entitásokat hozzáad, de a "cleanup-pal eltávolítottakat" NEM tartja le. Wider lesson: ha külön cleanup-pass-t futtatunk a Memgraph-ban (Tier-A+C delete), akkor minden subsequent re-extract `--reset` flag-gel mehet, hogy ne támadjon fel a noise. Vagy: a cleanup-rule-okat upstream-be (KO-DB-be) kell tolni, NEM downstream (Memgraph-ba).

3. **A "no new facts" stdout-üzenet aggregálási illúzió** — a `vault-ko-pending --process-ready` Done: 151/151 processed, ~0 new facts üzenete ellenére a DB-ben +2,034 sor jelent meg. Per-file-üzenetek aggregálása alulszámítja a tényleges DB-mutációt. **Wider lesson**: stdout-számláló önmagában NEM authoritative; mindig DB-side count-tal ellenőrizd.

## Next steps

### Sprint-1 (mai sürgős)
- **B-8 50-bullet pilot tracking** (külön audit-fájlban): kappa=0.660, agreement=84.62%, near-target (≥0.7).
- **Wider downstream-grep**: a `vault-graph-extract` mellett **15+ más vault-CLI** is hivatkozhat a `facts.provenance`-ra. Egy systemic grep-pass + bulk-patch-pass kell.

### Sprint-2 (1-2 hét)
- **Option-B tree-sitter pre-pass** Memgraph extraction-stack vocab-merge — a 2026-05-19 audit szerint a Jaccard ≥0.05 elérése csak strukturális vocab-merge-gel lehetséges. ETA ~1 nap design + 2-3h impl.
- **vault-graph-extract --reset + re-build pass** — törli a 4,138 zaj-entitást, majd újraépíti a 9,517 tényleges entity-szettel. ETA ~5 min run.

### Sprint-3
- **Phase-4 acceptance gate (Jaccard ≥0.05)** Option-B tree-sitter pre-pass után. ETA 2026-06-02 körül (eredeti plan).

## Related

- [[2026-05-19 Memgraph cleanup Phase-3 next-step plan]] — eredeti plan
- [[2026-05-19 Memgraph Phase-3 re-extract result]] — Phase-1 setup-work (subagent-fanout pending)
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — #34 regression-source ADR
- [[../11-wiki/schema-migration-downstream-grep-checklist]] — wider-lesson wiki (2026-05-19-én írva, mai run-on re-validálva)
- [[../11-wiki/two-tier-graph-extraction]] — Option-A vs Option-B rationale
- [[../11-wiki/subagent-fanout-for-planning-artifact.en]] — wave-based 8× parallel pattern
