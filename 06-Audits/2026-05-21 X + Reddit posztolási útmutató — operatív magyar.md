---
name: X + Reddit posztolási útmutató — operatív magyar
type: audit
created: 2026-05-21
updated: 2026-05-21
project: superintelligent-vault
tags: ["#type/audit", "#lang/hu", "topic/marketing", "topic/launch"]
related:
  - "[[2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]]"
  - "[[2026-05-20 HN-launch — magyar útmutató felhasználónak]]"
---

# X + Reddit posztolási útmutató — operatív magyar

> [!info] Cél
> Lépésről-lépésre, copy-paste-ready, magyar útmutató **a HN-submit utáni** X + Reddit kaszkádra. Minden szöveg az angol auditból, paste-and-go formában.

## Időrend áttekintés (kedd-péntek)

| Mikor (HU idő) | Hol | Mit | Mennyi idő |
|---|---|---|---:|
| **Kedd 17:00** | **HN** | Submit (külön útmutató) | 30 mp |
| **Kedd 17:30** | **X.com** | 11-tweet thread post | 5 perc |
| **Kedd 17:30-19:00** | HN-comments | Replyolj a 10 előre-írott válasz alapján | ~90 perc |
| **Kedd 18:30** | **X.com** | T+90 min "fronton" reply ha Tier-S | 2 perc |
| **Szerda 09:00** | **Reddit r/LocalLLaMA** | Submit | 3 perc |
| **Szerda 14:00** | Reddit-comments | Az első 5-10 reply szembe-jövő kommentre | ~30 perc |
| **Csütörtök 09:00** | **Reddit r/ObsidianMD** | Submit | 3 perc |
| **+1 hét múlva (csak ha κ=0.708 átment HN-scrutiny-n)** | **Reddit r/MachineLearning** | [P] submit | 5 perc |

---

## 1. X.com (Twitter) thread — Kedd 17:30 HU

### Mit fogsz csinálni

11 tweet egy szálban. A **1/-as első tweet** önállóan is megáll mint hook; a többi 10 tweet erre van replyolva mint thread.

### Lépések a böngészőben

1. Menj a [x.com](https://x.com) — bejelentkezve
2. Kattints a **"Post"** gombra (a + ikon, balra fent)
3. Paste-eld be **1/-es tweet szövegét** (lásd lent), kattints **"Post"**
4. Most az 1/-es tweet megjelent. **Kattints alá**, és a "Reply" mezőbe paste-eld a **2/**-es tweetet. Post.
5. **Folytasd ugyanígy 11-ig.** Minden következő tweet az ELŐZŐ-re replyolj (nem az 1/-re, hanem amit éppen az előbb posztoltál).
6. Az utolsó **(11/)** tweet végén ott a repo-link — ez az "end of thread" jelzés.

> [!warning] X-thread gotcha
> NE használd az X "Add another Post" pluszikont mert az schedule-ölés-ható. Mi MANUÁLIS thread-et akarunk, mert így minden tweet külön-külön kap engagement-et és önálló timestamp-pel keresztezhetjük HN-szel (Cmd+F-elhetők egyenként).

### A 11 tweet (copy-paste, sorrendben)

> [!tip] Tip
> Mindegyik tweet alatt egy üres sor van — az nem-szám tartozzon a tweet-hez (egy tweet 280 char). Ha a thread számláló X-en megtörik, az nem baj.

**1/**

```
I open-sourced the Obsidian vault three CLI agents share.

Claude Code, Codex, and Gemini all read+write the same markdown tree.
Self-improving via LLM-as-judge crystallization. A Memgraph knowledge
graph underneath with a 280× search speedup.

MIT-licensed, $0 marginal cost. 28-day continuous public run. 🧵
```

**2/**

```
The pattern is @karpathy's LLM-Wiki idea, taken literally:

  10-raw/        immutable inputs
  11-wiki/       distilled evergreen
  02-Projects/   state
  07-Decisions/  ADRs

Plus 85+ CLI tools that move bullets between layers automatically
at session-end.
```

**3/**

```
The auto-crystallization loop:

session-end → G-Eval LLM-as-judge scores each Learning bullet →
batch preview → user confirms → atomic write to the right vault
layer → sandbox branch + revert-monitor.

96.7% verdict-agreement on a 30-pair human-labeled calibration set.
```

**4/**

```
Today's milestone: B-8 RSI Critic Layer-4 hit production-flip.

100-bullet clean baseline, content-classifier ground-truth (NOT
mock-scorer-labeled). Cohen's κ = 0.708 ("substantial"). Effective
false-accept rate ≈ 0% post-noise-inspection.

Apply-mode still gated to W23. Carefully.
```

**5/**

```
The cost trick: "subagent fanout."

You spawn 8 parallel Claude Code subagents from inside one Claude
Code session. Subscription-bundled, $0 marginal. 27+ fanouts in
today's working session, 22 tasks landed in 6 hours.

(Disclosure: assumes Claude Code subscription.)
```

**6/**

```
The graph layer:

Memgraph CE 3.10 (free, local). 13,307 entities, 24K edges, 100%
typed. Native `CREATE VECTOR INDEX` replaced numpy-cosine.

Mean 1ms / p95 2.6ms — 280× faster. One Cypher line.
```

**7/**

```
Today's surprising find:

A 5-second schema-migration silently broke 15 of my CLI tools.
Including the entire MCP-tool stack. None threw errors. The whole
stack returned empty results for 30 hours.

Now: vault-schema-migration-victim-audit weekly cron + git hook.
```

**8/**

```
Save this thread — I'll be writing each up as standalone wikis:

- subagent-fanout (the $0-cost pattern)
- 15-silent-victim postmortem
- B-8 Critic κ=0.708 calibration methodology
- Memgraph native vector-index migration
- mgclient autocommit silent-rollback (2 weeks ago)
```

**9/**

```
Why three CLI agents instead of one?

Different agents, different temperaments. Claude is conservative.
Codex is fast and literal. Gemini is loose and exploratory. They
write to the same AGENTS.md via symlinks, with per-chat
session-IDs to prevent crosstalk.
```

**10/**

```
What's NOT in here:

- no fine-tuning
- no custom model
- no proprietary RAG library
- no business model
- no autonomous apply-mode (gated to W23)

Just markdown, Memgraph, bge-m3, mkdocs, and 85+ small bash/Python
tools. Boring stack, intentionally.
```

**11/**

```
Repo: github.com/MyForgeLabs/myforge-vault-1111
Site:  myforgelabs.github.io/myforge-vault-1111

283 wikis. 161 audits. 49 ADRs. 25 cron jobs. v1.0.10.2 tagged.

If you build on it, ping me — I'd love to see your 11-wiki/ tree.
If you find a bug, open an issue. Especially the embarrassing kind.
/end
```

### Optional T+90 reply (csak ha HN Tier-S)

Ha 18:30-ra a HN-poszt >100 pont és first-page-en van:

1. Készíts egy screenshot-ot a HN front-page-ről (cmd+shift+4 macen, Win+Shift+S Windows-on)
2. Replyolj a **11/** tweetedre:

```
Update: front-page on Hacker News, T+90 min.

[csatold a screenshot-ot]

Thanks for the engagement. Going back to reply to comments —
slow tempo (1 reply / 8 min) so it doesn't look astroturf-y.
```

### X-anti-rules

> [!warning] NE
> - **NE** kérj retweet-et / quote-tweet-et explicit ("RT plz") — engagement-bait, alacsonyabb reach
> - **NE** tag-eld @karpathy-t **kivéve** ha ő már quote-olt valamit a thread-ből — ne-spam-policy
> - **NE** kötelező hashtag — `#opensource #AI #LLM` engagement-bait jelzés, NEM kell
> - **NE** szerkeszd-át a tweetet 1 órán belül — az engagement-loss + Community Note flag

---

## 2. Reddit r/LocalLLaMA — Szerda reggel 09:00 HU

### Mit fogsz csinálni

Egy submit a `r/LocalLLaMA` subreddit-re. Link-post (NEM text-post), és a body-t a poszt utáni **első kommentként** add hozzá.

### Lépések

1. Menj a [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) — bejelentkezve
2. **Olvasd át a subreddit rules-t** (jobb sidebar) — `r/LocalLLaMA` viszonylag lazább, de:
   - **No self-promotion without contribution** — a posztod konkrét findings-okat tartalmaz, OK
   - **Code/demo links allowed** — OK
3. Kattints **"Create a post"**
4. **Post type:** "Link" (URL post). NE válaszd a "Text" típust, mert nem akarunk magyarázó-szöveget a posztban — az inkább a komment.
5. **Title:** (90 char)
   ```
   Self-improving knowledge graph for CLI agents — $0 marginal cost, 28-day run, MIT
   ```
6. **URL:**
   ```
   https://github.com/MyForgeLabs/myforge-vault-1111
   ```
7. **Flair:** Válaszd a "**Resources**" vagy "**Discussion**" flair-t (a sidebar-on listázzák). Ha nincs egyértelmű "Resources" → "Discussion"
8. **NSFW, Spoiler:** OFF, OFF
9. Kattints **"Post"**
10. **Most a poszt megjelent.** Görgess le, és a **saját poszt alá** írj egy kommentet — a Reddit-rules szerint a body-szöveg POST-on belül vagy első own-comment-ben, és a hosszabb body első-own-comment-tel jobban performál (a poszt-listán a link gif/preview látszik, NEM 400 szó text).

### Az első own-comment (Reddit r/LocalLLaMA)

> [!tip] Reddit-markdown
> A Reddit-markdown támogatja a `**bold**`, `_italic_`, `>` quote, és a `[text](url)` linket. Az alábbi szöveg már Reddit-markdown-syntaxisban van.

```
Sharing a personal project I've been running for 28 continuous days
and just tagged v1.0.10 (MIT-licensed).

**The setup:** a single Obsidian-readable markdown tree that Claude
Code, Codex CLI, and Gemini CLI all read and write to via shared
AGENTS.md symlinks. On top of it: a Memgraph CE 3.10 local instance
(13,307 entities, 24K edges, native vector-index, 1ms p50 search)
and a structured SQLite "KO-DB" with 23.9K extracted facts.

**The interesting bit for this sub** is the **subagent-fanout**
pattern. Spawn 8 parallel Claude Code subagents from inside one
parent session. Because they're subscription-bundled, marginal cost
is $0. I've used this pattern for: bulk wiki translation (HU→EN,
71 pages), G-Eval scoring, fact extraction, conflict-audit
cross-checks, and a 171-file Tier-1 backfill (177 subagent calls,
~2h wall-clock, $0 cost). Yes, it depends on you paying for Claude
Code — there's no free lunch, just a flat-fee one.

**Recent milestone:** B-8 RSI Critic Layer-4 hit production-flip
gate. 100-bullet clean baseline, Cohen's κ = 0.708 ("substantial").
Manual 10/10 false-accept inspection found that all 10 FAs were
actually content-classifier mining-noise, not real Critic failures
— effective FA rate ≈ 0%. Apply-mode (VAULT_CRITIC_ACTIVE=1) is
still gated to W23 after 2 weeks of shadow-monitoring. Carefully.

**Embeddings:** bge-m3 (multilingual, runs locally, MIT). **Reranker:**
bge-reranker-base for smart 2-pass retrieval on ambiguous queries.

**The auto-improvement loop:** at session-end an LLM-as-judge
(G-Eval, with bias-mitigation v0.3 that knocked self-enhancement
bias from 0.880 → 0.760 conf) scores each Learning bullet. High-
confidence Passes are batched and previewed to the user; on
confirm they get atomic-written to the right vault layer with a
sandbox-branch safety gate and a revert-monitor.

**Today's painful discovery:** a single column-drop in the KO-DB
silently broke 15 of my CLI tools, including the entire MCP-tool
stack. None of them threw errors. Now: vault-schema-migration-
victim-audit ships as a weekly cron + git pre-commit hook.

**What's open-source:** everything. ~5,000 LOC across 85+ small
Python and bash tools, 283 wikis, 161 audits, 25 cron jobs, the
full safety pipeline, the G-Eval prompts, the GEPA reflection
skeleton, the schema-migration audit CLI.

Repo: github.com/MyForgeLabs/myforge-vault-1111
Docs: myforgelabs.github.io/myforge-vault-1111

Happy to dig into the κ=0.708 calibration methodology, the
schema-migration audit-rail, or the 15-silent-victim postmortem.
Most curious for feedback on the GEPA Pareto-front next.
```

### r/LocalLLaMA comment-protokoll

- **Várj ~30 percet** a poszt után, mielőtt válaszolnál bárkinek — a posztodat kell hogy felfedezzék előbb
- **Első 5-10 comment közül a "Why X over Y?" típusra válaszolj** (technikai-érdeklődés jelzés)
- Ha a komment hangja **rossz** ("this is just X with extra steps") → **NE válaszolj** azonnal. Várj 1-2 órát, és ha valaki más megválaszolja helyetted, jó. Ha senki, akkor 1-2 sentence-ben koncedáld a valid részt + tedd hozzá a különbséget
- A `r/LocalLLaMA` lassabb-ritmusú mint HN, **8-12 óra alatt** alakul ki a komment-szál. **Csekkold újra estére** (kedd 20:00 HU)

---

## 3. Reddit r/ObsidianMD — Csütörtök reggel 09:00 HU

### Mit fogsz csinálni

Egy submit a `r/ObsidianMD`-re. **MÁSIK** angle, mert ez a sub az Obsidian-vault-rendszerre fókuszál, NEM az AI-stack-re.

### Lépések

1. Menj a [r/ObsidianMD](https://reddit.com/r/ObsidianMD) — bejelentkezve
2. **Olvasd át a sidebar-rules-t**:
   - **No SaaS / signup-gated content** — a tiéd MIT-OS, semmi signup, OK
   - **Personal vault-sharing OK** ha közösség-builder
   - **Self-promotion: csak ha 90/10 community-contribution** — a tiéd open-source playbook, OK
3. Kattints **"Create a post"**
4. **Post type:** "Link"
5. **Title:** (94 char)
   ```
   Self-improving Obsidian vault — Karpathy LLM-Wiki + 283 auto-distilled wikis (MIT)
   ```
6. **URL:**
   ```
   https://github.com/MyForgeLabs/myforge-vault-1111
   ```
7. **Flair:** "**Vault**" vagy "**Showcase**" vagy "**Plugin**" — ami szembe-jön. Ha bizonytalan, "Showcase"
8. Kattints **"Post"**
9. A poszt megjelent → **első own-comment** mint Reddit r/LocalLLaMA-nál

### Az első own-comment (Reddit r/ObsidianMD)

```
Sharing my Obsidian vault with the community — open-source (MIT,
v1.0.10.2), with the full agent toolkit that maintains it.
28 days of continuous public work.

Structure is Johnny-Decimal:

    00-Meta/         vault rules + tag taxonomy + frontmatter schema
    01-Daily/        daily logs
    02-Projects/     project state
    03-Hosts/        infra
    07-Decisions/    ADR-style decision log (49 today)
    08-Sessions/     raw session logs (Karpathy "raw" layer)
    10-raw/          immutable external inputs
    11-wiki/         distilled evergreen notes (Karpathy "wiki" layer, 283 today)

What's automated: at the end of every chat session with Claude Code
/ Codex / Gemini, a "crystallization" pipeline reads the session
log, extracts Learning bullets, scores them with an LLM-as-judge
(G-Eval, 96.7% verdict-agreement against a 30-pair human-labeled
calibration set), previews them as a batch ("propose 12
propagations — OK?"), and on confirmation writes them to the right
vault layer. The session file itself stays as the raw reference;
the distilled content goes evergreen.

This week the Critic-review (Layer-4 of a multi-layer-safety-gate)
hit production-flip — Cohen's κ=0.708 on a 100-bullet clean
baseline.

Plus: Obsidian Tasks plugin for backlog, DataviewJS for the audit
dashboard, mkdocs-material publishes the public subset.

Three CLI agents (Claude/Codex/Gemini) all share the vault. They
each see AGENTS.md via symlink, with per-chat session-ID env
vars so they don't crosstalk.

What I'd love feedback on:

- Tag taxonomy — I lock to #project/<slug> #env/prod #type/host
  style. Is yours different?
- 11-wiki organization — flat vs deep. I went flat (~283 files at
  one level). Curious if that scales past 1k.
- Daily vs session — I keep both. Daily is human, session is agent.
  Anyone unified them?

Repo + docs: github.com/MyForgeLabs/myforge-vault-1111

Note for the mods: this is genuinely a personal project, not a
SaaS, no signups, no email gate, MIT-licensed. Happy to remove if
it bumps a rule.
```

### r/ObsidianMD comment-protokoll

- Ez a sub **konstruktív, nem-cinikus**. Várd a "milyen plugin kell hozzá?" + "hogyan integrálható X-szel?" típusú kérdéseket
- **Mod-friendly:** az utolsó-bekezdés `Note for the mods` szándékosan benne van — előzd meg a remove-ot
- **Vissza-kérdezz** mindenki feedback-jére ("Mit használsz a tag-taxonomy-dhoz?"). A `r/ObsidianMD` szereti a kétoldalú beszélgetést, NEM az "én bemutatom, te bámulj" formátumot
- Ha valaki azt mondja "ez nem Obsidian-vault, ez egy SaaS-mockup" — koncedáld konkrétan: "Igazad van hogy 85 CLI eszköz nem 'plain vault'. A markdown-tree az Obsidian-natív, a CLI-rétege opt-in és a v1-en csak akkor használni ha kell"

---

## 4. Reddit r/MachineLearning [P] — Csak ha κ=0.708 átment HN-scrutiny-n (1 hét múlva)

> [!warning] CSAK akkor küldd be
> Ha a HN-poszton a κ=0.708 mérés-módszertanra **NEM jött komoly kritika**, vagy ha jött és tudtad jól-koncedálni. r/MachineLearning **szigorúbb** mint HN — egy "n=100 substantial-agreement" típusú claim itt komoly statistical pushback-et kap. Ha bizonytalanok vagyunk, hagyd ki.

### Lépések

1. Menj a [r/MachineLearning](https://reddit.com/r/MachineLearning) — bejelentkezve
2. **MÉLY-olvasd át a sidebar rules-t** — ez a sub a legszigorúbb:
   - **`[P]` tag KÖTELEZŐ** projekt-posztra
   - **No "Show HN"-style marketing** — methodology-rich content kell
   - **Detailed numbers > flowing narrative**
3. Kattints **"Create a post"**
4. **Post type:** "Text" (NEM link — ide a body kell elsőként)
5. **Title:** (97 char, `[P]` prefix-szel)
   ```
   [P] B-8 RSI Tier-2 LLM-as-judge Critic — 100-bullet clean baseline, Cohen's κ=0.708 substantial
   ```
6. **Body:** copy-paste-eld az alábbi szöveget
7. **Flair:** "Project" — ha nincs flair-választó, a `[P]` prefix elég
8. Kattints **"Post"**

### A body (Reddit r/MachineLearning [P])

```
[P] project tag. Sharing a small adversarial-critic calibration
study from a personal project, with paired numbers.

**Setup.** I run a 4-layer safety-gate before any auto-propagation
to a long-term knowledge vault. Layer 4 is an LLM-as-judge "Critic"
that reviews each candidate Learning bullet on a 5-dim rubric
(factuality, novelty, durability, vault_fit, safety) and can
veto a bullet that the upstream G-Eval scorer would have passed.
The Critic is Claude Opus 4.7 reviewing Claude Opus 4.7's own
session output — same family as the G-Eval setup, so partially-
controlled self-enhancement bias.

**The calibration task.** Mine 100 bullets from 08-Sessions/*.md
"Learnings → memória" sections, classify each as pass-expected
or fail-expected based on content-heuristics (named-pattern
markers, tool/version refs, "Wider lesson" callouts, narrative-
markers like time-of-day). Score with the Critic. Compare verdicts.

**100-bullet results (default-mode threshold: mean≥0.7 ∧ min≥0.5
∧ safety≥0.9):**

|                  | strict | default | lenient |
| ---------------- | ------ | ------- | ------- |
| Agreement        | 47%    | **86%** | 73%     |
| Cohen's κ        | 0.096  | **0.708** | 0.272 |
| False-discard %  | 88.3%  | 11.7%   | 3.3%    |
| False-accept %   | 0.0%   | 17.5%   | 62.5%   |

**κ=0.708 ≈ "substantial agreement"** in the Landis-Koch
interpretation. The strict mode is unusably tight (rejects 88%
of expected-passes). The lenient mode lets through 62.5% of
expected-fails. The default mode is the sweet spot.

**Manual 10/10 false-accept inspection** of the default-mode
mismatches: all 10 were content-classifier over-trigger (e.g.,
HH:MM regex over-triggered on a Intl.DateTimeFormat
durable-pattern bullet; IP-fragment regex over-triggered on a
GenericAgent L0/L1/L2 architecture-parallel bullet). **Effective
false-accept rate ≈ 0%.** Revised κ ≈ 0.85+ after relabeling the
10 mislabeled bullets.

**Verdict.** Default-mode threshold ratified as production-flip
candidate. Apply-mode (VAULT_CRITIC_ACTIVE=1) stays gated to W23
(2 weeks of shadow-monitoring) before going live.

**Code, prompts, calibration corpus, and the 26-unique +
100-clean response.json snapshots** are MIT-licensed:
github.com/MyForgeLabs/myforge-vault-1111

**Limitations.**
(1) Sample size 100 with 60/40 stratification — interpretable
upper bound on κ-precision is ±0.05.
(2) Content-classifier ground-truth had 10% misclassification rate
on the false-accept side — moderate-bias measurement of true Critic
performance.
(3) Judge and judged are the same model family (Claude Opus 4.7);
self-enhancement bias only partially controlled by the 5-dim rubric
+ Anchor A-E calibration prompts.

The broader project this lives inside is a self-improving Obsidian
vault that three CLI agents share. Happy to discuss the κ
methodology, the per-dim threshold-design choices, the safety-hard-
gate calibration, or the mining-classifier verifier-pass refinement.
```

### r/MachineLearning comment-protokoll

- **Stat-pushback várható** — "n=100 too small for κ-precision claim", "self-enhancement bias not controlled". **MIND igaz**. Koncedáld előre a body Limitations-szekciójában.
- **Methodology-detail kérdésekre RÉSZLETESEN válaszolj** — ez a sub a "show your work" subje. Ha valaki kérdezi a Cohen's κ-számítást, idézd a formula-t.
- **NE védd a κ-számot** — a methodology-jét védd. "κ=0.708 may collapse on n=300 human-labeled — agreed; that's the W23 plan."
- Ha a posztot le-flair-elik vagy törlik mod-által → ne sopánkodj, fogadd el. r/MachineLearning szigorú, ez a normál.

---

## Univerzális anti-rules (mindhárom platformon)

> [!warning] 5 piros vonal

1. **NE kérj upvote-ot sehol** — sem chat-en, sem privát üzenetben, sem Discord-on. Shadow-ban kockázat.
2. **NE link-spam-elj a comment-szekcióban** — a `github.com/...` link **csak** akkor, ha közvetlenül kérik. Inkább fájl-nevet idézz ("see `vault-schema-migration-victim-audit` in the repo").
3. **NE használj emoji-t a title-ben** — automatikus Tier-C jelzés mindenhol kivéve r/ObsidianMD-en, ahol bocsánatos.
4. **NE válaszolj gépiesen / chat-bot-szerűen** — minden platform azonnal kiszúrja. Ha unalmas a komment, hagyd ki.
5. **NE ígérj autonomous-RSI-t / "self-improving AI"-t** — a B-8 Critic κ=0.708 *substantial agreement*, de **NEM autonomous-apply-mode** (az W23-ig gated). Ha valaki kérdezi, koncedáld: "shadow-monitoring még, nem éles auto-apply".

## Univerzális zöld vonal

> [!success] 3 jó-gyakorlat

1. **First-person mindenhol** — "én", "nekem", "az én projektem". Sose "we", sose "the team", mert egyedül vagy.
2. **Koncedáld a hibát ha jogos** — ha valaki rátalál egy gyengeségre, ne védekezz. "Fair, igazad van, ezt nem dokumentáltam jól" >> minden marketing-szöveg.
3. **Vissza-kérdezz** specifikus technikai kérdést — a posztod NEM lecture, hanem **community-engagement**. "Mit használsz X-re a saját setup-odon?" típusú kérdés engagement-szorzó.

## Quick-reference URL-ek + címek

| Platform | URL | Title | Body |
|---|---|---|---|
| **HN** | `myforgelabs.github.io/myforge-vault-1111/wiki/schema-migration-downstream-grep-checklist/` | `One schema-migration silently broke 15 CLI tools. Here's the safety-rail` | Lásd HN-magyar útmutató |
| **X thread** | (-) | (no title, 11-tweet thread) | Lásd ↑ 1. fejezet |
| **r/LocalLLaMA** | `github.com/MyForgeLabs/myforge-vault-1111` | `Self-improving knowledge graph for CLI agents — $0 marginal cost, 28-day run, MIT` | Lásd ↑ 2. fejezet (első own-comment) |
| **r/ObsidianMD** | `github.com/MyForgeLabs/myforge-vault-1111` | `Self-improving Obsidian vault — Karpathy LLM-Wiki + 283 auto-distilled wikis (MIT)` | Lásd ↑ 3. fejezet (első own-comment) |
| **r/MachineLearning** | (text-post, no URL) | `[P] B-8 RSI Tier-2 LLM-as-judge Critic — 100-bullet clean baseline, Cohen's κ=0.708 substantial` | Lásd ↑ 4. fejezet |

## Kapcsolódó

- [[2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]] — a forrás-audit (X/Reddit body-k onnan jönnek)
- [[2026-05-20 HN-launch — magyar útmutató felhasználónak]] — a HN-submit lépésről-lépésre
- [[../11-wiki/schema-migration-downstream-grep-checklist]] — a wiki amit HN-ra submit-olunk
