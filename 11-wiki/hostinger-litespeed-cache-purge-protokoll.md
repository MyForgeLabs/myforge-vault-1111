---
name: hostinger-litespeed-cache-purge-protokoll
description: Hostinger shared-hosting LSCACHE 3-rétegű cache trap - wp cache flush NEM érvényteleníti, csak wp litespeed-purge all működik, és csak ha a plugin AKTÍV. 15 session-evidence (foxxi/rojtesbojt/kgc-marketing) cross-projekt failure-mode pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/wordpress", "#topic/hostinger", "#topic/cache", "playbook"]
status: stable
session-evidence: 15
---

# Hostinger LiteSpeed cache-purge protokoll

## A probléma — háromszor 15 session-ben elcsapott

Hostinger shared-hosting weboldalakon (example-foxxi.local, example-rojt.local, kgc-marketing-domain-ek) **változás-frissítések nem látszanak a frontend-en**, miközben a backend-en (wp-admin) már él az új tartalom. Standard `wp cache flush` + `wp w3-total-cache flush all` **NEM oldja meg** — a LiteSpeed server-szintű cache 7 napos default max-age-szel tartja a HTML-snapshot-ot.

### A 3 cache-réteg

| Réteg | Mit cache-el | `wp cache flush` érinti? | Helyes purge |
|---|---|---|---|
| WordPress object cache (Redis/Memcached dropin) | DB-query-result, post-meta, options | ✅ igen | `wp cache flush` |
| W3 Total Cache plugin | Page-cache, minified CSS/JS, browser-cache headers | ❌ csak ha aktivált | `wp w3-total-cache flush all` |
| **🔴 LiteSpeed server-szintű** | A teljes renderelt HTML — **7-nap max-age** | ❌ NEM | **`wp litespeed-purge all`** |

## Diagnosztika (előtt-után verifikálás)

```bash
curl -sI 'https://<staging-vagy-prod>/' | grep -iE "x-litespeed|x-hcdn-cache"
# x-litespeed-cache: hit  → SERVER cache hit (régi snapshot)
# x-litespeed-cache: miss → friss render
```

Ha `hit`, és a változás nem látszik → LSCACHE-rétegben régi snapshot. Ha `miss` → biztos hogy nem LSCACHE-trap; nézz tovább (browser-cache, CDN, plugin-page-cache).

## A purge-protokoll (a litespeed-cache plugin INAKTÍV state-jén is)

A `wp litespeed-purge` parancs csak akkor elérhető, ha a plugin AKTÍV. **De a server-szintű cache attól még működik** (a `.htaccess`-ben az `LSCACHE` direktíva). 3 lépés:

```bash
ssh hostinger 'cd ~/domains/<site>/public_html && \
  wp plugin activate litespeed-cache && \
  wp litespeed-purge all && \
  wp plugin deactivate litespeed-cache'
```

**Output:** `Success: Mindenkit megtisztítottunk!` jelzi a sikeres LSCACHE-flush.

> [!warning] Plugin-aktivátum-reaktiváció
> Az activate → purge → deactivate sorrend kötelező, mert az aktív LiteSpeed-cache plugin önmaga is **TOVÁBBI cache-réteget** ad (front-end optimization, image-lazy-load), ami a klienseknek lassabb. A production-state mindig **plugin INAKTÍV** (csak a server-szintű cache fut).

## Image-rename workaround (nem-flush-fallback)

Ha a LSCACHE-trap konkrétan **képek nem frissülnek** (foxxi-CTA, rojtesbojt-product, KGC-product-mockup): a flush helyett **fájlnév-rename** mindig azonnal él (cache-key változik):

```bash
# Manuál:
cd ~/domains/<site>/public_html/wp-content/uploads/2026/05/
cp logo-v3.png logo-v4.png  # új név
# wp-content/themes/foxxi/template-parts/header.php-ban update path

# Build-script automatikus (file-fingerprint):
img-fingerprint.sh logo.png  # → logo.7a2c.png mtime-hash-szel
```

A **file-fingerprint pattern** (mtime-hash a fájlnévben) build-process-ben automatizálható → minden CSS/JS/img build-időben új-név → cache-trap megszűnik. Ezt javasolt minden Hostinger-en futó projektnél bevezetni.

## Hosztingfél-stratégia (long-term)

A 15 session-density indokolja a hosting-stratégia újragondolását:

| Opció | Mikor jó | Mikor problémás |
|---|---|---|
| **Hostinger marad** + LSCACHE-protokoll | Minimal-traffic ügyfél, "egyszer-egyszer frissül" oldalak | Aktív content-update workflow (foxxi-blog, KGC-products) |
| **Caddy VPS** (mint 6 domain 0 incidens) | Új projektek + nagyobb traffic | Költség-érzékenység |
| **Hibrid**: Hostinger + build-time fingerprint | Meglévő ügyfél-projektek | Komplex deploy-pipeline |

Lásd: [[../05-Memory/feedback_caddy_over_traefik]] — Caddy mint default reverse-proxy.

## Cross-referenciák

- **15 session-evidence** (sorrend session-date szerint): 2026-04-30 foxxi, 2026-05-02 foxxi-weboldal, 2026-05-03 foxxi-en-translation, 2026-05-04 foxxi-seo-research, 2026-05-06 foxxi-weboldal, 2026-05-10 foxxi-weboldal, 2026-05-11 kinda-project, 2026-05-13 rojt-s-bojt, és további 7+
- [[../05-Memory/Infrastructure#Hostinger LiteSpeed cache]] — alap-pointer (most ez a wiki replaces-eli teljes)
- [[wp-elementor-template-conflicts]] — kapcsolódó WP-failure-pattern
- [[wpml-acf-elementor-multilingual-mirror]] — gyakran ugyanezen projekteken landol

## Új projekt-Day-0 checklist

Hostinger-en futó új WP-projektnél (foxxi/rojtesbojt/KGC-mintát követve) Day 0:

- [ ] LSCACHE diagnostic-curl rögzítve (`x-litespeed-cache` baseline)
- [ ] `wp litespeed-purge all` activate → purge → deactivate sequence dokumentálva README-ben
- [ ] Image-fingerprint build-script `package.json` `scripts.build:img`-ben
- [ ] Staging-prod LSCACHE-diff check `vault-cache-audit` script Week N (skeleton-todo)

## Kapcsolódó

- [[../05-Memory/Infrastructure]] — alapinfra pointer
- [[wp-elementor-template-conflicts]] — komplementer WP-failure
- [[wpml-acf-elementor-multilingual-mirror]] — gyakran ugyanazon foxxi-projekteken
- [[../02-Projects/foxxi]] / [[../02-Projects/rojtesbojt]] / [[../02-Projects/kgc-marketing]] — host-projekt-ek
