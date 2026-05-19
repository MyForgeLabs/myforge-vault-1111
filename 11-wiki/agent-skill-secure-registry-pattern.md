---
name: Agent-skill secure-registry minta
type: wiki
tags: ["#type/wiki", "skills", "supply-chain-security", "registry", "mcp", "governance"]
created: 2026-05-19
updated: 2026-05-19
source_repo: tech-leads-club/agent-skills
source_url: https://github.com/tech-leads-club/agent-skills
source_license: MIT (engine) + CC-BY-4.0 (skill-content)
---

# Agent-skill secure-registry minta

Egy minta arra, hogyan kell **biztonság-első, audit-elhető agent-skill disztribúciós réteget** építeni egy nyitott marketplace alternatívájaként. A tech-leads-club/agent-skills repo egy **curated, hardened library** koncepciót implementál, ami közvetlen választ a Snyk 2026 Agent Threat Report állítására: a public marketplace-eken a skill-ek 13.4%-a tartalmaz kritikus sebezhetőséget.

Ez egy ortogonális minta a sima [[external-skill-cherry-pick]]-hez: ott egy fejlesztő cherry-pick-eli amit akar; itt egy **maintainer-csoport curate-elt registry-jét** osztják meg sok consumer-rel és per-skill garantálnak biztonsági szintet.

## Threat-modell explicit (a kritikus rész)

Egy hardened registry attól értelmes, hogy **konkrét fenyegetésekre konkrét védelmet ad**. Négy tengely:

| Threat | Public marketplace | Hardened registry védelem |
|---|---|---|
| **Malicious payload** | Obfuszkált kód, binary, "black box" instrukciók | 100% open-source, no-binary policy, minden sor auditálható |
| **Credential theft** | Skill csendben env-var-okat exfiltrál | Static analysis CI-ben blokkol gyanús network-call-t / secret-access-t |
| **Supply chain attack** | Author push malicious update meglévő skill-re | Lockfile + SHA-256 content-hash, code nem változik explicit upgrade nélkül |
| **Prompt injection** | Hidden instruction agent-hijack-elésre | Human-curation, minden prompt manuális code-review-n megy át |

A 4-rétegű threat-mapping reusable minden olyan distribution-szal, ahol kód/utasítás 3rd-party-tól érkezik.

## CLI defense-in-depth (5 független layer)

Az installer-CLI minden művelete **MIND az 5 layer-en átmegy**, defense-in-depth: nem elég egy bypass.

### 1. Input sanitization

```typescript
const sanitizeName = (name: string): string =>
  name
    .replace(/[/\\]/g, '')          // path separator-ok
    .replace(/[\0:*?"<>|]/g, '')    // null-byte + Windows forbidden
    .replace(/^[.\s]+|[.\s]+$/g, '') // leading/trailing dot/space
    .replace(/\.{2,}/g, '')          // collapse ".."
    .replace(/^\.+/, '')             // no leading dots (hidden file)
    .substring(0, 255) || 'unnamed-skill'
```

Blokkolt input-ok: `../../../etc/passwd`, `skill\0name`, `/etc/passwd`, `skill:name`, `.hidden`, 300-char overflow.

### 2. Filesystem isolation (path-traversal protection)

```typescript
const isPathSafe = (basePath: string, targetPath: string): boolean => {
  const normalizedBase = normalize(resolve(basePath))
  const normalizedTarget = normalize(resolve(targetPath))
  return normalizedTarget.startsWith(normalizedBase + sep)
      || normalizedTarget === normalizedBase
}
```

**Mindkét path-ot full-resolve-olja** mielőtt összehasonlít — symlink / `..` szekvencia / relatív path eliminálódik. OS-specifikus `sep` (NEM hard-coded `/`), hogy ne lehessen `/allowed/dir../escape` trükközni. Minden write/read/delete művelet előtt fut.

### 3. Symlink guard (TOCTOU-mentes)

- **`lstat()` NEM `stat()`** — symlink-et detektál anélkül hogy követné. Kivédi a Time-Of-Check-Time-Of-Use támadást.
- **Target-validation** — chained symlink-ek esetén is a végső target-et resolve-olja és ellenőrzi.
- **Loop detection** — `ELOOP` (circular chain) → forcibly remove.
- **Windows junctions** — Windows-on directory-junction symlink helyett, jobb OS-szintű containment.

### 4. Lockfile integrity (`.agents/.skill-lock.json`)

- **Zod schema validation** — minden read strict-schema-n megy, invalid entry → graceful migration, NEM silent corruption.
- **Atomic write** — `backup → tmp → atomic rename`. Process-kill mid-write esetén az old fájl intakt marad.
- **SHA-256 content-hash per skill** — tamper-detection: ha a skill-fájl on-disk változik post-install, a hash-mismatch a következő művelet előtt detektálható.
- **Removal authorization** — skill nem törölhető lockfile-bejegyzés nélkül; `--force` bypass audit-logolt.

### 5. Audit trail (append-only)

Minden install/update/remove operáció JSONL-rekorddal megy `~/.config/agent-skills/audit.log`-ba:

```json
{"action":"install","skillName":"codenavi","agents":["cursor"],"success":1,"failed":0,"timestamp":"2026-02-25T10:00:00Z"}
```

**Soha nincs overwrite**, csak append. Ez a forenzikus record minden host-on. Ugyanaz a minta, mint nálunk az [[audit-log-append-only-pattern]] vault-side a propagation-log-ban.

## Security-scan CI-ben (Snyk Agent Scan)

Minden skill SHA-256-tal hash-elve, eredmény cache-elt (`.security-scan-cache.json`). Következő run: hash-change → re-scan, hash-same → cache-hit. Fast-enough hogy PR-onként és release-enként fusson. Release pipeline **kötelezi a passing scan-t**.

**Fork-PR-eknek nincs token-access** — opcionálisan GitHub Merge Queue-val áthidalható: a "Security Scan (merge queue)" check-et kell required-re tenni.

**Allowlist false-positive-okra** (`security-scan-allowlist.yaml`):

```yaml
entries:
  - skill: my-skill
    code: W011
    reason: "Trusted first-party API at api.example.com, reviewed 2026-01-01"
    allowedBy: github.com/username
    allowedAt: '2026-01-01'
    expiresAt: '2027-01-01'  # erősen ajánlott, lejár → újra auto-flag-el
```

A lejárati-dátum nélkül az exception "permanent technical debt" lesz. Hard-coded review-cycle a config-on keresztül.

## MCP-server progressive disclosure

A `@tech-leads-club/agent-skills-mcp` szándékosan **szűkebb threat-surface**:

- **Read-only** — nincs write-access a registry-hez
- **No auth** — local stdio, nem network-exposed
- **Path validation** — `fetch_skill_files` minden path-ot a registry `files[]` array-jéhez ellenőrzi, **lehetetlen arbitrary URL-t fetch-elni**
- **No local FS access** — csak CDN-fetch
- **stdout reserved for JSON-RPC** — minden log stderr-re (protokoll-corruption-mentes)

4 tool: `list_skills`, `search_skills`, `read_skill`, `fetch_skill_files`. A `list_skills` csak explicit user-kérésre — ez egy **progressive disclosure** minta a kontextusablak védelmére: NEM betölt minden skill-leírást előre, hanem search-first → fetch only-what-needed.

## Skill-quality standard a content-oldalon

Minden skill description-je követi a kötelező mintát: `[What it does] + [Use when ...] + [Do NOT use for ...]`. "Use when" actual user-phrases-szel, "Do NOT use for" negative-trigger overlap-detection-re. **<1024 char, no XML angle brackets, user-perspective**. Ez ugyanaz, amit a SV-vault [[skill-metadata-catalog-pattern]] is gyakorol a saját skill-jeinkkel.

## Tier-system a 19 agent-en

Tier 1 (Popular): Claude Code, Cline, Cursor, Copilot, Windsurf — első-pioritású-támogatás. Tier 2 (Rising): Aider, Antigravity, Gemini CLI, Kilo, Kiro, Codex, Roo, TRAE. Tier 3 (Enterprise): Amazon Q, Augment, Droid, OpenCode, Sourcegraph Cody, Tabnine. A tier-besorolás explicit governance-jel: melyik agent kap break-fix-prioritást.

## Mit tanulhatunk a saját SV stack-ünkbe

Lásd "Őszinte rivalitás" lent. Konkrét átvehető-elemek:

- **Audit-log append-only mintát** már átvettük (propagation-log) — de a CLI-operation-ok (vault-net-ingest, vault-ko-ingest, crystallize) audit-log-jai szétszórtak. Egységes `~/.config/vault/audit.log` JSONL bevezethető.
- **Lockfile + SHA-256 content-hash** — a graphify Tier-2 graph-ünknek nincs ilyen integrity-check. Re-extract után nem tudjuk megmondani, hogy egy node-ID stabil-e tartalom-szinten.
- **Skill-description struktúra (`Use when` + `Do NOT use for`)** — már sokat alkalmazzuk a saját skill-jeinkben, de NEM kötelező policy. Ez a minta megerősíti.
- **Snyk Agent Scan integration** — a vault-saját skill-eink (243+) jelenleg nincsenek security-scan-elve. Reasonable next-step ha vault publikálódik.
- **Atomic-write a vault-cleanup-ban** — most a `vault-autosave` cron 10 percenként commit-ol, de a fájl-write-ok NEM atomic-ok (`backup → tmp → rename`). Process-kill mid-write korrumpálhat egy nagy `Index.md`-t.

## Forrás-hivatkozások

- Repo: <https://github.com/tech-leads-club/agent-skills>
- npm: `@tech-leads-club/agent-skills` (MIT engine, CC-BY-4.0 skill-content)
- Snyk Agent Scan: <https://github.com/snyk/agent-scan>
- Snyk 2026 Agent Threat Report: <https://github.com/snyk/agent-scan/blob/main/.github/reports/skills-report.pdf>
- Raw-ingest: [[../10-raw/external/tech-leads-club_agent-skills/README]] + [[../10-raw/external/tech-leads-club_agent-skills/CLAUDE]] + [[../10-raw/external/tech-leads-club_agent-skills/SECURITY]]

## Kapcsolódó

- [[external-skill-cherry-pick]] — ortogonális minta (single-skill manual pick)
- [[skill-metadata-catalog-pattern]] — saját skill-frontmatter konvenciónk
- [[audit-log-append-only-pattern]] — append-only log-mintát alkalmazzuk
- [[multi-layer-safety-gate]] — defense-in-depth analógia
- [[sv-04-tool-composition]] — agent-tool-stack governance kontextus
