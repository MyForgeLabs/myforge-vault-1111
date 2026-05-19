---
name: 2026-05-19 vault-gh-bridge skeleton
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#topic/sv-brainstorm", "#topic/github", "#topic/skeleton-build"]
---

# vault-gh-bridge skeleton — first-run dry-run

SV brainstorm idea **#14 GitHub commit-history bridge** skeleton-build és első
dry-run smoke-test eredménye.

## Build

- **CLI path:** `/usr/local/bin/vault-gh-bridge`
- **LOC:** ~420 sor (header-docstring + frontmatter renderer együtt)
- **Wiki:** [[11-wiki/github-commit-history-ingest-pattern]]
- **Shared helper:** `/root/obsidian-vault/.vault-tools/lib/vault_atomic.py`
- **State file:** `~/.vault-config/gh-bridge-state.json` (per-file SHA-256 hash)
- **Atomic-lint:** ✓ compliant (`vault-atomic-lint --files vault-gh-bridge`)

## Smoke-test futás

```
$ /usr/local/bin/vault-gh-bridge --dry-run --days 30
[DRY-RUN] gh-bridge: 10 repos, 368 commits (window 30d)
  - PetykaMaki/obsidian-vault                     commits=300  would-write
  - PetykaMaki/boulium-web                        commits=  4  would-write
  - PetykaMaki/agents-skills                      commits=  1  would-write
  - PetykaMaki/obsidian-vault-starter             commits=  4  would-write
  - PetykaMaki/kgc-berles                         commits= 54  would-write
  - PetykaMaki/PetykaMaki.github.io               commits=  2  would-write
  - PetykaMaki/kgcshop                            commits=  3  would-write
  - PetykaMaki/koko-chatbot                       commits=  0  would-write
  - PetykaMaki/MyforgeCore                        commits=  0  would-write
  - PetykaMaki/petanque-app                       commits=  0  would-write
```

## Megfigyelések

- **10 aktív repo** (180-napos `pushedAt`-window) a `PetykaMaki/` namespace-ben.
- **368 commit** összesen az utolsó 30 napban — ebből 300 az `obsidian-vault`
  (vault-meta super-session burst-ök), 54 a `kgc-berles`.
- Az `obsidian-vault` 300-as szám a 3-page cap-en ül (per_page=100 × max_pages=3).
  Backfill-módhoz a `max_pages` bump kell; daily cron `--days 1`-gyel ez NEM gond.
- A 3 "0 commit" repo (`koko-chatbot`, `MyforgeCore`, `petanque-app`) `pushedAt`
  alapján aktív (180-napos ablakon belül van), de az utolsó 30 napban NEM volt
  commit. A `would-write` címke ekkor is megjelenik mert üres-state Markdown-t
  generálunk frontmatter-rel (`commit_count: 0`) — ez **szándékos**, így a
  state-file is felépül és a következő nap incremental-hash-skip működni fog.
- Hibák: 0. Minden `gh api` hívás 200-zal jött vissza.

## Design-döntések ami a brainstorm-eredetiből változott

1. **Linear-side DEFERRED.** A brainstorm-eredeti említi a Linear/GitHub-issue
   integrálást, de a user-nek (2026-05-19) nincs plumbing-Linear workspace-e.
   Most csak a GitHub commit-side. Per-project `gh-bridge.yaml` allow-list
   szintén DEFERRED — a `--repos owner/name,...` explicit list-flag fedi le
   az immediate use-case-et.
2. **Idempotency state-file-szintű, NEM commit-szintű.** A brainstorm
   "incremental" szót használ; én állapot-fájl + SHA-256 file-hash patternt
   választottam, mert atomic-write garanciát ad (sosem fél-fájl). Trade-off:
   1 új commit jövetelekor a teljes napi Markdown újraíródik (NEM
   append-diff). Daily cron mellett ez napi ~1× / repo / 50KB max — elhanyagolható.
3. **KO-DB ingest hook lazy-coupled.** A brainstorm direkt KO-DB triplet-extract-et
   említ; a skeleton csak `vault-ko-ingest --file <path> --dry-run`-nal hívja
   az upstream ingest-et, mert az még maga is 2-phase pending pattern-szinten
   van. A `--ingest-kodb` flag opt-in, NEM default.
4. **Predikátum-vocab kiterjesztés DEFERRED.** A `has_commit` predikátum még
   NEM része a 38-elemű KO-DB predicate-vocab-nak. Első tüzelésekor a heuristic
   extraction `has_string_value`-nak fogja klasszifikálni, és a B-1 Week 4
   predicate-vocab evolution pipeline fogja escalate-elni saját predikátummá.
   Ez **szándékos** (predikátum-floor traffic-driven, NEM upfront-design).
5. **Memgraph cross-link DEFERRED.** A brainstorm
   `Project --[:HAS_COMMIT]--> Commit --[:SOLVED]--> Issue` topológiát említ.
   A skeleton csak `10-raw/` + KO-DB lépcsőt csinálja; a Memgraph
   `:LINKS_TO`/`:HAS_COMMIT` edge-eket a meglevő
   `vault-graph-edge-from-facts` pipeline fogja felhúzni, ha a triplet-ek
   bekerülnek a `.vault-ko/facts.db`-be.

## Next-step ajánlás (production-ready bekerüléshez)

1. **Apply-flag smoke** — egy explicit `VAULT_GH_BRIDGE_APPLY=1 vault-gh-bridge
   --apply --days 7` futtatás, manual review a `10-raw/external/github/`
   alatti 10 fájlra (legalább egy nem-trivial repo Markdown-tartalmát átolvasni).
2. **KO-ingest contract stabilizálása** — a `vault-ko-ingest` `--file` flag-jét
   és a `VAULT_KO_INGEST_APPLY=1` env-flag-et explicit production-ready-ré
   tenni; addig a `--ingest-kodb` flag csak no-op.
3. **`has_commit` predikátum hozzáadása** — ha a triplet-traffic a `B-1 Week 4`
   pipeline-ban felmegy ≥1%-ra, escalate-elni saját predikátummá a vocab-ban.
4. **Cron-install** — pár dry-run nap után `vault-gh-bridge --print-cron`-ból
   bemásolni a crontab-ba (45 6 \* \* \* — vault-cleanup után, vault-net-watch
   előtt).
5. **Backfill mode** — `--backfill` flag + `--max-pages 20` bump az
   `obsidian-vault` history full-archive-jához (egyszeri ~2000-commit dump).
6. **Linear-bridge follow-up** — ha a user behúz egy Linear workspace-et,
   külön `vault-linear-bridge` script azonos pattern-nel.

## Kapcsolódó

- [[11-wiki/github-commit-history-ingest-pattern]] — pattern-doc
- [[06-Audits/2026-05-19 SV new development ideas brainstorm]] — eredeti #14
- [[02-Projects/superintelligent-vault]] — host-projekt
- `vault-browser-history-ingest` — pár-pattern (double-gate, 10-raw/external/)
