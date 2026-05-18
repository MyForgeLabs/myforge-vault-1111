---
name: Resend send-subdomain vs Hostinger Mail MX
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/playbook", "#service/resend", "#service/hostinger", "#dns"]
---

# Resend `send.<domain>` subdomain pattern — ütközés-mentes a Hostinger Mail-lel

A Resend a domain-verify-flow alatt 3 DNS-rekordot kér:

- `TXT  resend._domainkey  → p=MIGfMA0...` (DKIM, domain-szintű)
- `TXT  send               → v=spf1 include:amazonses.com ~all` (SPF, **subdomain**)
- `MX   send               → 10 feedback-smtp.eu-west-1.amazonses.com` (mail forward, **subdomain**)

**Kulcs:** a kettő `send` rekord a `send.<domain>` subdomain-en van. A **`from` cím a root `noreply@<domain>` is lehet**, mert a DKIM-selektor a domain-szinten van (`resend._domainkey.<domain>`).

## Miért fontos: Hostinger Mail-lel ütközés-mentesség

Ha a domain-en már fut Hostinger Mail (apex `@` MX-szel `mx1/mx2.shared-hosting-example.com.`), és felveszed Resend `send`-subdomain rekordjait → **NINCS ütközés**, a két szolgáltatás párhuzamosan él:

- Apex `@` MX → Hostinger Mail (fogad)
- `send.<domain>` MX → Resend (csak kimenő SPF + bounce-feedback)

## ⚠ De NE engedélyezd az "Enable Receiving" toggle-t!

A Resend dashboard "Enable Receiving" toggle-je egy **apex `@` MX-rekordot** kér (`inbound-smtp.eu-west-1.amazonaws.com`) — ez **ütközik** a meglévő Hostinger MX-szel. A Resend dashboardja "Conflicting MX records" warning-ot ad. Hagyd OFF, csak a "Enable Sending" kell.

## Hibajelek

- 403 `The boulium.com domain is not verified` a Resend API-tól → Resend még nem futtatta a re-verify-t a DNS-rekordok beadása után. Várj 5-10 percet vagy kattints a "Verify DNS Records" gombra. A DNS-rekordoknak a 3 sending-szekcióban **zöld pipát** kell kapniuk.
- `"status":true` válasz a Better Auth-tól, de email NEM érkezik → a Resend sending-only API-key 403-at kap, de a Better Auth elnyeli a hibát prod-ban (security). **Tegyél explicit `console.error` log-ot** a `sendMagicLink` callback-ben — `res.error` mező a Resend SDK return-jén.

## Dual-stack pattern más mail-szolgáltatókkal

Ugyanez a minta működik más kombinációkkal:

- Google Workspace apex + Resend `send` subdomain → ütközés-mentes
- Cloudflare Email Routing apex + Resend `send` → ütközés-mentes
- Egy mail-szolgáltató apex + másik tranzakcionális mail subdomain → mindig OK ha a kettő subdomain ≠ apex

## Implementáció Better Auth + Resend-szel

```ts
// lib/auth.ts
import { Resend } from "resend";

const resend = process.env.RESEND_API_KEY
  ? new Resend(process.env.RESEND_API_KEY)
  : null;

export const auth = betterAuth({
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        if (!resend) {
          console.warn(`[auth] RESEND_API_KEY missing — link for ${email}: ${url}`);
          return;
        }
        try {
          const res = await resend.emails.send({
            from: process.env.RESEND_FROM_EMAIL ?? "noreply@boulium.com",
            to: email,
            subject: "Belépési link",
            html: `<p>Kattints: <a href="${url}">${url}</a></p>`,
          });
          if (res.error) {
            console.error(`[auth] Resend error to ${email}:`, res.error);
          } else {
            console.log(`[auth] Magic-link sent to ${email}, id=${res.data?.id}`);
          }
        } catch (e) {
          console.error(`[auth] Resend exception to ${email}:`, e);
        }
      },
    }),
  ],
});
```

## Gmail prefetch quirk

A Gmail (és Apple Mail) **prefetcheli a magic-linkeket** biztonsági scan miatt → első kattintás felhasználja a tokent, második `INVALID_TOKEN` errort kap. Ez **Better Auth security feature**, nem bug. UX-fix: Flash-toast magyarázattal + `?error=INVALID_TOKEN` queryparam client-side auto-clear.

## Kapcsolódó

- [[nano-banana-cli-gotchas]] — más email-csapdák
</content>
