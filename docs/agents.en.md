---
name: Shared agent instructions
type: reference
tags: [meta, agent-instructions, "#type/reference"]
audience: [claude, codex, gemini]
created: 2026-04-23
updated: 2026-04-30
---

# Shared agent instructions (Claude / Codex / Gemini)

All three AI agents load this file at session start — it is the single entry point into the knowledge base.

## Who the user is

- **Name:** Peti (user@example.com)
- **Language:** Hungarian primarily, English technical terms are OK
- **Server:** `/root` headless Linux, VSCode extension + SSH + occasional VNC
- **Style:** terse responses, explanation only when needed. Details in [[05-Memory/User]]

## Vault structure (Johnny-Decimal folder-prefix + Karpathy LLM-Wiki pattern)

```
/root/obsidian-vault/
├── README.md                     human entry point
├── AGENTS.md                     this file (stays at root — symlink-compatible)
├── 00-Meta/                      vault rules
│   ├── README.md
│   ├── Tag-taxonomy.md           MANDATORY tag conventions (#env/prod, #type/host, etc.)
│   ├── Frontmatter-schema.md     MANDATORY YAML schema per type
│   ├── Glossary.md               slug + abbreviation resolver (KGC, MFL, MAPESZ, BMAD…)
│   └── templates/                Daily / Session / Project templates
├── 01-Daily/                     daily logs (YYYY-MM-DD.md, autogen)
│   └── Index.md
├── 02-Projects/                  READ THIS FIRST
│   ├── Index.md                  every project + status in 5 groups
│   └── <project>.md
├── 03-Hosts/                     VPSes + shared hosting
│   ├── Index.md
│   └── <host>.md
├── 04-Tasks/
│   ├── Backlog.md                Obsidian Tasks plugin
│   └── Dashboard.md              filtered query views
├── 05-Memory/                    persistent context
│   ├── README.md
│   ├── User.md                   user profile, preferences
│   ├── Infrastructure.md         server, VNC, ports, KGC Postgres
│   ├── Skill-map.md              243+ agent-skills grouped
│   ├── Agents-skill-suite.md     skills available on myforge-dashboard
│   └── Dashboard-access.md       Tailscale-only access protocol
├── 06-Audits/                    snapshot reports
│   ├── Index.md
│   └── System_Health.md          weekly auto-gen vault integrity
├── 07-Decisions/                 ADR-style decision log
├── 08-Sessions/                  /11.11-session logs (test → _archive/)
├── 10-raw/                       Karpathy: raw input (immutable)
│   └── Index.md
└── 11-wiki/                      Karpathy: distilled knowledge (evergreen)
    └── Index.md
```

## What to do AT SESSION START

**MANDATORY workflow** (after `/11.11-uj-session` the agent automatically):

1. **Detect the project** from the session name based on the [[wiki/Auto-context-loading#Projekt-detektálás a session-névből|project-detection table]]
2. **Aggressive pre-load** — read according to [[wiki/Auto-context-loading]]:
   - Project file + last 5 sessions + every relevant ADR + relevant slice of Memory + `#project/<slug>` Backlog entries + Host info + today's/yesterday's Daily
   - Target: ~15-20K token context
3. **Write a `## Pre-loaded context` section** into the session file — list what you read, with a 1-2 sentence summary of each
4. **Only then** wait for the user's first question — with full context

If an unknown abbreviation / slug comes up → [[meta/Glossary]]. If the project is ambiguous → ask back.

**If no project can be detected** (e.g. "wellbeing", "general thinking") — load only base context: [[../02-Projects/Index]], urgent items from [[../04-Tasks/Backlog]], today's + yesterday's Daily.

## When to WRITE here

Whenever some long-term useful info comes up:

| Event | Where to write |
|---------|---------|
| New project starts | New `02-Projects/<name>.md` + row in the matching group table in [[../02-Projects/Index]] |
| Existing project status changed | Update `02-Projects/<name>.md` "Current state" + `updated:` |
| Learned a user preference | [[05-Memory/User]] or new `05-Memory/Feedback-<topic>.md` |
| Server/infra knowledge (port, host, service) | [[05-Memory/Infrastructure]] |
| Major architecture decision | New `07-Decisions/YYYY-MM-DD <topic>.md` |
| **New TODO** | [[../04-Tasks/Backlog]] (red urgent / yellow watch / green hygiene) |
| **Task done** | [[../04-Tasks/Backlog]] — Completed section with date |
| **New concept / playbook** (evergreen) | `11-wiki/<topic>.md` — in your own words |
| **New article / transcript** (immutable) | `10-raw/YYYY-MM-DD — <source>.md` |

## Formatting conventions

- **Date:** `YYYY-MM-DD` ISO; convert relative dates from the user (e.g. "Thursday") to ISO
- **Wikilink:** `[[../02-Projects/teszt-eu]]` for internal references (folder-prefix mandatory)
- **Frontmatter:** every larger doc must have `name:`, `type:`, `created:`, `updated:` (see [[meta/Frontmatter-schema]])
- **Tags:** per [[meta/Tag-taxonomy]]
- **Callout:** `> [!info]`, `> [!warning]`, `> [!todo]`, `> [!success]`
- **Code/path:** in backticks

## Crystallization workflow (MANDATORY at session close)

**MANDATORY workflow** (after `/11.11-zar-session` the agent automatically):

1. **Summary + Learnings + Next** written into `08-Sessions/<slug>.md` based on chat history
2. **(optional, if `VAULT_CRYSTALLIZE_AUTO=1`)** `11.11crystallize <slug> --scorer claude-code --with-context` — automatic G-Eval scoring in shadow mode. If a pending request is created, spawn a general-purpose Agent with the G-Eval prompt + bullets + kodb_context; have it write response.json; then re-run `11.11crystallize` with the same flag to finalize.
3. **Routing — for every Learning bullet** apply the [[wiki/Crystallization-protocol#Routing decision tree|decision tree]] (architecture-level ADR / vault rule / wiki concept / glossary / infra / skill / user-pref / dashboard / project / task / ask). If a G-Eval output exists, use it as signal (high-confidence Pass → auto-prop candidate; Fail → discard; batch-preview → present to user)
4. **Batch preview** for the user — all proposals together, numbered:
   ```
   N learnings to propagate — I suggest these:
   [1] "<quote>" → <target> + preview
   [2] "<quote>" → <target> + preview
   ...
   OK like this? (yes / "1-3 OK, 4 rather X" / "skip 2" / "stop")
   ```
5. **After user confirmation** propagate the knowledge
6. **`## Propagation log`** section — timestamped, record what was propagated where

The session file remains a raw-like reference — the distillate goes into the indexed layers. This is Karpathy [[wiki/Karpathy-LLM-Wiki-pattern|crystallization]] at its minimum.

**Detailed rules:** [[wiki/Crystallization-protocol]]

### SV B-1 pipeline (LIVE since 2026-05-16)

| Layer | Command | Function |
|---|---|---|
| 0 migration | `migrate-hash-refactor-2026-05-19.py` | KO-DB fact-hash refactor: hash by `(s,p,o)` only, `fact_provenance` 1:N side-table (2026-05-19, 190 ms migration, unlocks Bayesian #21) |
| 1 ingest | `vault-ko-ingest --file <path>` | Triplet-extraction via subagent, 2-phase pending pattern |
| 2 score | `11.11crystallize <slug> --scorer claude-code --with-context` | G-Eval Learning-bullet scoring + KO-DB context-inject |
| 3 query | `vault-ko-query <pattern>` | Substring + filter + JSON + `--stats` + `--conflicts` + `--top-k` (cross-source rank) + `--semantic` (Memgraph bridge) |
| 3 report | `vault-ko-report [--last\|--session <slug>\|--days N]` | User-facing audit-log summary |
| 4 apply | `VAULT_CRYSTALLIZE_APPLY=1 VAULT_CRYSTALLIZE_REAL=1 11.11crystallize ... --apply` | REAL mode (sandbox-branch + 4-layer safety-gate + atomic-write + auto-commit) |
| 5 monitor | `vault-crystallize-monitor [--weeks N] [--json]` | Auto-rate / revert-rate / threshold-ramp recommendation |
| 5 conflicts | `vault-ko-conflicts-audit` | Weekly cross-source contradiction audit, predicate-aware heat-classifier |
| 5 revert | `crystallize-revert <bullet-hash>` | Auto-apply rollback (with audit-event) |

**Threshold-config:** `~/.vault-config/crystallize-threshold.txt` (hot-reloadable). Shadow=1.0 (default, no auto-prop), Conservative=0.95, Aggressive=0.85. Ramp protocol: [[wiki/crystallize-threshold-ramp]].

**Env-vars (opt-in):**
- `VAULT_CRYSTALLIZE_AUTO=1` — `11.11stop` runs the scoring automatically
- `VAULT_CRYSTALLIZE_SCORER=claude-code` — subagent-fanout scorer ($0 cost) vs `mock` (rule-based) vs `anthropic` (API-key required)
- `VAULT_CRYSTALLIZE_APPLY=1` — enables the `--apply` flag (Layer 1 ENV gate)
- `VAULT_CRYSTALLIZE_REAL=1` — REAL mode (write + commit). Default is skeleton-only ("would-have-applied" audit log)
- `VAULT_CRYSTALLIZE_ALLOW_MAIN=1` — `--apply` REAL run on main (DEFAULT: only on `crystallize-sandbox-*` branch). Dangerous.

## SV B-2 pipeline (LIVE since 2026-05-13, B-1↔B-2 bridge 2026-05-17)

| Layer | Command | Function |
|---|---|---|
| 1 embed | `vault-embed --backfill <dir>` | bge-m3 multilingual embed → Memgraph |
| 2 search | `vault-search "<query>" [--top-k N] [--json]` | semantic cosine-search (Memgraph in-Python) |
| 3 bridge | `vault-ko-query "<q>" --top-k N --semantic` | semantic → KO-DB top-K bridge (LIKE-fallback if Memgraph down) |

## Virtual-context (Letta/MemGPT) — PREVIEW (opt-in, since 2026-05-25 Day 0)

Alongside the classic aggressive ~17K-token pre-load there is an alternative: **core-memory + on-demand page-in**. Sprint plan: [[decisions/2026-05-25 vault-core-memory MemGPT integration sprint plan]]. Day 0 LANDED, integration between W1-5.

| Layer | Command | Function |
|---|---|---|
| 1 core | `vault-core-memory show` | ~2 KB always-loaded core (6 blocks: user_profile / active_project / open_tasks / glossary / infra_pins / recent_decisions) |
| 2 page-in | `vault-core-memory page-in "<query>" [--top-k N] [--max-chars N]` | Real Memgraph chunk-text retrieval, agent-paste-ready markdown |
| 3 simulate | `vault-core-memory simulate "<query>"` | Token-budget A/B (classic vs virtual) — does NOT mutate context |
| 4 update | `vault-core-memory update <block> "<text>"` | Atomic block mutation |

**Env-var (opt-in, default OFF in Week 1-4):**
- `VAULT_CORE_MEMORY_AUTO=1` — `11.11focus` + `/11.11-uj-session` auto-update + lean pre-loaded context (activates from W1-2)

**When to use page-in** (agent convention from W2):
- If the question CANNOT be answered from core-memory (query-overlap with the 6 blocks alone is not a hit) → `page-in "<query>"`
- The archival page-in result gives ~2-3 KB of chunk-text — instead of the classic 15-20K aggressive pre-load
- If >20 page-faults are needed within one session → flag that the core-memory is mis-sized (review required)

**Status:** Day 0 (2026-05-25) — `page-in` LANDED, integration not active (env-var OFF). See [[wiki/vault-core-memory-integration-roadmap]].

## Net-learning (since 2026-05-17)

- `vault-net-ingest --url <URL>` — firecrawl scrape → `10-raw/external/`
- `vault-net-ingest --repo owner/name [--paths "globs"]` — gh clone → key markdown → `10-raw/external/<owner>_<name>/`
- KO-DB extraction follows the subagent-fanout-pattern (2-phase pending) — triplets are uploaded after `claude_code_scorer_load_response`

## Per-chat session isolation (since 2026-05-17)

- Claude Code: `$CLAUDE_CODE_SESSION_ID` env-var (UUID)
- Codex companion: `$CODEX_COMPANION_SESSION_ID` (= Claude UUID)
- Codex standalone: `vault-detect-chat-id` auto-detect (from rollout filename)
- Gemini hook: `~/.gemini/.current-session-id` (written by SessionStart hook)
- Manual override: `CODEX_SESSION_ID` or `GEMINI_SESSION_ID` env-var
- The 6 `11.11*` scripts automatically extract the CHAT_ID from the chain, per-chat pointer file: `.active-session-$CHAT_ID`
- Matrix doc: [[wiki/cli-session-id-env-var-matrix]]

## What NOT to store here

- Secrets (passwords, tokens) — those stay in `.env` files. Exception: if the user explicitly requests it
- Generic info that can be extracted from git log or code
- Momentary session state that will be irrelevant in 1 day

## Tool-specific notes

- **Claude Code:** also sees a copy of this file as `~/.claude/CLAUDE.md`. The legacy auto-memory (`~/.claude/projects/-root/memory/`) also lives off this vault via symlinks
- **Codex CLI:** sees it as `~/.codex/AGENTS.md`. The `~/.codex/skills/` and `~/.claude/skills/` are updated together via shared symlinks
- **Gemini CLI:** sees it as `~/.gemini/GEMINI.md`. Same skill set, same vault

## Session orchestration (`11.11*` commands)

Detailed description: [[wiki/11.11-session-protokoll]]

> [!info] Slash vs shell
> The **shell CLI** (`/usr/local/bin/11.11*`) names are unchanged: `11.11start`, `11.11stop`, `11.11focus`, `11.11note`, `11.11ls`, `11.11`.
> The **Claude Code slash commands** received longer Hungarian names from 2026-05-17 (due to the popup UI — the VSCode extension only shows the command name, NOT the description):

| Slash command (Claude Code) | Shell CLI | Function |
|---|---|---|
| `/11.11-uj-session "project-task"` | `11.11start "..."` | New session file + focus. Without arg → interactive picker |
| `/11.11-lista` | `11.11ls` | Open sessions + last 5 closed |
| `/11.11-focus <slug>` | `11.11focus <slug>` | Switch focus to another open session. Without arg → interactive picker |
| `/11.11-jegyzet "..."` | `11.11note "..."` | Timestamped note into the **focused** session's `## Events` |
| `/11.11-jegyzet @<slug> "..."` | `11.11note @<slug> "..."` | Note targeted at a specific session (substring match) |
| `/11.11-zar-session [slug]` | `11.11stop [slug]` | Agent: Summary + Learnings + Next; Script: commit + push + close. Without arg + 2+ open → picker |
| `/11.11-egeszseg` | `11.11` | Health check: vault, symlinks, skills, services |

**Scripts:** `/usr/local/bin/11.11*` + `/11.11*` symlinks. **Agent env var:** `AGENT=claude|codex|gemini` goes into the commit message.

## Vault health

- **Live snapshot:** [[audits/System_Health]] — weekly cron `vault-cleanup` regenerates (Sunday 04:00)
- **Auto-save:** every 10 minutes cron `/usr/local/bin/vault-autosave` → commit + push to GitHub
- **Manual check:** `/11.11-egeszseg` (slash) or `11.11` (shell) — symlinks, skills, services

## How this file gets updated

If a new convention emerges, edit it directly — the change is live for all three agents immediately (symlink).

## Related

- [[README]] — human entry point
- [[meta/README]] — vault rules
- [[wiki/Karpathy-LLM-Wiki-pattern]] — the underlying pattern
- [[wiki/Johnny-Decimal-prefix]] — why the 00-, 01-, … prefix
- [[wiki/11.11-session-protokoll]] — session organization in depth
- [[../02-Projects/Index]] — project dashboard
