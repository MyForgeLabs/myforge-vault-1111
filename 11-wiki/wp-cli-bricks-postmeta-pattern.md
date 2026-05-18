---
name: WP-CLI Bricks postmeta build pattern
type: wiki
created: 2026-05-09
updated: 2026-05-09
agent: claude
tags: ["#topic/wordpress", "#topic/bricks", "#topic/wp-cli", "#workflow"]
---

# WP-CLI Bricks postmeta build pattern

> Hogyan építsünk Bricks Builder page-content-et **CLI-ből**, Bricks-Builder-admin-UI nélkül. Praktikus minta ha sok page-et kell egyszerre felépíteni vagy programatikusan generálni (Python-szkripttel a tartalmat → JSON-fájl → wp post meta).

## Kontextus

Bricks Builder a page-tartalmat a `_bricks_page_content_2` postmeta-ban tárolja — egy serializált PHP-array, minden Bricks-element egy `{id, name, parent, children, settings}` objektum. CLI-ből programmatikusan beírható, ha tudjuk a 2 fő gotcha-t.

## Gotcha 1: `wp post meta update` nem perzisztál `_bricks_page_content_2`-re

Tipikus WP-CLI-pattern (`wp post meta update <ID> <key> <value> --format=json`) **nem perzisztál** Bricks-postmeta-update-eknél. A Bricks valami security-hash-szel vagy serialize-tartalom-validálással blokkolja.

**Tünet:** `Success: Updated custom field` üzenet jön, de a frontend a régi tartalmat mutatja, és a meta-érték változatlan.

**Megoldás — `delete + add` ciklus:**

```bash
# Pull
wp post meta get 107 _bricks_page_content_2 --format=json > page-107.json

# Modify (Python-szkripttel locally)
python3 -c "
import json
data = json.load(open('page-107.json'))
# ... modify data ...
json.dump(data, open('page-107.json', 'w'), ensure_ascii=False)
"

# Push
wp post meta delete 107 _bricks_page_content_2
cat page-107.json | wp post meta add 107 _bricks_page_content_2 --format=json
```

A `delete + add` mindig megbízhatóan ír. Az `update` használata **kerülendő** Bricks-tartalom-frissítéskor.

## Gotcha 2: `code` element executeCode-signature CLI-blokkolt

Ha custom HTML/CSS-snippet-et akarsz beilleszteni egy page-be, NE használj Bricks `code` element-et CLI-ből. A `code` element `executeCode: true` flag mellett `eval`-elja a tartalmat, és a Bricks egy security-signature-t vár (kód-aláírás), amit csak a Bricks-Builder-admin-UI tud generálni. CLI-ből a `code` element **snippet-mode-ban** renderel (a HTML-t mint TEXT mutatja).

**Megoldás — `html` element:**

A Bricks `html` element közvetlenül `echo $settings['html']`-re renderel, nincs signature-ellenőrzés. Bár a Bricks `deprecated` flag-gel jelöli (csak Builder-UI-ban nem mutatja default-mode-ban), CLI-ből tökéletesen működik.

```json
[{
  "id": "htmlpg",
  "name": "html",
  "parent": 0,
  "children": [],
  "settings": {
    "html": "<section class=\"my-custom\">...</section>"
  }
}]
```

A `_bricks_editor_mode` meta-t is `bricks` értékre kell állítani:

```bash
wp post meta update 107 _bricks_editor_mode bricks
```

És a régi Elementor-meta-t törölni:

```bash
for key in _wp_page_template _elementor_data _elementor_version _elementor_pro_version \
          _elementor_template_type _elementor_edit_mode _elementor_page_settings \
          _elementor_controls_usage; do
  wp post meta delete <ID> "$key" 2>/dev/null
done
```

## Hostinger LiteSpeed cache-buster

A Bricks-rendering Hostinger-en a LiteSpeed CDN edge-cache mögött **7-napos** TTL-rel cache-elődik. Tartalom-frissítés után:

```bash
wp cache flush
wp eval 'if (function_exists("rocket_clean_domain")) rocket_clean_domain();'
```

DE: az image-asset-cache-t **NEM törli** ez. Image/SVG csere esetén **fájlnév-átnevezés** szükséges a CDN-bypass-hoz (lásd [[05-Memory/Infrastructure]]).

## Példa-recipe (4 page batch-build)

Lásd projekt: `/root/projektjeim/rojtesbojt/docs/claude-design-brief/99-FULL-COMBINED-PROMPT.md` — a teljes 4-page Bricks-content Python-szkripttel generálva, fájl-alapú postmeta-injection.

## Forrás

Rojt és Bojt session 2026-05-08 (4 page Bricks-3-rebuild iteration `wp eval-file` failure → switch to delete+add JSON file pattern). 5+ verzió-iteráció felett kísérletezve.

## Kapcsolódó

- [[wp-elementor-template-conflicts]] — Elementor-specific gotchas
- [[hellopack-wordpress-plugin-suite]] — HelloPack-pluginek (Bricks ecosystem benne)
- [[svg-asset-vs-vector-tradeoff]] — Asset-source-decision SVG/PNG-re
