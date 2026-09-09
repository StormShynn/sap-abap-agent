"""Notion remote MCP must appear in GUI inventory (not Core)."""
from __future__ import annotations

from mcp_sap_connect.cli import _MCP_JSON_INVENTORY


def test_notion_in_inventory_special_http():
    notion = next((e for e in _MCP_JSON_INVENTORY if e["name"] == "notion"), None)
    assert notion is not None, "notion missing from _MCP_JSON_INVENTORY"
    assert notion["category"] == "special"
    assert notion["transport"] == "http"
    assert notion["url"] == "https://mcp.notion.com/mcp"
    assert notion["name"] not in {"sap-connect", "sap-dict-bridge", "cds-kb", "mcp-sap-docs-btp"}


def test_notion_not_listed_as_core_server_name():
    core_names = {e["name"] for e in _MCP_JSON_INVENTORY if e["category"] == "core"}
    assert "notion" not in core_names
