---
name: SV B-8 RSI Tier-2 real-LLM Critic skeleton
type: wiki
status: skeleton
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#project/sv", "#concept/rsi-critic", "#concept/safety-gate"]
parent: [[sv-02-recursive-self-improvement]]
related:
  - "[[multi-layer-safety-gate]]"
  - "[[Crystallization-protocol]]"
  - "[[../06-Audits/2026-05-19 Wave-2 follow-up designs (SCD2 LongMemEval Critic)]]"
---

# SV B-8 — RSI Tier-2 real-LLM Critic (skeleton)

> 2026-05-19 — first landing of the **real-LLM Critic** Layer 4 of the
> multi-layer safety-gate. Skeleton-grade: opt-in env-flag, 2-phase pending
> pattern reused from `crystallize-pending`, $0 cost via subagent-fanout.

## Why

The `bmad-vault-bridge --apply` safety-gate had 4 deterministic rules at
Layer 4 (length / forbidden-target / git-hook / Critic-stub). The stub
was a placeholder. This skeleton turns the stub into a real **5-dim LLM
rubric** that can refuse propagation on semantic grounds — but stays
opt-in until calibration data accumulates.

## Architecture

```
                         ┌────────────────────────────────┐
candidate bullet ────────▶│  critic-review.py             │
                         │   Phase 1: write request.json │
                         └─────────────┬──────────────────┘
                                       │
                                       ▼
                         ┌────────────────────────────────┐
                         │  Claude subagent (crystallize- │
                         │  pending pattern — $0 cost)   │
                         │   reads request.json          │
                         │   writes response.json        │
                         └─────────────┬──────────────────┘
                                       │
                                       ▼
                         ┌────────────────────────────────┐
                         │  critic-review.py              │
                         │   Phase 3: parse response     │
                         │   apply threshold-policy      │
                         │   write audit-log JSONL       │
                         │   return verdict pass/fail    │
                         └────────────────────────────────┘
```

## 5-dim rubric (0.0 - 1.0 float each)

| Dim | Measures | 0.0 anchor | 1.0 anchor |
|---|---|---|---|
| `factuality` | Is the bullet verifiable + correct? | False / unverifiable | KO-DB match @ conf >= 0.95 |
| `novelty`    | Genuinely new info? | Exact-dup of existing wiki | First-of-kind playbook |
| `durability` | 6+ months relevant? | Session-debug noise | Architecture pattern |
| `vault_fit`  | Suits the target file? | ADR-content in MEMORY.md | Canonical fit |
| `safety`     | PII / kred / forbidden? | Leaks credential | Fully public-safe |

`safety` is a **hard gate `>= 0.9`** in every mode.

## Threshold modes (`VAULT_CRITIC_MODE`)

| Mode | Logic | When to use |
|---|---|---|
| `strict` (default) | all 5 dims >= 0.85 AND safety >= 0.9 | Aggressive ramp |
| `default` | mean >= 0.7 AND min >= 0.5 AND safety >= 0.9 | Conservative ramp |
| `lenient` | mean >= 0.5 AND safety >= 0.9 | Shadow calibration |

Mode is read from env at score time. Default is `strict` to stay
conservative until enough shadow data accumulates for ramp-down.

## File map

| File | Lines | Role |
|---|---|---|
| `.vault-ko/safety/critic-review.py` | ~260 | Runner: write request, parse response, apply threshold, audit-log |
| `.vault-ko/prompts/critic-review-template.md` | ~180 | 5-dim rubric, anchor examples, strict-JSON output |
| `.vault-ko/safety/git-pre-commit-hook.sh` | ~140 | Layer 3 + Layer 4 — invokes runner when `VAULT_CRITIC_ACTIVE=1` |
| `.vault-ko/tests/test_critic_review.py` | ~180 | 5 pytest tests (phase-1, parse, strict, safety-hard-gate, back-compat) |

## Activation

```bash
# Stay on the deterministic 4-rule stub (default — back-compat)
git commit ...

# Activate real-LLM Critic for THIS commit
VAULT_CRITIC_ACTIVE=1 \
VAULT_CRITIC_MODE=strict \
CRITIC_BULLET="<the candidate bullet text>" \
CRITIC_TARGET="<path/of/target/file.md>" \
CRYSTALLIZE_APPLYING=1 \
  git commit ...
```

The runner expects a Claude subagent to have written
`.vault-ko/safety/pending/<hash>-response.json` BEFORE the commit
attempts to land (typically dispatched by `bmad-vault-bridge` itself
during the apply pipeline, via the `crystallize-pending` skill).

## Fail-closed semantics

If no response.json appears within `VAULT_CRITIC_TIMEOUT` (default 300s)
or the JSON is malformed / missing dims, the runner returns
`verdict=fail` and the hook blocks the commit. There is no fail-open
path — that is intentional for Layer-4 safety.

## Audit log

Every Critic verdict appends one JSONL row to
`06-Audits/critic-review-log.jsonl`:

```json
{"ts":"2026-05-19T15:00:00Z","hash":"abc123","target_file":"11-wiki/foo.md","verdict":"pass","mode":"strict","scores":{...},"reasoning":"..."}
```

Stub-mode commits also log (with `"mode":"stub"`) so the audit-log gives
a single timeline view across both modes.

## What is NOT done (next-step)

- **No automatic subagent-spawn from the runner** — the caller
  (`bmad-vault-bridge --apply`) still has to orchestrate the
  Claude subagent invocation. Mirrors the `crystallize-pending` pattern.
- **No `kodb_context` injection yet** — the prompt template references
  it but the runner doesn't load it. Pending hook into the existing
  `vault-ko-query --top-k` bridge.
- **No threshold calibration data** — modes are tuned from the design
  doc, not measured. Needs 50-100 shadow-mode bullets before any ramp
  decision.
- **No `modified_bullet` flow** — the response schema supports it but
  the runner currently only consumes `scores` + `reasoning`. Wiring up
  the modify-pathway is the next iteration.

## Cost

`$0` per Critic invocation — Claude subagent dispatch happens on the
Claude Code subscription, no Anthropic API key required. Matches the
`crystallize-pending` skill cost profile.

## Related

- [[multi-layer-safety-gate]] — the 4-layer playbook this lives in
- [[Crystallization-protocol]] — upstream pipeline that triggers Critic
- [[claude-code-subagent-fanout]] — the underlying $0 dispatch pattern
- [[sv-02-recursive-self-improvement]] — Tier-2 RSI parent context
- [[../06-Audits/2026-05-19 Wave-2 follow-up designs (SCD2 LongMemEval Critic)]] — Design C source
