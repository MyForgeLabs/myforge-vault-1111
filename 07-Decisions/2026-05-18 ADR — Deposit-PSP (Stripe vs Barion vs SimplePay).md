---
name: ADR — Deposit-PSP választás (Stripe vs Barion vs SimplePay)
type: decision
status: draft-research
created: 2026-05-18
updated: 2026-05-18
tags: [decision, kgc-erp, kgc-berles, payment, deposit, "#project/kgc-erp", "#project/kgc-berles"]
related: [kgc-erp, kgc-berles]
session: 2026-05-18-kgc-all
---

# ADR — Deposit-PSP választás (Stripe vs Barion vs SimplePay)

> **Status:** draft-research — a [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7|Q5 research-output]] alapján Peti finomítja.

## Kérdés

A bérlés-flow-ban kaución ("deposit") flow szükséges: kártya-előengedélyezés (manual capture) bérlés alatt, release/capture bérlés után. A KGC-4 `Rental` model 4-állású deposit-tracking-et használ (required/Paid/Returned/Retained). A MyPOS stub-szinten van. Melyik PSP-vel élesítjük?

## Opciók

- (A) **Stripe Setup-Intent + Payment-Intent manual capture** — nemzetközi de FX-kockázat
- (B) **Barion Reservation** — magyar piac, 7-napos foglalt-keret limit
- (C) **SimplePay** — magyar, NAV-online integration tipikus, foglalt-keret kérdéses
- (D) **MyPOS** (jelenlegi stub) — élesítés saját banki kontraktussal
- (E) **Hybrid:** Stripe + Barion (fallback magyar kártya-felhasználóknak)

## Tradeoff-mátrix összefoglaló

Magyar piac specifika, FX-kockázat, foglalt-keret-időtartam, NAV-online integráció, refund-flow. Részletek: [[06-Audits/2026-05-18 KGC-4 integráció — research-output Q1..Q7#Q5 — Rental booking]]

## Várt döntés

Egy konkrét győztes + magyar piaci validáció + implementation-cost becslés.

## Kapcsolódó

- [[06-Audits/2026-05-18 KGC-4 integráció — architektúra v1]]
- [[02-Projects/kgc-erp]]
