---
name: wp-cli-shared-db-export-fallback
type: wiki
tags: ["#topic/wordpress", "#topic/hostinger", "#topic/backup"]
created: 2026-05-15
updated: 2026-05-15
---

# `wp db export` Hostinger shared-en silent fail → mysqldump direkt

Hostinger shared hosting (de-fra-web1813 AlmaLinux 9.7, WP-CLI 2.12.0, PHP 8.2.30) sajátossága: `wp db export <file>` és `wp db export -` is **exit 0**, üres output, semmilyen hiba. A fájl vagy 20 byte (csak gzip-header) vagy nem jön létre. Debug `--debug` flag-gel sem mutat hibát.

## Megbízható alternatíva — `mysqldump` direkt

```bash
cd ~/domains/<site>/public_html

DB_NAME=$(wp config get DB_NAME --skip-themes --skip-plugins)
DB_USER=$(wp config get DB_USER --skip-themes --skip-plugins)
DB_PASS=$(wp config get DB_PASSWORD --skip-themes --skip-plugins)
DB_HOST=$(wp config get DB_HOST --skip-themes --skip-plugins)

mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" 2>/dev/null \
  | gzip > ~/backups/${site}-pre-update-$(date +%Y%m%d-%H%M%S).sql.gz
```

A `wp config get` segéd-parancsok megbízhatóak — csak az export-pipeline tört. A `mysqldump` clientet a Hostinger telepítve adja (`mariadb-client 11.8.6`).

## Verify

```bash
ls -la ~/backups/<site>-pre-update-*.sql.gz
# >= 100KB várt egy normál WP-DB-re. 20 byte = silent-fail.
zcat ~/backups/<file>.sql.gz | head -20  # SQL-header látszik
```

## Reusable helper

```bash
wp_safe_db_export() {
  local site=$1
  cd ~/domains/$site/public_html || return 1
  local DB_NAME=$(wp config get DB_NAME --skip-themes --skip-plugins)
  local DB_USER=$(wp config get DB_USER --skip-themes --skip-plugins)
  local DB_PASS=$(wp config get DB_PASSWORD --skip-themes --skip-plugins)
  local DB_HOST=$(wp config get DB_HOST --skip-themes --skip-plugins)
  local OUT=~/backups/${site}-$(date +%Y%m%d-%H%M%S).sql.gz
  mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" 2>/dev/null | gzip > "$OUT"
  echo "  backup: $(ls -la "$OUT" | awk '{print $5}') bytes → $OUT"
}
```

## Hol jelent meg

2026-05-15 szerver-update session — 5 shared-WP frissítés frankpanama.com-on `wp db export -` 20-byte fájlt írt, frankpanama.store-tól már `mysqldump` használt. Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Kapcsolódó

- [[11-wiki/wp-elementor-template-conflicts]]
- [[03-Hosts/Shared Hosting (Cloud Professional)]]
