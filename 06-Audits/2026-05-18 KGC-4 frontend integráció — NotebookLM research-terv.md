---
name: KGC-4 ↔ publikus weboldal integráció — NotebookLM deep research-terv
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: [audit, research-plan, kgc-erp, kgc-berles, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles, robbantott-kereso]
session: 2026-05-18-kgc-all
status: research-in-progress
---

# KGC-4 ↔ publikus weboldal integráció — NotebookLM deep research-terv

> **Kontextus:** A [[06-Audits/2026-05-18 KGC-4 ERP v7.0 mélyaudit|KGC-4 mélyaudit]] feltárta a portal-API jelenlegi állapotát + integration-readiness gap-eket. A user (Peti) "teljes körű" kutatást kért NotebookLM-mel, 7 blokkos felépítéssel.
>
> **Cél:** olyan architektúra-dokumentumig eljutni amivel:
> 1. Zoli-call-on konkrét feature-csomagot lehet kérni a KGC-4-hez (Article modul, kép-mezők, SSO-bridge)
> 2. A kgc-berles oldali Next.js BFF-route-okat megtervezzük (proxy + cache + tenant-resolve)
> 3. CMS-választás és deploy-stack döntés (headless CMS vs MDX, ISR-stratégia)
> 4. ADR-jelöltek a `07-Decisions/`-be

## Kutatási blokkok

### 1. ERP-driven katalógus-szinkron patterns

**Q-mag:** Hogyan szinkronizál egy headless ERP-rendszer (NestJS+Prisma+RLS) publikus Next.js katalógussal? Mikor melyik pattern (webhook / poll / event-stream / CDC) jobb? Cache-invalidation, ISR vs on-demand revalidation? Stale-while-revalidate vs full-rebuild?

**Source-kategóriák:**
- Vercel ISR docs + on-demand revalidation
- Next.js 16 caching guides
- Webhook-vs-polling architecture posts (Sanity, Strapi blog)
- Postgres CDC: Debezium, pgBoss, LISTEN/NOTIFY
- Redis Streams + BullMQ as event-bus
- WooCommerce/Shopify product-feed sync patterns
- "Read-replica → public-site" pattern

### 2. Headless CMS választás — Article/Blog/Content modul

**Q-mag:** A KGC-4-ben NINCS Article modul. Külön headless CMS-t használjunk (Strapi/Sanity/Payload/Directus), vagy Next.js MDX/fs-based? Multi-tenant-támogatás, magyar admin UI, ERP-mező-merge (termék-adat ERP-ből + leírás-cikk CMS-ből). Költség, lock-in, host-control.

**Source-kategóriák:**
- Strapi 5 (open-source, self-hosted, multi-tenant beta)
- Payload CMS 3 (Next.js-native, self-hosted)
- Sanity (SaaS, Portable Text, GROQ)
- Directus (open-source, database-first)
- Contentful (enterprise SaaS)
- Keystone 6 (TypeScript-native)
- TinaCMS (git-backed)
- Next.js MDX patterns (next-mdx-remote, contentlayer)
- Hybrid: ERP product + CMS marketing-content merge case studies

### 3. Multi-tenant publikus API design

**Q-mag:** Anonymous-access publikus endpointokon mikor melyik tenant-resolution (Origin header / subdomain / query-param / API-key)? RLS-aware read-only views Postgres-ben. Rate-limit per tenant + bot-protection (hCaptcha, Cloudflare Turnstile). DDoS-mitigation.

**Source-kategóriák:**
- PostgreSQL RLS production patterns
- Supabase RLS + anon-key architecture
- Postgrest auto-API generation
- Cloudflare Turnstile + Workers rate-limit
- AWS API Gateway throttle + tenant-scoping
- Auth0 multi-tenancy patterns
- "Public API for SaaS" engineering posts

### 4. Cross-app SSO — portál-user → public-site

**Q-mag:** A KGC-4 portal-auth OTP/Magic-link alapú (jelszó-mentes). Hogy bridge-eljük a kgc-berles Next.js-felé? NextAuth + JWT shared-secret? OIDC + Keycloak (stub van!)? Cookie-cross-subdomain? GDPR + adatcsökkentés. Magic-link redirect-flow biztonság.

**Source-kategóriák:**
- NextAuth.js v5 / Auth.js docs (JWT, Credentials, Email magic-link providers)
- Keycloak OIDC integration with NestJS + Next.js
- Custom JWT bridge: shared-secret verify cross-app
- Cookie SameSite + subdomain cookies (`*.kisgepcentrum.hu`)
- WebAuthn / passkey trends 2026
- OWASP Auth Cheatsheet
- Engineering blog: "How we built SSO between admin and customer portal"

### 5. Rental/booking ERP↔site integráció specifikus

**Q-mag:** Real-time vs cached availability-calendar (29-nap forward, 5-min-stale tolerable?). Deposit-flow integrálás (Stripe Setup-Intent / Barion / SimplePay kártyás előengedélyezés). Booking → rental conversion atomicity. Late-fee számítás. Race-condition (két user ugyanazt a gépet foglalja).

**Source-kategóriák:**
- Stripe Setup-Intent + manual capture (deposit pattern)
- Barion / SimplePay magyar PSP docs
- Booking-engine architecture: Cal.com, Booking.com case studies
- Concurrent-booking race-condition patterns (DB row-lock, advisory-lock, Redis-lock)
- ICalendar/RFC 5545 availability-export
- Rental-platform engineering: GetYourGuide, Turo, Outdoorsy

### 6. Headless ERP-stack comparison — long-term

**Q-mag:** A KGC-4 = egyedi NestJS+Prisma+BMAD. Reális alternatívák public-site backendnek: Twenty CRM, Odoo, ERPNext/Frappe, Dolibarr. **Long-term:** fejlesztési-teher, host-cost, community-méret, magyar lokalizáció, e-invoice/NAV-online integráció. **Mikor érdemes** standardra váltani, mikor egyedi maradni.

**Source-kategóriák:**
- Twenty CRM (already in KGC-4 integration package)
- Odoo 17/18 (open-source ERP, rental-modul)
- ERPNext + Frappe (Python+JS, rental-extension)
- Dolibarr (PHP, magyar lokalizáció)
- Akeneo PIM (csak termék-katalógus)
- Pimcore (PHP, PIM+DAM+CMS)
- HN/Reddit threads "build vs buy ERP"
- Case studies: small-business ERP transitions

### 7. SEO + structured data ERP-katalógushoz

**Q-mag:** 119+ SEO-landing page (kgc-berles), 416-URL sitemap. Product schema.org JSON-LD per termék. BreadcrumbList + ItemList per kategória. ISR cache-vs-freshness trade-off SEO-szempontból (Googlebot crawls). Agentic-browsing readiness (llms.txt 2025-2026 trend).

**Source-kategóriák:**
- schema.org Product, Offer, AggregateRating specs
- Google Merchant Center + product structured data guidelines
- llms.txt (Anthropic + AI-crawler specs)
- Lighthouse "Agentic Browsing" score (2025 H2-tól)
- Next.js generateMetadata + sitemap.ts patterns
- E-commerce SEO 2026 case studies
- Shopify Headless SEO patterns

### +1. (opt-in szóló) WordPress vs Next.js ERP-frontend comparison

**Q-mag:** A foxxi (Budai Fogszabályozás) WP-Elementor-stack vs a kgc-berles Next.js-stack — mikor melyik győz egy ERP-driven publikus oldalon? Plug-in ökoszisztéma (WPML, WooCommerce, ACF) vs full-control. Hosting-cost. Editorial-control by non-tech (Domi-szerű kontent-szerkesztő).

**Source-kategóriák:**
- WordPress + WooCommerce + ERP-szinkron plugins
- Headless WordPress + Next.js (WPGraphQL)
- Static Next.js vs SSR vs ISR perf benchmarks
- TCO (total cost of ownership) elemzések
- Magyar piaci adatok WP-share vs Jamstack

## Záró szintézis Q

**Q-mag:** A 7 blokk anyaga alapján írj egy **"KGC-4 → publikus weboldal integráció architektúra v1"** dokumentumot. Tartalmazza:

1. **Choosen-stack** + indoklás (CMS, SSO-method, sync-pattern, deposit-PSP)
2. **"Mit kell létrehozni" Zoli-oldalon (KGC-4 PR-ek)** — sorrendben (Article modul / kép-mező-bővítés / SSO-endpoint / CSV-feed)
3. **"Mit kell létrehozni" Peti-oldalon (kgc-berles vagy új repo)** — Next.js BFF-routes, NextAuth setup, CMS-bootstrap, schema.org-generators
4. **Ütemezés** — 3-4 sprint-bontás (mi mehet párhuzamosan)
5. **ADR-jelöltek** (5-8 db) a `07-Decisions/`-be
6. **Kockázatok + mitigation** (RLS-bypass risks, GDPR, MyPOS-stub élesítés)
7. **Long-term skálázódási kérdés** (mikor érdemes a teljes ERP-t standardra váltani vagy maradni egyedinél)

## Várható output

- **`06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7.md`** — per-blokk Q&A markdown citation-okkal (~2-4K token/Q)
- **`06-Audits/2026-05-18 KGC-4 integráció — architektúra v1.md`** — szintézis-dokumentum (~10-15K token)
- **5-8 ADR-jelölt** a [[07-Decisions/]]-be (placeholder fájlokkal, hogy a user később finomítsa)
- **MEMORY.md** új sor: "KGC-4 integráció architektúra v1 elkészült, főbb döntések X/Y/Z"

## Futási paraméterek

- **NotebookLM Deep Research mód** (3-7 perc/Q)
- **Forrás-cél:** 100-200 source (10-30 per blokk)
- **Q-darabszám:** 8 (7 blokk + 1 szintézis)
- **Várható futás:** 60-90 perc
- **Költség:** $0 (NotebookLM ingyenes, Claude API NEM kell)
- **Audit-trail:** minden Q válasz citation-trackel; source-listák külön blokkokra mentve

## Status

- **2026-05-18 08:20** — research-terv véglegesítve, background agent indítva. Várok értesítést.
- **2026-05-18 08:42** — **KÉSZ.** NotebookLM `1e84eed9-d302-42f3-a0ea-1bfe500c8aac`, **161 source ready**, 8 deep-research Q lefutott. Outputok:
  - [[2026-05-18 KGC-4 integráció — research-output Q1..Q7]] — Q1..Q7b consolidated (~90KB, ~22K token)
  - [[2026-05-18 KGC-4 integráció — architektúra v1]] — Q8 szintézis (~22KB, ~5K token)
  - 8 ADR-placeholder a [[07-Decisions/]]-ben (CMS / SSO / Sync / Deposit-PSP / Tenant / Article / BFF / Agentic)
- **Futási idő:** ~20 perc end-to-end (notebook-create → 161 source upload → 8 parallel Q-run → consolidate)
- **Költség:** $0 (NotebookLM)
- **Source-listák:** `/tmp/kgc4-sources-block*.txt` per-blokk; `/tmp/kgc4-research-sources-2026-05-18-dedup.txt` aggregated

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 ERP v7.0 mélyaudit]] — input-audit
- [[02-Projects/kgc-erp]] — KGC-4 project-fájl
- [[02-Projects/kgc-berles]] — Next.js front-projekt
- [[07-Decisions/2026-05-18 KGC-ERP kanonikus repo = zolijavos KGC-4]]
- [[11-wiki/notebooklm-cli-gotchas]] — NotebookLM CLI quirks
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — 17×7 workflow minta
