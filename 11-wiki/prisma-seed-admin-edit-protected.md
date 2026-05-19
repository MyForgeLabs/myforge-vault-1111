---
name: prisma-seed-admin-edit-protected
description: Prisma seed `upsert.update`-jét csak biztonsági (flag) mezőkre korlátozzuk admin-edit-védelemhez — gotcha hogy data-frissítés külön SQL script
type: wiki
tags: ["#type/reference", "#tech/prisma"]
created: 2026-05-11
updated: 2026-05-19
tag_backfill: 2026-05-19
---
# Prisma seed admin-edit-védett upsert + külön data-update flow

## Probléma

Prisma `prisma.x.upsert({ where, create, update })` mintában az `update` ág minden seed-futáskor felülírja a meglévő rekordot. Ha az admin UI is írhatja ugyanazokat a mezőket (ár, név, leírás), akkor a `pnpm db:seed` **elveszíti** az admin változtatásait — visszaállítja a json-baseline-ra.

## Megoldás-minta

Az `update` ágban CSAK olyan mezőket szinkronizálunk vissza amik **biztosan a json az igazság-forrás** (flag-ek, kategória-besorolás, schema-szintű mezők). Pl. KGC-berles-ben:

```ts
await prisma.machine.upsert({
  where: { id: m.id },
  create: { /* minden mező a json-ból */ },
  update: { isAccessory: m.isAccessory ?? false },  // csak ez!
})
```

**Következmény:** ha a `data.seed/machines.json` ár-mezője változik (pl. Excel-csere bulk update), a `pnpm db:seed` **NEM** írja át a DB-t. Külön data-update kell.

## Külön data-update flow (példa: KGC-berles 2026-05-11)

1. **Python diff-script** — old `machines.json` vs új xlsx → `/tmp/apply.sql` (BEGIN/COMMIT, csak az érintett mezőkre `UPDATE`)
2. **Backup** `data.seed/_archive/machines.json.bak.<timestamp>`
3. **Json frissítés** (új baseline) — hogy a JÖVŐBELI `pnpm db:seed` ne haljon meg (új gépeknél az `upsert.create` ágat futtatja)
4. **DB apply** `psql -f /tmp/apply.sql` (4 DELETE + 121 UPDATE)
5. **`pnpm db:seed`** új gépeket felveszi + accessory/category-rebuild (a `deleteMany` + recreate idempotens szakaszokban)
6. **Build + restart** `pnpm build && systemctl restart <service>`

## Mikor használd

- Multi-actor data ownership: admin UI + seed-script + esetleg külső API (Excel-csere, ERP-sync)
- Idempotens seed kell de admin-edit nem veszhet el
- Bulk data-frissítés ritka esemény (havonta-negyedévente, NEM minden deploy)

## Mikor NE használd

- Append-only adat (Booking, Contact, ServiceRequest) — admin nem szerkeszti vissza a seed-be
- Pure-seed adat (Category-tree, RentalSettings singleton) — `update: {}` vagy `update: { name, sortOrder, ... }` mind OK

## Anti-pattern

```ts
// ❌ NE: minden mezőt szinkronizál
update: { ...m }  // → admin-edit elvész

// ❌ NE: csak az update üres
update: {}  // → flag-mezők (isAccessory, isPublished) sem szinkronizálódnak
```

## Kapcsolódó

- KGC-berles: `prisma/seed.ts` (2026-05-11 verzió, [[02-Projects/kgc-berles]])
- Tartozék-rendszer ADR: [[07-Decisions/2026-05-10 Tartozék-rendszer schema (MachineAccessory M-N)]] — itt vezettük be az `isAccessory` flag-szinkronizációt
- Excel-csere katalógus-frissítés flow: [[11-wiki/excel-redmark-3way-diff-workflow]]
