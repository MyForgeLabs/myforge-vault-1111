---
name: Demo Sprint Day 0 Skeleton-first
type: session
project: demo-vault-meta
status: closed
started: 2026-01-01T09:00+00:00
ended: 2026-01-01T11:30+00:00
agent: claude
eval_score: 4.2
eval_critique: passed
hallucination_flag: false
eval_l2_agreement: 0.92
tags: ["#type/session", "#project/demo", "example"]
---

## Pre-loaded context

Demo project → új projekt-bootstrap. Skeleton-first pattern alkalmazása (lásd [[../../11-wiki/sprint-day-0-skeleton-first]]).

## Cél

Új projekt Day 0 — funkcionális skeleton commit egy 2.5-órás session-ben, hogy a Week 1 implementáció már működő scaffold-on legyen.

## Events

- 09:15 — Repo init, Next.js 16 boilerplate, Prisma schema draft (5 entity: User, Project, Task, Comment, Tag)
- 09:45 — Postgres lokál Docker-up, schema migrate, smoke-CRUD
- 10:30 — Caddy reverse-proxy local-domain (`demo.local`), TLS self-signed
- 11:00 — CI-skeleton GitHub Actions (.github/workflows/test.yml), 1 dummy-passing test
- 11:20 — README scaffold + ADR `2026-01-01 stack-decisions.md`

## Summary

**Day 0 skeleton kész:** 1 commit / 1 hour-of-active-work, 12 fájl init-ben. Funkcionális minimum:
- Next.js 16 + Turbopack dev-server fut
- Prisma schema 5 entity + lokál Postgres
- Caddy reverse-proxy + self-signed TLS
- GitHub Actions CI green
- ADR + README

## Learnings → memória

- **Skeleton-first 5× idő-megtakarítást ad** a Week 1-en — bizonyítva a [[../../11-wiki/sprint-day-0-skeleton-first]] 6-iterációs ROI-táblán
- **Caddy default OK új projektre** (NE Traefik) — lásd [[../../11-wiki/Caddy-reverse-proxy-default]]
- **Turbopack dev-mode parallel-API gotcha** — `useSWR` deduplication kell ([[../../11-wiki/nextjs-turbopack-gotchas]] #1)

## Next session

- Week 1 Day 1: User-auth + Session-management impl
- Week 1 Day 2: Project CRUD UI + REST API integrate
- Week 1 Day 3: Test-coverage 60%+ ([[../../11-wiki/tdd]] minta)
