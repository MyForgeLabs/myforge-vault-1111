---
name: vault-ko-conflicts-audit design
type: wiki
tags: ["#type/wiki", "ko-db", "sv-1", "audit", "contradiction", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# `vault-ko-conflicts-audit` design

> [!todo] Bővítendő
> Heti cron script ami a KO-DB triplet-tár belső contradiction-jait keresi (NEM vault-vs-Learning, hanem fact-vs-fact előjeles ütközések). Komplementer a [[../06-Audits/2026-05-17 B-3 vault-coherence-drift check|B-3 vault-coherence-drift check]]-nek.

## Cél

Cross-source contradiction detect a KO-DB-ben (13K+ fact, predicate-aware heat-classifier). Példa: ha `KGC office hours = "07:00–16:00"` (forrás A) és `KGC office hours = "08:00–17:00"` (forrás B), audit-event lóg.

## Implementáció (vázlat)

- Script: `/usr/local/bin/vault-ko-conflicts-audit` (Phase B-1 Week 4)
- Output: `06-Audits/ko-conflicts-YYYY-MM-DD.json`
- Predicate-aware heat-classifier — bizonyos predicate-eken (pl. `is_a`, `same_as`) NEM contradiction, csak alias
- Cron: weekly Sunday 04:50

## Kapcsolódó

- [[sv-01-memory-architecture]] — KO-DB architektúra
- [[../06-Audits/2026-05-17 B-3 vault-coherence-drift check]] — Learning-vs-vault check
- [[../05-Memory/Infrastructure]] — script-listák
