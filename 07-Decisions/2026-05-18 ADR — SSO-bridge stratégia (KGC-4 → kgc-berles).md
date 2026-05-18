---
name: ADR — SSO-bridge stratégia (KGC-4 → kgc-berles)
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, sso, auth, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — SSO-bridge stratégia (KGC-4 → kgc-berles)

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q4 research-output]] alapján Peti finomítja.

## Kérdés

A KGC-4 ERP-ben **kétféle auth-rendszer** fut: admin-auth (klasszikus email+jelszó JWT) és portal-auth (jelszó-mentes, SMS OTP + Magic-link). A `keycloak-jwt.strategy.ts` stub létezik. Hogyan bridge-eljük a portal-auth-ot a kgc-berles Next.js-re?

## Opciók

- (A) **NextAuth.js v5 / Auth.js Credentials provider** ami a KGC-4 `/portal/auth/verify-otp`-t hív + JWT shared-secret session-cookie
- (B) **Keycloak OIDC** real integration (stub élesítése, Keycloak közbeiktatása identity-provider-ként)
- (C) **Custom JWT bridge:** KGC-4 ad portal-JWT-t, Next.js shared-secret-szel (RSA pubkey vagy HS256) verify-eli

## Tradeoff-mátrix összefoglaló

- Cookie-cross-subdomain: `*.kisgepcentrum.hu`, SameSite=Lax, Secure, httpOnly
- WebAuthn / passkey beépíthetőség 2026-trend szempontból
- GDPR data-minimization (portal-profile GDPR-delete LÉTEZIK)
- OWASP buktatók (session-fixation, CSRF, magic-link expiry, brute-force OTP)

Részletek: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q4 — SSO]]

## Várt döntés

Egy konkrét győztes az (A) / (B) / (C) opciók közül + következő Sprint-feature lista Zoli felé.

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
- [[11-wiki/cross-subdomain-cookie-session-bridge]]
