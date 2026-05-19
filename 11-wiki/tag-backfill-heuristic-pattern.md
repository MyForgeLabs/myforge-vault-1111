---
name: Tag-backfill heuristic pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "vault", "automation", "evergreen"]
status: evergreen
---

# Tag-backfill heuristic pattern

## TL;DR

A vault-tag-taxonomy bővítésekor a meglevő 200-300 fájl jelentős része NEM-tag-konform marad. A **tag-backfill heuristic pattern** 3 réteg-szerinti automatizált tag-detection (filename + frontmatter-list + custom-hierarchy), **FP <5%** + sentinel-jelölt revertible. A naive v1 (body-keyword-scan) **20% FP-rate**-ot ad — egy session ami EGYSZER említi a `wordpress` szót megkapja a `#tech/wordpress` tag-et. A v2 fix: **tech-tags csak filename-ből, NEM body-scan**.

## Háttér

- **Probléma**: Tag-taxonomy bővítés után 94 (31%) wiki/audit non-compliant az utolsó 7 napon
- **Naive v1** (body keyword-scan): 20% FP — over-tagging session-eket egy említés alapján
- **v2 fix-ek** (3 réteg):
  1. **Filename-only tech-tag** — pl. `wp-elementor-template-conflicts.md` → `#tech/wp`, NEM body-szóra
  2. **Multi-line YAML list parsing** — `tags:\n  - axis/B-7` listát NEM `axis/B-7` bare tag-ként parse-olni
  3. **Custom hierarchy permit** — `axis/B-7`, `layer/audit` compliant-ként ismerni `#` prefix nélkül

## Mintázat

1. **Scan time-window** (utolsó 7 nap) frontmatter `tags:` field-jét per-file
2. **3-réteg detection** filename + frontmatter + custom-hierarchy
3. **Confidence-threshold** (≥0.8) auto-apply
4. **Sentinel-marker** frontmatter-field (`tag_backfill: YYYY-MM-DD`) revertible
5. **Audit-log JSONL** minden mutation-re
6. **Dry-run default** + `--apply` flag

## Anti-pattern

- **Body keyword-scan** — over-fires (egy említés == teljes tag-attach). 20% FP.
- **No sentinel** — irreverzibilis cleanup, ha v2 fix kell, manual git revert.
- **No audit-log** — diff-only után nem lehet érteni mit-miért tag-elt.
- **Apply default-ON** — confidence-control nélkül destruktív.

## Reusable szabályok

1. **Filename > body** keyword-detection — fájlnév szándékos szerző-tag, body csak említés
2. **Sentinel-frontmatter** (`tag_backfill: <date>`) MINDIG, hogy bulk-revert `grep -l + git checkout`-tal megoldható
3. **Audit-log JSONL** (append-only) per-file decision-trace
4. **Idempotens** — re-run 0 új proposal compliance steady-state után
5. **Multi-line YAML list parse** — `tags:\n  - X\n  - Y` formát NEM bare X / bare Y-ként
6. **Custom hierarchy** (`axis/B-7`) compliant `#` prefix nélkül is — vault-specific konvenció

## Buktatók

- **Project-slug filename collision** — session `2026-05-18-koko-side-quest.md` ha valójában KGC-ről szól, megkapja a `#project/koko` tag-et. Low-impact (over-tagging, NEM mis-tagging), de tudni kell.
- **Sentinel-collision** — ha valaki manuálisan írta már a `tag_backfill: YYYY-MM-DD` field-et más céllal, ütközik. Convention: csak a script írja.

## Kapcsolódó

- [[00-Meta/Tag-taxonomy]]
- [[00-Meta/Frontmatter-schema]]
- [[audit-md-self-referential-loop]]
- [[verification-step-before-claim]]
