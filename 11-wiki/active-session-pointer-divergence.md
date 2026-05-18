---
name: Active-session pointer divergence (MEGOLDVA)
type: wiki
tags: ["#type/wiki", "vault", "11.11", "session", "multi-agent", "resolved"]
created: 2026-05-18
updated: 2026-05-18
status: resolved
---

# Active-session pointer divergence

## TL;DR

**MEGOLDVA 2026-05-17** — a 11.11 session-tracker eredetileg egyetlen `.active-session` pointer-fájllal dolgozott a vault gyökerében. Ez **multi-chat / multi-agent szcenárióban** (Claude + Codex párhuzamosan, vagy 2 Claude tab) átírta egymást: a `11.11note` rossz session-be került, az `11.11focus` a legutoljára indított session-re ugrott. 10+ incidens után a megoldás: **per-chat pointer-fájlok** `$CHAT_ID` env-var alapján (`.active-session-$CHAT_ID`). Backward-compat legacy fallback megtartva.

## Eredeti probléma

```
$ 11.11start "kgc-marketing"     # Claude tab A
$ # másik tabban:
$ 11.11start "robbantott-bra"    # Claude tab B
$ # tab A:
$ 11.11note "ezt a kgc-marketing-be akartam"
# → de a .active-session már a robbantott-bra-re mutat
# → note rossz session-be került
```

**Gyökér-ok:** single-pointer-pattern + shared filesystem state → race condition két párhuzamos session között. Ez nem csak két agent között lépett fel, hanem **ugyanazon agent két tab-ja** között is.

### Incidens-log (10+ eset 2026-03-tól 2026-05-16-ig)

- 2026-03-15: első észlelt eset (Codex+Claude párhuzamos session)
- 2026-04-02: kgc-weboldal session-be a robbantott-kereso note-ja
- 2026-04-20: 3× érintett, debugging
- 2026-05-10: workaround `11.11focus` manual minden note előtt (fáradtság)
- 2026-05-14: kgc-marketing kontamináció
- 2026-05-15: két browser-window egyidejűleg
- 2026-05-16: utolsó incidens; root-cause-analysis indul

## Megoldás

### Per-chat CHAT_ID detection

| Komponens | Mechanika | Forrás |
|---|---|---|
| Claude Code | `$CLAUDE_CODE_SESSION_ID` env-var (UUID) | Harness által set |
| Codex companion | `$CODEX_COMPANION_SESSION_ID` (= Claude UUID) | Cross-set by Claude |
| Codex standalone | `vault-detect-chat-id` auto-detect | Rollout-fájlnévből |
| Gemini hook | `~/.gemini/.current-session-id` | SessionStart hook |
| Manual override | `CODEX_SESSION_ID` / `GEMINI_SESSION_ID` | User export |

### Pointer-fájl séma

- Új: `.active-session-$CHAT_ID` (per-chat)
- Legacy: `.active-session` (backward-compat fallback)
- Fallback rend: env-var → `.active-session-$CHAT_ID` → `.active-session` (legacy)

### Patched scriptek (6 file)

- `11.11start`, `11.11stop`, `11.11focus`, `11.11note`, `11.11ls`, `11.11`
- Mindegyik a chain elején kiszedi a `CHAT_ID`-t és per-chat pointer-fájlt használ
- Idempotent — legacy környezetben (no env-var) ugyanúgy működik

## Mintázat (reusable)

1. **Soha ne shared-file pointer multi-agent / multi-tab kontextusban** — kvázi-mindig race condition lesz
2. **Env-var-alapú namespace** — `$CHAT_ID`, `$SESSION_ID`, `$INSTANCE_ID` — a process tudja önmagát identifikálni
3. **Cascading fallback** — env-var > new-format > legacy-format → 0-downtime migration
4. **Backward-compat min. 1 release** — a legacy `.active-session` még olvasott, de új write-ok per-chat formátumban
5. **Detection-script külön** — `vault-detect-chat-id` egyhelyen, ne másold a logikát 6 scriptbe
6. **Audit-event a chain-elején** — debug-céllal log-old, melyik CHAT_ID-t használja a script

## Anti-pattern

- **`$$` (PID)-alapú pointer** — child-process exec eltérő PID-t kap → ugyanaz a quirk
- **CWD-alapú detection** — sok agent ugyanabból a CWD-ből indul
- **`lockf`/`flock` single-pointer-en** — szerializál, NEM oldja meg a divergence-et
- **TTY-name detection** — VSCode-extensionben nincs TTY

## Buktatók

- `set -e` + `vault-detect-chat-id` exit-1 collision a parameter-expansion-ben (2026-05-18 patch, ld. MEMORY)
- Codex rollout-fájl néha késve íródik (~50ms) → detection retry-with-backoff kell
- Gemini hook első session-indításkor még nincs `.current-session-id` → ENV-fallback rendelt

## Kapcsolódó

- [[cli-session-id-env-var-matrix]] — matrix-doc (kanonikus session-id konvenciók)
- [[bmad-cross-machine-artifact-verification]] — analóg multi-agent state-eltérés
- [[../05-Memory/Infrastructure]] — script-listák
- [[11.11-session-protokoll]] — overall session-protokoll
- [[vault-corruption-detection-pattern]] — szélesebb integritás-pattern
