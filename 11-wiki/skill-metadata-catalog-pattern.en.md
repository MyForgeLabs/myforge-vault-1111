---
name: skill-metadata-catalog-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/agent", "#topic/skill-management", "#topic/progressive-disclosure", "#topic/scaling", "lang/en"]
lang: en
translated_from: skill-metadata-catalog-pattern.md
---

# Skill-metadata catalog — progressive-disclosure agent-skill loader

## TL;DR

The **Anthropic AgentSkills** spec is the key pattern: every skill is present in the agent's main prompt as a short (~100 char) `name + description` metadata block, **but the actual skill content (SKILL.md + examples + code) loads only** when the agent picks it. So 200-500 skills can fit under a 100K token budget (5-50K metadata layer) and runtime token cost is only for actually-active skills.

## Background (3+ source evidence)

- [[sv-03-multi-agent-orchestration]] — "skill metadata catalog, has_count: ~100 chars per skill"
- [[sv-03-multi-agent-orchestration]] — "AgentSkills Standard" Anthropic spec as progressive-disclosure pattern
- [[superintelligent-vault-research]] — Skill library growth and filesystem-as-state complementary pattern
- [[external-skill-cherry-pick]] — vault-applied cherry-pick via symlink (305 skills within 100K-prompt)
- Concrete evidence: `~/.claude/skills/` 305 skill folders with SKILL.md, each with a description in frontmatter

## Pattern

Three main building blocks:

1. **Catalog-level metadata block** in the main prompt. Each skill is one line: `<name>: <100-char description, what-to-use-when>`. 305 skills × ~150 char = ~45K token (still inside the cap).
2. **Skill-file content with progressive load**. When the agent decides to use `<skill-X>`, **then** it reads the full `SKILL.md` content (+ possibly sub-files). Detailed rules per level ([[Karpathy-LLM-Wiki-pattern#Progressive disclosure Level 1-3]]).
3. **Frontmatter-driven catalog generation**: the metadata is NOT a hand-written index file, but **generated from SKILL.md frontmatter**. The catalog stays auto-up-to-date.

Anthropic-spec-conformant structure (template):

```
~/.claude/skills/<skill-name>/
├── SKILL.md          ← frontmatter (name, description, triggers) + body
├── examples/         ← few-shot examples (load on demand)
└── scripts/          ← code helpers (executable Level-2)
```

## Anti-patterns

- **Loading every skill in full into the main prompt**: 305 skills × ~3000 token = 900K, main prompt explosion. Doesn't work even on 1M context (latency blowup).
- **Hand-maintained skill catalog**: time-consuming + drift. Generate from frontmatter, single source of truth.
- **Description explaining "one skill at length"**: the 100-char limit forces precise selection — at 500 chars the agent won't pick correctly.
- **No trigger condition in description**: "code well" description does NOT activate — the description tells **when to use** it, NOT what it does. Use "Use when X" / "Trigger: Y" convention.
- **Skill-name collision**: 2 skills with the same name at the same catalog level — ambiguity, agent picks at random. Namespace prefix mandatory (`bmad-*`, `wds-*`, `gds-*` etc.).

## Reusable rules

1. **Frontmatter-driven**: every skill at `~/.claude/skills/<name>/SKILL.md` + frontmatter `name`, `description`, `triggers` (opt).
2. **Description ≤ 200 char**, starting with 1-2 sentence "what + when". E.g. "Audit Azure quotas. Use when user mentions limits."
3. **Namespace prefix**: grouped skill bundles (BMAD, WDS, GDS, etc.) share a prefix — anti-collision.
4. **Progressive disclosure 3 levels**: Level 1 (SKILL.md body), Level 2 (`examples/`, `scripts/` on-demand), Level 3 (`docs/` deep-dive on-demand).
5. **Catalog build step**: generate `index.json` (or MEMORY/SKILLS.md) from frontmatters so it can be `cat`-ed into the main prompt.
6. **Trigger explicitness**: every description has `WHEN: ...` or `Trigger:` — else ambiguity → false-positive load.
7. **Plug-and-play symlink**: cherry-pick from external repo with a symlink ([[external-skill-cherry-pick]]) — don't copy, so upstream updates propagate.

## Pitfalls

- **Description drift**: over time the SKILL.md body grows with new features but the frontmatter description doesn't update → agent picks wrong skill. Weekly audit (`vault-skill-distill`).
- **Token-budget overshoot**: 305 skills × 150 char = 45K, but if someone writes 300-char descriptions it quickly hits 90K — main prompt damaged. Pre-commit hook at the 200-char cap.
- **Skill recursion**: if skill-A's description references skill-B and B references A → agent loops. Skill description should NOT be self-referential.
- **Trigger collision**: 2 skills "Use when user mentions database" — ambiguity-tie-break strategy needed (recency, project-context, explicit user-pick).

## Related

- [[sv-03-multi-agent-orchestration]] — multi-agent context where this pattern embeds
- [[external-skill-cherry-pick]] — vault-applied concrete implementation
- [[Karpathy-LLM-Wiki-pattern]] — progressive disclosure background
- [[memory-md-overflow-management]] — related token-budget thinking
- [[two-tier-graph-extraction]] — analogous "cheap-first, deep-on-demand" pattern

## Hungarian original

[[skill-metadata-catalog-pattern]]
