---
name: ADR — Tenant-resolution stratégia publikus API-n
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, multi-tenant, security, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — Tenant-resolution stratégia publikus API-n

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q3 research-output]] alapján Peti finomítja.

## Kérdés

A KGC-4 multi-tenant (PostgreSQL RLS). A `portal-equipment` MOST `?tenantId=...` query-paramban kapja a tenantot. A `public-inquiry` Origin-header alapú. Hogyan egységesítsük a publikus API-n a tenant-resolve-ot biztonságosan és SEO-kompatibilisen?

## Opciók

- (A) **URL-subdomain** (`elad.kisgepcentrum.hu` vs `berles.kisgepcentrum.hu`)
- (B) **Origin-header** alapú (a public-inquiry-stílus)
- (C) **Query-paraméter** (`?tenantId=...`, jelenlegi portal-equipment)
- (D) **Path-prefix** (`/t/:slug/...`)
- (E) **API-key header** (közéleti API-nak NEM ideális)
- (F) **Env-konstans** (Next.js BFF-ben hardcoded, a publikus felhasználó NEM látja)

## Tradeoff-mátrix összefoglaló

SEO, cache, security, RLS-kompatibilitás. Részletek: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q3 — Multi-tenant API]]

## Várt döntés

Egy konkrét győztes + RLS-aware read-only views implementáció + rate-limit-per-tenant stratégia.

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
