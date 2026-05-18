---
name: shopify-robots-agent-policy
type: wiki
created: 2026-05-12
updated: 2026-05-12
tags: [shopify, robots-txt, ai-agent, scraping-policy]
---

# Shopify built-in agent-policy a robots.txt-ben (2025-26)

Shopify 2025 H2-től **default robots.txt-ben** ASCII-art szekciót renderel ki, ami explicit megtiltja az **AI-agent vásárlást** (Operator, Computer Use, agent-checkout) anélkül, hogy human-review-step lenne a flow-ban.

## A blokk pontos szövege (nonplusz.hu, 2026-05-12)

```
#  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#  ┃  Robots & Agent policy                                               ┃
#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
#  ┃  Checkouts are for humans.                                           ┃
#  ┃  * Automated scraping, "buy-for-me" agents, or any end-to-end flow   ┃
#  ┃    that completes payment without a final human review step is not   ┃
#  ┃    permitted.                                                        ┃
#  ┃  * Legitimate integrators must use the official Checkout Kit:        ┃
#  ┃      https://www.shopify.com/checkout-kit                            ┃
#  ┃                                                                      ┃
#  ┃  Terms of Service: https://www.shopify.com/legal/terms               ┃
#  ┃  Contact: bots@shopify.com                                           ┃
#  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

User-agent: *
Disallow: /a/downloads/-/*
Disallow: /admin
Disallow: /cart
Disallow: /orders
Disallow: /checkouts/
Disallow: /checkout
Disallow: /29542062/checkouts
Disallow: /29542062/orders
Disallow: /carts
Disallow: /account
Disallow: /collections/*sort_by*
Disallow: /*/collections/*sort_by*
Disallow: /collections/*+*
```

## Miért fontos

- **Jogi vs technikai signal**: a robots.txt jogilag nem-bindings, de **AI-agent provider-ek** (Anthropic Computer Use, OpenAI Operator, Adept Agent) ToS-vita esetén ezt a szöveget hivatkozhatják. Shopify ezt explicit kifejezésre szánja.
- **Sort-by params blokkolva**: az `/collections/*sort_by*` egy klasszikus duplicate-content trap (kibővített Disallow 2026-tól minden Shopify-storefronton automatikus).
- **`/collections/*+*` blokk**: filter-kombinációk (color+size+price) infinit-URL-tree — szintén duplicate-content védelem.
- **`bots@shopify.com`** dedikált contact e-mail — legitim integrator (B2B reseller, comparison-site) használja, scrapingnek NEM workaround.

## Implementáció saját Shopify-storefront-on

Ez **default** minden új Shopify-store-ban. Custom `robots.txt.liquid`-del lehet overrideolni:

1. Admin → Online Store → Themes → Edit code → `templates/robots.txt.liquid`
2. **NE töröld az agent-policy block-ot** — Shopify ToS-szel ütközhet
3. Csak addíciók: pl. saját scraper-block extra `User-agent: GPTBot Disallow: /`

## Sanity-check curl-lal

```bash
curl -s https://example.myshopify.com/robots.txt | head -25
# Várt: a ASCII-art szekció a fájl elején
```

## Ahonnan a tudás jött

- [[06-Audits/2026-05-12 nonplusz.hu-basic webelemzés]] — nonplusz.hu robots.txt audit 2026-05-12

## Kapcsolódó

- [[11-wiki/lighthouse-agentic-browsing]] — agent-friendly site-design (ellentét: agent-policy szigorítás vs agent-browsing-score javítás — két különböző cél)
- [[11-wiki/shopify-yoast-dupla-og]] — egy másik Shopify-default vs Yoast interakció
- Shopify Checkout Kit: <https://www.shopify.com/checkout-kit>
