---
name: Next.js 16 — middleware.ts → proxy.ts rename
type: wiki
created: 2026-05-21
updated: 2026-05-21
tags: [wiki, nextjs, breaking-change, "#tech/nextjs"]
related: [kgc-berles, nextjs-16-server-component-onclick-trap]
---

# Next.js 16 — `middleware.ts` → `proxy.ts` átnevezés

## Mi történt

A Next.js 16 release (2026-late) átnevezte a `middleware.ts` file-konvenciót **`proxy.ts`**-re. A működés AZONOS — csak a fájlnév változott.

> Quote a hivatalos doku (Next 16, `01-app/01-getting-started/16-proxy.md`):
> "Starting with Next.js 16, Middleware is now called Proxy to better reflect its purpose. The functionality remains the same."

## Migrációs trap

⚠️ **Backwards-compat NINCS.** Egy Next 15 → 16 upgrade után a régi `middleware.ts` **silent ignored** — semmilyen warning, semmilyen error. Csak az auth-gate-ek, redirect-ek hirtelen nem futnak, és a fejlesztő nem tudja miért.

**Diagnosztika:** `pnpm build` kimenetében a következő sor mutatja:
```
ƒ Proxy (Middleware)
```
Ha ez **hiányzik**, akkor a `proxy.ts` (vagy `middleware.ts`) NEM kerül bekapcsolva.

## Új konvenció (Next 16+)

- File neve: `proxy.ts` (vagy `.js`) a project-root-on (vagy `src/`-en belül, ha van)
- Egy projektben **csak egy** `proxy.ts`
- Export: named `proxy` function VAGY `default` export
- Config: `export const config = { matcher: ... }`

```ts
// proxy.ts
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function proxy(request: NextRequest) {
  // ugyanazok a NextRequest/NextResponse API-k mint middleware-ben
  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}
```

## Mikor használd

A doku szerint a Proxy NEM "full session management or authorization solution" — csak **optimistic checks**-ra való:
- modify headers
- programmatic redirects
- A/B test rewrites
- coming-soon access-gate (lásd kgc-berles 2026-05-21 implementáció)

Slow data fetching (DB call, external API) **nem ajánlott** — Edge runtime-on fut.

## Példa: kgc-berles coming-soon access-gate

[components/layout/proxy.ts](../02-Projects/kgc-berles.md) (2026-05-21):
- cookie `kgc_access=granted` (30 nap)
- `?belepo=<token>` URL-paraméter → set cookie + redirect tisztára
- whitelist: `/coming-soon`, `/projektek`, `/api`, `/_next`, statikus asset-prefixek
- minden más → 307 redirect `/coming-soon`-ra

## Kapcsolódó

- [[nextjs-16-server-component-onclick-trap]] — másik Next 16 breaking change
- [[02-Projects/kgc-berles]] — projekt-implementáció
- Session: [[../08-Sessions/2026-05-21-kgc-weboldal]]
