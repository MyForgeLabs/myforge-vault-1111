---
name: wp-elementor-bricks-json-escape-trap
description: WordPress _elementor_data / _bricks_data postmeta programozott írásakor a wpdb-update inconsistent slash-handling miatt Unicode-escape elveszik (é → u00e9), invalid JSON-t ad ami eltöri a frontend builder rendert. Foxxi + rojt-és-bojt projekteken 4-5 session-evidence
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/wordpress", "#topic/elementor", "#topic/bricks", "#topic/json", "playbook"]
status: stable
session-evidence: 5
source: vault-meta NotebookLM Q2-#6 synthesis
---

# WP Elementor + Bricks JSON Unicode-escape trap

## A probléma

WordPress builder-meta-fieldek (`_elementor_data`, `_bricks_data`, `_bricks_page_content_2`) **programozottan való frissítésekor** (pl. WPML-tükör, ACF→Elementor migrációs script, multi-language sync) **a wpdb-update + update_post_meta inconsistent slash-handling** miatt a JSON-string Unicode-escape karaktere elveszik:

```
Helyes:    "title":"Üdvözöljük"  → JSON-encode: "title":"Üdvözlöjk"
Trap:      Ü → u00dc (a leading backslash törlődik)
Eredmény:  Invalid JSON → Elementor/Bricks frontend renderer NEM render
```

**Tünet**: a frontend builder kép nem rajzolódik, "Loading template..." stuck, console-ban `JSON.parse SyntaxError`. wp-admin-ban a builder NEM nyithat meg.

## Forrás-pattern (5-session-evidence)

1. **2026-04-30 foxxi** — első előfordulás, multilingual mirror script
2. **2026-05-02 foxxi-weboldal** — ismétlődés ACF→Elementor migrációban
3. **2026-05-08 rojt-s-bojt-weboldal** — Bricks-postmeta verzió ugyanazon traphez
4. **2026-05-13 rojt-s-bojt** — wp-cli batch postmeta-update közben
5. **2026-05-13 sv-week2-extend** — wpml-acf-elementor-multilingual-mirror playbook test

## Miért történik

WordPress `wpdb::update()` és `update_post_meta()` **eltérő slash-handling**:

| Művelet | Slash-behavior | Eredmény |
|---|---|---|
| `update_post_meta($id, '_elementor_data', $json_string)` | **wp_slash() implicit** | `é` → `\\u00e9` → DB-ben kettős-escape |
| `$wpdb->update(..., ['meta_value' => $json])` | **NEM slash-elve** | `é` → DB-ben `u00e9` (leading-backslash törlés) |
| `wp_unslash()` reverse | Csak `wp_slash`-elt input-ra | Inkonzisztens, ha `wpdb`-rőljön |

A wp-cli `wp post meta update --format=json` szintén a `wpdb::update`-et hívja → ugyanaz a trap.

## Diagnosztika

```bash
# JSON érvényesség check ELŐTT és UTÁN
wp post meta get <post_id> _elementor_data | python3 -c "import json,sys; json.loads(sys.stdin.read()); print('OK')"
# Output: OK → érvényes JSON; SyntaxError → escape-trap aktivált
```

```bash
# Direkt SQL-check
wp db query "SELECT SUBSTRING(meta_value, 1, 200) FROM wp_postmeta WHERE post_id=<id> AND meta_key='_elementor_data';"
# Ha a stringben "u00" lát, és NEM "\u00" → trap aktivált
```

## Helyes implementáció (3 minta)

### A) `update_post_meta` egyszerű string
```php
// HELYES — wp_slash() NEM kell, mert update_post_meta() implicit
update_post_meta($post_id, '_elementor_data', $json_string);
```

### B) `wpdb::update` raw SQL
```php
// HELYES — wp_slash() ELŐTT manuálisan
$wpdb->update(
    $wpdb->postmeta,
    ['meta_value' => wp_slash($json_string)],  // ← KRITIKUS
    ['post_id' => $post_id, 'meta_key' => '_elementor_data']
);
```

### C) wp-cli batch (megoldva 2026-05-13 rojt-s-bojt)
```bash
# HELYES — wp post meta delete + add --format=json (NEM update)
wp post meta delete <id> _elementor_data
wp post meta add <id> _elementor_data "$(cat data.json)" --format=json
# Az "add --format=json" wp-cli újabb verziókban (2.7+) helyes slash-handlinget alkalmaz
```

### D) Bricks-specifikus (`element` típus)
```bash
# Bricks builder element-postmeta JSON-array
wp post meta add <id> _bricks_page_content_2 "$(cat bricks.json)" --format=json
# A wiki [[wp-cli-bricks-postmeta-pattern]] alapján: "html" element "code" helyett
```

## Recovery (ha már broken-state)

Ha a DB-ben már escape-trap-elt JSON van:

```python
# Python regex-recovery
import re
broken_json = '...'  # a DB-ből kiszedett meta_value
fixed = re.sub(r'(?<!\\)u([0-9a-fA-F]{4})', r'\\u\1', broken_json)
# Verifikálás:
import json; json.loads(fixed)  # → ha OK, írjuk vissza
```

Aztán `update_post_meta()`-vel (NEM wpdb-direct) visszaírni → instant fix a frontend renderben.

## Atomic-write pattern (greenfield ajánlott)

Új migráció / sync-script Day 0-tól:

```php
function safe_elementor_update($post_id, $data_array) {
    // 1. encode UTF-8 unicode-escape KÉNYSZERÍTÉSSEL
    $json = json_encode($data_array, JSON_UNESCAPED_UNICODE);  // explicit, NEM default
    
    // 2. update_post_meta() implicit wp_slash — biztonságos
    $result = update_post_meta($post_id, '_elementor_data', $json);
    
    // 3. POST-VERIFY: olvasd vissza és JSON.parse
    $verify = get_post_meta($post_id, '_elementor_data', true);
    json_decode($verify, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        error_log("ELEMENTOR ESCAPE TRAP DETECTED: $post_id");
        return false;
    }
    return $result;
}
```

A **POST-VERIFY** lépés a legfontosabb — az inkonzisztens slash-handling akkor manifesztálódik amikor visszaolvasod.

## Mikor érdemes alkalmazni a wiki-t

- ✅ Új multilingual WP-projekt (WPML+ACF+Elementor mirror)
- ✅ ACF→Elementor migration script (foxxi-pattern)
- ✅ Bricks-postmeta batch-update (wp-cli)
- ✅ Multi-site WP-content-sync (example-foxxi.local staging → prod)
- ❌ Single-language standalone WP-page-edit (admin-UI normal flow)

## Kapcsolódó

- [[wpml-acf-elementor-multilingual-mirror]] — 3-lépéses mirror playbook (gyakori trap-forrás)
- [[wp-elementor-template-conflicts]] — komplementer WP-failure-pattern
- [[wp-cli-bricks-postmeta-pattern]] — Bricks-specific add vs update
- [[hostinger-litespeed-cache-purge-protokoll]] — gyakran ugyanazon projekteken
- [[../02-Projects/foxxi]] / [[../02-Projects/rojtesbojt]] — host-projektek
- [[../06-Audits/2026-05-18 vault-meta NotebookLM cross-projekt synthesis]] — Q2-#6 forrás-extrakt
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[wpml-multilingual-pattern-family]] (sem-rokon, score=0.48)
