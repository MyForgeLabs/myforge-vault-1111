---
name: Cross-subdomain cookie session bridge
type: wiki
tags: ["#type/reference", "#tech/nextjs"]
created: 2026-05-09
updated: 2026-05-19
tag_backfill: 2026-05-19
---
# Cross-subdomain cookie session bridge

Két különálló Next.js app (`beta.example-balance.local` és `balance.example-balance.local`) megosztja a `kinda_user` HMAC-aláírt session cookie-t — egy login a `beta.example-balance.local/belepes`-en, a user authentikáltan landol a `balance.example-balance.local/`-n.

## Mire jó

Több domain alatti app-pár (pl. `beta.example-balance.local` + `balance.example-balance.local`) közös user-session-jéhez:

- Egy login flow (ne kelljen kétszer jelszót megadni)
- Közös user-pool ugyanazon a DB-n
- Külön Next.js build, de "single sign-on" érzet

## Komponensek

### 1. Cookie attribútumok

A login-issuer (`beta.example-balance.local`) a cookie-t **közös szülő-domain-re** kell hogy állítsa:

```ts
cookies().set('kinda_user', `${payloadB64}.${sig}`, {
  domain: '.example-balance.local',     // KÖTELEZŐ — különben csak a saját subdomain-en él
  path: '/',
  httpOnly: true,
  secure: true,
  sameSite: 'lax',
  maxAge: 8 * 3600,
});
```

A pont előtag (`.example-balance.local`) a böngésző számára azt jelenti: "ez érvényes minden `*.example-balance.local`-ra".

### 2. Közös HMAC-secret

Mindkét app `.env.local`-jában AZONOS `USER_SESSION_SECRET` szerepeljen — különben a verifikáció bukik:

```bash
# beta-web/.env.local + balance-web/.env.local
USER_SESSION_SECRET=824412fa6453acf4cbd69d79465f6e77a3b58b4dea100e000cbac26f2328bcc6
```

### 3. Verify-only az egyik oldalon — DE ugyanaz a payload-shape

A login-flow csak az `issuer`-app-ban (`beta.example-balance.local`) él. A `balance.example-balance.local` csak **verifikál**.

> [!warning] A cookie payload formátumát a két app **azonosan kell várja**.
> Korábbi verzió ezen a wiki-n JSON-payload-ot mutatott; ez **nem** kompatibilis a Kinda kanonikus formátummal. A 2026-05-11-es session derítette ki hogy a két app eltérő shape-et várt → minden valódi login csak demo-fallback-ig jutott. Az alacsonyabb-trust végén (verify-only) **másoljátok le pontosan** az issuer formátumát.

A Kinda kanonikus formátum (issuer: `apps/web/lib/user-session.ts`):

```
kinda_user = "user.<userId>.<expiresAtMs>.<sigBase64url>"
sig = HMAC-SHA256-base64url(`user.<userId>.<expiresAtMs>`, USER_SESSION_SECRET)
```

A cookie **csak `userId`-t hordoz**; a role/email/orgId minden requestben DB-lookuppal jön (cheap, egy indexelt findUnique). Ez tartja a cookie-t kicsinek és a DB-t a forrásnak.

```ts
// apps/balance/lib/kinda-user-cookie.ts — verify-only mirror
import { createHmac, timingSafeEqual } from 'node:crypto';

export function verifyKindaUserCookie(raw: string | undefined | null) {
  if (!raw) return null;
  const parts = raw.split('.');
  if (parts.length !== 4) return null;
  const [role, userId, expiresAtStr, sig] = parts;
  if (role !== 'user' || !userId) return null;
  const expiresAt = Number(expiresAtStr);
  if (!Number.isFinite(expiresAt) || expiresAt < Date.now()) return null;
  const expected = b64url(createHmac('sha256', process.env.USER_SESSION_SECRET!)
    .update(`${role}.${userId}.${expiresAt}`).digest());
  const a = Buffer.from(sig), b = Buffer.from(expected);
  if (a.length !== b.length) return null;
  return timingSafeEqual(a, b) ? { userId, expiresAt } : null;
}

// apps/balance/lib/session.ts — hydrate with DB lookup
export async function getSession(): Promise<BalanceSession | null> {
  const raw = (await cookies()).get('kinda_user')?.value;
  const verified = verifyKindaUserCookie(raw);
  if (!verified) return null;
  const user = await prisma.user.findUnique({
    where: { id: verified.userId },
    select: { id: true, email: true, role: true, organisationId: true, isActive: true },
  });
  if (!user?.isActive) return null;
  return { userId: user.id, email: user.email, role: user.role, organisationId: user.organisationId ?? undefined, exp: Math.floor(verified.expiresAt / 1000) };
}
```

### 4. Issuer helper minden cookie-író route-on

A `Domain=.example-balance.local` opciót **minden** auth-route-on egyszerre kell beállítani (login, signup, magic-link verify, google callback, verify-email, reset/complete, **logout** is). Egyetlen `applyUserCookie(res, userId)` / `clearUserCookie(res)` helper a `user-session.ts`-ben — ne ismételd a 7 helyen a `{httpOnly, secure, sameSite, path, domain, maxAge}` blokkot.

```ts
// apps/web/lib/user-session.ts
export function userCookieOptions() {
  const domain = process.env.SESSION_COOKIE_DOMAIN;  // ".example-balance.local" prod-on, üres dev-en
  return { httpOnly: true as const, secure: true as const, sameSite: 'lax' as const, path: '/' as const, ...(domain ? { domain } : {}) };
}
export function applyUserCookie(res: NextResponse, userId: string) {
  const c = issueUserCookie(userId);
  res.cookies.set(c.name, c.value, { ...userCookieOptions(), maxAge: c.maxAge });
}
```

## Gotcha-k

- **Cookie-formátum egyetlen helyen kell definiálva legyen.** A 2026-05-11-es incidens: a Balance JSON-payload-ot várt, a kinda-web 4-segment string-et küldött; verify mindig bukott → demo-fallback eltakart mindent → e2e PASS, de valódi user-login értelmetlen. **Tanulság:** ha lehetséges, a verify-logika közös `packages/`-ben éljen; ha duplikálsz, **ne a kódot másold át, hanem az issuer formátumát**, és diff-eljen a két fájl HMAC algoritmusa identikusan (sha256 vs sha512, hex vs base64url, payload-stringification).
- **DB-hydrate vs. mindent-a-cookie-ba.** A Kinda cookie csak `userId`-t hordoz; role/email/orgId minden requestben DB-lookuppal jön. Cheap (egy indexelt findUnique), és a DB marad a forrás (a deaktivált user azonnal kilép minden subdomain-en).
- **Login redirect — a paraméter-név kontraktus mindkét oldalon.** Ha a balance-app-on landol egy unauth user, a login-flow-t a beta-app-on kell indítani query-paramra: `https://beta.example-balance.local/belepes?return_to=https%3A%2F%2Fbalance.example-balance.local%2F`. **2026-05-12 incidens:** a balance `?return_to=`-t küldött, de a beta login UI csak `?next=`-et olvasott — belépés után a beta főoldalra dobott vissza, a látogató "semelyik gomb nem visz tovább" érzettel ragadt. **Javítás:** a fogadó login UI **mindkét formátumot olvassa be**: `next` relatív path-hoz (router.push), `return_to` absolute URL-hez (`window.location.href`, hogy a friss cookie utazzon a következő requestben). Open-redirect védelem: absolute `return_to`-t **host-allowlist-tel** szűrd (`*.example-balance.local` és `example-balance.local`), különben támadó saját domain-jére redirektelhet. Magic-link send-route is honorálja a `nextUrl`-t a `redirectTo` body-mezőben.
- **CORS nem kell:** mert a böngésző saját maga küldi a cookie-t bármelyik subdomain-re ha a Domain attribútum jó
- **Logout:** a logout-flow `Domain=.example-balance.local`-n törli a cookie-t (Max-Age=0) — de FONTOS hogy a clear-cookie ugyanazon `userCookieOptions()`-t használja mint a set, különben a böngésző egy másik path/domain-en hagyhat egy szellem-cookie-t. Lásd: `apps/web/lib/user-session.ts:clearUserCookie`.
- **Dev/staging keveredés:** ha a `localhost`-on és a `*.example-balance.local`-n is kísérletezel, két külön cookie-store-od lesz. A localhost-on `SESSION_COOKIE_DOMAIN` env-vart hagyd üresen (host-only cookie); production-on `.example-balance.local`.

## Példa a kódban

`apps/balance/lib/session.ts` — verify-only HMAC bridge a Kinda projektben.

## Kapcsolódó

- [[02-Projects/teszt-eu]] — beta + balance dual-app setup
- [[11-wiki/nextjs-api-proxy-bridge|Next.js API proxy bridge]] — másik (server-side) inter-service kommunikációs minta
- [[11-wiki/demo-fallback-readonly-guard|Demo-fallback read-only guard]] — `isDemo` flag használata mutation route-okon hogy a "preview mode" valóban read-only legyen
