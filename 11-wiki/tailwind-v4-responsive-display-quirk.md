---
name: Tailwind v4 + Next 16 Turbopack — responsive display-utility quirk
type: wiki
created: 2026-05-21
updated: 2026-05-21
tags: [wiki, tailwind, nextjs, css-quirk, "#tech/tailwind"]
related: [nextjs-16-middleware-rename-proxy, kgc-berles]
---

# Tailwind v4 + Next 16 Turbopack — `hidden xl:inline-flex` quirk

## A bug

`<a className="hidden xl:inline-flex">Ajánlatkérés</a>` — várt viselkedés: `xl:` (≥1280 px) alatt `display: none`, fölött `display: inline-flex`.

**Tényleges viselkedés**: a `xl:inline-flex` szabály **media-query NÉLKÜL** generálódik a build-be, és **CSS source-order miatt mindig felülírja a `hidden`-t**. Eredmény: az elem mindig `display: flex`, akkor is amikor `<1280 px` viewport-on vagyunk.

## Reprodukció

1. Next.js 16.x + Tailwind v4 + Turbopack
2. Bármely elem: `className="hidden xl:inline-flex"`
3. Resize browser-t 1100 px-re
4. DevTools → Computed → `display: flex` (várt: `display: none`)
5. `getBoundingClientRect()` ad méreteket (várt: 0×0)

## Diagnosztika

A `.next/static/chunks/*.css`-ben grep-pelve:
```css
.hidden{display:none}
...
xl\:inline-flex{display:inline-flex}   /* ← NINCS @media (min-width: 1280px) wrapper! */
```

Várt minta lenne:
```css
@media (min-width: 1280px) {
  .xl\:inline-flex{display:inline-flex}
}
```

## Workaround-ok

| Megoldás | Mikor jó |
|---|---|
| **Töröld a duplikáló elemet** | Ha más helyen is van (pl. megamenu + NAV) — a legtisztább |
| **Conditional render** `{useWindowSize() > 1280 && <X />}` | Client-componentben, ha tényleg viewport-feltétel kell |
| **Arbitrary class** `[@media(min-width:1280px)]:inline-flex` | Bypass-olja a Tailwind-generálást, közvetlenül media-query CSS |
| **`!important`** `xl:!inline-flex` | Nem segít — a `hidden` nyer akkor is, mert source-order |

## Másik trap NE keverd

Tailwind v4-ben az `xl:hidden xl:inline-flex` (mindkettő `xl:` prefix) — utóbbi mindig nyer. Ez **váróan** működik (cascade source-order).

A jelen bug az hogy az `xl:`-prefix és a **non-prefixed** class között az utóbbi (`hidden`) elhalványul a non-media-query-wrapped `xl:`-class miatt.

## Bug-státusz

Tailwind v4 + Next 16 Turbopack-specifikus. Lehet Tailwind, Next, vagy Turbopack-bug — nem azonosítottam upstream-issue-t (2026-05-21). PostCSS-buildben (Next 15 + Turbopack-disabled) NEM jelentkezik.

## Hivatkozott példa

[kgc-berles Header.tsx](../02-Projects/kgc-berles.md) 2026-05-21 — az "Ajánlatkérés" gomb `hidden xl:inline-flex`-szel próbált csak desktop-on megjelenni, de minden viewport-on látszott + overflow-t okozott. **Megoldás**: gomb törlése (redundáns, a megamenu+NAV lefedi).

## Kapcsolódó

- [[nextjs-16-middleware-rename-proxy]] — másik Next 16 breaking change
- Session: [[../08-Sessions/2026-05-21-kgc-weboldal]]
