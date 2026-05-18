# Reproduction Guide — Superintelligent Vault saját környezetedben

> 5 lépés. Várt idő: **30-60 perc**.
> Cél: a saját Obsidian-vault-od **self-improving knowledge-system**-mé alakítása a SV 8-tengelyű architektúrája szerint.

## Előfeltétel

- Linux szerver vagy WSL2 (Ubuntu 22.04+ tesztelt)
- 8 GB RAM (bge-m3 model warm-betöltéshez)
- 10 GB szabad disk (Memgraph + model-cache)
- Docker + Docker Compose
- Python 3.10+
- Git, Bash
- (Opcionális) Claude Code CLI / Codex CLI / Gemini CLI

## Lépés 1 — Vault-szkeleton clone + személyre szabás

```bash
# 1.a. A public SV-repo clone
git clone --depth=1 https://github.com/<owner>/superintelligent-vault.git ~/sv-public

# 1.b. Saját vault inicializálás (külön mappa)
mkdir -p ~/obsidian-vault
cd ~/obsidian-vault
git init

# 1.c. Másold a generic-content-et (00-Meta + 11-wiki + 07-Decisions + AGENTS.md)
cp ~/sv-public/AGENTS.md ./
cp -r ~/sv-public/00-Meta ./
cp -r ~/sv-public/11-wiki ./
cp -r ~/sv-public/07-Decisions ./
mkdir -p 01-Daily 02-Projects 03-Hosts 04-Tasks 05-Memory 06-Audits 08-Sessions 10-raw 10-raw/external

# 1.d. Memory-template-eket másold + szabd személyre
cp ~/sv-public/.vault-skeletons/05-Memory/*.template.md 05-Memory/
mv 05-Memory/User.template.md 05-Memory/User.md
mv 05-Memory/Infrastructure.template.md 05-Memory/Infrastructure.md
# → editáld mindkettőt, töltsd ki a {{ placeholderek }}-et

# 1.e. Demo content (opcionális — eltávolítható ha a saját projekteddel kezdesz)
cp ~/sv-public/examples/projects/* 02-Projects/
cp ~/sv-public/examples/sessions/* 08-Sessions/
```

## Lépés 2 — Memgraph + Python venv

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

## Lépés 3 — Scriptek symlink-elése

```bash
# 3.a. Vault-tooling scripts publikus mappából
sudo cp ~/sv-public/scripts/11.11/* /usr/local/bin/
sudo cp ~/sv-public/scripts/vault-* /usr/local/bin/
sudo chmod +x /usr/local/bin/11.11* /usr/local/bin/vault-*

# 3.b. Sprint-skeleton-ok a vault-ba
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

## Lépés 4 — Initial embed + smoke

```bash
# 4.a. Embed a 11-wiki és 07-Decisions tartalmat
cd ~/obsidian-vault
vault-embed --backfill 11-wiki/
vault-embed --backfill 07-Decisions/

# 4.b. Search smoke
vault-search "skeleton first sprint pattern"

# 4.c. SKILL.md-k embed (ha vannak ~/.claude/skills/)
vault-skill-search --backfill

# 4.d. 11.11 session start smoke
11.11start "first-session-smoke"
echo "Hello Superintelligent Vault" > /tmp/first-note.txt
11.11note "First note from $(date)"
11.11stop
```

## Lépés 5 — Cron + monitoring (opcionális, ajánlott)

```bash
# 5.a. Vault-cron-ok
(crontab -l 2>/dev/null; cat <<'EOF'
*/10 * * * * /usr/local/bin/vault-autosave >/dev/null 2>&1
0 4 * * 0 /usr/local/bin/vault-cleanup --write >/dev/null 2>&1
0 6 * * 0 /usr/local/bin/vault-github-trending-recurrence --days 30 >/dev/null 2>&1
0 8 * * * /usr/local/bin/github-trending-report --since daily >/dev/null 2>&1
30 4 * * 0 /usr/local/bin/vault-ko-conflicts-audit >/dev/null 2>&1
35 4 * * 0 /usr/local/bin/vault-crystallize-monitor --json > ~/obsidian-vault/06-Audits/crystallize-health.json 2>&1
EOF
) | crontab -

# 5.b. (Opcionális) systemd vault-search-server warm-daemon
sudo cp ~/sv-public/scripts/systemd/vault-search.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vault-search.service

# 5.c. (Opcionális) GitHub-mirror remote
cd ~/obsidian-vault
git remote add origin git@github.com:<yourself>/vault-private.git
git add . && git commit -m "Initial vault"
git push -u origin main
```

## Verifikáció

```bash
# Health-check (egyszerre)
11.11   # vault health-check (symlinkek, services, Memgraph)

# Várt output:
# ✓ Memgraph: container running, port 7687
# ✓ vault-search.service: active
# ✓ Symlinkek: 11.11* mind /usr/local/bin/-ben
# ✓ Cron-ok: 6 entry
# ✓ Wiki: 87+ doc embed-elve
```

## Mit kapsz

- **Personal Obsidian-vault** Karpathy LLM-Wiki pattern-ben szervezve
- **8-tengelyű** evolúciós architektúra production-script-ekkel
- **Memgraph native vector-search** ~10-50 ms latency-vel
- **Subagent-fanout pattern** bulk-LLM-task-ra $0 cost (Claude Code subscription)
- **G-Eval + NLI + Coherence cascade** session-záráskor automatikus minőségbiztosítás
- **GitHub-trending heti monitoring** automatic cherry-pick suggestion
- **NotebookLM cross-projekt synthesis** ha NotebookLM-account-od van

## Backout

Bármely tengely kikapcsolható ENV-flag-gel (lásd `~/.vault-config/env-defaults.md`). A vault önmagában (klasszikus Obsidian-szinten) is teljesen funkcionális marad.

## Ki más csinálta meg

> _Ha sikerült reprodukálnod, PR-rel írj egy 2-mondatos visszajelzést ide: `docs/reproductions.md`._

## Probléma-megoldás

- **Memgraph connection refused** → `docker logs vault-memgraph`, port 7687 elérhetőség, container restart
- **bge-m3 OOM** → kisebb model: `intfloat/multilingual-e5-base` (~470 MB, helyettesít)
- **Claude Code subagent-fanout NEM működik** → ellenőrizd a subscription-státuszt + `claude --version`

## Kapcsolódó

- [README HU](../README.hu.md) · [README EN](../README.en.md)
- [8-axis architecture roadmap](../07-Decisions/2026-05-12%20Superintelligent%20vault%20evolution%20roadmap.md)
- [Karpathy LLM-Wiki pattern](../11-wiki/Karpathy-LLM-Wiki-pattern.md) — kiinduló minta
