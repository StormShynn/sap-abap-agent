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
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Iterable

import httpx

from ..config.store import load_config
from ..config.secrets import load_secrets, update_secrets

SAFETY_MARGIN_S = 30  # refresh som 30s truoc khi het han


# ===== Reauth types ================================================

@dataclass
class ReauthResult:
    """Ket qua tu re-auth: cookies moi hoac token moi."""
    cookies: dict[str, str] = field(default_factory=dict)
    access_token: str = ""
    expires_at: float = 0.0


ReauthHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, ReauthResult]]


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
        if self.secrets.get("accessToken") and self.secrets.get("expiresAt"):
            if time.time() < self.secrets["expiresAt"] - SAFETY_MARGIN_S:
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
        btp_url = self.config["btpUrl"].rstrip("/")
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
        """Luu cookies hien tai vao secrets de dung lai sau."""
        from ..config.secrets import update_secrets as upsert
        await upsert(self.profile_id, {"cookies": self._cookies})

    async def invalidate(self) -> None:
        """Xoa cookies + reset stampede."""
        self._cookies.clear()
        self._stampede.invalidate()


# ===== Web popup login helper ======================================

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

    login_url = f"{base_url.rstrip('/')}/sap/bc/adt/core/discovery"
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
                break
            lines.append(line.strip())
    except (EOFError, KeyboardInterrupt):
        pass

    cookie_str = " ".join(lines)
    if not cookie_str.strip():
        print("\n  ⚠️ Khong nhan duoc cookie. Thu lai sau.")
        return ReauthResult()

    cookies = _parse_cookie_string(cookie_str)

    if _session_cookie_names(cookies):
        print(f"\n  ✅ Da nhan {len(cookies)} cookies (co session cookie). Tiep tuc!")
    else:
        print(f"\n  ⚠️ Da nhan {len(cookies)} cookies nhung khong thay MYSAPSSO2 / SAP_SESSIONID.")
        print("     Co the can dang nhap lai hoac copy dung cookies.")

    return ReauthResult(cookies=cookies)


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

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        login_url = f"{base_url.rstrip('/')}/sap/bc/adt/core/discovery"
        await page.goto(login_url)

        print("  👉 Vui long dang nhap trong cua so trinh duyet (cho toi 5 phut)...")

        # Cho user dang nhap that su: poll session cookie xuat hien, KHONG dung
        # wait_for_url("**/sap/bc/adt/**") vi URL vua goto() da khop pattern nay
        # ngay lap tuc (chua he dang nhap), khien code chay tiep qua som.
        deadline = time.monotonic() + 300  # 5 phut, dong bo voi timeout cu
        logged_in = False
        while time.monotonic() < deadline:
            current = {c["name"] for c in await context.cookies()}
            if _session_cookie_names(current):
                logged_in = True
                break
            await page.wait_for_timeout(1000)

        if logged_in:
            # Cho request/redirect cuoi cung (sau submit form) hoan tat truoc khi doc cookie
            await page.wait_for_timeout(1500)
        else:
            print("  ⏰ Timeout cho login. Lay cookies hien tai...")

        cookies_raw = await context.cookies()
        cookies = {c["name"]: c["value"] for c in cookies_raw}
        await browser.close()

    if cookies:
        found = _session_cookie_names(cookies)
        if found:
            print(f"  ✅ Da lay duoc {len(cookies)} cookies (gom {', '.join(found)}). Tiep tuc!")
        else:
            print(f"  ⚠️ Da lay {len(cookies)} cookies nhung thieu session cookies.")
    else:
        print("  ❌ Khong lay duoc cookies nao.")

    return ReauthResult(cookies=cookies)


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
