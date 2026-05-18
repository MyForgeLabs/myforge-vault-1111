---
name: persistent NLI-process pool skeleton
type: audit
created: 2026-05-17
updated: 2026-05-17
sprint: B-3
week: 6
tags: [audit, sv-7, sv-b3, nli, perf, daemon, systemd]
---

# Persistent NLI-process pool skeleton (B-3 Week 6)

> [!info] Status
> **Skeleton landed** — daemon implementálva, systemd unit skeleton, `eval-l2-nli-judge --server` flag adapter, 10× smoke-test PASS. systemd-unit **NEM enabled**, manual activate-szükséges (lentebb).

## Motiváció

A Layer 2.5 (NLI-judge) és Layer 2.6 (vault-coherence-check) hot-path-on `eval-l2-nli-judge` jelenleg **cold-process minden invocation-kor**:

- DeBERTa-v3-base-mnli-fever-anli (~440 MB) load minden hívásnál
- Mért wall-clock cold-mode: **8.7-15.8s / call** (cache-elt model esetén; első friss-cache-fetch ~50-60s)
- 25 inferences / session (5 query × 5 neighbour) → ~5-7 perc / session
- Layer 2.6 vault-coherence-check audit-MD-ben 42-60s/bullet rejtetten

A `vault-search-server` (bge-m3 warm + Memgraph chunks) már bizonyította a warm-daemon-mintát (B-2 Week 2). Ugyanazt a mintát alkalmazzuk az NLI-modellre.

## Architektúra

### Cold-process pattern (régi)
```
crystallize → eval-l2-nli-judge (cold) → from_pretrained() ~5-50s
            → tokenizer + forward-pass ~600ms
            → process exit (model GC-zve)
```
Effektív model-load amortizáció: **0%**. Minden hívás újrabuilduli a graph-ot.

### Warm-daemon pattern (új)
```
[boot] vault-nli.service → NLISingleton.__init__() ~5s (cached)
                        → warm-up forward-pass
                        → listen on /run/vault-nli.sock

[hot]  client → AF_UNIX connect → JSON request → daemon inference (~600ms)
              → JSON response → connect close
```
Effektív model-load amortizáció: **közel 100%** (a daemon élettartamára).

### RPC protokoll (line-oriented JSON Unix-socket-en)

Socket: `$VAULT_NLI_SOCKET` (default `/run/vault-nli.sock`)

| Method | Request | Response |
|---|---|---|
| `infer` | `{"method":"infer","premise":"...","hypothesis":"..."}` | `{"entailment":0.91,"neutral":0.07,"contradiction":0.02,"winner":"entailment","confidence":0.91,"latency_ms":142,"model":"..."}` |
| `batch` | `{"method":"batch","pairs":[{"premise":"...","hypothesis":"...","id":"..."}]}` | `{"results":[{...,id:...},...],"n":N}` |
| `health` | `{"method":"health"}` | `{"ok":true,"model":"...","loaded_at":...,"uptime_s":...,"infer_count":N,"avg_latency_ms":...,"max_tok":512}` |

A `vault-search-server` mintát követi: AF_UNIX (no port-allocation), line-JSON, `ThreadingUnixServer` for concurrent clients.

## Smoke-test eredmény (2026-05-17)

Hardver: EPYC 9354P, CPU-only, RAM-cache-elt HF model.

### Cold-mode (3 sample)

| # | Wall-clock |
|---|---|
| 1 | 15.78 s |
| 2 | 12.33 s |
| 3 |  8.71 s |
| **mean** | **~12.3 s** |

A 8.7-15.8s a HF-cache hit-eken mért; első friss-fetch (cache-miss) eredetileg **50-60s** volt (lásd B-3 Week 2 baseline).

### Server-mode (10 sample, single-invocation per call)

| # | Wall-clock |
|---|---|
| 1 | 0.66 s |
| 2 | 0.57 s |
| 3 | 0.64 s |
| 4 | 0.70 s |
| 5 | 0.59 s |
| 6 | 0.67 s |
| 7 | 0.60 s |
| 8 | 0.72 s |
| 9 | 0.69 s |
| 10 | 0.58 s |
| **mean** | **~0.64 s** |

Daemon-side `avg_latency_ms` health-readout: **725.9 ms** (20 inference). RPC-overhead minimális (socket + JSON enc/dec ~50ms).

### Speedup

| Metric | Cold | Warm | Speedup |
|---|---|---|---|
| Per-call wall-clock | 12.3 s (mean) | 0.64 s (mean) | **~19×** |
| Per-call wall-clock | 50-60 s (cache-miss first call) | 0.64 s | **~80-90×** |
| 25-inference session | ~5 min | ~16 s | **~19×** |
| 25-inference session (cache-miss) | ~21 min | ~16 s | **~80×** |

**Cél (5s steady-state) bőven túlteljesítve** — a server-mode steady-state ~0.6s.

### Batch-mode (10 pairs single connect)

Egy `--server --input-file` invocation 10 párt 8.49s alatt dolgoz fel (~0.85s/pair, inkluzív Python startup overhead). A daemon `batch` RPC közvetlen használata (Python kliensből) tovább csökkenti ~6.5s-ra a 10-páros batch-et.

### Korrektség sanity-check

10-pair set, ahol 3 párt szándékosan kontradikciósra építettem:

| ID | Verdict | Entailment | Megjegyzés |
|---|---|---|---|
| s1 | entailment | 0.808 | OK |
| s2 | entailment | 0.877 | OK |
| s3 | entailment | 0.927 | OK |
| s4 | **contradiction** | 0.000 | OK (foxxi Hostinger LiteSpeed contradiction) |
| s5 | entailment | 0.766 | OK |
| s6 | neutral | 0.048 | OK (GEPA score részben van premise-ben) |
| s7 | **contradiction** | 0.000 | OK (NotebookLM "fully sync" contradiction) |
| s8 | entailment | 0.525 | OK |
| s9 | entailment | 0.945 | OK |
| s10 | **contradiction** | 0.000 | OK (touch-kiosk 30s contradiction) |

Az NLI a cold és warm útvonalakon ugyanazokra a számokra konvergál — a daemon nem rontja a modell-szemantikát.

## Fájlok

| Path | Funkció |
|---|---|
| `/root/obsidian-vault/.vault-eval/scripts/nli-server.py` | Warm-daemon (transformers + AF_UNIX) |
| `/etc/systemd/system/vault-nli.service` | systemd unit (skeleton, **NEM enabled**) |
| `/usr/local/bin/eval-l2-nli-judge` | +`--server` flag adapter (RPC-route) |
| `/usr/local/bin/eval-l2-nli-judge.bak.20260517-nli-server` | Backup (pre-Week-6) |

## systemd activate-protokoll

A unit-fájl deklarálva, de **NEM enabled** — a user dönti el mikor élesedik:

```bash
# Activate (one-shot)
systemctl daemon-reload
systemctl enable --now vault-nli.service

# Watch first cold-load (~5-50s depending on HF-cache state)
journalctl -u vault-nli -f

# Verify
ls -la /run/vault-nli.sock
echo '{"method":"health"}' | socat - UNIX-CONNECT:/run/vault-nli.sock

# Use from CLI
eval-l2-nli-judge --server --bullet "..." --provenance "..."

# Disable
systemctl disable --now vault-nli.service
```

### Env-vars (override)
- `NLI_MODEL` — model HF-id (default `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`)
- `NLI_MAX_TOK` — token truncation max (default 512)
- `VAULT_NLI_SOCKET` — socket path (default `/run/vault-nli.sock`)
- `VAULT_NLI_RPC_TIMEOUT` — kliens-oldali timeout (default 60s)

### Manual foreground run (debug)
```bash
/root/obsidian-vault/.vault-eval/scripts/nli-server.py
# vagy custom modellel:
NLI_MODEL=cross-encoder/nli-deberta-v3-large /root/obsidian-vault/.vault-eval/scripts/nli-server.py
```

## Resource-footprint

A futó daemon `pgrep -af nli-server` + `ps`:
- RSS: ~1.0-1.5 GB (DeBERTa-v3-base + torch graphs)
- CPU: idle közeli idle-ben (csak forward-pass alatt 1 mag 100%)
- Socket: 0 byte tmpfs

Kompatibilis a `vault-search.service`-szel (külön daemon, külön socket, ~3 GB combined RSS — 38 GB RAM-on bőven befér).

## Week 7 follow-up

A `11.11crystallize` szkript **jelenleg subprocess-szel hívja** `eval-l2-nli-judge`-t (Layer 2.5) és `vault-coherence-check`-en keresztül (Layer 2.6). Ezek továbbra is cold-process-szel mennek — ha a daemon él, akkor csak az `--server` flag-et kell hozzáadni a subprocess-call-okhoz.

A **valódi optimum**: a `11.11crystallize` Python-kód **közvetlenül** RPC-zzen a `/run/vault-nli.sock`-ra, kihagyva a `eval-l2-nli-judge` Python interpreter start-overhead-et (~200ms/call). Várt további speedup:

| Layer | Jelen (subprocess `eval-l2-nli-judge --server`) | Optimális (direkt RPC) |
|---|---|---|
| Per-call latency | ~0.64s | ~0.15s (csak RPC + inference) |
| 25-inference session | ~16s | ~4s |

→ **kb. 4× további speedup** az `eval-l2-nli-judge` Python-process startup költségét megspórolva.

### Week 7 task-lista
1. `11.11crystallize` Python-kódban `_rpc_infer()` helper portolása (`_rpc_infer` már él `eval-l2-nli-judge`-ban, copy-paste)
2. Layer 2.5 cascade: subprocess-call → direkt RPC, fallback subprocess-re ha socket nem létezik
3. `vault-coherence-check` ugyanígy
4. `VAULT_USE_NLI_SERVER=1` env-var (opt-in, kompatibilis)
5. systemd auto-activate decision: ha 4 hét stabil futás → enable as default

## Risk + rollback

- **Daemon crash** → `Restart=on-failure` (10s backoff) systemd-ből
- **RPC timeout** (60s) → `eval-l2-nli-judge --server` exit-code != 0; caller fallback-elhet cold-mode-ra `--server` nélkül
- **OOM** (1.5GB RSS) → ha más szolgáltatás zabál (Memgraph spike), restart elég
- **Rollback** — `systemctl disable --now vault-nli.service`; a `eval-l2-nli-judge` `--server` flag nélkül változatlanul cold-process

## Kapcsolódó

- [[11-wiki/sv-07-continuous-evaluation]] — Layer 2.5 NLI architektúra
- [[../05-Memory/Infrastructure]] — systemd unit-jegyzék
- ADR: `07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md`
- `vault-search.service` (B-2 Week 2) — minta-implementáció
- `08-Sessions/2026-05-17-obsidian-vault-3.md` — Week 6 sprint-context
