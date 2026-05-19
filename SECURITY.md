# Security policy

## Supported versions

Only the latest tagged release receives security fixes.

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ |
| < 1.0   | ❌ |

## Reporting a vulnerability

Email **peti.markovics@gmail.com** with subject `SECURITY: myforge-vault-1111`.
Please **do not** open a public issue for security bugs.

I aim to:

- Acknowledge within **48 hours**
- Patch high-severity issues within **14 days**
- Coordinate public disclosure with the reporter

## What's in scope

- Prompt-injection or jailbreak vectors against the G-Eval scorer prompts
  (in `.vault-ko/prompts/`) that escape the 4-layer safety-gate
- Memgraph Cypher injection through `vault_mcp_server.py`'s `memgraph_cypher`
  tool (read-only RPC; bypass of the mutation-keyword filter is in scope)
- Path traversal in any vault script that takes user-supplied paths
- Privilege escalation from a `vault-*` cron job (running as root by design)
  to outside `~/obsidian-vault/`
- Vault content exfiltration via the MCP STDIO transport (note: the
  transport is local-only by design; reports of "could be exposed remotely
  if mis-configured" are accepted but lower-severity)

## Out of scope

- Issues that require write access to your local Memgraph instance
  (Memgraph is local, you control it)
- Prompt-injection in vault content **you authored yourself**
- Resource exhaustion via local CLI agents (you control the agents)
- The `--apply` modes in `vault-sleep-consolidate` /
  `vault-browser-history-ingest` / `11.11crystallize` requiring an explicit
  env-var (`VAULT_*_APPLY=1`) — this is the intended safety gate, not a bug

## Hardening recommendations for operators

- Keep `vault-search.service` on a Unix socket with `0o660` perms (default)
- Do **not** expose `/run/vault-search.sock` over a network without an auth
  shim — the daemon assumes local trusted callers
- The `bmad-vault-watch@*.service` template has `MemoryMax=512M`; raise only
  if profiling shows actual usage above that
- Review `~/.vault-config/crystallize-disable.flag` — a watchdog-set flag
  blocks the `--apply` mode for crystallize until manually removed

## Credit

Reporters who follow coordinated disclosure get a credit in the next
release's `CHANGELOG.md` (or anonymous, your choice).
