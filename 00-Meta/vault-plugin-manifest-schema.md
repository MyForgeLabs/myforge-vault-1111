---
name: vault-plugin manifest + registry schema
type: spec
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/spec", "meta", "plugin-marketplace", "registry"]
related:
  - "[[../07-Decisions/2026-05-25 vault-plugin-install Day-0 plugin marketplace]]"
  - "[[../11-wiki/vault-plugin-marketplace-pattern]]"
---

# vault-plugin manifest + registry schema

Spec for the vault plugin system. Two JSON documents live under `~/.vault-plugins/`:

- `registry.json` — declarative catalog of known plugins (where to fetch, expected digest)
- `installed.json` — what's currently installed locally (idempotency + uninstall metadata)

Both are read/written by `vault-plugin-install`. The format is intentionally minimal — JSON, not YAML, no schemas-as-code, no registry mirror. Single-user vault, single-trust-domain.

## File locations

```
/root/.vault-plugins/
├── registry.json              # central catalog (name → metadata)
├── installed.json             # what's installed (idempotency + audit)
└── <plugin-name>/
    └── <plugin-name>          # the executable (mode 0755)
```

`/usr/local/bin/<plugin-name>` is a symlink to `~/.vault-plugins/<plugin-name>/<plugin-name>`.

The `$VAULT_PLUGIN_HOME` env-var overrides the default `/root/.vault-plugins/` (for testing under a worktree).

## `registry.json` schema

```jsonc
{
  "schema_version": 1,
  "generated_at": "2026-05-25",
  "plugins": {
    "<plugin-name>": {
      "version": "0.1.0",
      "source": "https://example.com/path/to/vault-foo",
      "sha256": "abcdef0123...",
      "summary": "One-line description shown by `vault-plugin-install registry`",
      "author": "name <email>",
      "license": "MIT",
      "homepage": "https://...",
      "added_at": "2026-05-25",
      "minimum_vault_version": "1.0.16"
    }
  }
}
```

**Required fields per plugin:** `version`, `source`, `sha256`, `summary`.
**Optional fields:** `author`, `license`, `homepage`, `added_at`, `minimum_vault_version`.

Day-0 (2026-05-25): registry is **empty**. Network-fetch from `source` is not implemented; install today goes through `--from-file <local-path>`. Registry exists so future entries can be added.

## `installed.json` schema

```jsonc
{
  "schema_version": 1,
  "installed": {
    "<plugin-name>": {
      "installed_at": "2026-05-25T21:18:00Z",
      "source_file": "/path/source-used-at-install",
      "sha256": "abcdef0123...",
      "safety_heat": "LOW",
      "stored_at": "/root/.vault-plugins/<plugin-name>/<plugin-name>",
      "symlink": "/usr/local/bin/<plugin-name>"
    }
  }
}
```

Written by `vault-plugin-install install --apply`. Removed by `vault-plugin-install uninstall --apply`.

## Plugin binary contract

A plugin is just an executable that follows the `vault-*` naming convention. There is no required structure beyond that, but plugins SHOULD:

- Have a one-line description in the first 5 lines (Python: docstring first line; shell: leading comment) — `vault-plugin-discover` extracts this
- Pass `vault-plugin-safety-scan` without HIGH findings (or document why the HIGH is intentional)
- Be idempotent for read operations (`--json`, `--help`, list-only modes)
- Make destructive operations explicit (require `--apply` flag, default dry-run)

## Install workflow (Day-0)

```bash
# Dry-run: preview the install plan
vault-plugin-install install vault-foo --from-file /tmp/vault-foo

# → Prints:
#     source / storage / symlink target / sha256 / safety heat
#     Then exits 0 (no changes)

# Apply: actually install
vault-plugin-install install vault-foo --from-file /tmp/vault-foo --apply

# → Copies to ~/.vault-plugins/vault-foo/vault-foo, symlinks to
#   /usr/local/bin/vault-foo, records in installed.json
```

Heat-gate: if `vault-plugin-safety-scan` classifies the binary HIGH, install refuses unless `--allow-high-heat` is passed.

Digest verification: if `--expected-sha256 <hex>` is passed, the actual digest must match or install refuses. Day-0: registry is empty so no automatic expected-digest; W1+ wires it in for `install <name>` (no `--from-file`).

## Future schema additions (W1+)

- `signature` — GPG-detached signature alongside `sha256`. Optional layered trust.
- `dependencies` — other vault-* plugins required. Resolve transitively.
- `mcp_servers` — MCP server registrations the plugin wants installed. Layered on `~/.claude/mcp.json` with user confirm.
- `hooks` — Claude/Codex/Gemini hook registrations. Strict heat-scan via `vault-plugin-hooks-audit` integration.
- `category` — auto-classify into vault umbrella `CATEGORIES` for `vault <cat>` completion.

## See also

- [[../07-Decisions/2026-05-25 vault-plugin-install Day-0 plugin marketplace]] — binding ADR
- [[../11-wiki/vault-plugin-marketplace-pattern]] — usage walkthrough
- [[../11-wiki/external-skill-cherry-pick]] — sister pattern (symlink-based without plugin manifest)
