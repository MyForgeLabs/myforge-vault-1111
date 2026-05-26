---
name: <ember-olvasható cím>
type: session
project: <slug — egyezik 02-Projects/<slug>.md-vel ha van>
status: open
started: YYYY-MM-DDTHH:MM+00:00
ended:
agent: claude | codex | gemini
tags: ["#type/session", "#project/<slug>"]
---

## Pre-loaded context

> Az agent SESSION INDULÁSKOR aggressive context-loadot csinál a [[11-wiki/Auto-context-loading]] szerint, és ide írja mit olvasott be (1-2 mondatos kivonat fájlonként). Ha a session-név nem detektál projektet, csak az alap-kontextust (Projects/Index + Tasks/Backlog + Daily).

**Projekt:** [[02-Projects/<slug>]]
- Status: 
- Tech: 

**Utolsó session-ök (max 5):**
- 

**ADR-ek:**
- 

**Backlog (#project/<slug>):**
- 

**Infra-relevánsak:**
- 

**User UI/UX preferenciák:**
- 

> N forrás · ~K token · ready

## Cél

<Mit akarunk elérni ebben a sessionben — 1-2 mondat>

## Events

- HH:MM — 

## Summary

<Lezáráskor (`/11.11stop`) az agent kitölti — 1-3 bekezdés a megtörténteket összegzi>

## Learnings → memória

<Bullet-pontok amik tartós érvényűek. Az agent a [[11-wiki/Crystallization-protocol]] szerint propagálja őket — batch preview UX-szel a usertől megerősítést kér.>

- 

## Next session

<Mivel kell folytatni, blockerek, függő döntések>

- 

## Propagation log

> Az agent SESSION ZÁRÁSKOR ide írja időbélyegezve hova propagált minden Learning bullet-et. Auditálható: később visszakereshető hogy egy adott Memory/ADR/wiki bejegyzés melyik session-ből származik.

- YYYY-MM-DDTHH:MM — [N] → <target fájl> (<rövid leírás>)
