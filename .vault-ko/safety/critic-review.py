#!/usr/bin/env python3
"""Real-LLM Critic runner — Layer 4 of bmad-vault-bridge safety-gate.

B-8 RSI Tier-2 skeleton (2026-05-19). Opt-in via `VAULT_CRITIC_ACTIVE=1`.

Pipeline (2-phase pending pattern, reused from crystallize-pending skill):

    Phase 1 (this script):  write pending/<hash>-request.json
    Phase 2 (Claude subagent): read request.json → write response.json
    Phase 3 (this script):  re-read response.json → apply threshold-policy → verdict

Until `VAULT_CRITIC_ACTIVE=1` is exported, callers fall through to the
deterministic 4-rule Critic-stub in the git pre-commit hook.

Public entrypoint:
    score_change(diff_text, target_file, bullet_text) -> dict

Returns:
    {
        "factuality": 0.0-1.0,
        "novelty":    0.0-1.0,
        "durability": 0.0-1.0,
        "vault_fit":  0.0-1.0,
        "safety":     0.0-1.0,
        "mean":       0.0-1.0,
        "min":        0.0-1.0,
        "reasoning":  "<text>",
        "verdict":    "pass" | "fail",
        "mode":       "strict" | "default" | "lenient",
        "request_hash": "<sha1-12>",
    }

Threshold modes (env VAULT_CRITIC_MODE, default=strict):
    strict   — all 5 dims >= 0.85 AND safety >= 0.9
    default  — mean >= 0.7 AND safety >= 0.9 AND min >= 0.5
    lenient  — mean >= 0.5 AND safety >= 0.9
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
PENDING_DIR = VAULT_ROOT / ".vault-ko" / "safety" / "pending"
AUDIT_LOG = VAULT_ROOT / "06-Audits" / "critic-review-log.jsonl"
PROMPT_TEMPLATE = VAULT_ROOT / ".vault-ko" / "prompts" / "critic-review-template.md"

DIMS = ("factuality", "novelty", "durability", "vault_fit", "safety")
SAFETY_HARD_GATE = 0.9
DEFAULT_TIMEOUT_S = 300  # 5 min (fail-closed)

log = logging.getLogger("critic-review")
if not log.handlers:
    logging.basicConfig(
        level=os.environ.get("CRITIC_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


# ---------------------------------------------------------------------------
# Hashing + paths
# ---------------------------------------------------------------------------


def _request_hash(diff_text: str, target_file: str, bullet_text: str) -> str:
    """Stable sha1-12 for a (diff, target, bullet) tuple. Idempotent."""
    h = hashlib.sha1()
    h.update(target_file.encode("utf-8"))
    h.update(b"\x1e")
    h.update(bullet_text.encode("utf-8"))
    h.update(b"\x1e")
    h.update(diff_text.encode("utf-8"))
    return h.hexdigest()[:12]


def _request_path(req_hash: str) -> Path:
    return PENDING_DIR / f"{req_hash}-request.json"


def _response_path(req_hash: str) -> Path:
    return PENDING_DIR / f"{req_hash}-response.json"


# ---------------------------------------------------------------------------
# Phase 1 — write request
# ---------------------------------------------------------------------------


def _load_prompt_template() -> str:
    if not PROMPT_TEMPLATE.exists():
        return "(template missing — score conservatively)"
    return PROMPT_TEMPLATE.read_text(encoding="utf-8")


def write_request(
    diff_text: str,
    target_file: str,
    bullet_text: str,
    req_hash: str | None = None,
) -> Path:
    """Phase 1: persist the Critic request. Idempotent (no overwrite)."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    req_hash = req_hash or _request_hash(diff_text, target_file, bullet_text)
    req_path = _request_path(req_hash)
    if req_path.exists():
        log.debug("request %s already on disk, skipping write", req_hash)
        return req_path
    payload = {
        "schema": "critic-review/v1",
        "hash": req_hash,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_file": target_file,
        "bullet_text": bullet_text,
        "diff_text": diff_text,
        "prompt_template_path": str(PROMPT_TEMPLATE),
        "expected_dims": list(DIMS),
        "output_format": "json-only-no-fence",
    }
    tmp = req_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(req_path)  # atomic
    log.info("phase-1 wrote request: %s", req_path.name)
    return req_path


# ---------------------------------------------------------------------------
# Phase 3 — read response + parse
# ---------------------------------------------------------------------------


def _coerce_float(v: Any, name: str) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError) as e:
        raise ValueError(f"dim '{name}' is not a float: {v!r}") from e
    if not (0.0 <= f <= 1.0):
        raise ValueError(f"dim '{name}'={f} out of [0,1]")
    return f


def parse_response(text: str) -> Dict[str, Any]:
    """Parse the subagent JSON response. Strip ```json``` fence if present.

    Returns dict with 5 dim floats + reasoning. Raises ValueError on malformed.
    """
    stripped = text.strip()
    if stripped.startswith("```"):
        # ```json ... ``` or ``` ... ```
        lines = stripped.splitlines()
        body = [ln for ln in lines if not ln.startswith("```")]
        stripped = "\n".join(body).strip()
    obj = json.loads(stripped)
    # Allow either flat schema or {"scores": {...}, "reasoning": ...}
    if "scores" in obj and isinstance(obj["scores"], dict):
        scores_src = obj["scores"]
        reasoning = obj.get("reasoning", "")
    else:
        scores_src = obj
        reasoning = obj.get("reasoning", "")
    out: Dict[str, Any] = {}
    for d in DIMS:
        if d not in scores_src:
            raise ValueError(f"missing dim '{d}' in response")
        out[d] = _coerce_float(scores_src[d], d)
    out["reasoning"] = str(reasoning)[:2000]
    return out


def read_response(req_hash: str) -> Dict[str, Any] | None:
    """Phase 3: load + parse the subagent response. None if not yet written."""
    resp_path = _response_path(req_hash)
    if not resp_path.exists():
        return None
    raw = resp_path.read_text(encoding="utf-8")
    return parse_response(raw)


# ---------------------------------------------------------------------------
# Threshold policy
# ---------------------------------------------------------------------------


def apply_threshold(scores: Dict[str, float], mode: str) -> str:
    """Return 'pass' or 'fail' per threshold mode.

    Safety hard-gate is enforced first in every mode.
    """
    safety = scores["safety"]
    if safety < SAFETY_HARD_GATE:
        return "fail"
    vals = [scores[d] for d in DIMS]
    mean = sum(vals) / len(vals)
    mn = min(vals)
    if mode == "strict":
        if all(v >= 0.85 for v in vals) and safety >= SAFETY_HARD_GATE:
            return "pass"
        return "fail"
    if mode == "default":
        if mean >= 0.7 and mn >= 0.5 and safety >= SAFETY_HARD_GATE:
            return "pass"
        return "fail"
    if mode == "lenient":
        if mean >= 0.5 and safety >= SAFETY_HARD_GATE:
            return "pass"
        return "fail"
    raise ValueError(f"unknown VAULT_CRITIC_MODE: {mode}")


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


def _append_audit(record: Dict[str, Any]) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False)
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as e:  # don't crash gate on audit failure
        log.warning("audit-log write failed: %s", e)


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def score_change(
    diff_text: str,
    target_file: str,
    bullet_text: str,
    mode: str | None = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> Dict[str, Any]:
    """Full 3-phase: write request → wait for response → verdict.

    If no response is available before `timeout_s` elapses, return
    `verdict=fail` (fail-closed) with reasoning="critic-timeout".

    NOTE: this skeleton does NOT itself spawn the subagent — that is the
    crystallize-pending pattern, owned by the caller (bmad-vault-bridge
    or 11.11crystallize). The caller is responsible for invoking a Claude
    subagent that reads the request.json and writes the response.json.
    """
    mode = (mode or os.environ.get("VAULT_CRITIC_MODE") or "strict").lower()
    req_hash = _request_hash(diff_text, target_file, bullet_text)
    write_request(diff_text, target_file, bullet_text, req_hash=req_hash)

    deadline = time.time() + timeout_s
    parsed: Dict[str, Any] | None = None
    last_err: str | None = None
    while time.time() < deadline:
        try:
            parsed = read_response(req_hash)
            if parsed is not None:
                break
        except (json.JSONDecodeError, ValueError) as e:
            last_err = str(e)
            log.warning("malformed response for %s: %s", req_hash, e)
            break
        time.sleep(1.0)

    if parsed is None:
        verdict_reason = f"critic-timeout-or-malformed: {last_err or 'no response'}"
        result: Dict[str, Any] = {
            d: 0.0 for d in DIMS
        }
        result.update(
            mean=0.0,
            min=0.0,
            reasoning=verdict_reason,
            verdict="fail",
            mode=mode,
            request_hash=req_hash,
        )
        _append_audit(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "hash": req_hash,
                "target_file": target_file,
                "verdict": "fail",
                "mode": mode,
                "scores": None,
                "reasoning": verdict_reason,
            }
        )
        return result

    scores = {d: parsed[d] for d in DIMS}
    verdict = apply_threshold(scores, mode)
    vals = list(scores.values())
    result = dict(scores)
    result.update(
        mean=sum(vals) / len(vals),
        min=min(vals),
        reasoning=parsed.get("reasoning", ""),
        verdict=verdict,
        mode=mode,
        request_hash=req_hash,
    )
    _append_audit(
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "hash": req_hash,
            "target_file": target_file,
            "verdict": verdict,
            "mode": mode,
            "scores": scores,
            "reasoning": result["reasoning"][:500],
        }
    )
    return result


# ---------------------------------------------------------------------------
# CLI surface (skeleton — primarily for the hook to invoke)
# ---------------------------------------------------------------------------


def _cli() -> int:
    import argparse

    p = argparse.ArgumentParser(description="B-8 Critic runner (skeleton)")
    p.add_argument("--target", required=True, help="target file path")
    p.add_argument("--bullet", required=True, help="bullet text")
    p.add_argument("--diff", default="", help="diff text (default empty)")
    p.add_argument("--mode", default=None, help="strict|default|lenient")
    p.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT_S, help="seconds"
    )
    p.add_argument(
        "--prepare-only",
        action="store_true",
        help="Phase 1 only: write request.json then exit (skeleton helper)",
    )
    args = p.parse_args()
    if args.prepare_only:
        path = write_request(args.diff, args.target, args.bullet)
        print(str(path))
        return 0
    out = score_change(
        args.diff, args.target, args.bullet, mode=args.mode, timeout_s=args.timeout
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out["verdict"] == "pass" else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
