---
name: Foxxi design system
title: Foxxi Design System — két szekció (theme-ortho + theme-fox) színpaletta + tipográfia
created: 2026-04-30
updated: 2026-04-30
type: wiki
tags: ["#tech/wordpress", "#tech/css", "#foxxi", "#design-system"]
status: living-document
project: foxxi
related:
  - wiki/wp-acf-flexible-to-elementor-migration
---

# Foxxi Design System

A Foxxi WordPress site **kettős szekciójú**: ugyanaz a `foxy` theme + ugyanaz a Theme Builder header/footer renderel **két különböző brand-élménnyel**, attól függően hogy a látogató a fogszab vagy a fogászat oldalon van.

A kettősséget egy single body class váltás vezérli (`is_fox_section()` → `theme-fox` vs `theme-ortho`).

## Szekció-architektúra

```
                                ┌────────────────────────────────────────┐
       /  (Választó)            │  /fogaszat/             /fogszab.../   │
       (split-hero, narancs)    │  body.theme-fox         body.theme-ortho│
                                │  ─────────────          ─────────────  │
                                │  Mint zöld paletta      Barna/narancs  │
                                │  Modern dental clinic   Orthodontic    │
                                │  Fogászati Centrum      Foxxi spec.    │
                                │  Felnőtt + gyermek      Invisalign     │
                                └────────────────────────────────────────┘
```

A két szekció ugyanazon a WP install-en, közös:

- 7 nav menü struktura (csak a `primary-menu` cserélődik `fox-menu`-re)
- Header + Footer Theme Builder template (közös HTML, eltérő színek)
- 19 Foxxi Elementor widget (slider, about, services, testimonials, feature, repeater, contact, cta, normal_content, blockquote, list_services, team, gallery_carousel, four_reasons, accordions, steps, before_after_gallery, video_carousel, header, footer, page_hero)

## Color Palette — Foxxi Warm (theme-ortho, fogszab)

Az **eredeti** Foxxi brand 7-color paletta (lásd `docs/foxxi_szinek.txt`):

| Token | Hex | Használat |
|---|---|---|
| `--foxxi-brown` | `#42291c` | Fő barna — felirat, footer, sötét sect. |
| `--foxxi-cypress` | `#f6ac6e` | Róka #1 — világos accent |
| `--foxxi-maple` | `#e37f56` | Róka #2 — közepes accent |
| `--foxxi-orange` | `#d75c20` | Róka #3 — fő narancs (CTA) |
| `--foxxi-cherry` | `#c97849` | Róka #4 — meleg pasztell |
| `--foxxi-oak` | `#9b413a` | Róka #5 — sötét meleg |
| `--foxxi-eucalyptus` | `#703e2a` | Róka #6 — eucalyptus barna |
| `--foxxi-cream` | `#faf3eb` | Sand cream — sect. background |
| `--foxxi-sand` | `#fff5ec` | Lighter sand |

## Color Palette — Foxxi Dental Mint (theme-fox, fogászat)

**Új paletta 2026-04-30** — a user explicit kérése (a kék/zöld korábbi tilalom felülírva), hogy a fogászati részleg vizuálisan más legyen:

| Token | Hex | Használat |
|---|---|---|
| `--fox-mint-50` | `#f3faf7` | Very light — testimonials bg, header bg |
| `--fox-mint-100` | `#dff1ea` | Light mint — section bg (about, services, repeater) |
| `--fox-mint-200` | `#c5e8de` | Mid-light — hover state |
| `--fox-mint-300` | `#a3d9ca` | Light teal — soft accent |
| `--fox-mint-400` | `#7dc8b0` | Mid teal — links |
| `--fox-mint-500` | `#5fbfa3` | Primary teal — buttons |
| `--fox-mint-600` | `#48a999` | Mid-dark teal — button hover, CTA bg |
| `--fox-mint-700` | `#2c8378` | Dark teal — headings, dark text, cross-link |
| `--fox-mint-800` | `#1f6e62` | Eucalyptus green — footer bg, dark sections |
| `--fox-mint-900` | `#154e46` | Deepest green — accents, footer subMenu |

### Semantic mapping

```css
body.theme-fox {
  --brand-primary:    var(--fox-mint-500);
  --brand-primary-dk: var(--fox-mint-700);
  --brand-accent:     var(--fox-mint-400);
  --brand-light:      var(--fox-mint-100);
  --brand-deep:       var(--fox-mint-800);
}
```

## Typography (közös mindkét szekciónak)

| Token | Font |
|---|---|
| `--display` (heading) | "TeX Gyre Adventor Bold", Helvetica Neue, sans-serif |
| `--sans` (body) | "Nunito Sans 10pt Regular", Nunito Sans, system-ui |

A foxy theme alapból betölti ezeket. NE adj hozzá Google Fonts import-ot.

## Layout konvenciók

### Page-level

Minden Elementor oldal (kivéve `/`-Választó) a `elementor_header_footer` page-template-en renderel:

```
┌─ Theme Builder Header (foxxi-header widget) ─────┐
├─ Page Hero (foxxi-page-hero widget) ─────────────┤
├─ Blockquote.top (foxxi-blockquote, pink color) ──┤  ← első tartalom-szekció
├─ Section #2 (about, services, repeater, ...) ────┤
├─ ... további szekciók ...                        │
├─ Cross-link banner (fox_render_cross_link) ──────┤  ← auto append
├─ Theme Builder Footer (foxxi-footer widget) ─────┤
```

### Section-level

Minden Foxxi widget egy 1-column Elementor section-ben (`content_width: full_width`, `padding: 0`, `gap: no`) — a foxy partial-ok teljes-szélesség background-okat vártak.

CSS bridge a `:has(.elementor-widget-foxxi-...)` szelektorral kényszeríti minden Elementor section-t full-width-re ahol Foxxi widget van.

### Két oldal fő különbség (theme-fox)

| Elem | theme-ortho (fogszab) | theme-fox (fogászat) |
|---|---|---|
| Section bg (about, services) | `#fcefe7` (light pink) | `#dff1ea` (light mint) |
| Footer bg | `#42291c` (sötét barna) | `#1f6e62` (eucalyptus) |
| Footer subMenu bg | (default sötétebb) | `#154e46` (deepest green) |
| CTA button bg | `#d75c20` (narancs) | `#48a999` (mid teal) |
| Cross-link bg | `#703e2a` (eucalyptus) | `#2c8378` (dark teal) |
| Hero caption SVG | narancs (eredeti) | hue-rotate(120deg) → zöld |
| Blockquote ötszög SVG | narancs (eredeti) | hue-rotate(120deg) → zöld |
| Header (Theme Builder) | fehér + barna nav | mint-50 + teal nav |

## File-térkép

| Cél | Fájl |
|---|---|
| Brand variables | `theme-foxy/assets/css/foxxi-brand.css` |
| Theme overrides + theme-fox/ortho | `theme-foxy/assets/css/split-hero.css` |
| Foxxi widget kód | `theme-foxy/elementor-widgets/widget-*.php` |
| Render funkciók (V2 paritás) | `theme-foxy/static-sections/render.php` |
| Theme Builder template generator | `scripts/phase4-create-theme-builder.php` |
| Page-hero adder | `scripts/phase5c-add-page-heroes.php` |
| Generic page migrator | `scripts/phase2-migrate-page.php` |

## Új szekció hozzáadásának checklist-je

1. **Render funkció** a `static-sections/render.php`-ben: `fox_static_render_<layout>($d)` — DOM = foxy theme partial 1:1
2. **Widget** a `elementor-widgets/widget-<layout>.php`-ben: `Foxxi_<Layout>_Widget extends Foxxi_Base_Widget`
3. **Loader.php**: új név hozzáadása a foreach listához
4. **Base widget func_map** bővítése: `'<layout>' => 'fox_static_render_<layout>'`
5. **CSS bridge** a `split-hero.css`-ben: `.elementor-widget-foxxi-<layout> > .elementor-widget-container { padding: 0 }`
6. **Generic migrator** case ág a `scripts/phase2-migrate-page.php`-ben (ACF-fields mapolás)
7. **theme-fox CSS overrides** ha színváltozat kell (`body.theme-fox .<layout-class>`)

## Tipikus hibajavítási sorrend

Új layout/widget bevezetésekor:

1. **HTML rendben?** — `curl` + grep, ellenőrizd hogy a render funkció a megfelelő DOM-ot adja vissza
2. **CSS érvényesül?** — Playwright `getComputedStyle` vagy DevTools, hogy a body.theme-fox felülírások működnek-e
3. **JS init?** — ha slider/carousel, az enqueued script-ek frontend-ben futnak-e (`fox_ensure_twentytwenty_assets()` mintát használj)
4. **Visual verify** — Playwright screenshot 1440×900 viewport-on
5. **Backup verify** — minden migrate után `_elementor_data_backup_<ts>` post meta + `/tmp/foxxi-id<X>-backup-<ts>.json`

## Continuity / "Honnan folytasd"

Ha új session indul ezen a projekten:

1. Olvasd el [[02-Projects/foxxi]] — fázis-státusz tábla
2. Olvasd el [[11-wiki/wp-acf-flexible-to-elementor-migration]] — teljes módszertan
3. Olvasd el ezt a fájlt — design-system reference
4. SSH staging: `ssh hostinger; cd ~/domains/violet-okapi-488175.hostingersite.com/public_html`
5. Local repo: `/root/projektjeim/foxxi/`
6. Deploy after CSS/PHP edit: `cd /root/projektjeim/foxxi && ./scripts/deploy-theme.sh --push`
7. Cache flush: `wp cache flush && wp w3-total-cache flush all`
8. Visual verify: `https://violet-okapi-488175.hostingersite.com/<slug>/?nocache=N`

## License & roadmap

A playbook + design system **public github repo alapanyag** lesz: `acf-to-elementor-migration` (MIT), a Foxxi-specifikus konfiguráció kiszedve. Alkalmazható minden meglévő ACF Flexible Content WordPress site-ra.
