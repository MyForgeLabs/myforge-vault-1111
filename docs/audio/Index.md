---
title: Audio Overviews — Top-EN wiki podcast
description: Gemini 3.1 Flash TTS narrated overviews + NotebookLM deep-dive 2-host podcasts for top EN evergreen wiki entries.
created: 2026-05-18
updated: 2026-05-20
tags:
  - audio
  - podcast
  - tts
  - gemini
  - notebooklm
---

# Audio Overviews

Two formats:

1. **TTS overviews** (Gemini 3.1 Flash, single voice `Charon` EN / `Kore` HU, ~1-2 min, MP3 96 kbps)
2. **Deep-dive podcasts** (NotebookLM 2-host conversational, ~5-20 min, MP3) — for HN-front-page-worthy entries

Subscribe via [RSS feed](../feed.xml) — new wiki entries and updates are syndicated automatically.

## 🎙️ Featured — v1.0.10 milestones (2026-05-20)

| Title | Format | Length | Audio |
|---|---|---:|---|
| **One dropped column broke fifteen AI tools** — v1.0.10 milestones (silent-victim cleanup, B-8 RSI Critic κ=0.708 production-flip, subagent-fanout scale, Sprint-2 gated work) | Deep Dive (NotebookLM 2-host) | ~20 min | [EN podcast](v1.0.10-milestones.en.mp3) |

Source audits (NotebookLM input):

- [Phase-3 re-extract execution + downstream P0 patch](../audits/2026-05-20 Phase-3 re-extract execution + downstream P0 patch.md)
- [Wave-A schema-migration-victim sweep (13 silent victims patched)](../audits/2026-05-20 Wave-A schema-migration-victim sweep (13 silent victims patched).md)
- [B-8 Critic 100-bullet clean re-sample (κ=0.708)](../audits/2026-05-20 B-8 Critic 100-bullet clean re-sample (kappa 0.708).md)
- [B-8 Critic 50-bullet (26 unique) scale-up](../audits/2026-05-20 B-8 Critic 50-bullet (26 unique) scale-up.md)
- [HN-launch refresh — v1.0.10 number-update + final-pick](../audits/2026-05-20 HN-launch refresh — v1.0.10 number-update + final-pick.md)
- [Schema-migration downstream-grep checklist](../wiki/schema-migration-downstream-grep-checklist.en.md)

## Top-7 HN-worthy entries (with NotebookLM deep-dive podcasts)

| Wiki | EN TTS overview | HU TTS overview | EN podcast (5 min, 2-host) |
|---|---|---|---|
| [Claude Code subagent fanout](../wiki/claude-code-subagent-fanout.en.md) | [EN MP3](claude-code-subagent-fanout.en.mp3) | [HU MP3](claude-code-subagent-fanout.hu.mp3) | (pending) |
| [mgclient autocommit silent rollback](../wiki/mgclient-autocommit-silent-rollback.en.md) | [EN MP3](mgclient-autocommit-silent-rollback.en.mp3) | [HU MP3](mgclient-autocommit-silent-rollback.hu.mp3) | (pending) |
| [G-Eval bias mitigation pattern](../wiki/g-eval-bias-mitigation-pattern.en.md) | [EN MP3](g-eval-bias-mitigation-pattern.en.mp3) | [HU MP3](g-eval-bias-mitigation-pattern.hu.mp3) | (pending) |
| [Memgraph CE feature limits](../wiki/memgraph-ce-feature-limits.en.md) | [EN MP3](memgraph-ce-feature-limits.en.mp3) | [HU MP3](memgraph-ce-feature-limits.hu.mp3) | (pending) |
| [Memgraph multi-labeling typedness](../wiki/memgraph-multi-labeling-edge-case-typedness-measurement.en.md) | — | — | [EN podcast](memgraph-multi-labeling-edge-case-typedness-measurement.en-podcast.mp3) |
| [Reranker cost optimization — not size](../wiki/reranker-cost-optimization-not-size.en.md) | — | — | [EN podcast](reranker-cost-optimization-not-size.en-podcast.mp3) |
| [Layered eval-cascading pattern](../wiki/layered-eval-cascading-pattern.en.md) | — | — | [EN podcast](layered-eval-cascading-pattern.en-podcast.mp3) |

## Other TTS overviews

| Wiki | EN audio | HU audio |
|---|---|---|
| [Multi-layer safety gate](../wiki/multi-layer-safety-gate.en.md) | [EN MP3](multi-layer-safety-gate.en.mp3) | [HU MP3](multi-layer-safety-gate.hu.mp3) |
| [Karpathy LLM Wiki pattern](../wiki/Karpathy-LLM-Wiki-pattern.en.md) | [EN MP3](Karpathy-LLM-Wiki-pattern.en.mp3) | [HU MP3](Karpathy-LLM-Wiki-pattern.hu.mp3) |
| [Crystallization protocol](../wiki/Crystallization-protocol.en.md) | [EN MP3](Crystallization-protocol.en.mp3) | [HU MP3](Crystallization-protocol.hu.mp3) |
| [Auto context loading](../wiki/Auto-context-loading.en.md) | [EN MP3](Auto-context-loading.en.mp3) | [HU MP3](Auto-context-loading.hu.mp3) |
| [Subagent fanout context-aware classification](../wiki/subagent-fanout-context-aware-classification.en.md) | [EN MP3](subagent-fanout-context-aware-classification.en.mp3) | [HU MP3](subagent-fanout-context-aware-classification.hu.mp3) |
| [Verification step before claim](../wiki/verification-step-before-claim.en.md) | [EN MP3](verification-step-before-claim.en.mp3) | [HU MP3](verification-step-before-claim.hu.mp3) |

## Pipelines

### TTS overview (1-2 min, single voice)

```
TL;DR (150-200 words) → Gemini 3.1 Flash TTS preview
                      ↓
        base64 PCM L16 24 kHz mono
                      ↓
        ffmpeg → MP3 96 kbps
```

- Voice models: `Charon` (EN, neutral male), `Kore` (HU, natural female accent)
- Audio tag: `[warm, friendly, conversational, moderate pace]`
- Cost: ~$0.001–0.01 per minute (Flash-tier preview pricing)

### Deep-dive podcast (5 min, 2-host)

```
Wiki .en.md  →  NotebookLM source (text)
              ↓
   notebooklm generate audio --format deep-dive --length default
              ↓
   2-host conversational MP3 (NotebookLM voices)
```

- Format: `deep-dive` (alternatives: `brief`, `critique`, `debate`)
- Length: `default` (~5 min); `short` ~2 min, `long` ~10 min
- Cost: $0 (Google account)
- Pre-written 2-host scripts (Alex + Jordan) in `.vault-nb/audio-overviews/scripts/`

## Related

- [Gemini TTS pipeline playbook](../wiki/gemini-3-1-flash-tts-pipeline.md)
- [NotebookLM CLI gotchas](../wiki/notebooklm-cli-gotchas.md)
- [RSS feed](../feed.xml) — subscribe to wiki updates
