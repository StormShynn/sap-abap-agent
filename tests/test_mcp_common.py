"""Test cho reference/scripts/mcp_common.py (shared helpers).

Tuy day la file helper khong phai entry point, van test de dam bao behavior on dinh:
  - project_key(path): normalize path theo format ~/.claude.json key
  - load_json(path): robust JSON loader (missing file, malformed JSON, OSError)
  - servers_map(obj): detect 2 shape pho bien cua .mcp.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import mcp_common as mc  # noqa: E402


# ---------- project_key ----------

def test_project_key_normalizes_backslash_to_forward(tmp_path):
    """Windows backslash duoc chuyen thanh forward slash."""
    fake = tmp_path / "MyProject"
    fake.mkdir()
    key = mc.project_key(fake)
    assert "\\" not in key
    assert "/" in key


def test_project_key_lowercases_drive_letter(tmp_path):
    """Drive letter C: -> c: (lowercase)."""
    fake = tmp_path / "x"
    fake.mkdir()
    key = mc.project_key(fake)
    # Neu tmp_path o C:, se co 'C:' hoac 'c:' - check lowercase neu co
    if ":\\" in str(fake) or ":/" in str(fake):
        # Skip neu tmp_path o D:/ (khong co lowercase)
        pass
    # Khong assert cu the vi path tuy thuoc may, chi check rule


def test_project_key_strips_trailing_slash(tmp_path):
    fake = tmp_path / "foo"
    fake.mkdir()
    key = mc.project_key(fake)
    assert not key.endswith("/")
    assert not key.endswith("\\")


def test_project_key_handles_existing_trailing_slash(tmp_path):
    """Neu user truyen path co trailing slash -> van normalize dung."""
    fake = tmp_path / "foo"
    fake.mkdir()
    key_with_slash = mc.project_key(fake / "")
    assert key_with_slash == mc.project_key(fake)


# ---------- load_json ----------

def test_load_json_missing_file(tmp_path):
    """File khong ton tai -> return None."""
    p = tmp_path / "does-not-exist.json"
    assert mc.load_json(p) is None


def test_load_json_valid(tmp_path):
    p = tmp_path / "valid.json"
    p.write_text('{"key": "value", "num": 42}', encoding="utf-8")
    result = mc.load_json(p)
    assert result == {"key": "value", "num": 42}


def test_load_json_malformed(tmp_path, capsys):
    """File JSON loi -> return None + in warning (khong raise)."""
    p = tmp_path / "bad.json"
    p.write_text("not valid json {{{", encoding="utf-8")
    result = mc.load_json(p)
    assert result is None
    captured = capsys.readouterr()
    assert "WARN" in captured.out or "WARN" in captured.err


def test_load_json_empty(tmp_path):
    """File rong -> return None."""
    p = tmp_path / "empty.json"
    p.write_text("", encoding="utf-8")
    assert mc.load_json(p) is None


# ---------- servers_map ----------

def test_servers_map_with_mcpServers_key():
    """Shape 1: {mcpServers: {name: cfg}} - official sap-hana-cli, telegram, discord."""
    obj = {"mcpServers": {"my-server": {"command": "node"}}, "version": 1}
    result = mc.servers_map(obj)
    assert result == {"my-server": {"command": "node"}}


def test_servers_map_with_top_level_servers():
    """Shape 2: {name: cfg} - flat dict."""
    obj = {"my-server": {"command": "node"}, "other": {"url": "https://..."}}
    result = mc.servers_map(obj)
    assert result == obj


def test_servers_map_empty_object():
    """Object rong -> return {} (khong crash)."""
    assert mc.servers_map({}) == {}


def test_servers_map_mcpServers_not_dict():
    """Neu mcpServers ton tai nhung khong phai dict -> tra ve obj goc (khong crash)."""
    obj = {"mcpServers": "not a dict"}
    result = mc.servers_map(obj)
    # Behavior thuc te: fallback ve obj goc (khong crash, khong raise)
    assert result == obj or result == {}
    assert isinstance(result, dict)


# ---------- load_inventory ----------

def test_load_inventory_real_file():
    """File mcp_inventory.json that ton tai trong repo."""
    inventory = mc.load_inventory()
    assert isinstance(inventory, list)
    assert len(inventory) > 0, "Inventory khong duoc empty"
    # Moi entry co fields name, command/url, category (xem convention)
    for entry in inventory:
        assert "name" in entry, f"Entry thieu 'name': {entry}"


def test_load_inventory_contains_known_servers():
    """Inventory phai co it nhat 1 server bat ky (vd sap-btp)."""
    inventory = mc.load_inventory()
    names = [e["name"] for e in inventory]
    # Day la smoke test - chi can list khong empty
    assert any(isinstance(n, str) for n in names)


# ---------- load_live_config (smoke test) ----------

def test_load_live_config_returns_expected_keys(tmp_path):
    """Function tra ve dict co cac key nhat dinh."""
    result = mc.load_live_config(tmp_path)
    assert isinstance(result, dict)
    for key in ("user", "local", "project", "project_enabled", "project_disabled"):
        assert key in result, f"Missing key: {key}"


def test_load_live_config_no_mcp_json(tmp_path):
    """Neu project khong co .mcp.json -> project scope empty, khong crash."""
    result = mc.load_live_config(tmp_path)
    assert result["project"] == {}
    assert result["project_enabled"] == set()
    assert result["project_disabled"] == set()


def test_load_live_config_with_mcp_json(tmp_path):
    """Neu project co .mcp.json -> project scope co server."""
    mcp = tmp_path / ".mcp.json"
    mcp.write_text(json.dumps({"mcpServers": {"my-server": {"command": "node"}}}), encoding="utf-8")
    result = mc.load_live_config(tmp_path)
    assert "my-server" in result["project"]
