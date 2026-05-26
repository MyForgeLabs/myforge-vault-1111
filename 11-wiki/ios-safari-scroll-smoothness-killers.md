---
name: ios-safari-scroll-smoothness-killers
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#frontend", "#mobile", "#performance"]
---

# iOS Safari scroll-smoothness — 5 fő killer

Mobil-app érzéshez (különösen iOS Safari + iPhone-on) **mind az 5-öt** ellenőrizni kell. Egyetlen is észrevehető jankot okoz.

## 1. `background-attachment: fixed`

**Tünet:** scroll-on minden frame-en újra-rajzolja a viewport-méretű background-réteget. Több réteg (`fixed, fixed, fixed`) → kumulatív repaint.

**Detect:** `getComputedStyle(document.body).backgroundAttachment`

**Fix:** mobile-on `scroll` (vagy egyáltalán semmi), desktop-on lehet `fixed`:
```css
body { background-attachment: scroll; }
@media (min-width: 768px) { body { background-attachment: fixed; } }
```

## 2. Viewport-méretű SVG / data-URL background pattern

**Tünet:** noise-texture, paper-texture, grit-overlay — minden scroll-frame-en újra-blitt-olódik.

**Fix:** csak desktop-on bekapcsolni, mobile-on egyszerű radial-gradient marad (vagy semmi):
```css
body {
  background-image: radial-gradient(...), radial-gradient(...); /* no SVG */
}
@media (min-width: 768px) {
  body { background-image: ...radials..., url("data:image/svg+xml;..."); }
}
```

## 3. N×kártya `::after` overlay

**Tünet:** 50+ kártya, mindegyiken egy `::after` repeating-linear-gradient scan-line texture. Layout/paint-tree-ben mind benne van.

**Detect:** `document.querySelectorAll('.bm-grit').length` — ha >20, gond.

**Fix:** desktop-only media-queryben:
```css
.bm-grit { position: relative; }
@media (min-width: 768px) {
  .bm-grit::after { content: ""; ... }
}
```

## 4. Hiányzó tap-polish

Az iOS Safari default-tap-flash (kék overlay), double-tap-zoom és long-press-callout érezhető lag-okat okoz.

**Fix globálisan:**
```css
html {
  -webkit-text-size-adjust: 100%;
  -webkit-tap-highlight-color: transparent;
}
button, a, [role="button"] {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  touch-action: manipulation;
}
```

`-webkit-text-size-adjust: 100%` az iOS landscape-ben az auto-zoom-ot tiltja (pl. inputra koppintáskor).

## 5. Fix-px font-size statikus értékek

**Tünet:** 64px headline 4 sorba tördelődik 375px viewporton, vagy 112px score 2× overflow-ol.

**Fix:** `clamp(min, vw, max)` minden nagy fontnál:
```tsx
fontSize: "clamp(40px, 12vw, 64px)"    // landing headline
fontSize: "clamp(72px, 22vw, 112px)"   // match stadium score
fontSize: "clamp(40px, 13vw, 56px)"    // Glicko rating tile
fontSize: "clamp(30px, 9vw, 38px)"     // page sub-headline
fontSize: "clamp(34px, 10vw, 44px)"    // login/onboarding headline
```

## Bonus: `overscroll-behavior: contain`

Belső scrollable container-en (pl. lista) megakadályozza, hogy a rubber-band scroll a parent-re továbbterjedjen. iOS Safari-on különösen érezhető.

```css
.bm-grit { overscroll-behavior: contain; -webkit-overflow-scrolling: touch; }
```

## Audit script

```js
// Run in Chrome DevTools console (mobile-emulation mode)
() => ({
  bgAttachment: getComputedStyle(document.body).backgroundAttachment,
  hasSvgNoise: getComputedStyle(document.body).backgroundImage.includes('svg'),
  gritCount: document.querySelectorAll('.bm-grit').length,
  largeFonts: Array.from(document.querySelectorAll('h1,h2,h3,.display')).filter(el => {
    const fs = parseFloat(getComputedStyle(el).fontSize);
    return fs >= 40 && !el.style.fontSize.includes('clamp');
  }).map(el => ({ tag: el.tagName, fs: getComputedStyle(el).fontSize })),
});
```

## Reference

- Client-C-app 2026-05-19 audit: [[../08-Sessions/2026-05-19-client-c-app-phase-2]]
- Chrome DevTools + Lighthouse mobile-emulation MCP-vel
