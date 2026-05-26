---
name: Fallback-pattern family taxonomy
type: wiki
lang: en
translated_from: fallback-pattern-family-taxonomy
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/fallback, taxonomy, evergreen, resilience]
---

# Fallback-pattern family taxonomy

> [!info] TL;DR
> Many distinct "fallback" concepts surface in real codebases, but there is rarely a **single taxonomy** that shows they all come from **5 different pattern families**. This wiki introduces the taxonomy + a selection decision tree.

## Cluster members (representative)

| Concept | Source layer | Family (below) |
|---|---|---|
| WPML language-aware fallback | i18n | Translation |
| Translation fallback | i18n | Translation |
| Render shape fallback | UI | Render |
| Suspense fallback | UI | Render |
| Theme header.php fallback | UI | Render |
| Footer ACF Options fallback | UI | Render |
| ended-listener loop fallback | DOM-event | Browser-event |
| canplay event without guard flag | DOM-event | Browser-event |
| Three-level fallback JSON decode | parser | Parse |
| String() fallback (gray-matter date) | parser | Parse |
| stripslashes() fallback | parser | Parse |
| fallback regex | parser | Parse |
| proxy fallback strategy | infra | Infra |
| mysqldump fallback | infra | Infra |
| Offline fallback (PWA) | infra | Infra |
| old kernel fallback | infra | Infra |
| silent fallback (URL-param) | UX | Anti-pattern |
| ADMIN_PASSWORD hardcoded fallback | security | Anti-pattern |
| marker-pattern fallback (NotebookLM CLI) | parser | Parse |

## The 5 fallback families

### 1. Translation fallback (i18n)
**Pattern:** if content is missing in the requested language → fall back to the source language (or default locale), **NOT** an empty page.

- `WPML language-aware fallback` — `wpml_object_id($id, 'page', true)` 3rd arg = allow-fallback
- `Translation fallback` — generic i18n pattern

**Selection rule:** always with an **explicit allow-fallback flag**, because silent-fallback ⇒ duplicated EN pages with HU content and SEO disaster.

### 2. Browser-event fallback (DOM / video / network)
**Pattern:** browser events fire NON-deterministically (`canplay`, `loadedmetadata`) → guard flag + timeout fallback.

- `ended-listener loop fallback` — `v.currentTime=0 + v.play()` if `ended` event didn't fire
- `canplay event without guard flag` → race condition
- `video oncanplay guard pattern` — `readyFired` flag

**Selection rule:** in event-driven code, **always** include an N-second timeout fallback + idempotent restart.

### 3. Render fallback (UI missing data)
**Pattern:** UI component does not render if data is missing → either skeleton, Suspense, or gracefully-empty.

- `Suspense fallback` — React `<Suspense fallback={...}>`
- `Theme header.php fallback` — WP child-theme missing → parent-theme
- `Footer ACF Options fallback` — empty ACF field → coded default
- `Render shape fallback` — polymorphic UI with dynamic shape

**Selection rule:** skeleton > spinner > empty-DIV. For SEO, the fallback content should be visible in SSR too.

### 4. Parse fallback (multi-strategy decode)
**Pattern:** primary parser may fail → secondary, then tertiary parser on the same string.

- `Three-level fallback JSON decode` — `json.loads()` → ujson → safe-eval
- `String() fallback` — `instanceof Date ? toISOString() : String(v)` (gray-matter)
- `stripslashes() fallback` — escaped input restore
- `fallback regex` — strict parser fail → permissive regex
- `marker-pattern fallback` — NotebookLM API JSON marker → text-scan

**Selection rule:** **always log** which layer caught it; if N1 always fires, N2/N3 is dead code.

### 5. Infra fallback (service degradation)
**Pattern:** primary service down → secondary path.

- `proxy fallback strategy` — Next.js API proxy: primary upstream → backup
- `mysqldump fallback` — native mysqldump fail → wp-cli export
- `Offline fallback` — PWA service-worker offline page
- `old kernel fallback` — boot-loader fallback-kernel stanza

**Selection rule:** infra fallback should be **stateful** (degraded-mode indicator in the UI), NOT silent.

## Anti-pattern: silent fallback

| Pattern | Why anti-pattern |
|---|---|
| `silent fallback` (URL-param plus-decode) | `?age=50+` → `"50 "` user has no idea what happened |
| `ADMIN_PASSWORD hardcoded fallback` | env-var missing → hardcoded fallback ⇒ security leak |

**Rule:** fallback triggers MUST go to telemetry (log/Sentry/audit-md). "Silent" only acceptable if the user experience does not degrade.

## Reusable rules (cross-cluster)

1. **Explicit-allow flag**: i18n + parse-fallback enabling is an explicit boolean, not-default
2. **Timeout parameter**: event-fallback and infra-fallback ALWAYS have a `timeoutMs` parameter, not hardcoded
3. **Audit log**: every fallback trigger emits `console.warn` or structured-log so the P95-percentile is measurable per layer
4. **Degraded UX indicator**: if the fallback content is noticeable to the user, MARK it (badge, faded colour)
5. **Dead-code review**: a fallback layer older than 3 months that never fired → delete

## Related

- [[wpml-acf-elementor-multilingual-mirror]]
- [[digital-signage-player-gotchas]]
- [[gray-matter-date-coerce]]
- [[url-param-plus-decode-quirk]]
- [[demo-fallback-readonly-guard]]
- [[notebooklm-cli-gotchas]]
- [[nextjs-search-params-force-dynamic]]
- [[guard-pattern-family-taxonomy]]
