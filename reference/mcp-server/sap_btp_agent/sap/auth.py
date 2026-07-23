"""OAuth2 + Cookie-based auth cho SAP BTP (xsuaa / IAS / SAP GUI).

Ho tro:
  - client_credentials (clientId + clientSecret)
  - password grant (username/password)
  - bearer tinh (token user nhap tay)
  - cookie-based (MYSAPSSO2, SAP_SESSIONID, sap-usercontext)
    + Tu dong popup web browser khi session het han de user dang nhap lai
"""
from __future__ import annotations

import asyncio
import contextlib
import os
import time
from collections.abc import Callable, Coroutine, Iterable
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config.secrets import load_secrets, update_secrets
from ..config.store import load_config

SAFETY_MARGIN_S = 30  # refresh som 30s truoc khi het han


# ===== Reauth types ================================================

@dataclass
class ReauthResult:
    """Ket qua tu re-auth: cookies moi hoac token moi."""
    cookies: dict[str, str] = field(default_factory=dict)
    access_token: str = ""
    expires_at: float = 0.0


ReauthHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, "ReauthResult"]]


class ReauthCancelled(Exception):
    """User da huy thu cong (Ctrl+C / EOF) giua luong dang nhap lai.

    Caller (CLI) bat exception nay de thoat sach: KHONG traceback, KHONG save
    cookie rac/cookie rong len disk, KHONG dong cookie cu con han.
    """

    def __init__(self, where: str = "?"):
        super().__init__(f"Reauth cancelled at {where}")
        self.where = where


# ===== Stampede protection =========================================

class ReauthStampedeGuard:
    """Chong nhieu request dong thoi cung goi re-auth.

    Giong stampede protection ben vibing-steampunk (reauthMu + reauthCooldown).
    - Chi 1 goroutine duoc re-auth 1 lan
    - Cac goroutine khac cho lock, neu re-auth da xong trong cooldown -> skip
    """

    def __init__(self, cooldown_s: float = 5.0):
        self._lock = asyncio.Lock()
        self._last_reauth: float = 0.0
        self._cooldown = cooldown_s

    async def guard(self, reauth_func: Callable[[], Coroutine[Any, Any, ReauthResult]]) -> ReauthResult:
        async with self._lock:
            now = time.time()
            if self._last_reauth > 0 and (now - self._last_reauth) < self._cooldown:
                # Co goroutine khac da re-auth thanh cong, bo qua
                return ReauthResult()

            result = await reauth_func()
            self._last_reauth = time.time()
            return result

    def invalidate(self) -> None:
        self._last_reauth = 0.0


# ===== OAuth2 Auth =================================================

class SapAuth:
    """Quan ly OAuth2 token cho 1 profile SAP."""

    def __init__(self, profile_id: str | None = None) -> None:
        self.profile_id = profile_id
        self.config: dict[str, Any] = {}
        self.secrets: dict[str, Any] = {}
        self._mem_token: str | None = None
        self._mem_expires_at: float = 0.0

    async def init(self) -> None:
        self.config = await _maybe_await(load_config(self.profile_id))
        self.secrets = await load_secrets(self.profile_id)
        if (
            self.secrets.get("accessToken")
            and self.secrets.get("expiresAt")
            and time.time() < self.secrets["expiresAt"] - SAFETY_MARGIN_S
        ):
            self._mem_token = self.secrets["accessToken"]
            self._mem_expires_at = float(self.secrets["expiresAt"])

    def is_ready(self) -> bool:
        return bool(self.config and self.config.get("btpUrl") and self.config.get("clientId"))

    async def get_access_token(self) -> str:
        # Con han trong bo nho
        if self._mem_token and time.time() < self._mem_expires_at - SAFETY_MARGIN_S:
            return self._mem_token
        # Bearer tinh
        if self.config.get("authMode") == "bearer":
            token = self.secrets.get("accessToken")
            if not token:
                raise RuntimeError("Chua co bearer token. Chay setup.")
            self._mem_token = token
            self._mem_expires_at = float("inf")
            return self._mem_token
        # Lay moi
        return await self._fetch_new_token()

    async def _fetch_new_token(self) -> str:
        self.config["btpUrl"].rstrip("/")
        client_id = self.config["clientId"]
        auth_mode = self.config.get("authMode", "oauth2")
        scope = self.config.get("scope", "")
        token_url = self._resolve_token_url()

        if auth_mode == "password" and self.secrets.get("username") and self.secrets.get("password"):
            form: dict[str, str] = {
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": self.secrets.get("clientSecret", "") or "",
                "username": self.secrets["username"],
                "password": self.secrets["password"],
            }
        else:
            if not self.secrets.get("clientSecret"):
                raise RuntimeError("Chua co client_secret. Chay setup.")
            form = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": self.secrets["clientSecret"],
            }
        if scope:
            form["scope"] = scope

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                token_url,
                data=form,
                headers={"Accept": "application/json"},
            )
        if resp.status_code >= 400:
            raise RuntimeError(f"OAuth2 that bai {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        expires_in = int(data.get("expires_in") or 3600)
        token = data["access_token"]
        expires_at = time.time() + expires_in
        self._mem_token = token
        self._mem_expires_at = expires_at
        await update_secrets(self.profile_id, {
            "refreshToken": data.get("refresh_token"),
            "expiresAt": expires_at,
            "tokenUrl": token_url,
            # Aliases cho license module (get_oauth_status).
            "access_token": token,
            "token_expires_at": expires_at,
            "saved_at": time.time(),
        })
        return token

    def _resolve_token_url(self) -> str:
        custom = self.secrets.get("tokenUrl")
        if custom:
            return custom
        return f"{self.config['btpUrl'].rstrip('/')}/oauth/token"

    async def invalidate(self) -> None:
        self._mem_token = None
        self._mem_expires_at = 0.0


# ===== Cookie Auth =================================================

class SapCookieAuth:
    """Quan ly SAP session cookies + tu dong re-auth qua web popup khi het han.

    Khi session cookie het han (401), tu dong:
      1. Mo trinh duyet web cho user dang nhap lai
      2. Lay cookie moi tu trinh duyet
      3. Tiep tuc request voi cookie moi

    Giong co che ReauthFunc ben vibing-steampunk (pkg/adt/http.go).
    """

    def __init__(
        self,
        profile_id: str | None = None,
        *,
        reauth_handler: ReauthHandler | None = None,
    ) -> None:
        self.profile_id = profile_id
        self.config: dict[str, Any] = {}
        self.secrets: dict[str, Any] = {}

        # Cookies hien tai (luu in-memory)
        self._cookies: dict[str, str] = {}

        # Callback de lay cookie moi khi session het han
        self._reauth_handler = reauth_handler

        # Stampede protection
        self._stampede = ReauthStampedeGuard(cooldown_s=5.0)

    async def init(self) -> None:
        self.config = await _maybe_await(load_config(self.profile_id))
        self.secrets = await load_secrets(self.profile_id)

        # Khoi phuc cookies tu secrets (neu co)
        saved = self.secrets.get("cookies")
        if isinstance(saved, dict):
            self._cookies = saved

    def get_cookies(self) -> dict[str, str]:
        return dict(self._cookies)

    def set_cookies(self, cookies: dict[str, str]) -> None:
        self._cookies = dict(cookies)

    def is_ready(self) -> bool:
        return bool(self.config and self.config.get("btpUrl"))

    def has_session(self) -> bool:
        return bool(_session_cookie_names(self._cookies))

    async def reauth(self, ctx: dict[str, Any] | None = None) -> ReauthResult:
        """Goi re-auth callback de lay cookies moi.

        Co stampede protection: nhieu request cung bi 401 chi 1 lan re-auth.
        """
        if self._reauth_handler is None:
            raise RuntimeError(
                "Cookie session expired nhung khong co reauth_handler. "
                "Hay cau hinh reauth_handler hoac chay lai sap-btp-agent setup."
            )

        merged_ctx = {
            "profile_id": self.profile_id,
            "base_url": self.config.get("btpUrl", ""),
            ** (ctx or {}),
        }

        result = await self._stampede.guard(
            lambda: self._reauth_handler(merged_ctx)  # type: ignore
        )

        if result.cookies:
            self._cookies.update(result.cookies)
        if result.access_token:
            self._cookies["access_token"] = result.access_token

        return result

    async def save_cookies(self) -> None:
        """Luu cookies hien tai vao secrets de dung lai sau.

        Dong thoi luu saved_at + cookie_expires_at (uoc luong = now + 8h) de
        license module co the canh bao sap het han.
        """
        import time as _t

        from ..config.secrets import update_secrets as upsert
        now = _t.time()
        # Uoc luong: 8h cho SAP cookie (co the override qua config cookieMaxAgeHours)
        try:
            from ..config.store import load_config
            cfg = load_config(self.profile_id)
            max_age_h = float(cfg.get("cookieMaxAgeHours", 8.0))
        except Exception:
            max_age_h = 8.0
        await upsert(self.profile_id, {
            "cookies": self._cookies,
            "saved_at": now,
            "cookie_expires_at": now + max_age_h * 3600,
            "cookie_max_age_hours": max_age_h,
        })

    async def invalidate(self) -> None:
        """Xoa cookies + reset stampede."""
        self._cookies.clear()
        self._stampede.invalidate()


# ===== Web popup login helper ======================================

async def _verify_discovery_session(base_url: str, cookies: dict[str, str]) -> bool:
    """Goi thuc GET /sap/bc/adt/core/discovery voi cookies hien tai de xac nhan
    da THUC SU dang nhap duoc backend ABAP.

    Chi dua vao TEN cookie xuat hien (vd 'sap-usercontext') la khong du: trong
    luong IAS/SAML, cookie nay co the xuat hien som (o buoc trung gian cua chuoi
    redirect) truoc khi ICF thuc su cap session cho ung dung ABAP, khien code
    tuong da dang nhap xong qua som roi dong browser/ket thuc paste, dan toi
    CSRF-fetch sau do van fail vi cookie thu duoc chua du quyen.
    """
    if not cookies:
        return False
    url = f"{base_url.rstrip('/')}/sap/bc/adt/core/discovery"
    cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                url,
                headers={"Accept": "application/xml", "Cookie": cookie_header},
            )
    except Exception:
        return False
    if resp.status_code >= 400 or resp.status_code in (302, 303, 307, 308):
        return False
    return "html" not in resp.headers.get("content-type", "").lower()


async def _launch_real_browser(pw):
    """Uu tien mo Edge/Chrome THAT da cai san tren may, thay vi Chromium rieng
    Playwright tu tai ve. Fallback ve Chromium bundled neu khong co channel nao.

    Ly do (vibing-steampunk - repo Go cung tac gia, da chay on cho SAP SSO -
    dung dung binary browser that qua duong dan exe, khong dung ban tai rieng):
    mot so co che SSO cong ty (Windows Integrated Auth/Kerberos, chung chi may,
    extension) chi hoat dong day du tren browser cai that, co the thieu trong
    Chromium bundled cua Playwright chay o profile cach ly.
    """
    for channel in ("msedge", "chrome"):
        try:
            return await pw.chromium.launch(headless=False, channel=channel)
        except Exception:
            continue
    return await pw.chromium.launch(headless=False)


async def web_login_popup(ctx: dict[str, Any]) -> ReauthResult:
    """Mo trinh duyet web cho user dang nhap SAP, tu dong lay cookie moi.

    Day la ReauthHandler mau, co the dung truc tiep hoac tuy bien.

    Luong xu ly:
      1. In huong dan ra terminal
      2. Mo trinh duyet web (webbrowser.open) toi SAP login page
      3. User dang nhap thu cong
      4. Sau do user paste cookie vao terminal
      5. Tra ve ReauthResult voi cookies moi
    """
    import webbrowser

    base_url = ctx.get("base_url", "")
    profile_id = ctx.get("profile_id", "?")

    print()
    print("=" * 60)
    print("  🔐 SESSION SAP DA HET HAN!")
    print("=" * 60)
    print()
    print(f"  Profile : {profile_id}")
    print(f"  URL     : {base_url}")
    print()
    print("  Dang mo trinh duyet web cho ban dang nhap...")
    print()

    # ADT root (HTML) thay vi /core/discovery (XML) - tranh Chrome/Edge tu tai
    # XML ve nhu file thay vi hien trang dang nhap (cung ly do nhu web_login_auto).
    login_url = f"{base_url.rstrip('/')}/sap/bc/adt/"
    webbrowser.open(login_url)

    print("  👉 Da mo trinh duyet. Vui long dang nhap SAP cua ban.")
    print()
    print("  Sau khi dang nhap xong, LAM THEO CAC BUOC SAU:")
    print("  1. Mo Developer Tools (F12) -> Application -> Cookies")
    print("  2. Copy tat ca cookies (name=value; name2=value2)")
    print("  3. Paste xuong duoi day:")
    print()

    import sys
    eof_hint = "Ctrl+Z roi Enter" if os.name == "nt" else "Ctrl+D"
    sys.stdout.write(f"  Cookie string (paste vao day, Enter, {eof_hint}):\n  ")
    sys.stdout.flush()

    lines = []
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                # Ctrl+D / Ctrl+Z+Enter: stdin dong, KHONG co du lieu -> huy that
                if not lines:
                    raise ReauthCancelled("cookie paste (stdin closed)")
                break
            lines.append(line.strip())
    except KeyboardInterrupt:
        # Ctrl+C: phan biet voi user paste xong roi muon thoat.
        # Neu chua co gi paste -> huy that. Neu da co 1+ dong -> tiep tuc xu ly.
        if not lines:
            print()
            raise ReauthCancelled("cookie paste (Ctrl+C)") from None
        # co du lieu roi -> silent fallthrough, xu ly tiep ben duoi

    cookie_str = " ".join(lines)
    if not cookie_str.strip():
        print("\n  ⚠️ Khong nhan duoc cookie. Thu lai sau.")
        raise ReauthCancelled("cookie paste (empty)")

    cookies = _parse_cookie_string(cookie_str)

    if await _verify_discovery_session(base_url, cookies):
        print(f"\n  ✅ Da nhan {len(cookies)} cookies - xac nhan goi duoc ADT discovery. Tiep tuc!")
        return ReauthResult(cookies=cookies)
    elif _session_cookie_names(cookies):
        print(f"\n  ⚠️ Da nhan {len(cookies)} cookies (co ten giong session) nhung goi thu "
              f"discovery van chua qua - co the client/quyen ADT chua du, hoac dang nhap chua xong.")
        print("     Van chap nhan vi co session-cookie. Neu lan sau bi loi, hay copy lai cookies.")
        return ReauthResult(cookies=cookies)
    else:
        # Paste chi co cookie rac (VD 1 dong debug) -> KHONG save de tranh
        # ghi de cookie cu con han trong secrets.json.
        print(f"\n  ❌ Da nhan {len(cookies)} cookies nhung khong thay MYSAPSSO2 / SAP_SESSIONID.")
        print("     Cookie cu cua ban KHONG bi thay doi. Thu lai va copy DUNG cookies tu DevTools.")
        raise ReauthCancelled("cookie paste (no session cookie)")


async def web_login_auto(ctx: dict[str, Any]) -> ReauthResult:
    """Tu dong mo browser, cho user dang nhap, tu dong trich xuat cookies.

    Yeu cau: playwright (`pip install playwright`).
    Tu dong phat hien khi user dang nhap xong.
    """
    base_url = ctx.get("base_url", "")
    profile_id = ctx.get("profile_id", "?")

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("⚠️ playwright chua duoc cai dat. Fallback ve manual paste.")
        return await web_login_popup(ctx)

    print()
    print("=" * 60)
    print("  🔐 SESSION SAP DA HET HAN!")
    print("=" * 60)
    print(f"\n  Profile : {profile_id}")
    print(f"  URL     : {base_url}")
    print("\n  Mo browser cho ban dang nhap...")
    print("  Sau khi dang nhap xong, browser se tu dong dong.")
    print()

    pw = None
    browser = None
    try:
        pw = await async_playwright().start()
        browser = await _launch_real_browser(pw)
        context = await browser.new_context()
        page = await context.new_page()

        # In real-time moi buoc redirect/navigation cua trang chinh ra terminal -
        # de biet ngay dang ket o dau (vd dung y tai /sap/saml2/sp/acs/080) thay
        # vi chi thay dong "dang cho" tinh, khong biet co tien trien hay khong.
        def _log_nav(frame):
            if frame == page.main_frame:
                print(f"     → {frame.url}")
        page.on("framenavigated", _log_nav)

        # login_url tro toi ADT root (HTML) thay vi /core/discovery (XML) - XML
        # khong co renderer trong Chrome nen se bi tai ve nhu file thay vi hien
        # trang, gay nham lan. Van giu handler huy download ben duoi de phong khi
        # redirect chain van roi vao 1 URL XML nao do.
        page.on("download", lambda dl: asyncio.ensure_future(dl.cancel()))

        login_url = f"{base_url.rstrip('/')}/sap/bc/adt/"
        with contextlib.suppress(Exception):
            await page.goto(login_url)
            # SSO redirect (Kerberos 401, SAML...) hay khien goto() bao loi
            # ERR_ABORTED ngay lap tuc - khong fatal, browser van o lai va tiep
            # tuc redirect, vong poll ben duoi se tu kiem tra tiep.

        # In huong dan cho user biet co the ket thuc som
        print("  👉 Vui long dang nhap trong cua so trinh duyet (timeout 30s)...")
        print("     (Bam Ctrl+C de HUY va giu nguyen cookie cu - khong bi ghi de)")
        print("     (Hoac BAM ENTER trong terminal / nut OK trong GUI de KET THUC SOM)")

        # Cho user dang nhap that su: poll session cookie xuat hien, KHONG dung
        # wait_for_url("**/sap/bc/adt/**") vi URL vua goto() da khop pattern nay
        # ngay lap tuc (chua he dang nhap), khien code chay tiep qua som.
        #
        # 3 dieu kien de considered "user da dang nhap xong" (tinh theo thu tu uu tien):
        #  1. External signal: ctx[early_finish_event].is_set() (user bam Enter/OK)
        #  2. Session cookie xuat hien + verify discovery OK (session that su)
        #  3. URL on dinh 3s lien tiep (user da ket thuc thao tac, co the SSO nhanh)
        #
        # Trong ca 3 truong hop, verify them 1 request GET discovery that de chan
        # truong hop session cookie xuat hien o buoc redirect trung gian cua SAML/IAS.

        # Lay early_finish_event (co the None neu caller khong cung cap)
        early_event = ctx.get("early_finish_event")

        URL_STABLE_S = 3.0  # URL giu nguyen 3s -> coi nhu user da xong
        POLL_INTERVAL_S = 0.2
        # So poll lien tiep de co 3s o dinh (poll 200ms)
        URL_STABLE_POLLS = int(URL_STABLE_S / POLL_INTERVAL_S)

        deadline = time.monotonic() + 30
        logged_in = False
        last_url = ""
        url_stable_count = 0
        finish_reason = ""

        while time.monotonic() < deadline:
            current_cookies = {c["name"]: c["value"] for c in await context.cookies()}
            current_url = page.url
            has_session = bool(_session_cookie_names(current_cookies))
            discovery_ok = False
            if has_session:
                discovery_ok = await _verify_discovery_session(base_url, current_cookies)

            # Dieu kien 1: external signal (user bam Enter/OK)
            if early_event is not None and early_event.is_set():
                if has_session and discovery_ok:
                    finish_reason = "user-confirmed"
                    logged_in = True
                    break
                else:
                    print("  ⏳ User bam nút OK nhung chua co session hop le, cho them...")
                    early_event.clear()  # reset, doi lan nua

            # Dieu kien 2: session + discovery OK (session that su)
            if has_session and discovery_ok:
                finish_reason = "session-detected"
                logged_in = True
                break

            # Dieu kien 3: URL on dinh (poll lien tiep thay URL khong doi)
            if current_url == last_url and current_url:
                url_stable_count += 1
            else:
                url_stable_count = 0
                last_url = current_url
            if url_stable_count >= URL_STABLE_POLLS:
                # URL on dinh 3s nhung chua co session -> van thu lay cookies hien
                # tai (co the user da o trang loi hoac SSO da xong nhung cookie ten khac).
                finish_reason = "url-stable"
                logged_in = has_session  # chi logged_in neu co session
                break

            await page.wait_for_timeout(int(POLL_INTERVAL_S * 1000))

        if not logged_in and not finish_reason:
            print("  ⏰ Timeout 30s. Lay cookies hien tai...")
            finish_reason = "timeout"

        if finish_reason == "user-confirmed":
            print("  ✓ User da xac nhan (Enter/OK) - lay cookies.")
        elif finish_reason == "url-stable":
            print(f"  ✓ URL on dinh {URL_STABLE_S}s - lay cookies.")
        elif finish_reason == "session-detected":
            print("  ✓ Session cookie + ADT discovery OK - lay cookies.")

        if logged_in:
            # Cho request/redirect cuoi cung (sau submit form) hoan tat truoc khi doc cookie
            await page.wait_for_timeout(1500)

        cookies_raw = await context.cookies()
        cookies = {c["name"]: c["value"] for c in cookies_raw}
    except KeyboardInterrupt:
        print()
        raise ReauthCancelled("Playwright login (Ctrl+C)") from None
    finally:
        # Dam bao browser + Playwright luon duoc dong khi:
        #  - User bam Ctrl+C giua luong (KeyboardInterrupt)
        #  - Timeout 30s ma chua dang nhap xong
        #  - Exception bat ky khi mo browser
        if browser is not None:
            with contextlib.suppress(Exception):
                await browser.close()
        if pw is not None:
            with contextlib.suppress(Exception):
                await pw.stop()

    if cookies:
        found = _session_cookie_names(cookies)
        if found:
            print(f"  ✅ Da lay duoc {len(cookies)} cookies (gom {', '.join(found)}). Tiep tuc!")
            return ReauthResult(cookies=cookies)
        else:
            # Cookie khong co session-cookie -> KHONG save de tranh ghi de cookie
            # cu con han trong secrets.json.
            print(f"  ❌ Da lay {len(cookies)} cookies nhung thieu session cookies (MYSAPSSO2/SAP_SESSIONID).")
            print("     Cookie cu cua ban KHONG bi thay doi. Thu lai va dam bao da dang nhap xong.")
            raise ReauthCancelled("Playwright login (no session cookie)")

    print("  ❌ Khong lay duoc cookies nao.")
    raise ReauthCancelled("Playwright login (no cookies)")


def _parse_cookie_string(cookie_str: str) -> dict[str, str]:
    """Parse cookie string: 'key1=val1; key2=val2' -> dict."""
    cookies: dict[str, str] = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            key, val = part.split("=", 1)
            cookies[key.strip()] = val.strip()
    return cookies


# Ten cookie session SAP thuong gap. SAP_SESSIONID co the co suffix
# he thong/client (VD: SAP_SESSIONID_S4H_100) nen phai match prefix,
# khong the so khop tuyet doi.
_SESSION_COOKIE_PREFIXES = ("MYSAPSSO2", "SAP_SESSIONID")
_SESSION_COOKIE_EXACT = {"sap-contextid", "sap-usercontext"}


def _session_cookie_names(cookies: Iterable[str]) -> list[str]:
    """Loc ra cac ten cookie duoc xem la session cookie SAP hop le.

    Nhan dict (name -> value) hoac bat ky iterable ten cookie nao (VD set tra
    ve tu Playwright context.cookies()).
    """
    return [
        name for name in cookies
        if name.upper().startswith(_SESSION_COOKIE_PREFIXES) or name.lower() in _SESSION_COOKIE_EXACT
    ]


def _parse_netscape_cookie_line(line: str) -> tuple[str, str] | None:
    """Parse 1 dong Netscape cookie file: domain, flag, path, secure, expiration, name, value."""
    parts = line.split("\t")
    if len(parts) >= 7:
        return parts[5], parts[6]
    return None


def _parse_netscape_cookie_text(text: str) -> dict[str, str]:
    """Parse noi dung Netscape cookie file (hoac paste truc tiep noi dung file nay).

    Dong khong dung 7-cot tab-separated nhung co dang 'name=value' duoc hieu
    nhu fallback (giu tuong thich voi file mix ca 2 dinh dang).
    """
    cookies: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = _parse_netscape_cookie_line(line)
        if parsed:
            cookies[parsed[0]] = parsed[1]
        elif "=" in line:
            key, val = line.split("=", 1)
            cookies[key.strip()] = val.strip()
    return cookies


def _looks_like_netscape_text(text: str) -> bool:
    """Nhan dien noi dung Netscape cookie file: header '# Netscape...' hoac
    dong dau la 7 cot tab-separated."""
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.upper().startswith("# NETSCAPE") or stripped.upper().startswith("# HTTP COOKIE FILE"):
        return True
    first_line = stripped.splitlines()[0]
    return len(first_line.split("\t")) >= 7


# ===== Helpers =====================================================

async def _maybe_await(value: Any) -> Any:
    """Helper: mot so wrapper async tra ve coroutine, mot so tra ve gia tri."""
    if asyncio.iscoroutine(value):
        return await value
    return value

