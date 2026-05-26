---
name: vault-plugin-install Day-0 plugin marketplace
type: adr
status: proposed
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/adr", "#project/sv", "plugin-marketplace", "v1.0.15-follow-up", "safety", "supply-chain"]
related:
  - "[[../11-wiki/external-skill-cherry-pick]]"
  - "[[../11-wiki/claude-code-harness-blocks]]"
  - "[[../00-Meta/vault-plugin-manifest-schema]]"
  - "[[../11-wiki/vault-plugin-marketplace-pattern]]"
---

# vault-plugin-install Day-0 — Plugin Marketplace v1

The third of the 2026-05-25 Big Bet Day-0 trio. Builds on the v1.0.15 foundation (`vault-plugin-discover` + `vault-plugin-safety-scan`) to add a single primitive: **install a third-party `vault-*` plugin with a registry + signature + safety-scan check**, replacing the current "symlink-by-hand" pattern.

## Context

Today there are 91 `vault-*` binaries on PATH; ~62 write to `06-Audits/`. The user has cherry-picked a handful from external sources (ECC plugin, GitHub repos) by symlinking manually — see [[../11-wiki/external-skill-cherry-pick]] for that pattern. This works but has friction:

- No record of where each external binary came from
- No way to verify the binary hasn't been swapped (no digest check)
- Safety-scan exists (`vault-plugin-safety-scan`) but isn't wired into the install step — it's a separate audit
- Uninstall is "find the symlink and rm it"

A "marketplace" doesn't have to mean a centralized SaaS. A registry file + a single install CLI is enough for a single-user vault that lets the user say "install this plugin" instead of "symlink this binary, run the scan, hope it's the right version".

## Decision

Land `vault-plugin-install` Day-0 with the minimum viable shape:

- **Registry stub** (`~/.vault-plugins/registry.json`) — JSON catalog, empty today, designed for future entries.
- **Install ledger** (`~/.vault-plugins/installed.json`) — what's installed locally, with digest + safety-heat + symlink path for uninstall.
- **`vault-plugin-install install <name> --from-file <path>`** — local install with copy → digest → safety-scan → symlink. Dry-run is the **default**; mutations require `--apply`.
- **`vault-plugin-install install <name>` (registry-fetch path)** — Day-0 returns "not implemented", points at `--from-file`. W1+ wires network fetch.
- **`vault-plugin-install uninstall <name> [--apply]`** — symmetric removal.
- **`vault-plugin-install list`** + **`vault-plugin-install registry`** — read-only inspection.
- **HIGH-heat block** — if safety-scan flags HIGH, install refuses without `--allow-high-heat`.

## What Day-0 lands today

1. `/usr/local/bin/vault-plugin-install` (symlink to `.vault-tools/scripts/vault-plugin-install.py`, ~280 LOC)
2. `~/.vault-plugins/registry.json` + `~/.vault-plugins/installed.json` (both initialized empty)
3. Manifest + registry schema spec: [[../00-Meta/vault-plugin-manifest-schema]]
4. Usage wiki: [[../11-wiki/vault-plugin-marketplace-pattern]]
5. Smoke-tested: install dry-run on `/usr/local/bin/vault-doctor` correctly derives heat=LOW (1 finding) from `vault-plugin-safety-scan` output, prints install plan, exits 0 without mutating anything.

## What Day-0 does NOT do

- Network fetch from registry `source` URLs — local-file only
- Registry-edit subcommand (`vault-plugin-install registry add ...`) — manual JSON-edit today; W2+
- GPG signature verification — SHA-256 only; layered GPG comes W2+ if anyone publishes external plugins
- Dependency resolution — no plugin depends on another today; revisit if it changes
- Auto-uninstall of plugins flagged HIGH by a later safety-scan cron — passive flagging only
- MCP-server / hooks plugin integration — these are higher-risk and deferred to W2+

## Acceptance criteria

- [x] `vault-plugin-install install foo --from-file /path` dry-run prints plan, computes digest, runs safety-scan, exits 0 without mutations
- [x] `--apply` copies + symlinks + writes installed.json atomically (verified with `vault-doctor-test` smoke)
- [x] HIGH heat blocks install unless `--allow-high-heat` (logic in place; not yet smoke-tested against a real HIGH binary)
- [x] `uninstall --apply` removes symlink + storage + installed.json entry symmetrically
- [x] `list` and `registry` show the right state in text + JSON formats
- [ ] **W1:** first registry entry — pick one of the user's external-cherry-pick plugins (e.g. from the ECC plugin set), add to `registry.json` manually, install via `vault-plugin-install foo`. Verifies the registry-fetch flow.
- [ ] **W2:** network fetch implementation (`curl --fail` + content-type check + size cap)
- [ ] **W3:** GPG signature support (optional layered trust)

## Why a per-plugin storage dir instead of just symlinking the source

The install copies the source into `~/.vault-plugins/<name>/<name>` and symlinks from there. Two reasons:

1. **Source-file ownership**: the original source might move, be deleted, or be a temp file. After install, the vault owns its copy and can uninstall cleanly.
2. **Per-plugin co-location**: future W3 schema adds `dependencies`, `mcp_servers`, `hooks` fields — those need a directory to live in (config files, attestations). Reserving the per-plugin dir today avoids a schema migration later.

## Trust model

Single-user, single-vault, single-trust-domain. The user is the publisher AND the consumer of every plugin. Day-0 trust:

- The source path is one the user has personally accessed (`--from-file <local path>`).
- The SHA-256 digest is recorded at install. If the symlink target changes silently, future audits can detect.
- The safety-scan is the only automatic gate — heat HIGH blocks, MID warns, LOW passes.

Once registry network-fetch lands (W2), trust expands to "the user explicitly added the registry entry with a known good source URL + digest". Still single-trust-domain, but the registry becomes the user's curated allowlist.

If we ever publish vault plugins for OTHERS to consume, the trust model needs a GPG signature layer + a key trust DB. Out of scope today.

## Rollback

`vault-plugin-install` is additive — removing the symlink + the two JSON files restores the prior state. The existing 91 vault-* binaries on PATH are untouched (they're symlinks created by the vault's own install scripts, not by `vault-plugin-install`).

## References

- [[../11-wiki/external-skill-cherry-pick]] — the manual symlink pattern this builds on
- [[../11-wiki/claude-code-harness-blocks]] — sibling supply-chain safety pattern
- [[../00-Meta/vault-plugin-manifest-schema]] — schema spec
- [[../11-wiki/vault-plugin-marketplace-pattern]] — usage walkthrough
- v1.0.15 CHANGELOG entry — `vault-plugin-discover` + `vault-plugin-safety-scan` landing
