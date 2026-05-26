---
name: ssh-timeout-remote-process-survives
type: wiki
tags: ["#topic/ssh", "#topic/devops"]
created: 2026-05-15
updated: 2026-05-15
---

# `timeout N ssh ... 'long-cmd'` — SSH-session kill ≠ remote process kill

```bash
timeout 300 ssh host 'apt-get -y upgrade'
```

Ha a remote `apt-get` 300 sec után még fut: a `timeout` parancs **kill-eli a lokális SSH TCP-t**, de a remote `apt-get` **tovább fut**. Ennek két oka van:

1. **`dpkg`-lock + atomic completion** — apt-get a megszakítást nem fogadja el mid-unpack, completing-igrácel
2. **`bash -s <<EOF`** heredoc-szerű invokálás esetén a remote-on `bash` SIGHUP-ot kap, de a child `apt-get` `nohup`-szerűen folytatja amíg a kernel-szignál-handler megszámolja a sigprocmask-ot

## Tünet

- Lokálisan: `Exit code 124` (timeout 124 = signal 12 + 124-128 kódolás)
- Remote-on: `pgrep -af apt` még mutatja a folyamatot, `tail /var/log/apt/history.log` Start-Date van End-Date NÉLKÜL

## Helyes monitoring egy másik SSH-val

Ne emelt timeout-tal próbálkozz, hanem külön SSH-val polling:

```bash
# polling másik shell-ben
while ssh host 'pgrep -af "apt|dpkg" | grep -v pgrep | head -1' | grep -q .; do
  sleep 10
done
ssh host 'tail -3 /var/log/apt/history.log'  # End-Date kiírja
```

Vagy Claude Code `Monitor` toollal:
```python
Monitor(command="""
  until ssh host '! pgrep -f apt-get'; do sleep 10; done
  echo APT-DONE
""", timeout_ms=600000)
```

## Helyes async pattern

`nohup`-szerű:
```bash
ssh host 'nohup bash -c "apt-get -y upgrade && touch /tmp/apt-done" >/var/log/apt-async.log 2>&1 &'
# később:
ssh host 'test -f /tmp/apt-done && echo DONE'
```

## Hol jelent meg

2026-05-15 prod apt upgrade — `timeout 300 ssh ...` exit 124-et adott, de a prod-on a 62 csomag-update **mégis befejeződött** (`/var/log/apt/history.log` End-Date 09:47:12). Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Kapcsolódó

- [[11-wiki/apt-upgrade-vs-install-new-packages]]
