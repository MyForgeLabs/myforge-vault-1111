---
name: SVG asset-source decision (kódolt vs vectorized vs Stock)
type: wiki
created: 2026-05-09
updated: 2026-05-09
agent: claude
tags: ["#topic/svg", "#topic/design-asset", "#topic/workflow", "#decision"]
---

# SVG asset-source decision — kódolt vs vectorized vs Stock

> Mikor melyik vector-asset-source érdemes web-design-ra? 3 opció (kódolt SVG, Adobe-vectorize raszter→SVG, Adobe Stock free-tier vector), 3 erősség és 3 trade-off. Praktikus döntési-fa.

## Az opciók

### 1. Kódolt SVG (kézzel írt `<line>`/`<path>`/`<text>` Google Fonts-szal)

**Példa:**
```svg
<svg viewBox="0 0 400 400">
  <defs><style>@import url('https://fonts.googleapis.com/css2?family=Playfair+Display');</style></defs>
  <g stroke="#c8a154" fill="none">
    <!-- 13 sunburst rays via transform="rotate" -->
  </g>
  <text font-family="Playfair Display" fill="#c8a154">RB</text>
</svg>
```

**Erősségek:**
- ✅ **Transparent-bg natívan** — semmi háttér-pixelt nem ad
- ✅ **Apró fájlméret** (1-3KB tipikusan)
- ✅ **Skálázható végtelen** (font-vector)
- ✅ **Paletta-token-cserélhető** (CSS-variable hivatkozások)
- ✅ **Web-célra ideális** — gyors load, accessibility

**Trade-offok:**
- ❌ **Csak akkor szép, ha vékony-vonalas/szöveg-alapú** — komplexebb illustration-okat (fotorealisztikus tárgy, struktúra) nehéz előállítani
- ❌ **Font-dependency** — Google Fonts-betöltés kell, vagy text-to-path konverzió Inkscape-pel
- ❌ **NEM AAA-quality print-ra** — nyomdai/foil-stamp célra a font-render eltérhet

**Mikor használd:** Logo, monogram, ikon, hairline-decoration, geometriai motívumok, web-hero-decoration.

### 2. Adobe Illustrator `image_vectorize` MCP (raszter PNG→SVG path-trace)

**Tool:** `mcp__claude_ai_Adobe_for_creativity__image_vectorize`

**Erősségek:**
- ✅ **Pixel-perfect path-only** — minden raszter-render-detail vektor-pathokká alakítva
- ✅ **Print-ready** (nyomdai, foil-stamp, packaging)
- ✅ **Font-mentes** (text-to-path automatikusan)
- ✅ **Zoom-rezisztens** (vector)

**Trade-offok:**
- ❌ **NEM transparent-friendly** — a teljes canvas-háttér is path-fa lesz (~250+ dark-pixel-path), és bg-rect törlés után is láthatóan opaque
- ❌ **Nagy fájlméret** (900KB-1.5MB)
- ❌ **Recolor nehéz** — sok különböző hex-szín, hue-shift csak a tisztán-szín-tartományt módosítja
- ❌ **Csak ha van forrás-PNG** (higgins-render vagy Stock-PNG)

**Mikor használd:** Master print-asset (CMYK PDF, foil-stamp), brand-guideline-master, packaging-print, NEM transparent-bg-web-icon.

### 3. Adobe Stock free-tier vector-illustration

**Tool:** `mcp__claude_ai_Adobe_for_creativity__asset_search` + `asset_license_and_download_stock`

**Erősségek:**
- ✅ **Profi illustration-design ingyen** (free-tier license)
- ✅ **Bonyolult tárgyak** (függöny, stage, drape, lambrequin) készen kapható
- ✅ **Vector .ai/.svg formátum** (skálázható)

**Trade-offok:**
- ❌ **NEM AAA-quality web-hero-ra** — a stock-illustration eredetileg specifikus paletta-hangsúlyokkal és gradient-ekkel készült (pl. piros bársony arany highlight-okkal), amit recolor (hue-shift) után a fény-részek átszövik az új paletta-base-t (pl. smaragd-nál a gold/narancs highlight-ok piros-vonzlatot adnak)
- ❌ **Generic-look** — nem brand-specific
- ❌ **Recolor-Python-szkript komplex** (15+ unique hex-szín)

**Mikor használd:** Print-collateral (poster, flyer), magyarázó-illustration (about-page-en kis ikon), NEM signature-hero-asset.

## Döntési-fa

```
Web-icon/logo TRANSPARENT-bg-vel?
├─ IGEN → kódolt SVG (1.)
└─ NEM (print/foil-stamp/CMYK)?
   ├─ IGEN → Adobe-vectorize (2.) higgins-render-ből
   └─ NEM (kis decoration / about-page-illustration)?
      └─ Adobe Stock free-tier (3.) — de NEM signature-asset
```

## Forrás-tanulság

Rojt és Bojt session 2026-05-08 — 4 logo-iteráció:
1. Kódolt CSS-sketch (5 sub-monogram preview HTML) — gyors, de stílus-csak vázlat
2. Higgins-render PNG (4 db) — lágyabb Cassandre + tassel-rojt motívum
3. Adobe-vectorize-ed SVG (4 variant) — pixel-perfect, DE transparent-issue
4. **Kódolt clean SVG (3KB) ← végleges döntés** — sunburst + RB + ROJT ÉS BOJT + tagline pure `<line>`+`<path>`+`<text>`

Plus 2 curtain-iteráció elvetve: CSS-only stage-curtain + Adobe Stock free-tier függöny-recolored. Mindkettő „csúnya".

**Tanulság:** Ha **transparent-bg + skálázható + brand-konzisztens + web-célú** → kódolt SVG GYŐZ minden más fölött. Adobe-vectorize csak akkor, ha print-master cél.

## Kapcsolódó

- [[wp-cli-bricks-postmeta-pattern]] — hogyan injektáld az SVG-t Bricks-tartalomba
- [[reference_nano_banana_image_gen]] — higgins/nano_banana_2 image-render workflow
- [[hellopack-wordpress-plugin-suite]] — Bricks-ecosystem
