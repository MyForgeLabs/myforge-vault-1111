---
name: Rojt és Bojt — Foglalási rendszer döntés (D3)
type: decision
project: rojtesbojt
created: 2026-05-08
agent: claude
recommendation_by: Claude (Opus 4.7)
status: recommended-pending-Gyuszi-confirmation
tags: ["#type/decision", "#project/rojtesbojt", "#topic/booking", "#topic/tech-stack"]
---

# D3 — Foglalási rendszer: Amelia Pro + Gravity Forms (HIBRID, kétszintes flow)

## Kontextus

A Tech-fázis-spec szerint a foglalási rendszer **kétszintes flow**:

- **Coffee normál asztalfoglalás** — egyszerű, gyors, mobile-first turisták + helyi vendégek számára
- **VIP / Lexus reggeli** — ajánlatkérő-flow: csomag-választás (Luxus 49K / Lexus 89K / Privé Wedding 120K+ Ft) + Stripe-előleg + privát-egyeztetés

A 2026-05-07 HelloPack-license-aktiválás után **5 erős opció** elérhető (492-plugin-katalógusból):

1. **Amelia** (most installed, free 2.3) — HelloPack Pro 7.4.1+ inject elérhető
2. **Fluent Booking Pro** — modern, FluentCRM-integrált
3. **Jet Appointments Booking** + **JetBooking** — Crocoblock-stack-bound
4. **WP Booking System Premium** + 20 add-on
5. **Bookio** (HU-leader) — NINCS HelloPack-ban
6. **Tablein** (1-SaaS kétszintes) — NINCS HelloPack-ban

## Recommendation

🎯 **Amelia Pro + Gravity Forms hibrid (kétszintes flow)**

### Coffee normál asztalfoglalás → Amelia Pro

**Why:**
- ✅ Most installed (free 2.3), HelloPack injekció Pro 7.4.1+
- ✅ Comprehensive: appointments + events + packages — Coffee-foglalás-flow széles spektrum
- ✅ „Automated booking specialist 24/7" — pontosan a turista-fókusz illik (turisták éjszaka, hétvégén foglalnak)
- ✅ HU + EN translations már installed; DE/FR/RU partial coverage HelloPack-GitHub-ról
- ✅ Bricks Builder kompatibilitás (Pro-tier shortcode + widget support)
- ✅ Visual customization-on belül brand-paletta integrálható
- ✅ Mobile-first booking-form natívan
- ✅ Customer-side dashboard (foglalás-management, módosítás, lemondás)

**Config plan:**
- 1 service-csoport: „Coffee asztalfoglalás" (időpontok 9:00-18:00 H-Szo, 9:00-13:00 V — utolsó óra előtt 1h booking-stop)
- Capacity: konfigurálandó Gyuszitól (kb. 30-40 fő egyidejű asztal-kapacitás)
- Customer-fields: név, telefon, fő-szám, megjegyzés
- Email-confirmation HU + EN auto-translation
- WP Mail SMTP via Hostinger (WP Mail SMTP installed)

### VIP / Lexus reggeli → Gravity Forms + Stripe Add-On

**Why:**
- ✅ Multi-step űrlap (csomag-választás → kapcsolat → Stripe-előleg → confirmation)
- ✅ Conditional logic — ha „Lexus Privé Wedding" választva, plusz mezők (tour-route preferencia, fotózás-igény)
- ✅ Gravity Forms Stripe Add-On natív Stripe-checkout (előleg/teljes/depozit-flow támogat)
- ✅ Akismet + reCAPTCHA add-on anti-spam
- ✅ Mailchimp / ActiveCampaign / FluentCRM lead-capture (post-foglalás follow-up)
- ✅ Webhook → admin-email + Slack ha Gyuszi-real-time-notification kell
- ✅ Multilingual: Gravity Forms Multilingual add-on (HelloPack-Pro)

**Config plan:**
- Form-mező-szerkezet:
  1. **Csomag-választás** (radio): Luxus Chapter 49K / Lexus Chapter 89K (+Buda Castle tour) / Lexus Privé Wedding 120K+
  2. **Dátum + időpont** (date-picker, csak 9:00-11:00 reggeli-ablak)
  3. **Fő-szám** (2-12, csomag-szerint)
  4. **Vendég-adatok** (név, email, telefon)
  5. **Speciális igények** (textarea, opcionális — nászút / születésnap / üzleti partner / proposal)
  6. **Stripe előleg-fizetés** (csomag-ár 50%-a vagy Gyuszi-döntés)
  7. **Submit + auto-confirmation**

- Email-flow:
  - Vendégnek: HU+EN confirmation, Lexus-csomag-leírás-attachment + cancellation-policy
  - Adminnek: Gyuszi+Orsi értesítés, Slack-webhook (ha kell)
  - 24h-pre-event reminder: vendégnek
  - Post-event follow-up: TripAdvisor-review-prompt

### Why NEM a többi

| Plugin | Miért NEM |
|---|---|
| **Fluent Booking Pro** | Younger, less mature. FluentCRM-integration only-strength — DE FluentCRM még nincs telepítve. Post-launch fontolható, ha email-marketing FluentCRM-re kerül. |
| **Jet Appointments / JetBooking** | Crocoblock-stack-bound — Bricks-migration-tal nem szervesen illeszkedik. JetEngine telepítés overhead. |
| **WP Booking System Premium** | 20+ add-on overkill. Vacation-rental-szegmens-fókusz — restaurant-szerű simple-asztalfoglaláshoz nem optimális. |
| **Bookio** | Nincs HelloPack-ban → SaaS-cost (~€30/hó Plus-tier). Bár HU-piaci-leader (Zsidai-csoport-validált), turista-fókuszú angol-language-quality gyengébb mint Amelia. |
| **Tablein** | Nincs HelloPack-ban → SaaS-cost. Kétszintes flow natívan, de magyar-piaci ismeretlenség alacsony adoption-arányt sugall. |

## Konzekvencia

### Tech-architektúra változás

A `tech-architecture-spec-v0.md` „Foglalási rendszer architektúra" szakasz frissítendő:

- ❌ Régi: „Bookio (normál) + Stripe-előleg saját Bricks-űrlap (VIP)"
- ✅ Új: **„Amelia Pro (normál) + Gravity Forms + Stripe Add-On (VIP/Lexus)"**

### Setup-feladatok (Tech-fázis-implementáció részeként)

1. **Amelia Pro update** HelloPack-en keresztül (auto-injection most már aktív license-zsel)
2. **Amelia config**: services + working-hours + customer-fields + email-templates HU+EN
3. **Gravity Forms install** HelloPack-Pro
4. **Gravity Forms add-on-batch:** Stripe + Akismet + reCAPTCHA + Multilingual
5. **VIP-form construct** a fenti spec szerint (multi-step + conditional)
6. **Stripe-account-setup** (test-mode → live-mode Gyuszi-creds-szel)
7. **TranslatePress-integration** mindkét flow-ra (Amelia-shortcode + Gravity-Forms-output)
8. **Bricks-template embed**: Coffee-flow `/asztalfoglalas/`, VIP-flow `/vip/` page-en

### Costs

- **Amelia Pro**: $0 (HelloPack)
- **Gravity Forms + add-ons**: $0 (HelloPack)
- **Stripe**: 1.4% + 25 cent per transaction (EU-card), 2.9% + 25 cent (non-EU). VIP 49K-120K Ft → ~700-2000 Ft per booking-fee.
- **WP Mail SMTP**: $0 (free, ya installed)

**Total**: $0 plugin-cost. Csak Stripe transaction-fee.

### Open Q-k Gyuszinak (Brand-brainstormon konfirmálandók)

- **G1:** Coffee asztal-kapacitás (egyidejű foglalás-szám)? Pl. ha 40 asztal van, akkor 40-es time-slot-cap.
- **G2:** Coffee-foglalás-confirmation manuális vagy auto? (Amelia auto-confirm + sms-notification, vagy admin-Gyuszi-jóváhagyás-után értesítés)
- **G3:** VIP előleg-arány: 50% / 30% / teljes-előre? Mit fogadtok el szakmailag?
- **G4:** No-show-cancellation policy: 24h előtt visszafizetés / 48h / nincs?
- **G5:** Stripe-account: van-e már (example-rojt.local-n a /vip/ csomag-ár-jelölés alapján — talán igen), vagy új-account-setup?
- **G6:** Email-templates Hangja: Odette Lumière-aforizmás-tone, vagy klasszikus „köszönjük a foglalást"?

## Risk

- **Amelia learning-curve Orsi+Gyuszinak** — 1-órás walkthrough Brand-launch előtt kötelező
- **Gravity Forms config-bonyolultság** — 7-mező multi-step űrlap tisztán dokumentálandó (`docs/booking/vip-form-spec.md` írandó)
- **Stripe-fee — turista-vendégeknek** Hungary-non-resident card-fee (2.9%) magasabb mint EU-card (1.4%) — ár-kalkulációba beépítendő

## Kapcsolódó

- Tech-fázis spec: [`design-artifacts/E-PRD/tech-architecture-spec-v0.md`](../../projektjeim/rojtesbojt/design-artifacts/E-PRD/tech-architecture-spec-v0.md)
- HelloPack vault wiki: [[11-wiki/hellopack-wordpress-plugin-suite]]
- HelloPack 492-katalógus: [`docs/site-fixes/2026-05-07-hellopack-full-catalog-492.md`](../../projektjeim/rojtesbojt/docs/site-fixes/2026-05-07-hellopack-full-catalog-492.md)
- D1 ADR (Bricks Builder migration): [[07-Decisions/2026-05-08 Rojt és Bojt — Bricks Builder migration (D1)]]
- Project hub: [[02-Projects/rojtesbojt]]
