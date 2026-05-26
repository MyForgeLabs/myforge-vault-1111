---
name: Audits index
type: index
tags: ["#type/index", "#type/audit"]
created: 2026-04-23
updated: 2026-05-19
tag_backfill: 2026-05-19
---
# Audits

Pillanatkép-jelentések a teljes vault-stack + SV-meta sprint-ekről. Minden audit önmagában teljes, nem élő dokumentum (nem frissítjük utólag) — kivéve a `System_Health.md` ami heti cron-nal regenerálódik.

> **Snapshot:** 71 audit-MD jelenleg.

## Élő audit-ok

- [[System_Health]] — heti `vault-cleanup` regenerálja (vasárnap 04:00). Vault-integritás, broken wikilinks, hiányzó frontmatter, orphan fájlok.
- [[Eval_Trend]] — B-3 continuous evaluation szöveg-trend (LLM-output minőség heti rolling).
- [[crystallize-health]] — B-1 crystallize-monitor heti JSON (`*/30 * * * *` cron + Sunday 04:35 ramp-recommendation).
- [[shadow-monitoring-trend]] — NLI L2.5 + Coherence L2.6 shadow-data heti rolling.
- [[broken-wikilinks-latest]] — daily broken-link audit (cél: 0).

## Audit-archívum (dátum szerint)

| Dátum | Audit | |
|-------|-------|--|
| – | [[skill-distill-candidates-2026-05-17]] | |
| – | [[skill-canonicalize-baseline-2026-05-17]] | |
| – | [[cross-source-conflicts-2026-W20]] | |
| 2026-05-18 | [[2026-05-18 wiki cross-link enrich\|wiki cross-link enrich]] | |
| 2026-05-18 | [[2026-05-18 vault-meta NotebookLM cross-projekt synthesis\|vault-meta NotebookLM cross-projekt synthesis]] | |
| 2026-05-18 | [[2026-05-18 vault-meta NB cross-projekt Q4-Q5\|vault-meta NB cross-projekt Q4-Q5]] | |
| 2026-05-18 | [[2026-05-18 Twitter thread draft (master)\|Twitter thread draft (master)]] | |
| 2026-05-18 | [[2026-05-18 MyForge OS sci-fi mission-control research\|MyForge OS sci-fi mission-control research]] | |
| 2026-05-18 | [[2026-05-18 MyForge OS YouTube design reference research\|MyForge OS YouTube design reference research]] | |
| 2026-05-18 | [[2026-05-18 MyForge OS Wave L1 foundation\|MyForge OS Wave L1 foundation]] | |
| 2026-05-18 | [[2026-05-18 MyForge OS UX audit pre-redesign\|MyForge OS UX audit pre-redesign]] | |
| 2026-05-18 | [[2026-05-18 KGC-4 integráció — research-output Q1..Q7\|KGC-4 integráció — research-output Q1..Q7]] | |
| 2026-05-18 | [[2026-05-18 KGC-4 integráció — architektúra v1\|KGC-4 integráció — architektúra v1]] | |
| 2026-05-18 | [[2026-05-18 KGC-4 frontend integráció — NotebookLM research-terv\|KGC-4 frontend integráció — NotebookLM research-terv]] | |
| 2026-05-18 | [[2026-05-18 KGC-4 ERP v7.0 mélyaudit\|KGC-4 ERP v7.0 mélyaudit]] | |
| 2026-05-18 | [[2026-05-18 HN-post drafts (4 EN wiki)\|HN-post drafts (4 EN wiki)]] | |
| 2026-05-18 | [[2026-05-18 GitHub trending weekly recurrence\|GitHub trending weekly recurrence]] | |
| 2026-05-18 | [[2026-05-18 GitHub trending recurrence + top-10 ingest\|GitHub trending recurrence + top-10 ingest]] | |
| 2026-05-17 | [[2026-05-17 shadow-monitoring extension\|shadow-monitoring extension]] | |
| 2026-05-17 | [[2026-05-17 predicate-vocab expansion 21 to 35-40\|predicate-vocab expansion 21 to 35-40]] | |
| 2026-05-17 | [[2026-05-17 predicate-remap Phase 2 fanout\|predicate-remap Phase 2 fanout]] | |
| 2026-05-17 | [[2026-05-17 persistent NLI-process pool skeleton\|persistent NLI-process pool skeleton]] | |
| 2026-05-17 | [[2026-05-17 cross-projekt synthesis prep\|cross-projekt synthesis prep]] | |
| 2026-05-17 | [[2026-05-17 broken-wikilinks scan\|broken-wikilinks scan]] | |
| 2026-05-17 | [[2026-05-17 bge-reranker score-gap smart-skip\|bge-reranker score-gap smart-skip]] | |
| 2026-05-17 | [[2026-05-17 auto-skill-distill Week 2\|auto-skill-distill Week 2]] | |
| 2026-05-17 | [[2026-05-17 SelfCheckGPT borderline-filter skeleton\|SelfCheckGPT borderline-filter skeleton]] | |
| 2026-05-17 | [[2026-05-17 OmniRoute cascade skeleton\|OmniRoute cascade skeleton]] | |
| 2026-05-17 | [[2026-05-17 Layer 2.6 vault-coherence integration\|Layer 2.6 vault-coherence integration]] | |
| 2026-05-17 | [[2026-05-17 GEPA Week 2 real-loop\|GEPA Week 2 real-loop]] | |
| 2026-05-17 | [[2026-05-17 G-Eval v0.3 30-sample paired kalibráció\|G-Eval v0.3 30-sample paired kalibráció]] | |
| 2026-05-17 | [[2026-05-17 ENV-defaults tracker\|ENV-defaults tracker]] | |
| 2026-05-17 | [[2026-05-17 ENABLE_TOOL_SEARCH activation\|ENABLE_TOOL_SEARCH activation]] | |
| 2026-05-17 | [[2026-05-17 B-8 GEPA prompt-mutator skeleton\|B-8 GEPA prompt-mutator skeleton]] | |
| 2026-05-17 | [[2026-05-17 B-7 wikilink-importer MENTIONS edges\|B-7 wikilink-importer MENTIONS edges]] | |
| 2026-05-17 | [[2026-05-17 B-7 Week 4 LLM-extraction\|B-7 Week 4 LLM-extraction]] | |
| 2026-05-17 | [[2026-05-17 B-7 Week 3 typed-labels + alias\|B-7 Week 3 typed-labels + alias]] | |
| 2026-05-17 | [[2026-05-17 B-7 Week 2 typed entity-nodes\|B-7 Week 2 typed entity-nodes]] | |
| 2026-05-17 | [[2026-05-17 B-6 Week 1 worker + smoke\|B-6 Week 1 worker + smoke]] | |
| 2026-05-17 | [[2026-05-17 B-5 vault-meta notebook hook\|B-5 vault-meta notebook hook]] | |
| 2026-05-17 | [[2026-05-17 B-5 notebooklm per-project bootstrap\|B-5 notebooklm per-project bootstrap]] | |
| 2026-05-17 | [[2026-05-17 B-5 Week 2 nb-crystallize integration\|B-5 Week 2 nb-crystallize integration]] | |
| 2026-05-17 | [[2026-05-17 B-4 auto-skill distillation skeleton\|B-4 auto-skill distillation skeleton]] | |
| 2026-05-17 | [[2026-05-17 B-4 Week 3 vault-search-server SkillChunk RPC\|B-4 Week 3 vault-search-server SkillChunk RPC]] | |
| 2026-05-17 | [[2026-05-17 B-4 Week 2 skill-embedding + search\|B-4 Week 2 skill-embedding + search]] | |
| 2026-05-17 | [[2026-05-17 B-3 vault-coherence-drift check\|B-3 vault-coherence-drift check]] | |
| 2026-05-17 | [[2026-05-17 B-3 session eval frontmatter\|B-3 session eval frontmatter]] | |
| 2026-05-17 | [[2026-05-17 B-3 Week 2 L2 NLI-judge\|B-3 Week 2 L2 NLI-judge]] | |
| 2026-05-17 | [[2026-05-17 B-3 L1 stuck-detection\|B-3 L1 stuck-detection]] | |
| 2026-05-17 | [[2026-05-17 B-2 reranker smart-trigger\|B-2 reranker smart-trigger]] | |
| 2026-05-17 | [[2026-05-17 B-2 native vector-index migration\|B-2 native vector-index migration]] | |
| 2026-05-17 | [[2026-05-17 B-2 bge-reranker 2-pass retrieval\|B-2 bge-reranker 2-pass retrieval]] | |
| 2026-05-17 | [[2026-05-17 B-2 Week 4 hybrid BM25 + semantic\|B-2 Week 4 hybrid BM25 + semantic]] | |
| 2026-05-17 | [[2026-05-17 B-2 Week 4 bge-reranker-base AB\|B-2 Week 4 bge-reranker-base AB]] | |
| 2026-05-17 | [[2026-05-17 B-2 Week 3 acceptance gate readout\|B-2 Week 3 acceptance gate readout]] | |
| 2026-05-17 | [[2026-05-17 B-1 predicate-remap-legacy phase1\|B-1 predicate-remap-legacy phase1]] | |
| 2026-05-17 | [[2026-05-17 B-1 per-target threshold overrides\|B-1 per-target threshold overrides]] | |
| 2026-05-17 | [[2026-05-17 B-1 NLI Layer 2.5 integration\|B-1 NLI Layer 2.5 integration]] | |
| 2026-05-17 | [[2026-05-17 B-1 G-Eval bias-mitigation v0.3\|B-1 G-Eval bias-mitigation v0.3]] | |
| 2026-05-17 | [[2026-05-17 B-1 Aggressive 0.85 ramp risk-assessment\|B-1 Aggressive 0.85 ramp risk-assessment]] | |
| 2026-05-12 | [[2026-05-12 nonplusz.hu-basic webelemzés\|nonplusz.hu-basic webelemzés]] | |
| 2026-05-12 | [[2026-05-12 himalajaijoga.hu webelemzés\|himalajaijoga.hu webelemzés]] | |
| 2026-05-10 | [[2026-05-10 Foxxi performance audit\|Foxxi performance audit]] | |
| 2026-05-10 | [[2026-05-10 Foxxi email deliverability diagnosis\|Foxxi email deliverability diagnosis]] | |
| 2026-05-10 | [[2026-05-10 Foxxi Google snippet diagnosis\|Foxxi Google snippet diagnosis]] | |
| 2026-05-08 | [[2026-05-08 Vault rendezesi audit\|Vault rendezesi audit]] | |
| 2026-04-23 | [[2026-04-23 Teljes infra audit\|Teljes infra audit]] | |

## Hogy olvasd

- **B-1, B-2, ... B-8** = 8-axis SV sprint-numerica ([[../11-wiki/sv-01-memory-architecture|sv-01]] etc.)
- **GitHub trending recurrence** = heti net-watch top-15 repo aggregálás
- **vault-meta NotebookLM** = cross-projekt NB query Q1-Q5 (63 source)
- **shadow-monitoring** = NLI Layer 2.5 + Coherence Layer 2.6 default-shift watch
- **predicate-remap** = KO-DB has_value/uses dump-arány csökkentés

## Kapcsolódó

- [[../11-wiki/Index|Wiki Index]] — evergreen tudás
- [[../07-Decisions/Index|ADR Index]] — architektúrális döntések
