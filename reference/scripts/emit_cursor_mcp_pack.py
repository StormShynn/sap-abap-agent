#!/usr/bin/env python3
"""Emit Cursor/VS Code mcp.json for SAP ABAP Agent Core (docs-only host).

Core = sap-connect + sap-dict-bridge + cds-kb + mcp-sap-docs-btp (same contract as
CLI/GUI mcp-setup). Does NOT install Claude skills/hooks.

Usage:
  python emit_cursor_mcp_pack.py              # stdout
  python emit_cursor_mcp_pack.py -o path.json
  python emit_cursor_mcp_pack.py --merge-existing ~/.cursor/mcp.json -o ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CDS_KB_SSE = "https://cds-kb-mcp-kit-production.up.railway.app/sse"
SAP_DOCS_SSE = "https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse"
CORE_KEYS = ("sap-connect", "sap-dict-bridge", "cds-kb", "mcp-sap-docs-btp")


def build_core_servers() -> dict:
    docs_env: dict[str, str] = {}
    hub = os.environ.get("SAP_API_HUB_KEY", "").strip()
    if hub:
        docs_env["SAP-API-HUB-KEY"] = hub

    docs: dict = {
        "command": "npx",
        "args": ["-y", "supergateway@2.0.0", "--sse", SAP_DOCS_SSE],
    }
    if docs_env:
        docs["env"] = docs_env

    return {
        "sap-connect": {"command": "mcp-sap-connect", "args": []},
        "sap-dict-bridge": {
            "command": "python",
            "args": ["-m", "mcp_sap_connect.bridge_server"],
        },
        "cds-kb": {
            "command": "npx",
            "args": ["-y", "supergateway@2.0.0", "--sse", CDS_KB_SSE],
        },
        "mcp-sap-docs-btp": docs,
    }


def merge_servers(existing: dict, core: dict) -> dict:
    """Keep non-core keys from existing; overwrite Core keys with fresh pack."""
    out = dict(existing)
    for key in CORE_KEYS:
        out[key] = core[key]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write mcp.json here (default: stdout)",
    )
    parser.add_argument(
        "--merge-existing",
        type=Path,
        help="Merge Core into an existing mcp.json (preserve other servers)",
    )
    args = parser.parse_args(argv)

    core = build_core_servers()
    servers = core
    if args.merge_existing and args.merge_existing.is_file():
        try:
            data = json.loads(args.merge_existing.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            print(f"Invalid JSON in {args.merge_existing}: {err}", file=sys.stderr)
            return 2
        existing = data.get("mcpServers") or data.get("servers") or {}
        if not isinstance(existing, dict):
            print("Existing file has no mcpServers object", file=sys.stderr)
            return 2
        servers = merge_servers(existing, core)

    payload = {
        "_comment": (
            "SAP ABAP Agent Core — Cursor/VS Code docs-only. "
            "Skills/hooks remain Claude Code only."
        ),
        "mcpServers": servers,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(str(args.output))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
