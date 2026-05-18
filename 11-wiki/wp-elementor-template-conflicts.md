---
name: WordPress Elementor template-konfliktusok
type: wiki
tags: ["#tech/wordpress", "#tech/elementor", "#topic/troubleshooting"]
created: 2026-05-03
updated: 2026-05-03
---

# WordPress Elementor template-konfliktusok

Gyakori conflict-pattern-ek amikor egy classic theme-ben Elementor (vagy Elementor Pro) bekerül, és a theme template valamiért blokkolja vagy duplázza a render-t.

## Pattern 1 — Theme template hero blokkolja az Elementor canvas-t

**Tünet:** Új post létrehozásakor (különösen CPT-n) az Elementor szerkesztő "Sajnáljuk, nem található tartalmi terület az oldalon. Ahhoz, hogy az Elementor ezen az oldalon működhessen, meg kell hívnia a 'the_content' függvényt az aktuális sablonban." hibát ad. Plus a meglévő post-okon a theme-szintű hero (`<div class="mainImage">`) renderel a `the_content()` ELŐTT — Elementor edit mode-ban így a hero szerkeszthetetlen banner.

**Ok:** A theme `single-*.php` template a `the_content()`-et csak feltételhez kötve hívja meg (pl. `if ($foxxi_has_elementor) { the_content(); } else { acf_draw_sections('sections'); }`). Új post-on `_elementor_edit_mode` még nem `'builder'`, ezért az ACF-ágba megy.

**Megoldás:**

```php
// single-szolgaltatasaink.php
$foxxi_has_acf_sections = function_exists('get_field') && !empty(get_field('sections'));
if ($foxxi_has_acf_sections && !$foxxi_has_elementor) {
    acf_draw_sections('sections');
} else {
    the_content();   // mindig hívd ha NEM ACF-flexible
}
```

Plus skip-eld a template-szintű hero-t Elementor edit/preview kontextusban:

```php
$foxxi_skip_template_hero =
    (get_post_meta(get_the_ID(), '_elementor_edit_mode', true) === 'builder')
    || (class_exists('\\Elementor\\Plugin') && \Elementor\Plugin::$instance->preview && \Elementor\Plugin::$instance->preview->is_preview_mode())
    || (class_exists('\\Elementor\\Plugin') && \Elementor\Plugin::$instance->editor && \Elementor\Plugin::$instance->editor->is_edit_mode())
    || !empty($_GET['elementor-preview']);

if (!$foxxi_skip_template_hero):
    // render <div class="mainImage">...</div>
endif;
```

## Pattern 2 — Elementor MEDIA control `condition` mező lemossa a kép-értéket

**Tünet:** A `_elementor_data` JSON-ban van kép `{id, url}`, de a render-funkcióban `$item['image']` üres/0. Az imageBox üresen renderel.

**Ok:** Az Elementor `MEDIA` control-on a `condition: ['type' => 'image']` paraméter — a `get_settings_for_display()` **kihagyja** a mező értékét, ha a condition NEM teljesül (pl. `type='list'` vagy `'before'`). A JSON-ban tárolt érték elveszik a render-ben.

**Megoldás 1 (preferred):** condition eltávolítása.

```php
$rep->add_control('image', [
    'label'       => __('Kép', 'foxxi'),
    'type'        => \Elementor\Controls_Manager::MEDIA,
    'description' => __('Kép, list és before típushoz egyaránt elérhető.', 'foxxi'),
    // condition eltávolítva — get_settings_for_display() átengedi minden típuson
]);
```

**Megoldás 2:** condition bővítése: `'condition' => ['type' => ['image', 'list', 'before']]`.

**Render-shape fallback:** Elementor `MEDIA` control `{id, url}` array-t tárol; régi ACF integer ID-t. Mindkét shape-et támogasd:

```php
$img_raw = $item['image'] ?? 0;
$iid     = is_array($img_raw) ? (int) ($img_raw['id'] ?? 0) : (int) $img_raw;
$iurl    = is_array($img_raw) ? ($img_raw['url'] ?? '') : '';
$isrc    = $iid ? wp_get_attachment_image_url($iid, 'full') : ($iurl ?: '');
```

## Pattern 3 — `_elementor_data` JSON dupla-escape bug `wp_slash`/`wp_unslash` cycle-ban

**Tünet:** `_elementor_data_backup_<ts>` post meta JSON-ban a `’` Unicode-escape-ek `u2019`-ra "dezskate-elt" formára változnak (a `\` eltűnik). `json_decode` Syntax error.

**Ok:** `update_post_meta($pid, '_elementor_data_backup_X', $raw)` — ahol `$raw` már slash-elt JSON. A `update_post_meta` automatikusan `wp_unslash`-eli, ami `\\u2019` → `’` transzformációt csinál — DE a `wp_slash` előzetesen csak `\` → `\\`-t csinált, és a JSON-bemenetben már egy `’` literal volt. A két cycle elront.

**Megoldás 1 — Visszaállítás regex-szel:**

```php
function fix_unicode_strip($raw) {
    return preg_replace('/(?<!\\\\)u([0-9a-fA-F]{4})/', '\\\\u$1', $raw);
}
$fixed = fix_unicode_strip($raw);
$data = json_decode($fixed, true);
```

**Megoldás 2 — Direct DB write `wp_unslash` nélkül:**

```php
$wpdb->query($wpdb->prepare(
    "UPDATE {$wpdb->postmeta} SET meta_value=%s WHERE post_id=%d AND meta_key='_elementor_data'",
    $json, $pid
));
```

A `wpdb->update`-tel `%s` placeholder NEM fut wp_unslash-en.

**Megoldás 3 — Lokális JSON-fájl backup párhuzamosan:** mindig ments a backup-ot postmeta + filesystem fájlra is (pl. `/tmp/foxxi-id<X>-backup-<ts>.json`).

## Pattern 4 — Phase-conversion `condition`-bound mezők a save-pipeline-ban elvesznek

**Tünet:** `update_post_meta($pid, '_elementor_data', json_with_condition_field)` után az olvasáskor a `condition`-bound mező hiányzik a JSON-ból.

**Ok:** Az Elementor save-pipeline (vagy `get_settings_for_display`) szigorúan szűr a `condition`-en a mezőket. Ha a `type='before'` mezőhöz tartozó `shortcode` mezőt programmatically beillesztjük, de a JSON-ben a `type` már 'image'-re változott (vagy a save-folyamat újra-megnézi a control conditions-et), a `shortcode` lemosódik.

**Megoldás:** kerüld meg az `update_post_meta`-t és a save-pipeline-t direkt `wpdb->update` + JSON-string-replace módszerrel:

```php
$old = '"},"title":"Lézernyomtatott';                 // anchor a JSON-string-ben
$new = '"},"shortcode":"[bafg id=\\"305\\"]","title":"Lézernyomtatott';
$new_raw = str_replace($old, $new, $raw);
$wpdb->query($wpdb->prepare(
    "UPDATE {$wpdb->postmeta} SET meta_value=%s WHERE meta_id=%d",
    $new_raw, $row->meta_id
));
```

## Pattern 5 — `__()` gettext + WPML lefordítatlan string

**Tünet:** A theme `__('Szolgáltatásaink', 'foxxi')` minden EN oldalon magyarul renderel.

**Ok:** Nincs `<theme>-en_US.mo` fordítási fájl, plus a WPML String Translation nem rögzítette a stringet.

**Megoldás (WPML language-aware fallback):**

```php
$is_en = defined('ICL_LANGUAGE_CODE') && ICL_LANGUAGE_CODE === 'en';
$heading = $is_en ? 'Our services' : __('Szolgáltatásaink', 'foxxi');
```

## Kapcsolódó

- [[11-wiki/wp-acf-flexible-to-elementor-migration]] — ACF→Elementor migrációs módszertan
- [[02-Projects/foxxi]] — projekt-állapot
<!-- auto-enriched 2026-05-18: +4 semantic inbound via vault-search  (FP-fixed: -1) -->
- [[wpml-multilingual-pattern-family]] (sem-rokon, score=0.33)
- [[wp-cli-shared-db-export-fallback]] (sem-rokon, score=0.51)
- [[wp-elementor-bricks-json-escape-trap]] (sem-rokon, score=0.62)
- [[wp-notion-elementor-import-pattern]] (sem-rokon, score=0.58)
## 2026-05-04 frissítés

### Elementor JSON CRLF + NBSP encoding-buktató

A copy-paste-elt forrásszövegekben gyakran van `\r\n` (CRLF Windows-style) + `\xa0` (non-breaking space) — a WordPress automatikusan átkonvertálja, és az Elementor `_elementor_data` JSON-ban így tárolódik.

**String-match cseréknél silent-fail:** a `str_replace($hu, $en, $json)` lefut sikeresen (visszaadja a buffer-t), de **0 cserét csinál** mert a backslash-eltérés vagy NBSP miatt nem matchel.

**Megoldás:** **path-alapú direkt-write** — JSON-decode → `set_by_path()` segéd-function-nel közvetlenül cserélni a node-on belül → JSON-encode.

```php
function set_by_path(&$root, $path, $value) {
  $parts = explode('.', $path);
  $cur = &$root;
  foreach ($parts as $i => $p) {
    $key = is_numeric($p) ? (int)$p : $p;
    if (!isset($cur[$key])) return false;
    if ($i === count($parts) - 1) { $cur[$key] = $value; return true; }
    $cur = &$cur[$key];
  }
  return false;
}

// Usage:
set_by_path($data, '1.elements.0.elements.0.settings.content', $en_translated);
$wpdb->update($wpdb->postmeta, ['meta_value' => wp_json_encode($data)], …);
```

A path az `_elementor_data` JSON-strukturában: `<sectionIdx>.elements.<colIdx>.elements.<widgetIdx>.settings.<field>`.

Plus: `wp_json_encode()` default unicode-escape-eli a non-ASCII karaktereket. `JSON_UNESCAPED_UNICODE` flag-szel olvashatóbb. De a UTF-8 vs unicode-escape inkonzisztencia is silent-fail forrás — round-trip-pel (decode → manipulate → encode) ezt elkerüli.

---

## Pattern 6 — `update_post_meta` Unicode-escape backslash-strip (KRITIKUS)

**Tünet:** Egy PHP scriptben `update_post_meta($id, '_elementor_data', $json)` lefut, `Changed=1`-et ad vissza, de a renderelt frontend SEMMIT nem jelenít meg a Notion-ből betöltött tartalomból. Re-fetching `get_post_meta` után a tartalom úgy néz ki rendben.

**Ok:** A WordPress `update_post_meta` belső `wp_unslash` step-je **lestrippeli a backslash-eket** a JSON-ban lévő Unicode-escape sequence-ekből:

```
"é" (ép Unicode-escape JSON-ban — jelenti: "é")
   ↓ wp_unslash strip
"u00e9" (sérült — sem JSON-escape, sem char)
```

A frontend `json_decode` az "u00e9"-t literal stringként értelmezi (nem decode-olja "é"-vé), így a HTML-ben "Egu00e9szsu00e9ges" jelenik meg "Egészséges" helyett — vagy escape-elve üresnek látszik.

**Diagnosztika:**
```sql
SELECT LEFT(meta_value, 200) FROM wp_postmeta
WHERE post_id=<X> AND meta_key='_elementor_data';
```
Ha `Egu00e9szsu00e9ges` mintázat (vagy bármi `u00xx` sans-backslash) látszik, sérült.

**Javítás (regex-pattern):**
```php
function fix_broken_unicode($s) {
    return preg_replace_callback(
        '/(?<!\\\\)u([0-9a-fA-F]{4})/',
        function($m) {
            return mb_chr(hexdec($m[1]), 'UTF-8') ?: $m[0];
        },
        $s
    );
}

// Apply, then write back via wpdb->update (NEM update_post_meta!)
$wpdb->update(
    $wpdb->postmeta,
    ['meta_value' => fix_broken_unicode($raw)],
    ['meta_id' => $row->meta_id]
);
```

**Megelőzés:** közvetlen `wpdb->update` használata `update_post_meta` HELYETT (lásd Pattern 7).

---

## Pattern 7 — WPML+Elementor+object-cache silent revert

**Tünet:** `update_post_meta` Changed=1, log-ban OK, de a **következő** `get_post_meta` még a régi értéket adja vissza. A változás silently elveszett.

**Ok:** WPML page-builder Elementor add-on filter-rendszer hooks-ot regisztrál `updated_post_meta` action-en. A filter:
- Ellenőrzi hogy a meta-key `_elementor_data` és a post WPML-translated
- Visszaolvassa a HU "master" verziót és **felülírja** az új értéket
- Plus: object-cache (Redis dropin pl.) cache-eli a régi értéket per-request

A combinált hatás: az UPDATE megtörténik a DB-ben, de a hooks-rendszer azonnal vissza-write-olja.

**Megoldás: közvetlen `wpdb->update` direct SQL (bypass hooks):**

```php
$row = $wpdb->get_row($wpdb->prepare(
    "SELECT meta_id FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key='_elementor_data'",
    $post_id
));
$wpdb->update(
    $wpdb->postmeta,
    ['meta_value' => $json],   // RAW string, NEM wp_slash-elt
    ['meta_id' => $row->meta_id],
    ['%s'], ['%d']
);
wp_cache_delete($post_id, 'post_meta');
clean_post_cache($post_id);
delete_post_meta($post_id, '_elementor_css');  // Elementor render-cache
```

A `wpdb->update` SQL-szintű — `update_post_meta` PHP-funkció hooks NEM trigger-elődnek.

---

## Pattern 8 — `wpdb->update` és `wp_slash` dupla-escape buktató

A `_elementor_data` érték a wp_postmeta táblában **slash-elt formában** tárolódik (`\"id\":\"abc\"`). WordPress konvenció: `update_post_meta` automatikusan `wp_slash`-eli, `get_post_meta` automatikusan `wp_unslash`-eli.

**Direct `wpdb->update` esetén:**
- Nincs automatikus slash-elés
- Ha a beírt érték **már slash-elt** (pl. backup-restore-ból), és újra `wp_slash`-eled → **dupla-escape**
- A `json_decode` invalid JSON-t ad

**Helyes pattern:**

```php
// CASE 1: új érték generálva — wp_json_encode-ból (NEM slash-elt)
$json = wp_json_encode($arr, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
$wpdb->update($wpdb->postmeta, ['meta_value' => $json], …);  // RAW

// CASE 2: backup-érték restore (eredetileg update_post_meta-val íródott — slash-elt)
$wpdb->update($wpdb->postmeta, ['meta_value' => $backup_raw], …);  // RAW slash-elt

// CASE 3: get_post_meta-ből jön (unslash-elt)
$wpdb->update($wpdb->postmeta, ['meta_value' => $value], …);  // RAW unslash-elt
```

Konzervatív verifikáció + 3-szintű fallback:
```php
$verify = $wpdb->get_var(...);
$arr = json_decode($verify, true);
if (!is_array($arr)) $arr = json_decode(wp_unslash($verify), true);   // unslash fallback
if (!is_array($arr)) $arr = json_decode(stripslashes($verify), true); // dupla-escape fallback (Pattern 8 öröksége)
if (!is_array($arr)) {
    error_log("Pattern 8/dupla-escape sérült: post_id=$id");
}
```

### 2026-05-06 reprodukció — saját rebuild-script

A Pattern 8 **megint reprodukálódott** a Notion-import során (`rebuild-dental-pages.php`):

```php
// HIBÁS — dupla escape
$json = wp_json_encode($arr, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
$wpdb->update($wpdb->postmeta,
  ['meta_value' => wp_slash($json)],   // ← ez a baj
  …
);
```

**Tünet:** APPLY után a frontend 0 H2/H3-at renderelt. A `_elementor_data` mező vizuálisan tartalmazta a tartalmat, de a JSON dupla `\\\\` escape-ekkel volt feltöltve, `json_decode` invalid → Elementor parse-elés bukik.

**Fix:** `wp_slash` eltávolítva. A `$wpdb->update` belső `mysqli_real_escape` elég.

```php
// HELYES
$wpdb->update($wpdb->postmeta,
  ['meta_value' => $json],   // ← raw, nem slash-elt
  …
);
```

**Tanulság:** `$wpdb->update` SOHA `wp_slash`-szel előtte. A `wp_slash` csak akkor kell, ha az API-réteg (pl. `update_post_meta`) automatikusan `wp_unslash`-eli — `$wpdb->*` direct nem teszi. Régi mantra: "WP-funkcióval slash-elsz, wpdb-vel raw mész".

(Ugyanez a tanulság már bent van a Pattern 8 fő szövegében — itt a reprodukció dokumentálva, hogy a következő agentnek konkrét incident-példa is legyen.)

---

## Pattern 9 — `is_fox_section()` szekció-detect Elementor-preview iframe-ben

**Tünet:** Az Elementor-builder iframe-ben a téma `is_fox_section()` (vagy hasonló custom section-detector) `false`-t ad vissza, mert az URL `/?elementor-preview=2226&...` formátumú — nem tartalmaz `/fogaszat/` fragmenst.

A `foxxi-list-services` widget pl. fogszab-CPT-ket listáz a fogászati page szerkesztésekor — ami zavaró (Domi azt látja "másik oldal" megnyitva).

**Ok:** A preview-iframe URL a domain-root + query-paraméter, nem a tényleges page-permalink. URL-fragment-alapú detektálás elhasal. Plus a `is_page()` és `global $post` is gyakran nem tölt be Elementor-preview kontextusban.

**Megoldás:** query-paraméter alapú post-ID detektálás + parent-hierarchia ellenőrzés:

```php
$candidate_ids = [];
foreach (['elementor-preview', 'preview_id', 'p', 'page_id', 'post'] as $qkey) {
    if (!empty($_GET[$qkey])) {
        $candidate_ids[] = (int) $_GET[$qkey];
    }
}
foreach ($candidate_ids as $pid) {
    $p = get_post($pid);
    if (!$p) continue;
    if (in_array($p->post_name, $section_slugs, true)) return true;
    foreach (get_post_ancestors($pid) as $aid) {
        $a = get_post($aid);
        if ($a && in_array($a->post_name, $section_slugs, true)) return true;
    }
}
```

Ez minden Elementor-mode-ban (preview, edit, finder) helyesen detektál. Plus URL-fallback és `is_page()`-fallback megmarad a frontend-context-hez.

---

## Pattern 10 — Elementor render-cache invalidation direct-DB modify után

Ha közvetlen `wpdb->update`-tel írsz `_elementor_data`-ra (Pattern 7-8 mintára), a tartalom-frissítés **nem renderelődik a frontend-en**, mert az Elementor saját render-cache-ét használja:
- `_elementor_css` post_meta (page-szintű inline CSS)
- `_elementor_assets_data` option (global asset-manifest)
- Page-szintű fájl-cache (uploads/elementor/css/)

**Teljes invalidation:**

```php
delete_post_meta($post_id, '_elementor_css');
delete_option('_elementor_assets_data');
wp_cache_delete($post_id, 'post_meta');
clean_post_cache($post_id);

// Plus szerver-szintű cache (Hostinger LiteSpeed):
// wp plugin activate litespeed-cache && wp litespeed-purge all && wp plugin deactivate litespeed-cache
```

Ha a frontend-en továbbra is a régi tartalom, WP-admin: `Elementor → Tools → Regenerate CSS & Data` gomb.

A `wp w3-total-cache flush all` NEM érinti az Elementor-saját cache-t, és NEM érinti a Hostinger LiteSpeed-server cache-t.

