---
name: KGC-Bérlés üzleti szabályok v1
type: decision
tags: [kgc-berles, pricing, business-rules, decision]
created: 2026-04-24
updated: 2026-04-24
project: kgc-berles
---

# KGC-Bérlés üzleti szabályok v1

> [!info] Forrás
> Peti szóbeli átadása 2026-04-24 walkthrough-ján. Ezek a **kanonikus üzleti szabályok** — a `lib/rental-pricing.ts` motornak ezt kell megvalósítania. Ha a kód eltér, a kód a hibás.

## 1. Napi bérlés alapértelmezett

- Átvétel X óra → **másnap X óra** a visszahozás = **1 nap**
- N-edik nap X órakor vissza → N nap

## 2. Fél nap szabály

- Fél nap = **maximum 5 óra** bérlés (ezen belül fix 50% napi díj)
- **Állítható** settings kulcs: `halfDayMaxHours: 5` (default)
- Egy napos fél napos bérlés UI-ban checkbox-ol választható

## 3. Aznapi átvétel korlát

- Aznapra foglalni csak **max 15:00-ig** lehet
- Későbbi időpont nem választható aznapra
- **Állítható** settings kulcs: `sameDayLatestPickupHour: 15` (default)

## 4. Reggeli visszahozás szabály

- **Reggel 7:00 előtt nincs visszahozás** (üzlet zárva)
- Ha valaki 15:00-kor elviszi és másnap 7:00-kor vissza = **fél nap** (nem teljes nap)
- Működés: ha a visszahozási óra `<= earliestReturnHour`, az utolsó nap **fél napnak** számít (nem teljesnek)
- **Állítható** settings kulcs: `earliestReturnHour: 7` (default)

## 5. Zárva napok

- Alapértelmezés: **csak vasárnap** zárva (`closedDays: [0]`)
- Rövid (< 7 napos) bérlésnél zárva nap = fél nap (`closedDayBilling: "halfDay"`)
- 7+ napos bérlésnél tier aktív — lásd 6.

## 6. Kedvezmény sávok (tier)

**Régi → új:**
| Minimum nap | Ajándéknap |
|-------------|------------|
| 7+ (1 hét)  | **1 nap**  |
| 14+ (2 hét) | **2 nap**  |
| 21+ (3 hét) | **4 nap**  |
| 28+ (4 hét) | **8 nap** (MAX — ezen felül nem nő) |

- Mind **állítható** settings-ben
- Az **ajándéknap mindig az utolsó** nap (last-day-free policy)
- **Tier aktív esetén a fél / zárva / ünnep nap TELJES ÁRON** számít be (a kedvezmény az ajándéknap, nem a zárva-nap-fél-díj)
- Indoklás: 7 napos H→V esetében a 6 munkanap + 1 vasárnap = fizet 6 napot; a vasárnap "ingyen" mert az az utolsó

## 7. Órás bérlés — **törlendő**

- A `hourlyEnabled / hourlyRate / hourlyMinHours / hourlyMaxHours` settings-et **kiszedjük**
- Csak fél nap / teljes nap van
- `lib/rental-pricing.ts` hourly ág törlendő
- Admin UI: hourly szekció eltávolítandó
- Frontend (DetailBookingCard, BookingModal): hourly opció eltávolítandó

## 8. Kaució fizetés

- **Most:** helyszíni fizetés (kp/kártya a boltban)
- **Betervezve:** kártyás előengedélyezés (SimplePay / Barion / Stripe) — külön feature, nem most
- A `calculateRentalPrice()` a `total = rentalCost + deposit`-et adja vissza, a fizetés maga a `/api/book` körén kívül

## 9. Foglalt gép láthatóság

- Aktív bérlésben lévő gép **NE legyen látható** a frontenden (sem listában, sem detail oldalon) amíg vissza nem vették
- A `bookings.json` státusz: `active` (átvett, még nem visszahozta) → gép ID-re tiltás a `/berles`, `/machine/[id]`-n
- `confirmed` (jóváhagyott foglalás, még nem vette át) → a foglalt időszakra naptárban nem választható, de gép oldala látszik

## Settings séma változások

### Hozzáadandó kulcsok
```json
{
  "halfDayMaxHours": 5,
  "sameDayLatestPickupHour": 15,
  "earliestReturnHour": 7
}
```

### Eltávolítandó kulcsok
```json
{
  "hourlyEnabled": ...,
  "hourlyRate": ...,
  "hourlyMinHours": ...,
  "hourlyMaxHours": ...
}
```

### Módosítandó kulcsok
```json
{
  "discountTiers": [
    { "minDays": 7,  "freeDays": 1, "label": "1 hét — 1 nap ajándék" },
    { "minDays": 14, "freeDays": 2, "label": "2 hét — 2 nap ajándék" },
    { "minDays": 21, "freeDays": 4, "label": "3 hét — 4 nap ajándék" },
    { "minDays": 28, "freeDays": 8, "label": "4 hét — 8 nap ajándék (max)" }
  ]
}
```

## Kódváltoztatások ahova érinteni kell

| Fájl | Mit |
|------|-----|
| `lib/rental-settings.ts` | `RentalSettings` type — új kulcsok hozzá, hourly-k el + DEFAULT_SETTINGS update |
| `lib/rental-pricing.ts` | hourly ág törlése, early-return half-day szabály, halfDayMaxHours validáció |
| `data/rental-settings.json` + `data.seed/rental-settings.json` | új baseline |
| `app/admin/(app)/settings/SettingsEditor.tsx` | Hourly szekció törlés, új 3 input (half day max h, same-day latest h, earliest return h) |
| `components/shared/DetailBookingCard.tsx` | Hourly opció törlés, return hour validáció `>= 7` |
| `components/shared/BookingModal.tsx` | Hourly törlés |
| `app/berles/page.tsx` + `app/machine/[id]/page.tsx` | Aktív bérléses gép hide filter |
| `lib/types.ts` | `BookingRequest` hourly mezők törlése ha vannak |

## Kapcsolódó

- [[02-Projects/kgc-berles]]
- Session átadás: [docs/2026-04-21/session-osszefoglalo-kgc-berles.md](/root/projektjeim/KGC-ALL/docs/2026-04-21/session-osszefoglalo-kgc-berles.md)
