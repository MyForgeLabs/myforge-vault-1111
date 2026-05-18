---
name: vault-ko-conflicts-audit design
type: wiki
tags: ["#type/wiki", "ko-db", "sv-1", "audit", "contradiction", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# `vault-ko-conflicts-audit` design

## TL;DR

Heti cron script ami a **KO-DB triplet-tár belső contradiction-jait** detektálja (NEM vault-vs-Learning, hanem **fact-vs-fact** előjeles ütközések). Komplementere a [[../06-Audits/2026-05-17 B-3 vault-coherence-drift check|vault-coherence-drift check]]-nek (ami Learning-bullet vs vault-state-et néz). Predicate-aware heat-classifier kizárja az értelmes alias-okat (`is_a`, `same_as`).

## Háttér

A KO-DB ([[sv-01-memory-architecture]]) 13K+ structured fact-et tárol SQLite-ban `(subject, predicate, object, source, confidence)` séma szerint. A facts különböző session-ekből, web-ingest-ből, github-trending-ből, NotebookLM-ből származnak — természetes hogy **ellentmondó verziók egymás mellé kerülnek**. Példák a vault-ból:

- `KGC office hours = "07:00–16:00"` (forrás: 2026-05-15 session) vs `KGC office hours = "08:00–17:00"` (forrás: scraped weboldal stale snapshot)
- `KGC-ERP repo = "zolijavos/KGC-3"` (forrás: 2026-02 session) vs `KGC-ERP repo = "zolijavos/KGC-4"` (forrás: 2026-05-18 ADR)

A friss/stale eldöntéséhez confidence-rank, source-recency és cross-corroboration kell. A `vault-ko-query --conflicts` (B-1 Week 3 layer, [[../05-Memory/Infrastructure]]) már ad ad-hoc query-felületet — a heti audit ezt **rendszerszintűvé** teszi.

## Mintázat

1. **Collect step** — minden `(subject, predicate)` kulcsra a tárolt object-ek halmaza
2. **Filter step** — ha `|distinct_objects| > 1` és predicate NEM alias-class → conflict-kandidát
3. **Predicate-aware heat-classifier:**
   - **Cold** (alias-class, ignorálni): `is_a`, `same_as`, `aliases`, `redirects_to`, `also_known_as`
   - **Warm** (multi-value OK): `tagged_with`, `relates_to`, `mentioned_in`, `has_aspect`
   - **Hot** (értékes contradiction): `equals`, `has_value`, `located_at`, `opens_at`, `version_is`, `default_is`
4. **Rank step** — cross-source-corroboration (több forrás ugyanaz = igaz), recency (újabb forrás súlyozása), confidence
5. **Output** — `06-Audits/ko-conflicts-YYYY-MM-DD.json` (machine) + `ko-conflicts-latest.md` (human)
6. **Suggested-resolution** — minden conflict-ra: "evict older / merge / manual review"

## Anti-pattern

- **Minden predicate-en futtatni** — `tagged_with = ["pdf", "extraction"]` és `tagged_with = ["pdf", "ux"]` NEM contradiction
- **Recency-only ranking** — egy frissen scraped stale-page felülírná a kézi ratify-t (ezért cross-source corroboration is kell)
- **Auto-evict** — soha ne töröljön a script önállóan; csak suggestion-listát adjon, mindig user/agent decision

## Reusable szabályok

1. **Predicate-classifier YAML konfig** — `~/.vault-config/ko-predicates.yaml`, hot/warm/cold címkékkel
2. **Confidence-weight** — `weighted_score = confidence × log(source_count + 1) × recency_decay`
3. **Cron weekly Sun 04:50** — post-`vault-broken-wikilinks-audit` (04:45)
4. **Threshold-alert** — ha `hot_conflicts > 10` → exit 1 (cron-email)
5. **Idempotent** — same-day re-run nem duplikál (overwrite latest.md)
6. **Auto-disable min-volume guard** — ha total-facts < MIN_VOLUME (pl. 1000) → SKIP (DB-corrupt false-positive ellen)

## Buktatók

- A KO-DB SQLite WAL-mode-ban van — `BEGIN IMMEDIATE` kell ha párhuzamosan fut a `vault-ko-ingest`
- Predicate-normalize ELŐSZÖR (`predicate.lower().strip("_")`); különben `OpensAt` vs `opens_at` false-distinct
- Hungarian-collation a value-comparison-nél — `Érd` vs `Erd` accent-strip után equal

## Kapcsolódó

- [[sv-01-memory-architecture]] — KO-DB architektúra
- [[../06-Audits/2026-05-17 B-3 vault-coherence-drift check]] — Learning-vs-vault check
- [[../05-Memory/Infrastructure]] — script-listák
- [[vault-cleanup-multi-script-policy]] — cron-ütemezés
- [[auto-disable-min-volume-guard]] — false-positive guard
- [[vault-corruption-detection-pattern]] — szélesebb integritás
