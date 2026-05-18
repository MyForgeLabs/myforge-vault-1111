---
name: Next.js — server component in client tree (gotcha)
type: wiki
created: 2026-05-08
updated: 2026-05-08
tags: ["#type/wiki", "nextjs", "react", "frontend"]
---

# Next.js — server async komponenst NEM lehet `"use client"` wrapper alá renderelni

## A hiba

```
Module not found: Can't resolve 'child_process'
./lib/vault.ts:3:1
[Client Component Browser]
```

A buildelő (turbopack / webpack) megpróbálja a vault.ts-t **kliens-bundle**-be tenni, mert egy `"use client"` komponens importál olyan szerver-komponenst aminek vault.ts a tranzitív függősége.

## A rossz minta

```tsx
// VaultPulse.tsx (server async)
import { getRecentCommits } from "@/lib/vault"  // node-only

export async function VaultPulse() {
  const commits = await getRecentCommits(10)
  return <div>...</div>
}

// VaultPulseClickable.tsx (BAD — client wrapper renderel server child-ot)
"use client"
import { VaultPulse } from "./VaultPulse"
import { useState } from "react"

export function VaultPulseClickable() {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <button onClick={() => setOpen(true)}>diff</button>
      <VaultPulse />  {/* ← ez a baj */}
    </div>
  )
}
```

A Next.js fordító **nem tudja statikusan eldönteni**, hogy a kliens-fa a szerver-komponenst csak SSR-en kapja vagy a kliens-bundle-be is be kell rakni — ezért biztonságból be akarja rakni → `child_process` módul nem létezik a böngészőben → build error.

## A jó minta — children prop

```tsx
// VaultPulseClickable.tsx (GOOD — server child as prop)
"use client"
import { useState } from "react"
import type { ReactNode } from "react"

export function VaultPulseClickable({ pulse }: { pulse: ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <button onClick={() => setOpen(true)}>diff</button>
      {pulse}
    </div>
  )
}

// page.tsx (server component)
import { VaultPulse } from "@/components/VaultPulse"
import { VaultPulseClickable } from "@/components/VaultPulseClickable"

export default function Page() {
  return <VaultPulseClickable pulse={<VaultPulse />} />
}
```

A ReactNode prop-on keresztül a kliens-komponens csak egy "render-eredményt" kap — a Next.js fordító látja hogy a szerver-komponens render-helye a parent (server), nem a kliens.

## Általános szabály

- "use client" komponens **NE importáljon** szerver-only modult (`fs/promises`, `child_process`, `node:*`)
- "use client" komponens **NE importáljon** szerver async komponenst és NE renderelje gyermekként
- Ha a kliens-komponens dekorál egy szerver-komponenst, **prop-on adja át** (`children` vagy named prop)

## Tipikus tünet

A build-error stack-trace mutatja a tranzitív útvonalat:

```
[Client Component Browser]:
    ./lib/vault.ts [Client Component Browser]
    ./components/VaultPulse.tsx [Client Component Browser]
    ./components/VaultPulseClickable.tsx [Client Component Browser]
    ./components/VaultPulseClickable.tsx [Server Component]
    ./app/page.tsx [Server Component]
```

A kulcs: ha a vault.ts megjelenik `[Client Component Browser]` ágként, akkor valahol a fa-fennakadt → keress meg minden `"use client"` fájlt ami a vault-ot húzza.

## Kapcsolódó

- [[07-Decisions/2026-05-08 Myforge OS Wave A-K dashboard expansion]]
- Hivatalos: https://nextjs.org/docs/app/getting-started/server-and-client-components
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[nextjs-turbopack-gotchas]] (sem-rokon, score=0.54)
