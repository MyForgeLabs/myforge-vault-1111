---
name: Web Speech API — continuous STT + echo-loop prevention
type: wiki
created: 2026-05-16
updated: 2026-05-16
tags: ["#type/wiki", "voice", "stt", "web-api", "browser"]
related:
  - "[[02-Projects/mfl-voice]]"
  - "[[11-wiki/gemini-3-1-flash-tts-pipeline]]"
  - "[[05-Memory/Infrastructure]]"
---

# Web Speech API — continuous STT + echo-loop prevention

A browser-native `SpeechRecognition` API (Chrome / Edge / Safari) **ingyenes** speech-to-text, magyar nyelvi támogatással (`lang='hu-HU'`). Always-on voice-chat MVP-hez tökéletes — DE két jellegzetes buktató van: **Chrome 60s auto-stop** és **echo-loop saját TTS-en**.

## Quick reference

| Property | Érték |
|----------|-------|
| Constructor | `window.SpeechRecognition \|\| window.webkitSpeechRecognition` |
| Engedély | HTTPS-context vagy `localhost` (Tailscale IP-n NEM — lásd [[05-Memory/Infrastructure#Web Speech API + Tailscale HTTPS]]) |
| Magyar minőség | Chrome HU-STT ~90% WER, mondat-vége intonációval jobb |
| Költség | $0 (browser-side, Google szerver-oldal) |
| Mikrofon-permission | Első használat-kor Chrome popup, "Always allow" opció permanens |
| Latency | ~200-500ms first-partial, ~1s end-of-speech detect |

## Minimal init

```javascript
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const recog = new SR();
recog.lang = 'hu-HU';
recog.continuous = true;        // always-on mode
recog.interimResults = true;    // partial + final results
recog.maxAlternatives = 1;

recog.onresult = (ev) => {
  let interim = '', final = '';
  for (let i = ev.resultIndex; i < ev.results.length; i++) {
    const tr = ev.results[i][0].transcript;
    if (ev.results[i].isFinal) final += tr;
    else interim += tr;
  }
  // interim → live preview; final → submit
};

recog.start();
```

## Gotcha 1: Chrome 60s auto-stop (auto-restart pattern)

A Chrome biztonsági szabálya: bármilyen continuous `SpeechRecognition` ~60s után **`onend` esemény-szel leállítja**, akkor is ha `continuous=true`. Ez nem hiba — privacy védelem ("avoid silent always-on surveillance").

**Helyes pattern — auto-restart az `onend`-en:**

```javascript
let alwaysOn = true;
let mutedForTTS = false;

recog.onend = () => {
  if (alwaysOn && !mutedForTTS) {
    setTimeout(() => {
      try { recog.start(); } catch (e) { console.warn(e); }
    }, 150);
  }
};
```

A 150ms delay azért kell, mert a recog-object internal state-je nem azonnal `'inactive'`. Túl gyors `start()` `InvalidStateError`-t dob.

## Gotcha 2: Echo-loop a TTS-en — mute-during-speech

Ha a STT folyamatosan hallgat ÉS a saját TTS-ed (Gemini, ElevenLabs, etc.) a hangszóróban játszódik, a mikrofon **vissza-hallja** a TTS-t → STT transzkripció → submit → újabb chat → újabb TTS → végtelen loop.

**Megoldás — TTS-during-mute:**

```javascript
async function playTTSResponse(blob) {
  // 1. Mute STT BEFORE audio starts
  mutedForTTS = true;
  try { recog.stop(); } catch {}

  // 2. Play TTS
  const audio = new Audio(URL.createObjectURL(blob));
  await new Promise((resolve) => {
    audio.addEventListener('ended', resolve);
    audio.addEventListener('error', resolve);
    audio.play();
  });

  // 3. Unmute STT after audio ends
  mutedForTTS = false;
  if (alwaysOn) setTimeout(() => recog.start(), 250);
}
```

A 250ms delay az `'ended'` event után azért kell, mert egyes audio-driverek (különösen Bluetooth headphone) tail-buffer-t pakolnak vissza, ami a mikrofonon megjelenne.

## Gotcha 3: `no-speech` és `aborted` errors benign always-on módban

A `recog.onerror` a következő error-okat dobhatja:
- `'not-allowed'` — user mikrofon-permission denied (komoly, mode-váltás push-to-talk-ra)
- `'no-speech'` — folyamatos csendben gyakran, **NE jelenítsd hibaként always-on módban**, a `onend` auto-restartol
- `'aborted'` — user-action vagy `recog.stop()` által kiváltott normal stop, **benign**
- `'network'` — Google STT cloud-side hiba, retry-elhető
- `'audio-capture'` — mikrofon hardware-hiba

**Helyes handling:**

```javascript
recog.onerror = (ev) => {
  if (ev.error === 'not-allowed') {
    setMode('push-to-talk');
    showPermissionDeniedMessage();
  } else if (ev.error === 'no-speech' || ev.error === 'aborted') {
    // benign — onend will fire and restart
  } else {
    console.warn('STT error:', ev.error);
  }
};
```

## Gotcha 4: Csak final-result-on submit, interim-result-ot mutasd

A `interimResults=true` mellett minden szótag után jön egy `result`-event. Ezeket **ne submit-eld** — csak vizuális preview. Submit-eld a `result.isFinal === true` szegmenseket.

```javascript
if (final.trim() && !busy && !mutedForTTS) {
  inputEl.value = '';
  submitMessage(final);
}
```

A `final.trim()` szűr a véletlen üres-string final-okra. A `!busy && !mutedForTTS` védő-guard: ha már fut egy submit, vagy a TTS éppen szól, ne lőjj másikat.

## Gotcha 5: Mode-toggle UX (always-on vs push-to-talk)

**Always-on előny:** természetes turn-taking, hands-free.
**Always-on hátrány:** mikrofon-on-state-anxiety, accidental triggers (háttér-beszélgetés a szobában → submit), Chrome 60s restart-jitter.

**Push-to-talk előny:** explicit user-intent, no accidental.
**Push-to-talk hátrány:** UI-elem kattintás kell (vagy Shift+Space hold).

**Helyes mintázat:** **default push-to-talk**, user-toggle always-on-ra. Az always-on aktiválása explicit consent-jellegű, és csendben kezeli a `no-speech` event-eket.

## Latency-budget

Tipikus end-to-end voice-chat lánc (STT + LLM + TTS, NEM Live API):

| Lépés | Latency |
|-------|---------|
| STT first-partial | ~200ms |
| STT end-of-speech detect | ~800-1500ms (a user beszéd-végi szünete) |
| Network → chat API | ~50ms |
| LLM gen (Gemini Flash, 150 token output) | ~600-1200ms |
| TTS gen (Gemini 3.1 Flash, 50 word) | ~400-800ms |
| Network → audio blob | ~100ms |
| Browser audio start | ~50ms |
| **Total TTFB** | **~2-4s** |

Ez NEM JARVIS-szintű reszponzivitás. Igazi real-time-hoz **Gemini Live API** vagy **OpenAI Realtime API** (bidi WebSocket, ~300ms TTFA) szükséges. Lásd [[11-wiki/mfl-voice-jarvis-mother-research#5-voice-agent-architektúra-2026]].

## Browser-támogatás (2026 H1)

| Böngésző | Web Speech API | HU lang |
|----------|----------------|---------|
| Chrome desktop | ✅ | ✅ |
| Chrome Android | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Safari macOS 17+ | ✅ (limited) | ⚠️ szegényes |
| Firefox | ❌ (disabled by default) | — |

Production-stack-hez: Chrome/Edge target, fallback push-to-talk. Safari/Firefox = degraded UX, írj text-input-ot.

## Kapcsolódó

- [[02-Projects/mfl-voice]] — szülő-projekt
- [[11-wiki/gemini-3-1-flash-tts-pipeline]] — TTS lánc második fele
- [[11-wiki/mfl-voice-jarvis-mother-research]] — VOICE_ARCH részletek (Q1-Q5)
- [[05-Memory/Infrastructure#Web Speech API + Tailscale HTTPS]] — HTTPS-context Tailscale-en
<!-- auto-enriched 2026-05-18: +1 semantic cross-link via vault-search -->
- [[sv-08-notebooklm-cognitive-layer]] (sem-rokon, score=0.56)
