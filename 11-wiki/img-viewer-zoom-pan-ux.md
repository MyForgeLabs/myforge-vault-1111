---
name: Image viewer zoom-pan UX pattern
type: wiki
tags: ["#type/wiki", "ux", "frontend", "react", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Image viewer zoom-pan UX

## TL;DR

Touch-és-deszk-friendly image-viewer (MachinePartDiagram, robbantott-bra, schematic, PDF-page-preview) **három épült primitive**-ből áll: (1) `onWheel` zoom prevent-default-tel, (2) double-click 1×↔2× toggle (= a "gyors fit-overflow") és (3) **drag-at-all-scales** (a pan akkor is engedélyezett, ha scale = 1). Ez a hármas eltünteti a tipikus "nem tudom mozgatni mert nincs zoomolva" frustrate-pattern-t.

## Háttér

A robbantott-kereso projekt ([[../02-Projects/robbantott-kereso]]) MachinePartDiagram komponensénél 2026-05-12-13 között 3 különböző fail-mode jött elő:

1. **Wheel-zoom NEM működött** mert React 17+ óta az `onWheel` listener default-passive → preventDefault hatástalan. Ezért nem lehetett scroll-during-zoom blokkolni, és az oldal görgött a kép helyett ([[../08-Sessions/2026-05-12-kgc-robbantott-bra]]).
2. **Double-click reset NEM működött** mobil-Safari-n, ahol a double-tap default zoomot trigger-elt. Fix: `touchstart` listener + manuális tap-counter, NEM `dblclick`.
3. **Pan disabled-when-fit** — feltételes "csak akkor pannable ha zoomolva van" guard miatt user nem tudta mozgatni az 1× nézetet (pedig a panning fit-overflow esetén is hasznos).

A megoldás-mintázat azóta a Client-A-ERP MachinePartDiagram-komponensben, a robbantott-keresőben, és a Client-A katalógus PDF-preview-ban is használt.

## Mintázat

### Wheel zoom

```tsx
useEffect(() => {
  const el = ref.current;
  if (!el) return;
  const handler = (e: WheelEvent) => {
    e.preventDefault();
    setScale(s => clamp(s * (e.deltaY < 0 ? 1.1 : 0.9), 0.5, 8));
  };
  el.addEventListener('wheel', handler, { passive: false });
  return () => el.removeEventListener('wheel', handler);
}, []);
```

### Double-click toggle

- 1× → 2× (a kattintás-pozíciót centerként)
- 2× → 1× (reset)
- Mobil: `touchstart` tap-counter (300ms window), NEM `dblclick`

### Drag-at-all-scales

- `onMouseDown` mindig regisztrál pan-listener-t, NEM csak `scale > 1` esetén
- Boundary-clamp: kép-középpont nem ugorhat ki a viewport-ból (de a kép széle kimehet)

## Anti-pattern

- **`onWheel` JSX-prop default-passive** — `<div onWheel={...}>` React 17+ óta passive, `preventDefault` no-op
- **`dblclick` mobil-Safari-n** — natív double-tap-zoom konfliktus, manuális tap-counter kell
- **Pan-guard `if (scale > 1)`** — frustrate-pattern, az 1× fit-overflow esetén is kell pan
- **Touch-event vs mouse-event külön kód** — pointer-events API-val egységesen kezelhető
- **Window-szintű wheel-listener** — ne a `window`-ra rakd, mert blokkolja a sticky-header scroll-t; localized ref-en

## Reusable szabályok

1. **Explicit `addEventListener('wheel', ..., {passive: false})`** — JSX-prop helyett ref + useEffect
2. **`touch-action: none` CSS** — a container-en, hogy a natív gestures ne lopjon
3. **Boundary-clamp center-pont, NEM bbox** — a kép széle túlhúzhat (jobban érzékelhető a "túl-pan" feedback)
4. **Reset-button mindig látható** — keyboard-shortcut `R` + visible icon
5. **Zoom-step 0.1–0.25** — finomabb 0.1 (wheel), durvább 0.25 (button-click)
6. **Pointer-events API** — `onPointerDown/Move/Up`, NEM külön mouse + touch handler

## Buktatók

- iOS Safari `touch-action: none` mellett is engedi a 2-finger pinch-zoom-ot — ezt külön kell elnyomni `gesturestart` listener-rel
- Tailwind `overflow-hidden` + `sticky` parent → a sticky overlap-elhet a viewport-on (ld. [[react-onwheel-passive-default]] sibling pattern memory)
- Scale-snap (pl. 1.0×-hez közeli értéknél auto-snap) **kerülendő** — UX-zavar, hirtelen ugrás

## Kapcsolódó

- [[../08-Sessions/2026-05-12-kgc-robbantott-bra|Robbantott-bra session]]
- [[../02-Projects/robbantott-kereso|robbantott-kereso projekt]]
- [[multi-figure-parts-list-pattern]] — sibling pattern ugyanabból a projektből
- [[parts-table-vs-figure-page-detection]]
- [[nextjs-server-component-in-client-tree]] — React client-tree gotcha context
