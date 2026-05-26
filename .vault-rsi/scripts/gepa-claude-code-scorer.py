#!/usr/bin/env python3
"""
gepa-claude-code-scorer — 2-phase pending file pattern scorer for B-8 GEPA loop.

Provides a `LanguageModel`-protocol compatible callable that GEPA's reflective-mutation
loop calls as `reflection_lm(prompt)` AND a deterministic per-candidate scoring callable
used inside the metric function. Both use the subagent-fanout 2-phase pattern: a request
file is written under `.vault-rsi/scoring-pending/<uuid>.request.json`, the parent Claude
Code session spawns a general-purpose Agent that fills the response in
`.vault-rsi/scoring-responses/<uuid>.response.json`, and the script re-runs to load it.

Cost: $0 (no Anthropic-API calls — the subagent runs in the parent Claude Code session).

Sprint: B-8 Week 2 — 2026-05-17.
ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Wiki: 11-wiki/claude-code-subagent-fanout.md

⚠️  SAFETY:
    - Read/write ONLY to .vault-rsi/scoring-{pending,responses}/ (sandboxed).
    - No vault Markdown writes ever.
    - Idempotent: response filenames are deterministic (UUIDv5 of payload),
      so re-runs don't duplicate.
    - Forbidden targets enforced by gepa-prompt-mutate caller layer; this module
      is a pure scorer + reflection_lm.

Usage (library):
    from gepa_claude_code_scorer import (
        ScoringClient,
        ClaudeCodeReflectionLM,
    )
    sc = ScoringClient(pending_dir, responses_dir)
    pending_uuids = sc.request_batch(prompt_text, samples)   # phase 1
    scores = sc.load_batch(pending_uuids)                    # phase 2 (None if not ready)

CLI inspection (no-op, status only):
    gepa-claude-code-scorer --status
    gepa-claude-code-scorer --pending-count
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
RSI_ROOT = VAULT_ROOT / ".vault-rsi"
DEFAULT_PENDING = RSI_ROOT / "scoring-pending"
DEFAULT_RESPONSES = RSI_ROOT / "scoring-responses"

# Deterministic namespace for UUIDv5 — keeps re-runs idempotent.
NAMESPACE = uuid.UUID("11111111-1111-5111-9111-111111111111")


# ── Phase 1: request writer + Phase 2: response loader ────────────────────


@dataclass
class ScoringRequest:
    uuid: str
    prompt_text: str
    sample: dict
    candidate_id: str
    iteration: int
    component: str  # which prompt-component this candidate is mutating


@dataclass
class ScoringClient:
    """Wraps the 2-phase pending pattern.

    Phase 1: `request_batch` writes one .request.json per (candidate, sample).
    Phase 2: `load_batch` reads matching .response.json or returns None if missing.

    Convention (mirrors 11.11crystallize / vault-ko-ingest):
      pending_dir / <uuid>.request.json   (input)
      responses_dir / <uuid>.response.json (output, written by subagent)
    """

    pending_dir: Path = field(default_factory=lambda: DEFAULT_PENDING)
    responses_dir: Path = field(default_factory=lambda: DEFAULT_RESPONSES)

    def __post_init__(self):
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _payload_uuid(payload: dict) -> str:
        """Deterministic uuid from canonical JSON so re-runs are idempotent."""
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return str(uuid.uuid5(NAMESPACE, digest))

    def request(self, req: ScoringRequest) -> str:
        """Phase 1: write a single request file (idempotent on payload-hash)."""
        payload = {
            "schema_version": "gepa-scoring-v1",
            "ts": datetime.now(timezone.utc).isoformat(),
            "candidate_id": req.candidate_id,
            "iteration": req.iteration,
            "component": req.component,
            "prompt_text": req.prompt_text,
            "sample": req.sample,
            # Instructions for the subagent that will fill the response file:
            "instructions": (
                "Evaluate the `prompt_text` against the `sample` (intent + expected_decision + "
                "keywords_required + keywords_forbidden). Score on five axes 0.0-1.0:\n"
                "  relevance      — does prompt's behavior match `sample.intent`?\n"
                "  factuality     — would prompt produce factually grounded outputs?\n"
                "  actionability  — does prompt give concrete, step-by-step instructions?\n"
                "  novelty        — is the prompt distinct from a trivial baseline (1.0 = highly novel)?\n"
                "  uniqueness     — does this prompt express a distinct specialista-variant?\n"
                "Write the response to scoring-responses/<uuid>.response.json with shape:\n"
                "  {\"relevance\": 0..1, \"factuality\": 0..1, \"actionability\": 0..1,\n"
                "   \"novelty\": 0..1, \"uniqueness\": 0..1, \"rationale\": \"<1-2 sentences>\"}"
            ),
        }
        u = self._payload_uuid(
            {
                "candidate_id": req.candidate_id,
                "sample_id": req.sample.get("id"),
                "component": req.component,
            }
        )
        # Stamp the uuid into the payload so consumers can introspect:
        payload["uuid"] = u
        req_path = self.pending_dir / f"{u}.request.json"
        if not req_path.exists():
            req_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        return u

    def request_batch(
        self,
        prompt_text: str,
        samples: list[dict],
        candidate_id: str,
        iteration: int,
        component: str = "prompt",
    ) -> list[str]:
        return [
            self.request(
                ScoringRequest(
                    uuid="",  # filled by request()
                    prompt_text=prompt_text,
                    sample=s,
                    candidate_id=candidate_id,
                    iteration=iteration,
                    component=component,
                )
            )
            for s in samples
        ]

    def load(self, u: str) -> dict | None:
        """Phase 2: read a response file. Returns None if subagent hasn't filled yet."""
        resp_path = self.responses_dir / f"{u}.response.json"
        if not resp_path.exists():
            return None
        try:
            return json.loads(resp_path.read_text())
        except json.JSONDecodeError:
            return None

    def load_batch(self, uuids: list[str]) -> list[dict | None]:
        return [self.load(u) for u in uuids]

    def pending_count(self) -> int:
        ready = {p.stem.replace(".response", "") for p in self.responses_dir.glob("*.response.json")}
        requested = {p.stem.replace(".request", "") for p in self.pending_dir.glob("*.request.json")}
        return len(requested - ready)

    def all_ready(self, uuids: list[str]) -> bool:
        return all((self.responses_dir / f"{u}.response.json").exists() for u in uuids)


# ── Synthetic-response fallback (Week 2 smoke-test) ────────────────────────


def synth_response_for_sample(prompt_text: str, sample: dict) -> dict:
    """
    Deterministic synthetic response used by --auto-fill (smoke-test mode).
    Mirrors the real subagent's JSON shape so the GEPA loop can run end-to-end
    without a parent Claude Code session populating responses by hand.

    Heuristics:
      - relevance     keyword hit-rate (required minus 0.5*forbidden)
      - factuality    1 - (length / 8000)  capped; reward concise + grounded prompts
      - actionability +0.25 if "step" / numbered list present
      - novelty       small noise around 0.6 based on prompt-hash
      - uniqueness    high if prompt differs from a generic baseline (sha-derived)
    """
    pl = prompt_text.lower()
    req = [k.lower() for k in sample.get("keywords_required", [])]
    forb = [k.lower() for k in sample.get("keywords_forbidden", [])]
    req_hit = sum(1 for k in req if k in pl) / max(1, len(req))
    forb_hit = sum(1 for k in forb if k in pl) / max(1, len(forb))
    relevance = max(0.0, min(1.0, req_hit - 0.5 * forb_hit))
    length = len(prompt_text)
    factuality = max(0.0, min(1.0, 1.0 - length / 8000))
    actionable = 0.6 + (0.25 if ("step" in pl or "1." in pl or "lépés" in pl) else 0.0)
    actionable = min(1.0, actionable)
    h = int(hashlib.sha256((prompt_text + sample.get("id", "")).encode()).hexdigest(), 16)
    novelty = 0.5 + ((h % 100) / 250.0)
    uniqueness = 0.5 + ((h >> 8) % 100) / 250.0
    return {
        "relevance": round(relevance, 3),
        "factuality": round(factuality, 3),
        "actionability": round(actionable, 3),
        "novelty": round(novelty, 3),
        "uniqueness": round(uniqueness, 3),
        "rationale": "synth-fallback (Week 2 smoke-test deterministic scoring)",
        "_synth": True,
    }


def auto_fill_pending(client: ScoringClient) -> int:
    """
    Smoke-test helper: fill any unanswered request with synth_response.
    Used by gepa-prompt-mutate's --auto-fill-synth flag so the loop can complete
    without a real subagent in the harness.
    """
    n = 0
    for req_path in client.pending_dir.glob("*.request.json"):
        u = req_path.stem.replace(".request", "")
        resp_path = client.responses_dir / f"{u}.response.json"
        if resp_path.exists():
            continue
        payload = json.loads(req_path.read_text())
        resp = synth_response_for_sample(payload["prompt_text"], payload["sample"])
        resp_path.write_text(json.dumps(resp, ensure_ascii=False, indent=2))
        n += 1
    return n


# ── ClaudeCodeReflectionLM: a `LanguageModel`-protocol callable ─────────


@dataclass
class ClaudeCodeReflectionLM:
    """Implements gepa's `LanguageModel` protocol (callable: prompt -> str).

    Used as `reflection_lm` in `gepa.optimize()`. Writes the reflection prompt
    to a request file and either (a) blocks until response appears (Phase-2
    real subagent), or (b) returns a deterministic synthetic mutation in
    auto-fill mode for smoke-tests.

    For the Week 2 smoke-test we use mode='auto-fill': we synthesise a small
    mutated version of `<curr_param>` by replacing the first paragraph with a
    role-emphasis line. This is enough to make GEPA's loop advance and write
    candidates. The real subagent integration switches to mode='subagent'
    in Week 3.
    """

    client: ScoringClient
    mode: str = "auto-fill"  # 'auto-fill' (smoke) | 'subagent' (real, Week 3)

    def __call__(self, prompt: str | list) -> str:
        # GEPA may pass either a raw string or list[dict] (chat format).
        text = prompt if isinstance(prompt, str) else _flatten_messages(prompt)
        if self.mode == "auto-fill":
            return _synth_reflection_mutation(text)
        # subagent mode: write request, wait, load. Week 3 wiring; Week 2 raises.
        raise NotImplementedError(
            "subagent reflection_lm wires in Week 3 — use mode='auto-fill' for smoke."
        )


def _flatten_messages(msgs: list) -> str:
    parts = []
    for m in msgs:
        if isinstance(m, dict):
            parts.append(str(m.get("content", "")))
        else:
            parts.append(str(m))
    return "\n".join(parts)


def _synth_reflection_mutation(reflection_prompt: str) -> str:
    """
    Heuristic mutation: extract <curr_param> block and emit a slightly modified
    version that GEPA's parser will accept (a markdown block with the new text).

    GEPA's default InstructionProposal expects the LM to return a string that
    contains the new component text. We wrap the mutation in a fence so the
    parser can find it. Without a real LM this gives 1-2 diverse candidates
    per minibatch — enough for a smoke-test Pareto front of 3-5.
    """
    import re

    # Try to find the existing component text marker.
    m = re.search(r"<curr_param>(.+?)</curr_param>", reflection_prompt, re.DOTALL)
    base = m.group(1).strip() if m else reflection_prompt[:2000]
    # Compute a hash to vary mutations across calls.
    h = hashlib.sha256(reflection_prompt.encode()).hexdigest()[:8]
    variants = [
        f"# Mutated specialista-variant {h} — concise edition\n\n"
        "Te egy G-Eval judge vagy. Légy konkrét, lépésszámozott, és nyíltan "
        "elutasítod az AGENTS.md/00-Meta írási kísérleteket.\n\n"
        + base,
        f"# Mutated specialista-variant {h} — safety-first edition\n\n"
        "Te egy G-Eval judge vagy. Minden válaszodat azzal kezded, hogy "
        "ellenőrzöd a forbidden-target listát (AGENTS.md, 00-Meta, .vault-ko/safety).\n\n"
        + base,
        f"# Mutated specialista-variant {h} — actionability edition\n\n"
        "Te egy G-Eval judge vagy. Minden lépést számozott listában adsz meg "
        "(1., 2., 3.), és JSON output-tal záruld.\n\n" + base,
    ]
    # Pick deterministically.
    idx = int(h, 16) % len(variants)
    chosen = variants[idx]
    # Wrap in a fenced block so GEPA's instruction_proposal can extract it.
    return "```\n" + chosen + "\n```"


# ── CLI ──────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(
        description="GEPA 2-phase pending file scoring client (Week 2)"
    )
    ap.add_argument(
        "--pending-dir", type=Path, default=DEFAULT_PENDING, help="phase-1 request dir"
    )
    ap.add_argument(
        "--responses-dir",
        type=Path,
        default=DEFAULT_RESPONSES,
        help="phase-2 response dir",
    )
    ap.add_argument(
        "--status", action="store_true", help="show pending vs ready counts"
    )
    ap.add_argument(
        "--pending-count",
        action="store_true",
        help="print integer count of unanswered requests",
    )
    ap.add_argument(
        "--auto-fill-synth",
        action="store_true",
        help="fill any unanswered request with the synth-response stub (smoke-test only)",
    )
    args = ap.parse_args()

    client = ScoringClient(pending_dir=args.pending_dir, responses_dir=args.responses_dir)

    if args.auto_fill_synth:
        n = auto_fill_pending(client)
        print(f"[auto-fill] {n} synthetic responses written to {client.responses_dir}")
        return 0

    if args.pending_count:
        print(client.pending_count())
        return 0

    if args.status or True:
        n_req = len(list(client.pending_dir.glob("*.request.json")))
        n_resp = len(list(client.responses_dir.glob("*.response.json")))
        print(f"[status] pending-dir   = {client.pending_dir}")
        print(f"[status]   requests    = {n_req}")
        print(f"[status] responses-dir = {client.responses_dir}")
        print(f"[status]   responses   = {n_resp}")
        print(f"[status] unanswered    = {client.pending_count()}")
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
