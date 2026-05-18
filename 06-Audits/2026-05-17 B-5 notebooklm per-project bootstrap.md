---
name: B-5 NotebookLM per-project bootstrap (Phase B Sprint 1 landolt)
type: audit
slug: 2026-05-17-b5-notebooklm-bootstrap
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "sv-8", "notebooklm", "bootstrap", "cognitive-layer"]
related: ["[[11-wiki/sv-08-notebooklm-cognitive-layer]]", "[[02-Projects/superintelligent-vault]]", "[[02-Projects/mfl-voice]]"]
---

# B-5 NotebookLM per-project bootstrap — Phase B Sprint 1 landolt

## TL;DR

A `notebooklm-bootstrap-project <slug>` parancs **éles** — `/usr/local/bin/notebooklm-bootstrap-project`. Egy projekt-slugból automatikusan létrehoz egy NotebookLM-notebookot, source-eli a projekt-fájlt + linked wikiket + utolsó N session-t, és a `notebooklm:` ID-t visszaírja a projekt-frontmatterbe. Audit-log JSONL-ben `06-Audits/notebooklm-bootstrap-YYYY-MM-DD.jsonl`-be.

**Élesít a B-5 Phase B Sprint 1** (lásd [[11-wiki/sv-08-notebooklm-cognitive-layer#Sprint 1 — Per-projekt notebook-pool (1 hét)]]). Validálta: **mfl-voice** projekten élesben — 5 source (1 project + 3 wiki + 1 session) feltöltve, status: `ready`. NB-ID: `cd6988ae-2b88-4a43-867d-a2aea46ad4e4`.

## Mi sikerült

| Elem | Status | Megjegyzés |
|---|---|---|
| Script létrehozva | ✅ | `/usr/local/bin/notebooklm-bootstrap-project` (executable Python3) |
| CLI design | ✅ | `<slug> [--name] [--max-wikis N] [--max-sessions N] [--dry-run] [--force]` |
| Existing-NB guard | ✅ | Projekt-frontmatter `notebooklm:` mezőt detektál, `--force` nélkül halt |
| Wikilink-resolver | ✅ | `[[link]]` regex + 11-wiki/ szűrés + glob-fallback |
| Session-finder | ✅ | `08-Sessions/*<slug>*.md` substring match, ISO-prefix → newest-first |
| Notebook-creation | ✅ | `notebooklm create <name> --json` → ID parsolva |
| Source-add | ✅ | per-source loop, `--type file --mime-type text/markdown`, failure-tracking |
| Frontmatter-writeback | ✅ | `notebooklm: <id>` + `updated:` bump (in-place YAML) |
| Audit-JSONL | ✅ | `06-Audits/notebooklm-bootstrap-YYYY-MM-DD.jsonl` (append) |
| Dry-run mode | ✅ | Tervet kiír, nem hív CLI-t, nem ír fájlt |
| Live teszt (mfl-voice) | ✅ | NB `cd6988ae-2b88-4a43-867d-a2aea46ad4e4`, 5/5 source `ready` |

## Mi blokkolt

- **Egy sem** — auth élt (`SV-1 Memory architecture` notebook aktív kontextusként visszaadta a `status`-on), CLI minden parancsra OK-kal válaszolt, rate-limit nem ütött be 5 source-nál.
- **Megfigyelt limit a `notebooklm-py` wrapperben:** a `source add` egyenként megy (nincs bulk-add API a community CLI-ben) → 20-50 source-nál percekbe telhet. Optimalizáció a Sprint 2-ben (parallel + retry) érvényesülhet, de MVP-hez egyenkénti elég.

## Tesztelt projekt

**mfl-voice** ([[02-Projects/mfl-voice]]):
- Forrás-pool: 1 projekt + 3 wiki (gemini-3-1-flash-tts-pipeline, mfl-voice-jarvis-mother-research, gemini-2-5-flash-thinking-budget) + 1 session (2026-05-15-mfl-voice-sprint-1)
- NB-ID: `cd6988ae-2b88-4a43-867d-a2aea46ad4e4`
- Idő: ~30s (notebook-create + 5× source-add szekvenciálisan)

## Audit-fájl

- **Ez:** `/root/obsidian-vault/06-Audits/2026-05-17 B-5 notebooklm per-project bootstrap.md`
- **Live audit (JSONL):** `/root/obsidian-vault/06-Audits/notebooklm-bootstrap-2026-05-17.jsonl`

## Mi következik

### Azonnal (Sprint 1 follow-up)

- [ ] Bulk-bootstrap az aktív projektekre — kgc-berles, kgc-marketing, mapesz, boulium, koko, teszt-eu. Egyszer kell futtatni, és onnantól mindegyiknek lesz "agya". (~10 projekt × 30s = ~5 perc)
- [ ] Az **mfl-voice** notebookra `notebooklm ask "Milyen state-ben van most az MFL-Voice projekt, mit kell elindítani Sprint 2-ben?"` — verifikálja, hogy a source-grounded Q&A a kontextusból ad konkrét választ.

### Heti auto-cron (Sprint 2 felé)

- [ ] Vasárnap esti cron: minden projekt-notebookhoz **delta-source-refresh**:
  - Új session-ök (`08-Sessions/*<slug>*.md` az utolsó futtatás óta) → `notebooklm source add ...`
  - Módosult wiki-k → `notebooklm source refresh -s <SOURCE_ID>` (CLI támogatja)
  - Audit-log: `06-Audits/notebooklm-refresh-YYYY-MM-DD.jsonl`
- [ ] Script-name: `/usr/local/bin/notebooklm-refresh-projects` — minden projekt-frontmatterben `notebooklm:` mezővel rendelkező projektet iterál, delta-add. Cron-line: `0 4 * * 0` (vasárnap 04:00, igazodva a vault-cleanup-hoz).

### Karpathy-réteg-illeszkedés

Ez a script a **semantic-memory réteg implementáció** a Karpathy-mintában (lásd [[11-wiki/Karpathy-LLM-Wiki-pattern]]):
- working memory = aktív session
- episodic = `08-Sessions/*<slug>*.md`
- **semantic = per-project NotebookLM (most élesítve)** ⭐
- meta = közös vault-meta NB (B-5 Sprint 3 = 11.11stop crystallization-hook)

## Kapcsolódó

- [[11-wiki/sv-08-notebooklm-cognitive-layer]] — B-5 axis research, ez a Sprint 1 implementációja
- [[02-Projects/superintelligent-vault]] — SV master tracker
- [[11-wiki/notebooklm-headless-login-fifo]] — auth-pattern ami élesíti a CLI-t
- [[11-wiki/notebooklm-cli-gotchas]] — `--json` empty-ID, retry-pattern (script már implementálja)
- [[02-Projects/mfl-voice]] — első élesített projekt-NB
