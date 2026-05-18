---
name: KGC-ERP kanonikus repo = zolijavos/KGC-4 (NEM KGC-3)
type: decision
status: decided
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, "#project/kgc-erp", "#project/kgc-berles"]
---

# KGC-ERP kanonikus repo = `zolijavos/KGC-4`

## Kontextus

A vault [[02-Projects/kgc-erp]] eddig a **KGC-3** repóra mutatott (`repo_prod: /root/projects/kgc` + `repo_dev: /root/projektjeim/kgc` → `origin = https://github.com/zolijavos/KGC-3.git`). Az audit (2026-05-18, [[06-Audits/2026-05-18 KGC-4 ERP v7.0 mélyaudit]]) feltárta:

1. **`/root/projects/kgc` prod path NEM létezik** — törölve, valószínűleg a 2026-05-15 `feedback_docker_prune_safety` incidens kontextusában (lásd Backlog #23).
2. **`/root/projektjeim/kgc` (KGC-3 dev)** parkolt 2026-02-09 óta, 80 commit behind `origin/main`. Upstream is megáll 2026-02-12-nél.
3. **`zolijavos/KGC-4` (külön repó)** = "KGC ERP v7.0 - Tesztelési Fázis (BMAD Phase 5)" — **MA reggel is push-olt rá Zoli** (`fde583b` 2026-05-18 09:30), Sprint 26 W1 D-3 fut, 100+ commit/30 nap density. **Ez az aktív KGC-ERP fejlesztés.**
4. Local clone `/root/projektjeim/KGC-ALL/KGC-4` létezik, de **1337 commit behind** origin/main (2026-03-25 óta érintetlen).

## Döntés

**A kanonikus KGC-ERP repo `https://github.com/zolijavos/KGC-4.git`. A KGC-3 archive-szekcióba kerül.** A vault [[02-Projects/kgc-erp]] project-fájlt ennek megfelelően átírtam.

## Indoklás

- Zoli aktívan fejleszti a KGC-4-et — közeledik a Sprint 26 vége, Phase 5 (Tesztelési) zárás közelében
- A kgc-berles "[#23 KGC-4 ERP integráció: bérlésszámító motor egyesítése](../04-Tasks/Backlog.md)" backlog item **ezzel a repóval értelmes** (a KGC-3 standalone `calculateRentalPrice()` vs. a KGC-4 RentalService 4-állású deposit-tracking + ADR-037/048 árazási motor)
- A `portal-equipment` modul a KGC-4-ben **MÁR készen áll a kgc-berles fogyasztására** anonymous + tenantId-query flow-val — közvetlen integráció ~30 perc wire-up

## Hatás

- [[02-Projects/kgc-erp]] frissítve: `repo: https://github.com/zolijavos/KGC-4.git`, `repo_local: /root/projektjeim/KGC-ALL/KGC-4`, status `production` → `active-development (Phase 5 testing)`, friss state-tábla
- [[02-Projects/Index]] frissítendő: KGC-ERP sor friss URL-lel
- KGC-3 nem törlődik, csak archive-szekcióba: jegyezve hogy `/root/projektjeim/kgc` parkolt és nincs hozzá Zoli-aktivitás
- A jövőbeli ERP-vonatkozású session-pre-load a KGC-4 fájl-pointer-jeire mutat (lásd audit §11)

## Tisztázandó (Zoli-call-agenda)

Az audit §10 10 pontja — főbbek:
1. Verzió-jelölés: `v7.0` (README) vs `3.0.0` (package.json) — szándékos vagy bug?
2. `online-booking` (in-memory) vs `portal-bookings` (Prisma) — melyik az aktív?
3. `portal-equipment` API: `EquipmentType.heroImageUrl` + `galleryImages[]` mikor kerül vissza a select-be?
4. `tenantId` átadás publikus API-n — query-string OK marad-e, vagy Origin-resolve?
5. `apps/kgc-portal` viszonya a tervezett `kgc-berles`-hez (külön marketing-site vs portal-flow-t is meghívja)?

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 ERP v7.0 mélyaudit]] — 11-szekciós audit, fájl-pointerekkel
- [[02-Projects/kgc-erp]] — frissített project-fájl
- [[02-Projects/kgc-berles]] — Next.js bérlés-frontend ami integrálni fog
- [[08-Sessions/2026-05-18-kgc-all]] — session ahol a döntés megszületett
