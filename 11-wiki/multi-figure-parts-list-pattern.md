---
name: Multi-figure parts-list pattern
type: wiki
tags: ["#type/wiki", "pdf", "extraction", "pattern", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# Multi-figure parts-list pattern

> [!todo] Bővítendő
> Pattern: "catalog-wide besorolatlan pool + figure-id pozícionálással áthelyezés" — reusable bármilyen many-to-one ábra-vs-tábla viewer projektre (akár KGC-Bérlés tartozék-rendszerre).

## Lényeg

1. Ingest-kor minden part egy "pool"-ba kerül (figure_id = NULL)
2. Per-figure matching → figure_id beállítása strukturális heurisztika alapján (`first_table_page`, `parts_per_page`)
3. Maradék pool látható "besorolatlan" rétegként — manual review

## Kapcsolódó

- [[parts-table-vs-figure-page-detection]] — strukturális detect
- [[../02-Projects/robbantott-kereso|robbantott-kereso projekt]]
- [[../08-Sessions/2026-05-12-robbantott-bra-keres|forrás-session]]
