---
name: vendor-feature-verify-before-workaround
description: Mielőtt workaround-script-et írunk egy infrastruktúra-feature-re, verifikáld a vendor jelenlegi képességeit — egy 30 perces release-note olvasás napokat megtakaríthat
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "engineering-discipline", "lesson", "sprint-planning"]
---

# Vendor feature verify — before workaround

## A pattern

Sprint-tervezéskor, amikor a vendor docs azt mondja "feature X not supported", **mielőtt elkezdjük a workaround-script implementációját:**

1. Ellenőrizd a **jelenlegi verzió** release-note-jait (különösen ha 3+ hónap telt el azóta, hogy a vendor docs-ot olvastad)
2. Ellenőrizd a CHANGELOG-ot vagy `[ENTERPRISE-ONLY]` flag-eket a feature mellett
3. Próbáld ki a feature-t egy `docker-shell`-ben vagy gyors smoke-test-ben: ha kapsz `SyntaxError`-t valid syntax-ra, akkor *valószínűleg* nem támogatott; ha más errort (`OOM`, `Capacity exceeded`) akkor TÁMOGATOTT, csak konfig kell

**ROI:** 30 perc release-note olvasás vs napok workaround-development.

## Élő példa — Memgraph CE 3.9.0 native vector-index

A SV B-2 sprint 2026-05-13-án indult numpy-cosine workaround-pattern-rel, mert a vault-docs (2026 elején olvasva) azt mondta hogy Memgraph CE nem támogat native vector-index-et. **2026-05-17-én verifikálva:** a 3.9.0 (2026-04 release) NATÍV `CREATE VECTOR INDEX` syntax-ot kínál + `vector_search.search` procedure-t. 4 nap workaround-development megspórolható lett volna.

A migráció eredménye: **280× speedup** (numpy 280ms → native 1ms mean). Részletek: [[memgraph-ce-feature-limits#2026-05-17 native vector-index VERIFIED LIVE]] + [[../06-Audits/2026-05-17 B-2 native vector-index migration]].

## Mikor érdemes alkalmazni

- ✅ Bármilyen 6+ hónapos roadmap-elemnél a release-cycle előtt (vendor lehet hogy közben implementálta)
- ✅ Workaround-script aki >1 napos effort-ot követelne (a verify ROI dominál)
- ✅ Open-source projektek esetén — GitHub release-notes + CHANGELOG kötelező pass

## Mikor NEM kell

- ❌ Triviális workaround (<1 óra) — hamarabb megírod mint hogy átolvasd a docs-t
- ❌ Closed-source vendor, ahol nincs release-note (akkor a verify ott történik amikor leszámlázzák a credit-eket)

## Kapcsolódó

- [[sprint-day-0-skeleton-first]] — skeleton-first elv, amibe ez beilleszthető
- [[memgraph-ce-feature-limits]] — élő példa
