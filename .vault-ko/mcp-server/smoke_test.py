#!/usr/bin/python3
"""
Smoke-test for vault_ko_mcp.py via the real MCP SDK client (stdio transport).

Spawns the server as a subprocess, runs each of the 4 tools, prints PASS/FAIL.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).parent / "vault_ko_mcp.py"


async def main() -> int:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    results: dict[str, dict] = {}

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_resp = await session.list_tools()
            tool_names = sorted(t.name for t in tools_resp.tools)
            results["list_tools"] = {
                "pass": tool_names == ["conflicts", "query", "stats", "top_k"],
                "tools": tool_names,
            }

            # Tool 1: query
            r = await session.call_tool("query", {"substring": "KGC", "top_k": 3})
            payload = json.loads(r.content[0].text)
            results["query"] = {
                "pass": isinstance(payload, list) and len(payload) >= 1
                        and all("subject" in f and "confidence" in f for f in payload),
                "count": len(payload) if isinstance(payload, list) else None,
                "sample": payload[0] if payload else None,
            }

            # Tool 2: stats
            r = await session.call_tool("stats", {})
            payload = json.loads(r.content[0].text)
            results["stats"] = {
                "pass": isinstance(payload, dict)
                        and "total_facts" in payload
                        and payload["total_facts"] > 0
                        and isinstance(payload.get("by_source_type"), list),
                "total_facts": payload.get("total_facts"),
                "source_types": [d.get("source_type") for d in payload.get("by_source_type", [])],
            }

            # Tool 3: conflicts
            r = await session.call_tool("conflicts", {})
            payload = json.loads(r.content[0].text)
            results["conflicts"] = {
                "pass": isinstance(payload, list),  # may be empty — still valid
                "count": len(payload) if isinstance(payload, list) else None,
                "sample": payload[0] if payload else None,
            }

            # Tool 4: top_k
            r = await session.call_tool("top_k", {"token": "KGC", "top_k": 3, "facts_per_subject": 2})
            payload = json.loads(r.content[0].text)
            results["top_k"] = {
                "pass": isinstance(payload, list)
                        and (len(payload) == 0 or all("source_count" in g and "facts" in g for g in payload)),
                "count": len(payload) if isinstance(payload, list) else None,
                "sample": payload[0] if payload else None,
            }

            # Bonus: invalid source_type → must surface as isError (SDK-layer enum validation)
            # or as a JSON error payload (our handler) — either is acceptable; the server
            # must NOT crash.
            r = await session.call_tool("query", {"substring": "x", "source_type": "bogus"})
            txt = r.content[0].text if r.content else ""
            try:
                payload = json.loads(txt)
                handler_err = isinstance(payload, dict) and "error" in payload
            except json.JSONDecodeError:
                handler_err = False
            sdk_err = bool(getattr(r, "isError", False))
            results["error_path"] = {
                "pass": handler_err or sdk_err,
                "isError": sdk_err,
                "message": txt[:120],
            }

    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    all_pass = all(v.get("pass") for v in results.values())
    print(f"\n{'PASS' if all_pass else 'FAIL'} — {sum(1 for v in results.values() if v.get('pass'))}/{len(results)}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
