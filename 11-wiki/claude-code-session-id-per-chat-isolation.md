---
name: CLAUDE_CODE_SESSION_ID per-chat izoláció pattern
type: wiki
tags: ["#type/wiki", "claude-code", "infra", "env-vars", "concurrency", "patterns"]
created: 2026-05-17
updated: 2026-05-17
status: stable
source:
  - "[[08-Sessions/2026-05-17-obsidian-vault-pro]]"
  - "[[05-Memory/feedback_active_session_pointer_divergence]]"
---

# CLAUDE_CODE_SESSION_ID per-chat izoláció pattern

A Claude Code minden chat-folyamatában beállítja a `CLAUDE_CODE_SESSION_ID` env-vart (UUID formátum, pl. `e102ffd5-b466-412f-98e1-6c5167e36e89`). Plus a Codex companion-folyamat (`CODEX_COMPANION_SESSION_ID`) ugyanazt az UUID-t kapja egy chat-en belül. Ez a **kulcs minden chat-state izolációhoz**: lock-fájl, queue, audit-trail, pointer-fájl, temp-dir.

## A felfedezés (2026-05-17)

10+ incidens után, ahol a `/root/obsidian-vault/.active-session` pointer divergált párhuzamos Claude Code chat-folyamatok miatt (ugyanazon a gépen több ablak), észrevettem a `CLAUDE_CODE_SESSION_ID` env-vart. Ez stabil per-chat UUID, ami nem változik a chat élete alatt.

```bash
$ env | grep CLAUDE_CODE_SESSION_ID
CLAUDE_CODE_SESSION_ID=e102ffd5-b466-412f-98e1-6c5167e36e89
$ env | grep CODEX_COMPANION
CODEX_COMPANION_SESSION_ID=e102ffd5-b466-412f-98e1-6c5167e36e89
```

A két env-var ugyanazt az UUID-t adja, mert a Codex companion-folyamat a Claude Code-chat-en belül fut.

## A pattern

Bármely chat-specifikus állapot-fájlhoz:

```bash
# Per-chat resource (pointer/lock/queue/temp-dir):
CHAT_ID="${CLAUDE_CODE_SESSION_ID:-${CODEX_COMPANION_SESSION_ID:-}}"
if [[ -n "$CHAT_ID" ]]; then
  RESOURCE="$BASE/.resource-$CHAT_ID"
else
  RESOURCE="$BASE/.resource"  # backward-compat fallback
fi
```

Cleanup: a fájl üresedésekor (pl. session-close) `rm -f "$RESOURCE"` ha CHAT_ID volt (per-chat fájl), különben hagyjuk (legacy single-file mód).

## Use case-ek

1. **`.active-session` pointer** (2026-05-17 telepítve) — `11.11start/stop/focus/note/ls` mind per-chat pointer-fájlt használ. Két párhuzamos chat már nem ütközik. Részletek: [[../05-Memory/feedback_active_session_pointer_divergence]]
2. **Lock-fájl** kritikus szakaszhoz — egy script több chat-ből hívva: per-chat lock = paralelizálható, single lock = serial.
3. **Tmp-dir / scratchpad** — pl. `/tmp/vault-$CHAT_ID/` chat-isolation, így a párhuzamos extraction-feladat nem írja egymás fájlját.
4. **Audit-trail** — minden mutation event a chat-ID alapján sorba rendezhető, ami debug-oláskor segít: melyik chat-ben történt, mikor.

## Stand-alone tool gotcha

Más CLI-eszközök (`codex` CLI, `gemini` CLI a Claude Code-on kívül) saját env-vart használnak. **Nem feltérképezett még 2026-05-17-én.**

Workaround: az universale `CHAT_ID="${TOOL_A:-${TOOL_B:-${TOOL_C:-}}}"` várólista, vagy: `SESSION_FILE=<path>` env-var override (a user explicit megadja, ha tudja).

## Backward-compat

Mindig adj fallback-et a non-Claude-Code-runtime-ra:

```bash
# Default: legacy single-file mode
RESOURCE="$BASE/.resource"

# Override: per-chat (ha env-var van)
if [[ -n "$CHAT_ID" ]]; then
  RESOURCE="$BASE/.resource-$CHAT_ID"
fi
```

A régi `.active-session` fájl megmarad, csak a 11.11* scriptek a chat-ID-vel preferenciát adnak az új-style fájlnak. Régi script-ek (vagy nem-Claude-Code-runtime-ok) továbbra is a legacy fájllal dolgoznak.

## Cleanup-stratégia

Per-chat fájlok halmozódhatnak (sok chat × idő). Két opció:

1. **`11.11stop` end-cleanup** — ha üres, törli a saját pointer-fájlt (aktuálisan implementált).
2. **Weekly GC** — `vault-cleanup` script vagy külön cron: `find $BASE -maxdepth 1 -name '.resource-*' -empty -mtime +7 -delete` (még TODO).

## Kapcsolódó

- [[05-Memory/feedback_active_session_pointer_divergence]] — 10+ incidens history + megoldás
- [[11-wiki/claude-code-harness-blocks]] — más Claude Code-runtime patterns
- [[11-wiki/multi-layer-safety-gate]] — kritikus-feature-ekhez chat-isolation egy a 4 rétegből
