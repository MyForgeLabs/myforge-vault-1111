---
name: BMAD-Method ↔ MyForge Vault 11.11 integráció design
type: audit
tags: ["#type/audit", "#topic/bmad", "#topic/vault-integration", "#source/research"]
created: 2026-05-18
updated: 2026-05-19
status: draft-design
---

# BMAD ↔ MyForge Vault 11.11 — integráció design

> [!info] Scope
> Hogyan kapcsoljuk be a vault-tudást (KO-DB + Memgraph + 02-Projects + wiki) a BMAD-Method workflow-jába, és hogyan ragadjuk be a BMAD-output-ot (PRD/Architecture/Epic/Story/Retro) automatikusan a vault-ba.

## 1. BMAD-Method pipeline overview (research)

Forrás: `https://docs.bmad-method.org/llms-full.txt` + lokális `/root/_bmad/bmm/config.yaml` + 208 telepített `bmad-*` skill SKILL.md vizsgálata.

### Phases (4 sequential)

| # | Phase | Output | Triggering skills |
|---|---|---|---|
| 1 | **Analysis** | brainstorming, research, product-brief, PRFAQ (opt) | `bmad-brainstorming`, `bmad-domain-research`, `bmad-market-research`, `bmad-product-brief`, `bmad-prfaq` |
| 2 | **Planning** | PRD vagy tech-spec | `bmad-bmm-create-prd`, `bmad-bmm-quick-spec`, `bmad-bmm-create-ux-design` |
| 3 | **Solutioning** | architecture (BMad/Enterprise only) | `bmad-bmm-create-architecture`, `bmad-bmm-create-epics-and-stories` |
| 4 | **Implementation** | epic → story → dev-story → retro | `bmad-bmm-create-story`, `bmad-bmm-dev-story`, `bmad-bmm-sprint-planning`, `bmad-bmm-retrospective` |

3 tracks scope szerint: **Quick Flow** (1-15 story, csak tech-spec), **BMad Method** (10-50 story, PRD+Arch+UX), **Enterprise** (30+ story, +Security+DevOps).

### Artifact-types és tárolás

BMAD natívan:
```
_bmad-output/
  planning-artifacts/
    PRD.md (vagy prd/index.md sharded)
    architecture.md
    epics/epic-N.md
    ux-design/
  implementation-artifacts/
    sprint-status.yaml
    stories/story-*.md
```

Konfig: 3-rétegű override (`_bmad/custom/*.user.toml` → `_bmad/custom/*.toml` → skill defaults). Per-projekt `_bmad/bmm/config.yaml` tárolja a `planning_artifacts`/`implementation_artifacts` path-okat — **MÁR most átirányítható** a vault-ba.

### Agent-szerepek (10+ persona)

`Analyst (Mary)`, `PM`, `Architect`, `UX Designer`, `Developer (Amelia)`, `QA`, `SM`, `Tech Writer`, plus GDS-családra `Game Designer / Game Architect / Game Dev / Game QA / Game SM / Solo-Dev`, plus CIS-családra `Brainstorming Coach / Creative Problem Solver / Design Thinking Coach / Innovation Strategist / Presentation Master / Storyteller`, plus TEA testarch agent, plus BMB module-builder agents.

### Lokális telepítés-state (2026-05-19)

- `/root/_bmad/` — BMM (Method), BMB (Builder), TEA (TestArch) globális
- Per-projekt: `/root/projektjeim/{KGC-ALL,mfl-bot,zsofi-law,kgc,_bmad-output}` + `/opt/chatwoot/ai-chatbot/_bmad-output/` (2 epic-file már létezik)
- Globális `output_folder: /root/_bmad-output` (NEM vault-be jelenleg)

## 2. Top-5 vault-integráció pont

1. **Pre-load context BMAD-skill induláskor** — `bmad-bmm-create-prd` / `create-architecture` / `dev-story` első lépésében olvasson be ~5K token kontextust a vault-ból (project-md head + KO-DB top-K + Memgraph semantic top-K + meglevő ADR-ek). Ez a **legmagasabb leverage**, mert minden BMAD-output minőségileg jobb lesz.
2. **BMAD-output → vault auto-ingest** — minden PRD/Arch/Story/Retro landolása után frontmatter-normalize + `vault-ko-ingest --file` + `vault-embed --file`, így a következő BMAD-session már látja KO-DB-ből / Memgraph-ból.
3. **Folder-konvenció vault-on** — `02-Projects/<slug>/bmad/<artifact>.md` (új subdir-konvenció, `type:` enum bővítendő: `prd | tech-spec | architecture | epic | story | sprint | retro | ux-design | product-brief | gdd`).
4. **BMAD `planning_artifacts` átirányítása** — per-projekt `_bmad/bmm/config.yaml`-ben:
   ```yaml
   planning_artifacts: /root/obsidian-vault/02-Projects/{project_slug}/bmad
   implementation_artifacts: /root/obsidian-vault/02-Projects/{project_slug}/bmad
   ```
   Így a BMAD natívan a vault-ba ír — ingest-bridge utólag csak normalizál.
5. **Cross-project knowledge-sharing** — `vault-ko-query --predicate uses_stack --top-k` képes több projekt PRD/Arch-jából extrahált tényt visszaadni → a "minden Next.js-projektnek mit építünk" kérdés out-of-the-box megválaszolt.

## 3. `bmad-vault-bridge` skeleton-state

**Location:** `/usr/local/bin/bmad-vault-bridge` (228 LOC, Python 3, executable).

**Modes:**

| Mode | CLI | Funkció | Smoke-test status |
|---|---|---|---|
| Ingest | `--ingest <file> --project <slug>` | frontmatter validate+normalize → `02-Projects/<slug>/bmad/<file>` → vault-ko-ingest + vault-embed | ✅ PASS (chatwoot epic-1 test-ingest 2026-05-19 04:49) |
| Context | `--context <slug> [--query "..."] [--top-k N]` | project-md head + KO-DB top-K + Memgraph top-K block, stdout vagy `--write` fájlba | ✅ PASS (boulium top-3 dry-run 2026-05-19 04:49) |

**Audit-log:** `/root/obsidian-vault/06-Audits/bmad-vault-bridge-log.jsonl` (JSONL, ts/event/payload).

**Frontmatter normalizáció:** auto-detect `type` filename/folder pattern alapján (BMAD_TYPE_MAP), kötelező mezők `name/type/created/updated`, default `tags: ["#type/<t>", "#source/bmad"]`, `source: bmad`.

**Integráció más vault-tooling-gel:** ha `vault-ko-ingest` / `vault-embed` a PATH-on → automatikusan meghívja; `--no-index` flag-gel kihagyható (dry-run / CI).

## 4. Mérnöki őszinte: production-ready-e?

**Skeleton SHIPPABLE, de blocker-ek a teljes integrációhoz:**

✅ **Működik:**
- Frontmatter normalize + ingest pipeline (smoke-test PASS).
- Context-pre-load (KO-DB + semantic search) működő subprocess-pipeline-nal.
- Audit-log JSONL append.

⚠️ **Részleges blocker-ek:**
1. **BMAD-skill nem hívja meg automatikusan a bridge-et** — minden `bmad-*` skill `SKILL.md` jelenleg `workflow.xml`-t indít, NINCS pre/post hook. Megoldás: vagy (a) manuálisan futtatja a user a `bmad-vault-bridge --context <slug>` parancsot a BMAD-skill ELŐTT és bemásolja a kimenetet, vagy (b) `bmad-bmm-generate-project-context` skill workflow-jába injektáljuk a vault-pre-load lépést (egyik `step-NN-*.md`-ben subprocess-call), vagy (c) Claude Code SessionStart-hook (kísérleti).
2. **`vault-embed` CLI** — listán szerepel design-szinten, de `which vault-embed` jelenleg NEM ad treffert (csak `vault-search`/`vault-bm25-backfill` van élesen). Az embed pipeline közvetlenül a Python-modulon át megy; bridge `--no-index` workaround-dal addig.
3. **Folder-konvenció áttörés** — most a BMAD `output_folder: /root/_bmad-output`. Ez nem törik el, csak ingest után a vault-be is megjelenik kópia. Tisztább lenne projekt-szintű `_bmad/bmm/config.yaml`-eket átírni `02-Projects/<slug>/bmad/` target-re — de az 5+ project átírása manuális.
4. **`type:` enum bővítése a Frontmatter-schema-ban** — kell hozzáadni `prd | tech-spec | architecture | epic | story | sprint | retro | ux-design | product-brief | gdd`. Ez egy 1-soros vault-edit, NEM blocker, csak TODO.

**Verdikt:** **sprint-ben implementálható** (3-5 nap), de Sprint 1 elég csak a bridge + manual-call patternre; auto-hook Sprint 2.

## 5. Sprint-prioritás 3-csomag (ajánlott sorrend)

### Csomag A — Bridge éleslő (1 nap) ✅ MOST KÉSZ

- [x] `bmad-vault-bridge` script (228 LOC) `/usr/local/bin/`-ban
- [x] Mode ingest + mode context smoke-tested
- [x] Audit JSONL log
- [ ] **TODO:** `vault-embed` CLI-shim — vagy a meglevő embed-Python-modulra wrapper (~30 sor) hogy a bridge teljes pipeline-t le tudja futtatni
- [ ] **TODO:** Frontmatter-schema bővítése `02-Projects/_unfiled/bmad/`-default mellett — `00-Meta/Frontmatter-schema.md`-be `type:` enum bővítés (prd/architecture/epic/story/retro/sprint/ux-design/gdd/tech-spec/product-brief)
- [ ] **TODO:** README a vault-on `02-Projects/<slug>/bmad/`-konvencióhoz

### Csomag B — Context-pre-load adoption (2 nap)

- [ ] **Manual usage pattern dokumentálása** `11-wiki/bmad-vault-context-preload.md`-ben — minden BMAD-skill futtatása ELŐTT `bmad-vault-bridge --context <slug> --write` parancs ajánlott, az output-fájlt @-attach-elve a BMAD-skill első prompt-jába
- [ ] **`bmad-bmm-generate-project-context` skill kiterjesztése** — első step injektálja a `bmad-vault-bridge --context` kimenetét a `_bmad/bmm/project-context.md`-be, így minden további BMAD-skill ami a project-context.md-t olvassa, automatikusan kap vault-context-et (ez a **legkevesebb skill-módosítással maximális leverage**)
- [ ] **3-5 valós projekten próbafutás** (kgc-berles / boulium / mapesz) — minden meglevő PRD/Architecture-fájlt retroaktívan ingest-elve a bridge-en, mérni a KO-DB növekedést és a következő BMAD-session prompt-minőség javulását

### Csomag C — Auto-output flow + per-projekt BMAD-redirect (2 nap)

- [ ] **Per-projekt `_bmad/bmm/config.yaml` átírás** — kgc / boulium / mapesz / mfl projektekben `planning_artifacts`/`implementation_artifacts` átirányítása `/root/obsidian-vault/02-Projects/<slug>/bmad/`-be, így BMAD natívan a vault-ba ír
- [ ] **Post-create hook** — BMAD `bmad-bmm-create-prd` / `create-architecture` / `create-story` workflow-jának utolsó step-jébe `bmad-vault-bridge --ingest --no-index` automatikus hívás (mert a fájl már a vault-ban van, csak frontmatter-normalize + KO-DB-ingest kell, embed nélkül)
- [ ] **`vault-ko-query` BMAD-typed predikátumok** — `bmad:prd-acceptance-criteria`, `bmad:epic-status`, `bmad:story-dependency` predikátumokkal a KO-DB egy mini-BMAD-tracker lesz, `vault-ko-query --predicate bmad:story-dependency --top-k 20` listázza projekt-független story-graph-ot
- [ ] **Audit + retrospektíva** `06-Audits/2026-05-25 BMAD-vault adoption metrics.md` — 1 hét után mérni: hány artifact ingest-elve, hány context-pre-load használva, mennyivel csökkent a BMAD-promptok kontextus-bevezető része

## Kapcsolódó

- `/usr/local/bin/bmad-vault-bridge` — bridge skeleton (228 LOC, smoke-tested)
- `/root/_bmad/bmm/config.yaml` — globális BMAD-config (user_name=Foxy, lang=Magyar)
- [[00-Meta/Frontmatter-schema]] — `type:` enum-bővítés szükséges
- [[02-Projects/Index]] — projektek listája, ahova a `<slug>/bmad/` subdir-ek kerülnek
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a BMAD-vault-bridge ennek a crystallization-mintának egy domain-specifikus alkalmazása (BMAD-artifact-okból raw → wiki-distilled tudás)
