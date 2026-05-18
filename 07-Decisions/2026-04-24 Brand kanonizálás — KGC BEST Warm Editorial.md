---
name: Brand kanonizálás — KGC BEST Warm Editorial v4.0
type: decision
tags: [kgc-berles, design, brand, decision]
created: 2026-04-24
updated: 2026-04-24
project: kgc-berles
---

# Brand kanonizálás — KGC BEST Warm Editorial v4.0

> [!info] Döntés időpont: 2026-04-24
> A KGC-Bérlés frontend-jén két párhuzamos design rendszer dokumentum élt — most véglegesítve melyik a kanonikus.

## Háttér — a feszültség

Két forrás eltérő palettát mondott:

1. **`BRAND.md` v3.0** (2026-04-18) — *Zapier-inspired warm cream*: cream `#FFFEFB`, ink `#201515`, narancs `#E87A20`, sand `#C5C0B1`, fontok Hanken Grotesk + Inter + Instrument Serif, **border-only** (no shadow), 4-5px radius, spacious 20×24 CTA padding.
2. **`app/globals.css` v5.0** (2026-04-19, élesben fut) — *Warm Editorial / KGC BEST petrolkék hero*: cream `#FAF6F1`, slate `#1A1614`, narancs `#E85D2F`, divider `#E5DAC9`, fontok Archivo + Inter + Caveat, **soft shadow** kártyán, **pill 9999px** primary CTA.

A két rendszer egymástól független színekkel, fontokkal, button-stílussal és card-elevation-nal dolgozott. **A komponensek a globals.css aliasrétegen** (`bg-ink`, `text-blaze`, `bg-bone` stb.) keresztül **automatikusan a v5.0-ra képződtek le**, így a vizuális UI mindig a v5.0-t mutatta — a BRAND.md gyakorlatilag fikció volt.

## Mi történt valószínűleg

- **Apr 18** — Egy designer-iteráció a Zapier rendszert dokumentálta BRAND.md-ben mint "kanonikus mankó".
- **Apr 19 (másnap)** — A Kisgépcentrum Prototípus (claude.ai/design export, Anthropic Design `dfHg29Vi88oF87nk0EQ9nQ`) áttette az UI-t **KGC BEST petrolkék hero** rendszerre. A `globals.css` v5.0 ezt implementálta, **de BRAND.md nem lett frissítve**.
- **Apr 24** — A frontend-folytatás session-ben felmerült a feszültség, döntés szükséges.

## Döntés

**Az élő `app/globals.css` v5.0 = kanonikus.** A `BRAND.md`-t v4.0-ra frissítettük, hogy az élő rendszert dokumentálja.

### Indoklás

| Szempont | Megfontolás |
|----------|-------------|
| **Élesben mi fut?** | A v5.0 — ez az amit a user (és minden látogató) ténylegesen lát |
| **Frissebb?** | v5.0 (apr 19) > v3.0 (apr 18) — egy nappal újabb |
| **Brand-koherens?** | Petrolkék `#0E8C8C` = Peti **valódi céges színe** (póló) → hero rangú, nem csak decoratív |
| **Forrás?** | Anthropic Design `dfHg29Vi88oF87nk0EQ9nQ` (KGC BEST) — szándékos design-választás, nem akcidentál |
| **Komponens-stabilitás?** | Aliasok mindkét irányba működnek — átírást nem igényel |
| **Trade-off** | A Zapier verzió önmagában letisztultabb (border-forward, 3-font hierarchia), de nem a KGC valódi arculata |

## Implementáció (2026-04-24, ez a session)

### Új fájlok / módosítások

- ✅ `BRAND.md` **v4.0 átírva** — KGC BEST Warm Editorial dokumentációja: paletta tokenekkel (`--color-soft-bg`, `--color-slate`, `--color-kgc-petrol`, `--color-kgc-orange`), tipográfia (Archivo + Inter + Caveat), komponens-stílusok (`btn-pill-orange`, `card-hover`, `gate-card`, `brand-swoosh`), animáció primitívek, legacy alias-tábla, 11. szekcióban dokumentálva mit távolítottunk el.
- ✅ `docs/archive/BRAND-v3-zapier.md` — eredeti Zapier v3.0 archiválva, tetején ⚠️ ARCHIVED bélyeg + kanonikus-mutató.
- ✅ `app/layout.tsx` — `TweaksPanel` import + render eltávolítva.
- ✅ `components/shared/TweaksPanel.tsx` — fájl törölve.
- ✅ `app/globals.css` — `body[data-accent="orange|amber|red"]` és `body[data-corner="square|rounded|pill"]` runtime tweak CSS-blokkok eltávolítva (~70 sor).

### Mit NEM bántottunk

- A v5.0 paletta tokenek mind maradtak (`--color-petrol-tint`, `--color-kgc-petrol-soft`, `--color-kgc-glow` stb.) — éles használatban vannak.
- A teljes legacy alias-réteg (`--color-ink`, `--color-blaze`, `--color-bone`, stb.) maradt — backward-compat.
- A 3 font (Archivo, Inter, Caveat) `next/font/google` betöltése változatlan, csak a CSS változó-aliasok (`--font-poppins` → Archivo, `--font-dm-sans` → Inter) maradtak fenn kompatibilitás miatt; az új BRAND.md ajánlja a `--font-display`, `--font-sans`, `--font-hand` használatát új kódban.

### Ellenőrzés

- Dev server `http://187.77.70.36:3004/` — HTTP 200 ✓ (Turbopack hot-reload OK)
- Fájl-szintű grep: `TweaksPanel` és `data-accent` / `data-corner` hivatkozás többé nincs.

## Következmények — ezt jelenti a továbbiakban

- **Új komponens / szekció** → ELŐBB a `BRAND.md` v4.0-t olvassa, csak ott listázott tokeneket / fontokat / komponens-stílusokat használ.
- **Új színt SOHA hardcode-olni** — minden `var(--color-...)` token vagy Tailwind alias.
- **Designer prompt** (ha kell, pl. új mockup nano-banana-val) — petrolkék hero + narancs CTA + cream canvas + Archivo display kontextusra építsen, NEM a Zapier "warm cream + Hanken" világra.
- **A Zapier tradícióból megtartottuk:** "szomszéd srác" hangnem (7. szekció) változatlan, karakterek (Félix, Flexi, Lexia, Kis János) változatlan.

## Open kérdés (későbbre)

- A jelenleg elérhető Lexia karakter képek hiányosak — `Lexia duo/trio` még generálandó (külön backlog item, `nano-banana` skill + `docs/2026-04-20/karakter-promptok/`).
- A `globals.css` még tartalmaz pár retro-decor osztályt (`brand-swoosh`, `gate-card`, `dot-pulse`, `shimmer-sweep`, marquee) — ezek **használatban vannak**, nem törlendők, de érdemes lenne audit hogy minden használati helye konzisztens-e a brand-narratívával.

## Kapcsolódó

- [[02-Projects/kgc-berles]]
- [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1]]
- Korábbi session: [[08-Sessions/2026-04-24-kgc-frontend-fejlesztes]]
- Aktuális brand: `/root/projektjeim/KGC-ALL/kgc-berles/BRAND.md` v4.0
- Archív: `/root/projektjeim/KGC-ALL/kgc-berles/docs/archive/BRAND-v3-zapier.md`
