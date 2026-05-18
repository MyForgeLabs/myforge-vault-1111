---
name: CLI session-ID env-var matrix (Claude Code / Codex / Gemini)
type: wiki
tags: ["#type/wiki", "agents", "11.11", "per-chat-isolation", "env-vars"]
created: 2026-05-17
updated: 2026-05-17
status: stable
---

# CLI session-ID env-var matrix

Per-chat pointer-isolation a `.active-session-$CHAT_ID` patternhez ([[claude-code-session-id-per-chat-isolation]]) — milyen env-var elérhető melyik CLI-ben, és mi a fallback ha nincs.

## A 4 CLI-helyzet

| CLI / mód | Env-var | UUID forrás | Megbízhatóság |
|---|---|---|---|
| **Claude Code (VSCode/desktop)** | `$CLAUDE_CODE_SESSION_ID` | UUID, set by Claude harness | ✅ 100% stabil |
| **Codex via Claude companion** (Claude Code subprocess) | `$CODEX_COMPANION_SESSION_ID` | Same UUID as Claude's | ✅ 100% stabil |
| **Codex standalone** (`codex` direkt invoke) | **NINCS env-var** | UUID printed to stdout + `~/.codex/sessions/YYYY/MM/DD/rollout-{ts}-{uuid}.jsonl` filename | 🟡 auto-detect lehetséges (mtime-based) |
| **Gemini standalone** | **NINCS env-var** (csak hook stdin-JSON-ban) | History dir checksum-named (`~/.gemini/history/<sha256>/`) | 🔴 nincs jó auto-detect, PPID fallback |
| **Gemini via hook** | `session_id` in hook stdin JSON | Gemini-internal UUID | ✅ csak hook scriptekből látható |

## Forrás-evidence

- **Claude Code:** session-bejelentkezésnél a Claude-bináris exportálja a env-vart. Validálva: 2026-05-17 obsidian-vault-pro session-ön ([[../08-Sessions/2026-05-17-obsidian-vault-pro]]).
- **Codex companion:** `$CODEX_COMPANION_SESSION_ID` az aktuális Claude session UUID-jét tükrözi (egyértelmű evidence: ugyanaz a UUID látszik `env | grep CODEX`-ben mint a `claude --debug`-ban).
- **Codex standalone:** `codex exec` indításkor stdout-ra ír `session id: 019e371e-a2ed-75e3-...`-t. Rollout-fájlnév formátum: `rollout-{ISO-ts}-{UUIDv7}.jsonl`. **NEM** állít be env-vart a subprocess számára.
- **Gemini standalone:** csak `--sandbox` flag van. Session-history `~/.gemini/history/<sha256(workdir)>/` checksum-named — workdir-alapú, NEM session-alapú. **Hook stdin** JSON tartalmazza a session-ID-t (`/root/.nvm/.../bundle/docs/hooks/reference.md`).

## A jelenleg implementált 11.11 chain

`/usr/local/bin/11.11{start,stop,focus,note,ls,list}` mind ugyanazt a chain-t használja:

```bash
CHAT_ID="${CLAUDE_CODE_SESSION_ID:-${CODEX_COMPANION_SESSION_ID:-}}"
if [[ -n "$CHAT_ID" ]]; then
  ACTIVE="$VAULT/.active-session-$CHAT_ID"
else
  ACTIVE="$VAULT/.active-session"   # legacy single-pointer fallback
fi
```

**Coverage:** Claude Code + Codex companion. Standalone Codex/Gemini fallback-ra esik.

## 2026-05-17 bővítés — manual export support + Codex auto-detect

A chain-t kibővítjük 2 további env-varral + 1 auto-detect helper-rel:

```bash
CHAT_ID="${CLAUDE_CODE_SESSION_ID:-\
${CODEX_COMPANION_SESSION_ID:-\
${CODEX_SESSION_ID:-\
${GEMINI_SESSION_ID:-\
$(vault-detect-chat-id 2>/dev/null)}}}}"
```

### Manual-export env-vars

A user (vagy egy wrapper script) explicite beállíthatja:

```bash
# Codex standalone — discoverable from latest rollout
export CODEX_SESSION_ID=$(ls -t ~/.codex/sessions/*/*/*/rollout-*.jsonl 2>/dev/null | head -1 | sed 's/.*rollout-[^-]*-[^-]*-[^-]*-[^-]*-[^-]*-\([a-f0-9-]*\)\.jsonl/\1/')

# Gemini standalone — workdir-checksum-based
export GEMINI_SESSION_ID=$(echo -n "$(pwd)" | sha256sum | cut -c1-32)
```

### Auto-detect helper

`/usr/local/bin/vault-detect-chat-id` — best-effort fallback ha nincs explicit env-var:

1. Megnézi a legutóbb módosított `~/.codex/sessions/*/*/*/rollout-*.jsonl` fájlt **mtime < 5min** (aktívan futó Codex)
2. Ha 1 ilyen találat → kiírja az UUID-t a fájlnévből
3. Ha 0 vagy 2+ találat → empty string (nem kockáztat ütközést)
4. Gemini-re NEM próbálkozik (checksum-workdir nem session-szintű izoláció)

### Mit jelent a 11.11 viselkedésre

| Helyzet | CHAT_ID forrás | Per-chat? |
|---|---|---|
| Claude Code (chat A) | `$CLAUDE_CODE_SESSION_ID` | ✅ |
| Claude Code (chat B, **másik** chat) | `$CLAUDE_CODE_SESSION_ID` (másik UUID) | ✅ |
| Codex Claude-companion (egy Claude chat-en belül) | `$CODEX_COMPANION_SESSION_ID` (= Claude UUID) | ✅ (Claude+Codex egy pointer) |
| Codex standalone, 1 példány fut | `$(vault-detect-chat-id)` rollout-fájlnévből | 🟡 (egyetlen Codex-szel jó, 2+ párhuzam → legacy fallback) |
| Codex standalone, 2+ párhuzamos | legacy `.active-session` | ❌ (régi ütközés) |
| Gemini standalone | legacy `.active-session` | ❌ |
| Gemini hook script | hook stdin `session_id` | ✅ (csak hook-ban, NEM 11.11 script-ből) |

## Per-CLI ajánlás

### Claude Code (primary)

Semmi teendő — `$CLAUDE_CODE_SESSION_ID` automatikus, a per-chat pointer él. Ez fedi le a current usage 99%-át.

### Codex Claude-companion-ben

Semmi teendő — `$CODEX_COMPANION_SESSION_ID` automatikus, ugyanaz a UUID mint a parent Claude chat-é. **Egy `.active-session-{uuid}` pointer mindkettő alatt.**

### Codex standalone

Két lehetőség:

**Egyszerű (1 Codex-példány):** semmi extra — a `vault-detect-chat-id` auto-detect-eli a futó rollout-fájlt.

**Robusztus (2+ párhuzamos Codex):**
```bash
# A Codex CLI elejére (vagy .bashrc-be ha mindig egy session):
export CODEX_SESSION_ID=$(...)   # lásd manual-export példa fent
```

### Gemini standalone

**Mostani állapot:** legacy `.active-session` single-pointer-re esik. Ha 2 párhuzamos Gemini fut, ütközés.

**Workaround manual export:**
```bash
export GEMINI_SESSION_ID="$(date +%s)-$$"   # PID + epoch → ugyanaz a Gemini-process alatt stabil, párhuzamosok különbözőek
```

A `$$` a shell PID-je → minden gemini-indítás külön ID-t kap. **Nem stabil session-resume között**, de a current-pointer szempontjából elég.

### Gemini via hook (long-term jobb)

A `~/.gemini/settings.json`-ban beállítható egy `SessionStart` hook ami exportálja a session_id-t egy fájlba:

```json
{
  "hooks": {
    "SessionStart": {
      "command": "jq -r .session_id > ~/.gemini/.current-session-id"
    }
  }
}
```

Aztán a `vault-detect-chat-id`-be hozzáadunk egy `cat ~/.gemini/.current-session-id` próbát. **Future work**, NEM most.

## Kapcsolódó

- [[claude-code-session-id-per-chat-isolation]] — eredeti pattern, Claude Code-only
- [[../08-Sessions/2026-05-17-obsidian-vault-pro]] — 10+ pointer-incidens végül megoldva
- `/usr/local/bin/11.11{start,stop,focus,note,ls,list}` — érintett scriptek
- `/usr/local/bin/vault-detect-chat-id` — új helper (2026-05-17)
