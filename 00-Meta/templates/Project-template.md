---
name: <Projekt teljes neve>
type: project
status: active                   # enum: active | done-with-backlog | production | paused | archived
repo_prod:                       # opcionális: prod útvonal
repo_dev:                        # opcionális: dev útvonal
public_url:                      # opcionális
tags: ["#type/project", "#env/...", "#tech/..."]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <Projekt címe>

<1-2 mondatos összefoglaló: mit csinál a projekt, kinek, miért>

## Jelenlegi állapot

<🟢 production / 🟡 active dev / 🟠 paused / 📁 archived — egy mondatban a most-helyzet>

## Tech-stack

- **Frontend:** 
- **Backend:** 
- **DB:** 
- **Hosting / runtime:** 

## Hol fut

| Környezet | Útvonal | Service / Port | Megjegyzés |
|-----------|---------|----------------|------------|
| prod      |         |                |            |
| dev       |         |                |            |

## Kulcs-fájlok / könyvtárak

- 

## Kapcsolódó döntések

- [[07-Decisions/YYYY-MM-DD <ADR>]]

## Backlog / TODO

(Ide csak referencia — a tényleges TODO-k a [[04-Tasks/Backlog]]-ban vannak `#project/<slug>` taggel)

- 

## Sessions

(Az [[08-Sessions/Index]] csoportosítása alapján — vagy a `#project/<slug>` tag alapján bekereshető)

- 

## Kapcsolódó

- [[02-Projects/Index]]
- [[03-Hosts/<host>]] — ahol fut
- [[05-Memory/Infrastructure]] — közös infra
