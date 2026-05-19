---
name: Puppeteer PDF render with system Chrome + token auth
type: wiki
tags: ["#type/reference", "#tech/nextjs"]
created: 2026-05-11
updated: 2026-05-19
tag_backfill: 2026-05-19
---
# Puppeteer PDF render — system Chrome + token-only auth

Server-belüli HTML-ből PDF készítése úgy, hogy ne kelljen 280MB Chromium-ot letölteni a függőségbe, és ne kelljen session-cookie-t smuggle-elni a puppeteer browser context-be.

## Mire jó

- Admin riport / számla / havi jelentés PDF-letöltése egy meglévő HTML view-ból (cél: dizájn-változás automatikusan propagálódjon, nincs külön PDF-builder).
- Email-mellékletként attached PDF küldés (Resend, Postmark stb. fogad `base64` attachment-et).

## A két trükk

### 1. `puppeteer-core` + system Chrome — nem `puppeteer`

`puppeteer-core` ~3MB, a teljes `puppeteer` ~280MB-os Chromium-ot tölt le `postinstall`-ban. Ha a host-on van Chrome (Linux VPS-en gyakori) vagy Chromium (Alpine), elég a core + `executablePath`:

```ts
import puppeteer from 'puppeteer-core';

const CHROME_PATHS = [
  process.env.PUPPETEER_EXECUTABLE_PATH,
  '/usr/bin/google-chrome',
  '/usr/bin/chromium-browser',
  '/usr/bin/chromium',
].filter(Boolean) as string[];

let cached: import('puppeteer-core').Browser | null = null;
async function getBrowser() {
  if (cached?.connected) return cached;
  cached = await puppeteer.launch({
    executablePath: CHROME_PATHS[0],
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  return cached;
}
```

A `cached` browser-példányt érdemes process-élettartamúra fogni (és process-leállításkor `close`-olni) — egyetlen Chrome process kiszolgál sok render-kérést.

### 2. Auth: short-lived HMAC token, NEM session cookie

Ha a renderelendő route admin-only (`requireAdmin()` mögött), elsőre kísértés átadni a session-cookie-t puppeteer `setCookie()`-jal. **NE** — túl sok mozgó alkatrész:
- a cookie domain/path/sameSite egyezésén bukhat a renderelő browser
- a session-cookie LM-élettartama nagy → ha valahol leak-elne (pl. PDF-belebújó iframe), nagyobb a kár
- ha a session-cookie formátuma változik, a PDF-renderelés is törik

Helyette: **célzott, rövid életű token** csak a print-route-ra:

```ts
// lib/report-token.ts
import crypto from 'node:crypto';

export function signReportToken(userId: string, orgId: string, ttlSec = 120): string {
  const payload = { userId, orgId, exp: Math.floor(Date.now() / 1000) + ttlSec };
  const b64 = Buffer.from(JSON.stringify(payload), 'utf-8').toString('base64url');
  const secret = process.env.REPORT_TOKEN_SECRET ?? process.env.USER_SESSION_SECRET!;
  const sig = crypto.createHmac('sha256', secret).update(b64).digest('hex');
  return `${b64}.${sig}`;
}
// verifyReportToken — szimmetrikus, lejárat-ellenőrzéssel
```

A renderelt route (`/admin-report?t=<token>`) önállóan auth-ol a token-ből — semmilyen kapcsolata a felhasználói session-nel.

## A teljes flow

```ts
// /api/report?format=pdf  (admin session-védett endpoint)
const session = await requireAdmin();           // session-cookie alapján
const orgId = await resolveOrg(session.userId);
const token = signReportToken(session.userId, orgId, 120);
const url = `${PRINT_BASE_URL}/admin-report?t=${encodeURIComponent(token)}`;

const browser = await getBrowser();
const page = await browser.newPage();
try {
  await page.setViewport({ width: 1024, height: 1440, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 20_000 });
  const pdf = await page.pdf({
    format: 'A4', printBackground: true,
    margin: { top: '14mm', bottom: '14mm', left: '14mm', right: '14mm' },
  });
  return new Response(new Uint8Array(pdf), {
    status: 200,
    headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': `inline; filename="report.pdf"` },
  });
} finally {
  await page.close();
}
```

## Gotcha-k

- **Next.js 16 + Turbopack:** a `next start` (production) ~30× gyorsabb mint a `next dev` cold-start, így puppeteer-ben érdemes prod-build-et használni.
- **A `(print)` route group + minimal layout:** a print-route NE örökölje az admin chrome-ot (sidebar, header) — `app/(print)/admin-report/page.tsx` saját `layout.tsx`-szel csak `<div className="print-shell">{children}</div>`.
- **`@media print`:** A4 padding/margin a `page.pdf({ margin: ... })`-en jön, NEM CSS-ben. Ha CSS `@page { size: A4 }`-t használsz, `preferCSSPageSize: true` a `pdf()` opció.
- **Lejárat:** 120s elég egy puppeteer-renderre; akár 30s is. **Ne** legyen több mint pár perc, különben a token-replay attack-window kinyílik.
- **`process.env.USER_SESSION_SECRET` fallback:** dev-ben egy közös secret elegáns; production-on érdemes külön `REPORT_TOKEN_SECRET`-et adni (kevesebb blast-radius ha bármelyik leak-el).

## Példa a kódban

Kinda projektben: `apps/balance/lib/{report-pdf,report-token}.ts` + `apps/balance/app/(print)/admin-report/page.tsx` + `apps/balance/app/api/balance/report/route.ts` (2026-05-11, commit `5c22acb`).

## Kapcsolódó

- [[02-Projects/teszt-eu]] — Balance riport-flow
- [[11-wiki/cross-subdomain-cookie-session-bridge]] — szessziókezelés ehhez orthogonális
