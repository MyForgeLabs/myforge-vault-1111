---
name: Tag taxonómia
type: reference
tags: [memory, taxonomy, tags]
created: 2026-04-23
updated: 2026-05-19
---

# Tag taxonómia

> [!important] Kötelező használni
> Az AI agentek (Claude/Codex/Gemini) **ezeket** a tageket használják. Ha új tag kell, ide írd be előbb, utána használd. Ezzel elkerüljük hogy egyik agent `#prod`-ot, másik `#production`-t, harmadik `#éles`-et írjon ugyanarra.

## Tag-hierarchia (struktúrált)

Kettőspontos hierarchia-szintaxis — Obsidian támogatja a `tag/subtag/...` formát.

### `#env/*` — környezet

| Tag | Mit jelöl |
|-----|-----------|
| `#env/prod` | éles/production (vps-prod-example, Cloud Professional éles site-ok) |
| `#env/dev` | dev/scratch (vps-dev-example) |
| `#env/staging` | staging / preview oldalak (pl. `*.hostingersite.com`) |
| `#env/local` | helyi gépen fut (Mac) |

### `#type/*` — tartalom-típus

| Tag | Mit jelöl |
|-----|-----------|
| `#type/host` | szerver/host dokumentum |
| `#type/project` | projekt-leírás |
| `#type/decision` | architektúra-döntés (ADR) |
| `#type/audit` | pillanatkép-jelentés |
| `#type/session` | 11.11 session log |
| `#type/memory` | user/infra memória |
| `#type/task` | elvégzendő feladat |
| `#type/research` | kutatási jegyzet (raw, wiki, scrape, NotebookLM Q&A) |
| `#type/daily` | napi napló (01-Daily/) |
| `#type/index` | index/dashboard fájl (mappa README, Index.md) |
| `#type/reference` | referencia / lookup-fájl (Glossary, Frontmatter-schema, Tag-taxonomy) |

### `#tech/*` — technológia-stack

| Tag | Mit jelöl |
|-----|-----------|
| `#tech/nextjs`, `#tech/nest`, `#tech/vite`, `#tech/react` | web frontend/backend keretek |
| `#tech/docker`, `#tech/systemd`, `#tech/pm2` | runtime managerek |
| `#tech/postgres`, `#tech/mysql`, `#tech/redis`, `#tech/minio` | datastore-ok |
| `#tech/nginx`, `#tech/caddy` | reverse proxy |
| `#tech/wordpress`, `#tech/php` | WP-stack |
| `#tech/python`, `#tech/node`, `#tech/bash`, `#tech/bun` | nyelvek/runtime-ok |

### `#project/*` — projekt-hivatkozás

Használd a projekt-slug-ot (ami a `Projects/<slug>.md` fájlnév):
`#project/teszt-eu`, `#project/koko`, `#project/kgc-erp`, `#project/kgc-berles`, `#project/kgc-marketing`, `#project/kgc-kivetitok`, `#project/kgc-tv-cms`, `#project/kgshop-bluebird`, `#project/petanque-kisgeparuhaz`, `#project/mapesz`, `#project/mfl-bot`, `#project/myforge-dashboard`, `#project/foxxi` (WP — fogszab), `#project/foxxi-cv-website` (Peti CV), `#project/foxxi-email-arhivum`, `#project/rojtesbojt` (kávézó)

> [!warning] Foxxi névütközés
> A `foxxi` slug **kétértelmű**: `#project/foxxi` = Foxxi Budai Fogszabályozás (dental, WP), `#project/foxxi-cv-website` = Peti személyes CV (foxxi labs branded). A foxxi-logo-* asseteket a CV-website tárolja, de Foxxi (dental) brand-jellegűek.

### `#op/*` — operatív státusz

| Tag | Mit jelöl |
|-----|-----------|
| `#op/todo` | teendő (nem feltétlenül a Tasks/Backlog-ban) |
| `#op/bug` | hibás működés |
| `#op/cleanup` | tisztítás/törlés |
| `#op/security` | biztonsági ügy |
| `#op/backup` | mentés-kapcsolatos |
| `#op/ssl` | tanúsítvány |
| `#op/monitoring` | figyelés/alerting |
| `#op/docs` | dokumentáció-frissítés |
| `#op/review` | ránézni, eldönteni |
| `#op/fix` | javítás történt |
| `#op/verify` | ellenőrzés történt |

### `#agent/*` — agent-kapcsolat (ritkábban)

| Tag | Mit jelöl |
|-----|-----------|
| `#agent/claude` | Claude Code által írva/kezelt |
| `#agent/codex` | Codex CLI |
| `#agent/gemini` | Gemini CLI |

### `#bmad/*` — BMAD module artifact-ok (2026-05-19 bővítés)

A BMAD (Breakthrough Method for AI-Driven Development) workflow által generált doksik.

| Tag | Mit jelöl |
|-----|-----------|
| `#bmad/prd` | Product Requirements Document |
| `#bmad/architecture` | technikai architektúra-doksi |
| `#bmad/ux-design` | UX-tervezési spec |
| `#bmad/story` | story-fájl (sprint-implementációhoz) |
| `#bmad/epic` | epic-bontás |
| `#bmad/retrospective` | post-epic retro |
| `#bmad/qa` | QA / test design / NFR |
| `#bmad/gdd` | Game Design Document (GDS module) |
| `#bmad/brief` | product-brief / game-brief |
| `#bmad/research` | market/domain/technical research output |

### `#cron/*` — cron-job futás-rytmus (2026-05-19 bővítés)

A `vault-cron-flock`-kal és automatizált scriptekkel futó folyamatok.

| Tag | Mit jelöl |
|-----|-----------|
| `#cron/10min` | 10 percenként (pl. `vault-autosave`) |
| `#cron/hourly` | óránként |
| `#cron/daily` | naponta (Daily-note autogen, embed-freshness) |
| `#cron/weekly` | hetente (vault-cleanup vasárnap 04:00, adr-aging-watch) |
| `#cron/monthly` | havonta |
| `#cron/manual` | nem cron-on, csak kézi futtatás |

### `#audit/*` — audit-doksi alkategória (2026-05-19 bővítés)

A `06-Audits/`-ban élő pillanatkép-jelentéseket kategorizálja.

| Tag | Mit jelöl |
|-----|-----------|
| `#audit/health` | rendszer-egészség (System_Health.md, host-állapot) |
| `#audit/conflict` | konfliktus-detect (cross-source contradictions) |
| `#audit/coverage` | lefedettség (wiki-quality, embed-coverage, kapcs.) |
| `#audit/adr` | ADR-pipeline-tracker, status-distribution |
| `#audit/cost` | költség-rollup, vault-cost |
| `#audit/security` | biztonsági-audit (server hardening, secret-scan) |
| `#audit/performance` | perf-audit (web vitals, lighthouse) |
| `#audit/seo` | SEO-audit |
| `#audit/research` | research-driven audit (NotebookLM-driven, deep-research) |

### `#dashboard/*` — dashboard-komponens hivatkozás (2026-05-19 bővítés)

A MyForge OS dashboard widget/tab/view-okhoz.

| Tag | Mit jelöl |
|-----|-----------|
| `#dashboard/widget` | widget-szintű komponens (skill-card, run-history, heatmap) |
| `#dashboard/tab` | top-level tab (chat, skills, projects, audits) |
| `#dashboard/view` | view/route szintű |
| `#dashboard/spec` | dashboard-specifikus PRD/spec/design |
| `#dashboard/wave` | Wave-A..K roadmap-szakasz (MyForge OS) |

## Konvenciók

- **Egyszerű** pont-nélküli tageket is használhatsz (pl. `#wordpress`, `#vault`) ha gyakori téma — de a strukturáltak **elsőbbséget** élveznek
- **Ne találj ki új tageket ad hoc** — vagy írd be ide, vagy használj meglévőt
- **Frontmatter-ben** mindig array: `tags: ["#env/prod", "#type/host"]` (helytelen: `tags: #prod`)
- **Body-ban** szabadon: `Ez egy #env/prod issue, #op/bug kategória`

## Példák

```yaml
# Projects/kgshop-bluebird.md:
tags: ["#type/project", "#env/prod", "#tech/docker", "#tech/postgres"]

# Tasks/Backlog.md egy item:
- [ ] KGC-ERP 502 fix  ⏫ #env/prod #project/kgc-erp #op/bug ➕ 2026-04-23

# Audits/*.md:
tags: ["#type/audit", "#env/prod", "#env/dev"]

# 06-Audits/wiki-quality-trend.md (auto-generated, coverage audit):
tags: ["#type/audit", "#audit/coverage", "#cron/weekly"]

# 06-Audits/adr-status.md:
tags: ["#type/audit", "#audit/adr", "#cron/weekly"]

# BMAD PRD output:
tags: ["#type/decision", "#bmad/prd", "#project/<slug>"]

# MyForge OS Wave-K spec:
tags: ["#type/project", "#dashboard/wave", "#dashboard/spec", "#project/myforge-dashboard"]
```

## Frissítési protokoll

Amikor egy agent új tag-et akar használni ami még nincs itt:
1. **Kérdezze meg a user-t** vagy **tegye fel a [[04-Tasks/Backlog]] 🟡-ba** hogy jóváhagyásra váró
2. Ha a user OK-val elfogadja → add hozzá ehhez a listához (Memory-tag-taxonomy)
3. Utána használható

## Kapcsolódó

- [[AGENTS]] — itt a hivatkozás
- [[00-Meta/Frontmatter-schema]] — YAML séma amibe ezek a tagek mennek
