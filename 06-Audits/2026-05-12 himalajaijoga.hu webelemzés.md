---
name: 2026-05-12-himalajaijoga-webelemzes
type: audit
target: https://himalajaijoga.hu/
target-type: website
audit-axes: [seo, a11y, performance, ux, conversion, stack]
created: 2026-05-12
updated: 2026-05-19
tags: ["#type/audit", "#audit/seo", "#tech/wordpress"]
tag_backfill: 2026-05-19
---
# Webelemzés — himalajaijoga.hu

> [!info] Kontextus
> A Himalájai Jóga Meditáció Közhasznú Egyesület honlapja. Tradicionális jóga + meditáció oktatás, kurzusok, webshop (könyvek + ruházat), órarend. WordPress + WooCommerce + LearnPress stack. Audit eszközök: Chrome DevTools Lighthouse (mobile, navigation), WebFetch content, curl headers, plugin-fingerprint.

## TL;DR — Top 5 sürgős teendő

1. **P0 SEO — meta description hiányzik a homepage-en**. Lighthouse hibára vág, klikkesedés a Google találati listáról emiatt alacsony. → Yoast SEO / Rank Math telepítése + per-page leírás. **1-2 óra munka.**
2. **P0 SEO — title duplikálva**: `Himalájai Jóga Tradíció – Himalájai Jóga Tradíció`. SEO + UX szempontból kínos. → WordPress beállítások → site title vs. tagline + SEO plugin template.
3. **P1 A11y — nincs `<main>` landmark, link-name hiányok, kontraszt-hibák**. Screen reader felhasználóknak + Google a11y-ranking-faktornak rossz.
4. **P1 Performance — Revolution Slider + image-size-responsive FAIL + plugin-duplikáció** (2 newsletter, 2 form). Mobile CWV szenved.
5. **P1 Konverzió — semmi lead magnet, nincs "Próbálj egy órát ingyen", obfuszkált telefonszám**. Az érdeklődő nem tud egyszerűen elköteleződni.

## Lighthouse audit (mobile, navigation)

| Kategória | Pontszám | Megjegyzés |
|---|---|---|
| Accessibility | **91** | jó alap, 4 javítható issue |
| Best Practices | **69** | console errors + deprecated API + responsive images |
| SEO | **85** | meta description hiánya viszi le |
| Agentic Browsing | **43** | AI agent-ekkel nehezen feldolgozható (a11y-tree malformed) |

Beágyazott report: `/tmp/lh-himalajaijoga-mobile/report.html`

## Tech stack (plugin-fingerprint)

| Réteg | Megoldás |
|---|---|
| Hosting | Apache (saját szerver, nincs CDN — `cf-ray` nincs) |
| CMS | WordPress |
| Téma | **Goodlayers Core** (`goodlayers-core`) |
| E-commerce | WooCommerce + Woo Product Bundle |
| Tanfolyam | **LearnPress** |
| Slider | **Revolution Slider** ⚠️ |
| Form | **WPForms ÉS Contact Form 7** ⚠️ duplikálva |
| Newsletter | **Mailchimp for WP ÉS Newsletter plugin** ⚠️ duplikálva |
| Térkép | WP Google Map Plugin |
| Órarend | MP Timetable |
| Szállítás HU | FoxPost-WC + Hungarian Pickup Points |
| Számlázás | Számlázz.hu integráció |
| Analytics | Google Site Kit |
| Extra | Jetpack ⚠️ (nehéz) |
| Fizetés | OTP SimplePay |

## SEO findings

### P0 — kritikus

- **Nincs meta description** (Lighthouse `meta-description: 0`). Csak `<meta name="robots" content="max-image-preview:large">` van. → Yoast SEO / Rank Math telepítése után minden fontos oldalra egyedi 140-160 karakteres leírás.
- **Title duplikálva**: `Himalájai Jóga Tradíció – Himalájai Jóga Tradíció`. WordPress Settings → General → Site Title + Tagline + SEO plugin template (`%%page_title%% | %%sitename%%`).
- **Links not crawlable** (Lighthouse `crawlable-anchors: 0`) — JS-injected linkek nem crawlable. Hero slider gomb-jai `href` nélkül vannak.

### P1

- Sitemap OK: `https://himalajaijoga.hu/wp-sitemap.xml` (WP default).
- Robots OK + szépen Disallow-olja a WooCommerce-pattern-eket.
- **`/sitemap.xml` 301-redirect-el, de `/sitemap_index.xml` 404** → Google Search Console-ban csak a `wp-sitemap.xml` legyen submitted.
- **OG / Twitter meta-ek hiányoznak** → social-share preview rossz.
- Schema.org strukturált adat (Organization, NonprofitOrganization, Course) hiányzik. Az egyesület + tanfolyam-rendszer miatt **erős nyereség** lenne.

## A11y findings (Lighthouse)

| Issue | Score | Hatás |
|---|---|---|
| `color-contrast` | 0 | szöveg-bg kontraszt < 4.5:1, részben az aranyszín-CTA-k |
| `landmark-one-main` | 0 | nincs `<main>` element → screen reader nem tud "main content"-re ugrani |
| `link-name` | 0 | ikon-linkek (social) `aria-label` nélkül |
| `label-content-name-mismatch` | 0 | gomb-szöveg ≠ aria-label |
| `agent-accessibility-tree` | 0 | a11y-tree nem well-formed (összefügg a felsőkkel) |

→ goodlayers téma footer.php / header.php: wrapping `<main role="main">`, ikon-linkek `aria-label="..."`, kontraszt-pár hex-szín emelése Customizer-ben.

## Performance findings

- **`image-size-responsive: 0`** — túl alacsony felbontású képeket szolgál ki nagyméretű viewport-okon. Lazy-load + `srcset` + WebP konverzió kell. (Plugin: ShortPixel / Imagify, vagy Hostinger LSCACHE image optimization, vagy Cloudflare Polish.)
- **CLS 0.117** (gyenge — 0.1 alatt kell). Hero slider + WooCommerce-mini-cart fontos LCP-elem CLS-be sodorja az under-fold-ot.
- **Revolution Slider** köztudottan a Core Web Vitals legnagyobb áldozata WP-n. Modern alternatíva: Swiper.js custom block, vagy egyszerűen statikus hero + CSS-animáció.
- **Plugin-konszolidáció**: 2 newsletter + 2 form = 4 plugin helyett 1+1 (Mailchimp + WPForms maradhat). Jetpack — gyakran kapcsoljuk ki és csak a Jetpack Boost-ot tartjuk meg.
- Console error: `ERR_FAILED` 4x — egy resource (külső skript?) nem töltődik be.

## UX / Konverziós findings

### Konverziós lyukak

- **Nincs lead magnet**. Csak hírlevél-feliratkozás van. **Erős javaslat:**
  - "Ingyenes 7 napos meditáció minibevezető PDF" (Mailchimp double-opt-in)
  - "Próbálj egy bevezető online órát ingyen" (LearnPress free-course)
  - "Mantrák és imák zip-letöltés"
- **Hero CTA gyenge**. „Bővebben" → Tradíció-oldal. Ez **információs**, nem **akció**. Inkább: "Jelentkezz az alaptanfolyamra (szept. 19-től)" vagy "Foglalj egy próbaórát".
- **Telefonszám obfuszkált** (`+36 30 579 8382`) anti-spam okból, **de nincs click-to-call** mobilon → `<a href="tel:+36305798382">`.
- **Email is obfuszkált** `info[kukac]himalajaijoga.hu` — érthető, **de** legalább JS-base64-encoded mailto-link, mert így senki nem fog rákattintani.
- A homepage **túl sok szekció** (slider + 12 program + about + 16+ termék + inspirációk + newsletter). **Fókusz-veszítés**. Strukturált információs hierarchia kell, F-vagy Z-pattern.

### Trust & social proof

- **Nincsenek testimoniál-ek** ("X év óta gyakorolok itt", "Az alaptanfolyam után megváltozott…"). A "Tanáraink" oldal van, de testimonial-kártyák a homepage-en hiányoznak — nagyon **erős hatású** lenne egy spirituális közösségnél.
- Trust signal mind a footer-ben elrejtve: közhasznú státusz, bírósági nyilvántartás. Ezt **a homepage hero-szekcióban** kellene mini-badge-ekkel kiemelni („közhasznú egyesület", „X éves tradíció", „X tanár").

### Mobil UX

- Hamburger menü + slider — mobil viewport (390×844) képernyőn ránézésre OK (lásd `assets/himalajaijoga-mobile.png`), de **a hero slide-szöveg túl sűrű**.
- **Footer telefonszám nem klikkelhető** mobilon.

## Tartalom-elemzés

| Erősség | Gyengeség |
|---|---|
| Erős küldetésnyilatkozat | Nincs cselekvésre szólító CTA hero-ban |
| Mély tradíció-tartalom (Guru vonal, beavatás) | Túl szerteágazó, nincs single primary user-flow |
| Webshop integrálva | Webshop-blokk a homepage-en zsúfolt, 16 termék-card |
| LearnPress alaptanfolyam (szept 19-től) | A "Tanárképző betelt" → érdeklődést frusztrál (várólista CTA kellene) |
| Egyesületi társadalmi misszió | Hiányzik "X év óta", "X tanítvány", konkrét számok |

## Action plan (prioritized)

### Quick wins — 1 nap alatt megcsinálható
- [ ] Yoast SEO vagy Rank Math telepítése + meta description-ök minden top-page-en
- [ ] Title-template javítása (Settings → General → Tagline tisztázás)
- [ ] OG image beállítása (1200×630, brand-logó + Himalája-háttér)
- [ ] `<main>` landmark hozzáadása a témához (vagy SEO/Accessibility plugin)
- [ ] Click-to-call telefonszám a header + footer minden példányán
- [ ] Sitemap submit a Google Search Console-ba

### Sprint 1 — 3-5 nap
- [ ] Lead magnet PDF (7 napos meditáció minibevezető) + Mailchimp dupla-opt-in flow
- [ ] Hero CTA átfogalmazás: "Foglalj próbaórát" / "Jelentkezz az alaptanfolyamra"
- [ ] Testimonial-szekció hero alatt (3-5 fő, fotó + 2 mondat)
- [ ] Trust badge-ek (közhasznú, X éve működik, X tanár)
- [ ] Revolution Slider lecserélése Swiper.js-blokkra (vagy statikus hero)
- [ ] Plugin-konszolidáció: 1 newsletter + 1 form plugin
- [ ] Képek WebP-konverzió + lazy-loading

### Sprint 2 — 1-2 hét
- [ ] Schema.org markup: Organization + NonprofitOrganization + Course + Product
- [ ] Foglalási widget direktben az órarend-oldalra
- [ ] Tanár-profil kártyák a homepage-en
- [ ] Featured-course slot ("Most induló kurzusok") a fold fölött

## Kapcsolódó

- [[06-Audits/Index]]
- [[06-Audits/2026-05-12 nonplusz.hu-basic webelemzés]] — egyidejű audit
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — ha competitor research is kell ehhez

## Mellékletek

- Desktop screenshot: `assets/himalajaijoga-desktop.png`
- Mobile screenshot: `assets/himalajaijoga-mobile.png`
- Lighthouse mobile report: `/tmp/lh-himalajaijoga-mobile/report.html`
