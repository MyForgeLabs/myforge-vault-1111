---
name: Higgsfield reel-flow KGC
type: wiki
tags: ["#type/wiki", "marketing", "video-generation", "social-media", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Higgsfield reel-flow (B2B equipment-rental marketing pattern)

## TL;DR

End-to-end AI video-generation pipeline B2B equipment-rental social-media-hoz (KGC use-case, de generic). **Source-assets** (gép-portré WebP + voiceover script) → **Higgsfield Grillo** (image-to-video, 5-8s reel) → **APEX auto-publish** (IG + TikTok + YouTube Shorts) → **virality-predictor MCP** (post-hoc analytics + pre-publish hint). Egy reel kb. ~168/2997 credit, audio teljesen szintetikus (Gemini 3.1 Flash TTS HU).

## Háttér

A KGC marketing-sprint 2026-05-14 ([[../08-Sessions/2026-05-14-kgc-marketing]]) megvizsgálta a B2B equipment-rental social-stack-eket. A klasszikus "fotó + szöveg-overlay" formátum reach-je 2025 H2 óta zuhan — Instagram/TikTok algoritmus a video-formátumot 4-6× erősebben preferálja. Saját video-stúdió KKV-szinten elérhetetlen (videós, megrendelés, kamera, helyszín), így a generative-AI pipeline a realista alternatíva.

A 2026-05-18 KGC-all session ([[../08-Sessions/2026-05-18-kgc-all]]) konkretizálta a stack-et: **Higgsfield Grillo** (image-to-video specialista, jobban kezeli a "gép-portré 360° pan" use-case-t mint a Veo/Runway), **APEX** (Higgsfield publish-modulja, ~30 platform), **virality-predictor MCP** (Higgsfield saját ML-modellje engagement-forecast-hez).

## Mintázat

### Stage 1: Source-asset preparation

- **Gép-portré** — sharp WebP ~1200px wide, lookbook-quality. Forrás: nano-banana ([[nano-banana-cli-gotchas]]) vagy stúdió-photo. Háttér: studio-grey vagy in-situ (építkezés).
- **Voiceover-script** — 60-80 szó (8s reel), HU, természetes-mondaszerkezet, action-CTA végén ("Bérelhető nálunk").
- **Voice synthesis** — Gemini 3.1 Flash TTS Kore voice ([[gemini-3-1-flash-tts-pipeline]]), PCM L16 24kHz → ffmpeg → MP3

### Stage 2: Video-generation

- **Higgsfield Grillo** — `mcp__claude_ai_higgins__generate_video` (image-to-video mode)
- Aspect-ratio: 9:16 (reel/Shorts) vagy 1:1 (feed)
- Length: 5-8s (algoritmus-sweet-spot 2026 Q2)
- Camera-motion: `slow-pan-right` (legtermészetesebb gép-portrén); pinning-marker: 0% (NO drift)
- Cost: ~168 credit/reel a Grillo-n (Pro 2× = ~336 credit)

### Stage 3: Audio-merge + caption

- ffmpeg merge: video + voiceover MP3 → final MP4
- Burned-in caption: HU + EN (opcionális, accessibility)
- Logo-watermark: bottom-right, alpha 70%, brand-color

### Stage 4: Multi-platform publish

- **APEX** (`mcp__claude_ai_higgins__select_workspace` + publish-flow)
- Platformok: Instagram (Reel + Story), TikTok, YouTube Shorts, optional LinkedIn
- Platform-specific caption (Instagram emoji-rich, LinkedIn formal, TikTok hashtag-heavy)

### Stage 5: Analytics + iteration

- **Pre-publish:** `mcp__claude_ai_higgins__virality_predictor` — engagement/attention/retention forecast; ha P50 < threshold → re-generate
- **Post-publish:** 24h, 7d engagement-snapshot → cluster a high-performer pattern-eket → feedback a Stage 1 script-prompt-ba

## Anti-pattern

- **Generic stock-music + minimum cuts** — feed-noise, nem reel; algoritmus lebüntet
- **Multi-machine egy reel-ben** — figyelem-fragmentation; 1 reel = 1 gép, ez a "hero pattern"
- **CTA végén URL-link** — Instagram nem clickable a video-bodyban; "link in bio" CTA, NEM URL
- **Pre-publish A/B-test 5+ variánssal** — TikTok/IG algoritmus penalty-zi a duplikált-content-et; max 2 variant
- **Voice-clone valódi személyről** — jogilag rizikós (GDPR + képmás); szintetikus voice (Gemini Kore) preferált

## Reusable szabályok

1. **1 reel = 1 hero-machine** — semmi multi-product
2. **Voice HU magyar piacra, NE auto-translate ENG-ből** — accent/mondat-szerkezet artifact-ok kifuttatják az engagement-et
3. **Camera-motion = slow-pan, NEM fast-zoom** — fast-zoom motion-sickness, retention-killer
4. **Burned-in caption mindig** — 80%-os mobile-mute-watching arány
5. **Pre-publish virality-forecast** — ne publikálj P50 < 0.4 alatt; iterate
6. **30-day cadence min. 8 reel** — algoritmus-friendly volume, nem spam; B2B vertical-ben elég
7. **Cost-budget per kampány** — ~3000 credit / hónap kalkulált (~18 reel/hó Grillo standard)

## Buktatók

- APEX néha 2-3 órát késik publish-kor (platform-side rate-limit) — schedule manually peak-hours-on
- Instagram Reel-jel az auto-crop néha rosszul vág 9:16 → 1:1; preview ELŐTT publish
- TTS Kore voice HU "ő" hang néha "ó"-ként ejtődik — post-edit subtitle-ben javítsd
- Higgsfield model-update (Grillo v2 → v3) közben pinning-marker default változhat — manuálisan 0%-ra állítsd
- A virality-predictor forecast NEM determinisztikus — 3× futtatva átlagolj

## Kapcsolódó

- [[kgc-social-trend-stack-2026]] — szélesebb stack-kontextus
- [[nano-banana-cli-gotchas]] — image-gen layer
- [[gemini-3-1-flash-tts-pipeline]] — voice-layer
- [[notebooklm-seo-competitor-research-pattern]] — content-strategy sibling
- [[../08-Sessions/2026-05-14-kgc-marketing|2026-05-14 kgc-marketing session]]
- [[../08-Sessions/2026-05-18-kgc-all]] — kontextus
