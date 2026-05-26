---
name: pillow-cream-spotlight-pattern
description: Pillow cream-spotlight Gauss-blur pattern — pattern-háttéren a karakterek/szöveg kiemelésére. Ellipse-fill + GaussianBlur(200) + alpha-composite.
type: wiki
tags: ["#type/wiki", "#tool/pillow", "#topic/design-pattern"]
created: 2026-05-22
updated: 2026-05-22
---

# Pillow cream-spotlight pattern

> **Probléma:** pattern-háttéren (akár halvány) a karakterek és szöveg elveszhetnek a vizuális zajban. **Megoldás:** 1-3 nagyon halvány, soft-edge cream-ellipse a kulcsfontosságú zónák alá — a karakterek/slogan „felragyognak" a háttérből, és a pattern visual-noise-ja eltűnik mögöttük.

## Recept

```python
from PIL import Image, ImageDraw, ImageFilter

FINAL_W, FINAL_H = 14112, 2688  # 5.25:1 car-wrap
CREAM = (250, 246, 241)

# 1. Pattern háttér (halvány)
pattern = Image.open("pattern.png").convert("RGB")
cream_layer = Image.new("RGB", (FINAL_W, FINAL_H), CREAM)
bg_faded = Image.blend(cream_layer, pattern, 0.35)  # 35% pattern, 65% cream

# 2. 3 cream-spotlight a karakter-zónák alá
spotlights = Image.new("RGBA", (FINAL_W, FINAL_H), (0, 0, 0, 0))
sd = ImageDraw.Draw(spotlights)

# Lexia spotlight (bal-zóna)
sd.ellipse([100, 200, 2900, 2700], fill=(*CREAM, 200))

# Center spotlight (slogan + KC logo zóna)
sd.ellipse([3500, 0, 10600, 2688], fill=(*CREAM, 220))

# Felix+Flexi spotlight (jobb-zóna)
sd.ellipse([11000, 200, 14000, 2700], fill=(*CREAM, 200))

# 3. Erős Gauss-blur a soft-edge átmenetért
spotlights_blur = spotlights.filter(ImageFilter.GaussianBlur(200))

# 4. Alpha-composite
canvas = bg_faded.convert("RGBA")
canvas = Image.alpha_composite(canvas, spotlights_blur)

# 5. Karakterek + szöveg-elemek ide jöhetnek tovább
```

## Paraméterek

| Paraméter | Default | Tartomány | Hatás |
|---|---|---|---|
| **Spotlight alpha** | 200-220 | 150-240 | Erősebb spotlight → karakterek tisztábban állnak ki, de pattern is jobban eltűnik |
| **GaussianBlur radius** | 200 | 100-300 | Nagyobb blur → simábrább átmenet, kisebb élvonal-detektálhatóság |
| **Pattern blend ratio** | 0.30-0.40 | 0.20-0.60 | Magasabb → erősebb pattern, kell magasabb spotlight-alpha |
| **Ellipse aspect** | wide-horizontal | bármilyen | Karakter alá inkább vertical-elongated (függőleges), center-alá inkább széles |

## Mikor használd

- Pattern-háttéren készülő multi-character brand-asset (car wrap, banner, hero)
- Ahol a karaktereket KIEMELNI kell a pattern-ből, de a pattern is megmaradjon brand-elemnek
- Slogan + logo center-zóna „aurázása" a háttér-zsongl őr nélküli olvashatóságért

## Mikor NE használd

- Tiszta cream BG (nincs mit kiemelni)
- Foto-háttér (real-world scene) — ott a soft-edge cream-pad zavar, inkább dark-translucent banner megy
- 9:16 vertical (Reels/Story) — egy spotlight elég, NEM 3

## Gauss-blur teljesítmény

A 14112×2688 px-en GaussianBlur(200) **lassú** (~10-15 sec Python-PIL-ben). Ha gyorsabb kell:
- Generálj kisebb spotlight-mask-ot (1920×400) Gauss-blur 30-cal, aztán resize 7x
- VAGY: numpy-scipy `gaussian_filter`-rel (gyorsabb)

## Cross-link

- [[multi-asset-brand-composite-workflow]] — a teljes composite workflow ahol ez a Pillow-spotlight része
- [[pillow-edge-tile-strip-issues]] — más Pillow-pattern-tricks
- [[higgsfield-aspect-ratio-limits]] — Higgsfield pattern wallpaper generálás-tipusok

## Történet

- **2026-05-22 v36-v37 car-wrap** — első alkalmazás Mercedes 210×40 cm matricán. 3 spotlight (Lexia/center/Felix-Flexi alá) eldöntötte a „pattern-zsongl őr vs olvashatóság" konfliktust.
