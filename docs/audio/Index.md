---
title: Audio Overviews — Top-10 EN wiki podcast
description: Gemini 3.1 Flash TTS narrated overviews of the top-10 EN evergreen wiki entries. 1-2 minutes each, MP3 96 kbps.
created: 2026-05-18
updated: 2026-05-18
tags:
  - audio
  - podcast
  - tts
  - gemini
---

# Audio Overviews

Narrated audio overviews for the top-10 EN evergreen wiki entries. Generated via [Gemini 3.1 Flash TTS](../wiki/gemini-3-1-flash-tts-pipeline.md) (preview), HU voice: `Kore`, EN voice: `Charon`. Length: ~1-2 minutes per overview.

Subscribe via [RSS feed](../feed.xml) — new wiki entries and updates are syndicated automatically.

## Overviews

| Wiki | EN audio | HU audio |
|---|---|---|
| [Claude Code subagent fanout](../wiki/claude-code-subagent-fanout.en.md) | [EN MP3](claude-code-subagent-fanout.en.mp3) | [HU MP3](claude-code-subagent-fanout.hu.mp3) |
| [mgclient autocommit silent rollback](../wiki/mgclient-autocommit-silent-rollback.en.md) | [EN MP3](mgclient-autocommit-silent-rollback.en.mp3) | [HU MP3](mgclient-autocommit-silent-rollback.hu.mp3) |
| [G-Eval bias mitigation pattern](../wiki/g-eval-bias-mitigation-pattern.en.md) | [EN MP3](g-eval-bias-mitigation-pattern.en.mp3) | [HU MP3](g-eval-bias-mitigation-pattern.hu.mp3) |
| [Memgraph CE feature limits](../wiki/memgraph-ce-feature-limits.en.md) | [EN MP3](memgraph-ce-feature-limits.en.mp3) | [HU MP3](memgraph-ce-feature-limits.hu.mp3) |
| [Multi-layer safety gate](../wiki/multi-layer-safety-gate.en.md) | [EN MP3](multi-layer-safety-gate.en.mp3) | [HU MP3](multi-layer-safety-gate.hu.mp3) |
| [Karpathy LLM Wiki pattern](../wiki/Karpathy-LLM-Wiki-pattern.en.md) | [EN MP3](Karpathy-LLM-Wiki-pattern.en.mp3) | [HU MP3](Karpathy-LLM-Wiki-pattern.hu.mp3) |
| [Crystallization protocol](../wiki/Crystallization-protocol.en.md) | [EN MP3](Crystallization-protocol.en.mp3) | [HU MP3](Crystallization-protocol.hu.mp3) |
| [Auto context loading](../wiki/Auto-context-loading.en.md) | [EN MP3](Auto-context-loading.en.mp3) | [HU MP3](Auto-context-loading.hu.mp3) |
| [Subagent fanout context-aware classification](../wiki/subagent-fanout-context-aware-classification.en.md) | [EN MP3](subagent-fanout-context-aware-classification.en.mp3) | [HU MP3](subagent-fanout-context-aware-classification.hu.mp3) |
| [Verification step before claim](../wiki/verification-step-before-claim.en.md) | [EN MP3](verification-step-before-claim.en.mp3) | [HU MP3](verification-step-before-claim.hu.mp3) |

## Pipeline

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

## Related

- [Gemini TTS pipeline playbook](../wiki/gemini-3-1-flash-tts-pipeline.md)
- [RSS feed](../feed.xml) — subscribe to wiki updates
