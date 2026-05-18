---
name: verification-step-before-claim
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/eval", "#topic/discipline", "#pattern/anti-hallucination"]
lang: en
translated_from: verification-step-before-claim.md
---

# Verification step before any claim

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[verification-step-before-claim]] (Hungarian version).

## TL;DR

Before ANY claim of "done", "completed", "working", "solved", run an **explicit verification step**: filesystem `ls`, `curl` smoke, `git log`, audit-log query, `ps` check, reference-fact match. Anti-hallucination / anti-event-vs-disk-state drift. Cross-source: 53+ supporting facts across 3 source types. **The single most frequent evergreen pattern in this knowledge base.**

## Background (3+ source evidence)

- **Cross-machine artifact verification:** an event notification ≠ disk state; at session close, `ls` every referenced `/root/...md` path
- **Feedback / claims verification:** before a UX or SEO opinion, verify on the reference (Lighthouse score, screenshot), not just on general best practices
- **Backup verification step:** UpdraftPlus `wpcore.zip` empty → verify BEFORE migration; if empty → `wp core download --force --skip-content`
- **Vendor feature verify before workaround:** Memgraph CE 3.9.0 native vector-index 280× speedup — VERIFY the feature first, don't workaround with numpy-cosine
- **Multi-page PDF callout check:** before claiming a "missing callout", check `figures>1` (it may be on another page)
- **Silent fail detection:** in voice-chat pipelines, silent-fail detection is a mandatory verification step
- **Bug universality verification:** before claiming a "reusable pattern", verify reproducibility on another browser/OS

## Pattern

```
Claim ──> "X is done / works"
            │
            ▼
        Verification step (mechanical, automatable)
            │
            ├─ ls / find — does the file exist?
            ├─ curl / smoke endpoint — 200 OK?
            ├─ git log — is the commit really in there?
            ├─ ps aux | grep — process running?
            ├─ audit-log query — entry really written?
            ├─ DB query — fact really in the DB?
            └─ screenshot / diff — visually correct?
            │
            ▼
        If ✓ — claim may proceed
        If ✗ — FIX FIRST, then claim
```

## Architectural rules

1. **Mechanical verification > narrative explanation** — `ls path` output > "I'm sure it's in there"
2. **Verification in the claim's Output** — session-file `## Verification` section or commit message `Verified: <bash output>`
3. **Cross-source corroboration** — if 2 sources disagree, DO NOT claim, mark `[conflict: see audit]`
4. **Session-close ritual on every reference** — explicit `ls` for every artifact path
5. **Bug-universality** — verify a feature claim in at least 2 environments (browser-OS pair, or local-prod) before generalizing
6. **Verification in the audit log** — per the audit-log-append-only pattern

## Verification-type → tool matrix

| Claim | Verification |
|-------|-------------|
| "File exists" | `ls -la <path>` (file-size > 0) |
| "Commit is in" | `git log --oneline \| grep <hash>` |
| "Service running" | `systemctl status <unit>` or `ps aux \| grep` |
| "Endpoint live" | `curl -sI <url> \| head -1` (HTTP 200) |
| "Fact in the DB" | `db-query "<subject>" --json` |
| "Wiki exists" | `ls /path/to/wiki/<slug>.md` |
| "Audit entry written" | `tail -1 audit/<event>-log.jsonl \| jq` |
| "Tests pass" | `pytest -x --tb=short` (exit 0) |
| "Embeddings fresh" | `embed-freshness` (no stale) |
| "Visual rendering OK" | Chrome DevTools MCP screenshot + diff |

## Anti-pattern

- ❌ **"I'm sure it's there"** narrative without verification
- ❌ **Event-only as disk-state** — event ≠ disk state, event-only claims are wrong
- ❌ **`git commit -m "X done"` without `git status`** — over-claim risk; could be an "untracked" file
- ❌ **Lighthouse-100 claim** without a local run — production CDN/cache may differ
- ❌ **"Tests pass" claim with `--last-failed`** — only ran the last-failed set, not the full suite

## Pitfalls

- ⚠️ **`db-query "<x>"` substring match** — `warm` matches `warmstart` too; use word-boundary regex
- ⚠️ **NBSP in filenames** — `ls "Filename 2.xlsx"` fails because of NBSP; use `find . -name "*ame*"` glob
- ⚠️ **Auto-save with 10-min commits** — `git log` is slow, use `--since="10 min ago"`
- ⚠️ **Time-sync drift** — multi-host audit log timestamp diff; always use UTC ISO

## When to use

| Context | Verification mandatory? |
|---------|-------------------------|
| Session close | ✅ `ls` every referenced path |
| Auto-prop crystallization | ✅ pre-state + post-state cross-check |
| Sprint-end retrospective | ✅ DB state for every epic |
| Code review | ✅ tests + smoke + manual |
| ADR publishing | ✅ references really exist |
| Daily note | ⚠️ light verification |
| Brainstorm | ❌ not needed (creative work) |

## Audio overview

- EN narration (Charon voice): `[[.vault-nb/audio-overviews/verification-step-before-claim.en.mp3]]`
- HU narration (Kore voice): `[[.vault-nb/audio-overviews/verification-step-before-claim.hu.mp3]]`

Generated via Gemini 3.1 Flash TTS preview. ~1-2 minutes each. See [[gemini-3-1-flash-tts-pipeline]] for the pipeline.

## Related

- [[multi-layer-safety-gate]] — verify as Layer 4
- [[mgclient-autocommit-silent-rollback]] — silent-rollback verification example
- [[g-eval-bias-mitigation-pattern]] — independent eval signal
- [[subagent-fanout-context-aware-classification]] — manual sampling as verification
