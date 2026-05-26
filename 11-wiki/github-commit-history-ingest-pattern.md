---
name: github-commit-history-ingest-pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/sv-brainstorm", "#topic/github", "#topic/ko-db", "#topic/ingest"]
---

# GitHub commit-history ingest pattern

A vault **decision-log**-ot ír (ADR-ek, sessions), de a **code-log**-ot eddig
NEM. Ezért egy hónap múlva visszanézve fáj rekonstruálni, mit csináltunk
valójában a kódban — csak a "miért" maradt. A `vault-gh-bridge` CLI ezt a rést
zárja be: a felhasználói GitHub repo-k commit-üzeneteit napi cron-tal lehúzza,
és per-repo Markdown digest-et tesz a `10-raw/external/github/<owner>__<name>/`
alá, ahonnan a KO-DB ingest pipeline triplet-ekké rágja őket.

A pattern az SV brainstorm idea **#14** skeleton-szintű build-je. Linear-side
DEFERRED — a brainstorm-eredeti említi, de a user-nek nincs Linear workspace-e
plumbing-szinten plumbing-szinten, ezért most csak a GitHub-fél van.

## Mit csinál

1. **Repo-felderítés** — `gh repo list --json nameWithOwner,pushedAt,isArchived`,
   szűrve `is_archived=false` + `pushedAt < N nap` (default 180). 2026-05-19
   állapotban 10 aktív repo a `PetykaMaki/` namespace-ben.
2. **Commit-fetch** — per repo `gh api repos/<o>/<n>/commits?per_page=100&since=<ISO>`,
   max 3 oldal = 300 commit/repo/futás (daily cron `--days 1`-gyel bőven elég).
3. **Render** — per repo egy `10-raw/external/github/<owner>__<name>/commits-YYYY-MM-DD.md`
   Markdown table: `| sha7 | author | date | message_first_line |`.
4. **Idempotency** — `~/.vault-config/gh-bridge-state.json` tárolja a per-file
   SHA-256 hash-ét; ugyanaz a window ugyanazt a fájlt termeli → atomic-write
   észleli + skippel.
5. **KO-DB ingest hook** — opcionális (`--ingest-kodb`). A digest-fájlt átadja
   a `vault-ko-ingest --file <path>`-nek; az upstream 2-phase pending-pattern-je
   miatt a triplet-extraction önmagában is `--dry-run`-os most.
6. **Audit-log** — `06-Audits/gh-bridge-log.jsonl`-be event-enként sor.

## KO-DB triplet-szándék

Minden commit megcélzott triplet-formája:

```
subject     = <owner>/<name>                    # pl. PetykaMaki/client-c-app-web
predicate   = has_commit
object      = <sha7> <message_first_line>       # pl. "a3c92f1 feat: glicko-2 backfill"
provenance  = github:<owner>/<name>@<sha>
source_type = github_commit
```

A `has_commit` predikátum még NEM a `vault-ko-ingest` 38-elemű vocab-jában van —
első tüzeléskor a heuristic extraction `has_string_value`-nak fogja klasszifikálni,
és a predicate-vocab evolution-pipeline ([B-1 Week 4]) fogja escalate-elni saját
predikátummá. Ez **szándékos** — predikátum-floor-traffic-driven.

## Safety + opt-in gate

- **Default dry-run.** A `--apply` flag önmagában NEM ír; **mindkét** gate kell:
  `--apply` + `VAULT_GH_BRIDGE_APPLY=1` env-var. Ez a vault-szabvány
  "double-gate" pattern (lásd `vault-browser-history-ingest`-ben is).
- **Read-only `gh`** — soha nem hívunk write-mutating gh-parancsot (push, create
  release, comment). Csak `gh api` GET + `gh repo list`.
- **Token nem kerül vault-ba.** A `gh auth status` zöld kell legyen (saját token,
  `~/.config/gh/hosts.yml`-ban marad), de a script semmit NEM olvas ki belőle.

## Gotcha-k

1. **300-commit cap per page-cap.** Default `max_pages=3` × `per_page=100` =
   300 commit/repo. Backfill módhoz (pl. `--days 180`) bumpolni kell —
   addig a 30-napos default ablakra az `obsidian-vault` repo (~300 commit/hó)
   pont határon táncol.
2. **NBSP-mentes filename.** `UNSAFE_FILENAME_RE` minden nem-`[A-Za-z0-9._-]`
   karaktert dash-re cserél, így az NBSP-buktatóra (lásd MEMORY.md
   "NBSP a fájlnévben") immunis.
3. **Idempotency állapot fájl-szintű, NEM commit-szintű.** Ha a 30-napos
   ablak ugyanaz, és nincs új commit, a render-output hash-stable → skip.
   De ha 1 új commit jön, az egész napi fájl újraíródik (NEM diff-append).
   Ez szándékos — atomic-write garanciát ad, az olvasó sosem lát fél-fájlt.
4. **`gh api ... ?page=N` empty-response = "no more"** — a 409/404 üzleti
   szempontból "üres repo" jelzés, `[warn]`-ral logozzuk de NEM hibázik.
5. **Repo-list `--limit` cap.** Default 100; a user 10-zel él, de ha 200+
   repo lenne (org-szintű), bumpoljuk.
6. **`vault-ko-ingest --file` még nem stabil contract.** A skeleton-ko-ingest
   `--file` flag-je előírt, de a triplet-extraction subagent-fanout-ja még
   2-phase pending; ezért a `kodb_ingest_file()` helper most mindig `--dry-run`-nal
   hívja. Production-ready ko-ingest contract-tal (`--apply` + `VAULT_KO_INGEST_APPLY=1`)
   ugyanaz az env-flag-pair-pattern majd működni fog.

## Cron-suggestion

```
# 45 6 * * * VAULT_GH_BRIDGE_APPLY=1 /usr/local/bin/vault-gh-bridge \
#   --apply --days 1 --json >> /var/log/vault-gh-bridge.log 2>&1
```

A `--print-cron` flag kiírja ezt. Bevezetés: pár dry-run smoke-után érdemes
csak élesíteni.

## Linear-side (DEFERRED)

A brainstorm-eredeti `gh-bridge.yaml` per-project allow-list-et és
Linear-integration-t is említ. Mivel a user-nek (2026-05-19) nincs
Linear workspace-e plumbing-szinten, ez egy külön `vault-linear-bridge`
script-be megy majd, ha valaha behúzzuk. Most a `--repos owner1/name1,...`
flag fedi le az explicit allow-list use-case-et.

## Kapcsolódó

- [[02-Projects/superintelligent-vault]] — host-projekt
- [[06-Audits/2026-05-19 SV new development ideas brainstorm]] — `#14` eredeti
- [[06-Audits/2026-05-19 vault-gh-bridge skeleton]] — first-run smoke
- `vault-browser-history-ingest` — szintén `10-raw/external/`-be ír, ugyanaz a double-gate pattern
- `vault-github-trending-recurrence` — más use-case (heti aggregálás a
  napi `10-raw/*GitHub trending*` jelentésekből), NEM commit-bridge
- `vault-ko-ingest` — downstream consumer
- [[11-wiki/multi-layer-safety-gate]] — a double-gate pattern általánosan
