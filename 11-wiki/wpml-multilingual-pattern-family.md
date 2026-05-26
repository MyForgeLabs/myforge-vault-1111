---
name: WPML multilingual pattern család
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/wpml, taxonomy, evergreen, wordpress, i18n, multilingual]
---

# WPML multilingual pattern család

> [!info] TL;DR
> A vault-ban **24 WPML-érintett Concept** szétszórva, eddig **1 specific wiki** ([[wpml-acf-elementor-multilingual-mirror]]). Itt taxonomy: a WPML hibák és minták **5 családba sorolódnak** — Mirror, Render, CLI, Menu-sync, URL-struktúra. Mindegyikhez a saját workaround-protokoll.

## Cluster-members

| Concept | Család | Forrás |
|---|---|---|
| WPML ACF Elementor multilingual mirror | Mirror | wiki |
| WPML mirror pipeline | Mirror | session |
| WPML EN setup | Mirror | session |
| WPML EN duplicates | Mirror (bug) | session |
| WPML page-builder Elementor add-on | Mirror | session |
| WPML language-aware fallback | Render | session |
| WPML language-aware render | Render | session |
| WPML language-aware render fallback | Render | session |
| WPML missing translation | Render | session |
| WPML wpml_object_id filter | Render | session |
| wpml_object_id fallback | Render | session |
| WPML being translated warning | Render (UX) | session |
| WPML being translated warning removal | Render (UX) | session |
| WPML undefined array key warning | Render (bug) | session |
| WPML CLI auto-translate | CLI | session |
| wp wpml command | CLI | session |
| WPML auto-translate | CLI | session |
| WPML | meta | session |
| WPML multilingual restore | meta/recovery | session |
| WPML menu-sync | Menu-sync | session |
| WPML menu-sync disable | Menu-sync | session |
| WPML menu-sync disabled | Menu-sync | session |
| WPML page hierarchy URL | URL-struct | session |
| WPML short URL /en/about-us-dental/ | URL-struct | session |
| WPML EN content review | meta | session |

## Az 5 család

### 1. Mirror (HU → EN tartalmi tükör)
**Cél:** ACF/Elementor magyar tartalmat angolra duplikáljuk 1:1 szerkezettel, csak a szöveg-mezőket fordítva.

**Mintázat:** `wpml-acf-elementor-multilingual-mirror` — 3 lépés:
1. `wpml_object_id` lookup minden HU postId-ra
2. ACF-mezők másolása szótár-cseréje EN-fordítással
3. Elementor `_elementor_data` JSON-walk + string-by-string fordítás

**Hibák:**
- **WPML EN duplicates** — auto-translate dupla EN-oldalt csinál ha menu-sync NEM disable-elve (lásd #4)
- **WPML page-builder Elementor add-on** szükséges Elementor-content-mirror-höz

→ [[wpml-acf-elementor-multilingual-mirror]]

### 2. Render (frontend nyelv-lookup)
**Cél:** template-fájlban a megfelelő nyelv-verzió jelenjen meg, fallback-tel.

**Mintázat:**
```php
$en_id = apply_filters('wpml_object_id', $hu_id, 'page', true);  // 3rd arg = fallback enable
if (!$en_id) {
  // Render fallback (lásd [[fallback-pattern-family-taxonomy]] §1)
}
```

**Hibák:**
- **WPML missing translation** — `wpml_object_id` `false`-t ad vissza fallback nélkül
- **WPML undefined array key warning** — PHP 8.x strict, WPML belső array-access; suppress vagy újabb WPML
- **WPML being translated warning** UX-zaj → admin-only display (`is_admin()` gate)

**Szabály:** `apply_filters('wpml_object_id', $id, $type, true)` **MINDIG** 3rd arg `true` = fallback engedélyezve (kivéve admin-edit context).

### 3. CLI (WP-CLI auto-translate)
**Cél:** batch-translate skripttel.

**Mintázat:**
```bash
wp wpml lang activate en
wp wpml job list --target-language=en --status=needs-update
wp wpml batch send-to-translation --target-language=en
```

**Hibák:**
- **wp wpml command** nem mindig elérhető — `wpml-cli` add-on kell
- `auto-translate` queue megakad ha credit-hiány → cron újraindítás

### 4. Menu-sync (KAPCSOLD KI!)
**Cél:** WPML-automatic menu-mirror — **gyakorlatilag mindig kapcsolódik ki**, mert dupla EN-oldalt csinál.

**Szabály:** WPML Settings → Synchronization → **Menu sync OFF**. Manuálisan szerkeszd az EN-menüt.

- **WPML menu-sync disable / disabled** — protokoll: új project Day 0 menu-sync OFF
- **WPML EN duplicates** root-cause: menu-sync ON + auto-translate ON kombináció

### 5. URL-struktúra
**Cél:** EN-permalinkek HU-page-hierarchy-tükrében + nyelv-prefix.

**Mintázat:**
- `/about-us` (HU, default-lang) → `/en/about-us` (EN)
- Hierarchia tükrözése: `/szolgaltatas/fogaszat` → `/en/services/dental`
- WPML „Different languages in different directories" mód

**Hibák:**
- **WPML page hierarchy URL** — EN-child-page `parent_id` lookup `wpml_object_id`-vel kell
- **WPML short URL `/en/about-us-dental/`** — Yoast/permalink-plugin kollízió ha slug nem-fordítva

**Szabály:** EN-slug fordítva (NEM eredeti HU-slug `/en/` prefix-szel).

## Közös WPML-szabályok

1. **`wpml_object_id` 3-arg true** Render-rétegben **mindenhol**, kivéve admin-edit
2. **Menu-sync OFF** Day 0 — manuális EN-menü
3. **`is_admin()` gate** WPML-UX-warning suppression-höz (front-end-en NE jöjjön)
4. **WPML mirror pipeline idempotens** — újrafutás safe (post-meta `wpml_translated_at` timestamp)
5. **Page-builder add-on** Elementor-content-translate-hez kötelező
6. **EN-slug fordított**, NEM HU-slug-másolat
7. **PHP 8.x strict-warning suppression** — WPML belső array-access (vagy upgrade-elj)

## Anti-pattern

| Anti-pattern | Hiba |
|---|---|
| `wpml_object_id` 3-arg `false` Render-en | white-page ha EN-vers nem-létezik |
| Menu-sync ON + auto-translate ON | dupla EN-oldal |
| EN-slug = HU-slug ékezet-nélkül | SEO-duplicate-content |
| `WPML being translated warning` front-end-en | user-confusion |
| Hand-craft EN-permalinkek WPML config helyett | regenerate URL-ek elveszítik az SEO-t |

## Kapcsolódó

- [[wpml-acf-elementor-multilingual-mirror]]
- [[wp-acf-flexible-to-elementor-migration]]
- [[wp-elementor-template-conflicts]]
- [[migration-pattern-family-taxonomy]]
- [[fallback-pattern-family-taxonomy]]
<!-- auto-enriched 2026-05-18: +1 semantic cross-link via vault-search -->
- [[wp-elementor-bricks-json-escape-trap]] (sem-rokon, score=0.48)
