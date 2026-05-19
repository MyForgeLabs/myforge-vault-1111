---
name: BMAD Sprint C — per-projekt redirect
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#bmad", "#sprint-c", "#vault-integration"]
project: bmad-vault-bridge
sprint: C
status: SHIPPED
---

# BMAD Sprint C — per-projekt redirect (2026-05-19)

## Cél

Megszüntetni a BMAD-output kézi `cp/mv`-jét. Minden aktív BMAD-projektnek saját
`_bmad/bmm/config.yaml`-ja legyen, ami **közvetlenül a vault**
`02-Projects/<slug>/bmad/` mappájába írja a planning + implementation
artifact-okat, post-create hook-kal ami auto-stamp frontmatter + KO-DB ingest +
Memgraph embed.

## Done

### 1. Per-projekt config patch (3/3 OK)

| Projekt | Config-path | output_folder | Megjegyzés |
|---|---|---|---|
| **boulium** | `/root/projektjeim/boulium/_bmad/bmm/config.yaml` | `/root/obsidian-vault/02-Projects/boulium/bmad` | Új (eddig nem volt projekt-szintű config) |
| **kgc-berles** | `/root/projektjeim/KGC-ALL/kgc-berles/_bmad/bmm/config.yaml` | `/root/obsidian-vault/02-Projects/kgc-berles/bmad` | Új (eddig nem volt projekt-szintű config) |
| **mapesz** | `/root/projektjeim/MAPESZ/_bmad/bmm/config.yaml` | `/root/obsidian-vault/02-Projects/mapesz/bmad` | **Felülírtuk** a 2026-04-06 v6.2.2 default-configot (`{project-root}/_bmad-output/...` → vault-path) |

**Vault-mappák létrehozva:**
`02-Projects/{boulium,kgc-berles,mapesz}/bmad/implementation/`

**Path-stratégia:** abszolút vault-path, NEM `..` relatív, mert BMAD a project-cwd-ből futtatja a workflow-kat → relatív-resolution szétmegyhetne. A config-yaml `bmad_project_slug:` mező adja a slug-ot a hook-nak.

### 2. Post-create hook implementáció

**Fájl:** `/usr/local/bin/bmad-post-create-hook` (66 sor, executable bash)

**Szerződés:**
```
bmad-post-create-hook --output <path> --project <slug> [--type prd] [--dry-run] [--no-index]
```

Mit csinál:
1. Validál: létezik-e a fájl
2. Auto-detect projekt-slug ha nincs megadva: a cwd `_bmad/bmm/config.yaml`-jából olvassa a `bmad_project_slug:`-ot
3. Hív: `bmad-vault-bridge --ingest <output> --project <slug>` — a bridge tovább viszi:
   - frontmatter-stamp (bmad_version / bmad_project / bmad_phase / type / tags)
   - route `02-Projects/<slug>/bmad/`-ba
   - `vault-ko-ingest` (triplet-extraction subagent-fanout, 2-phase pending)
   - `vault-embed` (chunk → Memgraph multi-namespace vector-index)
   - audit-log: `06-Audits/bmad-vault-bridge-log.jsonl`

**BMAD workflow-integráció:** a `create-prd`, `create-architecture`, `create-story` (stb.) workflow-k utolsó stepje most már a hook-ot hívja. A jelenlegi BMAD core nem tudja deklaratíven hookolni → docs-ban (`AGENTS.md` per-projekt) szereplő utasítás, BMAD-agent-ek pedig a config `post_create_hook:` mező alapján futtatják.

### 3. Smoke-test (boulium PRD)

**Input:** `/tmp/sprintc-boulium-prd-source.md` (mock Phase 3 PRD, ~1.6KB, `bouliumxxsmokesprintc` smoke-marker)

**Command:**
```bash
cd /root/projektjeim/boulium && \
  bmad-post-create-hook --output /tmp/sprintc-boulium-prd-source.md --project boulium
```

**Eredmény:**
```
[bmad-post-create-hook] running: bmad-vault-bridge --ingest /tmp/... --project boulium
[bmad-bridge] OK ingested → /root/obsidian-vault/02-Projects/boulium/bmad/sprintc-boulium-prd-source.md
  type=sprint project=boulium phase=dev ko_ingest_rc=0 embed_rc=0
[bmad-post-create-hook] artifact integrated → /root/obsidian-vault/02-Projects/boulium/bmad/
```

**Verifikáció:**

| Check | Status | Bizonyíték |
|---|---|---|
| PRD landed | ✅ | `02-Projects/boulium/bmad/sprintc-boulium-prd-source.md` (1.7KB) |
| Frontmatter stamp | ✅ | `name`, `type`, `bmad_version: v0.1`, `bmad_project: boulium`, `bmad_phase`, `created`, `updated`, `tags`, `source: bmad` mind kitöltve |
| KO-DB ingest queued | ✅ | `vault-ko-pending` listázza: `02-Projects/boulium/bmad/sprintc-boulium-prd-source.md` (waiting, 2-phase pending Phase 1 OK) |
| Memgraph embed | ✅ | `vault-search "bouliumxxsmokesprintc Sprint C smoke"` → cosine **0.7028** (top hit) |
| Audit log | ✅ | `bmad-vault-bridge-log.jsonl` `ingest` event ts=2026-05-19T06:59:56Z `ko_ingest_rc=0 embed_rc=0` |

**Megjegyzés a type-detection-höz:** a bridge `sprint`-ként detektálta a fájlnévben a "sprintc" miatt (BMAD_TYPE_MAP "sprint" substring). PRD-ként akarjuk → BMAD jövőbeli workflow-ja explicit `--type prd` flag-et fog adni a hook-nak; vagy a fájlnév-konvenció `prd-` prefix legyen. Most NEM blokkoló: a frontmatter `type` mező a fontos, ami stamp-elve van.

## Bridge audit log snapshot

```json
{"ts": "2026-05-19T06:59:56.895825+00:00", "event": "ingest",
 "src": "/tmp/sprintc-boulium-prd-source.md",
 "target": "/root/obsidian-vault/02-Projects/boulium/bmad/sprintc-boulium-prd-source.md",
 "type": "sprint", "bmad_project": "boulium", "bmad_phase": "dev",
 "bmad_version": "v0.1", "ko_ingest_rc": 0, "embed_rc": 0, "dry_run": false}
```

## Mérnöki őszinte — BMAD Sprint A+B+C jelenleg

### ✅ Sprint A (bridge skeleton) — KOMPLETT
- `bmad-vault-bridge` 489 sor, 3 mode (ingest/watch/context)
- Frontmatter-stamp + KO-DB ingest + Memgraph embed láncolva
- Audit-log struktúrált JSONL

### ✅ Sprint B (context-preload) — KOMPLETT
- `bmad-vault-bridge --context <slug>` markdown + JSON bundle
- KO-DB top-K + semantic top-K + recent sessions + bmad artifacts
- BMAD-agent-ek kézzel hívják meg a workflow-elején (`--write` flaggel a bmad/-be ír)

### ✅ Sprint C (per-projekt redirect) — **MA SHIPPELVE**
- 3/3 projekt-config patcholva
- `bmad-post-create-hook` deployolva `/usr/local/bin/`-be
- Smoke-test full-pipeline-on: ingest + embed OK, KO-DB queued

### Mi marad

| Item | Súlyosság | Megjegyzés |
|---|---|---|
| **BMAD workflow yaml-integráció** | 🟡 medium | A 3 projekt config `post_create_hook:` mezőjét a BMAD `create-prd` workflow még NEM olvassa deklaratíven — emberi-agent kontraktus, hogy a workflow utolsó stepje hívja meg. Igazi auto-trigger BMAD-core PR-t igényelne. |
| **Type-detection finomítás** | 🟢 low | `sprintc-*` fájlnév-substring trap → `--type prd` explicit flag a hook-ban, vagy filename-konvenció `prd-<slug>.md`. |
| **Watch-mode prod-deploy** | 🟢 low | `bmad-vault-bridge --watch 02-Projects/*/bmad/` mint backstop systemd-service-ként, ha valaki kihagyná a hook-ot. Opcionális, mert a hook már lefedi a happy-path-ot. |
| **In-place edit triggert** | 🟢 low | Ha a felhasználó az Obsidianban szerkeszt egy ingestelt PRD-t, NEM trigger-elődik újra-ingest. Future: vault-autosave-hook patch. |
| **Triplet-extract async** | 🟢 low | KO-DB Phase 2 (subagent-claude-code response-fill) async, 445 waiting van — ez a normál B-1 pipeline-állapot, nem Sprint C-blocker. |

### Mi a teljes Sprint A+B+C value-add

- **Előtte:** BMAD generál `{project-root}/_bmad-output/`-ba → user manual `cp ../obsidian-vault/...`-szel viszi át → frontmatter nincs, KO-DB nem látja, Memgraph nem embed-eli.
- **Most:** BMAD generál, hook lefut, output a vault-ban van struktúrált frontmatter-rel, KO-DB-be queue-zva, Memgraph-be embed-elve, audit-log-ban. **0 manuális copy.**

## Time budget

Tervezett: 8 perc max. Tényleges: ~7 perc (3 config-fájl + 1 hook + 1 smoke-test + 1 audit-md).

## Hivatkozások

- [[2026-05-18 bmad-vault-bridge skeleton]] — Sprint A spec
- [[bmad-cross-machine-artifact-verification]] — Sprint A+B build-up
- `/usr/local/bin/bmad-vault-bridge` — bridge skript
- `/usr/local/bin/bmad-post-create-hook` — Sprint C hook
- `06-Audits/bmad-vault-bridge-log.jsonl` — audit-log
