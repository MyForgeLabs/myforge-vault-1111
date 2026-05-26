---
name: Cross-CLI handoff pattern (vault-handoff)
type: wiki
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/wiki", "#concept/multi-agent", "b-6", "cross-cli", "handoff", "workflow"]
related:
  - "[[../07-Decisions/2026-05-25 vault-handoff cross-CLI bundle Day-0]]"
  - "[[cli-session-id-env-var-matrix]]"
  - "[[vault-core-memory-integration-roadmap]]"
---

# Cross-CLI handoff pattern (vault-handoff)

The vault runs on three agent CLIs (Claude Code, Codex, Gemini), all sharing `AGENTS.md` and the `11.11*` session protocol. `vault-handoff` is the primitive for moving a session from one CLI to another mid-work without losing context.

## When you need this

- Started a Claude session, hit the daily quota → continue on Codex
- Claude is busy with a long subagent fanout → kick off a parallel review thread on Gemini using the same session state
- Codex is doing the heavy code-write, you want a Gemini multimodal pass on a screenshot — pass it the live session
- End of day on the laptop with Claude → next morning on the workstation with Codex

## What's in the bundle

`vault-handoff export` produces a markdown (or JSON) block with **everything a fresh agent needs** to continue:

| Section | Source | Why |
|---|---|---|
| Session metadata | session-file frontmatter | which file to focus, which project, which agent started it, when |
| Core memory snapshot | `vault-core-memory show` | the 6-block "always-loaded" baseline (user / project / tasks / glossary / infra / decisions) |
| Recent notes | session's `## Events` section (last 5) | "what we were just talking about" |
| Open tasks | `04-Tasks/Backlog.md` filtered to `#project/<slug>` (top 5) | what's actually next |
| Recent decisions | `07-Decisions/*` files mentioning the project (last 3) | so receiving agent doesn't contradict yesterday |
| KO-DB top facts | `vault-ko-query <project-slug> --top-k 5` | structured ground-truth on the subject |

Total size: ~5-8 KB markdown. Same order of magnitude as a `vault-core-memory page-in` result. Designed to be paste-into-context for the receiving agent.

## The three subcommands

### `vault-handoff export`

```bash
# Export the FOCUSED session (uses CLAUDE_CODE_SESSION_ID / CODEX_* / GEMINI_*
# env-vars to find the per-chat .active-session-<chat-id> pointer)
AGENT=claude vault-handoff export > /tmp/handoff.md

# Or export a specific session by slug substring
AGENT=claude vault-handoff export --session superintelligent-vault

# JSON for programmatic consumers
AGENT=claude vault-handoff export --format json | jq '.session.project'
```

### `vault-handoff import`

```bash
# Day 0: print-only. The receiving agent pastes this into its context.
AGENT=codex vault-handoff import /tmp/handoff.md

# Week 1+ (not yet shipped): with --apply, creates the receiving session-file
# and sets the receiving CLI's .active-session-<chat-id> pointer.
# AGENT=codex vault-handoff import /tmp/handoff.md --apply
```

### `vault-handoff list`

```bash
# Show open sessions with CLI affinity + current focused
vault-handoff list

# JSON for piping
vault-handoff list --format json
```

Example output:

```
Current chat-id: 48bd22c4-b6ed-4bea-aa49-0c392d802289
Focused: 2026-05-25-superintelligent-vault

3 open session(s):
  [claude ] 2026-05-25-superintelligent-vault     project=superintelligent-vault ⭐
  [codex  ] 2026-05-25-kgc-marketing              project=kgc-marketing
  [gemini ] 2026-05-25-client-b-weboldal             project=client-b
```

## Three workflows

### Workflow A — Same machine, two CLIs

```bash
# Claude session paused
AGENT=claude vault-handoff export > /tmp/handoff.md

# Open Codex in another terminal on the same machine
AGENT=codex vault-handoff import /tmp/handoff.md
# Codex pastes the markdown into its context, picks up where Claude left off
```

Both CLIs share the same vault on disk, so the file-system-as-state convention means most of the work continues without explicit sync. The handoff bundle adds the agent's working memory on top.

### Workflow B — Cross-machine (laptop → workstation)

```bash
# On laptop, Claude
AGENT=claude vault-handoff export > /tmp/handoff.md
scp /tmp/handoff.md workstation:/tmp/handoff.md

# On workstation, after `git pull` brings the vault current
AGENT=claude vault-handoff import /tmp/handoff.md
```

The vault auto-save cron (every 10 min) handles the sync of the actual files; the handoff bundle handles the agent-context.

### Workflow C — Programmatic parallel review

```bash
# Claude is mid-work; spin up a Gemini multimodal pass on a side
AGENT=claude vault-handoff export --format json > /tmp/bundle.json

# Gemini agent script reads the JSON, builds a focused review prompt
AGENT=gemini gemini -p "$(cat /tmp/bundle.json | jq -r '.session.path' | xargs cat) Review this for screenshots needed."
```

## Day-0 limits (today, 2026-05-25)

- Receive-side is print-only. No auto-creation of the receiving session-file. The user / agent reads the bundle and does `11.11focus <slug>` (or opens a new session) on the receiving CLI manually.
- No cross-machine sync helpers built in (use `scp` / `git pull` / `vault-autosave` cron as today).
- No conflict resolution if the bundle slug already exists on the receiving side with newer content. W1 work.
- No bundle authentication/signing. Single-user vault = single-trust-domain.

## What's coming (W1-W3)

- W1: `import --apply` (writes session-file + sets pointer atomically on receive)
- W2: `vault-handoff sync` (auto-detect divergence between local + bundle slug, prompt for conflict resolution)
- W3: integration with the `11.11focus` hook — `11.11focus <bundle-file>` triggers auto-import

## Relationship to the full B-6 sprint

`vault-handoff` is the **passive handoff primitive**. The full B-6 sprint adds:

- **Active orchestration**: Planner agent kicks off N parallel workers
- **Worker spawning**: `11.11worker <task-id>` creates fresh CLI subprocess with isolated working-dir
- **Summary-only return**: workers report ≤500 tokens back to the Planner (not their full Learning-list)
- **Critic intercepts**: pre-flight check on every mutation tool-call
- **Summarizer convergence**: dedicated agent merges worker outputs into one Learning-set

Day-0 `vault-handoff` is reusable inside all of those — the Planner exports bundles to Worker contexts, Workers export summaries back, Critic reads a bundle to decide. So this primitive is the substrate of B-6, not a sibling.

## See also

- [[../07-Decisions/2026-05-25 vault-handoff cross-CLI bundle Day-0]] — the binding ADR
- [[cli-session-id-env-var-matrix]] — per-chat pointer system this builds on
- [[vault-core-memory-integration-roadmap]] — sister Day-0 Big Bet (core-memory is in every bundle)
- [[../07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]] — the full B-6 sprint plan
