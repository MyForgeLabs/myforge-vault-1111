---
name: Prisma compound unique key — null component quirk
type: wiki
tags: [wiki, prisma, db, gotcha]
created: 2026-05-09
updated: 2026-05-09
---

# Prisma compound unique key — null-component quirk

A Prisma `@@unique([a, b, c])` compound-unique constraint-ben **nem lehet** `null` érték a `where`-ben, mert a Prisma a generált TypeScript-where input-ot nem-null mezőkkel definiálja.

## Tünet

```
Argument `departmentId` must not be null.
    at throwValidationException ...
```

Tipikus eset: org-szintű KPI rekord (departmentId=null) upsert-elése egy `@@unique([organisationId, departmentId, period, periodStart, metric])` constraint-en.

## Miért

A Prisma `WhereUniqueInput`-ja a compound-unique kulcsból generált — ha bármelyik mező `null`-able, a runtime ennek ellenére dobja a fenti hibát. Ez ismert quirk (lásd [prisma/prisma#3197](https://github.com/prisma/prisma/issues/3197), [#5048](https://github.com/prisma/prisma/issues/5048)).

## Megoldás 1 — `findFirst + create/update` (egyszerű, de nem atomic)

```ts
const existing = await prisma.kPIMetric.findFirst({
  where: {
    organisationId: org.id,
    departmentId: null,
    period: 'MONTH',
    periodStart,
    metric: 'sick_days',
  },
});

if (existing) {
  await prisma.kPIMetric.update({ where: { id: existing.id }, data: { value } });
} else {
  await prisma.kPIMetric.create({ data: { ... } });
}
```

Hátrány: race condition két concurrent insert között. Seed-script-ben OK; production write-path-on `$transaction`-ba kell tenni.

## Megoldás 2 — sentinel string id helyett null

A `null` helyett egy sentinel értéket használj (pl. `'__org__'`) a `departmentId`-re ha a row globális (nem departmenthez kötött). Hátrány: a foreign-key reláció hibás (mert nincs `__org__` sor a `departments`-ben), tehát csak nullable FK-mentes mezőkre működik.

## Megoldás 3 — két index részleges átfedéssel

A schemában szét kell szedni a compound-unique-ot két index-re:

- `@@unique([organisationId, period, periodStart, metric], where: { departmentId: null })` — org-szintű egyediség
- `@@unique([organisationId, departmentId, period, periodStart, metric])` — department-szintű

A `where: ...` szintaktika viszont MySQL-ben Prismánál **nem támogatott** (csak Postgres+ partial index). MySQL-en csak az 1-es vagy 2-es megoldás megy.

## Példa a kódban

[apps/balance/packages/db/prisma/seed-balance.ts](../02-Projects/teszt-eu.md) — `KPIMetric` org-szintű seed-elése.

## Kapcsolódó

- [[02-Projects/teszt-eu]] — Balance Wellbeing 2.0 app, ahol ez a probléma előjött
