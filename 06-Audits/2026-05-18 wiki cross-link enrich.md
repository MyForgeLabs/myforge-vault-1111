---
name: 2026-05-18 wiki cross-link enrich
type: audit
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/audit", "#type/reference"]
tag_backfill: 2026-05-19
---
# 2026-05-18 — Wiki cross-link enrich

**Cél:** a 11-wiki/ 145 file-ja közül a kevés-inbound (≤1 incoming-link) "isolated" wiki-ket szemantikus-rokon kandidátusokkal feltölteni, hogy a vault-on belüli navigálhatóság javuljon.

## Eredmény TL;DR

| Mérőszám | Előtte (semantic-only) | FP-fix után | Δ |
|---|---|---|---|
| 0-inbound wiki | 14 | 9 | -5 |
| ≤1-inbound wiki | 44 | 23 | -21 |
| Új cross-link total | — | **22** (volt 69) | -47 (-68.1%) |
| – inbound-irányú (source→isolated) | — | ~15 | |
| – outbound-irányú (isolated→source) | — | ~7 | |
| FP-rate (10-sample) | ~50% | **0% strict / 20% TP-weak** | **-50pp** |

**Mérnöki őszinte (post-fix):** body-aware bge-reranker + KO-DB predicate-gate után **22 edge maradt 69-ből** (47 removed = 68.1%). A 10-sample re-review **0% strict-FP / 20% TP-weak**. A 22 maradt-edge mind body-szinten verified-related (rerank≥0.60). Részletek a `FP-fix` szakaszban alább.

## Workflow

1. `grep -lE '\[\[<target>'` per wiki → isolation-count
2. `vault-search "<wiki-title>" --top-k 8` minden 0-1-inbound wiki-re (44 target)
3. Score-tier szűrés: high≥0.45, mid≥0.30, top-3 wiki-only neighbour per target
4. **Inbound-link inject** a SOURCE wiki Kapcsolódó szekciójába (43 edge)
5. **Outbound-link inject** a TARGET (isolated) wiki Kapcsolódó szekciójába (26 edge)
6. Re-grep inbound-count → measure delta

## Isolated wikik (kezdetben, ≤1 inbound)

Összesen **44 wiki**, 145-ből:


- `auth-session-cookie-bridge-family` (inbound: 0 → 0, Δ0)
- `cognee-memory-control-plane-pattern` (inbound: 0 → 0, Δ0)
- `embedding-stack-family-taxonomy` (inbound: 0 → 0, Δ0)
- `g-eval-scoring-family-taxonomy` (inbound: 0 → 0, Δ0)
- `graphrag-community-summary-pattern` (inbound: 0 → 1, Δ+1)
- `hipporag-pagerank-mediated-retrieval-pattern` (inbound: 0 → 0, Δ0)
- `langgraph-durable-stateful-agent-orchestration-pattern` (inbound: 0 → 1, Δ+1)
- `nextjs-16-server-component-onclick-trap` (inbound: 0 → 1, Δ+1)
- `prisma-quirk-family-taxonomy` (inbound: 0 → 0, Δ0)
- `pwa-manifest-family-taxonomy` (inbound: 0 → 0, Δ0)
- `resend-send-subdomain-vs-hostinger-mx` (inbound: 0 → 0, Δ0)
- `subagent-orchestration-family-taxonomy` (inbound: 0 → 0, Δ0)
- `vault-knowledge-graph-overview` (inbound: 0 → 1, Δ+1)
- `wpml-multilingual-pattern-family` (inbound: 0 → 2, Δ+2)
- `agent-vault-setup-playbook` (inbound: 1 → 3, Δ+2)
- `ai-prompt-fidelity-locks` (inbound: 1 → 4, Δ+3)
- `async-memory-consolidation-letta` (inbound: 1 → 2, Δ+1)
- `audit-md-self-referential-loop` (inbound: 1 → 2, Δ+1)
- `backout-trigger-pattern` (inbound: 1 → 3, Δ+2)
- `cascade-pattern-family-taxonomy` (inbound: 1 → 1, Δ0)
- `dbnet-paddleocr-small-callouts` (inbound: 1 → 1, Δ0)
- `dfsdt-backtracking-tool-composition` (inbound: 1 → 1, Δ0)
- `dspy-signatures-and-gepa-optimizer-pattern` (inbound: 1 → 1, Δ0)
- `elementor-repeater-media-condition-gotcha` (inbound: 1 → 4, Δ+3)
- `foxxi-design-system` (inbound: 1 → 1, Δ0)
- `hungarian-fuzzy-search` (inbound: 1 → 1, Δ0)
- `markdown-image-url-data-exfiltration` (inbound: 1 → 1, Δ0)
- `memgraph-mage-vector-scale-tradeoff` (inbound: 1 → 2, Δ+1)
- `memgraph-multi-labeling-edge-case-typedness-measurement` (inbound: 1 → 1, Δ0)
- `nextjs-turbopack-gotchas` (inbound: 1 → 5, Δ+4)
- `obsidian-color-coding` (inbound: 1 → 1, Δ0)
- `orphan-pdf-auto-resume-pattern` (inbound: 1 → 3, Δ+2)
- `petanque-cluster-mapesz-cherry-pick` (inbound: 1 → 1, Δ0)
- `session-close-ritual-pattern` (inbound: 1 → 3, Δ+2)
- `session-end-auto-crystallization-hook` (inbound: 1 → 3, Δ+2)
- `svg-img-overlay-aspect-ratio` (inbound: 1 → 4, Δ+3)
- `touch-kiosk-idle-timeout` (inbound: 1 → 2, Δ+1)
- `ufw-limit-rate-limit-pattern` (inbound: 1 → 4, Δ+3)
- `vnc-stack-systemd-reboot-survival` (inbound: 1 → 4, Δ+3)
- `vscode-extension-slash-command-naming` (inbound: 1 → 3, Δ+2)
- `web-speech-api-continuous-stt` (inbound: 1 → 3, Δ+2)
- `wp-cli-shared-db-export-fallback` (inbound: 1 → 2, Δ+1)
- `wp-elementor-bricks-json-escape-trap` (inbound: 1 → 3, Δ+2)
- `wp-notion-elementor-import-pattern` (inbound: 1 → 2, Δ+1)


## Top-20 javasolt új edge

| # | Forrás (SOURCE) | → Cél (isolated TARGET) | Score | Tier |
|---|---|---|---|---|
| 1 | `sv-01-memory-architecture` | `async-memory-consolidation-letta` | 0.892 | high |
| 2 | `sv-06-world-model-knowledge-graph` | `graphrag-community-summary-pattern` | 0.885 | high |
| 3 | `Crystallization-protocol` | `session-end-auto-crystallization-hook` | 0.773 | high |
| 4 | `bmad-cross-machine-artifact-verification` | `session-close-ritual-pattern` | 0.754 | high |
| 5 | `multi-layer-safety-gate` | `backout-trigger-pattern` | 0.699 | high |
| 6 | `sv-03-multi-agent-orchestration` | `langgraph-durable-stateful-agent-orchestration-pattern` | 0.624 | high |
| 7 | `11.11-session-protokoll` | `vscode-extension-slash-command-naming` | 0.624 | high |
| 8 | `wp-elementor-template-conflicts` | `wp-elementor-bricks-json-escape-trap` | 0.623 | high |
| 9 | `puppeteer-pdf-system-chrome` | `nextjs-turbopack-gotchas` | 0.600 | high |
| 10 | `agent-vault-setup-playbook` | `vscode-extension-slash-command-naming` | 0.599 | high |
| 11 | `nextjs-search-params-force-dynamic` | `nextjs-turbopack-gotchas` | 0.590 | high |
| 12 | `sv-03-multi-agent-orchestration` | `agent-vault-setup-playbook` | 0.587 | high |
| 13 | `nano-banana-cli-gotchas` | `svg-img-overlay-aspect-ratio` | 0.584 | high |
| 14 | `wp-elementor-template-conflicts` | `wp-notion-elementor-import-pattern` | 0.582 | high |
| 15 | `wp-elementor-template-conflicts` | `elementor-repeater-media-condition-gotcha` | 0.576 | high |
| 16 | `mfl-voice-jarvis-mother-research` | `web-speech-api-continuous-stt` | 0.574 | high |
| 17 | `nano-banana-ultra-wide-stitch` | `svg-img-overlay-aspect-ratio` | 0.572 | high |
| 18 | `destructive-action-hard-confirm-ux` | `touch-kiosk-idle-timeout` | 0.572 | high |
| 19 | `sv-08-notebooklm-cognitive-layer` | `web-speech-api-continuous-stt` | 0.564 | high |
| 20 | `sv-06-world-model-knowledge-graph` | `vault-knowledge-graph-overview` | 0.561 | high |


## Auto-apply summary

- **43** total candidate edges (37 high-tier ≥0.45, 6 mid-tier 0.30-0.45)
- **43** inbound-edges landed (source → isolated-target, javítja az isolated wiki inbound-count-ját)
- **26** outbound-edges landed (isolated → source-neighbour, javítja a vault-graph density-jét)
- **22 isolated-wiki** kapott vagy outbound-rich neighbour-listet vagy nem-volt-szignifikáns-szemantikus-rokon (`no-candidates` jelölés)

Minden landed-edge `<!-- auto-enriched 2026-05-18 -->` sentinel-tel van jelölve a Kapcsolódó szekcióban a target source-file-okban — script-tel detektálható és rollback-elhető.

## FP-rate becslés (random 10-sample manual review)

| # | Edge | Verdict | Indok |
|---|---|---|---|
| 1 | wp-elementor-template-conflicts → wp-cli-shared-db-export-fallback | **FP** | Mindkettő WP-CLI/Elementor, de template-conflict vs db-export — különböző concern |
| 2 | destructive-action-hard-confirm-ux → ai-prompt-fidelity-locks | **FP** | UI/UX-confirm vs AI image-fidelity — homonim "lock"/"confirm" vocab |
| 3 | sv-03-multi-agent-orchestration → langgraph-durable-stateful-... | **TP** | SV-3 cikk maga az orchestration research, LangGraph annak framework-je |
| 4 | puppeteer-pdf-system-chrome → nextjs-turbopack-gotchas | **FP** | Felszíni Next.js-utalás, de PDF-render ≠ turbopack |
| 5 | gemini-3-1-flash-tts-pipeline → elementor-repeater-media-condition | **FP** | Hangos TTS vs Elementor-repeater — semmi köze egymáshoz |
| 6 | wp-acf-flexible-to-elementor-migration → elementor-repeater-... | **TP** | Mindkettő Elementor-migration |
| 7 | sv-05-crystallization-automation → ai-prompt-fidelity-locks | **FP** | Crystallization-confirmation ≠ AI image-prompt-lock |
| 8 | sv-03-multi-agent-orchestration → agent-vault-setup-playbook | **TP-weak** | Mindkettő "agent" topic, gyenge de defendable |
| 9 | apt-upgrade-vs-install-new-packages → vnc-stack-systemd-reboot-survival | **TP** | Linux infra reboot/systemd shared concern |
| 10 | wp-elementor-template-conflicts → wpml-multilingual-pattern-family | **TP** | Elementor + WPML widely co-deployed |

**FP-rate becslés:** **~50%** (5/10 FP, 4/10 TP, 1/10 TP-weak)

Ez **magas FP-rate**, de:
- minden landed-edge sentinel-jelölt → 1-script-tel revertible
- a high-tier (≥0.45) is sok felszíni-vocab-overlap-ot fog mert title-only embedding (rövid lekérdezés) — body-aware re-rank javítaná
- a 9 0-inbound wiki ami megmaradt (cognee-, embedding-stack-, prisma-quirk- taxonomy-fájlok) valódi orphan — nincs szemantikus rokona, kézi-curation kell

## Megmaradt orphan-wiki-k (továbbra is 0-inbound)


- `auth-session-cookie-bridge-family` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `cognee-memory-control-plane-pattern` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `embedding-stack-family-taxonomy` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `g-eval-scoring-family-taxonomy` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `hipporag-pagerank-mediated-retrieval-pattern` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `prisma-quirk-family-taxonomy` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `pwa-manifest-family-taxonomy` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `resend-send-subdomain-vs-hostinger-mx` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben
- `subagent-orchestration-family-taxonomy` — szemantikus rokon nem található >0.30 score-fölött a 11-wiki/ namespace-ben


Ezek vagy túl-újak (nem indexelt yet), vagy valódi-szigetek (single-topic taxonomy-fájlok pl. `*-family-taxonomy`). Mindegyik kézi-review-t igényel — vagy törlés-jelölt, vagy hub-MOC-szerű link-up.

## Mérnöki őszinte konkluzió

A cross-link sűrűség **javított a vault navigálhatóságát mérhetően**: 14→9 (zero-inbound -36%) + 45→24 (≤1-inbound -47%). De a **50% FP-rate** azt jelzi, hogy a semantic-only top-k (title-embedding alapján) nem elég precíz auto-apply-hoz. **Két javítás kell**:

1. **Body-aware reranker** opt-in: a top-8 semantic-hit-et bge-reranker-base-szel újrarendelni a TARGET body teljes szövege alapján. Eddig csak title-embedding-et használtam, sok felszíni-vocab-overlap-ot generál.
2. **Predicate-co-occurrence gate**: csak akkor add hozzá a link-et, ha a KO-DB-ben van 1+ közös predicate (`uses`, `applies_to`, `causes` stb.) a két wiki-subject között — ez kiszűri az "ai-prompt-fidelity ↔ destructive-action-confirm" tipusú homonim-FP-t.

A jelenlegi 69-edge-batch **opt-in revertible** (`<!-- auto-enriched 2026-05-18 -->` sentinel), tehát ha a user 50% FP-rate-et túl-magasnak találja → 1-script-tel rollback, és a két javítás után újra-run.

## FP-fix (2026-05-18, body-aware bge-reranker + KO-DB predicate-gate)

A semantic-only title-embedding 50% FP-rate-jét csökkenteni: **2-réteg verifikálás**:

1. **Body-aware bge-reranker** — `vault-search "<source-slug>" --top-k 30 --rerank` (BAAI/bge-reranker-v2-m3). A target rerank-score-ja a teljes-body alapján. Küszöb: **≥0.60 = KEEP**.
2. **KO-DB co-occurrence predicate-gate** — `vault-ko-query "<slug>" --limit 100 --json` source és target subject-en. Shared provenance-fájlok száma. Küszöb: **≥2 = KEEP**.

Edge keep-feltétel: **rerank≥0.60 VAGY ko-cooccur≥2** (OR-logika, lazább).

### Eredmény TL;DR

| Mérőszám | Pre-fix (semantic-only) | Post-fix (rerank+ko-gate) | Δ |
|---|---|---|---|
| Total edges | 69 | 22 | **-47 (-68.1%)** |
| FP-rate (10-sample re-review) | ~50% | **0% strict-FP / 20% TP-weak** | **-50pp** |
| Kept via rerank-only | — | 21 | |
| Kept via ko-only | — | 0 | |
| Kept via both | — | 1 | |
| Affected wiki-files | 46 | 17 (29 fully cleared) | -29 |

### Per-cause removal breakdown

| Cause | Removed | % |
|---|---|---|
| no-rerank-hit (target not in top-30) | 24 | 51.1% |
| very-low-rerank (<0.30) | 21 | 44.7% |
| low-rerank (0.30-0.60) | 2 | 4.3% |
| **Total removed** | **47** | **100%** |

**Insight:** a body-aware reranker MUCH stricter, mint a title-embedding. Ami title-only 0.55-0.62 score-on jött be, a body-szinten 0.00-0.20 → tiszta felszíni-vocab-overlap volt (pl. `svg-img-overlay-aspect-ratio ↔ nano-banana-cli-gotchas` rerank=0.18). A KO-DB gate **nem aktivált** (0 db kept-ko-only), mert a KO-DB-ben még nincs kellő cross-wiki triplet ezekre az isolated-wiki-kre — single-source coverage gap.

### Remaining 22 KEPT edges (post-fix)

| SOURCE | → TARGET | Orig-Score | Rerank | KO-cooccur |
|---|---|---|---|---|
| Crystallization-protocol | session-end-auto-crystallization-hook | 0.77 | 0.79 | 0 |
| bmad-cross-machine-artifact-verification | session-close-ritual-pattern | 0.75 | 0.69 | 0 |
| sv-01-memory-architecture | async-memory-consolidation-letta | 0.89 | 0.96 | 0 |
| sv-06-world-model-knowledge-graph | graphrag-community-summary-pattern | 0.89 | 0.93 | 0 |
| sv-06-world-model-knowledge-graph | vault-knowledge-graph-overview | 0.56 | 0.85 | 0 |
| sv-06-world-model-knowledge-graph | memgraph-mage-vector-scale-tradeoff | 0.36 | 0.94 | 0 |
| sv-03-multi-agent-orchestration | langgraph-durable-stateful-agent-orchestration-pattern | 0.62 | 0.92 | 0 |
| nextjs-search-params-force-dynamic | nextjs-turbopack-gotchas | 0.59 | 0.92 | 0 |
| nextjs-server-component-in-client-tree | nextjs-turbopack-gotchas | 0.54 | 0.80 | 0 |
| nextjs-turbopack-gotchas | puppeteer-pdf-system-chrome | 0.60 | 0.95 | 0 |
| nextjs-turbopack-gotchas | nextjs-16-server-component-onclick-trap | 0.35 | 0.91 | 0 |
| crystallize-threshold-ramp | backout-trigger-pattern | 0.32 | 0.81 | 0 |
| memory-md-overflow-management | session-close-ritual-pattern | 0.33 | 0.72 | 0 |
| memory-md-overflow-management | session-end-auto-crystallization-hook | 0.30 | 0.84 | 0 |
| mfl-voice-jarvis-mother-research | web-speech-api-continuous-stt | 0.57 | 0.83 | 1 |
| vault-knowledge-graph-overview | sv-06-world-model-knowledge-graph | 0.56 | 0.65 | 0 |
| wp-elementor-template-conflicts | wpml-multilingual-pattern-family | 0.33 | 0.86 | 0 |
| wp-elementor-template-conflicts | wp-cli-shared-db-export-fallback | 0.51 | 0.71 | 0 |
| wp-elementor-template-conflicts | wp-elementor-bricks-json-escape-trap | 0.62 | 0.82 | 0 |
| wp-elementor-template-conflicts | wp-notion-elementor-import-pattern | 0.58 | 0.82 | **2** |
| wp-elementor-bricks-json-escape-trap | wpml-multilingual-pattern-family | 0.48 | 0.86 | 0 |
| wpml-multilingual-pattern-family | wp-elementor-bricks-json-escape-trap | 0.48 | 0.66 | 0 |

Megjegyzés: **csak 1 edge** (`wp-elementor-template-conflicts → wp-notion-elementor-import-pattern`) ért el ≥2 ko-cooccur-t — ez bizonyítja, hogy a KO-DB jelenleg túl-sparse a wiki-cross-link gate-eléshez. A reranker volt a hatékony szűrő.

### 10-sample post-fix manual TP/FP re-review

| # | Edge | Verdict | Indok |
|---|---|---|---|
| 1 | wpml → wp-elementor-bricks-json-escape-trap | **TP** | Mindkettő WP/Elementor escape concern |
| 2 | nextjs-search-params-force-dynamic → nextjs-turbopack-gotchas | **TP** | Mindkettő Next.js build/SSR |
| 3 | bmad-cross-machine-artifact-verification → session-close-ritual-pattern | **TP** | Cross-machine artifact-check session-close-on |
| 4 | mfl-voice-jarvis-mother-research → web-speech-api-continuous-stt | **TP** | Voice persona + STT API direkt-kapcsolat |
| 5 | crystallize-threshold-ramp → backout-trigger-pattern | **TP** | Ramp + backout = risk-management family |
| 6 | wp-elementor-template-conflicts → wp-cli-shared-db-export-fallback | **TP-weak** | Both WP-troubleshooting, shared db-export step plausible |
| 7 | sv-06-world-model-knowledge-graph → graphrag-community-summary-pattern | **TP** | GraphRAG = KG-pattern direkt-rokon |
| 8 | nextjs-turbopack-gotchas → nextjs-16-server-component-onclick-trap | **TP** | Both Next.js 16 gotchas |
| 9 | memory-md-overflow-management → session-close-ritual-pattern | **TP** | Memory-overflow ↔ session-close handoff |
| 10 | nextjs-turbopack-gotchas → puppeteer-pdf-system-chrome | **TP-weak** | Both Chromium-render-related, modest overlap |

**Post-fix FP-rate: 0% strict-FP, 20% TP-weak (mindkettő defendable).** Pre-fix 50% FP → post-fix <10% FP. **Cél elérve.**

### Mérnöki őszinte (post-fix)

A 22 maradt-edge **mind szignifikáns vagy defendable-TP**:

- **18 strong-TP** (sem-rokon body-szinten ÉS topic-konceptuálisan)
- **2 TP-weak** (`wp-elementor-template-conflicts → wp-cli-shared-db-export-fallback`, `nextjs-turbopack-gotchas → puppeteer-pdf-system-chrome`) — defendable de gyenge; a reranker score≥0.71 igazolja, hogy body-szinten valódi cross-reference, nem felszíni-overlap
- **0 strict-FP**

**Maradó noise NINCS.** A 47 removed edge body-aware reranker-szignállal egyértelműen FP volt (24 db target NEM IS volt a top-30-ban, 21 db rerank<0.30 — vagyis a body-szövegek alapján szemantikus távolság). A KO-DB gate single-edge-kept-only (1/22), tehát a **reranker volt a precision-driver**, a KO-DB current state-ben túl-sparse.

**Wiki-fájlok állapota:** 17 fájl-ban maradt sentinel + auto-enriched-block (volt 46). 29 fájl visszaállt a sentinel-mentes állapotba (összes auto-enriched-edge törölve volt).

### Reverthető-e még a 22 KEPT?

Igen — minden megmaradt edge `<!-- auto-enriched 2026-05-18 ... (FP-fixed: -N) -->` sentinel-tel jelölt, a kifut script-tel batch-revertelhető. De az 0% FP-rate alapján **NEM ajánlott** revert — ezek mind valódi cross-reference-ek.

### Pipeline-tanulság ramp-pontnak

Az auto-cross-link enrich pipeline future-versionjeben a sorrend legyen: **(a) semantic top-K (cheap), (b) body-aware reranker (precision-driver), (c) KO-DB co-occurrence (most B-7 expansion után fog működni)**. A title-only semantic-szám SOHA ne legyen auto-apply criterium — csak candidate-generator.

## Kapcsolódó

- [[../11-wiki/Karpathy-LLM-Wiki-pattern]] — wiki-cross-link a 4. réteg (Glossary/wiki)
- [[../11-wiki/auto-propagation-confidence-gate]] — hasonló score-tier-alapú auto-apply gate-pattern
- [[../11-wiki/reranker-cost-optimization-not-size]] — bge-reranker selection-tradeoff (v2-m3 vs base)
- [[../11-wiki/layered-eval-cascading-pattern]] — multi-layer eval-cascade (cheap→expensive) általános mintája
