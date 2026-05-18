---
name: Demo Vault-Meta Project
type: project
slug: demo-vault-meta
status: 🟢 example
created: 2026-01-01
updated: 2026-01-01
tags: ["#project/demo", "#type/project", "example"]
---

# Demo Vault-Meta Project (example)

> Ez egy szintetikus példa-projekt amit a SV-rendszer **bemutatására** szolgál.
> Másold le, írd át, és lesz egy saját projekt-tracker-ed.

## Jelenlegi állapot

Demo state — sablon új projektek létrehozásához.

## Komponensek

- Frontend: Next.js 16 + Turbopack (kompatibilis a [[../../11-wiki/nextjs-turbopack-gotchas]] playbook-kal)
- Backend: PostgreSQL + Prisma
- Hosting: VPS + Caddy (lásd [[../../11-wiki/Caddy-reverse-proxy-default]])

## Milestone-ok

- [x] Day 0 — skeleton commit ([[../../11-wiki/sprint-day-0-skeleton-first]])
- [ ] Week 1 — funkcionális MVP
- [ ] Week 2 — UAT + feedback-loop
- [ ] Week 3 — production release

## Hol fut

- Dev: `localhost:3000`
- Staging: `staging.example.com`
- Prod: `app.example.com`

## Kapcsolódó

- [[../sessions/2026-W20-demo-skeleton-first]] — első demo-session
- [[../../11-wiki/sprint-day-0-skeleton-first]] — működési minta
- [[../../07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — host SV-architektúra
