---
name: Parts-table vs figure-page detection
type: wiki
tags: ["#type/wiki", "pdf", "extraction", "heuristic", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Parts-table vs figure-page detection

## TL;DR

Technical-PDF ingest-pipeline első feladata: melyik oldal **figure-page** (kép-domináns, exploded-view) és melyik **parts-table** (tábla-domináns, alkatrész-szám/megnevezés)? Három heurisztika kombinációja megbízható: (1) **`first_table_page >= 5`** strukturális szabály, (2) **`parts_per_page`-küszöb** (figure < 10, parts-table 20-50), (3) **image-aware classify_page** (embedded PIL → figure-page valószínűbb). Az ingest-mutex-szel kombinálva a robbantott-keresőben ([[../02-Projects/robbantott-kereso]]) ~95% F1.

## Háttér

A robbantott-keresoő 2026-05-13 sprint ([[../08-Sessions/2026-05-13-robbantott-bra-keres]]) parts-first pipeline újratervezésénél kiderült, hogy a naiv `if has_table(page): parts_table` osztályozó hibázott a következő esetekben:

- TOC-oldal (page 2-3) szintén tartalmaz táblát → false-positive parts-table
- Cover-oldalon lehet 1-2 part-szerű sor (pl. "Model: BH 55") → ingest-pollution
- Figure-page-en lehet 1-2 callout-table (jelzések) → félre-osztályozás

A három heurisztika együtt **strukturális szabályt** ad: cover/intro/TOC általában az első 4 oldal → `first_table_page >= 5` küszöb. A `parts_per_page` görbe segít a "kevert" oldalakat (figure + kis callout-table) azonosítani.

## Mintázat

### Heurisztika 1: `first_table_page >= 5`

```python
def detect_first_parts_table(pdf):
    for page in pdf.pages:
        if page.num < 5: continue  # skip cover/intro/TOC
        if has_table(page) and len(extract_table_rows(page)) >= 10:
            return page.num
    return None
```

### Heurisztika 2: `parts_per_page` distribution

| Page-type | parts_per_page (typical) |
|---|---|
| Cover / intro | 0-2 (callout-szerű) |
| TOC | 5-15 (section-list) |
| Figure-page | 0-10 (callout-jelzések) |
| Parts-table | 20-50+ |
| Mixed | 10-25 (figure + small table) |

Threshold: `>= 15` → parts-table candidate; `< 10` → figure-candidate.

### Heurisztika 3: `image-aware classify_page`

```python
def classify_page(page):
    has_img = bool(page.images) or has_embedded_pil(page)
    parts = len(extract_table_rows(page))
    if has_img and parts < 10: return 'figure'
    if has_img and parts >= 10: return 'mixed'
    if parts >= 15: return 'parts_table'
    if parts > 0: return 'mixed'
    return 'unknown'
```

## Anti-pattern

- **`has_table(page)` egyedül** — TOC + cover false-positive
- **Csak `image_count > 0`** — sok parts-table-en is van logo/illustration
- **Per-page osztályozás context nélkül** — két szomszédos oldal pattern-jét érdemes nézni (window=3)
- **Hard-coded page-range** — "parts-table mindig a page 5-10" típusú szabály törik, ha a PDF más struktúrájú

## Reusable szabályok

1. **Strukturális küszöb FIRST** — `first_table_page >= 5` mielőtt parts-extract-elsz
2. **Distribution-aware classifier** — `parts_per_page` küszöb DPI-szerű hisztogramból (NEM hard-coded)
3. **Image-aware classify** — `page.images` + `pdfplumber.has_embedded_pil` kombinálva
4. **`mixed` típus megengedett** — ne erőltesd a binary figure/parts döntést; flag-eld `mixed`-ként, post-processz
5. **DPI auto-tune 3-page heurisztika** — kezdj 300 DPI-vel, ha empty extract → 400 → 500 (lásd [[../08-Sessions/2026-05-13-robbantott-bra-keres]])
6. **Confidence-score per-page** — debug-friendly, audit-log-ban perzisztálva

## Buktatók

- A `pdfplumber` szerinti "table" lehet csak `<table>`-szerű layout (column-alignment), NEM tényleges tábla — `extract_table_rows` szigorúbban szűr
- Multi-language katalógusok (DE/FR/IT) — column-header-detection nyelvfüggő, normalize ELŐSZÖR
- Image-aware classify lassú (PIL load minden oldalra) — cache-elj per-pdf-hash
- TOC-oldal néha 20+ section-row-val érkezik → `parts_per_page` heurisztika önmagában false-positive lenne; ezért kell az `>= 5` küszöb is

## Kapcsolódó

- [[multi-figure-parts-list-pattern]] — sibling pattern (post-classify mapping)
- [[../02-Projects/robbantott-kereso|robbantott-kereso projekt]]
- [[../08-Sessions/2026-05-12-kgc-robbantott-bra|forrás-session]]
- [[../08-Sessions/2026-05-13-robbantott-bra-keres|sprint follow-up]]
- [[img-viewer-zoom-pan-ux]] — UI-réteg ugyanehhez a pipeline-hoz
