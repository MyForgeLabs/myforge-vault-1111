---
name: Magyar TTS multilingual pipeline — text-prep, code-switching, settings
type: reference
tags: ["#topic/voice-agent", "#topic/tts", "#topic/multilingual", "#topic/hungarian-nlp"]
created: 2026-05-19
updated: 2026-05-19
related:
  - "[[11-wiki/mfl-voice-tts-providers-comparison]]"
  - "[[11-wiki/voice-agent-architecture-patterns]]"
  - "[[11-wiki/jarvis-persona-design-spec]]"
  - "[[11-wiki/hungarian-fuzzy-search]]"
  - "[[11-wiki/gemini-3-1-flash-tts-pipeline]]"
source:
  - "10-raw/mfl-research-2026-05-15/HU_VOICE-Q4.md"
  - "10-raw/mfl-research-2026-05-15/HU_VOICE-Q5.md"
  - "10-raw/mfl-research-2026-05-15/HU_VOICE-Q3.md"
---

# Magyar TTS multilingual pipeline — text-prep, code-switching, settings

Evergreen-playbook a magyar nyelvű hangszintézis end-to-end pipeline-jához: text-prep, code-switching kezelése (HU↔EN), prozódia-finomhangolás csúszkákkal, voice-cloning HU-rich datasetre, mondatvégi intonáció kényszerítése.

## TL;DR — pipeline 5 lépésben

1. **Text-prep** — IPA-tag, fonetikus átírás, sorszámok kiírva, írásjelek prozódia-vezérlésre
2. **Engine-választás** — ElevenLabs Multilingual v3 (v3 model) HU prozódiához, Azure Neural ha skála kell
3. **Code-switching kezelés** — v3 natív HU↔EN váltás, vagy explicit `<phoneme alphabet="ipa">` tag
4. **Voice-settings** — Stability magas (monoton/formális) / alacsony (kifejező), Similarity ≥ 0.75
5. **Validation** — listen-test HU anyanyelvi beszélővel, "kérdő-vége" anomalia ellenőrzés

## Háttér — miért nehéz a magyar TTS

A magyar prozódia 3 sajátossága okozza a legnagyobb gondot az angol-trained TTS modelleknek:

1. **Mondatvégi intonáció** — A magyar kijelentő mondatok **süllyedő** dallammal végződnek (a "csúsztatott zárlat"). Az angol-bias modellek hajlamosak fenntartani a középmagas regisztert → a magyar fülnek "kérdő" vagy "lebegtetett" érzés.
2. **Ragozás és összetett szavak** — A magyar agglutináló nyelv, egy ige 100+ alakot vehet fel. Code-switching idején a model hajlamos angol szavakat hallucinálni a magyar rag helyébe.
3. **Hangrend és magánhangzó-harmónia** — A `-ban/-ben`, `-on/-en/-ön` váltakozása fonetikailag finom, a model gyakran az angol intonációval magyarosítja → "doker-konténerben" ↔ "docker container-bAn" típusú hibák.

> [!quote] Forrás
> "A többnyelvű (multilingual) teljesítmény még mindig elmarad az angol nyelv minőségétől. Magyar nyelven ez tipikusan abban nyilvánul meg, hogy a modell esetenként angolos prozódiát alkalmaz a hosszú összetett mondatoknál, vagy nem ejti le elég határozottan a hangmagasságot a kijelentő mondatok végén."  
> — [[10-raw/mfl-research-2026-05-15/HU_VOICE-Q5]]

## Mintázat 1 — text-prep best practices magyarra

**Idegen szavak fonetikus átírása:**
```
ROSSZ: "A docker-konténer fut"     → "doker dʒouk-kontejnər"-szerű hiba
JÓ:    "A doker-konténer fut"      → magyar fonetika
JÓ:    "A <phoneme alphabet="ipa" ph="ˈdɒk.ə">docker</phoneme>-konténer fut"
```

**Sorszámok, dátumok, számok — MINDIG betűvel:**
```
ROSSZ: "2026 január 1."            → "húsz-huszonhat" vagy bizonytalan
JÓ:    "kétezer-huszonhat január elsején"
JÓ:    "tizenötödik percben"       (NEM "15. percben")
```

**Írásjelek mint prozódia-vezérlők:**

| Írásjel | Hatás |
|--------|-------|
| `,` | rövid szünet (~150ms) |
| `.` | mondatvég, süllyedő dallam |
| `—` (gondolatjel) | drámai szünet (~400ms) |
| `-` (kötőjel) | mikroszünet (~50ms) |
| `..` (dupla pont) | force-süllyedő prozódia kényszerítése, ha a mondatvégi intonáció nem süllyed eléggé |
| `;` | hosszú szünet (~250ms), közbeékelt gondolat |

**Betűszavak kezelése:**
```
ROSSZ: "a kgc-postgres"            → "kéigísí-posztgresz" (random)
JÓ:    "a ká-gé-cé-posztgresz"     → ejtett rövidítés magyarul
JÓ:    "a kgc Postgres adatbázis"  → ejtett rövidítés + külön szó
```

## Mintázat 2 — code-switching HU↔EN

A 2026-os SOTA modellek 3 megközelítést támogatnak:

1. **Native code-switching (ElevenLabs v3, Gemini Flash):** A modell szövegen belül felismeri a nyelvváltást és tartja a hang-identitást. "A `kgc-postgres` docker-konténer fut" — automatikus átkapcsolás. Csak technikai szakszavaknál (rövidítések, brand-nevek) van baj.
2. **Explicit IPA-tag (ElevenLabs API):** `<phoneme alphabet="ipa" ph="ˈdɒk.ə">docker</phoneme>` — precíz angol kiejtés. **Trade-off:** glottal-stop / mikroszünetet okoz a tag előtt-után.
3. **Magyarosított fonetika:** "doker" / "nekszt" / "ájdíí" — egyszerű, robusztus, de "magyaros" akcentusú angol szavakat eredményez.

**Választási rubrika:**
- Brand-név / saját termék → magyarosított fonetika (`Nekszt.dzséesz` helyett `Next.js` magyarul ejtve)
- Standard angol IT-szakkifejezés → native code-switching (v3) vagy IPA-tag
- Több mint 2-3 angol szó egy mondatban → érdemes prompt-templateban megadni `<lang>` markert

## Mintázat 3 — voice-settings finomhangolás

Az ElevenLabs (és a legtöbb SOTA TTS) **3 fő csúszkát** ad:

| Csúszka | Alacsony érték | Magas érték | Magyar use-case |
|---------|---------------|-------------|-----------------|
| **Stability** | Variancia, érzelem (0.3-0.5) | Konzisztens, "flat" (0.7+) | MOTHER-stílus → 0.85+, FATHER/JARVIS → 0.5-0.65 |
| **Similarity Boost** | Lazább, kreatívabb | Pontos clone (≥ 0.75) | Brand-voice cloning → 0.85+ |
| **Style Exaggeration** | Kevésbé dramatikus | Drámaibb intonáció | Audiobook → 0.4-0.6, asszisztens → 0.2-0.4 |

**Magyar mondatvégi süllyedés trükkje:** ha a Stability 0.7+ mellett is "kérdő" maradnak a mondatok, **növeld a Style Exaggeration**-t 0.5+-ig, és a mondat végére tegyél **dupla pontot** (`..`) — ez gyakran kikényszeríti a lezáró prozódiát.

## Mintázat 4 — HU-rich voice cloning

Ha saját brand-hangot akarsz építeni magyaron (PVC):

1. **Source-language match KÖTELEZŐ.** Angol mintából magyar kimenet → angol akcentus magyaron. Magyar hírolvasó / podcaster felvétel kell.
2. **30 perc – 3 óra clean WAV** (44.1 kHz, 16/24-bit, -16 LUFS, -1 dBTP, NO compression). Több nyelvű klónozásnál **nyelvenként 30-45 perc** az optimális.
3. **Training script** — fedje le a célzott hangi spektrumot: rövid+hosszú mondatok, kérdések, nyugodt+izgatott tónusok, brand-specifikus szakkifejezések, dátumok, számok.
4. **Vocal drift elkerülése:** 24-48 órás ablakon belül, ugyanazzal a mikrofonbeállítással.
5. **Voice-Captcha verification** (ElevenLabs PVC): a beszélőnek élőben kell felolvasnia egy generált szöveget — biometrikus consent-check.

Részletek: [[11-wiki/mfl-voice-tts-providers-comparison#Mintázat — voice-cloning workflow]].

## Anti-pattern — gyakori hibák

1. **Csak "Magyar" nyelvi flaget állítasz, semmi más** — a modell hozza az angolos prozódiát, mondatvégek lebegnek. Mindig text-prep + stability tuning kell.
2. **Idegen szavakat változatlanul hagysz** — "Next.js" → "nekszt dzsé esz" random. Magyarosítsd vagy IPA-zd.
3. **Sorszámokat számjegyként adsz át** — "1." → bizonytalan kiejtés. Mindig betűvel.
4. **Angol cloning-source magyar kimenetre** — produkciós minőséget elveszítettél. Source-nyelv mindig egyezzen a célnyelvvel (vagy multi-nyelvű dataset 30-45 perc/nyelv).
5. **Túl magas Stability long-form narrációhoz** — 0.9+ → monoton, fárasztó. Audiobook-hoz 0.5-0.6 ideális, mondatvégi süllyedést Style csúszkával kompenzáld.
6. **Code-switching audit nélkül publikálsz** — listen-test KÖTELEZŐ minden technikai szakszó-átmeneten.

## Reusable — magyar TTS audit-checklista

Mielőtt egy magyar TTS-anyagot publikálsz:

- [ ] **Mondatvégi intonáció** — az utolsó 3-5 hang süllyed-e? Ha nem, `..` vagy magasabb Style.
- [ ] **Kódváltási pontok** — minden angol szó listen-test (random sample).
- [ ] **Sorszámok / dátumok** — egyik se maradt számjegyként?
- [ ] **Betűszavak** — brand-rövidítések ejtése konzisztens-e?
- [ ] **Hosszú összetett mondatok** — nincs "lemaradás" / "siettetés"?
- [ ] **Hangrend** — `-ban/-ben`, `-ról/-ről` váltakozása helyes?
- [ ] **Stability** — adott use-case-hez illik (monoton vs. kifejező)?
- [ ] **Source-language match** — clone esetén HU source?

## Per-voice magyar megjegyzések (ElevenLabs library)

[[10-raw/mfl-research-2026-05-15/HU_VOICE-Q5#5 Szakasz Konkrét per-voice review]] alapján:

- **Rachel** — meleg, reklámhoz JÓ, hosszú narrációra fárasztó (túl lelkes)
- **Lily** — nyugodt, lassú, mesekönyv / dokumentumfilm JÓ
- **Chris** — mély, magyarul a `r`/`l` pöszének hathat
- **Laura** — stabil hírolvasó stílus, corporate / e-learning JÓ
- **Adam** — legtermészetesebb HU férfihang, podcast/YT JÓ, code-switching gyenge
- **Voice Design generated** — animáció karakterhangok küzdenek `gy/ty/ny`-kal

## Kapcsolódó

- [[11-wiki/mfl-voice-tts-providers-comparison]] — engine-választó mátrix
- [[11-wiki/voice-agent-architecture-patterns]] — STT + LLM + TTS stack
- [[11-wiki/jarvis-persona-design-spec]] — persona-tervezés a hangon
- [[11-wiki/hungarian-fuzzy-search]] — accent-map + ragozás-tolerancia (kapcsolódó HU-nlp wiki)
- [[11-wiki/gemini-3-1-flash-tts-pipeline]] — Gemini-specifikus magyar TTS implementáció
- [[11-wiki/mfl-voice-jarvis-mother-research]] — master research desztillátum
