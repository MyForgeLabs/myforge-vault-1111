#!/root/.notebooklm-venv/bin/python3
"""
nli-server - long-running daemon for warm DeBERTa NLI inference.

Solves B-3 Week 6 perf-gap: `eval-l2-nli-judge` cold-loads
MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli (~440 MB) per invocation
-> 50-60s per call. 25 inferences/session = ~21 min. Unacceptable for
the Layer 2.5/2.6 cascade hot-path.

This daemon keeps the model + tokenizer warm in RAM. RPC clients send
{premise, hypothesis} and get {entailment, neutral, contradiction,
latency_ms} in ~50-300 ms steady-state (model already JIT-warmed).

ADR: 07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md
Sprint: B-3, Week 6 (2026-05-17-3) - persistent NLI-process pool.

Protocol: line-oriented JSON over Unix socket (same shape as vault-search-server).
    Request:  {"method": "infer", "premise": "...", "hypothesis": "..."}
    Response: {"entailment": 0.91, "neutral": 0.07, "contradiction": 0.02,
               "winner": "entailment", "latency_ms": 142,
               "model": "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"}
    Other methods: {"method": "health"}, {"method": "batch", "pairs": [{...}, ...]}

Managed by systemd (skeleton only, NOT enabled by default):
    /etc/systemd/system/vault-nli.service
    systemctl daemon-reload && systemctl enable --now vault-nli.service
"""

import json
import os
import signal
import socketserver
import sys
import threading
import time

NLI_MODEL = os.environ.get(
    "NLI_MODEL", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
)
NLI_MAX_TOK = int(os.environ.get("NLI_MAX_TOK", "512"))

# /run preferred (tmpfs, systemd-friendly); /tmp fallback for non-systemd boot
SOCKET_PATH = os.environ.get(
    "VAULT_NLI_SOCKET",
    "/run/vault-nli.sock" if os.access("/run", os.W_OK) else "/tmp/vault-nli.sock",
)


def log(msg: str) -> None:
    print(f"[vault-nli-server] {msg}", file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------
# Model wrapper (load once, infer many)
# ----------------------------------------------------------------------------
class NLISingleton:
    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        log(f"loading NLI model {NLI_MODEL} (this is the slow part)...")
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL)
        # Switch HuggingFace nn.Module into inference mode (disables dropout etc.)
        getattr(self.model, "eval")()
        self.torch = torch
        self.id2label = self.model.config.id2label
        # warm-up forward-pass (first call JITs torch graphs)
        inputs = self.tokenizer(
            "warmup premise", "warmup hypothesis",
            return_tensors="pt", truncation=True, max_length=NLI_MAX_TOK,
        )
        with torch.no_grad():
            _ = self.model(**inputs).logits
        log(f"NLI model ready in {time.time()-t0:.2f}s (labels={list(self.id2label.values())})")
        self.lock = threading.Lock()
        self.loaded_at = time.time()
        self.infer_count = 0
        self.cum_latency_ms = 0.0

    def infer(self, premise: str, hypothesis: str) -> dict:
        t0 = time.time()
        with self.lock:
            inputs = self.tokenizer(
                premise, hypothesis,
                return_tensors="pt", truncation=True, max_length=NLI_MAX_TOK,
            )
            with self.torch.no_grad():
                logits = self.model(**inputs).logits
            probs = self.torch.softmax(logits, dim=-1)[0]
            label_probs = {
                self.id2label[i]: float(probs[i].item()) for i in self.id2label
            }
        winner = max(label_probs, key=label_probs.get)
        latency_ms = (time.time() - t0) * 1000.0
        self.infer_count += 1
        self.cum_latency_ms += latency_ms
        return {
            "entailment": round(label_probs.get("entailment", 0.0), 4),
            "neutral": round(label_probs.get("neutral", 0.0), 4),
            "contradiction": round(label_probs.get("contradiction", 0.0), 4),
            "winner": winner,
            "confidence": round(label_probs[winner], 4),
            "latency_ms": round(latency_ms, 1),
            "model": NLI_MODEL,
        }


# ----------------------------------------------------------------------------
# Unix socket server (line-oriented JSON, one request per connection)
# ----------------------------------------------------------------------------
class Handler(socketserver.StreamRequestHandler):
    timeout = 60

    def handle(self):
        try:
            raw = self.rfile.readline()
            if not raw:
                return
            req = json.loads(raw.decode("utf-8"))
            method = req.get("method", "infer")

            if method == "health":
                avg_ms = (NLI.cum_latency_ms / NLI.infer_count) if NLI.infer_count else 0.0
                resp = {
                    "ok": True,
                    "model": NLI_MODEL,
                    "loaded_at": NLI.loaded_at,
                    "uptime_s": round(time.time() - NLI.loaded_at, 1),
                    "infer_count": NLI.infer_count,
                    "avg_latency_ms": round(avg_ms, 1),
                    "max_tok": NLI_MAX_TOK,
                }

            elif method == "infer":
                premise = req.get("premise") or ""
                hypothesis = req.get("hypothesis") or ""
                if not premise or not hypothesis:
                    resp = {"error": "missing premise or hypothesis"}
                else:
                    resp = NLI.infer(premise, hypothesis)

            elif method == "batch":
                pairs = req.get("pairs") or []
                if not isinstance(pairs, list):
                    resp = {"error": "pairs must be a list of {premise, hypothesis}"}
                else:
                    results = []
                    for p in pairs:
                        prem = p.get("premise") or ""
                        hyp = p.get("hypothesis") or ""
                        if not prem or not hyp:
                            results.append({"error": "missing premise or hypothesis"})
                            continue
                        out = NLI.infer(prem, hyp)
                        if "id" in p:
                            out["id"] = p["id"]
                        results.append(out)
                    resp = {"results": results, "n": len(results)}

            else:
                resp = {"error": f"unknown method: {method}"}

        except Exception as e:
            resp = {"error": f"{type(e).__name__}: {e}"}

        try:
            self.wfile.write((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
            self.wfile.flush()
        except BrokenPipeError:
            pass


class ThreadingUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True


# ----------------------------------------------------------------------------
# Globals + main
# ----------------------------------------------------------------------------
NLI: NLISingleton | None = None
SERVER: ThreadingUnixServer | None = None


def cleanup_socket():
    try:
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
    except OSError as e:
        log(f"socket unlink failed: {e}")


def shutdown(signum, _frame):
    log(f"signal {signum} received - shutting down")
    if SERVER is not None:
        threading.Thread(target=SERVER.shutdown, daemon=True).start()


def main():
    global NLI, SERVER

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    log(f"starting (socket={SOCKET_PATH})")
    NLI = NLISingleton()

    cleanup_socket()
    SERVER = ThreadingUnixServer(SOCKET_PATH, Handler)
    os.chmod(SOCKET_PATH, 0o660)  # owner+group rw - root group on systemd
    log(f"listening on {SOCKET_PATH}")
    try:
        SERVER.serve_forever(poll_interval=0.5)
    finally:
        cleanup_socket()
        log("shutdown complete")


if __name__ == "__main__":
    main()
