# `.vault-eval/` — Continuous evaluation pipeline (B-3 sprint)

3-szintű session-quality eval-pipeline: determinisztikus parser (L1, $0) + humán baseline (L2 Streamlit) + NLI hallucination-check (L2.5).

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md]]
**Research:** [[../11-wiki/sv-07-continuous-evaluation.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]
**Skeleton-pattern:** [[../11-wiki/sprint-day-0-skeleton-first.md]]
**Depends:** B-1 G-Eval (Crystallization), B-2 bge-m3 (semantic similarity)

## Tartalom

```
.vault-eval/
├── README.md                       ez a fájl
├── config/
│   └── eval-config.yml             3-szintű threshold + NLI-model + ground-truth path
├── prompts/
│   └── critique-shadowing.md       bináris Pass/Fail prompt v0.1
└── scripts/
    ├── eval-l1-parser.py           determinisztikus stuck-detection (no API)
    ├── eval-l2-llm-judge.py        NLI hallucination flag (local NLI model)
    └── vault-trace-viewer.py       Streamlit Pass/Fail UI (humán baseline)
```

## Status — 2026-05-17 (Phase B-3 sprint, Week 1-α — L1 LIVE)

- [x] Schema + 3 script-skeleton + critique-shadowing prompt + config (Day 0, 2026-05-13)
- [x] **Week 1 ✓ L1 baseline (2026-05-17):** parser újraírva a `06-Audits/crystallize-log.jsonl`-re, per-session metrika-aggregátor (bullets scored, auto/batch/discard distribution, critic approve/modify/discard, apply_real outcomes), text-table + `--json` + snapshot mód → `06-Audits/eval-l1-baseline-<ISO-ts>.jsonl`. Első baseline: 2 session (mfl-voice-sprint-1 + szerver-update), 42 scored bullet, 16 auto-prop, 4 apply_written.
- [ ] **Week 1 Day 3:** L2.5 Critique-shadowing prompt kalibráció (10 sample, Haiku-API)
- [ ] **Week 1 Day 4-5:** Streamlit `vault-trace-viewer` UI live + humán baseline-feed onboarding
- [ ] **Week 2 Day 1-2:** NLI-model integráció (tasksource/deberta-v3-base-nli download + smoke)
- [ ] **Week 2 Day 3-4:** L3 aggregator — `Eval_Trend.md` heti generátor a `vault-cleanup` mellé
- [ ] **Week 2 Day 5:** Acceptance gate — 50+ humán-baseline + AI-human agreement >85%

### L1 parser usage (Week 1-α — LIVE)

```bash
# Text-table per-session metrics from 06-Audits/crystallize-log.jsonl
.vault-eval/scripts/eval-l1-parser.py

# Machine-readable JSON
.vault-eval/scripts/eval-l1-parser.py --json

# Snapshot to 06-Audits/eval-l1-baseline-<ts>.jsonl
.vault-eval/scripts/eval-l1-parser.py --snapshot

# Legacy session-file quality heuristic (Day 0 skeleton, retained)
.vault-eval/scripts/eval-l1-parser.py --mode sessions --backfill
```

## Output-files

- `06-Audits/eval-l1-baseline-<ISO-ts>.jsonl` — **L1 baseline snapshot (LIVE 2026-05-17)** — per-session aggregált crystallize-pipeline metrikák
- `/tmp/vault-eval/eval-l1-<date>.jsonl` — legacy session-file mode (append-only)
- `/tmp/vault-eval/eval-l2-<date>.jsonl` — NLI hallucination output
- `/tmp/vault-eval/eval-l2-5-<date>.jsonl` — Critique-shadowing AI Pass/Fail
- `06-Audits/Human_Ground_Truth.jsonl` — humán baseline (perzisztens)
- `06-Audits/Eval_Trend.md` — heti trend (System_Health mellé)

## Költség-cap (Tier-$50)

| Komponens | Cost |
|---|---|
| L1 parser | $0 (Python, no API) |
| L2 NLI | $0 (local NLI model ~200MB) |
| L2.5 Critique-shadowing (Haiku) | ~$0.0002/session × 30 session/hét = $0.006/hét |
| L3 aggregator | $0 (no API) |
| **Total** | **<$0.03/hó** — Tier-$50 cap-be elhanyagolható |

## Backout

`EVAL_PIPELINE_MODE=disabled` ENV-flag → vault-cleanup nem hívja a L1/L2/L2.5 scripteket. Klasszikus `vault-cleanup` audit megmarad.

## Kapcsolódó

- B-1 (KO-DB + G-Eval, foundation): [[../.vault-ko/README.md]]
- B-2 (semantic similarity bge-m3): [[../.vault-memory/README.md]]
- B-6 (Multi-agent — Critic uses this): jövőbeli
