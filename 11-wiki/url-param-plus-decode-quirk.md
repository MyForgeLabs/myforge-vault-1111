---
name: URL-param `+` decodes to space, allow-list silently falls back
type: wiki
tags: [wiki, url, gotcha, querystring]
created: 2026-05-11
updated: 2026-05-11
---

# URL-paraméter `+` → space — csendben elveszett filter-érték

## A tünet

Filter-chip URL-state-ben: `?age=50+`. A frontend chip-re kattintva minden rendben (UI mutatja "50+"), de **valaki más-akit elküldöd a sharelinket** vagy aki **manuálisan curl-eli** az URL-t — a filter "nem szűr".

```
$ curl /admin?age=50+
→ totalN=44 (of 44)        # nincs filter
$ curl /admin?age=50%2B    # URL-encoded
→ totalN=26 (of 44)        # filter működik
```

## Miért

A query-string parser a **`+` jelet space-re dekódolja** (a `application/x-www-form-urlencoded` örökség). Tehát:

- `?age=50+` → query-paramban `age = "50 "` (space-szel)
- A server-side allow-list (`['<30', '30-49', '50+']`) **csendben "50+"-ra** nem matchelt → fallback `'all'` → nincs szűrés

A frontend (`URLSearchParams.set('age', '50+')`) automatikusan URL-encode-olja, ezért manuális share-link a fájdalompont, NEM a UI.

## Megoldások

### A) Kerüld a `+` és ` ` karaktert a filter-értékben

Egyszerűbb hosszú távon: ha a filter-chip belső értéke `50plus` vagy `over50`, az URL tiszta marad. UI-on a label-t magyaríthatod ("50+").

### B) Ha mégis kell `+`, explicit encode a manual-share-link generátorban

```ts
const link = `https://example.com/admin?age=${encodeURIComponent('50+')}`;
// → ?age=50%2B
```

### C) Server-side dual-allow-list

Az allow-list támogasson space-t is ekvivalensként:

```ts
const normalized = value.trim().replace(/ /g, '+');
if (allowed.includes(normalized)) return normalized;
```

Csak akkor, ha biztosan vissza akarod kompatibilitást a régi manual-share-linkekre.

## Detektálás

Ha a UI-chip működik **de** a manual URL nem, mindig kérdezd: a chip URL-állít össze, vagy egy kívülről beillesztett URL-t parsel? Ha az utóbbi, **futtass egy `decodeURIComponent`-et arra a mezőre** és nézd meg space-t. A space → ez az.

## Példa a kódban

Kinda projekt 2026-05-11-es Phase 2 (commit `b477a74`): az `age=50+` filter manual curl-tesztben "44/44" eredményt adott, csak `age=50%2B`-vel jött vissza a várt "26/44". A frontend chip viszont rendben volt. → érték-rename későbbi sprintben.

## Kapcsolódó

- [[11-wiki/nextjs-search-params-force-dynamic]] — `useSearchParams` allokáció
- [[02-Projects/teszt-eu]] — globális szűrők Phase 2
