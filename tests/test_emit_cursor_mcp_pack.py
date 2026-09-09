"""Tests for reference/scripts/emit_cursor_mcp_pack.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import emit_cursor_mcp_pack as emit  # noqa: E402


def test_build_core_has_kit_url_and_four_servers(monkeypatch):
    monkeypatch.delenv("SAP_API_HUB_KEY", raising=False)
    servers = emit.build_core_servers()
    assert set(servers) == set(emit.CORE_KEYS)
    assert servers["cds-kb"]["type"] == "http"
    assert servers["cds-kb"]["url"] == emit.CDS_KB_HTTP
    assert "env" not in servers["mcp-sap-docs-btp"]


def test_hub_key_added(monkeypatch):
    monkeypatch.setenv("SAP_API_HUB_KEY", "secret-hub")
    servers = emit.build_core_servers()
    assert servers["mcp-sap-docs-btp"]["env"]["SAP-API-HUB-KEY"] == "secret-hub"


def test_merge_preserves_other_servers():
    existing = {"other": {"command": "echo"}, "sap-connect": {"command": "old"}}
    core = emit.build_core_servers()
    merged = emit.merge_servers(existing, core)
    assert merged["other"]["command"] == "echo"
    assert merged["sap-connect"]["command"] == "mcp-sap-connect"


def test_cli_write(tmp_path, monkeypatch):
    monkeypatch.delenv("SAP_API_HUB_KEY", raising=False)
    out = tmp_path / "mcp.json"
    assert emit.main(["-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "sap-connect" in data["mcpServers"]
    assert "cds-kb" in data["mcpServers"]
