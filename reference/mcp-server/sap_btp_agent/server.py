"""MCP stdio server: serve cac tool SAP BTP (sap_ping, sap_search, ...) qua JSON-RPC.

Day la phan transport con thieu truoc day -- `sap-btp-agent` goi khong co
subcommand (setup/connect/profiles/reset) se chay server nay, dung cho
`claude mcp add --transport stdio sap-btp -- sap-btp-agent`.
"""
from __future__ import annotations

import asyncio
import sys

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from .tools.registry import build_tools


def _build_server() -> Server:
    tools = build_tools()
    tools_by_name = {t["name"]: t for t in tools}

    server: Server = Server("sap-btp-agent")

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


async def _start_keep_alive_for_active_profile():
    """Giu session song cho profile dang active - CHI voi cookie auth (OAuth2/
    password/bearer da tu refresh token khi het han qua get_access_token(),
    khong bi anh huong boi idle timeout theo kieu nay). Port tu vibing-
    steampunk (xem SapClient.start_keep_alive). Loi gi cung KHONG duoc lam
    server chet - server van phai chay duoc du keep-alive that bai.
    """
    try:
        from .config.profile import get_current_active
        from .config.store import load_config
        from .sap.client import SapClient

        pid = get_current_active()
        if not pid:
            return None
        cfg = load_config(pid)
        if cfg.get("authMode") != "cookie":
            return None

        client = SapClient(pid)
        await client.init()
        client.start_keep_alive(300)  # 5 phut - xem ghi chu trong start_keep_alive
        print(f"[KEEPALIVE] Bat cho profile '{pid}' (moi 5 phut)", file=sys.stderr)
        return client
    except Exception as err:
        print(f"[KEEPALIVE] Khong bat duoc (bo qua, khong anh huong server): {err}", file=sys.stderr)
        return None


async def run_stdio() -> None:
    server = _build_server()
    keep_alive_client = await _start_keep_alive_for_active_profile()
    print("SAP BTP Agent MCP server (stdio) dang chay... (Ctrl+C de dung)", file=sys.stderr)
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    finally:
        if keep_alive_client:
            keep_alive_client.stop_keep_alive()


def main() -> None:
    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
