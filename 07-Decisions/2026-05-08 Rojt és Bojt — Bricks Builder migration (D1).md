---
name: Rojt és Bojt — Bricks Builder migration döntés (D1)
type: decision
project: rojtesbojt
created: 2026-05-08
agent: claude
decision_by: Peti (2026-05-08 ~00:30)
status: locked
tags: ["#type/decision", "#project/rojtesbojt", "#topic/tech-stack", "#topic/builder"]
---

# D1 — Bricks Builder migration (Elementor → Bricks)

## Kontextus

A Rojt és Bojt redesign Tech-fázis-spec-jében (`design-artifacts/E-PRD/tech-architecture-spec-v0.md`) eredetileg **Elementor PRO maradás** volt 90% confidence-szintű ajánlás. Indok: time-to-launch, Orsi+Gyuszi-tudja, plugin-stack-él.

A 2026-05-07 HelloPack-license-aktiváláskor azonban kiderült, hogy **Bricks Builder Pro** elérhető a 492-plugin-katalógusban — ingyen, license-szel. Ez megnyitotta a builder-csere-opciót.

## Audit-adatok

A jelenlegi staging Lighthouse-eredmények:

- Mobile Perf: 66-73
- Desktop Perf: 59-71 (**paradox** — desktop gyengébb mint mobile!)
- LCP: 5.7-11.5s
- Elementor 1.16 MB / 75 req / 22 script / 22 CSS / 5 webfont
- WebP konverzió hiányzik (51 JPG vs 1 WebP)

Az Elementor önmagában jelentős JS+CSS-overhead-et hoz. ShortPixel WebP + Perfmatters + WP Rocket fine-tuning kombinációval **becsült javulás csak 80-85 Mobile Lighthouse-ig** (Mobile 90+ a cél).

Bricks Builder kontraszt:
- Lighthouse Mobile 95+ az iparági benchmark
- DOM-light: ~10 script + ~5 CSS Elementor 22-22-jéhez képest
- Theme integráció natív (Bricks egyben theme + builder)
- Modern WordPress 6.x+ Block Editor kompatibilitás

## Döntés

🟢 **Bricks Builder migration — elfogadva.**

Peti döntött (2026-05-08): „a fejlesztést D1 bricksben kiprobálnám, ha azt mondod jobb mint az elementor".

**A migration-trade-off:**

- **Költség:** ~2-3 hét re-build a 4 fő-page-re (homepage, /vip/, /asztalfoglalas/, /uzleteink/) + /boutique/ retail-flow + 6 nyelv multilingual-replikálás
- **Hozam:** drámai perf-jump (Mobile 66-73 → 95+ becsült), kisebb DOM, jobb a11y, modern dev-experience
- **Risk:** Orsi+Gyuszi NEM látta még a Bricks-builder-t — ha a content-frissítési-flow ismeretlen-bonyolult, post-launch-fenntartás-kockázat. **Mitigation:** Brand-fázis output-ja közvetlen Bricks-template-ben, Gyuszinak walkthrough Brand-launch előtt.

## Konzekvencia

### Tech-architektúra változások

1. **Bricks Builder Pro install** stagingre HelloPack-en keresztül (Pro-version automatikus)
2. **Bricks Theme** aktiválás Hello-Elementor helyett
3. **Elementor Pro deaktiválás** (csak deactivate, NE delete — fallback fenntartása)
4. **Brand-fázis design output Bricks-template-ben** (D-Design-System tokens + components → Bricks Global Classes + Templates)
5. **CartFlows Pro Bricks-kompatibilitás** verify (Bricks WC-flow kifejezetten szupportálva)
6. **Per-page CSS már Perfmatters-rel finomítható**

### Brand-fázis impact

A `D-Design-System v0` (1296 LOC) **közvetlenül Bricks-Global-Classes-ré transzformálható**:
- Color tokens → Bricks Color-palette
- Typography tokens → Bricks Typography-classes
- Motívum SVG-k → Bricks Section-divider-extras
- Komponens-spec → Bricks Custom-Component-Library

A Moodboard v2.0 lágyított Direction 1 design közvetlenül Bricks-mockup-on jelenik meg.

### Tech-fázis Implementation Plan változások

A Tech-fázis-spec-ben (E-PRD `tech-architecture-spec-v0.md`) a builder-szakasz **frissítendő:**

- ❌ Régi: „Elementor PRO marad + Crocoblock"
- ✅ Új: „Bricks Builder Pro + BricksExtras + Bricksforge" (mind HelloPack-Pro)
- BricksExtras + Bricksforge add-on-ok már a 492-katalógusban

### Migration playbook (új sub-projekt-feladat)

Új feladat-csomag: **„Bricks-migration sub-project"** a 02-Brand-fázis és 03-Tech-fázis közé:

1. Bricks Pro install + theme-aktiválás (1 nap)
2. D-Design-System Bricks-Global-Classes konvertálás (3-5 nap)
3. 4 fő-page Bricks-template-ben re-build (5-7 nap)
4. /boutique/ retail-flow Bricks + WooCommerce template (3-4 nap)
5. 6-nyelv multilingual replikálás Bricks → TranslatePress (2-3 nap)
6. WC + Amelia + Gravity Forms Bricks-template embed (2-3 nap)
7. Lighthouse-verifikáció Mobile 90+ + LCP <2.5s (1 nap)
8. Final verify staging vs migration-rollback-fallback (1 nap)

**Total estimate:** ~20-25 nap (4-5 hét) Bricks-migration. Tech-fázis-spec-frissítendő ezzel a roadmap-pel.

### Rollback-stratégia

Ha Bricks-migration meghiúsul (perf-improvement nem elég, vagy Orsi+Gyuszi UX-kontent-frissítés-rosszul-fogadja):

- Elementor PRO **NE legyen törölve** (deactivate csak)
- Bricks-template-ek mellett az Elementor-template-ek a postmeta-ban maradjanak (`_elementor_data` field érintetlen)
- Reaktiválás 1-click-en keresztül (Bricks deactivate → Elementor activate → page-load)
- Live-deploy ELŐTTI staging-Bricks-validation kötelező

## Kapcsolódó

- Tech-fázis spec: [`design-artifacts/E-PRD/tech-architecture-spec-v0.md`](../../projektjeim/rojtesbojt/design-artifacts/E-PRD/tech-architecture-spec-v0.md)
- Site audit (Elementor-perf-baseline): [`design-artifacts/A-Product-Brief/01-site-audit.md`](../../projektjeim/rojtesbojt/design-artifacts/A-Product-Brief/01-site-audit.md)
- HelloPack 492-katalógus: [`docs/site-fixes/2026-05-07-hellopack-full-catalog-492.md`](../../projektjeim/rojtesbojt/docs/site-fixes/2026-05-07-hellopack-full-catalog-492.md)
- HelloPack vault wiki: [[11-wiki/hellopack-wordpress-plugin-suite]]
- Project hub: [[02-Projects/rojtesbojt]]
