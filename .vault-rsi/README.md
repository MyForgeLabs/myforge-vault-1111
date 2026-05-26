# `.vault-rsi/` — Recursive Self-Improvement (B-8 sprint, **SAFETY-GATED**)

⚠️ **A LEGUTOLSÓ sprint a SV-roadmap-en, MAGAS-risk.** Csak B-1..B-7 stabilizálódása UTÁN (>4 hét production, B-3 eval >70% Pass-rate, semmi regresszió). Default: **DISABLED**.

3-rétegű felügyelt RSI: Skill Library Growth (Réteg 1, ReCreate-stílus) + Prompt Evolution (Réteg 2, GEPA + DSPy) + Self-Reflection Loop (Réteg 3, Reflexion + ReFlect-Harness).

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md]]
**Research:** [[../11-wiki/sv-02-recursive-self-improvement.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]
**Depends:** B-1..B-7 mind stabil. **NEM** indítható B-1 nélkül.

## Tartalom

```text
.vault-rsi/
├── README.md                       ez a fájl
├── config/
│   └── rsi-config.yml              Safety gates + Pareto-front + length-reg + forbidden targets
├── safety/
│   └── git-pre-commit-hook.sh      Forbidden-target blokk non-sandbox branchen
├── scripts/
│   ├── vault-skill-suggest.py     Réteg 1: új SKILL.md auto-draft (ReCreate, skeleton)
│   ├── vault-reflect.py            Réteg 3: weekly self-reflection (manuális promóció, skeleton)
│   ├── gepa-prompt-mutator.py     Réteg 2 v0: legacy stub (May-13 skeleton)
│   ├── gepa-prompt-eval.py        Réteg 2 v1 EVAL: minibatch read-only scorer (2026-05-17) ✅
│   └── gepa-prompt-mutate.py      Réteg 2 v1 MUTATE: gepa-ai/gepa Pareto wrapper (2026-05-17) ✅
├── prompts/
│   ├── baseline/                   live-prompt seed-másolatok (g-eval, critic, worker)
│   └── candidates/                 GEPA-generált variants land here (Week N+, üres ma)
├── eval-data/
│   └── g-eval.jsonl                8-sample minibatch gold-set (G-Eval router-decisions)
└── logs/
    ├── eval-<ts>.jsonl             per-eval-run mock-score snapshot
    └── mutations.jsonl             gepa-prompt-mutate audit-log (dry-run + apply)
```

## Status — 2026-05-17 (B-8 **Week 2 real-loop landed**, Layer-4 detect-only)

- [x] `scripts/gepa-prompt-eval.py` — minibatch eval, mock-scorer baseline working (smoke: 8 samples)
- [x] `scripts/gepa-prompt-mutate.py` — real `gepa.optimize()` loop wired with custom GEPAAdapter (Week 2)
- [x] `scripts/gepa-claude-code-scorer.py` — 2-phase pending file scorer + ClaudeCodeReflectionLM (Week 2 új)
- [x] `prompts/baseline/{g-eval,critic,worker}.md` — live-prompt copies as optimization seeds
- [x] `eval-data/g-eval.jsonl` — 8 router-decision gold samples (auto-promote, discard, route-memory, ADR, ask-user, forbidden-block, pareto-merge)
- [x] `scoring-{pending,responses}/` — UUIDv5 idempotent 2-phase scoring infra
- [x] `gepa-log.jsonl` — per-run audit-log (complete/pending/failed events)
- [x] Smoke-test green: 3 candidates @ scores 0.541 → 0.593 → 0.619 (Pareto-front) — audit: [[../06-Audits/2026-05-17 GEPA Week 2 real-loop]]
- [x] Apply Layer-1+2 verified: ENV-gate off → 0 writes; forbidden-target gate blocks AGENTS.md / 00-Meta/ / .vault-ko/safety/ / 11.11* / .vault-rsi/{scripts,logs,config,safety}/
- [x] Layer-4 detect-only: candidates carry `<!-- CANDIDATE — NOT LIVE -->` header, never auto-promoted
- [ ] **Week 3:** `rsi-eligibility-audit` + Critic-review gate + real subagent `reflection_lm` (replace synth-mutator) + batch-preview UX
- [ ] **Week N (apply-gate):** Critic-review + user-confirm to promote `candidates/<id>.md` → `.vault-agents/prompts/`

### `VAULT_RSI_APPLY` ENV-gate (Layer 1 hard-off)

| Mode | Command | What happens |
|---|---|---|
| dry-run (default) | `gepa-prompt-mutate --baseline ... --eval-data ...` | Baseline scored, Pareto-front printed, **0 candidates written**, log marks `_skeleton_dry_run: true` |
| dry-run explicit | `gepa-prompt-mutate ... --dry-run` | Same as above, always-dry |
| write-mode | `VAULT_RSI_APPLY=1 gepa-prompt-mutate ...` | Permits candidate-writes to `prompts/candidates/`. Week 1: still 0 candidates (real gepa.optimize wires Week 2) |
| REAL apply (Week N) | `VAULT_RSI_APPLY=1 ... --apply` (NOT WIRED YET) | Critic-review + Pareto-merge into `prompts/candidates/`. **Never** auto-promoted to live. |

**Forbidden targets** (Layer 2): `AGENTS.md`, `00-Meta/`, `.vault-ko/safety/`, `11.11*`, `.vault-rsi/` (only `prompts/candidates/` is writable).

## Status — 2026-05-13 (Phase B-8 sprint kickoff, Day 0 — **SKELETON-ONLY, RSI_MODE=disabled**)

- [x] 3 script-skeleton + safety-config + git-pre-commit-hook + README
- [ ] **B-1..B-7 stabilizálódás-gate** (várt: ~2026-08-01 körül, ~10 hét B-1 indulásától)
- [ ] **Week 1 Day 1:** Eligibility-check — `rsi-eligibility-audit` (B-1 4-wk stable? B-6 production-ready? eval >70%?)
- [ ] **Week 1 Day 2:** Git pre-commit hook install + test (rsi-sandbox-branch validation)
- [ ] **Week 1 Day 3-5:** Vault-skill-suggest real impl + ReCreate-template-engine
- [ ] **Week 2 Day 1-3:** Vault-reflect real impl + ReFlect-harness shape-validator
- [ ] **Week 2 Day 4-5:** GEPA-prompt-mutator first iteration on `worker.md` (max-friction target)
- [ ] **Week 3 Day 1-3:** Pareto-front-management (3-5 variants alive simultaneously)
- [ ] **Week 3 Day 4-5:** Acceptance gate — 1× full RSI-cycle without rollback, user-pass-rate >85%

## Safety hard-rules (Multi-layer Safety-Gate minta)

Részletes playbook: [[../11-wiki/multi-layer-safety-gate]] — 4 független védelmi réteg (ENV-flag + script-gate + git-hook + Critic-review). B-8 az első alkalmazás.

### Konkrét rétegek B-8-ban

| Rule | Mechanism |
|---|---|
| Default disabled | `RSI_MODE=disabled` ENV, scripts safety-gate-en exit-elnek |
| Forbidden targets | git pre-commit hook blokkol (AGENTS.md, 00-Meta/, .vault-rsi/, 11.11*) |
| Sandbox-only mutations | branch `rsi-sandbox-<topic>` kötelező a forbidden-target edit-ekhez |
| Pareto-merge | 3-5 specialista-variant, NEM 1 "legjobb" |
| Critic-review (B-6) | minden RSI-output Critic-review-n megy keresztül |
| Auto-disable triggers | vault-corruption / Critic 30%+ reject / user-manual |
| Auto-reflections | NEM auto-promote — emberi review mandatory minden Memory-root változáshoz |

## Phase C+ kihagyott területek

NEM része B-8-nak (a kockázat túl magas):
- **Code self-modification** (Gödel Agent monkey-patching) — Phase C+ idejére
- **Ab initio skill generation** (TTE method, $300-600/run) — ReCreate-stílus elég
- **Auto-ADR írás** — User-only, agent NEM ír új architektúra-döntést

## Eligibility audit (Week 1 Day 1)

A `rsi-eligibility-audit` script (skeleton later) ellenőrzi:

```yaml
preconditions:
  b1_g_eval_stable_weeks: 4              # /tmp/vault-eval/eval-l1-*.jsonl trending
  b6_multi_agent_stable_weeks: 4         # .vault-agents events.jsonl health
  b3_quality_a_rate_min: 0.70            # weekly System_Health.md Eval_Trend
  b6_critic_reject_rate_max: 0.20        # < 20% Critic-reject = healthy
  no_revert_incidents_30d: true
  vault_size_growth_normal: true         # NEM exponentially exploding
```

Ha minden ✓ → RSI eligible. Bármelyik ✗ → wait + alert.

## Backout (emergency)

```bash
# Azonnali RSI-disable:
echo "disabled" > ~/.vault-config/rsi-mode.txt
unset RSI_MODE

# Git: minden rsi-sandbox-* branch maradhat, de soha nem merge-elődik main-re Pareto-review nélkül

# Audit-cleanup:
cat /root/obsidian-vault/.vault-rsi/mutations.jsonl   # review what RSI did
```

## Kapcsolódó

- [[../11-wiki/sv-02-recursive-self-improvement]] — 1009-source research, "self-correction blind spot" 76-98%
- B-1 (G-Eval, Pareto-merge): [[../.vault-ko/README.md]]
- B-3 (eval-pipeline, eligibility-metrics): [[../.vault-eval/README.md]]
- B-6 (Critic + worker prompts that get mutated): [[../.vault-agents/README.md]]
