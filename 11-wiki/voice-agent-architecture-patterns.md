---
name: Voice-agent architektúra mintázatok — STT + LLM + TTS stack 2026 H1
type: reference
tags: ["#topic/voice-agent", "#topic/stt", "#topic/tts", "#topic/llm", "#topic/realtime-api", "#topic/architecture"]
created: 2026-05-19
updated: 2026-05-19
related:
  - "[[11-wiki/mfl-voice-tts-providers-comparison]]"
  - "[[11-wiki/mfl-voice-multilingual-pipeline]]"
  - "[[11-wiki/jarvis-persona-design-spec]]"
  - "[[11-wiki/mfl-voice-jarvis-mother-research]]"
source:
  - "10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q1.md"
  - "10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q2.md"
  - "10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q3.md"
  - "10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q4.md"
  - "10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q5.md"
---

# Voice-agent architektúra mintázatok — STT + LLM + TTS stack 2026 H1

Evergreen-referencia hangalapú asszisztensek tervezéséhez: 3-szintű architektúra-taxonómia (Level 1/2/3), wake-word stratégiák, transport-választás (WebSocket vs WebRTC), turn-taking + barge-in, state-machine, function-calling, function-call sandbox + audit-log.

## TL;DR — voice-agent stack 30 mp alatt

**3 alapvető architektúra-szint** (2026 H1):

| Szint | Példa | Jellemző | Use-case |
|------|-------|---------|---------|
| **L1 — natív S2S** | Moshi, Kyutai | ~200ms latencia, audio-tokenek | Konverzációs MVP, alacsony reasoning |
| **L2 — Beszéd-augmentált LLM** | Gemini 3.1 Live, GPT-Realtime-2, Qwen3-Omni | 570-1180ms, erős reasoning + natív audio | Voice agents, function-calling |
| **L3 — Kaszkádos pipeline** | Pipecat / LiveKit + Claude + ElevenLabs | 958-1054ms, modul-szabadság | Vállalati, magas customization, brand-voice |

**A "human turn-taking gap"** 200ms — ez a célzott TTFA. **800ms felett 40%-os call-abandon növekedés**, 3s felett a csendet inkompetenciának érzik.

## A 2026-os SOTA latencia-mátrix

A források szerint a következő mérések éles tesztekben (2026 H1):

| Engine | TTFA / Turn-taking | Megjegyzés |
|--------|--------------------|-----------|
| **Gemini 3.1 Flash-live (minimal)** | **570ms** | Sebességi rekord |
| **GPT-Realtime-1.5** | **590ms** | Második leggyorsabb |
| **GPT-Realtime-2 minimal** | 1180ms | Robusztusabb reasoning |
| **GPT-Realtime-2 xhigh** | 1630ms | Komplex feladatokhoz |
| **Kaszkádos (Deepgram STT + Claude + ElevenLabs)** | 958-1054ms | TTS 221ms + LLM TTFT 457ms |
| **Iparági medián (production)** | 1400-1700ms | Még a sok L3-as deployment |

> Forrás: [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q1]]

**Voice Agent Quality Index (VAQI)** mérési modell: 40% megszakítás-büntetés, 40% missed-response büntetés, 20% latencia. Paradox módon a Deepgram L3 kaszkádot mérték "legkellemesebbnek" (70+ pont) az alacsony megszakítás-ráta miatt.

## Mintázat 1 — transport: WebSocket vs WebRTC

**Trade-off:**

| Transport | Pufferelés | Csomagvesztés-kezelés | Komplexitás | Mikor |
|-----------|-----------|----------------------|-------------|-------|
| **WebSocket** | 100-200ms extra | Manuális | Egyszerű | <500ms cél nem kritikus, managed platformok (Vapi, Deepgram) |
| **WebRTC** | 20-50ms | Auto (adaptive bitrate) | Magasabb | <500ms TTFA célzott, multi-party, mobil/instabil hálózat |

> **500ms alatti TTFA → WebRTC kötelező**, ez az iparági standard. LiveKit SFU architektúrára épül.

## Mintázat 2 — wake-word stratégiák

3 opció, 4 dimenzió mentén:

| Stratégia | Privacy | Battery | Accuracy | Komplexitás |
|-----------|---------|---------|----------|-------------|
| **Picovoice Porcupine (on-device)** | Kiváló (100% local) | Minimális | Alacsony FPR, custom-trained | Közepes (API key + modell-fájl) |
| **Custom Whisper (tiny/small) + Silero VAD** | Kiváló (100% local) | Magas (CPU/GPU folyamatos) | Magas WER, FPR nehezebb | Magas (saját pipeline) |
| **Always-on cloud (Gemini Live)** | Alacsony (stream) | Közepes-magas (hálózat) | Extrém alacsony FPR (server-VAD) | Alacsony (WebSocket/WebRTC) |

**Default ajánlás Linux dev workstation + headset esetén:** Custom Whisper (tiny) + Silero VAD gating. Silero VAD = 2MB, <1ms / 32ms chunk, 0% felhős költség, 100% privacy. Forrás: [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q2]].

## Mintázat 3 — turn-taking + barge-in state-machine

**Klasszikus 5-állapot streaming VAD wrapper:**

```
[ IDLE ]
   ↓  speech detected
[ LISTENING ]
   ↓  silence 700ms / dynamic TRP predikció
[ PROCESSING ]
   ↓  LLM + TTS streaming start
[ SPEAKING ]
   ↓  done
[ IDLE ]
```

**Barge-in (megszakítás) ág:**
```
[ SPEAKING ]
   ↓  barge-in event (user utterance + echo-cancellation után)
[ TTS audio buffer flush ]  → AZONNAL [ LISTENING ]
```

**Kritikus fogalmak:**

- **TRP (Transition-Relevance Place)** — a beszédjog-átadás ideális pillanata. Predictive turn-taking modellek (VAP, TurnGPT, Moshi) szintaxis + prozódia + gesztusok alapján *előre* jósolják, így a generálás már a csend előtt megindul.
- **Backchanneling** — "aha", "mm-hm" → **együttműködő átfedés (cooperative)**, NEM jelent beszédjog-szerzést. Modern rendszerek NEM kezelik megszakításként.
- **Filler-Word Eater hiba** — naive 500ms csend-threshold belevág a felhasználó "őőő..." gondolkodásába. Adaptive interruption handling kell akusztikus + szintaxis-jelekkel.
- **TFO (Turn Floor Offset)** = 200ms emberi reakció. Válasz-tervezés 600ms — ezért a tiszta silence-based EOT kudarcra ítélt.

## Mintázat 4 — UX context vs. wake-word stratégia

| Kontextus | Akusztikus kihívás | Ajánlott UX |
|-----------|-------------------|-------------|
| Mobile (mozgásban) | Instabil hálózat, utcai zaj | Hibrid: PTT + always-on toggle |
| Desktop (csendes szoba) | Alacsony interferencia | **Always-on dominál** |
| Studio (multi-party) | Cocktail party probléma | Context-aware (ACTIVE / SILENT / BYSTANDER) |
| Car (vezetés) | Motor + szél + duda | Always-on (hands-free) + voiced speech gating |
| Accessibility | Motoros nehézség | **Always-on kritikus** (PTT akadály) |

## Mintázat 5 — function-call sandbox (shell-command végrehajtás)

Hangalapú LLM-mel **TILOS** közvetlenül nyers bash-t generáltatni — az LLM-ek inkonzisztensek a szabály-alkalmazásban. A 4-réteges védelem:

### 1. Allow-list pattern
Az LLM strukturált JSON-paramétereket ad, a backend validál egy előre definiált tool-szótár ellen (pl. `run_service_restart` paraméterekkel). NEM `bash -c "<LLM_OUTPUT>"`.

### 2. MCP-tool-bridge
Az LLM **soha nem kap nyers TTY-t**, hanem MCP (Model Context Protocol) connectoron keresztül:
- `mcp__chrome-devtools` — web debug
- `mcp__playwright` — UI testing
- `mcp__local_shell` — sandboxolt terminál, allow-list mögött

### 3. Confirmation-dialog destruktív műveletekre
Bármi `rm`, `drop table`, `force-push` → felfüggesztés, explicit TTS-promptolt megerősítés ("Biztosan törölni akarod a production adatbázist?"). Csak explicit **"Igen / Yes"** STT-felismerés után végrehajt. System-promptba beégetve: *"Várd meg az egyértelmű felhasználói jóváhagyást, mielőtt bármilyen funkciót meghívnál."*

### 4. Audit-log minden voice-command-ról
**Turn-Level Conversation Analysis** elv — naplózd:
- A kérés payload (LLM-input)
- A válasz payload (LLM-output / tool-call)
- Hálózati + végrehajtási latencia
- Státuszkód + hibatípus
- **STT-nyers átirat** (a pontos hangzott szöveg)

Forrás: [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q3]]

## Anti-pattern — voice-agent hibák

1. **Csend-based EOT detection only** — Filler-Word Eater hiba, "őőő" levágva. Predictive turn-taking kell.
2. **Always-on cloud streaming dev workstation-ön napi 8-10 órán át** — privacy + költség double-loss. Lokális VAD gate kötelező.
3. **LLM-re bízzuk a tool-arg validációt** — "Az LLM-ek inkonzisztensek a szabály-alkalmazásban". Kód-szintű validáció determinisztikus, tesztelhető.
4. **Backchannel-t megszakításként kezelni** — minden "aha"-ra leáll → frusztrálja a usert.
5. **Whisper-hallucinációkat tool-call-ba engedni** — ~1% hallucination, **38%-uk kártékony**. Mandatory HUN Rate (Hallucination-Under-Noise) < 2%, Downstream Propagation 0%.
6. **WebSocket TTFA <500ms cél esetén** — 100-200ms extra pufferelés meghaladja a budget-et. WebRTC kötelező.
7. **MCP-tool-bridge nélkül nyers shell-access** — még allow-list-tel is nehezen audit-álható; az MCP-réteg az iparági standard 2026-ra.

## Reusable — voice-agent architektúra-választó

```
START
  ↓
Q1: Kell brand-voice / persona-customization?
  ├─ Igen → L3 kaszkádos (Pipecat/LiveKit + Claude + ElevenLabs)
  └─ Nem → Q2
       ↓
Q2: <600ms TTFA követelmény?
  ├─ Igen → L2 (Gemini 3.1 Live vagy GPT-Realtime-1.5)
  └─ Nem → Q3
       ↓
Q3: Komplex reasoning / function-call kell?
  ├─ Igen → L3 (Claude tool-use + STT/TTS)
  └─ Nem → L1 (Moshi-szerű, MVP)
```

## Magyar nyelv-specifikus megjegyzések

- **STT (code-switching HU↔EN):** AssemblyAI Universal-3 Pro Streaming a SOTA — beépített code-switching + prompting (custom vocabulary), ~300ms latency, **$0.15/óra** (a teljes Voice Agent API $4.50/óra).
- **STT alternatíva:** Faster-Whisper (CTranslate2) lokálisan, 4× gyorsabb mint az original Whisper, 150-300ms. WER tiszta beszéden 95%+, irodai zaj +3-5%, utcai zaj +15-20%.
- **Magyar function-calling benchmark hiányzik** a forrásokból (sem AssemblyAI, sem OpenAI Whisper, sem Gemini specifikus HU-mérést nem közöl).
- **Anthropic Claude nem ad natív voice API-t** 2026 H1-ben — szöveges LLM-ként L3 kaszkádba illeszthető (Pipecat / LiveKit orchestráció).

## Költség-modell (referencia)

| Szolgáltató | Voice Agent ($/óra) | Megjegyzés |
|-------------|---------------------|-----------|
| LiveKit (infra only) | $0.01/perc-től | Csak transport, AI külön |
| AssemblyAI Universal-3 (STT only) | $0.15 | Olcsó standalone STT |
| Retell AI | $0.07/perc (~$4.20/h) | Managed |
| Deepgram Voice Agent (STT+LLM+TTS) | $4.50/óra | Integrált |
| OpenAI Realtime audio | $32/1M input + $64/1M output | Token-based |
| Anthropic Claude Sonnet 4 | $1.94/1M token | Csak text-LLM |

## Kapcsolódó

- [[11-wiki/mfl-voice-tts-providers-comparison]] — TTS engine-választó mátrix
- [[11-wiki/mfl-voice-multilingual-pipeline]] — magyar TTS text-prep + code-switching
- [[11-wiki/jarvis-persona-design-spec]] — persona-réteg az architektúra fölött
- [[11-wiki/mfl-voice-jarvis-mother-research]] — master research desztillátum
