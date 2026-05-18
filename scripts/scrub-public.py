#!/usr/bin/env python3
"""
scrub-public.py — Idempotens filter a Superintelligent Vault élő tartalmából
publishable open-source repo-vá.

Default: DRY-RUN. `--apply` flag-gel ténylegesen ír a target_repo-ba.

Algoritmus:
  1. Olvasd a scrub-rules.yaml-t
  2. Listázd az összes fájlt a source_vault-ban
  3. Match-eld minden fájl-path-et az include_paths globjaival
  4. Ha match, ellenőrizd hogy NINCS rajta always_skip pattern → publish-kandidát
  5. A publish-kandidátokon string-replace
  6. Verifikáld forbidden_strings (assert NOT IN content)
  7. Stats: file-count between expected_min/max
  8. Apply mode: rsync-like copy (mtime preservation, idempotent)
"""
import argparse
import fnmatch
import json
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print('[ERROR] PyYAML not installed. Run: pip install pyyaml', file=sys.stderr)
    sys.exit(1)


def _glob_to_regex(p: str) -> str:
    """Recursive-glob aware: '**/' = 0+ directory segments."""
    # Escape regex metacharacters except *, /, ?, [, ]
    out = []
    i = 0
    while i < len(p):
        c = p[i]
        if c == '*' and i + 1 < len(p) and p[i + 1] == '*':
            # ** — match 0+ chars including slashes
            # If followed by /, also consume the trailing slash (= 0+ dirs)
            if i + 2 < len(p) and p[i + 2] == '/':
                out.append('(?:.*/)?')
                i += 3
            else:
                out.append('.*')
                i += 2
        elif c == '*':
            out.append('[^/]*')
            i += 1
        elif c == '?':
            out.append('[^/]')
            i += 1
        elif c in '.^$+(){}|\\':
            out.append('\\' + c)
            i += 1
        else:
            out.append(c)
            i += 1
    return '^' + ''.join(out) + '$'


def matches_any_glob(rel_path: str, patterns: list) -> bool:
    """Glob-match relatív path-re. Pattern lehet 'foo/**/*.md' vagy '!foo/exclude'."""
    matched = False
    for p in patterns:
        is_neg = p.startswith('!')
        glob = p[1:] if is_neg else p
        # Both fnmatch (no-** support) and our regex (recursive **)
        is_match = fnmatch.fnmatch(rel_path, glob) or bool(re.match(_glob_to_regex(glob), rel_path))
        if is_match:
            matched = False if is_neg else True
    return matched


def apply_replacements(content: str, replacements: list) -> tuple:
    """Returns (replaced_content, replacement_count)."""
    count = 0
    for r in replacements:
        find_str = r['find']
        rep_str = r['replace']
        if find_str in content:
            count += content.count(find_str)
            content = content.replace(find_str, rep_str)
    return content, count


def check_forbidden(content: str, forbidden: list, path: str) -> list:
    """Returns list of forbidden strings still present."""
    return [f for f in forbidden if f in content]


def list_source_files(source_vault: Path) -> list:
    """Returns sorted list of (abs_path, rel_path)."""
    files = []
    for f in source_vault.rglob('*'):
        if f.is_file():
            try:
                rel = f.relative_to(source_vault).as_posix()
                files.append((f, rel))
            except ValueError:
                continue
    return sorted(files, key=lambda x: x[1])


def classify_files(files: list, rules: dict) -> tuple:
    """Returns (publish_candidates, skip_reasons)."""
    include = rules.get('include_paths', [])
    always_skip = rules.get('always_skip', [])
    publish = []
    skipped = []
    for abs_path, rel in files:
        # Step 1: matches always_skip → SKIP
        if matches_any_glob(rel, always_skip):
            skipped.append((rel, 'always_skip'))
            continue
        # Step 2: matches include_paths → PUBLISH
        if matches_any_glob(rel, include):
            publish.append((abs_path, rel))
        else:
            skipped.append((rel, 'not_in_include'))
    return publish, skipped


def process_publish(publish: list, rules: dict, target: Path, apply_mode: bool) -> dict:
    """For each publishable file: replace + forbidden-check + write."""
    stats = {
        'written': 0,
        'replaced_lines': 0,
        'forbidden_violations': [],
        'errors': [],
    }
    replacements = rules.get('replacements', [])
    forbidden = rules.get('forbidden_strings', [])

    for abs_path, rel in publish:
        try:
            # Binary detection (skip image, sqlite, etc.)
            with abs_path.open('rb') as f:
                head = f.read(1024)
            if b'\x00' in head:
                # Binary file — copy as-is, NO scrub
                if apply_mode:
                    dst = target / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(abs_path, dst)
                stats['written'] += 1
                continue

            content = abs_path.read_text(encoding='utf-8', errors='replace')
            new_content, replaced = apply_replacements(content, replacements)
            stats['replaced_lines'] += replaced

            # Forbidden check
            violations = check_forbidden(new_content, forbidden, rel)
            if violations:
                stats['forbidden_violations'].append((rel, violations))
                continue   # NEM írjuk

            if apply_mode:
                dst = target / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(new_content, encoding='utf-8')
            stats['written'] += 1
        except Exception as e:
            stats['errors'].append((rel, str(e)))

    return stats


def main():
    ap = argparse.ArgumentParser(description='Scrub vault content for public repo.')
    ap.add_argument('--rules', default='scripts/scrub-rules.yaml', help='Rules YAML')
    ap.add_argument('--apply', action='store_true', help='Actually write files (default dry-run)')
    ap.add_argument('--verbose', '-v', action='store_true')
    ap.add_argument('--show-skipped', action='store_true', help='List skipped paths')
    args = ap.parse_args()

    rules_path = Path(args.rules)
    if not rules_path.exists():
        # Try relative to script dir
        rules_path = Path(__file__).parent / 'scrub-rules.yaml'
    rules = yaml.safe_load(rules_path.read_text(encoding='utf-8'))

    source = Path(rules['source_vault'])
    target = Path(rules['target_repo'])

    if not source.exists():
        print(f'[ERROR] Source vault not found: {source}', file=sys.stderr)
        sys.exit(1)

    print(f'[INFO] Source vault: {source}')
    print(f'[INFO] Target repo:  {target}')
    print(f'[INFO] Mode: {"APPLY" if args.apply else "DRY-RUN"}')

    files = list_source_files(source)
    print(f'[INFO] Source files scanned: {len(files)}')

    publish, skipped = classify_files(files, rules)
    print(f'[INFO] Publish-candidates: {len(publish)}')
    print(f'[INFO] Skipped: {len(skipped)}')

    if args.show_skipped:
        for rel, reason in skipped[:50]:
            print(f'  SKIP[{reason}]  {rel}')

    # Process publish-candidates
    stats = process_publish(publish, rules, target, args.apply)

    print(f'\n=== STATS ===')
    print(f'  Written:                  {stats["written"]}')
    print(f'  Replacements applied:     {stats["replaced_lines"]}')
    print(f'  Forbidden-violations:     {len(stats["forbidden_violations"])}')
    print(f'  Errors:                   {len(stats["errors"])}')

    # Verifications
    min_f = rules.get('expected_min_files', 0)
    max_f = rules.get('expected_max_files', 9999)
    if stats['written'] < min_f:
        print(f'[FAIL] Written ({stats["written"]}) < expected_min ({min_f})')
        sys.exit(2)
    if stats['written'] > max_f:
        print(f'[FAIL] Written ({stats["written"]}) > expected_max ({max_f}) — too permissive!')
        sys.exit(3)

    if stats['forbidden_violations']:
        print(f'\n[FAIL] FORBIDDEN STRINGS DETECTED in {len(stats["forbidden_violations"])} files:')
        for rel, viols in stats['forbidden_violations'][:10]:
            print(f'  {rel}  →  {viols}')
        sys.exit(4)

    if stats['errors']:
        print(f'\n[WARN] {len(stats["errors"])} errors:')
        for rel, err in stats['errors'][:5]:
            print(f'  {rel}: {err}')

    print(f'\n[SUCCESS] Scrub complete. ' + ('Files written.' if args.apply else 'Dry-run only, NO files written.'))


if __name__ == '__main__':
    main()
