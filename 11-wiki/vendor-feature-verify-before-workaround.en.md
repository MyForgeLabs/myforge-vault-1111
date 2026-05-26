---
name: vendor-feature-verify-before-workaround
description: Before writing a workaround script for an infrastructure feature, verify the vendor's current capabilities — 30 minutes of release-note reading can save days
type: wiki
lang: en
translated_from: vendor-feature-verify-before-workaround
created: 2026-05-17
updated: 2026-05-18
tags: ["#type/wiki", "engineering-discipline", "lesson", "sprint-planning"]
---

# Vendor feature verify — before workaround

## The pattern

During sprint planning, when the vendor docs say "feature X not supported", **before starting workaround-script implementation:**

1. Check the **current version**'s release notes (especially if 3+ months have passed since you last read the vendor docs)
2. Check the CHANGELOG or `[ENTERPRISE-ONLY]` flags next to the feature
3. Try the feature in a `docker-shell` or quick smoke test: if you get a `SyntaxError` on valid syntax, it's *probably* unsupported; if you get a different error (`OOM`, `Capacity exceeded`), it is SUPPORTED, just needs config

**ROI:** 30 minutes of release-note reading vs days of workaround development.

## Live example — Memgraph CE 3.9.0 native vector-index

A search/retrieval sprint started with a numpy-cosine workaround pattern because the vault docs (read months ago) said Memgraph CE did not support a native vector index. **Verified later:** the 3.9.0 release introduces native `CREATE VECTOR INDEX` syntax + `vector_search.search` procedure. Days of workaround development could have been saved.

Migration result: **280× speedup** (numpy 280ms → native 1ms mean). See [[memgraph-ce-feature-limits]].

## When to apply

- ✅ Any 6+ month roadmap item before the release cycle (the vendor may have implemented it meanwhile)
- ✅ Workaround scripts that would require >1 day of effort (verify ROI dominates)
- ✅ Open-source projects — GitHub release notes + CHANGELOG mandatory pass

## When NOT to apply

- ❌ Trivial workaround (<1 hour) — faster to write than to read the docs
- ❌ Closed-source vendor with no release notes (verify happens when the bill arrives)

## Related

- [[sprint-day-0-skeleton-first]] — skeleton-first principle this slots into
- [[memgraph-ce-feature-limits]] — live example
