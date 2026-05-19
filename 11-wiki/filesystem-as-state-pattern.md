---
name: Filesystem-as-state pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/reference"]
tag_backfill: 2026-05-19
---
# Filesystem-as-state pattern

> [!info] Mit hív életre
> Az **agent állapotát** (memória, decision-trail, work-in-progress) **fájlrendszer-fájlokba** írja minden lépésnél, nem in-memory-objektumokba. A következmény: a chat-history-ból a teljes state visszaolvasható, multi-agent handoff jelszó-nélkül megy, és a git története maga a session-log.

## A pattern lényege

A klasszikus chat-agent in-memory tartja a state-et (context-window). Probléma: ha az agent meghal, ha kontextus túlcsordul, ha másik subagent kell folytatnia → adatvesztés. A **filesystem-as-state** ezt fordítja meg:

1. **Minden komponens fájl** — session-log, decision-log, todo-list, memory, agent-config
2. **Az agent fájlokat ír/olvas** — nem object-state-et passzol funkcióknak
3. **A "context-loading"** = `cat` a releváns fájlokról a beszélgetés elején
4. **A "context-saving"** = `Write` / `Edit` a releváns fájlokba a beszélgetés végén

A pattern az [Anthropic Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) javaslata, és a [Karpathy LLM-Wiki minta](Karpathy-LLM-Wiki-pattern.md) kanonikus alapja.

## Konkrét megvalósulás (vault)

A `/root/obsidian-vault/` vault egy filesystem-as-state implementáció multi-agent-re:

| Komponens | Hol fájl | Mit tárol |
|---|---|---|
| **Agent-konfig** | `AGENTS.md` (symlink-elve `~/.claude/CLAUDE.md` + `~/.codex/AGENTS.md` + `~/.gemini/GEMINI.md`) | Közös agent-utasítások |
| **Session-state** | `08-Sessions/<slug>.md` | Aktuális beszélgetés timeline + events |
| **Decision-trail** | `07-Decisions/YYYY-MM-DD <téma>.md` | ADR-szerű döntési napló |
| **Long-term memory** | `05-Memory/*.md` (User, Infrastructure, Skill-map) | Perzisztens user-profil + infra-fact |
| **Project state** | `02-Projects/<slug>.md` | Egy-projekt-egy-fájl, status + history |
| **Todo-state** | `04-Tasks/Backlog.md` | Obsidian Tasks plugin emoji-syntax (`✅` / `🔴` / `🟡`) |
| **Crystallized knowledge** | `11-wiki/<slug>.md` | Evergreen tudás, saját szavakkal |
| **Raw input** | `10-raw/YYYY-MM-DD — <forrás>.md` | Cikkek, transcriptek immutable formában |

## Miért fájl, miért nem DB

| Szempont | Fájl-alapú | DB-alapú |
|---|---|---|
| **Verziókezelés** | git out-of-the-box | DB-dump cron-nal vagy WAL |
| **Multi-agent handoff** | másik agent `cat` + Read tool | API + auth + schema-egyezés |
| **Audit-trail** | git log = lépésről-lépésre | trigger-table vagy event-sourcing |
| **Diff-elhetőség** | `git diff` natív | DB-specifikus tool |
| **Offline-szerkesztés** | bármilyen editor + sync git-pull | online connection kell |
| **Search** | grep / ripgrep / Obsidian | SQL / full-text-index |
| **Privacy** | local-only mindaddig amíg push nincs | mindig server-side |
| **Performance large-scale** | ~10K fájl-ig OK, utána lassú | skálázódik |

A vault filozófia: **filesystem-first** amíg lehet, indexelő rétegek **csak ezt tükrözik** (Memgraph vektor-index, KO-DB SQLite triplet-tár, embedding-cache). A fájl marad a Source-of-Truth.

## Karpathy-féle séma-réteg

Karpathy LLM-Wiki cikke 3 réteget definiál:
- **Raw layer** (`10-raw/`) — immutable, ahogy érkezett (cikk, transcript)
- **Wiki layer** (`11-wiki/`) — evergreen, saját szavakkal desztillált
- **Glossary layer** (`00-Meta/Glossary.md`) — slug-feloldó index

A Karpathy-pattern szerint a "raw" sosem szerkesztődik, csak ide-érkezik. A wiki-rétegbe csak **desztillált** tudás kerül — a session-log az átmeneti puffer.

## Anti-patternek

| Antipattern | Mi a baj | Helyes |
|---|---|---|
| **In-memory + cron-snapshot** | Crash = elveszett state két snapshot között | Inline-write minden lépésnél |
| **Single-mega-file** | `everything.md` 50MB → grep lelassul, git-diff hasznavehetetlen | Per-koncepció-fájl + index |
| **DB + symlink trick** | DB-ben az igazság, fájl csak export → drift | Fájl az igazság, DB csak index |
| **No-frontmatter** | YAML hiánya → Obsidian Dataview ki nem tudja olvasni a type/status mezőket | Minden fájl `type:` + `created:` + `updated:` frontmatter-rel |
| **No-wikilink** | "lásd a .../valami.md fájlt" stringként → linter nem ellenőrzi | `[[02-Projects/<slug>]]` mappa-prefix-szel |

## Bővítmény: indexelő rétegek a fájl fölött

Filesystem-as-state nem zárja ki az indexeket:
- **Memgraph** (`bolt://localhost:7687`) — entity-graph + native vector-search (`bge-m3`)
- **KO-DB** (`.vault-ko/facts.db`) — triplet-tár SQLite, 13801 fact
- **Embed-cache** — sentence-transformers chunks
- **Obsidian Dataview / Bases** — UI-réteg

Ezek **mindig regenerálhatók a fájlból** (vault-embed --backfill / vault-ko-ingest --file). A fájl marad a kanonikus.

## Implementációs checklist

- [ ] Minden agent-state-komponensnek dedikált fájl-helye
- [ ] Frontmatter minden fájlon (`type`, `created`, `updated` minimum)
- [ ] Wikilink minden cross-referencia helyett path-string
- [ ] Git-commit minden agent-session után (autosave 10 perc + 11.11stop)
- [ ] Index-rétegek **regenerálhatók** a fájlokból (idempotens backfill-script)
- [ ] Multi-agent: közös AGENTS.md symlink, NEM per-agent másolatok
- [ ] Session-end ritual: minden ideiglenes state-et committolni vagy `08-Sessions/_archive/`-ra mozgatni

## Source-evidence (KO-DB)

- 9 distinct subject 17 fact-tal, **3 source-type** (adr + session + wiki) — `filesystem-as-state` token
- Top-source: `11-wiki/Karpathy-LLM-Wiki-pattern.md` + `11-wiki/Kepano-File-over-App-filozofia.md` + `07-Decisions/2026-05-12 sv-1 memory architecture arch.md`
- Kapcsolódó pattern: Anthropic "Code Execution with MCP" (file-handle output ≠ in-memory return)

## Kapcsolódó

- [[Karpathy-LLM-Wiki-pattern]] — raw + wiki + glossary séma
- [[Kepano-File-over-App-filozofia]] — Obsidian Kepano filozófia
- [[Johnny-Decimal-prefix]] — miért 00-, 01-, 02- prefix
- [[Auto-context-loading]] — fájl-állapot-betöltés session-induláskor
- [[sv-01-memory-architecture]] — 5-rétegű memory ezen a fájl-alapon
- [[audit-log-append-only-pattern]] — speciális filesystem-as-state ahol az írás csak append
