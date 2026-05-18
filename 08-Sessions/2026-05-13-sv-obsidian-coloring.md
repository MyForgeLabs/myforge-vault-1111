---
name: sv-obsidian-coloring
type: session
project: sv-obsidian-coloring
status: closed
started: 2026-05-13T11:02+00:00
ended: 2026-05-13T11:06+00:00
agent: unknown
# B-3 eval fields (auto-backfilled, null = not yet evaluated)
eval_score: null
eval_critique: null
hallucination_flag: false
eval_l2_agreement: null
tags: ["#type/session", "#project/sv-obsidian-coloring"]
---

## Pre-loaded context

**Slug:** `sv-obsidian-coloring` — vault-meta / Obsidian-UX session. User-kérés: projekt-szín-kódolás Obsidian-ban hogy színesebb / felismerhetőbb legyen.

**Háttér:** 17 aktív projekt (02-Projects/), B-5 NB-sync most fejezte be. Vault Obsidian-config: 3 plugin (git, excalidraw, tasks), nincs még snippet vagy iconize. Graph.json `colorGroups: []` (üres).

**Bundle döntés:** plugin-mentes CSS snippet (`cssclasses` frontmatter alapján) + tag-alapú graph color-groups. Mac-oldalon `3d-graph` community plugin opcionális.

## Cél


## Events


- 11:03 — Obsidian project-color bundle alkalmazva: CSS snippet (project-colors.css 7 cluster-color: KGC kék / Foxxi mint / MyForge lila / Petanque narancs / Research cián / Rojt bor / SV magenta) + 17/17 projekt-fájl cssclasses: [proj-X] frontmatter + 17 .bak.20260513-colors backup + graph.json colorGroups 7 szabály (path: OR tag:#project/<slug>, showTags=true) + appearance.json enabledCssSnippets=['project-colors']. CSS: title-bar 8px color-marker, inline-title color, H1 left-border accent, tab-header inset shadow. Mac-oldalon: Obsidian reload (settings → reload theme or restart). 3d-graph plugin (community) install opcionális Mac-oldali wow-factor-hoz.
## Summary

**Obsidian projekt-szín-kódolás bundle** — 1 commit, ~10 perc, plugin-mentes.

**Új vault-fájl:**
- `.obsidian/snippets/project-colors.css` — CSS variábili 7 cluster-color + title-bar marker + inline-title szín + H1 left-border + tab-header inset shadow

**Módosított vault-fájlok:**
- 17 `02-Projects/*.md` — `cssclasses: [proj-X]` frontmatter (+17× `.bak.20260513-colors` backup)
- `.obsidian/graph.json` — 7 colorGroup (`(path:"02-Projects/foo") OR (tag:#project/foo)` query-szintaxis), `showTags: true`
- `.obsidian/appearance.json` — `enabledCssSnippets: ["project-colors"]`

**7 cluster-color mapping:**

| Cluster | Slug-ok | Szín | RGB-int |
|---|---|---|---|
| 🏗️ KGC | kgc-erp, kgc-berles, kgshop-bluebird, kgc-marketing, kgc-kivetitok, kgc-tv-cms | `#3b82f6` blue | 3900150 |
| 🦷 Foxxi | foxxi, foxxi-email-arhivum | `#10b981` mint | 1096065 |
| 🤖 MyForge | myforge-dashboard, koko, mfl-bot | `#a855f7` purple | 11032055 |
| 🎯 Petanque | petanque-kisgeparuhaz, mapesz | `#f97316` orange | 16347926 |
| 🔬 Research | teszt-eu, robbantott-kereso | `#06b6d4` cyan | 440020 |
| ☕ Rojt és Bojt | rojtesbojt | `#9f1239` wine | 10424889 |
| 🧠 SV-meta | superintelligent-vault | `#d946ef` magenta | 14239471 |

**Aktiválás Mac-oldalon:** Obsidian → Settings → Appearance → Reload theme (vagy app restart). A snippet + appearance.json + graph.json mind git-tracked, Obsidian-Git plugin pull-on a Mac is megkapja.

**3D Graph opcionális:** `obsidian-3d-graph` community plugin — Mac-oldalon manuális install (Settings → Community plugins → Browse → 3D Graph).

## Learnings → memória

**1. Obsidian `cssclasses` frontmatter — plugin-mentes per-file styling** — A `cssclasses: [class-name]` YAML-mező az adott dokumentum body-classlist-jébe injektál CSS-class-t Reading + Source mode-ban egyaránt. Custom CSS targetelhet `body.proj-foxxi .inline-title`-t, `:has()` selector-rel a `.workspace-leaf:has(.proj-foxxi)` is működik. **Reusable:** plugin-mentes alternatíva az Iconize / File Color community plugin-ekhez.

**2. Obsidian graph.json `colorGroups` query-szintaxis** — A `path:` és `tag:` operátorok OR-kombinálhatók (`(path:"02-Projects/foxxi") OR (tag:#project/foxxi)`) — első egyezés-szín win-eling. Plus `showTags: true` enableli a tag-nodes-t a graph-on, ami visual-rich. RGB-int decimal-formátum (0xRRGGBB → int). **Programatikusan írható** — JSON-edit script-tel batch-deploy 7 cluster-rule.

## Next session

1. **Mac-oldali verifikáció** — Obsidian reload, ellenőrizd hogy a 7 szín tényleg látszik a title-bar / inline-title / graph-node / tab-header-en. Visszajelzés ha valamelyik selector nem ér célt (Obsidian-version-specifikus class-nevek néha változnak).
2. **3D-graph plugin install** — Mac-oldalon `Settings → Community plugins → Browse → 3D Graph` → install. Ugyanazokat a colorGroups beállításokat manuálisan kell beállítani a plugin saját UI-ján (a `graph.json` NEM örökli a 3D-plugin-be).
3. **File-explorer color** — opcionális 2. lépés ha az `inline-title` szín nem elég vizuális. `obsidian-iconize` plugin emoji-prefix-et tud per-folder, plus per-file CSS-class-szal is működik.
4. **Tag-color community plugin** — ha a tag-szín (`#project/foxxi` chip) is színes legyen Reading mode-ban, akkor `colorful-tag` community plugin szükséges (külön Mac-install).

## Propagation log

**2026-05-13 11:05 — Auto-propagation (user-confirmed):**

- **L1+L2** (Obsidian color-coding plugin-mentes pattern) → NEW [[11-wiki/obsidian-color-coding]] (~210 sor playbook: cssclasses + CSS snippet példák + graph.json colorGroups + RGB-int kalkuláció + programatikus deploy script + community plugin alternatívák Iconize/Colorful-tag/3D-graph/File-color + Peti-vault 17/7-cluster élő példa + backout)

**Új vault-fájlok (2):**
- `.obsidian/snippets/project-colors.css`
- `11-wiki/obsidian-color-coding.md`

**Módosított vault-fájlok (3 + 17):**
- `.obsidian/graph.json` — colorGroups 7 cluster
- `.obsidian/appearance.json` — enabledCssSnippets
- 17 db `02-Projects/*.md` — cssclasses frontmatter (+17 `.bak.20260513-colors` backup)

