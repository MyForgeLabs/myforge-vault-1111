---
name: AI prompt fidelity locks (image compositing tasks)
type: wiki
created: 2026-05-04
updated: 2026-05-04
tags: ["#type/wiki", "#topic/ai", "#topic/prompts", "#topic/image-generation"]
---

# AI prompt fidelity locks — image compositing tasks

> Általánosítható szabály-csomag amikor egy AI image-generátor nem szabad hogy a referencia-elemeket "újrarajzolja". Eredeti kontextus: KGC Instagram carousel (PRODUCT FIDELITY LOCK — Jansen RD-300 incidens, 2026-05-04). Általánosítható minden olyan task-ra ahol egy referencia-asset (termékfotó, logó, karakter) **pixel-identikusan** kell megőrizni az output-ban.

## A probléma

Az AI image-generátorok (Nano Banana / Gemini Image / DALL-E / Midjourney / ChatGPT image) hajlamosak a referencia-képet "értelmezni" és újrarajzolni, NEM masking-elni vagy compositing-elni. Még explicit "FAITHFULLY", "PHOTOREALISTICALLY" szavak ellenére is: a modell szabadon variál.

## A 4 fidelity lock pattern

### 🔒 BLOCK A — PRODUCT/ASSET FIDELITY LOCK

A referencia-kép (termékfotó, asset) NEM rajzolódik újra. Helyette: position, scale, crop, rotation, drop-shadow változhat. Photoshop-LAYER-3 metafora.

```
═══════════════════════════════════════════════════════════
🔒 PRODUCT FIDELITY LOCK — KRITIKUS!
This is an IMAGE COMPOSITING task, NOT image generation.

The product from IMAGE 1 is a FIXED ASSET — paste, don't redraw.
LAYER 3 (the product) is FROZEN.

ALLOWED: Position, Scale, Crop, small Rotation, subtle Drop-shadow.
FORBIDDEN: Redrawing pixels, color shift, angle change, adding/removing parts, restyling.

Imagine Photoshop:
- LAYER 1 (bottom): the background you generate
- LAYER 2 (middle): design elements you generate
- LAYER 3 (TOP, UNTOUCHED): IMAGE 1 — the product as cutout

If the output product differs from IMAGE 1 in ANY way, FAILED.
═══════════════════════════════════════════════════════════
```

### 🔒 BLOCK B — LOGO FIDELITY LOCK (transzparens háttér)

A logót se írja át, és NE tegyen háttér-dobozt mögé.

```
═══════════════════════════════════════════════════════════
🔒 LOGO FIDELITY LOCK — KRITIKUS!
The logo from IMAGE 2 is a FIXED ASSET — paste, don't redraw.

ALLOWED: Position, Scale, subtle drop-shadow.
FORBIDDEN: Redrawing letters, changing typography, changing colors, adding ANY background box/plate/rectangle behind it, restyling.

TRANSPARENT BACKGROUND: the logo sits DIRECTLY on the page background — NO white box, NO colored box, NO frame, NO outline.

If output logo differs from IMAGE 2, FAILED.
═══════════════════════════════════════════════════════════
```

### 🎨 BLOCK C — COLOR/DECAL LOCK (color-agnostic verzió)

⭐ **Default ajánlott** — a SHAPE/STRUCTURE-leírást elválasztja a SZÍN/STICKER/BRAND-leírástól. A szín csak a referencia-képből származhat:

```
CRITICAL COLOR + DECAL RULE: The product takes its EXACT colors, decals, stickers, model numbers, brand labels, and text from IMAGE 1 ONLY. Do NOT describe colors based on "typical brand colors" or assume from memory. If IMAGE 1 shows red, output is red. If IMAGE 1 shows green, output is green. Sticker text appears identically. Brand logos appear identically.
```

**Tanulság (Jansen RD-300 incidens, 2026-05-04):** ha a prompton "BRIGHT JANSEN RED" volt, a generátor a "tipikus Jansen-szín" alapján rajzolt — a tényleges referencia-fotó színeitől eltérő eredmény. A javítás: a SHAPE-leírás (lánctalp, hidraulikus billentés, handlebars, méret) szöveggel megengedett, a SZÍN CSAK az IMAGE-ből.

### 🎨 BLOCK D — STYLE MIX RULE

Két különböző stílus (pl. photoreal termék + Pixar karakter) coexistál ugyanazon a slide-on, anélkül hogy egymást befolyásolnák.

```
CRITICAL STYLE RULE — STYLE MIX:
The product (IMAGE 1) is PHOTOREALISTIC product-photo style.
The character in the corner (Felix/Flexi/Lexia) is PIXAR 3D style.
These two styles must coexist on the same slide WITHOUT one influencing the other.
The product stays a real photo crop. The character stays a Pixar render. They are visually layered, not blended.
```

## Ha a generátor MÉG akkor is variálja: 2-lépéses Photopea workflow

Néhány modell (Midjourney, néha Nano Banana) **nem támogat valódi compose** módot — mindig újrarajzol. Ekkor:

**Lépés 1** — háttér + design + karakter generálása ÜRES termék-zónával:
```
🎨 STAGE 1 OF 2: BACKGROUND + DESIGN ONLY

In this generation, DO NOT include the product at all.
Instead, on the LEFT 35-40% of the canvas, leave a clean EMPTY ZONE — a soft grey rectangular placeholder (#3A3A3A, 5% opacity) with subtle "PRODUCT PLACEHOLDER — DO NOT FILL" guideline text in the corner.

Generate everything else as specified. The product zone stays empty — it will be composited in Stage 2 in Photoshop / Photopea / Canva.
```

**Lépés 2** — TÉNYLEGES termékfotó kézzel (Photopea / Canva / Photoshop):
- A `termék.png` (háttér nélküli verzió, remove.bg vagy photoroom.com-mal előzetesen)
- Új layer fent, position-elj a placeholder-zónába
- Subtle drop-shadow alá (10-15% black, 20px blur, 5px offset Y)
- Export

→ Garantált pixel-pontos termék.

## Mikor melyik blokk?

| Helyzet | A | B | C | D |
|---|---|---|---|---|
| Termékfotó-compositing (pl. Instagram carousel) | ✓ | ✓ | ✓ default C2 | ha karakter is van |
| Termékfotó pontos színnel (jól ismert brand) | ✓ | — | C1 erős | — |
| Karakter + termék egy slide | ✓ | — | ✓ | ✓ kötelező |
| Logo + sok minden | — | ✓ | — | — |
| Hero scene karakterekkel + showroom | — | — | C2 | — |

**Default csomag bármely image-compositing task-ra:** A + B + C2 + D (ha karakter is van).

## Implementációs példák a vault-ban

- [[02-Projects/kgc-berles]] — Instagram carousel prompt-tár (`docs/instagram-carousel-promptok/`):
  - README.md — a 4 BLOCK formal definíciói
  - _template.md — fill-in-the-blank új termékhez
  - 01-ariens, 02-grillo, 03-jansen, 04-weibang — konkrét promptok 4 termékhez × 3-3 slide

## Kapcsolódó

- [[07-Decisions/2026-05-04 Multi-category rendszer + új árazási szabályok v2]] — kontextus
- [[02-Projects/kgc-berles]] — Instagram carousel prompt-tár forrása
<!-- auto-enriched 2026-05-18: +3 semantic cross-link via vault-search -->
- [[destructive-action-hard-confirm-ux]] (sem-rokon, score=0.54)
- [[sv-05-crystallization-automation]] (sem-rokon, score=0.52)
- [[sv-02-recursive-self-improvement]] (sem-rokon, score=0.52)
