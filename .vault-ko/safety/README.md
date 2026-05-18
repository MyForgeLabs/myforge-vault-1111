---
name: .vault-ko/safety/ — B-1 PART 2 skeleton
type: doc
status: SKELETON 2026-05-17
playbook: 11-wiki/multi-layer-safety-gate.md
created: 2026-05-17
---

# `.vault-ko/safety/` — 11.11crystallize `--apply` safety-gate

**Status (2026-05-17):** B-1 Week 3-4 PART 2 **SKELETON installed, not yet active**. The `11.11crystallize --apply` flow now walks all 4 layers and records audit-log entries with `would_have_applied: true/false`, but **does NOT mutate vault files yet**. Real vault-write logic (target-file router + atomic write + commit) lands in **Week N**.

## 4-layer safety-gate

| Layer | What | Where |
|---|---|---|
| 1 ENV-flag | default-disabled, `VAULT_CRYSTALLIZE_APPLY=1` required | `apply_env_gate()` in `11.11crystallize` |
| 2 Script-gate | first-call inside `--apply` branch, abort if Layer 1 fails | `run_apply_skeleton()` in `11.11crystallize` |
| 3 Forbidden-targets | block writes to `AGENTS.md` / `00-Meta/` / `.vault-*/` / `.git/` / `11.11*` | `forbidden_target_check()` + git pre-commit hook |
| 4 Critic-review | 2-phase pending pattern, subagent verdict per auto-prop bullet | `.vault-ko/prompts/critic-review-template.md` + `critic_review_request/load_response()` |

## Files in this directory

- `git-pre-commit-hook.sh` — Layer 3 backup at the git level. Blocks commits touching forbidden targets unless on a `crystallize-sandbox-*` branch or `SKIP_CRYSTALLIZE_HOOK=1`.
- `README.md` — this file.

## Install (manual, not automatic)

```bash
cd /root/obsidian-vault
ln -sf ../.vault-ko/safety/git-pre-commit-hook.sh .git/hooks/pre-commit
# verify
ls -la .git/hooks/pre-commit
```

The hook is **harmless** until `11.11crystallize --apply` starts writing vault files in Week N — it only acts on staged forbidden targets.

## Usage today (skeleton verification)

```bash
# Layer 1 BLOCK (no ENV) — every other layer skipped:
11.11crystallize <slug> --scorer mock --threshold 0.7 --apply --dry-run

# All 4 layers walked, audit-log entries recorded:
VAULT_CRYSTALLIZE_APPLY=1 11.11crystallize <slug> --scorer mock --threshold 0.7 --apply --dry-run

# With KO-DB-context-aware Critic (recommended once real-mode lands):
VAULT_CRYSTALLIZE_APPLY=1 11.11crystallize <slug> --scorer claude-code \
    --apply --with-context
```

When Layer 4 PENDING fires, the script writes `/tmp/vault-crystallize-critic-pending/<slug>.request.json`. Spawn a general-purpose Agent with the Critic prompt (`.vault-ko/prompts/critic-review-template.md`), write the response to `<slug>.response.json`, then re-run the same command.

## Audit-log entries (in `06-Audits/crystallize-log.jsonl`)

The skeleton appends two new event-types:

- `apply_aborted` — `{layer, reason}` when Layer 1 blocks early.
- `apply_skeleton_review` — `{bullet_idx, proposed_target, critic_decision, would_have_applied, executed=false}` per auto-prop candidate after the full pipeline runs.

Both have `executed: false` until Week N adds the real write step.

## Week N additions (still TODO)

- [ ] `propose_target_file()` — promote from heuristic stub to canonical router (consult `00-Meta/Glossary.md` + KO-DB to dedup against existing wiki / ADR / Memory entries).
- [ ] `apply_to_target()` — atomic file-write step (temp-file + rename), idempotent on bullet_hash.
- [ ] `git_commit_apply()` — auto-commit with deterministic message `crystallize: auto-prop <bullet_hash[:8]> → <target>`.
- [ ] Auto-disable triggers (vault corruption detector, Critic reject-rate > 30%, eval pass-rate < 70%).
- [ ] Backout: `crystallize-revert <bullet_hash>` to undo a specific auto-prop.

## Related

- `11-wiki/multi-layer-safety-gate.md` — the playbook this implements.
- `07-Decisions/2026-05-12 sv-5 crystallization automation arch.md` — parent ADR.
- `.vault-ko/prompts/critic-review-template.md` — Layer 4 prompt skeleton.
- `02-Projects/superintelligent-vault.md` — sprint task `B-1 Week 3-4 PART 2`.
