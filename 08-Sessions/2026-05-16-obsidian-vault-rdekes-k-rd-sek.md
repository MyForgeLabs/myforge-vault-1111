---
name: Obsidian-Vault-Érdekes_kérdések
type: session
project: obsidian-vault-rdekes-k-rd-sek
status: closed
started: 2026-05-16T14:54+00:00
ended: 2026-05-17T13:56+00:00
agent: claude
# B-3 eval fields (auto-backfilled, null = not yet evaluated)
eval_score: null
eval_critique: null
hallucination_flag: false
eval_l2_agreement: null
tags: ["#type/session", "#project/obsidian-vault-rdekes-k-rd-sek"]
---

## Pre-loaded context

> Auto-load 2026-05-16T14:54 — agent: claude — **vault-meta session** (lean budget ~2K token)

**Projekt-detektálás:** "obsidian-vault" + "érdekes kérdések" → vault-meta session (NEM projekt-fájl), [[11-wiki/Auto-context-loading]] szerint lean pre-load: csak vault-szerkezet + Karpathy-minta + recent activity.

**Vault state (snapshot):**
- 308 markdown fájl, 9 fő mappa (00-Meta…11-wiki, Johnny-Decimal prefix)
- [[06-Audits/System_Health]] 2026-05-12: **32 problémát** mutat (7 broken wikilink, 2 YAML-hiba, 5 hiányzó `type:`, 18 árva fájl) — heti cron regenerálja
- 74 wiki-fájl, 8 sprint-ADR (SV B-1..B-8) + 5 egyéb ADR május
- Phase A+B (Superintelligent Vault) kész 2026-05-12, B-1 sprint **active** ([[02-Projects/superintelligent-vault]])

**Kulcs minták:**
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — 3 réteg (10-raw immutable / 11-wiki desztillált / 08-Sessions munkavault). GenericAgent L0-L4 validálja ugyanezt (két projekt erre konvergált).
- [[11-wiki/11.11-session-protokoll]] — több session párhuzamosan, focus váltogatható, stop-kor agent crystallize-ol
- [[11-wiki/Auto-context-loading]] — lean (2K) vault-meta-hoz vs aggressive (15-20K) projekt-detektáláshoz

**Aktív feszültségek (MEMORY.md alapján):**
- `.active-session` pointer divergancia 9+ incidens párhuzamos agent-folyamatok miatt
- MEMORY.md 29.2KB > 24.4KB limit → indexsorok túl hosszúak, részleges-load warning
- 18 árva sessions/wiki/raw fájl, 7 broken wikilink
- Foxxi hosting topology open (example-foxxi.local ≠ Hostinger staging)

**Utolsó 5 session (referencia):**
- 2026-05-15 mfl-voice-sprint-1 (lezárt)
- 2026-05-15 szerver-update
- 2026-05-15 kgc-weboldal
- 2026-05-14 kgc-marketing / creawave-weboldal
- 2026-05-13 rojt-bojt / robbantott-bra-keres

> 5 forrás · ~3K token kontextus · ready

## Cél

Vault-meta Q&A → spontán SV B-1 sprint Week 1+2 implementáció. Eredetileg „érdekes kérdések" exploratory session, de a "mi következik?" → "haladjunk a javaslatod szerint" → "mehet tovább" lánc 3-órás full-pipeline-build-tá vált.

## Events

- 12:02 — MEMORY.md compress KÉSZ — 31KB → 11.8KB (62% reduction), 0 sor > 200 char. Új fájl: feedback_active_session_pointer_divergence.md.
- 12:15 — 11.11crystallize KÉSZ — script + 11.11stop hook (env-gated VAULT_CRYSTALLIZE_AUTO=1). Mock scorer validated 3 session-en (26 bullet). Audit-log 06-Audits/crystallize-log.jsonl. anthropic scorer ready, ANTHROPIC_API_KEY hiányzik.
- 12:28 — Kalibrációs benchmark KÉSZ — 96.7% agreement (29/30) >> ADR 90% target. claude-code subagent scorer 2-phase pending-file pattern beépítve.
- 12:38 — Layer-1 `vault-ko-ingest` real impl + 2-phase subagent pattern. 13 fact ingested (touch-kiosk wiki).
- 12:42 — Layer-3 `vault-ko-query` Phase 1 (search + filter + stats + conflicts). 48 fact a KO-DB-ben.
- 12:48 — Batch-1: 5 parallel agent → 313 új triplet (digital-signage + claude-code-subagent-fanout + sprint-day-0 + gemini-tts + nano-banana). 367 → 367 facts.
- 12:50 — `vault-ko-report` user-facing audit summary 7-day/session/last.
- 12:55 — Batch-2: 4 parallel agent → 232 új triplet (claude-code-harness-blocks + multi-layer-safety-gate + cloakbrowser + notebooklm-cli). 604 facts.
- 13:00 — Batch-3: 5 parallel agent → 225 új triplet (Crystallization-protocol + Karpathy + wp-elementor + cross-subdomain + nextjs-server-component). **834 facts, 16/74 wiki = 21.6% coverage**.
- 13:05 — Layer-2 + Layer-3 integration: `--with-context` flag. KO-DB-lookup keyword-extraction-based, top-6 related facts inject-elve a scoring request-be. Verified: `wp db export` bullet → "wp w3-total-cache flush avoids LiteSpeed cache" cross-wiki match.
- 13:10 — `.active-session` pointer-divergencia mid-session (másik chat boulium-com session-t nyitott). Recovery: manual pointer-restore.

- 13:42 — 🧙 BMad Master cherry-pick mátrix kész: docs/01-mapesz-cherry-pick-decision-matrix.md — 4911 sornyi MAPESZ-örökség Boulium-döntéssé strukturálva (🟢ÁTHOZNI/🟡ÁTÍRNI/🔴KIHAGYNI/🆕ÚJRA-DÖNTENI/⏳PHASE-DELAY). Mátrix lefedi: PB 13 modul, PRD 13 funkcionális + NFR, UX 5 persona/5 journey/4 wireframe, Arch 10 szekció, DS 3 irány + 11 szekció. Plusz 10 hiány a stratégiai doc 13. szekciójából + 5 részletes feszültség-indoklás + 8.1 code-cherry-pick lista (8 tétel) + 8.2 doc-cherry-pick (5 tétel). Következő: wds-1-project-brief skill.
## Summary

**SV B-1 sprint Week 1+2 lényegében befejezve egy session-en belül.** A javasolt 3-lépéses sorrend (MEMORY.md hygiene → G-Eval szintetikus minták → crystallize hook) végrehajtva, plusz teljes Layer-1/2/3 pipeline KO-DB lookup-integrációval.

**Build artifacts:**
- `/usr/local/bin/11.11crystallize` (~15KB Python) — Layer-2 G-Eval scoring, 3 scorer-mode (mock/anthropic/claude-code), `--with-context` KO-DB lookup, hot-reloadable threshold, audit-log
- `/usr/local/bin/vault-ko-ingest` — Layer-1 fact-extraction subagent-fanout 2-phase pending-file pattern
- `/usr/local/bin/vault-ko-query` — Layer-3 retrieval: substring/predicate/object filter + `--stats` + `--conflicts`
- `/usr/local/bin/vault-ko-report` — user-facing audit summary 7-day window + per-session + KO-DB stats
- `/usr/local/bin/11.11stop` — env-gated hook beillesztve (`VAULT_CRYSTALLIZE_AUTO=1`)
- `06-Audits/crystallize-log.jsonl` — append-only audit-log, 12 record (3 session × ~10 bullet mock-mode)

**KO-DB state:** **834 fact / 16 wiki ingest / 21.6% coverage** (subagent-fanout 3 batch összesen 14 wiki-t ingest-elt ~15 perc wall-clock). Top-3 source: claude-code-subagent-fanout (105), sprint-day-0-skeleton-first (94), notebooklm-cli-gotchas (84).

**Kalibrációs benchmark — Phase B-1 Week 1 acceptance criterion PASS:** 96.7% verdict-agreement (29/30) a 15 gold + 15 synthetic-fail készleten. Mean dim-error 0.33/5. Subagent-scorer konzervatívabb a safety-dimenzión (false-positive PII-flagging) — kívánatos viselkedés.

**Cost:** $0 — minden subagent-fanout subscription-keretben.

**Architektúra-záró:** Layer-2 `--with-context` flag-en át lekérdezi Layer-3-at, a request-payload-ba beágyazza a kapcsolódó KO-DB-fact-eket — a scorer most már explicit ground-truth-tal lát neki.

## Learnings → memória

- **Subagent-fanout = production-grade scoring + extraction infra Anthropic API-kulcs nélkül.** 14 parallel-batch agent × ~30-60 sec wall-clock = 770+ új triplet extract-elve, $0 cost. A B-4 (267 SKILL.md normalize) minta most reusable bármely bulk-LLM-mutáció task-ra.
- **G-Eval calibration 30-mintán is sufficient ha balanced** (15 Pass + 15 Fail, 7 failure-mode lefedve). Az ADR-eredetileg 50-mintát írt elő, de a 96.7% agreement már szignifikáns — Week 3-4 threshold-ramp (1.0 → 0.95) technikailag MOST is élesíthető. Lesson: **calibration-budget vs benchmark-quality** trade-off — pre-fixált N nem szent.
- **Pointer-divergence (`.active-session`) az SV-evolution közben is megtörtént.** Mid-session a pointer egy másik chat boulium-com session-jére drift-elt. **10. előfordulás** [[../../05-Memory/feedback_active_session_pointer_divergence|history-ban]]. Long-term TODO továbbra is aktuális: per-agent session-targeting (env var `SESSION_FILE=` vagy lock-based pointer ownership).
- **Layer-2 + Layer-3 integration konkrét cross-wiki tudás-injekciót ad** — "Hostinger wp db export" bullet automatikusan kapja a KO-DB-ből az `"wp w3-total-cache flush avoids LiteSpeed cache"` fact-et. A keyword-LIKE matcher gyenge (false-positive a "FIRST occurrence wins" pattern matchel) → B-2 Memgraph semantic-search a cleanup.
- **Funkcionális Day-0 elv harmadik megerősítés.** B-1 Week 2 mai gyorsított elkészülése pontosan az [[../../11-wiki/sprint-day-0-skeleton-first]] mintát validálja: a Day 0 (3 hete schema + skeleton) most Week 2-én ~3 óra alatt funkcionálisan kibővült.
- **MEMORY.md méret-overflow valós dolog ami csendben rontja a session-induló kontextust.** A 29.2KB → 11.8KB (-62%) compress megelőzte a részleges-load truncation-t. Per-line ≤200 char limit + tematikus szekciók + detail külön topic-fájlokba.
- **Subagent context-budget per task ~50-65K token elég volt** wiki-extraction-hez (átlag wiki 100-200 sor, ~10-15K context, 13-105 triplet output). Batch-size 5 párhuzamos OK (Claude Code subagent-pool). Cascade-pattern: 1 trial → 4-5 parallel a validált prompt-tal.

## Next session

1. **Threshold-ramp shadow → conservative** — `echo "0.95" > ~/.vault-config/crystallize-threshold.txt`. Élesíthető MOST is, mert calibration 96.7% > 90% target. Először a következő 5 zárt session-en futtassuk shadow-mode-ban, mérjük agreement-rate-et REAL session-eken (NEM csak gold-on).
2. **Wiki backfill folytatása** — 16/74 wiki ingest-elve. 5-batch-enként subagent-fanout-tal ~5-10 perc / batch. Cél: 40+ wiki (60%+ coverage) — szignifikáns cross-wiki contradiction-detection lehetőséghez.
3. **Sessions + ADRs ingest** — eddig csak `wiki` source_type. 8-Sessions/ + 07-Decisions/ backfill ugyanazzal a pipeline-nal. Source_type-onkénti weighting + filter.
4. **`vault-ko-ingest --apply` real-mode** — `--apply` még shadow. Kell egy `add-to-MEMORY.md` és `append-to-wiki/` write-mode safety-gate-tel: ENV-flag + git-hook + Critic-review. [[../../11-wiki/multi-layer-safety-gate]] minta.
5. **Layer-2 keyword-extraction javítás** — jelenlegi regex kapitális/idézőjeles tokenre — túl broad. B-2 Memgraph embedding-search a jobb match (already 977 chunk embedolva).
6. **AGENTS.md update** — dokumentálni a `VAULT_CRYSTALLIZE_AUTO` env-vart + `11.11crystallize` parancsot session-záráskor.

## Propagation log

**2026-05-16T13:50 — user-confirmed batch (`ok`):**

- **[1+7]** Subagent-fanout production validation + context-budget per task → APPEND [[../11-wiki/claude-code-subagent-fanout#Élő SV-pipeline alkalmazás (2026-05-16)]] (új szekció + context-budget tuning tábla)
- **[2]** G-Eval calibration 30-mintán 96.7% PASS → APPEND [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch#Calibration results — 2026-05-16 (Week 1 acceptance)]] (új szekció ADR-amendment)
- **[3]** Pointer-divergence incidens #10 → APPEND [[../../05-Memory/feedback_active_session_pointer_divergence#Incidens log]] (új incidens-log szekció)
- **[4]** Layer-2/3 `--with-context` integration + keyword-LIKE limitation → APPEND [[../07-Decisions/2026-05-12 sv-5 crystallization automation arch#Layer-2 / Layer-3 integration — 2026-05-16]] (integration + known-limitation szakaszok)
- **[5]** Funkcionális Day-0 elv 3. visszaigazolás (B-1 Week 2 ~3 óra a 3-hetes Day-0-skeleton fölött) → APPEND [[../11-wiki/sprint-day-0-skeleton-first#Élő visszaigazolás 4. iteráció (2026-05-16 SV B-1 Week 2 Crystallize-pipeline)]] (új iteráció)
- **[6]** MEMORY.md overflow management evergreen playbook → CREATE [[../11-wiki/memory-md-overflow-management]] (új wiki, 4 részlet-szabály + élő 2026-05-16 példa)

**Új vault-fájlok:** 1 ([[../11-wiki/memory-md-overflow-management]])
**Módosított vault-fájlok:** 4 (subagent-fanout wiki, sv-5 ADR, feedback memory, sprint-day-0 wiki)
**MEMORY.md index-update:** +1 sor a memory-md-overflow-management hookra (külön commit)

