---
name: Elementor repeater MEDIA control + condition gotcha
description: Ha programmatically állítasz be image-et egy condition-bound MEDIA control-on, a type/feltétel-mezőt is be kell állítani — különben a render skip-eli
type: wiki
created: 2026-04-30
updated: 2026-05-09
tags: ["#tech/elementor", "#tech/wordpress", "#wiki/playbook"]
---

# Elementor repeater MEDIA control + `condition` gotcha

## A probléma

Custom Elementor widget-ben gyakori minta: van egy `type` SELECT control (`image`/`text`/`before` stb.), és egy `image` MEDIA control aminél a megjelenés feltétel-bound:

```php
$rep->add_control('type', [
    'type' => Controls_Manager::SELECT,
    'options' => ['image' => '...', 'text' => '...'],
    'default' => 'image',
]);
$rep->add_control('image', [
    'type' => Controls_Manager::MEDIA,
    'condition' => ['type' => 'image'],   // ← ez a gotcha
]);
```

Az Elementor a settings-be **bármikor mentheti** az image-értéket (pl. ha a user először type=image-et választott, képet feltöltött, majd type=text-re váltott — az image marad a DB-ben). DE a `get_settings_for_display()` és a render flow **NEM adja vissza** azokat a control-értékeket, amelyek `condition`-je nem teljesül a runtime-on.

Programmatikusan szintén: ha `wp post meta update`-tel beállítasz egy item-re `image: {id: X, url: Y}`-t de a `type` `text`-en marad, **a render üres imageBox-ot ad ki** mert a condition nem teljesül.

## A tünet

Egy foxxi-repeater item-en `image_id=2290` szerepel a DB-ben, de a frontend HTML üres `<div class="imageBox"></div>`-t renderel. Más item-en (ahol `type=image`) ugyanezzel az image_id-vel működne.

## A megoldás

**Programmatic data-update során mindig állítsd be a condition-mezőt is** ami feltétele a render-nek:

```php
$item['type']  = 'image';   // ← condition match!
$item['image'] = ['id' => $img_id, 'url' => wp_get_attachment_url($img_id)];
```

## Hol találkoztunk vele

[[02-Projects/foxxi]] Phase 6 + Phase 7:

- `/fogaszat/` "Miért a Foxxi Fogászati Centrum?" foxxi-repeater 4 elem közül 3-nak `type=text` volt → image üresen maradt
- `/araink-fogaszat/` "Fizetés és garancia" 3 elem ugyanígy
- `/szajhigienia-fogfeheries/` "Ragyogó mosoly" 2 fogfehérítési mód

Mindegyik esetben a `type='image'`-re javítás + image set kellett.

## Hogyan ellenőrizd

A widget `register_controls()` PHP-jét nézd meg minden `condition` kulcs után — a feltétel-mezőt mindig állítsd be a programmatic update során. Ha condition `['type' => ['image', 'video']]` array, az item `type`-ja legyen az egyik érték.

## Kapcsolódó

- [[02-Projects/foxxi]] — itt élesben szembesültünk vele
- Elementor docs: https://developers.elementor.com/docs/widgets/widget-controls/ (MEDIA control + conditional display)
<!-- auto-enriched 2026-05-18: +3 semantic cross-link via vault-search -->
- [[wp-elementor-template-conflicts]] (sem-rokon, score=0.58)
- [[wp-acf-flexible-to-elementor-migration]] (sem-rokon, score=0.54)
- [[gemini-3-1-flash-tts-pipeline]] (sem-rokon, score=0.53)
