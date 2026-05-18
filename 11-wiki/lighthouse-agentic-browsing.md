---
name: lighthouse-agentic-browsing
type: wiki
created: 2026-05-12
updated: 2026-05-13
tags: [seo, lighthouse, ai-agent, a11y, llms-txt]
---

# Lighthouse "Agentic Browsing" score

Új Lighthouse kategória (megjelent kb 2025 H2-ben), ami azt méri **mennyire jól tudja egy AI agent** (Claude, ChatGPT, Perplexity, Gemini, Brave Leo) **értelmezni és navigálni** az oldalon. Pontozza a `0-100`-as skálán.

## Mit mér

| Audit | Mit követel | Miért fontos |
|---|---|---|
| `agent-accessibility-tree` | Well-formed a11y-tree, semmelweis-szerű DOM ↔ a11y-tree konzisztencia | LLM agent-ek általában az a11y-tree-ből olvasnak (nem a vizuális render-ből), mert szöveges + szemantikus |
| `crawlable-anchors` | Minden `<a>`-nak van `href`-je (NEM JS-injected onClick handler) | Agent nem tudja követni a JS-onclick navigációt, csak `href` lánc követhető |
| `llms-txt` | `/llms.txt` követi az [llmstxt.org](https://llmstxt.org/) ajánlást | Agent ezt olvassa el ELSŐKÉNT a site struktúra megértéséhez |
| `link-name` | Minden link-nek diszkernálható neve (`aria-label` vagy szöveg) | "Click here" / üres ikon-link az agent-nek értelmezhetetlen |
| `label-content-name-mismatch` | Form-elem visible-label === aria-label | Agent ettől tudja melyik mezőt mire használja |
| Strukturált adat | Schema.org JSON-LD (Organization, Product, Article, …) | Agent first-class signal a típusra + entitásra |

## Tipikus pontszámok (2026 Q2 mérések alapján)

| Site-típus | Tipikus Agent score | Megjegyzés |
|---|---|---|
| Modern Shopify default theme + Yoast | 65-75 | Yoast meta-stack, de `user-scalable=0` viewport, llms.txt nélkül |
| Modern Next.js Vercel-edu | 80-95 | Static HTML + jó semantic markup |
| WordPress Goodlayers/Avada/Divi vanilla | 35-50 | Slider-plugin malformed a11y-tree, JS-injected links |
| Headless commerce (Shopify Hydrogen) | 85-95 | SSR + native semantic |

## Quick wins → Agent-score ugrás

1. **`llms.txt`** létrehozása (5 perc). Minimum:
   ```
   # NONPLUS
   > Fenntartható fashion brand magyar piacon.
   
   ## Kollekciók
   - [BASIC](https://nonplusz.hu/collections/basic): Alapdarabok
   - [SEASON](https://nonplusz.hu/collections/season): Szezonális kollekció
   ```
   Részletek: <https://llmstxt.org/>
2. **`<main>` landmark** hozzáadása a témához. WP-ben általában `header.php` / `footer.php` wrap-be `<main>`-t kell adni.
3. **Schema.org JSON-LD**: Organization, BreadcrumbList minimum. WP: Yoast/Rank Math automatikusan. Shopify: Yoast SEO Shopify app.
4. **Slider eliminálása vagy lecsúsztatása**. RevSlider / Slider Revolution gyakran törött a11y-tree-t generál.
5. **`<a href="..." onclick="...">` helyett** vagy normál `<a href>`, vagy `<button>` — soha JS-injected onClick handler `<div>`-en.

## Konkrét audit-eredmények ahonnan a tudás jött

- [[06-Audits/2026-05-12 himalajaijoga.hu webelemzés]] — **Agent 43** (RevSlider + JS-injected links + malformed a11y-tree)
- [[06-Audits/2026-05-12 nonplusz.hu-basic webelemzés]] — **Agent 67** (llms.txt nem-optimal + viewport zoom-block)
- [[08-Sessions/2026-05-13-rojt-s-bojt|2026-05-13 rojtesbojt staging]] — **Agent 33** (csak 4 fail: 2× üres Complianz link + agent-tree-cascade + Yoast-llms.txt BOM-bug). SEO 100, perf kiváló (LCP 302ms desktop). Tanulság: 1-2 üres aria-label + Yoast llms.txt-bug → 33 pont. **Yoast SEO v27.5 `llms.txt` template bug-jai (2026-05-13 felfedezés):** (a) BOM (`﻿`) az első byte-on → H1 nem matchel a Lighthouse-nál; (b) curly-quote-okat `\-`, `\.\.\.\-\.` backslash-escape-pel ír (markdown-incompatibilis); (c) WP `site_url()` trailing-slash + relative-path leading-slash **dupla-slash URL-eket** gyárt (`https://...com//etlap/`). **Workaround:** `wpseo_llms_txt_content` filter override (saját content), vagy WP page-stub `/llms.txt` permalink-kel + `Content-Type: text/plain` mu-plugin-rule. NE támaszkodj a Yoast auto-llms.txt-re.

## Kapcsolódó

- [[11-wiki/shopify-robots-agent-policy]] — Shopify built-in agent-policy robots.txt-ben (más mintázat: NEM Lighthouse-pontozott, de agent-friendly signal)
- [seo](../../.claude/skills/seo/) skill — cherry-pick ECC-ből
- Lighthouse docs: <https://developer.chrome.com/docs/lighthouse/agentic-browsing/>
