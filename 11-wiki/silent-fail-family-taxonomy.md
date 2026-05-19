---
name: Silent-fail család taxonomy
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/reliability", "#topic/observability", "pattern/silent-fail", "taxonomy", "evergreen"]
status: stable
session-evidence: 14
first-seen: 2026-W17
---

# Silent-fail család taxonomy

> [!info] TL;DR
> A vault-ban **40+ KO-DB fact** beszél „silent fail / silent revert / silent skip / silent truncation" mintázatról, és valójában **4 különböző jelentés-réteg** keveredik egy fogalom alatt. Ez a wiki disambiguálja a 4 családot, mindegyikhez ad detektálási-protokollt, és reusable szabályt — hogy ne kelljen újra meg újra felfedezni, hogy „no-error ≠ success".

## A 4 silent-fail család

### 1. Exit-0 silent-fail (script/CLI)

**Mintázat:** parancs `exit 0`-val tér vissza, de a kimenete üres / csonka / 20-byte gzip-header-only. Standard `if [[ $? -ne 0 ]]` check nem fog rajta.

**Példák:**
- `wp db export` Hostinger shared-en → **20-byte gzip-header**, exit 0, üres dump (KO-DB [4936], [4940], [4973], [13614]).
- `vault-detect-chat-id` `set -e`-vel + parameter-expansion-ben → exit 1 öl a chain-t, NEM jelzi (MEMORY 2026-05-18).
- `dev backup cron` 3 hónapig silent-elhalt — auto-mailbox-jelzés nélkül (KO-DB [13602]).

**Detektálási protokoll:**
1. **Size-verify**: `[[ $(stat -c%s "$f") -gt 1024 ]]` minden generált artefaktumra (a 20-byte gzip-header indikátor).
2. **Content-spot-check**: `head -c 100 "$f" | xxd | head -3` — látsz-e valódi data-bytes-ot?
3. **Sanity-marker**: dump-ok végén `-- Dump completed` (mysqldump) vagy `# COMMIT;` (pg_dump) — `tail -1` ellenőrzés.
4. **Tee + min-volume guard**: minden cron-script-ben `tee -a $LOG`, és heti audit-job `wc -l $LOG` < 5 → riaszt.

### 2. Mutation-silent-revert (sync/cache layer)

**Mintázat:** kódot/adatot ÍRSZ — az írás látszólag sikerült —, de egy másik réteg (cache, sync-plugin, ORM-flag) **csendben visszaforgatja**.

**Példák:**
- **WPML + Elementor**: lefordított `_elementor_data` → master HU verzióra visszacserélve (KO-DB [733], [10217]). Fix: direct `wpdb` update bypass + `wp cache flush`.
- **Mac Obsidian-Git auto-pull**: server-side fix (AUTO-GEN END marker) Mac auto-sync során eltűnik (KO-DB [11128], [11136]). Fix: server-side commit ELSŐKÉNT, Mac-pull MÁSODIKKÉNT, `git diff --cached` minden rebase-continue előtt.
- **Prisma seed `upsert.update`**: csak flag-mezőket szinkronizál, ár-mezőt NEM (lásd `prisma-seed-admin-edit-protected` wiki) — admin által manuálisan írt érték „silently survival".

**Detektálási protokoll:**
1. **Round-trip read**: minden mutáció után `read-back + assert(content==expected)`.
2. **3-way diff**: új-állapot vs. utolsó-snapshot vs. előző-snapshot (`excel-redmark-3way-diff-workflow` ezt formalizálja — KO-DB [1075], [1080], [1110]).
3. **Audit-log append-only**: minden mutációs path append-only logot ír; visszaolvasáskor látszik, ha „eltűnt" egy bejegyzés.

### 3. Parse/encode silent-coerce (string/encoding)

**Mintázat:** string-input csendben átalakul (URL-decode `+`→` `, NBSP→space, CRLF→LF, str_replace 0-replacement), kód továbbmegy, downstream allow-list-ben silent-fallback-be esik.

**Példák:**
- **URL `+` → space**: `?age=50+` → `"50 "`, allow-list nem matchel → silent-fallback `'all'` filter, `totalN=44 unfiltered` (KO-DB [2453], [2459], [2489], [11886], [12106]).
- **`str_replace` Elementor JSON-on**: UTF-8 vs unicode-escape, NBSP, backslash mismatch → 0 replacement, exit 0 (KO-DB [723], [10035], [10037]). Fix: path-based `set_by_path()` (KO-DB [724], [10038]).
- **`nano-banana -i` flag**: filename felülírja a prompt-stringet (KO-DB [333]).
- **Tailwind unknown token**: `bg-bg-drawer` → silent missing CSS, no error, transparent drawer (KO-DB [9124], [9147]).

**Detektálási protokoll:**
1. **Replacement-count assert**: `count = file.count(needle); assert count > 0 else raise`.
2. **Whitelist-coverage report**: filter-match-rate metric (`totalN` előtte/utána).
3. **Path-based mutation > string-match** ha lehet (JSON-path, AST-rewrite).
4. **Encode-explicit boundaries**: `encodeURIComponent` minden user-input URL-paramon.

### 4. Truncation/overflow silent-loss (context/memory layer)

**Mintázat:** input túllép egy ki-nem-mondott méret-limit-en, és **csendben csonkolódik** — agent/runtime látszólag normál módon működik, de „nem látja" a maradékot.

**Példák:**
- **MEMORY.md overflow**: 24.4KB+ → silent truncation at session start, agent partial-context (KO-DB [1975], [2026], [8141]). Fix: per-line ≤200 char, tematikus szekciók, detail topic-fájlokba (`memory-md-overflow-management`).
- **Caddy basic-auth wrong format**: silent 401 HTTP, NO server-side error (KO-DB [8667]).
- **Cloud-image SSH defaults**: hardening conf-d `/etc/ssh/sshd_config.d/` load-order-rel silently overridden (KO-DB [1869]).

**Detektálási protokoll:**
1. **Size-budget pre-check**: tudd a felső limitet, és `wc -c` előtte.
2. **HEAD/TAIL sanity-marker**: első és utolsó N karakter ellenőrzés visszaolvasáskor.
3. **Config-load `-T` test-mode**: `sshd -T` / `nginx -t` / `caddy validate` minden config-merge után.

## Cross-family disambiguáció szabály

Mikor sessionben „silent fail" szót használsz, **jelöld a réteget**:

| Szó | Jelentés |
|---|---|
| „exit-0 silent" | CLI/script no-error de empty output |
| „silent-revert" | sync/cache layer rollback mutáció után |
| „silent-coerce" | parse/encode csendes átalakulás |
| „silent-truncation" | méret-limit overflow csonkolás |
| meztelen „silent fail" | tilos, ambiguous |

## Anti-pattern: „no-error == success" feltételezés

Az összes 4 család mögött ez a hibás mental-model. **Reusable Q-protokoll**, minden „kész" deklaráció előtt:

1. **Méret?** — `stat -c%s` vagy `wc -c` ép-e?
2. **Tartalom?** — `head` + `tail` sanity-markerre?
3. **Round-trip?** — visszaolvasva ugyanaz?
4. **Allow-list match-rate?** — N előtte = N utána?
5. **Audit-log bejegyzés?** — látható a mutáció a logban?

Ha bármelyikre „nem tudom" → silent-fail-rizikó, vissza-research.

## Reusable szabályok

1. **Exit-code önmagában gyenge bizonyíték** — minden disk-output méret + tartalom + sanity-marker check kell mellé.
2. **Round-trip read-after-write** kötelező minden persistence-mutáció után (különösen cache-elt rétegeken).
3. **Path-based mutáció > string-match** struktúrált adat-formátumon (JSON, XML, YAML).
4. **MIN_VOLUME guard** minden cron-script-ben: ha output mennyiség leesik a normál-tartomány alá → riaszt, NE „passively" pass-eld.
5. **Auto-disable watchdog**: ha 7 napig 0 mutáció generálódik, auto-disable + alert (`auto-disable-min-volume-guard` wiki).
6. **3-way diff** áradat / katalógus-frissítés / sync-output detektáláshoz (új vs. utolsó vs. előző).
7. **Sanity-marker minden artefaktum végén** — `# DUMP_OK` / `-- COMPLETED` / „AUTO-GEN END" → `tail -1` check könnyű.

## Session-evidence (14 forrás)

| Project | Hét | Család |
|---|---|---|
| frankpanama.com backup | W17 | 1 (exit-0, 20-byte gzip) |
| myforge-dashboard | W17 | 3 (Tailwind token) |
| foxxi-elementor | W17 | 2 + 3 (WPML revert + str_replace) |
| vault-maintenance | W19 | 2 (Mac silent-revert) |
| kinda-project | W19 | 3 (URL `+` decode) |
| kgc-weboldal | W19 | 2 (Prisma seed) |
| szerver-update | W20 | 1 + 4 (wp db export, SSH conf) |
| obsidian-vault | W20 | 4 (MEMORY.md overflow) |
| kgc-bergep-frissites | W19 | 2 + 3 (silent kaució-fix, NBSP) |

## Kapcsolódó

- [[wp-cli-shared-db-export-fallback]] — 1. család konkrét incidens
- [[wp-elementor-template-conflicts]] — 2. család (Elementor JSON)
- [[url-param-plus-decode-quirk]] — 3. család (URL-decode)
- [[memory-md-overflow-management]] — 4. család (overflow)
- [[excel-redmark-3way-diff-workflow]] — 3-way diff defenzíva
- [[auto-disable-min-volume-guard]] — watchdog-pattern
- [[audit-log-append-only-pattern]] — append-only audit-trail
- [[cascade-pattern-family-taxonomy]] — analóg „többjelentésű szó" disambiguáció
