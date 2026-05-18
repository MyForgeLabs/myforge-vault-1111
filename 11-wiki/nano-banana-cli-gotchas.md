---
name: nano-banana-cli-gotchas
type: wiki
created: 2026-05-13
updated: 2026-05-13
tags: ["#topic/nano-banana", "#topic/cli-gotchas"]
---

# nano-banana CLI gotchas

A `nano-banana` Gemini Image CLI (telepítve `~/.nano-banana/` + `/usr/local/bin/nano-banana`). 2026-05-13 KGC car-wrap-session 15+ iteráció során a következő quirk-ek dolgozódtak ki.

## #1 — Reference image flag: `-r`, NEM `-i`

A help-output kifejezetten `-r` / `--ref`-ot mond, **de** ha tévedésből `-i`-t használsz, a CLI **NEM dob hibát** — hanem **prompt-string eltűnik** silent fashion.

Hibás:
```bash
nano-banana "long prompt here..." -i felix.png -i flexi.png
# Stderr: "Prompt: flexi-rolling-final.png"   ← prompt felülíródva fájlnévvel!
# Result: két suitcase egy reptéren ← hallucinated
```

Helyes:
```bash
nano-banana "long prompt here..." -r felix.png -r flexi.png
# Stderr: "Prompt: <correct prompt>"
# Stderr: "References: felix.png, flexi.png"   ← explicit visszajelzés
```

**Detektálás:** ha az output stderr-ben `Prompt: <fájlnév>.png` látszik (nem a tényleges prompt-szöveg), elnyelte. **Mindig olvasd a Prompt-sort a stderr-ben mielőtt elfogadnád az output-ot.**

## #2 — `-r` reference image FLATTEN-i a karakter-stílust

Ha a prompt comic-flat/illusztrált stílust kér ÉS a reference 3D Pixar-render → a model **FLAT-RE rendereli a karaktert** is, NEM keveri vissza az eredeti 3D stílust.

Élő példa (2026-05-13):
```bash
# Cél: retro comic poster, DE 3D Felix+Flexi megőrzése
# Bemenet:
nano-banana "retro 1960s flat comic poster… [Felix+Flexi]" -r felix-3d.png -r flexi-3d.png
# Eredmény: comic-flat Felix+Flexi, NEM 3D
```

**Megoldás**: ne `-r`-rel add be a karaktert. Generálj **csak hátteret** (üres burst-zónával), aztán **utólag composite-eld** a 3D PNG-t ImageMagick-kel:
```bash
# 1. background only
nano-banana "retro burst poster, EMPTY orange burst in center, NO characters" -m pro -s 4K -a 21:9 -o bg
# 2. composite real 3D character
convert bg.jpeg felix-3d.png -geometry +2533+270 -composite output.png
```

## #3 — Max aspect ratio = 21:9

`-a` flag elfogad: `1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 4:5, 5:4, 21:9`. **Ennél szélesebb (5.25:1, 6:1, panorámika) nem támogatott** — workaround 3-panel stitching, lásd [[nano-banana-ultra-wide-stitch]].

## #4 — 4K size + extreme aspect = LARGER mint várt

`-s 4K -a 3:2` ⇒ output **5056×3392** (NEM 4096×2730 ahogy várnánk a "max 4096"-ból). A modell a kisebb tengelyt 3392-ig is feltolja ha aspect tartható. **Scale-down kell** ha fix-méretű panelt szeretnél stitchhez:
```bash
convert ext.jpeg -resize x2688 ext-scaled.png   # height-match
```

## #5 — Költségek (2026-05-13 árazás)

| Model | 1K | 2K | 4K |
|---|---|---|---|
| Flash (default, `nb2`) | $0.067 | $0.10 | $0.15 |
| Pro (`nb-pro`) | ~2× Flash | ~$0.20 | **~$0.28-0.32** |

Brand-pontos retro halftone + Hungarian text accent (Ő, É, Á) Pro-t igényel. Flash gyakran rontja a magyar ékezeteket vagy halftone-texture nélkül renderel.

## #6 — `-t` transparent flag (green-screen workflow)

`nano-banana "robot mascot" -t -o mascot` → green-screen background-on generál + FFmpeg colorkey + despill = transparent PNG. **De**: ha a karakteren bárhol zöld-szín (pl. zöld overall, zöld háttér-elem), az is leszedődik. **Use case-specifikus**, marketing-design-on inkább Adobe MCP `image_remove_background`-ot használj az utómunkára.

## Kapcsolódó

- [[nano-banana-ultra-wide-stitch]] — 5.25:1+ workaround
- [[notebooklm-cli-gotchas]] — másik AI CLI quirk-kompiláció minta
