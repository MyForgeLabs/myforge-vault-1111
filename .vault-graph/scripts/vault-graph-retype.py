#!/root/.notebooklm-venv/bin/python3
"""
vault-graph-retype — typed-entity pass over flat :Entity nodes (SV B-7 Week 2-4).

Strategy
--------
The Week 1-α loader (``vault-graph-extract``) produced ~8975 generic
``:Entity {name: ...}`` nodes (subjects + cross-referenced objects). This
script applies a rule-based classifier to each entity name and adds a
secondary type-label so we can run typed queries like::

    MATCH (p:Project)-[:DEPENDS_ON]->(s:Server) RETURN p, s
    MATCH (e:Skill)-[]->() RETURN e LIMIT 20

Week 2 labels:
    :Project    — vault project (slug match against 02-Projects/*.md)
    :Person     — known people: Peti, Domi, Karpathy, …
    :Server     — host / VPS / external service (memgraph, postgres, hostinger…)
    :Skill      — agent skills / 11.11* / vault-* / bmad-* / wds-* / gds-* …
    :SourceFile — file paths (extension match or path-like w/ ext)

Week 3 additions:
    :Concept    — evergreen knowledge entities (GEPA, subagent-fanout,
                  crystallization, MEMORY.md, BMAD, …) — glossary-driven
    :Decision   — ADR-style nodes (``ADR …``, ``sv-N … arch.md``, etc.)
    :Sprint     — SV sprints (``B-1``, ``B-2 Week 3``, ``sv-bN-…``)
    :Alias      — short forms / abbreviations (``Domi``, ``KGC``…) connected
                  via ``[:ALIAS_OF]`` to the canonical entity. The canonical
                  is auto-created (with its typed label) if missing.

Week 4 additions:
    --phase llm-extract — LLM-aided extraction (cost-aware stand-in classifier).
        Reads the remaining ~7659 Generic :Entity nodes, splits them into
        8 batches of ~200, and (where Task-tool subagent-fanout is available)
        dispatches batch-LLM classification using a 2-phase pending pattern
        compatible with vault-ko-ingest. The default mode is a *stand-in*
        rule+context classifier (extended heuristics) which is conservative
        and ~$0 cost. Heuristics target:
            - "X wiki" / "Y workflow" / "Z pattern" → :Concept
            - "session YYYY-MM-DD-..." → :Sprint (session reference)
            - "Phase N", "Tier N", "Week N" → :Sprint (sprint-stage marker)
            - "X.md" / "X.py" extension → :SourceFile
            - "wp-...", "vault-...", "bmad-..." → :Skill
            - "X.eu", "X.hu", "kgc-postgres" etc. → :Server
            - "X bug", "Y quirk", "Z footgun" → :Concept (learning-pattern)
        Idempotent (SET label is no-op for already-typed nodes), batched
        commit at BATCH_SIZE intervals, audit-log per batch.

Memgraph CE 3.9.0 constraints
-----------------------------
- No DDL inside multicommand transactions — we use the existing
  ``:Entity(name)`` index (created via autocommit in Week 1-α) and
  ``session.run`` style application-MERGE on the secondary label.
- Adding a label is a normal write — works inside batched explicit
  transactions. We commit every BATCH_SIZE entities.
- Idempotent: re-running the script doesn't double-label nodes;
  ``SET n:Foo`` is a no-op when ``n`` already has ``:Foo``.

Usage
-----
    vault-graph-retype --dry-run
        Classify only; print distribution; no writes.

    vault-graph-retype
        Equivalent to ``--phase both``.

    vault-graph-retype --phase concept-decision-sprint
        Apply only the rule-based label pass (Week 2 + Week 3 labels).

    vault-graph-retype --phase alias
        Apply only the alias-extraction pass (creates :Alias nodes + canonicals).

    vault-graph-retype --phase llm-extract --dry-run
        Week 4 LLM-aided extraction pass (stand-in classifier by default).
        Reads Generic :Entity nodes only, splits into 8 batches, classifies
        each batch using the extended-rule stand-in, writes batch-level
        audit-log to graph-retype-llm-YYYYMMDD.jsonl.

    vault-graph-retype --phase llm-extract
        Apply the LLM-aided extraction labels.

    vault-graph-retype --phase llm-extract --emit-pending /tmp/b7-llm-classify-pending/
        Phase 1 of the 2-phase pending pattern: write 8 batch JSON files
        with entity-name lists + 8-class taxonomy prompt. A parent agent
        (Task-tool subagent-fanout) can then process each pending batch.

    vault-graph-retype --phase llm-extract --consume-pending /tmp/b7-llm-classify-pending/
        Phase 2: read the .response.json files produced by the subagents and
        apply the labels.

    vault-graph-retype --reset
        Remove all typed secondary labels first.

    vault-graph-retype --audit /path/audit.jsonl
        Append per-run audit events (dry-run counts, apply counts) to a JSONL
        file. Default: /root/obsidian-vault/06-Audits/graph-retype-YYYYMMDD.jsonl
        (or graph-retype-llm-YYYYMMDD.jsonl for llm-extract phase).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import mgclient
import yaml
from tqdm import tqdm

# ─── CONFIG ───────────────────────────────────────────────────────────────

MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
BATCH_SIZE = 500

PROJECTS_DIR = Path("/root/obsidian-vault/02-Projects")
HOSTS_DIR = Path("/root/obsidian-vault/03-Hosts")
DECISIONS_DIR = Path("/root/obsidian-vault/07-Decisions")
SKILLS_DIR = Path("/root/.agents/skills")
ALIAS_YAML = Path("/root/.vault-config/entity-aliases.yaml")
AUDIT_DIR = Path("/root/obsidian-vault/06-Audits")

# Week 2 + Week 3 secondary labels we apply via the rule classifier
TYPE_LABELS = (
    "Project", "Person", "Server", "Skill", "SourceFile",
    "Concept", "Decision", "Sprint",
)


# ─── KNOWN LIST DISCOVERY ─────────────────────────────────────────────────

def _load_project_slugs() -> set[str]:
    """Slugs from 02-Projects/*.md (skip Index and backup files)."""
    slugs: set[str] = set()
    if not PROJECTS_DIR.exists():
        return slugs
    for p in PROJECTS_DIR.glob("*.md"):
        if p.name == "Index.md":
            continue
        if ".bak" in p.name:
            continue
        slugs.add(p.stem.lower())
    # Manual augmentation — slugs the agents speak of every day
    slugs.update({
        "kgc-berles", "kgc-erp", "kgc-tv-cms", "kgc-marketing",
        "kgc-kivetitok", "kgshop-bluebird", "koko", "mapesz",
        "mfl-bot", "mfl-voice", "myforge-dashboard",
        "petanque-kisgeparuhaz", "robbantott-kereso", "rojtesbojt",
        "foxxi", "foxxi-cv-website", "foxxi-email-arhivum",
        "foxxi-sprint-2026-05", "boulium", "superintelligent-vault",
        "teszt-eu", "kinda", "balance",
    })
    return slugs


def _load_host_names() -> set[str]:
    """Hostnames + extras from 03-Hosts/ and Infrastructure."""
    names: set[str] = set()
    if HOSTS_DIR.exists():
        for p in HOSTS_DIR.glob("*.md"):
            if p.name == "Index.md":
                continue
            names.add(p.stem.lower())
            if " - " in p.stem:
                names.add(p.stem.split(" - ", 1)[0].lower())
    names.update({
        "vps-prod-example", "vps-dev-example",
        "hostinger", "vault-memgraph",
        "shared hosting (cloud professional)",
    })
    return names


def _load_skill_names() -> set[str]:
    names: set[str] = set()
    if SKILLS_DIR.exists():
        for d in SKILLS_DIR.iterdir():
            if d.is_dir():
                names.add(d.name.lower())
    return names


def _load_decision_titles() -> set[str]:
    """Titles of files in 07-Decisions/, lower-cased, used for exact match."""
    titles: set[str] = set()
    if not DECISIONS_DIR.exists():
        return titles
    for p in DECISIONS_DIR.glob("*.md"):
        if p.name == "Index.md":
            continue
        titles.add(p.stem.lower())
    return titles


PROJECT_SLUGS = _load_project_slugs()
HOST_NAMES = _load_host_names()
SKILL_NAMES = _load_skill_names()
DECISION_TITLES = _load_decision_titles()

# Hand-curated people roster (vault is single-tenant; list is small)
PEOPLE = {
    "peti", "domi", "rob", "karpathy", "yann lecun", "andrej karpathy",
    "samus shepard", "sally", "freya", "saga", "john", "dr. quinn",
    "domonkos petis", "markovics gyula", "gyuszi", "rob markovics",
    "user@example.com",
}

# Known server / infra entities
KNOWN_SERVERS = {
    "memgraph", "postgres", "postgresql", "sqlite", "redis", "mysql",
    "mariadb", "hostinger", "litespeed", "caddy", "nginx", "traefik",
    "apache", "docker", "vault-memgraph", "neo4j", "pinecone",
    "cloudflare", "vps", "noble vps", "ubuntu vps",
}

# Curated evergreen-Concept allow-list — names we explicitly want labeled
# as :Concept. Lower-cased keys.
KNOWN_CONCEPTS = {
    # Patterns / playbooks
    "karpathy llm wiki pattern", "karpathy llm-wiki pattern",
    "karpathy llm-wiki minta", "karpathy-llm-wiki", "karpathy llm wiki",
    "karpathy minimum stack", "karpathy index pattern", "karpathy compilation",
    "karpathy rag pattern", "karpathy memory stack",
    "subagent-fanout", "subagent fanout", "subagent-fanout playbook",
    "claude code subagent-fanout playbook",
    "crystallization", "crystallization protocol", "crystallization-protocol",
    "knowledge crystallization", "crystallization workflow",
    "auto-crystallization audit log",
    "gepa", "gepa evaluation framework", "g-eval", "g-eval foundation",
    "g-eval bias-mitigated v0.3", "nli layer 2.5", "bias mitigation",
    "self-enhancement bias",
    "memory.md", "memory.md overflow", "memory.md overflow management",
    "memory.md truncation", "memory.md partial-load",
    "memory.md per-line limit", "memory.md compression",
    "memgpt", "memgpt-style virtual context-load",
    "johnny-decimal", "johnny-decimal-prefix",
    "para", "para-like",
    "rag", "retrieval-augmented generation",
    "bmad", "business method-architecture-development",
    "prd", "product requirements document",
    "adr", "architecture decision record",
    "nfr", "non-functional requirement",
    "moc", "map of content",
    "ko-db", "knowledge object database",
    "ko-db top-k", "ko-db structured facts",
    "two-phase pending pattern", "2-phase pending pattern",
    "auto-disable min-volume guard", "multi-layer safety-gate",
    "skeleton-first playbook", "sprint day 0 skeleton-first",
    "pwa", "progressive web app",
    "rsi", "recursive self-improvement",
}

# Decision title-prefix patterns (case-insensitive).
DECISION_PREFIX_RE = re.compile(
    r"^(adr[\s\-]|adr$|adr-\d+|adr\s+\d{4}|"
    r"sv-\d+\s+.*\s+arch$|"
    r"\d{4}-\d{2}-\d{2}\s+sv-\d+.*\s+arch$|"
    r"\d{4}-\d{2}-\d{2}\s.*arch\.md$)",
    re.IGNORECASE,
)
# Looser: anything containing "ADR" as a standalone token at start
ADR_LEAD_RE = re.compile(r"^adr(?:[\s\-]|$)", re.IGNORECASE)

# Sprint patterns. SV uses B-1..B-9 (B-7 entity-graph stream, etc.) plus
# week markers ("B-1 Week 3"), plus the sv-bN-* slug-form, plus sv-1..sv-8
# (the 8 SV-tracks).
SPRINT_RE = re.compile(
    r"^("
    r"B-\d{1,2}"               # B-1, B-12
    r"(\s*\+\s*B-\d{1,2})?"    # B-1 + B-5
    r"(\s+Week\s+\d+([-–]\d+)?)?"  # B-1 Week 3 or B-1 Week 3-4
    r"|sv-b\d{1,2}(-[\w\-]+)?" # sv-b2-memory-architecture
    r"|sv-\d{1,2}(-[\w\-]+)?"  # sv-1-… / sv-01-…
    r"|sv-phase-b\d{1,2}.*"    # git-tag-like
    r")$",
    re.IGNORECASE,
)
# Slightly looser: starts with B-N or SV-N followed by space + more text
# (we want 'SV-3 NotebookLM' → :Sprint as a sprint-track reference)
SPRINT_LOOSE_RE = re.compile(r"^(B-\d{1,2}|SV-\d{1,2}|sv-b\d{1,2})(\s+|$)", re.IGNORECASE)

# File extensions → SourceFile
FILE_EXT_RE = re.compile(
    r"\.(md|py|sh|js|ts|tsx|jsx|json|yml|yaml|html|css|sql|conf|toml|cypher|cjs|mjs|env|cfg|ini|xml|csv|tsv|jsonl|txt|db|sqlite|sqlite3|pdf|pptx|xlsx|docx|zip|tar|gz|log|lock|map|svg|png|jpg|jpeg|webp|gif|ico|woff|woff2|ttf)$",
    re.IGNORECASE,
)
PATH_LIKE_RE = re.compile(r"^[~\.\/]?/?[\w\-.]+(?:/[\w\-.]+)+$")

# Server / host signals
PORT_RE = re.compile(r":\d{2,5}\b")
DOMAIN_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]*\.(?:hu|com|eu|net|org|io|dev|ai|app)$", re.IGNORECASE)
HOST_PATTERN_RE = re.compile(r"^(srv\d+.*|.*vps[\s\-_].*)$", re.IGNORECASE)

# Concept suffix heuristic — these suffixes signal evergreen playbooks
CONCEPT_SUFFIX_RE = re.compile(
    r"\b(pattern|playbook|protocol|workflow|doctrine|heuristic|antipattern|"
    r"anti-pattern|gotcha|gotchas|recipe|convention|minta|módszer|modszer)$",
    re.IGNORECASE,
)

# Skill signals
SKILL_PREFIX_RE = re.compile(
    r"^(11\.11[\w\-]*|vault-[\w\-]+|bmad-[\w\-]+|wds-[\w\-]+|gds-[\w\-]+|wp-[\w\-]+|azure-[\w\-]+|mcp-[\w\-]+|notebooklm)$",
    re.IGNORECASE,
)


# ─── CLASSIFIER ───────────────────────────────────────────────────────────

def classify(name: str) -> str | None:
    """Return one of TYPE_LABELS or None for 'no secondary label'.

    Rule order matters — earlier rules win. Specific (concept allow-list,
    sprint pattern) before generic (path/skill/server) before weak heuristics.
    """
    if not name:
        return None
    n = name.strip()
    nl = n.lower()

    # 1) Decision — strict (these must NOT be misclassified as SourceFile
    #    because many ADR titles end with ".md")
    if nl in DECISION_TITLES:
        return "Decision"
    if ADR_LEAD_RE.match(nl):
        return "Decision"
    if DECISION_PREFIX_RE.match(nl):
        return "Decision"

    # 2) Sprint — strict match only (B-1, B-1 Week 3, sv-bN-…, sv-1-…).
    #    The loose-match ("B-1 something") is deferred below SourceFile +
    #    Skill + Concept to avoid swallowing "B-3 eval-l1-parser.py".
    if SPRINT_RE.match(nl):
        return "Sprint"

    # 3) Concept — curated evergreen allow-list (exact, case-insensitive)
    #    + suffix heuristic ("…pattern" / "…playbook" / "…workflow" / "…protocol"
    #    / "…doctrine" / "…heuristic" / "…gotcha" / etc.). Single-word forms
    #    ("pattern", "workflow") are skipped — too generic.
    if nl in KNOWN_CONCEPTS:
        return "Concept"
    if CONCEPT_SUFFIX_RE.search(nl) and len(nl.split()) >= 2 and len(nl.split()) <= 8:
        return "Concept"

    # 4) SourceFile — file-extension or unmistakable path
    if FILE_EXT_RE.search(nl):
        return "SourceFile"
    if "/" in n and PATH_LIKE_RE.match(n.strip()) and " " not in n:
        return "SourceFile"

    # 5) Skill — installed-skill match OR single-token namespace prefix
    if nl in SKILL_NAMES:
        return "Skill"
    if "/skills/" in nl or "/.agents/skills" in nl:
        return "Skill"
    if SKILL_PREFIX_RE.match(nl):
        return "Skill"
    first = nl.split()[0] if nl.split() else ""
    if SKILL_PREFIX_RE.match(first) and len(nl.split()) <= 4:
        return "Skill"

    # 6) Project — slug match (exact or as first token of a short phrase)
    if nl in PROJECT_SLUGS:
        return "Project"
    if first in PROJECT_SLUGS and len(nl.split()) <= 4:
        return "Project"

    # 7) Server — known infra entities + hostname / domain / port style
    if nl in HOST_NAMES or nl in KNOWN_SERVERS:
        return "Server"
    if " " not in nl:
        if DOMAIN_RE.match(nl):
            return "Server"
        if HOST_PATTERN_RE.match(nl):
            return "Server"
        if PORT_RE.search(nl) and "/" not in nl:
            return "Server"

    # 8) Person — strict allow-list
    if nl in PEOPLE:
        return "Person"

    # 9) Sprint — loose fallback (B-1 + short qualifier). Only fires if
    #    nothing else matched, so 'B-3 eval-l1-parser.py' → :SourceFile (rule 4),
    #    'B-1 + B-5' → :Sprint (rule 2 strict), 'B-1 Pass-only baseline' → here.
    if SPRINT_LOOSE_RE.match(nl) and len(nl.split()) <= 6:
        return "Sprint"

    return None


# ─── WEEK 4 STAND-IN LLM CLASSIFIER ───────────────────────────────────────
#
# Conservative regex+context-rule classifier that acts as a $0-cost stand-in
# for the LLM-aided extraction pass. Conservative means: if uncertain, return
# None (leave the entity Generic). Target false-positive rate <5%.
#
# Order matters: more specific rules first. Most rules require multi-token
# context to avoid generic single-word false positives like "Deploy" or
# "Bug".

_LLM_WIKI_SUFFIX_RE = re.compile(r"\b(wiki|md)$", re.IGNORECASE)
_LLM_CONCEPT_SUFFIX_RE = re.compile(
    r"\b(pattern|playbook|protocol|workflow|doctrine|antipattern|anti-pattern|"
    r"recipe|convention|gotcha|gotchas|footgun|smell|trap|quirk|quirks|"
    r"approach|heuristic|strategy|method|tactic|principle|theorem|law|"
    r"compose|encoding|decoding|fallback|guard|gate|cascade|stack|loop|"
    r"backoff|throttle|debounce|caching|cache-busting|migration|onboarding|"
    r"deployment|rollout|rollback|escalation|handshake|invariant|contract|"
    r"taxonomy|schema|model|recipe|module|integration|bootstrap)s?\b",
    re.IGNORECASE,
)
_LLM_LEARNING_SUFFIX_RE = re.compile(
    r"\b(bug|bugfix|fix|crash|trap|footgun|gotcha|quirk|edge[-\s]?case|"
    r"caveat|antipattern|anti-pattern|workaround|hack|fallback|fail|"
    r"failure|misuse|pitfall|smell|leak)\b",
    re.IGNORECASE,
)
_LLM_SESSION_REF_RE = re.compile(
    r"^session\s+\d{4}-\d{2}-\d{2}[\w\-]*$", re.IGNORECASE,
)
_LLM_SPRINT_STAGE_RE = re.compile(
    r"^(phase|tier|week|sprint|stage|milestone|wave)\s+([0-9ivx]+|[a-z]\b|[0-9]+[-–][0-9]+)",
    re.IGNORECASE,
)
_LLM_SPRINT_TRACK_RE = re.compile(
    r"\b(sv-?\d+|sv-?b\d+|b-\d+\s+week|b-\d+\s+phase)\b", re.IGNORECASE,
)
_LLM_SOURCEFILE_DIR_RE = re.compile(
    r"^\d{2}-[A-Z][a-zA-Z]+(/[\w\-.]+)?$"
)
_LLM_SOURCEFILE_EXT_RE = re.compile(
    r"\.(md|py|sh|js|ts|tsx|jsx|json|yml|yaml|conf|toml|sql|cypher|env|cfg|"
    r"ini|xml|csv|tsv|jsonl|txt|db|log|lock|html|css|cjs|mjs|patch|diff)$",
    re.IGNORECASE,
)
_LLM_SOURCEFILE_PATH_RE = re.compile(r"^[\w\-.]+/[\w\-./]+$")
_LLM_SKILL_PREFIX_RE = re.compile(
    r"^(wp-|wpml-|vault-|vault_|bmad-|wds-|gds-|cis-|tea-|azure-|aws-|gcp-|"
    r"mcp-|11\.11|nano-banana|notebooklm|firefly|figma-|gemini-|claude-code|"
    r"genericagent|gepa-|11-wiki|01-daily|02-projects)",
    re.IGNORECASE,
)
_LLM_SERVER_DOMAIN_RE = re.compile(
    r"^[a-z0-9][a-z0-9.\-]+\.(?:hu|com|eu|net|org|io|dev|ai|app|me|us|sh|co|"
    r"xyz|cloud|host|tools|page|site|build|run|fyi|wtf|local)$",
    re.IGNORECASE,
)
_LLM_SERVER_KEYWORD_RE = re.compile(
    r"\b(postgres|postgresql|mariadb|mysql|sqlite|redis|memgraph|neo4j|"
    r"weaviate|qdrant|pinecone|elasticsearch|opensearch|"
    r"hostinger|cloudflare|aws|gcp|azure|digitalocean|linode|vercel|netlify|"
    r"caddy|nginx|apache|traefik|litespeed|haproxy|"
    r"docker|kubernetes|k8s|podman|compose)\b",
    re.IGNORECASE,
)
_LLM_SERVER_ENV_RE = re.compile(
    r"\b(staging|production|prod|sandbox|preview|preprod|dev-env|test-env)\b",
    re.IGNORECASE,
)
_LLM_TECH_PROPER_NOUN = {
    # Frameworks & libs (typically appear as standalone entities)
    "react", "next.js", "nextjs", "vue", "svelte", "astro", "remix", "nuxt",
    "node.js", "nodejs", "deno", "bun", "express", "fastify", "hono",
    "prisma", "drizzle", "knex", "typeorm", "sequelize",
    "playwright", "puppeteer", "cypress", "vitest", "jest", "mocha",
    "tailwind", "tailwindcss", "shadcn", "radix", "headless ui",
    "openai", "anthropic", "gemini", "claude", "gpt-4", "gpt-5", "gpt-4o",
    "llama", "mistral", "qwen", "deepseek", "phi",
    "huggingface", "transformers", "langchain", "llamaindex", "haystack",
    "pgvector", "lancedb", "chroma", "milvus", "vespa", "elasticsearch",
    "supabase", "firebase", "auth0", "clerk", "stripe", "paddle", "lemon squeezy",
    "wordpress", "elementor", "bricks", "gutenberg", "woocommerce", "shopify",
    "wpml", "polylang", "yoast", "rankmath", "advanced custom fields", "acf",
    "obsidian", "notion", "logseq", "anki", "readwise",
    "bge-m3", "bge", "all-minilm", "instructor", "openai-embedding",
    "jepa", "hrm", "moe", "mixture-of-experts", "rope", "flash-attention",
    "rag", "ragatouille", "colbert", "splade", "rerank", "reranker",
    "memgpt", "letta", "autogen", "crewai", "swarm",
    "gepa", "dspy", "ell", "guidance", "instructor-llm",
    "g-eval", "ragas", "deepeval", "promptfoo",
    "json canvas", "mermaid", "graphviz", "d3", "echarts", "plotly",
}
_LLM_TECH_KEYWORD_PHRASES = {
    # Multi-word tech phrases worth labeling as Concept
    "claude code", "claude code skill", "claude code subagent",
    "claude code session", "claude code harness", "claude code hooks",
    "subagent fanout", "subagent-fanout",
    "system prompt", "tool calling", "tool use", "function calling",
    "prompt caching", "context window", "context loading",
    "embedding model", "vector index", "vector search", "vector database",
    "knowledge graph", "knowledge object", "knowledge base",
    "retrieval augmented", "retrieval-augmented",
    "self-enhancement bias", "bias mitigation",
    "auto-distillation", "compaction", "context-load",
    "live snapshot", "auto-save", "auto-disable",
    "smoke test", "smoke-test", "smoketest",
    "feature flag", "feature-flag",
    "shadow mode", "shadow-mode", "dry run", "dry-run",
    "happy path", "happy-path",
    "edge case", "edge-case",
    "race condition", "race-condition",
    "dead letter", "dead-letter",
    "service worker", "service-worker",
}

# Single-token learning anchors — only fire if the entity is multi-token AND
# this anchor appears as suffix or in the middle, not standalone.
_LLM_LEARNING_ANCHORS = {
    "bug", "bugfix", "fix", "crash", "trap", "footgun", "gotcha", "quirk",
    "caveat", "antipattern", "workaround", "hack", "pitfall", "smell", "leak",
    "regression", "deadlock", "livelock",
}


def stand_in_classify(name: str) -> tuple[str | None, str | None]:
    """Conservative LLM-stand-in classifier for Week 4.

    Returns (label, rule_id) so the audit log can record provenance.
    Returns (None, None) when no confident rule fires.
    """
    if not name:
        return None, None
    n = name.strip()
    if not n:
        return None, None
    nl = n.lower()
    toks = nl.split()
    ntoks = len(toks)

    # Forbidden: skip vault-internal scaffolding patterns
    if nl.startswith("agents.md") or nl == "agents.md":
        return None, "skip-forbidden"
    if nl.startswith("00-meta") or nl.startswith("11.11"):
        # 11.11 namespace skills handled below by SKILL_PREFIX_RE; only skip
        # raw "11.11" or "00-Meta" exact-form references
        if nl in {"00-meta", "00-meta/", "11.11", "11.11*"}:
            return None, "skip-forbidden"

    # 1) Tech proper-noun exact (Concept)
    if nl in _LLM_TECH_PROPER_NOUN:
        return "Concept", "tech-proper-noun"
    for phrase in _LLM_TECH_KEYWORD_PHRASES:
        if nl == phrase:
            return "Concept", "tech-keyword-phrase"

    # 2) SourceFile — strict (extension or X-Y directory prefix or path-like)
    if _LLM_SOURCEFILE_EXT_RE.search(nl):
        return "SourceFile", "ext-suffix"
    if _LLM_SOURCEFILE_DIR_RE.match(n):
        return "SourceFile", "vault-dir-ref"
    if "/" in n and _LLM_SOURCEFILE_PATH_RE.match(n) and " " not in n:
        return "SourceFile", "path-like"

    # 3) Session-reference → Sprint
    if _LLM_SESSION_REF_RE.match(nl):
        return "Sprint", "session-ref"

    # 4) Sprint stage marker (Phase 4 / Week 3 / Sprint 1 / Tier 2)
    if _LLM_SPRINT_STAGE_RE.match(nl) and ntoks <= 4:
        return "Sprint", "sprint-stage"

    # 5) Sprint track ref (SV-3, B-7 Week …)
    if _LLM_SPRINT_TRACK_RE.search(nl) and ntoks <= 6:
        return "Sprint", "sprint-track"

    # 6) Skill prefix
    if _LLM_SKILL_PREFIX_RE.match(nl):
        return "Skill", "skill-prefix"
    first = toks[0] if toks else ""
    if _LLM_SKILL_PREFIX_RE.match(first) and ntoks <= 3:
        return "Skill", "skill-first-token"

    # 7) Server: domain or known-infra keyword in single-word names
    if ntoks == 1 and _LLM_SERVER_DOMAIN_RE.match(nl):
        return "Server", "domain"
    # Multi-word infra phrase like "self-hosted Memgraph", "kgc-postgres prod"
    if _LLM_SERVER_KEYWORD_RE.search(nl) and ntoks <= 5:
        # Reject "X hyphenated", "X quirk", "X bug" — these are learnings
        # about an infra tool, not the tool itself. Route those to Concept.
        if any(t in {"hyphenated", "naming", "quirk", "bug", "fix", "gotcha",
                     "trap", "footgun", "compose-issue"} for t in toks):
            return "Concept", "infra-learning"
        # Reject action-phrases like "Docker container start", "Memgraph deploy"
        if any(t in {"start", "stop", "restart", "deploy", "deployment",
                     "install", "uninstall", "remove", "delete", "create",
                     "build", "run", "boot", "shutdown", "reboot"} for t in toks):
            return None, None
        return "Server", "infra-keyword"
    if _LLM_SERVER_ENV_RE.search(nl) and ntoks >= 2 and ntoks <= 4:
        # Phrases like "violet-okapi staging" → only fire when there's a
        # project-like prefix AND the env-token sits at the END of the phrase.
        # Reject action-bare-noun phrases like "production cron hookup",
        # "successful production systems", "production-deploy multi-process".
        if any(t in {"cron", "hookup", "branch", "diff", "step", "task",
                     "checkpoint", "snapshot", "log", "issue", "ticket",
                     "widget", "service", "services", "system", "systems",
                     "multi-process", "process", "deploy", "deployment",
                     "rollout"}
               for t in toks):
            return None, None
        # Adjective forms ("successful", "fast", "great") → reject
        if any(t in {"successful", "broken", "great", "fast", "slow", "tiny",
                     "huge", "popular", "common"} for t in toks):
            return None, None
        # Require env-marker AT END (last token) — "violet-okapi staging" OK,
        # "production-deploy multi-process" not OK. Drop "preview" — too generic
        # (LinkedIn share preview etc.).
        env_markers = {"staging", "production", "prod", "sandbox", "preprod", "dev-env", "test-env"}
        if toks[-1] not in env_markers:
            return None, None
        if any(("-" in t and len(t) >= 4) or len(t) >= 6 for t in toks if t not in env_markers):
            return "Server", "env-suffix"

    # 8) Concept — "X wiki" / "X .md" type wiki-references
    if ntoks >= 2 and ntoks <= 5 and _LLM_WIKI_SUFFIX_RE.search(nl):
        last_tok = toks[-1]
        if last_tok in {"wiki"}:
            return "Concept", "wiki-suffix"

    # 9) Concept — pattern/playbook/workflow/etc. suffix (multi-token only)
    if 2 <= ntoks <= 7 and _LLM_CONCEPT_SUFFIX_RE.search(nl):
        return "Concept", "concept-suffix"

    # 10) Concept — learning-anchor suffix (bug/quirk/footgun/…)
    #     Only fire if anchor is the LAST token AND there are 2-5 tokens
    #     (single-word "Bug" should remain Generic).
    if 2 <= ntoks <= 5 and toks[-1] in _LLM_LEARNING_ANCHORS:
        return "Concept", "learning-suffix"

    # 11) Concept — embedded "claude code …" / "next.js …" / "wp …" prefix
    #     with a technical follow-up (rule of thumb: short multi-word phrase).
    if 2 <= ntoks <= 5:
        if toks[0] in {"claude-code", "claude", "next.js", "nextjs", "wp", "wpml",
                       "obsidian", "memgraph", "git", "github", "docker", "prisma",
                       "gepa", "bmad", "shopify", "yoast", "elementor", "bricks",
                       "hostinger", "nano-banana", "notebooklm", "vault"} \
           and not _LLM_LEARNING_SUFFIX_RE.search(nl):
            # Reject if it contains an action verb that signals one-off action
            action_words = {"deploy", "deployment", "restart", "start", "stop",
                            "create", "delete", "remove", "install", "uninstall",
                            "compile", "build", "test", "run", "fetch", "import",
                            "export", "download", "upload", "click", "press",
                            "implementation", "step", "task", "contact"}
            if any(t in action_words for t in toks):
                return None, None
            # Reject ordinal/step-marker phrases ("Vault implementation step 6")
            if any(t.isdigit() for t in toks) and any(t in {"step", "stage", "iter", "iteration"} for t in toks):
                return None, None
            return "Concept", "tech-namespaced-phrase"

    return None, None


# ─── MEMGRAPH I/O ─────────────────────────────────────────────────────────

def connect_mg():
    return mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)


def fetch_entity_names(conn) -> list[str]:
    cur = conn.cursor()
    cur.execute("MATCH (e:Entity) RETURN e.name AS name;")
    return [r[0] for r in cur.fetchall() if r and r[0] is not None]


def fetch_generic_entity_names(conn) -> list[str]:
    """Return :Entity nodes WITHOUT any of the Week 2-3 typed secondary labels.

    Excludes :Alias too (alias nodes are typed separately).
    """
    cur = conn.cursor()
    cur.execute(
        "MATCH (e:Entity) "
        "WHERE NOT (e:Concept OR e:Decision OR e:Sprint OR e:Project "
        "OR e:Skill OR e:SourceFile OR e:Server OR e:Person OR e:Alias) "
        "RETURN e.name AS name;"
    )
    return [r[0] for r in cur.fetchall() if r and r[0] is not None]


def reset_typed_labels(conn) -> None:
    """Remove any previous typed secondary labels. Idempotent."""
    cur = conn.cursor()
    for label in TYPE_LABELS:
        cur.execute(f"MATCH (e:Entity:`{label}`) REMOVE e:`{label}`;")
    conn.commit()


def count_label(conn, label: str) -> int:
    cur = conn.cursor()
    cur.execute(f"MATCH (n:`{label}`) RETURN count(n);")
    return cur.fetchall()[0][0]


def apply_labels(conn, plan: list[tuple[str, str]]) -> None:
    """plan: list of (entity_name, type_label) — applies secondary label."""
    cur = conn.cursor()
    pbar = tqdm(total=len(plan), desc="retype", unit="ent")
    for i, (name, label) in enumerate(plan, 1):
        # SET e:Foo is idempotent (no-op if already labeled)
        cur.execute(
            f"MATCH (e:Entity {{name: $n}}) SET e:`{label}`;",
            {"n": name},
        )
        if i % BATCH_SIZE == 0:
            conn.commit()
        pbar.update(1)
    conn.commit()
    pbar.close()


# ─── ALIAS PHASE ──────────────────────────────────────────────────────────

def load_alias_config(path: Path = ALIAS_YAML) -> list[dict]:
    if not path.exists():
        print(f"[alias] config not found: {path}", file=sys.stderr)
        return []
    with path.open() as f:
        doc = yaml.safe_load(f) or {}
    items = doc.get("aliases", []) or []
    valid: list[dict] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        if not it.get("alias") or not it.get("canonical"):
            continue
        valid.append({
            "alias": str(it["alias"]),
            "canonical": str(it["canonical"]),
            "type": str(it.get("type", "")).strip() or None,
            "notes": str(it.get("notes", "")).strip() or None,
        })
    return valid


def apply_aliases(conn, items: list[dict], dry_run: bool) -> dict:
    """Create :Alias nodes + canonicals + [:ALIAS_OF] edges.

    Idempotent: MERGE is used everywhere; SET only writes immutable-ish props.
    Returns a stats dict for the audit log.
    """
    cur = conn.cursor()

    created_alias = 0
    created_canonical = 0
    created_edges = 0
    skipped_invalid_type = 0
    valid_types = {"Person", "Project", "Concept", "Server"}

    pbar = tqdm(total=len(items), desc="alias", unit="al")
    for it in items:
        alias_name = it["alias"]
        canon_name = it["canonical"]
        canon_type = it["type"]

        if canon_type not in valid_types:
            skipped_invalid_type += 1
            pbar.update(1)
            continue

        if dry_run:
            # Dry-run: count what would be created. Crude approximation:
            cur.execute(
                "MATCH (a:Alias {name: $n}) RETURN count(a);",
                {"n": alias_name},
            )
            if cur.fetchall()[0][0] == 0:
                created_alias += 1
            cur.execute(
                "MATCH (c:Entity {name: $n}) RETURN count(c);",
                {"n": canon_name},
            )
            if cur.fetchall()[0][0] == 0:
                created_canonical += 1
            cur.execute(
                "MATCH (a:Alias {name: $a})-[r:ALIAS_OF]->(c {name: $c}) RETURN count(r);",
                {"a": alias_name, "c": canon_name},
            )
            if cur.fetchall()[0][0] == 0:
                created_edges += 1
            pbar.update(1)
            continue

        # 1) MERGE the canonical :Entity (typed-labeled). If it already
        #    exists as :Entity we just SET the extra label (idempotent).
        cur.execute(
            "MERGE (c:Entity {name: $n}) RETURN c;",
            {"n": canon_name},
        )
        cur.execute(
            f"MATCH (c:Entity {{name: $n}}) SET c:`{canon_type}`;",
            {"n": canon_name},
        )

        # 2) MERGE the :Alias node (also typed as :Entity so it shows up
        #    in vault-graph-query results that filter by :Entity).
        cur.execute(
            "MERGE (a:Alias {name: $n}) "
            "ON CREATE SET a.aliasOf = $c, a.notes = $notes "
            "ON MATCH  SET a.aliasOf = $c, a.notes = $notes;",
            {"n": alias_name, "c": canon_name, "notes": it.get("notes") or ""},
        )

        # 3) Create the [:ALIAS_OF] edge. Memgraph: MERGE on relationship
        #    requires both endpoints already match — we just matched them.
        cur.execute(
            "MATCH (a:Alias {name: $a}), (c:Entity {name: $c}) "
            "MERGE (a)-[:ALIAS_OF]->(c);",
            {"a": alias_name, "c": canon_name},
        )

        pbar.update(1)

    if not dry_run:
        conn.commit()

        # Recount actuals for the audit
        cur.execute("MATCH (a:Alias) RETURN count(a);")
        total_alias = cur.fetchall()[0][0]
        cur.execute("MATCH ()-[r:ALIAS_OF]->() RETURN count(r);")
        total_edges = cur.fetchall()[0][0]
    else:
        total_alias = -1
        total_edges = -1

    pbar.close()
    return {
        "items_input": len(items),
        "skipped_invalid_type": skipped_invalid_type,
        "would_create_alias_nodes": created_alias if dry_run else None,
        "would_create_canonicals": created_canonical if dry_run else None,
        "would_create_edges": created_edges if dry_run else None,
        "total_alias_nodes_post": total_alias if not dry_run else None,
        "total_alias_edges_post": total_edges if not dry_run else None,
    }


# ─── AUDIT LOG ────────────────────────────────────────────────────────────

def default_audit_path() -> Path:
    return AUDIT_DIR / f"graph-retype-{dt.date.today():%Y%m%d}.jsonl"


def default_llm_audit_path() -> Path:
    return AUDIT_DIR / f"graph-retype-llm-{dt.date.today():%Y%m%d}.jsonl"


def write_audit(audit_path: Path, event: dict) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("ts", dt.datetime.now().isoformat(timespec="seconds"))
    with audit_path.open("a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ─── MAIN ─────────────────────────────────────────────────────────────────

def run_classifier_phase(conn, args, audit_path: Path) -> dict:
    """Apply :Project/:Person/:Server/:Skill/:SourceFile/:Concept/:Decision/:Sprint."""
    names = fetch_entity_names(conn)
    print(f"[stats] :Entity nodes fetched: {len(names):,}", file=sys.stderr)

    plan: list[tuple[str, str]] = []
    per_type_samples: dict[str, list[str]] = {l: [] for l in TYPE_LABELS}
    for n in names:
        t = classify(n)
        if t:
            plan.append((n, t))
            if len(per_type_samples[t]) < max(5, args.sample):
                per_type_samples[t].append(n)

    counts = Counter(t for _, t in plan)
    generic = len(names) - sum(counts.values())

    print("\n=== Type distribution ===")
    for t in TYPE_LABELS:
        print(f"  :{t:<11} {counts.get(t, 0):>6,}")
    print(f"  (Generic)    {generic:>6,}")
    print(f"  TOTAL        {len(names):>6,}")

    if args.sample:
        print("\n=== Samples per type ===")
        for t in TYPE_LABELS:
            print(f"\n--- :{t} ---")
            for s in per_type_samples[t][:args.sample]:
                print(f"  {s}")

    if args.dry_run:
        print("\n[dry-run] no Memgraph writes performed.")
        write_audit(audit_path, {
            "phase": "concept-decision-sprint",
            "mode": "dry-run",
            "total_entities": len(names),
            "would_apply": dict(counts),
            "would_remain_generic": generic,
        })
        return {"plan": plan, "counts": dict(counts), "generic": generic}

    if args.reset:
        print("[reset] removing existing typed labels…", file=sys.stderr)
        reset_typed_labels(conn)

    apply_labels(conn, plan)

    # Read-back
    print("\n=== Memgraph read-back ===")
    readback: dict[str, int] = {}
    for t in TYPE_LABELS:
        c = count_label(conn, t)
        readback[t] = c
        print(f"  :{t:<11} {c:>6,}")

    write_audit(audit_path, {
        "phase": "concept-decision-sprint",
        "mode": "apply",
        "total_entities": len(names),
        "applied": dict(counts),
        "readback": readback,
        "reset": bool(args.reset),
    })
    return {"plan": plan, "counts": dict(counts), "readback": readback}


def run_alias_phase(conn, args, audit_path: Path) -> dict:
    items = load_alias_config()
    print(f"[alias] loaded {len(items)} alias entries from {ALIAS_YAML}", file=sys.stderr)

    stats = apply_aliases(conn, items, dry_run=args.dry_run)
    print("\n=== Alias phase ===")
    for k, v in stats.items():
        if v is not None:
            print(f"  {k:<32} {v}")

    write_audit(audit_path, {
        "phase": "alias",
        "mode": "dry-run" if args.dry_run else "apply",
        "stats": stats,
    })
    return stats


def run_llm_extract_phase(conn, args, audit_path: Path) -> dict:
    """Week 4: LLM-aided extraction over the *remaining* Generic :Entity nodes.

    Pipeline:
      1) fetch Generic-only entity names
      2) split into N batches (default 8) for fanout-style parallelism
      3) for each batch, apply the stand-in classifier (default mode) OR
         emit a pending JSON file (--emit-pending) OR
         read pending response JSON files (--consume-pending)
      4) collect plan and write labels (unless dry-run)
      5) audit-log per-batch + total
    """
    names = fetch_generic_entity_names(conn)
    print(f"[llm-extract] Generic :Entity nodes: {len(names):,}", file=sys.stderr)
    if not names:
        print("[llm-extract] nothing to do.")
        return {"total": 0, "applied": {}}

    # Smoke-test gate
    if args.smoke_test:
        names = names[: args.smoke_test]
        print(f"[llm-extract] smoke-test: trimming to first {len(names)} entities", file=sys.stderr)

    n_batches = max(1, args.batches)
    chunk_size = (len(names) + n_batches - 1) // n_batches
    batches: list[list[str]] = [
        names[i : i + chunk_size] for i in range(0, len(names), chunk_size)
    ]
    print(f"[llm-extract] split into {len(batches)} batches of ~{chunk_size}", file=sys.stderr)

    # --- Phase 1 of 2-phase pending pattern: emit pending JSON files
    if args.emit_pending:
        pending_dir = Path(args.emit_pending)
        pending_dir.mkdir(parents=True, exist_ok=True)
        for bi, batch in enumerate(batches, 1):
            buid = f"b7-llm-batch-{dt.date.today():%Y%m%d}-{bi:02d}"
            req = {
                "batch_id": buid,
                "batch_index": bi,
                "batch_count": len(batches),
                "taxonomy": list(TYPE_LABELS) + ["Generic"],
                "rules": (
                    "Classify each entity name into exactly one label from the "
                    "taxonomy. Use Generic when the name is too ambiguous, "
                    "describes a transient action, or is a one-off reference. "
                    "Prefer Concept for evergreen knowledge patterns; Sprint "
                    "for session-references and B-N/SV-N markers; Skill for "
                    "agent-skill-namespace prefixes (wp-/vault-/bmad-/wds-/gds-); "
                    "SourceFile for file paths and X.md/X.py forms; Server for "
                    "domains, hostnames, and known infra keywords; Decision for "
                    "ADR-style titles; Project for vault projects; Person for "
                    "humans. False-positive rate target: <5%."
                ),
                "entities": batch,
                "expected_response_format": {
                    "labels": {"<entity_name>": "<label_or_Generic>"},
                    "skipped": ["<name>"],
                },
            }
            (pending_dir / f"{buid}.json").write_text(json.dumps(req, ensure_ascii=False, indent=2))
        print(f"[llm-extract] emitted {len(batches)} pending request(s) → {pending_dir}", file=sys.stderr)
        write_audit(audit_path, {
            "phase": "llm-extract",
            "mode": "emit-pending",
            "total_generic": len(names),
            "n_batches": len(batches),
            "pending_dir": str(pending_dir),
        })
        return {"emitted": len(batches), "total": len(names)}

    # --- Phase 2: consume pending responses written by subagents
    if args.consume_pending:
        pending_dir = Path(args.consume_pending)
        plan: list[tuple[str, str]] = []
        from collections import Counter as _C
        per_label = _C()
        consumed = 0
        for resp in sorted(pending_dir.glob("*.response.json")):
            try:
                doc = json.loads(resp.read_text())
            except Exception as e:
                print(f"[llm-extract] skip {resp.name}: {e}", file=sys.stderr)
                continue
            labels = doc.get("labels", {}) or {}
            for name, label in labels.items():
                if label not in TYPE_LABELS:
                    continue
                plan.append((name, label))
                per_label[label] += 1
            consumed += 1
        print(f"[llm-extract] consumed {consumed} response(s) → {len(plan)} label-ops", file=sys.stderr)
        if args.dry_run:
            print(f"[dry-run] {dict(per_label)}")
            write_audit(audit_path, {
                "phase": "llm-extract",
                "mode": "consume-pending-dry",
                "consumed_responses": consumed,
                "would_apply": dict(per_label),
            })
            return {"would_apply": dict(per_label)}
        apply_labels(conn, plan)
        readback = {l: count_label(conn, l) for l in TYPE_LABELS}
        write_audit(audit_path, {
            "phase": "llm-extract",
            "mode": "consume-pending-apply",
            "consumed_responses": consumed,
            "applied": dict(per_label),
            "readback": readback,
        })
        return {"applied": dict(per_label), "readback": readback}

    # --- Default mode: stand-in classifier (regex+context-rule)
    from collections import Counter as _C
    plan: list[tuple[str, str]] = []
    per_label = _C()
    per_rule = _C()
    samples_per_label: dict[str, list[str]] = {l: [] for l in TYPE_LABELS}
    batch_stats = []

    for bi, batch in enumerate(batches, 1):
        b_plan: list[tuple[str, str]] = []
        b_per_label = _C()
        for nm in batch:
            label, rule = stand_in_classify(nm)
            if label:
                b_plan.append((nm, label))
                b_per_label[label] += 1
                per_rule[rule or "?"] += 1
                if len(samples_per_label[label]) < 6:
                    samples_per_label[label].append(nm)
        batch_stats.append({
            "batch_index": bi,
            "batch_size": len(batch),
            "classified": len(b_plan),
            "per_label": dict(b_per_label),
        })
        per_label.update(b_per_label)
        plan.extend(b_plan)
        print(f"[batch {bi}/{len(batches)}] {len(batch)} entities → {len(b_plan)} typed "
              f"({dict(b_per_label)})", file=sys.stderr)

    print("\n=== Stand-in classifier summary ===")
    print(f"  total Generic input  : {len(names):,}")
    print(f"  classified           : {sum(per_label.values()):,}  "
          f"({100*sum(per_label.values())/max(1,len(names)):.1f}%)")
    print(f"  remaining Generic    : {len(names) - sum(per_label.values()):,}")
    print("\n  per-label distribution:")
    for l in TYPE_LABELS:
        c = per_label.get(l, 0)
        if c:
            print(f"    :{l:<11} {c:>5,}")
    print("\n  per-rule distribution:")
    for r, c in per_rule.most_common():
        print(f"    {r:<28} {c:>5,}")
    print("\n  samples (first 3 per label):")
    for l, ss in samples_per_label.items():
        if ss:
            print(f"    :{l}")
            for s in ss[:3]:
                print(f"      {s!r}")

    if args.dry_run:
        write_audit(audit_path, {
            "phase": "llm-extract",
            "mode": "dry-run",
            "classifier": "stand-in",
            "total_generic_input": len(names),
            "would_apply": dict(per_label),
            "per_rule": dict(per_rule),
            "n_batches": len(batches),
            "batch_stats": batch_stats,
        })
        print("\n[dry-run] no writes performed.")
        return {"plan": plan, "counts": dict(per_label)}

    # Apply
    apply_labels(conn, plan)
    readback = {l: count_label(conn, l) for l in TYPE_LABELS}
    print("\n=== Memgraph read-back (post-apply) ===")
    for l in TYPE_LABELS:
        print(f"  :{l:<11} {readback[l]:>6,}")

    # Final typed-ratio
    cur = conn.cursor()
    cur.execute("MATCH (e:Entity) RETURN count(e);")
    total_entities = cur.fetchall()[0][0]
    cur.execute(
        "MATCH (e:Entity) "
        "WHERE NOT (e:Concept OR e:Decision OR e:Sprint OR e:Project "
        "OR e:Skill OR e:SourceFile OR e:Server OR e:Person OR e:Alias) "
        "RETURN count(e);"
    )
    remaining_generic = cur.fetchall()[0][0]
    typed_ratio = 100.0 * (total_entities - remaining_generic) / max(1, total_entities)
    print(f"\n  typed-ratio post-apply: {typed_ratio:.2f}%  "
          f"({total_entities - remaining_generic} / {total_entities})")

    write_audit(audit_path, {
        "phase": "llm-extract",
        "mode": "apply",
        "classifier": "stand-in",
        "total_generic_input": len(names),
        "applied": dict(per_label),
        "per_rule": dict(per_rule),
        "n_batches": len(batches),
        "batch_stats": batch_stats,
        "readback": readback,
        "typed_ratio_pct": round(typed_ratio, 2),
        "remaining_generic": remaining_generic,
    })
    return {
        "applied": dict(per_label),
        "readback": readback,
        "typed_ratio_pct": typed_ratio,
        "remaining_generic": remaining_generic,
    }


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[1])
    ap.add_argument("--dry-run", action="store_true", help="classify only, no writes")
    ap.add_argument("--reset", action="store_true",
                    help="remove existing typed labels first (classifier phase only)")
    ap.add_argument("--sample", type=int, default=0,
                    help="print N samples per type after classification")
    ap.add_argument("--phase",
                    choices=["concept-decision-sprint", "alias", "both", "llm-extract"],
                    default="both",
                    help="which pass to run (default: both)")
    ap.add_argument("--audit", type=Path, default=None,
                    help="audit JSONL output path (default depends on phase)")
    ap.add_argument("--limit", type=int, default=0,
                    help="for alias phase: limit to first N entries (smoke-test)")
    ap.add_argument("--batches", type=int, default=8,
                    help="llm-extract: number of fanout batches (default 8)")
    ap.add_argument("--smoke-test", type=int, default=0,
                    help="llm-extract: only process first N Generic entities")
    ap.add_argument("--emit-pending", type=str, default=None,
                    help="llm-extract Phase 1: write batch request JSONs into this directory")
    ap.add_argument("--consume-pending", type=str, default=None,
                    help="llm-extract Phase 2: read .response.json files and apply labels")
    args = ap.parse_args()

    # Per-phase default audit path
    if args.audit:
        audit_path = args.audit
    elif args.phase == "llm-extract":
        audit_path = default_llm_audit_path()
    else:
        audit_path = default_audit_path()

    conn = connect_mg()
    try:
        if args.phase == "llm-extract":
            run_llm_extract_phase(conn, args, audit_path)
        else:
            if args.phase in ("concept-decision-sprint", "both"):
                run_classifier_phase(conn, args, audit_path)
            if args.phase in ("alias", "both"):
                # apply --limit only in alias phase, by trimming the YAML in-memory
                if args.limit > 0:
                    global load_alias_config
                    _orig = load_alias_config
                    def _limited(path: Path = ALIAS_YAML, _n=args.limit):
                        return _orig(path)[:_n]
                    load_alias_config = _limited  # type: ignore[assignment]
                run_alias_phase(conn, args, audit_path)
        print(f"\n[audit] events appended → {audit_path}", file=sys.stderr)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
