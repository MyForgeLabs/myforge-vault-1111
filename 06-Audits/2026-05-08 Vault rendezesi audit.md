---
name: 2026-05-08 Vault rendezési audit
type: audit
date: 2026-05-08
author: claude
tags: ["#type/audit", "vault-rules", "#op/cleanup", "#op/review"]
created: 2026-05-08
updated: 2026-05-08
---

# Vault rendezési audit — 2026-05-08

> [!info] Kontextus
> A 2026-04-30-i restructure óta 8 nap telt el. Ezalatt új tartalom került a vault-ba (Foxxi sprint, Rojt és Bojt discovery, CV-asset import, daily firecrawl/GitHub trending output) — több helyen a Johnny-Decimal struktúra mellé / azt megkerülve. Ez a riport pillanatkép és prioritált akciólista.

## TL;DR — top 5 javítandó

1. **`raw/` (gyökérben) parallel a `10-raw/`-val** — 23 új fájl (05-01…05-07) rossz helyre került. **Karpathy-minta sérül.** [Akció A]
2. **`01-Daily/` 8 napja nem frissült** — utolsó: `2026-04-30.md`. Ma 2026-05-08. **8 napi napló hiányzik / backfillelendő.** [Akció B]
3. **CV-asset szétszórt a gyökérben** — `Önéletrajz.md` (10KB), 4 CV-fájl (.docx/.pdf), 2 portrait kép, 2 logo-mappa, `cv-website/`, `cv-photo/`. Egyikük sem dokumentált projektként. [Akció C]
4. **`02-Projects/` keveri a projekt-leírásokat és session-szerű artifaktokat** — 11 darab `foxxi-*-2026-05-*.md` fájl (üzenetek, checklist-ek, progress notes) project-fájlok közé szórva. [Akció D]
5. **`02-Projects/Index.md` elavult** — hiányzó projekt-bejegyzések (`foxxi-cv-website`), hiányzó alfájl-utalások (foxxi-blog-drafts/, foxxi-seo-research-output/, foxxi sprint-fájlok). [Akció E]

---

## Számokban

| Metrika | Érték |
|---------|-------|
| Markdown fájlok össz. | 212 |
| Top-szintű mappa | 11 (Johnny-Decimal) + 4 lógó (`raw/`, `cv-website/`, `cv-photo/`, `foxxi-logo-v2/`, `foxxi-logo-v3/`) |
| Frontmatter nélkül | 27 fájl |
| Hiányzó wikilink target | 0 kritikus + sok shell-szintaxis false-positive |
| 02-Projects/ projektfájlok | 13 + 11 sprint-artifakt + 2 aldir (19 fájl) + 1 canvas |
| 08-Sessions/ sessionfájl | 29 + 3 archive |
| 07-Decisions/ ADR | 17 |

---

## A — `raw/` parallel mappa a gyökérben (KRITIKUS)

### Találat

A `/raw/` mappa a vault gyökérben **23 fájlt** tartalmaz, amik az AGENTS.md és README.md szerint a **`10-raw/`** alá tartoznak (Karpathy-minta: immutable raw input).

```
raw/
├── 2026-05-01 — GitHub trending (daily).md
├── 2026-05-02 — GitHub trending (daily).md
├── … (5 további trending)
├── 2026-05-07 — firecrawl - rojt-es-bojt-* (15 firecrawl scrape)
└── 2026-05-07 — firecrawl - tassels-and-tassels-our-stores.md
```

A `10-raw/` viszont **megáll 2026-05-04-en** (utolsó: `competitor-*.md`). Tehát az automatáció (vagy a manuális munka) ettől kezdve rossz helyre ment.

### Kérdés / hipotézis

- **Automatáció hibája?** Van-e valamilyen cron/script ami `raw/`-ba dolgozik a gyökérben? (Lásd `00-Meta/bash-patches/`.)
- **Manuális tévedés?** Egy agent (vagy Peti) `raw/` parancsot adott útmutatás nélkül és az új mappába tette.

### Akció (javasolt)

1. `git mv raw/* 10-raw/` (összes fájl áthelyezése)
2. `rmdir raw/` (üres mappa törlése)
3. Ha van automatáció ami `raw/`-ba ír — kijavítani a path-t. **Ezt manuálisan kell ellenőrizni** (Peti tudja honnan jön).
4. **Frontmatter check**: A `raw/` 23 fájlja **MIND** rendelkezik frontmatterrel ✅ (jó hír — csak a hely rossz).

### Státusz: ✅ Lezárva (2026-05-09)

- `raw/` újra-létrejövés forrása: `/usr/local/bin/github-trending-report` (cron `0 8 * * *`) — `RAW = VAULT / 'raw'` hardkód a script 12. sorában.
- `Audits/` újra-létrejövés forrása: `/usr/local/bin/vault-cleanup` (cron `0 4 * * 0`) — `dest = VAULT / 'Audits' / 'System_Health.md'` a 245. sorban.
- **Javítva 2026-05-09:** mindkét script frissítve a Johnny-Decimal-prefixes path-okra (`10-raw/`, `06-Audits/`). 2026-05-09 pull-ban behúzott `raw/2026-05-09 — GitHub trending (daily).md` áthelyezve `10-raw/`-ba.
- Maradék 1 nyitott pont: a `Daily/2026-05-08.md` empty stub egyszeri eset (mac-cowork client?) — nem cron-eredetű. Egyetlen üres template-fájl volt, törölve.

---

## B — `01-Daily/` backfill hiánya (KRITIKUS)

### Találat

```
01-Daily/
├── 2026-04-23.md … 2026-04-30.md (8 fájl)
└── Index.md
```

**Ma 2026-05-08, az utolsó daily 2026-04-30-i.** 8 napi napló hiányzik (05-01 … 05-08).

A 2026-04-30 restructure dokumentálta hogy a daily backfill része volt a clean state-nek. Azóta nem futott újra.

### Akció

1. **Két opció van:**
   - **(B1) Backfill a session-ekből**: 08-Sessions/ alapján rekonstruálni a hiányzó daily-ket (mit csináltunk 05-01..05-08-on). Ez ~30 perc agent-munka.
   - **(B2) Csak a mait létrehozni**, és innentől folytatólagosan vezetni. A korábbi 7 nap helyett "Backfill ablak" jegyzet a 2026-05-08-ban.
2. **Ezenfelül**: Cron / habit kérdés — miért állt le a daily? (Restructure session lezárásakor megszakadt egy script / habit?)

### Javaslat

(B1) — backfill a session-ekből. A vault egészsége érdekében pontos napi audit-trail kell. Kontextus források: `08-Sessions/2026-04-30…2026-05-08`, `07-Decisions/`, `raw/` (új), 02-Projects/foxxi-* sprint-fájlok.

---

## C — CV-asset szétszórt a gyökérben (KÖZEPES)

### Találat — gyökér tartalom

| Fájl/Mappa | Méret | Mi ez |
|------------|-------|-------|
| `Önéletrajz.md` | 10 KB | Magyar önéletrajz (markdown) |
| `Markovics_Peter_Tamas_CV_2026_EN.docx` | 305 KB | Angol CV (Word) |
| `Markovics_Peter_Tamas_CV_2026_EN.pdf` | 228 KB | Angol CV (PDF) |
| `Markovics_Peter_Tamas_Onletrajz_2026.docx` | 305 KB | Magyar önéletrajz (Word) |
| `Markovics_Peter_Tamas_Onletrajz_2026.pdf` | 230 KB | Magyar önéletrajz (PDF) |
| `peti-headshot.jpeg` | 2.9 MB | Profilkép |
| `peti.portrait.jpg` | 250 KB | Profilkép (kicsi) |
| `foxxi_logo_variansok.png` | 284 KB | Foxxi logó-variánsok (PNG) |
| `foxxi-logo-v2/` (mappa) | — | Foxxi logo v2 assetek |
| `foxxi-logo-v3/` (mappa) | — | Foxxi logo v3 assetek |
| `cv-photo/` (mappa) | — | CV-fotó assetek |
| `cv-website/` (mappa) | — | CV weboldal kódja (README, DEPLOY) |

**Probléma:** a Johnny-Decimal struktúra azt jelenti hogy minden tartalom prefixált mappában van (00..11). A vault gyökérben **csak** `README.md`, `AGENTS.md`, és `.git/`/`.obsidian/`/`.gitignore` legyen.

A CV-fájlok és a Foxxi logó-asset egy projekthez tartoznak — egyikük sem dokumentált projekt!

### Akció

1. **Új projekt: `02-Projects/foxxi-cv-website.md`** — projekt-fájl frontmatterrel + link `cv-website/`-re és Önéletrajz fájlokra.
2. **Mappa-áthelyezés:**
   - `cv-website/` → `02-Projects/foxxi-cv-website/` (vagy `99-assets/foxxi-cv/`)
   - `cv-photo/` → `02-Projects/foxxi-cv-website/photos/`
   - `foxxi-logo-v2/`, `foxxi-logo-v3/` → 02-Projects/foxxi/logos/ (vagy új `99-assets/foxxi-logo/`)
3. **Önéletrajz.md áthelyezése** → `02-Projects/foxxi-cv-website/Önéletrajz.md`
4. **DOCX/PDF/JPEG bináris fájlok**: érdemes megfontolni külön `99-assets/` mappát (Johnny-Decimal extension), vagy `git lfs`-t használni. **Mostanra nem kritikus**, csak ne maradjanak a gyökérben.
5. **02-Projects/Index.md frissítés** — új sor a Foxxi szekcióba.

### Megjegyzés

A `99-assets/` mappa nem szerepel az AGENTS.md-ben. Ha bevezetjük, **dokumentálni kell** a 00-Meta/README, AGENTS.md, README struktúra-listájában.

---

## D — `02-Projects/` keveri a projekt-fájlokat és sprint-artifaktokat (KÖZEPES)

### Találat — `02-Projects/` root tartalma

**Tényleges projekt-fájlok (13):**
```
foxxi.md
foxxi-email-arhivum.md
kgc-berles.md
kgc-erp.md
kgc-kivetitok.md
kgc-marketing.md
kgc-tv-cms.md
kgshop-bluebird.md
koko.md
mapesz.md
mfl-bot.md
myforge-dashboard.md
petanque-kisgeparuhaz.md
rojtesbojt.md
teszt-eu.md
```

**Sprint/üzenet/checklist-szerű fájlok (11) — Foxxi 05-01…05-06 munka:**
```
foxxi-checklist-2026-05-05.md
foxxi-csapat-uzenet-2026-05-04.md
foxxi-domi-questions.md
foxxi-domi-uzenet-2026-05-04.md
foxxi-implementacios-terv-2026-05-05.md
foxxi-next-session-tervezet.md
foxxi-progress-2026-05-02.md
foxxi-seo-research-2026-05-04.md
foxxi-seo-uzenet-2026-05-04.md
foxxi-uzenet-2026-05-04-vegleges.md
foxxi-uzenet-2026-05-05-vegleges.md
foxxi-uzenet-2026-05-06-notion-sync.md
```

**Aldir 1 — `foxxi-blog-drafts/`** (5 fájl, **frontmatter nélkül**):
```
01-invisalign-vs-hagyomanyos.md
02-inyverzes-fogmosaskor.md
03-fogszabalyozas-ara-2026.md
04-faj-e-a-fogszabalyozas.md
05-cirkon-vs-femkeramia.md
```

**Aldir 2 — `foxxi-seo-research-output/`** (7 fájl, **frontmatter nélkül**):
```
q1-answer.md … q7-answer.md
```

### Probléma

- **Sprint-artifaktok (üzenetek, checklist, progress notes) NEM projekt-leírások** — ezek session-szerű artifactok. Kategorizálási opciók:
  1. `08-Sessions/` alá (de azok más struktúrával) — nem ideális
  2. `02-Projects/foxxi/` aldir alá — projekt-mappává tesszük a foxxi-t
  3. `02-Projects/foxxi-sprint-2026-05/` aldir — egy ablak archív
- **Aldir-ok frontmatter nélkül** — Frontmatter-schema sérül.
- **02-Projects/Index.md nem említi az aldir-okat** — láthatatlan tartalom.

### Akció (javasolt)

1. **Új mappa: `02-Projects/foxxi-sprint-2026-05/`** — ide az összes 11 sprint-artifakt + későbbi sprint-fájlok.
2. **`foxxi-blog-drafts/` és `foxxi-seo-research-output/`** **maradjon** ahol van, **DE**:
   - Adjunk minden fájlhoz minimális frontmattert (`name`, `type: reference`, `created`, `tags`).
   - Vagy alternatíva: ezek is `foxxi-sprint-2026-05/` alá menjenek.
3. **02-Projects/Index.md frissítés** — `foxxi-sprint-2026-05/` mint külön sor a Foxxi szekcióban.

---

## E — `02-Projects/Index.md` elavult (KÖZEPES)

### Hiányzó hivatkozások az Index-ből

| Hiányzó | Hol van |
|---------|---------|
| `foxxi-cv-website` projekt | NEM létezik még projekt-fájl, de a CV-anyag a vault-ban van |
| `02-Projects/foxxi-blog-drafts/` aldir | Nem említve |
| `02-Projects/foxxi-seo-research-output/` aldir | Nem említve |
| Foxxi sprint-artifaktok (11 fájl) | Egyik sem említve |

### "🔬 Kutatás / archív" szekció félrevezető

Csak `teszt-eu` szerepel benne — de a `10-raw/` és `11-wiki/` is kutatás-jellegű. Az Index szerepe a **02-Projects/ saját** projektjeinek dashboardja, nem teljes vault. **Ezt nem kell módosítani.**

### Akció

1. **Új sor a Foxxi szekcióba**: `[[02-Projects/foxxi-cv-website]] | (lásd projekt-fájl) | 🟢 active — magyar+angol CV, weboldal /cv-en/cv-hu | 2026-05-04`
2. **Új sor a Foxxi szekcióba**: `[[02-Projects/foxxi-sprint-2026-05]] (vagy aldir Index)` mint sprint-archive
3. **Aldir-utalások**: lábjegyzet `foxxi-blog-drafts/` (5 SEO blog post draft) és `foxxi-seo-research-output/` (7 SEO research Q&A) — vagy beolvasztva a Foxxi projekt-fájlba mint linkek.

---

## F — Frontmatter audit (KÖZEPES → részben kozmetikai)

### Frontmatter NÉLKÜLI fájlok (27 db)

| Fájl | Megjegyzés | Akció |
|------|------------|-------|
| `cv-website/README.md` | Deployment readme — kód-melléklet, nem vault-content | Áthelyezés ut. nem vault — kihagyható |
| `cv-website/DEPLOY.md` | Deploy szkript — ugyanaz | Ugyanaz |
| `02-Projects/foxxi-blog-drafts/01..05-*.md` (5 db) | SEO blog draftek | Frontmatter hozzáadás (`type: reference`) |
| `02-Projects/foxxi-seo-research-output/q1..q7-answer.md` (7 db) | SEO Q&A research | Frontmatter hozzáadás |
| `10-raw/2026-05-04 — articles-*.md` (12 db) | Firecrawl scrape | Frontmatter hozzáadás (`type: reference`, `#type/research`) |
| `10-raw/2026-05-04 — competitor-*.md` (6 db) | Firecrawl scrape | Ugyanaz |

### Hibás `type:` enum

A schema enum: `host | project | decision | audit | session | memory | task | reference | index | dashboard | research-summary | backlog`.

**Használatban, de schema-ban nem listázva:**
- `feedback` — `05-Memory/Feedback-claims-verification.md`, `05-Memory/Feedback-fresh-verify-before-work.md`
- `project-update` — sprint-artifaktok közt (nem mindenhol)
- `document` — egyik 10-raw helyen

### Akció

1. **Schema bővítés** `00-Meta/Frontmatter-schema.md`-ban: `feedback`, `project-update` → enumba (vagy normalizálandó).
2. **Frontmatter backfill** a 25 érintett fájlra (egyszerű YAML blokk minden tetejére).
3. **Tag-taxonomy kiegészítés**: `#type/research` (10-raw/) — már de facto használt.

---

## G — `05-Memory/` strukturális megjegyzés (KOZMETIKAI)

### Találat

`05-Memory/` mappa tartalma:
```
Agents-skill-suite.md
Dashboard-access.md
Feedback-claims-verification.md  ⭐ ÚJ, nem dokumentált
Feedback-fresh-verify-before-work.md  ⭐ ÚJ, nem dokumentált
Infrastructure.md
README.md
Skill-map.md
User.md
```

A `00-Meta/README.md` és `AGENTS.md` szerinti listában csak: `User.md`, `Infrastructure.md`, `Skill-map.md`, `Dashboard-access.md`, `Agents-skill-suite.md` — a két `Feedback-*` nincs említve.

### Akció

1. `05-Memory/README.md` — két új sor a táblázatba.
2. `00-Meta/README.md` — kiegészítendő (vagy a 05-Memory/README átfedés miatt elhagyható).
3. `AGENTS.md` — `Feedback-<téma>.md` mintát említi mint pattern → már OK.

---

## H — Egyéb apróságok (KOZMETIKAI)

| Megjegyzés | Akció |
|------------|-------|
| `.DS_Store` a gyökérben | `.gitignore`-ban már szerepel ✅ — nem fontos. |
| `.gitignore` rövid (5 sor) | OK — nincs bővítendő. |
| `KGC-ALL Architektura.canvas` Excalidraw fájl `02-Projects/`-ben | OK, vault-szabály-konform. |
| 08-Sessions/_archive/ 3 test-session | OK, dokumentált. |
| 11-wiki/ 23 fájl, Index frissített (2026-05-08) | OK ✅ — wiki réteg jó állapotban. |

---

## Akcióterv — javasolt commit-csomagok

A jóváhagyásod után a következő logikus commit-okra bontva csinálnám meg a javításokat:

| # | Commit | Tartalom | Risk | Idő |
|---|--------|----------|------|-----|
| **C1** | `chore(vault): merge raw/ into 10-raw/ + remove parallel folder` | 23 fájl áthelyezés (`git mv raw/* 10-raw/`) + `rmdir raw/`. **Zero content change.** | 🟢 low | 2 perc |
| **C2** | `docs(vault): backfill 01-Daily for 2026-05-01..05-08 from sessions` | 8 új daily fájl session-ekből rekonstruálva. **Új tartalom (gondos olvasásból).** | 🟡 medium | 30 perc |
| **C3** | `chore(vault): consolidate CV/Foxxi-logo assets under 02-Projects/foxxi-cv-website/` | Új projekt-fájl + 4-5 mappa-áthelyezés + Önéletrajz.md áthelyezés. Index frissítés. | 🟢 low | 10 perc |
| **C4** | `chore(vault): organize Foxxi sprint artifacts under 02-Projects/foxxi-sprint-2026-05/` | 11 fájl + 2 aldir áthelyezés. Index frissítés. | 🟢 low | 10 perc |
| **C5** | `docs(vault): backfill missing frontmatter (25 files)` | YAML blokk hozzáadás SEO research, blog drafts, firecrawl scrape fájlokhoz. | 🟢 low | 15 perc |
| **C6** | `docs(vault): update 02-Projects/Index, 05-Memory/README, Frontmatter-schema enum` | Index sorok + Schema enum bővítés (`feedback`, `project-update`) + tag-taxonomy `#type/research`. | 🟢 low | 5 perc |
| **C7** | `docs(vault): post-cleanup audit refresh (System_Health regen)` | `06-Audits/System_Health.md` újragenerálva — új clean state. | 🟢 low | 5 perc |

**Össz idő:** ~75 perc agent-munka.

**Risk:** **C2** közepes (új tartalom kell rekonstrukcióval) — javaslom külön user-jóváhagyással. A többi tisztán mechanikai.

---

## Mit NE csináljunk (most)

- **NE bontsunk létre `99-assets/` mappát** automatikusan — előbb dönts: assetek a 02-Projects projekt-mappában maradjanak, vagy külön asset-store legyen?
- **NE töröljünk session-fájlokat** a 02-Projects-ből — minden megőrzendő, csak átszervezni.
- **NE módosítsuk a 11-wiki tartalmát** — desztillált tudás, nem érintett.
- **NE érintsük a `.obsidian/` config-ot** — Obsidian app saját.

---

## Kapcsolódó

- [[06-Audits/2026-04-23 Teljes infra audit]] — előző teljes audit (infra-fókuszú)
- [[06-Audits/System_Health]] — heti auto-gen
- [[08-Sessions/2026-04-30-vault-restructure]] — utolsó restructure session
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — minta amit visszaállítunk
- [[11-wiki/Johnny-Decimal-prefix]] — mappa-prefix szabály amit megsértettünk

---

## Összefoglaló mondat

A 04-30-i restructure clean-state-je 8 nap alatt **mérsékelten elcsúszott**: a Karpathy raw-mappa duplikálódott, a daily-napló elhalt, és a Foxxi sprint + CV-import a Johnny-Decimal struktúrán kívülre került. **Minden javítható ~75 perc alatt, 7 logikai commit-tal, low-risk szinten** (kivéve a daily backfill ami medium risk).
