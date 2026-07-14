"""Shared helpers for mcp_status.py / mcp_register.py: reading Claude Code's
live MCP config (user/local/project scope) and this plugin's own
mcp_inventory.json. Not a standalone entry point - nothing here prints or
mutates anything.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
INVENTORY_PATH = SCRIPT_DIR / "mcp_inventory.json"
USER_CLAUDE_JSON = Path.home() / ".claude.json"


def project_key(path: Path) -> str:
    """Normalize a path the way ~/.claude.json keys its "projects" map
    (lowercase drive letter, forward slashes, no trailing slash)."""
    s = str(path.resolve()).replace("\\", "/")
    if len(s) >= 2 and s[1] == ":":
        s = s[0].lower() + s[1:]
    return s.rstrip("/")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"WARN: could not read {path}: {err}")
        return None


def servers_map(obj: dict[str, Any]) -> dict[str, Any]:
    """A standalone .mcp.json is shaped either way in real plugins we checked:
      {"mcpServers": {name: config}}   (e.g. the official telegram/discord plugins)
      {name: config}                   (e.g. the official sap-hana-cli plugin)
    """
    if isinstance(obj.get("mcpServers"), dict):
        return obj["mcpServers"]
    return obj


def load_inventory() -> list[dict[str, Any]]:
    data = load_json(INVENTORY_PATH)
    if not data:
        raise SystemExit(f"FATAL: inventory file not found or empty: {INVENTORY_PATH}")
    return data["servers"]


def load_live_config(project_root: Path) -> dict[str, Any]:
    """Everything this script can see about MCP registration relevant to
    `project_root`: user scope, local scope (this project only, private),
    and project scope (checked-in .mcp.json, needs approval)."""
    user_cfg = load_json(USER_CLAUDE_JSON) or {}
    user_scope = user_cfg.get("mcpServers", {}) or {}

    project_entry = (user_cfg.get("projects", {}) or {}).get(project_key(project_root), {}) or {}
    local_scope = project_entry.get("mcpServers", {}) or {}
    enabled_project_servers = set(project_entry.get("enabledMcpjsonServers", []) or [])
    disabled_project_servers = set(project_entry.get("disabledMcpjsonServers", []) or [])

    project_json = load_json(project_root / ".mcp.json") or {}
    project_scope = servers_map(project_json)

    return {
        "user": user_scope,
        "local": local_scope,
        "project": project_scope,
        "project_enabled": enabled_project_servers,
        "project_disabled": disabled_project_servers,
    }
