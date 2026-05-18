---
name: Karpathy LLM Wiki pattern
type: wiki
tags: ["#type/reference", "rag", "vault-design", "agents"]
created: 2026-04-30
updated: 2026-04-30
lang: en
translated_from: Karpathy-LLM-Wiki-pattern.md
source:
  - "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f"
  - "https://github.com/Ar9av/obsidian-wiki"
---

# Karpathy LLM Wiki pattern

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[Karpathy-LLM-Wiki-pattern.md]] (Hungarian version).

A minimal RAG pattern published by Andrej Karpathy in April 2026. **Core idea:** instead of classic retrieval (vector DB, embeddings, runtime search), the LLM **incrementally compiles** knowledge into a structured wiki that accumulates (compounds) over time.

## The three layers

| Layer | Purpose | Our equivalent |
|-------|---------|----------------|
| **raw/** | Immutable source — articles, transcripts, chat dumps, screenshot readings. The LLM **reads** but never **modifies**. | [[10-raw/]] |
| **wiki/** | Distilled knowledge, rewritten in own words. The LLM writes here — concepts, playbooks, glossary. Linked entries, consistent structure. | [[11-wiki/]] |
| **agent scratchpad** | Speculative notes, unorganized drag-drops. Unvalidated content allowed. | (not yet separated — `08-Sessions/` currently fills this role) |

## Compilation > Retrieval

Classic RAG: query → embed → search → top-k chunks → answer.

Karpathy: query → **read wiki-index.md** → drill into wiki pages → answer.

No vector DB. No embeddings. **Index.md is the map; the semantic structure lives in the wiki files.**

## Crystallization workflow

At the end of a working session (research thread, debug session, analysis), the LLM:
1. **Re-reads** the relevant `08-Sessions/` file
2. Produces an `11-wiki/` digest containing durable lessons
3. If a new concept emerged, writes a separate wiki entry
4. Leaves the `08-Sessions/` file raw — as reference

Our `/11.11stop` command already does this halfway: **Summary + Learnings + Next session** sections in the session file. The full Karpathy pattern further propagates the Learning bullets into separate `11-wiki/` entries.

## Operative components (Karpathy minimum stack)

- **CLAUDE.md / AGENTS.md** = the "schema-brain" — entity types, page formats, workflow rules. The LLM reads this first.
- **index.md** = the "map" — one per folder (Projects/Index.md, Hosts/Index.md, wiki/Index.md). The LLM uses these to navigate after the user's question.
- No vector DB — index + drill-down handles "hundreds of pages" (~200-300 files).

## What we adopt, what we don't

| Karpathy's pattern | Our vault |
|--------------------|-----------|
| `raw/` as immutable source | ✅ [[10-raw/]] exists |
| `wiki/` as distillate | ✅ [[11-wiki/]] exists (being developed) |
| Agent scratchpad separated | 🟡 Partial — `08-Sessions/` fills this, not cleanly separated |
| index.md per folder | 🟡 [[02-Projects/Index]], [[03-Hosts/Index]], [[06-Audits/Index]], [[10-raw/Index]], [[11-wiki/Index]] exist — being expanded |
| Crystallization workflow | 🟡 `/11.11stop` halfway — expandable with wiki propagation |
| CLAUDE.md schema-brain | ✅ [[AGENTS]] |

## Production validation — GenericAgent L0-L4 parallel

A 10.7k★ Chinese self-evolving agent framework, [`lsdefine/GenericAgent`](https://github.com/lsdefine/GenericAgent) (arXiv 2604.17091), chose the same 5-layer Karpathy pattern at production grade — two independent projects converged on this:

| GenericAgent | Our vault |
|---|---|
| **L0 — Meta Rules** (base behaviour + system constraints) | [[00-Meta/]] (Tag-taxonomy, Frontmatter-schema, AGENTS.md) |
| **L1 — Insight Index** (minimal index, fast routing/recall) | [[02-Projects/Index]], `MEMORY.md` |
| **L2 — Global Facts** (long-term stable knowledge) | [[05-Memory/User]], [[05-Memory/Infrastructure]] |
| **L3 — Task Skills / SOPs** (reusable workflows) | [[11-wiki/]] evergreen playbooks |
| **L4 — Session Archive** (distilled records of completed tasks) | [[08-Sessions/]] |

**9 atomic tools ≈ our stack:**

- `code_run`, `file_read/write/patch` ≈ Bash, Read, Write, Edit
- `web_scan`, `web_execute_js` ≈ WebFetch, WebSearch
- `ask_user` ≈ AskUserQuestion
- `update_working_checkpoint`, `start_long_term_update` ≈ session note + session-close crystallization

**Key difference: autonomy level.** GenericAgent does autonomous skill-growth (auto-crystallize after every task), our system is human-in-the-loop (batch preview + user approval at session close). The memory structure is the same, the autonomy level differs.

**Takeaway:** if you ever build a PaaS-style agent system, the 9-atomic-tool + L0-L4 layer pattern is a solid starting skeleton.

## Related

- [[Johnny-Decimal-prefix]]
- [[11.11-session-protokoll]]
- [[Kepano-File-over-App-filozofia]]
- [[Crystallization-protocol]]
- [[Auto-context-loading]]
