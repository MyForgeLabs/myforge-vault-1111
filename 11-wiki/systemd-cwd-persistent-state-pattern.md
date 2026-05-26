---
name: systemd-cwd-persistent-state-pattern
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#systemd", "#infra", "#pattern", "#playbook"]
---

# systemd CWD-based persistent state path pattern

> [!info] When to apply
> Wrapping a process under `systemd` that writes data to a **relative** path (e.g., `./data/`, `./logs/`, `./state.db`). Without explicit `WorkingDirectory=`, systemd defaults to `/` or `/root`, and your process either fails to create the path or scatters state in unintended locations. **Always set `WorkingDirectory=` explicitly** to a persistent dir.

## The trap

Many CLI tools / engines (`iii-engine`, `node` scripts, Python servers, Go binaries) write data to `./relative/path/...` based on their CWD at startup. When you launch them manually:

```bash
cd /tmp && node my-server.js              # writes to /tmp/data/...
cd /var/lib/app && node my-server.js      # writes to /var/lib/app/data/...
```

Now you wrap it in `systemd`:

```ini
[Service]
ExecStart=/usr/local/bin/my-server         # what's the CWD?
```

**Default systemd CWD = `/`** (or `/root` depending on user). The relative path resolves to `/data/...` — wrong location, possibly **wiped on reboot** if it lands in `/tmp`.

**Symptom**: state inexplicably lost on every reboot, or app fails to create dirs on startup, or two processes writing to "same" relative path actually write to different absolute paths depending on launch CWD.

## The fix

```ini
[Service]
Type=simple
WorkingDirectory=/var/lib/my-app          # ← THIS
ExecStart=/usr/local/bin/my-server         # now writes to /var/lib/my-app/data/...
Restart=on-failure
RestartSec=10
```

**`/var/lib/<app>/`** is the FHS-conventional path for persistent app-state. Combine with:

- `Environment=HOME=/root` (or appropriate) — if the app reads `~/.config/...`
- `StandardOutput=append:/var/log/<app>.log` — persistent logging
- `StandardError=append:/var/log/<app>.log` — same

## Concrete case — agentmemory.service (2026-05-20)

`agentmemory` (rohitg00/agentmemory v0.9.21) launches iii-engine 0.11.6 with config:

```yaml
# iii-config.yaml
workers:
  - name: iii-state
    config:
      adapter:
        config:
          file_path: ./data/state_store.db    # ← relative!
```

**Manual launch in /tmp**: state at `/tmp/data/state_store.db/` — **wiped on reboot**.

**Fix**: systemd unit with `WorkingDirectory=/var/lib/agentmemory/`:

```ini
[Unit]
Description=agentmemory v0.9.21 — persistent memory + RRF retrieval-stack
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/lib/agentmemory
Environment=HOME=/root
Environment=PATH=/root/.nvm/versions/node/v22.22.2/bin:/usr/local/bin:/usr/bin:/bin
Environment=NODE_OPTIONS=--max-old-space-size=512
ExecStart=/root/.nvm/versions/node/v22.22.2/bin/agentmemory
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/lib/agentmemory/agentmemory.log
StandardError=append:/var/lib/agentmemory/agentmemory.log

[Install]
WantedBy=multi-user.target
```

Now state persists at `/var/lib/agentmemory/data/state_store.db/`, survives reboot.

## Why this is easy to miss

- Manual testing usually `cd <project>` before launch — state ends up in `<project>/data/`, looks correct
- systemd's default `WorkingDirectory=/` (or `/root`) silently produces a "/data/" dir at the filesystem root, which **does exist** and gets written to
- The error doesn't show until reboot or until two processes race over the same fictional path

## Adjacent gotchas to check at the same time

1. **`Environment=HOME=`** — many CLI tools read `~/.config/<app>/`. If `User=` is set but `HOME=` isn't, behavior varies by distro
2. **`Environment=PATH=`** — if your process spawns sub-processes (e.g., `node` spawning `iii`), the PATH inheritance matters; include `node_modules/.bin` if relevant
3. **`StandardOutput=append:` vs `journal`** — systemd's default is journal, which is fine for short logs but gets indexed slowly for long; explicit `append:/var/log/...` is more predictable for grep-able logs
4. **`Restart=on-failure` vs `always`** — `always` restarts even on clean exit-0, which is usually NOT what you want; `on-failure` only on nonzero exit or signal-kill
5. **`User=` and file ownership** — if WorkingDirectory is created by hand before service-start, ownership should match `User=` (especially if `User != root`)

## Detection commands

```bash
# Check where a running process actually writes
readlink /proc/$(pgrep -f my-app)/cwd

# Find unexpectedly-created state dirs at filesystem root
ls -la /data /logs /state 2>/dev/null

# Verify systemd unit's effective WorkingDirectory
systemctl show my-app.service -p WorkingDirectory

# Test reboot-survival without rebooting
systemctl stop my-app.service
ls -la /var/lib/my-app/data/    # state should still be here
systemctl start my-app.service
# verify data is re-read correctly
```

## Source verified

- **agentmemory.service implementation**: `/etc/systemd/system/agentmemory.service` (2026-05-20)
- **iii-config.yaml relative-path**: `/root/.nvm/versions/node/v22.22.2/lib/node_modules/@agentmemory/agentmemory/dist/iii-config.yaml`
- **Production audit**: [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]

## Generalizes to

- Any Node.js / Python / Go process using relative paths for state/cache/logs
- Docker containers — same pattern with `WORKDIR` directive (write-to-volume)
- Long-running CLI tools wrapped in systemd (vector DBs, vector engines, RAG-pipelines)
- Database systems (SQLite, LevelDB, RocksDB) where the data-dir is configured relatively

## Kapcsolódó

- [[../05-Memory/Infrastructure]] — `agentmemory.service` szakasz
- [[../07-Decisions/2026-05-20 Production retrieval-stack v2 — RRF hybrid-fusion architecture]]
