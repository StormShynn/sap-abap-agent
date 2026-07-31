"""CLI entry point: mcp-sap-connect setup / connect / profiles / reset.

Usage:
  mcp-sap-connect                              Chay MCP stdio server (khong argument)
  mcp-sap-connect setup https://xxx.s4hana.cloud.sap
  mcp-sap-connect connect [profile-id]
  mcp-sap-connect profiles list|use|show|remove <id>
  mcp-sap-connect reset
  mcp-sap-connect --help
"""
from __future__ import annotations

import asyncio
import os
import sys
import threading
from typing import Any

from ..config.profile import (
    derive_profile_id_from_url,
    get_current_active,
    list_profiles,
    remove_profile,
    reset_all,
    set_active_profile,
    upsert_profile,
)
from ..config.secrets import load_secrets, save_secrets
from ..config.store import (
    SERVICE_TYPE_DEFAULT,
    SERVICE_TYPE_DESCRIPTIONS,
    SERVICE_TYPES,
    load_config,
    normalize_btp_url,
    normalize_service_type,
    save_config,
)
from ..sap.auth import (
    ReauthCancelled,
    _looks_like_netscape_text,
    _parse_cookie_string,
    _parse_netscape_cookie_text,
    _session_cookie_names,
    saml_or_browser_login,
)
from ..setup_vsp import VspSetupError, ensure_vsp
from . import _cancel as _sig
from .prompt import UserCancelled, ask, header, info, ok, warn


def _ask_service() -> str:
    """Hoi service type voi schema 5 edition (s4hc_(private)/s4hc_(public)/btp/onprem/rise_with_sap).

    Tuong thich nguoc: neu user nhap gia tri cu ("s4hc" hoac "rise") thi tu dong
    anh xa sang gia tri moi tuong ung. Validate ngay khi nhap de tranh config sai.
    Hien thi menu 1 dong cho moi service type kem mo ta ngan de user chon dung.
    """
    lines = []
    for st in SERVICE_TYPES:
        desc = SERVICE_TYPE_DESCRIPTIONS.get(st, "")
        lines.append(f"  {st:<16} - {desc}" if desc else f"  {st}")
    menu = "\n".join(lines)
    raw = ask(f"Service type:\n{menu}\nChon 1 gia tri", default=SERVICE_TYPE_DEFAULT)
    while True:
        try:
            return normalize_service_type(raw)
        except ValueError as err:
            print(f"  -> {err}")
            raw = ask(f"Service type:\n{menu}\nChon 1 gia tri", default=SERVICE_TYPE_DEFAULT)

def main() -> None:
    """Entry point: mcp-sap-connect <command> [args...]

    Khong co argument -> chay MCP stdio server (dung khi Claude Code/Desktop
    spawn qua `claude mcp add ... -- mcp-sap-connect`). Co argument -> CLI thuong.
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
        if cmd_args and cmd_args[0] == "--from-file":
            if len(cmd_args) < 2:
                print("  ❌ Thieu duong dan file. Dung: mcp-sap-connect setup --from-file <path>")
            else:
                runner(_setup_from_file, cmd_args[1])
        else:
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
    print("    mcp-sap-connect setup https://xxx.s4hana.cloud.sap")
    print("    mcp-sap-connect mcp-setup")
    print("    mcp-sap-connect connect")
    print("    mcp-sap-connect reauth")
    print("    mcp-sap-connect profiles list")
    print("    mcp-sap-connect doctor")
    print()
    print("  Neu 'mcp-sap-connect' khong duoc nhan dien (not recognized), chay:")
    print("    python -m mcp_sap_connect.doctor")
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
            "Lay cookies tu: (1) SAML fast-path (nhap user/pass, ~1-3s, KHONG mo browser -"
            " chi dung neu IAS KHONG MFA)  (2) Auto - mo browser dang nhap (ho tro ca MFA)  "
            "(3) File Netscape format  (4) Nhap tay",
            default="1",
        )

        if cookie_source == "1":
            from ..sap.auth import SamlLoginError, saml_form_login
            saml_user = ask("SAP Username (dang nhap IAS)")
            saml_pass = ask("SAP Password (dang nhap IAS)", secret=True)
            info("Thu dang nhap nhanh qua SAML form (HTTP truc tiep, khong mo browser)...")
            try:
                result = await saml_form_login(url, saml_user, saml_pass)
                cookies = result.cookies
                secrets_data["samlUsername"] = saml_user
                secrets_data["samlPassword"] = saml_pass
                ok("Dang nhap nhanh thanh cong - da luu (ma hoa) de tu dung lai cho lan reauth sau.")
            except SamlLoginError as err:
                warn(f"Dang nhap nhanh khong thanh cong ({err}) - fallback ve mo browser...")
                cookies = {}
                cookie_source = "2"  # roi qua nhanh browser ben duoi
            finally:
                saml_user = saml_pass = ""

        if cookie_source == "2":
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
        elif cookie_source == "3":
            cookie_file = ask("Duong dan file cookies (Netscape format)")
            cookies = _load_cookies_from_file(cookie_file)
            if not cookies:
                print("  ⚠️ Khong doc duoc cookies tu file. Thu nhap tay.")
                cookie_str = ask("Cookie string (name=value; name2=value2)")
                cookies = _parse_cookie_string(cookie_str)
        elif cookie_source == "4":
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
            "Che do re-auth khi session het han? (1) Manual paste  "
            "(2) Auto (SAML fast-path neu con dung duoc, fallback browser)",
            default="2" if cookie_source in ("1", "2") else "1",
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
    info("Ban co the kiem tra ket noi bang: mcp-sap-connect connect")
    print()
    if ask("Dang ky MCP servers voi Claude Code ngay?", default="y").lower() in ("", "y", "yes"):
        _cmd_mcp_setup()


# ===== SETUP TU FILE (non-interactive) =============================

_PLACEHOLDER_MARKERS = ("<", ">", "YOUR_", "REPLACE_ME")


def _looks_like_placeholder(value: Any) -> bool:
    """True neu value con la placeholder chua dien (vd '<CLIENT_ID>')."""
    return isinstance(value, str) and any(m in value for m in _PLACEHOLDER_MARKERS)


def _wire_early_finish_event(reauth_mode: str) -> asyncio.Event:
    """Cho web_login_auto: 2 cach bao 'da dang nhap xong, kiem tra ngay' thay vi
    cho poll tu nhien den khi tu phat hien session/timeout:
      1. GUI: SAP_BTP_EARLY_FINISH_FILE duoc touch -> event.set().
      2. CLI (reauth_mode == 'auto'): user bam Enter -> stdin doc 1 dong -> event.set().
    Dung chung boi _cmd_reauth va _setup_from_file (auto cookie mode).
    """
    early_event = asyncio.Event()
    marker_path = os.environ.get("SAP_BTP_EARLY_FINISH_FILE")
    is_tty = sys.stdin and sys.stdin.isatty()

    if marker_path:
        async def _watch_file():
            from pathlib import Path as _P
            while not early_event.is_set():
                if _P(marker_path).exists():
                    early_event.set()
                    break
                await asyncio.sleep(0.1)
        asyncio.get_event_loop().create_task(_watch_file())
    elif is_tty and reauth_mode == "auto":
        def _stdin_watcher():
            try:
                line = sys.stdin.readline()
                if line is not None:
                    early_event.set()
            except Exception:
                pass
        threading.Thread(target=_stdin_watcher, daemon=True).start()

    return early_event


async def _setup_from_file(path: str) -> None:
    """Tao profile tu 1 file JSON da dien san (xem reference/templates/
    mcp-sap-connect-profile-sample/), thay vi tra loi wizard tuong tac tung buoc.

    Goi lai DUNG 3 ham upsert_profile/save_config/save_secrets ma _wizard_setup
    da dung - KHONG viet lai logic ma hoa/luu tru. Muc dich: user chi can dien
    1 file roi chay 1 lenh, khong con phai tra loi tung cau hoi trong terminal.
    """
    import json
    from pathlib import Path

    header("SAP ABAP Agent — Setup tu file")

    file = Path(path).expanduser()
    if not file.is_file():
        print(f"  ❌ Khong tim thay file: {file}")
        return
    try:
        data: dict[str, Any] = json.loads(file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as err:
        print(f"  ❌ File JSON khong hop le ({file}): {err}")
        return

    raw_url = str(data.get("url", "")).strip()
    if not raw_url or _looks_like_placeholder(raw_url):
        print("  ❌ File thieu field 'url' hop le (con la placeholder hoac rong).")
        return
    url = normalize_btp_url(raw_url)

    profile_id = str(data.get("profileId", "")).strip() or derive_profile_id_from_url(url)
    if not profile_id:
        print("  ❌ Khong sinh duoc profile ID tu 'url', va file khong co field 'profileId'.")
        return

    auth_mode = str(data.get("authMode", "")).strip()
    if auth_mode not in ("oauth2", "password", "bearer", "cookie"):
        print(f"  ❌ 'authMode' khong hop le: {auth_mode!r}. Phai la 1 trong: "
              f"oauth2, password, bearer, cookie.")
        return

    try:
        service = normalize_service_type(data.get("service", SERVICE_TYPE_DEFAULT))
    except ValueError as err:
        print(f"  ❌ {err}")
        return

    config_data: dict[str, Any] = {
        "authMode": auth_mode,
        "btpUrl": url.rstrip("/"),
        "region": str(data.get("region", "eu10")).strip() or "eu10",
        "service": service,
    }
    secrets_data: dict[str, Any] = {}

    if auth_mode == "oauth2":
        client_id = str(data.get("clientId", "")).strip()
        client_secret = str(data.get("clientSecret", "")).strip()
        if not client_id or not client_secret or _looks_like_placeholder(client_id) or _looks_like_placeholder(client_secret):
            print("  ❌ Thieu hoac chua thay placeholder cho 'clientId'/'clientSecret'.")
            return
        config_data["clientId"] = client_id
        config_data["scope"] = str(data.get("scope", "")).strip()
        secrets_data["clientSecret"] = client_secret

    elif auth_mode == "password":
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", "")).strip()
        if not username or not password or _looks_like_placeholder(username) or _looks_like_placeholder(password):
            print("  ❌ Thieu hoac chua thay placeholder cho 'username'/'password'.")
            return
        config_data["clientId"] = str(data.get("clientId", "")).strip()
        secrets_data["username"] = username
        secrets_data["password"] = password

    elif auth_mode == "bearer":
        token = str(data.get("accessToken", "")).strip()
        if not token or _looks_like_placeholder(token):
            print("  ❌ Thieu hoac chua thay placeholder cho 'accessToken'.")
            return
        secrets_data["accessToken"] = token

    elif auth_mode == "cookie":
        cookies = data.get("cookies")
        cookies_missing = (
            not isinstance(cookies, dict) or not cookies
            or any(_looks_like_placeholder(v) for v in cookies.values())
        )
        reauth_mode = "auto" if data.get("reauthMode") == "auto" else "manual"

        if cookies_missing and reauth_mode == "auto":
            # Fast-path TUY CHON: neu file co dien them samlBootstrapUsername/
            # samlBootstrapPassword (khong placeholder), thu dang nhap SAML
            # qua HTTP form-fill truc tiep truoc (~1-3s, khong mo browser) -
            # port tu vibing-steampunk. CHI hoat dong voi IAS user/pass thuan,
            # KHONG MFA. Khong dien 2 field nay -> giu nguyen hanh vi cu (bo
            # qua thang xuong browser).
            #
            # Neu thanh cong: luu lai username/password nay (ma hoa trong
            # secrets, cung co che voi authMode=password) duoi ten
            # samlUsername/samlPassword, de saml_or_browser_login tu dung lai
            # cho cac lan reauth SAU nay (khong can mo browser moi lan session
            # het han). Neu that bai (vd MFA) thi KHONG luu, tranh luu credential
            # da biet la khong dung duoc qua duong nay.
            saml_user = str(data.get("samlBootstrapUsername", "")).strip()
            saml_pass = str(data.get("samlBootstrapPassword", "")).strip()
            if (
                saml_user and saml_pass
                and not _looks_like_placeholder(saml_user)
                and not _looks_like_placeholder(saml_pass)
            ):
                from ..sap.auth import SamlLoginError, saml_form_login
                info("Thu dang nhap nhanh qua SAML form (HTTP truc tiep, khong mo browser)...")
                try:
                    result = await saml_form_login(url, saml_user, saml_pass)
                    cookies = result.cookies
                    secrets_data["samlUsername"] = saml_user
                    secrets_data["samlPassword"] = saml_pass
                    info("Dang nhap nhanh thanh cong - da luu (ma hoa) de tu dung lai cho lan reauth sau.")
                except SamlLoginError as err:
                    warn(f"Dang nhap nhanh khong thanh cong ({err}) - fallback ve browser...")
                    cookies = None
                saml_user = saml_pass = ""
                cookies_missing = not isinstance(cookies, dict) or not cookies

            if cookies_missing:
                from ..sap.auth import web_login_auto
                info("Cookies con placeholder + reauthMode=auto -> tu mo browser de dang nhap...")
                info("(Neu bam Enter o terminal nay sau khi dang nhap xong, kiem tra session se chay ngay,"
                     " khong can cho tu phat hien/timeout.)")
                early_event = _wire_early_finish_event(reauth_mode)
                try:
                    result = await web_login_auto({
                        "base_url": url,
                        "profile_id": profile_id,
                        "early_finish_event": early_event,
                    })
                    cookies = result.cookies
                except Exception as err:
                    print(f"  ❌ Auto-login qua browser loi: {err}")
                    cookies = None
                cookies_missing = not isinstance(cookies, dict) or not cookies

        if cookies_missing:
            print("  ❌ Thieu hoac chua thay placeholder cho 'cookies' (phai la object "
                  "{\"MYSAPSSO2\": \"...\", ...}), va auto-login qua browser (neu co) khong lay duoc cookie.")
            return
        secrets_data["cookies"] = cookies
        config_data["reauthMode"] = reauth_mode

    tenant = str(data.get("tenant", "")).strip()
    if tenant:
        config_data["tenant"] = tenant

    upsert_profile(profile_id, url=url)
    save_config(profile_id, config_data)
    if secrets_data:
        await save_secrets(profile_id, secrets_data)

    print()
    ok(f"Da tao profile '{profile_id}' tu file '{file}'!")
    info(f"Auth mode: {auth_mode}")
    info(f"URL: {url}")
    info(f"Service: {service}")
    print()
    info("Kiem tra ket noi bang: mcp-sap-connect connect")
    print()
    if ask("Dang ky MCP servers voi Claude Code ngay?", default="y").lower() in ("", "y", "yes"):
        _cmd_mcp_setup()


# ===== CONNECT =====================================================

async def _cmd_connect(profile_id: str | None) -> None:
    from ..config.store import load_config
    from ..sap.auth import web_login_popup
    from ..sap.client import SapClient

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
            reauth_handler = saml_or_browser_login
            info("Re-auth mode: Auto (SAML fast-path neu co credential luu san, fallback browser)")
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
            print(f"     mcp-sap-connect reauth {pid}")
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
            print(f"     mcp-sap-connect reauth {pid}")


# ===== REAUTH (dang nhap lai / lay cookie moi, khong can setup lai tu dau) ==

async def _cmd_reauth(profile_id: str | None) -> None:
    """Lay cookie moi cho 1 profile cookie-auth da co san.

    Khac voi `setup` (hoi lai tu dau: auth mode, region, service type, tenant...),
    lenh nay chi doc lai config da luu roi kich hoat thang buoc lay cookie -
    dung khi chi can dang nhap lai vi session het han, khong doi gi khac.
    """
    from ..config.store import load_config
    from ..sap.auth import SapCookieAuth, web_login_popup

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
    reauth_handler = saml_or_browser_login if reauth_mode == "auto" else web_login_popup

    header(f"Dang nhap lai — {pid}")
    info(f"Re-auth mode: {'Auto (SAML fast-path neu co, fallback browser)' if reauth_mode == 'auto' else 'Manual (paste cookie)'}")

    early_event = _wire_early_finish_event(reauth_mode)

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
        info(f"Kiem tra lai: mcp-sap-connect connect {pid}")
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
        creds_state = "available" if st.get("has_credentials") else "missing"
        print(f"  Credentials : {creds_state}")
        try:
            cfg = load_config(profile_id)
        except Exception:
            cfg = {}
        raw_type = str((cfg or {}).get("authMode", "oauth2")).lower()
        safe_type = raw_type if raw_type in {"oauth2", "cookie"} else "***REDACTED***"
        print(f"  Type        : {safe_type}")
        if st["expires_at"]:
            import datetime as _dt
            exp_dt = _dt.datetime.fromtimestamp(st["expires_at"])
            if st.get("is_expired"):
                exp_state = "expired"
            elif st.get("is_warning"):
                exp_state = "expiring_soon"
            else:
                exp_state = "valid"
            print(f"  Expires at  : {exp_dt.strftime('%Y-%m-%d %H:%M:%S')} ({exp_state})")
        else:
            print("  Expires at  : (unknown)")
        if st.get("last_saved"):
            import datetime as _dt
            sv_dt = _dt.datetime.fromtimestamp(st["last_saved"])
            print(f"  Saved at    : {sv_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        if st.get("extra"):
            extra = st.get("extra") or {}
            token_endpoint = extra.get("token_endpoint")
            scope = extra.get("scope")

            print(f"  {'token_endpoint':11s}: {'[SET]' if token_endpoint else '(empty)'}")
            print(f"  {'scope':11s}: {'[SET]' if scope else '(empty)'}")

            unknown_keys = [key for key in extra if key not in {"token_endpoint", "scope"}]
            if unknown_keys:
                print("  extra      : [REDACTED]")
        print()
        if st["is_expired"]:
            print(f"  EXPIRED - chay: mcp-sap-connect reauth {profile_id}")
        elif st["is_warning"]:
            print("  Expiring soon - can chuan bi reauth")
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
        print("  (chua co profile nao - chay: mcp-sap-connect setup <url>)")
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
    print("  (*) = active profile. Dung `mcp-sap-connect license <id>` de xem chi tiet.")
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
        from ..config.secrets import load_secrets
        from ..config.store import load_config
        pid = arg or get_current_active()
        if not pid:
            print("  ❌ Chua co profile nao.")
            return
        try:
            cfg = await asyncio.to_thread(load_config, pid)
            await load_secrets(pid)
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
        print("    mcp-sap-connect profiles list")
        print("    mcp-sap-connect profiles use <id>")
        print("    mcp-sap-connect profiles show [id]")
        print("    mcp-sap-connect profiles remove <id>")


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

def _setup_vsp_server(register_fn) -> None:
    """Tai (neu can) va dang ky `sap-vsp` qua register_fn(name, transport, cmd=, args=, env=).

    SAP_ADT_URL luon lay tu profile active (btpUrl). SAP_ADT_USER/PASSWORD chi
    dien tu dong duoc khi authMode profile la "password" (onprem/rise_with_sap)
    - cac authMode khac khong co plain password de truyen cho 1 process rieng.
    Xem KNOWN_LIMITATIONS.md.
    """
    pinned_bin = os.environ.get("MCP_SAP_CONNECT_VSP_BIN", "").strip()
    if pinned_bin:
        vsp_path = pinned_bin
        ok(f"Dung vsp da pin qua MCP_SAP_CONNECT_VSP_BIN: {vsp_path}")
    else:
        try:
            vsp_path = str(ensure_vsp())
        except VspSetupError as err:
            warn(f"Khong tai duoc vsp: {err}")
            info("Cai thu cong binary roi set MCP_SAP_CONNECT_VSP_BIN toi duong dan do, "
                 "hoac chay lai 'mcp-sap-connect mcp-setup' khi mang on dinh.")
            return

    try:
        cfg = load_config()
    except RuntimeError as err:
        warn(f"Khong doc duoc profile active: {err}")
        info("Chay 'mcp-sap-connect setup' truoc, roi 'mcp-setup' lai de dien SAP_ADT_URL cho vsp.")
        cfg = {}

    vsp_env = {"SAP_ADT_URL": cfg.get("btpUrl", "")}
    if cfg.get("authMode") == "password":
        try:
            secrets = asyncio.run(load_secrets())
        except Exception:
            secrets = {}
        if secrets.get("username") and secrets.get("password"):
            vsp_env["SAP_ADT_USER"] = secrets["username"]
            vsp_env["SAP_ADT_PASSWORD"] = secrets["password"]
    if "SAP_ADT_USER" not in vsp_env:
        warn("Profile hien tai khong dung password auth (hoac chua co username/password) - "
             "vsp can SAP_ADT_USER/SAP_ADT_PASSWORD rieng de ket noi ADT.")
        info("sap-vsp van duoc dang ky; dien 2 bien nay thu cong sau neu can debug/package health "
             "(xem KNOWN_LIMITATIONS.md).")

    ok(f"Dang ky sap-vsp ({vsp_path})...")
    register_fn("sap-vsp", "stdio", cmd=vsp_path, args=["mcp"], env=vsp_env)


def _cmd_mcp_setup() -> None:
    """Dang ky toan bo MCP servers voi Claude Code (bat buoc + tuy chon)."""
    header("MCP Server Setup — Dang ky MCP servers voi Claude Code")

    import shutil
    import subprocess

    claude_path = shutil.which("claude")
    if not claude_path:
        warn("Khong tim thay 'claude' trong PATH.")
        info("Hay cai Claude Code truoc, roi chay lai: mcp-sap-connect mcp-setup")
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
    _register("sap-btp", "stdio", cmd="mcp-sap-connect")
    ok("Dang ky sap-dict-bridge...")
    _register("sap-dict-bridge", "stdio", cmd="python",
              args=["-m", "mcp_sap_connect.bridge_server"])

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

    # --- ABAP deep analysis (tuy chon, side-by-side voi sap-connect) ---
    header("ABAP deep analysis - vibing-steampunk (tuy chon)")
    if ask("Dang ky sap-vsp (vibing-steampunk - package health/dead-code/debug)?",
           default="n").lower() in ("y", "yes"):
        _setup_vsp_server(_register)

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
        with open(os.path.expanduser(filepath), encoding="utf-8") as f:
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
            raise UserCancelled("cookie paste (Ctrl+C)") from None
        # da paste du lieu roi -> silent fallthrough
    return "\n".join(lines)


if __name__ == "__main__":
    main()



