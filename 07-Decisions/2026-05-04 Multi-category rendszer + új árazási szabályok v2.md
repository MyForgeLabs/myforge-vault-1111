---
name: KGC-Bérlés multi-category rendszer + új árazási szabályok v2
type: decision
status: accepted
created: 2026-05-04
updated: 2026-05-04
tags: ["#type/decision", "#project/kgc-berles", "#architecture", "#pricing"]
---

# Multi-category rendszer + új árazási szabályok v2

> Az egész napos session során elfogadott architektúra-döntések. Az [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1]] kiegészítése.

## 1. Multi-category schema (Many-to-Many)

**Döntés:** Új `Category` (parentId, slug, path, level, sortOrder, icon, description) + `MachineCategory` (machineId, categoryId, isPrimary, sortOrder) join tábla. A meglévő `Machine.category/subcategory/subsubcategory` 3 string-mező DEPRECATED jelölve, **bidirectional sync** tartja konzisztensen amíg a kolumnák tényleg kiestnek.

**Miért:**
- Egy gép logikailag több kategóriába tartozhat (ipari porszívó = takarító + építkezési porelszívás)
- 3 schema-opció átgondolva: A) M:N proper ⭐ (választott), B) Postgres array, C) Hybrid. Az A tisztább hierarchia, slug-ok SEO-hoz, sort_order admin-DnD-vel
- A bidirectional sync biztosítja, hogy a régi mezőkből élő frontend és az új admin-picker is konzisztens

**Hatás:**
- 119 Category seed (5 fő × ~30 al × ~80 alal a Peti webkönyvtár táblázatából)
- 292 primary + 43 multi-cat MachineCategory entry
- Eloszlás: epitoipari 179 / kerti 66 / faipari 40 / meromuszerek 17 / egyeb 26
- 119 SEO landing-oldal (`/berles/[...path]` catch-all + `generateStaticParams`)
- Sitemap most 416 URL

## 2. Hero infrastruktúra full-bleed

**Döntés:** A category landing-oldalakon a hero kép a teljes viewport hátterét adja (`min-h-[calc(100vh-120px)]`), dark-petrol gradient overlay + fehér headline-text + lefelé pulzáló "Görgess ↓" scroll-indicator. A TrustBar (36/170+/4.9/<15) a katalógus "Bérelhető gépeink" cím alá került.

**Miért:** Peti UX-feedback: a meglévő split-layout túl kicsi és technokrata-érzés. Full-bleed cinematic hero modernebb és immersívebb. A TrustBar bizalmi jelek a katalógus-blokkban is élhetnek, nem szükséges a hero-térben helyet foglalni.

**Implementáció:**
- `PageHero` `heroImage` prop (`heroBackground` mode) — `<Image fill>` + dark gradient overlay (135deg, rgba(10,58,62,0.85→0.30))
- `lib/category-heroes.ts` `getHeroForCategory()` — specifikustól általánosig path-feloldás (level 3 → level 2 → level 1)
- 11 hero-kép (`public/heroes/*.jpeg`, ~700 KB / 16:9 / Pixar-stílus karakter-jelenettel) — Peti generálta nano-banana-val
- A 119 landing-oldal mind kap képet (specifikus 11 + szülő-fallback)

## 3. Új árazási szabályok v2 (Zsuzsi+Zoli kérése)

### 3.a Heti ár fix
**Volt:** `dailyPrice * 5` (5 munkanap)
**Most:** `dailyPrice * 6` (7 nap, 1 ajándék — konzisztens a Tier 7+/1 sávval)

### 3.b Multi-day half-day puffer
**Új algoritmus** (`calculateRentalPrice` `timeBasedDays` blokk):
- 24h-blokkok után fennmaradó óra = `remainder`
- `remainder ≤ 0` → csak teljes napok
- `0 < remainder ≤ halfDayMaxHours` (5h) → utolsó nap **fél**
- `remainder > halfDayMaxHours` → utolsó nap **teljes**

**Régi viselkedés (hibás):** `Math.ceil(hours/24)` → minden órányi átlépés után új teljes nap. Ez ütközött Zsuzsi-Zoli ár-elképzelésével.

### 3.c Per-weekday `latestReturnHour` cap
**Új mező** `OpeningHours.latestReturnHour?: number | null` — a visszahozás legkésőbbi órája az adott napon. Default-ok:
- H–P: 15:00 (3-ig, admin-felvételre marad 1 óra a 16:00 záráshoz)
- Szombat: 12:00 (dél)
- Vasárnap: null (zárva — nem lehet visszahozni)

A `DetailBookingCard` `returnHourOptions()` cap-eli erre. A meglévő `sameDayLatestPickupHour: 15` a pickup-ra, ez a return-re.

### 3.d Default return-óra szinkron
Multi-day esetén ha a user nem nyúlt hozzá a return-óra select-hez → automatikusan = pickupHour (másnap ugyanaz az óra). User override flag (`useRef`) — manuális választás után már nem szinkronizál.

### 3.e Early-return half-day CSAK overnight (<24h)
**Pontosítás:** az "early-return half-day" szabály (returnHour ≤ earliestReturnHour=7) csak akkor aktív, ha a teljes hossz < 24h (`fullDays === 0`, overnight scenario). Több napos bérlésnél a 5h puffer-algoritmus dönt.

**Peti hibajelentés:** 5/9 9:00 → 7/9 7:00 = 46h (multi-day) → most 2 teljes nap, NEM 1.5 (a régi viselkedés, ami az "early-return"-t multi-day-re is alkalmazta).

## 4. Utánfutó FÉL ÁRA gép mellé (KGC üzleti szabály)

**Bevezetve 2026-05-04, Zsuzsi+Zoli megerősítés.**

- Normál utánfutó: **10 000 Ft / nap**
- KGC gép mellé bérelve: **5 000 Ft / nap (-50%)**
- Kaució: 40 000 Ft (nem változik)

**Kommunikáció:** minden landing-oldal "Combo" card-on + Instagram carousel Slide 3-on kis KC orange accent-badge: `"✓ Utánfutó FÉL ÁRON — csak géphez"`.

## 5. Production-ready setup

- **`kgc-berles.service` systemd** (`/etc/systemd/system/`) — enabled, prod build (`pnpm exec next start -p 3004`), reboot-proof, `/var/log/kgc-berles.log`
- **`kgc_berles` napi backup** `/opt/backups/backup.sh`-ban (3:00, ~38 KB)
- **`pnpm build` sikeres** + 2 pre-existing TS hiba javítva (KioskLayout `renderInput`, bookings.ts `costBearer` ternary spread)
- **Admin jelszó** `kgc-admin-dev-2026` (env-ből, NEM `kgc-admin-2026`)
- **Domain + SSL még pending** — most `187.77.70.36:3004` port

## Kapcsolódó

- [[02-Projects/kgc-berles]]
- [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1]] — előd
- [[07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma]] — schema-alap
- [[11-wiki/ai-prompt-fidelity-locks]] — Instagram carousel prompt-tár alapja
- [[08-Sessions/2026-05-04-kgc-weboldal]] — implementáció részletek
