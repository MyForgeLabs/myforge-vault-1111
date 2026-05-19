---
name: excel-redmark-3way-diff-workflow
description: Excel-csere katalógus-frissítés flow — piros-font detekció openpyxl-lel + 3-way diff (új xlsx ↔ régi xlsx ↔ json) + SQL gen + Zsuzsi/Zoli-stílusú kérdés-doc
type: wiki
tags: ["#type/reference", "#project/kgc-berles", "#project/foxxi"]
created: 2026-05-11
updated: 2026-05-19
tag_backfill: 2026-05-19
---
# Excel-csere katalógus-frissítés flow

## Mikor

A user/ügyfél új Excel-fájlt küld termék-katalógus frissítéssel, **pirossal jelölve a változtatásokat**. Tipikus eset KGC-berles (Zsuzsi+Zoli árlistái) — de bármely Excel-source katalógusra alkalmazható (Foxxi árlistája, kgc-marketing termék-tár, MAPESZ klubok stb.).

## A flow

### 1. Piros-cella detekció — `openpyxl`

```python
import openpyxl
wb = openpyxl.load_workbook(file)  # NOT data_only=True — formatting kell
ws = wb.active

def is_red(cell):
    fc = cell.font.color
    return fc and fc.type == 'rgb' and fc.rgb == 'FFFF0000'
```

**Piros-szabály:** Excel default piros font = `FFFF0000`. Plus `FFCC0000`, `FFB30000` ritka variánsok. **Theme-color** (`theme:1`, `theme:10`) = default szöveg, NEM piros.

**Sor-osztályozás:**
- **Egész sor piros** (összes kulcs-cella piros) → új entry (új termék)
- **Csak ár-cella piros** → ár-változás
- **Csak deposit/kaució piros** → kauciósz-változás

### 2. 3-way diff (KRITIKUS)

NEM elég csak az új xlsx + json összevetése. **3 forrást** kell hasonlítani:

| Forrás | Mit jelez |
|---|---|
| Új xlsx (most kapott) | Mit AKART a user a frissítésben |
| Régi xlsx (előző kör) | Mit JELZETT a user a baseline-ban |
| `machines.json` (jelenlegi DB-baseline) | Mit IMPORTÁLTUNK |

**3 fontos eset:**

- **Új xlsx piros + json eltér** = szándékos változás, alkalmazd
- **Új xlsx NEM piros + régi xlsx EGYEZIK új xlsx-szel + json eltér** = silent data-bug a json-ban (rossz régi import), CSENDESEN javítható
- **Új xlsx NEM piros + régi xlsx ELTÉR új xlsx-től + json EGYEZIK régi xlsx-szel** = a user ELFELEJTETTE pirosra festeni az új változást → **ASK a usernél**

KGC-berles 2026-05-11 példa:
- `ABV 1` 12500 → 12000 (nem piros), de a régi xlsx is 12000 volt → silent data-fix
- `FN 19-24` deposit 0 → 30000 (nem piros), de mindkét xlsx 30000-et adott → silent data-fix
- 3 új gép piros-jel nélkül + nincs régi xlsx-ben → ASK (a user megerősítette: igen, vegyük fel)

### 3. SQL generálás (idempotens, transaction-ben)

Python-tól → `BEGIN; UPDATE ...; COMMIT;` minta:

```sql
BEGIN;
DELETE FROM "MachineCategory" WHERE "machineId" IN (...);
DELETE FROM "MachineAccessory" WHERE "baseMachineId" IN (...) OR "accessoryId" IN (...);
DELETE FROM "Machine" WHERE id IN (...);

UPDATE "Machine" SET "dailyPrice" = 12000 WHERE id = 'ABV 1';
-- N+121 sor

COMMIT;
```

Külön scriptként mert a Prisma `seed.ts` `upsert.update`-je admin-edit-védelem miatt csak flag-mezőket szinkronizál (lásd [[prisma-seed-admin-edit-protected]]).

### 4. Új gépek felvétele

Két lépcsős:
1. `data.seed/machines.json` baseline-frissítés (append-elés, kategória + alias)
2. `pnpm db:seed` futtatás — az `upsert.create` ág felveszi az új ID-kat, plus `MachineAccessory.deleteMany + recreate` és `MachineCategory.deleteMany + recreate` újraépíti a kapcsolatokat

### 5. Hiányos mező-pótlás (új gépek)

Új gépeknek gyakran HIÁNYZIK: `transport`, `extras`, `deposit`, `description`, `imageUrl`. Két stratégia:

- **Auto-fill hasonló gép alapján** — keress azonos `category/subcategory` legkisebb-távolságú ID-t (pl. `BCS 9 → BCS 10`, `UH 106/107 → UH 111`). Másolj transport/extras-t, deposit-ot is feltevésnek
- **Description sablon** — kézi prompt (gép-név + bullet-paraméterek), 180-230 char tipikus

### 6. Zsuzsi-Zoli stílusú kérdés-doc

Auto-fill **feltevéseket** (különösen deposit-ra) kérdés-doc-ba szervezz a megrendelőnek. Minta szekciók:

1. **Hiányzó értékek megerősítés** — táblázat: új-gép | feltevés | hasonló-gép-forrás
2. **Termékfotó kérés** — mely új gépekhez kell fotó (most kategória-fallback megy)
3. **Architektúra-döntés megerősítés** — pl. tartozék-átszervezés (régi 3 KF törlés, új 9 MAG-koronafúró cseréje)
4. **Törlések megerősítés** — pl. duplikátum-szanálás (UH 105 = UH 104 duplikátum)
5. **Silent fix-ek megerősítés** — adat-bug-javítások (`0 → 30000` deposit-fix a `machines.json`-ban)

Fájl tipikus helye: `docs/<dátum>-<topic>/zsuzsi-zoli-kerdesek.md` (`docs/2026-05-11-bergep-frissites/zsuzsi-zoli-kerdesek.md` minta).

### 7. Verify

- `/api/<entity>` count + ID-check (új gépek megjelennek, törölt 404 vagy lista-eltűnés)
- Sitemap URL-count regenerálva (új gépek bekerültek, accessory-k kihagyva)
- Kategória-landing oldalak (új gépek a megfelelő L3 listában)
- Spot-check 5-6 ár-update random ID-n
- Service `systemctl status` + log clean

## Reusability

- **KGC-berles** (this implementation) — 2026-05-11
- **Foxxi-services** — ha ACF-ből Excel-export migráció jön
- **kgc-marketing** — termék-tár ha Excel-vezérelt lesz
- **Bluebird-shop** — termékár-frissítések ha Zsuzsi/Zoli-tól jönnek

## Anti-pattern

- ❌ Csak az új xlsx-et nézni (silent data-fix-ek elsiklanak)
- ❌ `notFound` page nélkül törölt entity-re (Next.js client-render visszahívás 200 OK fals 404-szöveggel)
- ❌ `data.seed/<json>` és DB direct apply szétcsúsztatva — későbbi `pnpm db:seed` újra-importál, vissza-rontja
- ❌ Auto-fill deposit-ra megerősítés-doc nélkül

## Kapcsolódó

- [[prisma-seed-admin-edit-protected]] — miért kell külön SQL data-update
- [[02-Projects/kgc-berles#Bérgépek 2.xlsx — Zsuzsi katalógus-update]] — első élő alkalmazás
- [[08-Sessions/2026-05-11-kgc-weboldal]] — implementáció + tanulságok
- NBSP-gotcha: `Bérgépek 2.xlsx` fájlnévben NBSP elrejti az `ls`-t → `glob('B*rg*pek*.xlsx')` használandó
