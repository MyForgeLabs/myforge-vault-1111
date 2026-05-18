---
name: Tartozék-rendszer schema (MachineAccessory M:N)
type: decision
project: kgc-berles
tags: ["#type/decision", "#project/kgc-berles", "#topic/architecture", "#topic/schema"]
created: 2026-05-10
updated: 2026-05-10
---

# Tartozék-rendszer schema — MachineAccessory M:N

## Kontextus

A 2026-05-07 Zsuzsi+Zoli meeting (forrás: NotebookLM `Hang 260507_105416.m4a`) megfogalmazta hogy a kgc-berles katalógusban kezelni kell a **bérgéptartozékokat** — pl. magfúró → koronafúrók, adapterek.

Citat: *„ezek tartozékok, tehát hogy ennek nincs is kauciója, mert ezt külön nem szokták elvinni... kiválasztja az alapgépet, utána jön a bérgéptartozék, ami szintén bérgép, de ugye neki látni kell, hogy mondjuk ahhoz miket tud vinni"*

## Döntés

Új Prisma model + flag + adat-réteg, MVP scope-pal:

```prisma
model Machine {
  // ... existing fields ...
  isAccessory     Boolean @default(false)
  accessoryOf     MachineAccessory[] @relation("BaseAccessories")
  asAccessoryFor  MachineAccessory[] @relation("AccessoryOf")
}

model MachineAccessory {
  baseMachineId  String
  accessoryId    String
  sortOrder      Int     @default(0)
  baseMachine    Machine @relation("BaseAccessories", fields: [baseMachineId], references: [id], onDelete: Cascade)
  accessory      Machine @relation("AccessoryOf",     fields: [accessoryId],   references: [id], onDelete: Cascade)
  @@id([baseMachineId, accessoryId])
  @@index([accessoryId])
}
```

**Migration:** `20260510122403_add_machine_accessories`

### Minden tartozékra:
- **Nincs saját kauciója** — a `dailyPrice` lehet 0 (pl. KF, HA) vagy nem-0 (pl. KF 125: 4500 Ft/nap), de a `deposit` mindig effektíve nulla
- **NEM önállóan bérelhető** — `isAccessory=true`, `listMachines()` kihagyja default-ban (`where.isAccessory=false`), sitemap-ből kihagyja
- **Csak alapgép mellé** — a pultos veszi át; a frontend `MachineAccessories.tsx` csak listázza

## Alternatívák megfontolva

| Alternatíva | Miért nem |
|---|---|
| Egyszerű `parentMachineId String?` self-relation | Egy tartozék csak EGY alapgéphez tartozhat — túl szűk (pl. egy SDS-Max koronafúró több magfúróhoz is jó lenne) |
| `Machine.accessories Json[]` | Nincs FK-integrity, nincs ON DELETE CASCADE, nehéz query-zni |
| Új top-level `Accessory` model | Duplikálná a Machine-mezőket (név, kép, ár); a tartozék "ugyanúgy gép" csak nem önállóan bérelhető |

A M:N + `isAccessory` flag a leg-flexibilisebb és legkevesebb code-duplication.

## Adat-baseline (2026-05-10)

`data.seed/machine-accessories.json`:
```json
{
  "links": [
    { "baseMachineId": "MAG 1", "accessoryId": "KF",     "sortOrder": 10 },
    { "baseMachineId": "MAG 1", "accessoryId": "KF 125", "sortOrder": 20 },
    { "baseMachineId": "MAG 1", "accessoryId": "KF 153", "sortOrder": 30 },
    { "baseMachineId": "MAG 1", "accessoryId": "DCA 3",  "sortOrder": 40 },
    { "baseMachineId": "MAG 1", "accessoryId": "DCA 4",  "sortOrder": 50 },
    { "baseMachineId": "MAG 1", "accessoryId": "HA",     "sortOrder": 60 }
  ]
}
```

A 6 gép (KF, KF 125, KF 153, DCA 3, DCA 4, HA) `isAccessory=true` flag-et kapott a `data.seed/machines.json`-ben.

## Frontend és API

- **API:** `GET /api/machines/[id]/accessories` → `{ accessories: Machine[] }`
- **Service:** `getAccessoriesForMachine(machineId)` (`lib/services/machines.ts`)
- **Komponens:** `MachineAccessories.tsx` — alapgép detail-en (`/machine/[id]`) jelenik meg ha vannak tartozékok; kiemeli hogy "tartozékoknak nincs saját kauciójuk, átvételkor pultnál tudod hozzáadni"
- **Lista-szűrés:** `listMachines()` opció `includeAccessories` (default: false) — `/berles` katalógus, sitemap, search mind kihagyja

## MVP scope (2026-05-10)

**Kiterjedés:** schema + 1 alapgép-baseline (MAG 1 → 6 tartozék) + frontend listázás + kizárás katalógusból/sitemap-ből.

**MVP korlát:** a tartozékok jelenleg **NEM** kerülnek be a `Booking` rekordba. A pultos veszi át manuálisan az igénylista alapján.

## Phase 2 (későbbre)

1. **Multi-machine Booking** — `Booking.accessoryIds: Json` mező vagy új `BookingAccessory` join → frontend-en "+ Tartozék" gomb az alapgép foglalása mellé
2. **Admin UI** — `/admin/machines/[id]` szerkesztőben "Tartozékok" picker (M:N kapcsolat-szerkesztés). Most seed-vezérelt
3. **Több alapgéphez tartozék** — pl. a koronafúrók a magfúró ÉS bizonyos vésőgépek alá is mehetnek (most csak MAG 1 alá kötjük)
4. **Nullás cikkszámú vésőgép-tartozékok behozatala** — Zsuzsi/Zoli állítja össze a konkrét cikkszám-listát; az adat-réteg már ready

## Kódváltozások

| Fájl | Mit |
|------|-----|
| `prisma/schema.prisma` | Új `MachineAccessory` model + `Machine.isAccessory` flag + 2 self-relation |
| `prisma/migrations/20260510122403_add_machine_accessories/migration.sql` | Új tábla + index + flag-oszlop |
| `data.seed/machines.json` | 6 gép (KF, KF 125, KF 153, DCA 3, DCA 4, HA) `"isAccessory": true` |
| `data.seed/machine-accessories.json` | Új fájl: 6 link MAG 1 → tartozékok |
| `prisma/seed.ts` | `MachineSeed.isAccessory?` + `seedMachines` `update: { isAccessory }` + új `seedMachineAccessories()` (delete-then-create idempotens) |
| `lib/services/machines.ts` | `MachineRow.isAccessory?` + `toMachine` mappel + `listMachines({ includeAccessories })` filter + új `getAccessoriesForMachine()` |
| `lib/types.ts` | `Machine.isAccessory?: boolean` opcionális mező |
| `app/api/machines/[id]/accessories/route.ts` | Új API endpoint |
| `components/sections/MachineAccessories.tsx` | Új komponens — fetch + list + "nincs saját kaució" copy |
| `app/machine/[id]/page.tsx` | `<MachineAccessories machineId={machine.id} />` az "Hasonló gépek" előtt |
| `app/sitemap.ts` | `where: { isAccessory: false }` filter — 416 → 410 URL |

## Kapcsolódó

- [[02-Projects/kgc-berles#Tartozék-rendszer ⭐ MVP KÉSZ (2026-05-10)]] — projekt-fájl szakasz
- [[08-Sessions/2026-05-10-kgc-weboldal]] — implementáció session
- [[07-Decisions/2026-05-04 Multi-category rendszer + új árazási szabályok v2]] — előző schema-bővítés
- [[07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma]] — Prisma-alapozás
