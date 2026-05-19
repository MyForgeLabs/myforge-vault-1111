---
name: tsx --env-file vs dotenv import
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#stack/nodejs", "#stack/tsx", "#dotenv"]
---

# tsx scripts — `--env-file` flag a klasszikus `dotenv import` HELYETT

Standalone CLI-scripteknek amik egy meglévő Next.js codebase `lib/db`-jét
használják, a klasszikus `import "dotenv/config"` **túl későn fut**.

## A csapda

```typescript
// scripts/seed-achievements.ts — ROSSZ pattern
import { config } from "dotenv";
config({ path: ".env.local" });        // ← (1) ez user-kód, futna ELŐSZÖR

import { db } from "@/lib/db";          // ← (2) DE ez ESM-hoist-olódik (1) ELÉ
                                        //   és db-init-kor process.env.DATABASE_URL
                                        //   még UNDEFINED → "DATABASE_URL is not set" throw
```

ES Modules-ben az `import` statement-ek **HOIST-olódnak** a fájl tetejére
**bármilyen** runtime-kód előtt. A `dotenv.config()` az import-ok után fut, de
addigra a `lib/db/index.ts` modul-szintű kódja már lefutott, és az
`process.env.DATABASE_URL` üres volt.

## A megoldás — Node 20.6+ `--env-file` flag

```typescript
// scripts/seed-achievements.ts — JÓ pattern
import { db } from "@/lib/db";          // simán importálható
// ... rest of script
```

Futtatva:

```bash
tsx --env-file=.env.local scripts/seed-achievements.ts
```

A `--env-file` egy **Node-szintű flag** (Node 20.6 óta), ami a `process.env`-be
tölti a fájl tartalmát **a script-modulok BETÖLTÉSE előtt**. Tehát mire a
`lib/db/index.ts` lefut, a `DATABASE_URL` már ott van.

A `tsx` ezt a flag-et közvetlenül átadja a Node-nak, tehát ugyanúgy működik.

## package.json pattern

```json
{
  "scripts": {
    "seed-achievements": "tsx --env-file=.env.local scripts/seed-achievements.ts",
    "replay-glicko":     "tsx --env-file=.env.local scripts/replay-glicko.ts",
    "notify-events":     "tsx --env-file=.env.local scripts/notify-upcoming-events.ts"
  }
}
```

És `pnpm seed-achievements -- --write` átadja a `--write` flag-et a scriptnek.

## drizzle.config.ts kivétel

A `drizzle.config.ts` máshogy fut — a drizzle-kit `tsx`-vel saját maga
load-olja, és a config-fájl kódja **futás-időben fut** (NEM module-load-time-ban
külön DI-needet jelenít meg). Ezért **OTT marad jónak** a klasszikus pattern:

```typescript
// drizzle.config.ts — itt OK marad
import { config } from "dotenv";
import type { Config } from "drizzle-kit";

config({ path: ".env.local" });

export default {
  dbCredentials: { url: process.env.DATABASE_URL! },
  ...
} satisfies Config;
```

## Boulium-példa (2026-05-19)

3 CLI-script került be `scripts/`-be (`replay-glicko`, `seed-achievements`,
`notify-upcoming-events`) — mind `--env-file=.env.local`-lal fut, és
`@/lib/db`-t import-álja közvetlenül. Plus `lib/achievement-defs.ts` és
`lib/push-core.ts` server-only-mentes core-fájlok (lásd
[[server-only-core-extract-pattern]]).

## Kapcsolódó

- [[server-only-core-extract-pattern]] — `import "server-only"` ki-extract
- Node docs: `--env-file` flag (20.6+)
