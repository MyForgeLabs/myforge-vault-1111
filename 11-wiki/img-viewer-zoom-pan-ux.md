---
name: Image viewer zoom-pan UX pattern
type: wiki
tags: ["#type/wiki", "ux", "frontend", "react", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# Image viewer zoom-pan UX

> [!todo] Bővítendő
> Pattern: sima `wheel` zoom + double-click toggle (1×↔2×) + drag-at-all-scales — KGC totem MachinePartDiagram / robbantott-keresoő pattern.

## Building blocks

- **Wheel zoom** — `onWheel` (passive: false) preventDefault + scale step (0.1–0.25)
- **Double-click toggle** — 1× ↔ 2× (vagy az adott zoom-szint ↔ fit)
- **Drag-at-all-scales** — pan akkor is engedélyezett, ha scale = 1 (több feltételes "pannable" guard helyett)
- ⚠️ React 17+ default-passive `onWheel` — explicit ref + `addEventListener('wheel', ..., {passive: false})` kell

## Kapcsolódó

- [[../08-Sessions/2026-05-12-robbantott-bra-keres|Robbantott-bra session]] — eredeti forrás
- [[../02-Projects/robbantott-kereso|robbantott-kereso projekt]]
