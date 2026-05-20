---
name: Subagent collateral-bug discovery pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#concept/subagent", "#concept/debugging"]
---

# Subagent collateral-bug discovery pattern

When a subagent's task report includes **run-time errors from a side-quest** — code paths it tried but failed on while pursuing its primary objective — those errors are a **high-value bug-finding signal**, not noise to ignore.

## The pattern

1. Main thread spawns subagent X for task A.
2. Subagent X, while completing task A, exercises tangentially-related code path Y (e.g. read a dependent module, call a sibling CLI).
3. Code path Y throws an error.
4. Subagent X reports task A complete, mentioning the Y-error as an aside.
5. **Main thread treats Y-error as a separate, high-priority bug — extracts the stack trace and roots-causes.**

## Why this is signal, not noise

- Subagent X had no incentive to fabricate the Y-error. It happened to it organically.
- Main thread might never exercise Y directly. Subagent X's tangential exposure caught a bug that direct unit-tests missed.
- The Y-bug was likely silent — no user-visible symptom yet.

## When it bit us (2026-05-19)

Three P0/P1 bugs caught this way in a single PM session:

1. **SQLite `executescript()` implicit-COMMIT** — Wave-1 subagent designed the hash-refactor migration; while writing the script, a smoke-test surfaced `cannot commit - no transaction is active`. Reported as "decision-point #1 for main-thread review". → [[sqlite-executescript-implicit-commit]]

2. **`vault-gh-bridge` idempotency-FAIL** — Wave-4 subagent (#14 APPLY first-run) ran second-time-idempotency-test as part of the verify. Reported `files_unchanged: 0` as anomaly. → [[idempotency-frontmatter-date-anchor]]

3. **`vault-ko-ingest.upsert_fact` post-#34 P0 schema-bug** — Wave-4 Memgraph Phase-3 subagent tried to re-extract → `OperationalError: no column named provenance`. Reported as blocker. **Every new ingest silently broken across the vault until caught.** → [[schema-migration-downstream-grep-checklist]]

Without the subagent reports, all three bugs would have been latent for days-to-weeks. The Memgraph Phase-3 subagent specifically saved us from a vault-wide production-broken state.

## Anti-pattern: dismissing tangential errors

The temptation: "subagent says task A complete, that's the deliverable — Y-error is its problem, move on."

The cost: production-broken state that surfaces in 3 days when an unrelated workflow trips it. Now the debugging context (the subagent's intermediate state, the exact stack trace, the path that led there) is gone.

## How to extract the signal

When a subagent report includes:
- "Run-time error during smoke-test"
- "Decision-point N for main-thread review"
- "Anomaly N: ..."
- "Did not verify because <unrelated module> threw"

**Always**:
1. Read the full error message in the report
2. Trace to the offending file:line
3. Diagnose root-cause yourself (don't ask a subagent — context-loss between agents wastes tokens)
4. Patch + smoke-test
5. Add to the propagation log as a real bug-fix, not as session-noise

## Related

- [[subagent-fanout-for-planning-artifact.en]] — broader subagent-orchestration pattern
- [[schema-migration-downstream-grep-checklist]] — one of the bugs caught this way
- [[sqlite-executescript-implicit-commit]] — another bug caught this way
- [[idempotency-frontmatter-date-anchor]] — third bug caught this way
