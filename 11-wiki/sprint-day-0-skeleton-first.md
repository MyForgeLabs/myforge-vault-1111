---
name: Sprint Day 0 skeleton-first playbook
type: wiki
tags: ["#type/wiki", "sprint-playbook", "vault-meta", "best-practice"]
created: 2026-05-12
updated: 2026-05-17
status: stable
---

# Sprint Day 0 — skeleton-first commit playbook

Egy új sprint (B-1, B-2, …) első napján **egyetlen committal** rakd le a teljes vázat (scaffold), DE funkcionális kódot ne írj — az Week 1-2-re marad, kalibráció után.

## Miért

- **Reviewable foundation** — az ADR absztrakt-rétege átkonvertálódik konkrét fájlokra, a sprint mostmár **mérhető haladású**, nem absztrakció marad
- **Out-of-the-box dependency-check** — ha a skeleton dry-run-olható (de no-op), a Day 1-en már látod hogy a wiring stimmel, mielőtt funkcionalitást építenél rá
- **Cron + audit-compatibility ellenőrzés** — az új fájlok rögtön belekerülnek a `vault-cleanup` audit-pipeline-ba, frontmatter-hibák azonnal kiderülnek
- **Sprint-Backlog teljes láthatóság** — minden Week 1-6 task `#project/<slug>` taggel kiosztva, nem „valamikor majd"
- **Stage-gate kockázat-kontroll** — a skeleton mögötti git-tag (`sv-phase-bN-day0`) később explicit checkpoint a visszafordítható retreat-hez

## Mit tartalmaz a Day 0 commit

```
sprint/
├── README.md                    Sprint-overview + status + acceptance criteria
├── schema/                      Adatszint (SQL / YAML / JSON-schema)
│   └── <foo>.sql
├── scripts/
│   └── <main-tool>.py           SKELETON: --help működik, --dry-run runnable, real-extract = no-op stub
├── prompts/                     LLM-prompt-templátok (LLM-as-judge, extractor, summarizer)
│   └── <foo>-template.md
└── (config + audit-log helyek üresen, gitignored)
```

Plus **közös vault-fájlok ugyanabban a committban**:

- `02-Projects/<slug>.md` — projekt-fájl státusszal + sprint-táblával + sikermetrikákkal + backout-plan-nel
- `04-Tasks/Backlog.md` — `#project/<slug>` szekció hozzáadva Day 0-tól Week 6-ig minden taskkal
- `02-Projects/Index.md` — új sor a megfelelő csoport-táblába
- `.gitignore` — bináris/DB-fájlok kizárva (a schema és script TRACK-elt)
- Kapcsolódó ADR `parent:` vagy `sprint:` frontmatter-mezőjébe a projekt-file linkelve

## Konkrét példa — B-1 Crystallization automation Day 0 (2026-05-12)

| Vault-fájl | Méret | Mit tartalmaz |
|---|---|---|
| `.vault-ko/schema.sql` | 2.5KB | 3 SQLite tábla (facts, propagation_log, crystallization_runs) WAL mode + indexek |
| `.vault-ko/facts.db` | 52KB | SQLite DB initialized from schema (gitignored) |
| `.vault-ko/scripts/vault-ko-ingest.py` | 4.6KB | argparse `--backfill/--file/--session/--dry-run`, `extract_facts_stub()` no-op |
| `.vault-ko/prompts/g-eval-template.md` | 4.2KB | G-Eval prompt v0.1 (4-dim CoT scoring, JSON output) |
| `.vault-ko/README.md` | 2.0KB | Sprint status, 6-week plan, hot-reload threshold |
| `02-Projects/superintelligent-vault.md` | 4.5KB | 8-tengelyű projekt-táblázat + B-1 acceptance criteria + sikermetrikák |
| `04-Tasks/Backlog.md` | +11 task | B-1 Week 1-6 explicit, plus 7 future-sprint placeholder |
| `02-Projects/Index.md` | +1 sor | 🔬 Kutatás csoportban új sor |
| `.gitignore` | +5 sor | `.vault-ko/facts.db*` excluded |

**Funkcionális kód:** NULLA. Az `extract_facts_stub()` üres lista-t ad vissza. **De `--help` működik, `--dry-run` runnable** — wiring OK.

## Mit NE csinálj Day 0-n

- ❌ **API-integration** (Haiku/Sonnet hívás) — az Week 1 a kalibráció után, mert minden API-call cost
- ❌ **Real-extractor / -classifier kód** — a calibration-data dönti el a prompt-fine-tuning irányát
- ❌ **G-Eval threshold-routing live** — Week 3 shadow mode-tól kezdődik csak
- ❌ **Production cron-hookolás** (pl. `/11.11stop`-ba integráció) — előbb a script működjön Week 2-ben

## Mit IGENIS csinálj Day 0-n (kód-szintű low-risk komponensek)

A „skeleton ≠ no-op" elv: ha a kód-szintű impl **<20 sor és no-API**, írd meg már Day 0-n. Az ilyen komponensek azonnal hasznosak Week 1 baseline-ra, és **nem éri meg stub-nak hagyni amit nem kell**.

| Komponens | Day 0-n megírható? | Indok |
|---|---|---|
| **Determinisztikus parser** (regex, heurisztika) | ✅ IGEN | Pl. B-3 L1 eval — Quality A/B/C bucket egyetlen `--dry-run` futtatással baseline ad |
| **Frontmatter audit** | ✅ IGEN | Pl. B-4 `skill-canonicalize --audit` — 534 SKILL.md compliance scan, ~30 sor |
| **CLI argparse + --help + --dry-run** | ✅ IGEN | Mindig — `--help` runnable a wiring-checkre kell |
| **Filesystem traversal** (mkdir, file-discovery) | ✅ IGEN | Pl. B-5 `vault-nb-sync` — 17 projekt detect dry-run |
| **Status-snapshot** (event-log read, JSONL parse) | ✅ IGEN | Pl. B-6 `event-log-monitor --status` — read-only, no side-effect |
| **Safety-gate / ENV-flag check** | ✅ IGEN | B-8 RSI scripts mind exit-elnek ha `RSI_MODE != enabled` — kötelező Day 0-tól |
| **LLM-API hívás** (Haiku, Sonnet) | ❌ NEM | Költséges, kalibrációs-data nélkül rossz prompt → Week 1+ |
| **Docker container start** | ❌ NEM | Telepítési overhead — Week 1 Day 1 |
| **External service integration** (NotebookLM, MCP-server live) | ❌ NEM | Network-dependency, retry-pattern kalibráció kell |

**Ökölszabály:** ha read-only + lokális + <20 sor, **írd meg Day 0-n**. Ha write/state-changing vagy >20 sor, **stub Day 0-n, real Week 1**.

### Élő visszaigazolás (2026-05-13 SV B-3 sprint)

A B-3 Continuous evaluation Day 0-án (2026-05-12 20:55) a `.vault-eval/scripts/eval-l1-parser.py` ~110 sor pure-Python regex + heurisztika lett — no API, no Memgraph, no LlamaIndex dep. **Week 1 Day 1-én (2026-05-13 08:05) csak `eval-l1-parser --backfill` futtatás kellett** — 5 másodperc alatt 52 closed session-en quality-distribution baseline:

```
[write] 52 → /tmp/vault-eval/eval-l1-2026-05-13.jsonl
  Quality distribution: {'A': 43, 'B': 1, 'skip': 8}
```

**Nettó eredmény:** Day 0-n megírt 110 sor kód, Week 1 első órájában **azonnal hasznos baseline** további kódolás nélkül. Az ökölszabály visszaigazolva — a kód-szintű <30 sor + no-API komponensek Day 0-n megírva azonnali ROI-t adnak.

### Élő visszaigazolás 2. iteráció (2026-05-13 SV B-2 Week 1)

A B-2 sprint Day 0-án (2026-05-13 06:25) a `.vault-memory/scripts/{vault-embed,vault-search}.py` skeleton-okban már megvolt az **argparse + file-traversal + dry-run + chunk-method választás** (~150 sor placeholder + CLI). Week 1 Day 2-3-án (2026-05-13 08:30-09:00) **csak skeleton→real swap** kellett: a placeholder `embed_stub()` és `search_stub()` helyére bge-m3 + mgclient kód (~50 sor új kód a 4 placeholder helyén).

**Mérve:**

| Komponens | Day 0 (skeleton) | Week 1 (real swap) | Skeleton-előny |
|---|---|---|---|
| `vault-embed.py` | ~100 sor (argparse + traversal + stub) | ~60 sor új (chunkolás + bge-m3 + Cypher CREATE) | 5× gyorsabb |
| `vault-search.py` | ~70 sor (argparse + format-result + stub) | ~30 sor új (encode + cosine + sort) | 6× gyorsabb |

**Általánosítás:** ha Day 0-n complete-shape skeleton van (CLI + I/O + stub-function-signatures), Week 1 implementation **~5× gyorsabb** mint nulláról kezdeni — a I/O-boilerplate és error-handling már kész, csak a domain-logic-ot kell behúzni a stubok helyére.

### Élő visszaigazolás 3. iteráció (2026-05-13 SV B-2 Week 3 — skeleton+infra→UX-pipeline)

A B-2 Week 3 Day 1-2 (`load-session-context` skill rewrite) különleges minta: **NEM csak skeleton→real swap**, hanem **skeleton + B-2 Memgraph infra + B-4 SKILL-search → UX-rewrite**:

| Komponens | Mikor készült | Méret | Cél |
|---|---|---|---|
| `load-session-context/SKILL.md` skeleton | 2026-04-30 (B-2 előtti) | ~110 sor aggressive cat-pattern | régi UX |
| `.vault-memory/scripts/vault-search.py` (B-2 Week 1) | 2026-05-13 08:30 | ~70 sor real impl | semantic-search foundation |
| `.vault-memory/scripts/vault-context-load.py` | 2026-05-13 09:20 ⭐ | ~180 sor new | **MemGPT virtual rewrite** |
| `load-session-context/SKILL.md` v2 | 2026-05-13 09:20 ⭐ | ~120 sor MemGPT pattern | **UX-csere** |

Total **~30 perc** Week 3 implementation, mert a B-2 Memgraph + bge-m3 már fut, és a Day 0 skeleton-pattern már bevett. **UX-impact:** 15-20K → ~5K token context-load + 30s → <10s wall-clock per session-induláskor.

**Általánosítás 2:** ha (a) Day 0 skeleton + (b) Week 1 infra-szint élő, akkor (c) UX-rewrite Week 2-3-ban ~30 perc — a 3 réteg multiplikál.

### Élő visszaigazolás 4. iteráció (2026-05-16 SV B-1 Week 2 Crystallize-pipeline)

A B-1 Day 0 (2026-05-12, `.vault-ko/` skeleton + `facts.db` schema + script stubs) **3 hete** állt érintetlenül, üres `facts.db`-vel. 2026-05-16-án Week 2 implementation 1 session-en belül ~3 óra alatt:

| Komponens | Day 0 status (2026-05-12) | Week 2 mutation (2026-05-16) | Eredmény |
|---|---|---|---|
| `facts.db` schema | ✓ kész (47-soros SQL) | – | reusable |
| `vault-ko-ingest.py` skeleton | ✓ 140 sor placeholder | replace `extract_facts_stub` 2-phase subagent extractor-rel | functional Layer-1 |
| `prompts/g-eval-template.md` | ✓ kész (123 sor) | – | reusable |
| `calibration/sample-15-gold` | ✓ kész | + 15 synth-Fail | balanced 30-mintás benchmark |
| `11.11crystallize` script | hiányzott | new ~280 sor Python, 3 scorer-mode | functional Layer-2 |
| `vault-ko-query` | hiányzott | new ~150 sor Python | functional Layer-3 retrieval |
| `vault-ko-report` | hiányzott | new ~100 sor | user-facing summary |

**~3 óra wall-clock**, **$0 cost** (subagent-fanout), **1342 fact** a KO-DB-ben, **96.7% calibration agreement**. A 3-hetes Day-0 várakozás NEM holt-súly volt: a fájl-struktúra felgyorsította a script-lookup-ot, a Memory-context-loading szuper-tisztán hozta vissza a kontextust, és a meglévő G-Eval-template skipped 1-2 óra prompt-tervezést.

**Általánosítás 3:** **a Day 0 skeleton elavulhat 1-3 hetet** anélkül hogy a sprint elveszítse a velocity-t, mert a vault Karpathy-mintán fellépő file-as-state architektúrája rezilient a hosszú szünetre.

### Mit IGENIS csinálj Day 0-n — AUTO-GEN END marker pattern (bővítve 2026-05-13)

Minden olyan vault-fájlnál ami **auto-gen + emberi annotáció keveréke** (weekly cron rewrite + manuális kommentek), Day 0-tól tervezz `<!-- AUTO-GEN END -->` marker-pattern-t a script-be:

```python
# Aggregator script:
output_md = render_auto_gen_section()
existing = OUTPUT.read_text() if OUTPUT.exists() else ""
marker_idx = existing.find("<!-- AUTO-GEN END")
manual_tail = existing[marker_idx:] if marker_idx >= 0 else ""
final = output_md.rstrip() + "\n" + manual_tail.split("\n", 1)[1] if manual_tail else output_md
OUTPUT.write_text(final)
```

**Validált use-case-ek:**

| Fájl | Auto-gen script | Manual section |
|---|---|---|
| `06-Audits/System_Health.md` | `vault-cleanup --write` (vasárnap) | "Megnyitott kérdések" alá |
| `06-Audits/Eval_Trend.md` (új 2026-05-13) | `eval-l3-aggregator --write` | review-jegyzetek alá |

**Day 0 lépés:** ha új auto-gen audit-output készül, az aggregator-script ELSŐ commitja már tartalmazza a marker-handling-et. NE later-Week-2 retrofit, mert addig csak ütközés-veszély.

## Cascade pattern — több sprint Day 0-ja egyszerre

**Mikor érdemes single helyett cascade-t** (~2026-05-13 SV-cascade validálta):

| Feltétel | Single | Cascade |
|---|---|---|
| Egy projekt egy aktív sprint | ✅ | — |
| Egy projekt 3+ ADR-rel, mind Day 0-ra vár | — | ✅ |
| Sprint-ek függés-irányítottak (B-1 → B-2 → ...) | ✅ (előző Day 0 → következő tervezés) | — |
| Sprint-ek függetlenek (B-3/B-4/B-5/B-6/B-8 mind kódot ír) | — | ✅ |
| User-time-budget ~1 óra | 1-2 sprint | 5 sprint |
| User-time-budget ~25-30 perc | 1 sprint | — |

**Time-cost cascade-ben (mért 2026-05-13):**

| Komponens | Idő | Megjegyzés |
|---|---|---|
| Per-sprint fájl-írás (5-7 fájl) | ~10 perc | Repetitív, pattern-konform |
| Projekt-fájl 5× status update | ~5 perc | Single Edit hívás |
| Backlog 5× detailed expansion | ~10 perc | 5 új szekció (Day 0 ✅ + Week 1-3 tasks) |
| `.gitignore` update + chmod + verify | ~5 perc | |
| **Total 5 sprint Day 0** | **~30 perc** | (NEM 5 × 25 perc = 2+ óra) |

**Felgyorsító faktor:** a 2. sprinttől már a memóriában van a minta (mappa-struktúra, README-szakaszok, config-YAML-keret). A 3-5. sprintnél már 8-10 perc / sprint elég.

**NEM érdemes cascade:**
- Ha valamelyik sprint **éles funkcionalitást** is implementál Day 0-n (akkor single, fókuszáltabb)
- Ha az ADR-ek **konfliktusban vannak** egymással (előbb resolve, aztán cascade)
- Ha valamely sprintre **nincs még ADR** (előbb research + ADR)

## Validations (élő alkalmazások)

A playbook **2026-05-12-13-án 2 élő sprint Day 0**-ban validálódott — mindkettő ugyanazt a struktúrát követte, mindkettő ~30 perc alatt készült el:

| Sprint | Dátum | Mappa | Skeleton-fájlok | Day 0 idő |
|---|---|---|---|---|
| **B-1 Crystallization** | 2026-05-12 20:40 | `.vault-ko/` | schema.sql + facts.db + vault-ko-ingest.py + g-eval-template.md + README | ~30 perc |
| **B-2 Memory architecture** | 2026-05-13 06:25 | `.vault-memory/` | docker-compose.yml + vault-embed.py + vault-search.py + llamaindex-config.yml + README | ~25 perc |

**Konvergens minta** mindkét sprintnél:
- 1 mappa-prefix (`.vault-<feature>/`)
- 1 `README.md` (status + sprint-plan + cost-calc + backout)
- 1+ `scripts/<tool>.py` (skeleton, `--help`+`--dry-run` runnable, real impl no-op)
- 1+ `config/` vagy `prompts/` (YAML / md template-ek)
- 1 vault-projekt-fájl + Backlog + .gitignore update **ugyanabban a commitban**

**Time-cap:** ha a Day 0 >1 óra, valószínűleg már funkcionális kódot írsz — STOP, halaszd Week 1-re.

## Cross-sprint reuse — schema előbb mint kód

**Helyzet (2026-05-13 megtapasztalva):** a B-2 (Memory architecture, Memgraph + LlamaIndex) és B-7 (World-model / Knowledge graph) **közös infrastruktúrára épül** — ugyanaz a Memgraph DB, ugyanaz az entity-graph. Két sprint, egy schema.

**Tanulság:** ha sprint-X és sprint-Y közös data-ra / schema-ra / DB-re épül, **a schema-t előbb komititáld**, mint bármelyik konkrét sprint kódját. Ez:
1. **Single source of truth** — egy fájl, mindkét sprint reuse-olja
2. **Out-of-order sprint-rendezés OK** — B-7 schema-YAML 2026-05-12-én készült, B-2 másnap reuse-olta inputként
3. **Validation early** — ha a schema rossz, mindkét sprint kódolása sérül; jobb előbb kideríteni

**Konkrét B-2/B-7 példa:** [[00-Meta/graph-schema.yml]] (9 entity + 6 relation) → LlamaIndex `SchemaLLMPathExtractor` input a B-2 Week 1-ben + Cypher schema-init Memgraph-ba a B-7 Week 1-ben. Egy YAML, két sprint.

**Sprint-sequence general rule:**
```
1. Shared schema / data-model     (Day 0, owner: korábbi sprint)
2. Shared infrastructure          (Day 0, owner: integrátor sprint)
3. Sprint-X specific integration  (Week 1-2)
4. Sprint-Y specific integration  (Week 1-2)
5. Cross-sprint bridge / handoff  (Week 2-3, ha kell)
```

## A skeleton-first és a Karpathy LLM-Wiki

A skeleton-first commit a [[11-wiki/Karpathy-LLM-Wiki-pattern]] „compilation" fázisának analógiája: nyers ADR → kezdetleges working memory (skeleton) → később reflective compilation (Week 1-2 kalibráció) → semantic memory (production sprint Week 3+). A vault-ban ez **konkrétan láthatóvá teszi a tudás-folyam** legyen.

## Backout-plan

Day 0 commit **mindig revertable** — Day 1-én se a kód, se a Backlog tasks nem hatnak függvény-szinten a meglévő vault-flow-ra. ENV-flag (`<sprint>_MODE=disabled`) vagy egyszerű git revert lemossa.

## Élő visszaigazolás 5. iteráció (2026-05-17 — SV B-1 teljes ingest)

**Mintabizonyíték** a Day-0-skeleton-pattern produktivitására: a SV B-1 sprint Day-0 commit-ja 2026-05-12-én (KO-DB schema + 2-phase pending-pattern subagent-fanout + skeleton-script) **mai napon (2026-05-17)** lehetővé tette a teljes vault (173 fájl: 76 wiki + 28 ADR + 69 session) ingest-elését **3 óra wall-clock alatt** — Anthropic API kulcs nélkül, 174 párhuzamos subagent-tel, $0 cost. A pattern ennyiszer él már:

| # | Dátum | Sprint / feladat | Day-0 → Week N gyorsulás |
|---|---|---|---|
| 1 | 2026-04-30 | smoke-teszt mechanika scaffold | 1 commit → 1 hét scale-up |
| 2 | 2026-05-12 | SV B-1..B-8 (8 sprint) Day-0 | 8 commit → 4 hét parallel build |
| 3 | 2026-05-16 | SV B-1 Week 1+2 (cryst pipeline) | 3 hetes skeleton → 3 óra full-build |
| 4 | 2026-05-16 | G-Eval 30-mintás calibration | Day-0 prompt → 96.7% agreement |
| **5** | **2026-05-17** | **SV B-1 backfill TELJES (12 300 triplet)** | **Day-0 schema → 173 fájl ingest 3 óra alatt** |

A Day-0-skeleton ROI metrika: **5/5 elnyúlt sprint közvetlen visszatekintve a Day-0 commit-tól indul**, ez nem véletlen.

| 6 | 2026-05-17 | Week-1-α uniformity 3 sprint párhuzam | template-érettség |

### Élő visszaigazolás 6. iteráció (2026-05-17-2 — Week-1-α uniformity pattern)

A `2026-05-17-obsidian-vault-2` session során **3 új Week-1-α sprint mind UGYANAZT a skeleton-first pattern-t követte**: GEPA prompt-mutator (B-8), auto-skill distill (B-4+B-8), vault-coherence-check (B-3+B-1). Mindegyik:

- ENV-flag default OFF (`VAULT_RSI_APPLY=0`, `VAULT_COHERENCE_CHECK=0`)
- Detect-only / dry-run-only Week 1 (0 vault-mutáció)
- Real apply Week 2+ subagent-fanout-tal
- Audit-MD + Next-step-list

**Tanulság:** a Week-1-α skeleton-first ennyire uniform pattern-t ad, hogy érdemes **template-elni** — pl. `/root/.vault-config/sprint-template/week-1-alpha-skeleton.md` checklist (4 readiness criteria). Reusable a B-3/B-5/B-6/B-7 Week 2+ kickoff-okra is.

## Realpath-dedup discipline (2026-05-17 finding)

**Minden vault-audit-scriptnek `realpath` dedup-ot kell az első lépésben.** A B-4 SKILL.md baseline 2026-05-13-on "534 fájl"-t számolt, valójában 462 — `.claude/skills` és `.codex/skills` mind symlink `.agents/skills`-re, így 3×-os duplikáció. Pythonban:
```python
seen = set()
for f in candidates:
    real = f.resolve()    # follows symlinks
    if real in seen:
        continue
    seen.add(real)
    # ... process f
```
Skill-audit, embed-audit, chunk-count, file-listing — **mind** ide tartoznak.

## Kapcsolódó

- [[02-Projects/superintelligent-vault]] — élő példa (B-1..B-8)
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — háttér-minta
- [[11-wiki/Crystallization-protocol]] — Day-N session-ritálé
- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — első alkalmazás (B-1)
