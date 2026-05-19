---
name: shopify-yoast-dupla-og
type: wiki
created: 2026-05-12
updated: 2026-05-19
tags: ["#type/reference", "#audit/seo"]
tag_backfill: 2026-05-19
---
# Shopify default + Yoast Shopify dupla OG description tag konfliktus

Tipikus konfiguráció-hiba **Yoast SEO for Shopify app**-pal: az alap Shopify-theme Liquid template-jei (`theme.liquid`, `collection.liquid`) **saját** OG / Twitter meta-tag-eket renderelnek, és a Yoast app **fölülírja** őket — de NEM törli az eredetit. Eredmény: **két `<meta property="og:description">`** a `<head>`-ben.

## Tünet

```html
<head>
  <!-- Shopify default (theme.liquid render) -->
  <meta property="og:description" content="A BASIC kollekció a legnépszerűbb szezonális alapdarabjaink gyűjteménye…">
  
  <!-- Yoast Shopify saját -->
  <meta property="og:description" content="Fedezd fel a NONPLUS BASIC kollekció időtálló darabjait!" />
</head>
```

A Shopify default-ja a teljes collection-leírást levágja **200 karakternél középen** (pl. nonplusz: `"Mindezek melle"` szóban vágódik). A Yoast saját stringje rövidebb, marketing-orientált.

## Hatás

- **Facebook share preview** non-determinisztikus — vagy a Shopify-default-ot olvassa be (csonka mondat → kínos), vagy a Yoast-osat
- **Twitter / X share preview** ugyanaz
- **LinkedIn share** = általában a Shopify-default-ot olvassa elsőként
- Lighthouse audit nem jelzi (mert mindkét tag valid)

## Fix

### 1. Yoast Shopify app oldali toggle

App settings → "Disable native Shopify SEO tags" (ne overlap-eljünk):
- Bekapcsolva: Yoast átveszi az összes meta-tag render-t, a Shopify-default Liquid-block kikapcsol
- Nem minden téma kompatibilis (Yoast doksi szerint Dawn, Sense, Studio, Refresh OK)

### 2. Theme.liquid manuális edit (ha az 1. nem elég)

A `theme.liquid` `<head>` szekciójában meg kell keresni a Shopify-default OG-block-ot:

```liquid
{%- if template == 'collection' -%}
  <meta property="og:description" content="{{ collection.description | strip_html | truncate: 200 }}">
{%- endif -%}
```

És vagy törölni, vagy guard-olni:

```liquid
{%- unless settings.yoast_enabled -%}
  <meta property="og:description" content="{{ collection.description | strip_html | truncate: 200 }}">
{%- endunless -%}
```

### 3. Sanity-check curl-lal

```bash
curl -s -A "Mozilla/5.0" https://example.myshopify.com/collections/basic | grep -ic 'og:description'
# Helyes: 1
# Hibás: 2 vagy több
```

## Ahonnan a tudás jött

- [[06-Audits/2026-05-12 nonplusz.hu-basic webelemzés]] — `nonplusz.hu/collections/basic` audit, 2026-05-12.
  - Shopify default tag: `"A BASIC kollekció a legnépszerűbb szezonális alapdarabjaink gyűjteménye, amely a kényelmet kereső, minőségi és fenntartható divat szerelmeseinek szól. A ruháink és kiegészítőink kiváló minőségű, hosszú élettartamot garantáló alapanyagokból készülnek, és nem csupán egy-egy szezonra, hanem évekre tervezve. Mindezek melle"` (csonka)
  - Yoast tag: `"Fedezd fel a NONPLUS BASIC kollekció időtálló darabjait! Kényelmes és stílusos viselet, a NONPLUS SECOND SKIN kollekció részeként. Vásárolj most!"`

## Kapcsolódó

- [[11-wiki/lighthouse-agentic-browsing]] — Lighthouse SEO 100 a Yoast-tól, de duplikálás miatt social-share-en hibás
- [[11-wiki/shopify-robots-agent-policy]] — Shopify-spec robots-policy
- Yoast docs: <https://yoast.com/help/shopify-disable-native-seo/>
