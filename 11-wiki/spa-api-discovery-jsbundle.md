---
name: SPA API discovery via JS-bundle introspection
type: wiki
tags: ["#type/wiki", "#pattern/web-scraping", "#pattern/api-discovery"]
created: 2026-05-18
updated: 2026-05-18
---

# SPA API discovery via JS-bundle introspection

> Single-Page-App (React/Vue/Vite) backend-API endpoint-ok kinyerése a JS-bundle-ből, ha a HTML üres és nincs sitemap-ban.

## Mikor használd

Modern SPA-oldal scrape-elése amikor:
- A HTML-fő minimal (csak `<script>` + `<link>`)
- Sitemap-ban CSAK frontend-route-ok vannak (nem API URL)
- Nincs publikus REST-spec / OpenAPI dok
- A robots.txt megengedi a bot-traffic-et (etikus scrape, nem brute-force)

A SPA-k a TÉNYLEGES termék-adatot JS-runtime-ban töltik be — az API URL-ek ott vannak a bundle-ben hardcoded-ként. Ezeket grep-pel kinyerhetjük.

## Workflow

1. **HTML scrape + size-check**:
   ```bash
   curl -sS -L "https://target.com/" -o /tmp/index.html -w "%{http_code} %{size_download}\n"
   ```
   Ha `size < 5KB` → SPA gyanús.

2. **Robots / sitemap**:
   ```bash
   curl -sS "https://target.com/robots.txt"
   curl -sS "https://target.com/sitemap.xml"
   ```

3. **JS-bundle URL kinyerés a HTML-ből**:
   ```bash
   grep -oE 'src="/assets/[^"]+\.js"' /tmp/index.html | head -1
   ```

4. **JS-bundle letöltés + API-grep**:
   ```bash
   curl -sS -L "https://target.com<bundle-path>" -o /tmp/bundle.js
   grep -oE '"https?://[^"]+/(api|graphql)[^"]*"' /tmp/bundle.js | sort -u
   ```
   Kihalászza minden hardcoded API URL-t (REST, GraphQL).

5. **Endpoint direct call** + parse:
   ```bash
   curl -sS "https://target.com/api/<endpoint>" | python3 -m json.tool | head
   ```

## Validation case — kisgepcentrum.hu (2026-05-18)

- HTML size: **461 bytes** (clear SPA signal)
- Sitemap: **csak 4 URL** (`/`, `/products`, `/service`, `/contact` — route-ok, nem termékek)
- JS-bundle: `/assets/index-B5YjpxRp.js` (862KB)
- **API URLs in bundle** (regex hit):
  - `https://www.kisgepcentrum.hu/api/banner`
  - `https://www.kisgepcentrum.hu/api/catalogue`
  - `https://www.kisgepcentrum.hu/api/categories` ← jackpot
  - `https://www.kisgepcentrum.hu/api/datatable`
  - `https://www.kisgepcentrum.hu/api/exploded`
- `/api/categories` direct call → **195KB JSON, 181 termék + imgur.com CDN image URLs**
- Eredmény: 175 valódi termékfotó letöltve `brand/product-photos/kgc-website/` mappába kategória-bontásban

## Pitfalls

- **www vs non-www** — `https://target.com/api` 404, de `https://www.target.com/api` 200. A bundle-ben az aktuális URL van — használd EXAKT azt.
- **Auth / token / API-key** — néhány API CORS-restricted vagy `X-API-Key` header-t vár. Ha a HTML/bundle-ben látsz `Bearer` vagy hasonló pattern-t, az auth-required.
- **Rate-limiting** — bulk-fetch előtt nézd meg `Retry-After` header-eket. KGC-case: 175 imgur.com kép letöltés 0 retry-vel ment (imgur public CDN).
- **Robots.txt etika** — `Disallow: /admin` betartani. Csak `Allow:` vagy unspecified path-okat scrape-elj.

## Reusable patterns

| Bundle-grep pattern | Mit talál |
|---------------------|----------|
| `'"https?://[^"]+/(api|graphql)[^"]*"'` | Hardcoded API URL-ek (REST + GraphQL) |
| `'fetch\("[^"]+"\)'` | Inline fetch hívások |
| `'"\\/api\\/[a-z/-]+"'` | Relative API path-ok (escaped) |
| `'X-API-Key|Authorization|Bearer'` | Auth-header hint-ek |

## Kapcsolódó

- [[firecrawl]] — wrapper a `firecrawl` parancshoz amikor LLM-friendly markdown kell, NEM raw API-discovery
- [[defuddle]] — tiszta markdown extract single-page-ből (NEM SPA-hez)
- `feedback_claims_verification.md` — scraping előtt verifikáljuk hogy a robots.txt engedélyezi-e
