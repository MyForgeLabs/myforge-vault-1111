---
name: ADR — Boulium Friends-MVP foundation stack
type: decision
created: 2026-05-18
updated: 2026-05-18
status: implemented
project: boulium
tags: ["#type/adr", "#project/boulium", "#stack"]
---

# ADR — Boulium Friends-MVP foundation stack (2026-05-18)

## Status

**Implemented.** Az ADR-001 7 nyitott döntése a 2026-05-17-es session óta vég-realizálódott a 2026-05-18-as build-session-ben. Élesben működik: `https://boulium.com` (prod) és `https://dev.boulium.com` (dev).

## Context

A 2026-05-17 Boulium session 7 nyitott ADR-001 döntést hagyott a friends-MVP-foundation-re. A 2026-05-18 session-ben mindegyik eldőlt empirikusan a build közben + 2 NotebookLM deep-research alapján (tech-stack 2026 + advanced features).

## Decisions

### 1. Repo-stratégia — single-app `apps/web/`

**Eredeti javaslat:** pnpm monorepo + turborepo.
**Döntés:** Single Next.js app a `/root/projektjeim/boulium/apps/web/` alatt, monorepo Phase 2-re halasztva amikor `packages/` megjelennek.

### 2. MAPESZ-migráció — most NEM, Phase 3

**Eredeti javaslat:** cherry-pick NSR-client + szamlazz-client + design-artifacts.
**Döntés:** A friends-MVP-hez nincs szükség MAPESZ-örökségre (nem szövetségi platform). A 4-dim cherry-pick mátrix ([[../11-wiki/petanque-cluster-mapesz-cherry-pick]]) életben marad a Phase 3 szövetségi-integrációhoz. A `MAPESZ design-artifacts/` Mac-only marad.

### 3. boulium.blog ↔ boulium.com — külön

**Döntés:** A `boulium.blog` marad self-contained WP (Extra/Divi + Yoast) tartalom-blogként. A `boulium.com` a friends-MVP PWA. Cross-link csak header/footer szintű, közös auth NINCS.

### 4. Hosting — meglévő Hostinger VPS-ek

**Eredeti javaslat:** saját VPS Docker (mfl-server / frankpanama).
**Döntés:** A meglévő Hostinger VPS-eken co-locálva — **$0 extra/mo**:

- **DEV:** `vps-dev-example` (187.77.70.36) — Caddy + PM2 port 3011, kgc-postgres `boulium_dev` DB
- **PROD:** `vps-prod-example` (72.62.92.98) — Nginx + PM2 port 3009, dedikált `boulium-postgres` Docker container port 5436

### 5. Auth — Better Auth (NextAuth helyett)

**Eredeti javaslat:** NextAuth v5 + Google + magic-link.
**Döntés:** **Better Auth** — a NotebookLM deep-research finding: a NextAuth.js v5 maintenance-mode-ba ment 2026-tól, az új projekteket a Better Auth-ra terelik a maintainerek. Better Auth ingyenes self-host, 2FA/passkey/RBAC out-of-box, Drizzle-adapter trivial setup.

- Google OAuth (ingyen)
- Resend magic-link (`send.boulium.com` subdomain, Hostinger Mail-lel kompatibilis — lásd [[../11-wiki/resend-send-subdomain-vs-hostinger-mx]])
- Apple Sign In opt-in későbbre ($99/év Apple Developer + `@privaterelay.appleid.com` cím-fragmentation-handling)

### 6. DB — dedikált boulium-postgres prod-on

**Eredeti javaslat:** dedikált `boulium-postgres` container vagy közös kgc-postgres.
**Döntés:** Két env, két DB:

- **DEV:** közös `kgc-postgres` (már fut a dev VPS-en), új `boulium_dev` DB
- **PROD:** dedikált `boulium-postgres` Docker container (port 5436, saját volume), tiszta isolation a többi prod-projektttől

### 7. (új) Frontend — Next.js 16 + Drizzle + Tailwind v4

- **Next.js 16.2.6** (App Router + Server Actions + RSC) — saját CLAUDE.md figyelmeztet a 15→16 breaking change-ekre
- **Drizzle ORM** (nem Prisma) — lightweight, type-safe, kevesebb runtime-overhead
- **Tailwind v4** `@theme` config-fal — design tokens a `globals.css`-ben
- **Bricolage Grotesque** display + **Geist Sans** body + **JetBrains Mono** score-display (tabular-nums)

### 8. (új) Ranking — Glicko-2 (nem Elo)

A NotebookLM deep-research alapján Glicko-2 a 2026-os ajánlás casual social-sport-app-okra:

- Rating (1500 init)
- Rating Deviation / RD (350 init, smurf-detekt)
- Volatility (0.06 init, consistency tracker)
- Multi-team approach: team-avg rating mint single-opponent, minden játékosra külön update

### 9. (új) Engagement — Smart XP + Stake + Trust + Achievements

- **Smart XP curve:** Fanny-bonus (13:0 → +25), streak-multiplier (3-day 1.1×, 7-day 1.5×), daily-first-bonus (+5), skill-diff (erősebb-ellenfél +5/100rating-diff)
- **XP-stake:** escrow + max-stake 30% + trust-min 50 + dispute-refund — legal safe-harbor (XP-nek nincs fiat-érték, contest-of-skill)
- **Trust-score:** ±1 minden confirm után, −10 minden dispute után, floor 0 ceiling 100
- **24 hardcoded achievement** 4 tier-ben (bronze/silver/gold/special) — auto-grant a match/social/venue trigger-ekre

### 10. (új) Media — Sharp.js + local FS

- Sharp pipeline: `rotate() → strip EXIF → resize → webp({quality:80})`
- Local FS storage: `/var/lib/boulium/uploads/{kind}/{yyyy-mm}/{uuid}.webp`
- Public-serving: Nginx alias (prod), Caddy `file_server` (dev)
- Cloudflare R2 migration **opt-in env-var pattern** kódszinten előkészítve, user-action szükséges

### 11. (új) Geo — OSM Overpass + Haversine

- Venue GPS coordinates (DoublePrecision)
- Haversine distance lib (`lib/geo.ts`)
- OSM Overpass query `leisure=pitch sport=boules` — community court-database
- Broadcast-mode: public/friends/none (presence-szintű)

## Consequences

✅ **$0 extra/mo cost** — meglévő infra reuse + Better Auth self-host + local FS + Resend free tier
✅ **2 user élesben tesztel** (Peti + Javos), 3 meccs sikeresen confirmed, 23 route + 18 tábla
✅ **Skálázható Phase 2-re** — friend-graph, R2-migration, Apple Sign In, MAPESZ-integráció mind add-on

## References

- Research output: `/root/projektjeim/boulium/docs/research/2026-05-18-deep-research-{friends-mvp,advanced-features}.md`
- Session log: [[../08-Sessions/2026-05-18-boulium-petanque-app]]
- Project state: [[../02-Projects/boulium]]
- Bug-csapdák: [[../11-wiki/nextjs-16-server-component-onclick-trap]] · [[../11-wiki/resend-send-subdomain-vs-hostinger-mx]]
</content>
