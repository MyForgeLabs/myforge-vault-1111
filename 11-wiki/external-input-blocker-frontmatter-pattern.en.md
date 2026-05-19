---
name: External-input blocker frontmatter pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/workflow", "#topic/backlog", "#topic/consultancy", "pattern/blocked-by", "evergreen", "lang/en"]
status: stable
lang: en
translated_from: external-input-blocker-frontmatter-pattern.md
session-evidence: 10
first-seen: 2026-W17
---

# External-input blocker frontmatter pattern

> [!info] TL;DR
> The vault's `04-Tasks/Backlog.md` has **15+ tasks** tagged `#domi-input` / `#mariann-input` / `#zsuzsi-zoli` style — a single, fragile textual convention for "this task is waiting on input from an **external person**". The pattern is currently ad-hoc: no Dashboard query, no "blocked-since" timer, no proactive alert. This wiki formalizes a `blocked-by:` frontmatter field + Dashboard query so hidden-blocked tasks don't drift for 11+ days.

## The problem — drift evidence

In Backlog.md (2026-05-19 sample):

```
- [ ] Domi visual choice — Marcsi 20-SVG package (➕ 2026-05-10)   #foxxi #brand #domi-input
- [ ] Cookiebot CBID — waiting for Domi's UUID (➕ 2026-05-03)     #foxxi #domi-input
- [ ] Go-live date (example-foxxi.local) — Domi needs to pick (➕ 2026-05-10) #foxxi #domi-input
```

These have waited 9–16 days. The "➕ <date>" is the Tasks plugin add-date — but there's **no `blocked-since:` semantic**: invisible since when it's been blocked (could be 1 day, could be 16).

## Suggested frontmatter convention

Instead of (or alongside) tag-based marking, task-level **YAML frontmatter** if separate task file — or emoji field + ISO date at the end of the Backlog.md row:

```markdown
- [ ] **Cookiebot CBID setup** — need Domi's UUID ⏳ blocked-by:domi 2026-05-03 🔴 #foxxi #domi-input
```

Or in structured form (one task file per blocker, if bigger):

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

**Key fields:**
- `blocked-by:` — who or what blocks (person / external service / 3rd-party API)
- `blocked-since:` — when it became blocked (ISO)
- `last-poll:` — when we last asked about it (proactive reminder)
- `status: blocked` — explicit status, NOT just a tag

## Dashboard query (Dataview)

New section in `04-Tasks/Dashboard.md` (Dataview or Bases):

````markdown
## Tasks blocked on external input (live)

```dataview
TABLE
  blocked-by AS "From whom",
  blocked-since AS "Since",
  (date(today) - date(blocked-since)).days + "d" AS "Drift",
  last-poll AS "Last poll"
FROM "04-Tasks"
WHERE status = "blocked" OR contains(tags, "blocked/external")
SORT (date(today) - date(blocked-since)).days DESC
```
````

OR if you want to stay on Backlog.md row-tags — via regex grep:

```bash
# /usr/local/bin/vault-blocked-report (weekly cron)
grep -nE "blocked-by:\w+ \d{4}-\d{2}-\d{2}" /root/obsidian-vault/04-Tasks/Backlog.md
```

## Proactive poll reminder

Weekly audit script:

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

Above the 7-day drift threshold → reminder into today's `01-Daily/<today>.md`:

```markdown
## External polls suggested (3 tasks)
- 16 days: Cookiebot CBID — Domi UUID (Foxxi)
- 12 days: GA4 Enhanced Conversions — admin invite (Zozó)
- 9 days: Go-live date — Domi (Foxxi)
```

## Anti-pattern: hidden-blocked

| Anti-pattern | Problem |
|---|---|
| Only `#domi-input` tag, no date field | "since when?" has no answer |
| "Waiting for Domi reply" in a comment | not grep-able, not auditable |
| Task status = `open` when actually `blocked` | priority sort wrong, work queue confused |
| Manual poll reminder from memory | drift 11-16 days (see Foxxi examples) |
| Asked once, then forgotten | `last-poll:` field missing |

## Tag-taxonomy extension proposal

Add new sub-tag group to `00-Meta/Tag-taxonomy.md`:

```
#blocked/external        - waiting on external person/org input
#blocked/3rd-party-api   - waiting on external API provider
#blocked/internal        - waiting on internal team member (multi-person project)
#blocked/release-window  - waiting on deploy window (e.g. low-traffic time)
```

Existing ad-hoc `#domi-input`, `#mariann-input`, `#zsuzsi-zoli`, `#atti-blocked` can **stay** (valuable who-context), but each gets a `#blocked/external` parent tag.

## Reusable rules

1. **External blocker → structured marking**: `blocked-by:<who> <ISO-date>` minimum, not just a tag.
2. **`blocked-since:` mandatory** — for drift measurement an ISO date, NOT relative ("last week").
3. **`last-poll:` field** — for proactive reminder; if missing, defaults to `blocked-since`.
4. **Weekly audit job** — over 7-day threshold → poll reminder in Daily.
5. **Dashboard query** — visible drift, no grep search needed.
6. **Tag hierarchy** — `#blocked/external` parent, `#<personname>` specific.
7. **Status `blocked` ≠ `open`** — work-queue cleanliness.

## Session evidence (10 sources)

| Project | Week | Blocker | Drift (days to 2026-05-19) |
|---|---|---|---|
| Foxxi Cookiebot CBID | W17 | Domi (UUID) | 16 |
| Foxxi go-live date | W19 | Domi (date) | 9 |
| Foxxi GA4 Enhanced | W18 | Domi/Zozó (admin) | 14 |
| Foxxi 5 blog-posts publish | W17 | Domi (review) | 16 |
| Foxxi alt-text shortening 30 | W19 | Domi (confirm) | 9 |
| Foxxi DKIM key Tárhely.eu | W19 | Domi/Zozó (panel) | 9 |
| KGC Bérgépek 2.xlsx 3 deposits | W19 | Zsuzsi+Zoli (confirm) | 8 |
| Kinda Atti-blocked 4 tasks | W19 | Atti | 8 |
| Foxxi Marcsi 20-SVG visual choice | W19 | Domi (visual choice) | 9 |
| Foxxi 7 followups | W18 | Domi+Mariann | 14 |

## Related

- [[../00-Meta/Tag-taxonomy]] — tag-conventions source
- [[../00-Meta/Frontmatter-schema]] — `type: task` schema to extend
- [[../04-Tasks/Backlog]] — live application site
- [[../04-Tasks/Dashboard]] — Dataview-query target
- [[auto-disable-min-volume-guard]] — analogous "watchdog drift detection"
- [[bmad-cross-machine-artifact-verification]] — analogous "event ≠ disk-state"

## Hungarian original

[[external-input-blocker-frontmatter-pattern]]
