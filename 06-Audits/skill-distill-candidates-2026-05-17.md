---
name: skill-distill-candidates-2026-05-17
type: audit
tags: [audit, sv-b4, sv-b8, auto-distill, skeleton]
created: 2026-05-17
updated: 2026-05-17
---

# Skill-distill candidates — 2026-05-17

> SV B-4 + B-8 cross-axis sprint, **skeleton mode** (Week 1).
> Sessions scanned: **72** · with events: **24** · min-count threshold: **5**

## Top repetitive tool / skill tokens

| # | Token | Count | Distinct sessions | Examples |
|---|---|---|---|---|
| 1 | `batch` | 15 | 6 | 2026-05-08-rojt-s-bojt-weboldal, 2026-05-11-github-repo, 2026-05-12-obsidian-vault, +3 |
| 2 | `ingest` | 14 | 4 | 2026-05-12-obsidian-vault, 2026-05-16-kgc-robbantott-brakeres, 2026-05-17-obsidian-vault, +1 |
| 3 | `backfill` | 9 | 5 | 2026-04-30-vault-restructure, 2026-05-13-sv-functional-payoff, 2026-05-17-obsidian-vault, +2 |
| 4 | `vault-cleanup` | 7 | 4 | 2026-04-23-myforge-dashboard, 2026-05-09-vault-maintenance, 2026-05-12-obsidian-vault, +1 |
| 5 | `vault-search` | 6 | 5 | 2026-05-13-sv-b2-memory-architecture, 2026-05-13-sv-week1-implementation, 2026-05-14-kgc-marketing, +2 |

## Top tool-sequence bigrams (composition signal)

| # | A → B | Count |
|---|---|---|
| 1 | `vault-cleanup` → `vault-cleanup` | 3 |
| 2 | `batch` → `batch` | 3 |
| 3 | `ingest` → `ingest` | 3 |
| 4 | `backfill` → `backfill` | 2 |
| 5 | `batch` → `backfill` | 2 |
| 6 | `backfill` → `ingest` | 2 |

## Candidate distill targets

Tokens crossing threshold are **candidates** for auto-skill distillation. 
Skeleton mode does NOT generate drafts — Week 2 will spawn an LLM agent 
to draft `~/.claude/skills/auto-distilled/queue/<slug>.md` per candidate.

- [1] `batch` — 15 uses across 6 sessions — 🟢 strong
- [2] `ingest` — 14 uses across 4 sessions — 🟢 strong
- [3] `backfill` — 9 uses across 5 sessions — 🟡 borderline
- [4] `vault-cleanup` — 7 uses across 4 sessions — 🟡 borderline
- [5] `vault-search` — 6 uses across 5 sessions — 🟡 borderline

## Safety

- This run ONLY produced this audit file. **No** writes to `~/.claude/skills/`.
- Week 2 drafts will go to `~/.claude/skills/auto-distilled/queue/` (REVIEW state).
- Activation: user manually runs `mv queue/<slug>.md auto-distilled/<slug>/SKILL.md`.
- Forbidden targets: anywhere outside `~/.claude/skills/auto-distilled/`.

## Related

- [[11-wiki/sv-04-tool-composition]] — Voyager skill-library theory
- [[11-wiki/sv-02-recursive-self-improvement]] — ReCreate TTE, SAGE/SkillRL
- [[11-wiki/Crystallization-protocol]] — Learnings → skill auto-conversion
- `/usr/local/bin/vault-skill-distill` — this script
