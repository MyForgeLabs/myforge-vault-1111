---
name: Vault editor-portability — Obsidian + VS Code + Tolaria
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#topic/vault", "#topic/portability", "#tool/tolaria", "#tool/obsidian"]
---

# Vault editor-portability — Obsidian + VS Code + Tolaria (empirical proof)

> [!info] When this matters
> The "your data is yours" claim of a markdown-first vault is only credible if you can demonstrate the vault opens in **at least 3 different editors with zero adapter code**. This wiki records the 2026-05-20 empirical verification with Tolaria as the third app (after Obsidian + VS Code).

## The portability spec

A vault is "portable" iff:

1. **Files-first** — every note is a plain `.md` file on disk (NO proprietary container)
2. **Standards-based metadata** — YAML frontmatter at the top of each file
3. **Git-versioned** — the entire vault is a git repository
4. **Tool-agnostic linking** — `[[wikilinks]]` work without app-specific syntax
5. **No proprietary index** — no hidden binary database is required for the vault to be usable

If all 5 hold, the vault should open in any markdown-aware editor.

## Empirical test — 3 editors, same vault

### Obsidian (primary edit environment)

The vault structure as-of v1.0.10:
- 274 wikis (`11-wiki/<slug>.md`)
- 48 ADRs (`07-Decisions/YYYY-MM-DD <title>.md`)
- 140 audits (`06-Audits/YYYY-MM-DD <title>.md`)
- 18 project-notes (`02-Projects/<slug>.md`)
- 29 daily-notes (`01-Daily/YYYY-MM-DD.md`)
- 60+ session-logs (`08-Sessions/<slug>.md`)
- 3 host-cards (`03-Hosts/<slug>.md`)
- Plus: dashboards, indexes, playbooks, drafts, memories

Folder convention: **Johnny-Decimal-prefix** (`00-Meta/`, `01-Daily/`, … `11-wiki/`). Obsidian renders sidebar with these as folder-tree.

### VS Code (script + technical-edit environment)

The same files open as plain markdown. No special config required. Wikilinks `[[X]]` show as plain text (not rendered as hyperlinks unless extension installed). Frontmatter as YAML code-block.

Verdict: **functional, NOT user-friendly for browse**. Use VS Code for bulk-edit + git operations, NOT for daily-notes-style reading.

### Tolaria (verification target, 2026-05-20)

- Desktop app (Tauri 2 + React + TypeScript), macOS / Windows / Linux
- 11k+ GitHub stars, 3 months old, AGPL-3.0
- Convention: flat-vault expected, but tolerates nested folders

**The opening test** (2026-05-20):

```bash
# Sparse-checkout: 11-wiki/ + AGENTS.md only
git config core.sparseCheckout true
echo "11-wiki/" > .git/info/sparse-checkout
echo "AGENTS.md" >> .git/info/sparse-checkout
git pull origin main
open -a Tolaria .
```

Result:
- **279 files indexed instantly** (~3 sec on a Mac M-series)
- Sidebar TYPES: `wikis: 279`, `playbooks: 1`, `references: 5`, `raws: 3`, `indexes: 1`
- Center panel: notes-list with frontmatter snippets
- Editor: full markdown rendering with wikilinks live (Tolaria recognizes `[[mappa-prefix/name]]` AND `[[name]]`)

**Full vault test** (2026-05-20):

```bash
gh repo clone PetykaMaki/obsidian-vault myforge-vault-full
open -a Tolaria ~/Documents/vaults/myforge-vault-full
```

Result:
- **1103 of ~4000 files indexed instantly** (Tolaria filters to `type:`-jelölt notes by default; the `10-raw/` and unjelölt content stays in raw-mode)
- **20+ auto-detected type-categories** in sidebar from `type:` frontmatter:
  - `adrs: 1` · `audits: 140` · `backlogs: 1` · `blog-drafts: 5` · `daily-notes: 29` · `dashboards: 3` · `decisions: 47` · `documents: 1` · `drafts: 1` · `email-drafts: 1` · `feedbacks: 2` · `hosts: 3` · `indexes: 12` · `memories: 1` · `playbooks: 1` · `prds: 1` · `project-notes: 18` · `project-noteses: 1` (typo!) · `project-updates: 1` · `Projects: (icon)`

## The plus-finding: type-typo revealed by Tolaria

Tolaria's strict `type: <value>` categorization revealed a frontmatter-typo: 1 file in the vault has `type: project-noteses` instead of `project-notes`. This is a free **frontmatter-lint** byproduct of cross-app verification.

**Wider lesson**: opening the same vault in multiple editors with different type-handling logic catches single-character typos that no individual editor flags.

## What works across all 3

- ✅ Markdown body rendering (H1-H6, lists, tables, code-blocks, callouts)
- ✅ Frontmatter parsing (YAML-strict)
- ✅ Wikilinks (`[[X]]` and `[[mappa-prefix/X]]` both resolve)
- ✅ External hyperlinks
- ✅ Image references (`![](attachments/...)`)

## What differs by editor

| Feature | Obsidian | VS Code | Tolaria |
|---|---|---|---|
| Sidebar folder-tree | ✓ Johnny-Decimal-prefix mappák | ✓ (Explorer view) | ✓ FOLDERS section + auto-type-detect |
| Type-based filtering | Plugin (Tasks, Dataview) | Manual grep | **Native + auto-detect** |
| Graph view | ✓ native | — | TBD |
| Dataview-style queries | ✓ DataviewJS | — | TBD |
| Mobile sync | ✓ Obsidian Sync paid | — | TBD |
| AGENTS.md detection | — | — | ✓ native (Tolaria-pattern) |
| Tolaria-managed `_*` frontmatter | — | — | ✓ native |
| Theme + key-bindings | Customizable | Customizable | Customizable |
| Free | ✓ (personal) | ✓ | ✓ (AGPL) |

## Marketing-leverage from portability

For a HN/OSS-launch, the "vault opens in 3+ editors" claim:
- Disarms the "Obsidian-lock-in" objection
- Surfaces a co-amplification opportunity with each tool's community
- Provides visual-evidence material (multi-screenshot grid for HN/X-thread)

See [[hn-launch-angle-selection-rubric]] for how to integrate the portability-claim into the extended first-comment.

## Caveat — what Tolaria does NOT do (yet, for our vault)

- Sessions-folder (`08-Sessions/`): Tolaria filters to `type:`-jelölt notes; sessions with `type: session` show up, but the volume (60+ session-logs) means the type-filter is the only sane navigation
- MCP-integration: Tolaria has its own MCP-bridge (status-bar `MCP ⚠️` warning), but we use a separate `vault_ko_mcp` stack — Tolaria's MCP is not configured. NOT critical.
- Claude-integration: Tolaria's Claude-CLI integration (`Claude ⚠️` warning) is separate from our Claude Code setup. NOT critical.

These warnings are Tolaria's "configure additional features" prompts, NOT failures of vault-portability.

## Reproduction recipe

```bash
# macOS
brew install --cask tolaria

# Clone vault (or any markdown-vault git-repo)
gh repo clone <owner>/<vault-repo> ~/Documents/vaults/<name>

# Open in Tolaria
open -a Tolaria ~/Documents/vaults/<name>
```

That's it. Zero adapter code.

## Kapcsolódó

- [[Karpathy-LLM-Wiki-pattern]] — the foundational vault-architecture pattern
- [[Johnny-Decimal-prefix]] — folder convention
- [[hn-launch-angle-selection-rubric]] — how to use portability in launch-marketing
- [[../02-Projects/superintelligent-vault]] — the project this vault implements
