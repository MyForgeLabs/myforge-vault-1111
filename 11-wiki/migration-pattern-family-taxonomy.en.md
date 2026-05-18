---
name: Migration-pattern family taxonomy
type: wiki
lang: en
translated_from: migration-pattern-family-taxonomy
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/migration, taxonomy, evergreen, wordpress, prisma, schema]
---

# Migration-pattern family taxonomy

> [!info] TL;DR
> "Migration" gets used loosely, but it spans **4 totally different domains**: (1) WP-content (Elementor↔Bricks, ACF), (2) WP-hosting (subdomain, UpdraftPlus), (3) Prisma schema, (4) URL/wikilink. Each migration family has a **different safety protocol** — this wiki summarises the common rules.

## Cluster members (representative)

| Concept | Family |
|---|---|
| Elementor migration to Bricks | WP-content |
| Naive Elementor migration | WP-content |
| Bricks migration | WP-content |
| ACF Flexible Content migration | WP-content |
| ACF Flexible to Elementor migration | WP-content |
| ACF to Elementor migration | WP-content |
| Migration playbook / procedure / script | meta |
| All-in-One WP Migration | WP-hosting |
| Subdomain migration | WP-hosting |
| URL-stable migration | WP-hosting |
| UpdraftPlus migration pattern | WP-hosting |
| Prisma 7 migration | Prisma-schema |
| Schema migration DROP COLUMN | Prisma-schema |
| `Migration 20260510122403_add_*` (timestamp prefix) | Prisma-schema |
| Canvas migration planning | doc-meta |
| wikilink migration | doc-meta |

## The 4 migration families

### 1. WP-content migration (page-builder swap)
**Goal:** Elementor ↔ Bricks ↔ Gutenberg with content preserved.

**Patterns:**
- **Naive migration** (anti-pattern): page-builder export/import → loses UI customisations
- **Mirror pipeline**: ACF Flexible Content → Bricks/Elementor templates (WP-CLI `post meta delete + add --format=json`)
- **WPML mirror** [[wpml-acf-elementor-multilingual-mirror]] → 3-step HU→EN mirror

**Safety protocol:**
1. **Pre-migration screenshot** of every page (page-by-page diff afterwards)
2. **Staging clone** FIRST — production is NOT the first target
3. **WP-CLI script** idempotent (safe to re-run)
4. **Rollback export** beforehand: `wp db export pre-migration.sql`

→ [[wp-acf-flexible-to-elementor-migration]] · [[wp-cli-bricks-postmeta-pattern]] · [[wpml-acf-elementor-multilingual-mirror]]

### 2. WP-hosting migration (host swap, subdomain)
**Goal:** WP install from one host to another, or production → staging clone.

**Patterns:**
- **All-in-One WP Migration** plugin — simple, but chunked above 2GB
- **UpdraftPlus pattern**: backup zips + manual `wp core download` if `wpcore.zip` is empty
- **URL-stable migration**: domain replacement `wp search-replace` + `siteurl`/`home`

**Safety protocol:**
1. **Hostinger LiteSpeed cache** 7-day image edge → `wp cache flush` NOT enough, filename rename ([[hostinger-updraftplus-staging-migration]])
2. **`wp search-replace --dry-run` FIRST** — see how many rows are affected
3. **DB serialised data** → NEVER `sed/awk` URL replacement, ALWAYS `wp search-replace`

→ [[hostinger-updraftplus-staging-migration]]

### 3. Prisma-schema migration (DB)
**Goal:** ORM schema change on production DB.

**Patterns:**
- **`prisma migrate dev`** — dev environment auto-apply
- **`prisma migrate deploy`** — production apply (NOT `dev`)
- **`Schema migration DROP COLUMN`** — production danger; backup beforehand
- **`Migration 20260510122403_add_*`** — timestamp-prefix MIGRATION_NAME convention

**Safety protocol:**
1. **`prisma migrate diff`** FIRST — dry-run SQL
2. **`pg_dump`** beforehand (production DB before every migration)
3. **DROP COLUMN preceded by RENAME** two-phase deploy (deploy → wait → drop)
4. **Prisma 7 migration** — `@prisma/adapter-pg` runtime swap included; staging first

**Anti-pattern:** `prisma migrate dev` on production → data loss (resets the DB).

→ [[prisma-compound-unique-null-quirk]] · [[prisma-seed-admin-edit-protected]]

### 4. Doc/URL migration (link update)
**Goal:** Obsidian wikilink rename, canvas restructure, URL redirect.

**Patterns:**
- **wikilink migration** — vault rename → Obsidian auto-renames every link
- **Canvas migration planning** — `.canvas` JSON manual editing
- **URL-stable migration** — old-URL → new-URL redirect table

**Safety protocol:**
1. **Git commit beforehand** — commit the Obsidian rename cascade separately
2. **301 redirect** for old URLs (SEO preservation)
3. **Vault-rename with a desktop Obsidian session open** is risky (active second editor → detached HEAD risk)

## Common cross-domain rules

1. **Backup beforehand** — in all 4 families: WP `wp db export`, Prisma `pg_dump`, hosting full-zip, vault `git commit`
2. **Idempotent script** — safe to re-run (Prisma migration timestamp-prefix is automatic; WP-CLI script you must write idempotently)
3. **Dry-run support** — `--dry-run`, `migrate diff`, `search-replace --dry-run` everywhere FIRST
4. **Staging first** — NEVER directly to production
5. **Rollback plan WRITTEN** — in every migration PR: how to revert
6. **Migration script git-tracked** — Prisma `prisma/migrations/`, WP separate `migrations/YYYY-MM-DD-<name>.sh`
7. **Verification step after** — count check, sample-row check, screenshot diff
8. **Lock the source** during migration — WP `wp maintenance-mode activate`, Prisma `pgbouncer` pause

## Anti-patterns

| Anti-pattern | Bug | Family |
|---|---|---|
| Production WP plugin "migrate now" button without backup | no rollback | WP-content |
| `sed -i 's/old.com/new.com/g'` on a WP DB dump | serialised length breaks | WP-hosting |
| `prisma migrate dev` on production | DB reset | Prisma |
| Page-builder export → import only | UI customisations lost | WP-content |
| Bulk vault-rename with a second editor active | detached HEAD, conflict cascade | Doc |

## Related

- [[hostinger-updraftplus-staging-migration]]
- [[wp-acf-flexible-to-elementor-migration]]
- [[wp-cli-bricks-postmeta-pattern]]
- [[wpml-acf-elementor-multilingual-mirror]]
- [[prisma-compound-unique-null-quirk]]
- [[prisma-seed-admin-edit-protected]]
- [[multi-layer-safety-gate]]
