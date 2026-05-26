---
name: vault-ko-ingest prompt tightening 2026-05-19
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#project/sv", "extraction-quality", "prompt-engineering"]
---

# vault-ko-ingest extraction-prompt tightening (vocab v3, 2026-05-19)

## Trigger

Wave-1 Memgraph entity-cleanup analysis ([[../06-Audits/2026-05-19 Memgraph entity-cleanup analysis]]) found **8,975 sc≥1 KO-DB-rooted entities**, of which **51% single-mention** and **44% ≥3 token sentence-fragment**. The two-tier `vault-graph-diff` Jaccard against the deterministic Tier-2 graphify extraction was **0.0070** — the LLM extraction was generating noise at scale (quoted strings, hex colors, code fragments, sentence fragments as "entities").

## Changes

Vocab version: `2026-05-17-v2-38pred` → `2026-05-19-v3-38pred-antinoise7`

### 7 new anti-noise rules

1. **Quoted-string subject ban** — subject cannot start with `"`, `'`, `„`. Extract the unquoted concept instead.
2. **Hex/URL/port/path/numeric → object-side** — if the subject is purely `#abc123`, `http://...`, a port number, `./foo.py`, or a literal numeric, move it to the object field of an annotation triplet.
3. **Code/operator-expression ban** — `def`, `class`, `function`, `return`, `import`, `lambda`, and operator-laden expressions (`x = y + 1`, `a += b`) are never valid subjects.
4. **60-char / 4-token subject cap** — subject must be ≤60 chars AND ≤4 tokens. Multi-sentence fragments are forbidden.
5. **ALL_CAPS / snake_case-only ban** — pure `KGC_ADMIN` and `my_function_name` are code-symbols, not concepts. Skip unless explicitly defined as a named entity.
6. **Fenced code-block exclusion** — content inside ```…``` documents syntax, not domain concepts.
7. **Single-mention confidence floor ≤0.5** — if a triplet appears once in a single source-file with no prior mention, cap confidence at 0.5.

Plus a 5-case `### Anti-noise examples` block with ✗ Wrong / ✓ Right contrasts.

## Activation

Default-on as of 2026-05-19 — every new `vault-ko-ingest --file <path>` run uses the v3 prompt. The `vocab_version` field in `pending/<hash>-request.json` lets downstream subagent-response handlers distinguish the eras.

## Verification target

`vault-graph-diff` Jaccard 0.0070 → **≥0.05** (Phase-4 acceptance gate). Phase-1+2 deletes alone won't get there (deletes only shrink the denominator); selective re-extract of the 5,524 sentence-fragment source-files with the v3 prompt is needed — scheduled 2026-05-22-23. See [[../06-Audits/2026-05-19 Memgraph cleanup Phase-3 next-step plan]].

## Backup

Pre-tightening prompt-template snapshot: `.vault-ko/prompts/vault-ko-ingest.py.bak.20260519-pre-tighten` (10,575 bytes).

## Related

- [[two-tier-graph-extraction]] — Jaccard 0.0070 finding context
- [[../06-Audits/2026-05-19 Memgraph entity-cleanup analysis]] — 7-rule derivation
- [[llm-graph-noise-cleanup-composite-filter]] — sibling cleanup pattern
