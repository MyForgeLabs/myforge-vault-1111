---
name: Next.js API proxy bridge minta
description: Két önálló Node-szerver közti adatcsere Next.js API route proxy-val — no CORS, no public env-URL, try/catch fallback
type: wiki
created: 2026-05-08
updated: 2026-05-08
tags: ["#topic/architecture", "#topic/nextjs", "#topic/api"]
---

# Next.js API proxy bridge minta

## Probléma

Két különálló Node service ugyanazon a host-on:
- **Publikus:** Next.js app (`kgc-berles` :3004), kliensek innen kérdeznek
- **Backend:** belső admin/CMS (`kgc-signage` :8202, basic-auth-tal védett, JSON-storage)

A kliens-böngészőnek kéne `:8202`-ről adatot kapnia, de:
- ❌ **CORS** — eltérő origin → preflight, header-tweak nightmare
- ❌ **Public env-URL** — ha kiír a kliensbe `NEXT_PUBLIC_SIGNAGE_URL=http://localhost:8202`, az `localhost` a kliens gépén nem ott van
- ❌ **Basic-auth** — a kliensben tárolt jelszó publikus
- ❌ **Tűzfal** — ha :8202 csak loopback-ra figyel, a kliens egyáltalán nem éri el

## Megoldás: Next.js API route mint proxy

```
[Browser] ──▶ [Next.js :3004] ──▶ [Backend service :8202]
        public               loopback (basic-auth, no CORS, server-to-server)
```

### Implementáció

```ts
// app/api/<resource>/route.ts
import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"

const BACKEND_BASE = process.env.SIGNAGE_URL || "http://localhost:8202"
const BACKEND_AUTH = process.env.SIGNAGE_AUTH    // "user:pass" — server-side env, NEM NEXT_PUBLIC_

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const id = searchParams.get("id")
  if (!id) return NextResponse.json({ error: "missing id" }, { status: 400 })

  try {
    const res = await fetch(`${BACKEND_BASE}/api/totem/${encodeURIComponent(id)}`, {
      cache: "no-store",
      headers: BACKEND_AUTH
        ? { Authorization: `Basic ${Buffer.from(BACKEND_AUTH).toString("base64")}` }
        : {},
    })
    if (!res.ok) throw new Error(`backend ${res.status}`)
    return NextResponse.json(await res.json())
  } catch (err) {
    console.error("[/api/<resource>]", err)
    // fallback — kliens NE törjön ha a backend pillanatnyilag down
    return NextResponse.json({ slides: [], error: "backend-unavailable" }, { status: 200 })
  }
}
```

### Kliens hívás

```ts
// components/X.tsx
const res = await fetch(`/api/totem-content?id=${id}`)   // saját origin → no CORS
const data = await res.json()
if (data.error) {
  // fallback render — ne bukjon a UI
  return <DefaultSlides />
}
```

## Mikor használd ezt a mintát

- ✅ **2 service ugyanazon a host-on**, közös rendszer-gazda
- ✅ **Backend basic-auth-tal** védett, nem akarod a kliensbe szivárogtatni
- ✅ **Polling/no-cache** szükséges (`cache: "no-store"`)
- ✅ **Graceful fallback** kell — ha a backend down, a UI ne dőljön
- ✅ Pre-existing service amit nem akarsz Next.js-be merge-elni

## Mikor NE használd

- ❌ Backend egy **Next.js** service is — akkor common monorepo + shared lib jobb
- ❌ Több proxy-réteg a feasability miatt — minden hop +5-30ms latency
- ❌ Nagy payload (10+ MB) — a Next.js node-runtime nem stream-eli alapból
- ❌ Sub-100ms requirement — szerver-szerver fetch + JSON-decode kétszer (proxy + kliens) drága

## Cache-stratégia

```ts
// rövid cache, frissül 60s-ban — admin változások későn jelennek meg
return NextResponse.json(data, {
  headers: { "Cache-Control": "public, max-age=60, s-maxage=60" }
})

// VS no-cache (real-time, polling-szerű)
export const dynamic = "force-dynamic"   // route szintű
// + fetch() options:
fetch(url, { cache: "no-store" })
```

## Auth-pattern változatok

| Backend auth | Proxy hogyan kezeli |
|---|---|
| Basic auth | `Authorization: Basic <base64>` server-side env-ből |
| Bearer token | `Authorization: Bearer <token>` server-side env-ből |
| API key header | `x-api-key: <key>` server-side env-ből |
| mTLS | Node `https` agent + cert-pair (komplex) |
| **Loopback-only (no auth)** | `BACKEND_BASE=http://127.0.0.1:8202` — tűzfal védi |

## Origin

KGC-Bérlés ↔ kgc-signage TV CMS bridge (2026-05-06):
- Forrás: `/root/projektjeim/KGC-ALL/kgc-berles/app/api/totem-content/route.ts`
- Backend: `/opt/kgc-signage/server.js` :8202 (basic-auth: `kgc:kivetito2026`)
- Kliens: `components/totem/TotemIdleScreen.tsx` poll-ol 5 percenként

## Kapcsolódó

- [[05-Memory/Infrastructure]] — KGC kivetítő/TV-CMS portok
- [[08-Sessions/2026-05-06-kgc-weboldal]] — TV CMS integráció session
