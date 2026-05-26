---
name: Tool sandbox-eval playbook
description: Reusable evaluation flow for any third-party tool (Claude Code plugin, npm package, CLI) considered for vault integration — clone to /tmp, run deterministic parts standalone, measure overlap with existing stack, then decide integration strategy.
type: wiki
created: 2026-05-21
updated: 2026-05-21
tags: ["#type/wiki", "evaluation", "safety", "cherry-pick", "marketplace"]
---

# Tool sandbox-eval playbook

A reusable flow for evaluating a third-party tool **before** integration. Designed for the case where: a tool looks promising, the codebase is already substantial, and a wholesale install would risk hook-pollution, schema-drift, or maintenance bloat.

The pattern is the deeper version of [[external-skill-cherry-pick]] — that one says *"use symlinks, not wholesale install"*; this one walks the full **eval-decision-flow** that gets you to a defensible decision.

## When to use this playbook

- A marketplace plugin (Claude Code / Codex / Cursor / Copilot) is described as solving a real problem you have
- An npm/pnpm/Python package on GitHub overlaps with something you already built
- Someone DMs you "I built X for your problem, want to try it?"
- A trending repo looks like a missing puzzle piece in your stack

If the answer is *"obviously just install it"* → you don't need this playbook. If it's *"…is it worth the complexity?"* → run this.

## The 5-phase flow

### Phase 1 — Static intelligence (no install)

Pull the facts before pulling code. Use `gh repo view`, the README, and metadata:

| Fact to gather | Why it matters |
|---|---|
| License (MIT / Apache / GPL / proprietary) | Determines redistribution + cherry-pick legality |
| Last push date | Active project vs abandoned |
| Star count + fork count | Community-signal (not value-signal — 28k stars ≠ "this fits your stack") |
| Topics + description | Surface-overlap with your existing stack |
| Author profile + other repos | Bona-fide builder vs scout/grift |
| **Hook surface** (`hooks.json`, `install.sh`, `postinstall` scripts) | What gets auto-registered if you wholesale-install |
| Storage format | JSON / SQLite / proprietary — does it bridge to your data? |
| Build complexity | LOC count + dependency tree depth |

For a Claude Code plugin specifically, **always inspect `.claude-plugin/` + `hooks/hooks.json`** before any install. The hook command-strings are where instruction-injection lives (see [[claude-code-harness-blocks]] § 7).

### Phase 2 — Sandbox clone, no install

Clone to `/tmp/<tool>-clone`, **do not** run `install.sh` / `npm install -g` / `/plugin install`:

```bash
git clone --depth 1 https://github.com/<owner>/<tool> /tmp/<tool>-clone
```

Then **inspect** the install mechanism without running it:

- `install.sh` — what does it symlink, what does it touch in your home?
- `package.json` `postinstall` — does it write to anywhere outside `node_modules/`?
- `.claude-plugin/` — what slash-commands + agents + hooks get registered?

Document the touch-surface in your eval-notes. **An install-script that touches anything outside the tool's own dir is a red flag** that needs justification.

### Phase 3 — Run deterministic parts standalone

Most non-trivial tools have **deterministic** parts that work without the full LLM-orchestration layer:

- A parser script (Python, no external API)
- A static analyzer (tree-sitter, regex)
- A schema migration step

Find these and run them directly against your data, with a **symlinked sandbox** so you don't touch your real working tree:

```bash
mkdir -p /tmp/<tool>-sandbox
cd /tmp/<tool>-sandbox
ln -sfn /root/obsidian-vault/11-wiki wiki    # the tool's expected layout
ln -sfn /root/obsidian-vault/10-raw raw
cp /root/obsidian-vault/11-wiki/Index.md index.md
python3 /tmp/<tool>-clone/path/to/deterministic-parser.py .
```

This gets you **real output on real data** without registering any hooks, without symlinking into `~/.claude/`, without `pnpm install` pulling 500 transitive deps.

### Phase 4 — Quantitative overlap with existing stack

The decision-making question is rarely *"does this tool work?"* — it usually does. The real question is *"what does it add that I don't already have?"*. Measure:

| Metric | How |
|---|---|
| **File-coverage** | files indexed by tool ∩ ∪ files indexed by your stack |
| **Entity / node count** | tool's nodes vs your existing graph nodes |
| **Edge-set diversity** | what edges does the tool surface that your stack doesn't? |
| **Storage-format compatibility** | can your existing schema absorb the tool's output, or is there schema-drift? |
| **Performance** | runtime + memory on a realistic input size |

For overlap with our `vault` setup, a Python snippet that intersects:
- KO-DB `fact_provenance.provenance` set
- graphify `source_file` set
- Tool's output paths

…tells you in one number how much complement vs duplicate the tool brings. (Example: `Understand-Anything` on 2026-05-21 audit: 314 files indexed, 96 ∩ existing-stack-97, → 218 net-new wikis but 31% overlap on the wikis we already cover.)

### Phase 5 — A / B / C integration strategy

Now pick the strategy based on the Phase 1-4 findings:

| Strategy | When to pick | Risk | Effort |
|---|---|---|---:|
| **A — Wholesale plugin/install** | High value, low hook-surface, trusted author, our stack would absorb the tool's output cleanly | 🔴 highest (hooks auto-register) | minutes |
| **B — Sandbox-only reference** | Looked at it for a feature idea, didn't justify integration | 🟢 lowest | 0 (already done in Phase 1-3) |
| **C1 — Cherry-pick deterministic parts** | The Python parser / static analyzer is the killer feature; the LLM/orchestration layer duplicates what we have | 🟢 low | 2-4 hours |
| **C2 — Cherry-pick visualization/UI layer** | The web dashboard is the value; we feed it our own data, not the tool's | 🟡 medium (need schema-adapter) | 1-2 days |
| **C1 + C2** | Both deterministic + UI add value but the orchestration layer is bloat | 🟡 medium | ~3 days |

**A wholesale install** should be the **rarest** outcome, not the default. It costs less time upfront but the maintenance + uninstall cost is high.

**Sandbox-only reference** is the most common outcome and is **valid** — you learned the tool's design, decided not to integrate, documented why. The eval was the value.

## Anti-patterns

> [!warning] Pitfalls observed in earlier evaluations

1. **`/plugin install` first, evaluate second** — once the plugin is installed, hooks are registered and the transcript-context is polluted. Decision-making gets biased toward keeping it. **Phase 1-3 happen before any install.**

2. **"It's MIT-licensed, just go"** — MIT is necessary for cherry-pick but doesn't tell you about hook-pollution risk. Run the audit too.

3. **Trusting the README's quickstart blindly** — Quickstart sections optimize for time-to-first-impression, not safety. Read `install.sh` line-by-line before running.

4. **Skipping the overlap-measure** — without numbers, the eval becomes vibes. "Looks good" + "has stars" → wholesale-install → regret 3 weeks later when the maintenance cost shows up.

5. **Sandbox-test, then forget to clean up** — `/tmp/<tool>-clone` and `/tmp/<tool>-sandbox` are reboot-temporary, but the `~/.understand-anything/` and similar **persist**. If Phase 2 found install-script side-effects, verify you didn't accidentally run them.

## Tooling we have for this

| Tool | Use |
|---|---|
| `gh repo view` | Phase 1 metadata |
| `gh api repos/<owner>/<repo>/contents/path` | Phase 1 file-listing without clone |
| `vault-plugin-hooks-audit --roots <dir>` | Phase 2 hook-surface red-flag scan, with `--strict` for CI / pre-commit gating |
| `vault-graph-complementarity --json` | Phase 4 overlap with our existing graph stack |
| `vault-ko-query --top-k <N>` | Phase 4 overlap with our KO-DB structured-facts |
| `vault-public-sync --reason "<eval-finding>"` | Phase 5 commit-log entry if integration lands |

## Decision-doc template

Every Phase-5 outcome should leave a short trace, even Strategy B ("decided not to"). Format:

```markdown
## Tool eval: <name> (<date>)

- Static: <license, stars, last-push>
- Hook-surface: <count of HIGH/MID via vault-plugin-hooks-audit>
- Deterministic parts: <ran-it, output-stats>
- Overlap with existing stack: <numbers>
- Decision: A / B / C1 / C2 / C1+C2
- Reason (1 sentence): …
- Sandbox-clone kept at: /tmp/<tool>-clone (or "cleaned up: yes")
```

A `06-Audits/2026-MM-DD tool eval — <name>.md` entry is ideal — keeps the eval evidence searchable for future "did we ever look at X?" questions.

## Reference evaluations (chronological)

- **2026-05-21: `Lum1104/Understand-Anything`** → Strategy B (sandbox-only reference). Reason: 218 net-new wiki indexed mostly `.en.md` translations we don't need re-indexed, the visualization-layer value is real (backlog'd Strategy C2 for W23+ as a *standalone* dashboard fed by our own `graph.json`), the plugin hooks contained HIGH-heat instruction-injection patterns (`"Do not ask the user"`, `"just do it"`) — wholesale install vetoed. Audit: `06-Audits/plugin-hooks-audit-2026-W22.md`.

## Kapcsolódó

- [[external-skill-cherry-pick]] — the shorter "use symlinks, not install" version of this playbook
- [[claude-code-harness-blocks]] § 7 — marketplace plugin instruction-injection pattern
- [[vendor-feature-verify-before-workaround]] — sibling lesson: inspect data, not metadata
- [[multi-layer-safety-gate]] — companion safety pattern
- [[bulk-fanout-context-budget-checkpoint]] — eval-flows under context-budget pressure
