---
name: wiki Index
type: index
tags: ["#type/index", "wiki"]
created: 2026-04-23
updated: 2026-05-18
---

# 11-wiki/ — Desztillált tudás master-INDEX

**125 evergreen wiki-cikk, 9 témakörbe rendezve.** Karpathy LLM-Wiki minta szerinti **wiki-réteg** — saját szavakkal átírt tudás, AI-agent-kompatibilis. A nyers források a [[10-raw/Index|10-raw/]]-ban maradnak referenciának, a tudás itt kristályosodik ki.

> [!tip] Navigációs tipp
> Ha keresel valamit: `Ctrl+F` ezen az oldalon, vagy nézd meg a [[#Témakörök|témakör-térképet]] alább. Új ide? Kezdd a [[#1. Vault-design és Karpathy-réteg|vault-design]] szakasszal.

## Témakörök

1. [[#1. Vault-design és Karpathy-réteg|Vault-design és Karpathy-réteg]] — 8 cikk
2. [[#2. Superintelligent Vault — 8-tengelyű AGI roadmap|SV AGI roadmap]] — 9 cikk
3. [[#3. AI-engineering pattern-ek crystallization automation|AI-engineering — crystallization + automation]] — 28 cikk
4. [[#4. LLM-evaluation és cost-optimization|LLM-evaluation + cost-optimization]] — 12 cikk
5. [[#5. Multi-agent orchestration tool composition|Multi-agent + tool composition]] — 10 cikk
6. [[#6. Knowledge graph Memgraph retrieval|Knowledge graph + Memgraph + retrieval]] — 9 cikk
7. [[#7. Web-dev gotchas Next.js WordPress frontend|Web-dev gotchas (Next.js / WP / frontend)]] — 23 cikk
8. [[#8. Infra DevOps server hardening|Infra + DevOps + server hardening]] — 12 cikk
9. [[#9. AI tooling research scraping|AI tooling, research + scraping]] — 9 cikk
10. [[#10. Projekt-specifikus playbookok|Projekt-specifikus playbookok]] — 7 cikk

---

## 1. Vault-design és Karpathy-réteg

A vault szervezésének elveit dokumentáló cikkek. Ide kezdj ha új vagy.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[Karpathy-LLM-Wiki-pattern]] | Karpathy 2026-os LLM Wiki minta: raw/ + wiki/ + agent-vault hármas réteg, compilation > retrieval | vault-design, rag |
| [[Johnny-Decimal-prefix]] | Mappa-prefix konvenció (00-Meta, 01-Daily, …) — miért és hogyan | vault-design, naming |
| [[Kepano-File-over-App-filozofia]] | Steph Ango "File over App" elve — markdown szövegréteg agent-kompatibilis | vault-design, philosophy |
| [[11.11-session-protokoll]] | A `/11.11*` parancs-család és a session-fájl séma, crystallization workflow | agents, session |
| [[Auto-context-loading]] | Session-start aggressive pre-load (~15-20K token) — projekt-detektálás + 5 layer | agents, context |
| [[Crystallization-protocol]] | Session-stop propagáció: Learnings → ADR/wiki/glossary/memory/projekt | agents, crystallization |
| [[agent-vault-setup-playbook]] | Step-by-step telepítés új gépre (Mac + VS Code Claude Code): symlinkek, skillek, 11.11 scriptek | playbook, onboarding |
| [[Auto-context-loading]] | Detail elsőként projekt detekt, 5 layer load, ~15-20K token | context |

## 2. Superintelligent Vault — 8-tengelyű AGI roadmap

Phase A + A+ + B research master és a 8 tengely wiki-cikkei.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[superintelligent-vault-research]] | 8-tengelyű evolúciós research master index, Phase A + A+ + B 8 sprint-ADR | agi, master-index |
| [[sv-01-memory-architecture]] | SV-1: MemGPT-style 5-rétegű memóriaarchitektúra, working+top-K episodic+semantic | agi, memory, rag |
| [[sv-02-recursive-self-improvement]] | SV-2: GEPA real Pareto optimizer, $0 cost, 0.541→0.619 score improvement | agi, rsi, prompt-evolution |
| [[sv-03-multi-agent-orchestration]] | SV-3: Multi-agent orchestration, subagent-fanout patternek | agi, multi-agent |
| [[sv-04-tool-composition]] | SV-4: MCP, skill library, tool composition primitivek | agi, tool-use, mcp |
| [[sv-05-crystallization-automation]] | SV-5: RLAIF, constitutional AI, self-rewarding crystallization | agi, crystallization |
| [[sv-06-world-model-knowledge-graph]] | SV-6: Memgraph CE 3.9.0 native vector-index + GraphRAG | agi, knowledge-graph |
| [[sv-07-continuous-evaluation]] | SV-7: Continuous evaluation, benchmark, NLI cascade | agi, evaluation |
| [[sv-08-notebooklm-cognitive-layer]] | SV-8: NotebookLM mint külső kognitív réteg | agi, notebooklm |

## 3. AI-engineering pattern-ek + crystallization automation

Evergreen pattern-ek amelyeket bárhol használhatsz: safety-gating, rollback, automation.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[crystallize-threshold-ramp]] | 11.11crystallize threshold ramp protocol (shadow 1.0 → 0.95 → 0.85) | crystallize, ramp, safety |
| [[auto-propagation-confidence-gate]] | Auto-propagation confidence-gate (high-conf → auto, low → batch-preview) | automation, safety |
| [[batch-preview-confirmation-pattern]] | Batch-preview confirmation pattern (összes javaslat egyben + user-OK) | ux, propagation, safety |
| [[backout-trigger-pattern]] | Backout-trigger pattern (auto-revert ha metric drop) | pattern, rollback, monitoring |
| [[rollback-revert-strategy-tiers]] | Rollback / revert stratégia tier-ek (force / sandbox / soft) | safety, recovery |
| [[sandbox-branch-mutation-isolation]] | Sandbox-branch mutation isolation (apply csak crystallize-sandbox-* branchen) | safety, git, isolation |
| [[multi-layer-safety-gate]] | Multi-layer safety-gate (4-rétegű: ENV + script + git-hook + Critic) | safety, playbook |
| [[env-flag-default-disabled-gate]] | ENV-flag default-disabled gate (opt-in, NEM default-on) | safety, opt-in, rollout |
| [[hot-reload-config-pattern]] | Hot-reload config (no-restart threshold-update) | operability |
| [[audit-log-append-only-pattern]] | Audit-log append-only (no-overwrite, no-delete) | safety, observability |
| [[audit-md-self-referential-loop]] | Audit-MD self-referential loop false-positive elkerülés (recurring jobs) | vault-integrity, false-positive |
| [[verification-step-before-claim]] | Verifikációs lépés állítás előtt (anti-hallucination disciplin) | eval, discipline |
| [[ai-prompt-fidelity-locks]] | AI prompt fidelity locks (image-compositing prompt-leakage) | ai, prompts, image-gen |
| [[markdown-image-url-data-exfiltration]] | Markdown-image URL injection — privát adat-kiszivárogtatás LLM output-ból | security, prompt-injection |
| [[skill-metadata-catalog-pattern]] | Skill-metadata catalog (progressive-disclosure agent-skill-loader) | agent, skill-management |
| [[claude-code-subagent-fanout]] | Subagent-fanout playbook ($0 cost, 8× parallel bulk-LLM-mutáció) | claude-code, subagent |
| [[subagent-fanout-context-aware-classification]] | Subagent-fanout context-aware classification (NER, entity-typing) | subagent-fanout, classification |
| [[clean-context-subagent-handoff]] | Clean-context subagent handoff — multi-agent context-isolation primitív | multi-agent, context-mgmt |
| [[claude-code-session-id-per-chat-isolation]] | CLAUDE_CODE_SESSION_ID per-chat isolation pattern | claude-code, concurrency |
| [[cli-session-id-env-var-matrix]] | CLI session-ID env-var matrix (Claude / Codex / Gemini) | 11.11, env-vars |
| [[session-close-ritual-pattern]] | Session-close ritual (Summary + Learnings + Next + propagation) | session-management |
| [[session-end-auto-crystallization-hook]] | Session-end auto-crystallization hook (MemGPT-style sleep-time compute) | crystallization, sv-1 |
| [[async-memory-consolidation-letta]] | Async memory consolidation (Letta sleep-time compute pattern) | memory, agent, letta |
| [[memory-md-overflow-management]] | MEMORY.md overflow (24.4KB limit, tematikus szekciók, detail topic-fájlokba) | memory, vault-hygiene |
| [[skill-project-success-pattern]] | Skill-projekt successful pattern (sprint, productivity, meta) | project-management |
| [[skill-project-stuck-anti-pattern]] | Skill-projekt stuck anti-pattern (debugging) | anti-pattern |
| [[sprint-day-0-skeleton-first]] | Sprint Day 0 skeleton-first (scaffold 1 committal, funkcionális kód 0) | sprint-playbook |
| [[vendor-feature-verify-before-workaround]] | Vendor feature verify before workaround (Memgraph 280× speedup find) | engineering, lesson |

## 4. LLM-evaluation és cost-optimization

G-Eval, NLI, LLM-as-judge, smart-trigger, reranker — minden ami "evaluation + cost".

| Wiki | Abstract | Tags |
|------|----------|------|
| [[g-eval-bias-mitigation-pattern]] | G-Eval v0.3 bias-mitigation (self-enhancement bias mitigation, 30-sample paired kalibráció) | llm-eval, bias |
| [[llm-as-judge-evaluation-pattern]] | LLM-as-judge pattern (G-Eval, critique-shadowing, quality-gate) | evaluation, llm |
| [[nli-hallucination-check-pattern]] | NLI-alapú hallucination check (Learnings ↔ session-trace) | eval, rag |
| [[nli-eval-input-completeness-trap]] | NLI eval input-completeness trap (incomplete = false-fail) | llm-eval, data-quality |
| [[dont-hallucinate-abstain-pattern]] | „Don't Hallucinate, Abstain" — Multi-LLM Collaboration abstain pattern | rag, hallucination |
| [[layered-eval-cascading-pattern]] | Layered eval-cascading (cheap filter → expensive judge) | llm-eval, cost-opt |
| [[smart-trigger-cost-pattern]] | Smart-trigger cost pattern (cheap predicate ⇒ skip expensive call) | cost-opt, llm-pipeline |
| [[reranker-cost-optimization-not-size]] | Reranker cost optimization — NEM size, hanem trigger-rate (bge-reranker-base) | reranker, cost |
| [[hybrid-bm25-semantic-rrf-pattern]] | Hybrid BM25 + semantic RRF pattern (+8ms latency, +recall) | retrieval, search |
| [[top-k-cross-source-corroboration]] | Top-K cross-source corroboration ranking (multiple-sources → boost score) | retrieval, ranking |
| [[llm-daemon-warm-pattern]] | LLM-daemon warm pattern (cold-boot eliminated, 12s→0.64s) | performance, infra |
| [[gemini-2-5-flash-thinking-budget]] | Gemini 2.5 Flash thinking-budget — rövid task → token-elfogyás | gemini, llm |

## 5. Multi-agent orchestration + tool composition

Multi-agent koordináció, MCP, tool-composition, harness mintázatok.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[multi-agent-pointer-ownership-lock]] | Multi-agent pointer ownership lock pattern (concurrent write-safety) | orchestration, concurrency |
| [[dfsdt-backtracking-tool-composition]] | DFSDT backtracking multi-step tool-composition (agent reasoning) | multi-agent, tool-composition |
| [[filesystem-as-state-pattern]] | Filesystem-as-state pattern (Anthropic SSOT, durability) | agent-architecture, anthropic |
| [[claude-code-harness-blocks]] | Claude Code harness — runtime block patterns (bypassPermissions, systemd) | harness, claude-code, security |
| [[vscode-extension-slash-command-naming]] | VSCode Claude Code extension — slash-command naming UX | claude-code, ux |
| [[external-skill-cherry-pick]] | External skill cherry-pick — symlink-pattern (8 Tier-S ECC skill) | claude-code, skills |
| [[bmad-cross-machine-artifact-verification]] | BMad cross-machine artifact verification (event ≠ disk-state) | bmad, session-protocol |
| [[mfl-voice-jarvis-mother-research]] | MFL-Voice — Jarvis × Mother voice-agent deep research master | voice-agent, tts |
| [[web-speech-api-continuous-stt]] | Web Speech API — continuous STT + echo-loop prevention | voice, stt, browser |
| [[obsidian-color-coding]] | Obsidian projekt-szín-kódolás (plugin-mentes CSS playbook) | obsidian, ui, css |

## 6. Knowledge graph + Memgraph + retrieval

Memgraph CE feature-limit, vector-index, graph-extraction, retrieval-tuning.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[memgraph-ce-feature-limits]] | Memgraph CE feature-limits + workarounds (CE image, named volume, port-remap) | memgraph, graph-db |
| [[memgraph-mage-vector-scale-tradeoff]] | Memgraph MAGE vector-search scale trade-off (3.9.0 native 280× speedup) | scale, memgraph, vector |
| [[memgraph-multi-labeling-edge-case-typedness-measurement]] | Memgraph multi-labeling — tipizáltság-mérőszám edge-case (double-counting) | graph-metrics, labels |
| [[mgclient-autocommit-silent-rollback]] | mgclient autocommit silent-rollback pitfall (driver-default) | memgraph, python |
| [[two-tier-graph-extraction]] | Two-tier graph extraction (LLM Memgraph 8997 + graphify tree-sitter 5846, komplementer) | knowledge-graph, extraction |
| [[vault-net-ingest]] | vault-net-ingest — external knowledge intake (URL + GitHub repo → 10-raw) | external-knowledge, github |
| [[hungarian-fuzzy-search]] | Magyar fuzzy search (accent-map + Levenshtein + per-token score) | search, hungarian |
| [[orphan-pdf-auto-resume-pattern]] | Orphan-fájl auto-resume pattern (FastAPI self-healing, background tasks) | fastapi, resilience |
| [[dbnet-paddleocr-small-callouts]] | DBNet (PaddleOCR) vs Tesseract LSTM kis callout-detektálásra | ocr, paddleocr |

## 7. Web-dev gotchas (Next.js / WordPress / frontend)

23 cikk a web-dev quirk-ek és playbookok területéről.

### Next.js / React frontend

| Wiki | Abstract | Tags |
|------|----------|------|
| [[nextjs-api-proxy-bridge]] | Next.js API proxy bridge (2 Node-service közti adatcsere, no CORS, env-auth) | nextjs, api |
| [[nextjs-server-component-in-client-tree]] | Next.js — server async komponens NEM lehet `"use client"` wrapper alá | nextjs, react |
| [[nextjs-search-params-force-dynamic]] | Next.js 16 — `useSearchParams()` build-error static prerender-en | nextjs, turbopack |
| [[nextjs-turbopack-gotchas]] | Next.js Turbopack gotchas (incremental cache, FS-state) | nextjs, performance |
| [[nextjs-pwa-shell-minimum]] | Next.js PWA-shell minimum (manifest + apple-touch + appleWebApp metadata) | nextjs, pwa |
| [[gray-matter-date-coerce]] | gray-matter Date object coerce gotcha (YAML date → JS Date crash JSX-ben) | frontmatter, react |
| [[url-param-plus-decode-quirk]] | URL-paraméter `+` → space silent fallback (filter-érték csendben elveszik) | url, gotcha |
| [[cross-subdomain-cookie-session-bridge]] | Cross-subdomain cookie session bridge (issuer+verifier payload-format) | auth, cookies, nextjs |
| [[demo-fallback-readonly-guard]] | Demo-fallback session = read-only mirror (session.isDemo guard) | safety |
| [[svg-img-overlay-aspect-ratio]] | SVG-overlay `<img>` fölött — aspect-ratio CSS layout bug | css, react, layout |
| [[chromium-img-svg-parent-fill-bug]] | Chromium `<img src="*.svg">` parent-fill cascade bug | svg, browser-bug |
| [[svg-asset-vs-vector-tradeoff]] | SVG asset-source decision (kódolt vs vectorized vs Stock) | svg, asset, decision |
| [[puppeteer-pdf-system-chrome]] | Puppeteer PDF render — system Chrome + token-only auth | pdf, puppeteer |

### WordPress + Elementor + Bricks + WPML

| Wiki | Abstract | Tags |
|------|----------|------|
| [[wp-elementor-template-conflicts]] | WordPress Elementor template-konfliktusok (10 pattern playbook) | wordpress, elementor |
| [[wp-acf-flexible-to-elementor-migration]] | ACF Flexible Content → Elementor Pro migration playbook | acf, elementor |
| [[wpml-acf-elementor-multilingual-mirror]] | WPML ACF→Elementor multilingual mirror (3-lépéses HU→EN tükör) | wpml, multilingual |
| [[elementor-repeater-media-condition-gotcha]] | Elementor repeater MEDIA control + `condition` gotcha | elementor, wp |
| [[wp-elementor-bricks-json-escape-trap]] | WP Elementor + Bricks JSON Unicode-escape trap | wordpress, json |
| [[wp-cli-bricks-postmeta-pattern]] | WP-CLI Bricks postmeta build pattern (`post meta delete + add --format=json`) | wp-cli, bricks |
| [[wp-notion-elementor-import-pattern]] | Notion → WP-Elementor import pattern | wordpress, notion, import |
| [[wp-schema-org-mu-plugin-pattern]] | Schema.org bővítés WordPress-ben mu-plugin-nel | wordpress, seo, schema |
| [[wp-yoast-llms-txt-customization]] | Yoast llms.txt szabály-tisztítás (mu-plugin minta) | wordpress, yoast, ai |
| [[hellopack-wordpress-plugin-suite]] | HelloPack — WordPress prémium plugin-suite | wordpress, plugin |

## 8. Infra + DevOps + server hardening

Linux infra, SSH, UFW, VNC, Hostinger, Memgraph deploy patternek.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[apt-upgrade-vs-install-new-packages]] | `apt-get upgrade` ≠ új csomag-telepítés (kernel-update gotcha) | apt, linux, kernel |
| [[openssh-config-d-load-order]] | OpenSSH sshd_config.d load order — FIRST occurrence wins | ssh, security |
| [[ssh-timeout-remote-process-survives]] | `timeout N ssh ... 'long-cmd'` — SSH-session kill ≠ remote process kill | ssh, devops |
| [[ufw-limit-rate-limit-pattern]] | UFW `limit` — public-but-protected rate-limit policy | ufw, firewall |
| [[vnc-stack-systemd-reboot-survival]] | VNC stack reboot-survival — Xvfb + openbox + x11vnc + noVNC systemd-chain | vnc, systemd |
| [[hostinger-litespeed-cache-purge-protokoll]] | Hostinger LiteSpeed cache-purge protokoll (7-napos image edge-cache) | wordpress, hostinger |
| [[hostinger-updraftplus-staging-migration]] | Hostinger UpdraftPlus staging-migráció — 4 buktató | wordpress, hostinger |
| [[wp-cli-shared-db-export-fallback]] | `wp db export` Hostinger shared-en silent fail → mysqldump direkt | wordpress, backup |
| [[auto-disable-min-volume-guard]] | Auto-disable watchdog — min-volume guard pattern (false-positive elkerülés) | monitoring, watchdog |
| [[prisma-seed-admin-edit-protected]] | Prisma seed admin-edit-védett upsert + külön data-update flow | prisma, db |
| [[prisma-compound-unique-null-quirk]] | Prisma compound unique key — null-component quirk | prisma, db |
| [[excel-redmark-3way-diff-workflow]] | Excel-csere katalógus-frissítés flow (openpyxl piros-font + 3-way diff) | excel, workflow |

## 9. AI tooling, research + scraping

NotebookLM, nano-banana, Gemini TTS, CloakBrowser, SEO research patternek.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[notebooklm-cli-gotchas]] | NotebookLM CLI gotchas (10 quirks: `--json` empty-ID, marker fallback) | notebooklm, cli |
| [[notebooklm-headless-login-fifo]] | NotebookLM headless login (FIFO-stdin pattern) | automation, notebooklm |
| [[notebooklm-seo-competitor-research-pattern]] | NotebookLM SEO competitor research (17×7 source-kérdés, ~60-90 perc) | seo, notebooklm |
| [[nano-banana-cli-gotchas]] | nano-banana CLI gotchas (6 quirks: -r vs -i, flatten, max aspect, Pro cost) | nano-banana, cli |
| [[nano-banana-ultra-wide-stitch]] | nano-banana ultra-wide stitching (max 21:9, 5.25:1 3-panel `+append`) | image-gen, workflow |
| [[gemini-3-1-flash-tts-pipeline]] | Gemini 3.1 Flash TTS Preview — HU pipeline (PCM L16 24kHz → MP3) | gemini, tts |
| [[cloakbrowser-fingerprint-bypass]] | CloakBrowser stealth Chromium — fingerprint bypass playbook | scraping, playwright |
| [[lighthouse-agentic-browsing]] | Lighthouse "Agentic Browsing" score (llms.txt + `<main>` + JSON-LD) | seo, lighthouse |
| [[destructive-action-hard-confirm-ux]] | Destructive action hard-confirm UX pattern (custom modal, Mégse-autofocus) | ux, safety |

## 10. Projekt-specifikus playbookok

Egy-egy projekt köré csoportosított playbookok.

| Wiki | Abstract | Tags |
|------|----------|------|
| [[foxxi-design-system]] | Foxxi design system playbook | foxxi, wp, css |
| [[shopify-yoast-dupla-og]] | Shopify default + Yoast dupla OG description tag konfliktus | shopify, seo |
| [[shopify-robots-agent-policy]] | Shopify built-in agent-policy a robots.txt-ben (2025-26) | shopify, ai-agent |
| [[petanque-cluster-mapesz-cherry-pick]] | Petanque-cluster MAPESZ-örökség cherry-pick mátrix (4-dimenziós) | mapesz, boulium |
| [[touch-kiosk-idle-timeout]] | Touch-kiosk idle timeout — min 3 perc (date-picker tolerancia) | ux, kiosk |
| [[digital-signage-player-gotchas]] | Digital signage player debugging gotchas (5 pattern) | digital-signage |

---

## Frissen landed (utolsó 2 nap: 2026-05-17 → 18)

49 új wiki került be a B-1..B-7 sprint super-session sorozatban (3 super-session, 14× subagent-fanout, $0 cost). Tematikusan:

- **SV crystallization layer:** `crystallize-threshold-ramp`, `auto-propagation-confidence-gate`, `batch-preview-confirmation-pattern`, `backout-trigger-pattern`, `rollback-revert-strategy-tiers`, `sandbox-branch-mutation-isolation`, `multi-layer-safety-gate`, `env-flag-default-disabled-gate`, `hot-reload-config-pattern`, `audit-log-append-only-pattern`, `audit-md-self-referential-loop`, `session-close-ritual-pattern`, `session-end-auto-crystallization-hook`, `async-memory-consolidation-letta`
- **LLM evaluation:** `g-eval-bias-mitigation-pattern`, `llm-as-judge-evaluation-pattern`, `nli-hallucination-check-pattern`, `nli-eval-input-completeness-trap`, `dont-hallucinate-abstain-pattern`, `layered-eval-cascading-pattern`, `smart-trigger-cost-pattern`, `reranker-cost-optimization-not-size`, `hybrid-bm25-semantic-rrf-pattern`, `top-k-cross-source-corroboration`, `verification-step-before-claim`
- **Multi-agent + tool-composition:** `multi-agent-pointer-ownership-lock`, `dfsdt-backtracking-tool-composition`, `filesystem-as-state-pattern`, `clean-context-subagent-handoff`, `claude-code-session-id-per-chat-isolation`, `cli-session-id-env-var-matrix`, `vscode-extension-slash-command-naming`, `subagent-fanout-context-aware-classification`, `skill-metadata-catalog-pattern`
- **Knowledge-graph:** `memgraph-ce-feature-limits`, `memgraph-mage-vector-scale-tradeoff`, `memgraph-multi-labeling-edge-case-typedness-measurement`, `mgclient-autocommit-silent-rollback`, `two-tier-graph-extraction`, `vault-net-ingest`
- **Engineering discipline:** `vendor-feature-verify-before-workaround`, `llm-daemon-warm-pattern`, `markdown-image-url-data-exfiltration`, `skill-project-success-pattern`, `skill-project-stuck-anti-pattern`
- **Web-dev gotchas:** `nextjs-turbopack-gotchas`, `wp-elementor-bricks-json-escape-trap`

```dataview
TABLE WITHOUT ID file.link AS Wiki, file.mtime AS Updated
FROM "11-wiki"
WHERE file.mtime >= date(today) - dur(7 days) AND file.name != "Index"
SORT file.mtime DESC
LIMIT 20
```

## Orphan wiki-k (no-inbound-link, 2026-05-18 audit)

A következő 19 wiki-nek nincs inbound-wikilinkje a vault-on belül. Vagy frissen-landed és még nem propagált a 02-Projects / 05-Memory rétegekbe, vagy érdemes inbound-linket javasolni hozzá:

- `async-memory-consolidation-letta` — frissen-landed (SV-1 cluster)
- `audit-md-self-referential-loop` — frissen-landed (vault-hygiene)
- `backout-trigger-pattern` — frissen-landed (safety cluster)
- `batch-preview-confirmation-pattern` — frissen-landed (ux/safety cluster)
- `clean-context-subagent-handoff` — frissen-landed (multi-agent cluster)
- `dfsdt-backtracking-tool-composition` — frissen-landed (tool-composition)
- `elementor-repeater-media-condition-gotcha` — régebbi, érdemes a Foxxi/WP projektből linkelni
- `filesystem-as-state-pattern` — frissen-landed (anthropic SSOT)
- `llm-as-judge-evaluation-pattern` — frissen-landed (eval cluster)
- `markdown-image-url-data-exfiltration` — frissen-landed (security)
- `memgraph-mage-vector-scale-tradeoff` — frissen-landed (knowledge-graph)
- `memgraph-multi-labeling-edge-case-typedness-measurement` — frissen-landed (B-7 metric)
- `multi-agent-pointer-ownership-lock` — frissen-landed (orchestration)
- `nextjs-turbopack-gotchas` — frissen-landed (web-dev)
- `petanque-cluster-mapesz-cherry-pick` — projekt-link a `02-Projects/mapesz`-ből hiányzik
- `session-close-ritual-pattern` — frissen-landed (11.11 protokoll)
- `session-end-auto-crystallization-hook` — frissen-landed (SV-5)
- `vscode-extension-slash-command-naming` — frissen-landed (UX)
- `wp-elementor-bricks-json-escape-trap` — projekt-link hiányzik (WP-related)

**Akció:** propagation-batch a következő session-ben → propagate this Master-Index hivatkozásai az inbound-link-számot azonnal megemelik (most már mind hivatkozott innen). Re-audit ajánlott a következő `vault-cleanup` után.

---

## Mi kerül ide

- **Koncepciók** saját szavakkal (pl. "Karpathy LLM Wiki pattern", "Johnny-Decimal")
- **Playbookok** — "hogyan csináljunk X-et" (pl. "SSH deploy-key GitHub-hoz")
- **Összehasonlítások** — "Dataview vs Bases", "PARA vs Zettelkasten"
- **Mini-howtók** — rövid, lépésről lépésre receptek
- **Glosszárium** — egy-egy fogalom definíciója

## Fájl-konvenció

- Fájlnév: `<téma-címe>.md` — **nincs dátum prefix** (evergreen)
- **Kötőjelek** szóköz helyett (pl. `Karpathy-LLM-Wiki-pattern.md`)
- Frontmatter:
  ```yaml
  ---
  name: Téma címe
  type: wiki
  tags: ["#type/reference", "<téma-spec-tag>"]
  created: 2026-04-23
  updated: 2026-04-23
  source:
    - "[[10-raw/2026-04-23 — cikk]]"
    - "https://stephango.com/vault"
  ---
  ```

## Mi **nem** kerül ide

- Nyers, nem-átírt anyagok → [[10-raw/Index|10-raw/]]
- Projekt-specifikus dolgok → [[02-Projects/Index|02-Projects/]]
- Infra-tények amik változhatnak (port, IP) → [[05-Memory/Infrastructure]]
- Döntési indoklások → [[07-Decisions/]]

## Írási elv (Kepano stílus)

- **Rövid** — 1-2 bekezdés gyakran elég
- **Evergreen** — akkor is érvényes legyen 6 hónap múlva
- **Saját szavakkal** — ha csak copy-paste, akkor maradjon raw-ban
- **Linkeld a forrást** — raw/ fájlra vagy URL-re
- **Wikilinkeld a rokon koncepciókat** — így nő a graph-nézet értéke

## Kapcsolódó

- [[10-raw/Index]] — forrás-gyűjtemény
- [[AGENTS]] — agent setup
- [[Karpathy-LLM-Wiki-pattern]] — a meta-elv ami szerint ez működik
- [[02-Projects/Index]] — projekt dashboard
- [[06-Audits/System_Health]] — vault egészsége
