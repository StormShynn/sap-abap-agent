#!/usr/bin/env python3
"""Register all MCP servers documented by sap-abap-agent in one command.

Usage:
    python reference/scripts/mcp_register.py          # registration tuong tac
    python reference/scripts/mcp_register.py --apply  # auto-register (khong hoi rieng le)
    python reference/scripts/mcp_register.py --json   # chi sinh .mcp.json, khong chay claude mcp add

Server duoc chia 3 nhom:
  - auto:   co the register ngay, khong hoi - gom core + remote SSE (docs-remote) va dev-tool
            (vd chrome-devtools: khong can credential, tool dung chung khong SAP-specific -
            quyet dinh cua nguoi dung san pham: uu tien "cai het, khong bo sot" hon la hoi
            tung nguoi mot lan nua; chrome-devtools van KHONG duoc bundle vao .mcp.json dung
            chung git-tracked, chi auto-register per-user qua `claude mcp add --scope user`
            khi ho thuc su chay script/`/sap-setup` nay)
  - prompt: hoi Y/n truoc khi chay - chi con adt-alternative (SAP Official/ARC-1/mcp-abap-adt/
            mcp-abap-adt-dict la cac lua chon THAY THE nhau, khong co mac dinh dung nhat)
  - manual: can clone repo / cai dat them (notes, sf-mcp, cdata)

Script nay ghi vao 3 noi KHAC NHAU (khong noi nao thay the noi kia - thieu 1 la
user thay MCP "bien mat" o dung tool do):
  1. .mcp.json (project scope, git-tracked, dung chung ca team) - core+docs-remote
  2. ~/.claude.json mcpServers (Claude Code CLI, user scope) - qua `claude mcp add`
     NEU co `claude` tren PATH, LUON ghi truc tiep them 1 lan nua nhu fallback (an
     toan/idempotent) - can neu `claude` khong co tren PATH cua shell dang chay
     script (vd goi tu Claude Code VSCode extension qua Bash tool)
  3. claude_desktop_config.json (app Claude Desktop rieng, HOAN TOAN KHAC Claude
     Code CLI/.mcp.json - `claude mcp add` KHONG BAO GIO cham toi file nay)
"""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp_common import USER_CLAUDE_JSON, claude_desktop_config_path, load_inventory

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


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(path.name + f".bak-{ts}")
    backup.write_bytes(path.read_bytes())
    return backup


def merge_mcp_servers_into_json_file(
    path: Path, servers_to_add: dict[str, Any], *, create_dir_if_missing: bool
) -> str:
    """Doc 1 file config JSON dang co (`~/.claude.json` hoac
    claude_desktop_config.json), CHI them/cap nhat key "mcpServers" cho cac
    server cua plugin nay - giu nguyen 100% moi key/server khac (session,
    project khac, MCP server cua tool khac...). Backup truoc khi ghi (file
    nay co the rat quan trong/lon). Tra ve 1 dong status de in ra."""
    if not path.parent.exists():
        if not create_dir_if_missing:
            return "skip-no-dir"
        path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Any] = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            return f"error-khong-doc-duoc-file-cu: {err}"
        backup_file(path)

    if not isinstance(existing.get("mcpServers"), dict):
        existing["mcpServers"] = {}

    added: list[str] = []
    updated: list[str] = []
    for name, cfg in servers_to_add.items():
        if existing["mcpServers"].get(name) == cfg:
            continue
        if name in existing["mcpServers"]:
            updated.append(name)
        else:
            added.append(name)
        existing["mcpServers"][name] = cfg

    if not added and not updated:
        return "khong doi (da dung tu truoc)"

    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    parts = []
    if added:
        parts.append(f"+{len(added)} moi ({', '.join(added)})")
    if updated:
        parts.append(f"~{len(updated)} cap nhat ({', '.join(updated)})")
    return "OK: " + ", ".join(parts)


def safe_input(prompt: str, default: str = "") -> str:
    """input() wrapper: khong crash EOFError khi stdin non-interactive
    (vd Claude Code VSCode extension chay lenh nay qua Bash tool, khong co
    TTY thuc). Tra ve default (thuong la rong/skip) neu EOF."""
    try:
        return input(prompt).strip()
    except EOFError:
        print(f"{prompt}[non-interactive, dung default: {default or '(bo qua)'}]")
        return default


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
        val = safe_input(f"{prompt_text}: ", default)
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
            val = safe_input(f"    {var}: ")
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
    # het moi nguoi cai plugin nay - ke ca ai CHUA tung chay /sap-setup hay
    # script nay. adt-alternative la cac lua chon THAY THE nhau (khong nen
    # bundle ca 3 cung luc), product-specific co the can credential rieng
    # tung nguoi (vd ADT_USER/ADT_PASS) - khong duoc bake vao file dung
    # chung, du la placeholder rong hay gia tri that. dev-tool (chrome-
    # devtools) tu 2026-08 duoc auto-register KHONG hoi nua (xem
    # auto_categories o duoi) nhung van KHONG bundle vao .mcp.json chung o
    # day - dang ky per-user qua `claude mcp add --scope user` khi ho THUC
    # SU chay script/`/sap-setup`, khong tu bat cho nguoi chi clone repo ma
    # chua chay gi.
    print("\n--- Generating .mcp.json (core + docs-remote only) ---")
    mcp_config: dict[str, Any] = {"mcpServers": {}}
    bundled_categories = {"core", "docs-remote"}
    for entry in servers:
        if entry["category"] not in bundled_categories:
            continue
        cfg = build_mcp_json_entry(entry)
        if cfg:
            mcp_config["mcpServers"][entry["name"]] = cfg
    # Luon ghi .mcp.json (khong chi khi co --json/--apply): day la fallback
    # bat buoc phai co khi `claude` CLI khong nam tren PATH cua shell dang
    # chay script nay (vd Claude Code VSCode extension goi qua Bash tool -
    # khong co `claude` binary trong subshell), luc do `claude mcp add` cua
    # register_auto() se tra ve "skip" cho MOI server stdio, ke ca sap-connect
    # (server lõi) - .mcp.json la duong duy nhat con lai de Claude Code nhan
    # server o project scope sau khi khoi dong lai.
    MCP_JSON_PATH.write_text(
        json.dumps(mcp_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  Wrote {MCP_JSON_PATH} with {len(mcp_config['mcpServers'])} servers")
    if not claude_available():
        print(
            "  WARN  Khong tim thay `claude` CLI tren PATH cua shell nay -> "
            "cac buoc `claude mcp add` (auto/prompt) o duoi se bi SKIP. "
            ".mcp.json da ghi o tren van du de Claude Code nhan server "
            "core/docs-remote (project scope) sau khi khoi dong lai. Nhung "
            "adt-alternative/dev-tool/product-specific (khong nam trong "
            ".mcp.json) se can chay lai script nay tu mot terminal co "
            "`claude` tren PATH, hoac `claude mcp add` thu cong."
        )

    if args.json:
        print("\nDone (--json mode). Run `claude mcp add` manually to register.")
        return 0

    # --- Dong bo truc tiep vao ~/.claude.json (Claude Code, user scope) va
    # claude_desktop_config.json (app Claude Desktop rieng, KHAC Claude Code) ---
    # QUAN TRONG: 2 file nay dung 2 TAP category KHAC NHAU, khong phai giong
    # personal_categories chung:
    #   - ~/.claude.json (user scope): CHI dev-tool (chrome-devtools). core +
    #     docs-remote KHONG duoc ghi lai o day vi da co trong .mcp.json
    #     (project scope) roi - ghi ca 2 noi se khien mcp_status.py bao "!!
    #     defined in: user, project - may conflict" (da kiem chung thuc te
    #     2026-08-03: ghi ca 2 lam mcp_status.py tu bao conflict cho chinh
    #     5 server nay). dev-tool la ngoai le vi KHONG nam trong .mcp.json
    #     (xem bundled_categories o tren), nen day la noi DUY NHAT client
    #     Claude Code CLI co the thay chrome-devtools neu `claude` CLI thieu.
    #   - claude_desktop_config.json: CA core + docs-remote + dev-tool, vi
    #     Claude Desktop la app hoan toan tach biet, KHONG doc .mcp.json hay
    #     ~/.claude.json - day la NOI DUY NHAT no co the thay bat ky server
    #     nao trong 3 nhom nay, khong co "da co o cho khac" de lo ngai trung.
    user_scope_config: dict[str, Any] = {}
    desktop_config: dict[str, Any] = {}
    for entry in servers:
        cfg = build_mcp_json_entry(entry)
        if not cfg:
            continue
        if entry["category"] == "dev-tool":
            user_scope_config[entry["name"]] = cfg
        if entry["category"] in {"core", "docs-remote", "dev-tool"}:
            desktop_config[entry["name"]] = cfg

    print("\n--- Dong bo truc tiep vao Claude Code (user scope) + Claude Desktop ---")
    user_status = merge_mcp_servers_into_json_file(
        USER_CLAUDE_JSON, user_scope_config, create_dir_if_missing=False
    )
    print(f"  {USER_CLAUDE_JSON} (Claude Code CLI, user scope, chi dev-tool): {user_status}")

    desktop_path = claude_desktop_config_path()
    if desktop_path is None:
        print(
            "  Claude Desktop: khong xac dinh duoc thu muc config tren OS nay "
            "(chi ho tro Windows/macOS) - bo qua"
        )
    else:
        desktop_status = merge_mcp_servers_into_json_file(
            desktop_path, desktop_config, create_dir_if_missing=False
        )
        if desktop_status == "skip-no-dir":
            print(
                f"  Claude Desktop ({desktop_path.parent} khong ton tai): co "
                "the ban chua cai Claude Desktop tren may nay - bo qua, khong "
                "tu tao thu muc cho app chua cai. Cai Claude Desktop roi chay "
                "lai lenh nay se tu dong bo server vao do."
            )
        else:
            print(f"  {desktop_path} (Claude Desktop): {desktop_status}")

    # --- Register tung nhom ---
    print("\n--- Registering MCP Servers ---")

    results: dict[str, str] = {}

    # Nhom auto: core + docs-remote + dev-tool (chrome-devtools khong can credential va
    # theo quyet dinh cua nguoi dung san pham la khong hoi rieng nua - van KHONG bundle vao
    # .mcp.json dung chung, xem bundled_categories o tren)
    auto_categories = {"core", "docs-remote", "dev-tool"}
    for cat in auto_categories:
        for entry in groups.get(cat, []):
            name = entry["name"]
            status = register_auto(entry, registered)
            results[name] = status
            print(f"  [{status.upper():>10}] {name}")

    # Nhom prompt: chi con adt-alternative (lua chon thay the nhau, khong co mac dinh dung nhat)
    for cat in ("adt-alternative",):
        for entry in groups.get(cat, []):
            name = entry["name"]
            if name in registered:
                results[name] = "registered"
                print(f"  [ REGISTERED] {name}")
                continue
            if args.apply:
                status = register_auto(entry, registered | set(results.keys()))
            else:
                yn = safe_input(
                    f"\n  Register {name} ({entry['description']})? [Y/n] ", "n"
                ).lower()
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
