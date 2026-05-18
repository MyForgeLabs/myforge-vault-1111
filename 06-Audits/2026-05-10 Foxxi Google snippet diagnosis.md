---
name: Foxxi Google organikus snippet diagnózis (2026-05-10)
type: audit
project: foxxi
created: 2026-05-10
tags: ["#type/audit", "#project/foxxi", "#seo"]
---

# Foxxi — Google organikus snippet diagnózis

> **Domi 2026-03-31 email-panasz**: a Google organikusan furcsa szövegeket hoz ki a example-foxxi.local-ról, pl. "Magyar D. egy pácienssel konzultál...". WP admin felületen nem találja ezeket meta-leírásként.

## Diagnózis: a forrás **alt-text** mezőkben van

A `_wp_attachment_image_alt` mezőkben **130+ karakter hosszú, mondat-jellegű alt-text-ek** vannak több képnél. Ha a Yoast meta-description túl rövid vagy a kulcskifejezésre nem illeszkedik, a Google **átveszi az alt-text-et** és abból kreál snippet-et.

**Kulcs-bizonyíték**: az ID 1085 attachment alt-text-je pontosan az amit Domi panaszolt:
> "A Foxxi fogszabályozó-szakorvosa, dr. Magyar Dominika egy pácienssel konzultál"

## Top problémás alt-textek (>120 karakter)

| Att-ID | Hossz | Alt-text (eleje) |
|---|---|---|
| 1091 | 143 | "madárarc esetén az alsó állcsont mérete elmarad a felsőétől, emiatt jellegzetes,..." |
| 1090 | 142 | "madárarc esetén az alsó állcsont mérete elmarad a felsőétől, a képen jól látható..." |
| 1062 | 135 | "a Foxxi két fogszabályozó szakorvosa, dr. Magyar Dominika és dr. Pulay Zoltán sz..." |
| 1063 | 135 | (duplikát 1062) |
| 1087 | 133 | "a Foxxi fogszabályozó-szakorvosai, dr. Magyar Dominika és dr. Pulay Zoltán a min..." |
| 1009 | 130 | "AFoxxi fogszabályozó-szakorvosa, dr. Pulay Zoltán egy műtéti fogszabályozásra vá..." |
| 1031 | 120 | "felnőttkorban a láthatatlan fogszabályozók, mint pl. az Invisalign diszkrét fogs..." |
| 1108 | 120 | "A gyermekkori fogszabályozás fontossága, időben kell elkezdeni a kezlést, ne hal..." |
| 1082 | 118 | "páciens fogászati fotóján jól látható a nyitott harapás, rés van a bal alsó és b..." |
| 1051 | 118 | "A digitális fogszabályozás középpontját jelentő 3D scannerrel gyorsabb, precízeb..." |

**Plus**: 1085–1093 között további hasonló stílusú "dr. Magyar Dominika ..." prefixű alt-textek.

## Best-practice szabályok (alt-text)

- **<125 karakter** (screen-reader és Google-snippet-friendly)
- **frázis** legyen, NE mondat (pl. "Dr. Magyar Dominika fogszabályozó szakorvos" ✅, "A Foxxi fogszabályozó-szakorvosa Dr. Magyar Dominika egy pácienssel konzultál" ❌)
- **Ne ismételje** a környező body-szöveget
- **Kulcsszó** természetesen legyen benne, de NE keyword-stuffing

## Javasolt akció (Domi-confirm-mel)

### Fázis 1: Top 30 leghosszabb alt-text rövidítése (~30 perc)

Fenti táblázat ID-it bulk-update-eljük 60-90 karakter közé, frázis-jelleggel:

| Régi (143 char) | Új (~70 char) |
|---|---|
| "A Foxxi fogszabályozó-szakorvosa, dr. Magyar Dominika egy pácienssel konzultál" | "Dr. Magyar Dominika fogszabályozó konzultációt tart" |
| "madárarc esetén az alsó állcsont mérete elmarad a felsőétől, emiatt jellegzetes profil-eltolódás" | "Madárarc — alsó állcsont eltolódás profil-nézetből" |
| "a Foxxi két fogszabályozó szakorvosa, dr. Magyar Dominika és dr. Pulay Zoltán szívet formál" | "Dr. Magyar Dominika és Dr. Pulay Zoltán szívet formál" |

### Fázis 2: Yoast meta-description erősítés

Minden főoldalon ellenőrizzük hogy:
- A meta-description **130-160 karakter** (Google snippet-mérete)
- Tartalmaz **fő-kulcsszót** (pl. "Foxxi fogszabályozó", "Foxxi Fogászati Klinika", "Széll Kálmán")
- **Cselekvésre buzdít** ("Foglalj időpontot", "Tudd meg")

A Phase 14-es Yoast-átnevezésnél (Centrum→Klinika) már átnéztem — a meta-description-ek többsége OK, csak néhány page-en gyanús (lásd az alt-text-eket).

## Implementáció

Bulk-update WP-CLI script — `_wp_attachment_image_alt` mezőkre. Backup minden módosítás előtt (`_wp_attachment_image_alt_backup_<ts>`).

**Domi-jóváhagyás kell**: a tartalmi rövidítések szakmai-pontosságát Domi-nak kell ellenőriznie a 30 alt-text listán.

## Nyitva-marad: a example-foxxi.local (éles) is érintett

A panasz a example-foxxi.local organikus snippet-jére vonatkozott — az **Apache-on fut** (NEM Hostinger LiteSpeed), ott külön ssh-elérés szükséges. A staging-fix után az élesre is áttranszferáljuk az alt-text-rövidítést (XML-export vagy DB-szinkron).

## Kapcsolódó

- [[02-Projects/foxxi]]
- [[02-Projects/foxxi-email-arhivum]] — 2026-03-31-i Domi-panasz
- [[02-Projects/foxxi-sprint-2026-05/foxxi-uzenet-2026-05-10-osszefoglalo]]
