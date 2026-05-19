---
name: Skill-project stuck anti-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: [pattern, anti-pattern, project-management, stuck, debugging-skill, "lang/en"]
lang: en
translated_from: skill-project-stuck-anti-pattern.md
---

# Skill-project stuck anti-pattern

> [!info] What this distills
> Contrast document to [[skill-project-success-pattern]]. Here we collect the **stuck signals** — symptoms that **precede** project stall. If a new project shows one or two signals, **early intervention** is recommended (a 6-hour weekly workshop is **cheaper** than scrapping 3 months later).

## The 6 stuck signals (cross-project evidence)

### Signal 1: Planning-overload, code-undershoot

The BMAD artifact sequence is beautifully completed (5/7 green, thousands of lines of PRD/Architecture), BUT the codebase has **rested 3+ weeks**. Evaluation becomes "I'm planning how I'll build it" instead of building.

Evidence:
- `mapesz.md` (2026-04-24): 5 of 7 BMAD artifacts DONE (A-Brief 264 lines + C-UX 1046 + E-PRD 732 + G-Arch 2303), BUT "Last code change: 2026-04-01 (~3 weeks resting)"
- Stuck identifier: BMAD-artifact-line-count : commit-count ratio > 100:1 on the planning side

**Correct (success pattern):** BMAD max 2 weeks, then Day-0 skeleton immediately into code.

### Signal 2: Repo `null` or empty

The frontmatter `repo:` field is `null` or `(empty folder)`, and **weeks later** still no initial commit. The project is stuck at "discussion level".

Evidence:
- `boulium.md` (2026-05-17): `repo_local_server: null # 2026-05-17: NOT on Claude server` — though BMAD installed, no code yet
- Stuck identifier: `repo: null` AND `updated:` hasn't changed in 14+ days

**Correct (success pattern):** Day-0 skeleton in ONE commit, even if logic is empty.

### Signal 3: NotebookLM missing or stale

The frontmatter `notebooklm:` field is missing, or last source-add was 2+ months ago. The project advances **without decision evidence**.

Evidence:
- In multiple stuck projects: NotebookLM field missing → tech-stack decisions are "hunch-based"
- In success projects (`boulium`, `mapesz`, `mfl-voice`, `kgc-erp`) **all** have an NB-UUID

**Correct (success pattern):** new project = new NotebookLM, 5-10 sources upload, 3+ deep-dive Q&A.

### Signal 4: Session-file fragmentation (many CLOSED 08-Sessions/ scattered, NOT crystallized)

Many short session files CLOSED, but Learnings **never** propagated to wiki / ADR / Memory. The learnings deficit accumulates.

Evidence:
- In stuck projects: 4-5 session files CLOSED, but `11-wiki/<project-related>` folder is empty → learnings "lost"
- In success projects (`superintelligent-vault`, `robbantott-kereso`) **every** session close has a `## Propagation log` + 2-3 new wikis spawned

**Correct (success pattern):** on session close, crystallization protocol is MANDATORY, [[Crystallization-protocol]].

### Signal 5: Cross-link starvation

The project file has **<3 wikilinks** total. At session start the agent only sees this one file and can't "unwind" the full context.

Evidence:
- Stuck-signal projects typically: 0-2 wikilinks in `02-Projects/<slug>.md`
- Success projects (`robbantott-kereso`, `superintelligent-vault`, `foxxi`): 12-30 wikilinks in the file

**Correct (success pattern):** every decision/wiki/session reference goes in the project file as `[[...]]`, NOT as a path string.

### Signal 6: "I'll do it when I have time"

The project file `## Open` section has 5+ Open questions, **all needing a decision** (user input pending), but **no `next-call` date** anywhere. The project is user-blocked with **no unblock-action**.

Evidence:
- `mapesz.md` "8 decisions pending from Atti" — but in session terms has been queued long
- `teszt-eu.md` "Atti spec, 8 decisions pending"

**Correct (success pattern):** every Open question with a date (`needs-call-by: 2026-MM-DD`) and `04-Tasks/Backlog.md` 🔴 open.

## Heatmap: which project shows which signal

| Project | S1 (planning-overload) | S2 (repo null) | S3 (no-NB) | S4 (lost-learnings) | S5 (cross-link <3) | S6 (no-next-call) |
|---|---|---|---|---|---|---|
| `boulium` | — | ⚠️ | — (3 NB) | — | — | ⚠️ |
| `mapesz` | ⚠️⚠️ | — | — | — | — | ⚠️ |
| `teszt-eu` | — | — | — | — | — | ⚠️ |
| `kgc-marketing` | — | — | — | ⚠️ | — | — |

## Early-intervention checklist

When 2+ signals are active, weekly 30-minute "stuck-audit":
1. **Re-read** the project file — what's THE VALUE worth 1 hour of focus right now?
2. **Kill** or **archive** or move to **active** — no zombie projects
3. **Single smallest step** (15 min): if repo null → first commit; if planning-overload → 1 Day-0 skeleton; if no NB → 3 source uploads
4. **Re-evaluate** in 1 week: have the stuck signals decreased?

## Responsibility for the "zombie project"

Vault convention: **never delete a project file, always `status: archived`**. But move it under the `02-Projects/Index.md` "🔬 Research / archive" section after **3+ months** of no progress.

## Source evidence

- 19 project files analyzed in `02-Projects/`
- 2 projects clearly in "stuck" zone (boulium discovery + mapesz active-design since 04-24)
- 5 projects in PRODUCTION state (koko, mfl-bot, kgshop-bluebird, petanque-kisgeparuhaz, foxxi-email-arhivum)
- 12 projects in ACTIVE-shipping (kgc-erp, kgc-berles, robbantott-kereso, foxxi, kgc-marketing, kgc-kivetitok, kgc-tv-cms, teszt-eu, mfl-voice, rojtesbojt, superintelligent-vault, myforge-dashboard)
- Crystallization-protocol Learnings-propagation volume: success-projects 8-26 bullets/super-session vs stuck-projects <2 bullets/session

## Related

- [[skill-project-success-pattern]] — contrast: the 7 success patterns
- [[Crystallization-protocol]] — session-close learnings feed (against Signal 4)
- [[sprint-day-0-skeleton-first]] — Day-0 skeleton (against Signal 2)
- [[notebooklm-seo-competitor-research-pattern]] — NotebookLM research (against Signal 3)
- [[Auto-context-loading]] — cross-link → context-load (against Signal 5)
- [[bmad-cross-machine-artifact-verification]] — BMAD-artifact verification (Signal 1 mitigation)

## Hungarian original

[[skill-project-stuck-anti-pattern]]
