---
name: CloakBrowser stealth Chromium — fingerprint bypass playbook
type: wiki
tags: ["#type/playbook", "#tech/scraping", "#tech/playwright"]
created: 2026-05-11
updated: 2026-05-11
---

# CloakBrowser stealth Chromium — fingerprint bypass

Drop-in Playwright/Puppeteer-helyettesítő stealth Chromium-binary 49 C++ source-szintű fingerprint-patch-csel (NEM JS-injection). Cél: Cloudflare Turnstile + FingerprintJS + BrowserScan + reCAPTCHA v3 passzív átmenet.

**Forrás:** [CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser) (5.2k★, MIT, Python + JS, 78 napos repo, 2026-05-11 trending #4)

## Telepítés — root Linux szerveren

```bash
# Venv-ben (root-szerveren ajánlott, system Python ne szennyezzük):
source /root/.notebooklm-venv/bin/activate
pip install cloakbrowser

# Binary download (~200 MB, egyszeri)
cloakbrowser install
cloakbrowser info  # -> /root/.cloakbrowser/chromium-146.x.x.x/chrome
```

## Root flag-ek (KÖTELEZŐ)

Chrome rootként sandbox-nélkül indul csak. CloakBrowser launch root-on:

```python
from cloakbrowser import launch

browser = launch(args=["--no-sandbox"], humanize=True)
```

- `--no-sandbox` — Chrome sandbox ki (root-on KÖTELEZŐ, különben `Failed to launch chrome process` exit-tel áll meg)
- `humanize=True` — emberi egér-görbe, billentyűzet-timing, scroll-pattern (behavioral detection-pass)

## Fingerprint-pass részletek (Sannysoft test PASSED — 2026-05-11)

A `https://bot.sannysoft.com/` minden alap headless-detection PASSED, headless szerveren is:

| Test | Eredmény |
|---|---|
| User Agent | Mozilla/5.0 Win NT 10.0 Chrome/146.0.0.0 |
| **WebDriver** | **missing (passed)** — legkritikusabb fingerprint |
| Chrome | present (passed) |
| Plugins Length | 5 (normál headless: 0) |
| Plugins is PluginArray | passed |
| Languages | en-US |
| WebGL Vendor | Google Inc. (NVIDIA) |
| **WebGL Renderer** | **ANGLE (NVIDIA GeForce RTX 3060 Laptop GPU) Direct3D11** — fake GPU-string headless szerveren |
| Broken Image Dimensions | 16x16 |

## Cloudflare Turnstile gotcha (2026-05-11)

`https://nowsecure.nl/` (passive Turnstile-demo) **NEM ment át** 2s `wait_for_timeout` alatt. A challenge-page betöltött (175 KB HTML), de a "Verify you are human" checkbox még látszott a screenshot-on.

**Megoldás opciók:**

1. **Hosszabb wait:** `page.goto(url, wait_until="networkidle", timeout=30000)` + utána `page.wait_for_timeout(8000)` 
2. **Interactive click:** `page.locator("input[type=checkbox]").click()` (Turnstile checkbox-on)
3. **Wait specific selector:** `page.wait_for_selector("[data-cf-bm]")` (cf-bm cookie set after pass)

## Escalation pattern: firecrawl → playwright → cloakbrowser

```
1. firecrawl (self-hosted localhost:3012)
   ↓ ha blokk
2. playwright (sima headless Chromium)
   ↓ ha blokk vagy fingerprint-detect
3. cloakbrowser (drop-in, stealth, --no-sandbox + humanize=True)
   ↓ ha Cloudflare Turnstile
4. cloakbrowser + interactive click + hosszabb wait
```

## Mikor érdemes (use-case)

- **Magyar Hostinger/Apache competitor scrape** — NEM kell, normál playwright/firecrawl elég (hindent.hu, premiumdental.hu, dentalcoop.hu)
- **Cloudflare-védett SaaS / publicly-scrape** (pl. SEMrush, Booking.com analytics, LinkedIn) — itt jön be a többletérték
- **Bot-detection-aktív magyar oldalak** (pl. NAV publikus űrlapok, Cégtár stb.) — ha a normál playwright-tal "access denied"-ot kapsz

## Etikai határ

**Csak nyilvános adat** (review, ár, meta), NEM:

- Paywalled tartalom (cracked subscription)
- ToS-explicit-tiltott scrape (Facebook Graph, Twitter API megkerülése)
- Személyes adat scrape (GDPR-kockázat, kül. magyar kontextusban)

## Drop-in Playwright migráció

```diff
- from playwright.sync_api import sync_playwright
- pw = sync_playwright().start()
- browser = pw.chromium.launch(headless=True)
+ from cloakbrowser import launch
+ browser = launch(args=["--no-sandbox"], humanize=True)

page = browser.new_page()
page.goto("https://example.com")
# ... rest of your code works unchanged
```

A `humanize=True` opcionális (nélküle is működik), de behavioral-detection-aktív site-okon (pl. PerimeterX) szükséges.

## Kapcsolódó

- [[05-Memory/Infrastructure#Chrome DevTools MCP — telepítés és root-flag (2026-05-10)]] — másik Chrome-based eszköz root-on, ugyanazzal a `--no-sandbox` mintával
- [[08-Sessions/2026-05-11-github-repo]] — első spike + Sannysoft validation
- [[11-wiki/digital-signage-player-gotchas]] — másik playbook ahol Chrome quirkjei számítanak
