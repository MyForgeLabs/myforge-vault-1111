---
name: UFW `LIMIT IN` modern frontend trap
type: wiki
created: 2026-05-21
updated: 2026-05-21
tags: [wiki, firewall, ufw, debugging, "#tech/infra"]
related: [Infrastructure, robbantott-kereso]
---

# UFW `LIMIT IN` modern frontend trap

## A trap

A `sudo ufw limit <port>/tcp` szabály bekapcsolja az iptables `recent`-modult **max 6 connection / 30 másodperc / IP** korláttal. Ez **brute-force-elhárításra** való (SSH, login-form), nem frontend-szolgáltatásokra.

**De**: egy modern frontend (Vite dev-mode, Webpack dev-server, sőt sok production-asset-szerver is) HTTP/1.1-en **10+ párhuzamos image-load**-ot indít új TCP-konnektoton — a 7-edik fail-elődik DROP-pal.

## A tünet

- Kliens-böngészőben: `net::ERR_CONNECTION_REFUSED` (Chrome) / `NS_ERROR_CONNECTION_REFUSED` (Firefox)
- Szerveren `curl http://localhost:<port>/`: **200 OK** azonnal
- `ss -tlnp`: a port LISTEN, semmi baj
- `ufw status verbose`: `LIMIT IN` látszik az adott porton (kulcs-jel)

## Diagnosztika (3 perces)

```bash
sudo ufw status verbose | grep -E "LIMIT|<port>"
# Ha LIMIT IN — találtuk

# Stress-test:
for i in {1..10}; do
  curl -sS -m 3 -o /dev/null -w "%{http_code} " http://<host>:<port>/
done
# Várt: 10× 200 OK. Ha 6 után CONNECT-fail vagy timeout — bingo
```

## Fix

```bash
sudo ufw delete limit <port>/tcp
sudo ufw allow <port>/tcp comment 'frontend (was rate-limited)'
sudo ufw status verbose | grep "<port>"
```

## Másik nézőpont — érdemes-e?

A `LIMIT IN` brute-force-protection ELLEN szól, az `ALLOW IN` viszont nem védi a portot DDoS-tól. Hosszú távon a HELYES megoldás:

1. **Reverse-proxy mögé** (Caddy / Nginx) — a publikus port csak 80/443, a backend portok `127.0.0.1` bind-en — sose érhetők el direkten
2. **Cloudflare / front-CDN** rate-limit ott
3. **iptables custom** `--limit 30/min --limit-burst 100` finomabb hangolásra

A quick fix (`delete limit + allow`) RÖVID távra OK, ha:
- Csak fejlesztői / belső szolgáltatás (Vite dev-mode)
- Token-mögötti
- Vagy a backend amúgy is csak app-ből hívódik

## Példa: robbantott-kereső (2026-05-21)

- `:5173` (Vite frontend) + `:8000` (FastAPI uvicorn) — UFW `LIMIT IN`-en voltak
- A kgc-berles `/alkatresz-kereso` aloldal iframe-je 10+ image-loaddal indul → 7. CONN_REFUSED → szürke "törött dokumentum" ikon Chrome-ban
- Belső curl-ből (a szerveren) sose volt repro — kívülről mindig elesett
- Fix: ufw `delete limit + allow` → stress-test 10× curl mind <3ms 200 OK
- Hosszú távra: Next.js rewrites a kgc-berles:3004-en → proxy 127.0.0.1:5173 + 127.0.0.1:8000-re, akkor csak az access-gate-mögötti port publikus

## Kapcsolódó

- [[../05-Memory/Infrastructure]] — szerver-infra állapot
- [[../02-Projects/robbantott-kereso]] — projekt
- Session: [[../08-Sessions/2026-05-21-kgc-weboldal]]
