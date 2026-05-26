---
name: Auto-context-loading — start-time pre-load
type: wiki
tags: ["#type/reference", "agents", "11.11", "context"]
created: 2026-04-30
updated: 2026-04-30
lang: en
translated_from: Auto-context-loading.md
---

# Auto-context-loading

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[Auto-context-loading]] (Hungarian version).

After `/11.11start "<name>"`, the agent **immediately performs aggressive pre-load** — it reads all important context **before** the user asks the first question. Goal: have the full picture from second 1 of the session, no need to ask "what was happening last time".

## Project detection from the session name

The session name (`/11.11start` argument) contains a project-indicating keyword. The agent uses a project-detection table together with a glossary to resolve it:

| Session name contains | Project slug | Project file |
|-----------------------|--------------|--------------|
| `<project-keyword-1>`, `<alias-1>` | `<project-slug-1>` | `02-Projects/<project-slug-1>.md` |
| `<project-keyword-2>`, `<alias-2>` | `<project-slug-2>` | `02-Projects/<project-slug-2>.md` |
| ... | ... | ... |
| `vault`, `obsidian`, `agent-meta` | (vault-meta) | no project file, [[02-Projects/Index]] |
| `wellbeing`, generic words | (other) | (no project file) |

If ambiguous (multiple matches), the agent **asks**: "Which project does this refer to: ProjectA or ProjectB?"

## Aggressive pre-load — what to read

For a detected project slug = `<slug>`:

1. **Project file** — the full `02-Projects/<slug>.md`
2. **Last 5 sessions** — from `08-Sessions/` where `project: <slug>` in frontmatter (or substring match on filename)
3. **All affected ADRs** — from `07-Decisions/` where `tags` contain `#project/<slug>`, or name/body mentions the project
4. **Memory relevant section** — from `05-Memory/Infrastructure.md` the project section (e.g. for a backend project: the Postgres section, port mention, deploy info), `05-Memory/User.md` UI/UX preferences
5. **Tasks/Backlog #project tags** — from `04-Tasks/Backlog.md`, TODOs tagged `#project/<slug>` (open + last 10 closed)
6. **Host info** — if the project file has `repo_prod:` or `repo_dev:` for prod/dev, then the relevant "Runs here" section of `03-Hosts/<host>.md`
7. **Daily — today + yesterday** — `01-Daily/<today>.md` and the previous day, for context continuity

## The `## Pre-loaded context` section

The agent writes a `## Pre-loaded context` section near the top of the session file (BEFORE `## Goal`), listing what it read and a **short excerpt** (1-2 sentences) for each:

```markdown
## Pre-loaded context

> Auto-load 2026-04-30T15:23 — agent: claude

**Project:** [[02-Projects/<slug>]]
- Status: 🟡 active dev — dev mode on port 3004, deploy + design decision pending
- Tech: Next.js 16, Prisma 7 + adapter-pg, Postgres on :5433 with DB `<dbname>`

**Last 3 sessions:**
- [[08-Sessions/<date>-<slug>-feature-x]] — pricing v1 + email/SMS
- [[08-Sessions/<date>-<slug>-followup]] — settings UI, hide busy machines
- (older sessions exist — 2 more in the Sessions/Index)

**ADRs:**
- [[07-Decisions/<date> Business rules v1]] — tier 7/14/21/28, half-day, same-day cutoff
- [[07-Decisions/<date> Brand canonicalization]] — globals.css v5.0
- [[07-Decisions/<date> Git strategy — standalone repo + GitHub Flow]]
- [[07-Decisions/<date> Storage — Postgres own DB + Prisma]]

**Backlog (open #project/<slug>):**
- [ ] Add `<db>` to /opt/backups/backup.sh
- [ ] Admin Contact + ServiceRequest inbox UI
- [ ] Backend ERP integration
- [ ] Deploy stabilization — systemd <slug>.service
- [ ] Env-vars before prod-deploy
- [ ] systemd service <slug>.service
- [ ] Walkthrough §2-4

**Infra relevant:**
- [[05-Memory/Infrastructure#Postgres — `<host>-postgres` Docker container]]
- [[05-Memory/Infrastructure#Next.js 16 dev — cross-origin block]]
- [[03-Hosts/<dev-host>]] (project dev runs here)

**User UI/UX preferences:**
- HELP_<lang> under every section
- Click-time entity-id store, don't regex-parse
- "Make everything launchable from the dashboard"

> 7 sources · ~12K token context · ready
```

After the `> ready` marker, the agent waits for the user's first question **with the full preloaded context**.

## What if no project can be detected

The session name is e.g. "wellbeing", "agentic-os audit", "general thinking" — no specific project slug.

In this case the agent loads **only base context**:
1. [[02-Projects/Index]]
2. [[04-Tasks/Backlog]] first few paragraphs (urgent tasks)
3. [[01-Daily/Index]] today + yesterday
4. **Does NOT drill deeper** — waits for the user's direction

**Token budget for vault-meta sessions: ~2K tokens is enough.** The 15-20K cap is an upper limit on aggressive pre-load, **not a target**. If the session is vault-meta (workflow dev, vault restructure, smoke test, agent-meta work), the minimal version is cheaper and just enough — 3 sources × ~700 tokens. Use the 15-20K budget when a project is detected: project file + 5 sessions + ADRs + memory + backlog + host.

## When multiple projects are detected

E.g. `/11.11start "projectA + projectB review"`. The agent:
1. Loads both project files + the last 2-2 sessions (not 5-5, to avoid blow-up)
2. Focuses Memory pre-load only on the shared topic (e.g. brand)

## Budget

Target: **~15-20K token** pre-load. If you overshoot, first trim Tasks/Backlog entries (only top 5 priorities), then drop the older sessions.

## Audio overview

- EN narration (Charon voice): `[[.vault-nb/audio-overviews/Auto-context-loading.en.mp3]]`
- HU narration (Kore voice): `[[.vault-nb/audio-overviews/Auto-context-loading.hu.mp3]]`

Generated via Gemini 3.1 Flash TTS preview. ~1-2 minutes each. See [[gemini-3-1-flash-tts-pipeline]] for the pipeline.

## Related

- [[Crystallization-protocol]] — the stop-time counterpart
- [[Karpathy-LLM-Wiki-pattern]] — the meta-principle this implements
- [[claude-code-subagent-fanout]] — how to scale parallel work once context is loaded
