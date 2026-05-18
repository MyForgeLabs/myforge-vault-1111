---
name: 2026-05-17 B-5 vault-meta notebook hook
type: audit
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "#project/superintelligent-vault", "#axis/sv-5", "#axis/sv-8"]
---

# B-5 × B-8 — vault-meta NotebookLM crystallization hook (Week 2-α landed)

> Cross-project synthesis hook a SV-5 (Crystallization) ∩ SV-8 (NotebookLM cognitive layer)
> metszetén. Minden lezárt session `## Learnings`-szekciója egy közös **vault-meta**
> notebookba kerül, így a 7 cross-projekt synthesis kérdés ([[../11-wiki/sv-08-notebooklm-cognitive-layer#Sprint 5|sv-08 Sprint 5]]) immár futtatható.

## Mi épült

| Komponens | Path | Funkció |
|---|---|---|
| Vault-Meta notebook | NotebookLM ID `<vault-meta-nb-id-here>` | „Vault Meta — cross-project Learnings" |
| Notebook-ID pointer | `~/.vault-config/vault-meta-notebook.id` | hot-reloadable, egy soros |
| Push-script | `/usr/local/bin/vault-nb-meta-push` | idempotens, `--dry-run`, `--force` |
| Post-stop hook | `~/.vault-config/post-stop-hooks/01-vault-meta-push.sh` | env-gated (`VAULT_META_NB_AUTOPUSH=1`) |
| Audit-log | `06-Audits/vault-meta-pushes.jsonl` | JSONL per-push, idempotencia-forrás |

## Flow

1. **`11.11stop`** lefut a megszokott módon — summary + commit + push (érintetlen).
2. **`VAULT_META_NB_AUTOPUSH=1`** esetén a stop-runner végén a hook-loop végigfut a
   `~/.vault-config/post-stop-hooks/*.sh` script-eken. Az `01-vault-meta-push.sh`
   átadja a session-slug-ot a `vault-nb-meta-push`-nak.
3. **`vault-nb-meta-push <slug>`**:
   - audit-log lookup → ha már megvolt, skip (force-bypassolható)
   - `awk '/^## Learnings/{f=1;next} /^## /{f=0} f'` kivonat
   - empty → 0-val skip (sok session nem ad új tanulságot)
   - frontmatter-rich temp `/tmp/vault-meta-learnings-<slug>-XXXX.md`
   - `notebooklm source add --type file -n <NB_ID>`
   - `notebooklm source rename` (a CLI filename-ből titleli a file-source-okat, override slug-ra)
   - JSONL audit-bejegyzés

## Wire-in (manuális, NEM applied)

A `11.11stop` script-et NEM módosítottuk a feladat szerint. A wire-in egy ~6 soros
patch a `/usr/local/bin/11.11stop` végén (commit/push blokk után):

```bash
# === post-stop hooks (vault-meta, future) ===
if [[ "${VAULT_META_NB_AUTOPUSH:-0}" == "1" ]]; then
  for hook in "$HOME"/.vault-config/post-stop-hooks/*.sh; do
    [[ -x "$hook" ]] || continue
    "$hook" "$(basename "$FILE" .md)" "$FILE" 2>&1 | sed "s/^/  [post-stop] /"
  done
fi
# === end ===
```

A wire-in előtt is használható manuálisan: `vault-nb-meta-push <slug>`.

## Test-run (2026-05-17)

```
$ vault-nb-meta-push --dry-run 2026-05-15-mfl-voice-sprint-1
── DRY RUN ──
  notebook:  <vault-meta-nb-id-here>
  title:     2026-05-15-mfl-voice-sprint-1
  project:   mfl-voice
  bytes:     3537  (27 lines)

$ vault-nb-meta-push 2026-05-15-mfl-voice-sprint-1
✓ Pushed to vault-meta  2026-05-15-mfl-voice-sprint-1  (3537 B, source: 373114e3-…)

$ vault-nb-meta-push 2026-05-15-mfl-voice-sprint-1
↺ Already pushed (audit-log hit): 2026-05-15-mfl-voice-sprint-1
  use --force to re-push
```

NotebookLM oldalon `notebooklm source list -n 5469d2…` confirms `status: ready`.

## Backfill stratégia (manuális, ajánlott)

A jelenlegi pipeline csak új session-okat kap el. Backfillért egyszer érdemes:

```bash
for f in /root/obsidian-vault/08-Sessions/2026-05-*.md; do
  slug=$(basename "$f" .md)
  vault-nb-meta-push "$slug"
done
```

Idempotens — biztonságos újrafutni.

## Next step: cross-project synthesis queries

A vault-meta-notebookon havonta 1× a [[../11-wiki/sv-08-notebooklm-cognitive-layer#Sprint 5|Sprint 5]]
7-strukturált kérdés futtatható. Példák a wikiből:

```
notebooklm ask -n <vault-meta-nb-id-here> \
  "Mely tanulságok ismétlődnek 3+ projektben? Adj source-grounded listát."

notebooklm ask -n <vault-meta-nb-id-here> \
  "Mely failure-mode-ok közösek a 2026-05-* session-ökben?"

notebooklm ask -n <vault-meta-nb-id-here> \
  "Mely tech-stack döntések ütköznek egymással? (CORS, cookies, auth, hosting)"
```

A válaszok új `11-wiki/cross-project-synthesis-2026-05.md` cikkbe propagálhatóak.

## Korlátok / kockázatok

- **NotebookLM API hivatalosan nem támogatott** — community-CLI Google-policy-change-re sérülékeny. Vault marad canonical (dual-write).
- **`source rename` race** — ha a CLI lassú, a rename előtt a táblanézet még a filename-et mutathatja. Ártalmatlan.
- **Idempotencia kulcs = slug+audit-log** — ha valaki kézzel törli a JSONL-ből egy sort, a script újrapushol (duplikál a notebook-ban). A duplikátum-detektálás `--force` mellett szándékos.
- **Skip-if-empty** logika konzervatív: csak a `## Learnings → memória` body-t nézi. Ha üres, semmi nem megy a notebookba — ez OK.

## Kapcsolódó

- [[../11-wiki/sv-08-notebooklm-cognitive-layer]] — Sprint 3 specifikáció
- [[../11-wiki/Crystallization-protocol]] — SV-5 routing decision tree
- [[../02-Projects/superintelligent-vault]] — B-1..B-7 sprint dashboard
