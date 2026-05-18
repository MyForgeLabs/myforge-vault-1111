---
name: Touch-kiosk idle timeout
description: Mennyi idő után térjen vissza idle-screen-hez egy érintőképernyős kioszk — minimum 3 perc, mert date-picker / virtuális billentyűzet miatt a fókusz "elveszhet"
type: wiki
created: 2026-05-08
updated: 2026-05-08
tags: ["#topic/ux", "#topic/kiosk", "#topic/touch"]
---

# Touch-kiosk idle timeout

## TL;DR

Érintőképernyős kioszk (totem, signage, in-store self-service) state machine-jénél az **idle-back timer minimumát 3 percben** érdemes meghúzni — **NEM 60 másodpercben**, ahogy egy desktop screensaver tenné.

```ts
const IDLE_TIMEOUT_MS = 3 * 60 * 1000  // 3 perc
```

## Miért

A user "tétlenséget" mutat akkor is, amikor **aktívan használja** a kiosk-ot:

| Scenario | Mit lát az event-handler |
|---|---|
| Date-picker megnyitva, user 3 dátumot próbál ki, mielőtt klikkelne | Semmi `click`/`touchstart` a saját DOM-on — a date-picker overlay önálló subtree |
| Virtuális billentyűzet 2-3 betűs név begépelése + "ezt akarja?" hezitálás | 8-12 sec szünet keystroke-ok között |
| Telefonszám-formátum elgondolkodás (06 vs +36, "kéne-e space?") | 15-20 sec stuck |
| Szülő gyereket lök odébb a kioszk elől, közben browse-mode-ban van | 1-2 perc látszólagos idle |

**60 másodperces timeout** mindegyiket vissza-resetteli kezdő-képernyőre — a user dühös, mert "elvette tőle a foglalást".

## Mi resettelje a timer-t

Nem csak a `click`/`touchstart`. Minden user-interakció:

```ts
const events = ["touchstart", "touchmove", "mousedown", "keydown", "scroll"]
events.forEach(e => window.addEventListener(e, resetIdleTimer, { passive: true }))
```

A `keydown` kritikus a virtuális billentyűzethez: a billentyű `<button>`-ok `onClick` event-je nem feltétlenül jut el a window-ig (`stopPropagation` lehet bennük), de a `click`-eket DEBOUNCE-olja a 3min timer újraindítása. **Inkább a focus-event-eket figyeld:**

```ts
window.addEventListener("focusin", resetIdleTimer)   // input/keyboard interaction
window.addEventListener("pointerdown", resetIdleTimer) // touch + mouse
```

## State-tranzíciók példa (KGC Totem)

```
idle  ──tap──▶  browse  ──tap-machine──▶  detail  ──"Foglalom"──▶  form  ──submit──▶  confirmed
  ▲              │                          │                       │                    │
  └──────────────┴──── 3 min idle ──────────┴───────────────────────┴────────────────────┘
                          (vagy "Mégse" gomb)                                    (10s után auto)
```

A `confirmed` state-nek **rövid auto-timeout** legyen (10 sec) — a "Köszönjük, a foglalása felvéve" képernyő nem akar ott maradni 3 percig.

## Ne ezeket csináld

- **NE** úgy resetteld a timer-t hogy `setTimeout` minden state-váltáskor újraindul — race-condition: ha `useEffect` cleanup nem fut le rendesen, dupla timer fut → 1.5x sebességű idle-jump.
- **NE** állítsd 5+ percre — a következő user már odamegy a kiosk-hoz, és látja az előző bookin-form felénél, "ez mi?".
- **NE** felejtsd el a `confirmed` screen-en megállítani a 3 min timer-t — különben az auto-redirect után a `confirmed → idle` resetel, de utána még jön egy 3-min-late `idle → idle`, ami első ránézésre furcsa loop.

## Origin

KGC-Bérlés totem oszlopok (Tizen Samsung 1080×1920, 2 db: bejárat + pult), 2026-05-06. Eredetileg 60s, Peti megfigyelte hogy a date-picker használat közben a kiosk "elveszi" tőle a választott dátumot — átemelve `3 * 60 * 1000` ms-ra.

## Forrás

- Implementáció: `/root/projektjeim/KGC-ALL/kgc-berles/components/totem/TotemLayout.tsx`
- Session: [[08-Sessions/2026-05-06-kgc-weboldal]]
