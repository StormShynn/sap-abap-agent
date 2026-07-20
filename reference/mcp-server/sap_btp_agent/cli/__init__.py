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
import threading
from typing import Any

from ..sap.auth import (
    _looks_like_netscape_text,
    _parse_cookie_string,
    _parse_netscape_cookie_text,
    _session_cookie_names,
)
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
from ..sap.auth import ReauthCancelled
from .prompt import UserCancelled
from . import _cancel as _sig

from ..config.store import (
    SERVICE_TYPE_DEFAULT,
    SERVICE_TYPES,
    normalize_btp_url,
    normalize_service_type,
    save_config,
)
from .prompt import ask, header, info, ok, warn
def _ask_service() -> str:
    """Hoi service type voi schema moi (s4hc_(private)/s4hc_(public)/btp/onprem).

    Tuong thich nguoc: neu user nhap gia tri cu ("s4hc") thi tu dong anh xa
    sang gia tri moi tuong ung. Validate ngay khi nhap de tranh config sai.
    """
    opts = " / ".join(SERVICE_TYPES)
    raw = ask(f"Service type ({opts})", default=SERVICE_TYPE_DEFAULT)
    while True:
        try:
            return normalize_service_type(raw)
        except ValueError as err:
            print(f"  -> {err}")
            raw = ask(f"Service type ({opts})", default=SERVICE_TYPE_DEFAULT)

def main() -> None:
    """Entry point: sap-btp-agent <command> [args...]

    Khong co argument -> chay MCP stdio server (dung khi Claude Code/Desktop
    spawn qua `claude mcp add ... -- sap-btp-agent`). Co argument -> CLI thuong.
    """
    # Console Windows mac dinh cp1252 -> in emoji (❌✅⚠️...) se UnicodeEncodeError.
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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

    runner = _make_runner()
    if cmd == "setup":
        url = cmd_args[0] if cmd_args else ""
        runner(_wizard_setup, url)
    elif cmd == "connect":
        runner(_cmd_connect, cmd_args[0] if cmd_args else None)
    elif cmd == "reauth":
        runner(_cmd_reauth, cmd_args[0] if cmd_args else None)
    elif cmd == "profiles" and cmd_args:
        runner(_cmd_profiles, cmd_args[0], cmd_args[1] if len(cmd_args) > 1 else None)
    elif cmd == "reset":
        _cmd_reset()
    elif cmd == "doctor":
        from ..doctor import main as run_doctor
        run_doctor()
    elif cmd == "mcp-setup":
        _cmd_mcp_setup()
    elif cmd == "license":
        _cmd_license(cmd_args[0] if cmd_args else None)
    else:
        print(f"  ❌ Unknown command: {cmd}")
        _show_help()


def _make_runner():
    """Tra ve ham runner(coro_fn, *args) chay coroutine va bat 3 loai cancel:

    - KeyboardInterrupt: in 1 dong thong bao gon, KHONG in traceback (mac dinh
      asyncio.run tu Python 3.11+ in traceback dai 10+ dong rat kho chiu).
    - ReauthCancelled: in thong bao huy cu the, thoat code 0 (khong phai loi).
    - UserCancelled: nhu ReauthCancelled nhung cho setup wizard (prompt.ask,
      _read_cookie_paste) - huy setup/ghi config ban dau.

    Tat ca duong di khac (return binh thuong, exception that bai) giu nguyen.
    """
    def runner(coro_fn, *args):
        try:
            asyncio.run(coro_fn(*args))
        except ReauthCancelled as err:
            print(f"\n  ⏹  Huy dang nhap lai ({err.where}). Cookie cu KHONG bi thay doi.")
        except UserCancelled as err:
            print(f"\n  ⏹  Da huy tai buoc nhap ({err.where}). Config KHONG bi thay doi.")
        except KeyboardInterrupt:
            print("\n  ⏹  Da huy (Ctrl+C). Cookie cu KHONG bi thay doi.")
    return runner


def _show_help() -> None:
    print()
    print("  SAP ABAP Agent — CLI Tool (v1.8.0)")
    print("=" * 50)
    print()
    print("  Commands:")
    print("    setup [URL]            Thêm project SAP mới (wizard)")
    print("    connect [profile-id]   Test kết nối profile")
    print("    reauth [profile-id]    Đăng nhập lại (lấy cookie mới) - không hỏi lại từ đầu như setup")
    print("    mcp-setup              Đăng ký MCP servers với Claude Code")
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
    print("    sap-btp-agent mcp-setup")
    print("    sap-btp-agent connect")
    print("    sap-btp-agent reauth")
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

    # Thieu scheme (VD nhap "xxx.s4hana.cloud.sap" khong co "https://") lam
    # derive_profile_id_from_url fail va Playwright/httpx tu choi request
    # sau nay voi loi kho hieu - tu them https:// va bao lai cho user biet.
    normalized_url = normalize_btp_url(url)
    if normalized_url != url:
        info(f"Da tu them 'https://': {normalized_url}")
        url = normalized_url

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
        service = _ask_service()

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
        service = _ask_service()

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
        service = _ask_service()

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
            try:
                result = await web_login_auto({"base_url": url, "profile_id": profile_id})
                cookies = result.cookies
            except Exception as err:
                print(f"  ❌ Auto-login qua browser loi: {err}")
                cookies = {}
            if not cookies:
                print("  ⚠️ Khong lay duoc cookie tu browser. Thu nhap tay.")
                cookie_str = ask("Cookie string (name=value; name2=value2)")
                cookies = _parse_cookie_string(cookie_str)
        else:
            print()
            print("  👉 Mo SAP system trong trinh duyet, dang nhap, sau do:")
            print("     (F12 -> Application -> Cookies -> Copy cookie string,")
            print("      hoac paste noi dung file cookie Netscape - vd tu 'Get cookies.txt')")
            print()
            cookie_text = _read_cookie_paste()
            if _looks_like_netscape_text(cookie_text):
                cookies = _parse_netscape_cookie_text(cookie_text)
            else:
                cookies = _parse_cookie_string(cookie_text)

        region = ask("Region", default="eu10")
        service = _ask_service()

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
            found = _session_cookie_names(cookies)
            if found:
                ok(f"Nhan dien {len(cookies)} cookies (gom {', '.join(found)})")
            else:
                warn(f"Khong thay cookie ten SAP_SESSIONID*/MYSAPSSO2 sau khi parse "
                     f"({len(cookies)} cookies khac). Co the paste sai dinh dang hoac can dang nhap lai.")
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
    if ask("Dang ky MCP servers voi Claude Code ngay?", default="y").lower() in ("", "y", "yes"):
        _cmd_mcp_setup()


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
        ok(f"Doc du lieu (read): OK — Profile: {pid}")
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
            print("  💡 Dang nhap lai (nhanh hon, khong hoi lai tu dau nhu setup):")
            print(f"     sap-btp-agent reauth {pid}")
        return

    # Doc (GET) va ghi (POST/PUT/DELETE) la 2 dieu kien khac nhau - GET co the qua
    # trong khi xin CSRF token (dieu kien de goi activate/list_packages/run_unit_tests/
    # syntax_check) van fail. Kiem tra rieng de "connect" khong bao "thanh cong" roi
    # lenh ghi sau do lai loi ngay, gay kho hieu.
    try:
        await client.check_write_access()
        ok("Ghi du lieu (CSRF/write): OK")
        print()
        ok(f"Ket noi thanh cong — Profile '{pid}' san sang dung ca doc lan ghi.")
    except Exception as err:
        warn(f"Ghi du lieu (CSRF/write): THAT BAI — {err}")
        warn("Cac lenh GHI (activate/list_packages/run_unit_tests/syntax_check) se loi ngay bay gio.")
        warn("Doc-only (search/read_source/execute_query...) van dung binh thuong.")
        if auth_mode == "cookie":
            print()
            print("  💡 Dang nhap lai (nhanh hon, khong hoi lai tu dau nhu setup):")
            print(f"     sap-btp-agent reauth {pid}")


# ===== REAUTH (dang nhap lai / lay cookie moi, khong can setup lai tu dau) ==

async def _cmd_reauth(profile_id: str | None) -> None:
    """Lay cookie moi cho 1 profile cookie-auth da co san.

    Khac voi `setup` (hoi lai tu dau: auth mode, region, service type, tenant...),
    lenh nay chi doc lai config da luu roi kich hoat thang buoc lay cookie -
    dung khi chi can dang nhap lai vi session het han, khong doi gi khac.
    """
    from ..sap.auth import SapCookieAuth, web_login_popup, web_login_auto
    from ..config.store import load_config

    try:
        cfg = await asyncio.to_thread(load_config, profile_id)
    except RuntimeError as err:
        print(f"  ❌ {err}")
        return

    pid = profile_id or get_current_active() or "?"
    auth_mode = cfg.get("authMode", "oauth2")

    if auth_mode != "cookie":
        print(f"  ❌ Profile '{pid}' dung authMode='{auth_mode}', khong phai cookie.")
        print("     OAuth2/password/bearer tu refresh token luc goi API - khong can lenh nay.")
        return

    reauth_mode = cfg.get("reauthMode", "manual")
    reauth_handler = web_login_auto if reauth_mode == "auto" else web_login_popup

    header(f"Dang nhap lai — {pid}")
    info(f"Re-auth mode: {'Auto (Playwright)' if reauth_mode == 'auto' else 'Manual (paste cookie)'}")

    # Wire "early finish" signal: cho auto mode, 2 cach de ket thuc som:
    #  1. GUI: SAP_BTP_EARLY_FINISH_FILE duoc touch -> asyncio.Event set.
    #  2. CLI: user bam Enter -> stdin doc 1 dong -> asyncio.Event set.
    early_event = None
    import asyncio as _aio
    import os as _os
    early_event = _aio.Event()

    marker_path = _os.environ.get("SAP_BTP_EARLY_FINISH_FILE")
    is_tty = sys.stdin and sys.stdin.isatty()

    if marker_path:
        # GUI mode: watch file marker qua asyncio loop (khong can thread rieng)
        async def _watch_file():
            from pathlib import Path as _P
            while not early_event.is_set():
                if _P(marker_path).exists():
                    early_event.set()
                    break
                await _aio.sleep(0.1)
        _aio.get_event_loop().create_task(_watch_file())
    elif is_tty and reauth_mode == "auto":
        # CLI mode: thread rieng doc stdin (Enter)
        def _stdin_watcher():
            try:
                line = sys.stdin.readline()
                if line is not None:
                    early_event.set()
            except Exception:
                pass
        threading.Thread(target=_stdin_watcher, daemon=True).start()

    # Bat handler Ctrl+C 2-lan: lan 1 canh bao, lan 2 huy that.
    # Khoi phuc default handler khi xong (ke ca khi raise).
    _sig.install_double_ctrl_c(ReauthCancelled, lambda w: ReauthCancelled(w))
    try:
        cookie_auth = SapCookieAuth(pid, reauth_handler=reauth_handler)
        await cookie_auth.init()
        try:
            result = await cookie_auth.reauth(ctx={"early_finish_event": early_event})
        except ReauthCancelled:
            # Da in thong bao chi tiet trong handler (web_login_popup/auto).
            # KHONG save gi ca, thoat sach.
            return
        except Exception as err:
            print(f"  ❌ Dang nhap lai that bai: {err}")
            return

        if not result.cookies:
            # Phong truong hop handler tu custom tra ReauthResult rong ma khong raise.
            print("  ⚠️ Khong lay duoc cookie moi (co the ban da huy hoac timeout).")
            print("     Cookie cu KHONG bi thay doi.")
            return

        # Validate 1 lan cuoi truoc khi save: cookie moi phai chua session-cookie.
        # Neu khong co -> reject, giu nguyen cookie cu con han.
        from ..sap.auth import _session_cookie_names as _scn
        if not _scn(result.cookies):
            print("  ❌ Cookie moi khong chua session-cookie (MYSAPSSO2/SAP_SESSIONID).")
            print("     Cookie cu KHONG bi thay doi. Thu lai va copy DUNG cookies.")
            return

        await cookie_auth.save_cookies()
        print()
        ok(f"Da cap nhat cookie cho profile '{pid}'.")
        info(f"Kiem tra lai: sap-btp-agent connect {pid}")
    finally:
        _sig.uninstall()




# ===== LICENSE =====================================================

def _is_sensitive_key(key: str) -> bool:
    k = (key or "").lower()
    sensitive_markers = (
        "password",
        "passwd",
        "secret",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "cookie",
        "session",
        "client_secret",
        "apikey",
        "api_key",
    )
    return any(marker in k for marker in sensitive_markers)


def _safe_display_value(key: str, value: Any) -> str:
    if _is_sensitive_key(key):
        return "***REDACTED***"

    k = (key or "").lower()
    if k == "type":
        allowed_types = {"oauth2", "cookie"}
        v = str(value).lower()
        return v if v in allowed_types else "***REDACTED***"

    return str(value)


def _cmd_license(profile_id):
    """In trang thai license (cookie/token) cua 1 hoac tat ca profile.

    Args:
        profile_id: neu None -> in tat ca profile. Neu co -> in chi tiet 1 profile.
    """
    from .. import license as _lic

    if profile_id:
        # In chi tiet 1 profile
        try:
            st = _lic.get_profile_status(profile_id)
        except Exception as err:
            print(f"  Loi doc license: {err}")
            return

        print()
        print("=" * 60)
        print(f"  License: {profile_id}")
        print("=" * 60)
        print(f"  Type        : {st['type']}")
        creds_state = "available" if st.get("has_credentials") else "missing"
        print(f"  Credentials : {creds_state}")
        print(f"  Type        : {_safe_display_value('type', st['type'])}")
        print(f"  Has creds   : {st['has_credentials']}")
        if st["expires_at"]:
            import datetime as _dt
            exp_dt = _dt.datetime.fromtimestamp(st["expires_at"])
            print(f"  Expires at  : {exp_dt.strftime('%Y-%m-%d %H:%M:%S')} ({st['expires_in_human']})")
        else:
            print(f"  Expires at  : (unknown)")
        if st.get("last_saved"):
            import datetime as _dt
            sv_dt = _dt.datetime.fromtimestamp(st["last_saved"])
            print(f"  Saved at    : {sv_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        if st.get("extra"):
            safe_extra_keys = {"token_endpoint", "scope"}
            sensitive_markers = ("token", "secret", "password", "cookie", "authorization", "auth")
            for k, v in st["extra"].items():
                presence = "set" if v else "(empty)"
                print(f"  {k:11s}: {presence}")
                key_l = str(k).lower()
                if k in safe_extra_keys:
                    print(f"  {k:11s}: [SET]")
                elif any(m in key_l for m in sensitive_markers):
                    print(f"  {k:11s}: [REDACTED]")
                else:
                    print("  extra      : [HIDDEN]")
        print()
        if st["is_expired"]:
            print(f"  EXPIRED - chay: sap-btp-agent reauth {profile_id}")
        elif st["is_warning"]:
            print(f"  Expiring soon ({st['expires_in_human']}) - can chuan bi reauth")
        else:
            print("  OK")
        print()
        return

    # Bang tom tat tat ca profile
    try:
        statuses = _lic.list_all_statuses()
    except Exception as err:
        print(f"  Loi: {err}")
        return

    if not statuses:
        print("  (chua co profile nao - chay: sap-btp-agent setup <url>)")
        return

    print()
    print("=" * 86)
    print(f"  {'Profile':<40} {'Type':<8} {'Status':<12} {'Expires':<16}")
    print("=" * 86)
    for s in statuses:
        marker = "*" if s["is_active"] else " "
        if not s["has_credentials"]:
            status = "no creds"
        elif s["is_expired"]:
            status = "expired"
        elif s["is_warning"]:
            status = "warning"
        else:
            status = "ok"
        pid_disp = (marker + s["profile_id"])[:40]
        type_disp = _safe_display_value("type", s["type"])
        print(f"  {pid_disp:<40} {type_disp:<8} {status:<12} {s['expires_in_human']:<16}")
    print("=" * 86)
    print("  (*) = active profile. Dung `sap-btp-agent license <id>` de xem chi tiet.")
    print()


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
            print("  secrets: loaded")
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


# ===== MCP SETUP ===================================================

def _cmd_mcp_setup() -> None:
    """Dang ky toan bo MCP servers voi Claude Code (bat buoc + tuy chon)."""
    header("MCP Server Setup — Dang ky MCP servers voi Claude Code")

    import shutil
    import subprocess

    claude_path = shutil.which("claude")
    if not claude_path:
        warn("Khong tim thay 'claude' trong PATH.")
        info("Hay cai Claude Code truoc, roi chay lai: sap-btp-agent mcp-setup")
        info("Download: https://claude.ai/download")
        return

    def _register(name: str, transport: str, *,
                  url: str | None = None, cmd: str | None = None,
                  args: list[str] | None = None,
                  env: dict[str, str] | None = None) -> bool:
        """Goi claude mcp add, tra True neu thanh cong."""
        cli = [claude_path, "mcp", "add", "--transport", transport]
        if transport in ("sse", "http", "ws"):
            if url:
                cli.extend(["--url", url])
        else:
            if cmd:
                cli.append("--")
                cli.append(cmd)
                if args:
                    cli.extend(args)
        if env:
            for k, v in env.items():
                if v:
                    cli.extend(["--env", f"{k}={v}"])
        try:
            subprocess.run(cli, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    # --- Core servers (bat buoc) ---
    header("Core servers (bat buoc)")
    ok("Dang ky sap-btp...")
    _register("sap-btp", "stdio", cmd="sap-btp-agent")
    ok("Dang ky sap-dict-bridge...")
    _register("sap-dict-bridge", "stdio", cmd="python",
              args=["-m", "sap_btp_agent.bridge_server"])

    # --- Remote SSE servers (bat buoc - chi can URL) ---
    header("Remote servers (bat buoc)")
    ok("Dang ky cds-kb...")
    _register("cds-kb", "sse",
              url="https://cds-kb-mcp-production.up.railway.app/sse")
    ok("Dang ky mcp-sap-docs-btp...")
    sap_hub_key = os.environ.get("SAP_API_HUB_KEY", "")
    _register("mcp-sap-docs-btp", "sse",
              url="https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse",
              env={"SAP-API-HUB-KEY": sap_hub_key} if sap_hub_key else None)

    # --- ADT alternatives (tuy chon) ---
    header("ADT alternatives (tuy chon)")
    if ask("Dang ky arc-1 (Enterprise ADT MCP)?", default="y").lower() in ("", "y", "yes"):
        _register("arc-1", "stdio", cmd="npx", args=["-y", "arc-1@latest"])
    if ask("Dang ky mcp-abap-adt (community read-only)?", default="n").lower() in ("y", "yes"):
        adt_url = ask("ADT URL (VD: https://xxx.s4hana.cloud.sap)")
        adt_user = ask("ADT username")
        adt_pass = ask("ADT password", secret=True)
        _register("mcp-abap-adt", "stdio", cmd="npx", args=["-y", "mcp-abap-adt"],
                  env={"ADT_URL": adt_url, "ADT_USER": adt_user,
                       "ADT_PASS": adt_pass, "ADT_CLIENT": "100"})

    # --- Product-specific servers (manual) ---
    header("Product-specific servers (can cai dat them)")
    info("Cac server sau can cai dat thu cong. Xem skill doc huong dan chi tiet:")
    print("  - sap-notes:    skills/mcp-sap-notes/SKILL.md")
    print("  - sap-gui:      skills/mcp-sap-gui/SKILL.md")
    print("  - sf-mcp:       skills/mcp-sap-successfactors/SKILL.md")
    print("  - sf-cdata:     skills/mcp-sap-successfactors/SKILL.md")
    print("  - sap-concur:   skills/mcp-sap-concur/SKILL.md")
    print("  - sap-fieldglass: skills/mcp-sap-fieldglass/SKILL.md")
    print()

    ok("Hoan tat! Khoi dong lai Claude Code de nhan server moi.")
    info("Kiem tra bang: claude mcp list")


# ===== Helpers =====================================================

def _load_cookies_from_file(filepath: str) -> dict[str, str]:
    """Load cookies tu Netscape-format cookie file."""
    try:
        with open(os.path.expanduser(filepath), "r", encoding="utf-8") as f:
            text = f.read()
    except (FileNotFoundError, PermissionError) as err:
        warn(f"Khong doc duoc file: {err}")
        return {}
    return _parse_netscape_cookie_text(text)


def _read_cookie_paste() -> str:
    """Doc cookie string tu stdin.

    Neu dong dau tien phat hien dinh dang Netscape cookie file (tab-separated
    7 cot, hoac header '# Netscape...'), tiep tuc doc them cac dong con lai
    toi khi EOF - vi paste 1 file nhieu dong khong the lay het bang 1 lan
    readline() nhu cau hoi thuong (ask()).
    """
    sys.stdout.write("  Cookie string (name=value; name2=value2): ")
    sys.stdout.flush()
    first = sys.stdin.readline()
    if not first:
        raise UserCancelled("cookie paste (stdin closed)")
    first_line = first.rstrip("\n").rstrip("\r")
    if not _looks_like_netscape_text(first_line):
        return first_line.strip()

    eof_hint = "Ctrl+Z roi Enter" if os.name == "nt" else "Ctrl+D"
    print(f"  (Phat hien dinh dang Netscape cookie file - paste tiep cac dong con lai, "
          f"roi {eof_hint} de ket thuc)")
    lines = [first_line]
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            lines.append(line.rstrip("\n").rstrip("\r"))
    except KeyboardInterrupt:
        if not lines:
            raise UserCancelled("cookie paste (Ctrl+C)")
        # da paste du lieu roi -> silent fallthrough
    return "\n".join(lines)


if __name__ == "__main__":
    main()



