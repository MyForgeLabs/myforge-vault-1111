---
name: GEPA Week 2 real-loop
type: audit
created: 2026-05-17
updated: 2026-05-17
project: superintelligent-vault
sprint: B-8
tags: [audit, sv/b8, gepa, rsi, week2]
---

# GEPA Week 2 — real `gepa.optimize()` loop landed

**Sprint:** B-8 (Recursive Self-Improvement) — Réteg 2 (Prompt Evolution)
**Status:** Smoke-test green, 3 candidates materialized, Layer-4 detect-only.
**ADR:** [[../07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]]
**Project:** [[../02-Projects/superintelligent-vault]]
**Wiki:** [[../11-wiki/sv-02-recursive-self-improvement]] · [[../11-wiki/claude-code-subagent-fanout]]

## Deliverable

| Komponens | Path | Méret |
|---|---|---|
| Real `gepa.optimize()` wrapper | `.vault-rsi/scripts/gepa-prompt-mutate.py` | ~480 sor |
| 2-phase pending scorer | `.vault-rsi/scripts/gepa-claude-code-scorer.py` | ~330 sor (új) |
| Phase-1 request dir | `.vault-rsi/scoring-pending/` | UUIDv5 filenames |
| Phase-2 response dir | `.vault-rsi/scoring-responses/` | UUIDv5 filenames |
| Pareto-candidates dir | `.vault-rsi/prompts/candidates/<seed>-v0.3.<N>/` | 3 variant + meta.json |
| Audit-log | `.vault-rsi/gepa-log.jsonl` | append-only per iteration |
| Mutations-log | `.vault-rsi/mutations.jsonl` | append-only per run |

## 2-phase pending pattern (claude-code scorer)

A pattern megegyezik a `11.11crystallize --scorer claude-code` és `vault-ko-ingest` 2-phase pending pattern-jével (lásd [[../11-wiki/claude-code-subagent-fanout]]):

```
Phase 1 (request write):
  gepa-prompt-mutate
    → adapter.evaluate(candidate, batch)
      → ScoringClient.request_batch(prompt, samples)
        → for each (candidate, sample):
            uuid = uuidv5(NAMESPACE, sha256(canonical(payload)))
            scoring-pending/<uuid>.request.json
              { schema_version, prompt_text, sample, instructions, ... }

Phase 2 (response fill):
  Parent Claude Code session spawns a general-purpose Agent
    → reads scoring-pending/<uuid>.request.json
    → scores prompt against sample (5-axis 0-1)
    → writes scoring-responses/<uuid>.response.json
        { relevance, factuality, actionability, novelty, uniqueness, rationale }

Phase 3 (loop progression):
  gepa-prompt-mutate re-runs OR continues in-process
    → ScoringClient.load_batch(uuids) → list[dict|None]
    → if all ready: aggregate → score → GEPA evolves
    → if any missing: exit-4 with "re-run after subagent fills"
```

**Idempotency:** UUID a `(candidate_id, sample_id, component)` triple sha256-jából képződik. Második run nem ír újra meglévő request-et, és a már kitöltött response-okat instant betölti — partial-progress safe.

**Smoke-fallback:** `--auto-fill-synth` flag bekapcsolja a `synth_response_for_sample()` heuristic-ot (keyword-overlap + length-penalty + sha-based novelty), így a loop egy process-en belül lefut — Anthropic API vagy subagent nélkül. Determinisztikus, $0 cost, reusable smoke-tesztekre.

## Architektúra

```
.vault-rsi/scripts/
├── gepa-prompt-mutate.py          ← GEPA loop driver (Week 2 real, Layer 1-4 safety)
│   - argparse: --budget, --max-iterations, --scorer, --auto-fill-synth, --frontier-size
│   - build_adapter(): custom GEPAAdapter (evaluate + make_reflective_dataset)
│   - extract_pareto_front(): rank by (in_pareto_front desc, score desc, length asc)
│   - write_candidate_files(): writes `<stem>-v0.3.<N>/{<stem>.md, meta.json}` with
│       "CANDIDATE — NOT LIVE" HTML-comment header (Layer-4 detect-only)
│
├── gepa-claude-code-scorer.py     ← 2-phase pending client (új, Week 2)
│   - ScoringClient: request_batch / load_batch / pending_count / all_ready
│   - synth_response_for_sample(): deterministic in-process fallback
│   - auto_fill_pending(): fills any unanswered request with synth-response
│   - ClaudeCodeReflectionLM: gepa.LanguageModel-protocol callable
│       mode='auto-fill' (Week 2 smoke) | mode='subagent' (Week 3 real)
│
└── gepa-prompt-eval.py            ← Week 1 minibatch-eval, mock-scorer (változatlan)
```

## Smoke-test (2026-05-17 22:48 UTC)

**Command:**

```bash
VAULT_RSI_APPLY=1 python3 .vault-rsi/scripts/gepa-prompt-mutate.py \
  --baseline .vault-rsi/prompts/baseline/g-eval.md \
  --eval-data .vault-rsi/eval-data/g-eval.jsonl \
  --budget 32 --max-iterations 3 \
  --scorer claude-code --auto-fill-synth \
  --minibatch 3 --frontier-size 5 --seed 42
```

**Eredmény:**

| Iteration | Selected | Mutation | Valset score | Action |
|-----------|----------|----------|--------------|--------|
| 0 | baseline | — | 0.5414 | seed |
| 1 | program-0 | concise edition | 0.5933 (+0.052) | accept |
| 2 | program-0 | actionability edition | 0.6190 (+0.078) | accept |
| 3 | program-2 | concise edition | (skipped — subsample worse) | skip |

**Pareto-front (sorted by score desc):**

```
★ cand-002-4e300436   score=0.619  len=2174   ← actionability edition
★ cand-001-34935f34   score=0.593  len=2178   ← concise edition
★ cand-000-99a9f842   score=0.541  len=4040   ← baseline (seed)
```

**Idempotency check:** 2x futtatva ugyanazokkal a flag-ekkel:
- 1. run: 34 request + 34 response írva, 3 candidate-fájl
- 2. run: 0 új request (UUIDv5 collision-detect), 0 új response, 3 candidate-fájl unchanged

**Verifikáció:**
- ✅ Score-range 0.0–1.0 (mind érvényes)
- ✅ Pareto-front non-empty (3 unique variant)
- ✅ Candidate fájlok írva `prompts/candidates/g-eval-v0.3.{0,1,2}/`
- ✅ Minden candidate-MD `<!-- CANDIDATE — NOT LIVE -->` header-rel (Layer-4 detect-only)
- ✅ `meta.json` per variant: variant_id, score, length, pareto-flag, iteration_count, baseline_source
- ✅ Audit-log `gepa-log.jsonl` 5 entry (run-onkénti complete event)
- ✅ Idempotency: 2nd run zero side-effects

## Safety gates verifikált

| Layer | Mechanism | Test result |
|-------|-----------|-------------|
| 1 ENV-flag | `VAULT_RSI_APPLY=1` required to write candidates/ | ✅ default: dry-run, 0 files |
| 2 Forbidden | `forbidden_target_check()` blokk: AGENTS.md, 00-Meta/, .vault-ko/safety/, 11.11*, .vault-rsi/{scripts,logs,config,safety}/ | ✅ 6/7 path-on BLOCKED, csak candidates/ OK |
| 3 Pareto | 3-5 variant alive, NEM 1 "winner" auto-merge | ✅ frontier-size cap working, sort by (in_pareto, score, length) |
| 4 Manual apply | Candidates dir-ben "NOT LIVE" header — promotion külön user-confirm + Critic-review step (Week 3+) | ✅ detect-only, soha nem ír `.vault-agents/prompts/`-ba |

## Audit-log shape (`.vault-rsi/gepa-log.jsonl`)

Per-iteration complete event (1 sor / futás):

```json
{
  "event": "gepa_optimize_complete",
  "ts": "2026-05-17T22:48:45+00:00",
  "baseline": "...",
  "eval_data": "...",
  "scorer": "claude-code",
  "budget": 32,
  "max_iterations": 3,
  "iteration_count": 9,
  "frontier_size": 5,
  "auto_fill_synth": true,
  "baseline_aggregate": {"relevance": 0.279, "factuality": 0.579, ..., "score": 0.486},
  "pareto_front": [
    {"variant_id": "cand-002-...", "candidate_index": 2, "score": 0.619, "length": 2174, "in_pareto_front": true},
    {"variant_id": "cand-001-...", "candidate_index": 1, "score": 0.593, "length": 2178, "in_pareto_front": true},
    {"variant_id": "cand-000-...", "candidate_index": 0, "score": 0.541, "length": 4040, "in_pareto_front": true}
  ],
  "candidates_written": 3,
  "dry_run": false,
  "real_apply": true
}
```

Külön event-típusok: `gepa_optimize_pending` (Phase-2 wait), `gepa_optimize_failed` (recoverable error).

## Smoke-test scoring axes (synth fallback)

A `synth_response_for_sample()` 5 tengelyt mer (mind 0.0–1.0):

| Axis | Heuristic |
|------|-----------|
| relevance | `req_keywords_hit_rate - 0.5 * forb_keywords_hit_rate` |
| factuality | `1.0 - length / 8000` (concise prompts reward-ed) |
| actionability | `0.6 + 0.25 if "step"\|"1."\|"lépés"` |
| novelty | `0.5 + (sha256(prompt+sample_id) % 100) / 250.0` |
| uniqueness | `0.5 + (sha256(...) >> 8 % 100) / 250.0` |

A scorer-aggregate `score = mean(relevance, factuality, actionability)` — ez a primary GEPA-axis. Tényleges Phase-2 subagent ezt felülírja LLM-judge-output-tal Week 3-ra.

## Week 3 follow-up

| Task | Cél | Path |
|---|---|---|
| `rsi-eligibility-audit` | Pre-flight: B-1 4-wk stable, B-6 Critic-reject < 20%, B-3 A-rate > 70%, no revert-incidents 30d | új script `scripts/rsi-eligibility-audit.py` |
| Real subagent reflection_lm | `ClaudeCodeReflectionLM(mode='subagent')` 2-phase write/wait flow valódi parent-spawn-nal | `gepa-claude-code-scorer.py:_synth_reflection_mutation` cseréje |
| Critic-review gate | Promotion `candidates/<id>` → `.vault-agents/prompts/` előtt automatikus Critic-review (B-6 worker-prompt) | új `scripts/gepa-candidate-promote.py` |
| Batch-preview to user | "5 candidate kész, score range 0.49–0.62, melyiket promoveáljam?" UI-ablak | integrálás `11.11`/dashboard-szintű flow-ba |
| `frontier-type='hybrid'` | per-objective + per-instance Pareto kombinálva (multi-axis frontier) | `gepa.optimize(frontier_type='hybrid', ...)` |

## Korlátok / nyitott kérdések

- **`auto-fill-synth` ≠ real LLM-judge:** a smoke-eredmény score-progresszió (0.541 → 0.619) a heuristic-determinizmus eredménye, NEM bizonyítja a real-prompt-jobban-működik-tényt. Week 3 subagent-fanout szükséges erre.
- **`reflection_lm` jelenleg deterministic templating** (3 variant — concise / safety-first / actionability) — limit ennek a "mutation-diverzitása". Real subagent (Week 3) ezt LLM-driven reflective-rewrite-tal helyettesíti.
- **Cache `cache_evaluation=True`** csökkenti a metric-call-okat, de bug-prone ha a scorer determinisztikus → `--seed`-érzékenység (smoke-tesztben verifikálva, 2x run azonos eredmény).
- **`frontier-type='instance'`** default — per-sample Pareto. Multi-axis (relevance vs novelty vs uniqueness) trade-off-okat `hybrid` mode-ban majd Week 3+.

## Kapcsolódó

- [[2026-05-17 B-3 Week 2 L2 NLI-judge]] — előző B-3 audit, ugyanaz a sprint
- [[../11-wiki/multi-layer-safety-gate]] — 4-rétegű safety pattern (B-8 az első alkalmazás)
- [[../11-wiki/claude-code-subagent-fanout]] — 2-phase pending pattern referenciák
- [[../11-wiki/sv-02-recursive-self-improvement]] — GEPA háttér (35× fewer rollouts vs GRPO)
- [[../.vault-rsi/README]] — sprint README
