# `.vault-ko/` — Knowledge Objects (KO) substrate

Vault-szintű KO-DB + crystallization-pipeline szkriptek.

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch.md]]
**Research:** [[../11-wiki/sv-05-crystallization-automation.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]

## Tartalom

```
.vault-ko/
├── README.md                    ez a fájl
├── schema.sql                   SQLite schema (facts, propagation_log, crystallization_runs)
├── facts.db                     SQLite DB (gitignored, init: sqlite3 facts.db < schema.sql)
├── scripts/
│   └── vault-ko-ingest.py       Markdown → KO-tuple extractor (SKELETON)
└── prompts/
    └── g-eval-template.md       G-Eval Learning-scoring prompt (DRAFT v0.1)
```

## Status — 2026-05-12 (Phase B-1 sprint kickoff, Day 0)

- [x] Schema létrehozva (3 tábla: `facts`, `propagation_log`, `crystallization_runs`)
- [x] `facts.db` initializálva (WAL mode, indexek)
- [x] Ingest-script skeleton (no API calls yet — placeholder extractor)
- [x] G-Eval prompt template draft v0.1
- [ ] **Phase B-1 Week 1**: 50 sample Learning bullet manuális címkézés (gold-label)
- [ ] **Phase B-1 Week 1**: 3-modell benchmark (Haiku / Sonnet / Qwen 7B) az 50 mintán
- [ ] **Phase B-1 Week 2**: `vault-ko-ingest` real extractor (Haiku-API integration)
- [ ] **Phase B-1 Week 2**: `/usr/local/bin/11.11crystallize` script + `/11.11stop` hook
- [ ] **Phase B-1 Week 3-4**: Shadow → Konzervatív (threshold 0.95) felfutás
- [ ] **Phase B-1 Week 5-6**: Aggressive (threshold 0.85) — cél: 80% auto-rate

## Hot-reload threshold

```bash
mkdir -p ~/.vault-config
echo "1.0" > ~/.vault-config/crystallize-threshold.txt    # shadow mode default
```

## Backout

`CRYSTALLIZE_MODE=manual` env-flag a `/11.11stop`-ra → klasszikus batch-preview workflow ([[../11-wiki/Crystallization-protocol]]). A KO-DB megmarad, csak nem íródik bele.
