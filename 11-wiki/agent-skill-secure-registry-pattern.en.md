---
name: Agent-skill secure-registry pattern
type: wiki
tags: ["#type/wiki", "skills", "supply-chain-security", "registry", "mcp", "governance", "lang/en"]
created: 2026-05-19
updated: 2026-05-19
lang: en
translated_from: agent-skill-secure-registry-pattern.md
source_repo: tech-leads-club/agent-skills
source_url: https://github.com/tech-leads-club/agent-skills
source_license: MIT (engine) + CC-BY-4.0 (skill-content)
---

# Agent-skill secure-registry pattern

A pattern for building a **security-first, auditable agent-skill distribution layer** as an alternative to open marketplaces. tech-leads-club/agent-skills implements a **curated, hardened library** concept — a direct answer to the Snyk 2026 Agent Threat Report claim that 13.4% of skills in public marketplaces contain critical vulnerabilities.

This is orthogonal to plain [[external-skill-cherry-pick]]: there a developer cherry-picks what they want; here a **maintainer-group's curated registry** is shared with many consumers and each skill carries a guaranteed security level.

## Explicit threat model (the critical part)

A hardened registry is meaningful only because it gives **concrete defense for concrete threats**. Four axes:

| Threat | Public marketplace | Hardened registry defense |
|---|---|---|
| **Malicious payload** | Obfuscated code, binary, "black box" instructions | 100% open-source, no-binary policy, every line auditable |
| **Credential theft** | Skill silently exfiltrates env-vars | Static analysis in CI blocks suspicious network calls / secret access |
| **Supply chain attack** | Author pushes malicious update to existing skill | Lockfile + SHA-256 content hash, code doesn't change without explicit upgrade |
| **Prompt injection** | Hidden instruction to hijack agent | Human curation, every prompt goes through manual code review |

The 4-layer threat-mapping is reusable in any distribution where code/instructions come from a 3rd-party.

## CLI defense-in-depth (5 independent layers)

Every installer-CLI operation goes through **ALL 5 layers**, defense-in-depth: a single bypass is not enough.

### 1. Input sanitization

```typescript
const sanitizeName = (name: string): string =>
  name
    .replace(/[/\\]/g, '')          // path separators
    .replace(/[\0:*?"<>|]/g, '')    // null-byte + Windows-forbidden
    .replace(/^[.\s]+|[.\s]+$/g, '') // leading/trailing dot/space
    .replace(/\.{2,}/g, '')          // collapse ".."
    .replace(/^\.+/, '')             // no leading dots (hidden file)
    .substring(0, 255) || 'unnamed-skill'
```

Blocked inputs: `../../../etc/passwd`, `skill\0name`, `/etc/passwd`, `skill:name`, `.hidden`, 300-char overflow.

### 2. Filesystem isolation (path-traversal protection)

```typescript
const isPathSafe = (basePath: string, targetPath: string): boolean => {
  const normalizedBase = normalize(resolve(basePath))
  const normalizedTarget = normalize(resolve(targetPath))
  return normalizedTarget.startsWith(normalizedBase + sep)
      || normalizedTarget === normalizedBase
}
```

**Both paths fully resolved** before comparison — symlink / `..` sequence / relative path eliminated. OS-specific `sep` (NOT hard-coded `/`) so `/allowed/dir../escape` tricks fail. Runs before every write/read/delete.

### 3. Symlink guard (TOCTOU-safe)

- **`lstat()` NOT `stat()`** — detects symlink without following it. Defeats Time-Of-Check-Time-Of-Use attacks.
- **Target validation** — for chained symlinks, resolves and checks the final target.
- **Loop detection** — `ELOOP` (circular chain) → forcibly remove.
- **Windows junctions** — instead of symlinks on Windows, better OS-level containment.

### 4. Lockfile integrity (`.agents/.skill-lock.json`)

- **Zod schema validation** — every read goes through strict schema; invalid entry → graceful migration, NOT silent corruption.
- **Atomic write** — `backup → tmp → atomic rename`. Process-kill mid-write leaves the old file intact.
- **SHA-256 content hash per skill** — tamper detection: if the on-disk skill file changes post-install, hash mismatch is detected before the next operation.
- **Removal authorization** — skill can't be removed without a lockfile entry; `--force` bypass is audit-logged.

### 5. Audit trail (append-only)

Every install/update/remove operation writes a JSONL record to `~/.config/agent-skills/audit.log`:

```json
{"action":"install","skillName":"codenavi","agents":["cursor"],"success":1,"failed":0,"timestamp":"2026-02-25T10:00:00Z"}
```

**Never overwritten, only appended**. Forensic record on every host. Same pattern as our [[audit-log-append-only-pattern]] vault-side in the propagation log.

## Security-scan in CI (Snyk Agent Scan)

Every skill SHA-256 hashed, result cached (`.security-scan-cache.json`). Next run: hash change → re-scan, hash same → cache hit. Fast enough to run per PR and per release. Release pipeline **requires the passing scan**.

**Fork PRs have no token access** — bridgeable via GitHub Merge Queue, optionally requiring the "Security Scan (merge queue)" check.

**False-positive allowlist** (`security-scan-allowlist.yaml`):

```yaml
entries:
  - skill: my-skill
    code: W011
    reason: "Trusted first-party API at api.example.com, reviewed 2026-01-01"
    allowedBy: github.com/username
    allowedAt: '2026-01-01'
    expiresAt: '2027-01-01'  # strongly recommended, expiry → auto-flag again
```

Without expiry the exception becomes "permanent technical debt". Hard-coded review cycle via config.

## MCP-server progressive disclosure

`@tech-leads-club/agent-skills-mcp` is deliberately a **narrower threat surface**:

- **Read-only** — no write access to the registry
- **No auth** — local stdio, not network-exposed
- **Path validation** — `fetch_skill_files` validates every path against the registry's `files[]` array, **impossible to fetch arbitrary URLs**
- **No local FS access** — only CDN fetch
- **stdout reserved for JSON-RPC** — all logs to stderr (protocol-corruption-safe)

4 tools: `list_skills`, `search_skills`, `read_skill`, `fetch_skill_files`. `list_skills` only on explicit user request — a **progressive disclosure** pattern protecting the context window: does NOT preload every skill description, search-first → fetch only-what-needed.

## Skill-quality standard on the content side

Every skill description follows the mandatory pattern: `[What it does] + [Use when ...] + [Do NOT use for ...]`. "Use when" with actual user phrases; "Do NOT use for" with negative triggers for overlap detection. **<1024 chars, no XML angle brackets, user-perspective**. Same as the SV-vault [[skill-metadata-catalog-pattern]] applied to our own skills.

## Tier system for the 19 agents

Tier 1 (Popular): Claude Code, Cline, Cursor, Copilot, Windsurf — first priority support. Tier 2 (Rising): Aider, Antigravity, Gemini CLI, Kilo, Kiro, Codex, Roo, TRAE. Tier 3 (Enterprise): Amazon Q, Augment, Droid, OpenCode, Sourcegraph Cody, Tabnine. Tier categorization is an explicit governance signal: which agent gets break-fix priority.

## What we can adopt for our SV stack

Concrete adoptables:

- **Append-only audit log pattern** is already adopted (propagation log) — but CLI operation logs (vault-net-ingest, vault-ko-ingest, crystallize) are scattered. A unified `~/.config/vault/audit.log` JSONL is introducible.
- **Lockfile + SHA-256 content hash** — our graphify Tier-2 graph has no such integrity check. After re-extract we can't say a node-ID is content-stable.
- **Skill-description structure (`Use when` + `Do NOT use for`)** — applied a lot in our own skills, but not policy-enforced. This pattern strengthens it.
- **Snyk Agent Scan integration** — our 243+ vault-own skills aren't security-scanned. Reasonable next step if the vault publishes.
- **Atomic write in vault-cleanup** — `vault-autosave` cron commits every 10 min, but file writes are NOT atomic (`backup → tmp → rename`). Process-kill mid-write could corrupt a big `Index.md`.

## Source references

- Repo: <https://github.com/tech-leads-club/agent-skills>
- npm: `@tech-leads-club/agent-skills` (MIT engine, CC-BY-4.0 skill content)
- Snyk Agent Scan: <https://github.com/snyk/agent-scan>
- Snyk 2026 Agent Threat Report
- Raw ingest: [[../10-raw/external/tech-leads-club_agent-skills/README]] + [[../10-raw/external/tech-leads-club_agent-skills/CLAUDE]] + [[../10-raw/external/tech-leads-club_agent-skills/SECURITY]]

## Related

- [[external-skill-cherry-pick]] — orthogonal pattern (single-skill manual pick)
- [[skill-metadata-catalog-pattern]] — our own skill-frontmatter convention
- [[audit-log-append-only-pattern]] — append-only log pattern we use
- [[multi-layer-safety-gate]] — defense-in-depth analogy
- [[sv-04-tool-composition]] — agent-tool-stack governance context

## Hungarian original

[[agent-skill-secure-registry-pattern]]
