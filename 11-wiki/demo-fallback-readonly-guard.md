---
name: demo-fallback-readonly-guard
description: Bemutató/preview módban a demo-fallback session NEM lehet írható — különben a seed user valódi adatait módosítja. isDemo flag a session-modellben, guard minden mutation route-on
type: project
created: 2026-05-12
updated: 2026-05-19
tags: ["#type/reference"]
tag_backfill: 2026-05-19
---
# Demo-fallback session = read-only mirror

## A pattern

Egy "demo / preview / pilot" mód, ahol bárki a /belepes oldalra látogató megnyithat egy gombbal egy létező seed-user nézetét — login nélkül, csak böngészéshez. A Kinda Balance-app `BALANCE_PILOT_ORG_SLUG` env-var alapján csinálta ezt: cookie nélkül a `getSession()` egy szintetikus demo-session-t adott vissza ami **ugyanazt a `userId`-t** használta mint a valódi seed Anna.

## A csapda

Ha a mutation route-ok (earn / redeem / submit / update) **nem ellenőrzik** hogy a session demo-é vagy valódi, akkor a "Demó megnyitása" gombra kattintó látogatók **valódi módosításokat** tudnak végrehajtani a seed user nevében. Konkrét incident 2026-05-11-én: bárki a `balance.example-balance.local/belepes` → "Demó megnyitása" → "Jutalombolt → Adomány 1000 Ft → Beváltás" útvonalon **Anna 1500 Ft tárcájából** vont volna le 1000 Ft-ot. A "demó" feliratot olvasva a látogató úgy gondolta hogy ez izolált.

## A javítás

A session-modellben **már szándékosan** benne van `isDemo: boolean` (a demo-fallback igaz, a valódi login false), csak nem volt használva. Minden mutation route első sorában:

```typescript
const session = await getSession();
if (!session) return NextResponse.json({ error: 'UNAUTHORIZED' }, { status: 401 });
if (session.isDemo) return NextResponse.json({ error: 'DEMO_READ_ONLY' }, { status: 403 });
```

Form-encoded POST esetén redirect URL-be `?error=demo_read_only` query-paraméterrel jelez az UI-nak, hogy emberi olvasható üzenetet mutasson.

## Hol érvényes

- **Earn / Redeem / Pay** endpoint-ok — bármilyen wallet- vagy egyenleg-módosító
- **Submit / Update / Delete** endpoint-ok — bármilyen DB-write
- Read-only endpoint-okon (`/me`, `/list`, `/preview`) **NEM** kell guard — szabadon nézhetik

## Dokumentációs felelősség

A "Demó megnyitása" gomb mellett/dialógusban szövegesen ki kell mondani: **"Anna valódi nézete — bármilyen kattintás itt nem ment, csak böngészéshez"**. A "nem perzisztál" / "in-memory" megfogalmazás félrevezető, mert a session tényleg a DB-ből hidratálódik, csak a write-okat tiltjuk.

## Kapcsolódó

- [[cross-subdomain-cookie-session-bridge]] — a session-cookie-architektúra ami a `isDemo` flag-et hordozza
- Incident: `08-Sessions/2026-05-11-kinda-project-2.md` 20:00 event
- Commit: `46a4b62` "balance: lock demo-fallback sessions to read-only"
