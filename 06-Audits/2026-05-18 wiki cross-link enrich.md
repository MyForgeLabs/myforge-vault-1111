---
name: 2026-05-18 wiki cross-link enrich
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: [audit, vault, wiki, cross-link, semantic]
---

# 2026-05-18 — Wiki cross-link enrich

**Cél:** a 11-wiki/ 145 file-ja közül a kevés-inbound (≤1 incoming-link) "isolated" wiki-ket szemantikus-rokon kandidátusokkal feltölteni, hogy a vault-on belüli navigálhatóság javuljon.

## Eredmény TL;DR

| Mérőszám | Előtte | Utána | Δ |
|---|---|---|---|
| 0-inbound wiki | 14 | 9 | -5 |
| ≤1-inbound wiki | 44 | 23 | -21 |
| Új cross-link total | — | **69** | +69 |
| – inbound-irányú (source→isolated) | — | 43 | |
| – outbound-irányú (isolated→source) | — | 26 | |

**Mérnöki őszinte:** 10-sample manual FP review → **~50% FP**. A semantic-only matching score 0.45-fölött is gyakran felszíni vocab-overlap (pl. `wp-` prefix, `nextjs-` prefix, `sv-` SV-cikk) NEM topic-egyezés. A landed-edge-ek hash-comment-tel jelölve (`auto-enriched 2026-05-18`), reverthető. Min-quality threshold-emelés a következő ramp-pontnál (>0.55 score + predicate-co-occurrence) ajánlott.

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

## Kapcsolódó

- [[../11-wiki/Karpathy-LLM-Wiki-pattern]] — wiki-cross-link a 4. réteg (Glossary/wiki)
- [[../11-wiki/auto-propagation-confidence-gate]] — hasonló score-tier-alapú auto-apply gate-pattern
