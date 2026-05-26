---
name: svg-img-overlay-aspect-ratio
description: img + SVG overlay különböző aspect-ratio-n szétcsúszik max-h + overflow-auto-val. Fix - aspectRatio CSS-szel az inner wrapper-re, preserveAspectRatio=none az SVG-re.
type: wiki
created: 2026-05-12
tags: ["#tech/react", "#type/reference", "#project/superintelligent-vault"]
tag_backfill: 2026-05-19
updated: 2026-05-19
---
# SVG-overlay az `<img>` fölött — aspect-ratio CSS layout bug

## A tanulság

Ha SVG-vel overlay-zünk egy `<img>`-et (pl. callout-marker-ek), és a wrapper-container `max-h` + `overflow-auto` kombinációval van korlátozva, **az img és SVG különböző méretben renderelődnek**, és a koordináta-rendszerek szétcsúsznak.

**A felhasználói tünet:** "a piros gyűrű nem a számon van", "a klikk rossz helyre megy". Pedig az OCR-koordináták pontosak.

## Why

Tipikus rossz code:
```tsx
<div className="max-h-[80vh] overflow-auto inline-block">
  <img src={...} className="max-w-full" />
  <svg
    viewBox="0 0 3308 4678"
    preserveAspectRatio="xMidYMid meet"
    className="absolute inset-0 h-full w-full"
  />
</div>
```

Probléma:
1. **`<img>`** keeps natural aspect (3308:4678), scrolls when taller than `max-h`
2. **`<svg>`** sizes itself to the CLAMPED container (e.g., 600×640 instead of 600×848), with viewBox 3308×4678
3. **Different aspect ratios** → `preserveAspectRatio="meet"` adds horizontal padding to center the SVG content
4. **Coordinate mismatch:** egy bbox `(231, 736)` a kép-pixel-térben az SVG fölött eltolódik

## How to apply (fix pattern)

```tsx
{/* Outer = scrollable viewport */}
<div className="max-h-[calc(100vh-160px)] overflow-auto">
  {/* Inner = exact img-aspect dimensions */}
  <div
    className="relative"
    style={{ aspectRatio: `${imgWidth} / ${imgHeight}` }}
  >
    <img
      src={imageUrl}
      className="block h-full w-full"
    />
    <svg
      viewBox={`0 0 ${imgWidth} ${imgHeight}`}
      preserveAspectRatio="none"
      className="absolute inset-0 h-full w-full"
    >
      {/* rect-ek kép-pixel koordinátákban — most már pontosan rajta */}
    </svg>
  </div>
</div>
```

**Why ez működik:**
1. Inner `<div>` `aspectRatio: w/h` CSS-szel mindig ugyanaz az aspect ratio mint a kép
2. `<img>` `h-full w-full` kitölti az inner-t
3. `<svg>` `absolute inset-0 h-full w-full` ugyanazok a dimenziók mint az inner
4. `preserveAspectRatio="none"` — mivel a wrapper aspect = viewBox aspect, nincs distortion (a none csak akkor torzít ha különböznek)

## Bidirectional click bug társa

Plus: az SVG-rect `fill="transparent"` defaulton **NEM klikkelhető** (csak a 2px-es stroke fogad eseményt). Megoldás:
```tsx
<rect
  x={...} y={...} width={...} height={...}
  fill="white"
  fillOpacity={0.001}  // láthatatlan de full-area clickable
  onClick={...}
/>
```

`fillOpacity=0.001` invisible visuálisan de pointer-events-elfogadja a click-et az egész területen. Plus `pointer-events="all"` is explicit alternatíva.

## Implementáció

- [[02-Projects/robbantott-kereso]] `frontend/src/components/FigureViewer.tsx` line 100+ (commit `bd8b260`)

## Mikor érzed magad rajta

- "A klikk csak a vékony border-en regisztrálódik" → fillOpacity-fix
- "A piros gyűrű mellette van a számtól" → aspect-ratio container fix
- "Mobil-en máshol van mint desktop-on" → CSS responsive max-h interakció — aspect-container megoldja

## Kapcsolódó

- [[02-Projects/robbantott-kereso]] — implementáció (15+ commit, ebből `bd8b260` a layout-bug fix)
