---
name: 00-Meta/templates — sablonok
type: index
tags: ["#type/index", "templates", "meta"]
created: 2026-04-30
updated: 2026-04-30
---

# 00-Meta/templates/

Új fájlok minimális sablonjai. **Manuálisan másold át**, vagy konfiguráld az Obsidian Templates plugint hogy ezt a mappát használja templates folder-ként.

## Tartalom

| Sablon | Hova alkalmazandó |
|--------|-------------------|
| [[00-Meta/templates/Daily-template]] | `01-Daily/YYYY-MM-DD.md` — napi napló |
| [[00-Meta/templates/Session-template]] | `08-Sessions/YYYY-MM-DD-<slug>.md` — `/11.11start` által autogen, de kézi nyitásra is |
| [[00-Meta/templates/Project-template]] | `02-Projects/<slug>.md` — új projekt |

## Hogyan állítsd be Templates plugint

1. Settings → Templates → Template folder location: `00-Meta/templates`
2. Hotkey: pl. `Cmd+Shift+T` az "Insert template" parancsra
3. Új daily fájl: `Cmd+P` → "Daily Notes: Open today's note" + Templates be-insert

> [!info] Kézzel is működik
> Egy sablon csak egy markdown fájl — másold ki, illeszd be az új fájlba, töltsd ki a placeholder-eket.

## Placeholder-ek

A sablonokban `<...>` és `YYYY-MM-DD` jellegű placeholder-eket használunk. Az Obsidian Templates plugin tudja a `{{date}}`, `{{time}}` szintaxist is — ha úgy szeretnéd, frissítsd a sablonokat.

## Kapcsolódó

- [[00-Meta/Frontmatter-schema]] — minden type-ra a YAML séma
- [[00-Meta/Tag-taxonomy]] — milyen tag-ek mehetnek
- [[11-wiki/11.11-session-protokoll]] — session-fájl protokoll
