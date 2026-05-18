---
name: Daily index
type: index
tags: [daily, index]
created: 2026-04-23
updated: 2026-05-18
---

# Daily naplók

Napi rövid napló a session-orchestration + vault-state változásokról. Az 2026-04-23 óta vezetjük.

> **Privacy:** a per-day daily-fájlok client-projekt eseményeket tartalmaznak, ezért **NEM publikusak**. Csak ez az Index látható.

> **Snapshot:** 26 daily a vault-ban (2026-04-23 .. 2026-05-18).

## Frissítési gyakoriság

- **Auto-trigger:** `11.11start` minden új session-en gond.
- **Backfill:** ha napi log hiányzik, session-MD-k alapján rekonstruálható (`08-Sessions/<date>-*.md` listájával).

## Kapcsolódó

- [[../08-Sessions/Index|Sessions Index]] — per-session log
- [[../11-wiki/11.11-session-protokoll|11.11 session-protokoll]]
