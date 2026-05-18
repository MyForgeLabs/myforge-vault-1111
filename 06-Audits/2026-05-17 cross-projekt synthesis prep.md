---
name: 2026-05-17 cross-projekt synthesis prep
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "#project/superintelligent-vault", "#sv/B-5"]
status: prep-only
---

# Cross-projekt synthesis prep (SV B-5 Week 2+)

> [!info] Kontextus
> Phase 5.5 (73 session NotebookLM backfill) **futás közben** van; a `vault-meta` NotebookLM (`<vault-meta-nb-id-here>`) pillanatnyilag csak az `mfl-voice-sprint-1` source-ot tartalmazza. Ez a doc **prep-anyag**: query-templátok + kézi-extracted recurring pattern-ek + új evergreen-wiki javaslatok a következő synthesis-ülésre (amikor a 72 session már a NB-ben lesz).
>
> **NE futtass tényleges NotebookLM query-t** — minden eredmény placeholder/várt-struktúra.

## 1. NotebookLM cross-projekt query-templátek

A `vault-meta` notebook-on a Phase 5.5 backfill befejezése után (~30-50 perc) futtatható 3 query.

### Q1: Cross-projekt recurring tanulságok (top-10)

**Query (kopipálható NotebookLM input):**
```
Listáld a top-10 olyan tanulságot, ami legalább 3 különböző projekt session-jében felmerült (a session frontmatter `#project/<slug>` tagje alapján). Minden pattern-nél add meg:
- A pattern rövid címe (3-7 szó)
- 3-5 különböző projekt-slug, ahol előfordult
- 1-2 session-link reprezentatív példára
- Konkrét recurring-incidens-szám (hány session)
- Van-e már wiki róla (igen/nem + wikilink)
```

**Várt válasz-szerkezet:**
| # | Pattern | Projektek | Session-számláló | Wiki van? |
|---|---------|-----------|------------------|-----------|
| 1 | Subagent-fanout LLM-mutációra | superintelligent-vault, kgc-robbantott-bra, rojtesbojt, foxxi | 7+ iteráció | [[../11-wiki/claude-code-subagent-fanout]] |
| 2 | Skeleton-first Day 0 scaffold | sv-day0-cascade, sv-week1, kinda, robbantott-bra | 6+ sprint | [[../11-wiki/sprint-day-0-skeleton-first]] |
| 3 | Smart-trigger opt-in (cost-aware) | B-1 NLI, B-2 reranker, B-3 stuck-detect, B-7 entity | 5+ axis | (nincs) — kandidát |

(A NotebookLM a Phase 5.5 után tölti ki a többit a 73 source-on.)

**Source-citation acceptance:** minden pattern-nek **min. 3 session-link kell** (NotebookLM citation-szám) — alatta `signal_too_weak` flag (csak 2 forrás = projekt-pár, nem cross-projekt).

---

### Q2: Cross-projekt közös failure-mode-ok (top-5)

**Query:**
```
Listáld a top-5 failure-mode-ot, ami legalább 2 különböző projekt session-jében felmerült. Minden failure-nél add meg:
- Failure rövid címe + tünet
- 2-4 projekt-slug
- 1-2 session-link (Events vagy Learnings szekció)
- Volt-e gyors-fix vs root-cause fix
- Wiki/MEMORY pointer van-e
```

**Várt válasz-szerkezet:**
| # | Failure-mode | Projektek | Tünet | Wiki |
|---|--------------|-----------|-------|------|
| 1 | Hostinger LiteSpeed 7-day server-cache | foxxi, kgc-marketing, rojtesbojt | DB-write OK, frontend stale 7 napig | MEMORY: Hostinger LSCACHE |
| 2 | WPML ACF→Elementor multilingual mirror eltérés | foxxi, rojtesbojt, kgc | HU=EN string-ütközés, slug-conflict | [[../11-wiki/wpml-acf-elementor-multilingual-mirror]] |
| 3 | `update_post_meta` Unicode backslash-strip | foxxi, kgc | `u00e9` sérült karakter Elementor-data-ban | [[../11-wiki/wp-elementor-template-conflicts]] |
| 4 | git-rebase `--no-edit` invalid flag (instr. bug) | vault-maintenance, deploy-smoke | rebase abort, kézi konfliktus | AGENTS.md instr. fix |
| 5 | Vault-rename + Mac Obsidian-Git sync race | vault-restructure, obsidian-vault | detached HEAD + dupla conflict cascade | MEMORY: vault rename sync |

---

### Q3: Cross-projekt tech-stack döntés-ütközések / revisited (top-5)

**Query:**
```
Listáld azokat a tech-stack döntéseket, amik legalább 2 különböző projektben felmerültek, és ahol konfliktus VAGY revisited-decision volt. Minden döntésnél add meg:
- A komponens (pl. reverse-proxy, builder, graph-db)
- Az opciók (A vs B)
- Projektek, ahol felmerült
- Mi volt a végső döntés (vagy maradt-e nyitva)
- ADR/Memory pointer
```

**Várt válasz-szerkezet:**
| # | Komponens | Opciók | Projektek | Döntés | ADR |
|---|-----------|--------|-----------|--------|-----|
| 1 | Reverse-proxy | Caddy vs Traefik vs nginx | kinda, balance, myforge-os, foxxi-staging | **Caddy** default (6 domain, 0 incidens) | MEMORY: Caddy preferred |
| 2 | WP page builder | Elementor vs Bricks | foxxi (Elementor lock-in), rojtesbojt (D1 Bricks-migration), kgc (Elementor) | Greenfield → **Bricks**; legacy → Elementor | [[../07-Decisions/2026-05-08 Rojt és Bojt — Bricks Builder migration (D1).md]] |
| 3 | Graph-DB | Memgraph CE vs Neo4j EE | superintelligent-vault (B-2, B-6, B-7) | **Memgraph CE** (in-memory, free vector-index, 280× speedup) | [[../07-Decisions/2026-05-12 sv-1 memory architecture arch]] |
| 4 | Foglalási rendszer | Bookio vs Amelia vs Tablein vs Gravity Forms | rojtesbojt (D3), foxxi (saját-CPT) | **Amelia Pro + Gravity Forms** hibrid (HelloPack) | [[../07-Decisions/2026-05-08 Rojt és Bojt — Foglalási rendszer Amelia Pro + Gravity Forms (D3).md]] |
| 5 | LLM-mutáció execution | Anthropic API vs Claude Code subagent-fanout | SV B-1/B-2/B-5/B-7/B-8, kgc-robbantott | **Subagent-fanout** ($0 cost subscription-keretben) | [[../11-wiki/claude-code-subagent-fanout]] |

---

## 2. Kézi-extracted recurring pattern-ek (NotebookLM nélkül)

A 76 closed session Summary + Learnings szekciójának grep-pásztázása alapján.

### Pattern A — Subagent-fanout LLM-mutációra ($0 cost, 7+ iteráció)

**Session-source-ok:**
- [[../08-Sessions/2026-05-17-obsidian-vault]] — 4. iteráció, 174 párhuzamos subagent ~3 óra, 0 fail
- [[../08-Sessions/2026-05-17-obsidian-vault-2]] — 14× subagent-fanout R1 8 + R2 6
- [[../08-Sessions/2026-05-17-obsidian-vault-3]] — 13× subagent-fanout 4+4+5
- [[../08-Sessions/2026-05-17-obsidian-vault-pro]] — wiki/adr/session backfill 5-8 párhuzamos
- [[../08-Sessions/2026-05-13-sv-day0-cascade]] — 5 sprint × ~12 perc Day 0
- [[../08-Sessions/2026-05-08-rojt-s-bojt-weboldal]] — 7 párhuzamos agent Phase 3 persona-synthesis
- [[../08-Sessions/2026-05-04-rojt-s-bojt-weboldal]] — 4 agent-batch (research 5-track + brand 3-agent)

**Wiki:** [[../11-wiki/claude-code-subagent-fanout]] — már létezik, naprakész (4. iteráció dokumentálva).

**Recurring elemek:**
- 1 trial → 5-8 parallel validált prompt-tal
- Subagent context-budget ~50-65K token
- Source-type-specific prompt-template (wiki/adr/session)
- Cost: $0 (Anthropic subscription-keret)

### Pattern B — Skeleton-first Day 0 scaffold (6+ sprint)

**Session-source-ok:**
- [[../08-Sessions/2026-05-13-sv-day0-cascade]] — 5 sprint Day 0 egy menetben (B-3/4/5/6/8)
- [[../08-Sessions/2026-05-13-sv-week1-implementation]] — B-1, B-2, B-7 Day 0
- [[../08-Sessions/2026-05-13-sv-b2-memory-architecture]] — B-2 Day 0
- [[../08-Sessions/2026-05-13-sv-functional-payoff]] — Day 0 → Week 1 payoff
- [[../08-Sessions/2026-05-12-obsidian-vault]] — SV scaffolding start
- [[../08-Sessions/2026-05-17-obsidian-vault-3]] — még mindig hivatkozza skeleton-first-et iterációkban

**Wiki:** [[../11-wiki/sprint-day-0-skeleton-first]] — már létezik (Day 0 cascade pattern + funkcionális-skeleton-elv hozzáadva).

**Recurring elemek:**
- ~12-15 perc/sprint cascade módban (vs 25-30 single)
- Kód <20 sor + no-API → funkcionálisra Day 0-n (NEM stub)
- 1 commit scaffold-pass
- Backlog 1 future-line → ~12 day-by-day task

### Pattern C — Hostinger LiteSpeed 7-day server-cache visszatérő probléma (3+ session)

**Session-source-ok:**
- [[../08-Sessions/2026-04-23-kgc-innovation-tour-marketing]] — első előfordulás
- [[../08-Sessions/2026-05-04-foxxi-seo-research-notebooklm]] — Hostinger LSCACHE-rule audit
- [[../08-Sessions/2026-05-08-foxxi-rebrand-iteracio2]] — bug-vadászat: default WP-blog jelent meg, `wp litespeed-purge all` kellett
- [[../08-Sessions/2026-05-10-foxxi-weboldal-2]] — server: Apache ≠ LiteSpeed (example-foxxi.local éles)
- [[../08-Sessions/2026-05-10-github-repok]] — staging-on LSCACHE

**Wiki:** Részleges — MEMORY: Hostinger LiteSpeed cache (image 7-nap). **Hiányzik:** generikus "Hostinger response-header → LSCACHE-purge protokoll" wiki.

**Recurring elemek:**
- Tünet: DB-write OK, frontend stale 7 napig
- Detection: `x-litespeed-cache: hit` response-header
- Fix: `wp plugin activate litespeed-cache && wp litespeed-purge all && wp plugin deactivate`
- `wp cache flush` / `wp w3-total-cache flush all` **NEM elég**
- Image-edge-cache: 7-napos, fájlnév-rename kell

### Pattern D — Auto-mode safety-guardrail visszatérő incidens (5+ session)

**Session-source-ok:**
- [[../08-Sessions/2026-05-08-kinda-project-folytasa]] — auto-mode polish-csomag overload
- [[../08-Sessions/2026-05-12-kgc-robbantott-bra]] — destruktív DB-művelet pre-confirm-mel
- [[../08-Sessions/2026-05-13-robbantott-bra-keres]] — auto-mode classifier
- [[../08-Sessions/2026-05-15-szerver-update]] — confirm() vs custom modal
- [[../08-Sessions/2026-05-17-obsidian-vault-3]] — multi-layer-safety-gate prod-validation

**Wiki:** [[../11-wiki/multi-layer-safety-gate]] (4 réteg: ENV-flag + script-gate + git-hook + Critic-review) + MEMORY-pointer feedback_auto_mode_polish_packages, feedback_destructive_action_confirm, feedback_auto_mode_classifier.

**Recurring elemek:**
- "Nagyon profi" / "használj bármit" auto-mode = 6-10 pontos csomag/turn
- `confirm()` túl gyenge destruktív ops-ra → custom modal + Mégse-autofocus
- Settings.json pre-rule + chat-explicit "futtasd" konfirmáció
- ENV-flag + script-gate kettős gate magas-kockázatú feature-re

### Pattern E — WPML + ACF + Elementor multilingual mirror eltérés (4+ session)

**Session-source-ok:**
- [[../08-Sessions/2026-04-27-foxi]] — első előfordulás
- [[../08-Sessions/2026-04-30-foxxi]] — WPML+object-cache silent revert
- [[../08-Sessions/2026-05-02-foxxi-weboldal]] — string-row 300+ cleanup
- [[../08-Sessions/2026-05-03-foxxi-en-translation-followup]] — HU=EN tükör
- [[../08-Sessions/2026-05-04-rojt-s-bojt-weboldal]] — TranslatePress brand-corruption 60+
- [[../08-Sessions/2026-05-08-foxxi-rebrand-iteracio2]] — Unicode-escape backslash-strip

**Wiki:** [[../11-wiki/wpml-acf-elementor-multilingual-mirror]] (3-lépéses HU→EN tükör) + [[../11-wiki/wp-elementor-template-conflicts]] (Pattern 6-10 hozzáadva).

**Recurring elemek:**
- 3-lépéses HU→EN tükör + ACF lookup + szótár-csere
- `update_post_meta` Unicode `u00e9` regex-fix
- WPML + object-cache → `wpdb->update` bypass
- TranslatePress brand-glossary launch-előtt audit

### Pattern F — `confirm()` túl gyenge destruktív műveletekre (3+ session)

**Session-source-ok:**
- [[../08-Sessions/2026-05-08-kinda-project-folytasa]] — első incidens
- [[../08-Sessions/2026-05-08-myforge-os]] — bypass-mode flip script
- [[../08-Sessions/2026-05-15-szerver-update]] — server-hardening confirm-pattern

**Wiki:** Részleges — MEMORY: feedback_destructive_action_confirm. **Hiányzik:** dedikált UX-pattern wiki "destruktív műveletek hard-confirm UX".

---

## 3. Javasolt új evergreen wiki-k (title + abstract, NEM íras)

### W1: `cross-projekt-recurring-pattern-extraction.md`

**Title:** Cross-projekt recurring pattern extraction NotebookLM-mel

**Abstract (3 mondat):** A `vault-meta` NotebookLM-be a closed session-ek backfill-jén futtatott 3 query-templátet (recurring tanulság, közös failure, tech-stack ütközés) ad cross-projekt synthesis-input-ot, ha minden source-citation min. 3 különböző `#project/<slug>` tagű session. Az automatizált pattern-detection alternatívája a kézi grep-pásztázás (76 session, Summary+Learnings szekciók), ami ~6-8 pattern-t talál ~30 perc alatt cost $0-val. A két módszert érdemes párhuzamosan használni: NB-output → quantitative ranking, kézi-pass → kontextusos validáció.

**Forrás:** ez az audit-fájl.

### W2: `hostinger-litespeed-cache-purge-protokoll.md`

**Title:** Hostinger LiteSpeed-server cache purge protokoll (response-header alapú)

**Abstract:** Hostinger shared-hostingen a LiteSpeed server-szintű cache 7-napos max-age-gel ki tudja cache-elni a régi tartalmat akkor is, ha a `wp cache flush` és `wp w3-total-cache flush all` lefutottak. Detection: `curl -I` → `x-litespeed-cache: hit` response-header. Purge: aktiváld a LiteSpeed Cache plugint (átmenetileg), `wp litespeed-purge all`, deaktiváld. Image-cache külön 7-nap, fájlnév-rename a megoldás. Ez a recurring failure-mode (4+ session: foxxi, kgc, rojtesbojt) érdemes kanonikus wiki-nek MEMORY-rövidlink helyett.

**Forrás:** Pattern C above + MEMORY pointer.

### W3: `destructive-action-hard-confirm-ux.md`

**Title:** Destruktív műveletek hard-confirm UX pattern

**Abstract:** A natív `confirm()` 3+ session-ben kevésnek bizonyult (myforge dashboard, kinda, server-hardening) — a user "OK" gombbal véletlenül romboló műveletet futtatott. Helyette: custom modal + Mégse-autofocus + szöveges megerősítés ("írd be: DELETE") + 5-mp delay + audit-log. Az AI-agent oldalon szintén: settings.json pre-rule + chat-explicit "futtasd" + ENV-flag + script-gate kettős gate. Ez a pattern általánosítható minden romboló-ops-ra (DB-drop, mass-delete, push --force).

**Forrás:** Pattern F + MEMORY: feedback_destructive_action_confirm + [[../11-wiki/multi-layer-safety-gate]].

### W4: `wp-shared-hosting-ssh-cli-workflow.md`

**Title:** WordPress shared-hosting (Hostinger/Tárhely.eu) SSH + WP-CLI workflow

**Abstract:** A shared-hostingen WP-CLI hozzáférés SSH-key-auth-tal megoldható (Hostinger panel + Tárhely.eu). A workflow: SSH-key feltöltés panel-ben → `~/.ssh/config` Host-alias → `wp` parancsok lokálról `wp --ssh=alias`. Pitfall-ok: UpdraftPlus backup-from-staging migration-ban a `wpcore.zip` üres → `wp core download --force --skip-content` workaround. LiteSpeed cache (lásd W2) gyakran közbeszól. Recurring (5+ session: foxxi, rojtesbojt, kgc-marketing).

**Forrás:** Multiple sessions + MEMORY: hostinger-updraftplus-staging-migration wiki bővítés.

### W5: `tech-stack-decision-matrix-greenfield-vs-legacy.md`

**Title:** Tech-stack döntési mátrix: greenfield vs legacy projekt

**Abstract:** A Q3 cross-projekt audit (Caddy/Bricks/Memgraph/Amelia/subagent-fanout) közös elv: **greenfield projekten preferált modern stack, legacy projekten az ügyfél-tudás-kontextus felülbír**. Konkrétan: greenfield → Bricks/Caddy/Memgraph CE; legacy → Elementor maradt foxxi-on (ügyfél tudja), nginx-WordPress maradt kgc-en (Hostinger panel-default). Az "always Caddy default" / "always Bricks greenfield" döntés ADR-szintű, így új projekt-induláskor a default-rule egyértelmű. Ez a mátrix elkerüli az újra-tárgyalt döntéseket projekt-onboardingnál.

**Forrás:** Q3 várt válasz-szerkezet + ADR-ek.

---

## 4. Action items (következő synthesis-ülésre)

> [!todo] Phase 5.5 befejezése után (~30-50 perc)
>
> 1. Verify NB-source-count: `notebooklm -n <vault-meta-nb-id-here> sources list | wc -l` ≥ 73
> 2. Futtass Q1 + Q2 + Q3 query-t (kopipálható szövegek a 1. szekcióban) — wall-clock ~5-10 perc/query
> 3. Hasonlítsd össze a NotebookLM-output-ot a 2. szekció kézi-extracted pattern-jeivel — gap-elemzés
> 4. Promote 3-5 új evergreen wiki kandidát (3. szekció) → írj wiki-szöveget (skill: bmad-distillator vagy manual)
> 5. Update MEMORY.md projekt-pointerei a cross-projekt findings-szal
> 6. Update [[../11-wiki/Crystallization-protocol]] cross-projekt-routing szabállyal (ha 3+ projekt-overlap, automatikus wiki-promote)

## 5. Korlátok / nem-célok ehhez a doc-hoz

- **NEM futtattam** NotebookLM CLI query-t (Phase 5.5 in-progress)
- **NEM írtam** új wiki-szöveget (csak recommendation skeleton)
- **NEM módosítottam** AGENTS.md / 00-Meta-t / vault-meta NotebookLM-et
- A kézi-extracted pattern-listák **nem teljesek** — csak grep-based sampling 8-10 keyword-on. A NotebookLM-output ezeket bővíteni/finomítani fogja.

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — B-5 sprint context
- [[../11-wiki/sv-08-notebooklm-cognitive-layer]] — B-5 ADR háttér
- [[../11-wiki/claude-code-subagent-fanout]] — Pattern A wiki
- [[../11-wiki/sprint-day-0-skeleton-first]] — Pattern B wiki
- [[../11-wiki/multi-layer-safety-gate]] — Pattern D wiki
- [[../11-wiki/wpml-acf-elementor-multilingual-mirror]] — Pattern E wiki
- [[../06-Audits/Index]] — audit index
