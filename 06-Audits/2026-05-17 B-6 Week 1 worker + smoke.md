---
name: 2026-05-17 B-6 Week 1 worker + smoke
type: audit
created: 2026-05-17
updated: 2026-05-19
tags: ["#type/audit"]
tag_backfill: 2026-05-19
---
# 2026-05-17 B-6 Week 1 — `11.11worker.sh` real impl + első orchestrated-task smoke

**Sprint:** SV B-6 (Multi-Agent Orchestration)
**Phase:** Week 1 (real worker spawn)
**ADR:** [[../07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]]
**Parent project:** [[../02-Projects/superintelligent-vault]]
**Status:** ÉLES — worker layer megy, audit JSONL ír, monitor tail-f megy. Critic-hook + red-team Week 2.

## 1. Mit landoltunk

| Komponens | Path | Funkció |
|---|---|---|
| Worker spawn-script | `.vault-agents/scripts/11.11worker.sh` | Real impl claude-code subprocess + JSONL audit + `--append-system-prompt` |
| Worker system prompt | `.vault-agents/prompts/worker-system.md` | v0.1 — "egy feladat, egy output, NEM tool-loop" princípium |
| Event-log monitor | `.vault-agents/scripts/event-log-monitor.py` | Real impl — tail-f a `.vault-agents/runs/*.jsonl`-en, pretty-print, color, `--since-min`/`--once`/`--task-id` módok |
| Symlink | `/usr/local/bin/11.11worker` | → `11.11worker.sh` (PATH-on elérhető) |

## 2. Architektúra — claude-code subprocess (NEM API)

A worker **NEM** hív real Anthropic API-t. A spawn-pattern:

```
claude -p "<user-task>" \
  --append-system-prompt "<worker-system-prompt-tartalma>" \
  --output-format text \
  --allowedTools "Bash(date *),Bash(echo *)"   # override-olható WORKER_TOOLS env-vel
```

**Miért subprocess + nem API:**

1. **Költség:** subscription-fed (Anthropic Pro), per-run cost = $0 a user oldalán
2. **Stack-konzisztencia:** ugyanaz a claude-code binary fut workerként mint a parent agent → ugyanaz a tool-suite, skill-suite, hook-rendszer
3. **Permissions:** default toolset `Bash(date *),Bash(echo *)` — text-only smoke. Override `WORKER_TOOLS=` env-vel call-site-en (NEM globális bypassPermissions, user-policy szerint)
4. **Audit:** parent script (`11.11worker.sh`) wraps a `claude -p` hívást → input/output/wall-clock/exit/stdout-bytes/est-tokens egy JSONL-rekordba megy a `.vault-agents/runs/<uuid>.jsonl`-be

**Két CLI-shape, mindkettő supported:**

```bash
# A) Inline (új, Week 1)
11.11worker --task "<description>" [--skill <name>] [--max-tokens N] \
            [--worker-id N] [--output <path>] [--timeout <sec>]

# B) Prompt-file (legacy Week 1-α)
11.11worker <prompt-file.md> [--worker-id N] [--output <path>] [--timeout <sec>]
```

A `--skill` és `--max-tokens` flag-ek a user-message ELÉ szúrnak preambulumot (a worker invokálja a Skill tool-t, és advisory cap-et követ). NEM hard-cap — claude-code `-p` CLI-nek nincs hard token-output-limit flag-je.

## 3. JSONL audit-séma

Minden worker-run egy fájl: `.vault-agents/runs/<uuid>.jsonl` (1 row default, append-only — Week 2 bővülhet multi-event-re).

```json
{
  "event": "worker_run",
  "run_uuid": "a7fedf08-eb67-462e-a7e7-95715ed1e89d",
  "worker_id": "2",
  "agent_tag": "worker-2",
  "prompt_source": "(inline --task)",
  "skill": "bmad-distillator",
  "max_tokens_advisory": 200,
  "start_ts": "2026-05-17T22:49:09Z",
  "end_ts":   "2026-05-17T22:49:42Z",
  "wall_clock_sec": 33,
  "exit_code": 0,
  "stdout_bytes": 375,
  "est_tokens": 65,
  "output_path": "/tmp/b1-smoke.output.md",
  "output_head_400": "..."
}
```

**Token-estimate:** `(words * 13 + 9) / 10` (kb. 1.3 token/word). Audit-célra elég, NEM billing-grade.

## 4. Első smoke-task — input + output

**Task:** "50-szavas magyar summary az SV B-1 sprint Week 1-4 milestone-ról."

**Hívás:**
```bash
11.11worker \
  --task "$(cat /tmp/b1-smoke-task.md)" \
  --skill bmad-distillator \
  --max-tokens 200 \
  --worker-id 2 \
  --output /tmp/b1-smoke.output.md \
  --timeout 180
```

**Worker output (stdout, teljes szöveg):**

> Az SV B-1 sprint Week 1–4 alatt épült ki a vault crystallization automatizáció: Day 0 SQLite skeleton, Week 1 G-Eval prompt v0.2 96.7%-os verdict-agreement-tel, Week 2 ingest/query/report tooling + `/11.11stop` hook, Week 3–4 threshold-ramp 0.95-re, 4-rétegű `--apply` safety-gate, 99.4%-os wiki backfill (13675 fact, $0 cost), és Memgraph cross-source match POC.

**Mérőszámok:**

| Metrika | Érték |
|---|---|
| Wall-clock | **33 sec** |
| Exit-code | 0 |
| stdout-bytes | 375 B |
| est-tokens (output) | ~65 |
| Tényleges szószám (magyar) | ~52 szó (target: 45-55) PASS |
| skill invokáció | `bmad-distillator` advisory (worker inline-olta, nem futtatott skill-tool-t — read-only kontextus) |
| run-uuid | `a7fedf08-eb67-462e-a7e7-95715ed1e89d` |
| Audit JSONL | `.vault-agents/runs/a7fedf08-eb67-462e-a7e7-95715ed1e89d.jsonl` |

A summary szakmailag pontos: 4 mérföldkő mind említve (G-Eval, ingest/query/report, threshold-ramp + safety-gate, backfill), a számok stimmelnek (96.7% / 0.95 / 13675 fact / 99.4%), token-budget tartva.

## 5. Monitor sanity-check

```bash
$ event-log-monitor.py --once
2026-05-17T22:49:09Z w2 a7fedf08 worker_run skill=bmad-distillator exit=0 33s 375B/~65tok
  → # Worker output | - worker-id: 2 | - run-uuid: a7fedf08-eb67... | - skill: bmad-distillator | ...
```

Pretty-print működik: timestamp + worker-id + uuid-prefix + event + skill + exit + wall-clock + output-bytes/tokens, plus 1-line output-head preview. TTY-detektálással szín, non-TTY-ban plain.

Élő `tail -f`: `event-log-monitor.py` (Ctrl+C stop). Backfill: `--since-min 60`. Orchestrator-mód: `--task-id <id>` (Week 2-3-ban lesz aktív, amikor `/tmp/vault-workers/` populálódik).

## 6. Failure-mode-ok ÉS amik még nem védettek

| Failure-mode | Védve? | Megjegyzés |
|---|---|---|
| Timeout | ✓ | `timeout --preserve-status` default 300s, exit-code 124 |
| Empty prompt | ✓ | preflight check |
| Missing system-prompt | ✓ | preflight check |
| claude-binary missing | ✓ | preflight check |
| Tool-bypass via env | ✓ (user-policy) | `WORKER_TOOLS=` override-olható, de NINCS `--dangerously-skip-permissions` a script-ben |
| Context-bleed (két worker ugyanazt a fájlt írja) | ✗ | Week 3 file-lock kell |
| Cost-runaway | ✗ | `--max-tokens` advisory-only, nincs hard cap |
| Worker-stuck silent (no output, no exit) | részben | timeout véd, de "stuck producing slow output" nem detektált |

## 7. Week 2 follow-up

- **Critic-agent hook** minden MCP-mutation előtt (B-4 reuse). Pattern: 2-phase pending file (B-1 crystallize mintára), Critic spawn-ol egy second-worker-t a `prompts/critic.md`-vel
- **Red-team mode trigger** minden 10. mutation-re (orchestrator counter-rel) — `prompts/critic.md` already has red-team szakasz
- **JSONL audit bővítés**: `event` field-érték nem csak `worker_run` lesz hanem `worker_spawn`, `tool_call`, `mutation_attempt`, `critic_verdict`, `worker_complete` — multi-event/run
- **MCP-config injection** workerbe (`--mcp-config <file>`) hogy a vault MCP-tools elérhetők legyenek a worker számára scoped módon
- **Skill-trigger real invocation** — most a worker advisory-ként látja a `--skill X`-et, de nem mindig hív Skill tool-t. Week 2: stronger system-prompt hook hogy hívja kötelezően

## 8. Files érintve

```
NEW   .vault-agents/prompts/worker-system.md
EDIT  .vault-agents/scripts/11.11worker.sh         (JSONL audit + új CLI flags + --append-system-prompt)
EDIT  .vault-agents/scripts/event-log-monitor.py   (real tail-f + pretty-print + mode-A/B)
NEW   /usr/local/bin/11.11worker                   (symlink)
NEW   .vault-agents/runs/<uuid>.jsonl              (audit, runtime-generated)
NEW   06-Audits/2026-05-17 B-6 Week 1 worker + smoke.md  (this file)
```

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — SV roadmap
- [[../07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]] — parent ADR
- [[../.vault-agents/README]] — module README
- [[../11-wiki/claude-code-subagent-fanout]] — B-1 pattern, ami inspirálta a worker-spawn-t
- [[../11-wiki/multi-layer-safety-gate]] — Week 2 Critic-hook itt landol
