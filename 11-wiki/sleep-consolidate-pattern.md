---
name: sleep-consolidate-pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#project/sv", "sleep-consolidate", "subagent-fanout", "constitutional-critic"]
---

# Sleep-consolidate pattern

REM-style **cross-session learning consolidation** for the Superintelligent Vault. Loosely modelled on biological sleep: during the night, the system replays episodic memories (`08-Sessions/`) and proposes promotions to semantic memory (`11-wiki/`) when a learning recurs across multiple sessions. A **two-stage Constitutional Critic** gate approves or rejects each proposal before any vault write.

CLI: [`/usr/local/bin/vault-sleep-consolidate`](file:///usr/local/bin/vault-sleep-consolidate)
Tests: `/root/obsidian-vault/.vault-ko/tests/test_sleep_consolidate_critic.py`
Brainstorm origin: idea #15 in [[../06-Audits/2026-05-19 SV new development ideas brainstorm]]

## Pipeline overview

```
08-Sessions/*.md
   │ parse_learnings()
   ▼
recurrence-clusters (Jaccard ≥ 0.30, ≥2 sessions)
   │
   ▼ ─────────────── Stage 1 (always runs) ──────────────
   │   rule-based fast-gate:
   │     • min/max length (80..1200 chars)
   │     • min_recurrence ≥ 2 sessions
   │     • novel_vs_wiki (token-overlap < 0.45)
   │   FAIL → skip · BLOCKS Stage 2
   ▼
   │ ─────────────── Stage 2 (opt-in) ────────────────────
   │   VAULT_SLEEP_LLM_CRITIC=1
   │   2-phase pending-file pattern
   │     phase 1: write /tmp/vault-sleep-pending/<bhash>/request.json
   │     phase 2: agent spawns subagent → writes response.json
   │     phase 3: re-run script → harvests verdict
   ▼
06-Audits/sleep-consolidate-<date>.md   (human-readable report)
06-Audits/sleep-consolidate-log.jsonl   (per-run summary)
06-Audits/sleep-consolidate-critic-log.jsonl  (per-cycle gate trace)
```

## Stage-2 LLM-Critic activation

### Env-flag activation

| Flag | Default | Effect |
|---|---|---|
| `VAULT_SLEEP_LLM_CRITIC` | unset | Stage-2 SKIP — only rule-based gate decides |
| `VAULT_SLEEP_LLM_CRITIC=1` | — | Stage-2 ON — Stage-1-passers go through subagent-fanout |
| `VAULT_SLEEP_APPLY=1 VAULT_SLEEP_REAL=1` | unset | Real apply (still skeleton; promotion writes are locked) |

Stage-1 failure **always** blocks Stage-2 invocation — no pending file is written for a candidate that the cheap rule-gate already rejects. This is the safety invariant the pytest suite (`test_stage1_fail_blocks_stage2`) asserts.

### 5-dimensional rubric prompt

Each pending request embeds a Constitutional Critic prompt with five rubric dimensions (each 0.0–1.0):

1. **factuality** — claim is verifiable, not speculative
2. **novelty** — semantic novelty against the closest existing wiki (the rule-gate already filtered token-overlap; the LLM checks whether a careful reader of the closest_wiki could already derive this bullet)
3. **durability** — still useful 6 months from now (vs ephemeral fix)
4. **vault_fit** — matches the Karpathy-LLM-Wiki evergreen style
5. **safety** — not user-private, not credentials, not session-private

Verdict mapping: all five ≥ 0.7 → `promote`; one or more in 0.5–0.7 → `borderline`; any below 0.5 → `reject`.

### request.json schema

Written to `/tmp/vault-sleep-pending/<bhash>/request.json` (where `<bhash>` is the first 12 chars of SHA256 over the representative bullet text):

```json
{
  "bullet": "<representative bullet text>",
  "sources": ["2026-05-17-foo.md", "2026-05-18-bar.md"],
  "cluster_size": 3,
  "rep_tokens": ["alpha", "beta", "..."],
  "closest_wiki": "11-wiki/maybe-related.md",
  "wiki_overlap": 0.18,
  "prompt": "You are the Constitutional Critic for the Superintelligent Vault's sleep-consolidation pipeline. … (5-dim rubric)",
  "instructions": "Write response.json with: verdict (promote|borderline|reject), confidence (0.0-1.0 aggregate), rationale (1-3 sentences), scores ({factuality, novelty, durability, vault_fit, safety}).",
  "schema_version": "sleep-consolidate-critic-v1"
}
```

### response.json schema (subagent output)

The general-purpose subagent writes:

```json
{
  "verdict": "promote",
  "confidence": 0.82,
  "rationale": "Recurring across 3 sessions, factually verifiable from KO-DB, no overlap with the closest wiki beyond shared tokens; durable safety pattern.",
  "scores": {
    "factuality": 0.9,
    "novelty": 0.8,
    "durability": 0.85,
    "vault_fit": 0.9,
    "safety": 1.0
  }
}
```

Verdict synonyms accepted: `promote|approve|accept` → promote; `reject|discard|skip` → skip; `borderline` (or anything else) → fall back to Stage-1 verdict.

### Subagent-fanout trigger

The CLI **does not spawn subagents inline**. The pattern mirrors [[claude-code-subagent-fanout]] + the [[Crystallization-protocol|crystallize-pending skill]]:

1. The script writes `request.json` and exits with the candidate marked `"decision": "pending"`.
2. The **calling agent** (claude-code or codex CLI) detects pending requests and spawns one general-purpose Agent per pending bullet, passing the prompt + request.json path.
3. The subagent writes `response.json`.
4. The agent re-runs `vault-sleep-consolidate` — this time `_try_load_llm_critic()` finds the response, harvests the verdict, and finalises the audit log.

This is the same 2-phase pattern used by `11.11crystallize`'s G-Eval scoring, the KO-DB triplet-extraction ingest, and the BMAD vault bridge.

## Audit logs

| Path | Format | Purpose |
|---|---|---|
| `06-Audits/sleep-consolidate-<date>.md` | Markdown | Per-run human-readable report (one per CLI invocation) |
| `06-Audits/sleep-consolidate-log.jsonl` | JSONL | Per-run summary: candidates, promotions, pending count, stage-2 enabled? |
| `06-Audits/sleep-consolidate-critic-log.jsonl` | JSONL | **Per-cycle** gate trace: cluster_id, stage-1 decision + rules, stage-2 decision, final decision, sources, bullet preview |

The critic-log entry is appended **once per `critic_gate()` call** (i.e. per recurrence candidate), unless side-effects are suppressed by `--dry-run` / `--json` previewing flags.

## Pytest coverage

`/root/obsidian-vault/.vault-ko/tests/test_sleep_consolidate_critic.py` — 9 tests:

- `test_default_disabled_skip` — env-var unset → stage-2 SKIP, no pending file
- `test_enabled_writes_pending` — env-var set + stage-1 PASS → request.json with 5-dim rubric
- `test_response_parse[promote|approve|reject|discard|borderline]` — 5 parametrised verdicts
- `test_stage1_fail_blocks_stage2` — novelty-fail blocks stage-2 invocation (no pending file)
- `test_audit_log_written_per_cycle` — critic-log JSONL line emitted

Run: `pytest /root/obsidian-vault/.vault-ko/tests/test_sleep_consolidate_critic.py -v`

## Related

- [[claude-code-subagent-fanout]] — the underlying 2-phase pending pattern ($0 cost)
- [[Crystallization-protocol]] — analogous workflow for session-end Learning bullets
- [[multi-layer-safety-gate]] — Constitutional Critic + sandbox-branch dance
- [[Karpathy-LLM-Wiki-pattern]] — why "promote to evergreen" is the right primitive
- [[async-memory-consolidation-letta]] — Letta MemGPT prior art for sleep-style consolidation
