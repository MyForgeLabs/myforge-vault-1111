---
name: Cross-platform launch sequencing
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#topic/marketing", "#topic/oss", "#topic/launch"]
---

# Cross-platform launch sequencing (one-audit → 6 channel-paste-ready copies)

> [!info] When to use
> When launching an OSS-project across multiple channels (HN, X, Reddit, TikTok, Dev.to, Mastodon, LinkedIn). Same content, **different wedge per channel**, sequenced for max-engagement.

## The 6-channel canonical sequence

| T+ | Channel | Format | Wedge-element |
|---|---|---|---|
| **T+0** Tue 15:00 UTC | **HN** | Title + URL + extended first-comment (~600 words) | Engineering failure-story-with-fix |
| T+30min | **X / Twitter** | 11-tweet thread, hook in tweet 1 | Technical narrative + cliffhanger in tweet 6 |
| T+90min | **X recap** | Single conversation-boost tweet referencing HN-position | Replies-bait ("which should I dive into next?") |
| T+6h | **X day-1 recap** | Metrics + thanks | Conversation-velocity boost |
| T+1day (Wed AM UTC) | **r/LocalLLaMA** or **r/<community>** | Title + ~400 word body | $0-cost framing + local stack-keywords |
| T+2day (Thu AM UTC) | **r/Obsidian** or secondary | Title + ~330 word body | Community-fit-specific framing |
| T+3day (Fri) | **Dev.to** | Longform Karpathy-essay, canonical_url back to docs-site | Failure-log + reflection |
| Parallel | **TikTok / Reels** | 8-15 sec vertical video | Problem-pattern-interrupt visual-narrative |
| T+7day | **Mastodon** (fosstodon) | 3-toot thread | FOSS-community-fit reflection |

The cadence is **deliberate**, not arbitrary:
- HN at T+0 owns the canonical-thread (links from other channels go here)
- X T+30 lets HN-velocity rank organically before social amplifies
- Reddit T+1/T+2 avoids same-day cross-spam-detection from Reddit-mods
- Dev.to T+3 captures the "I saw this on HN, want longer version" audience
- TikTok parallel lets a different audience-segment discover

## Per-channel wedge-element principles

### HN (engineering-credibility audience)

**What works**: concrete failure-stories, specific numbers, named-the-broken-parts honesty.
**What doesn't**: marketing speak, AGI-language, vague generalities, "we are excited to announce".

**Body structure (340 words on the URL)**:
```
[Hook — 1 paragraph, concrete failure-incident with timeline]
[Diagnosis — 1 paragraph, what was actually wrong]
[Fix — 1 paragraph, the canonical solution + reproducibility]
[Wider lesson — 1 sentence: how it generalizes]
[Code-link + license + 1-line project-context]
```

**Extended first-comment (~600 words)**:
```
[Author here, happy to AMA.]
[The rest of the project this safety-rail lives inside — stack overview]
[Stack: storage, fact-layer, graph-layer, loop, cost-trick]
[Honest scope: what's NOT in here]
[Repo + Site + Release-notes links]
[Most curious for feedback on: 3 specific items]
```

### X / Twitter (developer-narrative audience)

**What works**: 11-tweet thread, hook in tweet 1 (≤270 chars, ≤2 emoji total), cliffhanger in tweet 5-6 ("the bug that almost killed it…"), repo-link only in last tweet.
**What doesn't**: link in tweet 1-10 (algorithm penalizes early-link), 280+ char tweets, more than 2 emoji per tweet, hashtag-spam.

**The 11-tweet template**:
1. Hook + thread-promise + 🧵
2. The pattern/architecture in 4 lines
3. The auto-loop (with 1 specific metric)
4. Today's milestone (the fresh thing)
5. Cost trick
6. **Failure-story** (the strongest tweet — usually does 3× engagement)
7. **Today's surprising find** (sticky)
8. "Save this thread — I'll write up each as standalone wikis"
9. Why N agents instead of 1
10. What's NOT in here
11. Repo: link + Site: link + closing CTA

### Reddit (community-specific audiences)

**Per-sub strategy**:

- **r/LocalLLaMA**: lead with `$0 marginal cost` + local-Memgraph + bge-m3. Mention Claude only in comment 5+ (sub downvotes Anthropic-first-mentions).
- **r/ObsidianMD**: lead with Johnny-Decimal-prefix + Karpathy LLM-Wiki + auto-distillation. Explicit "no SaaS, no signup, MIT".
- **r/MachineLearning** `[P]` tag: only post with numbers. Lead with calibration-table + methodology. NO project-promotion.
- **r/programming**: skip unless you have a genuinely novel CS finding. The sub is harsh on "look at my OSS" posts.

**Caveat**: don't use third-party schedulers (Buffer/Later/Hootsuite) for first 10-20 posts — the "reduced reach penalty" applies to scheduled posts.

### TikTok / Reels (cold-audience-discover)

**The 30-second blueprint** (see [[higgins-vertical-video-prompt-iteration]] for video-gen details):

```
0-2 sec  | Problem-pattern interrupt (dramatic visual + hook-error-text)
2-10 sec | Technical problem statement (captioned narrator-voice)
10-25 sec| Solution demo (screen-recording + motion-graphics)
25-30 sec| Single-action CTA ("link in bio")
```

**What works**: 9:16 vertical, NO human faces, captioned (TikTok auto-subtitle), trending-tech-instrumental sound (NOT commercial-music — use Pro-mode personal-account).
**What doesn't**: Business-account (FYP penalty), personal-introduction opening, longer than 60 sec, hard-signup-CTAs.

### Dev.to (longform-audience)

**Strategy**: cross-post the Karpathy-essay verbatim with `canonical_url:` pointing back to your docs-site (so search engines credit the docs-site for SEO).

**Tags**: `#ai #opensource #obsidian #claude` (4 max, niche-specific).

**Body structure**:
1. Opening hook (the failure-story, dramatized for narrative-flow)
2. Background section (what the project is)
3. The 3-5 highest-leverage learning moments
4. Code-link + thanks

**Cross-link**: in the HN-thread first-comment, link to the Dev.to essay as "I wrote a longer essay-style version here for anyone who wants the failure-log walkthrough." Typical conversion: 8-15% of HN-readers click through.

## The "one-audit → 6 channel-paste-ready" pattern

The single source artifact is an audit-MD with these sections:

```
# HN-launch refresh — v<version>
## Number-delta (last → current)
## Angle final-pick: <C|A|B|D>
## C-2 final-pick — HN submission
  ### Title (≤80 chars)
  ### URL
  ### Body (~340 words)
  ### Extended first-comment (~600 words)
  ### Comment plan for first 90 min
  ### Do-not-do list
## A — backup angle (Show HN)
## B — backup-secondary angle (Karpathy essay)
## 11-tweet X/Twitter thread
## Reddit body refresh — r/LocalLLaMA
## Reddit body refresh — r/ObsidianMD
## Reddit body refresh — r/MachineLearning  ← optional
## What still needs to happen before Tuesday
  | task | owner | date |
```

All 6 paste-blocks live in ONE FILE. On launch-day, you open this one audit-MD and copy-paste sequentially. No tab-switching between drafts.

See [[../06-Audits/2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]] for the canonical example.

## Retry-decision tree

```
HN Tier C (<40 pts, buried <90 min)
├── Wait 14 days
├── Try a different angle on a DIFFERENT URL
└── 2 angles bomb → stop HN attempts for 30+ days

Reddit Tier C (<50 upvotes, <5 comments)
├── Check if mod-removed; ask reason via DM
├── Reframe lead (different-keyword-first)
└── Try a different sub

X thread <10k impressions at 24h
├── Quote-tweet the strongest single-tweet standalone (usually tweet 6 — failure-story)
├── Reply to 3 relevant accounts with thoughtful 1-liner referencing their work
└── Re-thread the failure-mode story standalone in 7 days

TikTok <500 views at 24h
├── Reposting same video DOESN'T work; algorithm penalizes
├── Generate a v2 with different hook (a different concrete metric or count)
└── Manual-post (NOT scheduler) for first 10-20 videos to build trust
```

## Empirikus eredmény

- **2026-05-20 MyForge Vault 11.11 launch** (preparing for Tuesday 2026-05-26 15:00 UTC):
  - One audit-MD: `06-Audits/2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick.md`
  - 6 channel-paste-ready blocks
  - Angle C-2 (15-silent-victim safety-rail) chosen via [[hn-launch-angle-selection-rubric]]
  - TikTok video pre-generated via [[higgins-vertical-video-prompt-iteration]] flow
  - Karpathy-essay HU + EN epilogue (1635+1751 words) for Dev.to / Mastodon Friday-follow-up
  - NotebookLM Deep Dive podcast (20 min, 56 MB) published to docs-site as bonus-asset

## Kapcsolódó

- [[hn-launch-angle-selection-rubric]] — wedge selection
- [[higgins-vertical-video-prompt-iteration]] — TikTok-video pattern
- [[stale-numbers-in-static-artifacts-pattern.en]] — pre-launch number-refresh
- [[../06-Audits/2026-05-19 GitHub launch playbook]] — original strategic playbook
- [[../06-Audits/2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]] — concrete application
- [[github-release-self-notify-suppress]] — release-notification gotcha
