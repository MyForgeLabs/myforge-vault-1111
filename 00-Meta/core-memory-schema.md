---
name: Core-memory schema (Letta-style virtual-context)
type: spec
tags: ["#type/spec", "meta", "memory-architecture", "letta", "memgpt", "virtual-context"]
created: 2026-05-19
updated: 2026-05-19
related:
  - "[[11-wiki/letta-virtual-context-pattern.en]]"
  - "[[11-wiki/sv-01-memory-architecture]]"
  - "[[05-Memory/README]]"
---

# Core-memory schema — Letta-style virtual-context core

The `00-Meta/core-memory.yaml` file is the **always-loaded ~2 KB head** of the
agent's context. It plays the role of the **L1 / "core memory"** in the Letta
(MemGPT) virtual-context-OS pattern: the bytes that are paid for on every turn,
in exchange for never page-faulting on user identity, active project, or live
sprint state.

Everything else lives in **archival memory** — the full vault — retrieved
on-demand via `vault-search` (semantic) or `vault-ko-query` (structured facts).
The agent issues those calls **only when a question can't be answered from
core**.

## File location & format

- **Path:** `/root/obsidian-vault/00-Meta/core-memory.yaml`
- **Parser contract:** must round-trip through `yaml.safe_load()` — no custom
  tags, no anchors, no Python objects.
- **Editor contract:** human-readable. Every block is a multi-line string under
  `content:`, so Obsidian / VSCode / `vim` users can hand-edit without breaking
  the structure.
- **Write contract:** all mutations go through `vault-core-memory update` so
  they are atomic (`atomic_write` from `vault_atomic`) and update
  `last_updated` automatically.

## Top-level fields

| Field | Type | Required | Purpose |
|---|---|---|---|
| `version` | int | yes | Schema version. Bump when block-set changes. Current: **1** |
| `generated_at` | ISO-8601 string | yes | When the file was last regenerated (`init`) or mutated (`update`). |
| `budget_tokens` | int | yes | Soft target for the **rendered** core size. Default **2048**. `vault-core-memory size` warns above this. |
| `blocks` | mapping | yes | The 6 named blocks below. Order is canonical (preserve in writes). |

## The 6 canonical blocks

Each block is an object with three keys: `content` (the human-readable text the
agent will see), `last_updated` (ISO-8601), and `source_hint` (a wikilink the
agent can follow if it wants the full version).

```yaml
blocks:
  user_profile:
    content: |
      Multi-line text describing the user.
    last_updated: 2026-05-19
    source_hint: "[[05-Memory/User]]"
```

| Block | What it holds | Updated when |
|---|---|---|
| `user_profile` | Who the user is, language, style preferences, tooling, recurring "house rules". | New user-preference learned (e.g. "Peti prefers terse Hungarian"). |
| `active_project` | The current session focus: project slug, sub-goal, exact phase. **Single project at a time.** | Every `11.11start` / `11.11focus` switch. |
| `open_tasks` | The 3-5 highest-priority items the user is steering toward right now. NOT the full backlog. | When a 🔺/⏫ Backlog item changes state. |
| `glossary` | In-flight acronyms / slugs likely to appear this session. ~10-15 entries. | When a new abbreviation is introduced or an active project rotates. |
| `infra_pins` | The handful of infra facts the agent needs reflexively: prod-VPS IP, common ports, "Memgraph is on 7687", "VNC on 5900". | Infra change (new host, port move). |
| `recent_decisions` | Last 3-5 ADRs (titles + 1-line "why"). Lets the agent avoid contradicting yesterday's decision. | New `07-Decisions/<...>.md` is written. |

## Budget contract

- **Target:** 2048 tokens, hard ceiling 3000.
- **Estimator:** rough `chars / 4` (matches GPT-style BPE within ~15%).
- **Enforcement:** `vault-core-memory size` exits non-zero **above 3000**. CI
  can run this as a gate. `init` self-prunes if a block exceeds 600 tokens.
- **Why this number:** Anthropic Claude's 1M-context billing cares about
  *every* turn. A 2 KB head loaded on every turn of a 40-turn session costs
  ~80 KB total; an aggressive 20 KB pre-load costs ~800 KB — a 10× saving
  before any archival call.

## `archival_search()` protocol

When core lacks the info to answer a user question, the agent emits a
**page-fault**: a structured `vault-search` (or `vault-ko-query`) call, with
the query string, an `intent` hint (`why`, `how`, `who`, `what`), and a
`top-k`. Workflow:

1. **Core hit attempt.** Scan the 6 blocks for direct match.
2. **Miss → page-fault.** Issue `vault-search "<query>" --top-k 5 --json`.
3. **Inject result transiently.** The retrieved chunks live in *this turn's*
   context only — they don't get written back to core unless they qualify
   under the crystallization protocol.
4. **Optional structured fall-back.** If the question is fact-shaped
   ("when did X land?", "what depends on Y?"), call
   `vault-ko-query "<pattern>" --top-k 8` against the 13K-fact KO-DB.

The `simulate` command on `vault-core-memory` visualizes what this flow would
cost in tokens — without actually paging anything in.

## Mutability rules

- **`user_profile`, `glossary`, `infra_pins`:** rarely change. Edits go via
  `update`, append-style.
- **`active_project`, `open_tasks`:** change every session. `11.11start` is
  the natural hook for both (planned migration — see
  [[11-wiki/letta-virtual-context-pattern.en]]).
- **`recent_decisions`:** auto-tail. When a new ADR is written,
  `vault-core-memory update recent_decisions "<new>"` prepends and trims to 5.

## Anti-patterns

- ❌ Inlining the full Glossary (currently ~5 KB). Core takes only the 10-15
  acronyms relevant to the active project.
- ❌ Stuffing every open Backlog item. The 460-line Backlog is archival; core
  takes the 3-5 burning ones.
- ❌ Embedding ADR full bodies. Core takes title + 1-line rationale; the agent
  fetches the body via `vault-search` if it needs to argue against the
  decision.

## Related

- [[11-wiki/letta-virtual-context-pattern.en]] — the why, with diagram
- [[11-wiki/sv-01-memory-architecture]] — the sprint that birthed this
- [[05-Memory/README]] — the *de facto* core memory today (file-grep style)
- [[06-Audits/2026-05-19 Letta virtual-context skeleton]] — birth-audit
