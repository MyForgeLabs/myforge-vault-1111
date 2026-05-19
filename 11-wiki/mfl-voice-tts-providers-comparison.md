---
name: TTS provider összehasonlítás — 2026 H1 SOTA mátrix
type: reference
tags: ["#topic/voice-agent", "#topic/tts", "#topic/provider-comparison", "#topic/cost-modeling"]
created: 2026-05-19
updated: 2026-05-19
related:
  - "[[11-wiki/mfl-voice-multilingual-pipeline]]"
  - "[[11-wiki/voice-agent-architecture-patterns]]"
  - "[[11-wiki/jarvis-persona-design-spec]]"
  - "[[11-wiki/mfl-voice-jarvis-mother-research]]"
  - "[[11-wiki/gemini-3-1-flash-tts-pipeline]]"
source:
  - "10-raw/mfl-research-2026-05-15/HU_VOICE-Q1.md"
  - "10-raw/mfl-research-2026-05-15/HU_VOICE-Q2.md"
  - "10-raw/mfl-research-2026-05-15/HU_VOICE-Q3.md"
  - "10-raw/mfl-research-2026-05-15/VOICE_ARCH-Q1.md"
---

# TTS provider összehasonlítás — 2026 H1 SOTA mátrix

Evergreen-referencia a piacvezető TTS engine-ek tulajdonságairól: ár, latencia, prozódia, érzelmi kontroll, hangklónozás, streaming. **Provider-agnosztikus** — NEM project-specifikus, bármilyen voice-agent stack-választáshoz alapozó tábla.

## TL;DR — válassz 30 másodperc alatt

| Use-case | Ajánlott engine | Indok |
|----------|----------------|-------|
| Tartalomgyártás (filmes, érzelmes narráció) | **ElevenLabs Multilingual v3** | MOS ~4.1, finom érzelmi paraméterek, 10k+ közösségi hang |
| Vállalati IVR / e-learning skálán | **Azure Neural TTS** | $16 / 1M karakter, SSML, 400+ hang, stabil prozódia |
| Voice-agent real-time (TTFB <200ms) | **ElevenLabs Flash v2.5** vagy **Gemini 3.1 Flash TTS** | 75-150ms TTFB, WebSocket / natív streaming |
| Költségérzékeny podcast batch | **OpenAI TTS-1-HD** | $30 / 1M karakter, 6 fix hang, out-of-the-box minőség |
| Adatvédelem-kritikus, self-hosted | **Coqui XTTS-v2** | Lokális GPU, ingyenes szoftver, 6 másodperc clone |

## A 2026-os TTS piaci mátrix

A források szerint 5 fő engine versenyez a piacon, eltérő trade-off-okkal:

| TTS Engine | Prozódia (HU) | Érzelmi skála | Hang opciók / Clone | $/karakter | TTFB | Streaming |
| --- | --- | --- | --- | --- | --- | --- |
| **ElevenLabs Multilingual v3** | Kiváló (legtermészetesebb) | Magas (Stability + Style csúszka) | 10k+ közösségi, IVC + PVC | ~$0.00018-$0.00020 | 75ms (Flash), 200ms (Pro) | WebSocket |
| **Azure Neural TTS** | Nagyon stabil, tiszta | Közepes (SSML) | 400+ hang, Custom Neural Voice | $0.000016 ($16/1M) | 100-200ms | Real-time |
| **OpenAI TTS-1-HD** | Folyékony, enyhe akcentus | Alacsony (kontextus-függő) | 6 fix hang, NINCS clone | $0.00003 ($30/1M) | 300-500ms | Chunk API |
| **Gemini 3.1 Flash TTS** | Fejlődő preview | Közepes (natív prompt) | Limitált beépített | ~$0.00001 | 100-150ms | Native audio |
| **Coqui XTTS-v2** | Elmarad versenytársaktól | Alacsony | Bármilyen (self-hosted) | $0 + GPU | Hardverfüggő | Lokális |

> Forrás: a teljes elemzés [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q1]]-ben. Az ElevenLabs Multilingual v3 **MOS 4.1/5 és 89,60% természetességi ráta** angol nyelven, ami az iparági benchmark.

## Mintázat — ár vs. minőség Pareto-front

**Pareto-front 3 csoport:**

1. **Prémium tier (ElevenLabs Multilingual v3 + Flash v2.5)** — a legmagasabb természetességet adja, **a karakter-alapú kreditrendszer** miatt skálázódáskor drága ($22-99/hó Creator-Pro). Érdemes long-form content + brand voice esetén.
2. **Vállalati skála tier (Azure Neural)** — 10-20× olcsóbb mint az ElevenLabs ($16/1M karakter), de prozódia szempontból érezhetően "iparibb". Cserébe Pay-as-you-go, 500k karakter ingyenes / hó. Long-tail IVR, callcenter, e-learning.
3. **Ultra-budget / Preview tier (Gemini Flash TTS)** — kb. $0.00001/karakter, natív multimodális streaming-re tervezve. Még preview, intonáció nem teljesen kiforrott.

> [!quote] ElevenLabs vs. Azure trade-off
> "Az ElevenLabs abszolút uralja a szintetikus hangok piacát a minőség és a természetesség terén. Bár az árazása prémium kategóriás, a végeredmény (MOS 4.1) messze felülmúlja a versenytársakat."  
> — [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q1]]

## Mintázat — voice-cloning workflow

A klónozás **kétféle technológiát** kínál (ElevenLabs Reference, általánosítható):

- **Instant Voice Cloning (IVC):** 10mp – 5 perc clean audio, azonnali (<1 perc). Prototípus, social media.
- **Professional Voice Cloning (PVC):** 30 perc – 3 óra studio-grade audio. **44.1 kHz / 16-24 bit WAV**, -16 LUFS, -1.0 dBTP, **NEM kompresszált**. Stúdió-minőség, brand voice.

**Verification (consent-first):** Voice-Captcha biometrikus check — a hang tulajdonosának élőben fel kell olvasnia egy generált szöveget a mikrofonba. Resemble AI hasonlóan `Resemblyzer` open-source modullal validál.

## Anti-pattern — amit NE csinálj

1. **Filmrészletből / YouTube-rippelésből clone-olás:** Háttérzaj, zene, más beszélő → "garbage in, garbage out". Még jogi akadálytól eltekintve sem ad professzionális minőséget. Forrás: [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q2]].
2. **Híresség / közszereplő hangjának klónozása engedély nélkül:** ElevenLabs ToS explicit tiltja (personality rights). Fair-use NEM ad fedezetet biometrikus hangazonosító kereskedelmi célú másolására.
3. **Cross-language clone angol mintából magyar kimenetre:** A cél nyelvet a betanító dataset határozza meg — magyar prozódiához magyar source kell, különben "angol akcentussal beszél spanyolul" tipusú anomalia.
4. **MP3 / kompresszált audio PVC-hez:** Veszteséges tömörítési artifaktokat a model beletanulja. WAV PCM kötelező.
5. **OpenAI TTS-1-HD-választás ha brand voice / clone kell:** Szigorúan zárt ökoszisztéma, **6 fix hang**, semmi customization. Csak kész podcast/narráció.

## Reusable — az 5-engine választó-rubrika

Egy új voice-projekt indulásakor használd ezt a 4-kérdéses szűrőt:

1. **Kell-e brand-voice / clone?** Igen → ElevenLabs PVC vagy Coqui (self-hosted). Nem → mehet bármi.
2. **Hány óra audio / hó?** <10 óra → ElevenLabs Creator. 10-100 → Azure. 100+ → Azure enterprise vagy Coqui.
3. **TTFB követelmény?** <200ms → ElevenLabs Flash vagy Gemini. <500ms → OpenAI TTS-1-HD. Nem kritikus → Azure batch.
4. **Adatvédelem-kritikus?** Igen → Coqui (self-hosted, on-prem). Nem → felhő bármi.

## Magyar nyelv-specifikus megjegyzések

- **ElevenLabs Multilingual v2/v3 + Flash v2.5** hivatalosan támogatja a magyart (a 32 / 70+ nyelv egyikeként).
- **Code-switching (HU↔EN):** A v3 a piacvezető — egy mondaton belüli nyelvváltást zökkenőmentesen kezel a hang identitásának megtartásával.
- **Magyar Azure neurális hangok** (Noémi, Tamás) iparági standardnak számítanak, prozódiájuk stabil, de kevésbé filmszerű, mint az ElevenLabs.
- **Coqui XTTS-v2** hajlamos magyaron angolos intonációra és kiejtési hibákra a hosszabb mondatoknál.

Részletes magyar-pipeline: lásd [[11-wiki/mfl-voice-multilingual-pipeline]].

## Kapcsolódó

- [[11-wiki/mfl-voice-multilingual-pipeline]] — magyar TTS pipeline (text-prep, code-switching, settings)
- [[11-wiki/voice-agent-architecture-patterns]] — STT + LLM + TTS stack
- [[11-wiki/jarvis-persona-design-spec]] — persona-tervezés a TTS fölött
- [[11-wiki/mfl-voice-jarvis-mother-research]] — master research desztillátum
- [[11-wiki/gemini-3-1-flash-tts-pipeline]] — Gemini-specifikus implementáció
