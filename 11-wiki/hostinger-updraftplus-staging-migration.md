---
name: Hostinger UpdraftPlus staging-migráció buktatók
description: WP-site áttelepítése egyik Hostinger-staging-ről másikra UpdraftPlus-szal — 4 jellemző gotcha + procedure
type: wiki
created: 2026-05-04
tags: ["#tech/wordpress", "#tech/hostinger", "#tech/updraftplus"]
---

# Hostinger UpdraftPlus staging-migráció — 4 buktató

A Hostinger shared-hosting alatt egy fél-UpdraftPlus-restore közben (WP-site átültetése egyik sub-domain-ről másikra) jellemző hibák.

## 1. ⚠️ `wpcore` ZIP NEM tartalmazza a WP-core fájlokat

Az UpdraftPlus elnevezésével ellentétben a `backup_*-wpcore*.zip` fájlok **csak a NEM-standard WP fájlokat** tárolják — egyedi mappákat (pl. `_docs/`, `foxxi-test/`), régi `fogaszat.bak.*` áthelyezett mappákat, plus a non-content / non-config gyökérben lévő dolgokat.

A tényleges WP-core (`wp-admin/`, `wp-includes/`) **NINCS** ezekben a zip-ekben.

**Tünete:** restore közben PHP fatal: `Failed opening required '...wp-admin/includes/file.php'`

**Megoldás:**
```bash
cd /home/USER/domains/SITE/public_html
wp core download --force --skip-content
# Ez letölti a WP core-t, NEM bántja a wp-content/-et (uploads, plugins, themes)
```

A `--version=X.Y.Z`-t megadni nem kell, automatikusan a legfrissebb stabilra megy. Ha specifikus verzió kell, először `wp core version` (ha indulna).

## 2. mu-plugins **átkerülnek** a backup-zip-ben

A `backup_*-mu-plugins.zip` (vagy `backup_*-others.zip`) tartalmazza az összes `wp-content/mu-plugins/*.php` fájlt — restore után automatikusan aktívak. **DE:** ha a backup ELŐTT új mu-pluginokat csináltunk és a backup ELŐTT hoztuk létre őket, akkor benne lesznek; ha a backup UTÁN csináltuk őket, akkor manuálisan át kell vinni.

**Verify:**
```bash
ssh hostinger 'ls /home/USER/domains/NEW-STAGING/public_html/wp-content/mu-plugins/'
```

## 3. wp_options `siteurl` + `home` automatikusan átíródik

UpdraftPlus a restore során a wp_options `siteurl` + `home` mezőket átírja az új domain-re. Plus a wp_postmeta-ban lévő URL-eket is search-replace-eli.

**DE:** a `wp_postmeta._menu_item_url` mezők (custom-link menu items) — ezeket átírja domain-szinten, **DE** a path-component (`/fogaszat/...` vagy `/en/dental-center/...`) marad. Ha a backup a HU-path-ot tárolta, akkor az új staging-en is HU-path lesz minden EN dental menu item-en.

**Tünete:** `wp menu item list fox-menu-en` HU URL-eket ad (`/fogaszat/...` helyett `/en/dental-center/...` kéne)

**Megoldás:** path-fix script futtatása `wp eval-file`-lal, az EN page-ek `get_permalink($id)`-jével az EN nyelvi kontextusban (`do_action('wpml_switch_language', 'en')`).

## 4. Yoast llms.txt + Schema cache — regenerálandó

Yoast a `/llms.txt`-t cron-eseménnyel generálja (`wpseo_llms_txt_population`, hetente). A backup után friss generálás kell, hogy az új domain-rel jelenjen meg a tartalom.

```bash
wp cron event run wpseo_llms_txt_population
```

A Schema viszont request-szerinti, nincs cache-issue.

## Recommended migration procedure

```bash
# 1. Pre-migration: backup OK?
ssh hostinger 'ls -la wp-content/updraft/backup_*-wpcore*.zip'

# 2. Restore via UpdraftPlus admin UI (ne CLI!)
# Settings → UpdraftPlus → Existing backups → Restore

# 3. Ha megakad core-fájl-hiányzás miatt:
ssh hostinger 'cd public_html && wp core download --force --skip-content'

# 4. Cache flush
ssh hostinger 'cd public_html && wp cache flush && wp w3-total-cache flush all'

# 5. Verify mu-plugins
ssh hostinger 'ls public_html/wp-content/mu-plugins/'

# 6. Verify Schema, llms.txt
curl -s "https://NEW-STAGING/llms.txt" | head
curl -s "https://NEW-STAGING/" | grep -c application/ld+json

# 7. Yoast llms.txt regenerate
ssh hostinger 'cd public_html && wp cron event run wpseo_llms_txt_population'

# 8. Path-fix EN menu URLs (ha menu-translation van)
# (saját script wp_get_nav_menu_items + EN-context get_permalink-szel)
```

## Kapcsolódó

- [[wpml-acf-elementor-multilingual-mirror]] — WPML EN-tükör fixek
- [[wp-yoast-llms-txt-customization]] — llms.txt szabály-tisztítás
- Hostinger shared hosting cheatsheet — TBD (még nem készült el)
