---
name: 2026-05-19 SV new development ideas brainstorm
type: audit
status: brainstorm
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "brainstorm"]
related:
  - "[[../02-Projects/superintelligent-vault]]"
---

# SV new development ideas brainstorm

> Brainstorm-jellegű audit: **22 új fejlesztési ötlet** ami NEM szerepel a B-1/B-2/B-3/B-8/GEPA/LongMemEval backlogban. A cél: capability-gap-ek, 2026-os emerging patternek, daily-use friction, synergy a meglévő komponensek között, és külső adat-bridge-ek.

## Idea-track status (2026-05-19 PM final)

**Legend:** ✅ LANDED · 🟡 SKELETON · 🔴 DEFERRED

| # | Idea | Status | Shipped as |
|---:|---|:---:|---|
| 1 | RAGAS/DeepEval CI-gate | ✅ LANDED | `vault-eval-ci` skeleton + LongMemEval-S harness |
| 2 | `vault-explain` retrieval-trace | ✅ LANDED | `vault-explain` (Round 6) |
| 3 | KO-DB freshness-decay | ✅ LANDED | `vault-ko-freshness` (Round 6) |
| 4 | Daily-note `## Yesterday` auto-summarize | ✅ LANDED | `vault-daily-rollup` (Round 6) |
| 5 | KO-DB → Anki/Mochi export | ✅ LANDED | `vault-ko-anki` (Round 6) |
| 6 | ColBERT late-interaction fallback | 🟡 SKELETON | `vault-colbert-fallback` (Round 10, model not downloaded) |
| 7 | Cross-lingual HU↔EN entity-link | 🟡 SKELETON | `vault-entity-link` (Round 9, 0/8913 annotated) |
| 8 | Reverse-lookup provenance UI | ✅ LANDED | `vault-ko-why` (Round 7) |
| 9 | Temporal-KG SCD2 layer | ✅ LANDED | `vault-ko-temporal` + SCD2 fact-versioning hook ACTIVATED (1.0.9) |
| 10 | Predicate-aware schema-evolution | ✅ LANDED | `vault-ko-schema-evolve` (Round 8, 127 predicates audited) |
| 11 | HopRAG multi-hop reasoning | ✅ LANDED | `vault-multi-hop` (Round 9) |
| 12 | Vault-search query-rewrite | ✅ LANDED | `vault-search --explain` (Round 7) |
| 13 | Personal browser-history bridge | ✅ LANDED | `vault-browser-history` (Round 8) |
| 14 | GitHub commit-history bridge | ✅ LANDED | `vault-gh-bridge` (1.0.9 PM) |
| 15 | Sleep-consolidation cron | ✅ LANDED | `vault-sleep-consolidate` + Sleep-Critic stage-2 ACTIVATED (1.0.9) |
| 16 | Letta virtual-context OS layer | 🟡 SKELETON | `vault-core-memory` (Round 9, 996/2048 tokens) |
| 17 | RSI Tier-3 agent-on-agent | 🟡 SKELETON | B-8 RSI Critic skeleton ACTIVATED (1.0.9, safety-gated) |
| 18 | graphify × Memgraph diff-watcher | ✅ LANDED | `vault-graph-diff` (Round 8, Jaccard 0.0070) |
| 19 | NLI × KO-DB × Memgraph triangulation | ✅ LANDED | `vault-triangulate` (Round 7) |
| 20 | Vault-MCP server local-first | ✅ LANDED | `vault-mcp` (Round 3, 7 read-only tools) |
| 21 | KO-DB Bayesian-belief-update | ✅ LANDED | `vault-ko-belief` (Round 8) + hash-refactor UNBLOCKED (1.0.9) |
| 22 | NotebookLM deep-research → KO-DB | ✅ LANDED | `vault-nb-ingest` (Round 7-8) |

**Final tally: 22/22 LANDED or SKELETON (100%)** — 16 LANDED in PM, 6 SKELETON with explicit follow-up gates. No DEFERRED items after 1.0.9.

---

## TL;DR — top-5 highest-value

1. **#9 Temporal-KG SCD2 layer** — KO-DB-be `valid_from/valid_until` + `superseded_by_hash`, "amikor X-et tudtam" típusú lekérdezések, contradiction-history (M, mid-risk)
2. **#1 vault-search ColBERT late-interaction fallback** — bge-m3 dense miss-elő esetén token-level token-grained match (M, mid-risk)
3. **#15 Sleep-consolidation cron** — éjjeli "REM" job ami episodic-okat semantic-té promotálja entropy/conflict trigger alapján (L, mid-risk)
4. **#13 Personal browser-history bridge** — `~/.config/google-chrome/Default/History` SQLite → 10-raw, NLI-pre-filter, $0 (M, low-risk)
5. **#20 Vault-MCP server local-first** — STDIO MCP exposing KO-DB + vault-search + Memgraph, claude.ai web-ui-ról elérhető (M, mid-risk)

---

## Quick Wins (XS-S, low-risk)

### 1. RAGAS/DeepEval CI-gate a B-2 retrieval-en

**Headline:** DeepEval pytest-suite KO-DB és vault-search regression-gate-ként, threshold-ramp dönt.

**What it does:** A LongMemEval-S 67.68%-os Recall@5-öt és a 9/10 PASS rate-et átteszi **DeepEval Pytest-collector**-ba (50+ metric, CI/CD native). Minden `vault-embed --backfill` után automatikusan futna a `pytest tests/retrieval/` és blokkolja a merge-et ha Faithfulness < 0.85 vagy Context-Recall < 0.65. RAGAS-szal párhuzamos reference-free baseline.

**Why now:** 2026-ra a RAGAS+DeepEval+TruLens hármas a de-facto RAG-eval-stack, és a B-2 sprint-done óta nincs CI gate — minden regresszió csak ad-hoc 30-sample manual probe-ban derül ki. A `vault-crystallize-monitor` van, de retrieval-side nincs.

**Effort:** S. **Risk:** low. **Depends on:** vault-search daemon, LongMemEval-S harness, GitHub Actions.

Sources: [RAGAS, TruLens, DeepEval (Atlan 2026)](https://atlan.com/know/llm-evaluation-frameworks-compared/)

---

### 2. `vault-explain` — minden answer egy retrieval-trace-szel

**Headline:** Vault-query mellé generálj human-readable explain-graph-ot mely chunk/entitás/edge járult hozzá.

**What it does:** Új CLI `vault-explain "<query>"` ami a vault-search retrieval után visszaadja a top-K chunk + a Memgraph-ban érintett node-okat + a KO-DB triplet-eket amelyek cross-source-corroborate-ot adtak. Kimenete Mermaid-diagram + ranked-bullet-list "miért ez a chunk".

**Why now:** A user 4 retrieval-rétegen át (BM25+dense+rerank+KO-DB) ad választ, de nincs introspection — debug-elhetetlen miért bukik egy konkrét query. 2026-os GraphRAG-konszenzus szerint **traceability == production-ready**.

**Effort:** S. **Risk:** low. **Depends on:** vault-search, Memgraph, KO-DB.

Sources: [Graph RAG practitioner guide 2026](https://medium.com/graph-praxis/graph-rag-in-2026-a-practitioners-guide-to-what-actually-works-dca4962e7517)

---

### 3. KO-DB freshness-decay score predicate-szinten

**Headline:** Triplet-ek bizalmi-súlya csökkenjen időben, predicate-specifikus half-life-fal.

**What it does:** Új oszlop `confidence_decayed = base_confidence * exp(-Δt / half_life[predicate])`. `is_a` predicate-ek half-life=∞ (perzisztens), `currently_working_on` predicate half-life=7 nap, `status` half-life=30 nap. A `--top-k` rangsorban a decayed-confidence dominál.

**Why now:** A user vault-jában **idő-szenzitív tényállítások keverednek** ("currently working on B-2") és evergreen-tudás ("KGC-4 = NestJS+Prisma"). A heat-classifier már predicate-aware, ez a természetes következő lépés.

**Effort:** S. **Risk:** low. **Depends on:** KO-DB, predicate-heat-classifier.

---

### 4. Daily-note auto-summarize `## Yesterday` blokk

**Headline:** Minden Daily-note tetejére generált 5-bullet rekap a tegnapi session-ökből + `propagation log` diff.

**What it does:** `daily-rollup` cron (06:00) bge-m3+rerank-kel összegyűjti az előző nap `08-Sessions/*.md` `## Events` + `## Learnings` szakaszait → 5-pont, ADR-link és wiki-link aware. Beleszúrja a `01-Daily/YYYY-MM-DD.md` tetejére `## Yesterday` callout-ként.

**Why now:** 14 SV-meta session után **a daily-note félárván áll** — 27 daily, viszont nincs sequential narrative. Onboarding/recall-time MASSZÍV gyors-win.

**Effort:** S. **Risk:** low. **Depends on:** vault-search, subagent-fanout, daily-template.

---

### 5. KO-DB → Anki/Mochi spaced-repetition export

**Headline:** Magas-confidence evergreen-triplet-ek `cloze deletion` Anki-deck-ként.

**What it does:** `vault-ko-export --anki --predicate is_a,defined_as,solves --min-confidence 0.9` → `.apkg` file. Naponta-heti újra-generál. A cloze a subject+predicate-ből, az object kiderítendő ("KGC-4 = ?", answer "NestJS + Prisma + PG16").

**Why now:** A user 13800 fact-on ül és **nem tudja aktívan visszaidézni** őket. Az SV mint memóriabank reaktív (lekérdezésre válaszol). Spaced-repetition az **aktív recall** layer — Karpathy-spirit-ben "saját szavakkal megtanulni".

**Effort:** S. **Risk:** low. **Depends on:** KO-DB, predicate-heat-classifier.

---

## Capability Extensions (M, mid-risk)

### 6. ColBERT late-interaction fallback ambiguous query-re

**Headline:** Ha bge-m3 dense-search top-1 cosine < 0.55 (= ambigus), eszkalálj ColBERTv2 token-level late-interaction-re.

**What it does:** A current pipeline: BM25 → bge-m3 dense → rerank → answer. Új lépés: ha top-1 score gyenge ÉS query ≥3 tokent tartalmaz (multi-entity), futtass ColBERT-PyLate-et a top-100 candidate-re. ColBERT token-level match a **named-entity heavy query**-knál és a **code-search** retrieval-nél (~3 LOC-ban) verifikáltan jobb mint single-vector dense.

**Why now:** B-2 hybrid BM25+RRF+dense ÉLES; az "fine-grained token match" gap a vault SOK technikai-jegyzetében (Memgraph cypher, mgclient gotcha) érzékelhető. ECIR 2026 Late-Interaction Workshop és ColBERT-Att paper validálja a hybrid pattern-t. Cold-start cost: pre-compute doc-side token-embedding-eket (~30 min, ~2GB).

**Effort:** M. **Risk:** mid. **Depends on:** vault-search, bge-m3, rerank-trigger.

Sources: [ColBERT and Late Interaction (ML Journey)](https://mljourney.com/colbert-and-late-interaction-retrieval-how-it-works-and-when-to-use-it/), [Late Interaction Workshop ECIR 2026](https://www.lateinteraction.com/)

---

### 7. Cross-lingual HU↔EN entity-link layer

**Headline:** Memgraph-ban `Entity` node-okon `name_hu` + `name_en` + canonical-form, automatikusan extract-elve.

**What it does:** Subagent-fanout job ami minden Entity-re ráfut: "Adj 1 angol és 1 magyar kanonikus formát" (pl. "KGC-4" → en:"KGC-4 ERP system", hu:"KGC-4 vállalatirányítási rendszer"). A vault-search query-rewrite layer-ben hozzákapcsolva: HU query EN-Entity-t is talál és vice-versa.

**Why now:** 71 EN wiki ÉS a Karpathy-essay (3896 szó) közönsége fele EN — viszont a search-index egynyelvű chunk-on dolgozik. bge-m3 multilingual embedding-je elnyom néhány gap-et, de **named-entity disambiguation cross-lingually** (pl. "MAPESZ" en:"Hungarian Petanque Federation") komplett hiányzik. Hungarian-Webcorpus-2.0 (9B szavas) tokenizer-adat segíthet.

**Effort:** M. **Risk:** mid. **Depends on:** Memgraph entity-typing, subagent-fanout.

Sources: [Awesome Hungarian NLP (oroszgy)](https://github.com/oroszgy/awesome-hungarian-nlp), [Hungarian embedding interpretability](http://publicatio.bibl.u-szeged.hu/15460/1/main.pdf)

---

### 8. Reverse-lookup: "miért tudom ezt" entity-provenance UI

**Headline:** Memgraph `Entity`-n jobb-klikk → "Mikor és milyen forrásból került be?"

**What it does:** Minden Entity / triplet-extract már most carry-eli az `extracted_from_session` field-et — viszont nincs UI. mkdocs site-on JS-injection (mkdocs-material instant-loader-compatible): hover-card minden `[[02-Projects/..]]` wikilink-en lévő entity-pop-up = "first-seen: 2026-05-08 daily, last-seen: 2026-05-19 session, related-ADR: …". Memgraph Cypher `MATCH (e:Entity)-[:MENTIONED_IN]->(s:Session) RETURN s ORDER BY s.date DESC LIMIT 5`.

**Why now:** A vault **memóriaként** szerepel, de a "honnan tanultam meg X-et" lekérdezés ma `grep -r` — pedig az adat ott van Memgraph-ban. Karpathy-pattern: provenance = trust.

**Effort:** M. **Risk:** mid. **Depends on:** Memgraph, mkdocs-material build.

---

### 9. Temporal-KG SCD2 layer (Slowly-Changing-Dimensions Type 2)

**Headline:** KO-DB triplet-ekre `valid_from` / `valid_until` / `superseded_by_hash` (SCD2 pattern), historical-fact retrieval.

**What it does:** Új tábla `kodb_facts_history` ami minden contradiction-re NEM felülír, hanem új sort tesz be `valid_until = now()` flag-gel az előzőn. A `vault-ko-query --as-of 2026-04-15` time-travel query. T-GRAG / TG-RAG / STAR-RAG pattern integráció: a contradiction-detector-output (heti cron) FELES adatpárból ELŐ-UTÓ snapshot-tá konvertálódik. "Akkor még azt hittem, hogy a example-foxxi.local Hostinger LiteSpeed-en van" → 2026-05-10 superseded → "valójában Apache".

**Why now:** A vault **38 ellentmondás-pár** body-jában van predicate-heat-classifier-output; ezeket ma "fact-revoke" módon kezeljük. A 2025 dec ICLR T-GRAG + STAR-RAG papers verifikálták hogy a temporal-aware-graph 18-25%-kal jobb evolving-knowledge-domain-eken. Direct fit a session-based vault-evolution-höz.

**Effort:** M-L. **Risk:** mid. **Depends on:** KO-DB schema, conflict-audit cron.

Sources: [Temporal Graph RAG (Medium Feb 2026)](https://medium.com/@nitishkumarnitc/temporal-graph-rag-why-time-aware-knowledge-graphs-are-reshaping-ai-memory-04fc62dd0acd), [T-GRAG (arxiv 2508.01680)](https://arxiv.org/abs/2508.01680), [STAR-RAG (arxiv 2510.13590)](https://arxiv.org/abs/2510.13590)

---

### 10. Predicate-aware schema-evolution suggester

**Headline:** Subagent-job heti-cron-on néz: van-e új predicate ami threshold (5+) felett "free-text" formában fordul elő → javasol új kanonikus predicate-et.

**What it does:** `vault-ko-query --stats --ungrouped` listázza a low-frequency predicate-eket (`is_currently_blocked_by`, `was_inspired_by` stb. — most ad-hoc string-ek a triplet-extract-ben). Subagent javaslatot ad: "Promotáld `blocked_by`-ra (12 előfordulás), `inspired_by`-ra (7 előfordulás)". User-confirm után a heat-classifier-config-ba kerül + retro-rewrite SQL UPDATE.

**Why now:** A KO-DB **schema organic-an nő** — most ~80 predicate, de soha nem volt audit hogy melyek redundánsak. Free-text predicate-explosion long-term anti-pattern (heat-classifier zajos lesz).

**Effort:** M. **Risk:** mid. **Depends on:** KO-DB, predicate-heat-classifier, subagent-fanout.

---

### 11. Graph-walk multi-hop reasoning HopRAG-stílusban

**Headline:** Vault-search opció `--multi-hop N` — Memgraph-on N-hop BFS-szel találjon közvetett kapcsolatokat.

**What it does:** Jelenleg single-hop entity → chunk retrieval. HopRAG-stílusú multi-hop: "Miért lett Boulium-ban Better Auth a NextAuth helyett?" → entity-link "Better Auth" → :RELATED_TO → "NextAuth v5 maintenance-mode" → :MENTIONED_IN → wiki-article. 2-3 hop-on belül elérhető a teljes ok-okozati lánc. HopRAG paper +3% mérve HippoRAG-felett a logical-reasoning task-okon.

**Why now:** Memgraph 24K edge, 100% typed, 3431 :LINKS_TO. A graph-density elérte azt a kritikus tömeget ahol a multi-hop BFS értelmes signal-t ad (volt: érted < 5K edge esetén dominálta a hub-spam).

**Effort:** M. **Risk:** mid. **Depends on:** Memgraph typed edges, vault-search.

Sources: [HopRAG (arxiv 2502.12442)](https://arxiv.org/abs/2502.12442)

---

### 12. Vault-search "explain query" → query-rewrite suggester

**Headline:** Ha vault-search 0 hit-et ad VAGY top-1 score < 0.4, agent reformulálja a query-t és újra próbálja.

**What it does:** Subagent ami a failed query-t megnézi és HyDE-pattern-ben (Hypothetical Document Embedding) ír egy 2-mondatos paragraph-ot ami valószínűleg matchel — azt embed-eli újra. Plus: synonym-expansion (cross-lingual Entity-link, #7-tel összeköthető). Pl. "petanque versenykezelés" → bővítés "MAPESZ NSR API competition management Hungarian Petanque Federation".

**Why now:** Vault-search jelenleg cold-state "ha nem találja, kuss". A user gyakran kéri 2-3-szor át a query-t. HyDE pattern ICLR-óta dominans 0-shot retrieval helyzeteknél.

**Effort:** M. **Risk:** mid. **Depends on:** vault-search daemon, subagent-fanout.

---

## Big Bets (L-XL)

### 13. Personal browser-history bridge → 10-raw

**Headline:** `~/.config/google-chrome/Default/History` SQLite-ot heti-cron ingest-eli, NLI-pre-filter, vault-raw-ra.

**What it does:** Cron `browser-history-ingest`: olvassa Chrome/Firefox `History` SQLite-ot, filter-eli (no localhost / no private-tab / >30s dwell-time / domain-allowlist). NLI Layer 2.5 pre-filter: "Ez technical/learning content?" → ha yes, firecrawl → `10-raw/browse/YYYY-MM-DD-<domain>-<slug>.md`. KO-DB extract subagent-fanout-ban. **Local-only, NEM cloud.**

**Why now:** TraceMind és Trail-app 2026-os product-hunt-trend; a user már most NotebookLM-mel research-el (browser-tabok dominálnak), viszont semmilyen capture nincs. **0 friction**: már böngész = már történik az adat-gen. Cross-source-corroboration boost: KO-DB-ben "X = Y" eddig 1-source, browse-bejövő után 2-3-source confidence-bump.

**Effort:** L. **Risk:** mid (privacy: csak local-host, kategória-filter erős). **Depends on:** firecrawl, KO-DB ingest, NLI Layer 2.5.

Sources: [TraceMind blog](https://tracemind.app/blog/your-browser-history-is-a-goldmine-building-a-personal-knowledge-graph), [Trail Product Hunt](https://www.producthunt.com/products/trail-visualize-your-chrome-browsing)

---

### 14. GitHub commit-history + Linear-issue bridge (per-projekt)

**Headline:** Minden `02-Projects/<slug>.md` mellé auto-ingest a kapcsolódó GitHub repo commit-log + Linear/GitHub issue.

**What it does:** Per-projekt `gh-bridge.yaml`-ban tárolt repo-list (boulium, KGC-4, robbantott-kereso, …) → cron `gh-history-ingest` 24h-onta lehúzza az `git log --since="24h"` + PR-leírások + closed-issue-bodies. KO-DB triplet-extract: "commit-X solved issue-Y", "feature-Z merged on date-W". Cross-link Memgraph-on: `Project --[:HAS_COMMIT]--> Commit --[:SOLVED]--> Issue`. Boulium 60+ commit/hét × 12 projekt nagy signal-pool.

**Why now:** A vault **decision-log van, code-log nincs** — minden ADR a "miért" oldal, a "mit csináltunk" eltűnik. Reverse-engineering 1 hónap múlva fáj. GitHub MCP server in-place, gh CLI authentikálva, prod-data van. Linear opcionális (user-pref alapján).

**Effort:** L. **Risk:** low (read-only). **Depends on:** gh CLI, KO-DB ingest, subagent-fanout, Memgraph schema.

---

### 15. Sleep-consolidation cron (Active Dreaming Memory pattern)

**Headline:** Éjjeli "REM-phase" job — episodic session-jegyzetek → semantic wiki-promóció entropy/conflict-trigger alapján.

**What it does:** `crystallize-sleep-consolidation` cron (03:00 napi): néz minden 7-napnál régebbi `08-Sessions/*.md` `## Learnings` bullet-et. Ha entropy magas (sokszor előjön DIFFERENT-session-ökben, vagy contradiction-ed-másikkal) → auto-promote 11-wiki/-be Constitutional-AI Critic-review-val. Sleep-Consolidated-Memory (SCM) paper konkrét architektúra-blueprint: working-mem (recent sessions) → long-term graph storage (wiki + KO-DB) SleepCycle-trigger-rel. Active Dreaming Memory (ADM) 83% accuracy 6-domain-en.

**Why now:** A B-1 crystallization **manuális** (session-end agent + user-confirm). A vault-méret nőtt 251 wiki-ig — minden bullet-et kézzel review-zni nem skálázódik. Sleep-pattern ~5% auto-promotion-arányt javasol; a user-confirm-budget így megmarad a "fontos" 5%-ra.

**Effort:** L-XL. **Risk:** mid (false-promote = wiki-noise; mitigálva CAI-Critic-review + revert-funkcióval). **Depends on:** crystallize-pipeline, predicate-heat-classifier, Constitutional-AI skeleton (B-8 W2-real-LLM).

Sources: [SCM paper](https://www.emergentmind.com/papers/2604.20943), [Active Dreaming Memory engrxiv](https://engrxiv.org/preprint/download/5919/9826), [Sleep-Inspired Memory Consolidation (arxiv 2603.14517)](https://arxiv.org/pdf/2603.14517)

---

### 16. Letta-style virtual-context OS layer

**Headline:** A 11.11start auto-context-loading-ot futtasd **OS-style page-fault** lapozással, nem aggressive 15-20K pre-load-dal.

**What it does:** Letta minta (volt MemGPT): "core memory" (~2K token: User-profil + active-project + open-tasks) **mindig** loadolva; "archival memory" (~unlimited): on-demand `archival_search()` tool-call-on át. Mostani aggressive pre-load 15-20K → Letta-style ~3K core + 1-3 archival_search/turn. Részben már megvalósult B-2 lean ~5K loaddal — Letta-pattern szigorúbb formalizmust ad: a core-blokk **mutable** (Glossary, User, Infra), archival **immutable retrieval**.

**Why now:** A 14 SV-meta session után a vault-méret olyan, hogy a 15-20K pre-load context-eviction-t kezd okozni hosszabb session-eknél (>40 turn). Letta GA óta a virtual-context OS-pattern stabil.

**Effort:** L. **Risk:** mid (touch 11.11* scripts). **Depends on:** 11.11-session-protokoll, vault-search.

Sources: [Best AI Agent Memory Systems 2026 (Vectorize)](https://vectorize.io/articles/best-ai-agent-memory-systems), [Mem0 / Letta architecture](https://machinelearningmastery.com/the-6-best-ai-agent-memory-frameworks-you-should-try-in-2026/)

---

### 17. RSI Tier-3 — agent-on-agent meta-policy learner

**Headline:** Layer Constitutional-AI (Tier-2) FÖLÉ meta-rule-learner: új rule-okat MAGÁTÓL javasol Pareto-front-on.

**What it does:** Heti-batch ami megnézi: melyik B-8 rule fired-be-vain (false-positive) vs. melyik blokkolta a kárt (true-positive). GEPA reflection-LM (már megvan!) **a rule-set-en** futtatva: "Tegyél hozzá rule-t / módosítsd a wording-et". Pareto: precision vs. recall vs. user-friction. New rules user-veto-val mennek live-ba. Metacognitive-self-improvement paper (MARS) ad pattern-t — "principle-based + procedural reflection" duals.

**Why now:** B-8 RSI Tier-2 skeleton ÉLES, GEPA Tier-1 ÉLES, de SOHA nem találkoznak. Tier-3 = rule-discovery az evolution-loop hiányzó középső köve. Cost mostani $0-os subagent-fanout-tal nullához konvergál.

**Effort:** XL. **Risk:** high (recursive self-mod). **Depends on:** B-8 skeleton, GEPA pipeline, --apply blocked default.

Sources: [Meta-cognitive Reflection (arxiv 2601.11974)](https://arxiv.org/pdf/2601.11974), [Intrinsic Metacognitive Learning (arxiv 2506.05109)](https://arxiv.org/pdf/2506.05109)

---

## Synergy Plays

### 18. graphify × Memgraph diff-watcher

**Headline:** Heti cron: graphify (Tier-2 deterministic Leiden) re-run + diff a Memgraph LLM-extracted (Tier-1) gráffal.

**What it does:** `graphify-diff` ami detektálja:
- **Tier-1 says X, Tier-2 doesn't see X** → potential LLM-hallucinated entity, review
- **Tier-2 sees X (community-detected), Tier-1 doesn't have X** → potential coverage gap, ingest

A 5846 graphify-node vs. 8997 Memgraph-entity közti delta (~3k) "ami csak az egyikben van" listája hetente egy audit-MD-be megy. Két különböző extraction-methodology cross-validate-eli egymást — "two-tier graph verification" 2026-os emerging pattern.

**Why now:** A user már most fenntartja MINDKÉT graph-ot, de soha nem futottak párhuzamosan diff-pattern-ben. **5-perc cron**, free signal a graph-quality-re.

**Effort:** S-M. **Risk:** low. **Depends on:** graphify, Memgraph.

---

### 19. NLI×KO-DB×Memgraph triangulation score

**Headline:** Minden új KO-DB triplet kapja meg az NLI-entailment-score-t a Memgraph-related-chunk-okkal szemben.

**What it does:** Triplet "X solves Y" beérkezik. Memgraph-on `MATCH (X)-[:RELATED_TO*1..2]-(Y)` lekérdezi a related chunk-okat. NLI Layer 2.5 mond entailment-verdict-et: "X solves Y" mennyire következik a chunk-okból. **Cross-source-corroboration most string-match**, NLI-vel SEMANTIC corroboration. SelfCheck (NLI Layer 2.7) ráadásul detect-eli az ellentmondó-chunk-ot ha van.

**Why now:** A 3 layer (KO-DB facts + Memgraph entities + NLI judge) létezik de **soha nem hív be egymást ingestion-time-ben**. A triangulation lényegesen csökkenti a false-fact-rate-et (Constitutional Critic-val párhuzamos defense-layer).

**Effort:** M. **Risk:** mid. **Depends on:** B-3 NLI Layer 2.5, KO-DB, Memgraph.

---

### 20. Vault-MCP server local-first (STDIO)

**Headline:** Egyetlen MCP server ami expose-olja: vault-search, ko-query, memgraph-cypher, crystallize-pending olvasását.

**What it does:** `vault-mcp` server STDIO + HTTP local-only. Tool-spec:
- `vault.search(query, top_k)` → vault-search daemon proxy
- `vault.ko_query(pattern, predicate?)` → KO-DB CLI
- `vault.cypher(query)` → Memgraph read-only
- `vault.session_log(slug?, limit?)` → 08-Sessions/* tail
- `vault.audit(audit_name)` → 06-Audits/* read
Bekonfigolva Claude.ai web-UI-ra, mobil-on is elérhető. **Local-only, NEM cloud.**

**Why now:** A user 3 agent-en (Claude Code, Codex, Gemini) ül, mindhárom CLI-only. **Web-UI / mobil hozzáférés a vault-tudáshoz JELENLEG NULLA** — sajnos a vault headless szerveren. 2026-ra az MCP server-stack stable.

**Effort:** M. **Risk:** mid (auth + privacy: csak Tailscale-on át exponál). **Depends on:** vault-search daemon, KO-DB CLI, Memgraph driver.

Sources: [MCP Servers 2026 (Prefect)](https://www.prefect.io/resources/best-mcp-deployment-platforms-enterprise-2026), [Local MCP Tools (Microsoft Agent Framework)](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools)

---

### 21. KO-DB → Bayesian-belief-update on contradiction

**Headline:** Conflict-audit cron ne csak detektáljon, hanem **Bayes-update**-eljen — confidence-prior + new-evidence-likelihood → posterior.

**What it does:** Helyettesíti a current "newest-wins" politikát a contradiction-resolve-on. P(fact|evidence) = P(evidence|fact) × P(fact) / P(evidence). A "prior" a régi-confidence + decay (#3); az "evidence likelihood" a confirmation-count + scorer-confidence az új source-on. Asymmetric: high-confidence-evergreen-fact (KGC = NestJS) ellen 1 weak contradiction NEM dönt; >3 high-confidence kontra-evidence kell. Visualization-ban a "confidence-history-graph" timestamp-en.

**Why now:** A current heat-classifier predicate-aware-de-binary-resolve. Production-grade contradiction-handling Bayes-update kell, különösen browser-history bridge (#13) magas-zaj input mellett.

**Effort:** M. **Risk:** mid. **Depends on:** conflict-audit cron, KO-DB schema (history-table #9-cel együtt jó match).

---

## Bridge-out (external ingest)

### 22. NotebookLM "deep-research" output → KO-DB ingest auto

**Headline:** A NotebookLM custom-report 7-szekciós output-ja automatikusan KO-DB triplet-extract-be megy.

**What it does:** A user 3+ NotebookLM-research-t generált (Boulium Phase-2, KGC-4 integration, Rojt-bojt). Mindegyiknek a 7-szekciós custom-report MD-output-ja **10-raw/-ban van**, de **NEM ment át KO-DB extract-en** (Karpathy-ingest-pipeline lemaradt). Cron `notebooklm-output-ingest`: detektálja az új `10-raw/notebooklm-*.md`-t → subagent-fanout extract → cross-source-corroboration az existing facts-szel. NLI Layer 2.5-tel pre-filter (NEM-claim-state-ment "as discussed earlier" type chunk).

**Why now:** A NotebookLM-pattern lefedve (workflow ÉLES), viszont a downstream-vault-integration manual marad. A vault-koherencia magaslandó: NotebookLM-research-claim-ek a KO-DB-be kerülve cross-validate-elhetik a session-extract-eket.

**Effort:** M. **Risk:** low. **Depends on:** KO-DB ingest, NLI Layer 2.5, subagent-fanout, notebooklm-cli.

---

## Záró rangsor — top-10 by ROI

| # | Idea | Bucket | Effort | Risk | ROI |
|---|------|--------|--------|------|-----|
| 1 | #9 Temporal-KG SCD2 | Cap.Ext | M-L | mid | ⭐⭐⭐⭐⭐ |
| 2 | #1 RAGAS/DeepEval CI-gate | Quick | S | low | ⭐⭐⭐⭐⭐ |
| 3 | #15 Sleep-consolidation | Big Bet | L-XL | mid | ⭐⭐⭐⭐⭐ |
| 4 | #13 Browser-history bridge | Big Bet | L | mid | ⭐⭐⭐⭐ |
| 5 | #20 Vault-MCP server | Synergy | M | mid | ⭐⭐⭐⭐ |
| 6 | #6 ColBERT late-interaction | Cap.Ext | M | mid | ⭐⭐⭐⭐ |
| 7 | #4 Daily-note auto-summarize | Quick | S | low | ⭐⭐⭐⭐ |
| 8 | #18 graphify×Memgraph diff | Synergy | S-M | low | ⭐⭐⭐ |
| 9 | #14 GitHub commit bridge | Big Bet | L | low | ⭐⭐⭐ |
| 10 | #19 NLI×KO-DB×Memgraph triangulation | Synergy | M | mid | ⭐⭐⭐ |

---

## Forrás-aggregátor

- [State of AI Agent Memory 2026 (Mem0)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Best AI Agent Memory Frameworks 2026 (Vectorize)](https://vectorize.io/articles/best-ai-agent-memory-systems)
- [GraphRAG Complete Guide 2026 (Calmops)](https://calmops.com/ai/graphrag-complete-guide-2026/)
- [Graph RAG Practitioner Guide 2026 (Medium)](https://medium.com/graph-praxis/graph-rag-in-2026-a-practitioners-guide-to-what-actually-works-dca4962e7517)
- [Temporal Graph RAG (Medium Feb 2026)](https://medium.com/@nitishkumarnitc/temporal-graph-rag-why-time-aware-knowledge-graphs-are-reshaping-ai-memory-04fc62dd0acd)
- [T-GRAG arxiv 2508.01680](https://arxiv.org/abs/2508.01680)
- [STAR-RAG arxiv 2510.13590](https://arxiv.org/abs/2510.13590)
- [SCM: Sleep-Consolidated Memory](https://www.emergentmind.com/papers/2604.20943)
- [Active Dreaming Memory engrxiv](https://engrxiv.org/preprint/download/5919/9826)
- [Sleep-Inspired Memory Consolidation arxiv 2603.14517](https://arxiv.org/pdf/2603.14517)
- [Constitutional AI overview (Brenndoerfer)](https://mbrenndoerfer.com/writing/constitutional-ai-principle-based-alignment-through-self-critique)
- [Metacognitive Reflection arxiv 2601.11974](https://arxiv.org/pdf/2601.11974)
- [Intrinsic Metacognitive Learning arxiv 2506.05109](https://arxiv.org/pdf/2506.05109)
- [DSPy GEPA tutorial](https://dspy.ai/tutorials/gepa_ai_program/)
- [HopRAG arxiv 2502.12442](https://arxiv.org/abs/2502.12442)
- [HippoRAG enhancement (Graphwise)](https://graphwise.ai/blog/from-retrieval-to-reasoning-enhancing-hipporag-with-graph-based-semantics/)
- [ColBERT and Late Interaction (ML Journey)](https://mljourney.com/colbert-and-late-interaction-retrieval-how-it-works-and-when-to-use-it/)
- [Late Interaction Workshop ECIR 2026](https://www.lateinteraction.com/)
- [RAG Evaluation Frameworks 2026 (Atlan)](https://atlan.com/know/llm-evaluation-frameworks-compared/)
- [RAG Evaluation 2026 (DataVLab)](https://datavlab.ai/post/rag-evaluation-methods-metrics-2026-guide)
- [TraceMind blog — browser-history goldmine](https://tracemind.app/blog/your-browser-history-is-a-goldmine-building-a-personal-knowledge-graph)
- [Trail (Product Hunt)](https://www.producthunt.com/products/trail-visualize-your-chrome-browsing)
- [Best MCP Servers 2026 (Prefect)](https://www.prefect.io/resources/best-mcp-deployment-platforms-enterprise-2026)
- [Local MCP Tools (Microsoft)](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools)
- [MCP Server Ecosystem 2026 (DEV)](https://dev.to/sahil_kat/the-mcp-server-ecosystem-in-2026-integration-layer-for-ai-agents-2mln)
- [Awesome Hungarian NLP](https://github.com/oroszgy/awesome-hungarian-nlp)
- [Hungarian embedding interpretability](http://publicatio.bibl.u-szeged.hu/15460/1/main.pdf)
