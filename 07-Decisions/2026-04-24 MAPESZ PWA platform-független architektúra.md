---
name: MAPESZ PWA platform-független architektúra
title: MAPESZ — PWA platform-független architektúra
type: adr
status: accepted
created: 2026-04-24
updated: 2026-04-24
project: mapesz
tags: [decision, architecture, pwa, mapesz]
---

# ADR: MAPESZ platform-független PWA

## Kontextus

A [[02-Projects/mapesz]] projekt jelenlegi artifact-jai (product-brief.md, architecture-design.md, prd.md, ux-design.md, 2026-03-31 körüli dátummal) a következő megközelítést tükrözték:

- **Web-first** Next.js 16 (App Router, SSR+SSG) — admin portál, klub portál, versenyző portál, publikus oldal
- **Mobil**: csak *mobile-first responsive web*, dedikált natív app **nem** szerepelt
- **PWA** csak a **4. fejlesztési fázisban** jelent meg, mint "fejlett funkció" — offline, push, digitális tagsági kártya

Viszont a versenyző-használati esetek közül sok **mobile-native jellegű**:
- Élő eredményrögzítés a helyszínen (gyakran gyenge internetkapcsolat)
- Digitális versenyengedély QR-kóddal (offline kellhet belépéskor)
- Push értesítés sorsoláskor, rajtlistakor, eredményhirdetéskor
- Klubkereső / játékoskereső térkép → geolokáció

**2026-04-24, session "mapesz":** a user (Peti) explicit döntést hozott: **"ezt is találjuk ki, jó lenne PWA platform-független"**. Natív iOS/Android app fejlesztése és karbantartása **nem** életképes a ~200-500 fős versenyzői közösség méretére — egyetlen kódbázis kell, ami telefonra installálható.

## Döntés

**A MAPESZ platform egyetlen Next.js 16-os PWA lesz**, ami:

1. **Responsive web-appként** fut böngészőben (publikus oldalak, admin/klub portál desktopon)
2. **Telepíthető mobilra** (Android: Chrome "add to home screen" / iOS: Safari share sheet)
3. **Szerep-alapú routing** ugyanazon a kódbázison: `/` landing → `/versenyzo` → `/klub` → `/admin`
4. **Offline-képes** service worker + cache stratégia a kritikus utakra (versenyengedély QR, versenynaptár, saját ranglista, legutóbbi események)
5. **Push értesítés** Web Push API-n keresztül (VAPID) — nem kell FCM/APNs natív réteg
6. **Nincs külön mobil repó / Expo / React Native** — zero platform-divergence

## Következmények

### ✅ Pozitív
- **1 kódbázis** = karbantartási költség ~harmadára csökken
- **Gyorsabb MVP**: a BMAD 4. fázis PWA-ja előrébb kerül az alap architektúrába
- **Olcsóbb hosting**: nincs app store deployment, review, natív build pipeline
- **SEO + discoverability megmarad** — a web-rétegen minden URL publikusan indexelhető
- **Push notif díjmentes** (saját VAPID server, Web Push)
- **Design konzisztencia** — ugyanaz a token-rendszer és komponens-készlet minden platformon

### ⚠️ Negatív / kockázat
- **iOS push korlát**: Web Push iOS-en csak Safari 16.4+ és *csak telepített* PWA-ban működik — a user-nek tudnia kell hogy telepítenie kell
- **App Store jelenlét hiánya** — ha marketing szempontból fontos lesz a "keress meg minket az App Store-ban", utólag kell (pl. PWA-Bubblewrap Android, Capacitor iOS wrapper)
- **Background sync korlátok** — iOS Safari nem támogat background syncet, így az offline-eredményrögzítés csak akkor szinkronizál amikor az app újra nyitva van
- **Service worker debug-nehézség** — development-ben jellemző caching-problémák, kell disciplin (stale-while-revalidate vs cache-first stratégiák világosan dokumentálva)

### 🔁 Semleges / változatlanul marad
- **Prisma / Postgres backend** változatlan — az API route-ok ugyanúgy működnek
- **NSR integráció / Számlázz.hu / SimplePay** — szerveroldali, nem érinti
- **Auth** — NextAuth megmarad, csak a session-cookie-t a service worker-nek is látnia kell
- **SEO** — SSG + ISR rétegen megmarad a landing, szövetségi oldalak, versenynaptár

## Implementációs kötelezvények

A D-Design-System létrehozásakor és a frontend-design skill bemeneténél az alábbi PWA-követelmények **first-class polgárok**, nem utólagos réteg:

1. **App manifest** (`public/manifest.webmanifest`) — name, short_name, icons (192/512 maskable + any), theme_color, background_color, display: standalone, start_url, scope
2. **Service worker** — workbox vagy next-pwa alapon, prekocsizandó route-ok listája a `D-Design-System`-ben lesz
3. **Install prompt UX** — `beforeinstallprompt` event saját CTA-val (pl. versenyző dashboard tetején "Telepítsd a mapesz appot!")
4. **Offline fallback oldal** (`/offline` route már létezik a [src/app/offline/](MAPESZ/web/src/app/offline))
5. **Splash screen** ikonok iOS-hez (külön `apple-touch-icon` + iOS-specific splash képek)
6. **Push értesítés permission-flow**: opt-in UX versenyző dashboardon, nem automatikusan a landing-en
7. **Tokenek reszponzív minimumai**: touch-target 44×44 iOS / 48×48 Android (ui-ux-pro-max kötelező szabály)
8. **Safe-area-inset** támogatás (iPhone notch, Android gesture bar)

## Alternatívák amiket NEM választunk

- **React Native / Expo**: külön kódbázis, külön store deployment, ~2x fejlesztési idő — a 200-500 fős közönségre overkill
- **Capacitor / PWA-Bubblewrap store-ba**: jelenleg nem kell, de későbbi opció marad (nem zárjuk ki)
- **Csak reszponzív weboldal PWA nélkül**: elveszítjük az offline QR-versenyengedélyt és a push-t, ami jelentős versenyelőny

## Kapcsolódás

- A meglévő [architecture-design.md](MAPESZ/design-artifacts/G-Product-Development/architecture-design.md) "9. Deployment" szekcióját **update-elni kell** hogy a service worker + manifest rész kerüljön az indulási MVP-be (nem a 4. fázisba)
- A [prd.md](MAPESZ/design-artifacts/E-PRD/prd.md) "Fázis 1: MVP" epic-jébe beemelendő: `F14: PWA alapok (manifest, SW, install prompt, offline fallback)`
- A készülő [[02-Projects/mapesz]] fájlban ez mint **aktív architekturális irány** jelölendő

## Felülvizsgálat

**Felülvizsgálat indokolt, ha:**
- Kritikus versenyzői panasz érkezik iOS push-ra (2-3 eset felett → Capacitor wrapper-t vizsgálunk)
- App Store jelenlét marketingelőnyt jelent egy nagyobb szponzori körben
- Background-sync hiánya mérhető adatvesztést okoz offline eredményrögzítésnél
