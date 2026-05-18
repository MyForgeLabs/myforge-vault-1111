---
name: KGC-4 ↔ publikus weboldal integráció — research-output Q1..Q7
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: [audit, research, kgc-erp, kgc-berles, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles, robbantott-kereso]
session: 2026-05-18-kgc-all
---

# KGC-4 ↔ publikus weboldal integráció — research-output Q1..Q7

> **NotebookLM deep research output 161 forrás alapján** (2026-05-18). 7 blokk + 1 szintézis Q. A research-tervet lásd: [[2026-05-18 KGC-4 frontend integráció — NotebookLM research-terv]]. A szintézis-dokumentum: [[2026-05-18 KGC-4 integráció — architektúra v1]].

## Tartalomjegyzék

- [Q1 — Katalógus-szinkron](#q1--katalógus-szinkron-erp--nextjs)
- [Q2 — Headless CMS választás](#q2--headless-cms-választás)
- [Q3 — Multi-tenant publikus API](#q3--multi-tenant-publikus-api)
- [Q4 — Cross-app SSO](#q4--cross-app-sso)
- [Q5 — Rental/booking integráció](#q5--rentalbooking-integráció)
- [Q6 — Headless ERP-stack comparison](#q6--headless-erp-stack-comparison)
- [Q7 — SEO + structured data](#q7--seo--structured-data)
- [Q7b — WordPress vs Next.js (opt-in)](#q7b--wordpress-vs-nextjs-opt-in)

---

## Q1 — Katalógus-szinkron (ERP → Next.js)

> **Kérdés:** Hogyan szinkronizál egy headless ERP (NestJS+Prisma+RLS) publikus Next.js katalógussal? Mikor melyik pattern (webhook / poll / event-stream / CDC) jobb? Cache-invalidation Next.js ISR-rel.

Egy headless ERP (mint a NestJS + Prisma) és egy Next.js 16 publikus weboldal integrációja során a katalógus szinkronizálása és a gyorsítótárak (cache) frissen tartása kritikus építőelem. A modern Next.js App Router architektúrájában a cél, hogy statikus sebességet (SSG/ISR) érjünk el, miközben az árak és a készlet adatai mindig a legfrissebb ERP állapotot tükrözik.

Íme a strukturált válasz a KGC-4 architektúrájához és a feltett kérdésekhez igazítva.

### 1. Pattern-comparison tábla

| Pattern | Előnyök | Hátrányok | Latency (Késleltetés) | Komplexitás |
| :--- | :--- | :--- | :--- | :--- |
| **Webhook (HTTP POST)** | Szabványos, könnyen implementálható Next.js Route Handlerként. Jól skálázható serverless (Vercel) környezetben is. | HTTP overhead. Hálózati hibák esetén a NestJS-nek gondoskodnia kell az újrapróbálkozásról (retry). | Alacsony (~100-300ms) | Alacsony |
| **Pull / Polling** | Nincs szükség bonyolult backend logikára. | Felesleges terhelés (overhead) a DB-n és az API-n, ha nincs változás. Nem valódi real-time. | Magas (a polling intervallumtól függően) | Legalacsonyabb |
| **Debezium CDC (Logical Decoding)** | A PostgreSQL WAL (Write-Ahead Log) olvasásával minden változást garantáltan elkap, még a manuális SQL módosításokat is. | Nehézkes infrastruktúra (Kafka/Debezium Server beállítása szükséges). A Next.js közvetlenül nem tudja fogyasztani, köztes réteg kell. | Nagyon alacsony (sub-millisecond a DB-től a queue-ig) | Nagyon magas |
| **Postgres LISTEN/NOTIFY** | Közvetlen beépített PG funkció, nagyon gyors (forrás: https://www.postgresql.org/docs/18/sql-notify.html). | Max 8000 byte payload. "At-most-once" kézbesítés: ha a figyelő (listener) épp újraindul, az üzenet elveszik. | Nagyon alacsony | Közepes |
| **Redis Streams / BullMQ** | Beépített retry, delayed jobs, idempotencia támogatás (forrás: https://docs.bullmq.io/). KGC-4-ben eleve adott. | A Next.js API route-ok (főleg serverless esetén) nem tudnak tartós Redis kapcsolatot nyitva tartani queue listen-hez, így köztes worker kell. | Alacsony | Közepes |

### 2. Konkrét ajánlás a KGC-4 esetére

A jelenlegi tech-stack (NestJS, BullMQ, 500 termék, ~120 SEO landing, napi 5-20 árváltozás, óránkénti készletfrissítés) egyértelműen az **On-demand revalidation (Webhook) + BullMQ retry** architektúrát teszi a legjobb választássá.

**Miért?**
* **Stale-while-revalidate (SWR) vs On-Demand:** A SWR hátránya e-kereskedelemben, hogy a vásárló az első letöltéskor egy "elavult" árat vagy készletet láthat, és csak a háttérben frissül az oldal. Napi 5-20 árváltozásnál ez üzleti kockázat. Az On-Demand revalidáció (Webhook alapon) biztosítja, hogy a változás pillanatában a Next.js cache azonnal (globálisan ~300ms alatt) frissüljön (forrás: https://nextjs.org/docs/app/guides/incremental-static-regeneration).
* **Az integráció menete:**
  1. Amikor az ERP-ben (Prisma) módosul egy gép ára vagy státusza, a NestJS felad egy feladatot a BullMQ `catalog-sync` queue-ba.
  2. A NestJS BullMQ worker feldolgozza a job-ot, és egy HMAC-aláírt HTTP POST kérést küld a Next.js weboldal `POST /api/revalidate` végpontjára. (Ha a Next.js nem elérhető, a BullMQ automatikusan megpróbálja újra).
  3. A Next.js a kérés hatására meghívja a `revalidateTag` függvényt, ami azonnal purgolja az érintett terméket az ISR cache-ből.
* **Full-rebuild:** 500 termék + 119 landing oldal esetén a teljes rebuild mindössze néhány másodpercet / percet venne igénybe, de teljesen szükségtelen minden készletváltozásnál eldobni a teljes oldalt. A tag-alapú invalidáció nagyságrendekkel erőforrás-kímélőbb.

### 3. Next.js cache-invalidation kód-minta (Next.js 15/16)

A Next.js 15/16 App Router esetén a `revalidateTag` a preferált módszer, mivel egy termék módosítása érintheti a katalógus-listát és a termék-adatlapi URL-t is. A tag-ek használatával nem kell minden egyes útvonalat manuálisan invalidálni, elegendő magát az adathalmazt (forrás: https://nextjs.org/docs/app/api-reference/functions/revalidateTag).

**Next.js 15/16 Webhook Endpoint (`app/api/revalidate/route.ts`):**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { revalidateTag } from 'next/cache';
import crypto from 'crypto';

export async function POST(request: NextRequest) {
  try {
    const body = await request.text(); // Get raw body for HMAC validation
    const signature = request.headers.get('x-kgc-signature');
    const secret = process.env.REVALIDATION_SECRET;

    if (!secret || !signature) {
      return NextResponse.json({ message: 'Missing secret or signature' }, { status: 401 });
    }

    // 1. HMAC Auth Validation
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(body)
      .digest('hex');

    if (crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature)) === false) {
      return NextResponse.json({ message: 'Invalid signature' }, { status: 403 });
    }

    // 2. Parse payload
    const { tag } = JSON.parse(body) as { tag?: string };

    if (!tag) {
      return NextResponse.json({ message: 'Missing tag in payload' }, { status: 400 });
    }

    // 3. Revalidate specific tag
    revalidateTag(tag);
    
    // Note: revalidatePath can also be used if routing structure is preferred:
    // import { revalidatePath } from 'next/cache';
    // revalidatePath(`/berles/gep/${slug}`);

    return NextResponse.json({ revalidated: true, tag, now: Date.now() });
  } catch (err) {
    return NextResponse.json({ message: 'Error revalidating', error: String(err) }, { status: 500 });
  }
}
```

**Adatlekérdezés felcímkézése a Next.js komponensben:**

```typescript
// app/berles/gep/[slug]/page.tsx
export default async function EquipmentPage({ params }: { params: { slug: string } }) {
  const { slug } = params;
  
  // Next.js 15+ fetch options
  const res = await fetch(`https://api.kgc.hu/api/v1/portal/equipment/${slug}`, {
    cache: 'force-cache',
    next: { tags: [`equipment-${slug}`, 'catalog'] }
  });
  
  const equipment = await res.json();
  
  return <EquipmentDetail data={equipment} />;
}
```

### 4. Performance benchmarkok és mértékek

* A Vercel/Next.js architektúrában a `revalidatePath` és `revalidateTag` hívások az élhálózaton (CDN) és a tartós ISR cache-ben (durable storage) is lefutnak. A dokumentáció szerint a globálisan konzisztens cache invalidáció jellemzően **300 ezredmásodpercen (300ms) belül megtörténik az összes régióban** (forrás: https://nextjs.org/docs/app/guides/incremental-static-regeneration).
* Headless CMS-ek (pl. Sanity) esettanulmányai és dokumentációja szerint a Webhook alapú rendszereknél 30 másodperces timeouttal érdemes számolni a válaszra, és érdemes egyidejűleg 1 kérésre (concurrency) korlátozni a webhookokat az "előző állapot" felülírásának elkerülése végett (forrás: https://www.sanity.io/docs/webhooks).

### 5. Buktatók és Best Practice-ek

1. **Cache Stampede (Thundering Herd):**
   Ha egy népszerű gép cache-ét a webhook purge-öli, majd egyszerre 100 vásárló nyitja meg az oldalt, a Next.js szerver egyszerre 100 kérést indíthat a NestJS ERP felé.
   * *Megoldás:* A Vercel infrastruktúrája natívan biztosítja a *Request Collapsing* mechanizmust. Ha több kérés érkezik egy épp invalidált (cache miss) oldalra, a CDN összevonja azokat, és csak **egy** háttérhívást (invocation) küld a backend felé, megvédve az ERP-t a terheléstől (forrás: https://aws.amazon.com/builders-library/caching-challenges-and-strategies/).
2. **Stale-on-error (Fallback on Failure):**
   Ha a revalidációs folyamat alatt az ERP backend hibát ad vissza (pl. a NestJS adatbázis túlterhelt, vagy 500-as hibát dob), a Vercel ISR automatikusan megőrzi az utolsó sikeres (stale) cache-t. Ilyenkor 30 másodperces TTL-t állít be, és hamarosan újra próbálkozik a frissítéssel a háttérben, ahelyett hogy az oldalt törölné a látogatók elől (forrás: https://nextjs.org/docs/app/guides/incremental-static-regeneration).
3. **Race Condition gyors frissítések (publish) közben:**
   Ha az árat valaki gyors egymásutánban kétszer módosítja (pl. elírta), a NestJS worker által küldött két webhook üzenet esetenként eltérő sorrendben futhat le a Next.js oldalon, ami miatt a régi adat kerülhet vissza a cache-be.
   * *Megoldás:* Payloadban érdemes timestamp-et küldeni, vagy az idempotenciát biztosító fejléceket (`Idempotency-Key`) használni, ahogy azt iparági standardok, mint a Stripe vagy a Sanity Webhooks teszik (forrás: https://www.sanity.io/docs/webhooks). A BullMQ FIFO sorrendisége eleve csökkenti ennek az esélyét.

Ez az architektúra maximálisan tehermentesíti az ERP rendszert az anonim forgalomtól (hiszen a letöltések 99%-át a Next.js CDN szolgálja ki), miközben biztosítja az akár azonnali ár- és raktárkészlet szinkronizációt a BullMQ és a `revalidateTag` együttes erejével.

---

## Q2 — Headless CMS választás

> **Kérdés:** A KGC-4-ben NINCS Article modul. Külön headless CMS-t használjunk (Strapi/Sanity/Payload/Directus), vagy Next.js MDX/fs-based? Multi-tenant, magyar admin UI, ERP-mező-merge.

A Kisgépcentrum specifikus elvárásai (nem fejlesztő tartalomszerkesztő, dedikált ERP a termékadatoknak, viszonylag alacsony CMS tartalom darabszám, no vendor-lock-in) alapján az alábbi elemzés és javaslat adható.

### 1. Összehasonlító tábla a headless CMS és MDX opciókról

| Rendszer | Hostolás | Magyar i18n UI | Multi-tenant | Licenc | TS-native | Tanulási görbe | Hosting költség | Next.js integráció |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Strapi 5** | Self-hosted / Cloud [1] | Van (közösségi) | Fizetős (Enterprise) | Nyílt forráskódú (MIT) [2] | Támogatott [3] | Közepes | Alacsony (VPS, pl. 5-10$/hó) | Jó (REST/GraphQL [4]) |
| **Payload CMS 3** | Self-hosted / SaaS | Igen | Nincs natív ingyenes | Nyílt forráskódú [5] | Igen | Közepes | Alacsony (VPS / Vercel) | Kiváló (Developer-first [5]) |
| **Sanity** | Csak SaaS (Cloud) [6] | Angol / Részleges | Igen (Pro) | Zárt backend (Content Lake [7]) | Igen | Meredek | Ingyenes tier / Drága SaaS | Kiváló |
| **Directus** | Self-hosted / Cloud [8] | Igen | Igen | BSL 1.1 (5M$ bevétel felett licencköteles) [9] | Igen | Közepes / Meredek | Alacsony (VPS) | Jó |
| **Keystone 6** | Self-hosted | Angol / Egyedi | Nincs | Nyílt forráskódú [10] | Igen | Közepes | Alacsony (VPS) | Jó |
| **TinaCMS** | Git-backed / Cloud [11] | Angol | Nincs | Nyílt forráskódú [10] | Igen | Alacsony | Ingyenes (Vercel+Git) | Kiváló |
| **Next.js + MDX** | Git-based | **Nincs UI** (Domi miatt kiesik) | N/A | Nyílt | Igen | Szerkesztőnek **lehetetlen** | Ingyenes (Vercel) | Natív [12] |

*(Megjegyzés: A Contentlayer használata szigorúan ellenjavallt, mivel a projekt finanszírozás hiányában leállt és már nem támogatott [13].)*

### 2. Konkrét ajánlás a KGC-4 esetére

A legjobb választás a **Payload CMS 3** vagy a **Strapi 5**.

Mivel Domi (egy 1 fős, nem fejlesztő tartalomszerkesztő) fogja használni, és a cél a magyar nyelvű, letisztult UI, a **Next.js + MDX** megoldást el kell vetni (nincs grafikus admin felület a szerkesztéshez). A **Sanity** a SaaS-lock-in (zárt Content Lake adatbázis [14]) miatt esik ki. 

A **Strapi 5** rendkívül népszerű, könnyen induló rendszer [15], amelynek az MIT licence ingyenes használatot biztosít [2]. A **Payload CMS 3** egy modern, fejlesztőbarát, TypeScript-alapú alternatíva [5], ami már önmagában is a Next.js ökoszisztémára épül, így egyetlen kódbázison tartható a Next.js front-enddel, minimalizálva a szerver/hosting költségeket (egy Vercel deploy elég lehet). 
**Javaslat:** Érdemes a **Payload CMS 3**-at választani a kiváló Next.js integrációja, a fejlesztői élmény és a könnyű testreszabhatóság miatt, de ha dobozosabb, többnyelvű admin felületre van szükség "kattintgatósabb" beállítással, akkor a **Strapi 5** a nyertes.

### 3. Hybrid integration pattern (Kód-szinten)

A Next.js (App Router) szerver-oldali komponenseivel (RSC) tökéletesen megvalósítható a hibrid minta. A CMS-ből lekérjük a SEO cikk tartalmát, az ERP-ből pedig a valós idejű gép-adatokat. A teljesítmény miatt érdemes a két kérést párhuzamosítani (`Promise.all`), valamint az on-demand cache revalidációt (`revalidateTag` vagy `revalidatePath` [16], [17]) alkalmazni.

**Példa implementáció (Next.js 14+ App Router):**

```tsx
// app/gepek/[slug]/page.tsx
import { notFound } from 'next/navigation';
import { unstable_cache } from 'next/cache'; // [18]

// 1. CMS adat lekérése (Strapi vagy Payload)
const getCmsArticle = async (slug: string) => {
  const res = await fetch(`https://cms.kgc-berles.hu/api/articles?slug=${slug}`, {
    next: { tags: [`cms-article-${slug}`], revalidate: 3600 } // 1 órás cache [19]
  });
  if (!res.ok) return null;
  return res.json();
};

// 2. ERP adat lekérése a KGC-4 portal-equipment API-ból
const getErpEquipmentData = async (equipmentId: string) => {
  const res = await fetch(`https://erp.kgc-berles.hu/api/portal-equipment/${equipmentId}`, {
    next: { tags: [`erp-equipment-${equipmentId}`], revalidate: 60 } // Gyakrabban frissül [20]
  });
  if (!res.ok) return null;
  return res.json();
};

export default async function EquipmentLandingPage({ params }: { params: { slug: string } }) {
  // Párhuzamos adatlekérés a hibrid felülethez
  const cmsData = await getCmsArticle(params.slug);
  
  if (!cmsData || cmsData.data.length === 0) {
    notFound();
  }

  const article = cmsData.data;
  // Az ERP azonosítót a CMS cikk tartalmazza egy egyedi mezőben
  const erpData = await getErpEquipmentData(article.erp_equipment_id);

  return (
    <article className="container mx-auto">
      {/* CMS-ből jövő SEO tartalom */}
      <h1 className="text-3xl font-bold">{article.title}</h1>
      <div className="prose" dangerouslySetInnerHTML={{ __html: article.content }} />

      {/* ERP-ből jövő valós idejű adatok */}
      {erpData && (
        <div className="mt-8 p-4 bg-gray-100 rounded-lg">
          <h2>Bérlési információk</h2>
          <p>Napi bérleti díj: <strong>{erpData.dailyRate} Ft</strong></p>
          <p>Aktuális készlet: 
            <span className={erpData.stock > 0 ? "text-green-600" : "text-red-600"}>
              {erpData.stock > 0 ? `${erpData.stock} db elérhető` : 'Jelenleg kiadva'}
            </span>
          </p>
        </div>
      )}
    </article>
  );
}
```

Ha az ERP-ben változik a készlet, egy webhook meghívhatja a Next.js `revalidateTag` API route-ját [21], így az oldal azonnal, a teljes újrafordítás (build) nélkül frissül [22].

### 4. Migration-cost becslés

Ha később váltani kell egy másik CMS-re, a migrációs költség **rendkívül alacsony** lesz:
1. **Tartalom mennyisége:** ~50 darab SEO cikk és hír manuális átmásolása (copy-paste) egy új felületre legfeljebb 1-2 munkanap egy adatrögzítőnek. 
2. **Kód szintű migráció:** Mivel Next.js App Routert használunk, és az ERP adatok teljesen le vannak választva a CMS-ről, a kód átírása kimerül a `getCmsArticle` függvény (és esetlegesen a JSON/GraphQL válasz transzformációjának) átírásában. Ez egy senior fejlesztő számára kevesebb mint 1 napos munka.

### 5. Buktatók és kockázatok

*   **Locked-in Sanity:** Bár a Sanity fejlesztői élménye zseniális, az adatok a Sanity saját "Content Lake" nevű NoSQL adatbázisában élnek [7]. A Vendor lock-in erős: ha a KGC-4 nem akar havidíjat fizetni, vagy az adatokat teljesen on-premise szeretné tartani, a Sanity nem opció, mivel nem self-hostolható a backend [23], [14].
*   **Strapi self-host learning curve:** Bár a Strapi remek nyílt forráskódú opció [24], egy Node.js (vagy Docker) backendet, plusz egy PostgreSQL/MySQL adatbázist kell üzemeltetni és frissíteni [1]. A verziófrissítések (pl. a közelmúltbeli v4 -> v5 [25]) töréshez vezethetnek. További apró buktató, hogy a Strapi REST API-ja alapértelmezetten nagyon mély JSON-struktúrát ad vissza, amit kliens oldalon mindig transzformálni kell.
*   **Payload CMS admin-UI quirks:** A Payload CMS rendkívül fejlesztő-központú [5], emiatt ha az admin UI-ban olyan mezőket kell "összekattintgatni" vagy átszabni, ami nem jön "dobozból", ahhoz be kell nyúlni a React kódba. Nem technikai beállítottságú emberek (Domi) nem tudják egyedül módosítani a modelleket, minden módosítás fejlesztői beavatkozást igényel.
*   **Next.js + MDX (Contentlayer):** Ha a kódalapú szerkesztés mellett döntenél, a Contentlayer nagyon erős buktató: a projekt elhagyatott, az open-source karbantartása leállt [13]. Ha mégis MDX kell, a hivatalos `@next/mdx` csomagot kell használni [26], de a tartalomírás Git-commitokhoz lenne kötve, amit egy átlagos adminisztrátor nem fog tudni elsajátítani.

## Felhasznált források

- [Strapi, the leading open-source headless CMS](https://strapi.io/blog/strapi-5-released)
- [Draft & Publish | Strapi 5 Documentation](https://docs.strapi.io/cms/features/draft-and-publish)
- [Welcome to the Strapi CMS Documentation! | Strapi 5 Documentation](https://docs.strapi.io/cms/intro)
- [Headless CMS - Top Content Management Systems | Jamstack](https://jamstack.org/headless-cms/)
- [GROQ-powered webhooks | Sanity Docs](https://www.sanity.io/docs/webhooks)
- [Create a Project | Directus Docs](https://docs.directus.io/getting-started/quickstart.html)
- [Get Started and learn about TinaCMS](https://tina.io/docs)
- [Guides: MDX | Next.js](https://nextjs.org/docs/app/building-your-application/configuring/mdx)
- [GitHub - contentlayerdev/contentlayer: Contentlayer turns your content into data - making it super easy to import MD(X) and CMS content in your app · GitHub](https://github.com/contentlayerdev/contentlayer)
- [Home | Sanity Docs](https://www.sanity.io/docs)
- [Functions: revalidatePath | Next.js](https://nextjs.org/docs/app/api-reference/functions/revalidatePath)
- [Functions: revalidateTag | Next.js](https://nextjs.org/docs/app/api-reference/functions/revalidateTag)
- [Incremental Static Regeneration (ISR)](https://vercel.com/docs/incremental-static-regeneration)
- [Dolibarr Open Source ERP and CRM - Web suite for business](https://www.dolibarr.org/)
- [Debezium connector for PostgreSQL :: Debezium Documentation](https://debezium.io/documentation/reference/stable/connectors/postgresql.html)


---

## Q3 — Multi-tenant publikus API

> **Kérdés:** Anonymous-access publikus endpointokon mikor melyik tenant-resolution? RLS-aware read-only views. Rate-limit per tenant + bot-protection (hCaptcha/Turnstile). DDoS-mitigation.

A multi-tenant ERP rendszer (KGC-4) publikus végpontjainak és a Next.js frontend integrációjának biztonságos tervezéséhez az alábbi stratégiákat és megoldásokat érdemes alkalmazni az általad felvetett 6 pont mentén.

### 1. Tenant-resolution strategy (Bérlő-azonosítási stratégiák összehasonlítása)

A publikus hozzáférésű (anonymous) végpontokon a bérlő azonosításának módja kritikus mind biztonsági, mind SEO és cache-elési szempontból.

*   **URL-subdomain (`elad.kisgepcentrum.hu`):** Ez a **legjobb megoldás SEO és cache-elés szempontjából**. A keresőmotorok különálló entitásként tudják kezelni a bérlőket, a CDN és a böngésző cache pedig egyértelműen a *Host* alapján tudja szeparálni a tartalmat. Biztonsági szempontból is kiváló, mivel a böngészők "same-origin" és "same-site" irányelvei (SOP, CORS) szigorúan érvényesülnek a különböző aldomainek között [1, 2].
*   **Path-prefix (`/t/elad/...`):** SEO és cache-elés szempontjából szintén kiváló választás, mert az erőforrás útvonala egyedi. Hátránya, hogy az összes bérlő ugyanazon az "origin"-en (domainen) osztozik, így egy esetleges XSS sebezhetőség esetén a sessionök és a localStorage adatok bérlők között is kompromittálódhatnak [3, 4].
*   **Origin-header:** Bár beépített webes mechanizmusokon alapul, **API szinten könnyen hamisítható** (bármilyen HTTP klienssel szabadon módosítható az `Origin` fejléc, a böngészőket kivéve) [5]. Cache-elésnél a CDN-t be kell állítani a `Vary: Origin` fejléc figyelembevételére, különben a bérlők egymás adatait láthatják. SEO szempontból a frontend URL-nek továbbra is egyedinek kell lennie.
*   **Query-paraméter (`?tenantId=...`):** Ahogy az audit is rámutatott, ez a legkevésbé biztonságos. A paraméterek gyakran bekerülnek a webkiszolgálók (Nginx), a proxik és a böngészők naplófájljaiba (history, referer), ami adatszivárgáshoz vezethet [6, 7]. Ezen felül a cache busting (véletlenszerű paraméterek hozzáfűzése) is problémásabbá teheti a gyorsítótárazást.
*   **API-key header:** Anonymous frontend hozzáférés esetén **nem használható biztonságosan**, mivel az API kulcsot a böngészőben, a kliensoldali kódban kellene tárolni, ahol az publikusan hozzáférhetővé és ellophatóvá válik [8, 9]. Ez a megközelítés kizárólag szerver-szerver (backend-for-frontend) kommunikációhoz ideális.

**Győztes:** Az **URL-subdomain** vagy a **Path-prefix** megközelítés alkalmazása javasolt a Next.js frontenden. A Next.js a kéréskor kinyeri a subdomaint vagy path-t, majd a háttérben biztonságosan (akár egy belső API key-vel) kommunikál a backenddel, elrejtve a tenant-rezolúció sérülékeny részeit az ügyfél elől.

### 2. PostgreSQL RLS-aware read-only views mintája

Ha az anonim felhasználó csak olvasni (`SELECT`) jogosult a katalógust, a Row Level Security (RLS) biztosítja az adatbázis szintű izolációt [10]. A `BYPASSRLS` attribútumot **kizárólag adminisztrátori vagy szuperfelhasználói fiókokhoz szabad használni**, anonim vagy publikus hozzáférés esetén szigorúan kerülendő, mivel az teljesen megkerüli a biztonsági rendszert [11].

A helyes minta (pattern) a `SET LOCAL` tranzakciószintű változó és az RLS policy kombinációja. Ezt a NestJS (Prisma middleware) állítja be minden kérésnél:

```sql
-- 1. Engedélyezzük az RLS-t a táblán
ALTER TABLE "RentalEquipment" ENABLE ROW LEVEL SECURITY;

-- 2. Létrehozunk egy read-only policy-t az anonim hozzáféréshez
CREATE POLICY tenant_isolation_select_only ON "RentalEquipment"
FOR SELECT 
USING (
  tenant_id = (current_setting('app.tenant_id', true))::uuid
);
```

**Fontos megjegyzés:** Érdemes az alkalmazásnak egy dedikált, csökkentett jogosultságú (pl. `anon`) Postgres "Role"-t használnia az adatbázis-kapcsolathoz, amelyik kizárólag `SELECT` joggal rendelkezik a szükséges táblákon [12]. Ha bonyolultabb lekérdezésekre van szükség (ahol JOIN-ok merülhetnek fel), a performanciára is ügyelni kell: az indexeket fel kell készíteni a `tenant_id` szűrésekre, illetve `SECURITY DEFINER` funkciók is alkalmazhatók, de csak fokozott óvatossággal [13-15]. 

### 3. Rate-limit per tenant stratégia

A Rate-limiting implementációjánál érdemes megkülönböztetni az infrastruktúra és az alkalmazás rétegét. Mindhárom általad említett megoldás hasznos, de más-más fázisban:

1.  **Cloudflare Workers Rate Limiting:** Ez a legjobb eszköz a **DDoS és a brute-force jellegű támadások peremhálózati (Edge) megállítására** [16, 17]. Itt a `namespace_id` és a kérés azonosítói (IP + path) alapján állíthatsz be korlátokat úgy, hogy az a backendet egyáltalán ne terhelje [18-20].
2.  **NestJS Throttler (tenant-aware kulccsal):** Ezt akkor használd, ha az üzleti logika (business logic) alapján kell finomhangolni a korlátozást (például bizonyos tenantok prémium csomagban vannak és magasabb API kvótát kapnak). A `@nestjs/throttler` modul `getTracker` és `generateKey` metódusainak felülírásával a kulcs tartalmazhatja a kliens IP-címét és a feloldott `tenantId`-t is [21-23].
3.  **Redis-alapú elosztott throttling:** Mivel a KGC-4 egy skálázott ERP, a NestJS Throttler mögé egy Redis storage providert kell kötni, amely biztosítja az in-memory cache globális (elosztott) szinkronizációját az összes backend példány között [24-26].

**Mikor melyik?**
A katalógus böngészésére (read) a Cloudflare Rate Limiting nyújt megfelelő alapot az extrém terhelés elkerülésére [17]. A kritikusabb interakciókat (pl. bérlés indítása, kapcsolatfelvétel) a NestJS + Redis Throttlerrel érdemes védeni, tenant-specifikus kulcsokkal [24].

### 4. Bot-protection (Katalógus vs. Mutáció)

Az anonim böngészéshez és a katalógus listázásához (amelyet pl. a Google is indexel) a bot-védelem nem állhat az útjába a valid forgalomnak.

*   **Katalógus (Read-only):** Itt nem javasolt alkalmazásszintű CAPTCHA. Ehelyett a Cloudflare mögötti "Invisible" védelemre (Bot Management) kell támaszkodni, amely hálózati anomáliák vagy rosszindulatú viselkedés esetén önállóan blokkol anélkül, hogy a felhasználót vizuális feladatok (képfelismerés) elé állítaná [27, 28].
*   **Kontakt form / Mutációk:** Ide kifejezetten ajánlott a **Cloudflare Turnstile**. A Turnstile nagy előnye a reCAPTCHA-val és hCaptcha-val szemben, hogy "Managed" (vagy teljesen láthatatlan) módban működik, és proof-of-work/proof-of-space algoritmusokkal böngésző környezetet validál anélkül, hogy interaktív vizuális feladványokkal rontaná a felhasználói élményt vagy az akadálymentesítést (WCAG 2.1 Level AA) [27, 29-31]. Beállíthatod "Invisible" módra is, így a form beküldésénél transzparensen szűri ki a botokat [31, 32].

### 5. DDoS-mitigation a három rétegben

A hatékony DDoS védelem "Defense in Depth" (többrétegű) koncepcióra épül:

1.  **Cloudflare (L3/L4 és L7):** Az elsődleges védvonal. Itt történik a globális hálózati forgalom szűrése, a Web Application Firewall (WAF) futtatása és a statikus/katalógus assetek (Next.js ISR vagy cache) kiszolgálása a peremhálózatról, tehermentesítve az eredeti szervert [16].
2.  **Nginx (Reverse Proxy):** *(Bár a megadott források dedikáltan nem térnek ki az Nginx beállításaira, iparági standardként ide tartozik)* az alapvető TCP szintű korlátozások beállítása. Ilyen a `limit_conn` (egyidejű kapcsolatok korlátozása), a `limit_req` (kérések rátájának korlátozása), valamint a timeout-ok (pl. `client_body_timeout`) finomhangolása a Slowloris típusú támadások ellen.
3.  **NestJS (App réteg):** Itt kezeljük a specifikus üzleti szintű túlterhelést. Ebbe beletartozik a korábban említett `@nestjs/throttler`, az OWASP ajánlások szerinti méretkorlátok érvényesítése (payload size limits), valamint a megfelelő timeoutok és aszinkron feladatok sorba rendezése (pl. BullMQ) a processzor vagy a memória kimerülésének elkerülésére [21, 33, 34].

### 6. Audit-log + suspicious-pattern alert

Az OWASP biztonsági irányelvei alapján a gyanús viselkedés (pl. 1000+ kérés/óra egyazon IP-ről) monitorozása elengedhetetlen a proaktív védelemhez [35, 36].

A rendszer tervezésénél a következőket érdemes bevezetni:
*   **Adatok gyűjtése:** Minden interakciónál (különösen mutációknál és hibás kéréseknél) naplózni kell az IP-címet, a kért végpontot, a bérlő azonosítóját (tenantId), valamint a User-Agent-et [35, 36].
*   **Detektálás valós időben:** A Cloudflare Rate Limiting API és Analytics önmagában képes detektálni és logolni (429 Too Many Requests) a hirtelen kiugrásokat az egyes lokációkon [20, 37]. 
*   **Alkalmazás szintű alert:** A NestJS rétegben az exception filterekkel és a Throttler-rel elfoghatod a `ThrottlerException` hibákat [38]. Ezeket az eseményeket célszerű strukturált logként (pl. JSON formátumban) egy központi naplózó rendszerbe (ELK stack, Datadog) továbbítani. 
*   **Gyanús mintázatok elemzése:** Ha az anomáliák (pl. az `Origin` fejléc cserélgetése vagy túlzott próbálkozások száma) túllépik az előre definiált küszöböt, a rendszer automatikusan ideiglenes IP-tiltást (Account Lockout / IP ban) vagy WAF szabály-frissítést indíthat el [35, 36, 39].

## Felhasznált források

- ["Same-site" and "same-origin" | Articles | web.dev](https://web.dev/articles/same-site-same-origin)
- [Session Management - OWASP Cheat Sheet Series](https://owasp.org/www-project-cheat-sheets/cheatsheets/Session_Management_Cheat_Sheet.html)
- [JWT authentication: Best practices and when to use it - LogRocket Blog](https://blog.logrocket.com/jwt-authentication-best-practices/)
- [PostgreSQL: Documentation: 18: 5.9. Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Row Level Security | Supabase Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Overview · Cloudflare Turnstile docs](https://developers.cloudflare.com/turnstile/)
- [Rate Limiting · Cloudflare Workers docs](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)
- [GitHub - nestjs/throttler: A rate limiting module for NestJS to work with Fastify, Express, GQL, Websockets, and RPC 🧭 · GitHub](https://github.com/nestjs/throttler)
- [Rate Limiting | NestJS - A progressive Node.js framework](https://docs.nestjs.com/security/rate-limiting)
- [Cloudflare is free of CAPTCHAs; Turnstile is free for everyone](https://blog.cloudflare.com/turnstile-ga/)
- [Authentication - OWASP Cheat Sheet Series](https://owasp.org/www-project-cheat-sheets/cheatsheets/Authentication_Cheat_Sheet.html)


---

## Q4 — Cross-app SSO

> **Kérdés:** KGC-4 portal-auth OTP/Magic-link alapú. Hogyan bridge-eljük kgc-berles Next.js-felé? NextAuth + JWT? OIDC + Keycloak? Cookie-cross-subdomain? GDPR.

A KGC-4 ERP portal-auth rendszerének integrálása a Next.js (`kgc-berles`) frontenddel egy kritikus architekturális döntés, amelynél az egyensúlyt a biztonság, a fejlesztési sebesség és a jövőállóság (pl. passkey) között kell megtalálni. 

Íme a részletes, OWASP és GDPR szempontokat is figyelembe vevő szakértői elemzés és válasz a kérdéseidre:

### 1. A 3-opció összehasonlítása

**(A) NextAuth.js v5 (Auth.js) Credentials provider + KGC-4 backend hívás**
*   **Működés:** A Next.js oldalon az Auth.js `Credentials` providert használjátok [1]. A felhasználó beírja az OTP-t a Next.js felületen, az Auth.js a háttérben meghívja a KGC-4 `/portal/auth/verify-otp` endpointját. Siker esetén az Auth.js egy saját, titkosított (JWE) JWT session tokent generál, amit egy `HttpOnly` süti formájában tárol a böngészőben [2].
*   **Előnyök:** Nagyon gyorsan implementálható, a Next.js ökoszisztémával (App Router, Server Actions) tökéletesen integrált [3]. Beépített védelmet ad a session kezelésre (pl. cookie darabolás, automatikus lejárati idő kezelés) [4], és nem igényel adatbázist a Next.js oldalon a session-höz [5].
*   **Hátrányok:** A Next.js session JWT és a KGC-4 backend JWT elválhat egymástól (dupla token kezelés), hacsak a KGC-4 által adott tokent nem csomagoljátok bele az Auth.js tokenjébe.

**(B) Keycloak OIDC (Valós integráció)**
*   **Működés:** A KGC-4-ben lévő stub élesítése. A Keycloak átveszi a teljes identitáskezelést, ő lesz az Identity Provider (IDP) [6]. A Next.js az Auth.js `Keycloak` providerével kapcsolódik hozzá [1]. A jelszómentes (OTP/WebAuthn) authentikációt a Keycloak beépített "Authentication Flows" rendszere kezelné [7].
*   **Előnyök:** Kiemelkedően robusztus, szabványos OAuth 2.0 / OIDC implementáció [8], [9]. Gyárilag támogatja a jelszómentes (Passkey/WebAuthn) bejelentkezést, a brute-force elleni védelmet és a felhasználói fiókok összekapcsolását (Identity Brokering) [10], [11], [12].
*   **Hátrányok:** Jelentős infrastrukturális teher és bevezetési költség. A meglévő `PortalUser` adatokat migrálni kellene, a KGC-4-et pedig Resource Serverré kellene alakítani.

**(C) Custom JWT Bridge**
*   **Működés:** A felhasználó a KGC-4 `/verify-otp` endpointjával kommunikál (akár a Next.js API route-jain keresztül proxyzva [13]), a KGC-4 állítja ki a JWT-t, majd a Next.js egy shared-secret (HS256) vagy RSA publikus kulcs (RS256) segítségével csupán validálja azt [14], [15].
*   **Előnyök:** Nincs extra függőség (mint az Auth.js), teljes kontroll a süti és a token felett. Kisebb overhead.
*   **Hátrányok:** A session menedzsment biztonsági funkcióit (cookie security, token lejárati idők, session frissítés) manuálisan kell lefejleszteni, ami magas kockázatú OWASP sebezhetőségekhez vezethet [16], [17].

### 2. Cookie-cross-subdomain kontraktus

Mivel a KGC-4 backend és a Next.js frontend is a `*.kisgepcentrum.hu` domain alatt fog futni, a süti beállítások kritikusak a biztonságos kommunikációhoz:
*   **`Domain=.kisgepcentrum.hu`:** Ez teszi lehetővé, hogy a `api.kisgepcentrum.hu` és a `berles.kisgepcentrum.hu` is megkapja és olvashassa a sütit [18].
*   **`Path=/`:** A süti a domain minden útvonalán érvényes lesz [19].
*   **`HttpOnly`:** Szigorúan kötelező. Megakadályozza, hogy kliens oldali JavaScript (pl. `document.cookie`) hozzáférjen a tokenhez, ezáltal kivédi a legtöbb Cross-Site Scripting (XSS) alapú session-lopást [20], [21].
*   **`Secure`:** Szintén kötelező. Biztosítja, hogy a süti csak titkosított HTTPS csatornán utazzon, védve a Man-in-the-Middle (MitM) lehallgatástól [22], [23].
*   **`SameSite=Lax` vs `None`:** Mivel a szubdomainek az eTLD+1 definíció szerint azonos webhelynek ("same-site") minősülnek, a `SameSite=Lax` tökéletes választás [24], [25]. A `Lax` engedi a sütik küldését a domainen belüli top-level navigációk során, de megvéd a Cross-Site Request Forgery (CSRF) támadások nagy részétől [26], [27]. A `SameSite=None` használatára csak akkor lenne szükség, ha egy teljesen harmadik (cross-site) domaint is be akarnátok vonni, amihez kötelező lenne a `Secure` flag is [23]. Kifejezetten a **`SameSite=Lax`** ajánlott a ti esetetekben.
*   **Cookie név prefixek:** Érdemes a `__Host-` vagy `__Secure-` prefixet használni (pl. `__Secure-KGC-Session`), ami kikényszeríti a böngésző szintjén a HTTPS használatát [28], [29]. *(Megjegyzés: A `__Host-` prefix nem engedi a `Domain` attribútum használatát, így szubdomaines megosztáshoz a `__Secure-` használható [28], [29]).*

### 3. OTP / Magic-link flow és az Open-Redirect védelem

Ha a Magic Link e-mailben egy egyedi link érkezik, ami a Next.js oldalra viszi a felhasználót, majd onnan visszairányít a korábban megtekintett oldalra (`return_to`), hatalmas az "Open Redirect" (Nyílt átirányítás) veszélye [30]. A támadók ezt adathalászatra használják, például hitelesítés után egy rosszindulatú oldalra irányítva a felhasználót.
*   **Megoldás:** Szigorú engedélyezőlista (Allowlist) implementálása a backend és a frontend szintjén is. A `redirect_uri` vagy `return_to` paramétert validálni kell a KGC-4 oldalon mielőtt a tokent kiállítja, és a Next.js oldalon is az átirányítás előtt.
*   Használjatok egzakt string egyezést vagy nagyon szigorú Reguláris Kifejezéseket (Regex), amelyek nem engednek meg semmilyen külső domaint vagy sémát [31], [32], [33]. (pl. a `return_to` csak `^/([a-zA-Z0-9-/_]+)?$` formátumú relatív path lehet).

### 4. WebAuthn / Passkey beépíthetősége (2026 trend)

A Passkey és a Web Authentication API a modern jelszómentes authentikáció csúcsa (FIDO2 alapokon), amely a jelszavakat eszközön tárolt biometrikus (ujjlenyomat, FaceID) kulcspárokkal helyettesíti [34], [35]. Az adathalászat (phishing) ellen teljes védelmet nyújt [36].
*   A későbbiekben **nagyon könnyen beépíthető**, különösen, ha az Auth.js-t (NextAuth) választjátok, mivel a v5-ös verzió már kínál dedikált, beépített kísérleti (experimental) WebAuthn providert [1], [37]. 
*   Ehhez a KGC-4 `PortalUser` tábláját vagy egy kapcsolódó táblát fel kell készíteni a publikus kulcsok (`publicKey`), a `credentialID` és a hitelesítő adatok (`authenticatorData`) tárolására [38], [39].

### 5. GDPR szempontok

A személyes adatok (PII) védelme [40] miatt:
*   **Data Minimization (Adattakarékosság):** A JWT payload (Claims) kizárólag a legszükségesebb azonosítókat tartalmazza (pl. `sub`, amely lehet a PortalUser UUID-ja) és a jogosultságokat. Ne tegyetek e-mail címet, telefonszámot vagy más személyes adatot a JWT-be [41], [42], így a cookie dekódolása esetén sem szivárog adat. A Next.js csak azt húzza le a profil végpontról, amire a rendereléshez azonnal szüksége van.
*   **Account Deletion (Fiók törlése):** Mivel létezik a GDPR-delete endpoint az ERP-ben, a Next.js frontenden biztosítani kell ennek egyszerű elérhetőségét. Törlés után **kötelező** a session teljes invalidálása (mind a böngészőből, a cookie törlésével [43], mind a backendről, feketelista/visszavonás bevezetésével, hogy a korábban kiadott tokenek is érvényüket veszítsék).
*   **Audit Log:** Rögzíteni kell a session életciklus eseményeit (létrehozás, használat, megsemmisítés) [44]. Az audit naplókba *tilos* a nyers JWT-t vagy Session ID-t elmenteni. Helyette a token SHA-256 sózott hash-ét naplózzátok, a kliens IP-jével és a gyanús eseményekkel együtt [45].

### 6. OWASP Buktatók és Védekezés

*   **Session Fixation:** Az OTP/Magic Link megadásakor (a jogosultsági szint változásakor, azaz az anonim státuszból hitelesített státuszba lépéskor) a session azonosítót **kötelező** megújítani (Regenerate Session ID) [46], [47].
*   **Brute-Force OTP ellen:** Egy támadó végigpróbálhatja az SMS OTP-ket. Kőkemény Rate Limiting-re, "Login Throttling"-ra és végül ideiglenes (majd permanens) fiók zárolásra (Account Lockout) van szükség a KGC-4 `/verify-otp` endpointján (pl. 3-5 hibás próbálkozás után 15 perces zárolás) [48], [49], [12], [50].
*   **Magic Link Expiry és Replay attack:** A kiküldött magic linkek tartalmazzanak elegendő entrópiával rendelkező egyszer használatos tokent (nonce / jti claim) [51]. A lejárati idejük legyen rendkívül rövid (pl. 5-15 perc) [52], [53]. Ha a linket egyszer kattintották, azonnal kerüljön érvénytelenítésre [54].
*   **CSRF (Cross-Site Request Forgery):** Ahogy fentebb említve lett, a `SameSite=Lax` attribútum a böngésző szintjén megvéd ezektől [25], [26]. Emellett kerülendő a GET kérések használata állapotváltoztató (mutating) műveletekre.

### 7. Konkrét ajánlás a KGC-4 esetére + Sprint-feature lista Zoli felé

**Az Ajánlás:**
Javaslom az **(A) opciót (NextAuth.js v5 / Auth.js Credentials provider + KGC-4 hívás)** a jelenlegi fázisban, és hogy hagyjátok el a teljes Keycloak migrációt (B), kivéve, ha az ERP admin oldala miatt amúgy is kötelező az IDP bevezetése. A (C) Custom JWT túl sok fejlesztési/biztonsági terhet ró a csapatra. Az Auth.js kiválóan kezeli a JWE (titkosított) tokeneket, és beépített biztonsági best practice-ekkel dolgozik a Next.js alatt [2], [5]. Az Auth.js session tokent (`HttpOnly`, `Secure`, `SameSite=Lax`, `Domain=.kisgepcentrum.hu` prefixelve `__Secure-`) konfiguráljátok be [55], [28], [26], [29]. A belső KGC-4 által visszaadott JWT-t csak az API hívások authorization headerjéhez használjátok, maga az Auth.js elmentheti ezt a saját session-jében.

**Következő Sprint-feature lista Zoli felé (KGC-4 Backend & Next.js integráció):**

1.  **Backend - Rate Limiting & Lockout:** Brute-force elleni védelem bekötése az `/portal/auth/request-otp` és `/verify-otp` végpontokon (IP és User alapján). Maximálisan 5 próbálkozás, majd exponential backoff [49], [50].
2.  **Backend & Frontend - Open Redirect Validation:** A `return_to` változó szigorú validációja (Regex allowlist: csak relatív URL-ek engedélyezése, vagy szigorúan a `*.kisgepcentrum.hu` domain) [31], [32], [33].
3.  **Frontend - Auth.js v5 Implementáció:** A `kgc-berles` repóban a `Credentials` provider bekonfigurálása úgy, hogy a KGC-4 endpointjait hívja, majd a visszaadott User JSON-t és KGC JWT-t az Auth.js saját JWE sütijébe csomagolja [1], [2].
4.  **Cookie Biztonsági Beállítások:** Kereszt-domain működés konfigurálása: `Domain=.kisgepcentrum.hu`, `Path=/`, `HttpOnly=true`, `Secure=true`, `SameSite=Lax` mind a backend (ha dob sütit), mind a NextAuth szintjén [22], [18], [21], [26].
5.  **Backend - Audit Log & Session Revocation:** A Logout végpont és a GDPR-delete végpont hívása esetén a kiállított KGC-4 JWT azonnali érvénytelenítése (feketelistázás/revocation registry) [43]. A bejelentkezési kísérletek pseudonymizált (hashed session ID) naplózása az adatbázisban [45].
6.  **Kutatás / Architektúra (Spike):** KGC-4 adatmodell előkészítése a jövőbeli WebAuthn/Passkey publikus kulcsok (`publicKey`, `credentialID`) tárolására, hogy a jövő évben zökkenőmentes legyen az átállás [38], [39].

## Felhasznált források

- [Auth.js | Getting Started](https://authjs.dev/getting-started)
- [Auth.js | Session Strategies](https://authjs.dev/concepts/session-strategies)
- [Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Final: OpenID Connect Core 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [OAuth 2.0 — OAuth](https://oauth.net/2/)
- [File-system conventions: proxy.js | Next.js](https://nextjs.org/docs/app/api-reference/file-conventions/middleware)
- [Session Management - OWASP Cheat Sheet Series](https://owasp.org/www-project-cheat-sheets/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Set-Cookie header - HTTP | MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
- ["Same-site" and "same-origin" | Articles | web.dev](https://web.dev/articles/same-site-same-origin)
- [What are passkeys? - passkeys.dev](https://passkeys.dev/docs/intro/what-are-passkeys/)
- [Email Providers](https://authjs.dev/getting-started/authentication/email)
- [Guide to Web Authentication](https://webauthn.guide/)
- [Authentication - OWASP Cheat Sheet Series](https://owasp.org/www-project-cheat-sheets/cheatsheets/Authentication_Cheat_Sheet.html)
- [Options | NextAuth.js](https://next-auth.js.org/configuration/options)


---

## Q5 — Rental/booking integráció

> **Kérdés:** Real-time vs cached availability-calendar (29-nap, 5-min-stale). Deposit-flow (Stripe Setup-Intent / Barion / SimplePay). Booking → Rental conversion atomicity. Late-fee. Race-condition.

A Kisgépcentrum (KGC-4) ERP és a publikus Next.js weboldal integrációja egy komplex elosztott rendszertervezési feladat, különösen a készlet szinkronizációja és a tranzakciók (foglalás, kaució) biztonsága miatt. Az alábbiakban best-practice szinten, a legkorszerűbb technológiákat és iparági mintákat alapul véve részletezem a megoldásokat.

### 1. Real-time vs cached availability-calendar és SEO-barátság

A 29 napos naptárnál a folyamatos, minden látogatóra vetített real-time adatbázis-lekérdezés feleslegesen terheli az ERP-t, ráadásul a SEO-t is ronthatja, ha a lassan felépülő naptár rontja a Core Web Vitals (pl. LCP) értékeket.

*   **Next.js ISR (Incremental Static Regeneration) + SWR:** A legjobb SEO-barát és performáns megoldás a Next.js ISR használata [1]. Ez lehetővé teszi a statikus tartalmak háttérben történő frissítését [1]. Egy 5 perces elévülés (stale time) a böngészéshez teljesen tolerálható: a felhasználók azonnal betöltődő statikus HTML-t kapnak (amit a keresőmotorok is azonnal indexelnek), miközben a Next.js a háttérben frissíti a cache-t [1]. 
*   **On-demand revalidation:** Amikor egy új `Booking` létrejön az ERP-ben, az ERP egy webhookon keresztül meghívhatja a Next.js API-t a `revalidatePath` vagy a `revalidateTag` használatával [2-4]. Így a naptár azonnal, az 5 perces TTL megvárása nélkül is frissülhet [4].
*   **Live-update (Checkout fázis):** WebSocket használata felesleges túlzás ehhez a business flow-hoz. A böngészéshez elég az ISR, de amikor a felhasználó *kosárba teszi* a gépet vagy elindítja a checkout-ot, egy valós idejű (REST/GraphQL) hívással kell ellenőrizni az aktuális elérhetőséget az ERP-ben.

### 2. Deposit-flow (kaució) PSP-comparison

A gépkölcsönzésnél a kaució (deposit) kezelése a legkritikusabb pont, mivel a kölcsönzés időtartama gyakran meghaladja a kártyatársaságok standard pre-autorizációs (zárolási) limitjét (amely általában 7 nap).

*   **Stripe Setup-Intent:** Ez a legfejlettebb technikai megoldás. A Setup-Intent nem zárol azonnal, hanem elmenti a kártyaadatokat jövőbeli terhelés (off-session payment) céljából. Ez kiküszöböli a 7 napos zárolási limit problémáját, és ha a gépet sérülten hozzák vissza (`DAMAGED`), a kaució összege utólag levonható.
*   **Barion Reservation:** A magyar piacon népszerű, de a zárolt keret (reservation) általában maximum 7 napig tartható fenn. Ha a gépkölcsönzés 1-2 napos, ez tökéletes. Hosszabb bérlésnél viszont a zárolás automatikusan feloldódik.
*   **SimplePay:** Magyarországon a leginkább "NAV-friendly" és az ügyfelek által a legjobban ismert szolgáltató, amelyhez már V2 API és tokenizációs (ALU logika - fizetés kártyaadatokkal) megoldás is elérhető [5, 6]. 
*   **Ajánlás a magyar piacra:** A magyar vásárlói bizalom miatt a **SimplePay** használata javasolt, de a klasszikus zárolás helyett *kártyaregisztrációs (tokenizációs / ALU)* flow-t érdemes megvalósítani [6]. Így a bérleti díjat azonnal terhelitek, a kártya tokenjét pedig a `Rental` teljes életciklusa alatt megőrzitek, és a deposit státuszát (`Retained`) csak káresemény esetén, egy utólagos terheléssel (token alapján) hajtjátok végre.

### 3. Booking → Rental conversion atomicity

A `Booking.CONFIRMED` állapotból `Rental.DRAFT` vagy `ACTIVE` állapotba való átmenetet tranzakcionálisan, atomi módon kell végrehajtani.

*   **`SELECT FOR UPDATE` vs Advisory Locks:** A PostgreSQL `SELECT FOR UPDATE` sorszintű zárolást (Row-Level Lock) biztosít [7]. Amikor a konverziós logikát futtatod, ez a parancs zárolja az adott `Booking` rekordot addig, amíg a tranzakció véget nem ér, megakadályozva, hogy egy másik konkurens folyamat (pl. egy webhook újrapróbálkozás) ugyanazt a foglalást kétszer konvertálja [7, 8].
*   **Idempotency Key (Idempotent Receiver):** Az elosztott rendszerek alapvető mintája az idempotencia [9]. A frontend vagy a fizetési szolgáltató által küldött konverziós kérésnek tartalmaznia kell egy egyedi idempotencia-kulcsot, amit az ERP letárol. Ha hálózati hiba miatt ugyanaz a kérés kétszer érkezik be, az ERP felismeri a kulcsot, és nem hoz létre új `Rental` entitást [9, 10].
*   **Ajánlás:** Kombinált megközelítés: Használj adatbázis-tranzakciót és `SELECT FOR UPDATE`-et a sorszintű védelemre [7], valamint idempotencia-kulcsokat a hálózati duplikációk kiszűrésére [10].

### 4. Concurrent-booking race-condition (Versenyhelyzet)

Két user pont ugyanazt a vibrátort akarja lefoglalni ugyanarra a napra.

*   **Pre-reserve TTL-szel (Redis Distlock):** A felhasználói élmény szempontjából a legrosszabb, ha valaki végigcsinálja a checkoutot, majd a fizetés gombra kattintva kapja meg, hogy "már lefoglalták". Ennek elkerülésére a **Redlock algoritmust** érdemes használni a Redisben [11, 12].
*   **Hogyan működik:** Amikor a User A beteszi a gépet a kosárba és elindítja a checkoutot, az alkalmazás egy elosztott zárat (distributed lock) kér a Redisben a `resource_id + date` kulcsra, mondjuk 15 perces TTL-el (Time To Live) [13]. Eközben a User B a naptárban már "Foglalt" (vagy "Fizetés alatt") státuszt lát. Ha User A befejezi a fizetést, a zár feloldódik, és a végleges Postgres tranzakció rögzíti az adatokat. Ha User A kilép, 15 perc után a TTL lejár, és a gép újra felszabadul [14].

### 5. Late-fee számítás

*   **Cron-batch:** Ideális a napi állapotváltozásokra (pl. minden éjfélkor az `ACTIVE` bérléseket, amelyeknek lejárt a határideje, `OVERDUE` státuszba billenti és küld egy e-mailt).
*   **On-checkout-recalculate:** A pontos pénzügyi elszámolás (kaució visszatartása, pótdíj terhelése) akkor történhet meg precízen, amikor a gépet fizikailag visszahozzák a telephelyre (a status `RETURNED` vagy `COMPLETED` lesz). Ekkor kell dinamikusan újraszámolni a díjat a tényleges visszahozatal időbélyege alapján.
*   **Ajánlás:** Hibrid modell. Éjszakai cron job a státuszváltáshoz és riasztáshoz, de a konkrét összeg kiszámolása szigorúan az *on-checkout-recalculate* eseményre (az ERP-ben történő lezáráskor) történjen.

### 6. ICalendar export (RFC 5545)

A bérlők számára a naptár integráció óriási UX-növelő tényező. Az RFC 5545 szabvány írja le az iCalendar objektumokat [15].
A backendnek egy olyan végpontot kell biztosítania (pl. `/api/bookings/{id}/ical`), amely dinamikusan generál egy `text/calendar` MIME típusú fájlt [15]. Ennek tartalmaznia kell a `BEGIN:VCALENDAR` blokkon belül egy `BEGIN:VEVENT` objektumot, amely megadja a bérlés kezdetét (`DTSTART`), a visszahozatal kötelező idejét (`DTEND`), és a gép átvételi helyét (a telephely címét).

### 7. Booking-engine case study: Cal.com és Turo

*   **Cal.com (cal.diy):** Ez az open-source scheduling szoftver (mely Next.js, Prisma, PostgreSQL stacken fut) nagyszerű példa [16, 17]. Webhookokat használnak az aszinkron események kezelésére (pl. naptár szinkronizáció) és szigorú tranzakciókezelést alkalmaznak az időpontok egyidejű lefoglalásának elkerülésére [16]. Az integrációiknál (pl. fizetés) idempotens webhookokat alkalmaznak.
*   **Turo:** A peer-to-peer autóbérlő platform [18] megoldása a kauciókra pontosan a fent említett **kártyaregisztrációs / pre-autorizációs modell**. A Turo a bérlés elején egy biztonsági "deposit" állapotot ellenőriz (Stripe/hasonló PSP segítségével), és a bérlés lezárásáig ("checkout") fenntartja a terhelés lehetőségét az esetleges károkra vagy a késedelmi díjakra.

### 8. Konkrét implementációs roadmap (3-sprint) a KGC-4 számára

**Sprint 1: Core Availability és Frontend Caching**
*   **Backend:** Portal-equipment API kibővítése. Napi 30 napos ablak legenerálása és optimalizálása.
*   **Frontend:** Next.js ISR implementálása a gép-katalógushoz és a naptárakhoz [1]. A `revalidate: 300` (5 perc) beállítása [19].
*   **Integráció:** Webhook elkészítése az ERP-ben, amely a bérlés állapotának változásakor (pl. `AVAILABLE` -> `RESERVED`) meghívja a Next.js `revalidatePath` függvényét az adott eszköz oldalára [2].

**Sprint 2: Checkout flow, Pre-reserve és Fizetés**
*   **Race Condition kezelés:** Redis alapú Redlock bevezetése a frontend / BFF (Backend For Frontend) rétegen. 15 perces TTL zárolás a kosárba tételkor [13].
*   **Fizetés:** SimplePay V2 integráció [5]. Az ALU tokenizációs folyamat (kártyaadatok elmentése fizetéskor) lefejlesztése, hogy a későbbi late fee vagy kaució (deposit `Retained`) érvényesíthető legyen [6].
*   **iCal:** Az RFC 5545 alapú `.ics` generáló végpont elkészítése [15], amit a sikeres fizetés után e-mailben megkap a bérlő.

**Sprint 3: ERP Atomicity és Late-fee folyamatok**
*   **Konverzió:** A `Booking` -> `Rental` átalakító logika védelme `SELECT FOR UPDATE` sorszintű zárolással a PostgreSQL-ben [7] és idempotencia kulcsok bevezetése.
*   **Late-fee:** Éjszakai Cron batch implementálása az `OVERDUE` státuszokhoz.
*   **Telephelyi POS:** A MyPOS kaució-flow STUB cseréje élő logika alapján; az "on-checkout-recalculate" algoritmus élesítése az ERP-ben, amely figyelembe veszi a tényleges visszahozatali időt és a SimplePay-nél tárolt tokent használja az esetleges pótdíjakra.

## Felhasznált források

- [Guides: ISR | Next.js](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration)
- [Guides: Caching (Previous Model) | Next.js](https://nextjs.org/docs/app/building-your-application/caching)
- [Guides: Caching (Previous Model) | Next.js](https://nextjs.org/docs/app/building-your-application/caching)
- [Fejlesztőknek - SimplePay](https://simplepay.hu/fejlesztoknek/)
- [PostgreSQL: Documentation: 18: 13.3. Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Catalog of Patterns of Distributed Systems](https://martinfowler.com/articles/patterns-of-distributed-systems/)
- [GROQ-powered webhooks | Sanity Docs](https://www.sanity.io/docs/webhooks)
- [Distributed Locks with Redis | Docs](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)
- [RFC 5545 - Internet Calendaring and Scheduling Core Object Specification (iCalendar)](https://datatracker.ietf.org/doc/html/rfc5545)
- [GitHub - calcom/cal.diy: Scheduling infrastructure for absolutely everyone. · GitHub](https://github.com/calcom/cal.com)
- [Turo car sharing marketplace | Rent the perfect car](https://www.turo.com/engineering)


---

## Q6 — Headless ERP-stack comparison

> **Kérdés:** A KGC-4 = egyedi NestJS+Prisma+BMAD. Long-term alternatívák: Twenty CRM, Odoo, ERPNext, Dolibarr, Pimcore. Mikor érdemes standardra váltani, mikor egyedi maradni.

### 1. Headless ERP-stack alternatívák összehasonlítása

Felhívom a figyelmet, hogy míg a Twenty CRM, az Odoo, az ERPNext, a Dolibarr és a Pimcore technológiai háttere és képességei szerepelnek a megadott forrásokban, az *Akeneo PIM* részletes specifikációja, valamint bizonyos hazai (NAV) sajátosságok árazása és integrációs mélysége a forrásokon kívüli, iparági tudáson alapszik.

| ERP/PIM Rendszer | Tech-stack | License | Community méret | Magyar lokalizáció (NAV, ÁFA) | Multi-tenant readiness | Rental-modul minősége | Learning-curve | Host-cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Twenty CRM** | TypeScript, React, NestJS, Postgres [1] | Open Source (MIT, "Salesforce alternatíva") [2] | 45.9k+ GitHub star [3] | Nincs natív (egyedi integráció kell) | Támogatott (Workspace-ekkel) | Nincs | Közepes (NestJS + TS egyezik a KGC-4-el) | Alacsony/Közepes |
| **Odoo 17/18** | Python, JavaScript (OWL) [4] | Open Source (Community) & Enterprise [5] | 50.7k+ GitHub star [6] | Partneri szinten erős (magyar cégek fejlesztik a NAV bekötést) | Erős | Out-of-box elérhető (Rental orders, pricing, reservations) [7-9] | Meredek (speciális keretrendszer) | Változó (felhasználó/hó) [10] |
| **ERPNext + Frappe**| Python, JavaScript (Vue), MariaDB [11, 12] | Open Source (GPL-3.0) [13, 14] | 34k+ GitHub star [15] | Közösségi (általában gyengébb, mint az Odoo) | Erős (Frappe cloud / multi-tenant) [16] | Közösségi kiegészítő | Közepesen meredek [17] | Alacsony (Self-hosted is [16]) |
| **Dolibarr** | PHP [18] | FOSS (GPL) [19, 20] | Nagy (millió+ felhasználó) [20] | Erős (Magyar közösség és fordítások) | Alapvető | Alapvető | Lapos (könnyű betanulás) [19] | Nagyon alacsony |
| **Pimcore** | PHP, Symfony, MySQL [21, 22] | Open Source (GPL) [21] | 3.8k+ GitHub star [23] | N/A (Mivel PIM/DAM, az ÁFA/NAV nem releváns számára) [24] | Támogatott | N/A | Nagyon meredek | Közepes / Magas |
| **Akeneo PIM** | *PHP, Symfony, MySQL (Forráson kívüli adat)* | *OSL v3 / Enterprise (Forráson kívüli)* | *Nagy PIM specifikus bázis* | *N/A (Csak termékadatok)* | *Basic/Közepes* | *N/A* | *Közepes* | *Magas (Enterprise)* |

---

### 2. Build vs Buy decision framework

Az egyedi rendszerek és a dobozos termékek közötti választás a mikroszolgáltatás és monolit architektúrák fejlődésével új értelmet nyert [25, 26].

**Mikor érdemes egyedi maradni (Build)?**
*   **Mély domain-szakértelem és egyedi folyamatok:** Ha a bérlési logika és a Zoli által fejlesztett egyedi agentic-workflow (BMAD) folyamat olyan üzleti értéket képvisel, amelyhez a standard szoftverek (pl. Odoo) merev struktúráját túl költséges lenne hozzáhajlítani. Az egyedi mikroszolgáltatások (vagy monolitok) pontosan a "business capabilities" köré szervezhetők [27].
*   **Erős lokális/regulációs nyomás:** A hazai piacon a Nemzeti Adó- és Vámhivatal (NAV) folyamatosan változó szabályozásai (pl. online számla, speciális adókulcsok és élethelyzetek [28, 29]) gyors reakcióidőt követelnek. Egy egyedi rendszerben nem kell megvárni a szállító (vendor) frissítését.
*   **Technológiai egyezés:** A KGC-4 a modern NestJS + Prisma stacket használja, amely TypeScript alapú [1, 30]. Ez egy gyors, agilis környezet, szemben mondjuk egy nehezebben bővíthető régebbi architektúrával.

**Mikor érdemes standardra váltani (Buy)?**
*   **"Single-dev-burnout" kockázata:** Egyetlen fejlesztőre hárul a 72 adatbázis modell és a 68 NestJS modul, valamint a teljes infrastruktúra karbantartása. A "you build, you run it" (te építed, te üzemelteted) elv működik [31], de ha egyedül van a fejlesztő, az üzemeltetési teher (infrastructure automation, frissítések, hibajavítások) felemésztheti az új funkciók fejlesztésére szánt időt [32, 33].
*   **A "Commodity" funkciók újraírása:** Olyan funkciók, mint az auth, számlázás alapjai, raktárkezelés, ma már "dobozos" formában is magas minőségűek (pl. az Odoo raktárkezelése [34]). Ha Zoli az ideje nagy részét ezek karbantartására fordítja a BMAD workflow helyett, a "feature velocity" drasztikusan be fog zuhanni.

---

### 3. Hybrid pattern: KGC-4 mint integration-orchestrator

Ez egy rendkívül modern és életképes stratégia. A Pimcore egy natívan "Open Core Data & Experience Management Platform", amely magában foglalja a PIM (Product Information Management), MDM, DAM (Digital Asset Management) és DXP/CMS rendszereket [21]. Strukturált adatok automatikus vagy manuális kezelésére, több kimeneti csatornára optimalizálva tervezték [24, 35].

**A modell működése és realitása:**
*   A cikk-, tartalom- és médiakatalógust teljes egészében átveszi a Pimcore (vagy az Akeneo). A Pimcore-ban eleve rendelkezésre állnak az olyan funkciók, mint a fájlok metaadatainak gazdagítása, több kimeneti formátum generálása és a verziókezelés [24, 36].
*   A KGC-4 megmarad mint az üzleti logika (bérlés, BMAD) orkesztrátora. A "smart endpoints and dumb pipes" elv alapján [37, 38] a KGC-4 hívásokat intéz a Pimcore felé, illetve eseményekre reagál.
*   **Példa a megvalósításra:** A két rendszer közötti szinkronizációhoz "Event-Carried State Transfer" mintát érdemes alkalmazni [39, 40]. Amikor a Pimcore-ban egy cikk leírása vagy ára megváltozik, a rendszer egy Webhook [41] segítségével értesíti a KGC-4-et. A KGC-4 (például egy NestJS Queue vagy BullMQ segítségével [42, 43]) aszinkron módon frissíti a saját belső, olvasásra optimalizált (read-model) gyorsítótárát, így nem kell minden egyes bérlési tranzakciónál lekérdeznie a Pimcore API-ját.

---

### 4. Migration-cost becslés (3-5 év múlva)

*(Ez a rész a megadott adatokra, forrás-architektúrákra és iparági tapasztalatokra támaszkodik, konkrét migrációs költség számszerűsítése nincs a forrásokban).*
Egy 72 Prisma-modellel és 68 modullal rendelkező (100+ commit/hónap) ERP migrációja egy dobozos rendszerbe hatalmas projekt.
1.  **Adatmigráció:** A meglévő adatbázisok exportja és átalakítása az új rendszer (pl. Odoo vagy ERPNext) sémájára heteket vehet igénybe. Bár az ERPNext kínál Data Import eszközöket [44], az adatszerkezetek (impedance mismatch) ritkán egyeznek pontosan [45].
2.  **Kód és üzleti logika (BMAD) újraírása:** A saját fejlesztésű "agentic workflow" rendszert egy standard keretrendszerben (mint a Frappe [11] vagy az Odoo Python moduljai [46]) teljesen az alapoktól újra kell implementálni.
3.  **Betanítás:** A felhasználók átállítása egy új felületre hónapokig tarthat, ami átmeneti termelékenység-csökkenéssel jár.
Összességében a 3-5 év múlva történő teljes átállás egy ekkora aktív kódbázisnál valószínűleg *6-12 hónapnyi dedikált mérnöki munkát* (és a BMAD elvesztését/kompromisszumát) jelentené.

---

### 5. HN/Reddit-thread insight-ok kisvállalkozói szemszögből

*Felhívom a figyelmet, hogy explicit HackerNews és Reddit ERP-fórum beszélgetések szövege nem szerepel a forrásokban. A források csak a HackerNews említését tartalmazzák technológiai kiadásoknál [47], így ez a szekció az általános IT iparági konszenzust tükrözi a kérdésben:*

A "Build vs. Buy" ERP kérdéskörben a fejlesztői közösségek (HN/Reddit) általában a következőket emelik ki:
*   **"ERP-t építeni a semmiből hatalmas tech-adósság":** Sokan óva intenek attól, hogy egy solo-dev egy teljes ERP-t fejlesszen, mert a perem-funkciók (számlázás, ÁFA, jogosultságkezelés) lekódolása izgalommentes, végtelenül aprólékos munka, ami gátolja a skálázódást.
*   **A testreszabás pokla (The customization hell):** Ugyanakkor a "Buy" oldalról a fejlesztők arról számolnak be, hogy egy Odoo vagy Salesforce testreszabása (customization) olyan szinten monolitikus és vendor-specifikus (pl. Odoo OWL, vagy Frappe XML/Python hibridek), ami miatt egy TypeScript/NodeJS fejlesztő sokkal lassabban dolgozik, mint a saját maga által, modern stacken (Next/Prisma) írt kódjában.
*   **"Ha az egyedi flow a terméked, tartsd meg":** Ha a cég értékét a bérlési rendszerük és a BMAD automatizációk adják, a konszenzus az, hogy azt a modult custom kódban kell tartani, a többit (pl. könyvelés) pedig API-n keresztül átadni külső szolgáltatónak.

---

### 6. Konkrét ajánlás a KGC-4 esetére (Előkészülés a jövőbeli váltásra)

A jelenlegi helyzetben (Zoli masszív sebességgel fejleszt, a rendszer stabil) **most nem érdemes váltani**. Azonban a 3-5 éves horizontra fel kell készíteni a rendszert egy esetleges leválasztásra vagy "Buy" alternatíva beemelésére. 

Ezt az alábbi konkrét építészeti lépésekkel tehetitek meg (EASIER switch):

1.  **API-ként kezelt infrastruktúra (APIs as infrastructure):**
    Követve a Stripe [48, 49] és más modern rendszerek példáját, a KGC-4 belső funkcióit is API határok mentén érdemes szétválasztani. Biztosítani kell a visszamenőleges kompatibilitást (backwards compatibility) és az API verziózását [50, 51]. Így ha később a számlázást át is veszi az Odoo, a frontend (vagy a BMAD) csak a verziózott API-t hívja, mögötte a szolgáltatás "kicserélhető".
2.  **Webhookok és eseményvezéreltség bevezetése:**
    Ahogy a Supabase [52, 53] vagy a Sanity GROQ-alapú webhookjai is teszik [54, 55], a KGC-4 Prisma modelljeihez (esetleg trigger szinten) érdemes webhook értesítő rendszert építeni. Ha minden lényeges entitás-változás (pl. bérlés létrejötte, cikk módosítása) szabványos eseményként (event) is publikálva lesz egy Message Broker-be (pl. Redis + BullMQ [42, 43]), akkor az új rendszerek (pl. Pimcore) könnyen rá tudnak csatlakozni anélkül, hogy a KGC-4 kódját túlzottan módosítani kellene.
3.  **Felelősségi körök szegregálása (CQRS és Event Sourcing lépések):**
    Az összetett üzleti logikát (pl. bérlési aggregátumok, BMAD orkesztráció) érdemes fokozatosan az *Event Sourcing* vagy *Command Query Responsibility Segregation (CQRS)* minták felé tolni [56-58]. Ez azt jelenti, hogy az adatbázis nem csak a jelenlegi állapotot tárolja, hanem az események sorozatát, ami hihetetlenül megkönnyíti a későbbi adatmigrációkat és az adatbiztonságot [45]. A NestJS natívan támogatja a CQRS mintát, a dokumentáció szerint erre külön modul is van [59, 60].
4.  **Commodity funkciók leválasztása (Identity & Auth):**
    A fejlesztői kapacitás kímélése érdekében az olyan funkciókat, amik nem jelentenek versenyelőnyt, érdemes elsőként "kiszervezni". Ha a KGC-4 saját autentikációval rendelkezik, fontoljátok meg a leváltását nyílt szabványú (OAuth 2.0 / OpenID Connect [61-63]) dobozos szoftverekre, mint a Keycloak [64, 65] vagy a könnyen integrálható Auth.js [66, 67]. Ez azonnal levesz egy terhet Zoli válláról, és egy jövőbeli hibrid ERP (pl. KGC-4 + Pimcore) esetén biztosítja az Egyszeri Bejelentkezést (SSO) az összes alrendszer között [68, 69].

## Felhasznált források

- [GitHub - twentyhq/twenty: The open alternative to Salesforce, designed for AI. · GitHub](https://github.com/twentyhq/twenty)
- [Odoo Documentation — Odoo 17.0 documentation](https://www.odoo.com/documentation/17.0/)
- [Open Source ERP and CRM | Odoo](https://www.odoo.com/)
- [GitHub - odoo/odoo: Odoo. Open Source Apps To Grow Your Business. · GitHub](https://github.com/odoo/odoo)
- [Rental — Odoo 17.0 documentation](https://www.odoo.com/documentation/17.0/applications/sales/rental.html)
- [GitHub - frappe/erpnext: Free and Open Source Enterprise Resource Planning (ERP) · GitHub](https://github.com/frappe/erpnext)
- [Introduction](https://frappeframework.com/docs)
- [Dolibarr Open Source ERP and CRM - Web suite for business](https://www.dolibarr.org/)
- [GitHub - pimcore/pimcore: Core Framework for the Open Core Data & Experience Management Platform (PIM, MDM, CDP, DAM, DXP/CMS & Digital Commerce) · GitHub](https://github.com/pimcore/pimcore)
- [Microservices](https://martinfowler.com/articles/microservices.html)
- [A keresett oldal nem található ! - Nemzeti Adó- és Vámhivatal](https://nav.gov.hu/ado/szamla_es_nyugta/online-szamla)
- [Authentication | NestJS - A progressive Node.js framework](https://docs.nestjs.com/security/authentication)
- [What do you mean by “Event-Driven”?](https://martinfowler.com/articles/201701-event-driven.html)
- [Webhook](https://shopify.dev/docs/api/admin-rest/2024-07/resources/webhook)
- [BullMQ](https://docs.bullmq.io/guide/concurrency)
- [Queues | BullMQ](https://docs.bullmq.io/guide/queues)
- [Introduction](https://docs.erpnext.com/)
- [Pattern: Event sourcing](https://microservices.io/patterns/data/event-sourcing.html)
- [Cloudflare is free of CAPTCHAs; Turnstile is free for everyone](https://blog.cloudflare.com/turnstile-ga/)
- [APIs as infrastructure: future-proofing Stripe with versioning](https://stripe.com/blog/api-versioning)
- [Database Webhooks | Supabase Docs](https://supabase.com/docs/guides/database/webhooks)
- [GROQ-powered webhooks | Sanity Docs](https://www.sanity.io/docs/webhooks)
- [Rate Limiting | NestJS - A progressive Node.js framework](https://docs.nestjs.com/security/rate-limiting)
- [Authentication - OWASP Cheat Sheet Series](https://owasp.org/www-project-cheat-sheets/cheatsheets/Authentication_Cheat_Sheet.html)
- [Final: OpenID Connect Core 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Auth.js | Getting Started](https://authjs.dev/getting-started)
- [JWT authentication: Best practices and when to use it - LogRocket Blog](https://blog.logrocket.com/jwt-authentication-best-practices/)
- [https://supertokens.com/blog/sso-vs-oauth-vs-oidc](https://supertokens.com/blog/sso-vs-oauth-vs-oidc)


---

## Q7 — SEO + structured data

> **Kérdés:** 119+ SEO-landing + 416-URL sitemap. Product schema.org JSON-LD. BreadcrumbList + ItemList. ISR cache-vs-freshness. Agentic-browsing (llms.txt).

**1. Structured data complete catalog**

A keresőmotorok és az AI agentek (Lighthouse Agentic Browsing) számára a megfelelő strukturált adatok elengedhetetlenek. A 2026-os szabványok alapján a **JSON-LD** formátum a javasolt a Microdata vagy RDFa helyett, mivel ezt a legkönnyebb implementálni, karbantartani, és a Google is ezt ajánlja [1, 2]. A JSON-LD egy `<script>` tagbe ágyazott JavaScript notáció, amely teljesen el van különítve a felhasználó által látható HTML-től [1].

*   `schema.org/Product`: A termékoldalakon kötelező. Tartalmaznia kell a `name`, `image`, `brand`, `sku` (vagy `gtin`) mezőket [3-5]. A termékajánlatot a `schema.org/Offer` objektumon keresztül kell megadni, amely tartalmazza a `price`, `priceCurrency`, `availability` (pl. `https://schema.org/InStock`) és `priceValidUntil` mezőket [6-8]. Ha ezek az adatok hiányosak, a Google Merchant Center hibát jelezhet [9].
*   `schema.org/AggregateRating`: Ha egy géphez több mint 5 PortalReview érkezik, ezt a sémát kell beágyazni a `Product` alá. Tartalmazza a `ratingValue` (átlagos értékelés) és `reviewCount` (értékelések száma) mezőket [10-12].
*   `schema.org/BreadcrumbList`: A kategória-hierarchia megjelenítéséhez (pl. Gépek > Kompresszorok > Építőipari). A `BreadcrumbList` legalább két `ListItem` elemet tartalmaz, ahol a `position` szám (1-től kezdve) határozza meg a sorrendet [13-15].
*   `schema.org/ItemList`: Kategóriaoldalakon a terméklisták jelölésére szolgál. Ez egy `ListItem` elemekből álló tömb, amely a listában szereplő konkrét `Product` URL-ekre hivatkozik [16, 17].
*   `schema.org/LocalBusiness`: A Kisgépcentrum fizikai lokációjának ("Érd"), nyitvatartásának és elérhetőségeinek megadására, ami a helyi kereséseknél ("bérgép Érd") kiemelt fontosságú.

**2. ISR cache-vs-freshness trade-off SEO-szempontból**

Az ERP-driven webshopoknál (ahol az ár vagy az elérhetőség gyorsan változhat) a cache frissessége kritikus. Ha az ISR `revalidate: 3600` (1 óra) értékre van állítva, a betöltés villámgyors lesz, de a Google Merchant Center komoly büntetést (ban) oszthat ki, ha a termék feedben lévő ár eltér a landing oldalon (a cache-ből) kiszolgált, strukturált adatban szereplő ártól [9]. Az átlagosan heti 2x feltérképező Googlebot ráadásul pont a "stale" verziót fogja látni. A `revalidate: 60` csökkenti ezt a kockázatot, de növeli a szerverterhelést.

*A legjobb stratégia 2026-ban:* **On-Demand ISR** (`revalidatePath` vagy `revalidateTag`). Alapértelmezetten a termékoldalak végtelen ideig cache-elhetők, de amint az ERP-ben (a `portal-equipment` API-n keresztül) árváltozás történik, egy webhook meghívja a Next.js frontendet, amely a `revalidateTag('product-123')` vagy `revalidatePath('/termekek/kompresszor')` paranccsal azonnal, célzottan frissíti az oldalt [18-21]. A Vercel CDN architektúrájában a cache törlése és újraépítése globálisan 300 ms alatt végbemegy [22].

**3. Agentic-browsing readiness (llms.txt 2026)**

A 2026-os új szabvány, az `/llms.txt` fájl célja, hogy az LLM-ek (Claude, ChatGPT, Perplexity) szűkös kontextusablakába a legértékesebb webshop-információk jussanak be, felesleges HTML, JS és CSS overhead nélkül [23, 24]. 

A webshopodhoz a következő struktúrát érdemes követni az `/llms.txt` fájlban:
*   **H1 fejléc**: A projekt neve (pl. `# Kisgépcentrum Bérlés`) [25].
*   **Blockquote összefoglaló**: A bolt legfontosabb leírása ("> Érdi gépkölcsönző, fókuszban a kompresszorok, építőipari gépek..."). Ez adja meg a fő kontextust [25].
*   **Szabad Markdown szekciók**: Bérlési feltételek (kaució, házhozszállítás), valamint API útmutató az ügynököknek (hogyan kereshetnek gépeket a `portal-equipment` végponton) [25].
*   **Fájllisták (H2)**: Markdown linkek a részletes leírásokhoz (pl. `[Kompresszor bérlési útmutató](https://.../kompresszor-utmutato.md): Részletes műszaki paraméterek`). Opcionális linkek megadása a kevésbé fontos adatokhoz, amit az LLM kihagyhat [25, 26].

A teljes, részletes szöveges leírásokat az `/llms-full.txt` tartalmazza, ha a modell mélyebb adatokat igényel [27]. Továbbá célszerű a CMS-ből érkező cikkeknek külön egy `.md` végződésű útvonalat biztosítani [28].

**4. Next.js 16 `generateMetadata` + `sitemap.ts` + `robots.ts` kódminta**

A dinamikus SEO metaadatokat szerveroldalon futó `generateMetadata` segítségével állítjuk elő, amely blokkolás nélkül optimalizálja az oldalt a botok számára [29]. A lenti minta figyelembe veszi a magyar nyelvű long-tail keywordöket is:

```typescript
// app/termekek/[slug]/page.tsx
import { Metadata } from 'next';

type Props = { params: { slug: string } };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  // Adat lekérése a portal-equipment API-ból. A fetch automatikusan memoizálva van. [30, 31]
  const product = await fetch(`https://api.kgc.hu/portal-equipment/${params.slug}`).then(res => res.json());

  return {
    title: `${product.name} bérlés Érd | Kisgépcentrum`, // SEO optimalizált [32]
    description: `Béreljen ${product.category} típusú gépet, mint a ${product.name}, azonnal vihető Érden. Napi bérleti díj: ${product.price} Ft.`, [33]
    openGraph: {
      title: `${product.name} - Gépkölcsönzés`,
      images: [{ url: product.imageUrl }], // LCP kép optimalizálva [34]
    },
    alternates: {
      canonical: `https://kgc.hu/termekek/${params.slug}`, [35]
    },
  };
}

export default async function ProductPage({ params }: Props) {
  // Renderelés...
}
```

A `robots.ts` és `sitemap.ts` esetében a Next.js fájl-alapú metadata API-ját (`app/sitemap.ts` és `app/robots.ts`) érdemes használni [36]. A sitemap-et a `portal-equipment` és a CMS végpontjaiból aszinkron módon tudod iterálni, beleértve a 416+ long-tail URL-t.

**5. Google Merchant Center feed**

A Merchant Center XML/CSV feed elengedhetetlen, de a Google a strukturált adatokkal kombinálva tekinti hitelesnek a termékeket [9, 37].
*   A feed generálását a `portal-equipment` API-ra kötött háttérfolyamattal érdemes végezni (pl. napi 1x vagy egy ERP event hatására).
*   A feed-ben szereplő árnak, devizának (`HUF`), készletinformációnak maradéktalanul egyeznie kell az oldalon található JSON-LD strukturált adatokkal. Az eltérés automatikus kizárást vonhat maga után [9].

**6. Core Web Vitals ERP-driven webshopon**

A Lighthouse szigorúan fogja mérni a következőket (mobilon és asztali nézetben egyaránt):
*   **LCP (Largest Contentful Paint)**: Bőven 2.5 másodperc alatt kell lennie [38]. A hős-kép (hero image) vagy a fő termékkép optimalizálásával és a `next/image` használatával (pl. `priority` flag hozzáadásával) gyorsíthatod. Az LCP méri a "Time to First Byte" (TTFB) késedelmet is, ezért a gyors ERP-szerver válaszidő kulcsfontosságú [38].
*   **INP (Interaction to Next Paint)**: A vizuális visszajelzések gyorsasága, aminek 200 ms alatt kell maradnia [39]. A kliens oldali API hívásoknál (pl. kosárba rakás vagy szűrés) a JavaScript főszál lefoglalását minimalizálni kell [39, 40].
*   **CLS (Cumulative Layout Shift)**: A tartalom ugrálását méri, melynek 0.1 alatt kell maradnia [41]. A késleltetve (kliens oldalon) betöltődő elemek (például dinamikus árak az ERP-ből) betöltése esetén adj meg fix helyet a UI-ban egy *Skeleton loader* segítségével [42, 43].

**7. Magyar piac specifika**

A magyar piacon a Google-keresések dominálnak. Bár a tartalom ("bérgép Érd", "kompresszor bérlés") magyar nyelvű, a sémák kulcsainak (*name*, *offers*, *availability*) maradniuk kell az angol Schema.org szabványnál [44]. Fontos:
*   A többnyelvű tartalmaknál BCP-47 nyelvi kódokat lehet használni (pl. `name#hu`), de a sima magyar weblapnál elég a hagyományos sémadefiníció [44]. 
*   A long-tail "bérgép" kulcsszavakat a breadcrumbokban (`schema.org/BreadcrumbList`) és a JSON-LD `description` paramétereiben érdemes minél természetesebben elhelyezni [45].

**8. Buktatók (Pitfalls)**

*   **Dupla OG-tag**: Sok esetben, ha CMS pluginokat (pl. Yoast) és custom keretrendszereket (Next.js App Router metadata API) együtt használsz, a head szekcióban kétszer jelenik meg a meta tag [46]. Tisztán a Next.js `generateMetadata`-ra bízd a generálást.
*   **Vercel ISR + Googlebot caching**: Ne felejtsd el, hogy a Vercel CDN per-deployment alapon tárolja a cache-t [22, 47]. Ha on-demand ISR revalidációt hívsz (`revalidatePath`), az globálisan érvényesül, de a botok még mindig láthatják a *stale* tartalmat, amíg az új háttérben meg nem épül (stale-while-revalidate modell) [48, 49]. 
*   **JSON-LD validation errors**: Olyan adatok is indexelésre (vagy legalább is validációs próbára) kerülhetnek, melyeket hiányosan táplálsz a JSON-LD-be. Mindig használd a Google Rich Results Test eszközét a publikálás előtt, mert ha a Google spamnek vagy hibásnak (pl. hiányzó `price` mező) minősíti a kódot, manuális büntetést (Manual Action) is kioszthat [50, 51]. Továbbá kerülni kell a láthatatlan elemek JSON-LD formátumú megadását; csak az szerepeljen ott, ami az oldalon vizuálisan is prezentálva van a bérlőknek [52].

## Felhasznált források

- [Intro to How Structured Data Markup Works | Google Search Central | Documentation | Google for Developers](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- [Offer - Schema.org Type](https://schema.org/Offer)
- [Product - Schema.org Type](https://schema.org/Product)
- [Intro to Product Structured Data on Google | Google Search Central | Documentation | Google for Developers](https://developers.google.com/search/docs/appearance/structured-data/product)
- [AggregateRating - Schema.org Type](https://schema.org/AggregateRating)
- [BreadcrumbList - Schema.org Type](https://schema.org/BreadcrumbList)
- [How To Add Breadcrumb (BreadcrumbList) Markup | Google Search Central | Documentation | Google for Developers](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)
- [ItemList - Schema.org Type](https://schema.org/ItemList)
- [Functions: revalidatePath | Next.js](https://nextjs.org/docs/app/api-reference/functions/revalidatePath)
- [Functions: revalidateTag | Next.js](https://nextjs.org/docs/app/api-reference/functions/revalidateTag)
- [Guides: ISR | Next.js](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration)
- [Incremental Static Regeneration (ISR)](https://vercel.com/docs/incremental-static-regeneration)
- [The /llms.txt file – llms-txt](https://llmstxt.org/)
- [Functions: generateMetadata | Next.js](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)
- [Getting Started: Metadata and OG images | Next.js](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)
- [Largest Contentful Paint (LCP) | Articles | web.dev](https://web.dev/articles/lcp)
- [Interaction to Next Paint (INP) | web.dev](https://web.dev/articles/inp)
- [Cumulative Layout Shift (CLS) | Articles | web.dev](https://web.dev/articles/cls)
- [Final: OpenID Connect Core 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [Ecommerce SEO: A Beginner's Guide](https://ahrefs.com/blog/ecommerce-seo/)


---

## Q7b — WordPress vs Next.js (opt-in)

> **Kérdés:** foxxi WP-Elementor-stack vs kgc-berles Next.js-stack. Mikor melyik győz egy ERP-driven publikus oldalon? Editorial-control non-tech embernek.

A Foxxi (WordPress + Elementor) és a KGC-4 (Next.js + NestJS ERP) közötti váltás technológiai és üzleti szempontból is egy komoly szintlépést jelent. Az ERP-vezérelt publikus oldalak esetében a hagyományos CMS-ek és a modern, headless (Jamstack) architektúrák teljesen eltérő koncepcióra épülnek.

Íme a részletes válasz a kérdéseidre, a források és az iparági tapasztalatok alapján:

### 1. Összehasonlító tábla: WordPress vs. Next.js

| Szempont | WordPress (hagyományos) | Next.js (Headless + Custom/API) |
| :--- | :--- | :--- |
| **Plugin-ökoszisztéma** | Hatalmas (WooCommerce, WPML, ACF). Gyors indulás, de magas a "plugin-ütközés" és a bloatware kockázata [1, 2]. | Teljes kontroll. Nincs kész plugin (pl. a fizetést egyedileg kell bekötni), de az integrációk stabilabbak és testreszabhatóbbak. |
| **Editorial UX (Non-tech)** | Elementor/Gutenberg: "What you see is what you get" (WYSIWYG), de hajlamos a kódot teleszemetelni. | Strukturált tartalomkezelés (Sanity, Payload). A Sanity Studio-val integrált Next.js Visual Editing segítségével valós idejű, "kattints-és-szerkessz" élményt adható az iframe-en keresztül [3, 4]. |
| **Hosting & Cost** | Hagyományos megosztott tárhely vagy VPS. Általában olcsó, de skálázódásnál (forgalmi tüskék) drága és lassú lehet. | Vercel, Netlify vagy önálló Docker/Node.js host. A Vercel CDN alapú gyorsítótárazása és az ISR (Incremental Static Regeneration) rendkívül gyors skálázódást biztosít [5, 6]. |
| **Teljesítmény (LCP/INP)** | Általában gyengébb, a sok plugin rontja az optimalizációt. *(A jó LCP < 2,5 mp [7], a jó INP < 200 ms [8]).* | Kiváló teljesítmény az ISR és az Edge caching miatt. A Next.js natívan optimalizálja ezen Core Web Vitals metrikákat [5]. |
| **Biztonság** | Magas kockázat a harmadik féltől származó elavult pluginok miatt. Folyamatos frissítést igényel [1]. | Nagyon biztonságos. A frontend el van választva a backendtől, így kisebb a támadási felület. |

### 2. Headless WordPress + Next.js (WPGraphQL) — Mikor győz a hibrid stack?
A WordPress natív REST API-val és a WPGraphQL kiegészítővel headless CMS-ként is használható [2, 9, 10]. Ez a hibrid megoldás (ahol a backend a WP, a frontend pedig Next.js) akkor győz, ha:
*   **Az ügyfél ragaszkodik a megszokott WordPress adminhoz** (mert a tartalomgyártóik már ismerik, és nem akarnak új rendszert betanulni) [10].
*   A projektnek mégis szüksége van a Next.js által nyújtott **drasztikusan jobb teljesítményre** és biztonságra (egy headless WP architektúra akár 10-szer gyorsabb oldalbetöltést is eredményezhet a hagyományoshoz képest) [11].
*   Több csatornán (web, mobilapp) kell ugyanazt a tartalmat megjeleníteni [12, 13].

### 3. TCO (Teljes Birtoklási Költség) 3-év becslés
*(Megjegyzés: A pontos pénzügyi becslések iparági sztenderdeken alapulnak, amelyek a forrásokban nem szerepelnek közvetlenül, de a technológiák fenntartási logikáját a források is alátámasztják).*
*   **WP + Elementor + Woo (Foxxi-vonal):** A kezdeti fejlesztési költség alacsonyabb, mivel mindenre van dobozos plugin (pl. Stripe, SimplePay). Azonban a 3 éves TCO meredeken nőhet a **karbantartás** (kötelező heti/havi plugin frissítések a biztonsági rések miatt), a sérülékenység-kezelés és az esetleges teljesítmény-optimalizálási utómunkák miatt.
*   **Next.js + Sanity/Payload + Vercel (KGC-4 vonal):** A kezdeti fejlesztés időigényesebb és drágább. A fizetési kapukat (mint a Barion [14] vagy a SimplePay [15]) az API-jukon keresztül, egyedileg (pl. a NestJS backendben) kell implementálni. A 3 éves TCO viszont kiegyenlítődik vagy alacsonyabbá válik, mert a **karbantartási igény minimális**, a rendszer nem "omlik össze" egy plugin frissítéstől, és a szerverköltségek (pl. Vercel) a forgalomhoz jobban és gazdaságosabban igazodnak [16].

### 4. Magyar piaci adatok (WP vs. Jamstack)
Világszinten a WordPress a weboldalak több mint 43%-át hajtja meg [1]. *(Szerkesztői kiegészítés: a magyar KKV-szegmensben a becslések szerint a WP részesedése eléri a 60-70%-ot is, mivel ez a legkönnyebben elérhető belépő szintű megoldás).*
A Jamstack (amelybe a Next.js is beletartozik) trendje rohamosan nő, de főként az **enterprise, az e-kereskedelmi és a tech-tudatos (ERP-vezérelt) szegmensben**. A modern fejlesztői piacon egyre inkább a "Content as a Service" (CaaS) megközelítés az elvárás, ahol a CMS (pl. Strapi, Sanity) csak egy API végpont, ahogy ezt a KGC-4 projekt is megkívánja [12, 17].

### 5. Konkrét ajánlás a KGC-4 esetére (Validáció)
A választás a **Next.js + NestJS ERP** mellett tökéletes döntés volt a KGC-4 számára, a következő okok miatt:
1.  **Mély ERP integráció:** A NestJS (backend) és a Prisma eleve egy robusztus REST API-t szolgáltat a publikus oldal felé. A Next.js natívan arra lett kitalálva, hogy külső API-kból (mint a ti ERP-tek) húzza be az adatokat (pl. `fetch` hívásokkal, amelyeket akár Cache-elhet is az ISR segítségével) [5, 18].
2.  **Architekturális illeszkedés:** Ha WordPresst használtatok volna, a WP-nek egyedi PHP kódokon keresztül kellett volna kommunikálnia a NestJS ERP-vel, ami egy felesleges és lassú technológiai "híd" lett volna két teljesen más nyelvű és logikájú rendszer között. A Next.js (TypeScript) és a NestJS (TypeScript) viszont egységes full-stack JavaScript/TypeScript ökoszisztémát alkot.
3.  **Tökéletes teljesítmény:** Mivel a publikus weboldal valószínűleg a bérleti gépeket, árakat fogja listázni az ERP-ből, a Next.js segítségével ezeket részben statikusan elő lehet generálni, részben API-ról dinamikusan frissíteni, kompromisszummentes LCP és INP élményt adva [5].

## Felhasznált források

- [About – WordPress.org](https://wordpress.org/about/)
- [Headless CMS - Top Content Management Systems | Jamstack](https://jamstack.org/headless-cms/)
- [Visual Editing with Next.js Pages Router and Sanity Studio | Sanity.io guide](https://www.sanity.io/guides/nextjs-live-preview)
- [Guides: ISR | Next.js](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration)
- [Vercel](https://vercel.com/blog/nextjs-app-router-on-demand-isr)
- [Largest Contentful Paint (LCP) | Articles | web.dev](https://web.dev/articles/lcp)
- [Interaction to Next Paint (INP) | web.dev](https://web.dev/articles/inp)
- [Headless WordPress Hosting | WP Engine®](https://wpengine.com/resources/headless-wordpress/)
- [https://www.wpgraphql.com/](https://www.wpgraphql.com/)
- [Strapi, the leading open-source headless CMS](https://strapi.io/blog/build-a-website-with-strapi-5-and-nextjs)
- [Strapi, the leading open-source headless CMS](https://strapi.io/blog/strapi-5-released)
- [Blog Article](https://www.barion.com/hu/blog/kartyas-fizetes-online-aruhazba)
- [Fejlesztőknek - SimplePay](https://simplepay.hu/fejlesztoknek/)
- [Functions: generateMetadata | Next.js](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)

---

## Kapcsolódó

- [[2026-05-18 KGC-4 frontend integráció — NotebookLM research-terv]] — research-terv (bemenő)
- [[2026-05-18 KGC-4 ERP v7.0 mélyaudit]] — KGC-4 input-audit
- [[2026-05-18 KGC-4 integráció — architektúra v1]] — szintézis-dokumentum
- [[02-Projects/kgc-erp]] — projekt-fájl
- [[02-Projects/kgc-berles]] — Next.js front-projekt
- [[07-Decisions/2026-05-18 ADR — CMS-választás (KGC-4 integráció)]]
- [[07-Decisions/2026-05-18 ADR — SSO-bridge stratégia (KGC-4 → kgc-berles)]]
- [[07-Decisions/2026-05-18 ADR — Sync-pattern (webhook vs CDC vs poll)]]
- [[07-Decisions/2026-05-18 ADR — Deposit-PSP (Stripe vs Barion vs SimplePay)]]
- [[07-Decisions/2026-05-18 ADR — Tenant-resolution publikus API-n]]
- [[07-Decisions/2026-05-18 ADR — Article modul ERP-ben vagy CMS-ben]]
- [[07-Decisions/2026-05-18 ADR — Next.js BFF vs direkt API-call]]
- [[07-Decisions/2026-05-18 ADR — Agentic-browsing readiness (llms.txt)]]
