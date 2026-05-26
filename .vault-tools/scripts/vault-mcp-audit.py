#!/usr/bin/env python3
"""
vault-mcp-audit — scan installed MCP server registrations for risky patterns.

MCP (Model Context Protocol) servers are external tool-providers the agent
talks to. A malicious or misconfigured registration can: execute arbitrary
shell, exfiltrate context to untrusted HTTP endpoints, or leak credentials.

This audit scans every `.mcp.json` / `mcp.json` under `~/.claude/`, `~/.codex/`,
`~/.gemini/` and classifies each server-registration:

  🔴 HIGH  — direct shell-execution (`bash -c`, `sh -c`, `eval`, inline `-c`),
              non-HTTPS URLs (plain `http://` to a non-localhost host),
              or env-var with a literal credential
  🟡 MID   — http/sse server to an unknown domain, npx/uvx without
              version-pin, `rm`/`sudo` in command
  🟢 LOW   — stdio with a known package-runner (docker / playwright / context7),
              https URLs to well-known SaaS providers (Anthropic / GitHub /
              Linear / Asana / Greptile / Notion / etc.)
  ⚪ NEUTRAL — no flagged patterns

Run weekly via cron (Monday 05:45 UTC, after plugin-hooks-audit). Exit code 0.
Strict mode (--strict) exits 1 on HIGH for use in pre-commit / CI gating.

Wiki: 11-wiki/claude-code-harness-blocks.md § 7 (sibling pattern)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
try:
    from vault_atomic import atomic_write  # noqa: E402
except ImportError:
    def atomic_write(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
AUDITS_DIR = VAULT_ROOT / "06-Audits"

DEFAULT_SCAN_ROOTS = [
    Path("/root/.claude"),
    Path("/root/.codex"),
    Path("/root/.gemini"),
]

# Known-OK SaaS / vendor domains. Any HTTPS server to one of these = LOW.
KNOWN_DOMAINS = {
    "anthropic.com", "api.anthropic.com",
    "githubcopilot.com", "api.githubcopilot.com", "github.com",
    "linear.app", "mcp.linear.app",
    "asana.com", "mcp.asana.com",
    "greptile.com", "api.greptile.com",
    "notion.com", "notion.so",
    "openai.com", "api.openai.com",
    "context7.com", "mcp.context7.com",
    "stripe.com",
    "gitlab.com",
    "atlassian.net",
    "vercel.com",
    "supabase.co",
    "firebase.google.com",
}

# Well-known stdio package-runners. Their use is a LOW signal (not no-signal —
# supply-chain still applies, but the runner itself is well-vetted).
KNOWN_RUNNERS = {"docker", "uvx", "playwright", "php"}

# Risky command patterns (HIGH).
HIGH_CMD_PATTERNS = [
    re.compile(r"\bbash\s+-c\b"),
    re.compile(r"\bsh\s+-c\b"),
    re.compile(r"\beval\b"),
    re.compile(r"\bpython3?\s+-c\b"),
    re.compile(r"\bnode\s+-e\b"),
    re.compile(r"\bperl\s+-e\b"),
    re.compile(r"\bcurl\s+[^|]*\|.*sh"),  # curl pipe to shell
]

# MID command patterns.
MID_CMD_PATTERNS = [
    re.compile(r"\brm\s+-rf?\b"),
    re.compile(r"\bsudo\s+", re.IGNORECASE),
    re.compile(r"\bchmod\s+(\+s|7[0-9]{2})"),
    re.compile(r"\bcurl\s+-fsSL?\s+http://"),  # non-HTTPS download
]

# Credential-leak patterns in env values (literal secret looks vs ${VAR}).
CRED_PATTERN_LITERAL = re.compile(
    r"\b(?:sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{30,}|"
    r"pk_[a-zA-Z0-9]{20,}|xox[bp]-[a-zA-Z0-9]+|"
    r"AKIA[0-9A-Z]{16})\b"
)


@dataclass
class McpHit:
    file: Path
    server_name: str
    server_type: str           # stdio / http / sse / ws
    target: str                # command + args OR url
    heat: str                  # HIGH / MID / LOW / NEUTRAL
    matched: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


def _flatten_servers(blob: dict) -> dict:
    """Both {name: cfg} and {mcpServers: {name: cfg}} shapes."""
    if "mcpServers" in blob and isinstance(blob["mcpServers"], dict):
        return blob["mcpServers"]
    return blob


def _classify_url(url: str) -> tuple[str, list[str]]:
    matches: list[str] = []
    try:
        p = urlparse(url)
    except Exception:
        return "MID", ["malformed-url"]
    scheme = (p.scheme or "").lower()
    host = (p.hostname or "").lower()
    if scheme not in ("https", "wss"):
        # http to non-localhost is HIGH; localhost http is LOW
        if host in ("localhost", "127.0.0.1", "::1") and scheme in ("http", "ws"):
            return "LOW", ["localhost-http-ok"]
        if scheme in ("http", "ws"):
            return "HIGH", ["non-https-url"]
        return "MID", [f"unknown-scheme:{scheme}"]
    # HTTPS — known domain → LOW, else MID
    for known in KNOWN_DOMAINS:
        if host == known or host.endswith("." + known):
            return "LOW", [f"known-domain:{known}"]
    return "MID", ["unknown-domain"]


def _classify_command(command: str, args: list[str]) -> tuple[str, list[str]]:
    full = f"{command} {' '.join(args or [])}".strip()
    matches: list[str] = []
    # HIGH first
    for p in HIGH_CMD_PATTERNS:
        if p.search(full):
            matches.append(p.pattern)
    if matches:
        return "HIGH", matches
    # MID
    for p in MID_CMD_PATTERNS:
        if p.search(full):
            matches.append(p.pattern)
    if matches:
        return "MID", matches
    # Known package-runner → LOW
    head = (command or "").split("/")[-1].strip().lower()
    if head in KNOWN_RUNNERS or head == "npx":
        # npx alone is LOW; npx@latest = MID (no version pin)
        for a in (args or []):
            if a == "@latest":
                return "MID", ["npx-no-version-pin"]
        return "LOW", [f"known-runner:{head}"]
    return "NEUTRAL", []


def _classify_env(env: dict) -> tuple[str, list[str]]:
    matches: list[str] = []
    for k, v in (env or {}).items():
        if not isinstance(v, str):
            continue
        if CRED_PATTERN_LITERAL.search(v):
            matches.append(f"literal-credential-in-env:{k}")
    if matches:
        return "HIGH", matches
    return "NEUTRAL", []


def classify_server(name: str, cfg: dict) -> McpHit:
    server_type = cfg.get("type") or ("http" if "url" in cfg else "stdio")
    if "url" in cfg:
        heat, matched = _classify_url(cfg["url"])
        target = cfg["url"]
    else:
        cmd = cfg.get("command", "")
        args = cfg.get("args", []) or []
        heat, matched = _classify_command(cmd, args)
        target = f"{cmd} {' '.join(args)}".strip()
    # Env-var leak check (regardless of url/command)
    env_heat, env_matched = _classify_env(cfg.get("env", {}))
    if env_heat == "HIGH" or (env_heat == "MID" and heat in ("LOW", "NEUTRAL")):
        heat = env_heat
        matched = matched + env_matched
    return McpHit(file=Path(), server_name=name, server_type=server_type,
                  target=target, heat=heat, matched=matched, raw=cfg)


def scan(roots: list[Path]) -> list[McpHit]:
    hits: list[McpHit] = []
    files: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for f in root.rglob(".mcp.json"):
            files.add(f)
        for f in root.rglob("mcp.json"):
            files.add(f)
    for f in sorted(files):
        try:
            blob = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(blob, dict):
            continue
        servers = _flatten_servers(blob)
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            hit = classify_server(name, cfg)
            hit.file = f
            hits.append(hit)
    return hits


def render_markdown(hits: list[McpHit], scanned_files: int) -> str:
    now = datetime.now(timezone.utc)
    iso_week = now.strftime("%G-W%V")
    by_heat: dict[str, list[McpHit]] = {"HIGH": [], "MID": [], "LOW": [], "NEUTRAL": []}
    for h in hits:
        by_heat[h.heat].append(h)

    out: list[str] = []
    out.append("---")
    out.append(f"name: MCP server audit {iso_week}")
    out.append("type: audit")
    out.append(f"created: {now.strftime('%Y-%m-%dT%H:%M:%S%z')}")
    out.append('tags: ["#type/audit", "safety", "mcp-audit"]')
    out.append("generated_by: vault-mcp-audit")
    out.append("---")
    out.append("")
    out.append(f"# MCP server audit {iso_week}")
    out.append("")
    out.append(
        f"> Auto-generated by `vault-mcp-audit` at {now.strftime('%Y-%m-%dT%H:%M:%S%z')}. "
        f"Scanned **{scanned_files} .mcp.json files** under `~/.claude/`, `~/.codex/`, `~/.gemini/`."
    )
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- **{len(hits)}** total server registrations")
    out.append(f"- 🔴 **{len(by_heat['HIGH'])} HIGH** (shell-exec, non-HTTPS, literal credentials)")
    out.append(f"- 🟡 **{len(by_heat['MID'])} MID** (unknown HTTPS domain, unpinned npx, destructive cmd)")
    out.append(f"- 🟢 **{len(by_heat['LOW'])} LOW** (known SaaS HTTPS, known package-runner)")
    out.append(f"- ⚪ **{len(by_heat['NEUTRAL'])} NEUTRAL**")
    out.append("")
    out.append("**Heat definitions:**")
    out.append("")
    out.append("- 🔴 **HIGH**: shell-exec patterns (`bash -c`, `eval`, `python -c`), "
               "non-HTTPS URL to a non-localhost host, or env-var with a literal credential "
               "(`sk-*`, `ghp_*`, `xox[bp]-*`, AWS access-key shape)")
    out.append("- 🟡 **MID**: HTTP/SSE to an unknown domain, `npx @latest` without a version pin, "
               "`rm`/`sudo` in command")
    out.append("- 🟢 **LOW**: HTTPS to known SaaS (Anthropic / GitHub / Linear / Asana / Greptile / Notion / etc.) "
               "or stdio runner from known-list (docker / uvx / playwright)")
    out.append("- ⚪ **NEUTRAL**: no flagged patterns")
    out.append("")

    def block(heat: str, title: str):
        if not by_heat[heat]:
            return
        out.append(f"## {STATUS_ICON[heat]} {title}")
        out.append("")
        out.append("| Server | Type | Target | File | Matched |")
        out.append("|---|---|---|---|---|")
        for h in by_heat[heat]:
            try:
                rel = h.file.relative_to(Path.home())
                file_disp = f"~/{rel}"
            except ValueError:
                file_disp = str(h.file)
            patt = ", ".join(f"`{p}`" for p in h.matched[:3]) or "—"
            target_disp = h.target[:80] + ("…" if len(h.target) > 80 else "")
            out.append(f"| `{h.server_name}` | `{h.server_type}` | `{target_disp}` | "
                       f"`{file_disp}` | {patt} |")
        out.append("")

    block("HIGH", "HIGH-heat — action recommended")
    block("MID",  "MID-heat — eyeball")
    block("LOW",  "LOW-heat (informational)")

    out.append("## Related")
    out.append("")
    out.append("- [[../11-wiki/claude-code-harness-blocks]] § 7 — sibling plugin-hooks-audit pattern")
    out.append("- [[../11-wiki/tool-sandbox-eval-playbook]] — eval flow for any new MCP server")
    out.append("- [[../11-wiki/external-skill-cherry-pick]] — selective cherry-pick over wholesale install")
    out.append("")
    return "\n".join(out)


STATUS_ICON = {"HIGH": "🔴", "MID": "🟡", "LOW": "🟢", "NEUTRAL": "⚪"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit installed MCP server registrations")
    ap.add_argument("--roots", nargs="+", default=None,
                    help="dirs to scan (default: ~/.claude, ~/.codex, ~/.gemini)")
    ap.add_argument("--json", action="store_true",
                    help="emit JSON to 06-Audits/ instead of markdown")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any HIGH hit (for pre-commit/CI gating)")
    ap.add_argument("--quiet", action="store_true", help="suppress stdout summary")
    args = ap.parse_args()

    roots = [Path(r) for r in args.roots] if args.roots else DEFAULT_SCAN_ROOTS
    # count files scanned for the summary line
    scanned = 0
    for root in roots:
        if root.exists():
            scanned += len(list(root.rglob(".mcp.json"))) + len(list(root.rglob("mcp.json")))
    hits = scan(roots)
    high = len([h for h in hits if h.heat == "HIGH"])
    mid  = len([h for h in hits if h.heat == "MID"])
    low  = len([h for h in hits if h.heat == "LOW"])
    neutral = len([h for h in hits if h.heat == "NEUTRAL"])

    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    iso_week = datetime.now(timezone.utc).strftime("%G-W%V")

    if args.json:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scanned_files": scanned,
            "total_hits": len(hits),
            "by_heat": {"HIGH": high, "MID": mid, "LOW": low, "NEUTRAL": neutral},
            "hits": [
                {
                    "file": str(h.file),
                    "server_name": h.server_name,
                    "server_type": h.server_type,
                    "target": h.target,
                    "heat": h.heat,
                    "matched": h.matched,
                }
                for h in hits
            ],
        }
        out_path = AUDITS_DIR / f"mcp-audit-{iso_week}.json"
        atomic_write(out_path, json.dumps(payload, indent=2, ensure_ascii=False))
        if not args.quiet:
            print(f"  scanned {scanned} .mcp.json, {len(hits)} servers · "
                  f"🔴 {high} · 🟡 {mid} · 🟢 {low} · ⚪ {neutral}")
            print(f"✓ JSON written: {out_path}")
    else:
        md = render_markdown(hits, scanned)
        out_path = AUDITS_DIR / f"mcp-audit-{iso_week}.md"
        atomic_write(out_path, md)
        if not args.quiet:
            print(f"  scanned {scanned} .mcp.json, {len(hits)} servers · "
                  f"🔴 {high} · 🟡 {mid} · 🟢 {low} · ⚪ {neutral}")
            print(f"✓ Audit written: {out_path}")

    if args.strict and high > 0:
        print(f"⚠ STRICT mode: {high} HIGH-heat hits — failing", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
