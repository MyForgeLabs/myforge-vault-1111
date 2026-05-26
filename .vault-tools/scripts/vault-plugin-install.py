#!/root/.notebooklm-venv/bin/python3
"""
vault-plugin-install — install third-party `vault-*` plugins with manifest +
signature verification.

This is the Day-0 skeleton for the Plugin Marketplace v1 sprint. It builds
on the v1.0.15 foundation:

  - `vault-plugin-discover` — finds uncategorised `vault-*` binaries on PATH
  - `vault-plugin-safety-scan` — risk-classifies binary content
  - `vault_audit_base` — atomic-write + audit-MD helpers

It adds:

  - `~/.vault-plugins/registry.json` — central registry mapping plugin name to
    source URL, version, and SHA-256 digest
  - `~/.vault-plugins/installed.json` — what's currently installed (idempotency)
  - `vault-plugin-install <name>` — looks up registry, fetches, verifies digest,
    runs safety-scan, prompts for symlink-creation under /usr/local/bin/
  - `vault-plugin-install --from-file <path>` — local install (W1+ network
    fetch out of scope today)
  - `vault-plugin-install --list` — show installed
  - `vault-plugin-install --uninstall <name>` — remove symlink + installed.json entry

Day-0 defaults:
  - `--dry-run` is the default. Mutations require `--apply`.
  - No network fetch. `--from-file <path>` only.
  - SHA-256 verification optional today (warn but don't block) since the
    registry is empty.

Status: Day-0 skeleton 2026-05-25.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_HOME = Path(os.environ.get("VAULT_PLUGIN_HOME", "/root/.vault-plugins"))
INSTALL_TARGET = Path("/usr/local/bin")
REGISTRY = PLUGIN_HOME / "registry.json"
INSTALLED = PLUGIN_HOME / "installed.json"


def _load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"⚠ {path} is malformed; using default", file=sys.stderr)
        return default


def _save_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(path)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _safety_scan(binary_path: Path) -> dict | None:
    """Run vault-plugin-safety-scan --binary on the candidate, return JSON."""
    try:
        proc = subprocess.run(
            ["vault-plugin-safety-scan", "--binary", str(binary_path),
             "--json"],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0:
            print(f"⚠ safety-scan exit {proc.returncode}: "
                  f"{proc.stderr.strip()[:200]}", file=sys.stderr)
            return None
        return json.loads(proc.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as exc:
        print(f"⚠ safety-scan unavailable: {exc}", file=sys.stderr)
        return None


def _verify_digest(binary_path: Path, expected: str | None) -> tuple[bool, str]:
    """Return (ok, actual_digest). ok=True if expected is None (skip) OR matches."""
    actual = _sha256(binary_path)
    if expected is None:
        return True, actual
    return (actual == expected, actual)


def cmd_install(args: argparse.Namespace) -> int:
    registry = _load_json(REGISTRY, {"plugins": {}})
    installed = _load_json(INSTALLED, {"installed": {}})

    # Determine source path
    if args.from_file:
        src = Path(args.from_file).resolve()
        if not src.exists() or not src.is_file():
            print(f"✗ source file not found: {src}", file=sys.stderr)
            return 1
        plugin_name = args.name or src.name
        expected_digest = None
    else:
        plugin_name = args.name
        if not plugin_name:
            print("✗ --name required when not using --from-file", file=sys.stderr)
            return 2
        entry = registry.get("plugins", {}).get(plugin_name)
        if not entry:
            print(f"✗ '{plugin_name}' not in registry "
                  f"({REGISTRY}). Day-0: use --from-file for local install.",
                  file=sys.stderr)
            return 1
        # Day-0: no network fetch. Skeleton-only.
        print(f"⚠ Day-0 skeleton: network fetch of '{plugin_name}' not "
              f"implemented. Registry entry: {entry}", file=sys.stderr)
        print(f"  Use: vault-plugin-install --name {plugin_name} "
              f"--from-file <local-path>", file=sys.stderr)
        return 2

    # Plan: where will it land?
    target = INSTALL_TARGET / plugin_name
    plugin_dir = PLUGIN_HOME / plugin_name
    stored_binary = plugin_dir / plugin_name

    print(f"Install plan for '{plugin_name}':")
    print(f"  source:        {src}")
    print(f"  storage:       {stored_binary}")
    print(f"  symlink:       {target}")

    if target.exists() or target.is_symlink():
        existing = target.resolve() if target.is_symlink() else target
        print(f"⚠ target already exists: {target} → {existing}")
        if not args.force:
            print(f"  Use --force to overwrite.", file=sys.stderr)
            return 1

    # Digest
    ok, actual = _verify_digest(src, args.expected_sha256)
    print(f"  sha256:        {actual}")
    if args.expected_sha256:
        if not ok:
            print(f"✗ DIGEST MISMATCH (expected {args.expected_sha256})",
                  file=sys.stderr)
            return 1
        print(f"  digest match:  ✓")
    else:
        print(f"  digest match:  (no expected digest — skipped)")

    # Safety scan — derive heat from counts (HIGH > 0 → HIGH, else MID/LOW/NONE)
    scan = _safety_scan(src)
    if scan is not None:
        counts = scan.get("counts", {}) or {}
        if counts.get("HIGH", 0) > 0:
            heat = "HIGH"
        elif counts.get("MID", 0) > 0:
            heat = "MID"
        elif counts.get("LOW", 0) > 0:
            heat = "LOW"
        else:
            heat = "NONE"
        findings = scan.get("findings", {}) or {}
        flat = sum(len(v) for v in findings.values())
        print(f"  safety-scan:   heat={heat} ({flat} finding(s): "
              f"H{counts.get('HIGH',0)}/M{counts.get('MID',0)}/L{counts.get('LOW',0)})")
        # Day-0: warn on HIGH, don't block (the user is explicitly installing)
        if heat == "HIGH" and not args.allow_high_heat:
            print(f"⚠ Plugin classified HIGH heat. Re-run with "
                  f"--allow-high-heat to proceed.", file=sys.stderr)
            return 1
        # Save derived heat back for installed.json record
        scan["heat"] = heat
    else:
        print(f"  safety-scan:   (unavailable)")

    if not args.apply:
        print(f"\n(dry-run — use --apply to actually install)")
        return 0

    # Apply: copy to storage, symlink to target, update installed.json
    plugin_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, stored_binary)
    stored_binary.chmod(0o755)
    if target.is_symlink() or target.exists():
        target.unlink()
    target.symlink_to(stored_binary)
    installed.setdefault("installed", {})[plugin_name] = {
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_file": str(src),
        "sha256": actual,
        "safety_heat": (scan or {}).get("heat") or "unknown",
        "stored_at": str(stored_binary),
        "symlink": str(target),
    }
    _save_json(INSTALLED, installed)
    print(f"\n✓ Installed: {target} → {stored_binary}")
    print(f"  Recorded in {INSTALLED}")
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    installed = _load_json(INSTALLED, {"installed": {}})
    name = args.name
    entry = installed.get("installed", {}).get(name)
    if entry is None:
        print(f"✗ '{name}' is not in {INSTALLED}", file=sys.stderr)
        return 1
    target = Path(entry["symlink"])
    stored = Path(entry["stored_at"])

    print(f"Uninstall plan for '{name}':")
    print(f"  remove symlink: {target}")
    print(f"  remove storage: {stored}")
    if not args.apply:
        print(f"\n(dry-run — use --apply to actually uninstall)")
        return 0

    if target.is_symlink() or target.exists():
        target.unlink()
    if stored.exists():
        stored.unlink()
    plugin_dir = stored.parent
    if plugin_dir.exists() and plugin_dir.is_dir() and not any(plugin_dir.iterdir()):
        plugin_dir.rmdir()
    del installed["installed"][name]
    _save_json(INSTALLED, installed)
    print(f"\n✓ Uninstalled '{name}'")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    installed = _load_json(INSTALLED, {"installed": {}})
    inst = installed.get("installed", {})
    if args.format == "json":
        print(json.dumps(installed, indent=2, ensure_ascii=False))
        return 0
    if not inst:
        print(f"No plugins installed via vault-plugin-install.\n"
              f"  Registry: {REGISTRY}\n"
              f"  Installed: {INSTALLED}")
        return 0
    print(f"{len(inst)} plugin(s) installed:")
    for name, e in sorted(inst.items()):
        print(f"  {name:<30s}  heat={e.get('safety_heat','?'):<7s} "
              f"sha={e.get('sha256','?')[:12]}  installed={e.get('installed_at')}")
    return 0


def cmd_registry(args: argparse.Namespace) -> int:
    registry = _load_json(REGISTRY, {"plugins": {}})
    if args.format == "json":
        print(json.dumps(registry, indent=2, ensure_ascii=False))
        return 0
    plugins = registry.get("plugins", {})
    if not plugins:
        print(f"Registry is empty: {REGISTRY}")
        print(f"  Add entries with `vault-plugin-install --registry-add ...` (W1+)")
        return 0
    print(f"{len(plugins)} plugin(s) in registry:")
    for name, e in sorted(plugins.items()):
        print(f"  {name:<30s}  version={e.get('version','?')} "
              f"source={e.get('source','?')[:50]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-plugin-install",
        description="Install third-party vault-* plugins with safety-scan + digest verification.")
    sub = ap.add_subparsers(dest="cmd", required=False)

    # default: install (so `vault-plugin-install foo` works)
    p_inst = sub.add_parser("install", help="Install a plugin (default).")
    p_inst.add_argument("name", nargs="?",
                        help="plugin name (binary name without prefix)")
    p_inst.add_argument("--from-file", help="install from local file")
    p_inst.add_argument("--expected-sha256", help="expected SHA-256 digest")
    p_inst.add_argument("--apply", action="store_true",
                        help="apply changes (default: dry-run)")
    p_inst.add_argument("--force", action="store_true",
                        help="overwrite existing symlink")
    p_inst.add_argument("--allow-high-heat", action="store_true",
                        help="install even if safety-scan flags HIGH")
    p_inst.set_defaults(func=cmd_install)

    p_un = sub.add_parser("uninstall", help="Remove a plugin.")
    p_un.add_argument("name")
    p_un.add_argument("--apply", action="store_true")
    p_un.set_defaults(func=cmd_uninstall)

    p_ls = sub.add_parser("list", help="List installed plugins.")
    p_ls.add_argument("--format", choices=["text", "json"], default="text")
    p_ls.set_defaults(func=cmd_list)

    p_reg = sub.add_parser("registry", help="Show registry.")
    p_reg.add_argument("--format", choices=["text", "json"], default="text")
    p_reg.set_defaults(func=cmd_registry)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
