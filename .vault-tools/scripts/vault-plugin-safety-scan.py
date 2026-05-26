#!/root/.notebooklm-venv/bin/python3
"""
vault-plugin-safety-scan — static-grep safety scan for third-party `vault-*` binaries.

Sister to `vault-plugin-discover`. Greps the source of each plugin for known
risk patterns (shell invocation, plain-HTTP, literal credentials, etc.).

Same 3-tier classifier as vault-mcp-audit / vault-plugin-hooks-audit:
  HIGH    = blocks commit on staging
  MID     = warn, log to audit
  LOW     = info-only

Usage:
  vault-plugin-safety-scan                  # scan all discovered plugins
  vault-plugin-safety-scan --binary <name>  # scan one
  vault-plugin-safety-scan --json
  vault-plugin-safety-scan --markdown <path>
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

BIN_DIR = Path("/usr/local/bin")

# Patterns are split-string so this scanner itself doesn't trip its own rules.
HIGH = [
    (re.compile(r"shell\s*=\s*True"), "subprocess shell=True"),
    (re.compile(r"\bos" + r"\.sys" + r"tem\("), "os system call"),
    (re.compile(r"\b" + "ev" + r"al\s*\("), "eval call"),
    (re.compile(r"\b" + "ex" + r"ec\s*\("), "exec call"),
    (re.compile(r"curl\s+[^|]*\|\s*(bash|sh)\b"), "curl-piped-to-shell"),
]
MID = [
    (re.compile(r"http://(?!127\.|localhost|0\.0\.0\.0)"), "non-HTTPS non-local URL"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "literal sk- credential"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "literal ghp_ credential"),
    (re.compile(r"xox[bp]-[A-Za-z0-9-]{20,}"), "literal Slack token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "literal AWS access key"),
]
LOW = [
    (re.compile(r"\bsubprocess\."), "subprocess use (review args)"),
]


def scan_one(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return [{"severity": "MID", "rule": "unreadable", "match": ""}]
    findings = []
    for pat, label in HIGH:
        for m in pat.finditer(text):
            findings.append({"severity": "HIGH", "rule": label, "match": m.group(0)[:80]})
    for pat, label in MID:
        for m in pat.finditer(text):
            findings.append({"severity": "MID", "rule": label, "match": m.group(0)[:80]})
    for pat, label in LOW:
        for m in pat.finditer(text):
            findings.append({"severity": "LOW", "rule": label, "match": m.group(0)[:80]})
    return findings


def discover_plugins() -> list[str]:
    try:
        r = subprocess.run(["vault-plugin-discover", "--json"],
                           capture_output=True, text=True, timeout=15)
        plugins = json.loads(r.stdout)
        return [p["name"] for p in plugins]
    except Exception:
        return []


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-plugin-safety-scan")
    ap.add_argument("--binary", help="Scan one named binary instead of all plugins")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", type=Path, help="Write audit MD")
    args = ap.parse_args()

    targets = [args.binary] if args.binary else discover_plugins()
    out = {}
    counts = {"HIGH": 0, "MID": 0, "LOW": 0}
    for name in targets:
        p = BIN_DIR / name
        if not p.is_file():
            continue
        findings = scan_one(p)
        out[name] = findings
        for f in findings:
            counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    if args.json:
        print(json.dumps({"scanned": len(out), "counts": counts, "findings": out},
                          indent=2, ensure_ascii=False))
        return 0 if counts["HIGH"] == 0 else 2

    if args.markdown:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines = [
            "---",
            f"name: plugin safety-scan {ts}",
            "type: audit",
            f"created: {ts}",
            f"updated: {ts}",
            'tags: ["#type/audit", "plugin", "safety"]',
            "---",
            "",
            f"# Plugin safety-scan — {len(out)} uncategorized `vault-*` binary",
            "",
            f"Scanned via `vault-plugin-safety-scan`. Counts: HIGH {counts['HIGH']} / MID {counts['MID']} / LOW {counts['LOW']}.",
            "",
        ]
        if not any(out.values()):
            lines.append("Clean. No risk patterns matched.")
        else:
            for name, fs in out.items():
                if not fs:
                    continue
                lines.append(f"## `{name}`")
                lines.append("")
                lines.append("| severity | rule | match |")
                lines.append("|---|---|---|")
                for f in fs:
                    lines.append(f"| {f['severity']} | {f['rule']} | `{f['match']}` |")
                lines.append("")
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {args.markdown}", file=sys.stderr)
        return 0 if counts["HIGH"] == 0 else 2

    print(f"vault-plugin-safety-scan — {len(out)} scanned · HIGH {counts['HIGH']} / MID {counts['MID']} / LOW {counts['LOW']}")
    for name, fs in out.items():
        if not fs:
            continue
        print(f"\n  {name}")
        for f in fs:
            print(f"    [{f['severity']}] {f['rule']}: {f['match'][:60]}")
    return 0 if counts["HIGH"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
