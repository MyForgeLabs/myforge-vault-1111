---
name: HN-launch — magyar útmutató felhasználónak
type: audit
created: 2026-05-20
updated: 2026-05-20
project: superintelligent-vault
tags: ["#type/audit", "#lang/hu", "topic/marketing"]
related:
  - "[[2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]]"
---

# HN-launch — magyar útmutató felhasználónak

> [!info] Cél
> Ez a fájl ~5 perc alatt elolvasható. Konkrét lépések, magyarul, a kedd 2026-05-26-i Hacker News submit-hoz. Az angol audit a részletes anyag; ez itt a "te mit csinálsz" cheat-sheet.

## Mit fogunk csinálni 1 mondatban

Kedden, 2026-05-26 17:00-kor (magyar idő, = 15:00 UTC) submit-olunk egy linket a Hacker News-ra; ha jól megy, ~200-500 GitHub-star jön egy hét alatt, és néhány érdemi technikai-beszélgetés a comment-szekcióban.

## Mi az "angle" és miért C-2

A "wedge claim" a szlogen ami miatt a HN-olvasó kattint — az egy mondat amit a title-ben + body első bekezdésében lát, és eldönti hogy 10 másodperc vagy 10 perc.

Három angle-t mértünk fel (lásd angol audit). A nyertes a **C-2**:

> "Egy 5-másodperces schema-migration csendben tönkrevágta 15 CLI-eszközömet — köztük a teljes MCP-tool stack-et. Egyik sem dobott hibát. 30 órán át üres eredmény jött. Itt a downstream-grep + AST classifier + auto-patch amit erre csináltam."

Miért ez nyer: **friss** (ma történt), **konkrét** (15 eszköz, 30 óra), **engineering-hiteles** (a magad hibáit nevezed meg), **reusable** (bárki aki DB-API-2.0 drivert használ találkozhat ezzel). A HN-közönség ezt szereti: "valaki elcsesztem és itt a playbook hogy mások ne".

## A te lépéseid időpontra bontva

| Mikor | Mit | Mennyi idő |
|---|---|---|
| **Most → vasárnap** | HN-account regisztráció ha még nincs: `news.ycombinator.com` → Login → create | 1 perc |
| **Hétfő este** | Olvasd át az angol audit "C-2 final-pick" + "10 anticipated comment-replies" szekcióit | 30 perc |
| **Kedd 16:50 (HU)** | Nyiss egy böngészőt: HN + X (Twitter) + GitHub repo + a wiki URL. Készülj a copy-paste-re | 10 perc |
| **Kedd 17:00 (HU)** | HN submit: title + URL paste-eli, body üres marad (mert URL-submit, nem text-submit) | 30 másodperc |
| **Kedd 17:30 (HU)** | X-thread post: a 11-tweet thread az angol auditból, paste-and-go | 5 perc |
| **Kedd 17:30-19:00 (HU)** | HN-comment-watch + replyolj a 10 előre megírt szöveg alapján | ~90 perc |
| **Szerda reggel** | Reddit r/LocalLLaMA submit | 1 perc |
| **Csütörtök reggel** | Reddit r/ObsidianMD submit | 1 perc |

> [!info] Az URL amit submit-olsz
> NEM a repo, hanem a wiki-oldal: `https://myforgelabs.github.io/myforge-vault-1111/wiki/schema-migration-downstream-grep-checklist/`
> A title: `One schema-migration silently broke 15 CLI tools. Here's the safety-rail`

## HN-comment-protokoll (fontos!)

A HN-comment-szekciónak megvan a maga ritmusa. **Ezt érdemes betartani**:

1. **NE válaszolj minden kommentre az első 15 percben** — ez astroturf-gyanús, és a moderátorok flag-elik. Tempó: **1 reply / 8-10 perc** az első 90 percben.
2. **Minden válasz first-person** ("én", "nekem", "az én projektem") — sose írj "we"-t, sose "the team", mert egyedül vagy.
3. **Koncedáld a hibát ha jogos** — ha valaki rátalál egy gyengeségre, ne védekezz. "Fair, igazad van, ezt nem dokumentáltam jól" >> minden marketing-szöveg.
4. **Az előre megírt 10 reply** (másik audit) a leggyakoribb kérdés-formákat fedi le. Ha pontosan illik, paste-eld; ha nem, írd át 1-2 mondatban.
5. **A nyelv: egyszerű, technikai, magyaros-angol OK** — a HN-olvasó nem natív-angol-fasiszta, az lényeg hogy konkrét.

## Mit NE csinálj

> [!warning] 5 piros vonal

1. **NE kérj upvote-ot sehol** — sem X-en, sem Discord-on, sem privát üzenetben. A HN-modok ezt szankcionálják (shadow-ban).
2. **NE használj emoji-t a title-ben** — automatikus Tier-C jelzés.
3. **NE válaszolj gépiesen / chat-bot-szerűen** — a HN azonnal kiszúrja. Ha unalmas a komment, hagyd ki.
4. **NE link-spam-elj** a comment-szekcióban — a `github.com/...` link **csak akkor**, ha közvetlenül kérik. Inkább idézz konkrét fájl-nevet ("nézd a `vault-schema-migration-victim-audit` source-át a repo-ban").
5. **NE ígérj autonomous-RSI-t / "self-improving AI"-t** — a B-8 Critic κ=0.708 *substantial agreement*, de **NEM autonomous-apply-mode** (az W23-ig gated). Ha valaki kérdezi, koncedáld: "shadow-monitoring még, nem éles auto-apply".

## Mi történik ha bomban (Tier C)

Ha kedd 19:30-ra a poszt <40 pont, és nem kerül a first-page-re → **Tier C, buried**.

Ebben az esetben:
- **NE küldd be újra ugyanazt az URL-t 14 napon belül** — a HN duplicate-detection elkapja, és akkor permanent-shadow-ban-t kapsz a domain-re.
- Várj **2 hetet**, próbáld újra **Angle A-val** (Show HN: a repo-link verzió). Más title, más URL (repo-root, nem wiki-page).
- A Reddit-submitek attól még mehetnek szerda + csütörtök reggel — Reddit ≠ HN, külön közönség.

> [!success] Ha Tier-S
> ≥150 pont, first-page, ≥2 óra ott-marad → ~500+ GitHub-star egy hét alatt + 5-10 érdemi issue/PR. Az X-thread-et ekkor érdemes T+90 percnél egy "front-page-on" screenshot-tal frissíteni.

## Mit fogok én csinálni közben (agent)

- **Karpathy-essay HU+EN epilogue** — a `28-day continuous run` reflexió hozzáírása, hétvégén
- **Wiki English-translation finalize** — `schema-migration-downstream-grep-checklist.en.md` ÉLES legyen a publikus docs-site-on
- **Comment-plan-bővítés** — kész (10 anticipated reply az angol audit végén)
- **NotebookLM-elemzés** — competitor-research: az utolsó 5 hasonló profilú HN-launch (Karpathy-style personal-OSS) timing + first-90-min pattern-je
- **Backup-angle-szövegek** — ha C-2 megy bele Tier-C-be, Angle A 2 hét múlva paste-ready legyen

## Kapcsolódó

- [[2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]] — a teljes angol audit (title, body, 10 reply, backup-angle-ek)
- [[2026-05-19 GitHub launch playbook]] — a stratégiai keret
- [[2026-05-20 B-8 Critic 100-bullet clean re-sample (kappa 0.708)]] — a κ-mérés módszertan-forrása
- [[../11-wiki/schema-migration-downstream-grep-checklist]] — a wiki-oldal amit submit-olunk
