---
name: gemini-3-1-flash-tts-pipeline
type: wiki
tags: ["#topic/gemini", "#topic/tts", "#topic/api"]
created: 2026-05-15
updated: 2026-05-15
---

# Gemini 3.1 Flash TTS Preview — HU pipeline playbook

A 2026-05-15-i bejelentett Google modell. Preview API-n keresztül elérhető magyar (és 70+ más nyelv) szöveg-felolvasásra. Hangminőség Artificial Analysis TTS leaderboard #1 (1211 Elo).

## Quick reference

| Tulajdonság | Érték |
|---|---|
| Model ID | `gemini-3.1-flash-tts-preview` |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}` |
| Output formátum | base64-encoded raw PCM L16 24kHz mono |
| MIME | `audio/l16;rate=24000;channels=1` |
| Audio-tagek | `[warm, friendly, moderate pace]` inline szövegben működik |
| Voice-options | Kore, Puck, Charon, Aoede, Leda, Zephyr, Fenrir, Orus, és +20 |
| Magyar minőség | OK Kore-rel tesztelve, természetes akcentus |
| Auth | API-key (Gemini API) vagy Vertex OAuth |
| Watermark | SynthID minden output-ban |

## Minimal Python hívás

```python
import os, base64, json, urllib.request, subprocess
from pathlib import Path

KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3.1-flash-tts-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

text = "[warm, friendly] Szia Peti! Ez egy magyar hangteszt."

body = {
    "contents": [{"parts": [{"text": text}]}],
    "generationConfig": {
        "responseModalities": ["AUDIO"],
        "speechConfig": {
            "voiceConfig": {
                "prebuiltVoiceConfig": {"voiceName": "Kore"}
            }
        }
    }
}

req = urllib.request.Request(URL, method="POST",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"})

with urllib.request.urlopen(req, timeout=60) as resp:
    d = json.loads(resp.read())
    audio_b64 = d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    raw = base64.b64decode(audio_b64)
    Path("out.pcm").write_bytes(raw)

# PCM → MP3
subprocess.run([
    "ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
    "-i", "out.pcm", "-codec:a", "libmp3lame", "-b:a", "128k",
    "out.mp3"
])
```

## FFmpeg conversion

```bash
ffmpeg -y -f s16le -ar 24000 -ac 1 -i in.pcm \
  -codec:a libmp3lame -b:a 128k out.mp3
```

- `-f s16le`: signed 16-bit little-endian (L16)
- `-ar 24000`: sample rate 24kHz
- `-ac 1`: mono
- `-b:a 128k`: MP3 bitrate (96k elég is, 192k nagyon jó minőség)

## Audio-tagek (expression control)

Inline a szövegben, szögletes zárójelben:

| Tag | Hatás |
|---|---|
| `[warm, friendly]` | meleg, barátságos |
| `[calm, reflective]` | nyugodt, befelé forduló |
| `[energetic, upbeat]` | pörgős |
| `[serious, professional]` | hivataloskodó |
| `[whisper]` | suttogás |
| `[fast]` / `[slow]` | tempó |
| `[sad]` / `[happy]` / `[excited]` | érzelmi |
| Multi-tag | `[warm, slow, reflective]` |

Plus „Scene Direction" — narratíva-hint a modellnek mid-text: `She paused, then continued softly.`

## Multi-speaker (Director's Notes)

Több karakterhez `multiSpeakerVoiceConfig`:
```python
"speechConfig": {
    "multiSpeakerVoiceConfig": {
        "speakerVoiceConfigs": [
            {"speaker": "Speaker1", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}},
            {"speaker": "Speaker2", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Charon"}}}
        ]
    }
}
```
A szövegben: `Speaker1: Szia Peti! Speaker2: Szia, hogy vagy?`

## Költség becslés (preview, pricing changeable)

- ~1MB MP3 per 1 perc (128kbps)
- Per-character vagy per-second pricing várható — preview-ban még nincs publikus
- Becsült $0.001-0.01 / perc HU TTS (Flash-tier ár-szint)

## Gotcha — gemini-2.5-flash thinking-mode

A LLM-step (text-generation) `gemini-2.5-flash` modellnél **thinking-mode eszi a tokent**, rövid task-okat mid-sentence vág le. Fix:
```python
"generationConfig": {
    "maxOutputTokens": 4000,
    "thinkingConfig": {"thinkingBudget": 0}
}
```
Részletek: [[11-wiki/gemini-2-5-flash-thinking-budget]]

## Gotcha — safety-filter `PROHIBITED_CONTENT` blokk rövid text + agresszív audio-tag (2026-05-16)

**Tünet:** rövid (~5-20 char) text + erős audio-tag kombináció (`[neutral, formal, slow, monotone, distant] INTERPRETING.`) → a response NEM `candidates`-szel, hanem:

```json
{
  "promptFeedback": {"blockReason": "PROHIBITED_CONTENT"},
  "usageMetadata": {...},
  "modelVersion": "gemini-3.1-flash-tts-preview"
}
```

A safety filter összesen 15 token-en triggerelt, valószínű a tag-szavak (`monotone`, `distant`) + a kapitalizált `INTERPRETING.` (sci-fi parancs-szótár) kombináció. Hosszabb HU szövegnél (50+ token) ugyanaz a tag-set átmegy.

**Server-side fallback pattern:**
```python
def _call_tts(text, voice):
    # ... HTTP POST ...
    return json.loads(resp.read())

def gemini_tts(text, voice, persona=None):
    tag = TTS_TAGS.get(persona, "")
    primary = f"{tag} {text}" if tag else text
    d = _call_tts(primary, voice)
    cand = d.get("candidates")
    if not cand or "content" not in cand[0]:
        # PROHIBITED_CONTENT or other block — retry without audio-tag
        block_reason = d.get("promptFeedback", {}).get("blockReason", "UNKNOWN")
        print(f"TTS blocked ({block_reason}), retrying tag-less", flush=True)
        d = _call_tts(text, voice)
        cand = d.get("candidates")
        if not cand:
            raise RuntimeError(f"Gemini TTS blocked: {block_reason}")
    return base64.b64decode(cand[0]["content"]["parts"][0]["inlineData"]["data"])
```

**Tanulság:** a `KeyError 'candidates'` Python tracebackre szembetűnő, de a valódi hiba a `promptFeedback.blockReason`-ben van. A server-fallback transzparens (a TTS megszólal, csak persona-tag nélkül).

**Reusable szabály:** rövid + agresszív tag-kombináció esetén default-retry tag-strip-pel. Hosszú HU text (50+ token) általában mehet tag-gel.

## API-key location

Mai pilot a Chatwoot env-jét használta: 
```bash
grep -oP "^GEMINI_API_KEY=\K.+" /opt/chatwoot/.env
```
Részletek: [[05-Memory/Infrastructure#Gemini API key]]

## Hol jelent meg

2026-05-15 MVP: `/opt/vault-brief/vault-brief.py` napi briefing pipeline. Első output `vault/10-raw/audio/daily-brief-2026-05-15.mp3` 95 sec, 1.5MB. Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Folytatás

A teljes hangalapú projekt-pipeline [[02-Projects/mfl-voice]] néven külön projekt. Roadmap: voice AB-teszt, RSS-feed, Balance-meditation, KGC TV audio-overlay, Live API real-time HU voice agent.

## Kapcsolódó

- [[02-Projects/mfl-voice]]
- [[11-wiki/gemini-2-5-flash-thinking-budget]]
- [[11-wiki/notebooklm-cli-gotchas]]
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[elementor-repeater-media-condition-gotcha]] (sem-rokon, score=0.53)
