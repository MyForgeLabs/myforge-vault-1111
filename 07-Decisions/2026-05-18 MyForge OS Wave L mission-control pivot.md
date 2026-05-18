---
name: MyForge OS Wave L — Mission-Control pivot
type: decision
sprint: MyForge OS dashboard
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/decision", "#project/myforge-dashboard", "design", "ui-pivot"]
status: 🟡 active
context-source: [[../02-Projects/myforge-dashboard]]
research-source: [[../06-Audits/2026-05-18 MyForge OS sci-fi mission-control research]]
---

# MyForge OS Wave L — Mission-Control pivot

## Háttér

A MyForge OS (`/opt/agent-dashboard/web`, Tailscale-only) Wave A-K rebuild kész (56 commit, 80+ komponens, 7 tab). Most a **vault-meta sprint output-jainak vizualizációja** + **"csillagközi vezérlőpult" UX-pivot** következik (Wave L → Wave Q).

User-intent: *"oxigént megjeleníteni" + "látványosabban" + "csillagközi vagy valami szuper" + "tényleg ilyen vezérlőpult".* → **Mission-control feeling** (NASA / SpaceX-stílusú), **NEM cringe-szintű sci-fi**, hanem **utility-vel + telemetry-density-vel**.

## Mit kínál a vault most amit a dashboard MÉG NEM mutat

10 új integrációs lehetőség (összes ÉLES infra, csak az API + widget hiányzik):

| # | Vault-feature | Új API-endpoint | Widget-koncepció |
|---|---|---|---|
| 1 | **Memgraph entity-graph** 8997 entity / 28.9% typed | `/api/vault/memgraph` | **Knowledge Galaxy** — 3D rotating entity-cluster, color-coded per :Concept / :Decision / :Sprint |
| 2 | **KO-DB facts** 13890 fact / 126 predicate | `/api/vault/ko-db` | **Fact-flow telemetry** — per-week ingest-rate, predicate-distribution donut |
| 3 | **B-1 crystallize-log** (auto-prop / batch / discard ratio) | `/api/vault/crystallize-monitor` | **Crystallize health-meter** — auto-rate gauge + per-target threshold heat-map |
| 4 | **NotebookLM cross-projekt** 63 source | `/api/vault/notebooklm` | **Cross-projekt synthesis radar** — 8-axis tab, query-ready button |
| 5 | **Vault-search semantic** (native vector, p95 sub-ms) | `/api/vault/search-semantic` | **Holo-search** — full-screen overlay, particle-bg, type-as-you-search |
| 6 | **Vault-skill-search** 462 SkillChunk | `/api/vault/skill-search` | **Skill armory** — sci-fi inventory grid, category-cluster |
| 7 | **B-7 entity-graph types** Concept/Decision/Sprint | `/api/vault/entity-graph` | **Tipizáltság orb** — 28.9% typed → animált progress, target 50% |
| 8 | **GitHub-trending recurrence** + cherry-pick | `/api/vault/trending` | **External-radar** — incoming repo "asteroids", cherry-pick "tractor-beam" action |
| 9 | **GEPA Pareto-improvement** state | `/api/vault/gepa-state` | **RSI Pareto-front** — candidate-evolution timeline, +14.3% halo |
| 10 | **Shadow-monitoring** (NLI + Coherence) | `/api/vault/shadow-monitor` | **Life-support gauge** — NLI agreement-rate + Coherence FP-rate, "oxygen-tank" stílusú |

## Design-alapelvek (NEM cringe-sci-fi)

| Elv | Mit jelent | Mit NEM jelent |
|---|---|---|
| **Telemetry-density** | Sűrű numerikus info, NASA-féle "számoszlop" | Random graph-bloat |
| **Deep space + amber/cyan accent** | Sötét-háttér + 2-3 accent szín | Neon-color overload |
| **Animation discipline** | Csak status-shift-en (új-data érkezett, threshold-átlépés) | Loops + hover-bling |
| **Sound design opcionális** | Halk "click" / "alert"-on, mute-able | Üvöltő sci-fi audio |
| **Mission-control HUD overlay** | Permanent top-strip telemetry (CPU/RAM/Memgraph-latency/cron-state) | Floating widgets pop-up-ok |
| **Information-architecture-first** | Minden widget egy konkrét kérdést válaszol | Eye-candy without function |

## Wave L → Wave Q roadmap

### Wave L — Backend API (Week 1)
- 5 új API-endpoint: `/api/vault/{memgraph, ko-db, crystallize-monitor, notebooklm, entity-graph}`
- `lib/vault-extended.ts` — Memgraph mgclient + KO-DB sqlite + jsonl-stream parser
- Idempotens cache layer (60-second TTL — a vault-state ritkán változik)

### Wave M — Mission-Control HUD layer (Week 1)
- Új `components/agentic/mission-control/` mappa
- `StarfieldBackground` — `react-tsparticles` v3 (Next.js 16 + React 19 compatible)
- `TelemetryStrip` — permanent top-bar Memgraph latency + KO-DB facts + cron-state
- `OxygenGauge` — circular animated SVG (life-support stílusú), maps `context-load tokens / 5K target` ratio
- `MissionTime` — UTC + local + uptime-from-vault-init

### Wave N — Knowledge Galaxy widget (Week 2)
- `KnowledgeGalaxy` 3D — `@react-three/fiber` + `@react-three/drei`
- Memgraph entity-cluster, 8997 entity color-coded
- Pan/zoom/rotate, click → entity-detail panel
- Performance: max 2000 entity per frame (downsample), GPU-accel

### Wave O — Telemetry-widgets (Week 2-3)
- `FactFlowMonitor` — per-week ingest-rate, predicate-distribution donut
- `CrystallizeHealth` — auto-rate gauge, per-target threshold heat-map
- `ShadowMonitorPanel` — NLI agreement-rate + Coherence FP-rate, oxygen-tank stílusú
- `GEPAParetoFront` — candidate-evolution timeline

### Wave P — External-radar + Skill Armory (Week 3)
- `ExternalRepoRadar` — GitHub-trending "asteroids", click → cherry-pick action
- `SkillArmory` — 462 SkillChunk grid, category-cluster, vault-skill-search-integrated
- `HoloSearch` — full-screen Ctrl+Shift+F overlay, particle-bg

### Wave Q — NotebookLM Cross-Projekt + sound + polish (Week 3-4)
- `CrossProjektSynthesisPanel` — 8-axis tab, Q1/Q2/Q3-template "fire" buttons
- `MissionAudio` — opcionális `howler.js` subtle click/alert/threshold (mute by default)
- Theme: `mission-control` (sötét + amber/cyan), additional density-level "telemetry-max"

## Tech-stack additions (Wave L compatible)

| Package | Purpose | Compat |
|---|---|---|
| `@react-three/fiber` | 3D entity-galaxy | React 19 ✓ |
| `@react-three/drei` | 3D helpers | React 19 ✓ |
| `react-tsparticles` v3 | Starfield/particle bg | Next.js 16 ✓ |
| `recharts` | Donut/line charts (lightweight) | React 19 ✓ |
| `howler.js` | Audio (optional) | Pure JS ✓ |

## Acceptance criteria

- ✅ 5 új API működik (smoke `curl /api/vault/memgraph` → JSON 200)
- ✅ Új `mission-control` mode preset (5 workspace-preset mellé)
- ✅ "OxygenGauge" widget vault-state-et reflexel real-time
- ✅ "KnowledgeGalaxy" 3D 2000+ entity-t mutat <60fps
- ✅ Tailscale-only access továbbra is megőrzött
- ✅ Backward-compat: a meglévő 7-tab + 80-komponens semmi NEM törik

## Risk

| Risk | Mitigation |
|---|---|
| 3D-galaxy CPU/GPU drain on low-spec Mac | `quality=low|mid|high` toggle (downsample) |
| Memgraph latency widget-fetch-en | Cache 60s, daemon-RPC reuse (vault-search-server) |
| Animation-overload accessibility issue | `prefers-reduced-motion` respect, opt-in mode |
| Sci-fi vs utility balance "cringe-zone" | Design-alapelvek (lásd fent) + iteration W17 user-feedback |

## Kapcsolódó

- [[../02-Projects/myforge-dashboard]] — host projekt
- [[2026-04-23 Claude Code Agentic OS - build plan]] — eredeti build-plan
- [[2026-04-24 MYFORGE OS dashboard — roadmap v2]] — Wave A-K roadmap
- [[../06-Audits/2026-05-18 MyForge OS sci-fi mission-control research]] — research-input (subagent által, in-progress)
