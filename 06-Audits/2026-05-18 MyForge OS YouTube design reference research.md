---
name: 2026-05-18 MyForge OS YouTube design reference research
type: audit
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/audit", "#type/research", "#project/myforge-dashboard"]
  - research
  - youtube
  - myforge-os
  - claude-code
  - agentic-os
  - inspiration
related:
  - "[[02-Projects/myforge-dashboard]]"
  - "[[07-Decisions/2026-05-08 Myforge OS Wave A-K dashboard expansion]]"
  - "[[11-wiki/Karpathy-LLM-Wiki-pattern]]"
status: complete
tag_backfill: 2026-05-19
---
# MyForge OS YouTube design reference research — Chase AI

> [!info] TL;DR
> A srác **Chase AI** (csatorna: `@Chase-H-AI`, **126K követő**, **624 videó**) — ő az **agentic-OS / Claude-Code-dashboard** műfaj **fő népszerűsítője** (NEM kezdeményezője, de a **legnagyobb mainstream-csatorna** rajta). A flagship videó **122K views** (`Bgxsx8slDEA` — "Stop Using Claude Code Without an Agentic OS", 2026-05-05). A 2 kért videó az **architektúra + memory + command-center** triádot mutatja be, **NEM** a saját kódot — **Obsidian + DataviewJS + skill-fájlok + Claude CLI streaming**. A teljes value-proposition `chaseai.io` workshop + `skool.com/chase-ai` paid masterclass mögött van.

---

## 1. Videó-azonosítás

### A 2 kért videó

| # | Video ID | Cím (aktuális) | Cím (oembed cache) | Date | Views |
|---|---|---|---|---|---|
| 1 | `glAoiBWVkmU` | **"The Claude Code + Obsidian Setup That Now Runs My Life"** | "This Claude Code + Obsidian Command Center is INSANE" | 2026-05-15 (3d ago) | 23,451 |
| 2 | `d86VCtQ_dN8` | **"Claude Code Has Evolved"** | (ugyanaz) | 2026-05-14 (4d ago) | 19,283 |

> [!warning] Cím-eltérés
> A `glAoiBWVkmU`-nak két címe forog — az `oembed`-cache még a régi "Command Center is INSANE"-t adja vissza, de a YouTube-page jelenleg a "Setup That Now Runs My Life"-ot mutatja. Valószínűleg A/B-teszt vagy thumbnail-rotáció.

### Forrás-bizonyíték
- `oembed`: `https://www.youtube.com/oembed?url=...` JSON → `author_name: "Chase AI"`, `author_url: "https://www.youtube.com/@Chase-H-AI"`
- `r.jina.ai/youtube.com/watch?v=glAoiBWVkmU` → "Chase AI channel, 23,451 views, posted May 15, 2026"
- `r.jina.ai/youtube.com/@Chase-H-AI/videos` → "Channel Details: 126K subscribers, 624 total videos"

---

## 2. A szerző / channel

### Chase AI ≠ "Chase Adams" (curiouslychase)
- **Csatorna-tulajdonos:** "Chase AI" (consulting cég-brand, NEM személyes csatorna). A `chaseai.io`-n szereplő personal name **valószínűleg Chase Hannegan** (egy blog-poszt szerzőjeként így jelölve — [chase-ai-blog/persistent-memory](https://www.chaseai.io/blog/claude-code-obsidian-persistent-memory)). **NEM** összekeverendő **Chase Adams / curiouslychase**-szel ([github.com/curiouslychase](https://github.com/curiouslychase)) — az utóbbi a "AI-Native Obsidian Vault Setup Guide" szerzője (`curiouslychase.com/posts/ai-native-obsidian-vault-setup-guide/`), aki **a Karpathy-pattern fő dokumentátora** (000-OS / 100-Periodics / 300-Entities mappa-séma). Chase AI YouTube-csatorna **építkezik a curiouslychase patternre** + saját business-domain skill-megközelítésre.
- **Cég:** B2B AI consulting agency, 4 phase delivery (audit / quick wins / core build / scale). Service: AI agents, n8n workflows, RAG, AI strategy. Saját pitch: `chaseai.io`.
- **Monetization:** Skool paid masterclass `skool.com/chase-ai` ($98 ár-pont, kommentár-feedback szerint), free community `skool.com/chase-ai-community`, consultation `chaseai.io`.

### A "kezdeményezte-e a műfajt" kérdés
- **Részben.** A Karpathy-RAG-koncepció (`raw/` + `wiki/` mappa-pár) **Karpathy Twitter-posztból** származik (cca. 2026-03). A **curiouslychase** dokumentálta first-class playbook-ként. Chase AI **a YouTube-előfizetők tömegét felé exponálta** — 122K-244K views videókkal, "Claude Design is INSANE" 242K views.
- **Mainstream-trigger:** Chase AI **"Claude Code Agentic OS" terminológiát ő honosította meg** (a 122K-s `Bgxsx8slDEA` videó cím-frázis), és a **6 Levels of Claude Code** + **7 Levels of RAG** framework-jei a referens-anyaggá váltak (`mejba.me`, `mindstudio.ai`, `aiproductivity.ai` mind hivatkozik rá).
- **Időrend:** `Claude Code Agentic OS = UNSTOPPABLE` (84K, 2026-04-22) → `Stop Using Claude Code Without an Agentic OS` (122K, 2026-05-05) → `Claude Code Just Got a Dashboard` (53K, 2026-05-11) → `Claude Code Has Evolved` (19K, 2026-05-14) → `Setup That Now Runs My Life` (23K, 2026-05-15). **A "Claude Code dashboard" műfaj 4 hetes**, és Chase AI **a fő growth-driver** rajta.

### 5 további releváns videó tőle (a 2 kérten kívül)

| Cím | Views | Date | URL | Miért releváns |
|---|---|---|---|---|
| **Stop Using Claude Code Without an Agentic OS** | **122K** | 2026-05-05 | `Bgxsx8slDEA` | Flagship — **3-step framework** (Architecture / Memory / Observability) — ez a master-pattern |
| **Claude Code Just Got a Dashboard** | **53K** | 2026-05-11 | `7zxIeRWasbc` | **Anthropic Agent View** demo + reakció, terminál-multiplexer-vita |
| **Claude Code Agentic OS = UNSTOPPABLE** | **84K** | 2026-04-22 | `pfPi04pIfaw` | Eredeti 4-layer framework (memory / skill fleet / automations / dashboard) |
| **Karpathy's Obsidian RAG + Claude Code = CHEAT CODE** | **113K** | 2026-04-04 | `OSZdFnQmgRw` | A vault-szervezés rajzolata — `raw/`+`wiki/`+`_master-index.md` |
| **The 7 Levels of Claude Code & RAG** | 53K | 2026-04-12 | `kQu5pWKS8GA` | Tier-osztályozás (L1 prompt → L7 agentic-graph-RAG) — mérce |

---

## 3. Videó-transcript + technikai összegzés

> [!warning] Transcript-acquisition limit
> `yt-dlp` 2024.04.09 verziójú a szerveren + YouTube "Sign in to confirm not a bot" blokk aktív. Az `yt-pipeline` script ezért fail-el. Transcript-letöltés helyett a `r.jina.ai/<youtube-URL>` proxy-val szereztünk **chapter-timestamp + pinned-comment + reaction-feedback** szintű meta-infót, + a `chaseai.io/blog/*` cikkekből rekonstruált pattern-leírást. (A YouTube auto-CC textuális tartalma nem volt elérhető — ezért a UI-elem-leltár **a blog-cikkekből + a `aiproductivity.ai` 3rd-party recap-ből + a `jarvis-dashboard` clone-projektből** rekonstruált.)

### Videó 1 — "The Claude Code + Obsidian Setup That Now Runs My Life" (`glAoiBWVkmU`, 23K)

**Chapters** (forrás: `r.jina.ai`, chapter-extractor)
```
0:00 - Intro
0:34 - Command Center
4:19 - Customize
9:30 - Architecture
15:44 - Outro
```

**3-mondatos technikai összegzés:**
1. A videó **a Command Center-t demózza** (0:34-4:18) mint Obsidian-vault gyökerében élő `Dashboard.md` típusú DataviewJS-aggregátort, ami **skill-eket, agent-fleet-eket, session-aktivitást, daily-tasks-ot** mutat egy lapon — a Claude Code CLI-streaming-et **react-markdown-os live-output panel-be** renderelve.
2. Az architektúra-szegmens (9:30+) az **`000-OS/Claude/skills/`** + **`300-Entities/Projects/`** + **`200 Notes/AI Log/`** **mappa-szervezést** mutatja (Johnny-Decimal-szerű prefix), ahol a Claude CLI session-log-ok markdown-ba mentődnek, és a dashboard ezeket dataview-zal aggregálja.
3. A "Customize" rész (4:19-9:29) **YAML-frontmatter-vezérelt skill-konfigot** mutat — minden skill `~/.claude/skills/<name>/SKILL.md` fájlban él, `context_hint` field-del, ami a dashboard textarea placeholder-ébe kerül.

**Forrás-snippet** (curiouslychase.com `ai-native-obsidian-vault-setup-guide`, dashboard-arch szekció):
> "Teams overview / Upcoming events (3-month view) / Open action items (dataview query, max 20) / Active goals (dataview from 300 Entities/Goals) / Active projects (dataview from 300 Entities/Projects)"

### Videó 2 — "Claude Code Has Evolved" (`d86VCtQ_dN8`, 19K)

**Chapters**
```
0:00  - The Real Power
3:35  - Creating the Backbone
10:42 - What's the Point of Obsidian
13:53 - The Command Center
17:30 - The Landscape
```

**3-mondatos technikai összegzés:**
1. A videó **a Chase-féle "dashboard-first ANTI-pattern"-t cáfolja** (lásd `chaseai.io/blog/agentic-os-skill-backbone-not-dashboard`): a dashboard csak **"10% value-add"**, a valódi érték a **skill-backbone** (`000-OS/Claude/skills/` mappa, business-domain-okra bontva: sales / marketing / content / ops).
2. A "Creating the Backbone" szegmens (3:35+) **skill-fájlok auto-discoveryt** mutat — a Claude `~/.claude/skills/*/SKILL.md` frontmatter-ből nyeri ki a metadata-t (name, description, context_hint), és **slash-command-ként hívható** (`/skillname`).
3. A "Command Center" szegmens (13:53+) **valószínűleg ugyanazt a dashboard-build-et mutatja**, mint az 1-es videó — de mások a hangsúlyok: itt a **skill-execution stream + run-history sidebar** kerül előtérbe, nem a daily-tactical-view.

**Forrás-snippet** (`chaseai.io/blog/agentic-os-skill-backbone-not-dashboard`):
> "Your Claude Code agentic OS isn't working because you built it in the wrong order. The dashboard is a 10% value-add that only pays off once the bottom 90% (skills, automations, memory) is real."

> "The skill backbone is invisible, takes weeks to refine, and doesn't screenshot well. Doesn't matter — it's where the value lives."

---

## 4. 7 konkrét UI/UX building-block (NEM kreatív inspiráció — pixel-pontos elem)

> [!success] Ezek mind átemelhetők a `/opt/agent-dashboard/web` Next.js 16 + React 19 stack-be — a `command-centre` GitHub-clone (`JoeyBream/command-centre`) **pontosan ezt a stack-et használja** (Next 16 App Router + React 19 + Tailwind 4 + react-markdown + Claude CLI streaming SSE). 1:1 példa.

1. **Skill-card grid layout** — minden skill egy kártya, grid-be rendezve. Forrás: `JoeyBream/command-centre` README + Chase video `glAoiBWVkmU @ 0:34`. Minden card: `{icon, title, description, last-run-timestamp, "Run" button}`.

2. **Expanded skill panel + textarea + Run/Stop dual-button** — a card kibővül, textarea-t mutat a context-input számára, alatta `Run` (zöld, primary) és `Stop` (piros, destructive). Forrás: `command-centre` README — "Red Stop button terminates running operations", "context_hint placeholder from YAML frontmatter".

3. **Live streaming output panel + markdown render** — `react-markdown` komponens, ami **SSE-en érkező** Claude CLI output-ot streameli ("pulsing dots before first output", "terminal-style cursor while streaming"). Forrás: `command-centre` README.

4. **Run history sidebar (last 20 runs, restore-capable)** — bal vagy jobb oldali sidebar, kattintható elemekkel (timestamp + skill-name + status). "Restore" gomb visszatölti a textarea-t + scrollozza a logot. Forrás: `command-centre` README.

5. **Elapsed timer + status badge** — futó skill mellé "Running 00:14" felirat + színes badge (`running` / `success` / `error` / `cancelled`). Forrás: `command-centre` README — "Elapsed timer showing seconds since execution started".

6. **DataviewJS aggregator panel ("Active Projects" / "Open Tasks" / "Goals")** — Obsidian-mintára: bal-oldali sidebar vagy felső sáv, ami **több source-ot aggregál** (sessions/, projects/, tasks/, decisions/). Forrás: `curiouslychase.com` guide + video `glAoiBWVkmU @ 9:30`.

7. **Frontmatter-vezérelt skill-metadata** — minden skill `~/.claude/skills/<name>/SKILL.md` formátum, YAML frontmatter (`name`, `description`, `context_hint`, `tags`), és a dashboard ezeket **fájlrendszerből auto-discover**-eli. Forrás: `command-centre` README — "Reads skill metadata from `~/.claude/skills/*/SKILL.md` frontmatter".

**Plusz 3 a JARVIS-clone-ból** (`AndrewKochulab/jarvis-dashboard`) — Chase-pattern alapú külső clone-projekt, már ÉLES Obsidian dashboard:

8. **GitHub-style 30-day activity heatmap** — sessions / tokens / cost / model-breakdown négyzeteken. (Hasznos pl. költség-monitoringra.)
9. **Agent Card (live status, token-meter, model-badge, cost-rolling-sum)** — több futó Claude session = több kártya.
10. **Voice command + STT widget** — `whisper-cpp` STT + `piper` TTS — opcionális, mobilra hasznos. (Skip-pelhető komponens, ha nincs voice-igény.)

---

## 5. Mit lehet átvenni vs. mit NEM

### Átvehető (10 elem)

| # | UI-elem / pattern | Miért fits a `/opt/agent-dashboard/web`-be |
|---|---|---|
| 1 | **Skill-card grid + filter/search** | Wave A-K **80+ komponens** közt navigálni — pont ez a use-case |
| 2 | **Expanded panel + textarea + Run/Stop** | Voice-input + bypass-mode flip Wave-ekben — drop-in pattern |
| 3 | **SSE streaming output + react-markdown** | Next 16 App Router-rel natívan ([`stream-json` from Claude CLI](https://docs.anthropic.com/claude-code) — `command-centre` mintát követheti |
| 4 | **Run history sidebar (last N)** | Tailscale-only multi-user esetén audit-fontosság |
| 5 | **Elapsed timer + colored status badge** | Hosszú futó skill-ek (yt-pipeline, vault-embed) feedback |
| 6 | **DataviewJS-mintájú aggregator panel** | A vault-unkban már megvan a [[02-Projects/Index]] + [[04-Tasks/Backlog]] — UI-ban összesíteni 1 lapon |
| 7 | **YAML-frontmatter skill-metadata pattern** | Már megvan (`~/.claude/skills/`), csak a dashboard auto-discovery-jét kell hozzákötni |
| 8 | **Bal-oldali tab-architecture** (Wave A-K rendezésére) | Chase patternben **mappa-prefix → tab-csoport** (000/100/200/300/400/999) |
| 9 | **GitHub-style 30-day heatmap** (sessions/tokens/cost) | A 8-tengelyű SV-roadmap-ünknek vizuális KPI-felület |
| 10 | **Cmd+Enter keyboard-shortcut + URL-hash state persistence** | Power-user-features, kis kód, nagy UX-win |

### NEM átvehető (5 elem)

| # | Mit | Miért nem |
|---|---|---|
| 1 | **Anthropic Agent View** (`7zxIeRWasbc` videó tárgya) | **Az Claude Code CLI BUILT-IN** Anthropic-feature (`/agent-view`), NEM Next.js komponens — terminal-only |
| 2 | **localhost:127.0.0.1 binding** (`command-centre` default) | A mi setup-unk **Tailscale-multi-server**, multi-user — bind `0.0.0.0` + Tailscale-ACL kell, NEM `127.0.0.1` |
| 3 | **Voice command (`piper` neural TTS + `whisper-cpp` STT)** | Headless server, root user — voice nem use-case. Maradjon a Wave G voice-Web Speech API |
| 4 | **Tauri 2.0 + SwiftUI mobil-natív app** (JARVIS-clone) | Multi-platform overhead — a Next.js PWA elég, ne menjünk natív irányba |
| 5 | **Skool-masterclass paywall + community-CTA** | Sales-funnel pattern, NEM dashboard-feature — irreleváns |

---

## 6. Implementációs javaslat — 7 lépés (becsült idő)

> [!info] Cél: Wave A-K MyForge OS dashboard-ot fokozatosan **"Chase-style command-center"** formába hozni
> A jelenlegi setup (`/opt/agent-dashboard/web` Next 16 + React 19, 56 commit, 80+ komponens, Tailscale-only) **már 70%-ban** ezt a patternt követi (lásd [[07-Decisions/2026-05-08 Myforge OS Wave A-K dashboard expansion]]). Az alábbi lépések a **hiányzó 30%-ot** célozzák.

| # | Lépés | Becsült idő | Függőség |
|---|---|---|---|
| 1 | **Skill auto-discovery service** — `~/.claude/skills/*/SKILL.md` fájlok beolvasása, YAML-parse, frontmatter-validáció, in-memory cache + file-watch (chokidar) | **2-3h** | — |
| 2 | **Skill-card grid komponens** (`<SkillCard>` + `<SkillCardGrid>`) — Tailwind 4-ben, search-input + tag-filter, ScrollArea | **3-4h** | (1) |
| 3 | **Expanded skill panel + textarea + Run/Stop** — modal vagy slide-out drawer, `context_hint` placeholder, Cmd+Enter shortcut, URL-hash state persistence | **3-4h** | (2) |
| 4 | **SSE streaming endpoint + react-markdown live output** — Next 16 App Router `app/api/skill/run/route.ts` (Edge runtime), `child_process.spawn('claude', ['--output-format', 'stream-json', ...])`, EventSource client-side | **5-7h** | (3) |
| 5 | **Run-history sidebar + SQLite persistence** — `runs.db` (better-sqlite3), last-20 query, restore-capability, status-badge színek | **3-4h** | (4) |
| 6 | **DataviewJS-aggregator panel ("Active Sessions / Open Tasks / Goals")** — `/root/obsidian-vault/02-Projects/Index.md` + `/04-Tasks/Backlog.md` parsing-server-side, ISR + cron-revalidate | **4-5h** | — |
| 7 | **GitHub-style 30-day heatmap** — d3-cal-heatmap vagy `react-calendar-heatmap`, source: SQLite runs.db + token-cost log | **3-4h** | (5) |

**Összesen:** **~23-31 munkaóra** (3-4 fókuszált nap). Wave-prefix javaslat: **Wave L** (Skill Auto-Discovery), **Wave M** (Command-Center Refactor), **Wave N** (Activity Heatmap & Analytics).

---

## 7. Forrás-hivatkozások

### YouTube (primer)
- [`glAoiBWVkmU`](https://www.youtube.com/watch?v=glAoiBWVkmU) — "The Claude Code + Obsidian Setup That Now Runs My Life" / "Command Center is INSANE" — chapter 0:34, 4:19, 9:30
- [`d86VCtQ_dN8`](https://www.youtube.com/watch?v=d86VCtQ_dN8) — "Claude Code Has Evolved" — chapter 3:35, 10:42, 13:53, 17:30
- [`Bgxsx8slDEA`](https://www.youtube.com/watch?v=Bgxsx8slDEA) — "Stop Using Claude Code Without an Agentic OS" (122K, flagship)
- [`pfPi04pIfaw`](https://www.youtube.com/watch?v=pfPi04pIfaw) — "Claude Code Agentic OS = UNSTOPPABLE" (84K, eredeti framework)
- [`7zxIeRWasbc`](https://www.youtube.com/watch?v=7zxIeRWasbc) — "Claude Code Just Got a Dashboard" (53K, Agent View reakció)
- [`OSZdFnQmgRw`](https://www.youtube.com/watch?v=OSZdFnQmgRw) — "Karpathy's Obsidian RAG + Claude Code = CHEAT CODE" (113K)

### Chase AI blog (technikai mélység)
- [`agentic-os-skill-backbone-not-dashboard`](https://www.chaseai.io/blog/agentic-os-skill-backbone-not-dashboard) — a "dashboard nem first" érvelés
- [`claude-code-agentic-os-framework`](https://www.chaseai.io/blog/claude-code-agentic-os-framework) — master-pattern, 3 gap (memory/consistency/access)
- [`6-levels-of-claude-code`](https://www.chaseai.io/blog/6-levels-of-claude-code) — L1 prompt → L6 orchestrator
- [`karpathy-obsidian-rag-claude-code`](https://www.chaseai.io/blog/karpathy-obsidian-rag-claude-code) — `raw/`+`wiki/` mappa-pattern
- [`claude-code-obsidian-persistent-memory`](https://www.chaseai.io/blog/claude-code-obsidian-persistent-memory) — szerző: Chase Hannegan
- [`chaseai.io/workshop`](https://www.chaseai.io/workshop) — Agentic OS Workshop curriculum

### Külső kontextus
- [`curiouslychase.com/posts/ai-native-obsidian-vault-setup-guide/`](https://curiouslychase.com/posts/ai-native-obsidian-vault-setup-guide/) — **Chase Adams** (≠ Chase Hannegan!), 000-OS/100-Periodics/300-Entities mappa-séma — **első dokumentátor**
- [`github.com/JoeyBream/command-centre`](https://github.com/JoeyBream/command-centre) — Next 16 + React 19 + Tailwind 4 reference-clone, **pontosan a mi stack-ünk**
- [`github.com/AndrewKochulab/jarvis-dashboard`](https://github.com/AndrewKochulab/jarvis-dashboard) — DataviewJS Obsidian-implementáció, 13 widget, voice + analytics
- [`aiproductivity.ai/news/obsidian-claude-code-command-center-dashboard/`](https://aiproductivity.ai/news/obsidian-claude-code-command-center-dashboard/) — 3rd-party recap

---

## 8. Open kérdések (user-eldöntés)

1. **Wave-prefix:** L/M/N (folytatólagos) vs. külön "Refactor R" prefix? — javaslat: **L/M/N folytatólag**.
2. **Skill auto-discovery scope:** csak `~/.claude/skills/` (243+ skill, [[05-Memory/Skill-map]]) vagy plus `/root/obsidian-vault/000-OS/Claude/skills/` is? — javaslat: **mindkettő, layered**.
3. **SSE streaming Claude CLI binary:** `claude` (Claude Code) vagy a vault-os `subagent-fanout` wrapper? — javaslat: **közvetlen `claude --output-format stream-json`** (a fanout-pattern másik szint).
4. **Tailscale-multi-user authn:** bind `0.0.0.0` + `X-Tailscale-User` header-trust (Tailscale-serve mintára) vagy session-cookie + manual login? — javaslat: **Tailscale-trust header** (zero-friction).
5. **Voice / mobile widgets:** Wave G már voice-Web-Speech-API alapú — átmenjünk-e `whisper-cpp`-re a JARVIS-clone-mintára, vagy maradjon böngésző-natív? — javaslat: **maradjon Web Speech**, ne nyissunk Tauri/natív irányt.

---

## 9. Validation log

| Időbélyeg | Eszköz | Eredmény |
|---|---|---|
| 2026-05-18 ~09:00 | `yt-pipeline glAoiBWVkmU` | FAIL — "Sign in to confirm not a bot" |
| 2026-05-18 ~09:00 | `yt-dlp -j ...` | FAIL — Bot-block (yt-dlp 2024.04.09 outdated) |
| 2026-05-18 ~09:05 | `WebFetch oembed/?url=...` | OK — `author_name: Chase AI` |
| 2026-05-18 ~09:05 | `WebFetch youtube.com/watch?v=...` | FAIL — csak footer-content (consent-gate / German redirect) |
| 2026-05-18 ~09:10 | `WebFetch r.jina.ai/<youtube-url>` | OK — chapter-timestamps + comments + description |
| 2026-05-18 ~09:10 | `WebFetch chaseai.io/blog/*` | OK — minden article-content kibontva |
| 2026-05-18 ~09:15 | `WebFetch github.com/JoeyBream/command-centre` | OK — README + tech-stack confirm |
| 2026-05-18 ~09:15 | `WebFetch aiproductivity.ai/news/...` | FAIL — HTTP 403 |
| 2026-05-18 ~09:15 | `WebSearch "Chase AI" + variants` | OK — channel-context + clone-projects |

---

## 10. Záró összefoglaló

A user által megjelölt 2 videó **Chase AI** (`@Chase-H-AI`, 126K követő) **Claude-Code-Agentic-OS / Obsidian command-center** sorozatának **legfrissebb 2 darabja** (2026-05-14 + 2026-05-15). A csatorna **a műfaj fő mainstream-népszerűsítője**, NEM a kezdeményezője — az alap-pattern **Karpathy / curiouslychase**-tól származik (mappa-prefix + `raw/wiki/` szétválasztás), de Chase **a "skill-backbone + dashboard"-frame-et népszerűsítette**, és **122K view-s flagship-pel mainstream-be vitte**.

A 2 videó **vizuális inspirációja** a `JoeyBream/command-centre` GitHub-clone-ban **már nyíltan publikált pontos stack-en** (Next 16 + React 19 + Tailwind 4 + react-markdown + Claude CLI SSE-streaming) — ezt **drop-in lehet adaptálni** a `/opt/agent-dashboard/web`-re. **10 building-block átvehető**, **5 NEM** (Anthropic Agent View, localhost-bind, voice, Tauri-natív, Skool-paywall).

**Becsült integration-effort:** **~23-31 munkaóra (3-4 fókuszált nap)**, Wave L/M/N prefix-szel. **Kockázat:** alacsony — a stack 1:1 egyezik, csak a komponens-design + skill-auto-discovery + SSE-streaming a hiány.

> [!success] Next action
> User-eldöntés a 8. szekció 5 open kérdésén → Wave L story-card létrehozása → [[04-Tasks/Backlog]]-ba.
