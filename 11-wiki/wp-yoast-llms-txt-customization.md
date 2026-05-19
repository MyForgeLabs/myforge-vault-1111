---
name: WordPress Yoast SEO llms.txt — szabály-tisztítás (mu-plugin minta)
description: Yoast SEO Premium /llms.txt fizikai fájlt generál — hogyan szűrhető meg dev-backup, popup, stb. bejegyzésektől
type: wiki
created: 2026-05-04
tags: ["#tech/wordpress", "#tech/yoast-seo", "#tech/seo", "#ai"]
updated: 2026-05-19
---

# Yoast llms.txt szabály-tisztítás

## Mi az llms.txt

`/llms.txt` egy modern AI-feature: ChatGPT, Claude, Gemini stb. ezt a fájlt olvassa hogy megértse a weboldal struktúráját. Olyan mint a `robots.txt` AI-knek. Yoast SEO Premium **automatikusan** generálja.

## Kritikus tudnivaló

**A `/llms.txt` egy FIZIKAI FÁJL** a public_html gyökerében — Yoast cron-eseménnyel (`wpseo_llms_txt_population`) generálja, a webserver **közvetlenül szolgálja**. A WordPress és mu-plugin filterek **NEM HATNAK** rá normál request-folyamatban.

```bash
ls -la public_html/llms.txt   # → fájl, nem URL-route
```

## A 3 jellemző zaj-bejegyzés

1. **Trash-elt page-ek** maradványai (Yoast indexable-tábla cache-eli)
2. **Popup CPT-k** (Popup Maker plugin) — `popup` és `popup_theme` post-typeok bekerülnek, AI-knak haszontalanok
3. **Dev-backup oldalak** (pl. `fogszab-v2/v3/v4/v5`) — nem-publikus referencia-oldalak

## Tisztítási stratégia (3-rétegű)

### 1. réteg — Yoast settings (noindex)

```bash
wp eval "
\$opt = get_option('wpseo_titles');
\$opt['noindex-popup'] = true;
\$opt['noindex-popup_theme'] = true;
update_option('wpseo_titles', \$opt);
"
```

### 2. réteg — Yoast indexable-tábla cleanup

```bash
wp eval "
global \$wpdb;
\$tbl = \$wpdb->prefix . 'yoast_indexable';
\$wpdb->query(\"DELETE FROM \$tbl WHERE object_sub_type IN ('popup', 'popup_theme')\");
\$wpdb->query(\"DELETE FROM \$tbl WHERE permalink LIKE '%dev-backup-slug-pattern%'\");
"
```

### 3. réteg — mu-plugin auto-resanitize (futamidőre)

```php
<?php
/** Plugin Name: Foxxi — Clean llms.txt */
add_action('shutdown', 'my_resanitize_llms');
function my_resanitize_llms() {
  $path = ABSPATH . 'llms.txt';
  if (!file_exists($path)) return;
  static $checked = false;
  if ($checked) return;
  $checked = true;

  $s = @file_get_contents($path);
  if ($s === false) return;
  if (strpos($s, '## Popups') === false && strpos($s, 'fogszab-v') === false) return;

  $s = preg_replace('/^- \[[^\]]+\]\([^)]*?dev-backup-slug[^)]*\)\n/m', '', $s);
  $s = preg_replace('/^## Popups\n(?:- \[[^\]]+\]\([^)]+\)\n)+\n?/m', '', $s);
  $s = preg_replace('/^## Popup Themes\n(?:- \[[^\]]+\]\([^)]+\)\n)+\n?/m', '', $s);
  $s = preg_replace('/\n{3,}/', "\n\n", $s);

  @file_put_contents($path, $s, LOCK_EX);
}
```

## Yoast cron-rebuild trigger

Yoast hetente futtatja a `wpseo_llms_txt_population` cron-eseményt. Manual trigger:

```bash
wp cron event run wpseo_llms_txt_population
```

## Yoast filterek

- `wpseo_llmstxt_filesystem_path` — a cél-path felülírás (pl. más fájlnévre)
- `wpseo_llmstxt_link_description` — link-description felülírás post-szinten
- `wpseo_llmstxt_encoding_prefix` — BOM-prefix felülírás

DE: ezek a Yoast generálási folyamatban hatnak, nem a kész fájl szolgálásakor.

## Verify

```bash
# Should be 0 problematic lines:
curl -s "https://SITE/llms.txt" | grep -cE "fogszab-v|## Popup"
```

## Példa: Foxxi case (élő projekt)

A Foxxi projekt-ben a fenti 3-rétegű stratégia kombinációval:
- Mindhárom réteg implementálva
- Eredmény: `/llms.txt` clean (4 dev-backup + 7 popup-line eltávolítva)
- Yoast cron-rebuild után is tiszta marad (mu-plugin shutdown-hookon)

## Kapcsolódó

- [[wp-schema-org-mu-plugin-pattern]] — Schema.org mu-plugin párja
- [[hostinger-updraftplus-staging-migration]] — backup után újragenerálás
