---
name: HN-launch angle-selection rubric
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#topic/marketing", "#topic/oss", "#topic/launch"]
---

# HN-launch angle-selection rubric

> [!info] When to use
> Before submitting an open-source project to Hacker News. Selecting the wrong angle for the wrong moment usually buries the post in <90 minutes (Tier C: <40 points). This rubric picks the right wedge-claim for the right moment.

## The 4 baseline angles

| Angle | Format | When it wins |
|---|---|---|
| **A — Show HN repo-link** | `Show HN: <project-name> — <one-line description>` linking to the repo root | **v1.0.0 fresh launch**. Project is new to the world. |
| **B — Karpathy-essay (longform)** | `What I learned building <X> in <N> hours/days` linking to a docs-site essay | When you have a meaty technical-narrative ready (~3000+ word essay, multiple failure-stories). Optimizes dwell-time and star-conversion. |
| **C — Failure-story-with-fix** | `<Concrete bug-incident> — and the safety-rail I shipped` linking to the wiki playbook | **When you just shipped a fix to a real production incident**. Engineering-credibility through naming-the-broken-parts. |
| **D — Counter-intuitive technical finding** | `<X is wrong about Y> — <N>-sample study` linking to the methodology page | When you have measurement data that contradicts conventional wisdom (e.g. "BEIR/MTEB K=20 wrong for small corpora"). |

## The DECISION TREE (when to pick which)

```
Are you launching v1.0.0 (first time in public)?
├── YES → Angle A (Show HN). Use the wedge sparingly; the launch itself is the news.
└── NO (you're at v1.x.y, project already public)
    │
    Did you ship a notable failure-story+fix THIS WEEK?
    ├── YES → Angle C (failure-story). The freshness is the wedge.
    │   │
    │   ⚠️ Stale-failure trap: if the bug-story is more than ~14 days old,
    │   it loses HN-novelty. Pick a different angle.
    │
    └── NO → Do you have measurement data contradicting conventional wisdom?
        ├── YES → Angle D (counter-intuitive finding)
        └── NO → Skip HN this week. Stale-progression posts (
                  "I open-sourced X 2 weeks ago and here's an update")
                  almost always Tier C.
```

## Anti-pattern: "I open-sourced X 2 weeks ago and here's an update"

This format **almost always Tier C** on HN unless you have a fresh failure-story or counter-intuitive finding from the past week. HN values **novelty** above retrospective sample-updates.

If you reach this state and don't have fresh angle-material, **don't post**. Wait 7-14 days, do new engineering, then re-evaluate.

## Anti-pattern: AGI-language

Stack of `self-improving` + `RSI` + `agentic OS` + `Constitutional AI` reads as inflated. **Every claim must have a number, a benchmark, or a commit-hash**. Stay past-tense ("I built", "I measured"), avoid future-tense ("this will enable…"). Use `self-improving` sparingly — once in README, once in essay, **never in the title**.

## Anti-pattern: AGI hype + Show-HN-generic combination

`Show HN: My self-improving AGI-like Obsidian vault` → instant flag. The two reflexes combine multiplicatively.

## Sticky-hook pattern (for Angles B-D)

The wedge-claim should be **one sentence** that makes the click-through inevitable:

| Project-context | Working wedge |
|---|---|
| Schema-migration cleanup | "A 5-second column-drop silently broke 15 of my CLI tools. Here's the safety-rail I shipped." |
| Search-speedup | "One Cypher line replaced 280ms numpy-cosine with 1ms native vector-search." |
| LLM-as-judge bias | "Bias-mitigation prompt knocked self-enhancement confidence 0.880 → 0.760 on a 30-pair calibration." |
| Tool-pattern discovery | "Subagent-fanout: 8 parallel Claude Code agents from inside one session. $0 marginal cost." |

The pattern is: **one concrete metric or count + one concrete artifact + one specific failure-spec**.

## Extended first-comment pattern

HN convention: the OP's first comment on their own thread gets pinned top. **This is where context goes**.

For Angle C (failure-story), the 340-word body in the URL+wiki-link covers the narrative. Then a **600-word first-comment** delivers the broader project-context:

- The 340-word URL/body: hooks the click, tells the failure-story
- The 600-word first-comment: lists the wider stack, the milestones, the cost-disclosure, the honest "what's NOT in here"

This combination preserves the sticky-hook click-through AND prevents the "wait, what is this project actually?" follow-up frustration in the comments.

## Comment-protocol for first 90 minutes

The HN algorithm rewards conversation velocity in the first 90 minutes, but penalizes apparent astroturf:

- **NO replies in first 15 minutes** — looks like astroturf
- **15-90 min: 1 reply every 5-8 minutes** — steady, conversational pace
- **First-person, concede limitations, cite line numbers**
- **No marketing speak in replies** — "happy to dig in" beats "we are excited to share"
- **Pre-write 10 anticipated replies** for the top 10 question-shapes before posting

## Cohort-of-channels integration

HN is the wedge-channel. The same content should land on **5 channels with 5 channel-specific wedges**:

| Channel | Wedge | When (relative to HN) |
|---|---|---|
| HN | Failure-story (Angle C) | T+0 |
| X/Twitter | 11-tweet thread, hook in tweet 1, dramatic-cliffhanger in tweet 6 | T+30 min |
| r/LocalLLaMA / r/MachineLearning | Numbers-forward technical, $0-cost framing | Wed+Thu (NOT same-day as HN — different audience) |
| r/Obsidian / r/<community> | Community-fit-specific framing | Wed+Thu |
| Dev.to / Hashnode | Longform Karpathy-essay (Angle B), canonical_url back to docs-site | Friday |
| TikTok / Reels | Problem-pattern-interrupt visual-narrative (30-sec blueprint) | Parallel/staggered |

See [[cross-platform-launch-sequencing]] for the per-channel paste-ready content workflow.

## Retry-decision

If HN goes Tier C (buried <90 min, <40 points):

```
Wait 14 days (HN dupe window).
│
├── Try a different angle on a different URL
│   (NOT the repo if you tried repo, NOT the essay if you tried essay)
│
└── If 2 angles bomb → stop HN attempts for 30+ days.
    Focus channel-mix on Reddit + LinkedIn + newsletters.
```

NEVER:
- Re-submit the same URL within 30 days
- Ask for upvotes (instant flag pile-on)
- Reply to your own thread anonymously (account ban)

## Empirikus eredmény

- **2026-05-26 launch** of `MyForge Vault 11.11`: chose **Angle C-2** (silent-victim downstream-grep playbook) — fresh-today story, sticky-hook + 600-word extended first-comment with Tolaria-portability mention. See [[../06-Audits/2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]] for the full paste-ready package.

## Kapcsolódó

- [[cross-platform-launch-sequencing]] — per-channel wedge-element matrix
- [[../06-Audits/2026-05-19 GitHub launch playbook]] — original strategic frame
- [[../06-Audits/2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick]] — concrete application
- [[stale-numbers-in-static-artifacts-pattern.en]] — pre-launch readiness
