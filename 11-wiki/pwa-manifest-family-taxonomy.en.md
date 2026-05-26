---
name: PWA-manifest family taxonomy
type: wiki
lang: en
translated_from: pwa-manifest-family-taxonomy
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/pwa, taxonomy, evergreen, frontend, manifest]
---

# PWA-manifest family taxonomy

> [!info] TL;DR
> PWA configuration spans many concepts (manifest fields + service-worker + iOS-specific HTML meta), but they form a small **manifest-field-level master reference**: every field has a meaning, when it is required, and platform-specific quirks.

## Cluster members

| Concept | Field/Function | Platforms |
|---|---|---|
| manifest name field | identity | Android/iOS/Desktop |
| manifest short_name | identity | Android home-screen |
| manifest start_url | navigation | all |
| manifest scope | navigation | all |
| manifest display | UI shell | all |
| manifest orientation | UI shell | Android |
| manifest background_color | splash | Android |
| manifest theme_color | shell | Android, iOS partial |
| manifest icon-192 purpose | icon | Android |
| manifest icon-512 purpose | icon | Android splash |
| PWA icon-512 | icon | Android splash |
| PWA icon-192 | icon | Android home-screen |
| PWA icons | icon | all |
| Android PWA install | install flow | Android |
| Offline-mode PWA | service-worker | all |
| PWA telephone install icon | iOS-specific | iOS |
| Next.js PWA shell | implementation | all |
| Next.js PWA shell pattern | implementation | all |

## The 5 manifest-field families

### 1. Identity fields
**Purpose:** OS distinguishes apps on the home screen.

| Field | Length | Note |
|---|---|---|
| `name` | unlimited | long name in splash/install dialog |
| `short_name` | 12 char | home-screen icon label (Android crops > 12) |
| `description` | — | install promo |

**Anti-pattern:** `short_name === name` when `name > 12 char` → Android truncates.

### 2. Navigation fields
**Purpose:** standalone shell — where to launch and what URL range to stay within.

| Field | Default | Note |
|---|---|---|
| `start_url` | `/` | opens after install. Add tracking: `?source=pwa` |
| `scope` | manifest-path | leaving this URL range brings back the browser chrome |

**Quirk:** if `scope = /app/` and a link points to `/blog/` → a browser tab opens, NOT in-app navigation. Users panic.

### 3. UI-shell fields
**Purpose:** standalone vs browser-chrome appearance.

| Field | Values | Meaning |
|---|---|---|
| `display` | `standalone`/`fullscreen`/`minimal-ui`/`browser` | iOS: `standalone` gives "add-to-homescreen" feel |
| `orientation` | `portrait`/`landscape`/`any` | Android locks, iOS does NOT honour |
| `theme_color` | hex | Android status bar; iOS partially via `<meta name="theme-color">` |
| `background_color` | hex | splash-screen color while JS boots; iOS does NOT use it |

### 4. Icon fields (most bugs here)
**Purpose:** install icon on Android/iOS.

**Min-set (Next.js PWA shell):**
```json
"icons": [
  { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
  { "src": "/icon-192-maskable.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
  { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
  { "src": "/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
]
```

**`purpose` field quirks:**
- `any` — normal icon
- `maskable` — Android **safe zone** (concentrate the logo in the central 80%)
- `monochrome` — Android themed icons

**iOS-specific (NOT in manifest!):**
```html
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-title" content="MyApp" />
```

### 5. Install-flow fields
**Purpose:** `beforeinstallprompt` event on Android, hand-rolled instructions on iOS.

- Android: Chrome dispatches the `beforeinstallprompt` event → custom install button
- iOS: NO install-prompt API; user must manually "Share → Add to Home Screen"
- `PWA telephone install icon` — iOS needs its own instruction UI

## Reusable PWA rules

1. **Next.js metadata API** preferred over **public/manifest.json** — type-safe, build-time fingerprint
2. **`apple-touch-icon` + `manifest.json` ALWAYS together** — iOS does NOT read manifest icons for home-screen
3. **Maskable + non-maskable icons both required** — otherwise Android draws a white frame
4. **`display: standalone` + `apple-mobile-web-app-capable`** ⇒ full-screen feel on both OSes
5. **Service-worker offline fallback** only when truly needed — otherwise cache-debug hell
6. **start_url with source tracking**: `start_url: "/?source=pwa"` → install rate measurable in analytics
7. **EAS Build vs PWA dilemma** — if push/biometrics/native-API are NOT needed, PWA is enough (Next.js PWA shell minimum)

## Anti-patterns

| Anti-pattern | Bug |
|---|---|
| `display: standalone` + missing `apple-mobile-web-app-capable` | iOS browser-chrome remains |
| Only `192x192` icon | Android splash looks for 512, default-white background |
| `scope` MISSING + multi-domain link | browser tab opens |
| `theme_color` in manifest + `<meta>` tag DIFFER | Android uses `<meta>` |
| `purpose: "maskable"` MISSING | Android adaptive icon has white frame |

## Related

- [[nextjs-pwa-shell-minimum]]
- [[fallback-pattern-family-taxonomy]] (Offline fallback)
