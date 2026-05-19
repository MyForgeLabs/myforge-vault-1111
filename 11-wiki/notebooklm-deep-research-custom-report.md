---
name: NotebookLM deep research + custom report flow
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#service/notebooklm", "#research"]
---

# NotebookLM — Deep Research + Custom Report flow

A NotebookLM CLI-val ($0 cost) lefuttatható egy **deep research** ami new
sources-okat keres + importál a notebook-ba, plus egy **custom report-artifact**
ami az import-ált source-okból strukturált markdown-output-ot generál.

## A teljes flow

```bash
# 1. Pick a notebook (Boulium pl.)
notebooklm use d5b163f1

# 2. Launch deep research (queue-szerű, non-blocking)
notebooklm source add-research "<query>" --mode deep --no-wait
# Output: Task ID: a3979943-9931-...

# 3. Wait for all running research-tasks (auto-import sources)
notebooklm research wait --import-all      # blocking, ~10-30 min

# 4. Generate a custom report with explicit section list
notebooklm generate report "<long custom prompt with required sections>" --format custom
# Output: Started: 5f282621-6f40-...

# 5. Wait for artifact
notebooklm artifact wait 5f282621 --timeout 600

# 6. Download to local path
notebooklm download report -a 5f282621 /target/path/report.md
```

## A nyerő query-pattern

**Általános "petanque rules" kérdés → 2-3 generic source**.
**Specifikus + target-szövetségek + konkrét rules-listák → 5-7 hivatalos source.**

Példa (Boulium 2026-05-19 → 5 source):

```
Pétanque tournament formats and federation rules worldwide:
FIPJP international rulebook, FFPJP France Geslico classification
(Promotion/Honneur/Élite E1/E2/E3), MAPESZ Hungary, FBJB Belgium,
Pétanque Suisse qualificatif, FPUSA, Asian Pétanque Confederation.
Detailed scoring rules and protocols for:
Tête-à-tête / Doublette / Triplette / Mêlée-Brisure /
Tir de précision (5 stations 20 shots) / Tir progressif /
King-of-the-court / Pool+Bracket large 64-128 player tournaments /
Double elimination / Concours qualificatif.
Match standards: target scores (11/13/15), time limits,
boules per player, officials roles.
What does a digital platform need to support each region's standards?
```

Eredmény: hivatalos szabálykönyv-PDF-ek (FPUSA-condensed, FBJB Reglement 2025-2026),
YouTube-tutorialok, plus i18n-platform-comparison.

## Custom report-prompt — explicit section list

A `--format custom`-mal a prompt-od **konkrét szekciókat sorol fel** — az output
strukturáltan ezekkel a header-ekkel jön vissza:

```
Output: strukturált markdown briefing-doc EZEN szekciókkal:
1) Régió-mátrix (per-szövetség: classification tier-ek, licensz-rendszer,
   ranking-számítás).
2) Versenyform-katalógus (FIPJP-hivatalos versenytípusok pontos szabályaival).
3) Algoritmikus bajnokság-struktúrák.
4) Tir de précision EXACT szabályok.
5) Klub-management feature-listák.
6) Konkrét adatmodell-javaslatok Boulium-Drizzle-schemára.
7) Phase 2 prioritás-finomítás a research-findingek alapján.
```

Boulium-output: 7-szekciós markdown, ~106 sor, 7.3 KB. NotebookLM tisztán
megőrizte a számozott szekciókat, plus tényleges idézeteket adott a hivatalos
források-ból (FIPJP Article 1-41, Gracket v2.1 library reference).

## Cost & speed

- **$0** — NotebookLM consumer-tier
- Deep research: **10-30 perc** queue + processing
- Custom report: **5-10 perc** artifact generation
- Background-able mindkettő (`--no-wait` flag + `research wait` / `artifact
  wait` later)

## CLI quirks ([[notebooklm-cli-gotchas]] is tartalmazza)

- `download report -a <id> <path>` — NEM `-o <path>` (option NEM létezik)
- `research wait --import-all` az ÖSSZES running research-re vár, NEM csak az
  utolsóra
- `artifact wait <id> --timeout 600` — default 60s sokszor kevés deep custom
  report-hoz, legyen 10 perc

## Mikor használjuk

- **Phase planning / roadmap-validation** — pl. Boulium Phase 2 a 2026-05-19-i
  research-szel: 8 schema-bővítés vs. 13 javaslat (a riport 5-öt elvetettünk
  mint overkill)
- **Verseny-kompliance research** — FIPJP / FFPJP rule-szövegek elsődleges
  forrásként
- **Competitor analysis** — software-feature-listák, pricing, gaps
- **Multi-region adaptation** — pl. melyik feature kell HU/FR/DE/BE-ra

## Mikor NE használjuk

- Frissen-bekerült terminológiát kell explain-elni — a notebook nem ismeri
- Real-time data (árfolyam, time-sensitive news) — NotebookLM web-search
  tipikusan stabil source-okra céloz, nem live-feed-re
- Privát/sensitive code-review — a `source add-research` PUBLIC web-search-et
  indít

## Boulium-példa (2026-05-19)

2 deep research párhuzamosan + 1 custom report = **$0**, ~20-25 perc total
background-time. Output integrálva:

- 5 új source a Boulium notebook-ban (709 → 714)
- `docs/research/2026-05-19-phase2-deep-dive.md` 106-sor briefing
- ADR `07-Decisions/2026-05-19 Boulium Phase 2 roadmap.md` Research-validation
  szekcióval, 7 schema-bővítés rationale-szel
- 5 átvenni-NEM-átvenni döntés explicit dokumentálva (Yjs CRDT, Stream Chat,
  Clerk auth, BoulOmeter AR, Apple Verified Identifier — mind NEM)

## Kapcsolódó

- [[notebooklm-cli-gotchas]] — CLI-quirks
- [[notebooklm-seo-competitor-research-pattern]] — másik research-flow
- [[notebooklm-headless-login-fifo]] — auth-setup
