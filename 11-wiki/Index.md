---
name: wiki Index
type: index
tags: ["#type/index", "wiki"]
created: 2026-04-23
updated: 2026-05-08
---

# 11-wiki/

**Desztillált, saját szavakkal átírt tudás.** Karpathy LLM-Wiki minta szerinti **wiki-réteg** — evergreen, AI-agent-kompatibilis. A források a [[10-raw/Index|10-raw/]]-ban maradnak referenciának.

## Bejegyzések — vault-design

| Bejegyzés | Mit fed le |
|-----------|------------|
| [[11-wiki/Karpathy-LLM-Wiki-pattern]] | Andrej Karpathy 2026-os LLM Wiki mintája. raw/ + wiki/ + agent-vault hármas réteg. Compilation > retrieval. |
| [[11-wiki/Johnny-Decimal-prefix]] | Mappa-prefix konvenció (00-Meta, 01-Daily, …). Miért és hogyan. |
| [[11-wiki/11.11-session-protokoll]] | A `/11.11*` parancs-család és a session-fájl séma. Crystallization workflow. |
| [[11-wiki/Kepano-File-over-App-filozofia]] | Steph Ango (kepano) "File over App" elve. Markdown szövegréteg, AI-agent kompatibilis. |
| [[11-wiki/agent-vault-setup-playbook]] | Step-by-step telepítési doksi új gépre (Mac + VS Code Claude Code): vault sablon, 3-agent symlink, 4 obsidian-skill, 11.11 scriptek path-patch, launchd jobs, smoke test, troubleshooting. |
| [[11-wiki/superintelligent-vault-research]] | 8-tengelyű evolúciós research master index (Memory / RSI / Multi-agent / Tool / Crystallization / World-model / Eval / NotebookLM). Phase A + A+ + B 8 sprint-ADR. |
| [[11-wiki/notebooklm-cli-gotchas]] | NotebookLM CLI 8 quirks: `--json` empty-ID, explicit `-n` flag, marker-fallback, `--mode deep --no-wait` aszinkron, source-limit, multi-agent szekvenciális > párhuzamos, cross-vault védelem. |
| [[11-wiki/sv-01-memory-architecture]] · [[11-wiki/sv-02-recursive-self-improvement]] · [[11-wiki/sv-03-multi-agent-orchestration]] · [[11-wiki/sv-04-tool-composition]] · [[11-wiki/sv-05-crystallization-automation]] · [[11-wiki/sv-06-world-model-knowledge-graph]] · [[11-wiki/sv-07-continuous-evaluation]] · [[11-wiki/sv-08-notebooklm-cognitive-layer]] | 8 tengely Phase A + A+ wiki-cikkek (2900+ sor, ~4800 forrás-bázis NotebookLM-en) |

## Bejegyzések — projekt-specifikus playbookok

| Bejegyzés | Mit fed le |
|-----------|------------|
| [[11-wiki/foxxi-design-system]] | Foxxi design system playbook |
| [[11-wiki/wp-acf-flexible-to-elementor-migration]] | WP ACF Flexible Content → Elementor migrációs receptúra |
| [[11-wiki/wp-elementor-template-conflicts]] | Elementor template-conflict pattern-ek (10 pattern: theme-hero, MEDIA condition, JSON dupla-escape, save-pipeline-skip, gettext fallback, Unicode-strip, WPML silent revert, wpdb wp_slash, Elementor-preview detect, render-cache invalidation) |
| [[11-wiki/wpml-acf-elementor-multilingual-mirror]] | 3-lépéses HU→EN tükör-fordítási pipeline (mirror + ACF lookup + szótár-csere) |
| [[11-wiki/notebooklm-seo-competitor-research-pattern]] | NotebookLM SEO competitor research workflow (17×7 source-kérdés, ~60-90 perc, foxxi-projekt validation) |
| [[11-wiki/hungarian-fuzzy-search]] | Magyar accent + typo-toleráns search algoritmus (accent-map + Levenshtein + score) — KGC-bérlés `/api/search` minta, reusable Foxxi/example-balance.local-ra |
| [[11-wiki/touch-kiosk-idle-timeout]] | Érintőképernyős kioszk idle-timer minimum 3 perc (date-picker + virtuális billentyűzet focus-loss tolerancia) |
| [[11-wiki/nextjs-api-proxy-bridge]] | 2 Node-service közti adatcsere Next.js API route proxy-val: no CORS, server-side env-auth, try/catch fallback |

## Mi kerül ide

- **Koncepciók** saját szavakkal (pl. "Karpathy LLM Wiki pattern", "Johnny-Decimal")
- **Playbookok** — "hogyan csináljunk X-et" (pl. "SSH deploy-key GitHub-hoz")
- **Összehasonlítások** — "Dataview vs Bases", "PARA vs Zettelkasten"
- **Mini-howtók** — rövid, lépésről lépésre receptek
- **Glosszárium** — egy-egy fogalom definíciója

## Fájl-konvenció

- Fájlnév: `<téma-címe>.md` — **nincs dátum prefix** (evergreen)
- **Kötőjelek** szóköz helyett (pl. `Karpathy-LLM-Wiki-pattern.md`)
- Frontmatter:
  ```yaml
  ---
  name: Téma címe
  type: wiki
  tags: ["#type/reference", "<téma-spec-tag>"]
  created: 2026-04-23
  updated: 2026-04-23
  source:
    - "[[10-raw/2026-04-23 — cikk]]"
    - "https://stephango.com/vault"
  ---
  ```

## Mi **nem** kerül ide

- Nyers, nem-átírt anyagok → [[10-raw/Index|10-raw/]]
- Projekt-specifikus dolgok → [[02-Projects/Index|02-Projects/]]
- Infra-tények amik változhatnak (port, IP) → [[05-Memory/Infrastructure]]
- Döntési indoklások → [[07-Decisions/]]

## Írási elv (Kepano stílus)

- **Rövid** — 1-2 bekezdés gyakran elég
- **Evergreen** — akkor is érvényes legyen 6 hónap múlva
- **Saját szavakkal** — ha csak copy-paste, akkor maradjon raw-ban
- **Linkeld a forrást** — raw/ fájlra vagy URL-re
- **Wikilinkeld a rokon koncepciókat** — így nő a graph-nézet értéke

## Kapcsolódó

- [[10-raw/Index]] — forrás-gyűjtemény
- [[AGENTS]]
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a meta-elv ami szerint ez működik
