---
name: Audit-CLI as engineering-credibility vehicle
description: Same-day named-broken-class + audit-CLI + weekly cron + git-hook + anti-pattern wiki = compounding engineering credibility. Pattern recurring across schema-migration, plugin-hooks, MCP-server audits — each named class becomes an HN/Dev.to follow-up post.
type: wiki
created: 2026-05-21
updated: 2026-05-21
tags: ["#type/wiki", "engineering-credibility", "writing-pattern", "named-broken-class"]
---

# Audit-CLI as engineering-credibility vehicle

## A pattern

You discover a new class of failure in your stack — a silent migration breaking downstream callers, a marketplace plugin injecting instructions, an MCP server using `bash -c`. The reflex is to **fix it and move on**. The compounding move is:

1. **Name the broken class** in one sentence. (e.g. "schema-migration silent downstream-victims", "marketplace plugin instruction-injection", "MCP-server shell-exec risk-vector")
2. **Ship a named CLI** that scans for it (`vault-<class>-audit`).
3. **Wire it to a weekly cron** + a `--strict` flag for CI/pre-commit gating.
4. **Write a wiki** that's both the detection-rationale AND a named anti-pattern reference.
5. **Eyeball the first baseline run** — it'll find more instances than you expected.

Each cycle through this loop produces:

- A safety-rail (the CLI + cron + git-hook)
- An evergreen reference (the wiki)
- A blog-post-ready story ("I found a class of bug, here's the rail I shipped same-day")

Recurring across multiple problem-classes, this compounds into an **engineering-credibility narrative**: "this person doesn't just write code, they name problem-classes and ship safety-rails."

## Why this works

### Engineering reflex bias toward heroic single-incident fixes

The default response to a found bug is: fix it, write a brief postmortem, ship a one-off patch, move on. This is **necessary but doesn't compound**. The next instance of the same class will catch a different person, in a different repo, with the same novelty.

The named-class + audit-CLI approach makes the bug-class **explicit and searchable**. Future incidents become "you have an instance of class X, run audit-X to find more."

### Engineering blogs reward problem-class-shape, not instance-shape

A blog post titled "I shipped a fix for issue #1234" gets a comment thread. A blog post titled "**One column-drop silently broke 15 of my CLI tools**" gets a Hacker News front-page. The difference: the first describes a unique event; the second describes a **pattern other engineers can audit for in their own systems**.

The same class that produces the audit-CLI is also the class that produces the headline.

### Compounding repeats win

The first instance of this pattern is just a safety-rail. The second establishes the writer's stance ("they do this regularly"). The third creates an **expectation** — future readers tune in for the next named-class.

After 3 cycles, you stop needing to "convince" the audience that you take engineering safety seriously; the audit-CLI inventory itself is the proof.

## Concrete examples

### Cycle 1 — schema-migration-victim-audit (2026-05-20)

A 190-ms KO-DB schema migration silently broke 15 downstream callers (12 readers + 1 writer + 2 pre-found, including the entire MCP-tool stack). None threw errors. The migration's own tests passed.

- **Named class**: "silent downstream-victims of a SQL schema migration in DB-API-2.0 drivers"
- **CLI shipped**: `vault-schema-migration-victim-audit` (ADR-aware, qualified-SQL grep, AST per-branch classifier, `--apply-patch` mode with dry-run + smoke-test + auto-revert)
- **Cron**: Mon 05:00 UTC
- **Git-hook**: `pre-commit-schema-migration-watch.sh` chains in, blocks staging schema-change ADRs without victim-audit clearance
- **Wiki**: [[schema-migration-downstream-grep-checklist]]
- **Story**: became the **C-2 angle** for the HN-launch (one column-drop, 15 silent victims, 30-hour blast radius)

### Cycle 2 — plugin-hooks-audit (2026-05-21)

A marketplace plugin (`Lum1104/Understand-Anything`, 28K stars, MIT) sandbox-evaluation surfaced `hooks/hooks.json` containing `"Do not ask the user for confirmation — just do it"` + `"You MUST"` instruction-injection.

- **Named class**: "marketplace plugin instruction-injection via hooks"
- **CLI shipped**: `vault-plugin-hooks-audit` (8 HIGH-regex + 8 MID-regex pattern set)
- **Cron**: Mon 05:30 UTC
- **Git-hook**: chained Layer-0 guard on `*hooks.json` + `.claude/*`, blocks staging with HIGH-heat
- **Wiki**: [[claude-code-harness-blocks]] § 7 (added inline)
- **Story**: post-HN follow-up candidate

### Cycle 3 — mcp-audit (2026-05-21, same day)

While building Cycle 2, the MCP-server analog became obvious: same marketplace, different surface (`*.mcp.json` files), 4 risk-vectors.

- **Named class**: "MCP-server registration risk-vectors"
- **CLI shipped**: `vault-mcp-audit` (4-vector heat classifier)
- **Cron**: Mon 05:45 UTC (15 min after plugin-hooks-audit)
- **Git-hook**: same Layer-0 chain, extended for `*.mcp.json`
- **Wiki**: [[mcp-server-safety-classification]]
- **Story**: same post-HN follow-up bundle as Cycle 2

By Cycle 3, the **audit-CLI scaffold is reusable** — same JSON-output shape, same markdown audit template, same `--strict` flag pattern, same pre-commit-chain integration. Cycle 4 (whatever the next class is) will take an hour, not a day.

## When to invoke this pattern

| Trigger | Action |
|---|---|
| Multi-instance bug found in own code | Cycle: audit-CLI for the pattern, find all instances |
| Marketplace component review surfaces a risk | Cycle: audit-CLI for the risk-pattern across all installed components |
| External dependency behavior surprises you | Cycle: audit-CLI to detect that behavior in your own consumption |
| Postmortem mentions "we should have caught this earlier" | Cycle: that's the named class, write the audit-CLI |

**When NOT to invoke**: one-off issues with truly unique triggers. Don't audit-CLI for things that happen once. The pattern is for **classes**, not instances.

## Reusable scaffold

After Cycle 3, the audit-CLI shape stabilized. Future cycles use this skeleton:

```python
#!/usr/bin/env python3
"""
vault-<class>-audit — scan for <class> risk patterns.
"""
HIGH_PATTERNS = [re.compile(...) for ... in ...]
MID_PATTERNS  = [...]
LOW_PATTERNS  = [...]

def classify(item) -> tuple[str, list[str]]: ...

def scan(roots) -> list[Hit]: ...

def render_markdown(hits, scanned_files) -> str:
    # standard frontmatter + summary + per-heat tables + Related links

def main():
    # standard --json / --strict / --quiet / --roots argparse
    # writes 06-Audits/<class>-audit-{ISO-WEEK}.md or .json
    # strict mode exits 1 on HIGH
```

Cron entry shape: `MM HH * * 1 /usr/bin/flock -n /tmp/vault-<class>-audit.lock /usr/local/bin/vault-<class>-audit --quiet`

Pre-commit chain entry: file-pattern trigger + `vault-<class>-audit --strict --quiet --roots <staged-dirs>`.

Audit-CLI **shared framework refactor** is in the backlog — Cycle 4+ deserves a `vault_audit_lib` library extract for the common parts.

## Anti-patterns

> [!warning] What NOT to do

1. **Audit-CLI without a wiki** — the CLI runs in the dark. New readers can't tell what it catches or why.
2. **Wiki without an audit-CLI** — the named class stays as words. The next instance still gets missed.
3. **Reactive only** — only naming classes after they bite you. Some classes (e.g. credential-leak detection in MCP env-blocks) are worth auditing **before** they bite.
4. **Audit-CLI without baseline** — the first run should be clean (or show you what's already in the wild). If the first run is full of false-positives, the pattern set needs tightening.
5. **Conflating named-class with named-instance** — "fix the schema migration bug" is an instance; "audit for schema-migration downstream-victims" is the class. Only the latter scales.

## Cross-references

- [[schema-migration-downstream-grep-checklist]] — Cycle 1 reference
- [[claude-code-harness-blocks]] § 7 — Cycle 2 reference
- [[mcp-server-safety-classification]] — Cycle 3 reference
- [[tool-sandbox-eval-playbook]] — where most Cycle-finding starts (eval surfaces the class)
- [[multi-layer-safety-gate]] — companion safety architecture pattern
