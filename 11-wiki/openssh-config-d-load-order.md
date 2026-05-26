---
name: openssh-config-d-load-order
type: wiki
tags: ["#topic/ssh", "#topic/linux", "#topic/security"]
created: 2026-05-15
updated: 2026-05-15
---

# OpenSSH sshd_config.d load order — FIRST occurrence wins

A `sshd_config` `Include /etc/ssh/sshd_config.d/*.conf` direktívája **alfabetikus sorrendben** olvassa be a fájlokat. Az OpenSSH viszont az **ELSŐ előfordulást** alkalmazza minden direktívára — nem az utolsót.

## Gotcha

Cloud-image-szervereken (Hostinger, AWS, GCP) gyakran van egy `60-cloudimg-settings.conf` ami `PasswordAuthentication yes`-t állít. Ha `99-hardening.conf`-ban `PasswordAuthentication no`-t teszel, a **60-as fájl wins**, mert előbb olvassa.

## Detekció

```bash
sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'
```

A resolved érték mutatja, mit alkalmaz ténylegesen. Ha nem amit vártál, ellenőrizd:

```bash
grep -nE '^(Password|PermitRoot)' /etc/ssh/sshd_config.d/*.conf /etc/ssh/sshd_config
```

## Fix opciók

1. **Kikommentelni a régi fájlt** (`60-cloudimg-settings.conf`): `sed -i 's|^PasswordAuthentication yes$|#PasswordAuthentication yes|' /etc/ssh/sshd_config.d/60-cloudimg-settings.conf`
2. **Átnevezni a custom fájlt** prefix-vel: `00-hardening.conf` (előbb tölt mint 60)
3. **Backup mindig**: `cp ... .bak.$(date +%Y%m%d)` ELŐTT

## Reload, NEM restart

Ubuntu 24.04+-en `systemctl reload ssh.service` (NEM `sshd.service` — socket-activated). Reload nem ejti a meglévő session-öket, új connection-ök az új configgal jönnek. **Restart kockázat:** kizárhat ha config-hiba van.

## Validation előtt + utána

```bash
sshd -t && echo OK  # syntax check
# reload
systemctl reload ssh.service
# verify: új connection key-vel + új connection password-del
ssh -i ~/.ssh/key root@host 'echo ok'                          # success expected
ssh -o PreferredAuthentications=password root@host 'echo ok'   # rejection expected
```

## Hol jelent meg

2026-05-15 szerver-update session, prod SSH key-only hardgate. Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Kapcsolódó

- [[11-wiki/ssh-timeout-remote-process-survives]]
- [[05-Memory/Infrastructure#SSH service Ubuntu 24.04]]
