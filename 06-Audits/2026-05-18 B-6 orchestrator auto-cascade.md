---
name: B-6 orchestrator auto-cascade
type: audit
created: 2026-05-19T04:40:00Z
updated: 2026-05-19
tags: ["#type/audit", "#project/superintelligent-vault"]
tag_backfill: 2026-05-19
---
# B-6 follow-up — `11.11orchestrator` auto-cascade ÉLES (2026-05-19)

> [!success] Production-ready
> A Worker → Critic → (Publish | Reject | Batch-preview) → optional Summarizer auto-cascade ÉLES, 4 routing-ág + ENV-flag verified, end-to-end smoke 45s.

## Artefakt

- **Script:** `/root/obsidian-vault/.vault-agents/scripts/11.11orchestrator.sh` — **282 sor** bash
- **Symlink:** `/usr/local/bin/11.11orchestrator → .../11.11orchestrator.sh`
- **Audit-fájl:** `.vault-agents/runs/orchestrator-<uuid>.jsonl` (cascade-level summary row)
- **Batch-preview JSONL:** `.vault-agents/runs/preview-<uuid>.jsonl` (csak verdict=batch_preview esetén)

## Pipeline architektúra

```
--task "..." ──► [Stage 1: Worker]  ───────────────────────────────┐
                  └─► worker-output.md                              │
                                                                    ▼
                  [Stage 2: Critic] ◄─────────── worker-output.md
                  exit-code routing:
                    0 → approve    ─► [Stage 3a: Publish]    exit 0
                    2 → reject     ─► [Stage 3b: Abort]      exit 2
                    3 → batch_prev ─► [Stage 3c: Preview]    exit 3
                  124 → timeout                              exit 124

                  [Stage 4: Summarizer] (opcionális, csak approve esetén)
                  --with-summarizer flag → 11.11summarizer --inputs <worker-out>
```

## Smoke-test eredmények

| Test | Routing path | Exit | Wall | Status |
|---|---|---|---|---|
| 1 | `ORCHESTRATOR_DISABLED=1` short-circuit | 0 | <1s | PASS |
| 2 | Reject (forbidden target = `.claude/CLAUDE.md`) | 2 | 7s | PASS |
| 3 | Approve + publish (mock critic) | 0 | 6s | PASS |
| 4 | Batch-preview (shim critic exit 3) | 3 | 9s | PASS |
| 5 | **Full cascade** Worker → Critic → Summarizer | 0 | **45s** | PASS (<60s target) |

## Exit-code mátrix

| Verdict | Critic-RC | Orchestrator-RC | Side-effect |
|---|---|---|---|
| approve | 0 | 0 | `cp worker-out → publish-path` (vagy stdout) |
| reject | 2 | 2 | log + abort, NINCS publish |
| batch_preview | 3 | 3 | `preview-<uuid>.jsonl` írás, user-confirm step kell |
| timeout | 124 | 124 | abort |
| worker-fail | — | 2 | critic NEM fut, abort |

## ENV-flag verifikáció

```bash
ORCHESTRATOR_DISABLED=1 11.11orchestrator --task "anything"
# → no-op exit 0, audit row {"status":"disabled"} írva
```

VERIFIED — 0 worker-spawn, 0 critic-spawn, csak audit-row.

## Audit-record shape

A cascade audit row tartalmazza:
- `run_uuid`, `task`, `skill` (opcionális)
- `worker_output`, `worker_exit_code`
- `critic_output`, `critic_exit_code`, `critic_verdict`
- `publish_path`, `final_status`, `final_exit_code`
- `summarizer_ran`, `summarizer_output`, `summarizer_exit_code`
- `red_team`, `mock_critic`, `start_ts`, `end_ts`, `wall_clock_sec`

## CLI-flag-ek

| Flag | Funkció |
|---|---|
| `--task "..."` | Worker-prompt (REQUIRED) |
| `--skill <name>` | Skill-invocation hint a workernek (pl. `bmad-distillator`) |
| `--publish <path>` | Approve esetén ide kerül a worker-output (default: stdout) |
| `--targets "<csv>"` | Critic Layer-2 forbidden-target check input |
| `--with-summarizer` | Approve után futtat 11.11summarizer-t convergent-synthesis-ért |
| `--red-team` | Critic red-team mód |
| `--mock-critic` | Critic LLM-call skip (csak Layer 1-3 rule-based verdict) |
| `--worker-timeout <sec>` | Default 300 |
| `--critic-timeout <sec>` | Default 120 |

## Mérnöki őszinte — production-ready?

**IGEN** a 4-ágú routing + ENV-flag + audit-JSONL + end-to-end smoke alapján. **Hiányok / limitációk:**

1. **Batch-preview confirmation flow külön step** — orchestrator csak JSONL-rowot ír; a user-megerősítés + post-publish jelenleg manuális (`cat preview-*.jsonl` + `cp worker-out → publish-path`). Egy `11.11orchestrator --confirm <preview-uuid>` follow-up flag triviális hozzáadás.
2. **Worker eszközkészlet kicsi** — `WORKER_TOOLS` default `Bash(date *),Bash(echo *)`, file-write feladatokhoz ezt env-vel kell tágítani. Tudatos default-deny, de orchestrator-flag-gel finomhangolható lenne.
3. **Summarizer csak approve után** fut — reject/batch_preview után NEM aggregálódik, és a `--with-summarizer` csak az adott worker-output-on dolgozik, NEM multi-cascade-en (heti aggregate továbbra is külön `11.11summarizer --weekly` cron).
4. **NINCS retry-on-transient** — egyetlen worker-timeout = teljes cascade-failure. Egy `--retry N` flag B-6 W3-be tehetné.
5. **Konkurens cascade-ek** — audit-JSONL-ek külön UUID-okkal nem ütköznek, de SOHA nem teszteltük párhuzamosan; lock-fájl-ot B-7-be javaslom.

## Kapcsolódó

- ADR: [[07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]]
- Worker: `.vault-agents/scripts/11.11worker.sh`
- Critic: `.vault-agents/scripts/11.11critic.sh` (4-layer safety-gate)
- Summarizer: `.vault-agents/scripts/11.11summarizer.sh`
- Prev audit: `2026-05-18 B-6 critic+summarizer activation`
