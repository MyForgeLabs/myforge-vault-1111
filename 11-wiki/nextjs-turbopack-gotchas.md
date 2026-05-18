---
name: nextjs-turbopack-gotchas
description: Next.js 16+ Turbopack gotchák - dev memory-leak (parallel API calls + runtime-dir manipulation crash), production public/ cache (systemctl restart kell), HMR-lockup. 11 session-evidence (myforge + kgc + kinda + boulium). Cross-projekt failure-mode Q2-#2
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/nextjs", "#topic/turbopack", "#topic/performance", "gotchas"]
status: stable
session-evidence: 11
first-seen: 2026-W17
---

# Next.js Turbopack gotchas

## 6 visszatérő trap

### 1. Dev-mode parallel API calls → memory-spike → HMR-lockup
**Tünet**: 4-6 párhuzamos `fetch('/api/...')` egy `useEffect`-ből → Next.js dev-server memóriahasználat 800MB → 2.5GB → HMR-update lockup, kell `Ctrl+C` + `npm run dev` újra.

**Ok**: Turbopack dev-mode minden API-route-re külön module-graph + watch-file-list-et tart. Parallel-call N módban szétrobban.

**Megoldás**:
```ts
// Promise.all batchen NEM hatékony — sequential vagy chunked 2-3-asával
async function loadData() {
  const a = await fetch('/api/users');
  const b = await fetch('/api/posts');
  const c = await fetch('/api/comments');
  return { a, b, c };
}
// Nem:
// const [a,b,c] = await Promise.all([fetch('/api/users'), ...]);
```

vagy `useSWR` / `react-query` deduplication-nel (cache-aware).

### 2. `public/` mappa cache-trap production-ban
**Tünet**: új image / font / static-asset bekerül `public/`-ba → build sikeres → frontend a régi file-t mutatja → `systemctl restart` kell.

**Ok**: Next.js production-build a `public/` content-hash-elt-fingerprint-jét rögzíti — runtime-időben NEM újraolvassa.

**Megoldás A** — fingerprint-build-time:
```bash
# package.json scripts:
"build:assets": "node scripts/fingerprint-public.js && next build"
```
Minden `public/<file>.png` → `public/<file>.<hash>.png` deploy előtt, és a code-referenciák update-elve.

**Megoldás B** — runtime-friendly file-route:
```ts
// app/assets/[...path]/route.ts
import { readFile } from 'fs/promises';
export async function GET(req, { params }) {
  const file = await readFile(`public/${params.path.join('/')}`);
  return new Response(file, { headers: { 'Cache-Control': 'no-cache' } });
}
```
Lassú lesz, csak admin/dev-on használható.

### 3. `runtime/` adatmappa törlése HMR-crash-szel jár
**Tünet**: dev-mode-ban a `runtime/sessions/*.json` mappa fájljait `rm -rf`-fel törölted egy script-ben → HMR azonnal panic-elt, "Cannot find module '/runtime/...'".

**Ok**: Turbopack file-system-watcher beragadt egy törölt file-ra.

**Megoldás**: `runtime/` mappa törlése csak **dev-server állva**. Ha live-törlés kell:
```bash
# Stop dev → cleanup → restart
pkill -f 'next dev' && rm -rf runtime/sessions && npm run dev
```

### 4. `useSearchParams` build-error force-dynamic nélkül
**Tünet**: `npm run build` → `Error: useSearchParams() should be wrapped in a suspense boundary at page "/foo"`.

**Megoldás**:
```ts
// app/foo/page.tsx
export const dynamic = 'force-dynamic';  // explicit opt-out static-generation-ból
// vagy Suspense:
<Suspense fallback={<Spinner />}>
  <ClientComponent />
</Suspense>
```
Részletek: [[nextjs-search-params-force-dynamic]] (komplementer wiki).

### 5. Async server-component client-tree-ben
**Tünet**: `"use client"` directive → async-server-component child → "Cannot await server components in client tree" error.

**Megoldás**: server-component-et `children` prop-ként továbbítsd:
```tsx
// app/page.tsx (server)
<ClientLayout>
  <ServerData />  // ← server-component MINT children
</ClientLayout>

// components/ClientLayout.tsx ("use client")
export function ClientLayout({ children }) {
  return <div>{children}</div>;  // server-content marad untouched
}
```
Részletek: [[nextjs-server-component-in-client-tree]].

### 6. Production-build first-run extreme lassú (Turbopack 16+)
**Tünet**: `next build` első futás 4-8 percig pörög, cache hiány miatt.

**Megoldás**: `.next/cache` dir Docker-volume / CI-cache-be persist-eld:
```yaml
# .github/workflows/build.yml
- uses: actions/cache@v3
  with:
    path: |
      .next/cache
      node_modules/.cache
    key: ${{ runner.os }}-next-${{ hashFiles('**/package-lock.json') }}
```

## Session-evidence (11 forrás)

| Project | Hét | Trap-típus |
|---|---|---|
| myforge-dashboard | W17 | #1 + #2 |
| myforge-os | W17 | #3 |
| kgc-berles | W19 | #1 + #4 |
| kgc-weboldal | W19 | #4 + #5 |
| kinda-project | W19 | #2 + #3 |
| boulium | W20 | #1 + #6 |
| robbantott-kereső | W20 | #2 (PDF-asset) |
| myforge-dashboard-polish-tabs | W17 | #1 |
| kgc-erp | W18 | #4 |
| ... | ... | ... |

## Általános Day-0 checklist Next.js Turbopack projektre

- [ ] `package.json` scripts `dev` + `build` + `build:assets` (fingerprint)
- [ ] `.gitignore` `runtime/` + `.next/cache` (deploy explicit kezelése)
- [ ] CI-cache `.next/cache` + `node_modules/.cache` persist
- [ ] Default `dynamic = 'force-dynamic'` minden `useSearchParams`-páron
- [ ] `useSWR` vagy `react-query` az api-fetch-batch helyett
- [ ] `systemctl restart` script `public/`-asset-update után

## Kapcsolódó

- [[nextjs-search-params-force-dynamic]] — #4 részletes wiki
- [[nextjs-server-component-in-client-tree]] — #5 részletes wiki
- [[nextjs-pwa-shell-minimum]] — komplementer (PWA-perf)
- [[nextjs-api-proxy-bridge]] — komplementer (multi-service)
- [[../02-Projects/kgc-berles]] / [[../02-Projects/myforge-dashboard]] / [[../02-Projects/teszt-eu]] — host-projektek
- [[../06-Audits/2026-05-18 vault-meta NotebookLM cross-projekt synthesis]] — Q2-#2 cross-projekt
