---
name: Parts-table vs figure-page detection
type: wiki
tags: ["#type/wiki", "pdf", "extraction", "heuristic", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# Parts-table vs figure-page detection

> [!todo] Bővítendő
> "first_table_page" strukturális szabály + parts_per_page heurisztika — bármilyen technical-PDF tartalom-elemző projektre.

## Heurisztikák

- `first_table_page >= 5` — az első 4 oldal általában cover/intro/TOC, NEM parts-table
- `parts_per_page` görbe — figure-oldalak <10 part, parts-table oldalak 20-50 part
- `image-aware classify_page` — ha az oldalon kép-blokk van (PIL embedded), valószínűbb figure-oldal

## Kapcsolódó

- [[multi-figure-parts-list-pattern]] — sibling
- [[../02-Projects/robbantott-kereso|robbantott-kereso projekt]]
- [[../08-Sessions/2026-05-12-robbantott-bra-keres|forrás-session]]
