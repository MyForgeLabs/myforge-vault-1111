---
name: HelloPack — WordPress prémium plugin- és fordítás-suite
type: wiki
tags: ["#type/reference", "wordpress", "plugin-license", "tech-stack"]
created: 2026-05-08
updated: 2026-05-08
related:
  - "[[03-Hosts/Shared Hosting (Cloud Professional)]]"
  - "[[02-Projects/foxxi]]"
  - "[[02-Projects/rojtesbojt]]"
keyword: "#hellopack"
---

# HelloPack — WordPress prémium plugin-suite

> Evergreen referencia. Future-Peti és future-Claude/Codex/Gemini ezt a fájlt olvassa, ha új WP-projekt indul és el kell dönteni: melyik prémium plugin-t aktiválni a HelloPack-en keresztül, milyen fordítás-csomagot beszerezni, melyik domain-en aktiválni a license-t.

## Mi a HelloPack

A **HelloWP.io** (`hellowp.io`) egy magyar plugin-aggregator-szolgáltatás, amely **éves subscription-ben** ad **több száz prémium WordPress plugin-hez frissítési + Pro-feature-jogosultságot**. A vásárlás-modell: licensz-userId-hez kötött Bearer token, amit egy `HelloPack-Client` plugin csatol minden site-on. A HelloPack:

- **Pro-update-injection**-t végez (a wordpress.org-on free verzió települ, de a háttérben a Pro-binárisokat HelloPack injektálja a license-hez)
- API-szervere `api.hellowp.io`-n él, ahol a plugin-katalógus + download URL-ek + license-validitás kérdezhető
- Külön (ingyenes, public) GitHub-repó-t üzemeltet a **profi plugin-fordításokra** (`hellowpio/wordpress-translations`)

## License-info (Peti subscription)

> ⚠️ A konkrét token soha NEM kerül vault-ba — csak a magas-szintű info, amit Future-Peti tud.

- **userId:** `420042`
- **License-típus:** Regular License
- **Scopes:** `default`, `purchase:download`, `purchase:list`
- **Token-érvényesség (TTL):** ~10 év (315 360 000 sec)
- **Subscription supported until:** 2027-05-07 (utána renewal kötelező, vagy a Pro-update-injection elveszik és a plugin-ek free-tier-re visszaesnek)
- **Token tárolási hely:** WP option `hellopack_client.token` (NE git-be, NE public-doc-ba!)

A subscription a userId-hez kötődik, de **license-aktiválás per-domain történik** a HelloConsole-on (`https://hellowp.io/hu/helloconsole/hellopack-kozpont/` → API Creator → domain hozzáadás). Egy userId-en több domain (egyenként) regisztrálható — a `wordpress-plugins` endpoint **492 plugin-t** ad ki aktivált domain-en (ez a teljes katalógus, nem a régebbi „11 plugin"-cache, ami login előtt látszik).

## A 3 réteg, amit ad

A HelloPack három különálló-rétegű funkcionalitást hoz, mindegyik más cost-implikáció-val:

### Réteg 1 — Pro-update-jogosultság (492 plugin)

A `wordpress-plugins` endpoint listáz minden plugin-t, amihez **frissítési + Pro-feature-jogosultság** tartozik az aktuális subscription-en. Ezekhez a HelloPack-Client a wp-cron-on belül **Pro-binárisokat injektál** az update-flow-ba (a wordpress.org-on free települ, a Pro-feature-ek a HelloPack-injection után élnek).

**Cost-impact:** ~2 500 USD/év license-megtakarítás single-projekt-en (lásd [[#Cost-impact (project-szintű)]]).

### Réteg 2 — Modul-támogatás (81 modul a HelloPack-Client-ben)

A `wp-content/plugins/hellopack-client/modules/` mappa **81 PHP-fájlt** tartalmaz. Mindegyik egy konkrét prémium plugin-hez **license-injection + Pro-update-flow-t** definiál (pl. Elementor Pro-license-mező auto-fillelés, Gravity Forms-license auto-aktiválás, ACF-Pro-license auto-set).

A 81 modul a 492 plugin egy **hand-curated szelete** — a leggyakrabban használt prémium plugin-ekhez konkrét beépített injection-logika él. A többi 411 plugin csak download + update-flow-ra kap injection-t.

### Réteg 3 — Fordítás-modul (395 plugin × 23 nyelv, GitHub-public, INGYEN)

> 🔥 **KEY FINDING:** ez a réteg INGYEN elérhető, **nem** kell HelloPack-subscription, csak a public GitHub-repo!

**Forrás:** `https://github.com/hellowpio/wordpress-translations` (auth NEM kell, public repo)
**Tartalom:** **395 plugin** profi fordítása **23 locale-ban** (formal + informal verzió-ban):

```text
bg_BG · ca · cs_CZ · da_DK · de_DE · en_US · es_ES · fi · fr_BE · fr_FR ·
hu_HU · it_IT · nb_NO · nl_NL · pl_PL · pt_PT · ro_RO · ru_RU · sk_SK ·
sr_RS · sv_SE · tr_TR · uk
```

⚠️ **ZH_CN (kínai) NINCS a HelloPack-fordításokban** — Kína-target multilingual site-on a ZH-fordításokat máshonnan kell beszerezni (vagy nélkülözni).

**Telepítési flow** (HelloPack-Client Translate-modul):

1. `Comparator::compare_all()` — összeveti az installed plugin-eket a GitHub-fa-val
2. `FileInstaller::install($slug, $type)` — letölti és menti a `.json` + `.mo` fordítás-fájlokat a `wp-content/languages/plugins/` mappába
3. WordPress automatikusan használja a `.json` (Performance Translation API) + `.mo` fájlokat

## A 492 plugin kategorizálva (project-relevance + use-case)

Csak a **gyakran-használt, project-relevante** kategóriák vannak itt — a teljes 492 lista a forrás-doksi-ban. A „⭐ Default-pick" oszlop azt jelzi, hogy **új WP-projekt-en** melyik a leggyakoribb-választás.

### Page Builder

| Plugin | ⭐ Default-pick | Megjegyzés |
|---|---|---|
| **Elementor Pro** | ⭐ általános | Legtöbb projekt-en stabil-default. Pro-feature-ek (Theme Builder, Form, Popup, Pro-only-Repeater, Custom Code, Role Manager) ingyen. |
| **Bricks Builder** | ⭐ perf-priorty | Modern, performant builder (Lighthouse ~95+). Migration-cost magas, de új-projekt-en érdemes-megfontolni. |
| **Bricks-extras** | – | Bricks-widget-bővítmények |
| **BricksForge** | – | Bricks-stack-bővítmény (form, animation, popup) |
| **Oxygen + OxyExtras** | – | Régebbi „builder-perf" alternatíva. Erősen-fejlesztői. |
| **Divi Builder + 12 ext** | – | Divi-stack (Divi Carousel, Contact, Dynamic, Passwords, Responsive, Search, Social, Tabs, Taxonomy, Timer, Tools Pro, Supreme Modules Pro). Csak Divi-projekt-en. |
| **GenerateBlocks Pro** | – | GeneratePress-theme-mate, Gutenberg-builder |
| **GP Premium** | – | GeneratePress-theme Pro-feature-ek |
| **JS Composer (Visual Composer)** | – | Legacy, Elementor leváltotta |
| **WP Grid Builder** | – | Komplex faceted grid-builder |

**Builder-választás-decision-tree:**

1. Új-projekt, no-existing-content, perf-priority → **Bricks Builder**
2. Meglévő Elementor-content, klasszikus stack → **Elementor Pro + Crocoblock** (ha bonyolult-CPT-stack kell)
3. Gutenberg-natív-only, lightweight → **GenerateBlocks Pro + GP Premium**
4. Divi-legacy-projekt → **Divi + 12 extension**

### Elementor addons (ha Elementor a builder)

- **Dynamic Content for Elementor** — conditional-display, dynamic-tag-ek
- **The Plus Addons for Elementor** — 100+ extra widget
- **Ultimate Elementor** — Brainstorm Pro Elementor + 100+ pre-designed widgets
- **Crocoblock (JetEngine + JetElements + JetSmartFilters + JetMenu + JetBlog + JetReviews)** — comprehensive Elementor-superset, CPT-builder + advanced-filtering + dynamic-content. **Egy szuperplugin sokat ad** — Brand-fázis-mockup-implementációhoz erős.

### WooCommerce ecosystem

**Conversion + Funnel (Tier 1 default-pick boutique-shop-ra):**

- **CartFlows Pro** — funnel-templatek (order-bump, upsell, custom checkout) — ~239 USD/év list-price
- **CheckoutWC** — Stripe/Pay-style modern WC checkout — turisták-mobilra
- **Order Bump for WooCommerce** — checkout-bump-csomag
- **Bought Together for WooCommerce** — cross-sell, „vendégek ezt is megnézték"
- **Free Gifts for WooCommerce** — promóciós ajándék-csomag („N Ft fölött ajándék")

**Marketing automation:**

- **AutomateWoo** — cart-abandon, win-back, replenishment, follow-up emails
- **AI Product Recommendations for WooCommerce** — 50+ termék-volumen-felett értelmes

**Pricing + Discount:**

- **Discount Rules PRO 2.0** — bulk-discount + tier-pricing
- **Booster Elite for WooCommerce** — comprehensive WC enhancement (currency, EU-VAT, számla-PDF, ár-kezelés)

**Product customization + Custom fields:**

- **WooCommerce Product Add-Ons Ultimate** — custom-field-ok a termékre („ajándékkártya-szöveg" mező)
- **Product Extras for WooCommerce** — alternatív custom-field megoldás

**Email + Order:**

- **YayMail Pro - WooCommerce Email Customizer** — modern HTML order-email design
- **WooCommerce PDF Invoices & Packing Slips Premium** — számla-PDF + szállítólevél

**YITH suite (~30+ plugin)** — kis SKU-volumen-en overkill, 50+ termék-tó-l értelmes:

- YITH Ajax Product Filter
- YITH Infinite Scrolling
- YITH Wishlist
- YITH Compare
- YITH Quick View
- YITH Frequently Bought Together
- YITH WooCommerce Wishlist Premium
- YITH WooCommerce Subscription
- YITH WooCommerce Stripe Premium
- YITH Product Bundles
- YITH Product Add-Ons & Extra Options
- YITH Booking and Appointment for WooCommerce

### Booking + Calendar

| Plugin | Mikor választ |
|---|---|
| **Amelia** | Default, simple-booking elég. 6-nyelv-támogatás. |
| **Fluent Booking Pro** | Ha email-marketing-ot is FluentCRM-en csináljuk |
| **Jet Appointments Booking** | Ha Crocoblock-stack-et viszünk |
| **JetBooking** | Vacation-rental-tipus (több-helyszín) |
| **WP Booking System Premium + 20 add-on** (Authorize.Net, GoPay, Mollie, Pricelabs, Redsys, Square stb.) | Overkill — csak komoly multi-payment-foglalás |
| **WooCommerce Appointments** | Ha foglalást a WC-checkout-ba akarjuk integrálni |

### Form

**Gravity Forms ecosystem (60+ add-on):**

A komplett Gravity-stack 6 tipikus VIP-űrlap-funkcióhoz:

- **Gravity Forms** (mag) — multi-step űrlap, conditional-logic, anti-spam
- **Payment:** Stripe Add-On, PayPal Standard, Square, Authorize.Net
- **CRM-feed:** ActiveCampaign, Mailchimp, MailerLite, HubSpot, Zoho
- **Anti-spam:** Akismet Add-On, reCAPTCHA Add-On, hCaptcha
- **Advanced UX:** Signature Add-On (e-aláírás), User Registration, Polls, Quiz, Survey
- **Compliance:** GDPR-consent, conditional-emails, multi-step
- **Gravity SMTP** — email-deliverability natívan

**Fluent Forms ecosystem (Gravity-light alternatíva):**

- **Fluent Forms Pro Add On Pack** — pro-feature-set
- **FluentForm Signature** — e-aláírás
- **Gravity-helyett-választás:** ha email-marketing-ot is FluentCRM-en csináljuk (tight integration)

**Egyéb:**

- **Ninja Forms** — legacy, Gravity-alternatíva (kerülni érdemes új-projekt-en)

### Email + CRM

- **FluentCRM Pro (`fluentcampaign-pro`)** — newsletter-list, customer-segment, automation, cart-abandon-flow
- **MailPoet** — alternatíva FluentCRM-hez

### Performance + Image

- **Perfmatters** — granuláris perf-tweak: per-page Elementor-CSS-disable, lazy-load fine-tune, JS-defer-rules. **WP Rocket complement.**
- **WP Rocket** — page-cache + minify
- **Imagify** — kép-optimalizálás (ShortPixel alternatíva)
- **ShortPixel** — kép-optimalizálás

### Analytics + Pixel

- **Analytify Pro** — GA4 dashboard a WP-admin-on belül (laikus-friendly)
- **PixelYourSite Pro** — FB/Google/TikTok/Pinterest pixel — launch-ROI-mérés

### SEO

- **Yoast SEO Premium** + **News SEO** + **Video SEO** + **Local SEO** + **WooCommerce SEO** — komplett Yoast-Pro-suite. AI-LLM-optimization-ra (lásd [[wp-yoast-llms-txt-customization]]) is használható.
- **SEOPress Pro** — Yoast alternatíva, lighter, no-upsell

**Yoast Pro-feature-ek HelloPack-on:**

- Internal Linking Suggestions
- Redirect Manager
- 4-keyphrase-elemzés (free csak 1)
- Schema-markup-bővítések (FAQ, How-to, Product)
- Social-preview (FB, Twitter)
- Workout (cornerstone-content, orphan-content)
- WooCommerce-product-schema

### GDPR + Compliance

- **Complianz Privacy Suite (GDPR/CCPA) Premium** — EU-kötelező multi-nyelvű cookie-banner + auto-DSAR + GDPR-form. **Pre-launch kötelező EU-target site-on.**
- **LW Cookie** — light-weight alternatíva

### Translation

- **TranslatePress Business** — frontend-string-fordítás (page-content, menü, post-content)
- **Polylang Pro + Polylang for WooCommerce** — TranslatePress alternatíva, lighter
- **WPML + 14 add-on** (String Translation, Media Translation, Translation Management, SEO, ACF Multilingual, Gravity Forms Multilingual stb.) — robusztus, heavier

### Affiliate

- **AffiliateWP + 24 add-on** (REST API, Recurring Referrals, Tiered Commissions, Direct Link Tracking, Lifetime Commissions, Pushover Notifications stb.) — komplett affiliate program

### Membership + LMS

- **LearnDash + 18 add-on** (Stripe Integration, PayPal Integration, Notes, Notifications, ProPanel, Gradebook, Course Grid, Certificates Builder, Group Registration, Achievements, Question Types, Course Migrator stb.) — LMS, e-learning
- **MemberDash** — membership site, content-restriction, recurring-payment
- **Tutor Pro + Tutor Stripe** — LMS alternatíva (modern, Gutenberg-friendly)
- **Restrict Content Pro** — paywall / member-only-content

### Backup + Migration

- **UpdraftPlus** — backup + restore + migration
- **All-in-One WP Migration + Unlimited Extension + Dropbox/GDrive/OneDrive Extension** — site-méret-limit feloldó + cloud-backup destination. **Staging→live migration-flow-ra kötelező.**

### Security

- **Solid Security Pro** (régen iThemes Security Pro) — bruteforce-protect, 2FA, file-change-detection

### Custom Fields

- **ACF Pro** — Advanced Custom Fields Pro
- **ACF Multilingual (ACFML)** — ACF-Pro + WPML kombináció
- **Meta Box** — ACF alternatíva

## Translation-rendszer (kritikus a multilingual projekteknek!)

> Ha a projekt 2+ nyelvű, ez a réteg **erősen-megnövelt-érték** — Pro-fordítás-minőség 23 nyelven, ingyen.

A `hellowpio/wordpress-translations` GitHub-repo **public** — semmilyen subscription / token nem kell. A HelloPack-Client `Comparator + FileInstaller` modulja automatikusan letölti.

**Telepítési protokoll, új plugin install után:**

```bash
# WP-CLI
wp eval '
  HelloPack\Client\Translate\Comparator::clear_cache();
  $r = HelloPack\Client\Translate\Comparator::compare_all();
  $i = new HelloPack\Client\Translate\FileInstaller();
  foreach ($r as $item) {
    if ($item->status !== "up_to_date") {
      $i->install($item->slug, $item->type);
    }
  }
'

# Vagy WP-admin: HelloPack → Translations tab → "Update all" gomb
```

**Fallback wordpress.org-fordításokra** (HelloPack-en NEM-szereplő plugin-ekre):

```bash
wp language plugin install <plugin-slug> hu_HU
```

**TranslatePress vs HelloPack-translations** — **két különböző réteg, mindkettő kell** multilingual-site-hoz:

- **TranslatePress** = frontend-string-fordítás (page-szövegek, menü, post-content) — `wp_trp_dictionary_*` táblákban
- **HelloPack-translations** = plugin-admin + UI-string fordítás — `.mo`/`.json` fájlokban

**GitHub-tree cache TTL:** 12 óra (43 200 sec) a Comparator-cache-ben. Ha gyorsan kell új fordítás: `Comparator::clear_cache()` előtte.

## Workflow használat

### Új WP-projekt indítása

1. **WP setup** (Hostinger / másholiges) — wp_options-konfig kész
2. **HelloPack-Client install + activate**:
   ```bash
   wp plugin install hellopack-client --activate
   # Vagy: WP-admin → Plugins → Add New → search "HelloPack"
   ```
3. **License aktiválás:** `https://hellowp.io/hu/helloconsole/hellopack-kozpont/` → **API Creator** → új domain hozzáadás → token másolás
4. **Token beállítás:** WP-admin → HelloPack → Settings → API token mező → Save
5. **License verify:**
   ```bash
   curl -s "https://api.hellowp.io/v1/hp-content/apicheck/" \
     -H "Authorization: Bearer <token>" \
     -H "User-Agent: <site-url>"
   # Várt válasz: {"status": "active", "userId": ..., "supported_until": "..."}
   ```
6. **Tier-1 plugin-batch install** (lásd alább)

### Plugin install Pro-version

**Két út:**

**A) WP-CLI** (ajánlott batch-installhoz):
```bash
wp plugin install <slug-1> <slug-2> <slug-3> --activate
```
A wordpress.org-on free verzió települ; a HelloPack-Client a következő wp-cron-tickenkor (vagy `wp cron event run hellopack_check_updates`) Pro-frissítést injektál. Ha a Pro-szöveg azonnal kell, force-frissítés:
```bash
wp eval 'do_action("hellopack_fetch_schema");'
delete_site_transient hellopack_available_plugins
wp plugin update --all
```

**B) WP-admin HelloPack tab UI:**
WP-admin → HelloPack → Plugins → search → Install → Activate. UI-n közvetlenül a Pro-binárist tölti.

**Gotcha:** néhány plugin (Crocoblock, Bricks, egyes Divi-extension) **csak közvetlen Pro-csak-bináris-formátumban** elérhető — a WP-admin-UI-n kell kezdeményezni, mert a wordpress.org-on nincs free fallback.

### Translation install for installed plugins

Lásd [[#Translation-rendszer (kritikus a multilingual projekteknek!)]] feljebb.

### Domain-bound license

> ⚠️ **FONTOS:** a license **domain-re kötődik**, nem userId-re. Staging↔live váltáskor figyelni:

- **Staging-domain** hozzáadása a HelloConsole-on **külön** (pl. `staging.example.com`)
- **Production-domain** **külön** hozzáadás (pl. `example.com`)
- **Different-language-domain** szintén külön (pl. `example.de`, `example.fr`) — ha külön domain-en él
- **Migration során** (staging→live): a régi domain license-t **release** kell, az új domain license-t **re-add**
- **Subdomain-migration** (lásd [[hostinger-updraftplus-staging-migration]]): `staging.example.com` → `example.com` migrációkor a HelloConsole-on át kell állítani

A HelloConsole-on a "Domains" tab listázza az összes aktivált domain-t a userId alatt. Egy userId-en **N domain regisztrálható** (subscription-tier-függő, jellemzően 5-10 domain).

### API endpoint-ek (debugging)

| Endpoint | Funkció |
|---|---|
| `https://api.hellowp.io/v1/hp-content/apicheck/` | License-validitás check |
| `https://api.hellowp.io/v1/hp-content/wordpress-plugins` | Vásárolt plugin-lista (a 492) |
| `https://api.hellowp.io/v1/hp-content/wordpress-themes` | Vásárolt theme-lista |
| `https://api.hellowp.io/v1/hp-content/download` | Plugin-download URL |

**Auth-headers:**
```
Authorization: Bearer <token>
User-Agent: <site-url>
```

**Token forrás:** WP option `hellopack_client.token`:
```bash
wp option get hellopack_client --format=json | jq .token
```

## Cost-impact (project-szintű)

Tipikus **single-WP-projekt-en** mit takarít meg a HelloPack (publikus list-price-ok 2026-ban):

| Plugin | List-price (USD/év) |
|---|---|
| Elementor Pro | ~99 |
| Yoast SEO Premium | ~99 |
| WP Rocket | ~59 |
| ACF Pro | ~50 |
| CartFlows Pro | ~239 |
| Gravity Forms Elite | ~259 |
| Complianz Premium | ~129 |
| Perfmatters | ~25 |
| PixelYourSite Pro | ~99 |
| ShortPixel/Imagify | ~120 |
| Bricks Pro | ~80 |
| Crocoblock All-Inclusive | ~140 |
| WPML Multilingual Agency | ~199 |
| AffiliateWP All Access | ~299 |
| AutomateWoo | ~99 |
| CheckoutWC | ~149 |
| Solid Security Pro | ~99 |
| UpdraftPlus Premium | ~70 |
| Amelia | ~119 |
| **Részösszeg (top 19)** | **~2 430 USD/év** |

**Total HelloPack-ROI:** ~2 500 USD/év hard-cost-saving **single-projekt-en** + multi-projekt-en multiplikálódik (license-domain-bound, de 1 userId-en N domain feloldható HelloConsole-on, így **5 site-on ~12 000 USD/év**).

**Plus** kvalitatív multilingual-quality boost (Pro-fordítás 23 nyelven INGYEN) + Pro-plugin-flexibilitás (Bricks/Oxygen/Bricks-extras alternatívák, ha Elementor-perf gyenge).

## Risk-ek + caveats

- **License domain-bound:** új domain-en MUST aktiválni külön. Staging↔live váltáskor ne felejtsd! Migration-flow-ban release-then-readd.
- **Subscription-renewal-cost:** éves díj (USD), ha lejár a Pro-update-injection elveszik, plugin-ek free-tier-re visszaesnek (Pro-feature-ek lockout). Renewal-dátumot dokumentálni a project-md-ben.
- **Cache-stale `hellopack_available_plugins`:** option 1-5 év stale lehet (volt példa: 2022-06-10-ről maradt fenn 2026-ban a „11 plugin"-cache, holott 492 elérhető). Force-refresh:
  ```bash
  wp option delete hellopack_available_plugins
  wp transient delete hellopack_available_plugins --all
  wp eval 'do_action("hellopack_fetch_schema");'
  ```
- **API token security:** a token a `hellopack_client` opcióban tárolódik. **NE** kerüljön git-be (lásd [[../05-Memory/feedback_git_sensitive_data]]) és NE jelenjen meg public-doc-ban.
- **ZH (kínai) translation hiány:** `hellowpio/wordpress-translations` 23 nyelv, **ZH_CN nincs**. Kína-target site-on alternative kell (manuális fordítás vagy másik forrás).
- **GitHub-tree cache TTL 12 óra:** Comparator-cache. Új fordítás-kérésnél `Comparator::clear_cache()` előtte.
- **Pro-csak-bináris plugin-ek:** Crocoblock, Bricks, egyes Divi-extension nem elérhető wordpress.org-ról free-fallback-ben — WP-admin-HelloPack-UI-n keresztül kell installálni.
- **Update-conflict:** a HelloPack-Client wp-cron-on belül injektál; ha másik plugin (pl. WP Rollback Pro, MainWP) ugyanabban a cron-ciklusban update-et indít, race-condition lehet. Megoldás: `wp cron event run` manuálisan vagy `wp plugin update --all` után `wp eval 'do_action("hellopack_fetch_schema");'`.

## Mikor NE használd a HelloPack-on át

- **Free-version-ok wordpress.org-on jobbak** — Akismet, WordPress core, Wordfence (free elég kisebb site-on), egyes natív-WP-plugin-ek nincsenek a HelloPack-ban
- **Friss-fejlesztett plugin** amit HelloPack még nem támogat — új plugin-ek várhatóan **2-3 hónap-on belül** kerülnek be a katalógusba
- **Site-licensing-restrictions** — egyes plugin-ek per-domain-pricing-ot követelnek meg vendor-szerződésben (pl. enterprise-only plugin-ek). HelloPack-en injektálva license-megsértés lehet — kérdezd meg a developer-t mielőtt használnád.
- **Niche / very-specific plugin** — ha a katalógus 492 plugin-jében nincs benne, érdemes a fejlesztőtől közvetlenül vásárolni (és a license-cost-ot a project-budget-be kalkulálni).
- **Production-critical plugin** ahol a vendor support szükséges — HelloPack-en aktivált license-en a vendor support általában nem érvényes (a license-t nem te vetted, hanem HelloWP).

## WP-CLI cheatsheet (HelloPack-flow)

Minden gyakran-használt parancs egy helyen, copy-paste-ready. Cseréld a `<...>` placeholder-eket.

### License + status

```bash
# License-validitás check
curl -s "https://api.hellowp.io/v1/hp-content/apicheck/" \
  -H "Authorization: Bearer <token>" \
  -H "User-Agent: <site-url>" | jq

# Vásárolt plugin-lista (492 elemű)
curl -s "https://api.hellowp.io/v1/hp-content/wordpress-plugins" \
  -H "Authorization: Bearer <token>" \
  -H "User-Agent: <site-url>" | jq '.data | length'

# WP option-ban tárolt token
wp option get hellopack_client --format=json | jq .token
```

### Cache invalidation (stale-list-fix)

```bash
# A „11 plugin"-cache 2022-ről stale lehet — force-refresh:
wp option delete hellopack_available_plugins
wp transient delete hellopack_available_plugins --all
wp eval 'do_action("hellopack_fetch_schema");'

# Plugin-update force-injection HelloPack-Pro-binárisokra
wp eval 'do_action("hellopack_fetch_schema");'
wp plugin update --all
```

### Translation install

```bash
# Comparator + FileInstaller (HelloPack-translate-réteg, ingyenes)
wp eval '
  HelloPack\Client\Translate\Comparator::clear_cache();
  $r = HelloPack\Client\Translate\Comparator::compare_all();
  $i = new HelloPack\Client\Translate\FileInstaller();
  foreach ($r as $item) {
    if ($item->status !== "up_to_date") {
      $i->install($item->slug, $item->type);
      WP_CLI::log("Installed: " . $item->slug);
    }
  }
'

# Fallback wordpress.org-ra (HelloPack-en NEM-szereplő plugin-ekre)
wp language plugin install <plugin-slug> hu_HU
wp language plugin install --all hu_HU  # bulk

# Translation-status check
wp language plugin list --status=installed
```

### Batch install Tier 1 stack (tipikus új-projekt)

```bash
# 8-plugin batch (free fallback települ, HelloPack-Pro-injection a wp-cron-on)
wp plugin install \
  complianz-gdpr-premium \
  cartflows \
  checkoutwc \
  advanced-custom-fields-pro \
  gravityforms \
  perfmatters \
  pixelyoursite-pro \
  wp-rollback \
  --activate

# Pro-binárisokra force-update
wp eval 'do_action("hellopack_fetch_schema");'
wp plugin update --all
```

## Troubleshooting

### „11 plugin csak elérhető a HelloConsole-on, de én 492-t fizetek"

- **Ok:** régi cache (akár 2022-es), a `hellopack_available_plugins` option stale
- **Megoldás:**
  ```bash
  wp option delete hellopack_available_plugins
  wp transient delete hellopack_available_plugins --all
  wp eval 'do_action("hellopack_fetch_schema");'
  ```
- **Ha nem segít:** ellenőrizd a license-aktiválást a HelloConsole-on (a domain hozzá van-e adva), majd `apicheck/` endpoint-on `status: active`-t várj.

### „Pro-feature nem aktiválódik a Pro-bináris-update után"

- **Ok:** néhány plugin (Crocoblock, Bricks) WP-admin-UI-n keresztül kell installálni — nincs free-fallback wordpress.org-on
- **Megoldás:** WP-admin → HelloPack → Plugins → search → Install (HelloPack-UI-bináris)

### „Migration után a HelloPack-license offline"

- **Ok:** license-domain-bound, az új-domain nincs aktivált state-en
- **Megoldás:** HelloConsole → Domains → Add new domain (pl. `example.com`) → új token (vagy ugyanaz a token) → WP-admin → HelloPack → Settings → Save

### „Translation nem települ — `not_installed` marad"

- **Ok 1:** `Comparator::compare_all()` cache 12 órás
- **Megoldás 1:** `wp eval 'HelloPack\Client\Translate\Comparator::clear_cache();'`
- **Ok 2:** plugin slug nem szerepel a 395-ös GitHub-listán
- **Megoldás 2:** fallback `wp language plugin install <slug> hu_HU` (wordpress.org)

### „Race condition update-conflict (Rollback Pro / MainWP)"

- **Ok:** több update-flow ugyanabban a wp-cron-tickben
- **Megoldás:** szekvenciális futtatás — `wp plugin update --all` → `wp eval 'do_action("hellopack_fetch_schema");'` → (vár 30 sec) → `wp plugin update --all` újra

### „Update-flow lefagy a Pro-bináris-letöltésnél"

- **Ok 1:** `api.hellowp.io` rate-limit (gyakori bulk-install-nál)
- **Megoldás 1:** várj 60 sec, majd `wp plugin update --all` újra
- **Ok 2:** Hostinger LiteSpeed-cache teszi le a régi-binárist
- **Megoldás 2:** `wp litespeed-purge all` (lásd [[05-Memory/Infrastructure]])

### „A Bearer token public-doc-ban / git-ben láttam"

- **🚨 Azonnal:** HelloConsole → API Creator → Revoke token → Generate new
- **WP-admin** → HelloPack → Settings → új token mezőbe → Save
- **Git history scrub:** `git filter-repo --replace-text` (lásd [[05-Memory/feedback_git_sensitive_data]])

## Decision-tree — új projekt-en mit aktiválj

Új WP-projekt-en a következő decision-tree mutatja, melyik plugin-csoportot érdemes a HelloPack-en át aktiválni. A tree feltételezi, hogy a license aktív és a HelloPack-Client telepítve van a domain-en.

### 1. lépés — Builder választása

- **Brand-fázis-mockup már Elementor-ben kész?** → **Elementor Pro** (+ Crocoblock ha bonyolult-CPT-stack kell)
- **Új-projekt, no-existing-content, perf-priorty** → **Bricks Builder** (+ Bricks-extras + BricksForge)
- **Lightweight, Gutenberg-only** → **GenerateBlocks Pro + GP Premium**
- **Divi-legacy** → **Divi Builder + 12 extension**

### 2. lépés — WooCommerce vagy nem?

- **Nincs webshop** → skip a WC-ecosystem
- **Single-tier shop, < 50 termék** → **CartFlows Pro + CheckoutWC** (Tier 1 default)
- **Multi-tier shop, 50+ termék** → fenti + **AI Product Recommendations + YITH Ajax Filter + Discount Rules PRO**
- **Subscription-business** → fenti + **YITH WooCommerce Subscription**
- **Booking-shop (étterem, szolgáltatás)** → **Amelia + WooCommerce Appointments**

### 3. lépés — Multilingual?

- **Egynyelvű** → skip
- **2-3 nyelv, lightweight** → **TranslatePress Business**
- **5+ nyelv, robust + WooCommerce-multilingual** → **WPML + 14 add-on** (de migration-cost magas, ha már TranslatePress él)
- **Bármi multi-nyelv** → futtasd a HelloPack-translation-Comparator-t (Réteg 3, ingyen 23 nyelven)

### 4. lépés — Form?

- **Egyszerű kontakt-form** → Elementor Pro Form-widget elég
- **Komoly multi-step + payment + signature** → **Gravity Forms + Stripe + reCAPTCHA + Akismet**
- **CRM-tight-integration** → **Fluent Forms Pro** (FluentCRM-mate)

### 5. lépés — Performance + GDPR (always-do, EU-target)

**Kötelező batch minden EU-target site-on:**

- **Complianz Premium** (cookie-banner, GDPR-form)
- **Perfmatters** (per-page perf-tweak)
- **WP Rocket** (page-cache)
- **ShortPixel vagy Imagify** (kép-optimalizálás — ne kettőt egyszerre!)
- **WP Rollback Pro** (update-rollback-biztonság)
- **PixelYourSite Pro** (analytics-pixel-tracking)

### 6. lépés — Backup + Migration (mindenhol)

- **UpdraftPlus** (backup, GDrive-destination)
- **All-in-One WP Migration + Unlimited Extension** (staging→live migration, lásd [[hostinger-updraftplus-staging-migration]])

### 7. lépés — Security (mindenhol)

- **Solid Security Pro** (régen iThemes Security Pro) — bruteforce + 2FA + file-change-detection

### 8. lépés — SEO (content-driven projekt-en)

- **Yoast SEO Premium** + **WooCommerce SEO** (ha webshop) + **Local SEO** (ha lokál-business)
- **AI-LLM-mention-optimization:** [[wp-yoast-llms-txt-customization]]

### 9. lépés — Email + CRM (post-launch, ha email-marketing scope-ban)

- **FluentCRM Pro** — newsletter, automation, cart-abandon-flow
- **YayMail Pro** — modern HTML order-email (csak ha WC)
- **AutomateWoo** — WC-marketing-automation

## Project-példák (cross-reference)

| Project | HelloPack-használat |
|---|---|
| [[02-Projects/rojtesbojt]] | **Aktív 2026-05-04 óta.** 24 plugin telepítve staging-en, 4 fordítás-Pro-tier installed (Elementor / TranslatePress / UpdraftPlus / Yoast Premium HU). Tier-1 install-batch 8 plugin (Complianz Premium + CartFlows Pro + CheckoutWC + ACF Pro + Gravity Forms + Perfmatters + PixelYourSite Pro + WP Rollback Pro). License-active-until 2027-05-07. |
| [[02-Projects/foxxi]] | TBD — ha example-foxxi.local-n is használjuk a HelloPack-license-t, ott külön domain-aktiválás kell a HelloConsole-on. |

## Linkek

- **HelloWP.io:** https://hellowp.io/
- **HelloConsole:** https://hellowp.io/hu/helloconsole/hellopack-kozpont/
- **API endpoint base:** https://api.hellowp.io
- **Translation GitHub:** https://github.com/hellowpio/wordpress-translations
- **HelloPack-Client plugin:** https://github.com/hellowpio/hellopack-client (vagy WP-admin/Plugins → "HelloPack")

## Forrás-doksik (rojtesbojt-projekt deep-dive)

- `/root/projektjeim/rojtesbojt/docs/site-fixes/2026-05-04-hellopack-deep-analysis.md` — 3 réteg azonosítása, első telepítési-log
- `/root/projektjeim/rojtesbojt/docs/site-fixes/2026-05-04-hellopack-modules-relevance.md` — 81-modul Tier-1/2/3 relevance-elemzés boutique-RETAIL-flow-ra
- `/root/projektjeim/rojtesbojt/docs/site-fixes/2026-05-07-hellopack-full-catalog-492.md` — 492-plugin teljes katalógus license-aktiválás után

## Kapcsolódó

- [[03-Hosts/Shared Hosting (Cloud Professional)]] — Hostinger Cloud Pro fiók ahol a license most fut
- [[05-Memory/Infrastructure]] — szerver- és host-info
- [[02-Projects/rojtesbojt]] — első projekt-példa, élő 2026-05-04 óta
- [[02-Projects/foxxi]] — potenciális második projekt-példa
- [[11-wiki/wp-elementor-template-conflicts]] — Elementor-Pro-feature-conflict-pattern-ek (HelloPack-en aktivált Pro-version-on is jelentkeznek)
- [[11-wiki/wpml-acf-elementor-multilingual-mirror]] — multilingual-pipeline (HelloPack-translation-réteggel együttműködik)
- [[11-wiki/hostinger-updraftplus-staging-migration]] — staging→live migration-flow (license re-add szükséges!)
