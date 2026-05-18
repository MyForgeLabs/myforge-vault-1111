---
name: vnc-stack-systemd-reboot-survival
type: wiki
tags: ["#topic/vnc", "#topic/systemd", "#topic/headless"]
created: 2026-05-15
updated: 2026-05-15
---

# VNC stack reboot-survival — Xvfb + openbox + x11vnc + noVNC systemd-chain

Headless szerveren a VNC-stack 4 komponensből áll, és reboot után **csak akkor jön vissza automatikusan**, ha mind a 4 systemd-managed. Gyakori `nohup`-tal indított runtime ütközik a reboot-tal.

## 4-unit chain

```
xvfb.service  →  openbox-99.service  →  x11vnc.service  →  novnc.service
(virtual fb)     (window mgr)            (VNC server)       (websockify bridge 6080)
```

A láncot a systemd `Requires=` + `After=` direktívákkal kötjük össze, plus `ExecStartPre=/bin/sleep N` race-condition ellen (X-server `:99` ready-re).

## Unit-fájlok (TL;DR)

### `/etc/systemd/system/xvfb.service`
```ini
[Unit]
Description=Xvfb virtual framebuffer (display :99)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :99 -screen 0 1440x900x24
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/openbox-99.service`
```ini
[Unit]
Description=openbox WM on display :99
After=xvfb.service
Requires=xvfb.service

[Service]
Type=simple
Environment="DISPLAY=:99"
ExecStartPre=/bin/sleep 2
ExecStart=/usr/bin/openbox
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/x11vnc.service` (localhost-only!)
```ini
[Unit]
Description=x11vnc localhost-only (display :99)
After=xvfb.service openbox-99.service
Requires=xvfb.service

[Service]
Type=simple
ExecStartPre=/bin/sleep 3
ExecStart=/usr/bin/x11vnc -display :99 -rfbauth /root/.vnc/passwd -rfbport 5900 -localhost -forever -shared -noxdamage
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

⚠️ A `-localhost` flag **kritikus** — bind `127.0.0.1:5900`-ra, NEM `0.0.0.0:5900`. Standard VNC DES-jelszó gyenge, public bind = root-shell-eligible.

### `/etc/systemd/system/novnc.service`
```ini
[Unit]
Description=noVNC websockify bridge 6080 -> localhost:5900
After=x11vnc.service
Requires=x11vnc.service

[Service]
Type=simple
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc 6080 localhost:5900
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Enable + verify

```bash
systemctl daemon-reload
for s in xvfb openbox-99 x11vnc novnc; do
  systemctl enable $s.service
done

# reboot test
reboot   # vagy shutdown -r +1 ha session-ben vagy

# post-reboot
ss -tlnp | grep -E ":(5900|6080)"
# várt: 127.0.0.1:5900 (x11vnc) + 0.0.0.0:6080 (websockify)
```

## Access patterns

- **Helyi VNC kliens (TigerVNC, RealVNC):** SSH tunnel kell mert localhost-only:
  ```bash
  ssh -L 5900:localhost:5900 user@host
  # kliens csatlakozik localhost:5900-ra
  ```
- **Browser noVNC:** `http://host:6080/vnc.html` — UFW-ben 6080 ALLOW-on kell legyen
- **Tailscale-only:** `tailscale serve` vagy explicit Tailscale-IP bindelés

## Tipikus gotcha

- **Xvfb crash → x11vnc no display** — `Requires=xvfb.service` szigorúbb mint `Wants=`, mert Xvfb stop = x11vnc auto-stop
- **openbox nélkül**: az X-server megy, de kontextus-menü / mouse-cursor fura. openbox window manager-t INDÍTSD
- **Race condition**: a `Requires=` nem garantálja a READY state-et, csak hogy a unit elindult. Az `ExecStartPre=/bin/sleep` rugalmas hack — proper megoldás `Type=notify` + custom systemd-notify

## Hol jelent meg

2026-05-15 dev VPS — VNC `0.0.0.0:5900` (publikus DES-auth) localhost-only-ra rebindelve + 4-unit systemd-chain reboot-survival miatt. Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Kapcsolódó

- [[05-Memory/Infrastructure#VNC]]
- [[11-wiki/notebooklm-headless-login-fifo]]
<!-- auto-enriched 2026-05-18: +3 semantic cross-link via vault-search -->
- [[claude-code-subagent-fanout]] (sem-rokon, score=0.54)
- [[apt-upgrade-vs-install-new-packages]] (sem-rokon, score=0.54)
- [[llm-daemon-warm-pattern]] (sem-rokon, score=0.53)
