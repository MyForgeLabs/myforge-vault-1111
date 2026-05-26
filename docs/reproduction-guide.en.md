# Reproduction Guide — Superintelligent Vault in your own environment

> 5 steps. Expected time: **30-60 minutes**.
> Goal: turn your own Obsidian-vault into a **self-improving knowledge-system** following the SV 8-axis architecture.

## Prerequisites

- Linux server or WSL2 (Ubuntu 22.04+ tested)
- 8 GB RAM (for bge-m3 model warm-load)
- 10 GB free disk (Memgraph + model cache)
- Docker + Docker Compose
- Python 3.10+
- Git, Bash
- (Optional) Claude Code CLI / Codex CLI / Gemini CLI

## Step 1 — Vault skeleton clone + personalization

```bash
# 1.a. Clone the public SV repo
git clone --depth=1 https://github.com/<owner>/superintelligent-vault.git ~/sv-public

# 1.b. Initialize your own vault (separate folder)
mkdir -p ~/obsidian-vault
cd ~/obsidian-vault
git init

# 1.c. Copy the generic content (00-Meta + 11-wiki + 07-Decisions + AGENTS.md)
cp ~/sv-public/AGENTS.md ./
cp -r ~/sv-public/00-Meta ./
cp -r ~/sv-public/11-wiki ./
cp -r ~/sv-public/07-Decisions ./
mkdir -p 01-Daily 02-Projects 03-Hosts 04-Tasks 05-Memory 06-Audits 08-Sessions 10-raw 10-raw/external

# 1.d. Copy Memory templates + personalize
cp ~/sv-public/.vault-skeletons/05-Memory/*.template.md 05-Memory/
mv 05-Memory/User.template.md 05-Memory/User.md
mv 05-Memory/Infrastructure.template.md 05-Memory/Infrastructure.md
# → edit both, fill in the {{ placeholders }}

# 1.e. Demo content (optional — can be removed if you start with your own projects)
cp ~/sv-public/examples/projects/* 02-Projects/
cp ~/sv-public/examples/sessions/* 08-Sessions/
```

## Step 2 — Memgraph + Python venv

```bash
# 2.a. Memgraph CE Docker
docker run -d --name vault-memgraph \
  -p 7687:7687 -p 7444:7444 \
  -v vault-memgraph-data:/var/lib/memgraph \
  memgraph/memgraph:latest

# 2.b. Python venv + dependencies
python3 -m venv ~/.notebooklm-venv
source ~/.notebooklm-venv/bin/activate
pip install \
  sentence-transformers \
  transformers \
  mgclient pymgclient \
  rank-bm25 \
  pyyaml \
  llama-index-core \
  llama-index-embeddings-huggingface \
  llama-index-graph-stores-memgraph

# 2.c. bge-m3 model download (~2.3 GB, cached)
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

## Step 3 — Symlinking the scripts

```bash
# 3.a. Vault-tooling scripts from the public folder
sudo cp ~/sv-public/scripts/11.11/* /usr/local/bin/
sudo cp ~/sv-public/scripts/vault-* /usr/local/bin/
sudo chmod +x /usr/local/bin/11.11* /usr/local/bin/vault-*

# 3.b. Sprint skeletons into the vault
cp -r ~/sv-public/.vault-ko ~/obsidian-vault/
cp -r ~/sv-public/.vault-memory ~/obsidian-vault/
cp -r ~/sv-public/.vault-eval ~/obsidian-vault/
cp -r ~/sv-public/.vault-tools ~/obsidian-vault/
cp -r ~/sv-public/.vault-nb ~/obsidian-vault/
cp -r ~/sv-public/.vault-agents ~/obsidian-vault/
cp -r ~/sv-public/.vault-rsi ~/obsidian-vault/
cp -r ~/sv-public/.vault-graph ~/obsidian-vault/

# 3.c. Vault-config init
mkdir -p ~/.vault-config
echo "0.95" > ~/.vault-config/crystallize-threshold.txt
cp ~/sv-public/scripts/crystallize-threshold.yaml ~/.vault-config/
```

## Step 4 — Initial embed + smoke test

```bash
# 4.a. Embed the 11-wiki and 07-Decisions content
cd ~/obsidian-vault
vault-embed --backfill 11-wiki/
vault-embed --backfill 07-Decisions/

# 4.b. Search smoke test
vault-search "skeleton first sprint pattern"

# 4.c. Embed SKILL.md files (if any exist under ~/.claude/skills/)
vault-skill-search --backfill

# 4.d. 11.11 session start smoke test
11.11start "first-session-smoke"
echo "Hello Superintelligent Vault" > /tmp/first-note.txt
11.11note "First note from $(date)"
11.11stop
```

## Step 5 — Cron + monitoring (optional, recommended)

```bash
# 5.a. Vault crons
(crontab -l 2>/dev/null; cat <<'EOF'
*/10 * * * * /usr/local/bin/vault-autosave >/dev/null 2>&1
0 4 * * 0 /usr/local/bin/vault-cleanup --write >/dev/null 2>&1
0 6 * * 0 /usr/local/bin/vault-github-trending-recurrence --days 30 >/dev/null 2>&1
0 8 * * * /usr/local/bin/github-trending-report --since daily >/dev/null 2>&1
30 4 * * 0 /usr/local/bin/vault-ko-conflicts-audit >/dev/null 2>&1
35 4 * * 0 /usr/local/bin/vault-crystallize-monitor --json > ~/obsidian-vault/06-Audits/crystallize-health.json 2>&1
EOF
) | crontab -

# 5.b. (Optional) systemd vault-search-server warm daemon
sudo cp ~/sv-public/scripts/systemd/vault-search.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vault-search.service

# 5.c. (Optional) GitHub mirror remote
cd ~/obsidian-vault
git remote add origin git@github.com:<yourself>/vault-private.git
git add . && git commit -m "Initial vault"
git push -u origin main
```

## Verification

```bash
# Health check (all at once)
11.11   # vault health-check (symlinks, services, Memgraph)

# Expected output:
# OK Memgraph: container running, port 7687
# OK vault-search.service: active
# OK Symlinks: 11.11* all under /usr/local/bin/
# OK Crons: 6 entries
# OK Wiki: 87+ docs embedded
```

## What you get

- **Personal Obsidian-vault** organized in the Karpathy LLM-Wiki pattern
- **8-axis** evolutionary architecture with production scripts
- **Memgraph native vector-search** with ~10-50 ms latency
- **Subagent-fanout pattern** for bulk LLM-tasks at $0 cost (Claude Code subscription)
- **G-Eval + NLI + Coherence cascade** automatic quality control at session close
- **GitHub-trending weekly monitoring** with automatic cherry-pick suggestion
- **NotebookLM cross-project synthesis** if you have a NotebookLM account

## Backout

Any axis can be turned off via an ENV flag (see `~/.vault-config/env-defaults.md`). The vault remains fully functional on its own (at the classic Obsidian level).

## Who else has done it

> _If you successfully reproduced it, send a PR with a 2-sentence feedback to: `docs/reproductions.md`._

## Troubleshooting

- **Memgraph connection refused** → `docker logs vault-memgraph`, check port 7687 reachability, restart container
- **bge-m3 OOM** → smaller model: `intfloat/multilingual-e5-base` (~470 MB, drop-in replacement)
- **Claude Code subagent-fanout doesn't work** → check the subscription status + `claude --version`

## Related

- [README HU](../README.hu.md) · [README EN](../README.en.md)
- [8-axis architecture roadmap](../07-Decisions/2026-05-12%20Superintelligent%20vault%20evolution%20roadmap.md)
- [Karpathy LLM-Wiki pattern](wiki/Karpathy-LLM-Wiki-pattern.md) — starting pattern
