---
name: Claude Code subagent-fanout playbook
type: wiki
tags: ["#type/wiki", "claude-code", "subagent", "bulk-processing", "playbook"]
created: 2026-05-13
updated: 2026-05-17
status: stable
---

# Claude Code subagent-fanout — bulk-LLM-mutáció $0 cost

A klasszikus „N fájlra LLM-aided mutáció" feladatok (frontmatter normalize, summary-generation, taxonomy-tagging) megoldhatók **Anthropic API kulcs nélkül** Claude Code subagent-fanout-tal: a Claude Code subscription-keretében spawn-olsz N párhuzamos `general-purpose` subagent-et, mind a saját scope-jában LLM-mutál egy fájl-batch-en, majd visszaad egy összegző jelentést.

## Mikor használd

- ✅ **Bulk fájl-mutáció** ami `description` → `tags + trigger_keywords` szerű extraction (per-fájl independent)
- ✅ **Frontmatter normalize** N >100 dokumentumra
- ✅ **Tartalom-summary generálás** N session-fájlra (per-session independent)
- ✅ **Taxonomy-tagging** N article-re
- ❌ **Cross-document reasoning** (egy doc-hoz másikat olvasni kell) — egy agent kell, NEM fanout
- ❌ **State-machine work** (sorrend kötött) — sequential pipeline kell

## Architektúra

```
                        ┌── Agent2 (30 fájl) ──┐
                        ├── Agent3 (30 fájl) ──┤
   You (parent)         ├── Agent4 (30 fájl) ──┤
   ────────────────────►├── ...               ──┤── parallel ───► Aggregate report
                        ├── Agent8 (30 fájl) ──┤
                        └── Agent9 (27 fájl) ──┘
                              all background

   1. Trial: 1 agent × 30 files (validate output quality)
   2. User confirms quality
   3. Parallel: 8 agents × ~30 files each, run_in_background=true
   4. Async notifications → parent aggregates
```

## Batch-size tuning (2026-05-13 SV B-4 mért adatok)

| Batch size | Agent context | Per-agent duration | Cost |
|---|---|---|---|
| 10 fájl | ~30K token | ~30 sec | $0 (subscription) |
| **30 fájl** ⭐ | ~60K token | **~80-100 sec** | $0 (sweet spot) |
| 50 fájl | ~100K token | ~3 min | $0 (még OK) |
| 100 fájl | ~200K token | risk of context-overflow | risk |

**Ökölszabály:** 30 fájl / agent ideális, ~80-100K token kontextus, ~90 sec per-agent. 8-9 agent párhuzamosan max (a Claude Code subagent-pool limitálja).

## Trial → cascade minta (2026-05-13 SV B-4 validálva)

**Mindig** 2-lépéses bevezetés:

### 1. Trial (1 agent × 30 fájl) — quality validation

- **Diverz minta:** stride-N sampling (NEM első-N, hogy ne legyen homogén)
- **Detailed jelentés:** modified/skip/errors + 3-5 reprezentatív output minta
- **User-check:** quality OK? Tag-taxonomy egyezik? Edge-case handling jó?

### 2. Cascade (8 agent × ~30 fájl párhuzamosan) — bulk

- **`run_in_background=true`** mindegyik agent-re
- **Async notifikációk** parent-nek (NotificationToolUse) — agent-completion event-eket parent agg-eli
- **Identikus prompt-template** per-batch (csak a bemenet-fájl-lista változik)

## Cost-elemzés

**Direct API (Haiku 4.5):**
- ~$0.0001-0.0002 / fájl × 267 = ~$0.05-0.10 once
- Plus latency-cost (rate-limit), authentication-setup

**Subagent-fanout (Claude Code subscription):**
- **$0 marginális cost** (subscription-keretben)
- Network/auth-setup nincs (Claude Code internal auth)
- Parallelizable agentek között
- Caveat: a teljes Claude Code subscription cost-ja oszlik el az aktivitások között — heavy use → upgrade-szükséglet

**Rule-of-thumb:** ha <500 fájl + <30 sec/fájl, **subagent-fanout** ; ha >5000 fájl + cron-scheduled rendszeresen, **direct API + key**.

## Pitfall-ok

- **Overlapping work** — két agent NE módosítsa ugyanazt a fájlt. Disjoint batch-fájlok (`/tmp/sv-b4-batch{2..9}-files.txt`)
- **Prompt-drift** — batch-prompt változatok között inkonzisztens output. Megoldás: **identikus prompt-template** mindegyik agent-re, csak a bemenet-fájl változik
- **Backup-mandatory** — minden agent `.bak.20260513` backup-ot készítsen edit előtt; revert-able
- **YAML-validity** — output után batch-szintű validity check (PyYAML safe_load)

## Audit-loop

A parent (Te) minden agent után:
1. Olvasd a jelentését (modified/errors/samples)
2. Random-sample 1-2 fájl direct check
3. Audit-script futtatás (pl. `skill-canonicalize --audit`)
4. Ha minden OK → következő batch / mark-done

## Mikor NE használd — model-loading dominálta workload-ok

A subagent-fanout előnye akkor érvényesül, ha a per-fájl munka **gyors LLM-mutáció** (~30 sec / fájl, főleg context-shaping nem inference). **NEM érdemes** fanout-olni amikor:

| Workload | Per-fájl idő | Fanout-érdemes? |
|---|---|---|
| **Frontmatter normalize** (text-shaping) | ~5-10 sec | ✅ IGEN — 5-8× gyorsulás |
| **Tag/keyword extract from description** | ~3-5 sec | ✅ IGEN |
| **Summary generation** | ~10-15 sec | ✅ IGEN |
| **bge-m3 / sentence-transformers embedding** (CPU) | ~1-2 sec/chunk | ❌ NEM (lásd alább) |
| **CLIP / image embedding** (CPU) | ~3-5 sec/file | ❌ NEM |
| **Whisper transcription** (CPU) | ~10 sec/perc audio | ❌ NEM |

**Miért NEM CPU-inference?** A model-loading egy ~2-3GB modellre (bge-m3, Whisper-large) **~30-60 sec / agent**, plus minden agent saját RAM-példányát loadolja. 8 párhuzamos agent × 2.3GB = 18.4GB RAM összesen + 8× duplikált load-time. Versus: egy serial loop ami egyszer loadol, aztán 267 fájlt feldolgoz.

**Mért adat — SV B-4 2026-05-13:**

| Feladat | Pattern | Wall-clock | Per-fájl |
|---|---|---|---|
| 267 SKILL.md frontmatter normalize | 8 párhuzamos subagent ⭐ | ~5 perc | ~1 sec |
| 267 SKILL.md bge-m3 embed (serial) | 1 process, model 1× load | ~24 perc | ~5.5 sec |
| 267 SKILL.md bge-m3 embed (8 subagent — hipot.) | 8 párhuzamos, 8× model-load | **~12-15 perc** (becsült) | ~3-4 sec |

A fanout itt **legfeljebb 2× gyorsulás** lenne, de **8× RAM-overhead**-del és komplexebb error-handling-gel — ROI **alacsony**. Ezért: bge-m3-szerű CPU-bound feladatra serial.

**Döntési szabály:** ha per-fájl idő >50%-a **model-loading**, NEM fanout. Ha per-fájl idő <20%-a model-loading, fanout 5-8× gyorsulást ad.

## Élő példa — SV B-4 (2026-05-13)

**Feladat:** 267 SKILL.md → `tags` + `trigger_keywords` (frontmatter enrichment)

**Eredmény:**
- 1 trial (30 fájl, stride-9 diverz) → quality OK
- 8 parallel (batch2-9: 30/30/30/30/30/30/30/27) → mind 30/30 success
- **267/267 YAML-valid**, audit 0/534 → 534/534 Compliant
- Total wall-clock: ~5 perc (trial ~90 sec + parallel ~3-4 min)
- Cost: **$0**

Részletek: [[02-Projects/superintelligent-vault]] B-4 sprint + [[08-Sessions/2026-05-13-sv-functional-payoff]].

## Élő SV-pipeline alkalmazás (2026-05-16)

A B-1 sprint Layer-1 wiki-extraction-jén élesben validálódott a minta egy második independens use-case-en (B-4 mellett, ami SKILL.md-normalize volt):

- **14 parallel-batch agent** 3 batch-ben (5 + 4 + 5) ~5-10 perc wall-clock / batch
- **~770+ új triplet** extract-elve 19 wiki-fájlból
- **Cost = $0** (subscription-keretben, NEM Anthropic API)
- **Batch-size 5 párhuzamos OK** — Claude Code subagent-pool nem akadt el
- Cascade-pattern: 1 trial-extraction (touch-kiosk-idle-timeout, 13 triplet) → validált prompt → 4-5 parallel batch a többi wiki-re

### Context-budget tuning per task-típus (2026-05-16-os mérés)

| Task-típus | Per-agent context | Per-agent duration | Per-task output |
|---|---|---|---|
| SKILL.md frontmatter normalize (B-4) | ~80-100K | ~80-100 sec | ~30 fájl mutate |
| Wiki triplet-extraction (B-1) | ~50-65K | ~30-70 sec | 25-105 triplet / wiki |
| G-Eval scoring (B-1 Layer-2) | ~5-15K | ~20-30 sec | 10-15 bullet score |

A **wiki-extraction az egyik legolcsóbb fanout-task** (50-65K context elég, mert csak egy wiki + a rubric kell). Több batch közötti context-overlap szinte nulla — minden agent fresh-load.

## Élő SV-pipeline alkalmazás 4. iteráció (2026-05-17)

**Vault TELJES backfill 1 session-en belül** — minden 11-wiki + 07-Decisions + 08-Sessions ingest-elve KO-DB-be.

| Metrika | Eredmény |
|---|---|
| Subagent-batch wall-clock | ~3 óra total (10 wiki + 5 ADR + 9 session batch) |
| Maximális egyidejű subagent | 8 párhuzamos (validated stable) |
| Total subagent-hívás | 174 |
| Total új triplet | ~12 300 |
| Cost | $0 (subscription-keretben) |
| Fail-rate | 0% |

**Sub-agent context-budget validáció:** 50-66K token / extraction-task elég volt. Hosszabb wiki (sv-research-index 135 triplet output) ~65K-t hozott vissza. Session-extraction-höz a "focus Summary/Learnings/Next, skip Events timestamps" prompt-instrukció elég.

**Cascade-pattern reaffirm 4×:** 1 trial (Auto-context-loading wiki, 80 triplet) → 5 parallel batch → 8 parallel batch. Nem volt szükség progressive ramp-elésre — a 8-as csoport elsőre stabil.

### Source-type-specific prompt-templates

Eltérő `source_type`-okra eltérő minimum-prompt:

| Source | Prompt-fókusz | Min. instrukció |
|---|---|---|
| `wiki` (evergreen pattern) | A teljes szöveg tudásgazdag | "Capture evergreen practical knowledge" |
| `adr` (decision-record) | Decisions + motivations + alternatives | "Focus on Decisions made, Motivations, Constraints, Alternatives; use `decided_at`, `motivated_by`, `alternative_to` predicates" |
| `session` (work log) | Summary + Learnings + Next | "Focus on Summary + Learnings + Next sections (durable outcomes), SKIP ephemeral Events timestamps" |

A `session`-extraction-höz a "skip Events" instrukció kritikus — az Events log-jellegű timestamp-spam-mel borítja a triplet-listát ha nem szűrjük.

## Élő SV-pipeline alkalmazás 5. iteráció (2026-05-17 obsidian-vault session)

**13× subagent-fanout egy turn-ben, 0 ütközés:**
- 1× KO-extraction (obsidian-vault-pro session → 137 triplet)
- 8× tooling-batch (vault-search-server daemon + ko-normalizer + embed-freshness + crystallize-revert + auto-disable + net-watch + memory-monitor + orphan-wiki)
- 2× kiegészítő (diff-aware+backlog + ko-pending CLI)
- 5× sprint kickoff (B-3 L1 baseline + B-4 skill-audit + B-5 nb-crystallize + B-6 worker + B-7 entity-graph)

**Iteráció-tábla ROI-tracking:**

| Iteráció | Dátum | Subagent count | Wall-clock | Cost | Sikerek |
|---|---|---|---|---|---|
| 1 | 2026-05-13 | 8 | ~10 min | $0 | 240 SKILL.md tag-bővítés |
| 2 | 2026-05-15 | 10 | ~15 min | $0 | NotebookLM 17/17 source upload |
| 3 | 2026-05-16 | 15 | ~70 min | $0 | Wiki backfill 25→76 (51 wiki ingest) |
| 4 | 2026-05-17 reggel | 174 (kumulált) | ~3h | $0 | Vault-szintű ingest: 173/173 fájl, 13675 fact |
| **5** | **2026-05-17 este** | **13 (1 turn)** | **~1.5h** | **$0** | **8 új script + 5 sprint kickoff + 2 kiegészítő** |
| **6** | **2026-05-17 (-2)** | **14 (8+6)** | **2h15m** | **$0** | **8 SV-tengely érintve egy sessionben** |
| **7** | **2026-05-17 (-3)** | **13 (4+4+5)** | **~40 min** | **$0** | **18 task LANDED, 2 új SV-tanulság elkapva (time-limit + Task-tool unavailability)** |

**Új tanulság — task-felosztás kötelező a párhuzam-kockázathoz:** ha 2 subagent ugyanazt a fájlt edit-elné (pl. mind a `11.11crystallize`-t bővítené), ütközés lesz — a 8-batch-ben szándékosan más-más fájlt érintő task-okra felosztva (8 új script + független module-ok). Az egyetlen kiegészítő safety: ha közös fájl szükséges, az "fő-thread"-ben kell csinálni, NEM subagent-ben.

### Élő SV-pipeline alkalmazás 6. iteráció (2026-05-17-2)

A `2026-05-17-obsidian-vault-2` session során **8 párhuzamos R1 + 6 párhuzamos R2 = 14 subagent egy session-ben**, mind 8 SV-tengely érintve. 0 ütközés. Wall-clock ~2h15m, $0 cost.

- **R1:** ENABLE_TOOL_SEARCH activation + per-target threshold + wikilink-importer + L1 stuck-detect + session-eval-frontmatter + reranker smart-trigger + GEPA skeleton + auto-skill-distill
- **R2:** NotebookLM-bootstrap + vault-meta hook + NLI Layer 2.5 + vault-coherence-check + G-Eval bias-v0.3 + predicate-remap

**Tanulság:** pool-limit gyakorlatban 8-10 párhuzamos OK; vault-szerkezet (per-axis subagent ↔ per-axis audit-fájl) garantálja a fájl-ütközés-mentességet.

### Élő SV-pipeline alkalmazás 7. iteráció (2026-05-17-3) — két új kockázat-tanulság

A `2026-05-17-obsidian-vault-3` session során **13 párhuzamos subagent egy session-ben** (4 + 4 + 5 batch-eloszlás), 18 task LANDED, $0 cost. 2 új kockázat-tanulság elkapva, ami az előző 6 iterációban nem manifesztálódott:

**Tanulság (a) — time-limit-kockázat heavy-CPU task-ra:** egy bge-m3 embedding-batch subagent (462 SKILL.md, ~2.6GB RSS, 332% CPU) **~16 perc után timeout-olt**. Az encode + Memgraph-merge részfeladat MEGVOLT (462/462 SkillChunk perzisztálva), de az audit-MD-írás + 5-query smoke a parent-session manual-completion-re szorult. **Mitigation:** heavy-CPU task-okat ne adj subagent-nek > 15 perc várt wall-clock-ra, vagy oszdd ketté (batch-1 = encode + perzisztálás, batch-2 = audit + smoke).

**Tanulság (b) — subagent NEM tud további `Task`-tool-t hívni saját maga:** a `predicate-remap Phase 2 fanout` subagent szándékosan 10 sub-subagent-t akart spawn-olni a 3061-fact LLM-classify-ra, de a `Task` tool NEM elérhető subagent-szinten (csak parent). Workaround: **deterministic regex/keyword stand-in classifier** futott helyette → konzervatív remap-arány (285 fact vs várt ~1500-2000). **Mitigation:** ha a feladatot subagent-nek delegálod, és AZ ÚJABB fanout-ot akarna spawn-olni — végezd a parent-session-ben két lépcsőben (Phase-prepare-ben kibont batches → parent spawn N subagent → Phase-collect-ben aggregálás), NEM single-subagent-feladatként.

**Pool-limit konfirmáció:** 13 párh subagent egy turn-ben sikeres, 0 deadlock. A korábbi pool-limit becslés (8-10) felfelé bővíthető **~13 párh-ra** ha a task-ok független mappákban dolgoznak. Magasabb pool (15+) NEM volt tesztelve még.

## Kapcsolódó

- [[11-wiki/sprint-day-0-skeleton-first]] — komplementer playbook (Day 0 skeleton scaffold)
- [[11-wiki/multi-layer-safety-gate]] — high-risk fanout-hoz (RSI / auto-mutate)
- [[02-Projects/superintelligent-vault]] — B-4 + B-6 sprintek mind subagent-fanout-ra építenek
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[vnc-stack-systemd-reboot-survival]] (sem-rokon, score=0.54)
