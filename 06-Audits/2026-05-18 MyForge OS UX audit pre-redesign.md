---
name: MyForge OS UX audit — pre-redesign assessment
type: audit
sprint: MyForge OS Wave L→M pivot
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "#project/myforge-dashboard", "ux", "design-audit"]
project: [[../02-Projects/myforge-dashboard]]
context-source: 85 komponens-inventory + 27 API + 23 skill + 5 workspace + 8 tab
companion-audit: [[2026-05-18 MyForge OS YouTube design reference research]] (in-progress)
---

# UX audit pre-redesign (2026-05-18)

> Háttér: a user "Wave L1" mission-control widget-beillesztést **visszavonatta** azzal hogy "elég hülyén néz ki", és **alapvető redesign-t** kér (eredeti design + minden gomb/funkció + 2 YouTube-referencia alapján).

## Mit fed le ez az audit

Ez **lokál komponens-audit**, NEM screenshot-elemzés (a `chrome-devtools` MCP-server lehetne, de nem aktivált). A YouTube-research subagent ad konkrétebb UX-pattern-ajánlásokat — ez az audit a **vault-side context-et** szolgáltatja a synthesis-hez.

## Komponens-density baseline

| Réteg | Count | Példa |
|---|---:|---|
| **Header-strip** | 1 | `AgenticHeader` (brand + lang + help + permission-mode) |
| **Top control row** | 3 | `ActiveSessionCard`, `LiveTailStrip`, `CompactMetersRow` |
| **Intel strip** | 2 | `DailyBriefingTile`, `ProjectPulseWidget` |
| **Mode tabs** | 1 | `ModeTabs` (5 mode-pill) |
| **Skills strip** | 2 | `PinnedSkills`, `SkillsBranches` (4 branch × 5 skill) |
| **Tab-content panes** | 8 | `ClaudeCodeContent` / `ChatView` / `ShellView` / `VaultView` / `DailyNoteView` / `RunsFolderView` / `DraftsView` / `GraphView` |
| **Right sidebar** | 4 | `BacklogWidget`, `VaultPulse`, `SevenDayBars`, `RecentRuns` |
| **Bottom strip** | 3 | `CronTimeline`, `InfrastructureSection`, `BottomStatusBar` |
| **Modals / overlays** | 8 | `CommandPalette`, `VaultSearchOverlay`, `StreamingDrawer`, `FileViewerModal`, `SnippetLibrary`, `SessionSwitcher`, `ProjectSwitcher`, `AuditLogModal` |
| **Wave L1 mission-control** | 5 | `OxygenGauge`, `SprintRadar`, `StarfieldBackground` + 2 API |
| **TOTAL** | **85** | + 27 API + 23 skill |

## Mit jelent ez vizuálisan (heurisztikus értékelés)

### Erősségek (mit tart meg)
1. **Information-density** — sok adat egy screen-en, NASA / Bloomberg-stílus
2. **Command-palette** (`⌘K`) — fuzzy-search 61 item-en, ez **mission-control-szerű**, jó alap
3. **8 tab** logikus skill-csoportosítás (claude/chat/shell/vault/daily/runs/drafts/graph)
4. **5 workspace preset** — kontextus-shift gomb (morning/sprint/research/minimal)
5. **Skill suite** 23 darab branch-elve (memory/research/content/custom) — clear ontology
6. **API-coverage** 27 endpoint — minden adat backed
7. **Cron-monitor** — 10 active cron látható
8. **Audit-log** + **streaming-drawer** — operatív transparencia
9. **Dark-mode + density-toggle + zoom** — a11y figyelt
10. **PWA-manifest** + **VoiceInput** — modernek

### Lehetséges gyengeségek (mit redesign-elhetnénk)
1. **"Túl sok minden" first-render** — 85 komponens egy main-page-en, **vizuális overload** új-user-nek (a Wave L1 widget-eket "hülyén néz ki" észrevétel ennek a tünete)
2. **Brand-coherence** — Wave A-K iteratív rebuilds: brand-shift `AGENTICOS → MYFORGE OS™`, a régi 11-szekció `/legacy`-n megmaradt, de a fő-page-en is sok réteg
3. **Hierarchia** — nem világos hogy mi a **fő** (chat? sessions? skills?) és mi **támogató** (cron, hosts, infra)
4. **Color-system** — több helyen Tailwind defaults + Wave A-K-ban egyedi accent (`#FF7733` theme-color), de NEM egy unified palette
5. **Tipográfia** — Inter Tight (UI) + JetBrains Mono (numerikus, csak Wave L1-óta) — de a többi 80 komponens **NEM tabular-nums-ot** használ
6. **Animation discipline** — sok `framer-motion` (`motion@v12`) használat, de nem mindenhol indokoltán
7. **A11y** — a `prefers-reduced-motion` Wave L1-ben respected, de a Wave A-K-ban nincs explicit audit

## A "hülyén néz ki" Wave L1 root-cause-elemzés

A Wave L1 widget-rendszerem **NEM passzolt** a fő-page-be 3 okból:

1. **Vizuális mismatch** — a `mc-mode` deep-space + amber/cyan accent ütközött a fő-page Tailwind dark-mode-jával (slate + orange `#FF7733`)
2. **Layout-mismatch** — a fő-page `space-y-4` strict-rhythm volt, és az új `flex flex-wrap gap-4` row felülről "lazán" érkezett
3. **Information-context-mismatch** — az `OxygenGauge "OXYGEN 58"` egy **dekontextualizált szám** lett, semmi kapcsolódó UX-kontextus körülötte (a Wave A-K minden widget-je explicit cél-fókusszal van: `LiveTailStrip` → log-monitoring, `ActivityChart` → 30-day trend)

## Lehetséges redesign-irányok (várjuk a YouTube-research-et)

### A) Részletes refinement (kevés változás)
- Wave L1 widget-ek **ÁTSTYLE-olása** a fő-page tipográfiához (slate-szín, NEM cyan-deep-space, +tabular-nums minden numerikus elemen)
- Beillesztés a `RightSidebar`-ba mint **kompakt status-widget** (NEM dominans központi)
- **Idő**: 1-2 óra

### B) Új tab "Telemetry" (közepes változás)
- 9. tab a meglévő 8 mellé: `claude/chat/shell/vault/daily/runs/drafts/graph/telemetry`
- A `TabbedLeftPane`-ben új case `telemetry` → `TelemetryView` ami a Wave L1 + Wave L2 widget-eket teljes-page-en mutatja
- **Idő**: 3-4 óra (Wave L2 widget-ekre figyelve)

### C) Teljes "MyForge OS" rebrand a YouTube-srác mintájában (nagy változás)
- A `app/page.tsx` újrahúzva a referencia-design alapján
- A meglévő 85 komponens újrasztruktúrálva (egyik se törölve, csak újra-rendezve)
- Külön Wave M (3-5 nap) sprint
- **Idő**: 3-5 nap (1 sprint)

## Funkcionális hibák / nem-működő részek (smoke)

Ezt a YouTube-research subagent-tel együtt MAJD végzünk **(külön E2E-smoke-test)**. Jelenleg ismert:

| Komponens | Status | Megjegyzés |
|---|---|---|
| `/api/vault/oxygen-status` | ⚠️ 2/4 critical | Memgraph `mgclient` venv-path issue Node child-process-ben |
| `/api/vault/sprint-radar` | ✅ OK | Static-ish data (audit-MD-ből) |
| `/api/vault/diff`, `/pulse`, `/tree`, `/grep`, `/file`, `/graph` | ✅ OK | Wave G + Wave I-ben tesztelt |
| `PWA icon-{192,512,maskable}.png` | ✅ Fixed | ImageMagick generálta 10:04-kor |
| `content-script.js` console-error | ⚠️ Ignore | Browser-extension noise |
| Memgraph integráció | ⚠️ Tab-szint | A `/graph` view használja-e? E2E-smoke szükséges |

## Acceptance criteria a redesign-hoz (megalapozó kérdés)

A user-rel egyeztetendő (a YouTube-research output után):

- [ ] **Scope** — Refinement (A) / Új tab (B) / Teljes rebrand (C)?
- [ ] **Idő-budget** — 1-2 óra / 3-4 óra / 3-5 nap?
- [ ] **Inspirations-priority** — A YouTube-srác design-ja **abszolút referencia** (átvenni 1:1)? Vagy **lazább inspiráció** (egyes elemek átvétele, fő struktúra megőrzése)?
- [ ] **Risk-tolerance** — Production-stable (Wave A-K marad érintetlen, csak addon) vagy Iteratív (régi fő-page archiválható `/legacy-v2`-be)?
- [ ] **Mit törlünk?** — A 85 komponensből van-e valami amit a user már **NEM használ** (és törölhető)? Pl. `/legacy` 11-szekció — törölhető-e?

## Kapcsolódó

- [[../07-Decisions/2026-05-18 MyForge OS Wave L mission-control pivot]] — eddigi roadmap
- [[2026-05-18 MyForge OS sci-fi mission-control research]] — Wave L1 research input
- [[2026-05-18 MyForge OS YouTube design reference research]] — YouTube-research (in-progress)
- [[2026-05-18 MyForge OS Wave L1 foundation]] — eddigi Wave L1 deliverables
- [[../02-Projects/myforge-dashboard]] — host projekt
