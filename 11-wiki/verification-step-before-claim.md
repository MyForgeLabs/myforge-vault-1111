---
name: verification-step-before-claim
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/eval", "#topic/discipline", "#pattern/anti-hallucination"]
---

# Verifikációs lépés állítás előtt

## TL;DR

Bármilyen "kész", "elvégezve", "működik", "megoldva" állítás ELŐTT **explicit verifikációs lépés**: filesystem-`ls`, `curl` smoke, `git log`, audit-log query, `ps`-check, referencia-fact match. Anti-hallucináció / anti-event-vs-disk-state drift. Cross-source: 53+ fact, 3 source-type. **Az egyetlen leggyakoribb evergreen pattern**.

## Háttér (3+ source-evidence)

- **BMad cross-machine artifact verification:** `11.11note` event ≠ disk-state; session-záráskor `ls` minden hivatkozott `/root/...md` path-ot ([bmad-cross-machine-artifact-verification](bmad-cross-machine-artifact-verification.md))
- **Feedback claims verification:** UX/SEO-vélemény előtt verifikálj referencián (Lighthouse-score, screenshot), ne csak general-best-practice alapján ([feedback_claims_verification.md memory pointer](/root/.claude/projects/-root/memory/MEMORY.md))
- **Backup verification step:** UpdraftPlus `wpcore.zip` üres → verify ELŐTT migration; ha empty → `wp core download --force --skip-content` ([hostinger-updraftplus-staging-migration](hostinger-updraftplus-staging-migration.md))
- **Vendor feature verify before workaround:** Memgraph CE 3.9.0 native vector-index 280× speedup — VERIFIKÁLD a feature-t ELŐBB, ne workaround-ozz numpy-cosine-nal ([vendor-feature-verify-before-workaround](vendor-feature-verify-before-workaround.md))
- **Multi-page PDF callout-check:** "hiányzó callout" előtt ellenőrizd `figures>1` (másik oldalon lehet) ([MEMORY multi-page PDF callout-check bullet](/root/.claude/projects/-root/memory/MEMORY.md))
- **Silent fail detection:** Voice-chat pipeline-ban "silent fail detection" mint kötelező verification step ([mfl-voice voice-chat pipeline](mfl-voice-jarvis-mother-research.md))
- **Bug universality verification:** Reusable-pattern claim-ek ELŐTT verifikáld, hogy más browser/OS-en is reprodukálható ([orphan-pdf-auto-resume-pattern](orphan-pdf-auto-resume-pattern.md))

## Mintázat

```
Claim ──> "X kész/működik"
            │
            ▼
        Verification step (mechanikus, automatizálható)
            │
            ├─ ls / find — fájl létezik?
            ├─ curl /  smoke endpoint — 200 OK?
            ├─ git log — commit valóban benne van?
            ├─ ps aux | grep — process fut?
            ├─ audit-log query — entry valóban beírva?
            ├─ vault-ko-query — fact valóban a DB-ben?
            └─ screenshot / diff — vizuálisan stimmel?
            │
            ▼
        Ha ✓ — claim mehet
        Ha ✗ — JAVÍTSD ELŐBB, csak utána claim
```

## Architektúrális szabályok

1. **Mechanikus verification > narratív magyarázat** — `ls path` kimenete > "biztos benne van"
2. **Verifikáció a `claim` Output-jában** — session-fájl `## Verification` szekció vagy commit-üzenet "Verified: <bash output>"
3. **Cross-source corroboration** — ha 2 source mást mond, NE claim-elj, jelöld `[conflict: see audit]`
4. **`session-close` ritual minden referenciára** — bmad cross-machine cikk explicit: minden artifact path-ra `ls`
5. **Bug-universality** — feature-claim ELŐTT verify min. 2 environment-ben (browser-OS pár, vagy local-prod)
6. **Verification audit-log-ban** — `audit-log-append-only-pattern` szerint

## Verifikációs típus → eszköz mátrix

| Claim | Verification |
|-------|-------------|
| "Fájl létezik" | `ls -la <path>` (file-size > 0) |
| "Commit benne van" | `git log --oneline | grep <hash>` |
| "Service fut" | `systemctl status <unit>` vagy `ps aux | grep` |
| "Endpoint él" | `curl -sI <url> | head -1` (HTTP 200) |
| "Fact a KO-DB-ben" | `vault-ko-query "<subject>" --json` |
| "Wiki létezik" | `ls /root/obsidian-vault/11-wiki/<slug>.md` |
| "Audit-entry beírva" | `tail -1 06-Audits/<event>-log.jsonl | jq` |
| "Test pass" | `pytest -x --tb=short` (exit 0) |
| "Embed friss" | `vault-embed-freshness` (no stale) |
| "Visual rendering OK" | Chrome DevTools MCP screenshot + diff |

## Anti-pattern

- ❌ **"Biztos benne van"** narratív állítás verifikáció nélkül
- ❌ **`11.11note` event mint disk-state** — event != disk state, event-only claim hibás
- ❌ **`git commit -m "X kész"` `git status` nélkül** — túl-claim, lehet "untracked" fájl
- ❌ **Lighthouse-100-claim** lokális run nélkül — production CDN/cache eltérhet
- ❌ **"Test pass" claim** `--last-failed`-del — csak az utolsó failed-eket futtatta, nem fullsuite

## Buktatók

- ⚠️ **`vault-ko-query "<x>"` substring-match** — `warm` matchel `warmstart`-ra is; használj word-boundary regex
- ⚠️ **NBSP a fájlnévben** — `ls "Bérgépek 2.xlsx"` failel mert NBSP; `find . -name "*ér*"` glob ([MEMORY](/root/.claude/projects/-root/memory/MEMORY.md))
- ⚠️ **Auto-save 10-perces commit-okkal** — `git log` lassú, használj `--since="10 min ago"`
- ⚠️ **Time-sync drift** — multi-host audit-log timestamp diff; UTC ISO mindig ([audit-log-append-only-pattern](audit-log-append-only-pattern.md))

## Mikor használd

| Kontextus | Verifikáció kötelező? |
|-----------|----------------------|
| Session-close | ✅ minden hivatkozott path-ra `ls` |
| Auto-prop crystallization | ✅ pre-state + post-state cross-check |
| Sprint-end retrospective | ✅ minden epic-state DB-from |
| Code-review | ✅ tests + smoke + manual |
| ADR-publikálás | ✅ referenciák valóban léteznek |
| Daily note | ⚠️ light verification |
| Brainstorm | ❌ nem szükséges (kreatív munka) |

## Kapcsolódó

- [[bmad-cross-machine-artifact-verification]] — session-close artifact verify
- [[vendor-feature-verify-before-workaround]] — verify vendor feature ELŐTT workaround
- [[audit-log-append-only-pattern]] — verification mint audit-event
- [[multi-layer-safety-gate]] — verify mint Layer 4
- [[layered-eval-cascading-pattern]] — verify-cascade eval
- [[top-k-cross-source-corroboration]] — cross-source verify
