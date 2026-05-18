---
name: Audit-MD self-referential loop pattern
type: wiki
lang: en
translated_from: audit-md-self-referential-loop
tags: ["#type/wiki", "vault-integrity", "audit", "wikilink", "false-positive", "recurring-job"]
created: 2026-05-18
updated: 2026-05-18
status: stable
---

# Audit-MD self-referential loop

When a vault has **recurring auditor scripts** (broken-wikilink-scanner, system-health, conflicts-audit, orphan-wiki-detector, etc.) that write their findings into Markdown, and the audit output lists broken targets in **real `[[wikilink]]` form**, the next scan **re-flags** them as a new broken source — an infinite self-referential loop that inflates the issue count and hides real problems.

## TL;DR

- **Symptom:** broken-wikilink count grows monotonically scan after scan, e.g. `1656`, `1900`, `2200` issues, while the vault is essentially unchanged
- **Cause:** the auditor's output MD itself contains `[[broken-target]]` literals → the scanner picks it up as a broken source
- **Fix:** either backtick-wrap (`` `[[X]]` `` form) in the audit MD, or `is_excluded_path()` patch in the scanner to exclude audit MDs from the source set
- **Reusable:** every recurring vault-audit script needs **self-exclude**

## Background — recurring incident

A weekly Sunday cron regenerates a `06-Audits/System_Health.md` and `06-Audits/broken-wikilinks-latest.md`. A manual run reports **1656 broken-wikilink issues**, suspiciously high. Investigation: ~70-80% of the 1656 is **the audit MD from a previous run** — `broken-wikilinks-latest.md` contained literal `[[NON-EXISTENT-TARGET]]` lines (because those were the actual broken targets in the report), and the next scanner pass treated the audit MD as a **source file** referencing `[[NON-EXISTENT-TARGET]]`.

A classic **observer effect**: the observation tool corrupts the next measurement with its own output.

## The pattern (3 solutions)

### 1. Backtick-wrap in audit output (safest)

Wrap every broken-target literal in inline code:

```python
# audit-writer pattern
for issue in broken_links:
    f.write(f"- `[[{issue.target}]]` referenced from `{issue.source}`\n")
```

Because of the backticks, Obsidian/scanner does NOT interpret it as a wikilink. No config required.

### 2. `is_excluded_path()` patch in scanner

```python
EXCLUDE_PATTERNS = [
    r"06-Audits/.*\.md$",
    r"06-Audits/.*broken-wikilinks.*\.md$",
    r"08-Sessions/.*\.md$",  # sessions sometimes reference example broken-links
]

def is_excluded(path: Path) -> bool:
    return any(re.search(p, str(path)) for p in EXCLUDE_PATTERNS)

for md in vault.glob("**/*.md"):
    if is_excluded(md):
        continue
    scan_links(md)
```

Pros: vault authors can freely write literal wikilinks in audit MDs. Cons: real broken-sources inside audit MDs become invisible.

### 3. Marker frontmatter — "audit-output" flag

```yaml
---
type: audit-report
audit-self-exclude: true
---
```

The scanner reads this and skips. More generic than path patterns, but every audit writer must adopt the convention.

## Anti-pattern: post-hoc filter

Do NOT filter audit-MD broken links **after the fact** at report-generation time (`grep -v 'broken-wikilinks-latest.md'`). After a few iterations, new audit MDs (e.g. `conflicts-latest.md`, `orphan-wiki-latest.md`) also enter the noise, and the filter list becomes unmaintainable. Self-exclude belongs **at the scanner's source-set boundary**, not in the reporting phase.

Another anti-pattern: **file-link instead of literal-link** (`[broken: NON-EXISTENT-TARGET](non-existent-target.md)`). This is a markdown link, NOT a wikilink, but some scanners pick it up too. Backtick-wrap is universal.

## Reusable rules

| Audit script | Self-exclude target | Convention |
|---|---|---|
| `broken-wikilinks` | Own output MD | path-pattern `06-Audits/broken-wikilinks-*.md` |
| `System_Health` | Own + all audit MDs | path-pattern `06-Audits/**/*.md` |
| `conflicts-audit` | Own + audit-history | path-pattern `06-Audits/conflicts-*.md` |
| `orphan-wiki-detector` | The orphan list itself | path-pattern `06-Audits/orphan-*.md` |
| `link-graph-export` | All audit + raw input | path-pattern `06-Audits/**`, `10-raw/**` |

**General rule of thumb:** every script that iterates over `**/*.md` and processes wikilinks / references / mentions must **define an `EXCLUDE_PATTERNS`** as its first step, including:
- the **own output path** (and all variants: `-latest.md`, `-YYYY-MM-DD.md`)
- the `06-Audits/**` folder (typically)
- if sessions contain example links: `08-Sessions/**`
- raw input (`10-raw/**`) — often raw text, not part of the vault link graph

## Complementary patterns

- **Reproducible audit output** — the report should not contain inline timestamps, only in frontmatter. Git-diff then shows what genuinely changed between two scans
- **Severity bucket** — the output should not be a single list but `### Critical`, `### Warning`, `### Info` sections. Self-loop noise goes to info, the critical section stays clean
- **Diff-only report mode** — the script knows the previous scan's result and only lists new issues. Mitigates the self-loop even without explicit exclude

## Detection

Quick check: if audit-output broken-link count > 100 and vault size is small (< 1000 MD), it's very likely a self-loop. Sanity-check command:

```bash
# Which source files appear most as broken-link source in the audit MD?
grep -h "referenced from" /path/to/06-Audits/broken-wikilinks-latest.md \
  | grep -oE "from \`[^\`]+\`" | sort | uniq -c | sort -rn | head -10
```

If the top source is the audit MD itself or any `06-Audits/*` file, it's a self-loop.

## Related

- [[vault-corruption-detection-pattern]] — foundation of stable audit monitoring
- [[Karpathy-LLM-Wiki-pattern]] — vault structure that produces self-reference
- [[multi-layer-safety-gate]] — audit as a defense layer
