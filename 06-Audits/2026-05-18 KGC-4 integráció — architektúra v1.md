---
name: KGC-4 → publikus weboldal integráció — architektúra v1
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: [audit, architecture, kgc-erp, kgc-berles, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles, robbantott-kereso]
session: 2026-05-18-kgc-all
status: draft-architecture-v1
---

> **NotebookLM Q8 szintézis-output** (2026-05-18). Bemenő blokkok: [[2026-05-18 KGC-4 integráció — research-output Q1..Q7]]. ERP-audit: [[2026-05-18 KGC-4 ERP v7.0 mélyaudit]]. Research-terv: [[2026-05-18 KGC-4 frontend integráció — NotebookLM research-terv]].
>
> **Státusz:** Draft — Peti finomítja, Zoli-callon ratify-eljük. 8 ADR-jelölt placeholder a [[07-Decisions/]]-ben.

# KGC-4 → Publikus Weboldal Integráció Architektúra v1

**Dátum:** 2026-05-18
**Státusz:** Tervezet (Draft) / Jóváhagyásra vár
**Projekt:** Kisgépcentrum (Érd) ERP (KGC-4) és `kgc-berles` publikus Next.js weboldal integrációja.
**Környezet:** NestJS + Prisma + PostgreSQL (RLS) backend (Sprint 26 W1 D-3), Next.js 16 frontend (`:3004`).

Ez a dokumentum a korábbi auditok és technológiai spike-ok (Q1-Q7) alapján rögzíti az ERP és a publikus webshop integrációjának architekturális döntéseit, a fejlesztési ütemtervet, valamint a hosszú távú skálázódási stratégiát.

---

## 1. Választott stack indoklással (5 fő döntés)

Az architektúra kialakításakor a fő szempont a SEO-képesség, a magas teljesítmény (Core Web Vitals), a fejlesztői kapacitás (Zoli mint solo-dev a backend oldalon) és az üzleti igények (magyar piac, specifikus kaució-kezelés) egyensúlyba hozása volt.

### (a) CMS-választás: Strapi 5
**Döntés:** A SEO-landing oldalak és blogcikkek kezelésére a **Strapi 5** (https://docs.strapi.io/cms/installation) headless CMS-t vezetjük be az ERP mellé.
**Indoklás:** 
Bár a Payload CMS 3 fejlesztői élménye kiváló, a projektben egy nem technikai beállítottságú szerkesztő (Domi) fogja a tartalmakat kezelni. A Strapi 5 dobozból ad egy rendkívül letisztult, magyarítható admin felületet (https://docs.strapi.io/cms/features/internationalization), beépített Draft & Publish funkciókat (https://docs.strapi.io/cms/features/draft-and-publish), és a relációs adatbázis (PostgreSQL) révén könnyen self-hostolható ugyanazon az infrastruktúrán, amin a KGC-4 is fut. A Next.js+MDX megoldás grafikus UI hiányában (https://nextjs.org/docs/app/building-your-application/configuring/mdx) elvetve, a Sanity pedig a vendor-lock-in (zárt Content Lake) miatt (https://www.sanity.io/docs/content-lake) esett ki.

### (b) SSO-method: NextAuth.js (Auth.js) Credentials + Custom JWT Bridge
**Döntés:** A KGC-4 meglévő OTP/Magic-link flow-ját a **NextAuth.js v5 (Auth.js)** Credentials providerével (https://authjs.dev/getting-started/authentication/credentials) kötjük össze.
**Indoklás:**
A Keycloak OIDC teljes bevezetése (https://www.keycloak.org/docs/latest/server_admin/) túlzott infrastrukturális teher lenne egyetlen fejlesztő (Zoli) számára. A `PortalAuthGuard` már működik a KGC-4-ben. A Next.js oldalon az Auth.js biztonságos, HTTPOnly, SameSite=Lax (https://web.dev/articles/same-site-same-origin) JWE sütikbe csomagolja az ERP-től kapott JWT tokent. Ez gyorsan implementálható és megfelel az OWASP Session Management (https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) irányelveinek.

### (c) Sync-pattern: Webhook + `revalidateTag` (On-demand ISR)
**Döntés:** Az árváltozásokat és készlet-frissítéseket a KGC-4 BullMQ queue-ja (https://docs.bullmq.io/) által vezérelt HTTP Webhookokkal szinkronizáljuk a Next.js `revalidateTag` (https://nextjs.org/docs/app/api-reference/functions/revalidateTag) API-jával.
**Indoklás:**
Az átlagosan ~500 terméket és napi 5-20 árváltozást a Postgres LISTEN-NOTIFY (https://www.postgresql.org/docs/18/sql-notify.html) túl alacsony szinten kezelné, a Debezium CDC (https://debezium.io/documentation/reference/connectors/postgresql.html) pedig feleslegesen bonyolult infrastruktúrát (Kafka) igényelne. A webhook + ISR megközelítés garantálja, hogy a látogatók milliszekundumok alatt betöltődő statikus HTML-t kapnak (https://nextjs.org/docs/app/guides/incremental-static-regeneration), de a Merchant Center (Google) feed felé az árváltozás azonnal frissül a cache invalidálása révén, elkerülve a büntetéseket.

### (d) Deposit-PSP: SimplePay (Tokenizációs / ALU flow)
**Döntés:** A kaució és a bérleti díjak kezelésére a magyar piacon leginkább bizalmat ébresztő **SimplePay** (https://simplepay.hu/fejlesztoknek/) kerül bevezetésre.
**Indoklás:**
Bérlés esetén a gép 7 napnál tovább is az ügyfélnél lehet. A Barion Reservation 7 napos zárolási limitje emiatt problémás. Bár a Stripe Setup-Intent API-ja a legkorszerűbb (https://docs.stripe.com/payments/save-and-reuse), a magyar felhasználók és a NAV-kompatibilitás miatt a SimplePay v2 kártyaregisztrációs (ALU) flow-ja a nyertes. Ezzel a bérleti díj azonnal levonható, a kártya tokenje pedig megőrizhető a `Rental.COMPLETED` státuszig az esetleges késedelmi díjak terheléséhez.

### (e) Tenant-resolution publikus API-n: URL-subdomain alapján
**Döntés:** Az API és a frontend tenant feloldása **Subdomain** (`berles.kisgepcentrum.hu`) alapon fog működni a Query Parameter (`?tenantId=...`) helyett.
**Indoklás:**
A Query paraméteres megoldás súlyos biztonsági adatszivárgáshoz vezethet a logokban. Az Origin-header pedig könnyen hamisítható a kliensek által. A subdomain megközelítés a Next.js `Middleware`-ben interceptálható, majd a szerveroldali kommunikációban beállítható a KGC-4 `TenantContextInterceptor`-a felé, így a kliens sosem látja és nem tudja manipulálni a Tenant UUID-t. Biztonságos és SEO-barát (https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering).

---

## 2. KGC-4 oldali PR-ek (Zoli-feladatok)

Az alábbi Pull Requesteket az ERP (NestJS) repóban kell végrehajtani a megfelelő API és adatréteg kiszolgálása érdekében.

*   **PR-1: Article modul (Prisma model + REST endpoint)**
    *   Bár a CMS a Strapi lesz, az ERP-nek tudnia kell a termékeket összekötni a CMS cikkekkel. 
    *   Feladat: A `EquipmentType` táblához egy `cmsArticleSlug` mező hozzáadása a Prisma sémában.
    *   *Megjegyzés:* Ez az ADR döntés függvényében változhat, de a hibrid megközelítéshez szükséges az azonosító.
*   **PR-2: portal-equipment EquipmentType-aware + kép-URL-ek**
    *   Feladat: A meglévő `/api/v1/portal/equipment` refaktorálása. Jelenleg a fizikai `RentalEquipment` (egyedi gépek) entitásokat adja vissza. A webshopnak az aggregált `EquipmentType` (katalógus-nézet) adatokra van szüksége, amely magában foglalja az árat (`dailyRate`), az elérhető készletet (count of `status: AVAILABLE`), és a MinIO-ból (S3) generált presigned vagy public kép URL-eket.
*   **PR-3: portal-auth SSO-bridge endpoint**
    *   Feladat: A jelszómentes (OTP) login befejezésekor a `/portal/auth/verify-otp` módosítása úgy, hogy a KGC-4 egy rövid lejáratú, de biztonságos JWT tokent adjon vissza, amelyet a NextAuth.js fel tud dolgozni. Adatminimalizálás (https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) alkalmazása: csak a `sub` (PortalUser ID) és a `role` kerüljön a payloadba.
*   **PR-4: `/public/feed.json` katalógus-feed**
    *   Feladat: Egy új végpont vagy egy BullMQ cron job (https://docs.bullmq.io/guide/jobs/repeatable) elkészítése, amely generál egy Google Merchant Center kompatibilis XML vagy JSON feed-et a `EquipmentType` adatokból. Ezt a Next.js és a Google botok fogják fogyasztani.
*   **PR-5: Webhook trigger (Revalidation source)**
    *   Feladat: Prisma Middleware vagy NestJS Event Emitter (CQRS minta: https://microservices.io/patterns/data/event-sourcing.html) beállítása. Ha egy `Rental` létrejön (készlet csökken) vagy egy `EquipmentType` ára változik, a BullMQ felad egy aszinkron taskot, ami egy HMAC-SHA256 aláírt `POST` kérést küld a `:3004/api/revalidate` címre a megfelelő `tag`-gel (pl. `equipment-123`).
*   **PR-6: NAV-online + MyPOS éles integráció Barion-fallback-szel**
    *   Feladat: A jelenlegi MyPOS "STUB" lecserélése az éles SimplePay API hívásokra. Token alapú (ALU) levonási logika leprogramozása a `Booking.CONFIRMED` -> `Rental.DRAFT` állapotgép-átmenethez. A NAV online számla generálás bekötése a sikeres tranzakció után.

---

## 3. kgc-berles oldali fejlesztések (Peti-feladatok)

A Next.js (App Router) frontenden a "Smart endpoints and dumb pipes" (https://microservices.io/patterns/microservices.html) elvet követve a következő fejlesztések szükségesek:

*   **Next.js BFF route-ok (`/api/equipment`, `/api/booking`, `/api/revalidate`)**
    *   Feladat: Route Handler-ek (https://nextjs.org/docs/app/building-your-application/routing/route-handlers) írása, amik proxy-ként működnek a KGC-4 felé. Különösen a webhook fogadó `/api/revalidate` megírása, amely validálja a KGC-4 HMAC aláírását, és futtatja a `revalidateTag(tag)` függvényt (https://nextjs.org/docs/app/api-reference/functions/revalidateTag).
*   **NextAuth setup (Credentials + JWT shared-secret)**
    *   Feladat: Az `auth.ts` konfigurálása az Auth.js (NextAuth v5) használatával (https://authjs.dev/getting-started/authentication/credentials). A "Credentials" provider hívja meg a KGC-4 OTP verifikáló végpontját, és a válaszban kapott JWT-t mentse el a kliens cookie-jába, biztosítva a session kezelést.
*   **CMS-bootstrap (Strapi deploy + content-seeding)**
    *   Feladat: Strapi 5 inicializálása (VPS vagy Vercel + külső adatbázis), a `Category`, `Article`, és `EquipmentGuide` tartalomtípusok (Content Types) felépítése. Az ERP termékeivel való logikai összekötés (pl. ERP ID tárolása a Strapiban) megvalósítása.
*   **schema.org/Product + ItemList + BreadcrumbList JSON-LD**
    *   Feladat: A dinamikus oldalakon (`app/gepek/[slug]/page.tsx`) a Next.js `generateMetadata` kiterjesztése és a `<script type="application/ld+json">` beágyazása (https://schema.org/Product, https://schema.org/ItemList). Fontos a hierarchia és a valós ERP-ből származó ár (`offers`) megjelenítése.
*   **SimplePay deposit-flow UI**
    *   Feladat: A Checkout komponens megírása, amely a BFF-en keresztül kommunikál a backenddel, megjeleníti a SimplePay fizetési ablakát (vagy iframe-et), és sikeres ALU regisztráció után átirányít a siker-oldalra.
*   **`/llms.txt` + sitemap.ts + robots.ts**
    *   Feladat: Dinamikus `app/sitemap.ts` (https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap) készítése, amely a KGC-4 katalógusából olvassa az URL-eket. Ezen felül az Agentic Browsing (https://llmstxt.org/) számára egy `/llms.txt` fájl generálása, Markdown formátumban a gépkölcsönzés szabályairól és a terméklistáról.
*   **Magyar i18n (next-intl) + SEO-landing template**
    *   Feladat: Bár jelenleg csak magyar piac van, a `next-intl` bevezetése a szövegek tiszta kezelése érdekében, illetve egy újrahasználható RSC (React Server Component) template készítése a long-tail kulcsszavakra ("bérgép Érd", "kompresszor bérlés").

---

## 4. Ütemezés (4-Sprint Roadmap)

Az integrációt a KGC-4 és a `kgc-berles` párhuzamos fejlesztésével, "Contract-Driven" (https://microservices.io/patterns/microservices.html) API tervek mentén valósítjuk meg.

| Sprint | Időtartam (Hét) | Backend (Zoli - KGC-4) | Frontend (Peti - kgc-berles) |
| :--- | :--- | :--- | :--- |
| **Sprint A**<br>(Kickoff) | W1 - W2 | **PR-2:** `portal-equipment` végpont refaktorálása aggregált nézetre, MinIO kép URL-ek integrálása. Origin-header / Subdomain tenant resolver elkészítése. | Next.js projekt setup, UI alapok. **API Mocking:** BFF route-ok előkészítése a KGC-4 végpontok szerződései (Swagger/OpenAPI) alapján. |
| **Sprint B**<br>(Tartalom & Auth) | W3 - W4 | **PR-1 & PR-3:** CMS-ERP ID szinkronizációs mezők beállítása. OTP backend véglegesítése, SSO Bridge (JWT) elkészítése. | **NextAuth.js** bekötése a BFF-be. **Strapi CMS** integrálása: SEO-landing oldalak dinamikus generálása a CMS és az ERP adatok hibrid megjelenítésével. |
| **Sprint C**<br>(Üzleti logika) | W5 - W6 | **PR-5 & PR-6:** SimplePay ALU backend logika (MyPOS stub csere). Webhook infrastruktúra (BullMQ) megépítése és tesztelése a Next.js felé. | **Checkout Flow:** SimplePay UI implementálása. **Revalidation:** `/api/revalidate` végpont leprogramozása HMAC ellenőrzéssel (https://nextjs.org/docs/app/api-reference/functions/revalidateTag). |
| **Sprint D**<br>(Go-live & SEO) | W7 - W8 | **PR-4:** `feed.json` generátor a Merchant Center felé. Biztonsági finomhangolás (Rate Limiting, RLS audit). | JSON-LD sémák generálása (https://schema.org/Product). `/llms.txt`, sitemap és robots.ts véglegesítése. Teljesítmény optimalizálás (LCP, INP). |

---

## 5. 5-8 ADR-jelölt témafelvetése (Architecture Decision Records)

Az alábbi kérdéseket a Sprint A folyamán formális ADR-ekben kell rögzíteni.

1.  **ADR — CMS-választás (Strapi 5 vs Payload 3 vs Sanity vs MDX)**
    *   Hogyan biztosítjuk a legegyszerűbb UX-et a tartalomszerkesztőnk (Domi) számára, miközben elkerüljük a vendor lock-int és tartjuk a költségvetést?
2.  **ADR — SSO-bridge stratégia**
    *   Bevezessük-e a robusztus Keycloakot OIDC-vel, vagy elegendő a jelenlegi KGC-4 backend által dedikáltan aláírt JWT és a NextAuth.js kombinációja a jelszómentes bejelentkezéshez?
3.  **ADR — Sync-pattern (Webhook vs CDC vs Poll)**
    *   Melyik megközelítés garantálja a legalacsonyabb szerverterhelést és a legfrissebb árakat a Next.js ISR cache-ben anélkül, hogy bonyolult Kafka/Debezium infrastruktúrát építenénk?
4.  **ADR — Deposit-PSP (Stripe vs Barion vs SimplePay)**
    *   Melyik fizetési szolgáltató biztosítja a legmegbízhatóbb megoldást a 7 napot meghaladó gépkölcsönzések kauciójának (deposit) zárolására és későbbi érvényesítésére a magyar piacon?
5.  **ADR — Tenant-resolution publikus API-n**
    *   Az anonim API-hívások során hogyan azonosítjuk a tenant-ot (KGC vs Foxxi) biztonságosan, elkerülve a Query Paraméterek URL szivárgását és az Origin-fejlécek hamisíthatóságát?
6.  **ADR — Article modul ERP-ben vagy külön CMS-ben**
    *   Érdemes-e a Zoli által írt 72 Prisma modell közé bekötni a blogcikkeket, vagy tisztább architekturálisan, ha a tartalmak teljes egészében a Strapi/Payload adatbázisában élnek?
7.  **ADR — Next.js BFF vs Direkt API-call Front-endből**
    *   A Next.js Server Components használatával rejtjük el a KGC-4 API kulcsokat, vagy engedélyezzük, hogy a kliens böngészőből közvetlenül hívják a publikus KGC-4 végpontokat?
8.  **ADR — Agentic-browsing readiness (llms.txt) priorizálás**
    *   Milyen struktúrában és mélységben expozáljuk a termékkatalógust a jövőbeli AI ügynökök számára az `/llms.txt` fájlban, hogy maximalizáljuk a találati arányt az LLM alapú keresésekben?

---

## 6. Kockázatok + Mitigation (Kockázatkezelés)

A komplex elosztott rendszer számos biztonsági és teljesítménybeli kockázatot rejt, melyekre proaktív megoldásokat kell alkalmazni.

*   **RLS-bypass anonymous endpointokon:**
    *   *Kockázat:* A PostgreSQL Row Level Security (RLS) véletlen megkerülése (pl. `BYPASSRLS` attribútummal rendelkező role használata) adatszivárgáshoz vezethet a tenantok között. (Lásd: https://www.postgresql.org/docs/18/sql-createpolicy.html).
    *   *Mitigáció:* A backendben a Prisma Middleware szigorúan használja a `SET LOCAL app.tenant_id = '...'` parancsot a tranzakciók elején, és az adatbázishoz csatlakozó Postgres Role **nem** lehet superuser. A `tenantId` sosem érkezhet nyers, kliens által manipulálható Query paraméterből az anonim végpontokon.
*   **GDPR (PortalUser-data minimization, account-deletion):**
    *   *Kockázat:* Személyes adatok (PII) bennmaradása a session cookie-kban vagy az audit logokban. A fióktörlési jog nem érvényesül azonnal a frontend oldalon.
    *   *Mitigáció:* Az Auth.js által tárolt JWT payload csak a User UUID-t tartalmazhatja. A KGC-4 GDPR-delete endpoint meghívásakor azonnal invalidálni kell a sessiont a frontenden is. Logolásnál csak pszeudonimizált adatok (pl. hashelt session ID) kerülhetnek a rendszerbe.
*   **MyPOS stub élesítés:**
    *   *Kockázat:* A fizikai POS terminálok és az online SimplePay tokenizáció (ALU) szinkronizációs hibája, vagy a STUB logika okozta "false positive" foglalások az éles rendszerben.
    *   *Mitigáció:* Dedikált teszt-szerver környezet a Barion fallback-el, ha a SimplePay szolgáltatás kiesne. A `Booking.CONFIRMED` állapotváltozást szigorú idempotencia-kulccsal és elosztott zárral (Redis lock) kell védeni.
*   **Single-dev burnout (Zoli solo-aktivitás), bus-factor:**
    *   *Kockázat:* Az ERP komplexitása (72 modell, 68 modul, egyedi BMAD agentic workflow) kizárólag Zoli fejében létezik. A bus-factor 1.
    *   *Mitigáció:* A fejlesztések egy részének (tartalomkezelés, frontend) kiszervezése Petihez (Strapi + Next.js). Szigorú dokumentáció írása a BMAD modulról, és a "Buy vs Build" elv alapján új, commodity funkciók (pl. PIM, Auth) egyedi fejlesztésének leállítása dobozos megoldások javára.
*   **Cache-stampede revalidation-nél:**
    *   *Kockázat:* Egy árváltozás webhookja törli a cache-t, aminek hatására egyszerre 100+ kliens kérése zúdul be az ERP backendjére (Thundering Herd probléma).
    *   *Mitigáció:* A Next.js (Vercel) infrastruktúrájába beépített "Request Collapsing" mechanizmus használata (Lásd: https://aws.amazon.com/builders-library/caching-challenges-and-strategies/ és https://nextjs.org/docs/app/guides/incremental-static-regeneration). Ez biztosítja, hogy a cache invalidálása után csak **egy** kérés menjen el az ERP felé, a többi kliens a válaszra vár a CDN szintjén.
*   **SEO-stale-content (stale price → Merchant Center ban):**
    *   *Kockázat:* A statikus oldalon beragadt árat lát a Googlebot, miközben a Merchant Center XML feed már a friss ERP árat tartalmazza. Az eltérésért a Google felfüggesztheti a hirdetési fiókot.
    *   *Mitigáció:* Az árváltozás az ERP-ben **szinkron módon** is bevárhatja a Vercel `/api/revalidate` webhook 200 OK válaszát, mielőtt a feed-generálást engedélyezi, így a weboldal mindig megelőzi vagy egy időben frissül a Google felé küldött adatokkal.

---

## 7. Long-term skálázódás (3-5 éves horizont)

Mivel a KGC-4 jelenleg rendkívül gyors "feature velocity"-vel halad előre a BMAD agentic workflow-nak köszönhetően, a rendszer teljes lecserélése egy standard ERP-re (pl. Odoo (https://github.com/odoo/odoo), ERPNext (https://github.com/frappe/erpnext), vagy Twenty CRM (https://github.com/twentyhq/twenty)) **jelenleg nem javasolt**. Ugyanakkor a 3-5 éves távlatban a technológiai adósság és az üzemeltetési teher növekedésével a váltás elkerülhetetlenné válhat.

**Mit építünk MOST, hogy a váltás később könnyebb legyen?**

1.  **Anti-Corruption Layer (ACL) és API-first megközelítés:**
    *   Az ERP funkcióit szigorú, verziózott REST API határok ("APIs as infrastructure") mögé rejtjük. A Next.js frontend (`kgc-berles`) kizárólag a `/api/v1/portal/...` végpontokat ismeri. Így ha a háttérben az egyedi NestJS kódot lecseréljük egy Odoo Python modulra, a frontend ebből semmit sem vesz észre, amíg az API szerződés (Contract) változatlan marad.
2.  **Domain-Event-Bus kiépítése:**
    *   A jelenleg használt BullMQ (https://docs.bullmq.io/) sorokat érdemes kibővíteni egy valódi Event Bus architektúrává (Event-Carried State Transfer: https://microservices.io/patterns/data/event-sourcing.html). Ha minden entitás változását (pl. `RentalCreated`, `EquipmentPriceUpdated`) publikáljuk a message brokerbe, egy jövőbeli dobozos rendszer (pl. Pimcore vagy Akeneo a katalógusnak) könnyedén fel tud iratkozni ezekre az eseményekre és átveheti az adatok egy részének kezelését anélkül, hogy a KGC-4-be mélyen bele kellene nyúlni (Tight-Coupling elkerülése).
3.  **Commodity funkciók leválasztása (Hibrid modell):**
    *   A CMS-ként kiválasztott Strapi bevezetése az első lépés ezen az úton. Ahelyett, hogy Zoli írna egy egyedi Content Management modult a KGC-4-be (ami "Commodity", azaz nem jelent versenyelőnyt), egy kész terméket illesztünk a rendszerbe. Ha a bérleti motor (a BMAD workflow-val kiegészítve) jelenti a cég egyedi értékét, akkor azt kell házon belül tartani, minden mást (Számlázás, CRM, PIM, CMS) fokozatosan dobozos szoftverek felé delegálni, amik integrálódnak az Event-Bus-ra.
---

## Kapcsolódó ADR-jelöltek

A 8 placeholder ADR-fájl a [[07-Decisions/]] mappában jött létre, hogy Peti később finomítsa:

- [[07-Decisions/2026-05-18 ADR — CMS-választás (KGC-4 integráció)]]
- [[07-Decisions/2026-05-18 ADR — SSO-bridge stratégia (KGC-4 → kgc-berles)]]
- [[07-Decisions/2026-05-18 ADR — Sync-pattern (webhook vs CDC vs poll)]]
- [[07-Decisions/2026-05-18 ADR — Deposit-PSP (Stripe vs Barion vs SimplePay)]]
- [[07-Decisions/2026-05-18 ADR — Tenant-resolution publikus API-n]]
- [[07-Decisions/2026-05-18 ADR — Article modul ERP-ben vagy CMS-ben]]
- [[07-Decisions/2026-05-18 ADR — Next.js BFF vs direkt API-call]]
- [[07-Decisions/2026-05-18 ADR — Agentic-browsing readiness (llms.txt)]]

## Kapcsolódó dokumentumok

- [[2026-05-18 KGC-4 integráció — research-output Q1..Q7]] — per-blokk research output (Q1..Q7b)
- [[2026-05-18 KGC-4 ERP v7.0 mélyaudit]] — KGC-4 mélyaudit (integration-gap-ek)
- [[2026-05-18 KGC-4 frontend integráció — NotebookLM research-terv]] — research-terv
- [[02-Projects/kgc-erp]] — KGC-4 project-fájl
- [[02-Projects/kgc-berles]] — Next.js front-projekt
- [[11-wiki/nextjs-api-proxy-bridge]] — Next.js → REST-backend pattern (Peti-féle balance/example-balance.local minta)
- [[11-wiki/cross-subdomain-cookie-session-bridge]] — Cookie SSO pattern
- [[11-wiki/lighthouse-agentic-browsing]] — llms.txt + agentic readiness
