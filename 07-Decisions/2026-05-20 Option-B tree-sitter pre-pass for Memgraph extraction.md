---
name: Option-B tree-sitter pre-pass for Memgraph extraction
type: decision
created: 2026-05-20
updated: 2026-05-20
status: superseded
superseded_by: [[../06-Audits/2026-05-20 Option-B premise empirical refutation — graphify vocabulary is markdown not code]]
tags: ["#type/decision", "#project/sv", "memgraph", "extraction", "tree-sitter"]
---

# Option-B tree-sitter pre-pass for Memgraph extraction

## Status

🔴 **superseded 2026-05-20 PM** — empirical inspection of `graphify-out/graph.json` showed graphify parsed only `.md`/`.json`/`.sh` files (0 Python source files), so its vocabulary is markdown-section-paths, not code symbols. The Option-B prepass would add 156 code-symbol entities with **0 graphify intersection** → Jaccard moves from 0.0069 toward 0.0068 (slight regression from union growth).

See [[../06-Audits/2026-05-20 Option-B premise empirical refutation — graphify vocabulary is markdown not code]] for the full empirical diagnosis. The integration code (`extract_facts_treesitter`, 8 `code_symbol` predicates, `VAULT_KO_TREESITTER` env-gate) remains valid in the `treesitter-prepass-sandbox` branch as **KO-DB-only** capability (independent of Jaccard).

**Below: original proposal preserved for context. Do not act on it.**

---

**Originally: proposed** — design + skeleton landed 2026-05-20; integration into `vault-ko-ingest` deferred to Sprint-2 (target acceptance 2026-06-02).

## Context

A two-tier graph-extraction stack runs in parallel against the vault:

| Tier | Extractor | Vocabulary | Output |
|---|---|---|---|
| Tier-1 (LLM) | `vault-ko-ingest` (subagent-fanout) → `vault-graph-extract` | narrative concepts (`"Hostinger MCP SSH key discovery"`, `"silent-rollback gotcha"`) | 9,517 `:Entity` |
| Tier-2 (deterministic) | `graphify` (tree-sitter + Leiden) | code-symbols (`def extract_facts`, `class FactExtractor`) | 4,439 nodes |

The `vault-graph-diff` two-tier audit reports:

| Phase | Memgraph (Tier-1) | graphify (Tier-2) | Jaccard | Δ vs prior |
|---|---:|---:|---:|---:|
| Pre-cleanup (2026-05-19 AM) | 12,778 | 4,439 | 0.0070 | baseline |
| Post-cleanup (2026-05-19 PM) | 8,913 | 4,439 | 0.0078 | +0.0008 |
| Post-Phase-3 + reset (2026-05-20) | 9,517 | 4,439 | **0.0071** | ≈ flat |

The Phase-4 acceptance gate is **Jaccard ≥ 0.05** — a ~7× lift from the current 0.0071. The 2026-05-20 Phase-3 result audit + the 2026-05-19 vault-meta MEGA-session brainstorm (idea #14, Jaccard structural limit) conclude:

> **The two extraction stacks produce orthogonal vocabularies.** Pure prompt-tightening shrinks the Tier-1 denominator without growing the numerator (Tier-1 ∩ Tier-2). Structural vocab-merge is required to reach the gate.

The orthogonality is **not a defect** of either extractor — it is *by-design*: Tier-1's LLM is steered (correctly) to skip fenced code blocks (anti-noise rule #6), while Tier-2's tree-sitter parser only sees code. They cover **complementary halves of the corpus**.

## Three alternatives considered

### Option A — pure prompt-tightening (REJECTED post-Phase-3)

Iterate the `EXTRACTION_PROMPT_TEMPLATE` (vocab v3 → v4 → …) to nudge the LLM toward code-symbol vocabulary.

- **Pro**: cheap, no new infrastructure, single-file diff.
- **Con (decisive)**: even with vocab-v3 (38 predicates + 7 anti-noise rules + cleanup of 3,865 noise entities), Jaccard moved +0.0008. The LLM is being *steered away* from code-block extraction by rules #3 and #6 — exactly the right policy for narrative noise, but it forecloses code-symbol overlap. Removing rules #3+#6 would re-introduce the 30% noise we just cleaned up. Dead-end.

### Option B — tree-sitter pre-pass (RECOMMENDED)

Add a deterministic pre-pass to `vault-ko-ingest` that parses code blocks in the markdown source and emits typed `defines_function` / `defines_class` / `imports` triples *before* the LLM extractor runs on prose. These triples flow through the normal KO-DB ingest → `vault-graph-extract` → Memgraph pipeline as `:Entity` nodes whose names **structurally match** graphify's tree-sitter vocabulary.

- **Pro**: direct vocabulary-overlap construction. Deterministic ($0, no LLM). The extracted symbol names are byte-identical to graphify's (both use tree-sitter), guaranteeing numerator growth.
- **Pro**: orthogonal to the LLM anti-noise rules — they keep working on prose, the pre-pass owns code blocks.
- **Con**: only helps markdown files that *contain* code blocks (sessions, ADRs with examples, wiki gotcha-pages). Narrative-only files (project descriptions, retrospectives) are unaffected.
- **Con**: tree-sitter native binding is a new runtime dep — but the skeleton ships with a regex fallback for Python/JS, so no hard dep.

**Mitigation for the code-block-only risk**: optional **Tier-A+B HYBRID** — if Jaccard still under-gates after Option-B, layer Option-A (re-targeted prompt-tightening) on top, asking the LLM to surface code-symbols *mentioned in prose* (e.g. "the `extract_facts_subagent` function").

### Option C — graphify-as-secondary-extractor (REJECTED)

Run graphify as a sub-extractor of `vault-ko-ingest` (i.e. import its Leiden output into KO-DB).

- **Pro**: directly imports the 4,439 graphify nodes as `:Entity`. Jaccard → ~1.0 by construction.
- **Con (decisive)**: this is **circular** — it would import graphify's output back into the side we're measuring against graphify, and call the resulting tautology "agreement". The Jaccard metric becomes meaningless. We'd be measuring graphify-vs-graphify.
- **Con**: graphify owns its own ingest pipeline (Leiden community detection); decoupling its symbol-extraction from its clustering is non-trivial and brittle to graphify-tool version bumps.

## Recommendation

**Option-B**. The structural-vocab-merge premise is sound, the implementation is bounded (~250 LOC pre-pass + 8 new predicates), the risk is mitigatable (regex fallback + env-flag backout), and the expected Jaccard lift (0.0071 → ~0.06-0.10) clears the acceptance gate.

## Implementation plan (4-5 sub-tasks)

| # | Sub-task | LOC est. | Owner | ETA |
|---|---|---:|---|---|
| 1 | Standalone CLI `vault-ko-treesitter-prepass.py` with regex-fallback for Python/JS, JSON output matching `extract_facts_subagent` shape | 150-250 | this design session | Sprint-1 ✅ |
| 2 | Smoke-test `test_treesitter_prepass.py` with 3 code-block fixture | 50-80 | this design session | Sprint-1 ✅ |
| 3 | Wire pre-pass into `vault-ko-ingest.ingest_file` — call before `extract_facts_subagent`, merge results into the same triple-array | ~40 | Sprint-2 | 2026-05-22 |
| 4 | Re-ingest a representative slice (50 files: 11-wiki + 07-Decisions + 08-Sessions sampled), run `vault-graph-diff`, measure Jaccard lift | n/a | Sprint-2 | 2026-05-24 |
| 5 | If Jaccard ≥ 0.05 → roll out full backfill; if 0.03 ≤ J < 0.05 → enable Tier-A+B HYBRID; if J < 0.03 → revisit Option-C boundary | n/a | Sprint-2 | 2026-05-29 |

## New predicate vocabulary (8 typed predicates)

Add to `PREDICATE_VOCAB` in `vault-ko-ingest.py` under a new key `code_symbol`:

| Predicate | Subject | Object | Example |
|---|---|---|---|
| `defines_function` | source-file path | function name | (`11-wiki/sprint-day-0.md`, `defines_function`, `extract_facts_stub`) |
| `defines_class` | source-file path | class name | (`.vault-ko/scripts/scd2.py`, `defines_class`, `SupersessionResult`) |
| `defines_method` | source-file path | `Class.method` | (`.vault-ko/scripts/vault-ko-ingest.py`, `defines_method`, `Ingest.upsert_fact`) |
| `defines_constant` | source-file path | CONSTANT name | (`.vault-ko/scripts/vault-ko-ingest.py`, `defines_constant`, `PREDICATE_VOCAB`) |
| `imports` | source-file path | module/package name | (`.vault-ko/scripts/vault-ko-ingest.py`, `imports`, `sqlite3`) |
| `exports` | source-file path | exported symbol (JS/TS) | (`apps/web/src/lib/glicko.ts`, `exports`, `updateRating`) |
| `calls_function` | source-file path | function call site | (`.vault-ko/scripts/scd2.py`, `calls_function`, `fact_hash`) |
| `declares_variable` | source-file path | top-level variable | (`.vault-ko/scripts/vault-ko-ingest.py`, `declares_variable`, `SCD2_ACTIVE`) |

**vocab_version bump**: `2026-05-19-v3-38pred-antinoise7` → `2026-05-20-v4-46pred-treesitter8`.

Note: the **subject is the markdown source-file path** (the file the code-block lives in), NOT the inferred parent code-file. This keeps the provenance consistent with the rest of `vault-ko-ingest`. A future v5 could refine this to the *referenced* code-file path (parsed from a `// in foo.py` comment), but v4 keeps the contract simple.

## Acceptance criteria

- ✅ Standalone CLI runnable, `--help` works, `--dry-run` is a no-op
- ✅ Smoke-test passes (3 code-blocks → ≥3 `defines_*` triples)
- ⏳ After Sprint-2 integration + re-ingest of a 50-file slice: **`vault-graph-diff` reports Jaccard ≥ 0.05** on the next acceptance run
- ⏳ Full-vault backfill keeps Jaccard ≥ 0.05 (no regression after scale-up)
- ⏳ Memgraph entity-count grows by ≥ 500 (typed `defines_*` nodes), not by 5000+ (would indicate over-extraction noise — gate would auto-revert)

## Backout plan

- **Env-flag**: `VAULT_KO_TREESITTER=0` in the parent agent's env disables the pre-pass at `vault-ko-ingest` entry. Default `1` once Sprint-2 ships.
- **Layer-1 ENV-gate** (consistent with `VAULT_CRYSTALLIZE_APPLY`, `VAULT_KO_SCD2_ACTIVE`): the integration commit must check the env var on import, not at every call site.
- **Database-level revert**: all pre-pass triples carry `source_type = "code-symbol"` (new value) — a single SQL `DELETE FROM facts WHERE source_type = 'code-symbol'` cleanly rolls back the Memgraph entity inflation if Jaccard regresses.
- **Sandbox-branch first**: integration commit lands on `treesitter-prepass-sandbox` branch, re-ingest runs there, only `git merge` to main if Jaccard gate passes (consistent with the SV B-1 `crystallize-sandbox-*` branch pattern).

## Risk: code-block-only

**Risk**: markdown prose (project descriptions, retrospectives, narrative explanations) has zero code blocks → Option-B contributes nothing to those files' Jaccard slice.

**Mitigation**: optional **Tier-A+B HYBRID** — layer prompt-tightening (Option-A v4) *on top* of the tree-sitter pre-pass, asking the LLM to surface inline-code-references in prose (backticked symbols like `` `extract_facts_subagent` ``). The Option-A v4 prompt would say:

> "If the prose mentions a code symbol in backticks (e.g. `` `function_name` ``, `` `ClassName` ``, `` `module.method` ``), emit a `defines_function`/`defines_class` triple even though it's not inside a fenced code block. The pre-pass owns fenced blocks; you own backticked inline mentions."

This gives the LLM a *clear non-overlapping mandate* on code symbols (inline only), avoiding the rule #6 conflict.

ETA estimate for HYBRID layer (if Sprint-2 measurement triggers it): +1 session, ~2-3h.

## Related

- [[../11-wiki/two-tier-graph-extraction]] — pattern wiki (2026-05-20 section added)
- [[2026-05-19 vault-graph-diff cleanup Phase-3 next-step plan]] — predecessor plan
- [[../06-Audits/2026-05-19 Memgraph cleanup Phase-3 next-step plan]] — Phase-3 result audit
- [[../11-wiki/llm-graph-noise-cleanup-composite-filter]] — Tier-A+C cleanup pattern
- [[../11-wiki/sprint-day-0-skeleton-first]] — skeleton-first commit playbook this design follows
