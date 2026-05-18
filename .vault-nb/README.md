# `.vault-nb/` — NotebookLM cognitive layer (B-5 sprint)

3-rétegű NotebookLM-integráció: per-projekt auto-sync (Réteg 1) + 11.11stop crystallization-hook (Réteg 2) + heti commute-podcast cron (Réteg 3).

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch.md]]
**Research:** [[../11-wiki/sv-08-notebooklm-cognitive-layer.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]
**Depends:** B-1 G-Eval (crystallize-hook integration)
**External:** `notebooklm` CLI v0.3.4 telepítve `/root/.notebooklm-venv/`-ben

## Tartalom

```
.vault-nb/
├── README.md
├── config/
│   └── nb-projects.yml             3-rétegű sync + podcast config + failure-handling
└── scripts/
    ├── vault-nb-sync.py            Réteg 1: per-projekt NB auto-create + source-sync
    ├── vault-nb-crystallize.py     Réteg 2: 11.11stop hook (convergent/divergent/contradictory tag)
    └── vault-nb-podcast.py         Réteg 3: heti deep-dive podcast cron
```

## Status — 2026-05-17 (Phase B-5 Week 2-α)

- [x] 3 script-skeleton + config v0.1 + README
- [x] **Week 1 Day 1:** `vault-nb-sync` real impl + 8 projekt NB auto-create (idempotent)
- [x] **Week 1 Day 2-3:** Source-sync batch backfill (17/17 aktív projekt auto-synced May)
- [x] **Week 1 Day 4:** Cron 5-percenként — éles inkrementális sync
- [x] **Week 1 Day 5:** Smoke: új `02-Projects/test.md` → 5 percen belül NB-be sync
- [x] **Week 2 Day 1 (2026-05-17):** `vault-nb-crystallize` real impl — `notebooklm ask -n <id>` integráció + `10-raw/nb-crystallize/<slug>-<W>.md` write + KO-DB queue (`/tmp/vault-ko-pending/`). `--all` és `--dry-run` flag. Detected: **17 linked projects**.
- [ ] **Week 2 Day 2:** B-1 G-Eval routing-integráció (NB-answer → fact-confidence boost)
- [ ] **Week 2 Day 3-5:** `/11.11stop`-ba beépítés mint pre-batch-preview lépés
- [ ] **Week 3 Day 1-3:** `vault-nb-podcast` real impl + smoke (1 projekt podcast-generálás + download)
- [ ] **Week 3 Day 4:** Cron `0 22 * * 0` install (vasárnap 22:00)
- [ ] **Week 3 Day 5:** Acceptance gate — első hétfői multi-projekt podcast-batch ✓

### Crystallize CLI (Week 2-α)

```bash
vault-nb-crystallize <slug>           # one project
vault-nb-crystallize --all            # 17 linked projects
vault-nb-crystallize --dry-run --all  # preview targets, no NB query
```

Output: `10-raw/nb-crystallize/<slug>-<ISO-week>.md` (`type: raw, source: notebooklm-crystallize`) → KO-DB extraction request in `/tmp/vault-ko-pending/`. Robust per-project: NB-failure prints `⚠` and continues.

## NotebookLM gotchas (élesben kell)

Részletes: [[../11-wiki/notebooklm-cli-gotchas]] — 10 quirk:
- `--json` empty-ID bug → `grep -oE` parse
- Explicit `-n <NB_ID>` MINDEN parancsban
- Marker-pattern 600-char fallback → strict long-format prompt
- `--mode deep --no-wait` aszinkron
- Source-limit ~300/notebook
- Audio párhuzamos OK, ask szekvenciális
- Cross-vault contamination védelem
- **#9 Audit-first retry** (status-log autoritatív)
- **#10 Marker-fallback retry-prompt minta** (min 800 szó + KRITIKUS FORMÁTUM + ROW1/2/3)

## Költség-cap (Tier-$50)

| Komponens | Cost |
|---|---|
| NotebookLM Plus tier | $0 (ingyenes 50 source / 300 source plus tier) |
| Source-sync API-call | $0 (notebooklm CLI no-cost) |
| Crystallize-konzultáció (per session-zárás) | $0 (NotebookLM internal) |
| Weekly podcast (8 projekt) | $0 (Audio Overview ingyenes) |
| **Total** | **$0/hó** — vault-budget-cap-en kívül |

## Backout

```bash
export NB_SYNC_DISABLED=1     # auto-sync cron skip
# Heti podcast crontab disable: crontab -e → comment out `0 22 * * 0 ...`
```

## Kapcsolódó

- B-1 (G-Eval crystallization): [[../.vault-ko/README.md]]
- B-2 (semantic memory, comp az NB-hez): [[../.vault-memory/README.md]]
- [[../11-wiki/notebooklm-cli-gotchas]] — must-read az élesítés előtt
- [[../11-wiki/notebooklm-headless-login-fifo]] — auth-pattern
- [[../11-wiki/cloakbrowser-fingerprint-bypass]] — Cloudflare-fallback
