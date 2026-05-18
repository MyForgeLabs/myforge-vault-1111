---
name: Vault-corruption detection pattern
type: wiki
tags: ["#type/wiki", "vault", "integrity", "monitoring", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Vault-corruption detection pattern

## TL;DR

Egy 3000+ MD-fájl, 13K+ KO-DB-fact, 9K Memgraph-entity vault sokféleképpen tud "csendben sérülni" (broken-link bekúszik, encoding-bug, escape-strip, frontmatter-drift, self-referential-loop, orphan-wiki). A **vault-corruption detection pattern** ezt 5 detection-axison méri, mindegyik külön script-tel, JSON+MD output-tal, weekly cron-nal. A 5 axis komplementer — egyik sem helyettesíti a másikat.

## Háttér

A vault-szerkezet egyre bonyolultabb lett (Karpathy LLM-Wiki-pattern + Johnny-Decimal + B-1..B-8 SV-pipeline), és a "corruption" többé nem `git status` -szel látható. Néhány konkrét incidens vezetett a detection-axis-mátrixhoz:

- **2026-04-15** — Elementor JSON-export backslash-strip a Unicode escape-eken, `é` → `u00e9` raw-szöveg lett (silent corruption, csak rendering-kor látszott)
- **2026-05-10** — `audit-md-self-referential-loop` egy script-output beolvasta a saját korábbi snapshot-ját, körkörös aggregátum
- **2026-05-15** — vault-rename közben aktív Mac Obsidian-Git sync → detached HEAD, dupla conflict-cascade
- **2026-05-17** — broken-wikilinks scan ~120 broken-target talált, ami a Memgraph importer-ből nem volt látszó (`exists=false` not persisted)
- **2026-05-17** — orphan-wiki 0-ref MD-fájlok ~25 db (cleanup-candidate vagy index-be felvenni)

## Detection-axes (5)

### 1. Broken wikilinks

- **Script**: `vault-broken-wikilinks-audit` ([[wikilink-importer-pattern]])
- **Output**: `06-Audits/broken-wikilinks-YYYY-MM-DD.json` + `latest.md`
- **Symptom**: `[[target]]` link de a target MD nem létezik
- **Cron**: weekly Sun 04:45

### 2. Self-referential loops

- **Script**: `audit-md-self-referential-loop` pattern
- **Output**: detection-log + suggested-cleanup list
- **Symptom**: snapshot-MD beolvassa egy másik snapshot-MD-t ami beolvassa az elsőt; aggregátor körkörös; recursion-overflow
- **Detection**: import-graph (Cypher-szerű) DFS + cycle-detect

### 3. Encoding corruption

- **Script**: `vault-encoding-audit` (regex-scan)
- **Output**: minden `u00XX`, `\\xXX`, mojibake-pattern detect
- **Symptom**: `u00e9` helyett `é`, double-escaped Unicode (`\\u00e9`), Latin-1 misread mint UTF-8
- **Forrás**: Elementor JSON-export, WP-CLI postmeta encode, copy-paste browser → MD

### 4. Frontmatter drift

- **Script**: `vault-frontmatter-validate` (YAML schema)
- **Schema**: `00-Meta/Frontmatter-schema.md`
- **Symptom**: hiányzó `name:`, rossz `type:`, érvénytelen `created:` date-format, alias-collision
- **Output**: per-fájl validation-report

### 5. Orphan wiki

- **Script**: `vault-orphan-wiki`
- **Output**: 0-ref MD-fájlok listája (`backlink-count = 0`)
- **Action**: cleanup-candidate vagy `Index.md`-be felvenni

## Mintázat (overarching policy)

1. **Minden axis külön script** — egyik failure ne kaszkádolja a többit
2. **JSON + MD output minden script** — machine + human readable
3. **Weekly cron rotation** — Sun 04:45 → 05:30, +5-10 perc gap
4. **Delta-based threshold** — prev-vs-current; abszolút szám csak baseline-hoz
5. **System_Health.md aggregátor** — 5 axis output egy helyen vasárnap regenerálva

## Anti-pattern

- **Single mega-audit-script** — slow, hard-debug, kaszkád-failure
- **Manual ad-hoc scan** — nem reprodukálható, weekly delta nem mérhető
- **`git status` mint primary integrity-check** — silent corruption ezt nem mutatja (a fájl ott van, csak rossz tartalommal)
- **No baseline** — első run csak signal-baseline, NEM action; minden audit-nak kell prev-snapshot
- **Encoding-detect csak Unicode-on** — Latin-1 misread és double-escape külön regex

## Reusable szabályok

1. **5 axis külön, NEM merge-elve** — orthogonal concerns, eltérő failure-mode
2. **`latest.md` symlink minden axis-ra** — Obsidian-rendelhető human-overview
3. **Threshold-alert delta-on** — `regression +20%` → exit 1 + cron-email
4. **Spot-check minden axis-on havonta** — N=5 random fájl manual ground-truth
5. **Audit-log JSON-line** — `/root/.vault-config/audit-log.jsonl` minden script-event
6. **System_Health.md weekly regen** — 5 axis aggregátum, top-priority broken-cluster listázva
7. **Auto-disable min-volume guard** — corruption/restart utáni false-positive avoidance

## Buktatók

- A Memgraph wikilink-importer **nem perzisztálja az `exists=false`** flag-et → csak a regex-réteg látja a broken-target-eket; **mindig regex = ground-truth**
- `vault-orphan-wiki` false-positive lesz, ha a backlink-graph stale (Memgraph importer késett) → mindig friss graph-on futtass
- Encoding-corruption detect false-positive a code-block-okban (`u00e9` lehet legitim Python-kód) → fenced-block skip
- Frontmatter-validate strict-mode-ban a régi MD-k tömegével failnak → introduce gradually, exception-list TODO-flaggel
- Self-referential-loop detect mély DFS-szel → memo-cache kell, különben quadratic-time

## Kapcsolódó

- [[audit-md-self-referential-loop]]
- [[wikilink-importer-pattern]] — axis 1 mélyebb
- [[vault-ko-conflicts-audit-design]] — KO-DB layer (komplementer)
- [[vault-cleanup-multi-script-policy]] — cron orchestration
- [[../06-Audits/System_Health]] — aggregátor
- [[auto-disable-min-volume-guard]] — false-positive guard
- [[../00-Meta/Frontmatter-schema]] — schema-ref
