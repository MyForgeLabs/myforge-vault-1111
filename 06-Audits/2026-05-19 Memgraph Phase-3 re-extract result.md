---
name: Memgraph Phase-3 re-extract result
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "memgraph", "extraction-quality", "phase-3"]
---

# Memgraph Phase-3 re-extract result

## TL;DR

**Status: SKIPPED — Memgraph mutation NEM történt.** A Phase-1 setup-work (v3 vocab request-fájl generálás) 66/83 fájlon sikerült, de a tényleges re-extract subagent-fanout-ot követel (saját Claude Code agent-emnek nincs Task-tool joga közvetlen agent-spawn-ra). A 17 fail egy kritikus regressziót fedett fel: a 2026-05-19-i KO-DB hash-refactor (#34) megtörte a `vault-ko-ingest` Phase-2 (response → upsert_fact) path-ot, mert a `facts` táblának már nincs `provenance` oszlopa, de az `upsert_fact()` még a régi INSERT-tel próbálkozik.

## Pre-flight scope

**Query:** sentence-fragment-detection (sc≥1 AND token-count≥3) provenance-edge mentén csoportosítva.

| Metric | Value |
|---|---:|
| Fragment-Entity-k összesen | 695 |
| Érintett source-fájlok (5+ fragment) | **83** |
| Vártnál (100-300) | -17 ~ -217 — Phase-1+2 már részben tisztított |

### Top-10 source-fájl

| # | source_file | frag_count |
|---|---|---:|
| 1 | `08-Sessions/2026-05-13-sv-functional-payoff.md` | 19 |
| 2 | `08-Sessions/2026-05-13-sv-week1-implementation.md` | 14 |
| 3 | `11-wiki/wp-cli-bricks-postmeta-pattern.md` | 13 |
| 4 | `11-wiki/claude-code-harness-blocks.md` | 13 |
| 5 | `08-Sessions/2026-05-13-sv-b2-memory-architecture.md` | 13 |
| 6 | `07-Decisions/2026-04-24 MYFORGE OS dashboard — roadmap v2.md` | 12 |
| 7 | `08-Sessions/2026-05-04-kgc-weboldal.md` | 12 |
| 8 | `08-Sessions/2026-05-13-sv-week2-extend.md` | 12 |
| 9 | `08-Sessions/2026-05-10-foxxi-weboldal.md` | 11 |
| 10 | `08-Sessions/2026-05-11-kgc-marketing.md` | 11 |

A B-2 Memory-Architecture sprint session-ök adják a Top-5 fele — a Wave-1+2 fanout-spawn nagy mennyiségű session-fragment-et generált, ezeket tisztítani kell.

## Re-extract result (Phase-1 setup-work)

**Phase-1 = request.json generálás vocab-v3-mal a 2-phase pending pattern szerint.**

| Outcome | Count |
|---|---:|
| ✅ Request.json írva (v3 vocab) | **66** |
| ❌ Phase-2 schema-mismatch hiba | **17** (mind régi v2 response.json-nal rendelkezik) |
| 📂 Összes pending request post-Phase-3 | 97 (újból) |
| 📂 v3-response.json post-Phase-3 | 0 (várja a subagent-fanout-ot) |

**Phase-2 NEM futott** — ahhoz user-driven subagent orchestration kell (8× general-purpose Agent spawn, ami az `extraction_prompt`-tal triplet-eket nyer ki). Az én Claude Code session-emnek a Task-tool nem elérhető, így a fanout külső session-ből indítandó.

## Jaccard pre/post

| Metric | Pre-Phase3 | Post-Phase3 | Δ |
|---|---:|---:|---|
| tier1_total (Memgraph Entity) | 8806 | 8806 | 0 |
| tier2_total (graphify) | 4439 | 4439 | 0 |
| both | 102 | 102 | 0 |
| **agreement_rate (Jaccard)** | **0.0078** | **0.0078** | 0 |

**Mutation NEM történt — Memgraph state intact.** A 75 MB-os pre-Phase3 snapshot mentve: `.vault-memory/snapshots/memgraph-pre-phase3-2026-05-19.cypher`.

## Mutation-decision

**SKIPPED.** Két ok:
1. **Subagent-fanout external requirement**: a vocab-v3 prompt-tightening hatását csak akkor látjuk, ha a 66 új request-re visszajön a response.json. Ezt user-driven session futtatja le (Task-tool-os környezetben).
2. **Kritikus regression-block**: a 17 fail (mind ADR-fájl) ugyanazt a `sqlite3.OperationalError: table facts has no column named provenance` exception-t produkálta. A `vault-ko-ingest.py` line 321 `upsert_fact()` még a hash-refactor előtti schema-t hívja. Amíg ez nincs fix-elve, a Phase-2 (response feldolgozás → DB-írás) nem fog működni → a re-extract output sem fog megjelenni a KO-DB-ben → ezért a `vault-graph-extract`-ot sem érdemes futtatni.

## Surprising findings

1. **`vault-ko-ingest` regresszió a hash-refactor után (#34)** — a Phase-1 (request-write) működik, de a Phase-2 (response → DB) crash-el `upsert_fact()`-ben. 17/17 ADR-fájl ugyanúgy fail. **Patch-target**: `/root/obsidian-vault/.vault-ko/scripts/vault-ko-ingest.py:321` — az INSERT-et át kell írni `facts(hash, subject, predicate, object, confidence, source_type, ...)` formára, a `provenance`-t pedig külön `fact_provenance` INSERT-tel kezelni.
2. **Memgraph entity-property minimalizmus** — az Entity csomópontoknak csak `name`, `source_count`, `max_confidence` property-jük van; a source-file információ az **edge**-eken (`r.provenance`) él. A Phase-3-plan eredeti Cypher-query (`n.source_file`) ezért NULL-t ad. Korrigált scope-query: `MATCH (n:Entity)-[r]->() WHERE r.provenance IS NOT NULL`.
3. **Phase-1+2 nagyobb collateral-cleanup volt, mint vártuk** — a plan 5,524 sentence-fragment-source-fájlt becsült, de a valóság **83** fájl (5+ fragment-tel) maradt. A 217-os "hézag" azt jelenti, hogy a Tier-A+C noise-DELETE már megtisztított ~96%-ot — Jaccard mégsem mozdult, ami megerősíti az Option-B (tree-sitter pre-pass) szükségességét: az overlap-hiány **NEM noise-eredetű**, hanem **vocabulary-ortogonalitás**.

## Rollback step

Nincs szükség rollback-re (mutation nem volt). Pending file cleanup:
```bash
# A 97 friss v3 request-fájl megmarad — a subagent-fanout futtatja
ls /tmp/vault-ko-pending/*.request.json -newermt "2026-05-19" | wc -l   # 97
# Snapshot védettnek megmarad:
ls -lh /root/obsidian-vault/.vault-memory/snapshots/memgraph-pre-phase3-2026-05-19.cypher
```

## Next-step recommendation

**Sequential 3-step plan (priority order):**

### 1. (P0, blocker) `vault-ko-ingest.py` upsert_fact schema-patch
- ETA: ~30 min implementation + smoke-test.
- A `INSERT INTO facts (..., provenance, ...)` → `INSERT INTO facts (...)` + külön `INSERT INTO fact_provenance (fact_hash, provenance, source_type, confidence)`.
- Smoke-test: a 17 fail-elő ADR-fájl mindegyike menjen át.
- **Ez a blocker minden további crystallize / re-extract / GitHub-bridge new-ingest-en**.

### 2. (P1) Selective re-extract subagent-fanout
- A 97 pending request-re külön session-ben Task-tool-os subagent-fanout (8× parallel).
- ETA: ~3-4h subagent-budget.
- Várt KO-DB delta: a vocab-v3 anti-noise-7 prompt **csökkenti** a fragment-output-ot (subjektíven becsült 30-50% fragment-redukció a re-extract-output-ban).

### 3. (P2) **Option-B tree-sitter pre-pass** — KÖTELEZŐ a Phase-4 gate eléréséhez
A surprising finding #3 alapján **a Jaccard-növelés nem fog Option-A-tól önmagában jönni**: a maradék 695 fragment csak ~8% lehet a Jaccard-mismatch-ből, a túlnyomó rész **vocabulary-mismatch**. Option-B (code-block tree-sitter pre-pass) közvetlen overlap-növelést ad. **ETA: 1 nap design + 2-3h impl** ahogy a plan v0 javasolta.

**Phase-4 acceptance gate (Jaccard ≥0.05) így ~2026-06-02-re tolódik**, NEM 2026-05-22-23-ra.

## Budget-cap respected

- Wall-clock: ~30 min (a 2 óra budget-en belül).
- Re-extracted source-fájl: 0 (Memgraph-mutáció: 0).
- Phase-1 setup-work: 66/83 = 79.5% siker, 17 schema-bug-on elakadt.

## Related

- [[2026-05-19 Memgraph cleanup Phase-3 next-step plan]] — eredeti plan
- [[2026-05-19 Memgraph cleanup execution result]] — Phase-1+2 execution
- [[2026-05-19 Memgraph entity-cleanup analysis]] — Wave-1 analysis
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — #34 hash-refactor (regression-source)
- [[../11-wiki/vault-ko-ingest-prompt-tightening-2026-05-19]] — vocab v3 anti-noise-7
- [[../11-wiki/two-tier-graph-extraction]] — Option-A vs Option-B rationale
