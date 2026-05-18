---
name: wp-notion-elementor-import-pattern
type: wiki
tags: ["#type/reference", "wordpress", "elementor", "notion", "import"]
created: 2026-05-08
updated: 2026-05-08
source:
  - "[[08-Sessions/2026-05-06-foxxi-weboldal]]"
  - "[[11-wiki/wp-elementor-template-conflicts]]"
---

# Notion → WP-Elementor import pattern

2-rétegű import-pipeline ami egy Notion-export (HTML vagy `.md`) tartalmat strukturált Elementor canvas-ra alakít, **több oldalra kötegelve**, megőrzött hero/cross-link szekciókkal.

## Mikor használd

- Egy Notion-doc tartalma (intro szöveg + H2/H3-strukturált fő rész + GYIK-pairs) **több WP oldalon szétszórandó** (pl. 6-féle szolgáltatás).
- A célok már Elementor-canvas-on futnak; a hero + cross-link section-öket meg kell tartani; a középső 2-3 section-t le akarjuk cserélni a friss tartalomra.
- Manuális Elementor-szerkesztés túl lassú / hibázásra hajlamos lenne (50+ GYIK-bullet, 25+ H3-cím).

## Pipeline

### 1. Python parser — Notion → strukturált JSON

```
parse_notion.py:
  input:  notion-export.html (vagy md)
  output: pages.json
  séma:   {
    "page_slug_or_id": {
      "intro": "<p>...</p>",                  # blockquote-elemes intro
      "structured": [                          # H3-okkal felosztott fő rész
        {"h3": "Cím", "html": "<p>...</p><ul>..."},
        ...
      ],
      "faqs": [                                # GYIK-párok
        {"q": "Kérdés?", "a": "<p>Válasz</p>"},
        ...
      ]
    }
  }
```

Tipikus regex-pattern: H2 → page-boundary, H3 → struktúra-szelet, "GYIK" / "FAQ" / "Kérdések" → faq-section-trigger, az alatta lévő `<p><strong>` pairs → q/a.

### 2. PHP rebuild script — JSON → Elementor canvas

```
rebuild-dental-pages.php:
  input:  pages.json
  for each page:
    1. olvas: $current = json_decode(get_post_meta($id, '_elementor_data', true))
    2. backup: update_post_meta($id, "_elementor_data_notion_backup_$ts", json_encode($current))
    3. keep: első section (hero) + utolsó section (cross-link)
    4. replace: a középső szekciók (intro-blockquote + structured-blockquote + accordions)
    5. compose: foxxi-page-hero + foxxi-blockquote × 2 + foxxi-accordions
    6. write: $wpdb->update(...) — a tényleges UPDATE
```

**Backup pattern:** `_elementor_data_notion_backup_<unix_ts>` post meta — **NE** `_elementor_data_backup_*` (ütközés a manuális backup-pattern-nel).

### 3. Cache-purge + verify

```bash
ssh hostinger
wp cache flush && wp w3-total-cache flush all
wp plugin activate litespeed-cache
wp litespeed-purge all
wp plugin deactivate litespeed-cache

# HTTP-verify mind a 6 oldalra:
for url in /url1/ /url2/ ...; do
  curl -s "https://$STAGING$url?nocache=$(date +%s)" | grep -c '<h3'
done
```

## Buktató — Pattern 8 (`wp_slash` + `$wpdb->update`)

**FIGYELEM:** a rebuild script `$wpdb->update`-tel írja az `_elementor_data` mezőt — **NE** `wp_slash` előtte! A wpdb belső `mysqli_real_escape` elég. Ha `wp_slash`-elsz: dupla-escape, frontend 0 H2/H3-at renderel.

Lásd: [[11-wiki/wp-elementor-template-conflicts#Pattern 8 — `wpdb->update` és `wp_slash` dupla-escape buktató]]

## Reusability vs. egyediség

**Reusable:**
- Backup-pattern (`_elementor_data_notion_backup_<ts>`)
- "Keep hero + cross-link, replace middle" canvas-section-stratégia
- Pattern 8 elkerülése
- Cache-purge szekvencia (3 réteg Hostinger-en)

**Új parser-iteráció kell minden új oldal-sémához:**
- Notion exportok eltérő H2/H3-mélységgel jönnek
- GYIK-marker eltér ("GYIK" vs "FAQ" vs "Gyakori kérdések")
- A `<strong>` használat változó a Q/A felismeréshez
- Tehát a parser nem generikus, hanem oldal-família-specifikus.

## Példa — foxxi (2026-05-06)

- 6 fogászati szolgáltatás-oldal (Szájhigiénia, Fogágybetegségek, Esztétikai, Koronák, Gyermekfogászat, Szájsebészet)
- Notion: 67 GYIK + ~25 H3-cím + 6 intro-blockquote
- Rebuild eredmény: 67/67 GYIK + struktúrált H3-ok mind a 6 oldalon
- Egyik post (`2233 Gyermekfogászat`) DB-corrupcióval érkezett (Pattern 6 öröksége) — fixelve `stripslashes()` fallback-tel a parse-fázisban

## Kapcsolódó

- [[11-wiki/wp-elementor-template-conflicts]] — Pattern 6 (backslash-strip), Pattern 8 (dupla-escape), Pattern 10 (render-cache)
- [[11-wiki/wp-acf-flexible-to-elementor-migration]] — előző generációs migrációs minta (egyszer-fogyasztható, nem kötegelt)
- [[02-Projects/foxxi]] — projekt ahol kifejlődött a minta
