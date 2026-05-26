---
name: 2026-05-17 B-8 GEPA prompt-mutator skeleton
type: audit
tags: ["#type/audit", "sv-research", "rsi", "phase-b8", "gepa", "skeleton"]
created: 2026-05-17
updated: 2026-05-17
status: skeleton-landed
sprint: B-8 Week 1 Day 0
parent: [[../07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]]
research: [[../11-wiki/sv-02-recursive-self-improvement]]
project: [[../02-Projects/superintelligent-vault]]
---

# B-8 Week 1 — GEPA prompt-mutator skeleton audit

## TL;DR

A 2026-05-17 NotebookLM-mining **Tier-1 production-ready** ajánlása (GEPA / gepa-ai/gepa Python lib, Pareto-front + minibatch + reflective mutation) **B-8 Week 1 skeletonként ÉLES**. A `gepa==0.1.1` `pip install`-elt, a két új script (`gepa-prompt-eval.py`, `gepa-prompt-mutate.py`) smoke-test-pass-elt 3 baseline prompton + 8-sample gold-set-en. Az `VAULT_RSI_APPLY` ENV-gate Layer 1 működik — apply DEFAULT OFF. Real `gepa.optimize()` loop Week 2-re halasztva (reflection_lm-claude-code subagent fanout 2-phase pending pattern).

## Mi sikerült

### 1. `gepa-ai/gepa` Python-lib telepítve és verifikálva

- **Package:** `gepa==0.1.1` (pip-installed, 244 KB wheel, no native deps)
- **API verified:** `gepa.optimize(seed_candidate, trainset, valset, adapter, reflection_lm, ...)` — Pareto / current_best / epsilon_greedy / top_k_pareto candidate-selection-strategies, `frontier_type=instance|objective|hybrid|cartesian`, `use_merge`, `reflection_minibatch_size`, `stop_callbacks` (MaxMetricCalls / ScoreThreshold / NoImprovement / Timeout) — kontroll teljesen kompatibilis a B-8 ADR Pareto-front + length-regularization igényével.
- **Exports relevant:** `GEPAAdapter`, `EvaluationBatch`, `GEPAResult`, stop-conditions, `default_adapter`, `proposer` modul (reflective_mutation).

### 2. Skeleton scripts — Week 1 deliverable

```text
/root/obsidian-vault/.vault-rsi/
├── README.md                       # B-8 Week 1 status + VAULT_RSI_APPLY ENV-gate doc
├── scripts/
│   ├── gepa-prompt-eval.py        # NEW — minibatch eval, mock/claude-code/anthropic dispatcher
│   ├── gepa-prompt-mutate.py      # NEW — gepa-ai/gepa wrapper, Pareto-front skeleton
│   └── gepa-prompt-mutator.py     # legacy May-13 stub (kept for backward-compat)
├── prompts/
│   ├── baseline/                   # 3 seed-prompts: g-eval, critic, worker (live-copies)
│   └── candidates/                 # GEPA mutants land here (Week N+, üres ma)
├── eval-data/
│   └── g-eval.jsonl                # 8-sample router-decision gold-set
└── logs/
    ├── eval-<ts>.jsonl             # per-eval-run snapshot (read-only)
    └── mutations.jsonl             # mutate audit-log (dry-run + apply)
```

### 3. Smoke-test eredmények

**Eval (mock-scorer, baseline g-eval prompt, 8 samples):**

```
relevance      0.279
factuality     0.579
actionability  0.6
novelty        0.527
uniqueness     0.5
score          0.486
```

**Mutate dry-run (Layer 1 ENV unset):**

```
[safety] DRY-RUN (Layer 1) — set VAULT_RSI_APPLY=1 + remove --dry-run to write candidates/.
[pareto-front] target-size=4 budget=4
  - baseline             score=0.486 len=4040
[log] /root/obsidian-vault/.vault-rsi/mutations.jsonl  (dry-run skeleton entry)
```

**Mutate write-mode (VAULT_RSI_APPLY=1, critic baseline):**

```
[log] /root/obsidian-vault/.vault-rsi/mutations.jsonl  (write-mode, 0 candidates — Week 1)
```

→ Apply-gate műxik: ENV-flag nélkül `_skeleton_dry_run: true`, ENV-flaggel write-mode entry, **de Week 1-ben mindkét esetben 0 candidate** (real gepa.optimize() Week 2-re halasztva).

### 4. Safety-gate (4-layer mirror a `.vault-ko/safety/`-ból)

| Layer | Mechanism | Status |
|---|---|---|
| 1 ENV-flag | `VAULT_RSI_APPLY=1` required | ✅ Verified (default OFF) |
| 2 Forbidden targets | `AGENTS.md`, `00-Meta/`, `.vault-ko/safety/`, `11.11*`, `.vault-rsi/` (except `prompts/candidates/`) | ✅ `forbidden_target_check()` in mutate.py |
| 3 Pareto-front | 3-5 specialista-variants, no single "winner" auto-merge | ✅ Skeleton (real impl Week 2-3) |
| 4 Manual apply | candidates/ → live promotion = separate step + Critic-review + user-confirm | ✅ NOT WIRED (Week N) |

## Mi blokkolt

Semmi keményen. A `claude-code` és `anthropic` scorerek `NotImplementedError`-t dobnak (őszinte skeleton), real impl Week 2-ben jön a 2-phase pending pattern-nel (a `11.11crystallize --scorer claude-code --with-context` mintáját követve).

## Audit-fájl path

`/root/obsidian-vault/06-Audits/2026-05-17 B-8 GEPA prompt-mutator skeleton.md` (ez a fájl).

Kapcsolódó audit-log fájlok:

- `.vault-rsi/logs/eval-<ts>.jsonl` — eval-run snapshots (1 már létezik)
- `.vault-rsi/mutations.jsonl` — mutate dry-run + write-mode entries (3 már létezik a smoke-test-ekből)

## Next-step roadmap

### Week 2 — Real `gepa.optimize()` loop

- [ ] `claude-code` scorer wire-up — subagent-fanout 2-phase pending pattern (`/tmp/vault-rsi-pending/<id>.request.json` → general-purpose Agent spawn → `<id>.response.json` → resume)
- [ ] `reflection_lm` adapter — ugyancsak claude-code subagent (NEM Anthropic API a Tier-1 budget miatt)
- [ ] `gepa.GEPAAdapter` subclass — `build_program`, `evaluate`, `make_reflective_dataset` (lib-doc szerint)
- [ ] First REAL minibatch-eval run (`g-eval` prompt + 8-sample gold) → 1 candidate, score-comparison vs baseline

### Week 3 — Candidate-generation + Pareto-front

- [ ] `--budget 30-100` runs Pareto-front-tel (3-5 specialista-variants)
- [ ] Length-regularization (target 4× kompresszió, prompt-bloat penalty)
- [ ] Cross-eval: candidate vs baseline minden 8 gold-sample-on, per-axis score-diff

### Week N — Apply-gate (REAL promotion)

- [ ] `--apply` flag implementation: candidates/ → live (`.vault-agents/prompts/`) atomic-write
- [ ] Critic-review mandatory (B-6 reuse, ugyanaz a subagent-protokoll mint `.vault-ko/safety/`-ban)
- [ ] User-confirm batch-preview (mint a Crystallization-protocol Step 4 batch-preview)
- [ ] Auto-disable triggers: Critic reject-rate >30%, eval pass-rate drop, vault-corruption

### Acceptance criteria (Week 3-vége)

- [ ] 1 full GEPA-cycle without rollback (baseline → 4 candidates → Pareto-merge → log)
- [ ] User-pass-rate >85% a batch-preview-ben
- [ ] `mutations.jsonl` audit-log clean (no `apply_aborted` events)
- [ ] B-1..B-7 dependency-check (`rsi-eligibility-audit`) PASS — ez gate-eli a Week N apply-step indítását

## Risks / safety notes

- **NEM nyúltam:** `AGENTS.md`, `00-Meta/`, `.vault-ko/safety/`, `11.11*` — verified.
- **Apply HARD-OFF:** `VAULT_RSI_APPLY` ENV nélkül 0 candidate-write GARANTÁLT, akkor is ha a `--apply` flag később hozzáadódik (Layer 1 első a pipeline-ban).
- **Forbidden-target check** `mutate.py`-ban: csak `prompts/candidates/`-be ír, mindenhova máshova → exit-3.
- **gepa-ai/gepa lib version-pin:** `0.1.1` — Week 2 előtt érdemes `pip install gepa --upgrade` és re-verify, mert friss (2025-2026 release).

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]] — parent ADR (Réteg 2 = Prompt Evolution)
- [[../11-wiki/sv-02-recursive-self-improvement]] — research (Q1: GEPA Compound AI, 35× fewer rollouts)
- [[../02-Projects/superintelligent-vault]] — B-8 sprint task
- [[../11-wiki/multi-layer-safety-gate]] — playbook (4-rétegű minta, B-1 + B-8 reuse)
- `.vault-ko/safety/README.md` — B-1 PART 2 safety-gate (sister-pattern)
- `.vault-rsi/README.md` — sprint state + ENV-gate doc
