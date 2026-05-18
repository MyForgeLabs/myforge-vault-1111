---
name: Prisma-quirk PostgreSQL-driver család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "prisma", "postgresql", "orm", "quirk", "taxonomy", "evergreen"]
---

# Prisma-quirk PostgreSQL-driver család taxonomy

> [!info] TL;DR
> A vault-ban **24 Concept + 9 wiki-említés** beszél „Prisma"-quirk-ről, de a tényleges használat **5 különálló quirk-családot** keveredik: (1) **setup/install-quirk** (Prisma 7 driver-adapter + manuális deps), (2) **compound-unique null-quirk** (WhereUniqueInput runtime fail), (3) **seed-merge quirk** (upsert.update felülír adat-mezőket), (4) **migration-quirk** (`migrate dev` ≠ `generate`, DROP COLUMN risk), (5) **service-layer / RLS multi-tenancy quirk** (anonymous-tenantId + portal-equipment flow). Ez a wiki disambiguálja a 5 családot, mind alfa-pattern-eire pointer-rel.

## Cluster-members (vault Concept-corpus)

| Concept | Család | Forrás |
|---|---|---|
| Prisma 7 | setup | ADR/2026-04-26 |
| @prisma/adapter-pg | setup | ADR/2026-04-26 |
| driver-adapter modell | setup | ADR |
| provider = prisma-client-js (NEM 'prisma-client') | setup | session/2026-04-24 |
| @prisma/client-runtime-utils manuális pnpm add | setup | session/2026-04-24 |
| node-postgres (pg) | setup | ADR |
| prisma.kPIMetric.update existing.id | compound-unique-null | wiki |
| Prisma WhereUniqueInput | compound-unique-null | wiki |
| Prisma upsert non-null compound-unique fields | compound-unique-null | wiki |
| schema nullable field runtime block | compound-unique-null | wiki |
| @@unique([a,b,c]) | compound-unique-null | wiki |
| MySQL Prisma partial-index block | compound-unique-null | wiki |
| Prisma seed upsert.update overwrite | seed-merge | wiki/prisma-seed-admin-edit-protected |
| prisma.machine.upsert update branch | seed-merge | wiki |
| seed sync only flag fields not data fields | seed-merge | wiki |
| separate-sql-script avoids seed-admin-edit | seed-merge | wiki |
| Prisma 7 migration `prisma generate` | migration | session/2026-05-10 |
| Schema DROP COLUMN | migration | session/2026-05-04 |
| MAPESZ dev: prisma migrate dev + db seed | migration | session/2026-04-24 |
| prisma/seed.ts requires tsx | setup/migration | ADR |
| anonymous-tenantId flow portal-equipment | service-layer | MEMORY.md |
| RLS multi-tenancy | service-layer | MEMORY.md |
| 9 Prisma models (Balance schema) | service-layer | session/2026-05-08 |

## Az 5 quirk-család

### 1. Setup / install-quirk (Prisma 7 driver-adapter)

**Mintázat:** Prisma 7-tel **eltűnt a library-engine**, csak driver-adapter modell — több manuális lépés a default-install-on felül.

- **Kötelező lépések:**
  1. `pnpm add @prisma/adapter-pg` (driver-adapter)
  2. `pnpm add @prisma/client-runtime-utils` (manuális, nem auto-pulled — KGC-berles bug)
  3. `pnpm add pg` (node-postgres)
  4. `provider = 'prisma-client-js'` a schema-ban (NEM `'prisma-client'`)
  5. `prisma/seed.ts` requires `tsx`
- **Trigger:** új Prisma 7 projekt setup
- **Anti-pattern:** library-engine `provider = 'library'` → 7.0+ NEM létezik többé
- **Stack:** KGC-berles, KGC-4 ERP, Balance MVP mind Prisma 7-en
- **Verzió:** 7.8.0 (ADR/2026-04-26)

→ ADR: [[../07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma]]

### 2. Compound-unique null-quirk (WhereUniqueInput runtime fail)

**Mintázat:** `@@unique([a, b, c])` compound-unique constraint-ben **bármelyik nullable mező** → runtime fail (`Argument must not be null`), schema nullability ellenére.

- **Tünet:** `prisma.kPIMetric.upsert({ where: { ... departmentId: null } })` → `throwValidationException`
- **Ok:** Prisma generated `WhereUniqueInput` non-null type-okkal, runtime-check független a schema nullability-tól
- **Workaround:** `findFirst + create/update` (2 query, NEM atomic) VAGY raw SQL upsert (atomic, de Prisma-type-safety vész)
- **Cross-DB:** MySQL Prisma ezenfelül `@@unique where syntax`-ot is block-ol + partial-index NEM support-olt
- **GitHub issues:** prisma/prisma#3197, #5048 (open óta 2020-)

→ Alfa-pattern: [[prisma-compound-unique-null-quirk]]

### 3. Seed-merge quirk (`upsert.update` felülír adat-mezőket)

**Mintázat:** `prisma.machine.upsert({ where, create, update })` **minden seed-run-on overwrite-olja** a meglevő rekordokat — admin edit-elt értékek elvesznek.

- **Tünet:** admin frissít egy gép-árat a portal-on, következő `prisma db seed`-en visszaáll az alap-érték
- **Workaround:** `update` branch CSAK flag-mezőket szinkronizál (pl. `isAccessory`, `isActive`), adat-mezőket (név, ár, leírás) NEM
- **Ár-frissítés** külön SQL script-tel (NEM seed-en keresztül), pl. Excel → openpyxl piros-font 3-way diff → SQL → admin-edit védve
- **Stack:** KGC-berles `prisma/seed.ts` 2026-05-11
- **Reusable:** flag-only-update branch minden production-seed-en kötelező

→ Alfa-pattern: [[prisma-seed-admin-edit-protected]] + [[excel-redmark-3way-diff-workflow]]

### 4. Migration-quirk (`migrate dev` ≠ `generate`, DROP COLUMN)

**Mintázat:** Prisma 7-ben `prisma migrate dev` **NEM** trigger-eli `prisma generate`-t auto — külön lépés. Plus DROP COLUMN production-on risk-y, X-hét stabilitás után érdemes csak.

- **Tünet:** `migrate dev` után `@prisma/client` régi típusú → TypeScript-error a hozzáadott modell-mezőkön
- **Workaround:** `prisma migrate dev && prisma generate` (két lépés), VAGY `prisma migrate dev && pnpm install` (post-install hook)
- **DROP COLUMN protokoll:** új migration `field marked deprecated` → X hét stabil futás → új migration `DROP COLUMN`
- **Dev-env:** MAPESZ flow `npx prisma migrate dev + npx prisma db seed`, kötelező sorrend

### 5. Service-layer / RLS multi-tenancy quirk (anonymous-tenantId)

**Mintázat:** B2C portal API-nak **anonymous-tenantId** kell (no auth, public listing) — de RLS policy minden query-n tenantId-t vár.

- **Tünet:** `/api/v1/portal/equipment` public endpoint, RLS block-ol mert `tenantId IS NULL`
- **Workaround:** `anonymous-tenantId` constant (UUID, pl. `00000000-0000-0000-0000-000000000000`) + RLS policy `tenantId = current_tenant_id() OR is_public = true`
- **Stack:** KGC-4 ERP `apps/kgc-portal` B2C → `portal-equipment` API → kgc-berles fogyasztja
- **NestJS 10 + Prisma + PG16 + RLS** stack-en érvényes (KGC-4-en mért)

→ ADR: [[../07-Decisions/2026-05-18 KGC-ERP kanonikus repo = zolijavos KGC-4]]

## Mintázat — projekt-szintű döntés-mátrix

| Új projekt? | Stack-választás |
|---|---|
| Greenfield Postgres backend | Prisma 7 + adapter-pg + driver-adapter |
| Multi-tenant B2C portal | + RLS policy + anonymous-tenantId const |
| Admin-edit-able seed-data | flag-only update branch kötelező |
| Compound-unique with nullable | NE Prisma upsert, raw-SQL VAGY findFirst+create/update |
| Migration DROP COLUMN | X hét stable warmup, deprecated-flag először |
| MySQL helyett Postgres | Prisma feature-set jobban support-olt |

## Anti-pattern

- ❌ **„Prisma 7 install = `pnpm add prisma @prisma/client`"** — hiányzik adapter-pg + runtime-utils + pg, build-time-fail
- ❌ **„Schema nullable → runtime null OK compound-unique-ban"** — NEM, [[prisma-compound-unique-null-quirk]]
- ❌ **„upsert overwrite admin-edit OK"** — NEM, admin-data elveszik minden seed-run-on
- ❌ **„migrate dev → kész"** — NEM, `prisma generate` külön lépés
- ❌ **„DROP COLUMN seed-after"** — production-on adat-vesztés, deprecated-flag először
- ❌ **„RLS + public endpoint = anon role"** — NEM, anonymous-tenantId const + policy `is_public` flag
- ❌ **„MySQL Prisma = Postgres Prisma minus pg-features"** — partial-index, `@@unique where` MySQL-en hiányzik
- ❌ **„`provider = 'prisma-client'` Prisma 7-en"** — `prisma-client-js` kell, session/2026-04-24 bug

## Reusable szabály — minden Prisma-projekt indulásakor

```bash
# 1. Setup
pnpm add prisma @prisma/client @prisma/adapter-pg @prisma/client-runtime-utils pg
pnpm add -D tsx

# 2. Schema header
generator client {
  provider        = "prisma-client-js"   # NEM "prisma-client"
  previewFeatures = ["driverAdapters"]
}

# 3. Seed protocol (admin-edit-protected)
# update branch CSAK flag-mezőket szinkronizál

# 4. Migration sequence
pnpm prisma migrate dev --name <slug>
pnpm prisma generate                      # KÖTELEZŐ külön lépés Prisma 7-ben

# 5. Compound-unique nullable mező?
# → NE upsert, raw SQL VAGY findFirst+create/update
```

## Kapcsolódó

- [[prisma-compound-unique-null-quirk]] — alfa-pattern: család 2
- [[prisma-seed-admin-edit-protected]] — alfa-pattern: család 3
- [[excel-redmark-3way-diff-workflow]] — család 3 sister: külön SQL ár-frissítés
- [[migration-pattern-family-taxonomy]] — meta: migration-strategy taxonomy
- [[../07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma]] — alapító ADR
- [[../07-Decisions/2026-05-10 Tartozék-rendszer schema (MachineAccessory M-N)]] — M:N self-relation Prisma
- [[../07-Decisions/2026-05-18 KGC-ERP kanonikus repo = zolijavos KGC-4]] — service-layer (család 5)
- [[../02-Projects/superintelligent-vault]] — Memgraph/Prisma stack mention
- [[mgclient-autocommit-silent-rollback]] — analóg PG-driver quirk Memgraph-on
- [[../05-Memory/Infrastructure]] — KGC Postgres host-info

## Forrás

- KO-DB facts 1084, 1085, 1620, 1621, 1628, 1629, 1660, 1663, 4680, 4681, 4699, 4710, 4712, 4722, 4724, 4747, 4748, 5537, 5547–5553, 5588, 5590, 8952, 8961–8964, 9062, 10589, 10859, 11447, 10368
- Memory bullet: KGC-4 ERP NestJS 10 + Prisma + PG16 + RLS (2026-05-18 audit)
- Memory bullet: KGC-berles seed.ts 2026-05-11 admin-edit-protected
- 9 Prisma-érintő ADR/wiki/session forrás (lásd cluster-members tábla)
