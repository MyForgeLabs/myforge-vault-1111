---
name: ADR — Sync-pattern KGC-4 → kgc-berles (webhook vs CDC vs poll)
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, sync, cache, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — Sync-pattern KGC-4 → kgc-berles (webhook vs CDC vs poll)

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q1 research-output]] alapján Peti finomítja.

## Kérdés

Hogyan szinkronizálja a kgc-berles Next.js katalógus a KGC-4 ERP termékadatait? ~500 termék, napi 5-20 árváltozás, óránkénti készlet-frissítés, 119+ SEO-landing oldal.

## Opciók

- (A) **Webhook + Next.js `revalidateTag`** — KGC-4 POST-ol minden change-en a Next-end-pointra
- (B) **Postgres LISTEN/NOTIFY** + Next.js cron-poll
- (C) **Debezium CDC** Kafka-streammel — overkill ezen scale-en?
- (D) **Redis Streams + BullMQ event-bus** (a KGC-4 már használja BullMQ-t)
- (E) **Egyszerű poll** (Next.js cron 15min-enként `/portal/feed.json`-on)
- (F) **Hybrid:** poll + webhook (poll-fallback ha a webhook elveszik)

## Tradeoff-mátrix összefoglaló

Latency, komplexitás, race-condition kezelés, cache-stampede védelem. Részletek: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q1 — Katalógus-szinkron]]

## Várt döntés

Egy konkrét győztes a 6 opció közül + HMAC webhook-auth implementáció specifikáció + buktató-mitigation (cache-stampede + stale-on-error).

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
- [[11-wiki/nextjs-api-proxy-bridge]]
