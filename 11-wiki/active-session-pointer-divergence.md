---
name: Active-session pointer divergence (MEGOLDVA)
type: wiki
tags: ["#type/wiki", "vault", "11.11", "session", "resolved"]
created: 2026-05-18
updated: 2026-05-18
status: resolved
---

# Active-session pointer divergence

> [!success] MEGOLDVA 2026-05-17
> `$CLAUDE_CODE_SESSION_ID`-szel per-chat `.active-session-$CHAT_ID` pointer-fájl az 5 `11.11*` script-ben. Backward-compat legacy fallback. 10+ incidens után.

## Eredeti probléma

Egyetlen `.active-session` pointer-fájl, ha párhuzamosan futott 2 chat (Claude + Codex pl.), a focus mindig az utolsó started session-re ugrott. `11.11note` rossz session-be írt.

## Megoldás

| Komponens | Mechanika |
|---|---|
| Claude Code | `$CLAUDE_CODE_SESSION_ID` env-var (UUID) |
| Codex companion | `$CODEX_COMPANION_SESSION_ID` (= Claude UUID) |
| Codex standalone | `vault-detect-chat-id` auto-detect (rollout-fájl) |
| Gemini hook | `~/.gemini/.current-session-id` (SessionStart hook) |
| Manual override | `CODEX_SESSION_ID` / `GEMINI_SESSION_ID` |

A 6 `11.11*` script automatikusan kiszedi a CHAT_ID-t a chain-ből, per-chat pointer-fájl: `.active-session-$CHAT_ID`.

## Kapcsolódó

- [[cli-session-id-env-var-matrix]] — matrix-doc
- [[bmad-cross-machine-artifact-verification]] — analóg multi-agent state-eltérés
- [[../05-Memory/Infrastructure]] — script-listák
