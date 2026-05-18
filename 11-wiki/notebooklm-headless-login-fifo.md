---
name: NotebookLM headless login (FIFO-stdin pattern)
type: wiki
tags: ["#type/wiki", "#topic/automation", "#tool/notebooklm", "#topic/headless"]
created: 2026-05-10
updated: 2026-05-10
---

# NotebookLM headless login (FIFO-stdin pattern)

> Reusable pattern bármilyen interaktív CLI-flow-hoz ami headless szerveren TTY-t / ENTER-t vár, de a user csak GUI-n (VNC) tudja elvégezni a köztes lépést.

## A probléma

A `notebooklm login` parancs:
1. Megnyit egy Chromium ablakot (Playwright, persistent profile)
2. A user beírja a Google-credential-eket
3. **A CLI várja az ENTER-t** a TTY-ról (`[Press ENTER when logged in]`)
4. Mentés `~/.notebooklm/storage_state.json`-be

Headless szerveren, agent-ből futtatva nincs TTY → a parancs azonnal aborts:
```
Aborted!
```

## A megoldás — FIFO-stdin + sleep-holder

A trükk: 
1. Egy named pipe (FIFO) a stdin helyén
2. Egy `sleep` process EOF-mentesen NYITVA tartja a FIFO-t (különben a writer-zárás után a reader EOF-ot kap)
3. Az agent külön Bash-call-lal `echo > FIFO` küld ENTER-t a megfelelő pillanatban

```bash
# Setup
FIFO=/tmp/notebooklm-login.fifo
rm -f "$FIFO"
mkfifo "$FIFO"

# Holder process — 10 percig tartja nyitva a FIFO-t (különben EOF-szakadás)
sleep 600 > "$FIFO" &
HOLDER_PID=$!

# Login — a FIFO-ról olvas, log fájlba ír
DISPLAY=:99 notebooklm login < "$FIFO" > /tmp/notebooklm-login.log 2>&1 &
LOGIN_PID=$!
```

**A user közben:**
1. Csatlakozik VNC-n (`http://<host>:6080/vnc.html`)
2. Elvégzi a Google-loginot a Chromium-ban
3. Vár míg a NotebookLM homepage betölt
4. **Szól az agent-nek** ("kész")

**Az agent ellenőrzi vizuálisan + küldi az ENTER-t:**

```bash
# 1. Screenshot ellenőrzés — tényleg betöltött a homepage?
DISPLAY=:99 import -window root /tmp/vnc-check.png
# (Read tool olvassa a PNG-t — vizuálisan ellenőrzi a homepage-t)

# 2. ENTER küldése a FIFO-ba — a login script megkapja, menti a cookie-kat
echo "" > "$FIFO"

# 3. Várj 4-5 mp, ellenőrizd az output-ot
sleep 4
cat /tmp/notebooklm-login.log
# Várt: "Authentication saved to: /root/.notebooklm/storage_state.json"

# 4. Cleanup
kill "$HOLDER_PID" 2>/dev/null
pkill -f "notebooklm/browser_profile" 2>/dev/null
rm -f "$FIFO" /tmp/notebooklm-login.log /tmp/vnc-check.png
```

## Miért nem működik egyszerűbb verzió

| Próbálkozás | Mi történik | Miért rossz |
|---|---|---|
| `notebooklm login &` | Azonnal abort | Nincs stdin, az `input()` EOF-ot kap |
| `notebooklm login < /dev/null` | Azonnal abort | EOF rögtön |
| `notebooklm login < file_with_newline` | Azonnal abort | EOF a newline után |
| `notebooklm login < FIFO` (writer nélkül) | Bash blokkol a shell-startup közben | A FIFO open-for-read blokkol amíg nem nyitja valaki write-ra |
| `echo "" \| notebooklm login` | Azonnal abort + browser bezáródik | Az `echo` rögtön befejeződik → EOF, mielőtt a user logolt volna |
| `notebooklm login < FIFO` + `echo > FIFO` | ✓ Működik | A `echo` writer azonnal zár → EOF a reader-nek, de mert már korábban kapott egy újsort, az `input()` visszatér |

A `sleep 600 > FIFO` trükk **a writer-oldalt nyitva tartja** addig amíg az agent végre nem hajt egy szándékos `echo > FIFO`-t. A `sleep` write-er-ként van nyitva (output-redirect), de soha semmit nem ír — viszont a FIFO file-descriptor nyitva marad.

Amikor az agent `echo "" > FIFO`-t ír, az ENTER newline átmegy a `notebooklm login`-nak. A `sleep` továbbra is fogja a FIFO-t, de nincs több olvasandó adat → a `notebooklm login` `input()` visszatér.

## Reusability

A pattern bármi-re jó ami:
- Headless agent-ből futtatandó
- Köztes user-interakciót igényel (VNC, manuális lépés, stb.)
- TTY-t / ENTER-t vár

Példák:
- `gh auth login` (GitHub CLI device flow)
- Bármi ami `read -p "Press enter to continue"`-t használ
- Heroku CLI, Vercel CLI login flow-k

## Vizuális ellenőrzés

A `DISPLAY=:99 import -window root` ImageMagick-szel egy PNG-screenshot-ot ad. Az agent (Claude Code) a Read tool-lal képet "lát" — onnan ellenőrzi:
- A megfelelő homepage / app betöltött-e
- Nincs-e még egy 2FA / verify-screen
- A user ténylegesen végzett-e

Csak akkor küld ENTER-t a FIFO-ba ha a screenshot OK.

## Kapcsolódó

- [[05-Memory/Infrastructure#NotebookLM CLI auth (2026-05-10)]] — auth-fájl, élettartam, keepalive cron
- [[08-Sessions/2026-05-10-kgc-weboldal]] — első alkalmazás, KGC-weboldal session
