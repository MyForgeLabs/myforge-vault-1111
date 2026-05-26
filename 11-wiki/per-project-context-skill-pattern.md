---
name: Per-project context-skill pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#tech/agent-skills", "context-loading", "evergreen"]
status: evergreen
---

# Per-project context-skill pattern

## TL;DR

Multi-projekt agent-vault-on a session-start aggressive context-load 15-20K token volt — projekt-szintű context-skill suite (`<slug>-context/SKILL.md`) ezt **2.1-3.7K token-ra csökkenti** (median ~2K, **78-86% token-saving**). Per-projekt skill-fájl Claude Code AgentSkills auto-discovery-vel beágyazódik, és a skill `description:` field-jén szöveg-triggerre indul. Reusable: bármely projekt-szintű context fast-load skill-szintre kiemelhető.

## Háttér

- **Problem**: session-start `cat 02-Projects/<slug>.md + utolsó 5 session + minden érintett ADR` aggressive pre-load = 15-20K token
- **Solution**: Lean per-project context-skill (~50-100 sor SKILL.md) = ~2K token
- **Mechanism**: AgentSkills auto-discovery `name:` + `description:` frontmatter alapján, trigger-szövegre
- **Wider context**: B-2 sprint Week 3 rewrite `load-session-context` skill-ben (`lean ~5K token working+top-K episodic + semantic on-demand`)

## Mintázat

**SKILL.md format:**

```markdown
---
name: <slug>-context
description: "Pre-loaded context for <project>. Triggers when user asks about <project> / <slug> / <related-keywords>."
---

# <Project Name> — Context Pre-load

## Quick state
<frissh státusz a 02-Projects/<slug>.md alapján>

## Key files
- [[../../../obsidian-vault/02-Projects/<slug>]]
- [[../../../obsidian-vault/07-Decisions/<adr-list>]]

## Recent sessions (last 5)
<lista>

## Active backlog
<top-3 backlog-task>

## Convention / lock-state
<projekt-specifikus konvenció>

## Useful queries
- `vault-ko-query --substring "<projekt-slug>"`
- ...
```

## Anti-pattern

- **Aggressive 15-20K cat-jel** — minden session-start 12-18 perc agent-time + token-cost magas
- **No-projekt-state skill** — agent kérdezi a projekt-history-t 12-15 round → 3-5 round (skill-pre-load)
- **Skill túl-bőséges** (>200 sor) — defeats lean-purpose
- **Stale skill** — projekt-state változik, skill nem frissül

## Reusable szabályok

1. **Egy skill / projekt** — NEM N skill, NEM közös skill
2. **Frontmatter `description:` trigger-words** specifikusak (slug + kulcs-keywords)
3. **Min 50 sor / max 200 sor** — lean-but-complete
4. **Cross-link `02-Projects/<slug>.md` master**-re — single source of truth
5. **Refresh weekly** (cron-rec) ha projekt-state változó
6. **Konvenció / lock-state szakasz** kritikus — agent NE újra-kérdezze (pl. Client-A-Bérlés URL = `187.77.70.36:3004`, BMAD Sprint 26 W1)
7. **Recent sessions szakasz** auto-frissítendő (mtime-rank sessions/<slug>)

## Buktatók

- **Slug ütközés** (pl. `client-b` = Client-B Client-B-clinic + client-b-cv-website) — explicit disambiguation `description:`-ben
- **Project-PII** — context-skill NEM publikálható publikus repó-ba (client-info). `02-Projects/**` always-skip a scrub-rules-on
- **Stale-trigger** — projekt-status változik de skill nem frissül → context outdated

## Mérnöki őszinte (vault-szintű 5 skill landed)

| Skill | Token-cost | ROI tier |
|---|---|---|
| kgc-erp-context | ~2.2K | Tier-1 (aktív Sprint 26 W1) |
| superintelligent-vault-context | ~2.7K | Tier-1 (meta-projekt) |
| rojtesbojt-context | ~3.7K | Tier-1 (complex brand-lock) |
| internal-dashboard-context | ~2.9K | Tier-2 (less-frequent) |
| client-d-federation-context | ~2.1K | Tier-2 (parkolt projekt, re-spin cost magas) |

**Median token-saving**: ~75-80% vs aggressive cat-jel.

## Kapcsolódó

- [[load-session-context-pattern]]
- [[Auto-context-loading]]
- [[skill-metadata-catalog-pattern]]
- [[bmad-context-preload-pattern]]
