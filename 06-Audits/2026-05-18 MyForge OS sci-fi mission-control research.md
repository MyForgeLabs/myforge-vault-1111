---
name: MyForge OS sci-fi mission-control research
type: audit
created: 2026-05-18
updated: 2026-05-18
tags:
  - audit
  - project/myforge-os
  - type/research
  - topic/ui-design
  - topic/agentic-os
related:
  - "[[02-Projects/superintelligent-vault]]"
  - "[[07-Decisions/2026-05-08 Myforge OS Wave A-K dashboard expansion]]"
  - "[[05-Memory/Dashboard-access]]"
---

# MyForge OS — Sci-Fi Mission-Control UI Pivot — Research Audit (2026-05-18)

> [!info] Forrás-stack (live)
> Next.js 16 + React 19 + Framer Motion (most már `motion@v12`) + Lucide + Zustand + Tailwind v4. 80+ komponens, 7 tab, AgenticOS branding, Wave A-K rebuild kész (56 commit). Pivot-cél: **"csillagközi vezérlőpult + oxigén-megjelenítés"** mission-control feeling, NEM-cringy módon.

> [!warning] Stack-kompatibilitási konklúzió ELŐRE
> - ✅ **Motion v12** (volt Framer Motion) — React 19 + Next 16 hivatalosan támogatott, 0 breaking change v11→v12-re
> - ❌ **Arwes** — csak React 18, NEM RSC-kompatibilis, NEM strict-mode-safe — **kihagyni**
> - ⚠️ **react-tsparticles** — React 19 működik, de a CSR-only működés Suspense-be csomagolva ajánlott
> - ✅ **scificn-ui** — React 19 + Vite konfirmált, copy-paste/shadcn CLI, Radix-alap
> - ✅ **react-launch-gauge / react-gauge-component / naikus svg-gauge** — vanilla SVG, framework-agnostic, drop-in
> - ⚠️ **Motion for R3F** — még React 18-only — 3D animációhoz nyers `@react-spring/three` ajánlott

---

## 1. Tervezési input pontok (8 axis)

### 1.1 — Inspiráció: NASA Open MCT mint északi csillag

A Wave A-K dashboard most a "Vercel-szürke + neon-accent" zónában van — a mission-control feeling nem szín-overlay-ből jön, hanem **information-architecture-ből**. NASA's Open MCT (4.2k★, NASA Ames, Mars Cube One + ASTERIA + Cold Atom Lab missziókhoz használt) három kulcs-mintát ad át:

1. **Display canvas — user-composable layout**: a UI nem fix grid, hanem drag-droppable widget-mátrix per role/per session. (lásd `react-grid-layout` 4.4)
2. **Telemetry-first, control-second**: a képernyő 70-80%-a read-only adat, csak ~20% interaktív kontroll. Wave A-K most ~50/50, túl-interaktív.
3. **"Object-oriented" widget model**: minden widget egy "domain object" (Vault, Agent, Sprint, Memgraph…) → menthető view + reusable composition. Wave A-K most tab-alapú, ezt érdemes mátrix-osítani.

→ **Action**: NEM portolni Open MCT-t (Vue-alap, NEM React), HANEM a **layout-filozófiát** átvenni: per-user composable canvas + telemetry-dominált screen-real-estate.

### 1.2 — Inspiráció: SpaceX Dragon flight UI

A SpaceX Dragon-konzol public-demók (2020 Demo-2, 2024 Polaris) három pattern-t cementeztek be a 2026-os mission-control nyelvbe:

1. **Single-source numeric primitive**: minden szám monospaced, fix-width, baseline-aligned tabular nums (`font-variant-numeric: tabular-nums`). Wave A-K most Inter-rel rendereli — váltás `JetBrains Mono` vagy `Space Grotesk` numeric-display-re.
2. **Status-by-color, NOT-by-icon**: 4 állapot (nominal/caution/warning/critical) → 4 fix-szín (cyan / amber / orange / red), ikonok csak supplementer. Lucide most spike-os, NEM mission-control kompatibilis.
3. **Circular gauge dominance**: oxigén / üzemanyag / battery / pressure mind kör-skála. SpaceX-inspirált React komponens létezik: `react-launch-gauge` (D3-alap, Michael Lyons, 145★).

### 1.3 — Inspiráció: Retro-Futurism 2026 trend

A Lucky Graphics 2026 style-guide szerint az **aesthetic paradox** (CRT scanline + Y2K gradient + AI-driven layout) az év fő irányzata. Konkrét beépítendő elemek:

- **Subtle scanline overlay**: 3px gradient stripe `repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,0.05) 2px 3px)` (NE 100% opacity, csak 5-8%)
- **Phosphor-glow text-shadow**: `text-shadow: 0 0 8px currentColor` az aktív státusz-numerikákon (csak >18px font-size-on)
- **CRT vignette**: radial-gradient mask a viewport-szegélyeken (3-5% opacity, NEM látszik tudatosan)

→ Aggregát: `afterglow-crt` (HauntedCrusader, 320★, pure-CSS, 0 WebGL) drop-in opt-in toggle-ként (egy ctx-provider `<CRTMode enabled={user.pref.crtOverlay} />`).

### 1.4 — Színpaletta: deep-space telemetry

NEM cyberpunk-neon. NEM Vercel-szürke. A mission-control "neutrum-háttér + szelektív accent" minta:

| Szerep | Hex | Használat |
|---|---|---|
| Void black | `#0a0e14` | App-háttér (NEM pure black — eye-strain) |
| Panel deep | `#0f1419` | Widget-background |
| Hairline | `#1c2630` | Border, divider — soha NEM rgba-fehér |
| Telemetry cyan | `#00d4ff` | Nominal status, primary numerics |
| Phosphor amber | `#ffaa00` | Caution / pending |
| Hazard orange | `#ff6a00` | Warning |
| Critical red | `#ff2d55` | Error, threshold breach |
| Ghost text | `#5a6b7a` | Secondary labels |
| Active text | `#c8d4e0` | Primary content |

Forrás: Recon Dashboard live-demo + Lucky Graphics 2026 guide + Open MCT default-theme inspekció.

### 1.5 — Typography stack

- **Numerics**: `JetBrains Mono` (tabular-nums + locked-width digits) — minden szám/timestamp/ID
- **UI labels**: `Space Grotesk` (geometric sans, baseline-friendly) — minden cím/menu/button
- **Body**: rendszer-stack `system-ui, -apple-system, …` — minden long-form leíró szöveg

Wave A-K most Inter-only — váltás 3-stack-re a brand-elem.

### 1.6 — Animation discipline (NEM gimmick)

**Szabály**: minden animáció **kötelezően status-change-hez** kötött. Idle-animation = TILTOTT (kivéve cursor-blink). Konkrét pattern:

- **Status-shift** (nominal→caution): 250ms ease-out szín-átmenet + 1× pulse (NEM loop)
- **Value-tick** (numerikus update): 80ms flash-cyan a delta-cellán, utána fade
- **Panel-mount**: 180ms slide-in + opacity 0→1, EGYSZER (NE rehydrate-kor)
- **Loading**: shimmer-bar (NEM spinner) — implicit status, NEM dekoráció

Forrás: Motion v12 docs + LogRocket "best React animation libraries 2026" — minden 2026-os benchmark a "restraint scales better than visual complexity" mantrát erősíti.

### 1.7 — Accessibility (sötét-háttér legibility)

- **Contrast ratio**: minden body-text ≥ 7:1 (`#c8d4e0` on `#0a0e14` = 11.4:1 ✓)
- **Font-weight bump**: dark-mode-on +50 weight bump (regular → medium) — 2026 dark-mode best-practice
- **Letter-spacing**: numerics-en `+0.5px tracking` — tabular-nums legibility boost
- **NE relegálj információt CSAK színre** — minden 4-state-state-nek legyen ikon/glyph fallback is

### 1.8 — Information density curve

Open MCT + SpaceX Dragon-konzol benchmark: **3 zone density-curve**:

- **Center 60%**: dense telemetry (10-15 widget visible), monitoring focus
- **Side rails 20%/20%**: navigation + chat + log-stream (lower density, scroll-friendly)
- **Top/bottom bars**: status-strip (compact one-liner ribbon), 32px-48px max height

Wave A-K most 7 tab-szal flat-strukturált — pivot: **canvas-mode** (composable grid) + **focus-mode** (single-widget zoom) toggle, NEM tab-only.

---

## 2. GitHub-repo / npm-package ajánlás (drop-in pack)

| # | Csomag | Verzió (2026-05) | React 19 + Next 16 | Mire |
|---|---|---|---|---|
| 1 | `motion` (volt framer-motion) | 12.x | ✅ Hivatalos | Animáció — meglévő `framer-motion` lecseréléséhez `npm rm framer-motion && npm i motion`, import-shift `from "framer-motion"` → `from "motion/react"` |
| 2 | `react-tsparticles` + `@tsparticles/slim` | 2.12.x | ✅ (CSR, `dynamic({ssr:false})`) | Starfield/particle BG — `twinkle` preset alap, custom `starfield` config |
| 3 | `react-gauge-component` | 2.0.29 | ✅ (peer ^18 \|\| ^19) | NASA-style circular gauge (oxigén, KO-DB capacity, sprint-health) — `type="radial"` mode |
| 4 | `react-launch-gauge` | 0.5.x | ⚠️ D3-alap (react peer ^16+), 21 commit (régi), de zero-overhead drop-in | SpaceX-inspirált thrust/altitude meter |
| 5 | `naikus/svg-gauge` (vanilla) | 1.0.x | ✅ Framework-agnostic | Minimalista, 0-dep alternative ha `react-gauge-component` túl-stylezott |
| 6 | `react-grid-layout` | 1.4.x → 2.0.0 | ✅ (2.0.0+ React 18+) | Composable canvas widget-mátrix (NASA Open MCT-szerű layout) |
| 7 | `recharts` | 2.13.x | ✅ | Radar-chart (8-axis sprint health), area-chart (KO-DB ingest-rate), line-chart (token-usage curve) |
| 8 | `@react-three/fiber` + `@react-three/drei` | R3F 9.x | ✅ React 19 | 3D Memgraph globe vagy radar-spinner (egy widget-be izolálva, NEM full-page) |
| 9 | `r3f-globe` | 1.x | ✅ (R3F 9 peer) | Live 3D adat-globusz a Memgraph 8997 entity vizualizációhoz |
| 10 | `howler.js` | 2.2.x | ✅ Framework-agnostic | Subtle audio cue-k (status-shift "blip", critical "ping") — Star Trek LCARS minta |
| 11 | `scificn-ui` (baxy5) | shadcn-stílusú copy-paste | ✅ React 19 + Vite + Tailwind | 33 retro-sci-fi komponens (Panel, NodeGraph, StatusGrid, ProgressRing) — cherry-pick 4-6 db |
| 12 | `afterglow-crt` (HauntedCrusader) | pure-CSS | ✅ Framework-agnostic | Opt-in CRT-overlay (scanline + vignette + glow) — toggle-elhető prefence |

**NE használd** (kompatibilitás okán):
- ❌ `arwes` — React 18-only, NEM RSC, NEM strict-mode
- ❌ `nygardk/react-scifi` — 8 év régi, React 15-kori experimental
- ❌ Motion for R3F — még React 18-only (három.js animációhoz használj `@react-spring/three`-t)

---

## 3. Inspiráló live-demók (videók + cikkek)

1. **Recon Dashboard (Hafidz)** — [github.com/syedmuhdhafidz/recon-dashboard](https://github.com/syedmuhdhafidz/recon-dashboard) + live: [recon-dashboard-eight.vercel.app](https://recon-dashboard-eight.vercel.app) — R3F + Tailwind 3 cybersec mission-control. **2 mondat**: CyberGlobe wireframe + particle-swarms a Memgraph-globe-bohoz közvetlen template. CRT scanline + reactive stroke-dasharray gauge a Vault-life-support widget-hez közvetlen átvehető.

2. **OpenClaw Mission Control (manish-raana)** — [github.com/manish-raana/openclaw-mission-control](https://github.com/manish-raana/openclaw-mission-control) — Convex + React real-time agent-task UI. **2 mondat**: Kanban-state agent-task vizualizáció Inbox→Assigned→In-Progress→Review→Done. A "Live agent-traffic" widget-koncepcióhoz közvetlen task-state-mapping pattern.

3. **NASA Open MCT** — [github.com/nasa/openmct](https://github.com/nasa/openmct) + [nasa.github.io/openmct](https://nasa.github.io/openmct/) — Vue, NEM portolható, DE filozófia-forrás. **2 mondat**: User-composable display canvas + integrated situational awareness pattern. A canvas-mode pivot direkt UX-referenciája.

4. **Lucky Graphics — Retro-Futurism 2026 Style Guide** — [lucky.graphics/learn/retro-futurism-2026-style-guide](https://lucky.graphics/learn/retro-futurism-2026-style-guide/) — **2 mondat**: A 2026-os "aesthetic paradox" trend: CRT scanline + Y2K gradient + AI-driven layout kombinálva modern 3D depth-szel. Konkrét hex-paletta + scanline-spec a sci-fi-mission-control irányba.

5. **Building the Agentic UI Stack — earezki.com (2026-05)** — [earezki.com/ai-news/2026-05-01-...](https://earezki.com/ai-news/2026-05-01-a-coding-deep-dive-into-agentic-ui-generative-ui-state-synchronization-and-interrupt-driven-approval-flows/) — AG-UI + A2UI protokollok. **2 mondat**: ~16 event-type SSE-stream real-time agent-observability + declarative component-tree. Az MyForge-runs/drafts/chat-tab pivot-ja: state-sync + interrupt-driven approval pattern.

6. **Designly — Animated Stars BG in React/Next.js** — [dev.to/designly/...](https://dev.to/designly/how-to-create-an-animated-space-stars-background-effect-in-react-nextjs-30p5) — **2 mondat**: tsParticles starfield preset alap-implementáció Next.js-ben. Drop-in `next/dynamic({ssr:false})`-szel + ZIndex -10 layer.

7. **Creative Navy — Mission Control Software UX Patterns** (UX Planet) — [uxplanet.org/mission-control-software-ux-design-patterns](https://uxplanet.org/mission-control-software-ux-design-patterns-benchmarking-e8a2d802c1f3) — **2 mondat**: 6-software benchmarking (OpenMCT, NavSpark, Mission Planner, …) + IA pattern-extraction. Density-curve + zone-allocation kvantitatív referenciája.

8. **Motion v12 upgrade guide** — [motion.dev/docs/react-upgrade-guide](https://motion.dev/docs/react-upgrade-guide) — **2 mondat**: 0 breaking change framer-motion v11 → motion v12 + React 19 + Next 16 support. Migration: `rm framer-motion && npm i motion` + import-shift `motion/react`.

---

## 4. Tervezési alapelvek — 6 design-principle (anti-cringy mission-control)

> [!warning] Anti-cringy szabály
> A "sci-fi feeling" NEM scanline-overlay vagy futurisztikus font kérdése — az **viselkedés-szintű mintákból** jön: idle-no-animation, status-color-discipline, telemetry-density, numerical-precision. Ha bármelyik elv hype-driven, NEM utility-driven, ki kell hagyni.

1. **Telemetry over chrome** — minden pixel-real-estate read-only adat-megjelenítés, kivéve az explicit kontroll-felület. Decorative elem (border-glow, particle-swarm) <5% screen-real-estate.

2. **Status-shift discipline** — animáció CSAK állapot-változáskor (250ms max, single-fire, NEM loop). Idle = statikus. (Open MCT alap-szabály, NASA "no-idle-motion" guideline.)

3. **Tabular-nums + monospace numeric primitive** — minden szám fix-width, baseline-aligned, JetBrains Mono. UI-labels Space Grotesk. NEM proportional-font numerikus-cellában.

4. **4-state-color taxonomy** — 4 fix szín (cyan nominal / amber caution / orange warning / red critical) + ikon-redundancia accessibility-hez. Tilos 5+ accent-color.

5. **Composable canvas over fixed tabs** — Wave A-K 7 tab-ot tab-mode + canvas-mode toggle-be alakítja. Per-user widget-layout perzisztálva localStorage-ba (vagy `~/obsidian-vault/05-Memory/Dashboard-layout.json`-ba).

6. **Subtle audio cue-k (opt-in)** — Star Trek LCARS-minta: state-shift "blip" (40ms, -24dB), critical "ping" (200ms, -18dB). Default OFF, user-toggle. NEM ambient-loop, NEM voice.

**Bonus elv** (opcionális, ha a user vállalja a brand-elemet):
7. **CRT-overlay toggle** — pure-CSS afterglow-crt-szerű opt-in scanline + vignette layer, NEM default-on, user-preferenceből kapcsolható. NE keverj WebGL-shader-CRT-t (perf-cost > brand-érték).

---

## 5. Vault-integration widget-koncepciók (8 db)

A `~/obsidian-vault` live-state ([B-1..B-7 sprint](../02-Projects/superintelligent-vault.md), Memgraph 8997 entity / 3 namespace, KO-DB 13890 fact, NotebookLM 63 source, GEPA loop, MEMORY.md) mission-control-stílusú vizualizációja:

### 5.1 — "Vault Life Support" gauge (oxygen-style)
- **Metric**: context-load-token / 5K target (B-2 lean-cat)
- **Vizu**: `react-gauge-component` radial gauge, 0-5K skála, color-bands [nominal:cyan 0-4K / caution:amber 4-4.5K / warning:orange 4.5-5K / critical:red >5K]
- **Pulse**: 1× flash session-start-kor (`vault-detect-chat-id` event-trigger)
- **Label**: "VAULT O₂ — LEAN CONTEXT BUDGET"

### 5.2 — "B-1..B-8 Sprint Radar"
- **Metric**: 8-axis SV-tengely (recursive-self-improvement / lean-cat / memory / KO-DB / RSI / entity-graph / external-knowledge / threshold-ramp) sprint-progress 0-100%
- **Vizu**: `recharts` RadarChart, 8 axis, 2 overlay (current + last-week ghost-line)
- **Source**: `02-Projects/superintelligent-vault.md` frontmatter `progress` + per-sprint MD parse
- **Label**: "SV PROGRAM TELEMETRY"

### 5.3 — "Knowledge-Flow Telemetry"
- **Metric**: KO-DB ingest-rate (fact/min, 60-perces rolling window) + crystallize success-rate
- **Vizu**: `recharts` AreaChart, dual-axis, 24-órás scrolling-window
- **Source**: `vault-ko-pending` + `vault-crystallize-monitor --json` outputja
- **Label**: "KO-DB INGEST RATE — 13,890 FACTS TOTAL"

### 5.4 — "Live Agent Traffic" (asteroid radar)
- **Metric**: running subagent-ek (general-purpose fanout, Claude Code spawn-ok)
- **Vizu**: 2D polar-plot (`recharts` PolarGrid + custom SVG), asteroid-szerű dot-ok with bearing+distance (agent-PID + uptime)
- **Source**: `ps aux | grep claude` + custom subagent-registry (lehet új script: `vault-agent-radar`)
- **Label**: "ACTIVE SUBAGENT TRAFFIC — 0 NOMINAL / 3 ACTIVE / 0 STALE"

### 5.5 — "Memgraph Pulse"
- **Metric**: entity-count (8997) + relation-count (13812) + cross-namespace activity (Chunk 2829 / SkillChunk 462 / Entity 8997)
- **Vizu**: 3D globe-mode (`r3f-globe`) — minden namespace egy continent-overlay, entity-density heatmap, real-time pulsation a recent-write-eken
- **Source**: Memgraph Bolt :7687 query (`MATCH (n) RETURN count(n)` minden namespace-en)
- **Label**: "MEMGRAPH 3.9.0 — VECTOR-INDEX 280× SPEEDUP"
- **NB**: ez a "wow" widget, izolált viewport-ban (max ~400×400px), NEM full-page

### 5.6 — "Session Mission Timeline"
- **Metric**: open 11.11 session-ök (`11.11ls` output), focused session highlighted
- **Vizu**: Gantt-szerű horizontal-bar timeline, current-time cursor (vertical line + tick)
- **Source**: `~/obsidian-vault/08-Sessions/*.md` frontmatter `created`+`status` parse + `.active-session-$CHAT_ID` pointerek
- **Label**: "MISSION-T+ {hh:mm:ss} — {focused-session-slug}"

### 5.7 — "Health-Check Status Grid"
- **Metric**: `/11.11-egeszseg` health-check 8-12 row eredménye (vault-mount, memgraph-up, symlinks, skill-count, vault-autosave-cron, …)
- **Vizu**: `scificn-ui StatusGrid` (33-komp-os library egyik komponense) — 4-state color-coded LED-mátrix
- **Source**: `11.11` shell-script JSON-output (új flag: `11.11 --json`)
- **Label**: "SYSTEM HEALTH — 12/12 NOMINAL"

### 5.8 — "Threshold-Ramp Telemetry" (crystallize control)
- **Metric**: B-1 crystallize-threshold value (`~/.vault-config/crystallize-threshold.txt`) + auto-rate + revert-rate (`vault-crystallize-monitor` 4-week window)
- **Vizu**: 3-row stack: [threshold slider 0.85-1.0] + [auto-rate sparkline] + [revert-rate sparkline]
- **Source**: `vault-crystallize-monitor --json --weeks 4`
- **Label**: "CRYSTALLIZE THRESHOLD — 1.00 SHADOW / 4-WK AUTO-RATE: ..."

---

## 6. Implementációs roadmap (3-sprint pivot)

> [!info] Wave L (proposed) — "Mission Control Pivot"
> Wave A-K befejezett, ez a következő logikus fázis.

**Sprint L1 — Foundation (1-2 nap)**:
- Migrate `framer-motion` → `motion@v12` (0 breaking)
- Install `motion`, `react-tsparticles`, `@tsparticles/slim`, `recharts`, `react-grid-layout`, `react-gauge-component`, `howler`
- Cherry-pick scificn-ui-ból 4 komponens (Panel, StatusGrid, ProgressRing, NodeGraph) → copy-paste `components/scifi/*`
- Új színpaletta a `tailwind.config.ts`-be (deep-space + 4-state-color taxonomy)
- Font-stack swap (Inter → JetBrains Mono + Space Grotesk)

**Sprint L2 — Widgets (3-4 nap)**:
- Build Widget #1 (Vault Life Support gauge) — `react-gauge-component` + B-2 token-budget API
- Build Widget #2 (Sprint Radar) — `recharts` RadarChart + `superintelligent-vault.md` frontmatter parse
- Build Widget #5 (Memgraph Pulse) — `r3f-globe` + Bolt :7687 query (CSR-only, `next/dynamic({ssr:false})`)
- Build Widget #7 (Health Status Grid) — `scificn-ui StatusGrid` + `11.11 --json`
- starfield-BG opt-in feature-flag (CSR, tsparticles twinkle preset)

**Sprint L3 — Polish + Audio (2 nap)**:
- Howler.js audio-cue layer (state-shift blip, critical ping) — default OFF, user-pref
- Afterglow-CRT overlay opt-in toggle
- Composable canvas-mode (`react-grid-layout`) + tab-mode toggle
- Widget #3 (Knowledge-Flow), #4 (Agent Traffic), #6 (Mission Timeline), #8 (Threshold-Ramp) build
- A11y audit (contrast 7:1, font-weight-bump, ikon-redundancia)

---

## 7. Risk & anti-pattern lista

| Risk | Mitigáció |
|---|---|
| **Cringy / hype-driven feeling** | Tervezési alapelv #1 (telemetry over chrome) + #2 (status-shift discipline) — minden animáció utility-okhoz kötött |
| **Perf-regress** R3F globe-tól | Single-instance, izolált viewport (max 400×400), opt-in feature-flag, `requestIdleCallback` mount |
| **Arwes telepítés** (React 18-only) | NE telepítsd — scificn-ui + custom CSS lefedi a 80%-ot |
| **CRT overlay accessibility-degradál** | Default OFF, user-preference toggle, NEM full-screen-mandatory |
| **Audio cue-k spam-elnek** | Default OFF, user-pref, max 1 cue/3sec rate-limit, debounce |
| **react-grid-layout SSR-issue** | `<WidthProvider>` + `next/dynamic({ssr:false})` wrap |
| **Motion v11→v12 migration** | 0 breaking change, csak `from "framer-motion"` → `from "motion/react"` import-shift |
| **3D globe data-firehose** | Memgraph query rate-limit 1Hz, client-side throttle, NEM real-time stream |

---

## 8. Források (összesítve)

**GitHub repos**:
- [arwes/arwes](https://github.com/arwes/arwes) — ⚠️ React 18-only (NE telepítsd)
- [baxy5/scificn-ui](https://github.com/baxy5/scificn-ui) — ✅ React 19, 33 komp, copy-paste
- [nasa/openmct](https://github.com/nasa/openmct) — filozófia-forrás (NEM React)
- [syedmuhdhafidz/recon-dashboard](https://github.com/syedmuhdhafidz/recon-dashboard) — live R3F + CRT minta-projekt
- [manish-raana/openclaw-mission-control](https://github.com/manish-raana/openclaw-mission-control) — agent-task UI minta
- [vasturiano/r3f-globe](https://github.com/vasturiano/r3f-globe) — 3D globe komponens
- [michaellyons/react-launch-gauge](https://github.com/michaellyons/react-launch-gauge) — SpaceX-inspired gauge
- [naikus/svg-gauge](https://github.com/naikus/svg-gauge) — zero-dep vanilla SVG gauge
- [HauntedCrusader/afterglow-crt](https://github.com/HauntedCrusader/afterglow-crt) — pure-CSS CRT overlay
- [Imetomi/retro-futuristic-ui-design](https://github.com/Imetomi/retro-futuristic-ui-design) — inspiráció-collection
- [tsparticles/tsparticles](https://github.com/tsparticles/tsparticles) — particle/starfield engine
- [react-grid-layout/react-grid-layout](https://github.com/react-grid-layout/react-grid-layout) — composable canvas

**npm packages** (verifikált React 19 + Next 16 kompatibilis):
- [motion](https://www.npmjs.com/package/motion) (v12.x)
- [react-tsparticles](https://www.npmjs.com/package/react-tsparticles) (v2.12.x)
- [react-gauge-component](https://www.npmjs.com/package/react-gauge-component) (v2.0.29)
- [recharts](https://recharts.org/) (v2.13.x)
- [@react-three/fiber](https://r3f.docs.pmnd.rs/) (v9.x)
- [howler.js](https://howlerjs.com/) (v2.2.x)

**Cikkek / tutorialok**:
- [Motion & Framer Motion Upgrade Guide](https://motion.dev/docs/react-upgrade-guide)
- [Animated Stars BG in React/Next.js (Designly)](https://dev.to/designly/how-to-create-an-animated-space-stars-background-effect-in-react-nextjs-30p5)
- [Mission Control Software UX Patterns (UX Planet)](https://uxplanet.org/mission-control-software-ux-design-patterns-benchmarking-e8a2d802c1f3)
- [Retro-Futurism 2026 Style Guide (Lucky Graphics)](https://lucky.graphics/learn/retro-futurism-2026-style-guide/)
- [Building the Agentic UI Stack (earezki.com)](https://earezki.com/ai-news/2026-05-01-a-coding-deep-dive-into-agentic-ui-generative-ui-state-synchronization-and-interrupt-driven-approval-flows/)
- [Best React Animation Libraries 2026 (LogRocket)](https://blog.logrocket.com/best-react-animation-libraries/)
- [Dark Mode Best Practices 2026 (Tech-RZ)](https://www.tech-rz.com/blog/dark-mode-design-best-practices-in-2026/)
- [Open MCT Documentation](https://nasa.github.io/openmct/)

**Inspiráció (galleries)**:
- [Sci-Fi Interfaces Blog](https://scifiinterfaces.com/)
- [Recon Dashboard Live Demo](https://recon-dashboard-eight.vercel.app)
- [Futuristic Dashboard Builder (Trickle)](https://trickle.so/tools/futuristic-dashboard-builder)
- [SCIFICN/UI Live](https://www.scificn.dev)

---

## Conclusió

**TL;DR**: A pivot **NEM design-overlay** (scanline+neon), HANEM **3-szintű refactor**:

1. **Information-architecture shift** — Wave A-K 7-tab flat → canvas-mode composable widget-mátrix (Open MCT minta)
2. **Numerical primitive discipline** — JetBrains Mono tabular-nums + 4-state-color taxonomy + status-shift-only-animation
3. **Vault-state telemetry layer** — 8 új widget vizualizálja a B-1..B-7 sprint + Memgraph + KO-DB + sessions live-state-jét, mind drop-in csomagokból (`recharts`, `react-gauge-component`, `r3f-globe`, `scificn-ui`)

**Stack-konklúzió**: `motion@v12` + `react-tsparticles` + `recharts` + `react-gauge-component` + `react-grid-layout` + `@react-three/fiber` + `howler.js` + scificn-ui cherry-pick — minden React 19 + Next 16 + Turbopack kompatibilis. **Arwes-ot kihagyni**.

**Brand-elem**: opt-in CRT-overlay + opt-in audio cue-k — user-preference, NEM default-on, anti-cringy.

3-sprint roadmap (L1 foundation / L2 widgets / L3 polish) ~7-8 nap dev-effort, közvetlen Wave L commit-flow.

---

> [!todo] Next actions (ha user OK)
> 1. Wave L sprint-plan kickoff: `bmad-bmm-sprint-planning` skill
> 2. `02-Projects/myforge-os.md` frissítése Wave L roadmap-pel
> 3. PoC commit: 1 widget (Vault Life Support gauge) + új színpaletta + JetBrains Mono swap → `/opt/agent-dashboard/web` branch `feat/wave-l-mission-control`
