#!/usr/bin/env bash
# devcontainer post-create — runs once after the codespace/dev-container builds.
# Goal: get a "vault-search works" smoke-test green inside the container in
# under 5 minutes, with zero manual steps from the user.

set -euo pipefail

WORKSPACE="${PWD}"
echo "▶ post-create starting in ${WORKSPACE}"

# ── 1. Python deps ────────────────────────────────────────────────────────
if [ -f requirements.txt ]; then
  echo "▶ installing Python deps from requirements.txt"
  pip install --user --no-cache-dir -r requirements.txt
else
  echo "▶ no requirements.txt yet; installing minimal dev deps"
  pip install --user --no-cache-dir pytest pyyaml ruff mkdocs-material
fi

# ── 2. Start Memgraph CE in Docker (port 7687) ────────────────────────────
if ! docker ps --format '{{.Names}}' | grep -q '^memgraph$'; then
  echo "▶ starting Memgraph CE container on :7687"
  docker run -d --name memgraph -p 7687:7687 memgraph/memgraph:latest >/dev/null || \
    echo "  ⚠ Memgraph start failed — features that need the graph won't work, but the wiki content is still readable"
else
  echo "▶ Memgraph already running"
fi

# ── 3. Friendly hint banner ───────────────────────────────────────────────
cat <<'BANNER'

────────────────────────────────────────────────────────────────────
🎉 MyForge Vault 11.11 devcontainer is ready.

What to try first:

  make help                         # list all targets
  make build-docs                   # mkdocs build --strict (no-network test)
  make docs                         # mkdocs serve → http://localhost:8000
  pytest .vault-eval/regression/ -m fast   # retrieval-quality gate

To use the agent CLIs (Claude Code / Codex / Gemini) you'll need to
authenticate them per their docs. They are NOT auto-installed in the
devcontainer because each has its own auth flow.

Read the FAQ → 11-wiki/faq.en.md
Read the architecture → 11-wiki/architecture-overview.en.md
────────────────────────────────────────────────────────────────────
BANNER
