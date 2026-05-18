---
name: Foxxi email deliverability diagnózis (2026-05-10)
type: audit
project: foxxi
created: 2026-05-10
tags: ["#type/audit", "#project/foxxi", "#email", "#dns"]
---

# Foxxi — info@example-foxxi.local email-deliverability diagnózis

> **Zozó 2025-12-18 panasz**: az `office@example-foxxi.local` és `info@example-foxxi.local`-ról küldött emailek **nem érkeznek meg nemzetközi szolgáltatóknak** (kettő nem ért oda 1 héten belül). Magának küldött teszt megjön. Levelező: **Tárhely.eu webmail** + **Gmail-továbbítás**.

## DNS-konfiguráció (2026-05-10)

| Rekord | Érték | Status |
|---|---|---|
| **MX** | `0 mail.example-foxxi.local` → `185.51.188.50` (Tárhely.eu IP) | ✅ OK |
| **PTR (reverse)** | `tefifty.tarhely.eu` | ✅ OK (Tárhely-szerver legitim) |
| **SPF** | `v=spf1 include:sendersrv.com +a +mx +exists:%{i}.spfcheck.eu ~all` | 🟡 OK de **soft-fail** (`~all`) |
| **DKIM** (`default._domainkey` / `tarhely._domainkey` / `mail._domainkey` / `google._domainkey`) | **NINCS** | 🔴 **HIÁNYZIK** |
| **DMARC** | `v=DMARC1; p=none; sp=none;` | 🟡 Csak monitor, nem reject |

## A FŐ probléma: HIÁNYZÓ DKIM

A nemzetközi szolgáltatók (Gmail, Outlook, Yahoo) **2024 óta szigorítottak** a "Bulk Sender Requirements" miatt:
- **Gmail + Yahoo**: DKIM kötelező a sikeres delivery-hez. SPF nem-elég.
- **Outlook**: DKIM-hiányzó email-ek könnyen spam-be vagy DROP-ba.

**Magyar címzettek** (Tárhely.eu, Gmail.com magyar IP, T-Online stb.) gyakran **kíméletesebbek**, ezért Zozó tesztjei magán-Gmail-fiókban átmennek. **Nemzetközi cégeknek** szigorúbb a kontroll → ezekhez nem érkezik meg.

## Megoldás: 4 lépés (Domi/Zozó-akció Tárhely.eu kontrolpanelen)

### 1️⃣ DKIM-kulcs generálás (KRITIKUS)

1. Belépés `tarhely.eu` admin-ba
2. Email-fiókok → `info@example-foxxi.local` (vagy domain-szintű DKIM) → **DKIM beállítás** / "Engedélyezés"
3. Tárhely-rendszer generál egy **selector + public-key TXT rekordot** (pl. `tarhely._domainkey.example-foxxi.local`)
4. Ezt a rekordot **automatikusan beilleszti** a example-foxxi.local DNS-zónába (mivel Tárhely a name-server)
5. **Verify** DNS-propagation után: `dig +short TXT tarhely._domainkey.example-foxxi.local`

### 2️⃣ SPF szigorítás (opcionális, de ajánlott)

Jelenlegi: `~all` (soft-fail) → **`-all`** (hard-reject) változtatás.

> ⚠️ **Csak akkor**, ha biztos hogy minden legitim küldő be van foglalva az `include:sendersrv.com`-ban. Ha nem (pl. más SaaS szolgáltatás is küld example-foxxi.local nevében), maradjon `~all`.

### 3️⃣ DMARC erősítés (több hét után)

Jelenlegi: `p=none; sp=none;` (csak monitor). DKIM-fix után **egy hetes monitorozás**, majd:
- `p=quarantine; sp=quarantine; rua=mailto:dmarc-reports@example-foxxi.local;` (gyanús email-ek spam-be)
- Hosszú távon: `p=reject;` (teljes elutasítás)

### 4️⃣ Gmail-továbbítás kivezetés (DKIM-break workaround)

A `info@example-foxxi.local` → @gmail.com **forwardolás** közben **a Gmail újra-aláírja** az emailt a maga DKIM-jével (jó), DE **az SPF/DMARC-rekord már a Gmail-relay-IP-jét veszi** — eredmény: **DMARC failure** ha az eredeti küldő `-all` (forward-IP nincs az SPF-ben).

**Megoldás-opciók:**
- **A) IMAP/POP3 letöltés** — Gmail közvetlenül tölti le a Tárhely-mailbox-ot (NEM forward), megőrzi az eredeti DKIM-aláírást
- **B) ARC** (Authenticated Received Chain) — Gmail-en alapértelmezett, de Tárhely.eu-nál nem mindig — ellenőrizés szükséges
- **C) Maradhat forward**, ha DMARC `p=none` (most is ez, jó, csak deliverability-romlás)

## Email-küldés gyakorlati teszt (Domi/Zozó kéri ezt elindítani)

```
1. Küldj egy email-t info@example-foxxi.local-ról egy Gmail-fiókba (saját)
2. Gmail-ben nyisd meg: "Show original" → ellenőrizd a header-eket:
   - SPF: PASS / NEUTRAL / FAIL?
   - DKIM: PASS / NONE?
   - DMARC: PASS / FAIL?
3. Plus: küldj Outlook-ra és Yahoo-ra is, lásd megjön-e
```

A `mail-tester.com` egy publikus diagnostikai eszköz: küldj egy email-t a generated cím-re, és kapsz egy 0-10 skálát + részletes hibalistát. **Ezt javaslom** Domi-nak.

## Implementáció (mit tudok én csinálni)

- **Diagnostika**: ✅ kész (ez a fájl)
- **Tárhely.eu admin-akció**: 🔴 **csak Domi/Zozó tudja** (saját login szükséges)
- **DNS-rekord beillesztés**: csak ha Tárhely.eu admin után megkapom a DKIM TXT-rekordot, akkor **manuálisan tudok DNS-zóna** felé valami másik registrar-on (Hostinger DNS pl.). DE ha Tárhely a name-server is, akkor ott magától beáll.
- **SPF/DMARC szigorítás**: tudom CSAK ha Tárhely.eu admin-elérés van, vagy hostinger-DNS-en.

## Prioritás

🔴 **Magas** — ha Domi rendszeresen küld emailt nemzetközi pácienseknek vagy partnereknek (pl. külföldi referencia-orvosok). 

Ha csak ritkán → **lehet halasztani** Phase 16-ra.

## Kapcsolódó

- [[02-Projects/foxxi-email-arhivum]] — 2025-12-18 Zozó panasz
- [[02-Projects/foxxi]]
