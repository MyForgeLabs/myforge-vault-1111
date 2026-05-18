---
name: ufw-limit-rate-limit-pattern
type: wiki
tags: ["#topic/ufw", "#topic/security", "#topic/firewall"]
created: 2026-05-15
updated: 2026-05-15
---

# UFW `limit` — public-but-protected rate-limit policy

`ufw limit <port>/tcp` egy köztes védelem `allow` és `deny` között: **6 connection / 30 sec / source IP** — utána DROP. Védelem brute-force / port-scan ellen, miközben a port publikusan elérhető marad.

## Mikor használd

- Dev-szerver dev-server-portjai publikus IP-n, de nincs alkalmazás-szintű auth (vite, FastAPI, etc.)
- SSH-n ha még password-auth-os (de inkább rakd `key-only`-ra)
- Bármilyen "publikus de NEM bot-magnet" port

## Alkalmazás

```bash
# régi allow rule törlése (ha van)
ufw delete allow 5173/tcp

# limit alkalmazás
ufw limit 5173/tcp comment 'robbantott-kereso vite (rate-limited)'

# verify
ufw status | grep 5173
# 5173/tcp                   LIMIT       Anywhere
```

## Miben különbözik az allow-tól

| Action | Kerál |
|---|---|
| `allow` | Korlátlan connection accept |
| `limit` | 6 conn / 30 sec / source IP, fölött DROP + log |
| `deny` | Minden DROP |
| `reject` | DROP + ICMP unreachable (informativabb az attacker-nek, ezért ritka) |

## Tesztelés (csak local!)

```bash
# 10 gyors connection ugyanarra a portra
for i in {1..10}; do
  curl -s -m 2 -o /dev/null -w "$i: %{http_code} (%{time_total}s)\n" http://localhost:5173 &
done
wait
# 7-8 connection után már timeout — UFW limit drop
```

## Iptables alatt mit csinál

`ufw limit` az `iptables -m recent` modult használja:
```
-A ufw-user-limit -m recent --update --seconds 30 --hitcount 6 --name DEFAULT --rsource -j ufw-user-limit-accept
-A ufw-user-limit-accept -m limit --limit 3/min -j LOG
-A ufw-user-limit-accept -j DROP
```

## Caveat: NEM auth helyettesítő

A `limit` csak rate-limit. Bot detection ellen védi az appot, de **autentikációt nem ad**. Ha az alkalmazás default-credential-es admin paneles WP/Tomcat etc, és valaki tudja a credentials-t, a 6 conn/30s nem véd. **Auth-réteg + limit = teljes**.

## Hol jelent meg

2026-05-15 dev VPS hardening — `5173` (robbantott-kereso vite) + `8000` (uvicorn) publikus portokat `limit`-re cseréltük, mert a user „egyelőre publikusak de védettek legyenek" mondta. Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Kapcsolódó

- [[05-Memory/Infrastructure#UFW rules]]
- [[11-wiki/openssh-config-d-load-order]]
<!-- auto-enriched 2026-05-18: +3 semantic cross-link via vault-search -->
- [[crystallize-threshold-ramp]] (sem-rokon, score=0.52)
- [[g-eval-bias-mitigation-pattern]] (sem-rokon, score=0.52)
- [[Crystallization-protocol]] (sem-rokon, score=0.51)
