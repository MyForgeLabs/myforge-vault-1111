---
name: Chromium img-svg parent-fill cascade bug
description: Chromium az `<img src="*.svg">` mode-ban néha figyelmen kívül hagyja a child path-ok saját `fill="..."` attributumait, ha a parent `<g>` style-jában van fill-cascade. Cairo helyesen renderel ugyanazt a fájlt. Workaround: PNG-vé renderelni cairosvg-vel.
type: wiki
tags: ["#wiki", "#tech/svg", "#tech/browser-bug"]
created: 2026-05-10
updated: 2026-05-10
---

# Chromium `<img src="*.svg">` parent-fill cascade bug

## Tünet

Adott egy SVG fájl ahol a `<g id="g34">` parent-csoport NINCS saját fill-attributuma, és a gyermek `<path>` elemek mindegyikén explicit `fill="#color"` attribute van (különböző színekkel a multi-coloured grafikához). A SVG ugyanabban a `<g>`-ben tartalmaz `<g aria-label="..." style="...fill:#ffffff">` text-csoportokat is.

- **Cairo render** (cairosvg, librsvg) → szerveroldali PNG-render: helyesen, multi-color path-ok megjelennek
- **Chromium render** (`<img src="...svg">` HTML-ben): **child path fill-attributumokat ignorálja**, helyettük a parent text-csoport fehér fill-jét örökölteti → multi-color grafika fehéren renderel

Md5-egyezés: a fájl-tartalom IDENTIKUS — a bug Chromium SVG-rendererében van, NEM a fájlban.

## Reprodukció (példa)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 332 52">
  <g id="g34">
    <!-- Multi-color fox graphic with per-path fills -->
    <path d="..." fill="#c97749" id="path2" />
    <path d="..." fill="#9b413a" id="path4" />
    <path d="..." fill="#d75c21" id="path8" />
    ...
    <!-- White text letters with per-path fills -->
    <path d="..." fill="#ffffff" id="path20" />
    <path d="..." fill="#ffffff" id="path22" />
    ...
    <!-- White-text group with style-fill cascade -->
    <g aria-label="TAGLINE" id="text30" style="fill:#ffffff">
      <path d="..." id="path45" />  <!-- inherits white -->
      <path d="..." id="path47" />
    </g>
  </g>
</svg>
```

A `<img src="logo.svg">` Chromium-ban: a `path2`, `path4`, `path8` (multi-color fox) is fehéren renderel, NEM a saját fill-attributumokon.

## Verifikáció

1. `<svg fill="none">` outer-attribute eltávolítása NEM segít.
2. Md5-check a serverről letöltött SVG-vel: azonos a deployolt fájllal.
3. `getComputedStyle()` az `<img>` elemen: `filter`, `opacity`, `mixBlendMode` mind alapértelmezett — semmi CSS shenanigans.
4. A SVG-fájlt közvetlenül browser-URL-ben megnyitva (NEM `<img>`-ben): renderelés szintén hibás (ugyanaz a Chromium SVG-pipeline).
5. A SVG-t inline `<svg>...</svg>` HTML-ben (DOM-szinten): valószínűleg helyesen renderel — a bug az `<img>` raster-mode-on van.

## Workaround

**PNG-vé renderelni cairosvg-vel** szerveroldalon, és a PNG-t deployolni:

```python
import cairosvg, io
from PIL import Image

out = io.BytesIO()
cairosvg.svg2png(url='logo.svg', output_height=200, write_to=out)
img = Image.open(io.BytesIO(out.getvalue())).convert('RGBA')
img.save('logo.png', optimize=True)
```

A `output_height=200` retina-ready (2× a tipikus 100px header-magassághoz). PNG ugyanaz minden böngészőben — Cairo-renderelt → predictable.

## Mikor ne használd a workaround-ot

- Ha az SVG **mono-coloured** (egyetlen `fill` cascade) — ott a bug nem manifestálódik
- Ha az SVG **inline DOM-ban** van (`<svg>...</svg>` közvetlenül a HTML-ben) — DOM-szintű rendering OK
- Ha SVG sprite (`<use href="#icon">`) — más renderpath
- Ha CSS `mask: url(...svg)` — egyébként renderel

## Ahol ezt felfedezve

Foxxi-projekt ([[02-Projects/foxxi]]) Phase 13 (2026-05-10): Marcsi-féle `magyaroldal_logo.svg` (color fox + fehér FOXXI text + fehér tagline) Chromium-ban fehér rókát renderelt a Választó hero-n. Cairo-render preview ugyanezt a fájlt SZÍNES rókával mutatta. Workaround: cairosvg → `logo-choice.png` (1278×200, 35 KB).

## Kapcsolódó

- [[11-wiki/wp-elementor-template-conflicts]] — más WP+Elementor render-bug-ok
- Chromium upstream issue (TBD): a bug pontos triggerét érdemes minimal-reproducer-rel kiizolálni és bejelenteni

## Megjegyzés

A jelenség Chromium-specifikus. Firefox és Safari render-engine-jeit nem ellenőriztük 2026-05-10 állapotában — érdemes lenne tesztelni hogy a bug univerzális-e a böngészők között.
