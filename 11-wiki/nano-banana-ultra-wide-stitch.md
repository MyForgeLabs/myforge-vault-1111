---
name: nano-banana-ultra-wide-stitch
type: wiki
created: 2026-05-13
updated: 2026-05-13
tags: ["#topic/nano-banana", "#topic/image-generation", "#topic/workflow"]
---

# nano-banana ultra-wide stitching workaround

## Probléma

`nano-banana` (Gemini 3.1 Flash/Pro Image) **max aspect ratio = 21:9 (~2.36:1)**. Ennél szélesebb output (pl. autó-matrica 5.25:1, ultra-wide billboard 6:1) nem támogatott a CLI-ben — a `-a` flag csak a következő ratio-kat fogadja: `1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 4:5, 5:4, 21:9`.

Két naiv megoldás **NEM működik**:

1. **Generálj 21:9-en + pad cream-mel oldalt** → design szabadon "lebeg" üres szegélyek között, user-feedback: *"az egészen kellene elterülnie"*
2. **Generálj 21:9-en + horizontal stretch 5.25:1-re** → ImageMagick `-resize 14112x2688\!` torzít kb. 2.2× faktorral, betűk és arc-arányok használhatatlanok
3. **Adobe MCP `image_generative_expand`** → blob-upload finalize lánca komplex (508 redirect után "Bad Request"), nem reliable

## Working solution: 3-panel stitching

Generálj **HÁROM panelt** különböző promtokkal és összefűzd `+append`-pel.

### 1. Center panel (21:9)

A fő design — slogan + karakter-zóna + kontakt-blokk. Hagyd üresnek a karakter-zónát ha utólag composite-elsz valódi PNG-t bele.

```bash
nano-banana "Retro comic-poster center: KC logo top-left + slanted slogan + ORANGE IMPACT BURST (EMPTY CENTER — no characters) + HÍVJ MOST! callout + phone + URL" \
  -m pro -s 4K -a 21:9 -o center
```

Output: 6336×2688.

### 2-3. Side extension panels (3:2)

Ez a kulcs trükk — generálj kettő különálló **3:2 wide** panelt brand-decorations-szel. nano-banana 3:2-nél 4K size = ~5056×3392 (height > 2688, scale-down kell).

**Bal extension prompt** (KC monogramok + tool ikonok + sub-burst + lightning + brand-strip alul, JOBB SZÉLEN teal-fade hogy a center teal-paneljébe blend-eljen):

```bash
nano-banana "Vertical panel for LEFT EDGE of retro vehicle wrap. ENTIRE BACKGROUND cream paper with halftone grain. RIGHT EDGE: gentle teal-stained transition to merge with adjacent teal panel. ELEMENTS: 3-4 KC monogram badges, 4-6 black flat tool icons (mower/drill/chainsaw), secondary orange impact-burst with hammer+wrench, lightning-bolts, KISGÉPCENTRUM brand-strip ribbon at bottom." \
  -m pro -s 4K -a 3:2 -o left-ext
```

**Jobb extension prompt** — szimmetrikus, de a BAL szélen kell cream-fade (a center cream zónájába kapcsolódik), és a fő ornamentum lehet egy ribbon-banner ("GÉPKÖLCSÖNZŐ · SZERVÍZ · ÁRUHÁZ").

### 4. Stitching

```bash
# Scale extensions to height 2688
convert left-ext.jpeg  -resize x2688 left-s.png   # → 4007×2688
convert right-ext.jpeg -resize x2688 right-s.png  # → 4007×2688

# Crop to 3888 wide — KEEP THE BLEND EDGE
# Left ext: keep RIGHT 3888 px (teal-fade edge meets center)
convert left-s.png  -crop 3888x2688+119+0 +repage left-crop.png
# Right ext: keep LEFT 3888 px (cream-fade edge meets center)
convert right-s.png -crop 3888x2688+0+0   +repage right-crop.png

# Final stitch: 3888 + 6336 + 3888 = 14112 ✓
convert left-crop.png center.jpeg right-crop.png +append matrica-final.png
```

Output: **14112×2688 = 5.25:1 edge-to-edge**.

## Seam-hiding tippek

- **Color blend zónák** — a panel-prompt-ban kérd KIFEJEZETTEN a panel-éleknél a szomszédos color-t (pl. *"RIGHT EDGE: gentle teal-stained transition"*). nano-banana megérti és blend-területet rajzol.
- **Halftone consistency** — minden panel-prompt-ban azonos hex-kódok (`#0E8C8C` teal, `#E87A20` narancs, `#FAF6F1` cream) + `subtle halftone dot grain texture and slight off-register print feel`. Így a textúra konzisztens.
- **Brand-strip ribbon a panelek alján** — vízszintes folytonosság illúziója (még ha a két ribbon nem is exact-match, a szem benne látja a folyamatosságot).

## Költség

- 3 generálás Pro 4K = **~$0.92 / verzió** (Pro $0.28-0.32 / kép)
- Flash-en olcsóbb (~$0.15/kép) de a halftone-textura és karakter-konzisztencia gyengébb

## Limitációk

- **Karakter-átfedés panel-seamen** kerülendő — ha a center burst kilóg az extension-be, seam láthatóvá válik. Tervezd úgy hogy karakterek a center 6336-on belül vannak.
- **Két extension promt SZÁMÍT**: ha mindkettő ugyanazt kéred, sym­metrikus de unalmas. Diverzifikáld: bal = tool-icon-rich, jobb = ribbon-text-rich (pl).

## Élő példa

KGC autó-matrica 210×40 cm (`/root/projektjeim/Kisgépcentrum-marketing/brand/car-wrap-2026-05/matrica-Q-v19-final.png`, 2026-05-13) — bal extension 3 KC monogram + tool-rich + sub-burst, jobb extension SZERVÍZ-burst + ribbon. Center 21:9 retro comic-burst poster üres-burst karakter-zónával, utólag 3D Felix+Flexi PNG composite ImageMagick-kel.

## Kapcsolódó

- [[nano-banana-cli-gotchas]] — CLI flag-bugok
- [[wp-elementor-template-conflicts]] — másik konfliktus-playbook minta
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[svg-img-overlay-aspect-ratio]] (sem-rokon, score=0.57)
