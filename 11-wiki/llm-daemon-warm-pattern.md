---
name: LLM-daemon warm-pattern (cold-boot elimination)
type: wiki
tags: ["#type/wiki", "performance", "daemon", "llm", "infrastructure"]
created: 2026-05-17
updated: 2026-05-17
status: stable
---

# LLM-daemon warm-pattern

Ha ugyanaz az LLM-call (embed, klasszifikáció, score) másodpercenként-percenként ismétlődik, a **boot-overhead** (modell-load, SDK-init, Python-interpreter, embedding-cache feltöltés) gyakran a teljes futási idő 90-98%-a. A pattern: egy **long-running daemon** tartja melegen a modellt + a forró állapotot, a hívók egy **Unix-socket JSON-RPC** API-n keresztül beszélnek vele. Companion CLI **socket-first-with-fallback** logikával: ha a daemon él, 50-200ms latencia; ha nem, esik vissza az eredeti in-process útra (graceful degradation, soha nem törik).

## A probléma

Minden naiv LLM-CLI a következő lépéseket csinálja minden hívásra:

1. Python interpreter boot (~200ms)
2. SDK / model import (`sentence-transformers`, `anthropic`, `notebooklm`) (~500-2000ms)
3. **Modell-load CPU/GPU-ra** (bge-m3 ~3-5s, qwen-embedding ~8s)
4. State-feltöltés (DB-query, chunk-cache, embedding-mátrix) (~1-5s)
5. **Actual work** (50-200ms — cosine, API-call, prompt)
6. Exit

A `4`-es után `5`-ös csak töredék. Ha 100× lefuttatod ugyanazt, a `1-4` 100×-szor megy újra → ~98% kidobott munka.

## A pattern

```
              LEGACY                        DAEMON-WARM
   ┌──────────────────────┐         ┌──────────────────────┐
   │ client (CLI)         │         │ client (CLI)         │
   │  ↓ boot Python       │         │  ↓ socket connect    │
   │  ↓ load bge-m3 (5s)  │         │  ↓ JSON-RPC (5ms)    │
   │  ↓ load chunks (3s)  │   VS    │                      │
   │  ↓ cosine (50ms)     │         │                      │
   │  → exit              │         │                      │
   └──────────────────────┘         └──────────┬───────────┘
            ~8.5s                              ↓
                                     ┌──────────────────────┐
                                     │ daemon (systemd)     │
                                     │  • bge-m3 in RAM     │
                                     │  • chunks np.array   │
                                     │  • cosine (50ms)     │
                                     │  → reply             │
                                     └──────────────────────┘
                                              ~165ms
```

## Implementation checklist

1. **Daemon process** — `Type=simple` systemd unit, `Restart=on-failure`, `User=root` ha socket `/run/`-ban él
2. **Unix-socket** (NEM TCP) — `/run/<service>.sock`, `0666` permission, atomic create (`unlink` előtte ha létezik)
3. **State warm-loading** boot-kor: modell + összes chunk → `numpy.ndarray` (NEM list of dicts — vektorizálva ~10× gyorsabb cosine)
4. **JSON-RPC line-protocol** — `{"method": "search", "params": {...}}\n` → `{"result": [...]}\n`. Trivális, NEM kell gRPC.
5. **Signal handling** — `SIGTERM` → graceful close socket, `SIGHUP` → state-reload (chunk-cache invalidáció új ingest után)
6. **Health-endpoint** — `{"method": "ping"}` → `{"result": "ok", "uptime": N, "model": "..."}`. Companion CLI ezt használja warm-check-re.
7. **Companion CLI** — `try socket first → fallback to in-process` ha `ECONNREFUSED` vagy timeout (3s). User SOHA ne lássa hogy a daemon halott.
8. **systemd unit** — `After=memgraph.service docker.service`, `TimeoutStartSec=120s` (modell-load lassú lehet első SSD-hideg-cache-ből)
9. **Reload-endpoint** — `{"method": "reload"}` — új chunk-ok beszúrása után CLI hívja (NE kelljen daemon-restart)
10. **OOM-guard** — `MemoryMax=` systemd-ben (bge-m3 ~2GB, ne legyen több 2-3 daemon parallel — különben swap-thrashing)

## Élő példa — vault-search-server (2026-05-17)

Referencia-implementáció: `/usr/local/bin/vault-search-server` (244 sor) + companion `/usr/local/bin/vault-search` (155 sor).

**Konkrét számok:**
- Cold-boot legacy: **14.0s** (bge-m3 load 5s + Memgraph fetch 3s + cosine 50ms + exit 6s overhead)
- Socket-mode: **165ms** (JSON-RPC 5ms + cosine 50ms + serialization 100ms)
- **Speedup: ~80×**
- RAM-footprint: 2803 chunk × 1024 dim float32 = ~11MB chunk-mátrix + ~2GB bge-m3 = **~2.1GB resident**

**Systemd unit** (`/etc/systemd/system/vault-search.service`):

```ini
[Unit]
Description=Vault semantic-search daemon (bge-m3 warm + Memgraph chunks in RAM)
After=network.target memgraph.service docker.service
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/obsidian-vault
Environment=MEMGRAPH_HOST=127.0.0.1
Environment=MEMGRAPH_PORT=7687
Environment=EMBED_MODEL=BAAI/bge-m3
Environment=VAULT_SEARCH_SOCKET=/run/vault-search.sock
ExecStart=/usr/local/bin/vault-search-server
Restart=on-failure
RestartSec=10s
TimeoutStartSec=120s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Hol érdemes alkalmazni

| Use-case | Boot-cost / call | Várt speedup | Daemon-név javaslat |
|---|---|---|---|
| **G-Eval scorer** (`11.11crystallize` Anthropic mode) | ~500ms (SDK init + HTTP) | 5-10× | `g-eval-server` |
| **Critic-review Layer 4** (bge-m3 chunking) | ~5s (modell-load) | 30-50× | reuse `vault-search-server` |
| **NotebookLM ask-batch** | ~10s (Python+CLI init) | 50-100× | `notebooklm-daemon` |
| **vault-net-distill** (jövőbeli, raw→pattern) | ~3s (embed + LLM-call) | 10-20× | `vault-distill-server` |
| **PDF-OCR PaddleOCR** (Robbantott-kereso) | ~2s (modell+lang-load) | 5-10× | `paddleocr-server` |

Ahol **nem éri meg**: ha a call <10/nap (cron-job-szerű), a daemon RAM-foglalása nagyobb költség mint a boot-overhead.

## Pitfall-ok

- **Socket-permissions race** — daemon `unlink` + `bind` közben más process már próbál connect-elni → `EACCES`. Fix: `umask(0)` daemon-init-ben + `chmod` `bind` után.
- **Modell-reload lock-contention** — `SIGHUP` közben élő `search` request-ek timeout-olnak. Fix: copy-on-write (új mátrix build háttérben → atomic pointer-swap).
- **OOM ha N daemon parallel** — bge-m3 + qwen-embed + Anthropic-client + NotebookLM = ~8GB. VPS-en 16GB-os limit gyorsan jön. Fix: `MemoryMax=` per unit + monitoring.
- **Daemon-crash silent fail** — companion CLI fallback-el, user észre se veszi hogy a daemon halott napokig (és lassú minden hívás). Fix: companion CLI `ping`-re ha >500ms latency vagy ECONNREFUSED → log warning + `systemctl status` hint.
- **Stale state** — új chunk-ok ingest után a daemon-cache elavult. Fix: ingest-script utolsó lépése `echo '{"method":"reload"}' | nc -U /run/<sock>.sock`.

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — B-2 sprint Week 3 performance-pillér
- [[sprint-day-0-skeleton-first]] — skeleton-first komplementer (daemon a "boot a CLI-ban" után jön)
- [[claude-code-subagent-fanout]] — fanout horizontálisan skáláz (N parallel call), daemon vertikálisan (1 call gyors). Kombinálható.
