---
name: Silent-fail family taxonomy
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/reliability", "#topic/observability", "pattern/silent-fail", "taxonomy", "evergreen", "lang/en"]
status: stable
lang: en
translated_from: silent-fail-family-taxonomy.md
session-evidence: 14
first-seen: 2026-W17
---

# Silent-fail family taxonomy

> [!info] TL;DR
> The vault has **40+ KO-DB facts** about "silent fail / silent revert / silent skip / silent truncation" patterns, but they really mix **4 distinct meaning layers** under one term. This wiki disambiguates the 4 families, gives each a detection protocol and a reusable rule — so you don't keep rediscovering that "no-error ≠ success".

## The 4 silent-fail families

### 1. Exit-0 silent-fail (script/CLI)

**Pattern:** command returns `exit 0`, but output is empty / truncated / 20-byte gzip-header-only. Standard `if [[ $? -ne 0 ]]` check misses it.

**Examples:**
- `wp db export` on Hostinger shared hosting → **20-byte gzip header**, exit 0, empty dump.
- `vault-detect-chat-id` with `set -e` inside parameter expansion → exit 1 kills the chain, NOT surfaced.
- `dev backup cron` silently dead for 3 months — no mailbox notification.

**Detection protocol:**
1. **Size-verify**: `[[ $(stat -c%s "$f") -gt 1024 ]]` on every generated artifact (the 20-byte gzip-header indicator).
2. **Content spot-check**: `head -c 100 "$f" | xxd | head -3` — do you see real data bytes?
3. **Sanity marker**: dumps end with `-- Dump completed` (mysqldump) or `# COMMIT;` (pg_dump) — `tail -1` check.
4. **Tee + min-volume guard**: every cron script writes `tee -a $LOG`, weekly audit job `wc -l $LOG` < 5 → alert.

### 2. Mutation-silent-revert (sync/cache layer)

**Pattern:** you WRITE code/data — the write appears to succeed — but another layer (cache, sync plugin, ORM flag) **silently rolls back**.

**Examples:**
- **WPML + Elementor**: translated `_elementor_data` → swapped back to master HU version. Fix: direct `wpdb` update bypass + `wp cache flush`.
- **Mac Obsidian-Git auto-pull**: server-side fix (AUTO-GEN END marker) disappears during Mac auto-sync. Fix: server-side commit FIRST, Mac pull SECOND, `git diff --cached` before every rebase-continue.
- **Prisma seed `upsert.update`**: only flag fields sync, price field does NOT (see `prisma-seed-admin-edit-protected`) — admin-written value "silently survives".

**Detection protocol:**
1. **Round-trip read**: after every mutation, `read-back + assert(content==expected)`.
2. **3-way diff**: new-state vs. last-snapshot vs. previous-snapshot (`excel-redmark-3way-diff-workflow` formalizes this).
3. **Audit-log append-only**: every mutation path writes append-only log; on read-back you can see if an entry "vanished".

### 3. Parse/encode silent-coerce (string/encoding)

**Pattern:** string input silently transforms (URL-decode `+`→` `, NBSP→space, CRLF→LF, str_replace 0-replacement), code keeps going, downstream allow-list falls into a silent fallback.

**Examples:**
- **URL `+` → space**: `?age=50+` → `"50 "`, allow-list doesn't match → silent fallback to `'all'` filter, `totalN=44 unfiltered`.
- **`str_replace` on Elementor JSON**: UTF-8 vs unicode-escape, NBSP, backslash mismatch → 0 replacements, exit 0. Fix: path-based `set_by_path()`.
- **`nano-banana -i` flag**: filename overwrites the prompt string.
- **Tailwind unknown token**: `bg-bg-drawer` → silent missing CSS, no error, transparent drawer.

**Detection protocol:**
1. **Replacement-count assert**: `count = file.count(needle); assert count > 0 else raise`.
2. **Whitelist-coverage report**: filter-match-rate metric (`totalN` before/after).
3. **Path-based mutation > string-match** where possible (JSON-path, AST-rewrite).
4. **Encode-explicit boundaries**: `encodeURIComponent` on every user-input URL param.

### 4. Truncation/overflow silent-loss (context/memory layer)

**Pattern:** input exceeds an unstated size limit and **silently truncates** — agent/runtime appears to work normally but "doesn't see" the rest.

**Examples:**
- **MEMORY.md overflow**: 24.4KB+ → silent truncation at session start, agent partial-context. Fix: per-line ≤200 char, thematic sections, detail in topic files (`memory-md-overflow-management`).
- **Caddy basic-auth wrong format**: silent 401 HTTP, NO server-side error.
- **Cloud-image SSH defaults**: hardening conf-d `/etc/ssh/sshd_config.d/` load-order silently overridden.

**Detection protocol:**
1. **Size-budget pre-check**: know the upper limit, `wc -c` before.
2. **HEAD/TAIL sanity-marker**: check first and last N chars on read-back.
3. **Config-load `-T` test-mode**: `sshd -T` / `nginx -t` / `caddy validate` after every config merge.

## Cross-family disambiguation rule

When using "silent fail" in a session, **mark the layer**:

| Term | Meaning |
|---|---|
| "exit-0 silent" | CLI/script no-error but empty output |
| "silent-revert" | sync/cache layer rollback after mutation |
| "silent-coerce" | parse/encode silent transformation |
| "silent-truncation" | size-limit overflow truncation |
| bare "silent fail" | forbidden, ambiguous |

## Anti-pattern: "no-error == success" assumption

All 4 families come from this faulty mental model. **Reusable Q-protocol**, before every "done" declaration:

1. **Size?** — is `stat -c%s` / `wc -c` healthy?
2. **Content?** — `head` + `tail` for sanity marker?
3. **Round-trip?** — read-back identical?
4. **Allow-list match rate?** — N before = N after?
5. **Audit-log entry?** — is the mutation visible in the log?

If any answer is "don't know" → silent-fail risk, back to research.

## Reusable rules

1. **Exit code alone is weak evidence** — every disk-output needs size + content + sanity-marker check alongside.
2. **Round-trip read-after-write** mandatory after every persistence mutation (especially across cached layers).
3. **Path-based mutation > string-match** on structured data formats (JSON, XML, YAML).
4. **MIN_VOLUME guard** in every cron script: if output volume drops below normal range → alert, do NOT "passively" pass.
5. **Auto-disable watchdog**: if 7 days produce 0 mutations, auto-disable + alert (`auto-disable-min-volume-guard`).
6. **3-way diff** for stream / catalog refresh / sync output detection (new vs. last vs. previous).
7. **Sanity marker at every artifact end** — `# DUMP_OK` / `-- COMPLETED` / "AUTO-GEN END" → `tail -1` check is cheap.

## Session evidence (14 sources)

| Project | Week | Family |
|---|---|---|
| frankpanama.com backup | W17 | 1 (exit-0, 20-byte gzip) |
| myforge-dashboard | W17 | 3 (Tailwind token) |
| foxxi-elementor | W17 | 2 + 3 (WPML revert + str_replace) |
| vault-maintenance | W19 | 2 (Mac silent-revert) |
| kinda-project | W19 | 3 (URL `+` decode) |
| kgc-weboldal | W19 | 2 (Prisma seed) |
| szerver-update | W20 | 1 + 4 (wp db export, SSH conf) |
| obsidian-vault | W20 | 4 (MEMORY.md overflow) |
| kgc-bergep-frissites | W19 | 2 + 3 (silent deposit-fix, NBSP) |

## Related

- [[wp-cli-shared-db-export-fallback]] — family 1 concrete incident
- [[wp-elementor-template-conflicts]] — family 2 (Elementor JSON)
- [[url-param-plus-decode-quirk]] — family 3 (URL decode)
- [[memory-md-overflow-management]] — family 4 (overflow)
- [[excel-redmark-3way-diff-workflow]] — 3-way diff defence
- [[auto-disable-min-volume-guard]] — watchdog pattern
- [[audit-log-append-only-pattern]] — append-only audit trail
- [[cascade-pattern-family-taxonomy]] — analogous "polysemic term" disambiguation

## Hungarian original

[[silent-fail-family-taxonomy]]
