---
name: gray-matter — Date object coerce gotcha
type: wiki
created: 2026-05-08
updated: 2026-05-08
tags: ["#type/wiki", "frontmatter", "react", "nextjs"]
---

# gray-matter Date object coerce gotcha

## A hiba

```
Error: Objects are not valid as a React child (found: [object Date]).
```

YAML frontmatter-ben datum-szerű értékek (`created: 2026-04-23`) automatikusan **JS Date objektumra** parse-olnak gray-matter-ben — nem string-re. JSX-be renderelve crash.

## Hibás kód

```tsx
import matter from "gray-matter"

const { data } = matter(raw)
const created = data.created as string | undefined  // ← typecast LIES, ez Date
return <div>{created}</div>  // ← crash: "Objects are not valid as a React child"
```

A `as string` cast **runtime-ban semmit nem csinál** — TypeScript "trust me, bro", de a Date objektum tényleg ott van.

## Jó megoldás

Always-coerce util:

```tsx
function dateStr(v: unknown): string {
  if (!v) return ""
  if (v instanceof Date) return v.toISOString().slice(0, 10)
  return String(v)
}

const created = dateStr(data.created)
const updated = dateStr(data.updated)
return <div>created {created} · updated {updated}</div>
```

## Mely YAML-mezők lesznek Date

A YAML 1.2 spec szerint bármi ami `YYYY-MM-DD` vagy `YYYY-MM-DD HH:MM:SS` formátumban van → Date. A gray-matter ezt nem konfigurálható, mert a `js-yaml`-tól örökli. Tipikus mezők:
- `created`, `updated`, `due`
- ISO date-stringek `'...'` aposztróffal lennének mentve string-ként, de jellemzően nem így írjuk

## Megelőzés

1. Definiálj egy `frontmatter()` helper-t ami minden mezőt String-coerce-el
2. TypeScript-ben az frontmatter típusát `Record<string, unknown>` legyen, ne `Record<string, string>`
3. `String(...)` és `instanceof Date` check minden render-pontnál

## Kapcsolódó

- [[07-Decisions/2026-05-08 Myforge OS Wave A-K dashboard expansion]]
