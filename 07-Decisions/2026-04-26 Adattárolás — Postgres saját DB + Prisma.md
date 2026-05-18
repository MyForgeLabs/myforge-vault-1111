---
name: Adattárolás — saját kgc_berles Postgres + Prisma 7
type: decision
tags: [kgc-berles, db, prisma, postgres, decision]
created: 2026-04-26
updated: 2026-04-26
project: kgc-berles
---

# Adattárolás — saját kgc_berles Postgres + Prisma 7

> [!info] Döntés időpont: 2026-04-26
> A KGC-Bérlés frontend 6 entitást migrál JSON-fájlokból dedikált Postgres DB-be. 5-fázisú fokozatos refactor, mind a 6 entitás Prisma-n keresztül.

## A 4 alkérdés döntése

### 1. JSON marad vagy Postgres?
**🟢 Postgres** — KGC-ERP `kgc_erp` jelenleg ÜRES (0 tábla), nincs migrálandó shared state. Saját DB.

### 2. Saját DB vagy megosztott KGC-ERP-vel?
**🟢 Saját `kgc_berles`** — ugyanazon a `kgc-postgres` Docker container-en, csak külön DB. Független schema, deploy lifecycle, backup, permission. Operatív teher minimális (egy `CREATE DATABASE` parancs).

### 3. ORM
**🟢 Prisma 7** — schema-first, type-gen, migration tooling a legjobb a Next.js stack-ben. Driver adapter (`@prisma/adapter-pg`) modell — **a régi library engine megszűnt Prisma 7-ben**, csak adapter-alapú működés.

### 4. Migrációs sorrend
**🟢 Fokozatos, entitás-onként** — minden fázis után smoke + commit, sokkal kevesebb risk mint mindent egyszerre. Kemény átállás (nincs JSON fallback).

## Stack

- **Prisma 7.8.0** + `@prisma/adapter-pg`
- **node-postgres (`pg`)** mint connection pool
- **tsx** a `prisma/seed.ts` futtatásához
- **dotenv** a CLI tools-hoz (Prisma a runtime-ban a Next.js env-loader-ét használja)
- DB: `kgc-postgres` Docker container (port 5433), DB neve `kgc_berles`, credentials = ugyanaz mint KGC-ERP-nél

## Schema — 6 model (`prisma/schema.prisma`)

| Model | Cél | PK | Méret |
|-------|-----|----|-------|
| `Machine` | bérelhető gép-katalógus | `id: String` (pl. `"ABV 1"`) | 291 sor |
| `ShopProduct` | webshop termékek | `id: String` (pl. `"s01"`) | 12 sor |
| `Booking` | ügyfél-foglalások | `id: String` (`BK-{timestamp}`) | 0 — runtime adat |
| `RentalSettings` | árazási config | `id: Int @default(1)` (singleton) | 1 sor |
| `Contact` | kapcsolat-form leadek | `id: String @default(cuid())` | 0 — runtime |
| `ServiceRequest` | szerviz-intake | `id: String @default(cuid())` | 0 — runtime |

`Booking.machineId → Machine` FK `Restrict` policy-vel: gépet nem lehet törölni amíg foglalás van rá.

JSONB oszlopok: `ShopProduct.specs`, `ShopProduct.rentable`, `Booking.costBearer`, `RentalSettings.holidays / discountTiers / openingHours` — Postgres JSONB az árnyékolt nested struktúrákhoz.

## A 6 commit (sprint összegzés)

| Hash | Cím | Méret |
|------|-----|-------|
| `4772b20` | `feat(db): adopt Prisma + migrate Machine to Postgres (kgc_berles)` | 25 fájl, +2102/-232 |
| `196448d` | `feat(db): migrate ShopProduct to Postgres` | 10 fájl, +146/-140 |
| `d202f34` | `feat(db): migrate RentalSettings to Postgres (singleton row)` | 4 fájl, +115/-55 |
| `35f3f74` | `feat(db): migrate Booking to Postgres` | 7 fájl, +294/-219 |
| `b586f8d` | `feat(db): migrate Contact + ServiceRequest to Postgres` | 3 fájl, +53/-57 |
| `8ed99dd` | `chore(db): drop bootstrap-data.sh, document Prisma in README` | 3 fájl, +99/-46 |

## Architektúra

```
prisma/schema.prisma
   │
   │  prisma migrate dev (DDL → Postgres)
   ▼
kgc_berles DB (kgc-postgres:5433)
   ▲
   │  lib/db.ts  (singleton PrismaClient + adapter-pg, hot-reload safe)
   │
lib/services/<entity>.ts        ← service réteg: mapping + business helpers
   │   (machines, shop, settings, bookings, leads)
   │
   ├─ Server components (admin oldalak, sitemap)
   ├─ API routes (publikus + admin)
   └─ /api/{machines,shop,settings,bookings/unavailable}  ← public hidratáció
       └─ kliens komponensek useEffect/Zustand-on át fetch-elik
```

## Mellékhatások / nem-trivi

### Kliens-side state hidratáció
- `useAppStore` (Zustand) eddig importálta `data/machines.json`-t bundle-time. Most `hydrate()` action a `/api/machines`-ből fetch-eli az 291 gép-listát.
- `<StoreHydrator />` komponens a root layout-ben, useEffect-en triggeli a hidratációt egyszer.
- `app/webshop/page.tsx` és `app/webshop/[id]/page.tsx` (mindkettő `"use client"`) most useEffect + fetch-tel hidratál.

### Prisma 7 driver-adapter (új modell)
Prisma 7 deprekálta a régi library engine-t. **Csak driver-adapter** támogatott:
```ts
import { PrismaPg } from "@prisma/adapter-pg"
import { PrismaClient } from "./generated/prisma"
const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
const prisma = new PrismaClient({ adapter })
```
Pluszban: a `@prisma/client-runtime-utils` peer dep **nem auto-install** — manuálisan kellett `pnpm add`-olni.

### Generator: `prisma-client-js`, NEM `prisma-client`
A Prisma 7 default `prisma init` `provider = "prisma-client"` engine-typed-ot ad, ami "engine type client"-et használ (Edge runtime-célzott, adapter vagy `accelerateUrl` kötelező). Hagyományos Node.js + Postgres setup-hoz a `provider = "prisma-client-js"` értelmes — ez használja az adapter-t common-js módon, és a generated kliens a `lib/generated/prisma/index.js`-ben kerül.

### KGC-4 ERP API fallback megmaradt
A `lib/data-service.ts` még tartalmaz egy `config.useRealApi`-flag-en futó KGC-4 ERP API hívást (`PortalEquipment` → `Machine` mapping). Ez egy **alternatív read-source**, nem az alapértelmezett. Ha KGC-4-be lépés történik majd valamikor, a flag bekapcsolásával működik (write-helyek továbbra is `kgc_berles` DB-be írnak).

## Ellenőrzés

- 8 commit `main`-en (1 baseline + 7 előző + 6 új DB-fázis)
- Working tree clean (commit-ok után)
- DB-ben: 291 Machine, 12 ShopProduct, 1 RentalSettings (seed után), Booking/Contact/ServiceRequest 0 (runtime indul)
- Smoke: `/`, `/berles`, `/webshop`, `/api/machines`, `/api/shop`, `/api/settings`, `/api/bookings/unavailable`, `/api/book` (POST teszt + DB persist + cleanup), `/api/contact` (POST + cleanup), `/api/service` (POST + cleanup) — mind 200, body validátok átmentek
- Sensitive scan minden commit előtt: tiszta

## Új környezet bootstrap (CI / friss klón)

```bash
docker exec kgc-postgres psql -U kgc -d kgc_erp -c "CREATE DATABASE kgc_berles"
# .env beállítás (lásd .env.example) — DATABASE_URL kötelező
pnpm install                       # postinstall futtatja prisma generate-et
pnpm exec prisma migrate deploy
pnpm db:seed
pnpm dev                           # vagy pnpm build && pnpm start
```

## Backup stratégia (új feladat)

A `kgc_berles` DB jelenleg **nincs felvéve** a napi backup rotációba. Azonnal hozzáadandó az `/opt/backups/backup.sh`-hoz (ami a `kgc_erp` DB-t dumpolja már). Backlog item.

## Pending munka

- [ ] **Push GitHub-ra** — 6 új commit lokálban (`4772b20..8ed99dd`), a `git push` futtatása szükséges
- [ ] **Backup**: `/opt/backups/backup.sh` bővítés `kgc_berles` DB-vel
- [ ] **CI** (`pnpm exec prisma migrate deploy` + `pnpm db:seed` lépés a deploy-pipeline-ba ha lesz)
- [ ] **Admin Contact/ServiceRequest inbox** — most a táblák léteznek, de admin UI még nem látja őket. Új Phase 6 lehet.
- [ ] **KGC-4 ERP API integráció** — 4. nagy döntéspont, még nem indítva

## Kapcsolódó

- [[02-Projects/kgc-berles]]
- [[07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial]]
- [[07-Decisions/2026-04-24 Git stratégia — standalone repo + 7 commit + GitHub Flow]]
- [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1]]
- Code: `prisma/schema.prisma`, `prisma/README.md`, `lib/services/*`, `lib/db.ts`
