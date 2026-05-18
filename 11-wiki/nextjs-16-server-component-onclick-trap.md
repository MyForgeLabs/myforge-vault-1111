---
name: Next.js 16 Server Component onClick trap
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/playbook", "#stack/nextjs", "#nextjs/16"]
---

# Next.js 16 — Server Component `onClick` prod-crash

Next.js 15-ig a Server Component-ben `<Link onClick={...}>` mintázat csendesen érvénytelen volt fejlesztés alatt, **prod-build viszont crash-el** Next.js 16-tól:

```
⨯ Error: Event handlers cannot be passed to Client Component props.
  {href: "#", className: ..., aria-disabled: ..., onClick: function onClick, children: ...}
                                                            ^^^^^^^^^^^^^^^^
If you need interactivity, consider converting part of this to a Client Component.
    at stringify (<anonymous>) {
  digest: '187511925'
}
```

A digest a böngészőben csak `"An error occurred in the Server Components render"`-ként látszik (security: szervezett-info az SC-hibákról), a tényleges üzenet csak a PM2 / `pnpm logs`-ban.

## A csapda

A "disabled link" anti-pattern egy SC-ben:

```tsx
// ❌ Next.js 16 prod-build → crash
<Link
  href={canDo ? "/target" : "#"}
  aria-disabled={!canDo}
  onClick={(e) => !canDo && e.preventDefault()}
>
  Művelet
</Link>
```

Az `onClick={(e) => ...}` egy function-prop, amit a Server Component nem tud átadni a Client Component-nek (`<Link>` client).

## Helyes pattern — conditional render

```tsx
// ✓ tiszta SC, nincs function-handler
{canDo ? (
  <Link href="/target" className="...">
    Művelet
  </Link>
) : (
  <div className="... opacity-50 cursor-not-allowed">
    Művelet (még nem lehet)
  </div>
)}
```

A két JSX-ág teljesen tiszta SC — semmi event-handler, semmi state. Ha tényleg kell client-side feedback (pl. tooltip a tiltott állapotról), wrap-eld be egy külön `"use client"` komponensbe.

## Diagnosztika

A digest-hibák PM2-ban:

```bash
pm2 logs <app> --lines 50 --nostream | grep -B2 "Event handlers cannot be passed"
```

A `digest` kódot meg lehet feleltetni a renderelt oldalon a `<RootErrorBoundary>` üzenetével — minden SC-render egyetlen digest-jét generálja az adott deploy-on.

## Kapcsolódó

- [[nextjs-server-component-in-client-tree]] — másik SC↔Client interop-csapda
- [[nextjs-search-params-force-dynamic]] — Next.js 15+ Suspense + searchParams
</content>
<!-- auto-enriched 2026-05-18: +1 semantic cross-link via vault-search -->
- [[nextjs-turbopack-gotchas]] (sem-rokon, score=0.35)
