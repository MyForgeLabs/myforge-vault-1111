---
name: ADR — Article modul KGC-4 ERP-ben vagy külön CMS-ben
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, content, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — Article modul KGC-4 ERP-ben vagy külön CMS-ben

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q2 research-output]] alapján Peti finomítja.

## Kérdés

A KGC-4 ERP-ben NINCS Article/Blog/Content modul. Két fő útvonal:
1. **Új Article modul a KGC-4 Prisma-schemájában** — Zoli új epic-feature, ~3-5 SP
2. **Külön headless CMS** (Strapi/Payload/Sanity) — Peti deploy-olja

A választás összefügg a CMS-választás ADR-rel: [[2026-05-18 ADR — CMS-választás (KGC-4 integráció)]].

## Opciók

- (A) **KGC-4 saját Article modul** — multi-tenant out-of-box, Zoli admin-UI-t épít hozzá
- (B) **Külön CMS** (Strapi/Payload/Sanity) — gyorsabb spin-up, magyar editorial-UX
- (C) **Hybrid:** Equipment-leírás a KGC-4-ben (`EquipmentType.descriptionMd`), önálló cikk-tartalom külön CMS-ben

## Tradeoff-mátrix összefoglaló

Long-term lock-in, single-source-of-truth elv, Zoli kapacitás, magyar editorial UX. Részletek: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q2 — CMS]]

## Várt döntés

Egy konkrét győztes + a `2026-05-18 ADR — CMS-választás` ADR-rel egyező döntés.

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
- [[2026-05-18 ADR — CMS-választás (KGC-4 integráció)]]
