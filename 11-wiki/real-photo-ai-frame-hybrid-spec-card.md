---
name: Real-photo + AI-frame hibrid spec-card workflow
type: wiki
tags: ["#type/wiki", "#pattern/ai-image", "#pattern/marketing"]
created: 2026-05-18
updated: 2026-05-18
---

# Real-photo + AI-frame hibrid spec-card

> Valódi termékfotó mint primary reference + AI által generált brand-frame (template-layout + tipográfia + brand-elemek) → autentikus márka-logók + brand-konzisztens UX. Pure-AI render-nél sokkal jobb spec-card minőség.

## Mikor használd

Termékkártya (FB/IG spec-poszt) ahol:
- A termék VALÓDI márka (Stihl, Honda, Jansen, Bosch, Makita stb.) — a logók pontosan kellenek
- Tipográfia + ár + spec-bullet-listák brand-templét szerint
- Skálázható kell — N termékre ugyanaz a layout
- Pure-AI render = hallucinált decal-ok, fake brand-felirat, márka-pontatlanság

KGC validáció (2026-05-18): iter-12 pure-AI ipari spec-card → „generic petrol log-splitter" (fake brand). iter-13 real-photo ref + AI-frame → autentikus „JANSEN HS-20DS" feliratokkal a vázon.

## Workflow

1. **Reference photo source** — bekérni a vagy ügyfél, vagy public CDN (kisgepcentrum.hu/api/categories → imgur.com lásd [[spa-api-discovery-jsbundle]])
2. **Layout reference** (egyszer kell) — kérj egy közeli referencia-mintát ami a target layout-ot mutatja. KGC-eset: a user által felülmutatott „Mower_compositing_task_instructions" jpeg.
3. **Brand assets ref** (egyszer): KC logo transparent PNG, mascot karakter portrék (Soul-based → lásd [[higgsfield-soul-training-multi-character]])
4. **Multi-ref `nano_banana_2` call** mindegyik termékre:
   - Reference 1: TERMÉK valódi fotó (primary character of the scene)
   - Reference 2: LAYOUT-template (target composition rhythm)
   - Reference 3: brand-logo (top-right composite)
   - Reference 4: mascot (bottom-right composite)
   - Prompt: explicit a layout-ról + spec-bullet szöveg + brand-paletta strict
   - Aspect_ratio: 16:9 (vagy 9:16 ha Reels)
5. **Output**: a valódi termék + brand-logo + Flexi mascot + AI-generated tipográfia és spec-szöveg

## KGC validáció — 4 ipari spec-card (2026-05-18)

| Termék | Real-photo ref | Output |
|--------|---------------|--------|
| BREAKER BK60 lapvibrátor | `epitoipari/talajtomorito/breaker-bk60.png` (kisgepcentrum.hu API) | „BREAKER BK60" felirat autentikusan a vázon |
| JANSEN RD-300 motoros talicska | `anyagmozgato/jansen--rd-300.png` | JANSEN logo + RD-300 badge megmaradt |
| JANSEN HS-20DS rönkhasító | `fafeldolgozo/jansen-hs-20-ds.png` | JANSEN branding rendben |
| HONDA TR-5E AVR áramfejlesztő | `egyeb-epitoipari/honda--tr-5e-avr.png` | HONDA-piros engine + TR-5E badge |

Eredmény: 4×4cr = **16 credit** mindössze, 4 ipari pro-szintű spec-card.

## Pitfalls

- **Aspect-ratio mismatch** — ha a layout-ref 16:9 és a kért output 9:16, AI gyakran rosszul kombinálja. Tartsd ugyanaz a ratio. 9:16-ra később ffmpeg-pad fehérre OK.
- **Reference-overload** — 5+ ref-kép után az AI elveszti a layout-instrukciót. **Max 4 ref** ajánlott (termék + layout + logo + mascot).
- **Magyar diakritika Ű→Ú** — `nano_banana_2` gyakran rosszul rendel double-acute-ot. Workaround: szöveg-overlay Pillow-ban post-process, VAGY explicit prompt-instrukció.
- **„a kép illusztráció" overlay** — ha a reference-fotón rajta volt, AI átveheti. Vágd ki a footer-feliratot előtte (ImageMagick crop), vagy explicit a promptban: „NO text watermarks".

## Cost saving vs pure-AI

| Approach | Cr/spec-card | Quality |
|----------|--------------|---------|
| Pure-AI (no termék-ref) | 4 cr | Generic, hallucinated brand |
| Multi-ref (no real photo) | 4-8 cr | Better brand-shape, still fake decals |
| **Real-photo + AI-frame** | **4 cr** | **Autentikus márka + brand-template** ✓ |

## Kapcsolódó

- [[spa-api-discovery-jsbundle]] — hogyan szerezzünk 175+ valódi termékfotót egy SPA-API-ból
- [[higgsfield-soul-training-multi-character]] — Soul-trained karakter mint mascot-ref a spec-card-hoz
- [[nano-banana-cli-gotchas]] — `nano_banana_2` egyéb quirk-ek
- `02-Projects/kgc-marketing.md` — KGC marketing workflow ahol a pattern született
