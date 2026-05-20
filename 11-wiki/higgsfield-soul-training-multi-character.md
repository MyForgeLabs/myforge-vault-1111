---
name: Higgsfield Soul training — multi-character workflow
type: wiki
tags: ["#type/wiki", "#tool/higgsfield", "#pattern/ai-image"]
created: 2026-05-18
updated: 2026-05-18
---

# Higgsfield Soul training — multi-character workflow

> Brand-konzisztens AI karakter-rendering 5-20 ref-képből; multi-character szcénák külön Soul-okkal + nano_banana_2 komponálással.

## Mikor használd

Brand-projekt amelyik **ismétlődő, konzisztens karaktert** igényel (mascot, recurring narrator, brand-személy). Pure-prompt vagy multi-ref nano_banana_2 NEM elég a pixel-pontosságra — minden generálás kis változással szül (más arc, más outfit, más detail). Soul training egyszeri befektetés ami örökre kifizetődik.

KGC validáció (2026-05-18): Felix + Flexi 3 órás multi-ref próbálkozás után UI-szinten elfogadhatatlan volt; Soul training 10 perc/karakter és **9 nap múlva is pixel-pontos** marad.

## Workflow

1. **Ref-képek gyűjtése** — 5-20 db / karakter. Sokféle szög, póz, expresszió. Lehetnek meglévő AI-generálták is, ha brand-konzisztens design-uak.
2. **Upload Higgsfield-re** — `media_upload` + `media_confirm` mindenre. Vagy https URL-eket átadhatsz közvetlenül (CDN képeknél).
3. **Soul training kick-off**:
   ```
   show_characters(action="train", name="<KaraktérNév>", images=[<url1>, <url2>, ...])
   ```
   Returns `soul_id` (UUID) + status="training", raw_status="queued". A training **~5-10 perc**, NEM blokkol (background).
4. **Polling** — `show_characters(action="status", soul_id="...")`. Sikeres → `status="ready"`, `raw_status="completed"`.
5. **Use the Soul** — `generate_image(model="soul_2", soul_id="...", prompt="...")`. Pixel-pontos karakter, brand-konzisztens.

## ⚠️ Multi-character KORLÁT

`soul_2` modell **CSAK 1 `soul_id` paramétert fogad** (per `models_explore`). Tehát Felix + Flexi együtt EGY képben soul_2-vel nem megy.

**Megoldás (validated):**

1. **Egyenként generáld a karaktereket** soul_2-vel, kanonikus pózban (standing portrait, white BG): `Felix standing in neutral pose` → portrait-1; `Flexi standing` → portrait-2.
2. **Upload a portrékat** Higgsfield-re mint új media-id-k.
3. **Komponáld a final szcénát nano_banana_2-vel multi-ref-fel** — pass the soul-portré media_ids mint reference images + prompt: „Match the supplied Felix portrait reference EXACTLY for character accuracy + match the supplied Flexi portrait reference EXACTLY".

A multi-ref nano_banana_2 a soul-portrékat erős STYLE-anchor-ként használja, így a karakterek konzisztensek maradnak — bár NEM olyan pixel-pontosan mint pure soul_2, de sokkal jobb mint multi-ref-only.

## Validation case — KGC (2026-05-18)

- **KGC Felix** soul_id `6eafea30-a874-47c6-9b7a-8a022f071a62` (9 ref: 4 pose + 3 face + 1 main + 1 duo studio)
- **KGC Flexi** soul_id `a2a2bfac-1715-4d96-afe3-f30c3df2d03b` (10 ref: 1 pose + 2 eyes + 1 main + 5 duo + 1 studio)
- Training time: **9-10 perc** mindkettő párhuzamosan
- Cost: **0 cr** training, 4cr/generation (nano_banana_2-ben mint ref használva)

## Pitfalls

- **media_id UUID NEM működik soul-training-en** — `show_characters(action="train")` `Expected a media_id UUID, completed image generation job ID, or https:// URL` errort dob régi media_id-kre. **Workaround**: használj https URL-eket direkt (`https://d2ol7oe51mr4n9.cloudfront.net/.../<media_id>.png`)
- **"fetch failed" transient** — a Higgsfield-szerver időnként eldobja a kérést. Retry 1-2x és átmegy.
- **Higgsfield CDN URL ≠ image-input** — a CDN-en lévő soul-preview .png URL-t **nem fogad el** `generate_image(medias=...)`-ben (`Unsupported content-type: binary/octet-stream`). **Workaround**: töltsd le, töltsd fel újra `media_upload`-dal → új media_id használható ref-ként.

## Költség-becslés

- Training: **$0** (a Higgsfield ingyenesen biztosítja a Myforge labs team plan-ben)
- Per-generation: változó (soul_2 ~4-8 cr, nano_banana_2 multi-ref ~4 cr)
- ROI: 1 brand-karakter Soul = elvileg ezer+ generálás minőség-degradáció nélkül

## Kapcsolódó

- [[nano-banana-cli-gotchas]] — `nano_banana_2` quirks (multi-ref, aspect ratio, magyar diakritikák)
- [[real-photo-ai-frame-hybrid-spec-card]] — Real-photo + AI-frame template, ami a soul-portrékat is fel tudja használni
- `02-Projects/kgc-marketing.md` — KGC marketing workflow ahol a Soul pattern született
