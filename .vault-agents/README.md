# `.vault-agents/` — Multi-agent orchestration (B-6 sprint)

4-elemű orchestrator-worker arch: Planner + isolated Worker + Critic safeguard + Summarizer convergence. Filesystem-as-State alapon, MCP-RPC kommunikációval (B-4 réteg).

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch.md]]
**Research:** [[../11-wiki/sv-03-multi-agent-orchestration.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]
**Depends:** B-4 (MCP-server, Critic-review-hook), B-1 (G-Eval threshold-routing)

## Tartalom

```text
.vault-agents/
├── README.md
├── prompts/
│   ├── orchestrator.md            Elem 1: Planner (Sonnet/Opus) — prompt-template only
│   ├── worker.md                  Elem 2: Subagent (Haiku default) — prompt-template
│   ├── worker-system.md           Elem 2: System-prompt appended by worker.sh
│   ├── critic.md                  Elem 3: Safeguard (Haiku, red-team minden 10.)
│   └── summarizer.md              Elem 4: Convergent synthesis (Sonnet)
└── scripts/
    ├── 11.11worker.sh             Worker spawning (Week 1 ÉLES, 2026-05-17)
    ├── 11.11critic.sh             Critic 4-layer safety-gate (Week 2 ÉLES, 2026-05-19)
    ├── 11.11summarizer.sh         Summarizer weekly + inputs (Week 2 ÉLES, 2026-05-19)
    └── event-log-monitor.py       Audit-JSONL tail-monitor
```

## Status — 2026-05-17 (Phase B-6, Week 1 ÉLES)

- [x] 4 prompt-template + 2 script-skeleton + README (Day 0, 2026-05-13)
- [x] **Week 1-α (2026-05-17):** `11.11worker.sh` real impl — claude-code subprocess spawn
  - Spawns `claude -p` non-interactively via `/root/.local/bin/claude`
  - Default toolset `Bash(date *),Bash(echo *)` — override via `WORKER_TOOLS=` (no bypassPermissions, by user policy)
  - Smoke: `prompts/smoketest-worker.md` → 6s roundtrip, exit 0 (see `prompts/smoketest-worker.output.md`)
- [x] **Week 1 (2026-05-17, est):** worker hardening — `worker-system.md` + JSONL audit + új CLI
  - **Új CLI:** `11.11worker --task "<desc>" [--skill X] [--max-tokens N] [...]` mellett a legacy prompt-file shape is megy
  - `--append-system-prompt` injektálja a `prompts/worker-system.md`-t ("egy feladat, egy output, NEM tool-loop")
  - **JSONL audit:** minden run → `.vault-agents/runs/<uuid>.jsonl` (input, output-path, wall-clock, exit, stdout-bytes, est-tokens, output-head)
  - **Monitor:** `event-log-monitor.py` real impl — tail-f a `runs/*.jsonl`-en, pretty-print + color, `--once`/`--since-min`/`--task-id` módok
  - **Symlink:** `/usr/local/bin/11.11worker` → script
  - **Smoke:** SV B-1 Week 1-4 50-szavas summary (skill bmad-distillator, max-tokens 200) → 33s wall-clock, exit 0, 52 magyar szó, audit JSONL OK
  - Audit-MD: [[../06-Audits/2026-05-17 B-6 Week 1 worker + smoke]]
- [ ] **Week 1-β:** B-4 dependency check — MCP-server működik? Critic-hook integration előfeltétele
- [ ] **Week 1-γ:** Orchestrator prompt v0.2 — első manuális orchestrated-task smoke (2-3 worker fan-out)
- [ ] **Week 2 Day 1-2:** Critic-agent hookolva minden MCP-mutation előtt (B-4 reuse)
- [ ] **Week 2 Day 3:** Red-team mode trigger (minden 10. mutation) + escalation-test
- [ ] **Week 2 Day 4-5:** Summarizer integráció — 3 worker-task batch + merged summary
- [ ] **Week 3 Day 1-3:** First production multi-agent task (e.g. full-stack feature kgc-berles-en)
- [ ] **Week 3 Day 4-5:** Acceptance gate — task-completion ~70%+, summary-quality user-rated >4/5

### Week 1-α smoketest record (2026-05-17 19:27 UTC)

```text
worker-1 → claude -p (text output, allowed: Bash(date *),Bash(echo *))
start: 2026-05-17T19:27:21Z   end: 2026-05-17T19:27:27Z   (6s)   exit: 0
stdout: date: 2026-05-17 | 2+2 = 4 | worker-status: ok
```

### Week 1 smoketest record (2026-05-17 22:49 UTC) — B-1 distill

```text
worker-2 → claude -p + --append-system-prompt worker-system.md
task: "50-szavas magyar summary SV B-1 Week 1-4-ről"
skill: bmad-distillator   max-tokens: 200   timeout: 180s
start: 2026-05-17T22:49:09Z   end: 2026-05-17T22:49:42Z   (33s)   exit: 0
stdout-bytes: 375   est-tokens: 65   ~52 magyar szó (target 45-55) PASS
audit:  .vault-agents/runs/a7fedf08-eb67-462e-a7e7-95715ed1e89d.jsonl
```

Worker layer + audit + monitor unblocked. Next: orchestrator → worker fan-out (Week 1-γ) + Critic-hook (Week 2).

## Várt impact (Phase A+ SV-3)

| Metrika | Most | B-6 után |
|---|---|---|
| Complex task completion (e.g. e2e feature) | 1 agent, ~5-10 session-back-and-forth | 4 agent parallel, ~1 session |
| Token cost per task | ~50K-100K | **~750K-1.5M (15× cost)** — Anthropic mérés |
| Quality | baseline | **+90%** (Critic-review elkapja a hibás mutációkat) |
| User-time per task | 1-2 óra | 15-30 perc |

**Trade-off:** 15× token-cost cserébe a +90% minőségért. Cost-tudatosan kapcsolható ki ha drága (`MULTI_AGENT_DISABLED=1`).

## Failure-mode protections (Phase A+ SV-3 Q1)

- **Context-bleed** → strict friss session per-worker (`/tmp/vault-workers/<task-id>/<worker>/`)
- **Race-condition** → 1 worker per file (file-lock)
- **Cost-runaway** → Orchestrator estimated_total_duration validation pre-spawn
- **Worker-stuck** → 15 perc timeout abort, alternative-skill retry

## Backout

```bash
export MULTI_AGENT_DISABLED=1
# Orchestrated-task requests fallback to single-agent klasszikus 11.11start workflow
```

## Kapcsolódó

- B-4 (MCP-server + Critic-hook): [[../.vault-tools/README.md]]
- B-1 (G-Eval threshold-routing): [[../.vault-ko/README.md]]
- B-8 (RSI — Prompt Evolution mutates these prompts): jövőbeli safety-gated
