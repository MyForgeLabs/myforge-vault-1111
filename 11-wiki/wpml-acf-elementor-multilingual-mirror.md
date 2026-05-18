---
name: WPML ACF→Elementor multilingual mirror — 3-lépéses fordítási pipeline
type: wiki
tags: ["#tech/wordpress", "#tech/wpml", "#tech/elementor", "#tech/acf", "#topic/playbook"]
created: 2026-05-03
updated: 2026-05-03
---

# WPML ACF→Elementor multilingual mirror

3-lépéses fordítási pipeline ahhoz, amikor egy **WPML-multilingual WP site**-on a HU oldalak **Phase 1-3-as ACF Flexible Content → Elementor migráción** átestek, de az EN nyelvi-páros oldalak NEM. Plus később a HU-n új tartalom került Elementor widget-szinten ami az EN ACF-ben nincs.

## Kontextus

- HU oldal Phase 1-3 előtt: ACF Flexible Content (`sections` post_meta) — magyar szöveg
- HU oldal Phase 1-3 után: Elementor `_elementor_data` JSON — magyar szöveg
- HU oldal Phase 5+ után: új Elementor widget-ek (foxxi-page-hero, foxxi-cross-link) — új magyar szöveg
- EN páros: ACF Flexible Content `sections` post_meta angolul (régi szakmai fordítás), Elementor `_elementor_data` üres vagy hiányzó

**Cél:** EN oldalak ugyanaz a Elementor-szerkeszthető layout mint a HU-n + EN szöveg minden release pontossággal. A régi szakmai EN fordítást **megőrizzük**.

## 3-lépéses pipeline

### Lépés 1 — HU `_elementor_data` mirror EN-re

```php
$hu_data = get_post_meta($hu_id, '_elementor_data', true);
$wpdb->query($wpdb->prepare(
    "UPDATE {$wpdb->postmeta} SET meta_value=%s WHERE post_id=%d AND meta_key='_elementor_data'",
    $hu_data, $en_id
));
update_post_meta($en_id, '_elementor_edit_mode', 'builder');
update_post_meta($en_id, '_wp_page_template', 'elementor_header_footer');
update_post_meta($en_id, '_thumbnail_id', get_post_meta($hu_id, '_thumbnail_id', true));
```

**Eredmény:** EN oldalon a HU layout 1:1 azonos, de **magyar szöveg**.

### Lépés 2 — EN ACF Flexible Content lookup → szakmai EN szöveg

A meglévő `sections_*` post_meta-kból építünk widget-szöveg-listát, és a HU `_elementor_data` minden widget-jébe (azonos `widgetType` és occurrence-index alapon) bekapcsoljuk:

```php
function en_acf_sections($pid) {
    $layouts = maybe_unserialize(get_post_meta($pid, 'sections', true));
    if (!is_array($layouts)) return [];
    global $wpdb;
    $out = [];
    foreach ($layouts as $idx => $layout) {
        $section = ['type' => $layout, 'fields' => [], 'repeaters' => []];
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT meta_key, meta_value FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key LIKE %s",
            $pid, "sections_{$idx}_%"
        ));
        foreach ($rows as $r) {
            $rel = substr($r->meta_key, strlen("sections_{$idx}_"));
            if (preg_match('/^([a-z_]+)_(\d+)_(.+)$/', $rel, $m)) {
                $section['repeaters'][$m[1]][(int)$m[2]][$m[3]] = $r->meta_value;
            } else {
                $section['fields'][$rel] = $r->meta_value;
            }
        }
        $out[] = $section;
    }
    return $out;
}
```

A HU `_elementor_data` widget-jeit végigjárjuk (occurrence-index alapján foxxi-blockquote[0], foxxi-repeater[1], stb.), és ha van EN ACF megfelelő, **a szöveg-mezőket** (title, section_title, content, description, button_text) cseréljük. **A képeket, layout-konfig-ot, ID-kat megőrizzük** a HU-ról.

**ACF layout → Elementor widget mapping:**

| ACF layout | Elementor widget |
|---|---|
| `repeater` | `foxxi-repeater` |
| `blockquote` | `foxxi-blockquote` |
| `services` | `foxxi-services` |
| `testimonials` | `foxxi-testimonials` |
| `gallery_carousel` | `foxxi-gallery_carousel` |
| `before_after_gallery` | `foxxi-before_after_gallery` |
| `video_carousel` | `foxxi-video-carousel` |
| `cta` | `foxxi-cta` |

### Lépés 3 — Hardcoded HU→EN szótár (Phase 5+ új tartalom)

Az új Elementor-only widget-ek (foxxi-page-hero, foxxi-cross-link, foxxi-choice) **NINCSENEK** az EN ACF-ben. Plus pár Phase 5+ módosítás elhagyhatott egyes szövegeket. **Hardcoded mapping** a maradékra:

```php
$translations = [
    'Miért a Foxxi?' => 'Why Foxxi?',
    'Bemutatkozunk' => 'About us',
    'Pácienseink kamera előtt' => 'Our patients on camera',
    'Kriszta egész családjának rendbe tettük a fogait' => 'We straightened the teeth of Kriszta\'s entire family',
    /* ... 200+ entry ... */
];

uksort($translations, function($a, $b) { return strlen($b) - strlen($a); });  // longest-first

function tx(&$node, $map) {
    if (is_string($node)) {
        if (isset($map[$node])) { $node = $map[$node]; return; }
        foreach ($map as $hu => $en) {
            if (strpos($node, $hu) !== false) {
                $node = str_replace($hu, $en, $node);
            }
        }
    } elseif (is_array($node)) {
        foreach ($node as $k => &$v) tx($v, $map);
        unset($v);
    }
}
```

**Longest-first sortolás** fontos: ha "FOGSZABÁLYOZÁS" előtt "FOGSZAB" cserélődik le "ORTHO"-ra, akkor a végén "ORTHOÁLYOZÁS" lesz. Hosszabb match előbb.

## WPML language-aware render fallback

Theme render-funkciókban hardcoded HU stringek esetén a `ICL_LANGUAGE_CODE` alapján fallback-elni:

```php
$is_en = defined('ICL_LANGUAGE_CODE') && ICL_LANGUAGE_CODE === 'en';
$heading = $is_en ? 'Our services' : __('Szolgáltatásaink', 'foxxi');
```

Plus a CTA-linkek és parent-ID-k WPML language-context szerint:

```php
$default_btn_url = $is_en ? '/en/our-services/' : '/szolgaltatasaink/';
$parent_id = $is_en ? 2244 : 2226;
```

## WPML "being translated" warning eltávolítása

Ha az EN-page renderelődve a tartalom helyett "⚠ This page is being translated. Below is the Hungarian source content for reference." warning-ot mutat:

```sql
UPDATE wp_icl_translations SET source_language_code=NULL WHERE element_id=628 AND language_code='en';
```

Plus töröld a `post_content`-be beszúrt warning-szöveget:

```bash
wp post update 628 --post_content=""
wp post meta delete 628 _yoast_wpseo_metadesc
wp post meta delete 628 _yoast_wpseo_opengraph-description
```

## Kapcsolódó

- [[11-wiki/wp-acf-flexible-to-elementor-migration]] — Phase 1-3 ACF→Elementor metodológia
- [[11-wiki/wp-elementor-template-conflicts]] — Elementor template-conflictok
- [[02-Projects/foxxi]] — Foxxi projekt-state ahol ezt használtuk

## 2026-05-04 frissítés

### WPML primary-menu-en slug-ütközés (kritikus gotcha)

Ha új EN nav-menut hozol létre **`primary-menu-en` slug-gel**, a `wp_get_nav_menu_object('primary-menu-en')` a HU `primary-menu` term-et adja vissza (term 9), mert WPML automatikusan EN-translation-virtuális-slug-ként interpretálja.

**Megoldás:** egyedi slug, pl. `primary-menu-english`. A theme-szintű `fox_swap_menu` filter-ben `'primary-menu-english'`-t kell használni.

### Language Switcher két kritikus bug

A custom `fox_append_language_switcher` filter-ben (vagy hasonló WPML-aware switcher-ben):

1. **`wpml_object_id` post_type-érzékeny** — hardcoded `'page'` esetén a `szolgaltatasaink` (vagy bármely más CPT) translation-pár NEM map-elődik. Mindig dinamikusan a `$post->post_type`-tal hívd:

```php
$cur_post_type = $post->post_type ?? 'page';
$target_pid = apply_filters('wpml_object_id', $post->ID, $cur_post_type, false, $target_lang);
```

2. **`get_permalink()` aktuális nyelvi-kontextusban** — EN page-en hívva EN URL-t ad vissza, NEM a target HU URL-t. Switcher generálásához nyelvi-kontextus váltás kell:

```php
do_action('wpml_switch_language', $target_lang);
$target_url = get_permalink($target_pid);
do_action('wpml_switch_language', $cur_lang);
```

