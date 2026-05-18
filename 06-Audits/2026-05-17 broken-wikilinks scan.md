---
name: Broken-wikilinks scan (B-7 cross-cut)
type: audit
sprint: B-7
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "#project/sv", "sv-7", "vault-integrity"]
project: [[../02-Projects/superintelligent-vault]]
data: [[broken-wikilinks-2026-05-17.json]]
---

# Broken-wikilinks scan (2026-05-17)

> Deterministic regex-scan (`[[target]]` pattern) az egész vault-on (409 md), B-7 wikilink-importer komplementere. Memgraph nem perzisztálja az `exists=false` flaget — külön scan kell.

## TL;DR

| Metrika | Érték |
|---|---|
| Scanned md files | **409** |
| Total broken targets | **189** |
| Total broken references | **292** |
| Top-target refs | 9 (`01-Daily/2026-05-11`) |

## Hiba-kategóriák (kézi triage a top-20-ból)

### A) Tényleges hibák (~50%)
- **Missing Daily-files** — `01-Daily/2026-05-{10,11,12}` (System_Health.md hivatkozik rájuk, de nincsenek napi-fájlok)
- **Missing ADR** — `07-Decisions/2026-05-XX agentmemory vs vault-grep` (placeholder, soha NEM lett megírva)
- **Missing meta** — `00-Meta/graph-schema.yml` (3 hely hivatkozik, nem létezik)
- **External memory** — `feedback_destructive_action_confirm` / `feedback_claims_verification` → `~/.claude/projects/-root/memory/` (auto-memory NEM része a vaultnak)

### B) Escape-bug (~25%)
- `[[02-Projects/koko\]]`, `[[02-Projects/teszt-eu\]]`, stb. — backslash escape a render-fázisban (`\]` kerül a target-be).
- Source: 02-Projects/Index.md tábla-formatter
- **Fix:** táblákban a `[[...]]` után NEM kell backslash, Obsidian/markdown autoescape OK

### C) Placeholder / dokumentum-példa (~15%)
- `[[X]]`, `[[^\]]`, `[[regex-snippet]]` — kód-példában vagy template-ben
- **Fix:** code-fence (`` `[[X]]` ``) vagy escape

### D) Header-anchor / nem-vault (~10%)
- `[[some-link#header]]` ahol a fájl létezik de a header nem (header-kontextus nélkül false-positive)

## Top-15 broken (refs ≥ 3)

| refs | broken target | top forrás |
|---|---|---|
| 9 | `[[01-Daily/2026-05-11]]` | System_Health.md |
| 7 | `[[07-Decisions/]]` | README + Index |
| 6 | `[[08-Sessions/]]` | README + Index |
| 6 | `[[01-Daily/2026-05-10]]` | System_Health.md |
| 5 | `[[02-Projects/koko\]]` | Index escape-bug |
| 5 | `[[02-Projects/teszt-eu\]]` | Index escape-bug |
| 4 | `[[00-Meta/graph-schema.yml]]` | Backlog, sprint-day-0, sv-b2 session |
| 4 | `[[feedback_claims_verification]]` | rojt-s-bojt sessions (auto-memory ref) |
| 4 | `[[feedback_destructive_action_confirm]]` | rojt-s-bojt + kgc-robbantott sessions |
| 3 | `[[07-Decisions/2026-05-10 Tartozék-rendszer schema (MachineAccessory M:N)]]` | parens-issue M:N → M-N tényleges fájl |
| 3 | `[[02-Projects/kgc-erp\]]` | escape-bug |
| 3 | `[[02-Projects/kgshop-bluebird\]]` | escape-bug |
| 3 | `[[02-Projects/KGC-ALL Architektura]]` | `.canvas` fájl NEM `.md` |
| 3 | `[[02-Projects/mfl-bot\]]` | escape-bug |
| 3 | `[[02-Projects/petanque-kisgeparuhaz\]]` | escape-bug |

## Recommended fixes (priorities)

### P1 — Low-effort, high-impact (~30 ref)
1. **Escape-bug fix** (5 + 3 + 3 + 3 + 3 = ~17 ref) — `02-Projects/Index.md` táblákban `\]` → `]` cseréje (regex `s/\\\]\]/]]/g`)
2. **`[[07-Decisions/]]` és `[[08-Sessions/]]`** (13 ref) → `[[07-Decisions/Index]]` / `[[08-Sessions/]]` folder-link
3. **`(MachineAccessory M:N)` → `(MachineAccessory M-N)`** (3 ref) — colon-cleanup, már `M-N` a tényleges fájlnévben

### P2 — Medium
1. **Auto-memory linkek** (`feedback_*`) — vagy `~/.claude/projects/-root/memory/feedback_*.md` teljes path, vagy mozgatás `05-Memory/`-ba (B-2 Memory Architecture decision)
2. **`00-Meta/graph-schema.yml`** — fájl megírása vagy linkek `00-Meta/Frontmatter-schema` mutatóra cseréje

### P3 — Low-impact
1. **Missing Daily** (`01-Daily/2026-05-{10,11,12}`) — System_Health auto-gen sablon hibája (nem létező napokra linkel). System_Health generátor fix.
2. **Code-example linkek** (`[[X]]`, `[[^\]]`) — code-fence wrap

## Cron-rec

```bash
# /etc/cron.weekly/vault-broken-wikilinks (Sunday 04:45 — vault-cleanup után)
0 4 * * 0 /usr/local/bin/vault-broken-wikilinks-audit --audit-md
```

**Script TODO Week 2:** `/usr/local/bin/vault-broken-wikilinks-audit` — JSON regen + audit-MD update + threshold-alert ha `broken_count > prev_week * 1.2` (regression-detect).

## Adatfájl

- Full broken-list JSON: [[broken-wikilinks-2026-05-17.json]] (189 target × source-list)

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — B-7 sprint
- [[../11-wiki/wikilink-importer-pattern]] — komplementer Memgraph-extraction (ha létrejön)
- [[System_Health]] — daily-link bug forrás
