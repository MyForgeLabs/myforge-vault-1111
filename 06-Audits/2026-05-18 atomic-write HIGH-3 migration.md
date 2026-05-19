---
name: 2026-05-18 atomic-write HIGH-3 migration
type: audit
created: 2026-05-19
updated: 2026-05-19
tags:
  - audit
  - atomic-write
  - vault-tools
  - sv-b1
---

# atomic-write HIGH-3 migráció

A `vault_atomic.py` shared modul (10/10 unit-test PASS, [[2026-05-18 vault_atomic.py shared modul]]) bevezetését követő második hullám: 3 HIGH-rizikó script migrálása, ahol a nem-atomic `Path.write_text(...)` reader-collision-t okozhatott session-fájlokon / audit-MD-n / fanout request-JSON-eken.

## Migrált scriptek (3/3 OK)

| Script | Write-site | Mutáció-célpont | Rizikó |
|---|---|---|---|
| `vault-ko-remap-legacy` | L446 (`req_path.write_text(...)`) | `/tmp/vault-ko-remap-batches/<bid>.json` fanout request JSON | Közepes — sub-agent egyidejű olvasás truncated JSON-ról |
| `vault-ko-remap-legacy` | L824 (`AUDIT_MD_PATH.write_text(...)`) | `06-Audits/2026-05-17 B-1 predicate-remap-legacy phase1.md` | Magas — Obsidian fél-renderelt MD, broken-wikilink false-positive |
| `vault-session-eval-backfill` | L106 (`path.write_text(new_text, ...)`) | `08-Sessions/*.md` frontmatter mutáció (B-3 backfill) | Magas — session-tartalom-elvesztés rizikó crash-kor |
| `vault-session-eval-run` | L237 (`path.write_text(...)`) | `08-Sessions/<slug>.md` eval-mező upsert | Magas — `eval_score` / `hallucination_flag` overwrite közben crash |

Mind a 4 write-site `atomic_write(...)` hívásra cserélve. Mind a 3 fájl tetejére bekerült:

```python
sys.path.insert(0, '/root/obsidian-vault/.vault-tools/lib')
from vault_atomic import atomic_write  # noqa: E402
```

## Verify

**py_compile (mind 3 OK):**

```
OK vault-ko-remap-legacy
OK vault-session-eval-backfill
OK vault-session-eval-run
```

**Functional smoke (dry-run / help):**

- `vault-session-eval-backfill --dry-run` → 80 session scanned, 73 already-ok, 6 would-change, sample-output rendben (5 listed). ENCODING és frontmatter-detection változatlan.
- `vault-session-eval-run --help` → argparse output változatlan.
- `vault-ko-remap-legacy --help` → argparse output változatlan.
- `vault-ko-remap-legacy --phase regex --limit 50 --json` → 50 fact scanned, JSON-output valid.

**Backup-ok:** `/tmp/vault-{ko-remap-legacy,session-eval-backfill,session-eval-run}.bak`. Diff-summary commit-üzenetbe írandó session-zárás-kor.

## Diff summary

```
vault-session-eval-backfill   +3 / -1   (import + 1 write-site)
vault-session-eval-run        +3 / -1   (import + 1 write-site)
vault-ko-remap-legacy         +3 / -2   (import + 2 write-site)
```

Összesen: **+9 / -4 sor**, NULL viselkedés-változás. Az `encoding="utf-8"` paraméter mind a 4 helyen explicit átadva — `atomic_write` szignatúra-kompatibilis.

## Maradék MEDIUM-2 — érdemes-e most?

A `grep "write_text" /usr/local/bin/vault-* /usr/local/bin/11.11*` további write-site-okat talált:

| Script | Hely | Cél | Rizikó-szint | Migráljuk most? |
|---|---|---|---|---|
| `vault-net-watch` | L156 | report MD | MEDIUM | **Igen** (humán-olvasott audit-output) |
| `vault-github-trending-recurrence` | L130, L151 | audit MD + JSON suggest | MEDIUM | **Igen** (gyakran-futó cron) |
| `vault-auto-disable-check` | L196 | flag-file (kis-string, single-write) | LOW | Nem — < 100 byte, single-call, kernel-atomic O_WRONLY+O_TRUNC effectív |
| `vault-graph-retype` | L1005 | fanout JSON request | MEDIUM | Igen — ugyan az a pattern mint vault-ko-remap-legacy L446 |
| `vault-stats-generator` | L169 | stats JSON | LOW | Nem — `tmp` változó-név alapján már intermediate, valószínűleg utána rename |
| `vault-selfcheck` | L115 | response JSON | LOW | Nem — self-check belső, nem-publikus |
| `11.11crystallize` | L304, L385, L406, L617, L1243 | session-body re-write + flag-file | **HIGH** | **Igen** — session-body re-write L385/L406 magas-rizikó, külön sprint kell (5 site, fő crystallization-flow érintve) |

**Javaslat:**
1. **Most-azonnal (1-2 perc):** `vault-net-watch` + `vault-github-trending-recurrence` + `vault-graph-retype` — 4 write-site, mindegyik 1-soros csere, alacsony-rizikó migráció.
2. **Külön sprint (15-30 perc):** `11.11crystallize` — 5 write-site, ebből 2 session-body re-write (L385/L406), tesztelés-igényesebb (G-Eval pipeline-ban él), külön audit-MD-vel és git-bisect-fallback-kel érdemes.
3. **Skip:** `vault-auto-disable-check` flag-file (LOW), `vault-stats-generator` (LOW, már intermediate-pattern), `vault-selfcheck` (LOW, belső).

## Kapcsolódó

- [[2026-05-18 vault_atomic.py shared modul]] — shared modul + unit-test
- [[../11-wiki/Crystallization-protocol]] — milyen scriptek érintettek a session-flow-ban
- [[../05-Memory/Infrastructure]] — vault-tools cluster
