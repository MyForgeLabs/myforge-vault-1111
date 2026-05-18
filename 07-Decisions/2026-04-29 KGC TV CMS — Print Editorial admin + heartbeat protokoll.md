---
name: KGC TV CMS — Print Editorial admin + heartbeat protokoll
type: decision
tags: ["#type/decision", "#project/kgc-tv-cms", "#env/prod"]
created: 2026-04-29
status: accepted
---

# KGC TV CMS — Print Editorial admin + heartbeat protokoll

## Kontextus

A Kisgépcentrum-i Samsung QH43C kivetítőkre tartalom-management rendszert építettünk
2026-04-27 — 04-29 között. Az admin felület első MVP-je működött, de vizuálisan amatőr,
és a kivetítők státusza nem volt valós (mock-réteg).

## Döntések

### 1. Vizuális irány: Print Editorial (Claude Design Studio A irány)

A Claude Design Studio által generált 3-irányból (A: Print Editorial · B: Industrial
Control Room · C: Soft Workspace) a **Print Editorial** lett választva. Indok:
- A KGC brand "Warm Editorial" mood-ja [[07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial]] tökéletesen illeszkedik
- Magazinos hierarchia (Fraunces serif + Inter + JetBrains Mono) elkülöníti a kollégai
  toolt egy generic SaaS-tól — szakmai érzést ad
- A "esti műsor"-rovat a live monitoring-ot magazin-szerű formában oldja meg (NEM NOC
  dashboard, ami túl technikai lenne)

A B és C iránynak később lehet még helye: B-t a tv-makita-tour-hoz (sötét NOC-stílus),
C-t alternatív "kollégás" verzióként.

### 2. Heartbeat-protokoll

Live monitoring backend-tracking-gel, NEM mock-réteggel.

**Player → backend:**
```
POST /api/screen/<id>/heartbeat
Content-Type: application/json

{
  "currentItem": {"type": "html", "src": "...", "title": "..."},
  "itemElapsedSec": 12
}
→ 204 No Content
```

A player minden 30s polling után automatikusan küldi.

**Backend storage:** `data/heartbeats.json` (in-memory + 5s debounce-olt fájl-write)

**Status derivátum (szerver-oldali):**
- `online === true` → `now - lastHeartbeat < 90s`
- `online === false` → `> 90s`
- `online === null` → soha nem pollozott (a kivetítő még nincs beállítva)

A 3-state status nem 2-state — mert ha `null` "offline"-nak látszott, az félrevezető
volt (amikor egy kollégát megijesztett hogy "miért offline a Műhely?").

### 3. Vanilla JS + no innerHTML

Az admin frontend NEM React/Vue, hanem vanilla JS. Indok:
- Nincs build-step — egyszerűbb deploy (rsync 3 fájl)
- A security-hook blokkolja az `innerHTML` használatot (XSS prevention) — minden
  DOM-műveletet `createElement` + `textContent` + `setAttribute`-tel
- Sortable.js CDN-ről (drag-drop), egyetlen külső lib

### 4. URL séma + auth

- **Admin:** `http://72.62.92.98:8201/admin/` basic-auth (kgc/kivetito2026, env-ből)
- **Player:** `http://72.62.92.98:8201/s/<screen-id>` (publikus, redirect /player/?id=)
- Per-kivetítő egyedi URL — egy Samsung-ra 1× beírva, onnan adminban változtatsz tartalmat
- Aldomén + HTTPS (`kivetito.kisgepcentrum.hu` Let's Encrypt-tel) későbbi iteráció

## Konzekvenciák

### Pozitív
- A Print Editorial design tényleg kollégaknak is olvasható, professzionális érzés
- Heartbeat-tracking → tényleg látszik mit lát a TV (currentItem mező a `/api/admin/screens` válaszában)
- 3-state status (online/offline/null) elkerüli a félrevezetést
- Vanilla JS = no build = bárki, bárhol bele tud nyúlni

### Negatív
- Vanilla JS + no innerHTML = sok createElement-zaj a kódban (~700 sor app.js)
- A Print Editorial light-only (dark mode külön munkát igényel)
- Az aldomén + HTTPS hiánya: a Samsung-okba `72.62.92.98:8201` IP-t kell írni

## Kapcsolódó

- [[02-Projects/kgc-tv-cms]] — teljes tech doc
- [[02-Projects/kgc-kivetitok]] — a 7 statikus TV-fal HTML
- [[07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial]] — brand alapok
- [[05-Memory/Infrastructure]] — port 8200/8201 dokumentálva
