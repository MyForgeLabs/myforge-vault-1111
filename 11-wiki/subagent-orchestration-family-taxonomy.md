---
name: Subagent-orchestration család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "claude-code", "subagent", "orchestration", "taxonomy", "evergreen", "fanout"]
---

# Subagent-orchestration család taxonomy

> [!info] TL;DR
> A vault-ban **7 Concept + 25 wiki-említés** beszél „subagent-fanout"-ról, de a tényleges használat **5 különböző orchestration-protokoll** keveredik egy szó alatt: (1) **flat fanout** (1-szint, N-parallel), (2) **subagent-tree** (2-szint, lead+children), (3) **cascade fanout** (Day 0 trial → 8-parallel ramp), (4) **2-phase pending** (extraction subagent + finalize), (5) **context-aware classification** (subagent-tree elágazás per-task-typology). Ez a wiki disambiguálja melyik mikor használandó, mit NEM, és mi a Task-tool elérhetőségi protokoll.

## Cluster-members (vault Concept-corpus)

| Concept | Protokoll | Forrás |
|---|---|---|
| subagent-fanout | flat | wiki/claude-code-subagent-fanout |
| Claude Code subscription | platform | wiki |
| general-purpose subagents | agent-class | wiki |
| parallel spawn pattern | mechanizmus | wiki |
| cascade phase 8 agents x 30 files | cascade | wiki (SV B-4) |
| run_in_background=true | mechanizmus | wiki |
| async notifications | mechanizmus | wiki |
| 2-step introduction trial then cascade | cascade-ramp | wiki |
| Subagent context-budget ~50–65K tokens | context-budget | session/2026-05-16, 2026-05-17 |
| clean-context-subagent-handoff | context-handoff | wiki/clean-context-subagent-handoff |
| 2-phase pending pattern (KO-DB extraction) | 2-phase | MEMORY.md |
| 13× subagent-fanout super-session | live-deploy | MEMORY.md |
| subagent-fanout-context-aware-classification | branching | wiki/subagent-fanout-context-aware-classification |
| multi-agent-pointer-ownership-lock | concurrency | wiki/multi-agent-pointer-ownership-lock |
| agent-tree cascade failure | hibatűrés | session |

## Az 5 orchestration-protokoll

### 1. Flat fanout (1-szint, N-parallel) — a klasszikus
**Mintázat:** parent N=5–10 general-purpose subagent-et **párhuzamosan** spawnol, mindegyik egy fájl-batch-en LLM-mutál, eredmény visszafolyik a parent-be (map-reduce).
- **Trigger:** 5+ azonos típusú független task
- **Mechanizmus:** Task-tool fanout, `run_in_background=true`
- **Cost:** $0 (Claude Code subscription, NEM Anthropic API)
- **Context-budget:** ~50–65K token per task elég extraction-höz
- **Hibatűrés:** 1 subagent fail NEM borítja a többi futását, parent-aggregator dönt
- **Példa:** SV B-4 cascade 8×30 fájl, MEMORY.md 13× super-session

→ [[claude-code-subagent-fanout]]

### 2. Subagent-tree (2-szint, lead + children)
**Mintázat:** lead-subagent (clean-context) maga is N grandchild-et spawnol — fan-out fan-out.
- **Trigger:** rekurzív feladat (research → per-source extraction)
- **Mechanizmus:** Anthropic platform limit, NEM minden Claude Code session-ben elérhető (lásd Task-tool elérhetőség lent)
- **Context-budget:** lead 50K + children 50K = ~150K total, parent-budget-et nem fogyasztja
- **Anti-pattern:** sequential pipeline ne legyen subagent-tree, csak parallel-decomposable task

→ [[clean-context-subagent-handoff]]

### 3. Cascade fanout (Day 0 trial → 8-parallel ramp)
**Mintázat:** **2-step** rollout — előbb **1 trial-agent × 30 file** (validate output quality), user-confirm, majd **8-parallel × 30 file** cascade.
- **Trigger:** N >100 fájl, ismeretlen kimeneti minőség
- **Mechanizmus:** trial-batch validate → confirm-gate → cascade
- **Cost:** trial 1× cost, cascade 8× cost, total 9× (NEM 16× ha rögtön 8-parallel)
- **Hibatűrés:** trial fail → cascade NEM indul (1× cost megspórolva)
- **Példa:** SV B-4 462/462 SkillChunk cascade (8-parallel × 30)

→ [[claude-code-subagent-fanout]] + [[sprint-day-0-skeleton-first]]

### 4. 2-phase pending (extraction subagent + finalize)
**Mintázat:** **két különálló run** — első run: extraction-subagent generál pending-JSON-t, second run: parent betölti és véglegesít.
- **Trigger:** KO-DB triplet-extraction, G-Eval scoring (`claude_code_scorer_load_response`)
- **Mechanizmus:** `/tmp/vault-crystallize-pending/<slug>.json` file-állapot mediál
- **Filesystem-as-state:** [[filesystem-as-state-pattern]]
- **Cost:** $0, $0 (két fanout-run egyenként)
- **Példa:** `vault-ko-ingest`, `11.11crystallize --scorer claude-code --with-context`

### 5. Context-aware classification (subagent-tree elágazás per-task-typology)
**Mintázat:** lead-subagent ELŐSZÖR taxonomy-classificálja a task-okat, MAJD a megfelelő-protokollú children-flow-t indítja (flat / cascade / 2-phase).
- **Trigger:** heterogén task-batch (pl. „processzáld ezt a session-summary-t" — lehet extraction VAGY scoring VAGY routing)
- **Mechanizmus:** lead-classifier → branch-router → children-spawn
- **Cost:** lead-classifier ~1× small, children N× regular

→ [[subagent-fanout-context-aware-classification]]

## Task-tool elérhetőség (KRITIKUS)

A subagent-spawn-ot az Anthropic platform a `Task` tool-on keresztül teszi elérhetővé:

- ✅ **Main session** (Claude Code interactive) — `Task` elérhető, általában megengedett
- ⚠️ **Sub-agent context** — `Task` NEM mindig elérhető (platform-side block, anti-recursion), csak lapos fanout (1-szint) garantált
- ❌ **General-purpose subagent → general-purpose grandchild** — platform-block, NEM 2-szint fanout
- 💡 **Workaround:** 2-phase pending pattern + filesystem-as-state (lead írja a pending-JSON-t, second top-level run finalizálja)

Detektálás: subagent-promptban `Task`-hivás → ha `InputValidationError: tool not available` → fallback 2-phase pending.

## Context-budget tuning (mért adatok)

| Task-típus | Per-subagent budget | Forrás |
|---|---|---|
| Frontmatter normalize, 30 fájl | ~20–30K token | wiki (B-4 sprint) |
| Session-summary, 5 fájl | ~50–65K token | session 2026-05-16/17 |
| KO-DB triplet-extraction, 1 doc | ~50K token | MEMORY.md B-4 |
| G-Eval scoring, 1 bullet | ~5–8K token | crystallize hook |
| NB-backfill, 1 session | ~30K token | MEMORY.md Phase 5 |

**Reusable szabály:** subagent-prompt méret ≈ task-input + 5–10K instruction overhead. Ha output JSON-fanout, +10K margin. Ha output Markdown-doc, +20K margin.

## Mintázat — döntés-mátrix

| Helyzet | Protokoll | Batch-size |
|---|---|---|
| 30 fájl × frontmatter | Flat fanout | 5 agents × 6 fájl |
| 100+ fájl × LLM-mutáció ismeretlen minőséggel | Cascade (Day 0 trial) | 1×30 trial + 8×30 cascade |
| KO-DB triplet-extraction (Task-tool blocked) | 2-phase pending | 1 extraction + 1 finalize |
| Heterogén task-batch | Context-aware classification | lead 1 + children 5–8 |
| Per-source-research → aggregálás | Subagent-tree (ha elérhető) | lead 1 + grandchildren 3–5 |
| Cross-document reasoning | ❌ NEM fanout — sequential agent | 1 |
| State-machine sorrend-kötött | ❌ NEM fanout — sequential pipeline | 1 |

## Anti-pattern

- ❌ **„Több agent mindig jobb"** — Claude Code subagent-pool limit ~10, 11+ → rate-limit. SV B-4 max 8-parallel a sweet-spot.
- ❌ **„Subagent-ben Task-tool van"** — platform-block, NEM 2-szint. Workaround: 2-phase pending.
- ❌ **„Cross-document reasoning fanout-tal"** — egy agent kell, NEM fanout (egy doc-hoz másikat kell olvasni).
- ❌ **„Cascade Day 0-án 8-parallel"** — trial nélkül 8× cost a vakon, fail esetén 8× veszteség. ELŐBB trial.
- ❌ **„Subagent context-budget unlimited"** — ~50–65K cap a hatékony, fölötte degradál.
- ❌ **„Subagent-fanout = batch-API"** — NEM, ez Claude Code subscription-flow, NEM Anthropic Message Batches.
- ❌ **„run_in_background nélkül"** — parent blokkolódik, párhuzamosság elveszik. Cascade-hez kötelező.

## Pointer-ownership lock (concurrency)

Több subagent egyszerre írhat ugyanarra a fájlra (pl. KO-DB SQLite) → race condition. **Globális mutex / pointer-lock kötelező:**

- SQLite: `INGEST_MUTEX` global lock + outer-conn `conn.commit()` (lásd MEMORY.md robbantott-kereso bug-fix)
- KO-DB: per-source `provenance` constraint + idempotent upsert
- Session-pointer: `.active-session-$CLAUDE_CODE_SESSION_ID` per-chat (lásd [[claude-code-session-id-per-chat-isolation]])

→ [[multi-agent-pointer-ownership-lock]]

## Kapcsolódó

- [[claude-code-subagent-fanout]] — alfa-pattern: flat fanout playbook
- [[subagent-fanout-context-aware-classification]] — alfa-pattern: protokoll 5
- [[clean-context-subagent-handoff]] — alfa-pattern: subagent-tree handoff
- [[multi-agent-pointer-ownership-lock]] — concurrency lock
- [[filesystem-as-state-pattern]] — 2-phase pending mediátor
- [[claude-code-session-id-per-chat-isolation]] — per-chat session-isolation
- [[cascade-pattern-family-taxonomy]] — sister-taxonomy (cascade 4 jelentés-réteg)
- [[sprint-day-0-skeleton-first]] — cascade Day 0 trial-rampa
- [[sv-03-multi-agent-orchestration]] — architektúra-szint
- [[batch-preview-confirmation-pattern]] — user-gate cascade előtt
- [[claude-code-harness-blocks]] — Task-tool platform-side block-pattern

## Forrás

- Memory bullet: 13×, 14×, 19× subagent-fanout super-session 2026-05-17-{1,2,3}
- Memory bullet (Phase 5): 9× subagent-fanout / 3-csomag (ramp-prep + cross-projekt synthesis + perf/B-7)
- KO-DB facts 86–113, 121–126, 131–132, 183, 8119, 13766 (subagent context-budget mért adatok)
- Session 2026-05-16-obsidian-vault-rdekes-k-rd-sek (context-budget tuning)
- [[../11-wiki/claude-code-subagent-fanout]] (alfa-pattern, jelenleg ~10K token)
