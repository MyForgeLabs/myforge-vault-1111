---
name: Robbantott-kereso KGC integráció iránya — API proxy bridge
type: decision
status: decided
created: 2026-05-17
updated: 2026-05-17
tags: [decision, robbantott-kereso, kgc-berles, '#project/robbantott-kereso', '#project/kgc-berles']
---

# Robbantott-kereso ↔ KGC-Bérlés integráció iránya — API proxy bridge

## Kontextus

A [[02-Projects/robbantott-kereso]] standalone Python+FastAPI+SQLite+React+Vite projekt 2026-05-12 óta működik (98% Makita 1002BA / 76% 2106 numeric-match). Eredeti motiváció: a [[02-Projects/kgc-berles]] totem-feature "Bácsimegőrző" mintázat — szervizes szakkifejezésekkel a kollégákat tehermentesítő alkatrész-böngésző. 5 nyitott kérdés a 2026-05-12 esti session óta: melyik integráció-irány?

## Két opció

| Megközelítés | Pro | Con |
|---|---|---|
| **A) API proxy bridge** | 2 service független, deploy/restart nem érinti egymást; Python/Node stack-keverés natural; minimum invazív | 2 service-t kell menedzselni; közös user/auth nehezebb (most nincs auth-igény) |
| **B) Schema-bővítés** | 1 konszolidált rendszer; közös auth/user/admin natural | Python-Node bridge bonyolult; ingest 80s = HTTP-timeout-kockázat; ingest-pipeline újra-csomagolás CLI-vé jelentős munka |

## Döntés

**A) API proxy bridge** — 2026-05-17 user-döntés.

## Indoklás

1. **A robbantott-kereso pipeline 6-rétegű OCR-stack-kel (Tesseract + PaddleOCR DBNet + multi-validated voting) szigorúan Python-natív.** CLI-vé csomagolás + Node-spawn-bridge bonyolítaná a 80s-os OCR-process timeout-kockázattal.
2. **Az embed-flow technikailag KÉSZ a robbantott-kereso oldalán:** `EMBED_MODE` + `?embed=1&catalog=N` query-params + `postMessage('parts-cart:add')` parent-irányba + `/api/parts/{id}/snippet` CORS-allow `*.kisgepcentrum.hu`-ra. ~30 perc wire-up a kgc-berles oldalán (iframe-komponens + cart-store-add handler).
3. **A 2 service deploy-független** — robbantott-kereso saját systemd unit-tal (`robbantott-kereso-api.service` + `robbantott-kereso-web.service`), reboot-survived; kgc-berles saját `kgc-berles.service`. Egyik restart-ja nem érinti a másikat.
4. **Auth jelenleg nem kritikus** — mindkét rendszer publikus/admin nélküli most. Ha később kell, scoped API-token a kgc-berles-felé.

## Implementáció

**Robbantott-kereso oldalán (kész):**
- `EMBED_MODE` const a `frontend/src/App.tsx`-ben (`?embed=1` → tisztított UI, csak böngészés + add-to-cart)
- `?catalog=N` / `?figure=N` auto-load query-params
- `window.parent.postMessage({type:'parts-cart:add', item: {...}}, "*")` a "Kosárba" gombnál
- `/api/parts/{id}/snippet?padding=160&max_width=720` — bbox-crop PNG, CORS-allow közvetlen `<img src>`-re
- CORS allow `localhost:3004 + 127.0.0.1:3004 + 187.77.70.36:3004` (kgc-berles dev/prod)

**kgc-berles oldalán (pending):**
- Új admin-route: `/admin/machines/[id]/parts` → `<iframe src="http://187.77.70.36:5173/?embed=1&catalog=N">`
- `window.addEventListener('message', ...)` handler — origin-check `187.77.70.36:5173` vagy később `parts.kisgepcentrum.hu`-ra
- `cartStore.addPart({callout, partNumber, description, snippetUrl})` action
- Minta-kód: [/root/projektjeim/robbantott-kereso/docs/embed-integration.md](file:///root/projektjeim/robbantott-kereso/docs/embed-integration.md)

## Production-deploy URL

**Marad dev-only** (2026-05-17 user-döntés). A `parts.kisgepcentrum.hu` DNS + Caddyfile site-block + Vite-build külön sprint-re halasztva. Jelenleg az iframe-src az IP-direkt `http://187.77.70.36:5173/?embed=1&catalog=N`.

## Open-ek

- **kgc-berles oldali React-komponens implementálás** — ~30 perc, dokumentált minta szerint
- **Auth majd ha kell** — most nincs scope-ban
- **VLM upgrade** (PaddleOCR-VL 0.9B) — half-day sprint külön, ha 76% bbox-arány nem elég

## Kapcsolódó

- [[02-Projects/robbantott-kereso]]
- [[02-Projects/kgc-berles]]
- [[08-Sessions/2026-05-16-kgc-robbantott-brakeres]] — 7-commit session ahol a döntés megszületett
- [/root/projektjeim/robbantott-kereso/docs/embed-integration.md](file:///root/projektjeim/robbantott-kereso/docs/embed-integration.md) — minta-kód
