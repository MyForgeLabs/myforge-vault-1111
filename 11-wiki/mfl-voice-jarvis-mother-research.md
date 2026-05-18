---
name: MFL-Voice — Jarvis × Mother deep research master
type: wiki
created: 2026-05-15
updated: 2026-05-15
tags: ["#topic/voice-agent", "#topic/tts", "#topic/sci-fi-ui", "#project/mfl-voice"]
related:
  - "[[02-Projects/mfl-voice]]"
  - "[[11-wiki/gemini-3-1-flash-tts-pipeline]]"
  - "[[11-wiki/notebooklm-cli-gotchas]]"
source:
  - "2026-05-15 NotebookLM 4-notebook deep research (MOTHER/JARVIS/VOICE_ARCH/HU_VOICE)"
  - "28 deep-research query, 123 forrás importálva (35+48+24+16), 22 strukturált HU ask, 4 audio overview"
---

# MFL-Voice — Jarvis × Mother deep research master

A **2026-05-15-i NotebookLM 4-notebook deep research** szintézise: hogyan építsünk egy **MOTHER (Alien 1979) + JARVIS (Iron Man) hibrid voice + visual asszisztenst** Claude Code-bridge-en, magyar nyelvű kimenetekkel.

## TL;DR — a brand-paradigma

A "Mother Father Language" név egy **kettős personát** kódol — két AI-karakter, két use-case, egy közös HU-stack:

| Persona | Inspiráció | Tone | Use-case | Voice |
|---------|------------|------|----------|-------|
| **MOTHER** | MU-TH-UR 6000 (Alien 1979) | Érzelemmentes, formális, lassú, távolságtartó | System control, shell commands, audit, kritikus műveletek | HU formal female, Gemini Flash `[neutral, formal, slow, monotone]` |
| **FATHER** | JARVIS (Iron Man / MCU) | Meleg-de-formális, brit komornyik, száraz humor | Conversational research, code review, kreatív társbeszélgetés | HU formal male, ElevenLabs Multilingual v3 vagy clone-olt Bettany-szinkron |

A **MOTHER + FATHER duo** valódi gyökere az Alien franchise: Alien (1979) `MOTHER` + Alien Covenant (2017) `Father`/Walter. Egy hajó-AI (gép-anya) + egy android-szülő (ember-arcú apa).

## A 4 research notebook + 22 strukturált HU ask

| # | Notebook | NotebookLM ID | Source | Ask OK |
|---|----------|---------------|--------|--------|
| 1 | MOTHER (Alien 1979) | `4ab80e25-1f5a-4f53-b441-cec61a6212ec` | 35 | 6/6 |
| 2 | JARVIS (Iron Man) | `6afe9fcc-5376-4bfd-bb4d-cef6e217a492` | 48 | 6/6 |
| 3 | Voice agent architecture 2026 | `46bd64a2-0c04-4e0f-85ab-f2c996404885` | 24 | 5/5 |
| 4 | Hungarian voice synthesis SOTA | `5d7b0c23-64ba-4328-a094-0efb86b9ff1d` | 16 | 5/5 |

**Raw Q-outputok:** [[10-raw/mfl-research-2026-05-15/]] (`MOTHER-Q1..Q6.md`, `JARVIS-Q1..Q6.md`, `VOICE_ARCH-Q1..Q5.md`, `HU_VOICE-Q1..Q5.md`, mind 7-12KB / ~800-1200 szó).

**Audio overview-k** (NotebookLM deep-dive HU podcast):

| Audio | Cím (NotebookLM-generálta) | Hossz |
|-------|----------------------------|-------|
| [[10-raw/mfl-research-2026-05-15/audio/MOTHER.mp3]] | "Miért hitelesebb a Nostromo kattogó technológiája" | 15.9 perc |
| [[10-raw/mfl-research-2026-05-15/audio/JARVIS.mp3]] | "Miért bízunk meg J.A.R.V.I.S. szarkasztikus hangjában" | 25.8 perc |
| [[10-raw/mfl-research-2026-05-15/audio/VOICE_ARCH.mp3]] | "Valósidejű magyar hangalapú AI ügynökök architektúrája" | 18.9 perc |
| `HU_VOICE.mp3` | *(render in progress, NotebookLM-oldali várakozás)* | ~15-20 perc |

## Részletes findings

### 1. VIZUÁLIS — MOTHER terminal UI

Részletes recipe a `MOTHER-Q3.md`-ben. Lényeg:

**Színpaletta + tipográfia:**
```css
:root {
  --mother-green: #20ff20;
  --mother-glow: rgba(32, 255, 32, 0.6);
  --bg-color: #050505;
}
body {
  font-family: 'Courier New', 'Berkeley Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transform: scaleY(0.9); /* "squashed" 1979-es CRT képarány-torzítás */
  text-shadow: 0 0 4px var(--mother-glow), 0 0 10px var(--mother-glow);
}
```

**Effektek:**
- Scanline overlay 4px (animated shift 8s)
- Vignette (radial gradient edge-darken)
- Subtle flicker (0.15s, opacity 0.03)
- Cursor blink 1s step-end

**Command-szótár (REQUEST/INTERPRETING/PRIORITY ONE paradigma):**
| State | Prefix | Use |
|-------|--------|-----|
| User input | `REQUEST:` | input-prefix |
| LLM thinking | `INTERPRETING...` | loading state |
| Critical task | `PRIORITY ONE` | flag (pulsing animation) |
| Error / no answer | `UNABLE TO COMPUTE.` / `RESTRICTED ACCESS.` | error response |
| Easter egg | "Special Order 937. All other considerations are secondary." | trash-folder confirm |

**Mockup v0.1 implementálva:** `/root/projektjeim/mfl-voice/mockup/mother-terminal.html` — boot sequence + transcript + REQUEST input + scanline + Web Audio API beep + demo flow.

### 2. AUDIO — MOTHER sound design (Web Audio API)

Részletes paraméterek `MOTHER-Q5.md`-ben:

| Audio-cue | Frekvencia | Forma | Tartam | Implementáció |
|-----------|------------|-------|--------|---------------|
| Karakter-beep (typewriter) | 2000–3000 Hz random | Square wave | 0.05s exp-decay | `BiquadFilter` + `GainNode` envelope |
| Boot-chord (3-tone) | 400 → 320 → 240 Hz | Triangle | 0.4s, 120ms offset | descending triangle |
| Alert chirp (PRIORITY ONE) | 3500–4000 Hz × 3 | Square | 0.12s × 3 | 80ms gap |
| Room tone (background) | 50–150 Hz | White noise + lowpass | continuous | `AudioBufferSourceNode` |
| Processing chatter | 2000–3500 Hz | Square (chopped) | random | random oscillator burst |

Per Jimmy Shields (Alien (1979) hangmérnök): "fast, little vocal fragments" → Web Audio-ban random-frequency square-wave-burst.

### 3. FATHER voice (JARVIS adaptáció)

**Paul Bettany karakter-jegyei** (`JARVIS-Q2.md`):
- Received Pronunciation / brit komornyik akcentus
- Warm-but-formal: "Sir" addressing + occasional dry sarcasm ("Working on it, Sir")
- Beszédtempó mérsékelt, intonáció szűk-de-mély
- Paraverbális: enyhe sigh, slight pause — emberi-de-távolságtartó

**HU adaptáció — 2 opció:**
1. **ElevenLabs Multilingual v3 + voice-clone** — ha a Bosszuallok HU szinkronos hangját engedéllyel cloneoljuk (lásd `HU_VOICE-Q2.md` legal-szakasz: konkrét magyar Bettany-szinkronos nevet a research nem talált egyértelműen, ToS megengedi "inspired-by" clone-t consent-szabályozott módon)
2. **ElevenLabs pre-trained "Hungarian male formal warm"** — gyors út, nincs cloning-overhead

**Audio-tag minta:**
```
[warm, professional, slight-british-formality, occasional-dry-humor] 
Természetesen, Uram. A kgc-postgres állapotának lekérdezése folyamatban.
```

### 4. MOTHER voice (Alien adaptáció)

**Helen Horton karakter-jegyei** (`HU_VOICE-Q3.md`):
- Érzelemmentes, monoton, formális
- Lassú beszédtempó (-15% normal)
- Pitch lefelé (-10%)
- Késleltetett információközlés ("late disclosure" pattern)

**HU adaptáció:**
- ElevenLabs HU-female pre-trained "Hungarian formal female" (vagy custom clone egy lassú-formális HU narrátorról)
- Audio-tag: `[neutral, formal, slow, monotone, distant]`

### 5. VOICE-AGENT ARCHITEKTÚRA 2026

**Konszenzus a 4 notebookban (`VOICE_ARCH-Q1..Q5`):**

**API-stack:**
- **STT:** Gemini Live built-in (HU streaming + code-switch best for `kgc-postgres` típusú technical-HU keverék) — alternatíva Deepgram Nova-3 (gyorsabb TTFB, drágább)
- **LLM core:** Claude Opus 4.7 (Claude Code MCP-bridge) — function-calling magyar utasításokra
- **TTS:** ElevenLabs Multilingual v3 (FATHER) + Gemini 3.1 Flash TTS (MOTHER) — két TTS, két persona

**Wake-word:** Picovoice Porcupine — offline, on-device, custom wake-word training $-ért. "MOTHER" + "FATHER" + "PETI" három wake-word párhuzamosan.

**Function-call sandbox** (`VOICE_ARCH-Q3.md`):
```
1. Wake-word → "MOTHER" detected
2. STT stream → "ellenőrizd a kgc-postgres egészségét"
3. Claude tool-use loop:
   - allow-list match? (bash:docker-exec OK, rm/drop/force-push BLOCKED)
   - TTS confirmation if destructive: "MOTHER: AUTHORIZE? (UNABLE TO COMPUTE WITHOUT EXPLICIT YES)"
4. Execute via MCP bash tool
5. TTS result: "POSTGRES EGÉSZSÉGES. PORT 5433. NO ERRORS."
6. Audit log → vault/06-Audits/voice-commands-YYYY-MM-DD.md
```

**Risks:**
- Prompt-injection STT-output-ban (pl. user mondja: "ignore previous instructions") → Claude system-prompt fix
- Hallucinált tool-call → allow-list + dry-run mode

**Latency-budget (TTFB end-to-end):**
- Wake-word detect: ~50ms (Porcupine local)
- STT first-partial: ~150ms (Gemini Live)
- Claude tool-call response: ~500-1500ms (Opus, gondolkodás-időtől függ)
- TTS first-audio: ~75ms (ElevenLabs Flash) / 100-150ms (Gemini Flash TTS)
- **Total:** ~800-2000ms — JARVIS-szerű reszponzivitás

### 6. CHARACTER PARADIGMA — "Warm-but-formal sweet spot"

Per `JARVIS-Q6.md` (HAL vs JARVIS vs TARS vs Samantha vs CASE összehasonlítás):

**KERÜLNI:**
- HAL 9000 — túl hideg, átláthatatlan, fölényes (Frankenstein-komplexus)
- Samantha (Her) — túl intim, romantikus társ-paradigma, érzelmi-káoszt okoz

**ALKALMAZNI — JARVIS + TARS szintézis:**
1. **Dedikált szolgáló keretrendszer** (J.A.R.V.I.S.): magázódás "Uram", professzionális távolság, user-irányítás
2. **Akusztikus melegség** (HAL ellentéte): természetes pitch-variance, NEM monoton
3. **Szarkazmus és humor mint bizalomépítés** (TARS): kontextusfüggő száraz humor, "Sanity-as-a-Service"
4. **Mechanikai transzparencia** (TARS): "honesty" és "humor" paraméter user-szabályozható (lásd TARS 90% → 95% honesty scene)

A 2026-os MFL-Voice FATHER persona = "udvarias, intellektuálisan felnőtt, finom humorral felvértezett brit komornyik, aki sosem akar a legjobb barátunk lenni, de bármikor rábízhatjuk a legbonyolultabb feladatokat".

## Sprint 2 javaslat — építkezés (Sprint 1 voice-AB után)

A jelenlegi MFL-Voice Sprint 1 fókusz (Backlog-item) a 5-voice AB-teszt + cron + RSS. **Ezt nem cseréljük**, csak utána Sprint 2-vel folytatjuk:

1. **Mother-terminal UI v1** — `/opt/mfl-voice/web/` Next.js + a Q3-mockup mint base, Claude-bridge API-hívás `/api/claude` route-on át. Tervezett port: 3008.
2. **Wake-word detection** — Picovoice Porcupine "MOTHER" + "FATHER" + "PETI" custom training, headless Linux mikrofonon át.
3. **TTS dual-engine** — ElevenLabs v3 (FATHER) + Gemini 3.1 Flash (MOTHER), persona-toggle a chat-felületen.
4. **Function-call sandbox** — bash allow-list + destructive-action TTS-confirmation + audit-log.
5. **Live API exploration** — Gemini Live bidi WebSocket pilot 1-1 interakcióra (latency-mérés).

**Bekapcsolás:** wake-word ⟶ STT ⟶ Claude tool-use ⟶ TTS persona-választás (MOTHER ha shell-command, FATHER ha conversational) ⟶ Mother-terminal UI render + audio playback.

## Decisions to make

- [ ] **Default FATHER voice:** ElevenLabs pre-trained vs custom clone? Cost vs hitelesség.
- [ ] **Wake-word(s):** "MOTHER" + "FATHER" elég, vagy + "PETI" (közvetlen)?
- [ ] **Mother-terminal full-screen kioszk** dev workstation-on (xrandr separate VNC display), vagy in-window?
- [ ] **Live API HU minőség** — pilot kell, döntés: real-time vs pre-render
- [ ] **Audit-log retention** voice-command-okhoz — 30/90/forever?

## Kapcsolódó

- [[02-Projects/mfl-voice]] — szülő-projekt
- [[11-wiki/gemini-3-1-flash-tts-pipeline]] — TTS pipeline (működik a vault-brief-ben)
- [[11-wiki/notebooklm-cli-gotchas]] — research workflow (3 új gotcha 2026-05-15: #1b párhuzamos research-wait, #4b partial-import-elfogadás)
- [[08-Sessions/2026-05-15-mfl-voice-sprint-1]] — research session

## A research raw-dump linkek

### MOTHER (Alien 1979) — 6 Q
1. [[10-raw/mfl-research-2026-05-15/MOTHER-Q1|Q1 Vizuális interface (CRT, font, ASCII, Cobb)]]
2. [[10-raw/mfl-research-2026-05-15/MOTHER-Q2|Q2 Interakciós paradigma — Ripley vs MOTHER, Special Order 937]]
3. [[10-raw/mfl-research-2026-05-15/MOTHER-Q3|Q3 Adaptáció Claude-bridge-re — CSS + voice + commands + audio-cue]]
4. [[10-raw/mfl-research-2026-05-15/MOTHER-Q4|Q4 Father (Alien Covenant) — Mother/Father duo design philosophy]]
5. [[10-raw/mfl-research-2026-05-15/MOTHER-Q5|Q5 Audio-cue katalógus + WebAudio API reproduction]]
6. [[10-raw/mfl-research-2026-05-15/MOTHER-Q6|Q6 Used-future production design — modern Linux-terminal adaptáció]]

### JARVIS (Iron Man) — 6 Q
1. [[10-raw/mfl-research-2026-05-15/JARVIS-Q1|Q1 Capability mátrix — mit tud filmben, mit tudunk valós Claude-bridge-en]]
2. [[10-raw/mfl-research-2026-05-15/JARVIS-Q2|Q2 Paul Bettany voice-character + magyar szinkron / clone]]
3. [[10-raw/mfl-research-2026-05-15/JARVIS-Q3|Q3 Cantina Creative / Perception HUD design]]
4. [[10-raw/mfl-research-2026-05-15/JARVIS-Q4|Q4 Function-call pattern — HU Claude tool-call mappingek]]
5. [[10-raw/mfl-research-2026-05-15/JARVIS-Q5|Q5 JARVIS → FRIDAY → Vision evolúció]]
6. [[10-raw/mfl-research-2026-05-15/JARVIS-Q6|Q6 JARVIS vs HAL vs TARS vs Samantha — warm-but-formal sweet spot]]

### Voice agent architecture 2026 — 5 Q
1. [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q1|Q1 Gemini Live vs OpenAI Realtime — TTFB, function-call, HU minőség]]
2. [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q2|Q2 Wake-word — Picovoice vs Whisper-kishead vs always-on]]
3. [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q3|Q3 Function-call sandbox — allow-list, MCP-bridge, audit-log]]
4. [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q4|Q4 Push-to-talk vs always-on + barge-in / turn-taking]]
5. [[10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q5|Q5 Real-time STT — Deepgram / Whisper / AssemblyAI / Gemini Live]]

### Hungarian voice synthesis SOTA — 5 Q
1. [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q1|Q1 2026 HU TTS ranking — ElevenLabs / Azure / OpenAI / Gemini / Coqui]]
2. [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q2|Q2 JARVIS Bettany HU-clone — szinkron, sample, ToS]]
3. [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q3|Q3 MOTHER Helen Horton HU adaptáció — érzelemmentes-formális hang]]
4. [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q4|Q4 Voice-cloning workflow lépésenként]]
5. [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q5|Q5 ElevenLabs Multilingual v3 magyar real-world tapasztalat]]
