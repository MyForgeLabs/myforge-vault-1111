---
name: Fallback-pattern család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/fallback, taxonomy, evergreen, resilience]
---

# Fallback-pattern család taxonomy

> [!info] TL;DR
> A vault-ban **28 különálló Concept** és **33+ wiki-említés** beszél „fallback"-ről, de eddig **nem volt egy közös taxonómia** ami megmutatná, hogy a sokféle „fallback" valójában **5 különböző mintázat-családból** ered. Ez a wiki bevezeti a taxonómiát + a választási döntési-fát.

## Cluster-members (vault Concept-corpus)

| Concept | Forrás-réteg | Család (lásd lent) |
|---|---|---|
| WPML language-aware fallback | wiki/wpml-acf-elementor-multilingual-mirror | Translation |
| WPML language-aware render fallback | wiki | Translation |
| Translation fallback | session | Translation |
| ended-listener loop fallback | wiki/digital-signage-player-gotchas | Browser-event |
| canplay event without guard flag | wiki | Browser-event |
| video oncanplay guard pattern | wiki | Browser-event |
| Render shape fallback | session | Render |
| Suspense fallback | wiki/nextjs-search-params-force-dynamic | Render |
| Theme header.php fallback | wiki | Render |
| Footer ACF Options fallback | session | Render |
| Three-level fallback JSON decode | wiki | Parse |
| String() fallback | wiki/gray-matter-date-coerce | Parse |
| stripslashes() fallback | session | Parse |
| fallback regex | session | Parse |
| proxy fallback strategy | wiki | Infra |
| mysqldump fallback | session | Infra |
| Offline fallback | wiki | Infra |
| old kernel fallback | session | Infra |
| ADMIN_PASSWORD hardcoded fallback | session | Anti-pattern |
| silent fallback | wiki/url-param-plus-decode-quirk | Anti-pattern |
| group fallback logic | session | Domain |
| demo-fallback readonly guard | wiki | Domain |
| marker-pattern fallback | wiki/notebooklm-cli-gotchas | Parse |
| Fallback feature | session | meta |

## A 5 fallback-család

### 1. Translation fallback (i18n)
**Mintázat:** ha a kért nyelven nincs tartalom → vissza-esés a forrás-nyelvre (vagy default-locale-ra), **NEM** üres oldal.

- `WPML language-aware fallback` — `wpml_object_id($id, 'page', true)` 3. arg = fallback-ra-engedély
- `Translation fallback` — generikus i18n minta

**Választási szabály:** mindig **explicit allow-fallback flag**-gel, mert silent-fallback ⇒ duplikált EN-oldalakon HU-tartalom és SEO katasztrófa.

### 2. Browser-event fallback (DOM/video/network)
**Mintázat:** browser event NEM-deterministically firenelődik (`canplay`, `loadedmetadata`) → guard-flag + timeout-fallback.

- `ended-listener loop fallback` — `v.currentTime=0 + v.play()` ha `ended` event nem jött
- `canplay event without guard flag` → race-condition
- `video oncanplay guard pattern` — `readyFired` flag

**Választási szabály:** event-driven kódban **MINDIG legyen** N-másodperces timeout-fallback + idempotens-újraindítás.

### 3. Render fallback (UI hiányzó-adat)
**Mintázat:** UI-komponens nem renderel ha az adat hiányzik → vagy skeleton, vagy Suspense, vagy gracefully-empty.

- `Suspense fallback` — React Suspense `<Suspense fallback={...}>` 
- `Theme header.php fallback` — WP child-theme hiányzik → parent-theme
- `Footer ACF Options fallback` — ha ACF-mező üres → kódolt default
- `Render shape fallback` — sokrétű UI-elem dinamikus shape-pel

**Választási szabály:** skeleton > spinner > üres-DIV. SEO-szempontból a fallback-content látható-legyen SSR-ben is.

### 4. Parse fallback (multi-strategy decode)
**Mintázat:** primary parser fail-elhet → másodlagos, majd harmadlagos parser ugyanazon stringre.

- `Three-level fallback JSON decode` — `json.loads()` → ujson → eval-with-safe
- `String() fallback` — `instanceof Date ? toISOString() : String(v)` (gray-matter)
- `stripslashes() fallback` — escape-elt input visszafejtés
- `fallback regex` — strict-parser fail → permissive-regex
- `marker-pattern fallback` — NotebookLM API JSON-marker → text-scan

**Választási szabály:** **mindig log-old** melyik réteg fogta el; ha N1 mindig fut, N2/N3 holt-kód.

### 5. Infra fallback (service degradáció)
**Mintázat:** primary service down → secondary path.

- `proxy fallback strategy` — Next.js API proxy: primary upstream → backup
- `mysqldump fallback` — natív mysqldump fail → wp-cli export
- `Offline fallback` — PWA service-worker offline-page
- `old kernel fallback` — boot-loader fallback-kernel-stanza

**Választási szabály:** infra-fallback **state-ful** legyen (degraded-mode-jelzés a UI-ban), NEM silent-fallback.

## Anti-pattern: silent fallback

| Pattern | Miért anti-pattern |
|---|---|
| `silent fallback` (url-param-plus-decode) | `?age=50+` → `"50 "` user nem-tudja-mi-történt |
| `ADMIN_PASSWORD hardcoded fallback` | env-var hiányzik → kódolt fallback ⇒ security-leak |

**Szabály:** fallback-trigger MINDIG menjen telemetry-be (log/Sentry/audit-md). „Silent" csak akkor jó, ha a user-experience nem-degrad.

## Reusable szabályok (cross-cluster)

1. **Explicit-allow flag**: i18n + parse-fallback engedélyezés explicit boolean, nem-default
2. **Timeout-paraméter**: event-fallback és infra-fallback MINDIG legyen `timeoutMs` paraméter, nem-hard-coded
3. **Audit-log**: minden fallback-trigger `console.warn` vagy structured-log, hogy P95-percentile mérhető legyen melyik réteg fut
4. **Degradált UX-jelzés**: ha a fallback-content user-szempontból észrevehető, JELEZD (badge, halvány-szín)
5. **Holt-kód-revízió**: 3 hónapnál régebbi fallback-réteg, ami sosem futott → töröld

## Kapcsolódó

- [[wpml-acf-elementor-multilingual-mirror]]
- [[digital-signage-player-gotchas]]
- [[gray-matter-date-coerce]]
- [[url-param-plus-decode-quirk]]
- [[demo-fallback-readonly-guard]]
- [[notebooklm-cli-gotchas]]
- [[nextjs-search-params-force-dynamic]]
- [[guard-pattern-family-taxonomy]]
