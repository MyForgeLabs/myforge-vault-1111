---
name: Skill-project successful pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: [pattern, project-management, sprint, productivity, meta, "lang/en"]
lang: en
translated_from: skill-project-success-pattern.md
---

# Skill-project successful pattern

> [!info] What this distills
> Distills the **common patterns** across the vault's 19 active/production projects into a single evergreen playbook. When a new project starts, this checklist is the "Day 0" kit — copy it, do these IN ORDER. When an existing project stalls, contrast against this list to find the missing piece.

## The 7 canonical patterns (cross-project evidence)

### 1. One-project-one-file Source-of-Truth

Every project starts with ONE `02-Projects/<slug>.md` file, with **frontmatter**: `name`, `type: project`, `status:`, `created:`, `updated:`, `repo:`, `notebooklm:` (if any), `cssclasses:`. The file is a **living document** — not a static README but a **daily-updated state**.

Concrete evidence:
- `koko.md` frontmatter `status: done-with-backlog`, `originSessionId`, `notebooklm` UUID → from 1 file you can reconstruct the full project history
- `robbantott-kereso.md` 80+ lines current-state section, HEAD commit hash, pytest baseline
- `mfl-bot.md` 40 lines: systemd-service name, log-path, dev-path — everything "where it runs and how I check it"

**Value:** at session start, one `Read` gives the agent full context.

### 2. NotebookLM deep-research for every new project

In most successful projects: a **dedicated NotebookLM** UUID in frontmatter + 3-7 sources uploaded + 5-10 deep-dive Q&A documented. Research shortens the **planning phase** by 1-2 weeks.

Evidence:
- `boulium.md`: 3 NotebookLMs (boulium + 2× MAPESZ cross-ref) + 5 deep-dive Q&A docs
- `mapesz.md`: `notebooklm: e7b17612-…` + BMAD-planning output 7 artifacts
- `mfl-voice.md`: 4 NotebookLMs, 123 sources, 22 HU asks, 3 audio overviews
- `kgc-erp.md`: NotebookLM KGC-4 integration research, 161 sources / 28K token

**Value:** technology decisions are evidence-grounded, not hunch-based.

### 3. BMAD workflow / 7-artifact planning

Stuck projects are the ones where planning-output **never converted** to code. Successful projects do the 7-artifact BMAD (A-Product-Brief, B-Trigger-Map, C-UX-Scenarios, D-Design-System, E-PRD, F-Testing, G-Architecture) quick-pass (ideal: <2 weeks), then **immediately build the Day-0 skeleton**.

Evidence:
- `mapesz.md` marks 5 of 7 artifacts DONE (1046+732+2303 lines) — but the code side has rested 3+ weeks → planning-overload risk
- `robbantott-kereso` reversed this: FIRST the Day-0 pipeline, BMAD only after 7 commits stood

**Value:** structured planning state, but does NOT replace code.

### 4. Day-0 skeleton-first

Every NEW project's FIRST commit is a **skeleton in 1 commit**, functional code = 0 (except <20-line + no-API). What it contains: package.json, .gitignore, README.md skeleton, 1 health-check endpoint, 1 sketch UI. See [[sprint-day-0-skeleton-first]].

Evidence:
- `robbantott-kereso` BMAD-less Day-0 → 7 commits in one sprint
- `mfl-voice` sprint 1 — mockup HTML first, voice MVP second
- `kgshop-bluebird` production, scaffold-first → PM2 + scraper later

**Value:** codebase starts, momentum can build.

### 5. Session-driven progress (08-Sessions/<slug>.md)

Every work block gets a dedicated session file: `08-Sessions/YYYY-MM-DD-<project>.md`. Frontmatter `project:` + `originSessionId:`. **Summary + Learnings + Next** sections on session close. Per crystallization protocol, the Learnings propagate to the vault.

Evidence:
- `robbantott-kereso` 2026-05-16 session → 7 commits + 3 new wikis + new ADR
- `superintelligent-vault` 5× "super-session" (~3-16h) landed 95 tasks
- Vault has 168 session files (`08-Sessions/`) in the last 6 months

**Value:** timestamped progress history, learnings feed, crystallization input.

### 6. Production = systemd + nginx + named-deploy-path

EVERY project with PRODUCTION status has:
- **Dedicated deploy-path** (e.g. `/opt/petanque/web`, `/root/projects/mfl-bot`)
- **Process manager** (PM2 or systemd-service)
- **Nginx reverse-proxy** (or Caddy)
- **Named service** and audit-log (`journalctl -u <service>`)
- **Backup path** in canonical location (`/opt/backups/daily/`)

Evidence:
- `mfl-bot.service` systemd + journalctl
- `kgshop-bluebird` PM2 + cron-scraper
- `petanque-kisgeparuhaz` PM2 `petanque-web` port 3002
- `foxxi` Hostinger staging + nginx + lscache
- `myforge-dashboard` systemd + Tailscale-only

**Value:** "runs in prod" reproducible minimum package.

### 7. Cross-link project → wiki + ADR + Memory

Every successful project file wikilinks its **wiki patterns**, its own **ADRs**, and relevant **Memory** sections. This is the Karpathy filesystem-as-state — the index system unfolds naturally.

Evidence:
- `robbantott-kereso.md` 12+ wikilinks: `[[07-Decisions/...]]`, `[[08-Sessions/...]]`, `[[11-wiki/nextjs-api-proxy-bridge]]`
- `mapesz.md` `[[07-Decisions/2026-04-24 MAPESZ PWA platform-független architektúra]]`
- `foxxi.md` design-system wiki + ACF→Elementor playbook

**Value:** at session start, the agent unwraps the entire context graph from one file.

## Order (the meta-pattern)

```
1. (Discovery) → 02-Projects/<slug>.md + frontmatter
       ↓
2. NotebookLM deep-research + 5-10 Q&A documented
       ↓
3. BMAD 7-artifact (fast, max 2 weeks) — but DONE planning ≠ code
       ↓
4. Day-0 skeleton commit (1 commit, 0 functional code except <20 lines)
       ↓
5. Session blocks (08-Sessions/) — Summary+Learnings+Next on every close
       ↓
6. Production (systemd+nginx+backup+monitoring) — if the use case warrants
       ↓
7. Cross-link every step → wiki + ADR + Memory (filesystem-as-state)
```

## What signals a "healthy" project file

The last-updated metric **<14 days**. The project file contains:
- [ ] Current frontmatter (`updated:` < 14 days)
- [ ] Current-state section with date
- [ ] HEAD commit hash or production version
- [ ] 3+ wikilinks (cross-link)
- [ ] NotebookLM UUID (research evidence)
- [ ] Tech-stack table
- [ ] 1+ session link in the last month

## Related

- [[sprint-day-0-skeleton-first]] — Day-0 skeleton-first playbook
- [[skill-project-stuck-anti-pattern]] — contrast: what does NOT work
- [[bmad-cross-machine-artifact-verification]] — BMAD artifact verification on session close
- [[Auto-context-loading]] — project-file detection at session start
- [[11.11-session-protokoll]] — session organisation
- [[notebooklm-seo-competitor-research-pattern]] — NotebookLM research flow
- [[Karpathy-LLM-Wiki-pattern]] — background philosophy (filesystem-as-state)

## Hungarian original

[[skill-project-success-pattern]]
