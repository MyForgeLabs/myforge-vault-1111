---
name: Migration-pattern család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/migration, taxonomy, evergreen, wordpress, prisma, schema]
---

# Migration-pattern család taxonomy

> [!info] TL;DR
> A vault **23 Concept**-en keresztül beszél „migration"-ról, de ezek **4 teljesen különböző tartomány**: (1) WP-content (Elementor↔Bricks, ACF), (2) WP-hosting (subdomain, UpdraftPlus), (3) Prisma-schema, (4) URL/wikilink. A négy migration-családnak **különböző biztonsági-protokollja** van — ez a wiki összegzi a közös szabályokat.

## Cluster-members

| Concept | Család | Forrás |
|---|---|---|
| Elementor migration to Bricks | WP-content | session |
| Naive Elementor migration | WP-content | session |
| Bricks migration | WP-content | session |
| Bricks migration sub-project | WP-content | session |
| Bricks migration total | WP-content | session |
| ACF Flexible Content migration | WP-content | wiki/wp-acf-flexible-to-elementor-migration |
| ACF Flexible to Elementor migration | WP-content | wiki |
| ACF to Elementor migration | WP-content | wiki |
| Bricks Builder migration | WP-content | session |
| Migration playbook | meta | session |
| Migration procedure | meta | session |
| Migration script | meta | session |
| migration script | meta | session |
| All-in-One WP Migration | WP-hosting | session |
| Subdomain migration | WP-hosting | session |
| URL-stable migration | WP-hosting | wiki |
| URL-stable migration approach | WP-hosting | wiki |
| UpdraftPlus migration pattern | WP-hosting | wiki/hostinger-updraftplus-staging-migration |
| Prisma 7 migration | Prisma-schema | session |
| Schema migration DROP COLUMN | Prisma-schema | session |
| `Migration 20260510122403_add_machine_accessories` | Prisma-schema | session |
| Canvas migration planning | doc-meta | session |
| wikilink migration | doc-meta | session |

## A 4 migration-család

### 1. WP-content migration (page-builder swap)
**Cél:** Elementor ↔ Bricks ↔ Gutenberg között tartalom-megőrzés.

**Mintázatok:**
- **Naive migration** (anti-pattern): page-builder export-import → veszít UI-customokat
- **Mirror-pipeline**: ACF Flexible Content → Bricks/Elementor template-ek (WP-CLI `post meta delete + add --format=json`)
- **WPML mirror** [[wpml-acf-elementor-multilingual-mirror]] → 3-lépéses HU→EN tükör

**Biztonsági-protokoll:**
1. **Pre-migration screenshot** minden oldalról (page-by-page diff utólag)
2. **Staging-clone** ELŐSZÖR — production NEM első tárgy
3. **WP-CLI script** idempotens (újrafutás safe)
4. **Rollback-export** ELŐTTE: `wp db export pre-migration.sql`

→ [[wp-acf-flexible-to-elementor-migration]] · [[wp-cli-bricks-postmeta-pattern]] · [[wpml-acf-elementor-multilingual-mirror]]

### 2. WP-hosting migration (host-swap, subdomain)
**Cél:** WP-installt egyik host-ról másikra, vagy production → staging clone.

**Mintázatok:**
- **All-in-One WP Migration** plugin — egyszerű, de >2GB-on chunked
- **UpdraftPlus pattern**: backup zip-ek + manuális `wp core download` ha `wpcore.zip` üres
- **URL-stable migration**: domain-csere `wp search-replace` + `siteurl`/`home`

**Biztonsági-protokoll:**
1. **Hostinger LiteSpeed cache** 7-napos image-edge → `wp cache flush` NEM elég, fájlnév-rename ([[hostinger-updraftplus-staging-migration]])
2. **`wp search-replace --dry-run` ELŐTT** — látod hány érintett row
3. **DB-szerializált data** miatt SOHA ne `sed/awk` URL-csere, MINDIG `wp search-replace`

→ [[hostinger-updraftplus-staging-migration]]

### 3. Prisma-schema migration (DB)
**Cél:** ORM-séma változtatás production-DB-n.

**Mintázatok:**
- **`prisma migrate dev`** — dev-environment auto-apply
- **`prisma migrate deploy`** — production apply (NEM `dev`)
- **`Schema migration DROP COLUMN`** — production-ban danger; backup ELŐTTE
- **`Migration 20260510122403_add_machine_accessories`** — timestamp-prefix MIGRATION_NAME konvenció

**Biztonsági-protokoll:**
1. **`prisma migrate diff`** ELŐTT — dry-run SQL
2. **`pg_dump`** ELŐTTE (production-DB minden migration előtt)
3. **DROP COLUMN megelőzően RENAME** kétszakaszú deploy (deploy → wait → drop)
4. **Prisma 7 migration** — `@prisma/adapter-pg` runtime-csere is benne; staging-en először

**Anti-pattern:** `prisma migrate dev` production-on → adat-veszés (reset-eli a DB-t).

→ [[prisma-compound-unique-null-quirk]] · [[prisma-seed-admin-edit-protected]]

### 4. Doc/URL migration (link-update)
**Cél:** Obsidian wikilink-átnevezés, canvas-restruktúra, URL-redirect.

**Mintázatok:**
- **wikilink migration** — vault-rename → Obsidian auto-rename minden link
- **Canvas migration planning** — `.canvas` JSON manuális szerkesztés
- **URL-stable migration** — old-URL → new-URL redirect-table

**Biztonsági-protokoll:**
1. **Git-commit ELŐTTE** — Obsidian rename-cascade-t commitold külön
2. **301-redirect** régi URL-okra (SEO-megőrzés)
3. **Vault-rename Mac/Obsidian sync** óvatosan (Mac aktív session-nél detached HEAD risk)

→ Memory: vault-rename Mac Obsidian-Git sync incident

## Közös cross-domain szabályok

1. **Backup ELŐTTE** — minden 4 családban: WP `wp db export`, Prisma `pg_dump`, hosting full-zip, vault `git commit`
2. **Idempotens script** — újrafutás safe (Prisma migration timestamp-prefix automatikus; WP-CLI script-ed te írod meg úgy)
3. **Dry-run support** — `--dry-run`, `migrate diff`, `search-replace --dry-run` mindenhol ELŐSZÖR
4. **Staging-first** — production-ra SOHA közvetlenül
5. **Rollback-plan ÍRD LE** — minden migration-PR-ban: hogyan-vissza
6. **Migration-script git-trackolt** — Prisma `prisma/migrations/`, WP külön `migrations/YYYY-MM-DD-<név>.sh`
7. **Verification-step utána** — count-check, sample-row-check, screenshot-diff
8. **Lock the source** during migration — WP `wp maintenance-mode activate`, Prisma `pgbouncer` pause

## Anti-pattern

| Anti-pattern | Hiba | Család |
|---|---|---|
| Production WP plugin „migrate now" gomb backup nélkül | semmilyen rollback | WP-content |
| `sed -i 's/old.com/new.com/g'` WP DB-dump-on | szerializált hossz törik | WP-hosting |
| `prisma migrate dev` production-on | DB reset | Prisma |
| Page-builder export → import csak | UI-customok veszítenek | WP-content |
| Bulk vault-rename aktív Mac session-nél | detached HEAD, conflict-cascade | Doc |

## Kapcsolódó

- [[hostinger-updraftplus-staging-migration]]
- [[wp-acf-flexible-to-elementor-migration]]
- [[wp-cli-bricks-postmeta-pattern]]
- [[wpml-acf-elementor-multilingual-mirror]]
- [[prisma-compound-unique-null-quirk]]
- [[prisma-seed-admin-edit-protected]]
- [[multi-layer-safety-gate]]
