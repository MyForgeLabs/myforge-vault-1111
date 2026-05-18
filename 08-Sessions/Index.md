---
name: SV-meta Sessions index
type: index
tags: [sessions, index, sv-meta]
created: 2026-04-23
updated: 2026-05-18
---

# SV-meta Sessions

Az SV (Superintelligent Vault) **meta-session-ök** — a 8-axis sprint fejlesztési története. Minden session a `11.11start`/`11.11stop` workflow-val nyílt és záródott, plus crystallization-protokoll a Learnings → wiki/ADR/MEMORY propagáció.

> A teljes session-történet a vault-ban van; itt csak a **publikussá tett SV-meta** rész jelenik meg. Az ügyfél-projekt session-ek (KGC, Foxxi, MFL, stb.) nem publikusak.

> **Snapshot:** 14 SV-meta session.

## Session-lista (újabb először)

| Dátum + slug | Téma | |
|--------------|------|--|
| 2026-05-18 | [[2026-05-18-obsidian-vault\|obsidian-vault]] | |
| 2026-05-17 | [[2026-05-17-obsidian-vault\|obsidian-vault]] | |
| 2026-05-17 | [[2026-05-17-obsidian-vault-pro\|obsidian-vault-pro]] | |
| 2026-05-17 | [[2026-05-17-obsidian-vault-3\|obsidian-vault-3]] | |
| 2026-05-17 | [[2026-05-17-obsidian-vault-2\|obsidian-vault-2]] | |
| 2026-05-16 | [[2026-05-16-obsidian-vault-rdekes-k-rd-sek\|obsidian-vault-rdekes-k-rd-sek]] | |
| 2026-05-13 | [[2026-05-13-sv-week2-extend\|sv-week2-extend]] | |
| 2026-05-13 | [[2026-05-13-sv-week1-implementation\|sv-week1-implementation]] | |
| 2026-05-13 | [[2026-05-13-sv-obsidian-coloring\|sv-obsidian-coloring]] | |
| 2026-05-13 | [[2026-05-13-sv-obsidian-coloring-fix\|sv-obsidian-coloring-fix]] | |
| 2026-05-13 | [[2026-05-13-sv-functional-payoff\|sv-functional-payoff]] | |
| 2026-05-13 | [[2026-05-13-sv-day0-cascade\|sv-day0-cascade]] | |
| 2026-05-13 | [[2026-05-13-sv-b2-memory-architecture\|sv-b2-memory-architecture]] | |
| 2026-05-12 | [[2026-05-12-obsidian-vault\|obsidian-vault]] | |

## Workflow

1. **`11.11start "<projekt-feladat>"`** — új session-fájl + focus
2. **`11.11note "..."`** — timestamped jegyzet az `## Events`-be
3. **`11.11stop`** — Summary + Learnings + Next ; agent: crystallization-protokoll
4. **Cron auto-sync** 30-perc — minden change a public-repo-ra

## Kapcsolódó

- [[../11-wiki/11.11-session-protokoll|11.11 session-protokoll wiki]]
- [[../11-wiki/Crystallization-protocol|Crystallization protocol]]
- [[../11-wiki/Auto-context-loading|Auto-context loading]]
