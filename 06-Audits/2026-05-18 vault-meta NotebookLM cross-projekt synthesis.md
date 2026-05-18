---
name: Vault-meta NotebookLM cross-projekt synthesis — Q1+Q2+Q3 ÉLES
type: audit
sprint: B-5
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "#project/sv", "sv-5", "notebooklm", "cross-projekt", "synthesis"]
project: [[../02-Projects/superintelligent-vault]]
notebook-id: <vault-meta-nb-id-here>
conversation-id: <nb-conversation-id-here>
sources-count: 63
---

# Vault-meta NotebookLM cross-projekt synthesis (2026-05-18)

> 🎉 **ELSŐ valós cross-projekt synthesis** a vault-meta NotebookLM-en (63 source: 62 closed session + mfl-voice-prep). A Phase 5.6 prep-szerinti 3 query (Q1+Q2+Q3) végrehajtva.

## Konfiguráció

- **Notebook:** `Vault Meta — cross-project Learnings` (`<vault-meta-nb-id-here>`)
- **Forrás-szám:** 63 (62 session-summary + mfl-voice initial push)
- **Conversation ID:** `<nb-conversation-id-here>`
- **Query-time:** ~10-15 sec per query (3 query × 3 = ~45 sec total)
- **Cost:** $0 (NotebookLM-subscription)

## Q1 — Mely tanulság ismétlődik 3+ projektben?

**8 cross-projekt recurring pattern** (forrás-citation-nel):

| # | Pattern | Érintett projektek |
|---|---|---|
| 1 | `.active-session` pointer divergencia párhuzamos környezetben | kgc-kivetit, foxxi, kinda-project, boulium, obsidian-vault (13+ incidens) |
| 2 | Subagent-fanout mass-LLM feladatokra (~30s/fájl, $0) | myforge-dashboard, rojt-s-bojt, sv-*, obsidian-vault |
| 3 | NotebookLM CLI RPC timeout + 600-karakteres csonkolás | mapesz, foxxi, kgc, mfl-voice, sv-* |
| 4 | Day-0 Skeleton-first (~5× gyorsabb Week 1) | obsidian-vault, sv-b2, sv-day0, sv-functional, sv-week1 |
| 5 | Next.js Turbopack memóriaszivárgás + static-cache | myforge, kgc-berles/weboldal, kinda-project |
| 6 | Hostinger LiteSpeed 7-napos edge-cache | foxxi, rojt-s-bojt, github-repok |
| 7 | Claude Code Safety Harness auto-blokk | myforge-os, robbantott-bra-keres, mfl-voice |
| 8 | Karpathy-féle Crystallization workflow szükségessége | vault-restructure, myforge, github-repo, obsidian-vault |

## Q2 — Mely failure-mode-ok közösek 2+ projektben?

**6 közös failure-mode**:

| # | Failure-mode | Mitigation | Wiki-státusz |
|---|---|---|---|
| 1 | `.active-session` pointer divergencia | explicit `11.11focus` / `@<slug>` argumentum | ✅ MEGOLDVA `$CLAUDE_CODE_SESSION_ID` (2026-05-17) |
| 2 | Next.js Turbopack memory-leak + `public/` cache | systemctl restart, runtime-dir manipuláció kerülése | ⚠️ skill `nextjs-turbopack` van, gotchas-wiki HIÁNYZIK |
| 3 | NotebookLM CLI RPC timeout / 600-char truncation | szekvenciális 30-60 mp delay, explicit marker prompt | ✅ `notebooklm-cli-gotchas.md` |
| 4 | Safety Harness auto-blokk (systemd, port, DB-delete) | `/tmp/` snippet → user manuál futtatás | ✅ `claude-code-harness-blocks.md` |
| 5 | Hostinger LiteSpeed 7-day edge-cache | filename-rename / `wp litespeed-purge all` activate-cycle | ✅ **MA írva** [[../11-wiki/hostinger-litespeed-cache-purge-protokoll]] |
| 6 | 🔴 **ÚJ insight:** JSON Unicode-escape Elementor/Bricks metában (`é` → `u00e9`) | regex-recovery + atomic `update_post_meta` slash-aware | ❌ **NINCS wiki, ÚJ pattern!** Foxxi+rojt-és-bojt sessions |

## Q3 — Mely tech-stack döntés ütközik / revisited 2+ projektben?

**7 tech-stack trade-off**:

| # | Döntés | Result | Projektek |
|---|---|---|---|
| 1 | Bricks Builder **vs** Elementor | **Bricks** új projekteknél (Mobile 95+ vs Elementor 66-73 plafon) | rojt-s-bojt, foxxi |
| 2 | Tailscale Serve **vs** Caddy/Traefik | **Tailscale** belső admin, **Caddy** éles webes, Traefik elvetve | myforge-*, mfl-voice, szerver-update |
| 3 | numpy-cosine **vs** Memgraph CE native vector | **Native** 280× speedup (vendor-feature-verify lecke) | sv-week1, obsidian-vault |
| 4 | PWA shell **vs** Native Expo/EAS build | **PWA** korai MVP-re, native csak haptic/push-igénynél | kinda-project, boulium |
| 5 | Tesseract LSTM **vs** PaddleOCR DBNet | **PaddleOCR** ipari robbantott ábrákon (95% → 98%) | robbantott-kereso |
| 6 | Subagent fanout **vs** szekvenciális compute | **Fanout** API-LLM-task-ra, szekvenciális CPU-embed-re | sv-week1, obsidian-vault |
| 7 | Adobe Vectorize **vs** kódolt SVG | **Kódolt SVG** web, **Adobe** csak print-master | rojt-s-bojt, foxxi |

## Mit jelent ez a Superintelligent Vault rendszernek

### Konfirmáció (a build-up jó irányba megy)

- A 8 Q1-pattern közül **6 már wiki-formátumban él** + 2 más auxiliary-pattern (Crystallization-workflow, pointer-divergencia) explicit megoldott
- A B-7 entity-graph LLM-extraction (Week 4) szempontjából ezek a recurring-pattern-ek **erős signal** — automatikusan `:Concept` típusúak kellene legyenek (jelenleg 1025 :Concept, ezek a 8 valószínűleg már benne)
- A NotebookLM cross-projekt query **mérhetően működik** — 10-15 sec per query, mind source-cited, mind magyar válasz

### Hiányosság (action-item)

- **6. failure-mode JSON Unicode-escape Elementor/Bricks**: nincs wiki, foxxi + rojt-és-bojt 4-5 session-re kiterjedő. **Új evergreen-wiki kandidát** (`wp-elementor-bricks-json-escape-trap.md`).
- **Next.js Turbopack gotchas**: skill van, de evergreen-wiki dedicated nincs (myforge + kgc + kinda 3 projekten).
- **Q3 #2 Tailscale Serve**: ez a `vault-net-watch` patternnel kapcsolatos lehet — `tailscale-serve-vs-caddy-decision-matrix.md` skeleton candidate.

## Mit jelent a munkámnak (Peti operatív szintjén)

### WP-ecosystem (foxxi + rojtesbojt + KGC-marketing — 13 session)
- Új WP-projektre **Bricks default**, NEM Elementor (Mobile-perf miatt)
- Hostinger-projektre **LSCACHE-protokoll** Day 0-tól (image-fingerprint build-script)
- WPML+ACF mirror playbook (19+16 session-evidence) instant alkalmazható

### KGC ecosystem (kgc-berles + kgc-erp + kgc-marketing — 10 session)
- Frontend: **Next.js Turbopack** care-aware (restart-protokoll documentated)
- Backend: **Postgres + sandbox-branch** safety-pattern reuse
- Auto-mode classifier safety (auto-mode explicit konfirmáció destruktív DB-műveletre)

### Robbantott-kereső (2 session, KGC integration)
- **PaddleOCR > Tesseract** confirmed (98% accuracy)
- Parts-first pipeline bug-fixek (first_table_page≥5, image-aware classify_page, conn-lock)

### MFL-Voice (1 session lezárt, P1 jövőbeli)
- TTS voice-quality scoring **G-Eval Layer 2 + NLI Layer 2.5** reuse-elhető (most már 3-rétegű eval-cascade ÉLES)

### Universal cross-projekt eszközök
- **`/usr/local/bin/vault-skill-search`** — natural-language → top-3 SKILL.md mindenhol (8-13ms native search)
- **`/usr/local/bin/vault-search`** — natural-language → top-5 wiki+session chunk (hybrid BM25+semantic, smart-rerank)
- **`/usr/local/bin/notebooklm-bootstrap-project <slug>`** — új projekt automatikus NB-bootstrap 5-perc alatt
- **`/usr/local/bin/11.11worker --task "..."`** — egy-feladat-egy-output worker (claude-code subprocess, $0 cost)

## Következő action-item-ek

| Prioritás | Action | Becsült idő |
|---|---|---|
| 🔴 P1 | `wp-elementor-bricks-json-escape-trap.md` wiki (6. failure-mode) | 15-20 perc |
| 🟡 P2 | `nextjs-turbopack-gotchas.md` wiki (#5 + Q2-#2) | 20-30 perc |
| 🟡 P2 | `tailscale-serve-vs-caddy-decision-matrix.md` wiki (Q3-#2) | 15-20 perc |
| 🟢 P3 | B-7 LLM-extraction Week 5 — igazi parent-spawn 8 batch × 800 entity (cél 50%+ tipizáltság) | 30-60 perc |
| 🟢 P3 | Backlog auto-extract a 6 failure-mode + 8 pattern-ből 04-Tasks/Backlog.md-be | 10-15 perc |

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — B-5 sprint host
- [[../11-wiki/hostinger-litespeed-cache-purge-protokoll]] — Q2-#5 wiki (ma született)
- [[2026-05-17 cross-projekt synthesis prep]] — Phase 5.6 előkészítés
- [[../11-wiki/Karpathy-LLM-Wiki-pattern]] — Q1-#8 forrás-pattern
- [[../11-wiki/claude-code-subagent-fanout]] — Q1-#2, Q3-#6 forrás
- [[../11-wiki/notebooklm-cli-gotchas]] — Q1-#3 forrás
- [[../11-wiki/memgraph-ce-feature-limits]] — Q3-#3 forrás
