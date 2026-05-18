# Contributing to MyForge Vault 11.11

Thank you for considering a contribution! This repo is a **reference implementation** of a self-improving Obsidian-vault architecture — we welcome both small fixes and pattern-level contributions.

## Quick links

- [Live docs site](https://myforgelabs.github.io/myforge-vault-1111/)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Changelog](./CHANGELOG.md)
- [Issue tracker](https://github.com/MyForgeLabs/myforge-vault-1111/issues)

## What can you contribute?

### 1. **New evergreen wiki** (`11-wiki/<slug>.md`)
A reusable pattern, lesson, or architectural insight. Must be **evergreen** (not project-specific), **source-cited** (3+ evidence bullets), and **min. 70 lines**. See existing wikis for format. Frontmatter:

```yaml
---
name: <slug>
type: wiki
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: ["#type/wiki", "<topic-tag>"]
---
```

### 2. **Architecture Decision Record** (`07-Decisions/<date> <topic>.md`)
A significant architectural choice with rationale, alternatives considered, and backout plan.

### 3. **Bug-fixes** to scripts or `mkdocs.yml`
Verify locally before PR — `mkdocs build` should succeed.

### 4. **English translations** of existing Hungarian wikis
Pattern: `<original-slug>.en.md` sibling file with `lang: en` and `translated_from:` frontmatter.

### 5. **Frontier-research wiki**
Distillation of a 2026+ paper / repo (DSPy, Letta, GraphRAG, etc.). License-aware — credit the upstream source.

## Workflow

1. **Fork** + clone
2. **Branch:** `feat/<short-description>` or `fix/<short-description>`
3. **Make changes** — keep diffs scoped (one wiki / one ADR / one fix per PR)
4. **Local check:** `pip install -r requirements.txt && mkdocs build`
5. **PR** with descriptive title and brief summary

## Style guide

- **Markdown:** GFM-compatible, no Obsidian-only callouts in public files (use `> [!note]` GFM-style)
- **Wikilinks:** `[[target]]` allowed in `11-wiki/` and `07-Decisions/` (Obsidian-native), but mkdocs renders them as plain text — prefer markdown `[label](path)` when broader reach matters
- **Language:** Hungarian primary, English translations welcome (`*.en.md`). Both languages first-class.
- **Source-citation:** every claim in a wiki must point to ≥1 source (vault session, ADR, external paper)

## Code of Conduct

This project follows the [Contributor Covenant](./CODE_OF_CONDUCT.md). Please be respectful and constructive in all interactions.

## Questions?

Open a [Discussion](https://github.com/MyForgeLabs/myforge-vault-1111/discussions) or email `11.11@myforgelabs.com`.
