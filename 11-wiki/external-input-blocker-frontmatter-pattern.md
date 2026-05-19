---
name: External-input blocker frontmatter pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/workflow", "#topic/backlog", "#topic/consultancy", "pattern/blocked-by", "evergreen"]
status: stable
session-evidence: 10
first-seen: 2026-W17
---

# External-input blocker frontmatter pattern

> [!info] TL;DR
> A vault `04-Tasks/Backlog.md`-jében **15+ task** tag-elt `#domi-input` / `#mariann-input` / `#zsuzsi-zoli` formában — egyetlen, sebezhető szöveges konvenció arra, hogy „ez a task **külső személytől** vár inputot". A pattern jelenleg ad-hoc, nincs Dashboard-query, nincs „blocked-since" timer, nincs proaktív riasztás. Ez a wiki formalizálja a `blocked-by:` frontmatter-mezőt + Dashboard-query-t, hogy a hidden-blocked task-ok ne drift-eljenek el 11+ napon át.

## A probléma — drift bizonyíték

A Backlog.md-ben (2026-05-19 állapot, sample):

```
- [ ] Domi visual choice — Marcsi 20-SVG csomag (➕ 2026-05-10)   #foxxi #brand #domi-input
- [ ] Cookiebot CBID — Domi UUID-jét várjuk (➕ 2026-05-03)        #foxxi #domi-input
- [ ] Élesítési időpont (example-foxxi.local) — Domi-tól dátum kell (➕ 2026-05-10) #foxxi #domi-input
```

Ezek 9–16 napja várnak. A „➕ <date>" Tasks-plugin add-date — de **nincs `blocked-since:` szemantika**: nem látszik, mióta vár külső inputra (lehet, hogy 1 napja, lehet, hogy 16 napja).

Forrás: KO-DB [10499] Domi/Zozó admin-meghívó kérés (W17); [11873] Atti-blocked 4 task #1+#3+#6+#7 (W19); [10665], [10667] Zsuzsi+Zoli 14 questions in 5 areas (W18); MEMORY 2026-05-11 `zsuzsi-zoli kérdés-doc`.

## A javasolt frontmatter-konvenció

Tag-alapú jelölés helyett (vagy mellette), task-szintű **YAML frontmatter** ha külön task-fájl van — vagy emoji-mező + ISO-dátum a Backlog.md-sor végén:

```markdown
- [ ] **Cookiebot CBID setup** — Domi UUID kell ⏳ blocked-by:domi 2026-05-03 🔴 #foxxi #domi-input
```

Vagy strukturált formában (task-fájl per blocker, ha nagyobb):

```yaml
---
name: Cookiebot CBID setup
type: task
priority: high
blocked-by: Domi (UUID)
blocked-since: 2026-05-03
last-poll: 2026-05-15
status: blocked
tags: ["#type/task", "#blocked/external", "#foxxi"]
---
```

**Kulcs-mezők:**
- `blocked-by:` — ki vagy mi blokkolja (személy / külső szolgáltatás / 3rd-party API)
- `blocked-since:` — mikor lett blokkolva (ISO)
- `last-poll:` — utoljára mikor kérdeztük rá (proaktív emlékeztető)
- `status: blocked` — explicit status, NEM csak tag

## Dashboard-query (Dataview)

`04-Tasks/Dashboard.md`-be új szekció (Dataview vagy Bases):

````markdown
## Külső inputtól blokkolt task-ok (élő)

```dataview
TABLE
  blocked-by AS "Kitől",
  blocked-since AS "Mióta",
  (date(today) - date(blocked-since)).days + "d" AS "Drift",
  last-poll AS "Utolsó poll"
FROM "04-Tasks"
WHERE status = "blocked" OR contains(tags, "blocked/external")
SORT (date(today) - date(blocked-since)).days DESC
```
````

VAGY ha a Backlog.md sor-tag-eken kívánsz maradni — regexp-grep-pel:

```bash
# /usr/local/bin/vault-blocked-report (heti cron)
grep -nE "blocked-by:\w+ \d{4}-\d{2}-\d{2}" /root/obsidian-vault/04-Tasks/Backlog.md
```

## Proaktív poll-emlékeztető

Heti audit-script:

```bash
# weekly-blocked-poll-reminder.sh
today=$(date +%s)
grep -nE "blocked-since:(\d{4}-\d{2}-\d{2})" /root/obsidian-vault/04-Tasks/Backlog.md | \
while read -r line; do
  bsince=$(echo "$line" | grep -oP "\d{4}-\d{2}-\d{2}")
  days=$(( (today - $(date -d "$bsince" +%s)) / 86400 ))
  if [[ $days -gt 7 ]]; then
    echo "POLL REMINDER: $line — blocked $days days ago"
  fi
done
```

7-napos drift-küszöb felett → emlékeztető a `01-Daily/<today>.md`-be:

```markdown
## Külső poll javasolt (3 task)
- 16 napja: Cookiebot CBID — Domi UUID (Foxxi)
- 12 napja: GA4 Enhanced Conversions — admin-meghívó (Zozó)
- 9 napja: Élesítési időpont — Domi (Foxxi)
```

## Anti-pattern: hidden-blocked

| Anti-pattern | Probléma |
|---|---|
| Csak `#domi-input` tag, dátum-mező nélkül | „mióta?" kérdés-re nincs válasz |
| „Vár Domi visszajelzésére" comment-ben | nem grep-elhető, nem audit-álható |
| Task-status = `open` ha valójában `blocked` | priority-sort téves, work-queue zavaros |
| Manual poll-emlékeztető fejből | drift 11-16 nap (lásd Foxxi-példák) |
| Egyszer megkérdezi, aztán elfelejti | `last-poll:` mező hiánya |

## Tag-taxonomy bővítés-javaslat

A `00-Meta/Tag-taxonomy.md`-hez új altag-csoport:

```
#blocked/external        - külső személy/szervezet inputjára vár
#blocked/3rd-party-api   - külső API-szolgáltatóra vár
#blocked/internal        - belső team-tagra vár (több-fős projekt esetén)
#blocked/release-window  - deploy-időablakra vár (pl. low-traffic-time)
```

A meglévő ad-hoc `#domi-input`, `#mariann-input`, `#zsuzsi-zoli`, `#atti-blocked` átmenetileg **maradhatnak** (értékes who-context), de mind kapjon `#blocked/external` szülő-taget is.

## Reusable szabályok

1. **Külső blokkoló → struktúrált jelölés**: `blocked-by:<who> <ISO-date>` minimum, nem csak tag.
2. **`blocked-since:` kötelező** — drift-méréshez ISO-dátum, NEM relatív („utolsó hét").
3. **`last-poll:` mező** — proaktív emlékeztetőhöz; ha hiányzik, default `blocked-since`.
4. **Heti audit-job** — 7-napos küszöb felett poll-emlékeztető Daily-be.
5. **Dashboard-query** — látható drift, ne kelljen grep-pel keresni.
6. **Tag-hierarchia** — `#blocked/external` szülő, `#<personname>` specifikus.
7. **Status `blocked` ≠ `open`** — work-queue tisztaság.

## Session-evidence (10 forrás)

| Project | Hét | Blocker | Drift (napok 2026-05-19-ig) |
|---|---|---|---|
| Foxxi Cookiebot CBID | W17 | Domi (UUID) | 16 |
| Foxxi élesítési időpont | W19 | Domi (dátum) | 9 |
| Foxxi GA4 Enhanced | W18 | Domi/Zozó (admin) | 14 |
| Foxxi 5 blog-cikk publikálás | W17 | Domi (szakmai review) | 16 |
| Foxxi alt-text rövidítés 30db | W19 | Domi (confirm) | 9 |
| Foxxi DKIM kulcs Tárhely.eu | W19 | Domi/Zozó (panel) | 9 |
| KGC Bérgépek 2.xlsx 3 kaució | W19 | Zsuzsi+Zoli (confirm) | 8 |
| Kinda Atti-blocked 4 task | W19 | Atti | 8 |
| Foxxi Marcsi 20-SVG visual choice | W19 | Domi (visual choice) | 9 |
| Foxxi 7 visszakérdezés | W18 | Domi+Mariann | 14 |

## Kapcsolódó

- [[../00-Meta/Tag-taxonomy]] — tag-konvenciók forrása
- [[../00-Meta/Frontmatter-schema]] — `type: task` séma-bővítendő
- [[../04-Tasks/Backlog]] — élő alkalmazási hely
- [[../04-Tasks/Dashboard]] — Dataview-query célhely
- [[auto-disable-min-volume-guard]] — analóg „watchdog drift-detekció"
- [[bmad-cross-machine-artifact-verification]] — analóg „event ≠ disk-state"
