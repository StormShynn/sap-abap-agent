"""
SAP Dict Bridge MCP Server — Tao Domain, Data Element, Database Table
bang cookie auth sap-btp-agent (khong can basic auth).

Chay nhu 1 MCP server rieng:
  python -m sap_btp_agent.bridge_server

Dang ky voi Claude Code:
  claude mcp add --transport stdio sap-dict-bridge -- python -m sap_btp_agent.bridge_server
"""
from __future__ import annotations

import asyncio
import sys

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from .tools.dictionary import build_dict_tools


def _build_server() -> Server:
    tools = build_dict_tools()
    tools_by_name = {t["name"]: t for t in tools}

    server: Server = Server("sap-dict-bridge")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(name=t["name"], description=t["description"], inputSchema=t["inputSchema"])
            for t in tools
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
        tool = tools_by_name.get(name)
        if tool is None:
            raise ValueError(f"Unknown tool: {name}")
        result = await tool["handler"](arguments or {})
        text = result if isinstance(result, str) else str(result)
        return [types.TextContent(type="text", text=text)]

    return server


async def run_stdio() -> None:
    server = _build_server()
    print("SAP Dict Bridge MCP server (stdio) dang chay... (Ctrl+C de dung)", file=sys.stderr)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
