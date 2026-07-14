#!/usr/bin/env python3
"""Audit MCP servers documented by the sap-abap-agent plugin against what is
actually registered in Claude Code, for the current project.

Read-only: never writes any file, never runs `claude mcp add/remove`, never
prints a secret value (only whether an expected env var / header key is
present, never its value).

    python reference/scripts/mcp_status.py

Scope this script CAN see:
  - user scope:    ~/.claude.json -> top-level "mcpServers"
  - local scope:   ~/.claude.json -> projects[<this project>].mcpServers
  - project scope: <project-root>/.mcp.json, cross-referenced with
                    projects[<this project>].enabledMcpjsonServers /
                    disabledMcpjsonServers for approval state
                    (this also doubles as the plugin's own bundled servers
                    when this repo IS the plugin root, e.g. during dev)

Known blind spots (not an error - just not checkable from a script):
  - MCP servers provided by a DIFFERENT plugin (lifecycle = `claude plugin
    enable/disable`, declared in that plugin's own .claude-plugin/plugin.json
    or its own .mcp.json). Check with `claude plugin list` / `claude mcp list`.
  - VS Code-extension-registered servers (e.g. the bundled sap-btp-mcp .vsix
    under reference/.vscode-extensions/) - these register themselves live
    inside VS Code's process; there is no static config file to read.

See also: mcp_register.py (registers the servers this script reports as
"not registered", where that's actually automatable).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp_common import load_inventory, load_live_config


def _config_issues(cfg: dict[str, Any], expected_env: list[str]) -> list[str]:
    """Structural checks only - never returns/prints an actual secret value."""
    issues = []
    if "url" in cfg and "type" not in cfg:
        issues.append(
            'has "url" but no "type" -> Claude Code will skip this server '
            '(add "type": "http" / "sse" / "ws")'
        )
    env = cfg.get("env", {}) or {}
    for var in expected_env:
        if var not in env:
            issues.append(f'missing expected env var "{var}"')
    return issues


def build_report(project_root: Path) -> int:
    inventory = load_inventory()
    live = load_live_config(project_root)

    scopes = {"user": live["user"], "local": live["local"], "project": live["project"]}
    matched_names: set[str] = set()

    categories: dict[str, list[dict[str, Any]]] = {}
    for entry in inventory:
        categories.setdefault(entry["category"], []).append(entry)

    print("=" * 72)
    print("  sap-abap-agent - MCP server status (read-only report)")
    print(f"  project: {project_root}")
    print("=" * 72)

    for category, entries in categories.items():
        print(f"\n[{category}]")
        for entry in entries:
            name = entry["name"]
            found_scope = None
            found_cfg = None
            for scope, servers in scopes.items():
                if name in servers:
                    found_scope, found_cfg = scope, servers[name]
                    matched_names.add(name)
                    break

            if found_cfg is None:
                print(f"  -     {name:<20} not registered   ({entry['description']})")
                continue

            issues = _config_issues(found_cfg, entry.get("envVars", []))
            approval = ""
            if found_scope == "project":
                if name in live["project_disabled"]:
                    approval = "  [REJECTED - run: claude mcp reset-project-choices]"
                elif name not in live["project_enabled"]:
                    approval = "  [likely PENDING approval - will prompt next session]"

            if issues:
                print(f"  WARN  {name:<20} {found_scope} scope - {'; '.join(issues)}{approval}")
            else:
                print(f"  OK    {name:<20} {found_scope} scope{approval}")

    orphans = [
        (scope, name, servers[name])
        for scope, servers in scopes.items()
        for name in servers
        if name not in matched_names
    ]
    if orphans:
        print("\n[unknown to sap-abap-agent docs - verify manually, not auto-flagged as a problem]")
        for scope, name, cfg in orphans:
            note = "not documented by any sap-abap-agent skill/README"
            issues = _config_issues(cfg, [])
            if issues:
                note += "; " + "; ".join(issues)
            print(f"  ?     {name:<20} {scope} scope - {note}")

    scope_hits: dict[str, list[str]] = {}
    for scope, servers in scopes.items():
        for name in servers:
            scope_hits.setdefault(name, []).append(scope)
    duplicates = {name: sc for name, sc in scope_hits.items() if len(sc) > 1}
    if duplicates:
        print("\n[same name registered in more than one scope - may conflict]")
        for name, sc in duplicates.items():
            print(f"  !!    {name:<20} defined in: {', '.join(sc)} - remove the redundant one")

    print("\n" + "-" * 72)
    print("Not covered by this script (check separately):")
    print("  - servers from a DIFFERENT plugin (e.g. hana-cli) -> claude plugin list / claude mcp list")
    print("  - VS Code-extension-registered servers            -> VS Code Chat: type @mcp")
    print("Use mcp_register.py to register what's actually automatable from 'not registered' above.")
    print("No per-server enable/disable here (Claude Code CLI doesn't have one either) - for a cross-tool")
    print("toggle UI (Claude Code/Desktop, Codex, Gemini CLI...), see https://github.com/StormShynn/mcp-switch")
    print("-" * 72)
    return 0


def main() -> int:
    return build_report(Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
