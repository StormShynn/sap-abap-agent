"""CLI entry point: sap-btp-agent setup / connect / profiles / reset.

Usage:
  sap-btp-agent                              Chay MCP stdio server (khong argument)
  sap-btp-agent setup https://xxx.s4hana.cloud.sap
  sap-btp-agent connect [profile-id]
  sap-btp-agent profiles list|use|show|remove <id>
  sap-btp-agent reset
  sap-btp-agent --help
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any

from ..sap.auth import _parse_cookie_string
from ..config.profile import (
    derive_profile_id_from_url,
    get_current_active,
    list_profiles,
    remove_profile,
    reset_all,
    set_active_profile,
    upsert_profile,
)
from ..config.secrets import save_secrets
from ..config.store import save_config
from .prompt import ask, header, info, ok, warn


def main() -> None:
    """Entry point: sap-btp-agent <command> [args...]

    Khong co argument -> chay MCP stdio server (dung khi Claude Code/Desktop
    spawn qua `claude mcp add ... -- sap-btp-agent`). Co argument -> CLI thuong.
    """
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    if not args:
        from ..server import main as run_mcp_server
        run_mcp_server()
        return
    if args[0] in ("--help", "-h"):
        _show_help()
        return

    cmd = args[0]
    cmd_args = args[1:]

    if cmd == "setup":
        url = cmd_args[0] if cmd_args else ""
        asyncio.run(_wizard_setup(url))
    elif cmd == "connect":
        asyncio.run(_cmd_connect(cmd_args[0] if cmd_args else None))
    elif cmd == "profiles" and cmd_args:
        asyncio.run(_cmd_profiles(cmd_args[0], cmd_args[1] if len(cmd_args) > 1 else None))
    elif cmd == "reset":
        _cmd_reset()
    elif cmd == "doctor":
        from ..doctor import main as run_doctor
        run_doctor()
    else:
        print(f"  ❌ Unknown command: {cmd}")
        _show_help()


def _show_help() -> None:
    print()
    print("  SAP ABAP Agent — CLI Tool (v0.9.3)")
    print("=" * 50)
    print()
    print("  Commands:")
    print("    setup [URL]            Thêm project SAP mới (wizard)")
    print("    connect [profile-id]   Test kết nối profile")
    print("    profiles list          Liệt kê tất cả profile")
    print("    profiles use <id>      Chọn profile active")
    print("    profiles show          Xem chi tiết profile active")
    print("    profiles remove <id>   Xóa một profile")
    print("    reset                  Xóa TẤT CẢ dữ liệu (cẩn thận!)")
    print("    doctor                 Kiểm tra môi trường (PATH, dependency...)")
    print()
    print("  (Khong argument = chay MCP stdio server, dung cho claude mcp add)")
    print()
    print("  Examples:")
    print("    sap-btp-agent setup https://xxx.s4hana.cloud.sap")
    print("    sap-btp-agent connect")
    print("    sap-btp-agent profiles list")
    print("    sap-btp-agent doctor")
    print()
    print("  Neu 'sap-btp-agent' khong duoc nhan dien (not recognized), chay:")
    print("    python -m sap_btp_agent.doctor")
    print()


# ===== SETUP WIZARD ================================================

async def _wizard_setup(url: str) -> None:
    header("SAP ABAP Agent — Setup Wizard")

    # --- URL ---
    if not url:
        url = ask("Nhap URL SAP BTP / S/4HANA Cloud",
                  default="https://xxx.s4hana.cloud.sap")
    if not url:
        print("  ❌ Khong co URL. Huy.")
        return

    profile_id = derive_profile_id_from_url(url)
    if not profile_id:
        profile_id = ask("Khong the sinh ID tu URL. Nhap profile ID manually",
                         default="my-sap-project")
    info(f"Profile ID: {profile_id}")

    # --- Auth Mode ---
    header("Chon phuong thuc xac thuc")
    print("  1. OAuth2 (client_credentials)  — Mac dinh, M2M, khuyen dung")
    print("  2. Password (username/password) — Dang nhap bang tai khoan SAP")
    print("  3. Bearer token                 — Token co san (nhap tay)")
    print("  4. Cookie-based                 — SAP session cookies + web popup re-auth")

    auth_choice = ask("Chon (1-4)", default="4")
    auth_modes = {"1": "oauth2", "2": "password", "3": "bearer", "4": "cookie"}
    auth_mode = auth_modes.get(auth_choice, "oauth2")
    info(f"Auth mode: {auth_mode}")

    config_data: dict[str, Any] = {
        "authMode": auth_mode,
        "btpUrl": url.rstrip("/"),
    }
    secrets_data: dict[str, Any] = {}

    # --- Prompt theo auth mode ---
    if auth_mode == "oauth2":
        client_id = ask("Client ID")
        client_secret = ask("Client Secret", secret=True)
        scope = ask("Scope (de trong neu khong can)", default="")
        region = ask("Region", default="eu10")
        service = ask("Service type (s4hc / btp / onprem)", default="s4hc")

        config_data.update({
            "clientId": client_id,
            "scope": scope,
            "region": region,
            "service": service,
        })
        secrets_data.update({
            "clientSecret": client_secret,
        })

    elif auth_mode == "password":
        username = ask("Username")
        password = ask("Password", secret=True)
        client_id = ask("Client ID")
        region = ask("Region", default="eu10")
        service = ask("Service type (s4hc_(private) / s4hc_(public) / onprem)", default="s4hc_(public)")

        config_data.update({
            "clientId": client_id,
            "region": region,
            "service": service,
            "authMode": "password",
        })
        secrets_data.update({
            "username": username,
            "password": password,
        })

    elif auth_mode == "bearer":
        token = ask("Bearer Token", secret=True)
        region = ask("Region", default="eu10")
        service = ask("Service type (s4hc_(private) / s4hc_(public) / onprem)", default="s4hc_(public)")

        config_data.update({
            "region": region,
            "service": service,
        })
        secrets_data.update({
            "accessToken": token,
        })

    elif auth_mode == "cookie":
        info("Cookie auth: SAP session cookies (MYSAPSSO2, SAP_SESSIONID, ...)")
        print()

        cookie_source = ask(
            "Lay cookies tu: (1) File Netscape format  (2) Nhap tay  "
            "(3) Auto - mo browser dang nhap (can playwright)",
            default="3",
        )

        if cookie_source == "1":
            cookie_file = ask("Duong dan file cookies (Netscape format)")
            cookies = _load_cookies_from_file(cookie_file)
            if not cookies:
                print("  ⚠️ Khong doc duoc cookies tu file. Thu nhap tay.")
                cookie_str = ask("Cookie string (name=value; name2=value2)")
                cookies = _parse_cookie_string(cookie_str)
        elif cookie_source == "3":
            from ..sap.auth import web_login_auto
            result = await web_login_auto({"base_url": url, "profile_id": profile_id})
            cookies = result.cookies
            if not cookies:
                print("  ⚠️ Khong lay duoc cookie tu browser. Thu nhap tay.")
                cookie_str = ask("Cookie string (name=value; name2=value2)")
                cookies = _parse_cookie_string(cookie_str)
        else:
            print()
            print("  👉 Mo SAP system trong trinh duyet, dang nhap, sau do:")
            print("     (F12 -> Application -> Cookies -> Copy cookie string)")
            print()
            cookie_str = ask("Cookie string (name=value; name2=value2)")
            cookies = _parse_cookie_string(cookie_str)

        region = ask("Region", default="eu10")
        service = ask("Service type (s4hc_(private) / s4hc_(public) / onprem)", default="s4hc_(public)")

        # Cache cookies trong secrets
        secrets_data["cookies"] = cookies

        # Reauth mode
        reauth_mode = ask(
            "Che do re-auth khi session het han? (1) Manual paste  (2) Auto (Playwright)",
            default="2" if cookie_source == "3" else "1",
        )
        config_data["reauthMode"] = "auto" if reauth_mode == "2" else "manual"
        config_data.update({
            "region": region,
            "service": service,
        })

        if cookies:
            important = {"MYSAPSSO2", "SAP_SESSIONID", "sap-contextid", "sap-usercontext"}
            found = important & set(cookies.keys())
            if found:
                ok(f"Nhan dien {len(cookies)} cookies (gom {', '.join(found)})")
            else:
                warn(f"Khong thay session cookies (MYSAPSSO2/SAP_SESSIONID). "
                     f"Co the can dang nhap lai.")
        else:
            warn("Khong co cookies. Profile se can cap nhat sau.")

    # --- Tenant (optional) ---
    tenant = ask("Tenant (de trong = lay tu URL)", default="")
    if tenant:
        config_data["tenant"] = tenant

    # --- Luu ---
    upsert_profile(profile_id, url=url)
    save_config(profile_id, config_data)

    if secrets_data:
        await save_secrets(profile_id, secrets_data)

    print()
    ok(f"Da tao profile '{profile_id}' thanh cong!")
    info(f"Auth mode: {auth_mode}")
    info(f"URL: {url}")
    print()
    info("Ban co the kiem tra ket noi bang: sap-btp-agent connect")
    print()


# ===== CONNECT =====================================================

async def _cmd_connect(profile_id: str | None) -> None:
    from ..sap.client import SapClient
    from ..sap.auth import web_login_popup, web_login_auto
    from ..config.store import load_config

    try:
        cfg = await asyncio.to_thread(load_config, profile_id)
    except RuntimeError as err:
        print(f"  ❌ {err}")
        return

    pid = profile_id or get_current_active() or "?"
    auth_mode = cfg.get("authMode", "oauth2")
    reauth_mode = cfg.get("reauthMode", "manual")

    header(f"Kiem tra ket noi — {pid}")

    # Chon reauth_handler theo config
    reauth_handler = None
    if auth_mode == "cookie":
        if reauth_mode == "auto":
            reauth_handler = web_login_auto
            info("Re-auth mode: Auto (Playwright)")
        else:
            reauth_handler = web_login_popup
            info("Re-auth mode: Manual (paste cookie)")

    client = SapClient(pid, reauth_handler=reauth_handler)
    try:
        await client.init()
    except Exception as err:
        print(f"  ❌ Init that bai: {err}")
        return

    try:
        me = await client.get(
            "/sap/bc/adt/repository/informationsystem/search",
            query={"operation": "quickSearch", "query": "ZZZZZZ_NO_MATCH_AAA", "maxResults": 1},
        )
        ok(f"Ket noi thanh cong! Profile: {pid}")
        info(f"URL: {cfg.get('btpUrl', '?')}")
        info(f"Auth: {auth_mode}")
        if isinstance(me, dict) and "error" not in me:
            info("API OK")
        else:
            info(f"API: {str(me)[:100]}")
    except Exception as err:
        print(f"  ❌ Ket noi that bai: {err}")
        if auth_mode == "cookie":
            print()
            print("  💡 Thu chay lai setup de cap nhat cookies:")
            print(f"     sap-btp-agent setup {cfg.get('btpUrl', '')}")
        return


# ===== PROFILES ====================================================

async def _cmd_profiles(subcmd: str, arg: str | None) -> None:
    if subcmd == "list":
        data = list_profiles()
        active = data.get("active")
        print()
        header("Cac profile SAP")
        for p in data.get("items", []):
            marker = "*" if p["id"] == active else " "
            print(f"  {marker} {p['id']}  ({p.get('label', p['id'])})")
            if p["id"] == active:
                print(f"     URL: {p.get('url', '?')}")
        print(f"\n  Active: {active or '(none)'}")
        print()

    elif subcmd == "use" and arg:
        try:
            set_active_profile(arg)
            ok(f"Da chuyen sang profile '{arg}'")
        except RuntimeError as err:
            print(f"  ❌ {err}")

    elif subcmd == "show":
        from ..config.store import load_config
        from ..config.secrets import load_secrets
        pid = arg or get_current_active()
        if not pid:
            print("  ❌ Chua co profile nao.")
            return
        try:
            cfg = await asyncio.to_thread(load_config, pid)
            secrets = await load_secrets(pid)
            print()
            header(f"Profile: {pid}")
            for k, v in cfg.items():
                print(f"  {k}: {v}")
            print(f"  secrets keys: {list(secrets.keys())}")
            print()
        except RuntimeError as err:
            print(f"  ❌ {err}")

    elif subcmd == "remove" and arg:
        try:
            result = remove_profile(arg)
            ok(f"Da xoa profile '{arg}'")
            if result.get("newActive"):
                info(f"Active moi: {result['newActive']}")
        except RuntimeError as err:
            print(f"  ❌ {err}")

    else:
        print("  Usage:")
        print("    sap-btp-agent profiles list")
        print("    sap-btp-agent profiles use <id>")
        print("    sap-btp-agent profiles show [id]")
        print("    sap-btp-agent profiles remove <id>")


# ===== RESET =======================================================

def _cmd_reset() -> None:
    print()
    warn("CANH BAO: Ban sap xoa TOAN BO du lieu cau hinh SAP BTP Agent!")
    print("  Tat ca profile, secrets se bi mat.")
    confirm = input("  Go 'yes' de xac nhan: ").strip().lower()
    if confirm == "yes":
        reset_all()
        ok("Da xoa tat ca du lieu.")
    else:
        info("Huy lenh reset.")


# ===== Helpers =====================================================

def _load_cookies_from_file(filepath: str) -> dict[str, str]:
    """Load cookies tu Netscape-format cookie file."""
    cookies: dict[str, str] = {}
    try:
        with open(os.path.expanduser(filepath), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]
                elif "=" in line:
                    kv = line.split("=", 1)
                    cookies[kv[0].strip()] = kv[1].strip()
        return cookies
    except (FileNotFoundError, PermissionError) as err:
        warn(f"Khong doc duoc file: {err}")
        return {}


if __name__ == "__main__":
    main()
