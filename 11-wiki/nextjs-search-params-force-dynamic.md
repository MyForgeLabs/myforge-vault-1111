---
name: Next.js 16 — useSearchParams needs force-dynamic (or Suspense)
type: wiki
tags: [wiki, nextjs, turbopack, gotcha]
created: 2026-05-11
updated: 2026-05-11
---

# Next.js 16 — `useSearchParams()` build-error a statikusan prerendert route-on

## A tünet

Build közben (`pnpm build` → Turbopack):

```
useSearchParams() should be wrapped in a suspense boundary at page "/ceg".
Read more: https://nextjs.org/docs/messages/missing-suspense-with-csr-bailout
```

## Miért

Next.js 16 a turbopack-buildben **statikusan prerendelne** minden olyan page-t, amelynél nem tud server-time-on dependency-t megállapítani. Ha a page kliens-komponensbe húz `useSearchParams()`-ot, a `?query` rész **csak runtime-on** van — a static prerender ezért bukik, és vagy Suspense-boundary-t vár (CSR-bailout határa), vagy explicit dynamic-jelzést.

## A két megoldás

### A) `export const dynamic = 'force-dynamic'` (preferred a dashboard-tipusra)

```tsx
// app/ceg/page.tsx
import { CompanyAdmin } from './_components/CompanyAdmin';

// useSearchParams a CompanyAdmin-ban — ezért nem prerenderelhető
export const dynamic = 'force-dynamic';

export default function CegPage() {
  return <CompanyAdmin initialLang="hu" />;
}
```

Mikor jó: amikor a route úgyis 100% logged-in, dinamikus tartalom (admin dashboard, user-szabású oldal). Nincs prerender-előny, és nincs is veszteség.

### B) `<Suspense>` boundary (preferred ha a route nagyrészt statikus)

```tsx
// app/foo/page.tsx
import { Suspense } from 'react';
import { FooClient } from './FooClient';

export default function FooPage() {
  return (
    <Suspense fallback={<FooSkeleton />}>
      <FooClient />
    </Suspense>
  );
}
```

Mikor jó: marketing-oldal, blog, valami amit statikusan érdemes szállítani, de egy kis client-island olvas URL-state-et.

## Gotcha-k

- **A hiba csak `pnpm build`-nél jön elő, dev-ben nem.** Ezért könnyű elcsúszni: a feature dev-en működik, CI-ban bukik. Tipp: futtass `pnpm build`-et minden olyan PR előtt, ami kliens-komponensbe URL-state-et húz.
- **A hiba a kliens-komponens szintjén dől el, nem a page-en.** Ha a kliens-komponens import-lánc valahol `useSearchParams()`-ot használ (akár közvetve egy hook-on át), a page-en is hat. Egy "tiszta" page-fájl is bukhat ha a child kliens-komponens csendben behúzza.
- **`router.replace(url, { scroll: false })`** — URL-state-mutáció: `replace`, ne `push` (különben minden tab-click history-pusht okoz, és a back-gomb értelmetlen lesz). `scroll: false` hogy a tab-váltáskor ne ugorjon a tetejére.
- **Default-érték törlése a query-stringből** — szebb URL-ek: ha a default ('all') érvényes, töröld a kulcsot:

  ```ts
  const updated = new URLSearchParams(params.toString());
  if (next === defaultValue) updated.delete(key); else updated.set(key, next);
  ```

## Példa a kódban

Kinda projekt: `apps/web/lib/use-url-state.ts` + `apps/web/app/admin/_components/AdminDashboard.tsx` + `apps/web/app/ceg/page.tsx` (2026-05-11, commit `7094f85`).

## Kapcsolódó

- [[11-wiki/nextjs-server-component-in-client-tree]] — másik Next.js 16 gotcha (server async komponens client-fában)
- [[02-Projects/teszt-eu]] — globális szűrők Phase 1
