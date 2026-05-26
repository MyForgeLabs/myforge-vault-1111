---
name: vault-plugin marketplace pattern
type: wiki
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/wiki", "#concept/plugin-marketplace", "v1.0.15-follow-up", "supply-chain", "safety"]
related:
  - "[[../07-Decisions/2026-05-25 vault-plugin-install Day-0 plugin marketplace]]"
  - "[[../00-Meta/vault-plugin-manifest-schema]]"
  - "[[external-skill-cherry-pick]]"
---

# vault-plugin marketplace pattern

`vault-plugin-install` is the install primitive for third-party `vault-*` binaries. Single-user, single-trust-domain, registry-backed, safety-scan-gated. Day-0 lands 2026-05-25.

## The four pieces

| Piece | Role |
|---|---|
| `~/.vault-plugins/registry.json` | catalog of known plugins (name → source URL + digest + metadata). Empty Day-0. |
| `~/.vault-plugins/installed.json` | what's installed locally (idempotency + uninstall record) |
| `~/.vault-plugins/<name>/<name>` | the executable, owned by the plugin system |
| `/usr/local/bin/<name>` | symlink so the binary is on PATH |

## Three install paths

### Path A — local file (Day-0 default)

```bash
# Dry-run preview
vault-plugin-install install vault-foo --from-file /tmp/vault-foo

# Apply
vault-plugin-install install vault-foo --from-file /tmp/vault-foo --apply
```

The install computes SHA-256, runs `vault-plugin-safety-scan`, prints heat (H/M/L/NONE), and creates the symlink atomically. The plugin lives at `~/.vault-plugins/vault-foo/vault-foo` and a symlink lands at `/usr/local/bin/vault-foo`.

### Path B — registry-fetch (W1+)

```bash
# Once the registry has the entry
vault-plugin-install install vault-foo

# Or specific version
vault-plugin-install install vault-foo --version 0.2.1
```

Day-0 returns "not implemented" with a pointer to Path A.

### Path C — uninstall

```bash
# Dry-run
vault-plugin-install uninstall vault-foo

# Apply
vault-plugin-install uninstall vault-foo --apply
```

Symmetric to install: removes the symlink, the storage file, and the `installed.json` entry. The per-plugin storage dir is removed if it ends up empty.

## Safety gates

Three layers, all run by `vault-plugin-install install`:

1. **SHA-256 digest** — if you pass `--expected-sha256 <hex>`, the actual digest must match. Registry entries (W1+) will always supply the expected digest, so the gate is automatic.
2. **`vault-plugin-safety-scan`** — risk-classifies the binary content. Heat=HIGH blocks install unless `--allow-high-heat`. Heat=MID/LOW prints the finding count but doesn't block.
3. **Symlink overwrite** — if `/usr/local/bin/<name>` already exists, install refuses unless `--force`. Protects the existing 91 vault-* binaries from accidental overwrite by a plugin sharing a name.

## Why this beats manual symlink

Before: `ln -sf /path/to/some/repo/vault-foo /usr/local/bin/vault-foo`.

| Problem with manual symlink | Solved by `vault-plugin-install` |
|---|---|
| No record of source location | `installed.json["vault-foo"].source_file` |
| No digest snapshot at install time | `installed.json["vault-foo"].sha256` |
| Safety-scan exists but isn't run on install | run automatically, heat in install record |
| Uninstall = "find symlink, remember path, rm both" | `vault-plugin-install uninstall <name> --apply` |
| Multiple ways to "install" (some by-hand, some by skill) | one CLI, one ledger |

## What's NOT in Day-0

- **Network fetch** — registry has `source: "https://..."` field but Day-0 returns "not implemented". W2+ wires `curl --fail` with content-type + size caps.
- **GPG signatures** — only SHA-256 today. W2+ adds optional `signature` field to registry entries.
- **Dependencies** — no plugin depends on another today.
- **Plugin-bundled MCP servers / hooks** — these are HIGH-heat by default ([[claude-code-harness-blocks]]) and need a separate W2+ flow with explicit per-resource user confirm.
- **Auto-uninstall on safety regression** — a future heat re-scan cron is passive (warns); never auto-removes.

## Smoke test (Day-0, verified)

```
$ vault-plugin-install install vault-doctor-test --from-file /usr/local/bin/vault-doctor
Install plan for 'vault-doctor-test':
  source:        /root/obsidian-vault/.vault-tools/scripts/vault-doctor.py
  storage:       /root/.vault-plugins/vault-doctor-test/vault-doctor-test
  symlink:       /usr/local/bin/vault-doctor-test
  sha256:        eee5543133c5b1b35650851b10e7d6e5a99a6de8ac14e28d7e6a2af574ecd851
  digest match:  (no expected digest — skipped)
  safety-scan:   heat=LOW (1 finding(s): H0/M0/L1)

(dry-run — use --apply to actually install)
```

The dry-run path is the always-safe entry point. `--apply` is opt-in for the actual install.

## Future: a small public registry?

If the vault eventually publishes plugins others might want to use, the registry becomes a public-facing JSON file:

- Hosted on GitHub Pages (`https://myforgelabs.github.io/myforge-vault-1111/registry.json`)
- Includes GPG signature in each entry
- Verified against a small key-trust DB on first install
- `vault-plugin-install registry refresh` pulls the latest registry

This is out of scope until the marketplace is anything other than "the user's own external cherry-picks".

## See also

- [[../07-Decisions/2026-05-25 vault-plugin-install Day-0 plugin marketplace]] — binding ADR
- [[../00-Meta/vault-plugin-manifest-schema]] — JSON schema for registry + installed
- [[external-skill-cherry-pick]] — the prior pattern this replaces (symlink-by-hand)
- [[claude-code-harness-blocks]] — sibling supply-chain safety pattern
- v1.0.15 deliverables — `vault-plugin-discover` + `vault-plugin-safety-scan` (the foundation)
