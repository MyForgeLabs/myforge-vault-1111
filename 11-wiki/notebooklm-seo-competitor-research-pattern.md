---
name: NotebookLM SEO competitor research pattern
type: wiki
tags: ["#type/wiki", "#topic/seo", "#tool/notebooklm", "#research"]
created: 2026-05-05
last_modified: 2026-05-05
source:
  - "[[08-Sessions/2026-05-04-foxxi-seo-research-notebooklm]] — foxxi-projekt validation (17×7 workflow)"
related:
  - "`notebooklm` (CLI-skill)"
  - "[[02-Projects/foxxi-seo-research-2026-05-04]]"
updated: 2026-05-19
---

# NotebookLM SEO competitor research pattern

> Komplett versenytárs-elemzés és kulcsszó-gap research **1 órán belül** Google NotebookLM-mel. Kipróbálva a foxxi-projekten (17 source × 7 strukturált kérdés). A pattern független a domain-től — fogászat, autószerelő, B2B SaaS, bármi.

## Mikor használd

- Új weboldal előtt: kulcsszó-stratégia + content-roadmap
- Meglévő site SEO-deficit feltárása versenytárs-elemzéssel
- Blog-tartalom-tervezés (kulcsszó + címötlet egyszerre)
- USP-mátrix és CTA-stratégia validáció

## 5 lépéses workflow

### 1. Kulcsszó-térkép (saját szakmai tudás → ~10-15 keyword)

Saját ismeretedből + a célzott domain szakmai jellegzetességeiből készíts keyword-listát:
- **Tématerületek** (pl. fogszab szakterületek: Invisalign, műtéti, gyermek, felnőtt, hasadékos)
- **Lokáció** (pl. Buda, Széll Kálmán, Mammut, Margit körút)
- **Bizalom-build** (pl. szakorvos, Ph.D., specialista, garancia)
- **Ár / finanszírozás** (pl. csomagár, részletfizetés, egészségpénztár)
- **Tipikus search-intent** (probléma vs megoldás)

Cél: ~15-20 keyword 5 kategóriában.

### 2. SERP-keresés versenytárs-jelöltekért (4-5 query)

A top kulcsszavakra **WebSearch** (vagy Google manual) — a SERP top 10-ből választd ki a top 8-12 versenytársat:
- Geo-relevánsak elsőként (földrajzi rivális)
- "Mindenes" + erős marketing rivális (pl. Mindentment-szerű)
- Specialista rivális (pl. csak fogszab)

Tipp: a párhuzamos `WebSearch` query-k jól működnek (4-5 egyszerre).

### 3. NotebookLM source-add (sequential, ~3-5 sec/url)

```bash
notebooklm create "Cég SEO Research YYYY-MM-DD" --json
# parse out the notebook_id

# Add source URLs one by one (parallel may rate-limit)
for url in "${URLS[@]}"; do
  notebooklm source add "$url" --notebook "$NB_ID" --json
done

# Verify all ready (status=ready, not "error")
notebooklm source list -n "$NB_ID" --json | jq '.sources[] | {title, status}'
```

**Buktatók:**
- Egyes URL-ek 404-elnek vagy auth-falnak ütköznek → broken state, törölni + helyettes URL
- A `--no-wait` flag csak `add-research`-en van, a sima `source add` automatikusan vár
- Optimum source-szám: 15-20 (foxxi: 17 v1 + 12 v2 = 29). Standard plan limit 50.

### 4. 7 strukturált kérdés (`notebooklm ask` JSON-vel)

A kipróbált 7 kérdés-set (a foxxi-research alapján):

```
Q1. Keyword-gap (TOP 20 hiányzó kifejezés 5 kategóriában)
Q2. FAQ-gap (5 kategória × 4-5 kérdés példa-válaszokkal)
Q3. USP-mátrix (saját unique vs versenytárs-erősebb vs overlap)
Q4. Árlista-struktúra + 5 best practice
Q5. CTA-elemzés (6 kategória versenytárs-szövegekkel)
Q6. 15 blog-téma prioritás-rendben + saját USP-erősség per cikk
Q7. TOP 25 long-tail keyword + landing-page javaslat
```

**Pattern:** mindegyik kérdés `--json` flag-gel + outputot fájlba menteni:
```bash
notebooklm ask "Q1 szöveg..." --notebook "$NB_ID" --json > /tmp/research/q1.json
jq -r '.answer' /tmp/research/q1.json > q1-answer.md
```

### 5. Output-szerkezet

```
02-Projects/<projekt>-seo-research-output/
├── q1-answer.md  (raw NotebookLM válaszok citation-ökkel)
├── q2-answer.md
├── ...

02-Projects/<projekt>-seo-research-YYYY-MM-DD.md  (összegző project-note)
├── TL;DR — 7 fő tanulság
├── Forrás-leltár (NotebookLM source-list)
├── Top 20 keyword-gap kategóriánként
├── FAQ-gap blokkok
├── USP-mátrix
├── Árlista best-practice
├── CTA-stratégia + saját gyengeség-értékelés
├── 15 blog-téma prioritás
├── 25 long-tail keyword + landing-cél
├── Yoast meta-action a kulcs-page-ekre
└── Implementációs prioritás-mátrix (Quick win / Közép / Hosszabb)
```

## Robusztusság / hibakezelés

### NotebookLM RPC instabilitás (502 Bad Gateway)

Egyetlen kérdés (általában a hosszabbak) elhasalhat 502-vel. **Pattern:** `null` válasz esetén egyszerű retry 1× azonnal — általában megy. Ne adj `--retry`-flag-et az `ask`-nek (csak `generate`-eknek van).

### Auth time-out

Hosszabb session során a NotebookLM auth elveszhet. Re-auth: `notebooklm login` (browser-flow). A source-add lehet sikeres auth-után is, de chat/ask-hez aktív session kell.

### Tartalom-minőség

A NotebookLM válasz-minősége **radikálisan jobb** mint külön WebSearch + manual aggregation, mert:
- Konkrét idézetek a forrás-szövegekből
- Citation-pointer minden állításnál
- Magyar nyelven is működik (UTF-8 source-okkal)
- Cross-source aggregation (pl. "ezt 3 versenytárs is hangsúlyozza")

## Időbecslés

| Fázis | Idő |
|---|---|
| 1. Kulcsszó-térkép | 5-10 perc |
| 2. SERP-keresés | 5-10 perc |
| 3. Source-add (15-20 URL) | 1-2 perc |
| 4. 7 kérdés feltevése | 4-6 perc compute |
| 5. Output-szerkezet írása | 30-60 perc (ez a leglassabb) |
| **Összesen** | **~60-90 perc** |

A research-output strukturálása + interpretálása viszi a legtöbb időt — a NotebookLM-compute kb. 5-10 perc.

## Versenytárs-bővítés (v2 research)

Ha a user a research-output átolvasása után jelez "ezeket a versenytársakat is" — **ne csinálj új notebookot**, hanem ugyanahhoz add hozzá a +12 új source-t:
```bash
for url in "${NEW_COMPETITORS[@]}"; do
  notebooklm source add "$url" --notebook "$NB_ID" --json
done
```
Az eredeti 17 source + 12 új = 29 source — még mindig <50 (Standard plan limit).

Aztán **ugyanazokat a 7 kérdést** újra felteheted — a válaszok most már a kibővített source-poolt használják, és a v1 vs v2 különbségek mutathatják a kibővítés értékét.

## Kapcsolódó

- `notebooklm` — a CLI-skill (claude-skill, nem vault file)
- [[02-Projects/foxxi-seo-research-2026-05-04]] — első kipróbálás (foxxi v1, 10 versenytárs)
- [[08-Sessions/2026-05-04-foxxi-seo-research-notebooklm]] — workflow validation session
