---
name: Letta virtual-context skeleton — birth audit
type: audit
tags: ["#type/audit", "memory-architecture", "letta", "memgpt", "virtual-context", "skeleton"]
created: 2026-05-19
updated: 2026-05-19
related:
  - "[[00-Meta/core-memory-schema]]"
  - "[[11-wiki/letta-virtual-context-pattern.en]]"
  - "[[02-Projects/superintelligent-vault]]"
session: "[[08-Sessions/2026-05-19-obsidian-vault]]"
---

# Audit — Letta virtual-context skeleton (idea #16, brainstorm 2026-05-19)

## Scope

Brainstorm idea **#16 Letta-style virtual-context OS layer** from
`06-Audits/2026-05-19 SV new development ideas brainstorm.md`. Skeleton-first
delivery — schema + CLI + simulator + migration doc + populated YAML — with
**zero touch on the live `11.11start` pipeline**. The migration itself is the
documented next step.

## What landed

| Artifact | Bytes | Role |
|---|---|---|
| `00-Meta/core-memory-schema.md` | ~5 KB | Formal spec of the 6-block file format, budget contract, page-fault protocol. |
| `00-Meta/core-memory.yaml` | ~4.8 KB | Populated core: distilled from User / SV-project / Backlog / Glossary / Infrastructure / ADRs. |
| `.vault-memory/scripts/vault-core-memory.py` | ~16 KB | CLI: `init` / `show` / `update` / `size` / `simulate` / `diff`. |
| `/usr/local/bin/vault-core-memory` | symlink | PATH-exposed CLI. |
| `11-wiki/letta-virtual-context-pattern.en.md` | ~7 KB | ~900-word migration guide, ASCII diagram, comparison with mem0 / Cognee / OpenAI Memories. |
| `06-Audits/2026-05-19 Letta virtual-context skeleton.md` | this file | Birth audit. |

## Token-savings projection

Empirical baseline: the legacy aggressive pre-load (cat-jel of 5 files at
`11.11start`) sums to ~15–20 K tokens. Mean ≈ 17 K.

Virtual mode (this skeleton):

| Component | Tokens | Note |
|---|---:|---|
| Core memory (always loaded) | **~1 K** | Measured: 995 tokens via `vault-core-memory size`. Budget allowed 2 K — we land 50 % under budget on day 0. |
| Archival page-fault (when needed) | ~2.5 K | 5 × ~500-token chunks via `vault-search`. Many turns won't need this. |
| **Total per session** | **~3.5 K** | vs. ~17 K classic. |
| **Saving** | **~13.5 K (79 %)** | Compounding across a 40-turn session: ~540 K tokens saved. |

The 79 % figure assumes one page-fault per session. In practice many sessions
will fault zero times (short Q&A, no need for archival), pushing the *average*
saving higher.

## The 6-block layout chosen

1. **`user_profile`** — Peti's house rules (language, terseness, destructive-edit
   confirmation). ~127 tokens. Source: `05-Memory/User.md`.
2. **`active_project`** — current session focus, status string from project frontmatter.
   ~107 tokens. Source: `02-Projects/superintelligent-vault.md`.
3. **`open_tasks`** — top 5 🔺/🔼 items from the urgent section.
   ~218 tokens. Source: `04-Tasks/Backlog.md`.
4. **`glossary`** — 14 hand-picked acronyms.
   ~208 tokens. Source: `00-Meta/Glossary.md` + hand-added (KO-DB, MemGPT).
5. **`infra_pins`** — reflexive infra facts (prod VPS IP, ports, paths).
   ~124 tokens. Hand-distilled.
6. **`recent_decisions`** — last 5 ADRs by mtime, title + 1-line `why`.
   ~184 tokens. Source: `07-Decisions/`.

Total: **968 char + structure overhead ≈ 995 tokens.** Comfortably under the
2048-token soft budget; the 3 K hard ceiling won't trigger.

## What is NOT in scope today

- **Migrating `11.11start`.** The new `VAULT_CONTEXT_MODE=virtual` flag is
  documented but unwired. The aggressive cat-jel remains the default.
- **A post-commit hook to auto-refresh `recent_decisions`.** Sketched in the
  wiki, not implemented. Would live in `vault-autosave`.
- **`active_project` auto-update on `11.11focus`.** The `update` CLI is built;
  the trigger isn't wired into the focus-switch script.
- **Shadow-mode acceptance gate.** Two-week parallel run between aggressive
  and virtual modes — depends on step 1 first.
- **Project-scoped glossary blocks.** Today one global `glossary` block. A
  per-project variant is an open question (in the wiki's "open questions").

## Unexpected findings (one)

The `05-Memory/` directory has files like `Feedback-claims-verification.md`,
`Feedback-fresh-verify-before-work.md`, `Agents-skill-suite.md`,
`Dashboard-access.md`, `Skill-map.md` — each holds 1–4 KB of *de facto* core
memory (recurring rules, agent-skill maps). The Letta schema's 6-block layout
**doesn't have a home for "skill suite" or "feedback rules"**. Two ways
forward:

1. Add a 7th block `feedback_rules` for cross-cutting house rules, raising the
   budget to ~2.5 K.
2. Keep those files in archival and let `vault-search` page them in when the
   agent's working context mentions a relevant keyword.

Option (2) is the Letta-orthodox call (archival is unlimited, core stays
small). Option (1) is more pragmatic if the feedback rules are referenced
*every* session. The acceptance gate measurements will decide.

## Smoke test results

```
$ vault-core-memory init
✓ Wrote /root/obsidian-vault/00-Meta/core-memory.yaml (4,852 bytes, ~995 tokens rendered)

$ vault-core-memory size
  rendered: 3,986 chars / ~995 tokens
  budget:   2048 tokens (soft)
  ceiling:  3000 tokens (hard)
  → exit 0 ✓

$ vault-core-memory simulate "Memgraph keepalive bge-reranker daemon"
  Direct core matches: infra_pins
  Saving: ~13,505 tokens (79 %)
  → exit 0 ✓

$ python3 -c "import yaml; print(list(yaml.safe_load(open('00-Meta/core-memory.yaml'))['blocks'].keys()))"
  ['user_profile', 'active_project', 'open_tasks', 'glossary', 'infra_pins', 'recent_decisions']
  → exit 0 ✓
```

All four checks pass.

## Next step (the actual migration)

`11.11start` currently sources `load-session-context` skill which still does
the aggressive pre-load. The minimal migration:

1. Wrap the cat-jel in `if [ "$VAULT_CONTEXT_MODE" = "virtual" ]; then
   vault-core-memory show; else ...`.
2. Default `VAULT_CONTEXT_MODE=aggressive` for one release cycle.
3. Add a `--virtual` flag to `11.11start` for per-session opt-in.
4. After two weeks of shadow-mode + acceptance metrics, flip the default.

That migration is the **next sprint task** — explicitly NOT this session.

## Related

- [[00-Meta/core-memory-schema]] — formal spec
- [[11-wiki/letta-virtual-context-pattern.en]] — narrative guide
- [[02-Projects/superintelligent-vault]] — parent project
- [[11-wiki/sv-01-memory-architecture]] — the B-2 sprint that's adjacent
- [[06-Audits/2026-05-19 SV new development ideas brainstorm]] — source of idea #16
