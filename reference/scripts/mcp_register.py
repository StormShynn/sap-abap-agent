#!/usr/bin/env python3
"""Register all MCP servers documented by sap-abap-agent in one command.

Usage:
    python reference/scripts/mcp_register.py          # registration tuong tac
    python reference/scripts/mcp_register.py --apply  # auto-register (khong hoi rieng le)
    python reference/scripts/mcp_register.py --json   # chi sinh .mcp.json, khong chay claude mcp add

Server duoc chia 3 nhom:
  - auto:   co the register ngay (core + remote SSE)
  - prompt: hoi Y/n truoc khi chay (npx/uvx mot dong, khong can credential rieng) - gom
            adt-alternative (cac lua chon ADT thay the nhau) va dev-tool (tool dung chung
            khong SAP-specific, vd chrome-devtools - van hoi truoc du khong can credential,
            vi la nang luc dieu khien that (browser...), khong nen tu dong bat)
  - manual: can clone repo / cai dat them (notes, sf-mcp, cdata)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp_common import load_inventory

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MCP_JSON_PATH = PROJECT_ROOT / ".mcp.json"


def group_servers(servers: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for s in servers:
        groups.setdefault(s["category"], []).append(s)
    return groups


def get_registered_servers() -> set[str]:
    """Doc cac server da register tu ~/.claude.json va .mcp.json (neu co)."""
    registered: set[str] = set()
    paths = [Path.home() / ".claude.json", MCP_JSON_PATH]
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                servers = data.get("mcpServers", {}) or {}
                if isinstance(servers, dict):
                    registered.update(servers.keys())
            except (OSError, json.JSONDecodeError):
                pass
    return registered


def claude_available() -> bool:
    return shutil.which("claude") is not None


def run_claude_add(
    name: str,
    transport: str,
    *,
    url: str | None = None,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    scope: str = "user",
) -> bool:
    if not claude_available():
        return False
    # Real syntax (verified via `claude mcp add --help`): `claude mcp add
    # [options] <name> <commandOrUrl> [args...]` - <name> is always
    # positional (there is no --name flag), there is no --url flag (the URL
    # is <commandOrUrl>), and -e/--env must come BEFORE the `--` separator -
    # after it, it would be passed as a literal arg to the subprocess itself.
    cmd = ["claude", "mcp", "add", "--transport", transport, "--scope", scope, name]

    if env:
        # Filter out empty env vars to avoid invalid format errors
        for k, v in env.items():
            if v:  # Only add non-empty env vars
                cmd.extend(["--env", f"{k}={v}"])

    if transport in ("sse", "http", "ws"):
        if url:
            cmd.append(url)
    elif command:
        cmd.append("--")
        cmd.append(command)
        if args:
            cmd.extend(args)
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def build_mcp_json_entry(entry: dict) -> dict | None:
    """Sinh cau hinh .mcp.json cho 1 server."""
    transport = entry["transport"]
    cfg = entry.get("config", {})
    if transport in ("sse", "http", "ws"):
        url = cfg.get("url") or entry.get("url")
        if not url:
            return None
        return {"type": transport, "url": url}
    command = cfg.get("command", "").strip()
    if not command:
        return None
    result: dict[str, Any] = {"type": "stdio", "command": command}
    args = cfg.get("args")
    if args:
        result["args"] = list(args)
    env = cfg.get("env", {})
    if env:
        result["env"] = env
    return result


def prompt_env_vars(entry: dict) -> dict[str, str]:
    """Hoi user nhap env var neu can."""
    env_result: dict[str, str] = {}
    needed = entry.get("envVars", [])
    if not needed:
        return env_result
    cfg = entry.get("config", {})
    existing_env = cfg.get("env", {})
    name = entry["name"]
    print(f"\n  === {name}: can cau hinh env vars ===")
    for var in needed:
        default = existing_env.get(var, "")
        prompt_text = f"    {var}"
        if default:
            prompt_text += f" (default: {default[:20]}{'...' if len(default) > 20 else ''})"
        val = input(f"{prompt_text}: ").strip()
        if not val and default:
            val = default
        if val:
            env_result[var] = val
    return env_result


def register_auto(entry: dict, registered: set[str]) -> str:
    """Tu dong register server core + remote SSE."""
    name = entry["name"]
    if name in registered:
        return "registered"

    cfg = entry.get("config", {})
    transport = entry["transport"]

    if transport in ("sse", "http", "ws"):
        url = cfg.get("url") or entry.get("url", "")
        if claude_available():
            ok = run_claude_add(name, transport, url=url)
            return "ok" if ok else "error"
        return "skip"

    command = cfg.get("command", "")
    args = cfg.get("args")
    env = cfg.get("env", {})
    if claude_available():
        ok = run_claude_add(
            name, transport, command=command, args=args, env=env if env else None
        )
        return "ok" if ok else "error"
    return "skip"


def register_prompt(entry: dict, registered: set[str]) -> str:
    """Register server can hoi env vars."""
    name = entry["name"]
    if name in registered:
        return "registered"

    cfg = entry.get("config", {})
    transport = entry["transport"]
    command = cfg.get("command", "")
    args = cfg.get("args")

    env = prompt_env_vars(entry)
    if claude_available():
        ok = run_claude_add(name, transport, command=command, args=args, env=env if env else None)
        return "ok" if ok else "error"
    return "skip"


def register_manual(entry: dict) -> str:
    """Khong the auto-register, chi huong dan."""
    return "manual"


def ensure_env_files(skip_env: bool = False) -> dict[str, str]:
    """Kiem tra / tao env files cho CData servers."""
    env_dir = PROJECT_ROOT / ".env"
    env_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}

    cdata_servers = {
        "sf-cdata": {
            "file": "sap-successfactors.prp",
            "vars": ["Connection.ConnectionString", "User"],
        },
        "sap-concur": {
            "file": "sap-concur.prp",
            "vars": ["Connection.ConnectionString", "User"],
        },
        "sap-fieldglass": {
            "file": "sap-fieldglass.prp",
            "vars": ["Connection.ConnectionString", "User"],
        },
    }

    for srv, info in cdata_servers.items():
        fpath = env_dir / info["file"]
        if fpath.exists():
            results[srv] = "env_ok"
            continue
        if skip_env:
            results[srv] = "env_skip"
            continue
        print(f"\n  === {srv}: tao file cau hinh ===")
        print(f"  File: {fpath}")
        lines = []
        for var in info["vars"]:
            val = input(f"    {var}: ").strip()
            if val:
                lines.append(f"{var}={val}")
        if lines:
            fpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
            results[srv] = "env_created"
        else:
            results[srv] = "env_skip"
    return results


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Register all MCP servers for sap-abap-agent"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply ngay (khong hoi, dung config mac dinh)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Chi sinh .mcp.json, khong chay claude mcp add",
    )
    parser.add_argument(
        "--skip-env",
        action="store_true",
        help="Khong hoi tao env files",
    )
    args = parser.parse_args()

    servers = load_inventory()
    groups = group_servers(servers)

    print("=" * 72)
    print("  sap-abap-agent — MCP Server Unified Setup")
    print(f"  Project: {PROJECT_ROOT}")
    print("=" * 72)

    registered = get_registered_servers()

    # --- Xay dung .mcp.json ---
    # CHI core + docs-remote: day la file se commit vao git, dung chung cho
    # het moi nguoi cai plugin nay. adt-alternative la cac lua chon THAY THE
    # nhau (khong nen bundle ca 3 cung luc), product-specific co the can
    # credential rieng tung nguoi (vd ADT_USER/ADT_PASS) - khong duoc bake vao
    # file dung chung, du la placeholder rong hay gia tri that. dev-tool (vd
    # chrome-devtools) khong can credential nhung van KHONG bundle - day la
    # nang luc dieu khien that (browser...), phai la lua chon tu nguyen cua
    # tung nguoi dung, khong nen tu dong bat cho moi nguoi cai plugin.
    print("\n--- Generating .mcp.json (core + docs-remote only) ---")
    mcp_config: dict[str, Any] = {"mcpServers": {}}
    bundled_categories = {"core", "docs-remote"}
    for entry in servers:
        if entry["category"] not in bundled_categories:
            continue
        cfg = build_mcp_json_entry(entry)
        if cfg:
            mcp_config["mcpServers"][entry["name"]] = cfg
    if args.json or args.apply:
        MCP_JSON_PATH.write_text(
            json.dumps(mcp_config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  Wrote {MCP_JSON_PATH} with {len(mcp_config['mcpServers'])} servers")

    if args.json:
        print("\nDone (--json mode). Run `claude mcp add` manually to register.")
        return 0

    # --- Register tung nhom ---
    print("\n--- Registering MCP Servers ---")

    results: dict[str, str] = {}

    # Nhom auto: core + docs-remote
    auto_categories = {"core", "docs-remote"}
    for cat in auto_categories:
        for entry in groups.get(cat, []):
            name = entry["name"]
            status = register_auto(entry, registered)
            results[name] = status
            print(f"  [{status.upper():>10}] {name}")

    # Nhom prompt: adt-alternative (lua chon thay the nhau) + dev-tool (tool dung chung,
    # khong can credential nhung van hoi truoc vi la nang luc dieu khien that)
    for cat in ("adt-alternative", "dev-tool"):
        for entry in groups.get(cat, []):
            name = entry["name"]
            if name in registered:
                results[name] = "registered"
                print(f"  [ REGISTERED] {name}")
                continue
            if args.apply:
                status = register_auto(entry, registered | set(results.keys()))
            else:
                yn = input(f"\n  Register {name} ({entry['description']})? [Y/n] ").strip().lower()
                if yn in ("", "y", "yes"):
                    status = register_prompt(entry, registered | set(results.keys()))
                else:
                    status = "skipped"
            results[name] = status
            print(f"  [{status.upper():>10}] {name}")

    # Nhom manual: product-specific
    print("\n--- Product-specific servers (manual setup required) ---")
    for entry in groups.get("product-specific", []):
        name = entry["name"]
        cfg = entry.get("config", {})
        desc = entry["description"]
        install_hint = cfg.get("install_hint", "See skill doc for install instructions")
        results[name] = "manual"
        print(f"\n  [{name}] {desc}")
        print(f"    {install_hint}")

    # Env files cho CData
    env_results = ensure_env_files(args.skip_env)
    results.update(env_results)

    # --- Summary ---
    print("\n" + "=" * 72)
    print("  Summary")
    print("=" * 72)
    for name, status in sorted(results.items()):
        print(f"  [{status.upper():>12}] {name}")

    ok_count = sum(1 for s in results.values() if s in ("ok", "registered", "env_ok", "env_created"))
    manual_count = sum(1 for s in results.values() if s == "manual")
    skipped_count = sum(1 for s in results.values() if s in ("skipped", "env_skip"))
    error_count = sum(1 for s in results.values() if s == "error")

    print(f"\n  {ok_count} registered, {manual_count} manual, {skipped_count} skipped, {error_count} errors")
    print("\n  Sau khi register xong, khoi dong lai Claude Code de nhan server moi.")
    print("  Kiem tra bang: python reference/scripts/mcp_status.py")
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
