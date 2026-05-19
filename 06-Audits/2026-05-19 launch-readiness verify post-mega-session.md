---
name: 2026-05-19 launch-readiness verify post-mega-session
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [audit, launch-readiness, hn-launch, deploy-verify]
---

# 2026-05-19 launch-readiness verify post-mega-session

Mega-session lezárása utáni deploy-verify a HN-launch (2026-05-26) elott.

## 1. HN-essay v2 deployment — RENDEREL HELYESEN

- **URL (helyes):** `https://myforgelabs.github.io/myforge-vault-1111/wiki/what-i-learned-building-self-improving-vault.en/` → HTTP 200, 71 426 byte.
- **URL (téves task-specifikáció):** `/11-wiki/...` → HTTP 404. A mkdocs build a Johnny-Decimal prefix nélküli `docs/wiki/` mappába pakolja a fájlokat.
- **§2 table:** 4 `<table>` blokk rendel a kimenetben — `## 2. The 8-axis architecture` 8-soros táblája HTML-table-ként van renderelve.
- **§3.3 asciicast:** A source NEM tartalmaz `<asciinema-player>` markert — csak egy `> ▶ Watch it live: [3-min terminal demo](.../demo/)` linket az essay-ben (line 130). A tényleges asciinema-player embed a `/demo/` aloldalon van: `AsciinemaPlayer` + `asciinema-player.css` + `.cast` referencia mind jelen — HTTP 200, működik.
- **Verdict:** ÉLES, működik. A task-prompt `/11-wiki/` path félreértés.

## 2. PUBLIC repo audit — TISZTA

- **Mai 11:00+ commit-ok:** 6 db (3× scheduled-sync 30-min cron + 1× hero-banner v2 + 1× Session 2026-05-19 close 11 Learnings + 1× scheduled-sync 12:30).
- **Tag-ek:** `v1.0.1`..`v1.0.8` mind ÉL (8 release megfelel). **Hiányzik a `v1.0.0` tag** a shallow clone-ban — gh oldalon ellenőrizendő (lehet shallow depth=50 artifact).
- **CHANGELOG.md:** v1.0.8 friss bejegyzés "round 10 — consolidation", 5 cross-cutting finding listázva, mega-session summary audit hivatkozva.
- **`docs/assets/hero-banner.png`:** 1280×640, 397 153 byte, MD5 `a0487d074d545c959642abeb260e7980` — egyezik a v2-specifikációval (1280×640, 397KB).

## 3. #14 GitHub-Linear bridge — **NEM LANDOLT**

- `/usr/local/bin/`-ben CSAK `vault-github-trending-recurrence` (más feature, idea #15). NINCS `vault-linear-*`, NINCS `vault-commit-history*`, NINCS `vault-github-linear-bridge`.
- A vault-ban nincs `github-linear` vagy `commit-history-bridge` named-file az utolsó 24h-ban.
- A session-log expliciten rögzíti: "**#14 GitHub commit-history + Linear bridge** — szubagent B még futott a session zárásakor, lehet hogy landolt v1.0.9-be" → **NEM landolt v1.0.9-be** (a legutolsó tag v1.0.8). A subagent task vagy nem futott le, vagy timeout/error nélkül elveszett.
- **Verdict:** 19/22 idea LANDED claim helyett valójában **18/22 (#14 nem landolt)**, vagy ha más idea közben land-elt, akkor a 19-es count másra hivatkozik. CHANGELOG.md v1.0.7-ben szerepel: "GitHub-Linear bridge still in flight". Tehát a végállapot a session zárásakor változatlanul "in flight" maradt.

## 4. MEMORY.md overflow — 26 054 byte (limit 24 400)

**+1 654 byte overflow (+6.8%)**. Top hosszúságok: 1. sor (mega-session összefoglaló) `~2 400 char`, 2. sor (EPIC super-session) `~2 100 char`, 3. sor (Boulium Phase 1+2) `~1 350 char`. Javaslat: az 1. sor mai super-session-summary átírása 1 mondatos pointer-re (target ~400 char), részletek a `06-Audits/2026-05-19 mega-session summary.md`-ben már megvannak — csak hivatkozni kell.

## 5. GitHub repo social snapshot (HN-launch baseline)

- **Stars:** 0 · **Forks:** 0 · **Watchers:** 0 · **Open issues:** 0 · **Open PRs:** 0
- **Topics:** 20 db (agentic-ai, anthropic, claude-code, crystallization, graphrag, karpathy-llm-wiki, knowledge-management, memgraph, notebooklm, obsidian, self-improving, vault, ai-agents, bge-m3, embedding, llm-eval, local-first, personal-knowledge-management, rag, vector-search)
- **CreatedAt:** 2026-05-18T08:04 (~33 óra public)
- **Workflows:** CI, Deploy docs site, Link check (external), PR Labeler, Mark stale — mind `active`

## Actionable items (5)

1. **#14 GitHub-Linear bridge pickup vagy defer-formalizálás** — task-spec szerint "még futott". A subagent eredménye nincs sehol. Vagy futtasd újra most (`vault-net-ingest` mintára 2-phase pending), vagy ratify-eld DEFERRED-ként a CHANGELOG.md-be (jelenleg v1.0.8 release notes "1 still in-flight (#14)" — ezt vagy v1.0.9-ben lezárni, vagy nyíltan deferred-listára tenni).
2. **MEMORY.md 1. sor (mega-session summary) lerövidítése** — target -1 800 char, detail az audit-ban. Ugyanaz a workflow mint a 2026-05-18 EPIC-summary refactor a 2. sorba.
3. **HN-essay task-prompt URL-fix** — bárhol a docs/wiki/audit-ban hivatkozzuk `/11-wiki/` URL-lel a publikus essay-t, az 404. Helyes: `/wiki/`. Egy `grep -r "/11-wiki/" docs/` kell.
4. **`v1.0.0` tag verify gh-oldalon** — shallow clone depth=50-ben hiányzik, de a release-list szerint létezik. `gh release view v1.0.0`-val konfirmálni.
5. **Star-count baseline: 0** — HN-launch (2026-05-26 15:00 UTC) ELŐTTI snapshot készen. Post-launch összehasonlításra. Pre-launch warm-up: javasolt `gh repo edit --description` polish + 1-2 reddit/twitter pre-tease, mert 33 óra publicban 0 star = nincs organic discovery yet.
