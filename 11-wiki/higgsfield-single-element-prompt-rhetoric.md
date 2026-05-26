---
name: higgsfield-single-element-prompt-rhetoric
description: Higgsfield nano_banana_pro single-element prompt retorika — EXACTLY ONE + position-percent + ABSOLUTE CRITICAL záró-blokk a duplikáció elkerülésére
type: wiki
tags: ["#type/wiki", "#tool/higgsfield", "#topic/prompt-engineering"]
created: 2026-05-22
updated: 2026-05-22
---

# Higgsfield single-element prompt retorika

> **Kontextus:** Higgsfield `nano_banana_pro` (alias `nano_banana_2`) hajlamos szöveges/grafikus elemek (badge, sticker, slogan) DUPLIKÁCIÓJÁRA. A 2026-05-20-i Mercedes-matrica v22-v27 iterációkban folyamatosan visszajött a probléma. A 2026-05-22-i v31-en sikerült letörni — itt a recept.

## Probléma

A gyenge `"ONE single badge"` vagy `"do NOT draw two"` prompt-fragmens **NEM garantálja** a single-példányt. A modell mégis 2× vagy 3× kirajzol egy elemet (különösen szöveges sticker / star-burst esetén), mert:

- a referencia-képek (multi-ref) több helyen mutathatnak hasonló elemet
- a komppozíciós AI „kitölti" a térrész 1-2 további kópiával ha üresnek látja
- a single-utasítás csak gyenge soft-constraint

## Bevált 4-elemes retorika

A `nano_banana_pro` Pro 4K-n a **2026-05-22-i v31-gen** elsőre eltalálta a single-badge-et az alábbi prompt-struktúrával:

### 1. **Explicit position-percent specifier**

NEM `"on the right"` — hanem konkrét bbox-zóna százalékban:

```
FAR-RIGHT EDGE (x: 90%-99%): EXACTLY ONE single orange star-burst sticker...
```

A modell így pontosan tudja hol legyen a single-példány, NEM keresgéli más zónákban.

### 2. **EXACTLY ONE + NEVER + ANYWHERE ELSE**

Mindhárom retorikai eszköz együtt:

```
This is the ONLY orange burst sticker in the entire image — there must
NOT be any second copy of this sticker anywhere else.
```

Az „EXACTLY ONE" + „NEVER duplicate" + „anywhere else" együtt erős negative-constraint.

### 3. **Layout-zónák explicit (LEFT THIRD / CENTER / RIGHT THIRD)**

Minden karakter/elem a saját zónájához van rendelve:

```
LEFT THIRD (x: 5%-30%): Lexia...
CENTER (x: 35%-65%): The slogan...
RIGHT THIRD (x: 65%-95%): Felix and Flexi...
FAR-RIGHT EDGE (x: 90%-99%): EXACTLY ONE sticker...
```

Így a modell nem keveri a zónákat, és nem dupliálja a stickert a center-zónába vagy bárhova.

### 4. **ABSOLUTE CRITICAL RULES záró-blokk**

A prompt VÉGÉN egy retorikai kiemelés:

```
ABSOLUTE CRITICAL RULES (failing any of these makes the image unusable):
- EXACTLY ONE HÍVJ MOST orange burst sticker, located only at the far-right edge.
  NEVER duplicate it.
- EXACTLY ONE Lexia, EXACTLY ONE Felix, EXACTLY ONE Flexi.
- NO text whatsoever on Flexi's display face — ONLY the single round blue eye.
- Hungarian language only — no English words.
- The slogan appears exactly ONCE in the center.
```

A „**failing any of these makes the image unusable**" + listapointok együtt a legszigorúbb retorikai garancia.

## Mikor használd

- Bármilyen `nano_banana_pro` / `nano_banana_2` multi-element 21:9 layout-ban (autó-matrica, hero-banner, social-creative)
- Különösen ha szöveges sticker, badge, plecsni jelenik meg (text-rendering = legmagasabb duplikáció-rizikó)
- Multi-character composition (3+ karakter) — explicit LEFT/CENTER/RIGHT zónák

## Költség-margin

Még a SZIGORÚ retorikával is ~10-15% esély a duplikációra. Erre tervezz **2-3 re-gen budget**-et Pro 4K-n (8-12 cr).

## Cross-link

- [[higgsfield-aspect-ratio-limits]] — Higgsfield max 21:9 + flash vs Pro cost-map
- [[multi-asset-brand-composite-workflow]] — alternatíva: külön asset-ek + Pillow composite ha a single-prompt-retorika nem elég
- [[nano-banana-cli-gotchas]] — text-rendering AI-duplikáció más kontextusban

## Történet

- **2026-05-22 v31 car-wrap session** (Mercedes 210×40 cm) — első sikeres single-badge generálás Pro 4K-n. Tegnapi v22-v27 iter mind duplikált, ma az 1. re-gen elsőre tisztán
