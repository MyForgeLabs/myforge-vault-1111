---
name: systemd template-unit multi-project daemon pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#tech/systemd", "automation", "evergreen"]
status: evergreen
---

# systemd template-unit `@<instance>` multi-project daemon pattern

## TL;DR

Több (3-10) projekt-szintű daemon (pl. file-watcher, sync-process, monitor) NEM külön-külön `.service` fájlokba kerül — egy **template-unit `bmad-vault-watch@.service`** + per-projekt `systemctl enable bmad-vault-watch@<slug>`. Automatic restart, journal-logging, per-instance lifecycle, 1-file maintenance. **Gotcha**: NINCS resource-limit alapból → 3+ daemon × bge-m3 embed pile-up rizikó (mitigation: `MemoryMax=512M`).

## Háttér

A vault BMAD-integráció Sprint D: 3 projekt (boulium / kgc-berles / mapesz) mindegyikre real-time edit watch + auto re-ingest kell. **NEM** 3 külön service-file kód-duplikáció, hanem **template-unit pattern**.

## Mintázat

**Template-unit** `/etc/systemd/system/bmad-vault-watch@.service`:

```ini
[Unit]
Description=BMAD vault-watch for %i
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/bmad-vault-bridge --watch /root/obsidian-vault/02-Projects/%i/bmad
Restart=on-failure
RestartSec=5
MemoryMax=512M
TasksMax=50
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Per-projekt activate:**

```bash
systemctl enable bmad-vault-watch@boulium
systemctl start bmad-vault-watch@boulium
systemctl enable bmad-vault-watch@kgc-berles
# ... etc.
```

**Status-monitoring:**

```bash
systemctl list-units 'bmad-vault-watch@*'
journalctl -u bmad-vault-watch@boulium -f
```

## Anti-pattern

- **N külön `.service` fájl** — kód-duplikáció + maintenance-nightmare
- **Bash-wrapper script ami N daemon-t spawn-ol** — restart-policy elveszett, journal-fragmentált
- **No resource-limit** — 3+ daemon × heavyweight tool (bge-m3 embed) → OOM-killer rizikó
- **Manual systemd-start cron-ban** — restart-on-failure missing

## Reusable szabályok

1. **`%i` placeholder** a template-unit-ban — runtime instance-name (`<slug>`)
2. **`MemoryMax` + `TasksMax`** kötelező multi-instance + heavyweight tool kombóra
3. **`StandardOutput=journal`** centralized log + journalctl per-instance filtering
4. **`Restart=on-failure` + `RestartSec=5`** auto-resilience
5. **Per-instance enable** `systemctl enable <unit>@<slug>` → boot-perzisztens
6. **`After=network.target`** ha network-dependency
7. **`User=` explicit** (NEM default root) ha file-permission scope-szűkítés kell

## Buktatók

- **Watchdog dependency missing** — pl. Python `watchdog` PyPI csomag `/usr/bin/python3`-on NINCS default, csak venv-ben. Fix: `pip3 install watchdog --break-system-packages` VAGY `ExecStart=` venv-Python-ra mutat.
- **In-memory dedup process restart-on RESET** — duplicate ingest possible across restart. Solution: Redis-based dedup heavy edit-volume-on.
- **Manual `--ingest` race** — daemon + manual concurrent → ko-DB triplet-row double-count (atomic-write mitigates corruption, de count-anomalia marad). Mitigation: lock-file vagy mutex.

## Kapcsolódó

- [[external-tool-integration-4-sprint-progression]]
- [[bmad-vault-integration-pattern]]
- [[multi-layer-safety-gate]]
