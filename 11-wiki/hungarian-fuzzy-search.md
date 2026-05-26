---
name: Magyar fuzzy search algoritmus
description: Accent-toleráns + typo-toleráns string-matcher magyar input-hoz, Fuse.js nélkül — accent-strip map + per-token Levenshtein 1-2 + score
type: wiki
created: 2026-05-08
updated: 2026-05-08
tags: ["#topic/search", "#topic/algoritmus", "#lang/hungarian"]
---

# Magyar fuzzy search algoritmus

## Mit tud

- **Accent-toleráns**: `véső` ≡ `vesogep` ≡ `VÉSŐ` ≡ `vesõ`
- **Typo-toleráns** 1-2 karakter elgépelésre: `bosch` ↔ `bosh` ↔ `bsoch`
- **Részleges-toleráns**: `furo` találat fúrógép-re és fúrókalapács-ra is
- **Token-szintű** match: "bosch véső" külön kulcsszó, mindkettőnek illeszkednie kell a target-be
- **Score-alapú** sortolás, nincs binary match/no-match
- **Zero deps** — nincs Fuse.js, nincs MiniSearch, csak egy 200-soros TS modul

## Mikor érdemes

- **300-3000 elemű** in-memory dataset (Client-A: 292 gép, ~1ms / query / elem)
- Magyar input — angol-csak app-ra Fuse.js-default `extended search` is OK
- Kategória-fa is ott van — egy hívásból kétféle output (gép + kategória)

Ennél nagyobbra: Postgres `pg_trgm` + `unaccent`, vagy Meilisearch/Typesense.

## Algoritmus

### 1. Accent-strip + lowercase normalize

```ts
const ACCENTS_MAP: Record<string, string> = {
  á: "a", é: "e", í: "i", ó: "o", ö: "o", ő: "o",
  ú: "u", ü: "u", ű: "u",
  Á: "a", É: "e", Í: "i", Ó: "o", Ö: "o", Ő: "o",
  Ú: "u", Ü: "u", Ű: "u",
}

function normalize(s: string): string {
  let out = ""
  for (const ch of s) out += ACCENTS_MAP[ch] ?? ch.toLowerCase()
  return out
}
```

> A `String.prototype.normalize('NFD').replace(/[̀-ͯ]/g, '')` is megy, de a magyar `ő/ű` Unicode-pontok bonyolultabbak (két lehetséges decompozíció böngésző-fontonként). A statikus map robusztusabb.

### 2. Levenshtein DP (két sor optimalizálva)

```ts
function levenshtein(a: string, b: string): number {
  if (a === b) return 0
  if (!a.length) return b.length
  if (!b.length) return a.length
  const m = a.length, n = b.length
  const prev = new Array<number>(n + 1)
  for (let j = 0; j <= n; j++) prev[j] = j
  for (let i = 1; i <= m; i++) {
    let curr = i
    let prevDiag = prev[0]
    prev[0] = i
    for (let j = 1; j <= n; j++) {
      const tmp = prev[j]
      curr = Math.min(
        prev[j] + 1,                                 // deletion
        prev[j - 1] + 1,                             // insertion
        prevDiag + (a[i - 1] === b[j - 1] ? 0 : 1)   // substitution
      )
      prevDiag = tmp
      prev[j] = curr
    }
  }
  return prev[n]
}
```

### 3. Score-match per token

```ts
function scoreMatch(target: string, query: string): number {
  // target+query már normalizált (no-accent, lowercase)
  const tokens = query.split(/\s+/).filter(Boolean)
  if (tokens.length === 0) return Infinity

  let totalScore = 0
  for (const tok of tokens) {
    // 1. Exact substring → 0 (vagy 1 ha NEM szó-elején van)
    if (target.includes(tok)) {
      const at = target.indexOf(tok)
      const isStartOfWord = at === 0 || target[at - 1] === " " || target[at - 1] === "-"
      totalScore += isStartOfWord ? 0 : 1
      continue
    }
    // 2. Fuzzy: legjobb Levenshtein a target szavain (csak ha hossz közel ±2)
    const targetWords = target.split(/[\s/]+/)
    let bestLev = Infinity
    for (const tw of targetWords) {
      if (tw.length < 3) continue
      if (Math.abs(tw.length - tok.length) > 2) continue
      bestLev = Math.min(bestLev, levenshtein(tw, tok))
    }
    if (bestLev === 1) totalScore += 5
    else if (bestLev === 2) totalScore += 12
    else return Infinity   // egyik token-re sincs match → skip
  }
  // tie-breaker: rövidebb target preferált
  return totalScore + Math.min(target.length / 100, 0.5)
}
```

### 4. Használat (Next.js API endpoint)

```ts
const nq = normalize(q)
const scored = items
  .map((m) => ({ m, score: scoreMatch(normalize(`${m.name} ${m.path}`), nq) }))
  .filter((x) => x.score < Infinity)
  .sort((a, b) => a.score - b.score)
  .slice(0, 8)
```

## Score-tábla

| Forgatókönyv | Score | Példa (query → target) |
|---|---|---|
| Exact word-prefix | 0 | `bosch` → `Bosch GBH 5-40` |
| Exact substring (mid-word) | 1 | `kasza` → `motoros fűkasza` |
| Lev=1 (1 typo) | 5 | `bosh` → `bosch` |
| Lev=2 (2 typo) | 12 | `vsogep` → `vesogep` |
| No match | ∞ | (skip) |

Tie-breaker: minél rövidebb a target (`+ length/100, max 0.5`), annál előbb (a "Bosch GBH 5-40" legyen az "Áramfejlesztő Bosch tartozék"-nál előrébb).

## Limitációk

- **Cyrillic / sajátos karakter** nincs az `ACCENTS_MAP`-ban — bővíthető
- **Stemming nincs** (`fűnyíró` ≠ `fűnyírók` ≠ `fűnyírást`) — magyarra ragozós nyelven nehéz; ha kell: `magyarspeller`-rel post-process
- **Phonetic match nincs** (`czé` vs `cé`) — Soundex magyarra rossz, jobb manuális szabályok
- **Per-elem 1ms** ~3000 elem felett már észrevehető — ott `Worker`-be vagy szerver-szintű `pg_trgm`

## Reusable importálás

A `kgc-berles/app/api/search/route.ts` self-contained — emelhető `lib/fuzzy-hu.ts`-be: 3 export (`normalize`, `levenshtein`, `scoreMatch`). Client-B keresőhöz, teszt.eu instrumentum-keresőhöz is jó.

## Forrás

- Implementáció: `/root/projektjeim/Client-A-ALL/kgc-berles/app/api/search/route.ts`
- Session: [[08-Sessions/2026-05-06-kgc-weboldal]]
- Validation: `curl -s 'http://localhost:3004/api/search?q=véső|vesogep|bosh'` mindhárom releváns hit-tel tér vissza
