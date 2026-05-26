---
name: Anthropic-protokoll proxy wrapper minta — provider-független Claude Code
type: wiki
tags: ["#type/wiki", "agent-runtime", "proxy", "openai-anthropic-bridge", "vendor-portability", "local-llm"]
created: 2026-05-19
updated: 2026-05-19
source_repo: Alishahryar1/free-claude-code
source_url: https://github.com/Alishahryar1/free-claude-code
source_license: MIT
---

# Anthropic-protokoll proxy wrapper minta

Egy minta arra, hogyan lehet egy zárt vendor-protokollt (Claude Code Anthropic Messages API) **kliens-szinten stabilan tartani**, miközben a szerver-oldalt teljesen lecseréljük: NVIDIA NIM, OpenRouter, DeepSeek, lokális LM Studio / llama.cpp / Ollama. A Alishahryar1/free-claude-code repo (`fcc-server` + `fcc-claude`) ezt egy FastAPI-proxy-val oldja meg, ami **Anthropic-kompatibilis route-okat** (`/v1/messages`, `/v1/messages/count_tokens`, `/v1/models`) ad ki, és per-modell-tier routing-ot támogat.

Ez egy **vendor-portability** és **cost-optimization** minta egyszerre: lecseréled a vendor-stack-et anélkül, hogy a kliensed (Claude Code CLI, VSCode extension, JetBrains ACP) tudna róla.

## Az alapelv

A Claude Code kliens **Anthropic-protokollt beszél**. Ezt két különböző réteg adja vissza:

1. **Helyi: Anthropic-Messages-szerű provider** (Wafer, OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama) — átkapcsolható transport, alig kell normalizálás
2. **Helyi: OpenAI Chat-Completions provider** (NIM, OpenCode Zen, Z.ai) — OpenAI-SSE-t kell **Anthropic SSE-vé translálni**

Ez a fordító-réteg a kulcs-érték: az SSE-event-stream-eket átalakítja, a thinking-block-okat (`thinking`/`redacted_thinking`) normalizálja, a tool-call-okat egységes shape-be hozza, és a token-usage metadata-t Claude Code-kompatibilis formátumba teszi.

## Per-model-tier routing

A Claude Code 3 modell-tier-t használ: Opus / Sonnet / Haiku, plus fallback. A proxy mind a négyet külön-külön provider-re routolhatja:

```
MODEL          = zai/glm-5.1                              # fallback
MODEL_OPUS     = nvidia_nim/moonshotai/kimi-k2.5          # Opus → NIM Kimi
MODEL_SONNET   = open_router/deepseek/deepseek-r1-0528:free # Sonnet → OpenRouter free
MODEL_HAIKU    = lmstudio/unsloth/GLM-4.7-Flash-GGUF       # Haiku → local LM Studio
```

Ez a minta szabványosítható minden olyan rendszerre, ahol egy "model name" valójában egy **cost/latency-tier**, nem konkrét modell — a tier feloldása késleltethető a runtime-ra.

## Gateway model discovery + native picker support

A `/v1/models` endpoint visszaadja a proxy által elérhető modelleket. A `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` env-var-ral a Claude Code **native `/model` picker-ben** megjelennek a gateway-modellek — vagyis a user runtime-ban válthat NIM-Kimi és Wafer-DeepSeek közt anélkül, hogy proxy-config-ot szerkesztene.

Ez egy fontos UX-elv: a vendor-portability ne legyen "vagy-vagy" döntés install-time-ban — legyen runtime switch.

## Admin UI (loopback-only) + validáció pattern

A proxy `127.0.0.1:8082/admin` URL-en egy lokális Admin UI-t exponál. Ez NEM internet-facing, **loopback-only** binding. Minden config-mező (`NVIDIA_NIM_API_KEY`, `MODEL`, voice-settings, Discord/Telegram-token) Validate → Apply 2-lépéses commit-on megy keresztül. Mivel a config-fájl `~/.fcc/.env` és a server SIGHUP-ra reload-ol, a validáció megakadályozza hogy egy rosszul típusozott value crash-elje a futó-proxy-t.

Reusable elemek:

- **Admin UI loopback-binding** — credential-management mindig local-only, soha 0.0.0.0
- **Validate → Apply 2-stage commit** — minden Admin-mode-műveletre általánosítható
- **`/admin` mint stabil URL** — első-class endpoint, nem külön port

## Optional integrations (opt-in extras-pattern)

A repo `pyproject.toml` optional-extras-t használ a voice és voice_local feature-ökhöz:

```bash
uv tool install --force "free-claude-code[voice] @ git+..."        # NIM Riva gRPC
uv tool install --force "free-claude-code[voice_local] @ git+..."  # Local Whisper CPU/CUDA
uv tool install --force "free-claude-code[voice,voice_local] @ git+..." # both
```

A `--torch-backend cu130` flag CUDA-builds-re. Ez a **modular install** minta — alap-package könnyű marad, a heavy-deps (PyTorch, gRPC) opt-in. Hasonló a `npm install --include=optional` / `pip install pkg[extra]` általános konvencióhoz.

## Auto-compact-window override

A `fcc-claude` indít minden Claude-process előtt `CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000` env-var-t. Ez azért lényeges, mert a free-tier vagy local-LLM provider-ek context-window-ja gyakran 200K körül van (NIM Kimi, Z.ai GLM-5.1) — a Claude Code default-auto-compact gyakran túl-konzervatív. A proxy kliens-oldalt írja át, NEM a server-választ.

## Bot wrappers (Discord / Telegram) — remote-session pattern

A `messaging/` modul a fcc-server-en kívül egy remote-coding-session-wrapper-t implementál. Discord vagy Telegram bot:

- Streams progress (SSE-szerű incremental)
- Reply-thread = conversation-branch
- `/stop`, `/clear` per-branch granularity
- `Allowed Directory` absolute-path config — bot csak ezen a workspace-en dolgozhat
- `Allowed Discord Channels` / `Allowed Telegram User ID` — explicit allowlist

Ez egy **remote-coding-on-mobile** UX-minta, ami máshol is reusable (pl. SV-vault: 11.11note mobil-bevitelre Telegram bot-tal).

## Provider-katalógus + factory pattern

A `config.provider_catalog` registry-ben minden provider metadata + endpoint-template, a `providers.registry` factory-ben pedig a transport-class (`OpenAIChatTransport` vagy `AnthropicMessagesTransport`) wiring. **Új provider hozzáadása: extend transport + registrer entry**, nincs core-change. Ugyanaz a registry-pattern, mint a codegraph multi-target-installer-jénél [[codegraph-pre-indexed-token-saver#Multi-agent installer architektúra]].

## Local-request optimization

A proxy **lokálisan válaszol triviális Claude Code probe-okra** (health-check, capability-discovery), hogy ne költsön quota-t / latency-t a provider-en. Ez egy klasszikus proxy-pattern (response-shortcut), de itt explicit a Claude Code-protokoll context-jében.

## Mit tanulhatunk a saját SV stack-ünkbe

Lásd "Őszinte rivalitás" lent. Konkrét átvehető-elemek:

- **Anthropic-protokoll-proxy mint vendor-portability bástya** — a SV-vault stack-ünk most hardcoded API-key-eken keresztül Anthropic-API-zik. Ha valaha a cost-tier-en akarunk gondolkodni (Opus→DeepSeek-R1-free), egy ilyen proxy az alap-feltétel.
- **Local LLM provider mint $0 fallback** — a vault-ko-ingest, crystallize-scoring subagent-fanout-jaink jelenleg subagent-Claude-Claude. Egy lokális Ollama-fallback előkészítve a `claude-code-scorer` interface-en érdekes lehet egyszerű scoring-feladatokhoz.
- **Admin UI Validate→Apply 2-stage minta** — a `~/.vault-config/crystallize-threshold.txt` hot-reloadable, de NEM type-validált. Egy Admin-UI-szerű validate-step hozzáadhatja a config-konzisztenciát.
- **Optional extras `[voice]` minta** — a vault-net-ingest jelenleg minden firecrawl+gh-cli-t kötelezően installál. Egy `vault-tools[net]` opcionális-extra elválaszthatná a net-tanulás-stack-et az alap vault-toolingtól.
- **Telegram-bot mint remote 11.11note** — ha vault-on dolgozunk mobil-ról, egy Telegram-bot wrapper a 11.11note-on egy lehetséges UX-extension.

## Forrás-hivatkozások

- Repo: <https://github.com/Alishahryar1/free-claude-code>
- License: MIT
- Stack: Python 3.14 + uv + FastAPI + uvicorn + loguru
- 10 provider: NVIDIA NIM, Kimi, Wafer, OpenRouter, DeepSeek, LM Studio, llama.cpp, Ollama, OpenCode Zen, Z.ai
- Raw-ingest: [[../10-raw/external/Alishahryar1_free-claude-code/README]] + [[../10-raw/external/Alishahryar1_free-claude-code/AGENTS]]

## Kapcsolódó

- [[sv-04-tool-composition]] — agent-tool-stack-ben provider-réteg
- [[nextjs-api-proxy-bridge]] — Next.js proxy-minta analógja
- [[multi-layer-safety-gate]] — Admin-UI Validate→Apply analógja
- [[claude-code-harness-blocks]] — Claude Code env-var runtime-block-okkal
- [[agent-vault-setup-playbook]] — multi-agent setup, ahol egy proxy elhelyezkedhet
