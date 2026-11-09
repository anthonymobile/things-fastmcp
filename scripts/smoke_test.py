#!/usr/bin/env python3
"""
Stdio handshake smoke test for the Things MCP server.

Launches the ``things-mcp`` console script as a subprocess, performs the MCP
initialize handshake over stdio and lists the tools, exactly as Claude Desktop
would. Prints the tool names and exits non-zero on failure.

Uses only the MCP SDK's own stdio client, so it works on macOS without GNU
``timeout``. Does not require Things 3 to be running.

Usage: .venv/bin/python scripts/smoke_test.py [path/to/things-mcp]
"""
import asyncio
import os
import sys

from mcp import Client, StdioServerParameters

EXPECTED_TOOL_COUNT = 22
TIMEOUT_SECONDS = 30


async def main(command: str) -> int:
    params = StdioServerParameters(command=command, args=[])
    async with Client(params, read_timeout_seconds=TIMEOUT_SECONDS) as client:
        info = client.server_info
        print(f"handshake ok: server={info.name!r} version={info.version!r} "
              f"protocol={client.protocol_version}")
        result = await client.list_tools()
        names = sorted(t.name for t in result.tools)
        print(f"tools/list ok: {len(names)} tools")
        for name in names:
            print(f"  - {name}")
        if len(names) != EXPECTED_TOOL_COUNT:
            print(f"FAIL: expected {EXPECTED_TOOL_COUNT} tools, got {len(names)}", file=sys.stderr)
            return 1
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    default = os.path.join(os.path.dirname(sys.executable), "things-mcp")
    cmd = sys.argv[1] if len(sys.argv) > 1 else default
    try:
        rc = asyncio.run(asyncio.wait_for(main(cmd), timeout=TIMEOUT_SECONDS + 15))
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        rc = 1
    sys.exit(rc)
