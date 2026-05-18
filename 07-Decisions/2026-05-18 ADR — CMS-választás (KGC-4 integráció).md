---
name: ADR — CMS-választás a KGC-4 ↔ kgc-berles integrációhoz
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, cms, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — CMS-választás a KGC-4 ↔ kgc-berles integrációhoz

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q2 research-output]] alapján Peti finomítja.

## Kérdés

A KGC-4 ERP-ben NINCS Article/Blog/Content modul. A kgc-berles Next.js front ~10-30 SEO-landing oldalt + 5-10 blog/promóció cikket fog kiszolgálni magyar nyelven, NEM-tech kontent-szerkesztő (Domi-szerű ember) admin-UI-val. Melyik CMS-stratégiát válasszuk?

## Opciók

- (A) **Strapi 5** — TypeScript, self-hosted, OSS, multi-tenant beta, magyar i18n UI
- (B) **Payload CMS 3** — Next.js-native, self-hosted, OSS, TS-strict, multi-tenant plugin
- (C) **Sanity** — SaaS, Portable Text, GROQ, magyar i18n studio, lock-in közepes
- (D) **Directus** — DB-first, OSS, REST/GraphQL auto-API
- (E) **Next.js + MDX (contentlayer/fs)** — git-backed, NEM-tech ember NEHEZEN tud szerkeszteni
- (F) **Hybrid:** Article modul a KGC-4 Prisma-schemájába kerül (új migráció Zoli-call)

## Tradeoff-mátrix összefoglaló

Részletes mátrix: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q2 — Headless CMS választás|Q2 output]]

## Várt döntés

Egy konkrét győztes a fenti 6 opció közül + bevezetési ütemezés. A "Választott stack" szekcióban: [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1#Választott stack]]

## Kapcsolódó

- [[02-Projects/kgc-erp]]
- [[02-Projects/kgc-berles]]
- [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7]]
- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
