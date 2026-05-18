---
name: Auth/session/cookie-bridge család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/auth, taxonomy, evergreen, security, cookies, session, jwt, cross-subdomain]
---

# Auth/session/cookie-bridge család taxonomy

> [!info] TL;DR
> A vault-ban **18 cookie + 9 auth + 10 token + 31 session-érintett Concept** szétszórva, de a cross-app auth/session-bridging-nek **csak 1 wiki**-je van ([[cross-subdomain-cookie-session-bridge]]). Itt taxonomy: a session-management **5 koncentrikus rétege**, és milyen cookie/token-szerződés-ütközések fordulnak elő ha ezeket keverjük.

## Cluster-members

| Concept | Réteg | Forrás |
|---|---|---|
| cf-bm cookie | layer-0 (CDN) | session |
| kinda_user cookie | layer-2 (app-session) | session |
| kinda_user cookie format | layer-2 | session |
| kinda_user cookie signature | layer-2 | session |
| kinda_user cookie payload | layer-2 | session |
| incompatible cookie payload shapes | layer-2 (bug) | session |
| mismatched clear cookie options | layer-2 (bug) | session |
| Cookie issuance source | layer-2 (meta) | session |
| Cookie contract | layer-2 (meta) | session |
| cookie Domain attribute | layer-3 (cross-sub) | session |
| Cross-subdomain shared cookie | layer-3 | wiki |
| Kinda-web canonical cookie | layer-3 | session |
| kinda-web cookie | layer-3 | session |
| cross-subdomain cookie session bridge pattern | layer-3 | wiki |
| session cookie in puppeteer | layer-4 (server-side reuse) | wiki/puppeteer-pdf-system-chrome |
| session cookie leak | layer-2 (security) | session |
| session cookie format change | layer-2 | session |
| JWT cookie auth | layer-2 (token-type) | session |
| HMAC token / TTL / payload / encoding | layer-1 (token-spec) | wiki/puppeteer-pdf-system-chrome |
| token exhaustion / usage / budget cap | LLM-token (nem-auth) | session |
| API token meter | layer-1 (API-key) | session |
| Auth / auth routes / auth layer + limit | layer-2 | session |
| admin auth | layer-2 | session |
| Session-based auth | layer-2 | session |
| Auth upgrade | meta | session |
| Dashboard auth upgrade | meta | session |
| PDF route auth | layer-1 (route-scoped HMAC) | wiki |

## Az 5 koncentrikus réteg

### Layer 0 — CDN/edge (`cf-bm`, `__cf_bm`)
**Felelős:** Cloudflare bot-management. NEM a te dolgod, NEM piszkáld.

**Szabály:** soha ne masszírozd `cf-bm`-et. Ha session-debugban ez cookie-előugrik, **figyelmen kívül hagyd**.

### Layer 1 — Token-spec (HMAC, JWT, API-key)
**Felelős:** stateless token előállítás+verifikáció.

| Spec | Mire jó |
|---|---|
| **HMAC** | route-scoped short-TTL (pl. PDF-render 120s) |
| **JWT** | cross-app payload (user-id, roles, exp) |
| **API-key** | service-to-service, opaque |

**Szabály:**
- HMAC payload = `{ssid, exp, scope}`, kódold base64url; secret env-var (`PDF_HMAC_SECRET`)
- JWT RS256 production, HS256 csak ha 1 service (key-rotation nehéz)
- TTL: PDF/file-token 60-180s, session-JWT 24h, refresh-token 30d
- HMAC token encoding URL-safe (PDF-routes-on URL-param-ban megy)

→ [[puppeteer-pdf-system-chrome]]

### Layer 2 — App-session cookie (`kinda_user`, `next-auth.session-token`)
**Felelős:** browser ↔ origin perzisztens-session.

**Cookie-payload-format szabály:**
- **EGY** cookie-name = **EGY** payload-shape (string vagy JSON, soha vegyesen)
- **Issuer** ↔ **Verifier** payload-shape egyezés **KÖTELEZŐ** (incompatible cookie payload shapes bug)
- Cookie-attribútumok issuance ÉS clear oldalon **AZONOS**-ak (mismatched clear cookie options bug — különben `Set-Cookie` nem törli a régit)

**Audit-szabály:** issuer-code + verifier-code git-grep-pel összefésülve PR-ban. Ha 2-féle issuer ír ugyanazt a cookie-t (pl. NextAuth + custom legacy), payload-format-egyeztetés.

**Anti-pattern:** `Set-Cookie: kinda_user=...; Path=/` és `Set-Cookie: kinda_user=; Path=/; Domain=.kinda.app` — Path/Domain-eltérés → browser KÉT cookie-t tart, login-loop.

### Layer 3 — Cross-subdomain bridge (Domain-attribute)
**Felelős:** `app.kinda.app` ↔ `balance.kinda.app` session-megosztás.

**Szabály:**
- Cookie `Domain=.kinda.app` (leading dot) — minden sub-domain megosztja
- `SameSite=Lax` (vagy `None`+`Secure` ha cross-site)
- **Egyetlen issuer** (canonical) — `Kinda-web canonical cookie` minta, NEM 2-app párhuzamosan issue-oljon

**`return_to` open-redirect veszély:**
- Login utáni redirect param → **allowlist**-en menjen át (`balance.kinda.app`, `app.kinda.app`, …)
- Soha ne `return_to=https://evil.com` engedélyezve

→ [[cross-subdomain-cookie-session-bridge]]

### Layer 4 — Server-side cookie-reuse (Puppeteer, scraping)
**Felelős:** browser-issued cookie back-portolása server-side request-be (PDF-render, screenshot).

**Mintázat:**
```js
// Puppeteer példa
await page.setCookie({ name: 'kinda_user', value: token, domain: '.kinda.app', ... });
```

**Szabály:**
- Soha ne hard-code-old a session-tokent — proxy-d a request-hez tartozó cookie-t
- HMAC route-scoped token > session-cookie-reuse (kisebb attack-surface)

→ [[puppeteer-pdf-system-chrome]]

## Cookie-szerződés-ütközés sablonok

| Ütközés | Tünet | Fix |
|---|---|---|
| **Issuer/verifier payload shape eltér** | random 401 | spec git-tracked, JSON-schema validáció |
| **Cookie Path eltér** | dupla cookie, logout nem-tisztít | egységes Path=/ |
| **Cookie Domain eltér** | parent + sub domain mindkettő setet | egységes Domain=.kinda.app |
| **SameSite=Strict cross-site link-en** | session „kiesik" külső linkről jövéskor | SameSite=Lax |
| **2 issuer ugyanazt a cookie-t** (NextAuth + legacy) | flap-pelő login | 1 canonical issuer, másikat törölni |

## Reusable szabályok

1. **Cookie-contract dokumentum** — minden cookie-hoz `name / scope / path / domain / samesite / max-age / payload-schema` (1 markdown-tábla a vault-ban app-onként)
2. **HMAC route-scoped token** drága-route-ra (PDF, file-download) — JWT-session refresh-flow helyett
3. **Allowlist `return_to`** — open-redirect close kötelező
4. **Cookie + token NE keveredjenek** ugyanazon route-on; vagy session-cookie ELLENŐRZÉS, vagy HMAC-token ellenőrzés, NEM mindkettő (DoS-rés)
5. **`SameSite=None`** csak `Secure`-ral + jó indok (cross-site iframe)
6. **Telemetry**: minden 401 log-oljon `which-layer-failed` mezőt (CDN/token/cookie/cross-sub/server-reuse)
7. **Layer-1 token-secret rotation**: HMAC `PDF_HMAC_SECRET` 90-naponta cseréld

## Anti-pattern

| Anti-pattern | Probléma |
|---|---|
| `ADMIN_PASSWORD hardcoded fallback` | env-var hiányzik → kódolt fallback ⇒ leak ([[fallback-pattern-family-taxonomy]]) |
| Cookie-Set-Cookie clear-options eltér | logout NEM törli a cookie-t |
| 2 issuer ugyanazt a cookie-t írja eltérő payload-tal | random session-bug |
| `return_to` allowlist nélkül | phishing-rés |
| HMAC TTL >10 perc PDF-routes-on | scraper-vektor |

## Kapcsolódó

- [[cross-subdomain-cookie-session-bridge]]
- [[puppeteer-pdf-system-chrome]]
- [[demo-fallback-readonly-guard]]
- [[fallback-pattern-family-taxonomy]]
- [[guard-pattern-family-taxonomy]]
