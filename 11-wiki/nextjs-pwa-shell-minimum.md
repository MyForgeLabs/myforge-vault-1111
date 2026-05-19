---
name: nextjs-pwa-shell-minimum
description: A "natívnak érződő" mobil-app PWA-shell minimuma egy Next.js app-on — manifest.webmanifest + apple-touch-icon + appleWebApp meta + theme-color → Add to Home Screen full-screen ikonnal
metadata:
  type: project
created: 2026-05-12
updated: 2026-05-19
tags: ["#type/reference", "#tech/nextjs"]
tag_backfill: 2026-05-19
---
# Next.js PWA-shell minimum

A "telepíthető, app-szerű" élmény (saját ikonos, full-screen, address-bar nélküli) NEM kell EAS Build / TestFlight / Play Store / App Store-t. Egy Next.js web-app **5 perc** alatt PWA-shell-é alakítható, és iOS Safari "Hozzáadás a kezdőképernyőhöz" / Android Chrome "Telepítés" után **95%-ban "native-feeling"** lesz egy bemutatóra.

## Mikor érdemes

- Bemutató holnapra van, ahol fontos hogy a vendég/ügyfél "letöltse az appot" érzést kapjon
- A funkcionalitásban nincs olyan gesture-igény / haptic / push notification / native sensor (HealthKit, Bluetooth) amit a webnél nem érsz el
- A backend és a web-UI már él, csak a "csomagolás" hiányzik

## Ha EAS / App Store kell

- Push notification (web-push limitált iOS-en)
- Native gesture-ek (swipe-back, edge-detection)
- Native haptic engine (`expo-haptics`)
- HealthKit / CoreMotion / kamera / Bluetooth közvetlen access
- IAP (StoreKit / Google Play Billing)

## A minimum recept (Next.js 15+/16, App Router)

### 1. PWA ikonok generálása

ImageMagick-kel 5 perc alatt egy színes háttér + monogram + brand-felirat:

```bash
mkdir -p apps/<app>/public

# 512x512 forrás (forest-zöld háttér + arany "B" + sage-zöld felirat)
convert -size 512x512 xc:"#2d3e2f" \
  -gravity center -fill "#c9a955" \
  -font DejaVu-Sans-Bold -pointsize 280 -annotate +0-20 "B" \
  -fill "#7a9b7e" -pointsize 60 -annotate +0+160 "balance" \
  apps/<app>/public/icon-512.png

convert apps/<app>/public/icon-512.png -resize 192x192 apps/<app>/public/icon-192.png
convert apps/<app>/public/icon-512.png -resize 180x180 apps/<app>/public/apple-touch-icon.png
convert apps/<app>/public/icon-512.png -resize 64x64 apps/<app>/public/favicon.ico
```

Brand-konzisztens design: a `tokens.css` `--forest` / `--gold` / `--sage` változókat használd háttérre / fő-elemre / kiegészítő szövegre.

### 2. `manifest.webmanifest`

```json
{
  "name": "Balance — Wellbeing 2.0",
  "short_name": "Balance",
  "description": "Jólléti tárca, ROI dashboard, 4 dimenzió.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#f5f1ea",
  "theme_color": "#2d3e2f",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ]
}
```

A `display: "standalone"` adja a "full-screen, address-bar nélkül" élményt. `theme_color` az iOS status-bar színe lesz (világos témánál sötét-zöld, kontraszt).

### 3. Layout metadata

```tsx
// app/layout.tsx
import type { Metadata, Viewport } from 'next';

export const metadata: Metadata = {
  title: 'Balance — Wellbeing 2.0',
  description: 'Jólléti tárca, ROI dashboard.',
  manifest: '/manifest.webmanifest',
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
    ],
    apple: '/apple-touch-icon.png',
  },
  appleWebApp: {
    capable: true,
    title: 'Balance',         // home-screen alatti felirat
    statusBarStyle: 'black-translucent',
  },
};

export const viewport: Viewport = {
  themeColor: '#2d3e2f',
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',     // notch / dynamic-island safe-area-ok kihasználása
};
```

A `appleWebApp.title` az iOS "Hozzáadás" dialógus default-szövege lesz.

### 4. Verifikáció

```bash
curl -sI https://your-app/manifest.webmanifest  # 200 OK
curl -sI https://your-app/apple-touch-icon.png  # 200 OK

# Chrome DevTools — Application tab > Manifest: van-e installable marker
```

## Buktatók

- **Static export-nál a manifest path-ja `output.basePath`-tel kerülhet kollízióba.** Verifikáld curl-lel hogy a teljes URL elérhető.
- **iOS NEM tölti le a manifest-et "Hozzáadás" előtt, csak az apple-touch-icon-t és a meta-tageket.** Tehát a `manifest.webmanifest` lényegében csak Androidot szolgálja; iOS-en a `appleWebApp.*` meta-tagek + `apple-touch-icon` PNG-je adja az élményt. Mindkettő kell.
- **Bookmark vs Home Screen elnevezés:** iOS Safari "Add to Home Screen" — Android Chrome "Telepítés" / "Add to home screen". Multi-platform doc-ban használd a "Hozzáadás a kezdőképernyőhöz" magyar megfogalmazást.
- **HTTPS kötelező** — `manifest.webmanifest` és service worker is csak HTTPS-en él (localhost is OK dev-re).
- **Service worker NEM kell** az alap "telepíthető" élményhez. Csak offline-mode-hoz. Ha kell, használj `next-pwa`-t vagy a Next.js 16+ beépített `@next/pwa`-t.
- **App-shell-szerű layout**: a bottom-nav (`/`/`/jutalombolt`/stb.) sticky-positioned div-kel — `position: sticky; bottom: 0` + `padding-bottom: env(safe-area-inset-bottom)` a iPhone notch / dynamic-island miatt.

## Mit nyersz vs natív Expo build

| | PWA-shell | Expo native (EAS Build) |
|---|---|---|
| Telepítés idő (user-oldalon) | 10 sec ("Add to Home Screen") | 5-10 perc App Store/Play letöltés |
| Backend deploy | 5 perc kód-write | 1-2 hét App Store review (review fee, dev account) |
| App-ikon, full-screen | ✅ | ✅ |
| Push notification | ⚠️ csak Android, iOS limitált | ✅ |
| Native gesture / haptic | ❌ | ✅ |
| HealthKit / Bluetooth | ❌ | ✅ |
| Demo-pitch impact | "telepítettük az appot!" | "letöltöttük az appot!" |
| Cost / time | $0 / 5 perc | $99/év Apple + $25 Google + 1-2 hét |

## Példa a kódban

A Kinda Balance app (`/root/projektjeim/kinda/apps/balance/`) — commit `d5f7704`. `apps/balance/public/` + `apps/balance/app/layout.tsx`.

## Kapcsolódó

- [[02-Projects/teszt-eu]] — a Balance Wellbeing app PWA-shell-je
- Demo session: `08-Sessions/2026-05-11-kinda-project-2.md`
