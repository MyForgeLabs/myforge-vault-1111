---
name: ADR — Agentic-browsing readiness (llms.txt) priorizálás
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, seo, agentic, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — Agentic-browsing readiness (llms.txt) priorizálás

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q7 research-output]] alapján Peti finomítja.

## Kérdés

2026 H2-től a Lighthouse "Agentic Browsing" score (Claude/ChatGPT/Perplexity-crawler-readiness) mérőszám lesz. Megéri-e MOST befektetni az `llms.txt` + `/llms-full.txt` + `schema.org/Product` structured data komplettálásába, vagy várjunk a Sprint D-re?

## Opciók

- (A) **Sprint A-ban azonnal** (llms.txt skeleton + alap schema.org JSON-LD a termék-oldalra)
- (B) **Sprint D-ben (SEO-finalize)** — kompletten egyben
- (C) **Hybrid:** Sprint A = llms.txt skeleton + Product JSON-LD; Sprint D = AggregateRating + ItemList + agentic-browsing finomítás
- (D) **Csak schema.org-ig, llms.txt-t kihagyjuk** (a trend még nem konszolidálódott)

## Tradeoff-mátrix összefoglaló

llms.txt jelenlegi adoption-szint (Anthropic, Vercel, Stripe, Notion már használja), magyar piac érettség, Google-rank impact. Részletek: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q7 — SEO]]

## Várt döntés

Egy konkrét ütemezés + tartalom-template az `/llms.txt`-nek + 5 schema.org JSON-LD generátor specifikáció (Product, Offer, AggregateRating, BreadcrumbList, ItemList).

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
- [[11-wiki/lighthouse-agentic-browsing]]
