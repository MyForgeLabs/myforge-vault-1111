---
name: VSCode Claude Code extension — slash-command naming UX
type: wiki
tags: ["#type/wiki", "ux", "claude-code", "vscode", "slash-commands", "naming"]
created: 2026-05-17
updated: 2026-05-17
status: stable
source:
  - "[[08-Sessions/2026-05-17-obsidian-vault-pro]]"
---

# VSCode Claude Code extension — slash-command naming UX

A VSCode Claude Code extension slash-command picker popup-ja **csak a parancs-nevet (`name`-et) jeleníti meg** — a markdown frontmatter `description:` mezőt **NEM** mutatja. Ez különbség a Claude Code TUI-hoz képest (a terminálban a description látszik).

## A felfedezés (2026-05-17)

A `/11.11*` család description-jeit emoji+magyar magyarázattal frissítettem (`🟢 Új session indítása — interaktív picker, ha nincs név megadva` formátum), de a popup-ban így néztek ki:

```
/11.11
/11.11focus
/11.11list
/11.11ls
/11.11note
/11.11start
/11.11stop
```

Csak a parancs-név látszott. A description+emoji teljesen invisible volt a UI-ban — csak Claude Code TUI-ban / dokumentációban élt.

## A megoldás: beszédes command-name

A parancs-név önmagáért beszélő legyen, mert csak ez látszik:

| Régi (nem-beszédes) | Új (önmagyarázó) |
|---|---|
| `/11.11start` | `/11.11-uj-session` |
| `/11.11stop` | `/11.11-zar-session` |
| `/11.11focus` | `/11.11-focus` (változatlan, már elég) |
| `/11.11note` | `/11.11-jegyzet` |
| `/11.11ls` | `/11.11-lista` |
| `/11.11` | `/11.11-egeszseg` |

A `/11.11-` prefix megtartása fontos: a popup `/11`-szűréskor minden 11.11-es parancs előjön egyben.

## Egyéb tanulságok

- A `description:` még mindig kell — TUI-ban + dokumentációban él, plus `/help` parancsban használt.
- Az `argument-hint: <kötelező>` vs `[opcionális]` szintaxis a parancs-input után jelez meg a UI-ban, de a tapasztalat szerint `<...>` formátum jobban segít a kurzor-elhelyezésben.
- Az `AskUserQuestion` tool fallback-ként működik a parancs-input-mezőhöz: ha üres argumentum, popup-os választó (recent options + Other free-text). Lásd `/11.11-uj-session.md` markdown logikát: `if [ -n "$ARGUMENTS" ]; then ...; else echo "__NEEDS_NAME__"; fi`, majd Claude AskUserQuestion-t hív a `__NEEDS_NAME__` marker láttán.

## Mikor alkalmazandó

- Bármely slash-command-ot tartalmazó plugin/agent-pack, amit főleg VSCode-extension-ben használsz.
- Plus: nem-magyar (angol) command-családra is — pl. `/git-commit-staged` > `/gitc`.
- Nem alkalmazandó: ha a parancs annyira ritkán hívott, hogy a user kifejezetten begépeli (akkor a hosszabb név inkább zavar).

## Shell-CLI vs slash-command külön névadás

A `/usr/local/bin/11.11*` shell-CLI nevek **változatlanok** (`11.11start`, `11.11stop`, stb.) — ott a terminal-context önmagáért beszél. Csak a slash-parancsok kapnak hosszabb nevet. Az AGENTS.md a két névrendszert külön táblában mutatja.

## Kapcsolódó

- [[11-wiki/claude-code-harness-blocks]] — más Claude Code-specifikus runtime-quirk-ök
- [[11-wiki/external-skill-cherry-pick]] — skill management ahol a name-mező szintén kritikus
