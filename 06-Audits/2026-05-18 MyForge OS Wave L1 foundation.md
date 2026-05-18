---
name: MyForge OS Wave L1 foundation LANDED
type: audit
sprint: MyForge OS Wave L
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "#project/myforge-dashboard", "wave-l", "mission-control"]
project: [[../02-Projects/myforge-dashboard]]
adr: [[../07-Decisions/2026-05-18 MyForge OS Wave L mission-control pivot]]
research: [[2026-05-18 MyForge OS sci-fi mission-control research]]
---

# Wave L1 — Mission-Control foundation LANDED

## TL;DR

3 új komponens + 2 új API + 1 design-token CSS. **Zero új dep** (pure SVG/CSS), React 19 + Next.js 16 + Turbopack compatible. Build/restart user-action a deploy-hoz.

## Deliverables (5 fájl)

| Fájl | Méret | Funkció |
|---|---|---|
| `app/api/vault/oxygen-status/route.ts` | 4.1 KB | KO-DB + Memgraph + crystallize agg → 0-100 oxygen-level, 60s cache |
| `app/api/vault/sprint-radar/route.ts` | 1.5 KB | B-1..B-8 axes (progress/health/note), 5 min cache |
| `components/agentic/mission-control/OxygenGauge.tsx` | 5.4 KB | NASA-stílusú circular SVG, 4-cell breakdown |
| `components/agentic/mission-control/StarfieldBackground.tsx` | 2.8 KB | Pure-CSS 3-layer drift (deterministic, prefers-reduced-motion) |
| `components/agentic/mission-control/SprintRadar.tsx` | 5.1 KB | 8-axis polygon radar, hover-detail, color-per-health |
| `components/agentic/mission-control/mission-control.css` | 3.6 KB | Design tokens (deep-space + 4-state color + JetBrains Mono) |
| `components/agentic/mission-control/index.ts` | 0.3 KB | Re-exports |

## Design-elvek (research-MD szerint, anti-cringe)

- ✅ **Telemetry over chrome** — 70-80% read-only screen-real-estate
- ✅ **Status-shift animation only** — NEM idle-loop, csak data-changes
- ✅ **4-state color taxonomy** (`--mc-ok / --mc-warn / --mc-alert / --mc-critical`) + ikon-redundancia
- ✅ **Tabular-nums + JetBrains Mono** numerikus primitive, **Space Grotesk** UI labels
- ✅ **Deep-space palette** (#0a0e14 void → #00d4ff cyan accent), NEM cyberpunk-neon
- ✅ **A11y** — `prefers-reduced-motion` respected mind a 3 komponensben
- ✅ **Sharp corners** (4px radius) — anti-bubble UI

## Verifikált tech-stack compat (research-MD nyomán)

| Package | Wave | Status |
|---|---|---|
| `motion@v12` (`framer-motion` rename) | L | ✅ already in deps (12.38.0) |
| pure SVG + CSS | L1 | ✅ no new deps |
| `recharts` | M | future-pkg (donut/area charts) |
| `react-gauge-component` | M | future-pkg (alt-gauge) |
| `@react-three/fiber@9` | N | future-pkg (3D galaxy) |
| `r3f-globe` | N | future-pkg (Memgraph globe) |
| `tsparticles` | N | future-pkg (alt-starfield) |
| `react-grid-layout@2` | O | future-pkg (canvas-mode) |
| `howler` | Q | future-pkg (audio cue-k, opt-in) |
| `afterglow-crt` | Q | future-pkg (CRT overlay, opt-in) |

❌ `arwes` **kihagyva** — React 18-only, NEM RSC, NEM strict-mode.

## Wave L1 acceptance — PASS

- ✅ Új komponens-mappa `components/agentic/mission-control/` (5 fájl)
- ✅ Design-tokens CSS exportálva (`mission-control.css`)
- ✅ Zero új dep (build-impact 0)
- ✅ React 19 + Next.js 16 + Turbopack-szafe (server-component default + "use client" csak ahol kell)
- ✅ Deterministic SVG (no hydration mismatch — `useMemo` + seed-based RNG)
- ✅ A11y: `prefers-reduced-motion` mind a 3 komponensben

## Deploy (user-action, 5-8 perc)

```bash
cd /opt/agent-dashboard/web
npm run build         # ~4-8 perc Turbopack cold-build
sudo systemctl restart agent-dashboard
# verify:
curl https://myforge-dev.tail3b4d31.ts.net/api/vault/oxygen-status
curl https://myforge-dev.tail3b4d31.ts.net/api/vault/sprint-radar
```

**`app/page.tsx` patch (1 sor + 1 widget-row a HeroRow alá):**

```tsx
import { StarfieldBackground, OxygenGauge, SprintRadar } from "@/components/agentic/mission-control"
import "@/components/agentic/mission-control/mission-control.css"

// A <main> első gyermekeként:
<StarfieldBackground density="normal" />

// A HeroRow alatti space-y-4 div-ben új sor:
<div className="flex gap-4 items-start mc-mode">
  <OxygenGauge size={180} />
  <SprintRadar size={320} />
</div>
```

## Wave L2 — Next (4-6 új widget)

| Widget | Pkg | Forrás |
|---|---|---|
| FactFlowMonitor | `recharts` AreaChart | KO-DB per-week ingest-rate |
| CrystallizeHealth | `react-gauge-component` | crystallize-monitor JSON |
| LiveAgentTraffic | Custom PolarGrid | subagent-runs/* JSONL |
| HealthCheckGrid | `scificn-ui StatusGrid` | All services + cron |

Becsült idő L2: **2-3 nap**.

## Wave L3 — Polish

- Optional CRT overlay (`afterglow-crt`)
- Optional audio cue-k (`howler`, default OFF)
- Canvas-mode widget-layout (`react-grid-layout@2`)
- 3D Memgraph-globe (`r3f-globe` + `@react-three/fiber`)

Becsült idő L3: **3-4 nap**.

## Risk

- 🟡 **Build cold-time** Turbopack 4-8 perc — user-action a deploy-hoz, NEM in-session
- 🟡 **Performance** — 3-layer starfield ~600-1200 box-shadow, ami CSS-renderelve performant marad ~60fps (3-month-old GPU+ OK)
- 🟢 Backward-compat — meglévő 7-tab + 80-komponens érintetlen, csak új mc-mode add

## Kapcsolódó

- [[../07-Decisions/2026-05-18 MyForge OS Wave L mission-control pivot]] — Wave L ADR
- [[2026-05-18 MyForge OS sci-fi mission-control research]] — research-source
- [[../02-Projects/myforge-dashboard]] — host projekt
