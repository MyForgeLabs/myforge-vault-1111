#!/usr/bin/python3
"""
vault-core-memory — Letta-style virtual-context core-memory CLI.

Manages /root/obsidian-vault/00-Meta/core-memory.yaml — the ~2 KB
always-loaded "core" of the agent context, complement to archival memory
(full vault, retrieved on-demand via vault-search / vault-ko-query).

Commands
--------
    vault-core-memory init                  Build a fresh core-memory.yaml
                                            from current vault state.
    vault-core-memory show                  Print current core to stdout.
    vault-core-memory update <block> <text> Mutate a single block, atomic.
    vault-core-memory size                  Token estimate (chars/4).
    vault-core-memory simulate "<query>"    Show what would page-in via
                                            archival vault-search.
    vault-core-memory diff                  Show delta since last init.

Schema spec: /root/obsidian-vault/00-Meta/core-memory-schema.md
Wiki:        /root/obsidian-vault/11-wiki/letta-virtual-context-pattern.en.md

This is a SKELETON. `simulate` does NOT mutate the LLM context — it only
visualizes the saving versus the legacy aggressive pre-load.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Allow vault_atomic import without manual PYTHONPATH.
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
sys.path.insert(0, str(VAULT_ROOT / ".vault-tools" / "lib"))

try:
    from vault_atomic import atomic_write  # type: ignore
except ImportError as exc:
    print(
        f"✗ Cannot import vault_atomic from {VAULT_ROOT}/.vault-tools/lib: {exc}",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    import yaml
except ImportError:
    print("✗ Missing dependency: PyYAML (apt install python3-yaml)", file=sys.stderr)
    sys.exit(2)


CORE_PATH = VAULT_ROOT / "00-Meta" / "core-memory.yaml"
SNAPSHOT_PATH = VAULT_ROOT / "00-Meta" / ".core-memory.snapshot.yaml"
BUDGET_TOKENS_DEFAULT = 2048
BUDGET_HARD_CEIL = 3000

BLOCK_ORDER = [
    "user_profile",
    "active_project",
    "open_tasks",
    "glossary",
    "infra_pins",
    "recent_decisions",
]


# ----------------------------------------------------------------------
# token / size helpers
# ----------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """Rough token estimate: chars / 4. Matches BPE within ~15%."""
    return max(1, len(text) // 4)


def render_core(doc: dict[str, Any]) -> str:
    """Render the core as the agent would see it (just the block contents)."""
    parts = []
    for block_name in BLOCK_ORDER:
        block = doc.get("blocks", {}).get(block_name)
        if not block:
            continue
        parts.append(f"## {block_name}\n{block.get('content', '').rstrip()}\n")
    return "\n".join(parts)


# ----------------------------------------------------------------------
# init — build from current vault state
# ----------------------------------------------------------------------


def _read_file(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars:
        return text[:max_chars]
    return text


def _extract_user_profile() -> str:
    """Distil 05-Memory/User.md down to ~120-180 tokens."""
    src = VAULT_ROOT / "05-Memory" / "User.md"
    if not src.exists():
        return "TODO: 05-Memory/User.md missing — populate manually."
    return (
        "Peti (user@example.com). Hungarian-speaker, English tech terms OK.\n"
        "Headless Linux /root, VSCode extension + SSH + occasional VNC.\n"
        "Style: terse, code-blocks for commands, tables welcome, no bullet-dumps.\n"
        "Uses 3 CLI agents (Claude Code primary, Codex review, Gemini multimodal).\n"
        "Auto-mode for many small steps; explicit decision-prompt for destructive ops.\n"
        "Destructive vault-edits (Memory, Backlog, ADR rewrite) require diff-preview + OK\n"
        "before save — auto-mode does NOT bypass this. Append-only is fine."
    )


def _extract_active_project() -> str:
    """Distil 02-Projects/superintelligent-vault.md status header."""
    src = VAULT_ROOT / "02-Projects" / "superintelligent-vault.md"
    if not src.exists():
        return "TODO: no active project marker found."
    text = _read_file(src, max_chars=6000)
    # Pull frontmatter status + a 1-2 line summary.
    status_line = ""
    for line in text.splitlines():
        if line.startswith("status:"):
            status_line = line[len("status:"):].strip()
            break
    return (
        "Superintelligent Vault (SV) — 8-axis evolutionary roadmap.\n"
        f"Status: {status_line[:240]}\n"
        "Active sprints: B-2 (memory arch, done) + B-1 crystallize (Week 3-4) + "
        "B-8 RSI Tier-2 skeleton. Today (2026-05-19): pursuing the 22-idea "
        "brainstorm — building Letta virtual-context skeleton (idea #16)."
    )


def _extract_open_tasks() -> str:
    """Top 5 🔴 sürgős / 🔺 highest items from 04-Tasks/Backlog.md."""
    src = VAULT_ROOT / "04-Tasks" / "Backlog.md"
    if not src.exists():
        return "TODO: 04-Tasks/Backlog.md missing."
    text = _read_file(src, max_chars=20000)
    open_lines: list[str] = []
    in_urgent = False
    for line in text.splitlines():
        if line.startswith("## 🔴"):
            in_urgent = True
            continue
        if line.startswith("## ") and in_urgent:
            break
        # Pick open tasks with high priority markers.
        if in_urgent and line.startswith("- [ ] ") and ("🔺" in line or "🔼" in line or "⏫" in line):
            # Strip wikilinks and emoji-stats noise; keep the headline.
            cleaned = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", line)
            cleaned = re.sub(r"\s+➕\s+\d{4}-\d{2}-\d{2}.*$", "", cleaned)
            cleaned = re.sub(r"\s+#\S+", "", cleaned)
            # Truncate each item to ~160 chars to keep the block lean.
            if len(cleaned) > 180:
                cleaned = cleaned[:177] + "..."
            open_lines.append(cleaned)
            if len(open_lines) >= 5:
                break
    if not open_lines:
        open_lines.append("- (no high-priority open tasks)")
    return "\n".join(open_lines)


def _extract_glossary() -> str:
    """Pull ~10-15 most-likely-active acronyms from 00-Meta/Glossary.md."""
    src = VAULT_ROOT / "00-Meta" / "Glossary.md"
    if not src.exists():
        return "TODO: 00-Meta/Glossary.md missing."
    text = _read_file(src)
    # Lift table rows that look like "| **KGC** | Kisgépcentrum ... |"
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        m = re.match(r"\|\s*\*\*([A-Z][A-Za-z0-9.\-]+)\*\*\s*\|\s*\*?\*?([^|]+?)\*?\*?\s*\|", line)
        if m:
            slug = m.group(1).strip()
            meaning = m.group(2).strip()
            # First sentence only — drop "—" suffixes, wikilinks, and bold markers.
            meaning = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", meaning)
            meaning = meaning.split("—")[0].strip()
            meaning = meaning.replace("**", "").strip()
            if 1 < len(slug) < 30 and 2 < len(meaning) < 120:
                rows.append((slug, meaning))
    # Hand-pick the most-likely-active 14.
    priority_slugs = {
        "SV", "KGC", "MFL", "MAPESZ", "Foxxi", "Kokó", "BMAD", "ADR",
        "PRD", "NFR", "RAG", "PWA", "PM2", "Tailscale",
    }
    picked: list[tuple[str, str]] = []
    seen: set[str] = set()
    for slug, meaning in rows:
        if slug in priority_slugs and slug not in seen:
            picked.append((slug, meaning))
            seen.add(slug)
    # Pad with first-encountered rows up to 14 if priority list under-covers.
    for slug, meaning in rows:
        if len(picked) >= 14:
            break
        if slug not in seen:
            picked.append((slug, meaning))
            seen.add(slug)
    # Append KO-DB / SV-internal slugs that aren't in the Glossary table.
    extras = [
        ("KO-DB", "Knowledge Objects SQLite triplet store (13K+ facts)"),
        ("G-Eval", "G-Eval CoT-based LLM-judge scoring (Crystallization)"),
        ("MemGPT", "Letta-precursor; virtual-context-OS pattern (this file)"),
    ]
    for slug, meaning in extras:
        if slug not in seen:
            picked.append((slug, meaning))
            seen.add(slug)
    lines = [f"- **{slug}** — {meaning}" for slug, meaning in picked]
    return "\n".join(lines)


def _extract_infra_pins() -> str:
    """Hand-distil the reflexive infra facts."""
    return (
        "- Vault root: `/root/obsidian-vault/` (Claude/Codex/Gemini share via symlinks).\n"
        "- Prod VPS: `vps-prod-example` / `72.62.92.98` (Hostinger KVM 8).\n"
        "- Dev VPS: `vps-dev-example` / `187.77.70.36` (agent hub).\n"
        "- KGC Postgres: `kgc-postgres` Docker, port `5433` (DBs: `kgc_erp`, `kgc_berles`).\n"
        "- Memgraph: container `vault-memgraph`, port `7687` (vault vector + graph store).\n"
        "- VNC: `x11vnc :99`, port `5900`; noVNC on `6080`; `DISPLAY=:99`.\n"
        "- KO-DB: `/root/obsidian-vault/.vault-ko/facts.db` (13K+ facts, sqlite)."
    )


def _extract_recent_decisions() -> str:
    """Last 5 ADRs by filename mtime — title + 1-line `why`."""
    adr_dir = VAULT_ROOT / "07-Decisions"
    if not adr_dir.exists():
        return "TODO: 07-Decisions/ missing."
    adr_files = sorted(
        [p for p in adr_dir.glob("*.md") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:5]
    lines = []
    for p in adr_files:
        title = p.stem
        # First non-frontmatter, non-heading paragraph as `why`.
        body = _read_file(p, max_chars=2000)
        why = ""
        in_fm = False
        for line in body.splitlines():
            if line.strip() == "---":
                in_fm = not in_fm
                continue
            if in_fm:
                continue
            if not line.strip() or line.startswith("#"):
                continue
            why = line.strip()
            break
        # Truncate why to ~100 chars.
        if len(why) > 110:
            why = why[:107] + "..."
        lines.append(f"- **{title}** — {why}" if why else f"- **{title}**")
    return "\n".join(lines) if lines else "- (no recent ADRs)"


def build_default_core() -> dict[str, Any]:
    """Build a fresh core-memory doc from current vault state."""
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    today = dt.date.today().isoformat()
    return {
        "version": 1,
        "generated_at": now,
        "budget_tokens": BUDGET_TOKENS_DEFAULT,
        "blocks": {
            "user_profile": {
                "content": _extract_user_profile(),
                "last_updated": today,
                "source_hint": "[[05-Memory/User]]",
            },
            "active_project": {
                "content": _extract_active_project(),
                "last_updated": today,
                "source_hint": "[[02-Projects/superintelligent-vault]]",
            },
            "open_tasks": {
                "content": _extract_open_tasks(),
                "last_updated": today,
                "source_hint": "[[04-Tasks/Backlog]]",
            },
            "glossary": {
                "content": _extract_glossary(),
                "last_updated": today,
                "source_hint": "[[00-Meta/Glossary]]",
            },
            "infra_pins": {
                "content": _extract_infra_pins(),
                "last_updated": today,
                "source_hint": "[[05-Memory/Infrastructure]]",
            },
            "recent_decisions": {
                "content": _extract_recent_decisions(),
                "last_updated": today,
                "source_hint": "[[07-Decisions]]",
            },
        },
    }


def dump_yaml(doc: dict[str, Any]) -> str:
    """Stable yaml dump with block-literal strings."""

    class LiteralStr(str):
        pass

    def literal_repr(dumper: yaml.SafeDumper, data: LiteralStr) -> Any:  # type: ignore
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", str(data), style="|"
        )

    yaml.SafeDumper.add_representer(LiteralStr, literal_repr)

    def coerce(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: coerce(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [coerce(v) for v in obj]
        if isinstance(obj, str) and "\n" in obj:
            return LiteralStr(obj)
        return obj

    return yaml.safe_dump(
        coerce(doc),
        sort_keys=False,
        allow_unicode=True,
        width=10_000,
    )


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    doc = build_default_core()
    text = dump_yaml(doc)
    atomic_write(CORE_PATH, text)
    # Snapshot for `diff`.
    atomic_write(SNAPSHOT_PATH, text)
    rendered = render_core(doc)
    tokens = estimate_tokens(rendered)
    print(f"✓ Wrote {CORE_PATH} ({len(text):,} bytes, ~{tokens} tokens rendered)")
    if tokens > BUDGET_HARD_CEIL:
        print(
            f"⚠ Rendered size ({tokens} tokens) exceeds hard ceiling "
            f"({BUDGET_HARD_CEIL}). Prune blocks.",
            file=sys.stderr,
        )
        return 1
    if tokens > doc["budget_tokens"]:
        print(
            f"⚠ Rendered size ({tokens} tokens) above soft budget "
            f"({doc['budget_tokens']}).",
            file=sys.stderr,
        )
    return 0


def load_core() -> dict[str, Any]:
    if not CORE_PATH.exists():
        print(
            f"✗ {CORE_PATH} not found. Run `vault-core-memory init`.",
            file=sys.stderr,
        )
        sys.exit(1)
    with CORE_PATH.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not isinstance(doc, dict) or "blocks" not in doc:
        print(f"✗ {CORE_PATH} is malformed.", file=sys.stderr)
        sys.exit(1)
    return doc


def cmd_show(args: argparse.Namespace) -> int:
    doc = load_core()
    if args.raw:
        sys.stdout.write(CORE_PATH.read_text(encoding="utf-8"))
    else:
        sys.stdout.write(render_core(doc))
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    doc = load_core()
    block_name = args.block
    if block_name not in BLOCK_ORDER:
        print(
            f"✗ Unknown block: {block_name}. Choose from {BLOCK_ORDER}.",
            file=sys.stderr,
        )
        return 1
    text = args.text
    today = dt.date.today().isoformat()
    blocks = doc.setdefault("blocks", {})
    block = blocks.setdefault(block_name, {})
    block["content"] = text
    block["last_updated"] = today
    block.setdefault("source_hint", "")
    doc["generated_at"] = dt.datetime.now(dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%MZ"
    )
    atomic_write(CORE_PATH, dump_yaml(doc))
    print(f"✓ Updated block `{block_name}` ({len(text)} chars).")
    return 0


def cmd_size(args: argparse.Namespace) -> int:
    doc = load_core()
    rendered = render_core(doc)
    total = estimate_tokens(rendered)
    print("Core-memory size estimate")
    print(f"  rendered: {len(rendered):,} chars / ~{total} tokens")
    print(f"  budget:   {doc.get('budget_tokens', BUDGET_TOKENS_DEFAULT)} tokens (soft)")
    print(f"  ceiling:  {BUDGET_HARD_CEIL} tokens (hard)")
    print()
    print("Per-block:")
    for block_name in BLOCK_ORDER:
        block = doc.get("blocks", {}).get(block_name)
        if not block:
            print(f"  {block_name:18s}: (missing)")
            continue
        c = block.get("content", "")
        print(f"  {block_name:18s}: {len(c):4d} chars / ~{estimate_tokens(c):4d} tokens")
    if total > BUDGET_HARD_CEIL:
        return 1
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    query = args.query
    doc = load_core()
    rendered = render_core(doc)
    core_tokens = estimate_tokens(rendered)

    print(f"Query: {query!r}")
    print()
    print("=== Core hit ===")
    print(f"Core size: ~{core_tokens} tokens (always loaded)")
    print()

    # Heuristic: does the query string overlap any block content?
    hit_blocks = []
    q_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    for block_name in BLOCK_ORDER:
        block = doc.get("blocks", {}).get(block_name, {})
        content = block.get("content", "").lower()
        if any(t in content for t in q_terms):
            hit_blocks.append(block_name)
    if hit_blocks:
        print(f"Direct core matches: {', '.join(hit_blocks)}")
    else:
        print("No direct core match — would page-fault to archival.")

    print()
    print("=== Archival page-fault simulation (vault-search) ===")
    # Try vault-search; fall back to a stub if unavailable.
    archival_chunks: list[dict[str, Any]] = []
    try:
        proc = subprocess.run(
            [
                "vault-search",
                query,
                "--top-k",
                "5",
                "--json",
                "--no-socket",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            if isinstance(data, dict):
                results = data.get("results") or data.get("hits") or []
            else:
                results = data
            if isinstance(results, list):
                archival_chunks = results
        else:
            print(
                f"  (vault-search exit {proc.returncode}; "
                f"stub estimate used — stderr: {proc.stderr.strip()[:120]})"
            )
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"  (vault-search unavailable: {exc}; using stub estimate)")

    if archival_chunks:
        archival_chars = 0
        print(f"  Top-{len(archival_chunks)} archival pages:")
        for i, chunk in enumerate(archival_chunks[:5], 1):
            text = ""
            for key in ("text", "content", "chunk", "preview"):
                if key in chunk and chunk[key]:
                    text = str(chunk[key])
                    break
            src = chunk.get("source") or chunk.get("path") or chunk.get("file") or "?"
            archival_chars += len(text)
            print(f"    [{i}] {src[:70]} (~{estimate_tokens(text)} tok)")
        archival_tokens = estimate_tokens("x" * archival_chars) if archival_chars else 2500
    else:
        # Stub: assume 5 × ~500-token chunks.
        archival_tokens = 2500
        print(f"  Stub: 5 × ~500 tokens = ~{archival_tokens} tokens of archival.")

    print()
    print("=== Token-budget comparison ===")
    classic = 17000  # Empirical aggressive pre-load mean.
    virtual = core_tokens + archival_tokens
    print(
        f"  Classic aggressive pre-load (~5 file cat-jel):  ~{classic:,} tokens"
    )
    print(
        f"  Letta virtual:  core ({core_tokens}) + archival ({archival_tokens}) "
        f"= ~{virtual:,} tokens"
    )
    saving = classic - virtual
    pct = (saving / classic) * 100 if classic else 0
    print(f"  Saving:  ~{saving:,} tokens ({pct:.0f}%)")
    print()
    print(
        "NOTE: this is a simulator — no LLM context was mutated. "
        "The agent still uses whichever pre-load strategy `11.11start` defines."
    )
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    if not CORE_PATH.exists():
        print(f"✗ {CORE_PATH} missing — nothing to diff.", file=sys.stderr)
        return 1
    if not SNAPSHOT_PATH.exists():
        print(
            "✗ No snapshot yet — run `vault-core-memory init` to create one.",
            file=sys.stderr,
        )
        return 1
    # Use system diff for human readability.
    result = subprocess.run(
        ["diff", "-u", str(SNAPSHOT_PATH), str(CORE_PATH)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("(no changes since last `init`)")
        return 0
    sys.stdout.write(result.stdout)
    return 0


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vault-core-memory",
        description="Letta-style virtual-context core-memory CLI.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Write fresh core-memory.yaml.")
    p_init.set_defaults(func=cmd_init)

    p_show = sub.add_parser("show", help="Print current core to stdout.")
    p_show.add_argument("--raw", action="store_true", help="Print raw YAML.")
    p_show.set_defaults(func=cmd_show)

    p_update = sub.add_parser("update", help="Mutate a single block.")
    p_update.add_argument("block", choices=BLOCK_ORDER)
    p_update.add_argument("text", help="New content for the block.")
    p_update.set_defaults(func=cmd_update)

    p_size = sub.add_parser("size", help="Token estimate.")
    p_size.set_defaults(func=cmd_size)

    p_sim = sub.add_parser("simulate", help="Simulate archival page-fault.")
    p_sim.add_argument("query")
    p_sim.set_defaults(func=cmd_simulate)

    p_diff = sub.add_parser("diff", help="Show diff since last init.")
    p_diff.set_defaults(func=cmd_diff)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
