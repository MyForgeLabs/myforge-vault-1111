---
name: PWA-manifest család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/pwa, taxonomy, evergreen, frontend, manifest]
---

# PWA-manifest család taxonomy

> [!info] TL;DR
> A vault-ban **28 Concept** (16 PWA + 12 manifest) érinti a PWA-területet, és **csak 1 specific wiki** (`nextjs-pwa-shell-minimum`) van. Itt a **manifest-mező-szintű** mester-referencia: minden mező mit jelent, mikor szükséges, milyen platform-specifikus quirk-kel.

## Cluster-members

| Concept | Mező/Funkció | Platform-érintettség |
|---|---|---|
| manifest name field | identitás | Android/iOS/Desktop |
| manifest short_name | identitás | Android home-screen |
| manifest start_url | navigáció | minden |
| manifest scope | navigáció | minden |
| manifest display | UI-shell | minden |
| manifest orientation | UI-shell | Android |
| manifest background_color | splash | Android |
| manifest theme_color | shell | Android, iOS partial |
| manifest icon-192 purpose | ikon | Android |
| manifest icon-512 purpose | ikon | Android splash |
| PWA icon-512 | ikon | Android splash |
| PWA icon-192 | ikon | Android home-screen |
| PWA icons | ikon | minden |
| Android PWA install | install-flow | Android |
| Offline-mode PWA | service-worker | minden |
| PWA telephone install icon | iOS-specific | iOS |
| PWA architektúra | meta | — |
| Next.js PWA shell | implementáció | minden |
| Next.js PWA shell pattern | implementáció | minden |

## A 5 manifest-mező-család

### 1. Identitás-mezők
**Cél:** OS megkülönböztesse az app-okat a home-screen-en.

| Mező | Hossz | Megjegyzés |
|---|---|---|
| `name` | korlátlan | hosszú név splash/install-dialógban |
| `short_name` | 12 char | home-screen ikon felirat (Android crop-ol > 12) |
| `description` | — | install-promóciónál |

**Anti-pattern:** `short_name === name` ha `name > 12 char` → Android törli a végét.

### 2. Navigációs-mezők
**Cél:** standalone-shell hova-indít és milyen URL-tartományban marad.

| Mező | Default | Jegyzet |
|---|---|---|
| `start_url` | `/` | install után ez nyílik. Query-param-mal A/B-teszt: `?source=pwa` |
| `scope` | manifest-path | ezen kívüli URL-re menve a browser-chrome visszajön |

**Quirk:** ha `scope = /app/` és link `/blog/` → browser-tab nyílik, NEM in-app navigáció. Domi-szerű user-kupán pánikol.

### 3. UI-shell-mezők
**Cél:** standalone vs browser-chrome megjelenés.

| Mező | Értékek | Mit jelent |
|---|---|---|
| `display` | `standalone`/`fullscreen`/`minimal-ui`/`browser` | iOS-on `standalone` az „add-to-homescreen" feeling |
| `orientation` | `portrait`/`landscape`/`any` | Android lock-olja, iOS NEM tartja be |
| `theme_color` | hex | Android-status-bar; iOS részben `<meta name="theme-color">` kell |
| `background_color` | hex | splash-screen-color amíg JS bootol; iOS NEM használja |

### 4. Ikon-mezők (legtöbb hiba itt)
**Cél:** install-ikon Android/iOS-en.

**Min-set (Next.js PWA shell):**
```json
"icons": [
  { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
  { "src": "/icon-192-maskable.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
  { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
  { "src": "/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
]
```

**`purpose` mező quirk:**
- `any` — normál ikon
- `maskable` — Android **safe-zone** (80% középre koncentráld a logót)
- `monochrome` — Android themed-icons

**iOS-specific (NEM manifest-ben!):**
```html
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-title" content="MyApp" />
```

### 5. Install-flow-mezők
**Cél:** `beforeinstallprompt` event Android-on, iOS-en hand-roll-instrukció.

- Android: Chrome dispatch-eli a `beforeinstallprompt` event-et → custom install-gomb
- iOS: NINCS install-prompt API; user-nek manuálisan kell „Share → Add to Home Screen"
- `PWA telephone install icon` — iOS-en saját instrukció-UI kell

## Reusable PWA-szabályok

1. **Next.js metadata-API** előnyben **public/manifest.json** előtt — type-safe, build-time-fingerprint
2. **`apple-touch-icon` + `manifest.json` MINDIG együtt** — iOS NEM olvas manifest-icon-ből home-screen ikont
3. **Maskable + non-maskable ikon mindkettő kell** — Android különben fehér-keret-rajzol
4. **`display: standalone` + `apple-mobile-web-app-capable`** ⇒ full-screen feel mindkét OS-en
5. **Service-worker offline-fallback** csak ha tényleg kell — különben cache-debug-pokol
6. **start_url-be source-tracking**: `start_url: "/?source=pwa"` → analytics-ben mérheted az install-rate-et
7. **EAS Build vs PWA dilemma** — ha NEM kell push/biometrics/native-API, PWA bőven elég (Next.js PWA shell minimum)

## Anti-pattern

| Anti-pattern | Hiba |
|---|---|
| `display: standalone` + `apple-mobile-web-app-capable` HIÁNYZIK | iOS browser-chrome marad |
| Csak `192x192` ikon | Android splash 512-t keres, default-fehér háttér |
| `scope` HIÁNYZIK + multi-domain link | browser-tab nyílik |
| `theme_color` manifest-ben + `<meta>` tag-ben DIFF | Android `<meta>`-t használja |
| `purpose: "maskable"` HIÁNYZIK | Android Adaptive Icon fehér-keretű |

## Kapcsolódó

- [[nextjs-pwa-shell-minimum]]
- [[fallback-pattern-family-taxonomy]] (Offline fallback)
