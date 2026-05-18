---
name: Foxxi performance audit (2026-05-10)
type: audit
project: foxxi
created: 2026-05-10
tags: ["#type/audit", "#project/foxxi", "#performance"]
---

# Foxxi staging — performance audit (2026-05-10)

> **URL audited**: `https://mediumseagreen-eagle-536843.hostingersite.com/fogaszat/?nocache=perfaudit`
> **Eszköz**: Chrome DevTools MCP performance trace + Lighthouse insights
> **Eszköz-csatlakozás**: desktop, no throttling

## Core Web Vitals

| Metrika | Érték | Threshold | Status |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | **2274 ms** | <2500 ms (jó) | 🟢 Borderline |
| **CLS** (Cumulative Layout Shift) | **0.09** | <0.1 (jó) | 🟢 Jó |
| **TTFB** (Time to First Byte) | **1125 ms** | <600 ms (jó) | 🔴 **LASSÚ** |

**Megfigyelés**: Az LCP 2274 ms-ja akkor *borderline jó* (2.5s alatti), ha asztali, throttling nélküli teszt. **Mobil 4G simulált throttling-on várhatóan 4-6s** — ennek a fő oka a TTFB.

## LCP-bontás (2274 ms = TTFB + Render delay)

| Fázis | Idő | %  |
|---|---|---|
| TTFB (server response) | 1125 ms | 49% |
| Load delay (LCP image discovery) | 16 ms | 1% |
| Load duration (image download) | 27 ms | 1% |
| **Render delay** (CSS+JS parsing+execution) | 1105 ms | 49% |

**A TTFB 1125 ms az igazi sárkány** — szerver-cache nem aktív vagy nem-effektív.
**A Render delay 1105 ms** — render-blocking CSS+JS (Elementor + WPML + Trustindex + Google Fonts).

## Top probléma-csomagok (Lighthouse insights)

### 🔴 1. DocumentLatency (1022 ms savings lehetséges)

A TTFB 1125 ms — szerver-side response. Lehetséges fix:

- **W3 Total Cache page-cache** ellenőrizés — most aktív de nem-effektív (Domi 2026-04-30 kérdezte: Redis-re próbál csatlakozni de Redis nincs shared hostingon)
- **LiteSpeed cache** — Hostinger natív, csak akkor aktív ha a plugin engedélyezett (jelenleg deactivated)
- **Text compression** (gzip/brotli) — valószínűleg már aktív Hostinger-en, de érdemes header-ellenőrzés
- **Reduce TTFB**: shared hosting limit; akár upgrade a Cloud-ra (de Domi nem fog)

### 🟡 2. RenderBlocking — sok blocking CSS/JS

82 network request, ebből kb. 25 render-blocking CSS+JS:
- `/wp-content/themes/foxy/dist/index.css` (foxxi téma alap)
- `/wp-content/uploads/elementor/css/post-{2224,2268,2273,2274}.css` (4 Elementor CSS)
- `/wp-content/plugins/elementor/assets/css/frontend.min.css`
- `/wp-content/plugins/foxxi-before-after-v331/assets/css/before-after.css`
- `/wp-content/plugins/foxxi-video-carousel/assets/css/video-carousel.css`
- WPML 2 CSS
- Google Fonts CSS

### 🔴 3. **404 hiba**: popup-maker block-library-style.css

```
GET /wp-content/plugins/popup-maker/dist/packages/block-library-style.css?ver=7424eb959f91acb8bbb2 [404]
```

A `popup-maker` plugin egy block-library CSS-re hivatkozik ami nem létezik. **Plugin update vagy deactivate megoldja.** A Foxxi nem használ popup-okat (Phase 5f-ben az 1753-as popup törölve), tehát **a popup-maker plugin teljesen deactivable**.

### 🟡 4. Cache Lifetime — javítható

A statikus assetek (CSS, JS, fonts) cache-headerei nem-optimálisak. Hostinger LiteSpeed automatikusan teszi, de a `?ver=` query-string miatt minden CSS-update minden látogatónál friss letöltést okoz.

### 🟡 5. Third Parties

| 3rd party | Hatás |
|---|---|
| `cdn.trustindex.io/loader.js` | Phase 15 inline embed után csak a fogaszat/fogszab home-on |
| `fonts.googleapis.com/css2` (Montserrat) | Render-blocking |
| `gstatic.com/firebasejs` | nem-azonosított, esetleg WPML vagy Cookiebot |

## Network request breakdown

- **82 total request** a fogászat home-on
- **30+ image** (AI-generált hero-bannerek + page-hero + service-card-ok)
- **25 CSS file**
- **15+ JS file**

## 🎯 Quick wins (Domi-input nélkül)

| Akció | Idő | Impakt |
|---|---|---|
| **Popup-maker plugin deactivate** (404 fix + ~50KB JS megtakarítás) | 5 perc | 🔴 magas |
| **W3 Total Cache page-cache state ellenőrzés** + Disk-cache fallback ha Redis nincs | 30 perc | 🔴 magas (TTFB 1125→500ms cél) |
| **LiteSpeed cache plugin AKTÍV-ra állítás** + minimal config | 1 óra | 🟡 közepes (Hostinger LiteSpeed-natív) |
| **Hero-image preload** `<link rel="preload" as="image">` a `foxxi-page-hero` widget LCP-képére | 1 óra | 🟡 közepes |
| **Google Fonts swap** — `display=swap` ellenőrzés | 15 perc | 🟢 alacsony |

## ⚠️ Major refactor (NEM most)

- **Elementor CSS-bundle reduction** — 4 db post-specific CSS + frontend.min.css összevonás (Elementor "Improved CSS Loading" experiment)
- **Image lazy-loading** — már aktív (Imagify), de Elementor `<img>` lazy attribute ellenőrzés

## Kapcsolódó

- [[02-Projects/foxxi]]
- [[02-Projects/foxxi-sprint-2026-05/foxxi-uzenet-2026-05-10-osszefoglalo]]
