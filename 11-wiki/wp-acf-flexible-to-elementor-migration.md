---
name: WP ACF Flexible Content → Elementor migráció
title: WordPress — ACF Flexible Content → Elementor Pro migration playbook
created: 2026-04-29
updated: 2026-04-29
type: wiki
tags: ["#tech/wordpress", "#tech/elementor", "#tech/acf", "#playbook"]
status: living-document
project: foxxi
source-of-truth: /root/projektjeim/foxxi/theme-foxy/elementor-widgets/
license-target: MIT (planned public github repo)
---

# ACF Flexible Content → Elementor Pro migration playbook

> A theme-tied legacy WordPress site-ot (PHP partial + ACF Flexible Content alapú szekciók)
> hogyan cserélünk **vizuálisan editálható Elementorra** úgy, hogy:
>
> - URL-ek, slug-ok, SEO meta-k, redirect-ek **mind változatlanok maradnak**
> - A meglévő téma-CSS pixel-pár renderelődik (nincs vizual-regresszió)
> - A nem-tech ügyfél (Domi) az Elementor visual builder-ben szerkeszti

## Kontextus / Mikor kell

Tipikus szituáció:
- Egyedi WordPress téma, sok PHP partial-lal (`partials/section--*.php`)
- ACF Pro Flexible Content layout-okkal szekcionálható tartalom
- Az ügyfél a régi szerkesztő-flowt nehezen érti (CPT admin + ACF mezők)
- Ki akarja cserélni vagy bővíteni Elementorral, **anélkül hogy az URL-ek változnának**

A "naïv" Elementor migráció (a téma cseréje, új oldalak Elementor canvas-szal) sok problémát hoz:
- Új URL → SEO regresszió, redirect-szervezés
- A téma PHP-szekciók logikája (pl. `is_fox_section()`) elveszik
- A pixel-pár renderelés újra-építése drága (új design-system bevezetése)

## Az architektúra: 4 réteg

### 1. Réteg — base widget (abstract)

Egy `\Elementor\Widget_Base` leszármazott absztrakt osztály, ami minden widget-nek közös csontváz.

```php
// theme/elementor-widgets/base-widget.php
abstract class Foxxi_Base_Widget extends \Elementor\Widget_Base {
    public function get_categories() { return ['foxxi']; }   // saját kategória
    abstract protected function get_layout(): string;          // mely partial
    abstract protected function map_settings(array $s): array; // controls → render args

    protected function render() {
        $settings = $this->get_settings_for_display();
        $data = $this->map_settings($settings);
        // delegate render to existing theme partial
        $func_map = [
            'slider'        => 'fox_static_render_slider',
            'about'         => 'fox_static_render_about',
            'services'      => 'fox_static_render_services',
            // ...
        ];
        $fn = $func_map[$this->get_layout()] ?? null;
        if ($fn && function_exists($fn)) $fn($data);
    }
}
```

**Kulcs ötlet:** a widget **nem renderel HTML-t**, csak delegál a meglévő téma partial-jára.
Az Elementor "settings" → partial "$d array" mapping a `map_settings()`-ben történik.

### 2. Réteg — concrete widgets (thin, controls-only)

Minden ACF Flexible layout-hoz egy widget. Csak a **controls** definiálódik bennük.

```php
class Foxxi_Services_Widget extends Foxxi_Base_Widget {
    public function get_name()  { return 'foxxi-services'; }
    public function get_title() { return __('Foxxi — Szolgáltatások', 'foxxi'); }
    public function get_icon()  { return 'eicon-posts-grid'; }
    protected function get_layout(): string { return 'services'; }

    protected function register_controls() {
        $this->start_controls_section('section_text', ['label' => __('Szöveg + CTA', 'foxxi')]);
        $this->add_control('section_heading', [
            'label' => __('Cím', 'foxxi'),
            'type'  => \Elementor\Controls_Manager::TEXT,
        ]);
        $this->add_control('section_lead', [
            'label' => __('Alcím / lead szöveg (HTML megengedett)', 'foxxi'),
            'type'  => \Elementor\Controls_Manager::TEXTAREA,
            'rows'  => 5,
        ]);
        // CTA button text + URL controls...
        $this->end_controls_section();

        $this->start_controls_section('section_cards', ['label' => __('Kártyák', 'foxxi')]);
        $this->add_control('mode', [
            'type'    => \Elementor\Controls_Manager::SELECT,
            'default' => 'auto',
            'options' => [
                'auto'   => 'Automatikus (CPT-ből)',
                'manual' => 'Manuális — alább megadott lista',
            ],
        ]);
        $rep = new \Elementor\Repeater();
        $rep->add_control('image', ['type' => \Elementor\Controls_Manager::MEDIA]);
        $rep->add_control('title', ['type' => \Elementor\Controls_Manager::TEXT]);
        $rep->add_control('link',  ['type' => \Elementor\Controls_Manager::TEXT]);
        $this->add_control('services', [
            'type'        => \Elementor\Controls_Manager::REPEATER,
            'fields'      => $rep->get_controls(),
            'title_field' => '{{{ title }}}',
            'condition'   => ['mode' => 'manual'],
        ]);
        $this->end_controls_section();
    }

    protected function map_settings(array $s): array {
        $services = [];
        foreach (($s['services'] ?? []) as $row) {
            $services[] = [
                'image' => $row['image']['id'] ?? 0,
                'title' => $row['title'] ?? '',
                'link'  => $row['link']  ?? '',
            ];
        }
        return [
            'section_heading' => $s['section_heading'] ?? '',
            'section_lead'    => $s['section_lead']    ?? '',
            'mode'            => $s['mode']            ?? 'auto',
            'services'        => $services,
        ];
    }
}
```

### 3. Réteg — render partial (extended for overrides)

A meglévő téma partial-t kibővítjük úgy, hogy a paraméterezett `$d` array-ből
felülírható minden mező, **az ACF default érték pedig fallback marad**.

```php
// static-sections/render.php
function fox_static_render_services(array $d): void {
    // 1. Téma-szintű alapértelmezések (is_fox_section() alapján más-más)
    if (is_fox_section()) {
        $default_heading = 'Szolgáltatásaink';
        $default_lead    = 'A teljeskörű fogászati ellátás...';
    } else {
        $default_heading = 'Szolgáltatásaink';
        $default_lead    = 'Mindketten kizárólag fogszabályozással...';
    }

    // 2. Per-instance override (Elementor / ACF / shortcode mind ugyanezt küldi)
    $section_heading = !empty($d['section_heading']) ? $d['section_heading'] : $default_heading;
    $section_lead    = isset($d['section_lead']) && $d['section_lead'] !== ''
                         ? $d['section_lead']
                         : $default_lead;

    // 3. Cards: $d['mode'] === 'manual' → $d['services'] lista,
    //     egyébként WP_Query a CPT-re
    if (($d['mode'] ?? 'auto') === 'manual' && !empty($d['services'])) {
        $cards = array_map(fn($s) => [
            'title'   => $s['title'] ?? '',
            'link'    => $s['link']  ?? '',
            'img_url' => $s['image'] ? wp_get_attachment_image_url($s['image'], 'thumbnail') : '',
        ], $d['services']);
    } else {
        // Auto: WP_Query a CPT-re ($args is_fox_section() szerint)
    }

    // 4. Render — ugyanaz az HTML mint az eredeti partial
    ?>
    <div class="section-service">
        <!-- ... -->
    </div>
    <?php
}
```

**Kulcs ötlet:** a partial 3 hívási kontextusban **ugyanúgy működik**:
- ACF Flexible Content (régi) — `acf_draw_sections()` → `case 'services': fox_static_render_services($section)`
- Elementor widget (új) — `Foxxi_Services_Widget::render()` → `fox_static_render_services($mapped_settings)`
- Shortcode — `[foxxi_section type="services"]` → `fox_static_render_services($section_data)`

### 4. Réteg — loader

```php
// theme/elementor-widgets/loader.php
if (!did_action('elementor/loaded')) return;

add_action('elementor/elements/categories_registered', function ($mgr) {
    $mgr->add_category('foxxi', ['title' => 'Foxxi szekciók', 'icon' => 'fa fa-plug']);
});

add_action('elementor/widgets/register', function ($mgr) {
    require_once __DIR__ . '/base-widget.php';
    foreach (['slider', 'about', 'services', 'testimonials', 'feature', 'repeater', 'contact'] as $name) {
        require_once __DIR__ . '/widget-' . $name . '.php';
        $cls = 'Foxxi_' . ucfirst($name) . '_Widget';
        if (class_exists($cls)) $mgr->register(new $cls());
    }
});
```

## CSS bridge (kötelező)

A téma partial-jai gyakran full-bleed background blokkokat (`.section-service`,
`.featureRow`) emit-elnek és Bootstrap row-kat negatív margin-nel.
Az Elementor section default 1140px boxed container-rel jön, ami **levágja**
a full-bleed háttért és a row-okat.

A megoldás: minden Elementor section/column/widget-wrap-ot ami foxxi-* widget-et
tartalmaz, full-width-re kényszeríteni.

```css
.elementor-section:has([class*="elementor-widget-foxxi-"]),
.elementor-element.elementor-section:has([class*="elementor-widget-foxxi-"]) {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
  width: 100% !important;
}
.elementor-section:has([class*="elementor-widget-foxxi-"]) > .elementor-container {
  max-width: 100% !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}
.elementor-section:has([class*="elementor-widget-foxxi-"]) .elementor-column,
.elementor-section:has([class*="elementor-widget-foxxi-"]) .elementor-widget-wrap {
  padding: 0 !important;
  margin: 0 !important;
}
[class*="elementor-widget-foxxi-"] > .elementor-widget-container {
  padding: 0 !important;
  margin: 0 !important;
}
```

A `:has()` modern szelektor (2026 minden browser-ben működik). Plusz a generator
script section-szettings-ekben is `content_width: 'full_width'`, padding/margin = 0.

## Migration script — elementor_data generálás PHP-ben

A page `_elementor_data` post meta-ja JSON, amit **kódból generálhatunk**, hogy
az ACF Flexible mezőket → Elementor widget-ekre konvertáljuk:

```php
// scripts/migrate-page-to-elementor.php
// wp eval-file ./scripts/migrate-page-to-elementor.php

$page_id = 2;  // pl. fogszab homepage

// 1. Az ACF sections backup-olása
$acf_sections = get_post_meta($page_id, 'sections', true);
update_post_meta($page_id, '_acf_backup_' . date('Ymd'), $acf_sections);

// 2. Az ACF layout-ok mappolása foxxi-* widget-ekre
$id_seq = 0;
$el_id  = fn() => substr(md5('mig-' . ++$id_seq), 0, 7);
$img    = fn($id) => ['id' => (int) $id, 'url' => wp_get_attachment_url($id)];

$section_with_widget = function ($widget_type, array $settings = []) use ($el_id) {
    $zero = ['unit' => 'px', 'top' => '0', 'right' => '0', 'bottom' => '0', 'left' => '0', 'isLinked' => true];
    return [
        'id' => $el_id(), 'elType' => 'section',
        'settings' => [
            'content_width' => ['unit' => 'full_width', 'size' => '', 'sizes' => []],
            'gap' => 'no', 'padding' => $zero, 'margin' => $zero,
        ],
        'elements' => [[
            'id' => $el_id(), 'elType' => 'column',
            'settings' => ['_column_size' => 100, '_inline_size' => null, 'padding' => $zero, 'margin' => $zero],
            'elements' => [[
                'id' => $el_id(), 'elType' => 'widget',
                'widgetType' => $widget_type,
                'settings' => (object) $settings,
                'elements' => [],
            ]],
        ]],
    ];
};

$elements = [];
foreach ($acf_sections as $section) {
    switch ($section['acf_fc_layout']) {
        case 'slider':
            $elements[] = $section_with_widget('foxxi-slider', [
                'slides' => array_map(fn($s) => [
                    '_id'     => substr(md5(json_encode($s)), 0, 7),
                    'image'   => $img($s['image']),
                    'title'   => $s['title'] ?? '',
                    'content' => $s['content'] ?? '',
                    'link'    => $s['link'] ?? '',
                ], $section['slides'] ?? []),
            ]);
            break;
        case 'services':
            // ...
            break;
        // case-ek minden ACF layoutra
    }
}

// 3. Persistence
update_post_meta($page_id, '_elementor_edit_mode', 'builder');
update_post_meta($page_id, '_elementor_template_type', 'wp-page');
update_post_meta($page_id, '_elementor_version', ELEMENTOR_VERSION);
update_post_meta($page_id, '_wp_page_template', 'elementor_header_footer');

$json = wp_json_encode($elements, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
update_post_meta($page_id, '_elementor_data', wp_slash($json));

\Elementor\Plugin::$instance->files_manager->clear_cache();
```

**Fontos:** `wp_slash($json)` **kötelező** — a `wp_unslash()` ami a WP core-ban
sok helyen fut, eszi a backslash-eket a JSON-ban (pl. `ő` → `u0151`).

## Domi-barát szerkeszthetőség (UX)

Egy **non-tech ügyfél** (Domi) UX-ben placeholder + üres input == "ezt nem tudom szerkeszteni".

**Pattern:** a generator script tölts fel **valódi tartalommal** minden szöveg/URL/repeater mezőt:
- Heading / lead / CTA: explicit ortho/fox default szöveggel
- Repeater (services, testimonials, team): pre-generated lista a CPT-ből (`mode: 'manual'`)
- Kép kontroll: `wp_get_attachment_image_url($id, 'thumbnail')` URL-lel

Ez kulcsfontosságú — placeholder-rel hagyott input-okat az ügyfél nem találja meg.

**Render-pattern a partial-ban:** `!empty($d['x']) ? $d['x'] : $default` — ha a user
kitörli az értéket (üresre teszi), visszaesik a téma alapszövegére (V2 paritás).

## URL-megőrzés (zero-downtime)

```bash
# 1. Az új Elementor data egy STAGING URL-en (pl. /fogszab-v5/) készül
wp eval-file scripts/create-fogszab-v5-page.php

# 2. Vizuális ellenőrzés Playwright-tal vagy manuálisan
curl -s "https://site/fogszab-v5/?nocache=1" | head

# 3. Ha minden OK: az _elementor_data-t bemásoljuk a LIVE post-ra
LIVE_ID=2  # /fogszabalyozas-invisalign/
STAGING_ID=2269  # /fogszab-v5/

DATA=$(wp post meta get $STAGING_ID _elementor_data)
wp post meta update $LIVE_ID _acf_backup_$(date +%Y%m%d) "$(wp post meta get $LIVE_ID _elementor_data 2>/dev/null)"
wp post meta update $LIVE_ID _elementor_data "$DATA"
wp post meta update $LIVE_ID _elementor_edit_mode builder
wp post meta update $LIVE_ID _wp_page_template elementor_header_footer

wp cache flush && wp w3-total-cache flush all
```

URL nem változik. SEO marad. Domi a meglévő admin URL-en találja meg.

## Header / Footer (Elementor Pro Theme Builder)

Elementor Pro-val:
1. Templates → Theme Builder
2. Új Header template, display condition: "Entire site" vagy specifikus szekció
3. Az Elementor saját header-widget-jeit használjuk (Site Logo, Nav Menu, Search, stb.)
4. Vagy custom Foxxi widget a fejléchez (logó + menu + cta gomb)

A téma `header.php` / `footer.php` **fall-back** marad — ha nincs Theme Builder
template aktív, a téma renderel. Ez biztonsági háló.

## Auto vs Theme-fox / Theme-ortho

A `is_fox_section()` PHP függvény (body class swap) **változatlan marad**.
Az Elementor renderelt page-ek is megkapják a `theme-fox` / `theme-ortho` body
class-t, és a CSS override-ok (`.split-hero.css`) érvényesülnek. Tehát:

- Ortho oldalak (fogszab) → barna design
- Fox oldalak (fogászat) → narancs design

Mind a kettő ugyanazokat a `foxxi-*` widget-eket használja, csak a render
partial belül `is_fox_section()`-tel váltogat default-okat és színeket.

## Backup + rollback

Minden migrate-elt page-ra:
```sql
update_post_meta($page_id, '_acf_backup_' . date('Ymd'), $acf_sections);
update_post_meta($page_id, '_elementor_data_backup_' . date('Ymd'), $old_data);
```

Rollback: `wp post meta update $page_id _elementor_data ''` és/vagy az ACF mezőt visszaírni.

## Phase 5 — gyakorlati tanulságok (FOXXI, 2026-04-29 → 2026-04-30)

### 5a. AI image generation workflow — nano-banana CLI

A Foxxi fogászati szekció redesign-jához ~30 generált hero/portrait kép készült Gemini 3.1 Flash Image Preview-vel, batch-ben.

**Setup:**

```bash
# nano-banana CLI install (per-host)
git clone https://github.com/kingbootoshi/nano-banana-2-skill ~/tools/nano-banana-2
cd ~/tools/nano-banana-2 && bun install && bun link
echo "GEMINI_API_KEY=..." > ~/.nano-banana/.env
```

**Per-image cost:** ~$0.09 (Gemini 3.1 Flash). 20 hero kép ~$1.80.

**Tematikus prompting per page-type:**

- Hero banner (21:9): "Wide cinematic horizontal banner. {scene}. Empty space on {side} for caption overlay. Editorial photography. 21:9 ultrawide aspect."
- Team portrait (1:1): "Professional headshot of Hungarian {gender} dentist in white coat. Light cream background. 1:1 square aspect."
- Service hero (3:2): "{service-specific dental scene}. Premium clinical photography. 3:2 aspect."

**Parallel generation:** több nano-banana hívás párhuzamosan (`&` shell), 3-4 db egyszerre OK.

**Bulk upload to WP:**

```bash
for f in hero-rolunk hero-szolg ...; do
  scp "${f}.png.jpeg" "host:/tmp/foxxi-${f}.jpg"
done
ssh host 'wp media import /tmp/foxxi-${f}.jpg --title="..." --porcelain'
```

A `--porcelain` flag visszaadja az új attachment ID-t — rögzítsd egy mapping array-be a generator script-be.

### 5b. Page-hero (`.mainImage.mainImagePage`) reprodukálása Elementorban

A foxy theme natív `single-{cpt}.php` template-jeiben van egy `<div class="mainImage mainImagePage">` block (featured image hero + page title overlay). Az `elementor_header_footer` page-template viszont nem rendeli ezt — a tartalom közvetlenül a header alatt kezdődik, ami csúnya.

**Megoldás:** új `foxxi-page-hero` widget ami pixel-pár 1:1 másolatát adja vissza a foxy `mainImage` HTML-jének:

```html
<div class="mainImage mainImagePage">
  <div class="imageBox"><img src="..." style="object-position:..." /></div>
  <div class="container-fluid"><div class="row"><div class="col-12">
    <div class="caption"><h1>...</h1></div>
  </div></div></div>
</div>
```

Mindkét SVG (`.caption` narancs trapéz overlay + `.blockquote.top blockquote` ötszög) **egymásba illeszkedik** ha a következő `.blockquote.top` `.pink` color-ban renderel (`#fcefe7` rózsa-krém háttér). A `feher` color a két SVG közötti vizuális gap-et okozza.

**CSS fix az illeszkedéshez:**

```css
.elementor-section:has(.elementor-widget-foxxi-page-hero) + .elementor-section .blockquote.top {
  margin-top: 0 !important;
  padding-top: 0 !important;
}
body.theme-fox .blockquote.top.feher,
body.theme-ortho .blockquote.top.feher {
  background: #fcefe7 !important;
}
```

**Migration script** (idempotens): `array_unshift($elements, $page_hero_section)` — a meglévő `_elementor_data` elejére beilleszti a hero-t. Ha már van, csak a settings-et frissíti.

### 5c. Theme color pivot — SVG hue-rotate trükk

Ha **runtime** akarsz színt cserélni egy theme `body` class alapján (pl. fogászat narancs → türkiz/zöld), és a HTML/SVG-k már narancsban vannak hard-coded:

```css
body.theme-fox .mainImage .caption,
body.theme-fox .blockquote.top blockquote {
  filter: hue-rotate(120deg) saturate(0.85);
}
/* A szöveget visszafordítjuk hogy ne színeződjön: */
body.theme-fox .mainImage .caption h1,
body.theme-fox .blockquote.top blockquote div {
  filter: hue-rotate(-120deg) saturate(1.18);
  color: var(--target-color) !important;
}
```

**Hue-rotate(120deg)** narancs → zöld átfordítás. **Saturate(0.85)** kissé kontroll-csillapít a túltelítettség ellen.

A **dupla-filter pattern** (parent: hue-rotate, child: ellenkezőleg) megőrzi a szöveg-színt, csak a SVG-háttért érinti.

### 5d. ACF Options-fallback PHP — `??` vs `!empty()`

A render-funkciókban gyakran szükséges:

```php
// HIBÁS — a `??` csak null esetén ad fall-back-et:
$footer_contact = $d['footer_contact'] ?? get_field('footer_contact', 'options');
// Ha $d['footer_contact'] = '' (üres string), a $? nem fall-back-el.

// HELYES:
$pick = fn($v, $k) => !empty($v) ? $v : get_field($k, 'options');
$footer_contact = $pick($d['footer_contact'] ?? '', 'footer_contact');
```

Az Elementor widget settings-ből gyakran üres string érkezik (nem null), ezért `!empty()`-ternary kell.

### 5e. Brand color tokens — 10-shade scale

Új **Foxxi Dental Mint** paletta (#f3faf7 → #154e46) `--fox-mint-50` … `--fox-mint-900` formában a `foxxi-brand.css`-ben. Lehetővé teszi a jövőben:

- Elemenkénti szín-finomítás (mid-light hover, deep accent, stb.)
- Dark/light theme-toggle bevezetése
- A/B teszt különböző accent-szintekkel

Az eredeti foxszab paletta (`--foxxi-orange`, `--foxxi-brown`, stb.) **érintetlen marad** — a fogszab oldalak (theme-ortho) változatlanok.

### 5f. Hibajegyzék: Foxxi Phase 1-5 (3 nap, 20 oldal + theme builder)

| # | Issue | Root cause | Fix |
|---|---|---|---|
| 1 | Header overlap content | `elementor_header_footer` template + foxy `.placeholder` 80px nem elég | `:first-of-type` section padding-top 40px (kivéve ha page-hero) |
| 2 | Repeater "before"-type képek nem renderelnek | `[bafg]` shortcode HTML rendben, de jQuery twentytwenty plugin nem inicializál | `fox_ensure_twentytwenty_assets()` enqueue helper |
| 3 | aboutWrapper text fehér marad cream alapon | foxy `.aboutWrapper * { color: #fff }` magasabb specificity | universal-selector + `!important` override |
| 4 | Theme Builder display condition nem triggerel | `'general/include'` formátum hibás | helyes: `'include/general'` |
| 5 | Footer üres (Kapcsolat/Social) | `$d['x'] ?? $opt(...)` üres string fall-back hiba | `!empty()`-ternary |
| 6 | Hero+blockquote vizuális gap | `.blockquote.top.feher` fehér, kell `pink` (#fcefe7) | universal `:not(.brown):not(.pink)` override |
| 7 | Mind 11 fogászat oldal placeholder ACF-fel | `normal_content` + üres mezők | `notion.md` brief alapján 100% tartalom-feltöltés |
| 8 | Theme color pivot rajzolt SVG-kkel | hard-coded narancs SVG-k | `filter: hue-rotate(120deg)` + dupla-filter szöveg-megőrzés |

## Phase 4 — Theme Builder display condition format (FOXXI, 2026-04-29)

Az Elementor Pro Theme Builder display condition formátuma:

- **Helyes:** `'include/general'` — entire site (vagy `'include/post/123'` egy post-ra)
- **Helytelen:** `'general/include'` — ezt a `parse_condition()` `type='general', name='include'`-ra parse-olja, és az `$is_include = 'include' === 'general'` false → a feltétel sosem match-el

A `parse_condition()` az Elementor Pro `conditions-manager.php`-ban explode `/`-vel: első szegmens = type ('include' vagy 'exclude'), második = name ('general', 'singular', 'archive', stb.), harmadik+ = sub-target.

Plus: a `_elementor_conditions` post meta + `elementor_pro_theme_builder_conditions` option együtt működnek. A cache `regenerate()` is futnia kell:

```php
\ElementorPro\Modules\ThemeBuilder\Module::instance()
    ->get_conditions_manager()
    ->get_cache()
    ->regenerate();
```

A téma natív `header.php` / `footer.php`-t override-olni kell, hogy az `elementor_theme_do_location('header')` hookot meghívja — különben a Theme Builder template nem kapcsolódik be:

```php
// header.php elejére:
if (function_exists('elementor_theme_do_location') && elementor_theme_do_location('header')) {
    // TB rendered <header> — skip the legacy theme markup
} else {
    // ... eredeti theme header HTML
}
```

## Phase 2 — JS-init függő slider/carousel widgetek (FOXXI, 2026-04-29)

A `gallery_carousel` (Swiper-alapú) és `before_and_after_gallery` (jQuery
twentytwenty) layout-ok renderelt HTML-jük van rendben — viszont a
**JS init** nem fut Elementor render-context-ben, mert a téma frontend.js
ACF-context-függő szelektorral keresi a slider div-eket, vagy a script
csak a `wp_enqueue_scripts` hook-ban kerül be a meglévő ACF-szekcióknál.

Részleges fix: `fox_ensure_twentytwenty_assets()` helper enqueue-olja a
twentytwenty plugin script-jeit `wp_enqueue_scripts` hook helyett közvetlenül
a render funkcióból. De a Swiper init-hez (gallery_carousel) is hasonló
kéne, és néha a CSS is a plugin saját stylesheet-jéből hiányzik.

**Tanulság:** plugin-függő slider/carousel widget-eknél deploy után tesztelni
kell hogy a JS frontend valóban inicializál — különben a HTML látható
elemek (img tag) láthatatlanok maradnak CSS / overflow:hidden miatt.
Visual issue, nem blokkoló a migrációhoz — a tartalom HTML-ben szerepel,
Domi szerkeszteni tudja.

## Phase 2 — repeater "before" altípus (FOXXI, 2026-04-29)

A `repeater` layout-nak több `type` altípusa van: `image`, `text`, `before`.
A `before` típus esetén a kép helyett **WordPress shortcode** renderelődik
(pl. `[bafg id="321"]` → előtte/utána slider). Az adatszerkezetben a `image`
mező hiányzik, helyette `shortcode` mező van.

A `fox_static_render_repeater()`-be hozzá kell adni: `if ($type === 'before')
echo apply_shortcodes($shortcode); else echo '<img ...>';` — különben a
shortcode-os repeater elemek **kép-placeholder helyként** jelennek meg.

## Phase 2 — plugin-függő ACF layout-ok (FOXXI, 2026-04-29)

A `video_carousel` és `before_and_after_gallery` ACF layout-okat dedikált
plugin-ok renderelik (`foxxi-video-carousel` 1.2.0, `foxxi-before-after-v331`).
A `partials/section--video_carousel.php` fallback az `acf_draw_sections()`
ACF-context-ot várja (`get_row()`, `get_sub_field()`) — Elementor render-context-ben
ez NEM működik.

Megoldás: a generator script kiolvassa a `sections_X_videos_Y_*` mezőket és
**explicit array-ben** átadja az Elementor widget settings-be. A
`fox_static_render_video_carousel()` függvénynek így a `$d['videos']` array
elég lesz, plugin nélkül is renderel.

Tanulság: minden plugin-által-renderelt ACF layout-ot **standalone** PHP
függvénybe kell extract-elni a render.php-ben — különben az Elementor migráció
plugin-függőségbe ütközik.

## Phase 2 — partial-feature parity gotcha (FOXXI, 2026-04-29)

A theme `partials/section--<layout>.php` partial-jaiban gyakran több branch
van (pl. contact: `info_enable` vs `img_left` ágak). Az első round-ban a
`fox_static_render_<layout>()` extracted függvényt csak EGY ág-ra írtam
meg (img_left, mert a fogszab homepage-en az kellett) — Kapcsolat oldalon
viszont `info_enable=1, img_left=0` jött, és az info-kártya (Rendelő /
Nyitvatartás / utvonalList) néma maradt.

**Tanulság:** új page migrációja előtt diff-elj a teljes partial-lal és
ellenőrizd hogy MINDEN feltételes ág át van-e véve. ACF Options-page mezők
(`get_field('x', 'options')`) mind elérhetőek render-context-ben is, nem
ACF-flexible-context-only.

## Phase 1 — gyakorlati tanulságok (FOXXI, 2026-04-29)

- A LIVE post `_elementor_data` 0-byte volt → tehát az ACF render-flow független az Elementor adattól. Phase 1-ben elég volt a `_wp_page_template` átállítás (`default` → `elementor_header_footer`) + `_elementor_data` feltöltése, az ACF mezőket NEM kellett törölni — érintetlenül backupban maradnak, és a régi template visszaállítása rollback.
- Teljes post_meta JSON backup gyors (~21KB / page) — érdemes minden phase-nél csinálni `/tmp/foxxi-id<X>-backup-<timestamp>.json` fájlba.
- `wp post meta get` üres value-ra exit code 1-et ad, scriptelni `2>/dev/null` szükséges.
- Cache-flush mátrix Hostinger-en: `wp cache flush && wp w3-total-cache flush all` + Elementor `\Elementor\Plugin::$instance->files_manager->clear_cache()` PHP-ből, plusz `?nocache=N` query a Hostinger CDN bypass-hoz vizuális ellenőrzéskor.

## Hibakeresési sufnitár

| Tünet | Diagnózis |
|---|---|
| Brown szekció középen 1140px-ben | Section content_width nem 'full_width' / CSS bridge nem érvényesül → cache flush |
| `ő` literál szöveg | `wp_slash()` hiányzik az `update_post_meta` előtt |
| Kép szétnyúlik 50%-ra | `medium_large` méret aránytalan kép esetén → `thumbnail` (150x150 crop) |
| WPML "Undefined array key fields" warning | Non-blocking, WPML translation parser nem ismeri custom widget-et |
| Admin canvas-on classic editor | Disable Gutenberg / Classic Editor plugin → `use_block_editor_for_post` filter |

## Status / TODO (FOXXI projekt-specifikus)

- [x] V1: ACF Flexible (eredeti)
- [x] V2: PHP static renderer (`/fogszab-v2/`)
- [x] V3: Gutenberg core blocks (`/fogszab-v3/`)
- [x] V4: Custom Gutenberg dynamic blocks (`/fogszab-v4/`)
- [x] V5: Elementor custom widgets (`/fogszab-v5/`)
- [ ] Phase 1: V5 → ID 2 (live homepage)
- [ ] Phase 2: 8 fő fogszab oldal migrálás (Rólunk, Miért a Foxxi, ..., Karrier)
- [ ] Phase 3: 6 szolgáltatás CPT → Elementor edit mode
- [ ] Phase 4: Header + Footer Theme Builder template
- [ ] Phase 5: Fogászat (Fox) szekció új design-system + content copy

## Forrás-fájlok (FOXXI repo)

```
/root/projektjeim/foxxi/
├── theme-foxy/elementor-widgets/
│   ├── loader.php
│   ├── base-widget.php
│   ├── widget-slider.php
│   ├── widget-about.php
│   ├── widget-services.php
│   ├── widget-testimonials.php
│   ├── widget-feature.php
│   ├── widget-repeater.php
│   └── widget-contact.php
├── theme-foxy/static-sections/render.php   # 7 fox_static_render_*() funkció
├── theme-foxy/assets/css/split-hero.css    # CSS bridge
└── scripts/create-fogszab-v5-page.php      # generator
```

## License plan

Ez a playbook + példa kód publikus GitHub repó alapanyaga lesz: `acf-to-elementor-migration` (MIT).

## Kapcsolódó

