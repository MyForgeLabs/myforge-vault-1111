---
name: orphan-pdf-auto-resume-pattern
description: Self-healing pipeline pattern — filesystem = source-of-truth, DB = derived state. Backend-startup-handler scan-eli az orphan input-fájlokat és újra-feldolgozza háttér task-ban.
metadata:
  type: wiki
created: 2026-05-12
tags: ["#type/reference"]
tag_backfill: 2026-05-19
updated: 2026-05-19
---
# Orphan-fájl auto-resume pattern

## A tanulság

Ha a backend in-memory job-state-ben tartja az async upload-pipeline állapotát (FastAPI BackgroundTasks, asyncio.create_task, Celery in-process worker), **bármilyen restart elveszíti az in-flight feladatokat**. A felhasználói tünet: "a feltöltés sorbanállva marad / nem sikerült".

**Megoldás (self-healing):** backend-startup-kor scan-elni a `data/uploads/` (vagy bárhol az input-fájlok mennek) könyvtárat, kiszedni a DB-ből az ismert (processed) fájlokat, **a difference = orphan** → háttér task-ban újra-ingest. **Filesystem = source-of-truth, DB = derived state.**

## Why

```
User uploads PDF → backend saves file + registers job in _jobs dict + BackgroundTasks
                ↓
        Backend restart (code deploy, OOM, OS reboot, crash)
                ↓
        _jobs dict üres (in-memory)
                ↓
        UI poll /api/jobs/{id} → 404 forever
                ↓
        File saved to disk de soha nem processzeolt → DB-ben nincs catalog
```

A felhasználó látja a "queued" status-t hosszan, miközben a backend már nem dolgozik rajta semmin.

## How to apply

**FastAPI startup-handler:**

```python
# backend/app/startup.py
import asyncio
import logging
from pathlib import Path
from backend.app.db.database import get_connection
from backend.pipeline.ingest import ingest_pdf

logger = logging.getLogger(__name__)

def _find_orphan_pdfs() -> list[Path]:
    """PDF-ek a data/pdfs/-ben amiknek nincs catalog-rekordjuk."""
    pdfs = sorted(Path("data/pdfs").glob("*.pdf"))
    with get_connection() as conn:
        rows = conn.execute("SELECT source_pdf FROM catalogs").fetchall()
        known = {Path(r["source_pdf"]).name for r in rows}
    return [p for p in pdfs if p.name not in known]

async def _auto_resume_orphans():
    orphans = _find_orphan_pdfs()
    if not orphans:
        return
    logger.warning("Auto-resume: %d orphan PDF, ingest indul", len(orphans))
    for pdf in orphans:
        # Blocking ingest egy thread-en — ne blokkolja az event-loop-ot
        await asyncio.to_thread(ingest_pdf, pdf, reset=False)

def schedule_auto_resume(app):
    @app.on_event("startup")
    async def _startup():
        asyncio.create_task(_auto_resume_orphans())
```

**Hozzákapcsolás:**

```python
# backend/app/main.py
from backend.app.startup import schedule_auto_resume
app = FastAPI(...)
schedule_auto_resume(app)
```

**Frontend fallback (nem helyettesíti, csak kiegészíti):**

A frontend a job_id-t pollozza, ha 404 érkezik → fallback `/api/catalogs` listához és matchel filename-stem-mel. Ha találja → treat as done.

## Mikor kell ez a pattern

- ✅ Bármilyen pipeline ahol a feldolgozás >5s, és restartok happen (dev, deploy, OOM)
- ✅ Input-fájl-alapú workflow (a fájl = source-of-truth)
- ✅ FastAPI BackgroundTasks single-worker (in-process state)
- ❌ NEM kell ha:
  - Redis-backed job-queue (Celery/Sidekiq) — already persistent
  - Idempotent endpoints amik nem hagynak köztes állapotot
  - Stream-processing (Kafka, etc.)

## Architektúra-elv

**Filesystem = source-of-truth, DB = derived state.**

Ennek implikációi:
- DB DROP után rebuild lehet a filesystem-ből
- Backend restart NEM veszít adatot, csak átmeneti workflow-állapotot
- Idempotens re-ingest (új catalog row, NEM update) — minden re-run egy "next try"
- Disk-térrel fizetjük: input-fájlokat sosem töröljük (csak ha a user expliciten kéri)

## Tovább-fejlesztés

Ha a self-healing-en túl lépünk:
- **SQLite job-table** ahelyett hogy in-memory dict — DB-ben tárolt status, frontend pontosan látja a "recovering 3/5" üzenetet
- **Idempotency-key** a POST /api/upload-ra → ugyanaz a key = ugyanaz a job_id, deduplication
- **Worker pool** (uvicorn workers>1 vagy Celery + Redis) — több párhuzamos ingest

## Implementáció

- [[02-Projects/robbantott-kereso]] `backend/app/startup.py` (commit `c302b3d`)
- Felhasználói "megint nem sikerül feltölteni" → diagnosztikus session-ből kiderült: 4 orphan PDF + auto-resume → 95% recovery probléma nélkül

## Kapcsolódó

<!-- auto-enriched 2026-05-18: semantic neighbours via vault-search -->

- [[Karpathy-LLM-Wiki-pattern]] (sem=0.51)
- [[puppeteer-pdf-system-chrome]] (sem=0.49)

