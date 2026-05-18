---
name: bash-patches — telepítési útmutató
type: index
tags: ["#type/index", "11.11", "deploy", "bash"]
created: 2026-04-30
updated: 2026-04-30
---

# 00-Meta/bash-patches/

A `/usr/local/bin/11.11start` és `/usr/local/bin/11.11stop` scriptekhez tartozó **kibővítések**. A vault-protokoll ([[11-wiki/Auto-context-loading]] + [[11-wiki/Crystallization-protocol]]) **agent-szinten kötelező** — ezek a patch-ek a script-szintű kapcsolódást adják hozzá, hogy a `## Pre-loaded context` és `## Propagation log` szekciók ott legyenek a session-template-en, és a stop-kor a Learnings clipboard-ba is kerüljön.

## Patch-fájlok

| Patch | Mit tesz | Ahol fut |
|-------|----------|---------|
| `00-Meta/bash-patches/11.11start.patch` | A script által generált session-fájl új template-jét használja a [[00-Meta/templates/Session-template]]-ből (Pre-loaded context + Propagation log szekciókkal) + agent-prompt fájl-végbe ami `auto-context-load:`-ot mond | dev VPS + prod VPS + Mac |
| `00-Meta/bash-patches/11.11stop.patch` | Záráskor: a `## Learnings` szekciót clipboard-ba másolja (xclip / pbcopy) + agent-prompt-ot ír egy `.last-stop-prompt` fájlba ami a propagáció batch preview-ját szólítja | dev VPS + prod VPS + Mac |

## Telepítés (dev + prod + Mac)

```sh
# 1. Klónold le a vault-ot ha még nincs (a dev VPS-en már megvan, prod-ra kell)
cd /root/obsidian-vault   # vagy ahol a vault-od van

# 2. Backup a jelenlegi scriptekről
cp /usr/local/bin/11.11start /usr/local/bin/11.11start.bak
cp /usr/local/bin/11.11stop  /usr/local/bin/11.11stop.bak

# 3. Apply patches
patch /usr/local/bin/11.11start < 00-Meta/bash-patches/11.11start.patch
patch /usr/local/bin/11.11stop  < 00-Meta/bash-patches/11.11stop.patch

# 4. Permission check
chmod +x /usr/local/bin/11.11start /usr/local/bin/11.11stop

# 5. Smoke teszt — egy próba session
11.11start "patch teszt"
11.11ls
11.11note "működik?"
11.11stop
# Várd: a session-fájlban legyen ## Pre-loaded context, és a stop után
# a clipboard-on legyen a `## Learnings` szekció szövege
```

## Mac-specifikus: pbcopy vs xclip

A patch `xclip -selection clipboard` -ot használ Linux-on, `pbcopy` -t Mac-en. A patch automatikusan detektálja:

```bash
if command -v pbcopy >/dev/null 2>&1; then
    CLIPBOARD_CMD="pbcopy"
elif command -v xclip >/dev/null 2>&1; then
    CLIPBOARD_CMD="xclip -selection clipboard"
else
    CLIPBOARD_CMD=""   # gracefully no-op
fi
```

## Rollback

```sh
cp /usr/local/bin/11.11start.bak /usr/local/bin/11.11start
cp /usr/local/bin/11.11stop.bak  /usr/local/bin/11.11stop
```

## Mi van **NEM** ebben a patch-ben

- **A tényleges agent-viselkedés** (pre-load + propagation) nem itt él, hanem [[AGENTS]]-ben + [[11-wiki/Auto-context-loading]] + [[11-wiki/Crystallization-protocol]]-ban. Az agent ezeket a session elején/végén olvassa (mert mindhárom agent az AGENTS.md-t betölti).
- **A session-template valamilyen integrációja** — a patch csak placeholder szöveget ír; az agent feladata kitölteni.

## Kapcsolódó

- [[11-wiki/Auto-context-loading]]
- [[11-wiki/Crystallization-protocol]]
- [[11-wiki/11.11-session-protokoll]]
- [[07-Decisions/2026-04-30 Crystallization workflow + auto-context-loading]]
