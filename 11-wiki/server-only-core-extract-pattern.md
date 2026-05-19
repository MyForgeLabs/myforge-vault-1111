---
name: server-only core-extract pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#stack/nextjs", "#refactor"]
---

# `import "server-only"` — core-extract pattern script-szintű importáláshoz

Egy `lib/<name>.ts` ami `import "server-only"`-t használ Next.js-server-guard
gyanánt, **NEM importálható** standalone `tsx`-scriptből, kliens-komponensből
vagy bármilyen NEM-Next.js-context-ből — a `server-only` package egy stub ami
csak Next-build-time-context-ben "ott van".

```
Error: Cannot find module 'server-only'
```

## A pattern

**Két fájlra bontás:**

```
lib/<name>-core.ts   ← logika, NO server-only import
lib/<name>.ts        ← server-only + re-export a -core-ból
```

**Példa — `lib/push-core.ts`** (logika):

```typescript
import webpush from "web-push";
import { db } from "@/lib/db";
import { pushSubscription } from "@/lib/db/schema";

// ... full implementation ...

export async function sendPushToUsers(userIds: string[], payload: PushPayload) {
  // ...
}
```

**`lib/push.ts`** (Next-server-guard):

```typescript
import "server-only";
export { sendPushToUser, sendPushToUsers, type PushPayload } from "@/lib/push-core";
```

## Importálási konvenció

| Hol használjuk | Mit importálunk |
|---|---|
| `app/**/*.tsx`, `app/**/actions.ts` (Server Component vagy Server Action) | `@/lib/<name>` — kapja a server-only guardot |
| `scripts/**/*.ts` (CLI, tsx-runtime) | `@/lib/<name>-core` — NO guard, simán fut |
| `"use client"` komponens | NEM importálja — közvetlen webserver-only-import-ra build-time-error jönne |

## Boulium-példa (2026-05-19, 2× alkalmazva)

1. **`lib/achievement-defs.ts`** (ACHIEVEMENTS const, ACHIEVEMENT_MAP — pure data)
   + **`lib/achievements.ts`** (re-export + `evaluateAchievements()` ami `db`-vel
   dolgozik, server-only). A `scripts/seed-achievements.ts` a
   `-defs`-et importálja, az `app/achievements/page.tsx` a re-export-os főfájlt.

2. **`lib/push-core.ts`** (`sendPushToUser`, `sendPushToUsers` — `web-push`-szal
   közvetlenül) + **`lib/push.ts`** (re-export + server-only). A
   `scripts/notify-upcoming-events.ts` a `-core`-t importálja, az
   `app/match/[id]/actions.ts` a re-export-os főfájlt.

## Miért NEM csak elhagyni a server-only?

A `server-only` egy **build-time biztosíték** — ha véletlenül egy `"use client"`
komponens importálja a fájlt, a Next.js build-error-t dob azonnal. Enélkül a
build silently átmegy, és a kliens-bundle-ben landolnak DB-credentials vagy
api-secrets. **NE vedd ki** a server-only marker-t soha.

A core-extract a tisztább megoldás: a `server-only` őrző marad ott ahol kell, és
a script-ek tudják importálni ami **adatkereszt-szintű** (pure logic, no
client-side risk).

## Kapcsolódó

- [[tsx-env-file-vs-dotenv-import]] — másik tsx-script-Next.js interop quirk
- Next.js docs: `server-only` package — `node_modules/server-only/`
