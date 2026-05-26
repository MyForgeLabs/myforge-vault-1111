---
name: vault umbrella CLI
description: A single `vault <cat> <sub> [args]` dispatcher wrapping ~80 `vault-*` binaries. Category-grouping + help-search + default-binary-fallback + bash-completion turns a hostile-to-newcomers tool-pile into a discoverable surface.
type: wiki
created: 2026-05-21
updated: 2026-05-25
tags: ["#type/wiki", "cli", "discoverability", "onboarding"]
---

# vault umbrella CLI

## Why

The vault accumulated **~80 `vault-*` binaries** over a year — `vault-ko-query`, `vault-graph-extract`, `vault-search-fusion`, `vault-crystallize-monitor`, `vault-schema-migration-victim-audit`, and so on. On a fresh shell, `vault-<TAB>` autocomplete drops a wall of 80 lines.

For a new user (or new vault-clone on a fresh machine), this is hostile. Three specific failure modes:

1. **Discovery** — "I want to search the vault" → no obvious starting point among 80 names
2. **Naming-collision overload** — `vault-graph-query` vs `vault-ko-query` vs `vault-search` all sound like "search"
3. **Forgotten tools** — `vault-stats-generator` exists but only the author remembers it

The `vault` umbrella CLI is a thin **dispatcher + categorizer** that fixes all three.

## How

`vault` is a single Python script at `/usr/local/bin/vault` that:

- Maintains a `CATEGORIES` dict mapping `(category, sub-command) → (full-binary-name, one-line-desc)`
- With no args: lists categories + counts
- With one arg: lists tools in that category
- With two+ args: dispatches to the matching `/usr/local/bin/vault-*` binary, forwarding all remaining args

```bash
$ vault
vault — unified umbrella for ~80 vault-* tools

Categories:
  ko               14 tool(s)
  graph             9 tool(s)
  search            5 tool(s)
  audit            11 tool(s)
  embed             6 tool(s)
  crystallize       2 tool(s)
  session           6 tool(s)
  skill             2 tool(s)
  wiki              5 tool(s)
  nb                3 tool(s)
  net               2 tool(s)
  infra            18 tool(s)

$ vault audit
vault audit — 11 tool(s):

  vault audit  plugin-hooks    marketplace plugin instruction-injection scan
               (→ vault-plugin-hooks-audit)
  vault audit  mcp             MCP server registration safety scan
               (→ vault-mcp-audit)
  ...

$ vault audit mcp --json
# → vault-mcp-audit --json
```

## Three discoverability features

### 1. `vault help <pattern>` — search by description

```bash
$ vault help "broken"
vault help — 3 match(es) for /broken/:

  vault audit      broken-wikilinks        broken-wikilink scanner
  vault wiki       broken-wikilinks        broken-wikilink scanner (alias)
  vault infra      cleanup                 weekly vault-cleanup (broken-links, lint, ...)
```

The pattern is a regex applied to category + sub + full-name + description. Found something? Run it.

### 2. Default-binary fallback

Categories with a `("", full-name, desc)` "default" entry handle the case where the user types `vault <cat> "first arg"` (e.g. `vault search "memgraph multi-namespace"` → `vault-search "memgraph multi-namespace"` — no double-naming required).

```python
# search category:
"search": [
    ("",         "vault-search",         "semantic search (Memgraph + bge-m3 hybrid)"),
    ("fusion",   "vault-search-fusion",  "RRF hybrid: vault-search + agentmemory"),
    ("health",   "vault-search-health",  "search-pipeline health-check"),
    ...
],
```

`vault search "X"` → `vault-search "X"`. `vault search fusion --top-k 1` → `vault-search-fusion --top-k 1`.

### 3. Auto-categorized `other`

Any `vault-*` binary on PATH that isn't in the `CATEGORIES` map appears under `vault other`. Forgotten tools become visible.

```bash
$ vault other
vault other — 0 uncategorized tool(s):
Add to CATEGORIES in vault.py to group them.
```

Currently zero (all 80 tools are categorized), but the next `vault-foo` binary that lands will show up here until manually grouped.

## Adding a new tool

When you ship a new `vault-<name>` binary, the umbrella picks it up automatically (it appears under `vault other`). To group it into a category, add one line to `CATEGORIES` in `/root/obsidian-vault/.vault-tools/scripts/vault.py`:

```python
"<category>": [
    # existing entries...
    ("<sub-name>", "vault-<full-name>", "<one-line desc>"),
],
```

That's it. Autocomplete and help-search update on the next invocation.

## What the umbrella does NOT do

- **Does not wrap or proxy** — it `subprocess.run`s the real binary directly. Any arg is forwarded verbatim. No "magic" interpretation.
- **Does not duplicate help** — the real binary's `--help` is what shows. The umbrella's own `--help` shows the dispatcher's surface.
- **Does not auto-update CATEGORIES** — explicit grouping requires a human-curated decision (which category does this belong to?).
- **Does not gate** — no permission checks, no warnings, no rate-limiting. The umbrella is pure shorthand.

## Bash-completion (LANDED 2026-05-25)

```bash
$ vault <TAB>
ko  graph  search  audit  embed  crystallize  session  skill  wiki  nb  net  infra  help  stats

$ vault audit <TAB>
plugin-hooks  mcp  schema-migration  conflicts  continuous  orphan-wiki
broken-wikilinks  adr-aging  atomic-lint  auto-disable  coherence
```

### How it works

A small `vault --complete <mode>` introspection-flag emits flat machine-readable lists:

- `vault --complete categories` → cat-names + `help`, `stats`, `other`
- `vault --complete subs <cat>` → sub-commands for that category

The bash-completion script ([`.vault-tools/scripts/vault-completion.bash`](../.vault-tools/scripts/vault-completion.bash)) shells out to these on every TAB. Python startup is ~50ms cold, faster warm — acceptable latency for interactive completion. An escape hatch `VAULT_COMPLETE_STATIC=1` falls back to a hardcoded category list (drift-prone but zero-latency) for slow machines.

### Install

```bash
# Canonical (if /etc/bash_completion.d/ is sourced):
ln -sf /root/obsidian-vault/.vault-tools/scripts/vault-completion.bash \
       /etc/bash_completion.d/vault

# Direct (no dep on system bash-completion loader):
echo 'source /root/obsidian-vault/.vault-tools/scripts/vault-completion.bash' \
     >> ~/.bashrc
```

Both are wired up. The direct `~/.bashrc` source is the load-bearing one on this server, since the system `bash-completion` loader is commented out in `/etc/bash.bashrc`.

### Design choices

- **Only completes 2 positions** — `vault <cat>` and `vault <cat> <sub>`. After that the dispatched tool handles its own args; we don't try to introspect every `vault-*` binary's `--help`.
- **Lazy** — no caching, no shell-startup work. The first TAB pays the Python cold-start; subsequent are cheap.
- **No alias completion** — `vault help` and `vault stats` are completed as cat-tokens at position 1, but get no further completions at position 2 (they take a regex / no args respectively).

## Anti-patterns

> [!warning] Resist scope creep

1. **Don't add aliases endlessly** — `vault s` for search, `vault q` for query, etc. The umbrella exists for **discoverability**, not brevity. Users who type fast already know the full names.
2. **Don't bake business logic into the dispatcher** — keep `vault.py` thin. All real logic stays in the `vault-*` binaries.
3. **Don't let CATEGORIES drift** — every new `vault-*` binary should land in a category within a week. Otherwise `vault other` becomes the only useful command.
4. **Don't try to subsume `11.11*` family** — session-management has its own protocol (see [[11.11-session-protokoll]]). Not every CLI belongs under `vault`.

## Compounding leverage

Three places this pays off as the vault grows:

1. **New contributors** — `vault` (with no args) is now the canonical "where do I start" answer. README quickstart can say: install, run `vault`, read the categories.
2. **Future audit-CLIs** — each new `vault-<class>-audit` lands in the `audit` category. Discoverability for the [[audit-cli-as-credibility-vehicle]] pattern.
3. **Tool consolidation** — when two tools accumulate overlapping responsibilities, `vault <cat>` listing surfaces the redundancy ("we have 5 search tools — are they all needed?").

## Related

- [[Auto-context-loading]] — sibling onboarding asset (vault-context-loading at session-start)
- [[audit-cli-as-credibility-vehicle]] — meta-pattern for the `audit/` category's content
- [[11.11-session-protokoll]] — the orthogonal session-management family
- [[memory-md-overflow-management]] — sibling discoverability limit (MEMORY.md ≤24.4KB)
