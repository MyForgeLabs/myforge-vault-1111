---
name: Sharp.js face-aware avatar crop
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#stack/sharp", "#image-processing"]
---

# Sharp.js `position: "attention"` — face-aware avatar crop

Avatar-feltöltések feldolgozásakor a default `fit: "cover"` a **kép közepét**
veszi. Selfie-knél (különösen iPhone-on portrait-mód-ban) a face gyakran NEM a
középen van — full-body shot esetén a feje csak a felső 30%-on. A default
center-crop levágja az arcot.

## A fix

```typescript
await sharp(buf)
  .rotate()                              // EXIF auto-orient
  .resize(400, 400, {
    fit: "cover",
    position: "attention",               // ← face-detect, focuses on most "interesting" area
    withoutEnlargement: true,
  })
  .webp({ quality: 82 })
  .toBuffer();
```

A `position: "attention"` (libvips beépített funkciója) **entropy-based
detection-t** futtat — talál egy "salient region"-t (általában az arcot, vagy a
legdetail-dúsabb területet) és arra centeráz.

Alternatívák:

- `position: "entropy"` — hasonló de tisztán entropy-alapú, kevésbé okos
  multi-face-en
- Manual face-detection (pl. `@vladmandic/face-api`) — sokkal pontosabb, de
  külön WASM-load + setup-overhead

A `"attention"` 90%-ban megoldja a problémát és teljesen built-in.

## Boulium pattern (Phase 1 + 2)

```typescript
const PRESETS: Record<Kind, { width, height, quality, fit, position? }> = {
  match:  { width: 1400, height: null, quality: 80, fit: "inside" },   // aspect-keep
  venue:  { width: 1400, height: null, quality: 78, fit: "inside" },   // aspect-keep
  avatar: { width: 400,  height: 400,  quality: 82, fit: "cover", position: "attention" },
};
```

`match` és `venue` esetén `fit: "inside"` = aspect-keep, csak width-szerint
constrain. Itt nincs crop, nincs `position`.

Avatar viszont **square output** (400×400) — itt **kötelező** a `fit: "cover"`
és érdemes `position: "attention"`-nel hozni a face-t.

## UI-oldal pár-rajzolás

A `PhotoUpload` komponens-ben az `aspect` prop:

```tsx
<PhotoUpload
  aspect="square"    // 1:1 preview match the server-side avatar output
  capture="user"     // iOS/Android front-camera
/>
```

Square preview → user pontosan azt látja amit a server is fog kapni.

## Caveat — `withoutEnlargement: true`

A `withoutEnlargement` opció megakadályozza hogy a kép FELskáláz-ódjon. Ha a
forrás 300×500, akkor `target=400×400 cover` esetén **300×300**-ra fog cropolni
(a kisebb dimenzió korlátozza). Ez OK — kis kép kis avatar lesz, NEM blur.

Ha mindig pontosan 400×400-as output kell, `withoutEnlargement: false` (default)
— akkor pixelesen felskáláz-ódhat a kis kép. Boulium-ban a friends-MVP NEM
ragaszkodik 400×400-hoz pontosan, tehát `true` marad.

## Boulium-példa (2026-05-19)

Az `EditProfileForm` és `lib/upload.ts` ezzel a setup-pal él a 2026-05-19-i
deploy-tól. iPhone-Safari verify pending.

## Kapcsolódó

- libvips docs: position: attention
- [[../11-wiki/nano-banana-cli-gotchas]] — másik image-pipeline quirk
