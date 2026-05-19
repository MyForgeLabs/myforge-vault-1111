---
name: 2026-05-18 atomic-write 11.11crystallize + MEDIUM-2
type: audit
created: 2026-05-19
updated: 2026-05-19
tags:
  - audit
  - atomic-write
  - vault-tools
  - sv-b1
  - crystallize
---

# atomic-write 11.11crystallize + MEDIUM-2 wrap-up

Az [[2026-05-18 atomic-write HIGH-3 migration]] follow-up: a fennmaradó **8 write-site** atomic-write migrációja **4 scriptben**. Ezzel a Layer-1 atomic-write védelem a vault-cluster **fő mutátorain** komplett (kivéve a tudatosan SKIP-elt LOW-rizikó site-okat).

## A — `11.11crystallize` (5 write-site) — kritikus G-Eval pipeline

| L# | Funkció | Cél | Rizikó | Csere |
|---|---|---|---|---|
| 304 | `critic_review_request` — Layer-4 pending JSON | `.vault-ko/critic-pending/<slug>.request.json` | **MAGAS** — sub-agent egyidejű read truncated JSON-ról → Critic-review fél-input |
| 385 | wiki create (auto-crystallize new) | `11-wiki/<slug>.md` | **MAGAS** — half-write evergreen wiki → broken-wikilink + Obsidian fél-render |
| 406 | ADR draft create | `07-Decisions/<slug>.md` | **MAGAS** — half-write ADR → audit-trail korrupt |
| 617 | claude-code-scorer pending JSON | `.vault-ko/scorer-pending/<slug>.request.json` | **MAGAS** — G-Eval subagent read truncated → Pass/Fail-mismatch |
| 1243 | `CRYSTALLIZE_IN_PROGRESS_FLAG` | `.vault-ko/.crystallize-in-progress` | KÖZEPES — pre-commit hook olvas; partial-write → "?-state" |

A pontosítás kedvéért: a user-jegyzet "L385/L406 session-body re-write" megfogalmazása **nem pontos** — ezek **wiki + ADR create** site-ok (új-fájl, nem session-body re-write). Ettől függetlenül **HIGH-rizikó**, mert új evergreen / immutable artefactot teremtenek a vault-ban. Az auditban tartom a HIGH minősítést.

A `with open(target, "a")` append-write site-ok (L367 MEMORY.md append, L387 wiki update append, L863 audit-log) **nem lettek migrálva** — POSIX `O_APPEND` < PIPE_BUF (4096B) garanciára támaszkodnak, ami a `vault_atomic` modul saját doc-ja szerint elfogadott.

## B — MEDIUM-2 csomag (3 script, 3 write-site)

| Script | L# | Cél | Helper |
|---|---|---|---|
| `vault-net-watch` | 156 | weekly cron audit MD (`06-Audits/net-watch-<ISO-week>.md`) | `atomic_write` |
| `vault-github-trending-recurrence` | 130 | weekly cron audit MD | `atomic_write` |
| `vault-github-trending-recurrence` | 151 | suggestion JSON (`/root/.vault-config/github-trending-cherry-pick.json`) | `atomic_write_json` |
| `vault-graph-retype` | 1005 | fanout request JSON (per batch) | `atomic_write_json` |

A `vault-github-trending-recurrence` L151 átírásánál a JSON-encoding `atomic_write_json`-re egyszerűsítve (indent=2 default-ja egyezik az eredeti hívás formátumával).

## Pattern (mind 4 scriptben)

```python
sys.path.insert(0, '/root/obsidian-vault/.vault-tools/lib')
from vault_atomic import atomic_write  # noqa: E402
# vagy: from vault_atomic import atomic_write, atomic_write_json
```

`encoding="utf-8"` paraméter mind az 5 write-site-on (ahol szerepelt) megőrizve — `atomic_write` szignatúra-kompatibilis (a tényleges encode-ot ő végzi, ezért redundáns de nem hibás).

## Verify

**py_compile (mind 4 OK):**

```
OK 11.11crystallize
OK vault-net-watch
OK vault-github-trending-recurrence
OK vault-graph-retype.py
```

**Functional smoke (--help mind 4-en):**
- `11.11crystallize --help` → argparse-output változatlan (slug + 5 flag listázva).
- `vault-net-watch --help` → argparse-output változatlan (--config / --dry-run / --only).
- `vault-github-trending-recurrence --help` → argparse-output változatlan (--days / --top / --json).
- `vault-graph-retype.py --help` → argparse-output változatlan (--dry-run / --reset / --phase stb.).

**Round-trip helper-test:**
- `atomic_write(str)` → read-back OK
- `atomic_write_json` → JSON round-trip OK
- `atomic_write(json.dumps(...))` (a 11.11crystallize pattern) → JSON parse OK

## Diff summary

```
11.11crystallize                    +3 / -5   (import + 5 write-site cseré)
vault-net-watch                     +3 / -1   (import + 1 write-site)
vault-github-trending-recurrence    +4 / -2   (import + 2 write-site)
vault-graph-retype.py               +3 / -1   (import + 1 write-site)
```

Összesen: **+13 / -9 sor**, NULL viselkedés-változás.

## Mérnöki őszinte — LAYER-1 komplett-e?

**NEM TELJESEN.** Két csoport-maradék:

### B/1. Tudatosan SKIP-elt LOW-rizikó site-ok (előző audit-ban azonosítva)

| Script | L# | Indoklás |
|---|---|---|
| `vault-auto-disable-check` | 196 | <100B flag-file, single-write, kernel-atomic |
| `vault-stats-generator` | 169 | `tmp` változó — intermediate-pattern, downstream rename |
| `vault-selfcheck` | 115 | belső self-check, nem-publikus response |

Ezek **szándékos kihagyások**, nem regresszió.

### B/2. Még nem-átnézett scriptek (ezt a wrap-up nem fedte le)

A friss `grep "write_text|write_bytes" /usr/local/bin/` további site-okat talált, amik ELŐZŐ auditban nem szerepeltek:

| Script | L# | Cél | Rizikó-becslés |
|---|---|---|---|
| `vault-wiki-quality-score` | 268, 269 | trend JSON + render MD | **KÖZEPES** — heti riport, humán-olvasott |
| `vault-adr-aging-watch` | 191 | audit MD | **KÖZEPES** — ADR-aging audit |
| `github-trending-report` | 135 | napi MD report | **KÖZEPES** — cron-driven, Obsidian-render |
| `bmad-vault-bridge` | 240, 246, 448 | frontmatter target.md write | **MAGAS** — BMAD bridge mutátor |

→ **HIGH-4 sprint javasolt** — főleg `bmad-vault-bridge` (3 site, fő mutátor), `vault-wiki-quality-score` (2 site, dual-write race-rizikó).

### Composite-summary

A LAYER-1 atomic-write védelem **a vault-cluster legkritikusabb mutátorain** (session-eval-backfill, session-eval-run, ko-remap-legacy, 11.11crystallize) most **komplett**. A vault-cluster periférikus eszközei (net-watch, trending-recurrence, graph-retype) szintén védettek. A maradék **HIGH-4 csomag** (`bmad-vault-bridge`, `vault-wiki-quality-score`, `vault-adr-aging-watch`, `github-trending-report`) egy 10-15 perces külön sprintben elvégezhető — ezután valóban full-vault-atomic Layer-1.

**A mai sprintben:** kritikus crystallization-pipeline + cron-jobok = **védve**. Half-write rizikó eltüntetve a session-záró 11.11* pipeline-ról és a fő G-Eval flow-ról.

## Kapcsolódó

- [[2026-05-18 atomic-write HIGH-3 migration]] — előző hullám (3 script)
- [[2026-05-18 vault_atomic.py shared modul]] — shared modul + 10/10 unit-test
- [[../11-wiki/Crystallization-protocol]] — crystallize-pipeline kontextus
- [[../05-Memory/Infrastructure]] — vault-tools cluster térképe
