---
name: Multi-agent pointer ownership lock pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/orchestration", "#topic/concurrency", "sv-3", "multi-agent"]
source: vault-meta NotebookLM Q4#5 / Q5#3 (2026-05-18, 63-source synthesis)
status: evergreen
project: [[../02-Projects/superintelligent-vault]]
related: [[claude-code-session-id-per-chat-isolation]], [[cli-session-id-env-var-matrix]], [[sv-03-multi-agent-orchestration]]
---

# Multi-agent pointer ownership lock pattern

> **Tl;dr:** Egy globális mutable pointer (pl. `.active-session`, `current.txt`) párhuzamosan futó agent-folyamatok között **versenyhelyzetet (race-condition)** okoz. A klasszikus "egy-pointer, egy-agent" feltételezés multi-agent fanout-ban összeomlik. A megoldás **NEM** retry-loop, hanem **per-agent ownership** (env-var, file-lock, vagy mindkettő).

## Mi a probléma

A vault-meta NotebookLM cross-projekt synthesis (63 session, 2026-05-18) **13+ dokumentált incidenst** számolt össze, ahol a `~/.claude/projects/<X>/.active-session` pointer-fájl divergált — egy háttér-agent felülírta a fókusz-pointert, és a következő `11.11note` parancs **másik projekt session-fájljába írt**.

Ez **nem konfigurációs bug** — ez **architektúrális hiányosság**:

1. A globális pointer mutable shared state
2. Subagent-fanout (8-174 párhuzamos) ezt a state-et **konkurrensen** írja
3. Nincs locking, nincs ownership-verifikáció
4. Idempotency hiányzik (a "felülírás" silent, NEM merge)

## Miért NEM elég a session-id env-var

A [[claude-code-session-id-per-chat-isolation|2026-05-17 fix]] (`$CLAUDE_CODE_SESSION_ID` UUID a 5 `11.11*` scriptben) **csökkenti, de NEM oldja meg** a problémát:

- ✅ Más-más session-ID-jú párhuzamos Claude Code chat **NEM** írja egymás `.active-session`-jét
- ❌ DE: ha **ugyanaz** a chat 8 subagent-fanout-ot indít, mind ugyanazt a `CLAUDE_CODE_SESSION_ID`-t örökli → race-condition vissza
- ❌ Codex/Gemini cross-CLI agent shared `.active-session` → még mindig sebezhető

## A megoldás: per-agent ownership lock

### Réteg 1 — Env-var-driven session-targeting

```bash
# 11.11note implementation skeleton
SESSION_FILE="${SESSION_FILE:-$(cat ~/.claude/projects/$PROJ/.active-session)}"
# az SESSION_FILE explicit env-var fixed targeting, MINDIG felülírja a pointer-fájlt
echo "$(date -Iseconds) | $NOTE" >> "$SESSION_FILE"
```

**Előny:** Az agent-spawn-er pontosan tudja, melyik session-fájlba kell írni.
**Hátrány:** Minden subagent-call-nál átadni kell.

### Réteg 2 — Advisory file-lock (`flock`)

```bash
# 11.11focus implementation
flock -x ~/.claude/projects/$PROJ/.active-session.lock -c "echo $SLUG > ~/.claude/projects/$PROJ/.active-session"
```

**Előny:** OS-szintű serialization, atomi `read-modify-write`.
**Hátrány:** Stuck lock (crashed agent) → manuál cleanup.

### Réteg 3 — Per-agent UUID-prefixed pointer

```
~/.claude/projects/<proj>/.active-session              # legacy (backward-compat)
~/.claude/projects/<proj>/.active-session-<UUID>       # per-Claude-chat
~/.claude/projects/<proj>/.active-session-<UUID>-<N>   # per-subagent (UUID + worker-N)
```

A `11.11note` first tries the UUID-N pointer, falls back to UUID, then legacy.

## Reference implementations

- **`rohitg00/agentmemory`** (NotebookLM forrás) — MCP-alapú izolált memory-architektúra; minden agent-instance saját namespace + lock-controlled write
- **`MemGPT`** (Berkeley) — virtual context-management event-system; minden agent-instance saját episodic-memory-namespace
- **`GenericAgent`** L0-L4 architektúra — per-agent context-shard, no shared mutable pointer

## Miért fontos a Superintelligent Vault-nak

A B-3 (Multi-agent Orchestration) sprint **8-174 párhuzamos subagent-fanout-ot** futtat (vault-skill-distill, ko-extract, gepa-mutate, eval-l2-nli-judge). Ezek **mind írják** valamilyen formában a vault-state-et. A jelenlegi 13+ pointer-divergencia-incidens csak a `.active-session`-re vonatkozott; **számtalan más shared pointer is létezik** (`/root/.vault-config/env-defaults.md`, `~/.notebooklm-data/conversations/`, `/var/lib/vault-ko-db/audit.log`).

Az ownership-lock-pattern **architecturally muszáj** a B-3 Week 2-3 sprintben, különben minden új subagent-fanout-feladat új race-condition surface-area.

## Anti-patterns (mit NE csinálj)

1. **Retry-loop pointer-conflict-detektálásra** — silent overwrite-ot NEM lehet detektálni, mert nincs version-stamp
2. **Sleep-loop a write előtt** — szerencse, nem szinkronizáció
3. **Global mutex egy chat-en belül** — a parent-agent NEM tudja, hány subagent-spawn lesz dinamikusan
4. **Ignorálás "csak ritkán fordul elő" alapon** — 13+ dokumentált incidens NEM ritka

## Cross-projekt evidence

A vault-meta NB Q5 idézte:
- **6 különböző session** említi a `.active-session` divergencia-incidenst (kgc-kivetit, foxxi, kinda-project, boulium, obsidian-vault, sv-week1)
- **Mind ugyanaz a root-cause:** globális mutable pointer + párhuzamos write
- **Mind ugyanaz a band-aid fix:** `11.11focus <slug>` explicit átirányítás — DE ez **NEM gyökér-megoldás**, csak fókusz-recover

## Implementation roadmap

| Fázis | Munka | Eredmény |
|-------|-------|----------|
| 1 | `SESSION_FILE=` env-var support a 5 `11.11*` scriptben | Explicit targeting opt-in |
| 2 | `flock` wrapper a `.active-session` read/write-on | Advisory locking |
| 3 | Per-subagent UUID-N namespace pattern | Full per-agent isolation |
| 4 | Audit-log minden pointer-write-on (timestamp + agent-UUID) | Incident-forensics |

## Mikor érvényes ez a pattern

- ✅ Multi-agent system globális mutable shared state-et tart fenn
- ✅ Subagent-fanout (>2 párhuzamos) jelen van
- ✅ Cross-CLI (Claude / Codex / Gemini) ugyanahhoz a state-hez fér
- ❌ Single-agent CLI session-en belül **nem szükséges**

## Kapcsolódó

- [[claude-code-session-id-per-chat-isolation]] — 2026-05-17 első-rétegű fix (csak env-var)
- [[cli-session-id-env-var-matrix]] — Claude / Codex / Gemini session-ID source-of-truth
- [[sv-03-multi-agent-orchestration]] — B-3 sprint host
- [[sandbox-branch-mutation-isolation]] — analogue pattern git-szinten
- [[../06-Audits/2026-05-18 vault-meta NB cross-projekt Q4-Q5]] — forrás-audit
