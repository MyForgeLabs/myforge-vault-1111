#!/usr/bin/env python3
"""
vault-nb-ingest — NotebookLM deep-research report → KO-DB fact ingest.

Brainstorm idea #22 from `06-Audits/2026-05-19 SV new development ideas brainstorm.md`.

Why
---
NotebookLM "deep research" custom-report MD files contain dense factual content
(canonical multi-source synthesis with cited claims) but the existing vault
crystallization pipeline only flows session/wiki/adr text into KO-DB. These
7-section reports never reach the structured fact-store, so cross-source
corroboration ranking misses them.

This script mirrors the `vault-ko-ingest` 2-phase pending pattern:
  1. Scans `10-raw/external/notebooklm/` (+ legacy locations) for fresh reports
  2. Parses the 7-section MD with a NotebookLM-aware heuristic
  3. Pre-filters claim blocks (drops anchor-only / reference-only / questions)
  4. Phase 1: writes per-batch request.json files to /tmp/vault-nb-ingest-pending/
  5. Phase 2: harvests response.json files, validates triplets, deduplicates,
     and (if --apply + env-gate) inserts into KO-DB with source_type='notebooklm'.

Safety
------
Two-layer apply gate: `--apply` flag AND `VAULT_NB_INGEST_APPLY=1` env. Either
alone keeps dry-run. Default is dry-run.

Forbidden subject prefixes (mirrors vault-ko-remap-legacy):
  AGENTS.md, 00-Meta/, 11.11*, MEMORY.md

PII filter drops triplets whose object matches email/credential patterns.

Usage
-----
    vault-nb-ingest --file <path> --dry-run
    vault-nb-ingest --scan-dir 10-raw/external/notebooklm/ --days 7 --dry-run
    VAULT_NB_INGEST_APPLY=1 vault-nb-ingest --apply --days 1 --skip-existing
    vault-nb-ingest --help            # prints suggested cron at end
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
from vault_atomic import atomic_append_jsonl, atomic_write_json  # noqa: E402


# ============================================================================
# Configuration
# ============================================================================

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
KO_DB = Path(os.environ.get("VAULT_KO_DB", str(VAULT_ROOT / ".vault-ko" / "facts.db")))
PENDING_DIR = Path("/tmp/vault-nb-ingest-pending")
AUDIT_LOG = VAULT_ROOT / "06-Audits" / "vault-nb-ingest-log.jsonl"

# Where NotebookLM reports might live. Order matters — first hit wins per file.
DEFAULT_SCAN_DIRS = [
    VAULT_ROOT / "10-raw" / "external" / "notebooklm",   # canonical target
    VAULT_ROOT / "10-raw" / "notebooklm",                # short-form
    VAULT_ROOT / "10-raw",                               # legacy: NotebookLM-* files
    VAULT_ROOT / "06-Audits",                            # current real location
]

# How we detect that a markdown file IS a NotebookLM-output report.
# A file qualifies if EITHER its name matches one of these patterns OR its
# YAML frontmatter contains `notebook-id:` / `conversation-id:`.
NB_FILENAME_PATTERNS = [
    re.compile(r"notebooklm", re.IGNORECASE),
    re.compile(r"\bNotebookLM\b"),
    re.compile(r"\bNB\s+cross-projekt\b", re.IGNORECASE),
    re.compile(r"\bresearch[- ]output\b", re.IGNORECASE),
    re.compile(r"\bdeep[- ]research\b", re.IGNORECASE),
]
NB_FRONTMATTER_KEYS = ("notebook-id", "conversation-id")

# Forbidden subject prefixes — mirrors vault-ko-remap-legacy
FORBIDDEN_SUBJECT_PREFIXES = (
    "AGENTS.md", "00-Meta/", "00-Meta", "11.11", "MEMORY.md",
)

# 38-predicate vocab (mirrors vault-ko-ingest PREDICATE_VOCAB)
PREDICATE_VOCAB = {
    "value_typing": [
        "has_count", "has_url", "has_path", "has_port", "has_version",
        "has_color", "has_cost", "has_credential", "has_threshold",
        "has_string_value", "has_status", "has_date",
    ],
    "typed_uses": [
        "uses_database", "uses_framework", "uses_runtime", "uses_library",
        "uses_protocol", "uses_algorithm", "uses_endpoint", "uses_model",
        "uses_flag", "uses_pattern",
    ],
    "relational": [
        "runs_on", "deployed_at", "migrates_from", "tested_with",
        "monitored_by", "authored_by", "documented_in", "triggered_by",
        "extends", "replaces", "fixes",
    ],
    "universal": [
        "depends_on", "produces", "requires", "applies_to",
        "causes", "equals", "decided_at",
    ],
    "fallback": ["has_value", "uses"],
}
VALID_PREDICATES: set[str] = {
    p for group in PREDICATE_VOCAB.values() for p in group
}

# PII patterns — object values matching any of these get the triplet dropped.
PII_PATTERNS = [
    # email
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    # JWT-ish token
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    # GitHub PAT
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    # Generic API key shape
    re.compile(r"\b(?:api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}", re.IGNORECASE),
    # AWS access key id
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # Bearer token
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}", re.IGNORECASE),
    # SSH private-key marker
    re.compile(r"-----BEGIN\s+(?:RSA|OPENSSH|DSA|EC)?\s*PRIVATE\s+KEY-----"),
]

# Pre-filter regexes
RE_ANCHOR_ONLY = re.compile(
    r"^(?:\s*[-*]\s*)?(?:as discussed|see (?:section|above|below)|"
    r"lásd (?:fent|lent|fent[ie]|alább|feljebb|szekció)|"
    r"említettem|previously mentioned)\b",
    re.IGNORECASE,
)
RE_URL_ONLY = re.compile(r"^\s*(?:[-*]\s+)?https?://\S+\s*$", re.MULTILINE)
RE_QUESTION_BLOCK = re.compile(r"^\s*(?:[-*]\s+)?[^.!]*\?\s*$", re.MULTILINE)
RE_HAS_VERB_SENTENCE = re.compile(
    r"\b(?:is|are|was|were|has|have|had|does|do|did|"
    r"van|vannak|volt|voltak|kell|lett|legyen|"
    r"uses?|requires?|depends?|supports?|provides?|"
    r"használ|igényel|függ|támogat|biztosít|tartalmaz|"
    r"runs?|hosts?|stores?|caches?|deploys?|deployed|implements?|"
    r"fut|tárol|cache|deploy|implementál)\b",
    re.IGNORECASE,
)

EXTRACTION_PROMPT_TEMPLATE = """\
Extract structured facts from the NotebookLM deep-research claim block below
as (subject, predicate, object) triples.

CONTEXT
-------
Source: NotebookLM custom-report, section "{section_title}".
Provenance: {provenance}

Each claim block is a section of a multi-source synthesis. Focus on
DECLARATIVE FACTS, not questions, not anchor references, not URL-only blocks.

PREDICATE VOCABULARY (use ONLY these — pick the MOST SPECIFIC one):

VALUE-TYPING (object is a literal value):
  has_count, has_url, has_path, has_port, has_version, has_color, has_cost,
  has_credential, has_threshold, has_string_value, has_status, has_date

TYPED-USES (object is a tool/component):
  uses_database, uses_framework, uses_runtime, uses_library, uses_protocol,
  uses_algorithm, uses_endpoint, uses_model, uses_flag, uses_pattern

ACTION / RELATIONAL:
  runs_on, deployed_at, migrates_from, tested_with, monitored_by,
  authored_by, documented_in, triggered_by, extends, replaces, fixes

UNIVERSAL (fallback):
  depends_on, produces, requires, applies_to, causes, equals, decided_at

FALLBACK (use ONLY if no typed alternative fits):
  has_value, uses

EXAMPLES
--------
"NotebookLM custom report contains 7 sections" →
  {{"subject": "NotebookLM custom report", "predicate": "has_count",
    "object": "7 sections", "confidence": 0.95}}

"KGC-4 uses Strapi 5 as headless CMS" →
  {{"subject": "KGC-4", "predicate": "uses_framework",
    "object": "Strapi 5", "confidence": 0.95}}

"Next.js revalidateTag invalidates the ISR cache in ~300ms globally" →
  {{"subject": "Next.js revalidateTag", "predicate": "has_count",
    "object": "~300ms global cache invalidation", "confidence": 0.85}}

AVOID
-----
- Triples where the subject starts with: AGENTS.md, 00-Meta/, 11.11, MEMORY.md
- Triples whose object contains credentials, emails, tokens, PII
- Triples whose object is just a citation/URL-only block

Output: JSON array of triples. No commentary.

CLAIM BLOCKS:
{claim_blocks}
"""

BATCH_SIZE = 20
MAX_BATCHES_PER_FILE = 8


# ============================================================================
# Data classes
# ============================================================================


@dataclass
class ClaimBlock:
    section_title: str
    text: str
    line_start: int


@dataclass
class FileReport:
    path: Path
    provenance: str
    parsed_blocks: int = 0
    filtered_blocks: int = 0
    batches_written: int = 0
    triplets_collected: int = 0
    triplets_after_validation: int = 0
    triplets_after_pii: int = 0
    triplets_after_forbidden: int = 0
    new_facts: int = 0
    updated_facts: int = 0
    skipped_existing: int = 0
    skipped_invalid_predicate: int = 0
    skipped_pii: int = 0
    skipped_forbidden: int = 0
    pending_request_paths: list[str] = field(default_factory=list)
    pending_response_paths: list[str] = field(default_factory=list)
    error: str | None = None


# ============================================================================
# Discovery
# ============================================================================


def is_notebooklm_file(path: Path) -> bool:
    """Detect whether a markdown file is a NotebookLM-output report.

    Two signals: (a) frontmatter contains `notebook-id:` or `conversation-id:`
    (strongest signal — the NotebookLM CLI / vault-nb-* scripts stamp these
    into the YAML when an artifact is downloaded), or (b) filename matches a
    NotebookLM-output naming convention AND the path is not under a path that
    just *mentions* NotebookLM (08-Sessions/, 11-wiki/).

    Session files like `2026-04-23-notebooklm-obsidian-vault.md` are session
    write-ups ABOUT NotebookLM, not NotebookLM reports themselves — exclude.
    Wiki files (`11-wiki/notebooklm-*.md`) are evergreen docs — exclude.
    """
    # Exclusions by path
    try:
        rel = path.relative_to(VAULT_ROOT)
        rel_str = str(rel)
    except ValueError:
        rel_str = str(path)
    if rel_str.startswith("08-Sessions/") or rel_str.startswith("11-wiki/"):
        return False

    # Lightweight frontmatter peek (only first ~50 lines)
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            head_lines = []
            for i, line in enumerate(fh):
                head_lines.append(line)
                if i > 50:
                    break
        head = "".join(head_lines)
    except OSError:
        return False

    if head.startswith("---"):
        fm_end = head.find("\n---", 3)
        if fm_end != -1:
            fm = head[3:fm_end]
            for key in NB_FRONTMATTER_KEYS:
                if re.search(rf"^{re.escape(key)}\s*:", fm, re.MULTILINE):
                    return True

    # Fallback: filename pattern.
    name = path.name
    for pat in NB_FILENAME_PATTERNS:
        if pat.search(name):
            return True
    return False


def discover_files(scan_dirs: Iterable[Path], days: int) -> list[Path]:
    """Find NotebookLM-output markdown files modified within `days` days."""
    cutoff = time.time() - days * 86400
    seen: set[Path] = set()
    results: list[Path] = []
    for d in scan_dirs:
        if not d.exists():
            continue
        for md in d.rglob("*.md"):
            if md in seen:
                continue
            try:
                mtime = md.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                continue
            if not is_notebooklm_file(md):
                continue
            seen.add(md)
            results.append(md)
    results.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return results


# ============================================================================
# Parsing — 7-section NotebookLM heuristic
# ============================================================================


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    after = text[end + 4:]
    return after.lstrip("\n")


def parse_claim_blocks(text: str) -> list[ClaimBlock]:
    """Parse a NotebookLM report into (section_title, text) claim blocks.

    Strategy (NotebookLM custom-report aware):
      1. Strip YAML frontmatter.
      2. Walk the markdown. Track the most-recent `## ` heading as the current
         section. Each `### ` heading (or paragraph break under a `## `) starts
         a new claim block.
      3. If a file has no `### ` headings at all, fall back to splitting on
         double-newline paragraph breaks under each `## ` section.
      4. Skip code blocks (```), HR (`---`), and table-only blocks.

    Returns list of ClaimBlock with section_title, text, line_start.
    """
    text = strip_frontmatter(text)
    lines = text.splitlines()
    blocks: list[ClaimBlock] = []

    current_h2 = ""
    current_h3 = ""
    block_lines: list[str] = []
    block_start = 0
    in_code = False

    def flush(end_line: int) -> None:
        if not block_lines:
            return
        body = "\n".join(block_lines).strip()
        if not body:
            block_lines.clear()
            return
        title = current_h3 or current_h2 or "(unsectioned)"
        blocks.append(ClaimBlock(
            section_title=title,
            text=body,
            line_start=block_start,
        ))
        block_lines.clear()

    has_h3_in_file = any(line.startswith("### ") for line in lines)

    for idx, line in enumerate(lines):
        stripped = line.rstrip()
        # Track code fences — skip claim parsing inside them but keep them in
        # the current block as-is (they often contain useful examples).
        if stripped.startswith("```"):
            in_code = not in_code
            block_lines.append(line)
            continue
        if in_code:
            block_lines.append(line)
            continue
        if stripped.startswith("## "):
            flush(idx)
            current_h2 = stripped[3:].strip()
            current_h3 = ""
            block_start = idx + 1
            continue
        if stripped.startswith("### "):
            flush(idx)
            current_h3 = stripped[4:].strip()
            block_start = idx + 1
            continue
        # No-h3 fallback: split on blank line under an h2
        if not has_h3_in_file and current_h2 and not stripped:
            if block_lines:
                flush(idx)
                block_start = idx + 1
            continue
        # Drop pure HR
        if stripped == "---":
            continue
        block_lines.append(line)

    flush(len(lines))
    return blocks


# ============================================================================
# Pre-filter
# ============================================================================


def pre_filter_block(block: ClaimBlock) -> tuple[bool, str]:
    """Return (keep, reason). reason is empty when kept, else why-dropped."""
    body = block.text.strip()
    if not body:
        return False, "empty"
    # Drop reference-only blocks (just `## Felhasznált források` followed by
    # URLs / bullets)
    title_lower = block.section_title.lower()
    if any(k in title_lower for k in (
        "felhasznált forrás", "források", "references", "kapcsolódó",
        "related", "tartalomjegyzék", "table of contents",
        "következő action-item", "next action",
    )):
        return False, "reference-section"
    # Drop blocks that are only headings or URL lines
    non_blank_lines = [ln for ln in body.splitlines() if ln.strip()]
    if not non_blank_lines:
        return False, "no-content"
    url_lines = sum(1 for ln in non_blank_lines if RE_URL_ONLY.match(ln))
    if url_lines == len(non_blank_lines):
        return False, "url-only"
    # Drop anchor-only (≤1 short line that just references elsewhere)
    if len(non_blank_lines) <= 2 and any(
        RE_ANCHOR_ONLY.search(ln) for ln in non_blank_lines
    ):
        return False, "anchor-only"
    # Drop blocks that are ONLY questions
    question_lines = sum(1 for ln in non_blank_lines if RE_QUESTION_BLOCK.match(ln))
    if question_lines and question_lines == len(non_blank_lines):
        return False, "question-only"
    # Require at least one declarative verb somewhere
    if not RE_HAS_VERB_SENTENCE.search(body):
        return False, "no-declarative-verb"
    # Very-short blocks (< 80 chars total) likely have no extractable claims
    if len(body) < 80:
        return False, "too-short"
    return True, ""


# ============================================================================
# Subagent-fanout: 2-phase pending pattern
# ============================================================================


def file_hash(path: Path) -> str:
    return hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:12]


def batch_dir(fhash: str) -> Path:
    return PENDING_DIR / fhash


def request_path(fhash: str, batch_id: int) -> Path:
    return batch_dir(fhash) / f"batch-{batch_id:02d}.request.json"


def response_path(fhash: str, batch_id: int) -> Path:
    return batch_dir(fhash) / f"batch-{batch_id:02d}.response.json"


def write_pending_batches(
    file_path: Path,
    provenance: str,
    blocks: list[ClaimBlock],
) -> list[Path]:
    """Phase 1: write per-batch request.json files for subagent fanout.

    Idempotent — skips batches whose request.json already exists OR whose
    response.json is already present (means the batch has been processed).
    """
    fhash = file_hash(file_path)
    batch_dir(fhash).mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for batch_id, start in enumerate(range(0, len(blocks), BATCH_SIZE), start=1):
        if batch_id > MAX_BATCHES_PER_FILE:
            break
        req = request_path(fhash, batch_id)
        resp = response_path(fhash, batch_id)
        if resp.exists() or req.exists():
            continue
        chunk = blocks[start:start + BATCH_SIZE]
        claim_blocks_text = "\n\n---\n\n".join(
            f"### Section: {b.section_title}\n\n{b.text}" for b in chunk
        )
        # Pick the first section title for the prompt context (most blocks in
        # a batch share a section).
        section_title = chunk[0].section_title if chunk else "(unsectioned)"
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            section_title=section_title,
            provenance=provenance,
            claim_blocks=claim_blocks_text,
        )
        payload = {
            "file_path": str(file_path),
            "provenance": provenance,
            "batch_id": batch_id,
            "batch_size": len(chunk),
            "block_section_titles": [b.section_title for b in chunk],
            "extraction_prompt": prompt,
            "vocab": PREDICATE_VOCAB,
            "vocab_version": "2026-05-17-v2-38pred",
            "source_type": "notebooklm",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        atomic_write_json(req, payload)
        written.append(req)
    return written


def collect_pending_responses(file_path: Path) -> list[dict]:
    """Phase 2: collect response.json files and return concatenated triplets.

    Each response.json is expected to be a JSON array of triplet dicts:
      [{"subject": ..., "predicate": ..., "object": ..., "confidence": 0.x}, ...]
    """
    fhash = file_hash(file_path)
    bdir = batch_dir(fhash)
    if not bdir.exists():
        return []
    triplets: list[dict] = []
    for resp in sorted(bdir.glob("batch-*.response.json")):
        try:
            data = json.loads(resp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and "triplets" in data:
            # Tolerate {"triplets":[...]} wrapper
            data = data["triplets"]
        if not isinstance(data, list):
            continue
        for t in data:
            if not isinstance(t, dict):
                continue
            t.setdefault("_response_path", str(resp))
            triplets.append(t)
    return triplets


# ============================================================================
# Validation
# ============================================================================


def is_forbidden_subject(subject: str) -> bool:
    if not subject:
        return False
    s = subject.strip()
    return any(s.startswith(p) for p in FORBIDDEN_SUBJECT_PREFIXES)


def contains_pii(value: str) -> bool:
    if not value:
        return False
    for pat in PII_PATTERNS:
        if pat.search(value):
            return True
    return False


def validate_triplet(t: dict) -> tuple[bool, str]:
    """Return (ok, reason)."""
    subj = (t.get("subject") or "").strip()
    pred = (t.get("predicate") or "").strip()
    obj = (t.get("object") or "").strip()
    if not (subj and pred and obj):
        return False, "missing-field"
    if is_forbidden_subject(subj):
        return False, "forbidden-subject"
    if pred not in VALID_PREDICATES:
        return False, "invalid-predicate"
    if contains_pii(obj) or contains_pii(subj):
        return False, "pii"
    # Reasonable length guards
    if len(subj) > 200 or len(obj) > 500:
        return False, "too-long"
    return True, ""


def fact_hash(subject: str, predicate: str, object_: str) -> str:
    payload = f"{subject}|{predicate}|{object_}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ============================================================================
# KO-DB I/O
# ============================================================================


def ko_connect() -> sqlite3.Connection:
    if not KO_DB.exists():
        raise FileNotFoundError(
            f"KO-DB not found at {KO_DB}. "
            f"Run vault-ko-ingest first to initialize."
        )
    return sqlite3.connect(KO_DB)


def existing_hashes(conn: sqlite3.Connection,
                    hashes: Iterable[str]) -> set[str]:
    hashes = list(hashes)
    if not hashes:
        return set()
    qmarks = ",".join("?" * len(hashes))
    rows = conn.execute(
        f"SELECT hash FROM facts WHERE hash IN ({qmarks})",
        hashes,
    ).fetchall()
    return {r[0] for r in rows}


def upsert_fact(conn: sqlite3.Connection, fact: dict) -> str:
    """Return one of: 'new', 'updated'.

    Post-#34 schema (2026-05-19): `facts.provenance` column dropped;
    provenance lives in side-table `fact_provenance`. Schema-detect to
    handle both legacy + post-#34 (canonical pattern mirroring
    vault-ko-ingest.upsert_fact:333-365).
    """
    h = fact_hash(fact["subject"], fact["predicate"], fact["object"])
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("PRAGMA table_info(facts)")
    cols = {row[1] for row in cur.fetchall()}
    has_pv = bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fact_provenance'"
    ).fetchone())
    post34 = "provenance" not in cols and has_pv

    if post34:
        try:
            conn.execute(
                """INSERT INTO facts (hash, subject, predicate, object,
                                      confidence, source_type, created_at, updated_at,
                                      provenance_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (h, fact["subject"], fact["predicate"], fact["object"],
                 fact.get("confidence", 0.8), "notebooklm", now, now),
            )
            status = "new"
        except sqlite3.IntegrityError:
            conn.execute(
                "UPDATE facts SET updated_at = ?, "
                "    confidence = COALESCE(?, confidence) "
                "WHERE hash = ?",
                (now, fact.get("confidence"), h),
            )
            status = "updated"
        # Add provenance row (idempotent via PK (fact_hash, provenance))
        conn.execute(
            """INSERT OR IGNORE INTO fact_provenance
                  (fact_hash, provenance, source_type, confidence, ingested_at)
               VALUES (?, ?, ?, ?, ?)""",
            (h, fact["provenance"], "notebooklm",
             fact.get("confidence", 0.8), now),
        )
        # Refresh provenance_count
        conn.execute(
            "UPDATE facts SET provenance_count = "
            "(SELECT COUNT(*) FROM fact_provenance WHERE fact_hash = ?) "
            "WHERE hash = ?",
            (h, h),
        )
        return status

    # Legacy pre-#34 schema (back-compat)
    try:
        conn.execute(
            """INSERT INTO facts (hash, subject, predicate, object, provenance,
                                  confidence, source_type, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (h, fact["subject"], fact["predicate"], fact["object"],
             fact["provenance"], fact.get("confidence", 0.8),
             "notebooklm", now, now),
        )
        return "new"
    except sqlite3.IntegrityError:
        conn.execute(
            "UPDATE facts SET updated_at = ?, "
            "    confidence = COALESCE(?, confidence) "
            "WHERE hash = ?",
            (now, fact.get("confidence"), h),
        )
        return "updated"


# ============================================================================
# Per-file pipeline
# ============================================================================


def process_file(
    file_path: Path,
    *,
    dry_run: bool,
    apply_env_ok: bool,
    skip_existing: bool,
    conn: sqlite3.Connection | None,
) -> FileReport:
    try:
        provenance = str(file_path.relative_to(VAULT_ROOT))
    except ValueError:
        provenance = str(file_path)

    report = FileReport(path=file_path, provenance=provenance)

    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        report.error = f"read-error: {exc}"
        return report

    blocks = parse_claim_blocks(text)
    report.parsed_blocks = len(blocks)

    kept_blocks: list[ClaimBlock] = []
    for b in blocks:
        keep, _reason = pre_filter_block(b)
        if keep:
            kept_blocks.append(b)
    report.filtered_blocks = len(kept_blocks)

    # Phase 1: write pending request files (idempotent)
    pending_writes = write_pending_batches(file_path, provenance, kept_blocks)
    report.batches_written = len(pending_writes)
    report.pending_request_paths = [str(p) for p in pending_writes]

    # Phase 2: collect any responses already produced
    triplets = collect_pending_responses(file_path)
    report.triplets_collected = len(triplets)
    if triplets:
        fhash = file_hash(file_path)
        bdir = batch_dir(fhash)
        report.pending_response_paths = [
            str(p) for p in sorted(bdir.glob("batch-*.response.json"))
        ]

    # Validate
    valid: list[dict] = []
    for t in triplets:
        ok, reason = validate_triplet(t)
        if not ok:
            if reason == "forbidden-subject":
                report.skipped_forbidden += 1
            elif reason == "pii":
                report.skipped_pii += 1
            elif reason == "invalid-predicate":
                report.skipped_invalid_predicate += 1
            continue
        valid.append({
            "subject": t["subject"].strip(),
            "predicate": t["predicate"].strip(),
            "object": t["object"].strip(),
            "confidence": float(t.get("confidence", 0.8)),
            "provenance": provenance,
        })
    report.triplets_after_validation = len(valid)
    report.triplets_after_pii = len(valid)
    report.triplets_after_forbidden = len(valid)

    if not valid:
        return report

    # Dedupe via fact_hash + skip-existing
    hashes_to_check = [
        fact_hash(v["subject"], v["predicate"], v["object"]) for v in valid
    ]
    existing: set[str] = set()
    if conn is not None and skip_existing:
        existing = existing_hashes(conn, hashes_to_check)
    final: list[tuple[str, dict]] = []
    seen_in_batch: set[str] = set()
    for v, h in zip(valid, hashes_to_check):
        if h in seen_in_batch:
            continue
        seen_in_batch.add(h)
        if skip_existing and h in existing:
            report.skipped_existing += 1
            continue
        final.append((h, v))

    # Apply or dry-run
    if dry_run or conn is None or not apply_env_ok:
        # Estimate "would-be" new vs updated using existing-set
        report.new_facts = sum(1 for h, _ in final if h not in existing)
        report.updated_facts = sum(1 for h, _ in final if h in existing)
        return report

    for _h, v in final:
        result = upsert_fact(conn, v)
        if result == "new":
            report.new_facts += 1
        else:
            report.updated_facts += 1
    conn.commit()
    return report


# ============================================================================
# Audit log
# ============================================================================


def log_audit(report: FileReport, *, mode: str) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "provenance": report.provenance,
        "parsed_blocks": report.parsed_blocks,
        "filtered_blocks": report.filtered_blocks,
        "batches_written": report.batches_written,
        "triplets_collected": report.triplets_collected,
        "triplets_after_validation": report.triplets_after_validation,
        "new_facts": report.new_facts,
        "updated_facts": report.updated_facts,
        "skipped_existing": report.skipped_existing,
        "skipped_invalid_predicate": report.skipped_invalid_predicate,
        "skipped_pii": report.skipped_pii,
        "skipped_forbidden": report.skipped_forbidden,
        "error": report.error,
    }
    try:
        atomic_append_jsonl(AUDIT_LOG, event)
    except OSError:
        pass


# ============================================================================
# Output rendering
# ============================================================================


def render_markdown(reports: list[FileReport], *, mode: str,
                    scan_dirs: list[Path], days: int) -> str:
    lines = []
    lines.append("# vault-nb-ingest dry-run" if mode == "dry-run"
                 else "# vault-nb-ingest apply-report")
    lines.append("")
    scanned_paths = ", ".join(
        str(d.relative_to(VAULT_ROOT)) if d.is_relative_to(VAULT_ROOT) else str(d)
        for d in scan_dirs
    )
    lines.append(f"Scanned: {scanned_paths}")
    lines.append(f"Window: last {days} days")
    lines.append(f"Reports detected: {len(reports)}")
    lines.append("")

    if not reports:
        lines.append("No NotebookLM reports found in window.")
        return "\n".join(lines) + "\n"

    for r in reports:
        lines.append(f"## {r.provenance}")
        lines.append("")
        if r.error:
            lines.append(f"- ERROR: {r.error}")
            lines.append("")
            continue
        lines.append(f"- Parsed claim blocks: {r.parsed_blocks}")
        lines.append(f"- After pre-filter: {r.filtered_blocks}")
        lines.append(f"- Pending batches written (phase 1): "
                     f"{r.batches_written}")
        if r.batches_written:
            lines.append(f"  (batch dir: /tmp/vault-nb-ingest-pending/"
                         f"{file_hash(r.path)}/)")
        lines.append(f"- Phase-2 triplets collected: {r.triplets_collected}")
        if r.triplets_collected:
            lines.append(f"- Validated triplets: {r.triplets_after_validation}")
            if r.skipped_forbidden:
                lines.append(f"  - Skipped (forbidden subject): "
                             f"{r.skipped_forbidden}")
            if r.skipped_pii:
                lines.append(f"  - Skipped (PII): {r.skipped_pii}")
            if r.skipped_invalid_predicate:
                lines.append(f"  - Skipped (invalid predicate): "
                             f"{r.skipped_invalid_predicate}")
            if r.skipped_existing:
                lines.append(f"  - Skipped (already in KO-DB): "
                             f"{r.skipped_existing}")
            lines.append(f"- {'Would-write' if mode == 'dry-run' else 'Wrote'} "
                         f"new facts: {r.new_facts}")
            if r.updated_facts:
                lines.append(f"- Updated facts: {r.updated_facts}")
        else:
            # No triplets yet — estimate yield
            est_low = max(0, r.filtered_blocks * 2)
            est_high = max(0, r.filtered_blocks * 3)
            lines.append(f"- Would-extract estimate: "
                         f"~{est_low}-{est_high} triplets "
                         f"(2-3 per filtered block)")
            lines.append(f"- Next: run subagent fanout on "
                         f"`/tmp/vault-nb-ingest-pending/{file_hash(r.path)}/`"
                         f" then re-run this script to harvest")
        lines.append("")

    # Aggregate
    total_parsed = sum(r.parsed_blocks for r in reports)
    total_filtered = sum(r.filtered_blocks for r in reports)
    total_collected = sum(r.triplets_collected for r in reports)
    total_new = sum(r.new_facts for r in reports)
    total_updated = sum(r.updated_facts for r in reports)
    total_skipped_existing = sum(r.skipped_existing for r in reports)
    est_low = sum(max(0, r.filtered_blocks * 2) for r in reports
                  if r.triplets_collected == 0)
    est_high = sum(max(0, r.filtered_blocks * 3) for r in reports
                   if r.triplets_collected == 0)

    lines.append("## Aggregate")
    lines.append("")
    lines.append(f"- Total claim blocks: {total_parsed}")
    lines.append(f"- Total filtered (kept): {total_filtered}")
    if total_collected:
        lines.append(f"- Total triplets collected: {total_collected}")
        lines.append(f"- {'Would-write' if mode == 'dry-run' else 'Wrote'} "
                     f"net new facts: {total_new}")
        lines.append(f"- Updated facts: {total_updated}")
        lines.append(f"- Skipped (existing): {total_skipped_existing}")
    if est_low or est_high:
        lines.append(f"- Net-new estimate (pending fanout): "
                     f"~{est_low}-{est_high} triplets")

    lines.append("")
    if mode == "dry-run":
        lines.append("(Run with --apply + VAULT_NB_INGEST_APPLY=1 to actually "
                     "write to KO-DB.)")
    return "\n".join(lines) + "\n"


# ============================================================================
# CLI
# ============================================================================


CRON_SUGGESTION = """\
Recommended cron (daily 05:00, between net-watch and morning sync):

    0 5 * * * VAULT_NB_INGEST_APPLY=1 /usr/local/bin/vault-cron-flock \\
        vault-nb-ingest /usr/local/bin/vault-nb-ingest --apply \\
        --days 1 --skip-existing >/dev/null 2>&1

DO NOT install automatically — verify dry-run yield first.
"""


class _HelpEpilogFormatter(argparse.RawDescriptionHelpFormatter):
    pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="vault-nb-ingest",
        description="Ingest NotebookLM deep-research reports into KO-DB.",
        epilog=CRON_SUGGESTION,
        formatter_class=_HelpEpilogFormatter,
    )
    ap.add_argument("--file", help="Single NotebookLM report path "
                                   "(absolute or vault-relative)")
    ap.add_argument("--scan-dir", action="append", default=[],
                    help="Directory to scan (repeatable). "
                         "Default: 10-raw/external/notebooklm/ + 10-raw/ + "
                         "06-Audits/")
    ap.add_argument("--days", type=int, default=7,
                    help="mtime window in days (default 7)")
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="Preview only — never writes to KO-DB (default)")
    ap.add_argument("--apply", action="store_true", default=False,
                    help="Actually insert facts (requires "
                         "VAULT_NB_INGEST_APPLY=1 env var)")
    ap.add_argument("--skip-existing", action="store_true", default=False,
                    help="Skip triplets whose hash is already in KO-DB")
    ap.add_argument("--json", action="store_true", default=False,
                    help="Emit JSON report instead of markdown")
    return ap.parse_args(argv)


def resolve_file_arg(arg: str) -> Path:
    p = Path(arg)
    if p.is_absolute() and p.exists():
        return p
    candidate = VAULT_ROOT / arg
    if candidate.exists():
        return candidate
    if p.exists():
        return p.resolve()
    raise FileNotFoundError(arg)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    mode = "apply" if args.apply else "dry-run"

    # Two-layer gate
    apply_env = os.environ.get("VAULT_NB_INGEST_APPLY") == "1"
    if args.apply and not apply_env:
        print("ERROR: --apply requires VAULT_NB_INGEST_APPLY=1 env var "
              "(second-layer safety gate). Falling back to dry-run.",
              file=sys.stderr)
        args.apply = False
        mode = "dry-run"
    apply_ok = args.apply and apply_env

    # Discover files
    if args.file:
        try:
            path = resolve_file_arg(args.file)
        except FileNotFoundError:
            print(f"ERROR: file not found: {args.file}", file=sys.stderr)
            return 2
        files = [path]
        scan_dirs = [path.parent]
    else:
        scan_dirs = ([Path(d) for d in args.scan_dir]
                     if args.scan_dir else list(DEFAULT_SCAN_DIRS))
        files = discover_files(scan_dirs, args.days)

    # KO-DB connection only when actually applying or skip-existing
    conn: sqlite3.Connection | None = None
    if apply_ok or args.skip_existing:
        try:
            conn = ko_connect()
        except FileNotFoundError as exc:
            print(f"WARN: {exc}", file=sys.stderr)
            conn = None

    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    reports: list[FileReport] = []
    for f in files:
        r = process_file(
            f,
            dry_run=not apply_ok,
            apply_env_ok=apply_ok,
            skip_existing=args.skip_existing,
            conn=conn,
        )
        reports.append(r)
        log_audit(r, mode=mode)

    if conn is not None:
        conn.close()

    # Render
    if args.json:
        payload = {
            "mode": mode,
            "scan_dirs": [str(d) for d in scan_dirs],
            "days": args.days,
            "files_found": len(reports),
            "reports": [
                {
                    "provenance": r.provenance,
                    "parsed_blocks": r.parsed_blocks,
                    "filtered_blocks": r.filtered_blocks,
                    "batches_written": r.batches_written,
                    "triplets_collected": r.triplets_collected,
                    "triplets_after_validation": r.triplets_after_validation,
                    "new_facts": r.new_facts,
                    "updated_facts": r.updated_facts,
                    "skipped_existing": r.skipped_existing,
                    "skipped_pii": r.skipped_pii,
                    "skipped_forbidden": r.skipped_forbidden,
                    "skipped_invalid_predicate": r.skipped_invalid_predicate,
                    "pending_request_paths": r.pending_request_paths,
                    "pending_response_paths": r.pending_response_paths,
                    "error": r.error,
                }
                for r in reports
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(reports, mode=mode,
                              scan_dirs=scan_dirs, days=args.days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
