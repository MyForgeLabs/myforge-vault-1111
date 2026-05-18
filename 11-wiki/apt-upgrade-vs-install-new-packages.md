---
name: apt-upgrade-vs-install-new-packages
type: wiki
tags: ["#topic/apt", "#topic/linux", "#topic/kernel"]
created: 2026-05-15
updated: 2026-05-15
---

# `apt-get upgrade` ≠ új csomag-telepítés (kernel-update gotcha)

`apt-get upgrade` **CSAK létező csomagokat upgrade-el**. Új dependency-t — pl. `linux-image-6.8.0-117-generic` ami eddig nem volt installed — NEM húz be. Metapackage `linux-image-virtual` upgrade-elhető de a beépülő image-csomag külön telepítendő.

## Tünet

```bash
$ apt list --upgradable
linux-image-virtual ...      [upgradable from: 6.8.0-90.91 to 6.8.0-117.117]
$ apt-get upgrade -y
# fut, "kernel up-to-date" jelentés
$ uname -r
6.8.0-90-generic   # MÉG MINDIG RÉGI
$ ls /boot/vmlinuz-*
/boot/vmlinuz-6.8.0-90-generic   # csak régi
```

A metapackage version-szám frissült, de a `linux-image-X-Y-generic` package külön telepítendő — `apt-get upgrade` nem adott hozzá új csomagot.

## Megoldás

### 1. Explicit kernel install

```bash
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  linux-image-6.8.0-117-generic \
  linux-headers-6.8.0-117-generic \
  linux-modules-6.8.0-117-generic \
  linux-modules-extra-6.8.0-117-generic
```

### 2. Vagy `full-upgrade` / `dist-upgrade`

```bash
DEBIAN_FRONTEND=noninteractive apt-get -y \
  --allow-change-held-packages \
  full-upgrade
```

A `full-upgrade` agresszívabb: új csomagokat hozzáad, régieket eltávolít ha kell a dependency-resolution-höz. **Hold-eknél** (apt held packages) a `--allow-change-held-packages` flag kell.

## Verify

```bash
[ -f /var/run/reboot-required ] && cat /var/run/reboot-required.pkgs
# várt output:
# linux-image-6.8.0-117-generic
# linux-base

ls /boot/vmlinuz-*
# várt: /boot/vmlinuz-6.8.0-117-generic + a régi mellette
```

## Autoremove régi kernel(eket)

Reboot UTÁN az új kernel él, a régi marad fallback-ként. 2-3 hét után `apt autoremove -y` tisztít:
```bash
apt autoremove -y --purge  # --purge: config-fájlokat is törli
```

## `linux-virtual` metapackage held-back

Ha a metapackage held vissza (`5 not upgraded`):
```bash
apt-get install -y --allow-change-held-packages linux-virtual linux-image-virtual linux-headers-virtual
```

## Hol jelent meg

2026-05-15 prod + dev apt upgrade — mindkét VPS-en kernel 6.8.0-90/110 → 6.8.0-117 frissült, de **az első `apt-get upgrade` nem hozta be az új image-et** — explicit install kellett.

## Kapcsolódó

- [[11-wiki/ssh-timeout-remote-process-survives]]
- [[05-Memory/Infrastructure#Unattended-upgrades]]
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[vnc-stack-systemd-reboot-survival]] (sem-rokon, score=0.54)
