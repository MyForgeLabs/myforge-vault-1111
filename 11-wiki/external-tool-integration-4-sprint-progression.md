---
name: External-tool integráció 4-sprint progression pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "integration", "evergreen", "meta-pattern"]
status: evergreen
---

# External-tool integráció 4-sprint progression pattern

## TL;DR

Egy külső AI-tool / framework (pl. BMAD-Method, Cursor, Claude Agent SDK) integrációja a vault-tudás-rétegbe **NEM big-bang launch**, hanem **4-sprint progression**: (A) bridge-skeleton → (B) skill-level adoption → (C) output-redirect → (D) daemon-watch. Minden sprint külön ROI + measurable, később hozzáadható nélkül a previous sprint-ek bontása nélkül. **Validated 2026-05-18 BMAD-bridge integrációval** (3-5× gyorsulás PRD/Architecture generálás, 0 manuális copy, real-time auto-ingest).

## Háttér

- A `MyForge Vault 11.11` bridge-integráció a BMAD-Method-tal (208 BMAD-skill) **NEM big-bang** működött
- 4 sprint A→D külön-külön measurable + low-risk + reverthető
- Wider lesson: bármely external-tool vault-integráció hasonló progression-t követ

## Mintázat — 4-sprint progression

### Sprint A: **Bridge skeleton (1-2 nap effort)**

- CLI-script: `<external>-vault-bridge` (~300-500 sor)
- 3 mode minimum: `--ingest <file>` / `--context <projekt>` / `--watch <dir>`
- Smoke-test: mock-output 1 projekt-en, end-to-end roundtrip verify
- Frontmatter normalization (külső → vault-konvenció)
- Audit-log JSONL append-only
- **Cél**: standalone CLI-szintű ÉLES, manual-trigger működik
- **ROI**: quick-win demo, későbbi sprint-ek alapja

### Sprint B: **Skill-level adoption (2-3 nap effort)**

- Az external-tool skill-rendszerébe **pre-load step** beépítés
- Mode: skill-első-lépésként `<external>-vault-bridge --context <slug> --json` futtatás
- JSON-output (KO-DB top-K + Memgraph chunks + project-md + recent sessions) injektálódik az agent prompt context-jébe
- Új wiki `<external>-context-preload-pattern.md` documentation
- Per-projekt smoke (3 projekt min, mind PASS)
- **Cél**: külső skill auto-load vault-state-tel mielőtt elkezd dolgozni
- **ROI**: 3-5× gyorsulás (less discovery questions, 0 tool-call stack identification, cross-projekt tanulás unlock)

### Sprint C: **Output-redirect / per-projekt config (2 nap effort)**

- Külső-tool config patch per-projekt (`<external>/config.yaml` planning_artifacts vault-path-re)
- Post-create hook: minden external-output → `<external>-vault-bridge --ingest`
- Frontmatter auto-stamp (`<external>_version`, `<external>_project`, `<external>_phase`)
- Folder-konvenció: `02-Projects/<slug>/<external>/<artifact>.md`
- **Cél**: külső-tool output **natívan** a vault-be ír, 0 manuális copy
- **ROI**: knowledge persistence, frictionless workflow

### Sprint D: **Daemon-watch (1-2 nap effort)**

- systemd template-unit `<external>-vault-watch@.service`
- Per-projekt `systemctl enable <external>-vault-watch@<slug>`
- File-watcher (watchdog/inotify) auto re-ingest on-edit
- Smoke: touch-file → auto-ingest log within 5-10s
- Resource-limit (`MemoryMax=512M`)
- **Cél**: real-time editing → auto re-ingest, Obsidian-szerkesztés is detectálódik
- **ROI**: zero-touch knowledge sync, manual-trigger felesleges

## Anti-pattern

- **Big-bang launch** — minden 4 sprint egyszerre, sok-rizikó, hard-to-debug
- **Skip Sprint A** — direct skill-integration nélkül bridge-skeleton → CLI-test nem szigetelt, debug-hard
- **Skip Sprint B** — output-redirect (Sprint C) anélkül hogy a skill tudja használni a vault-context-et → asymmetric (output landolódik, de discovery still cold)
- **Skip Sprint D** — manual-trigger marad sok-projekt-en, drift-rizikó

## Reusable szabályok

1. **A→D progression sorrend kötelező** — Sprint B Sprint A nélkül = bridge-szigetelés-nélkül; Sprint C Sprint B nélkül = output-redirect hely de pre-load nincs (asymmetric)
2. **Mindegyik sprint külön ROI-mérhető** — NEM "wait until D" attitude. A önmagában demo-érték; B 3-5× gyorsulás; C frictionless; D zero-touch
3. **Idempotens minden lépés** — re-run nem-destruktív, output-stamp idempotens (MERGE NEM INSERT)
4. **Audit-log per-sprint** — JSONL append-only, audit-MD week-summary
5. **Smoke-test mind 3+ projekten** — single-project verify nem elég, edge-case-ek diff-elnek
6. **Reverthető minden sprint** — Sprint D kikapcs: systemd disable; Sprint C kikapcs: config revert; Sprint B kikapcs: skill workflow.md restore; Sprint A kikapcs: bridge-script eltávolítás

## Buktatók

- **External-tool CLI API-változás** — egy major version-bump break-elheti a `--ingest` formátumot. Pin-elt verzió + integration-tests CI-ben.
- **Frontmatter-schema collision** — external-tool standard frontmatter vs vault-konvenció (pl. `bmad_version` field NEM `version:` field). Explicit prefix kötelező.
- **Privacy gotcha** — external-tool output client-PII tartalmazhat (KGC-projekt). `02-Projects/**` always-skip a scrub-rules-on PUBLIC-publikálásnál.
- **Per-projekt config drift** — Sprint C-ben patch-eljük per-projekt config-okat, de external-tool újra-init-kor felülírja. Solution: per-projekt `.<external>-override.yaml`.
- **Daemon resource pile-up** — Sprint D többs projekt-en külön daemon, mind bge-m3 embed-pile-up rizikó. `MemoryMax` kötelező + Redis-dedup heavy-volume-on.

## Mérnöki őszinte (BMAD-validation 2026-05-18)

| Sprint | Effort | Status | Value-add |
|---|---|---|---|
| A bridge | 1 nap | ÉLES (489 sor, 3 mode, 6/6 smoke) | manual CLI works |
| B context-preload | 2 nap | ÉLES (step-00 + workflow patch + 3-projekt smoke PASS) | **3-5× gyorsulás** PRD/Arch |
| C per-projekt redirect | 2 nap | ÉLES (3 config + post-create hook + smoke PASS) | **0 manuális copy** |
| D systemd-watch | 1 nap | ÉLES (template-unit + 3 instance + 6s latency smoke) | **zero-touch real-time** |
| **TOTAL** | **~6 nap effort** | **mind ÉLES 2026-05-18** | **end-to-end auto-integráció** |

**Wider lesson**: az integration-effort NEM front-load. A→D-ig folyamatos value-add, mindegyik sprint külön shippable.

## Kapcsolódó

- [[bmad-vault-integration-pattern]]
- [[bmad-context-preload-pattern]]
- [[systemd-template-unit-multi-project-pattern]]
- [[per-project-context-skill-pattern]]
- [[sprint-day-0-skeleton-first]]
- [[multi-layer-safety-gate]]
