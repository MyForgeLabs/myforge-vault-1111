#!/usr/bin/env bash
# Superintelligent Vault — interactive setup script
# Reprodukáció a `docs/reproduction-guide.md` szerint, automatizált formában

set -euo pipefail

PUBLIC_REPO_DIR="${PUBLIC_REPO_DIR:-$HOME/sv-public}"
VAULT_DIR="${VAULT_DIR:-$HOME/obsidian-vault}"

log() { printf '\033[1;36m[setup]\033[0m %s\n' "$*"; }
ok()  { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn(){ printf '\033[1;33m  ⚠\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m  ✗\033[0m %s\n' "$*"; }

confirm() {
  read -rp "  $1 [y/N] " yn
  [[ "$yn" =~ ^[Yy]$ ]]
}

# === Step 0: Preflight ===
log "Step 0 — Preflight check"
for cmd in docker python3 git bash; do
  command -v "$cmd" >/dev/null 2>&1 || { err "$cmd missing"; exit 1; }
done
ok "Docker, Python3, Git, Bash available"

if [[ ! -d "$PUBLIC_REPO_DIR" ]]; then
  err "Public repo not found at $PUBLIC_REPO_DIR. Clone it first."
  echo "      git clone https://github.com/<owner>/superintelligent-vault.git $PUBLIC_REPO_DIR"
  exit 2
fi
ok "Public SV-repo at $PUBLIC_REPO_DIR"

# === Step 1: Vault init ===
log "Step 1 — Vault skeleton init"
if [[ -d "$VAULT_DIR" ]]; then
  warn "Vault already exists at $VAULT_DIR"
  confirm "Continue anyway (won't overwrite existing content)?" || exit 0
else
  mkdir -p "$VAULT_DIR"
  cd "$VAULT_DIR"
  git init -q
  ok "Init $VAULT_DIR"
fi

cd "$VAULT_DIR"
mkdir -p 01-Daily 02-Projects 03-Hosts 04-Tasks 05-Memory 06-Audits 07-Decisions 08-Sessions 10-raw 10-raw/external 11-wiki

# Public-szafe content
for f in AGENTS.md; do
  [[ -f "$PUBLIC_REPO_DIR/$f" && ! -f "$f" ]] && cp "$PUBLIC_REPO_DIR/$f" ./ && ok "Copied $f"
done
for d in 00-Meta 11-wiki 07-Decisions; do
  if [[ -d "$PUBLIC_REPO_DIR/$d" && ! -d "$d" ]]; then
    cp -r "$PUBLIC_REPO_DIR/$d" ./
    ok "Copied $d/"
  fi
done

# Sprint skeletons
for d in .vault-ko .vault-memory .vault-eval .vault-tools .vault-nb .vault-agents .vault-rsi .vault-graph; do
  if [[ -d "$PUBLIC_REPO_DIR/$d" && ! -d "$d" ]]; then
    cp -r "$PUBLIC_REPO_DIR/$d" ./
    ok "Copied $d/"
  fi
done

# Memory templates
if [[ -d "$PUBLIC_REPO_DIR/.vault-skeletons/05-Memory" ]]; then
  for tmpl in "$PUBLIC_REPO_DIR/.vault-skeletons/05-Memory/"*.template.md; do
    fname=$(basename "$tmpl" .template.md).md
    if [[ ! -f "05-Memory/$fname" ]]; then
      cp "$tmpl" "05-Memory/$fname"
      ok "Memory template → 05-Memory/$fname (edit me!)"
    fi
  done
fi

# === Step 2: Docker Memgraph ===
log "Step 2 — Memgraph CE container"
if ! docker ps --format '{{.Names}}' | grep -q '^vault-memgraph$'; then
  if confirm "Start Memgraph container (vault-memgraph, port 7687)?"; then
    docker run -d --name vault-memgraph \
      -p 7687:7687 -p 7444:7444 \
      -v vault-memgraph-data:/var/lib/memgraph \
      memgraph/memgraph:latest >/dev/null
    sleep 3
    ok "Memgraph started"
  else
    warn "Memgraph skipped — B-2/B-4/B-7 features won't work"
  fi
else
  ok "Memgraph already running"
fi

# === Step 3: Python venv ===
log "Step 3 — Python venv + dependencies"
VENV_DIR="${VENV_DIR:-$HOME/.notebooklm-venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  if confirm "Create venv at $VENV_DIR (~2.5 GB with bge-m3)?"; then
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install \
      sentence-transformers \
      transformers \
      pymgclient \
      rank-bm25 \
      pyyaml \
      llama-index-core
    ok "venv created at $VENV_DIR"
  fi
fi

# === Step 4: Scripts symlink ===
log "Step 4 — Vault-tooling scripts"
if [[ -d "$PUBLIC_REPO_DIR/scripts" ]]; then
  for sub in 11.11 vault; do
    for src in "$PUBLIC_REPO_DIR/scripts/$sub"-*; do
      [[ -f "$src" ]] || continue
      fname=$(basename "$src")
      target="/usr/local/bin/$fname"
      if [[ ! -e "$target" ]]; then
        if sudo cp "$src" "$target" 2>/dev/null && sudo chmod +x "$target"; then
          ok "Installed $fname"
        else
          warn "Need sudo to install $fname"
        fi
      fi
    done
  done
fi

# === Step 5: Vault-config ===
log "Step 5 — Vault config defaults"
mkdir -p "$HOME/.vault-config"
[[ ! -f "$HOME/.vault-config/crystallize-threshold.txt" ]] && echo "0.95" > "$HOME/.vault-config/crystallize-threshold.txt" && ok "crystallize-threshold = 0.95"

# === Done ===
log "Setup complete"
cat <<EOF

Következő lépések:
  1. Editáld a 05-Memory/User.md és Infrastructure.md fájlokat (placeholderek!)
  2. cd $VAULT_DIR && git add . && git commit -m "Initial vault" (saját PRIVÁT repo-ba)
  3. Smoke-test:  vault-search "test"
  4. Reproduction-guide részletekért: cat $PUBLIC_REPO_DIR/docs/reproduction-guide.md
EOF
