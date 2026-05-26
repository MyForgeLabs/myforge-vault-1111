---
name: Multi-figure parts-list pattern
type: wiki
tags: ["#type/wiki", "pdf", "extraction", "pattern", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Multi-figure parts-list pattern

## TL;DR

Technical-PDF ingest (robbantott-bra/exploded-view/parts-catalog) tipikus struktúrája: **több figure-page + egy közös parts-table** (vagy fordítva). A naiv "page-by-page" parsing elveszíti a part↔figure mapping-et. A reusable pattern: **"catalog-wide besorolatlan pool + figure-id pozícionálással áthelyezés"** — minden part először egy `figure_id IS NULL` pool-ba kerül, majd strukturális heurisztika alapján rendelődik figure-höz. A maradék pool látható "besorolatlan" rétegként, manual reviewra.

## Háttér

A robbantott-kereso projekt ([[../02-Projects/robbantott-kereso]]) 2026-05-13-15 sprint-jében ([[../08-Sessions/2026-05-13-robbantott-bra-keres]]) kiderült, hogy a Wacker BH 55 katalógus tipikus szerkezete:

- Oldal 1-4: TOC, cover, intro
- Oldal 5-7: figure-page 1 (gép-bontás)
- Oldal 8-12: közös parts-table (mind a 3 figure-höz)
- Oldal 13-14: figure-page 2 (alkatrész-szerelvény)
- Oldal 15-17: figure-page 3 (kopó-alkatrész)

A naiv parsing minden parts-table-sort az "előző figure-höz" rendelt → de a parts-table 8-12 oldal egy közös tábla volt, így az első figure 60 partot kapott, a többi 0-t. A javítás: **pool-first ingest**, majd "position-recover" pass.

## Mintázat

### Ingest phase 1: pool-first

```python
for page in pdf.pages:
    cls = classify_page(page)  # 'cover' | 'figure' | 'parts_table' | 'mixed'
    if cls == 'parts_table':
        for row in extract_table_rows(page):
            parts.append({**row, 'figure_id': None, 'source_page': page.num})
```

### Ingest phase 2: figure-id matching

Strukturális heurisztikák ([[parts-table-vs-figure-page-detection]]):

1. **Position-based** — egy parts-table-sor pozíciójához legközelebbi figure-page (page-distance + label-match)
2. **Label-match** — figure-label `"Fig. 3-7"` szerepel a part-row-ban → match
3. **Cross-figure indicator** — ha label-szám több figure-szel matchel → multi-figure part (M:N)

### Ingest phase 3: unmatched pool

A maradék (`figure_id IS NULL`) parts a UI-on **"Besorolatlan" tab**-ban jelenik meg, manual-review-ra. Empirikusan a Wacker BH 55-nél ~12% maradt unmatched.

## Anti-pattern

- **Page-sequential greedy assign** — minden part-row az "előző figure"-höz; gyors, de elveszíti a multi-figure shared-tables-t
- **No-pool fallback** — ha nincs match, eldobni a partot; tipikusan 10-20% adatvesztés
- **Pre-bake figure-id az ingest-időben** — később nem javítható multi-figure relation; pool-pattern flexibilisebb
- **Strict figure-label-match** — vannak katalógusok ahol a part-row nem említi a figure-számot, csak position alapján van rendezve

## Reusable szabályok

1. **Pool-first ingest** — minden part `figure_id = NULL` default-tal
2. **M:N self-relation a DB-séma-ban** — `MachineAccessory(machine_id, part_id, figure_id)` 3-way junction (lásd [[../07-Decisions/2026-05-10 Tartozék-rendszer schema (MachineAccessory M-N)]])
3. **Page-distance + label-match composite scoring** — sem position-only, sem label-only nem elég
4. **Unmatched tab a UI-on** — ne rejtsd el; manual-review hatékonyabb mint az újra-ingest
5. **Idempotent re-ingest** — same-pdf re-run nem duplikál, csak frissít (hash-alapú dedupe)
6. **Audit-log a phase-2 mapping-ekről** — confidence-score per-part, debugger-felület

## Buktatók

- A `pdfplumber` extract-table eltér a `tabula-py`-tól; bonyolult táblákon érdemes mindkettőt futtatni és diff-elni
- `figure_id` integer-key sokszor stringként jön ("3-7", "A-12") — normalize-olj
- A "besorolatlan pool" méretét meta-szinten követni kell: ha hirtelen >30% → ingest-pipeline regresszió

## Kapcsolódó

- [[parts-table-vs-figure-page-detection]] — strukturális detect (sibling)
- [[../02-Projects/robbantott-kereso|robbantott-kereso projekt]]
- [[../08-Sessions/2026-05-12-kgc-robbantott-bra|forrás-session]]
- [[../07-Decisions/2026-05-10 Tartozék-rendszer schema (MachineAccessory M-N)]]
- [[img-viewer-zoom-pan-ux]] — UI-réteg ugyanehhez az ingest-pipeline-hoz
- [[multi-page-pdf-figure-check]] — sibling heuristic
