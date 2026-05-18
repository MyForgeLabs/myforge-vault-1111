---
name: Frontmatter séma
type: reference
tags: [memory, schema, frontmatter, yaml]
created: 2026-04-23
updated: 2026-05-08
---

# YAML frontmatter séma

> [!important] Kötelező
> Minden vault-fájlnak legyen frontmatter-e. Dátumok **ISO-8601** formátumban (`YYYY-MM-DD` vagy `YYYY-MM-DDTHH:MM:SS±ZZ`). Listák mindig `tags: []` array-ként.

## Közös mezők (minden fájl)

```yaml
---
name: Rövid cím (1 sor, displayben látszódik)
type: host | project | decision | audit | session | memory | task | reference | index | dashboard | research-summary | backlog | daily-note | feedback | document
tags: ["#env/prod", "#type/host"]   # lásd [[00-Meta/Tag-taxonomy]]
created: 2026-04-23                  # ISO-8601
updated: 2026-04-23                  # ISO-8601 — frissítsd minden módosításkor
---
```

> [!info] Enum bővítések 2026-05-08
> - `daily-note` — [[01-Daily/]] napi naplók (autogen, Sessions/Decisions/Raw/Audits összegzés)
> - `feedback` — [[05-Memory/]] agent-viselkedés feedback mintázatok
> - `document` — egyéb hosszabb dokumentum (pl. CV, hosszú jegyzet) ha nem illik másik enumba

## Típus-specifikus mezők

### `type: host` ([[03-Hosts/]] fájlok)

```yaml
---
name: "vps-prod-example - prod"
type: host
hostname: vps-prod-example.hstgr.cloud
ipv4: "72.62.92.98"
ipv6: "2a02:4780:41:2242::1"
role: prod                           # enum: prod | dev | staging | shared
status: active                       # enum: active | archived | decommissioned
tags: ["#type/host", "#env/prod"]
created: 2026-04-23
updated: 2026-04-23
---
```

### `type: project` ([[02-Projects/]] fájlok)

```yaml
---
name: Kokó projekt
type: project
status: active                       # enum: active | done-with-backlog | production | paused | archived
repo_prod: /path/on/prod            # opcionális
repo_dev: /path/on/dev              # opcionális
public_url: https://...              # opcionális
notebooklm: <UUID>                   # opcionális (B-5 vault-nb-sync auto-write)
tags: ["#type/project", "#env/prod"]
created: 2025-12-24
updated: 2026-04-23
---
```

**Status-konvenció (2026-05-13 bővítve B-5 vault-nb-sync miatt):**

A `status:` mező **heterogén** a vault-ban — egyes projekt-fájlok emoji-prefix-szel (🟢/🟡), mások plain string-gel ("active"/"production") jelölik. Mindkettő elfogadott. Auto-script-ek **permissive irányba defaultoljanak** (NOT-exclude archived/deprecated/abandoned/closed/obsolete keyword-eket), NEM strict-emoji-include-ra.

| Format | Példa | Active? |
|---|---|---|
| **Emoji-prefix** | `🟢 active — production` | ✅ |
| **Emoji-prefix sárga** | `🟡 Day 0 ✓ (2026-05-13)` | ✅ |
| **Plain string** | `active` / `production` / `done-with-backlog` | ✅ |
| **Archived-tagged** | `archived` / `deprecated` / `abandoned` | ❌ |
| **Empty** | (frontmatter-mező hiányzik) | ❌ |

`vault-nb-sync.py` `ARCHIVED_KEYWORDS` szabálya: status-szöveg lower() → NEM contains archived/deprecated/abandoned/closed/obsolete = active.

### `type: decision` ([[07-Decisions/]] fájlok — ADR)

```yaml
---
name: Döntés címe (pl. "Egységes agent memória")
type: decision
status: accepted                     # enum: proposed | accepted | rejected | superseded | in-progress
date: 2026-04-23                     # mikor döntöttünk
tags: ["#type/decision", "#tech/..."]
---
```

### `type: audit` ([[06-Audits/]] fájlok)

```yaml
---
name: Audit címe
type: audit
date: 2026-04-23
author: claude                       # melyik agent csinálta
tags: ["#type/audit", "#env/prod", "#env/dev"]
---
```

### `type: session` ([[08-Sessions/]] fájlok — `/11.11start` által generálva)

```yaml
---
name: session-név
project: projekt-slug                # slug egyezik a Projects/<slug>.md-vel ha van
status: open | closed
started: 2026-04-23T18:37+00:00
ended:                               # ISO-8601 ha closed
agent: claude | codex | gemini
tags: ["#type/session", "#project/..."]
---
```

### `type: task` (egyedi task fájlok, ha vannak)

Jelenleg a [[04-Tasks/Backlog]] egyetlen fájl. Ha külön task-fájlok kellenek:

```yaml
---
name: Task leírás
type: task
priority: highest | high | medium | low | lowest    # Obsidian Tasks emoji: 🔺⏫🔼🔽⏬
due: 2026-04-30
status: open | done | cancelled
tags: ["#type/task", "#op/..."]
---
```

### `type: memory` ([[05-Memory/]] fájlok)

```yaml
---
name: Memória-téma
type: memory                         # vagy reference a lookup-fájloknak
tags: ["#type/memory"]
created: 2026-04-23
updated: 2026-04-23
---
```

### `type: research-summary` ([[07-Decisions/]] kutatási desztillátumok)

```yaml
---
name: Kutatás-összefoglaló címe
type: research-summary
tags: [research, ...]
date: 2026-04-23
sources_count: 483                   # opcionális, honnan jött
notebooklm_notebook_id: ...          # opcionális, NotebookLM visszalinkelés
---
```

## Szabályok

1. **ISO dátum kötelező** — ne használj "2026. ápr 23" / "április 23" / "Thursday" formát, mindig `YYYY-MM-DD`
2. **Listák array-ben** — `tags: []`, nem `tag1, tag2`
3. **Mezőnevek kisbetűsen**, snake_case: `created`, `updated`, `public_url`, **nem** `Created` vagy `publicURL`
4. **Enum értékek kisbetű** a státuszokhoz: `active`, `archived`, `accepted`
5. **Hiányzó mezők** — ha nem tudod az értéket, inkább **hagyd ki a mezőt** mint `null`-t vagy üres stringet írj bele
6. **Wikilink a frontmatterben** — formailag fura; inkább a body-ban hivatkozz

## Ellenőrzés

Az [[06-Audits/System_Health.md]] (ha majd létrejön) Dataview-query-vel listázza:
- fájlok hiányzó frontmatterrel
- érvénytelen dátum-formátummal
- type: nélküli fájlokkal
- ismeretlen type-okkal

## Kapcsolódó

- [[00-Meta/Tag-taxonomy]] — tag-konvenciók
- [[AGENTS]] — itt hivatkozva
- **Obsidian Dataview docs:** https://github.com/blacksmithgu/obsidian-dataview
