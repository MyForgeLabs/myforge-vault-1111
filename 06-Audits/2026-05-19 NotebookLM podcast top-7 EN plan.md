---
title: NotebookLM podcast top-7 EN — generation plan
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit"]
status: in-progress
tag_backfill: 2026-05-19
---
# NotebookLM podcast top-7 EN — generation plan

## Goal

Generate 5-minute conversational 2-host EN podcasts (deep-dive format) for the 7 HN-front-page-worthy EN wiki entries on Hacker News Launch Console.

## Top-7 EN wikis

| # | Wiki slug | EN audio status (2026-05-19) | Script status |
|---|---|---|---|
| 1 | `claude-code-subagent-fanout` | EXISTS (Gemini-TTS, 18-05) | — |
| 2 | `mgclient-autocommit-silent-rollback` | EXISTS (Gemini-TTS, 18-05) | — |
| 3 | `g-eval-bias-mitigation-pattern` | EXISTS (Gemini-TTS, 18-05) | — |
| 4 | `memgraph-ce-feature-limits` | EXISTS (Gemini-TTS, 18-05) | — |
| 5 | `memgraph-multi-labeling-edge-case-typedness-measurement` | NEW (NotebookLM, 19-05) | Script ready |
| 6 | `reranker-cost-optimization-not-size` | NEW (NotebookLM, 19-05) | Script ready |
| 7 | `layered-eval-cascading-pattern` | NEW (NotebookLM, 19-05) | Script ready |

## Approach

### Existing 4 audio overviews (entries 1-4)

These were generated 2026-05-18 via **Gemini 3.1 Flash TTS preview** (single voice, `Charon`, 96 kbps MP3 24 kHz mono). They are narrated TL;DRs (~1-2 min each), NOT NotebookLM deep-dive 2-host podcasts. **Quality is good but format differs** from what NotebookLM provides:

- Length: 1-2 min vs target 5 min
- Voices: 1 vs 2
- Format: narrated overview vs conversational deep-dive

**Decision:** keep the Gemini TTS files as-is for entries 1-4; the NotebookLM-pipeline applies to the 3 NEW entries (5-7) plus is available as a future upgrade path for entries 1-4 if a richer format is requested.

### NEW 3 podcasts (entries 5-7) — NotebookLM real-audio pipeline

Per-wiki workflow:

1. `notebooklm create "Wiki Audio: <slug> (2026-05-19)"` → new notebook
2. `notebooklm source add <wiki>.en.md -n <nb-id>` → wiki uploaded as text source
3. `notebooklm generate audio "<deep-dive prompt>" --format deep-dive --length default --language en -n <nb-id>` → task queued
4. `notebooklm artifact wait <task-id> -n <nb-id>` → blocks until completion
5. `notebooklm artifact download <artifact-id> -n <nb-id> --out <path>` → MP3 save
6. Save: `/root/obsidian-vault/.vault-nb/audio-overviews/<slug>.en-podcast.mp3`
7. Copy → `/root/projects/myforge-vault-1111/docs/audio/<slug>.en-podcast.mp3`
8. Update `Index.md` with new column "EN podcast (5 min)"

## Notebook IDs (2026-05-19)

| # | Wiki slug | Notebook ID | Audio task ID |
|---|---|---|---|
| 5 | `memgraph-multi-labeling-edge-case-typedness-measurement` | `19e89b17-0e98-457f-81cf-dfd93f31f338` | `a61ce5c6-8a99-4ec1-94ba-2a50a19fba16` |
| 6 | `reranker-cost-optimization-not-size` | `3c2f2729-344b-4a30-bc2f-cf9217ab748a` | `3091c39d-8cb1-4b49-8aa6-1b35bb19c6af` |
| 7 | `layered-eval-cascading-pattern` | `6f5ef7a4-7044-4e8b-af98-3507d48e0b88` | `f550adf4-91c5-4040-984f-2a6339e51971` |

## Podcast scripts (fallback if real-audio fails)

Pre-written 2-host EN dialogue scripts in `/root/obsidian-vault/.vault-nb/audio-overviews/scripts/`:

- `memgraph-multi-labeling-edge-case-typedness-measurement.en-podcast.md` — ~720 words, ~5 min
- `reranker-cost-optimization-not-size.en-podcast.md` — ~745 words, ~5 min
- `layered-eval-cascading-pattern.en-podcast.md` — ~750 words, ~5 min

Each script has:
- Two hosts: Alex (curious co-host) + Jordan (technical lead)
- Intro/outro music cues
- Conversational deep-dive structure
- Cross-references to related wiki entries

These can be:
- Fed to ElevenLabs/Gemini-TTS multi-voice if NotebookLM rate-limits
- Used as published transcripts alongside the audio
- Re-recorded by humans

## Audio pipeline summary

```
NotebookLM (entries 5-7):     TXT wiki → NB source → deep-dive 2-host MP3
                              ~5 min duration, AAC quality
                              $0 cost (Google account)

Gemini TTS (entries 1-4):     TL;DR (200 words) → single-voice MP3
                              ~1-2 min duration, 96 kbps MP3 24 kHz mono
                              ~$0.001-0.01 per minute (Flash preview)
```

## Verification checklist

- [x] NotebookLM CLI available (`/root/.notebooklm-venv/bin/notebooklm` v0.3.4)
- [x] Auth state valid (notebooks list works)
- [x] 3 new notebooks created
- [x] 3 wiki sources uploaded
- [x] 3 audio gen tasks queued
- [x] Audio download → vault `.vault-nb/audio-overviews/` (2026-05-19 07:22)
- [x] Audio copy → public `myforge-vault-1111/docs/audio/`
- [x] `Index.md` updated with podcast column
- [x] Per-wiki audio link added (`## 🎧 Audio overview` section in 3 EN wikis)

## Download completion (2026-05-19 07:22)

| Wiki | NB ID | Artifact Title | Size | Status |
|---|---|---|---:|---|
| memgraph-multi-labeling-edge-case | `19e89b17` | "The 88.4 Percent Data Illusion" | 44 MB | ✅ |
| reranker-cost-optimization-not-size | `3c2f2729` | "Why Smaller AI Models Worsen Search" | 39 MB | ✅ |
| layered-eval-cascading-pattern | `6f5ef7a4` | "Slash AI evaluation costs with layered cascades" | 38 MB | ✅ |

Total: **121 MB** across 3 deep-dive podcasts. All artifacts status `completed`, generation ~5-15 min after enqueue. Download time: ~30s per MP3 over notebooklm CLI.

## Related

- [[../11-wiki/notebooklm-cli-gotchas]] — known quirks of the CLI
- [[../11-wiki/gemini-3-1-flash-tts-pipeline]] — alternative TTS pipeline
- [[../.vault-nb/README]] — vault-NB integration overview
