"""HTTP client goi SAP BTP / S/4HANA API + ADT REST API cho ABAP.

Async, retry 429/5xx, auto-reconnect khi 401.
"""
from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlencode

import httpx

from .auth import (
    ReauthHandler,
    ReauthResult,
    ReauthStampedeGuard,
    SapAuth,
    SapCookieAuth,
)

REAUTH_COOLDOWN_S = 5.0  # Stampede: khong re-auth trong vong 5s sau lan cuoi


class SapClient:
    """REST client cho 1 profile SAP.

    Ho tro ca OAuth2 (client_credentials, password, bearer) va cookie auth.
    Khi session cookie / token het han:
      - OAuth2: tu dong refresh token
      - Cookie: goi reauth_handler (neu co) -> mo web popup cho user dang nhap lai
    """

    def __init__(
        self,
        profile_id: str | None = None,
        *,
        reauth_handler: ReauthHandler | None = None,
    ) -> None:
        self.profile_id = profile_id
        self.config: dict[str, Any] = {}

        # OAuth2 auth
        self.auth = SapAuth(profile_id)

        # Cookie-based auth (dung song song, tuy theo config)
        self.cookie_auth = SapCookieAuth(profile_id, reauth_handler=reauth_handler)

        # Stampede protection cho 401 re-auth (dung chung cho ca 2 loai)
        self._reauth_guard = ReauthStampedeGuard(cooldown_s=REAUTH_COOLDOWN_S)

        self._initialized = False
        self._keep_alive_task: asyncio.Task | None = None

    async def init(self) -> None:
        if self._initialized:
            return
        from ..config.store import load_config
        self.config = await _maybe_await(load_config(self.profile_id))
        await self.auth.init()
        await self.cookie_auth.init()
        self._initialized = True

    @property
    def auth_mode(self) -> str:
        return self.config.get("authMode", "oauth2")

    @property
    def use_cookie_auth(self) -> bool:
        return self.auth_mode == "cookie"

    def _base(self) -> str:
        return self.config["btpUrl"].rstrip("/")

    def _adt_base(self) -> str:
        return f"{self._base()}/sap/bc/adt"

    async def get(self, path: str, *, query: dict[str, Any] | None = None,
                   headers: dict[str, str] | None = None,
                   allow_404: bool = False, is_json: bool = True) -> Any:
        return await self._request("GET", path, query=query, headers=headers,
                                   allow_404=allow_404, is_json=is_json)

    async def post(self, path: str, body: Any = None, *,
                   query: dict[str, Any] | None = None,
                   headers: dict[str, str] | None = None,
                   is_json: bool = True) -> Any:
        return await self._request("POST", path, body=body, query=query,
                                   headers=headers, is_json=is_json)

    async def put(self, path: str, body: Any = None, *,
                  query: dict[str, Any] | None = None,
                  headers: dict[str, str] | None = None,
                  is_json: bool = True) -> Any:
        return await self._request("PUT", path, body=body, query=query,
                                   headers=headers, is_json=is_json)

    async def delete(self, path: str, *,
                     query: dict[str, Any] | None = None,
                     headers: dict[str, str] | None = None,
                     is_json: bool = True) -> Any:
        return await self._request("DELETE", path, query=query,
                                   headers=headers, is_json=is_json)

    async def _request(self, method: str, path: str, *,
                       body: Any = None, query: dict[str, Any] | None = None,
                       headers: dict[str, str] | None = None,
                       allow_404: bool = False, is_json: bool = True) -> Any:
        await self.init()
        url = self._build_url(path, query)

        # Lay token / cookies
        if self.use_cookie_auth:
            cookies = self.cookie_auth.get_cookies()
            authorization = None
        else:
            try:
                token = await self.auth.get_access_token()
            except Exception as err:
                raise RuntimeError(f"Khong lay duoc token: {err}") from err
            authorization = f"Bearer {token}"
            cookies = None

        is_adt = "/sap/bc/adt/" in path
        default_accept = "application/xml, */*" if is_adt else ("application/json" if is_json else "*/*")
        final_headers: dict[str, str] = {
            "Accept": default_accept,
        }
        if authorization:
            final_headers["Authorization"] = authorization
        if headers:
            final_headers.update(headers)
        if body is not None and is_json:
            final_headers["Content-Type"] = "application/json"

        timeout_s = (self.config.get("timeoutMs") or 30000) / 1000

        # ADT ghi (POST/PUT/DELETE) khong the gui literal "fetch" cho x-csrf-token -
        # phai xin token thuc truoc qua GET /core/discovery.
        if is_adt and method != "GET" and final_headers.get("x-csrf-token") == "fetch":
            final_headers["x-csrf-token"] = await self._fetch_csrf_token(cookies, authorization, timeout_s)
            if self.use_cookie_auth:
                # _fetch_csrf_token co the da tu reauth ben trong (session het han) ->
                # lay lai cookies moi nhat truoc khi gui request ghi chinh, tranh
                # dung nham cookies cu (da bi invalidate).
                cookies = self.cookie_auth.get_cookies()

        resp = await self._fetch_with_retry(
            method, url, final_headers, body, timeout_s, 2,
            cookies=cookies,
        )

        # === Xu ly session het han: 401 THAT SU, hoac SAP tra HTML/redirect
        # (nhieu tenant dung IAS/SAML SSO KHONG tra 401 chuan khi cookie het han -
        # ma tra 200 kem trang logon HTML, hoac 3xx redirect toi IdP) ===
        if self._looks_unauthenticated(resp) and self.config.get("autoReconnect", True):
            if self.use_cookie_auth:
                # Cookie auth: popup web cho user dang nhap lai
                reauthed = await self._handle_cookie_reauth()
                if reauthed:
                    fresh_cookies = self.cookie_auth.get_cookies()
                    resp = await self._fetch_with_retry(
                        method, url, final_headers, body, timeout_s, 2,
                        cookies=fresh_cookies,
                    )
            else:
                # OAuth2: refresh token
                await self.auth.invalidate()
                fresh = await self.auth.get_access_token()
                final_headers["Authorization"] = f"Bearer {fresh}"
                resp = await self._fetch_with_retry(
                    method, url, final_headers, body, timeout_s, 2,
                )

        if resp.status_code == 404 and allow_404:
            return None
        if resp.status_code >= 400:
            txt = resp.text[:500]
            raise RuntimeError(f"SAP {method} {path} -> {resp.status_code}: {txt}")

        # Sau khi reauth (hoac khong can), request ADT van tra ve HTML/redirect ->
        # session van khong hop le (reauth that bai/bi huy) - KHONG duoc coi day la
        # thanh cong (truoc day rot vao day va tra thang HTML nhu la "OK").
        if is_adt and self._looks_unauthenticated(resp):
            raise RuntimeError(
                f"SAP {method} {path} -> session khong hop le: nhan ve HTML/redirect "
                f"thay vi du lieu that (status {resp.status_code}). Co the reauth that "
                f"bai, bi huy, hoac cookie/token khong con quyen truy cap."
            )

        ct = resp.headers.get("content-type", "")
        return resp.json() if "json" in ct else resp.text

    @staticmethod
    def _looks_unauthenticated(resp: httpx.Response) -> bool:
        """SAP (dac biet tenant dung IAS/SAML SSO) thuong KHONG tra 401 chuan khi
        cookie session het han - ma tra 200 kem 1 trang HTML dang nhap, hoac 3xx
        redirect toi IdP. ADT/OData luon ky vong XML/JSON nen Content-Type HTML la
        dau hieu chac chan chua dang nhap, bat ke status code la gi. Thieu check nay
        khien reauth khong bao gio duoc kich hoat cho cac tenant loai nay (van dung
        cookie cu da invalid, "pass qua" ma khong dung lai xin dang nhap)."""
        if resp.status_code in (401, 302, 303, 307, 308):
            return True
        return "html" in resp.headers.get("content-type", "").lower()

    async def _handle_cookie_reauth(self) -> bool:
        """Xu ly re-auth cho cookie auth.

        Co stampede protection: nhieu request cung bi 401
        chi goi re-auth 1 lan (giong vibing-steampunk reauthMu + reauthCooldown).

        Khi stampede skip (cooldown), van tra ve True neu
        da co cookies tu thread khac -> request duoc retry.
        """
        try:
            result = await self._reauth_guard.guard(
                lambda: self.cookie_auth.reauth()
            )
            if result.cookies:
                await self.cookie_auth.save_cookies()
                return True
            # Stampede skip: thread khac da lay cookies, thu retry
            if self.cookie_auth.get_cookies():
                return True
            return False
        except Exception as err:
            raise RuntimeError(f"Re-auth that bai: {err}") from err

    async def _fetch_csrf_token(self, cookies: dict[str, str] | None,
                                 authorization: str | None, timeout_s: float) -> str:
        """Xin CSRF token thuc tu ADT discovery endpoint.

        ADT yeu cau GET voi header x-csrf-token: fetch truoc; token thuc
        nam trong response header cua GET nay, khong the dung literal "fetch"
        lam token de gui kem request ghi (POST/PUT/DELETE).

        Phai gui GET nay kem dung co che auth nhu request chinh (Authorization
        Bearer cho oauth2/password/bearer, hoac Cookie cho cookie-auth) - truoc day
        chi truyen cookies nen oauth2/password/bearer luon goi discovery o trang
        thai unauthenticated -> SAP tra ve khong co header x-csrf-token. Voi cookie
        auth, neu session da het han thi tu reauth (popup/Playwright) roi thu lai
        1 lan - neu khong discovery se fail ngay ma khong bao gio kich hoat lai dang
        nhap, du reauthMode=auto. Dung _looks_unauthenticated() thay vi chi check
        == 401, vi nhieu tenant SAML/IAS tra 200 (HTML logon page) hoac 3xx thay vi
        401 khi session het han - check == 401 don thuan se KHONG BAO GIO kich hoat
        reauth cho nhung tenant nay (cookie cu invalid van duoc dung lai vo han).
        """
        url = self._build_url("/sap/bc/adt/core/discovery", None)
        headers = {"Accept": "application/xml", "x-csrf-token": "fetch"}
        if authorization:
            headers["Authorization"] = authorization

        resp = await self._fetch_with_retry(
            "GET", url, headers, None, timeout_s, 2, cookies=cookies,
        )

        if self._looks_unauthenticated(resp) and self.use_cookie_auth and self.config.get("autoReconnect", True):
            if await self._handle_cookie_reauth():
                resp = await self._fetch_with_retry(
                    "GET", url, headers, None, timeout_s, 2,
                    cookies=self.cookie_auth.get_cookies(),
                )

        token = resp.headers.get("x-csrf-token", "")
        if not token:
            raise RuntimeError("Khong lay duoc CSRF token tu /sap/bc/adt/core/discovery.")
        return token

    async def check_write_access(self) -> str:
        """Kiem tra rieng kha nang GHI (activate/list_packages/run_unit_tests/syntax_check...):
        co xin duoc CSRF token thuc tu discovery khong.

        Doc du lieu (GET) va ghi du lieu (POST/PUT/DELETE) la 2 dieu kien khac nhau -
        GET co the qua (vd session con du de doc) trong khi CSRF-fetch van fail. Dung
        ham nay trong `connect` de connect test phan anh dung tinh trang, tranh bao
        "ket noi thanh cong" roi lenh ghi sau do lai fail.
        """
        await self.init()
        if self.use_cookie_auth:
            cookies = self.cookie_auth.get_cookies()
            authorization = None
        else:
            token = await self.auth.get_access_token()
            authorization = f"Bearer {token}"
            cookies = None
        timeout_s = (self.config.get("timeoutMs") or 30000) / 1000
        return await self._fetch_csrf_token(cookies, authorization, timeout_s)

    def start_keep_alive(self, interval_s: float = 300.0) -> None:
        """Bat 1 task nen tu dong "ping" SAP dinh ky de giu session song -
        dac biet quan trong voi cookie auth: nhieu SAP tenant het session vi
        IDLE timeout (khong hoat dong 1 khoang), khong phai vi het thoi gian
        tuyet doi - ping dinh ky giu session "duoc dung" nen khong bao gio
        idle du lau de bi huy, giam han so lan phai bat lai popup dang nhap.

        Port tu vibing-steampunk pkg/adt/client.go StartKeepAlive() + http.go
        Ping() - ho dung interval mac dinh 300s (5 phut) voi ghi chu nguyen
        van: "interval nen ngan hon session timeout cua SAP server; 5 phut la
        gia tri hop ly". Ping() ben Go = goi lai chinh ham xin CSRF token (ho
        khong co logic rieng) - o day dung lai check_write_access() cho dung
        tinh chat.

        Goi lai se tu dung task cu truoc khi bat task moi (giong ban goc).
        Ping khong co reauth_handler rieng (client tao qua ham nay thuong
        khong duoc gan reauth_handler) - neu session da chet that su luc ping,
        se fail am tham (khong tu bat popup dang nhap ngoai y muon trong luc
        nen) - lan goi tool that su tiep theo se tu xu ly reauth binh thuong.
        """
        self.stop_keep_alive()
        self._keep_alive_task = asyncio.ensure_future(self._keep_alive_loop(interval_s))

    def stop_keep_alive(self) -> None:
        if self._keep_alive_task and not self._keep_alive_task.done():
            self._keep_alive_task.cancel()
        self._keep_alive_task = None

    async def _keep_alive_loop(self, interval_s: float) -> None:
        while True:
            await asyncio.sleep(interval_s)
            try:
                await self.check_write_access()
            except Exception:
                pass  # best-effort - loi that su se lo dien o lan goi tool tiep theo

    def _build_url(self, path: str, query: dict[str, Any] | None) -> str:
        base = path if path.startswith("http") else f"{self._base()}/{path.lstrip('/')}"
        if query:
            qs = urlencode({k: v for k, v in query.items() if v is not None and v != ""})
            if qs:
                base = f"{base}?{qs}"
        return base

    async def _fetch_with_retry(
        self, method: str, url: str, headers: dict[str, str],
        body: Any, timeout_s: float, attempts: int,
        cookies: dict[str, str] | None = None,
    ) -> httpx.Response:
        last_err: Exception | None = None
        for i in range(attempts):
            try:
                async with httpx.AsyncClient(timeout=timeout_s) as ac:
                    req_headers = dict(headers)
                    if cookies:
                        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
                        req_headers["Cookie"] = cookie_header

                    if method == "GET":
                        resp = await ac.get(url, headers=req_headers)
                    elif method == "PUT":
                        json_body = body if (body is not None and "Content-Type" in headers
                                             and "json" in headers["Content-Type"]) else None
                        data_body = body if json_body is None else None
                        if json_body is not None:
                            resp = await ac.put(url, headers=req_headers, json=json_body)
                        else:
                            resp = await ac.put(url, headers=req_headers, data=data_body)
                    elif method == "DELETE":
                        resp = await ac.delete(url, headers=req_headers)
                    else:
                        json_body = body if (body is not None and "Content-Type" in headers
                                             and "json" in headers["Content-Type"]) else None
                        data_body = body if json_body is None else None
                        if json_body is not None:
                            resp = await ac.post(url, headers=req_headers, json=json_body)
                        else:
                            resp = await ac.post(url, headers=req_headers, data=data_body)
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    await asyncio.sleep(0.25 * (i + 1))
                    continue
                return resp
            except Exception as err:
                last_err = err
                await asyncio.sleep(0.25 * (i + 1))
        raise last_err or RuntimeError("Het luot retry.")

    # ============ Helper ABAP / ADT ===================================
    async def list_packages(self, parent: str = "") -> Any:
        # nodestructure la POST-only endpoint (GET -> 405); can CSRF token thuc.
        return await self.post("/sap/bc/adt/repository/nodestructure", query={
            "parent_type": "DEVC",
            "parent_name": parent or "$TMP",
            "withShortDescriptions": "true",
        }, headers={"x-csrf-token": "fetch"})

    async def search_objects(self, query: str, object_type: str = "") -> Any:
        return await self.get("/sap/bc/adt/repository/informationsystem/search", query={
            "operation": "quickSearch",
            "query": query,
            "maxResults": 50,
            "objectType": object_type,
        })

    async def read_source(self, object_uri: str, object_type: str) -> Any:
        from urllib.parse import quote
        enc = quote(object_uri, safe="")
        t = quote(object_type, safe="")
        kind = "classes" if object_type == "CLAS" else "programs"
        path = f"/sap/bc/adt/oo/{kind}/{enc}/source/main"
        return await self.get(path, headers={"Accept": "text/plain"}, is_json=False)

    async def syntax_check(self, object_uri: str, object_type: str) -> Any:
        return await self.post(
            "/sap/bc/adt/checkruns",
            body={"objectUri": object_uri, "objectType": object_type, "runType": "syntax"},
            headers={"x-csrf-token": "fetch"},
        )

    async def activate(self, object_uri: str, object_type: str) -> Any:
        return await self.post(
            "/sap/bc/adt/activation",
            body={"objectUri": object_uri, "objectType": object_type, "transport": ""},
            headers={"x-csrf-token": "fetch"},
        )

    # ============ New tools ===========================================
    async def find_where_used(self, object_name: str, object_type: str) -> Any:
        """Tim noi su dung 1 object (where-used list)."""
        return await self.get(
            "/sap/bc/adt/repository/informationsystem/usage",
            query={
                "operation": "whereUsed",
                "objectName": object_name,
                "objectType": object_type,
            },
        )

    async def execute_query(self, table_name: str, object_type: str = "TABL", top: int = 50) -> Any:
        """Truy van du lieu tu 1 bang / CDS view.

        Su dung ADT data preview endpoint, tra ve top dong.
        objectType: TABL (bang), DDLS (CDS view), VIEW (view)...
        """
        return await self.get(
            "/sap/bc/adt/data/preview",
            query={
                "objectName": table_name,
                "objectType": object_type,
                "maxRows": str(top),
            },
        )

    async def run_unit_tests(self, object_uri: str, object_type: str) -> Any:
        """Chay ABAP Unit tests cho 1 class."""
        return await self.post(
            "/sap/bc/adt/abapunit/testruns",
            body={
                "objectUri": object_uri,
                "objectType": object_type,
                "runMode": "all",
            },
            headers={"x-csrf-token": "fetch"},
        )

    async def get_system_info(self) -> Any:
        """Lay thong tin he thong SAP (version, release, database...)."""
        return await self.get("/sap/bc/adt/core/discovery", query={"scope": "all"})

    async def analyze_dump(self, dump_id: str | None = None, top: int = 20) -> Any:
        """Doc phan tich ST22 dump.

        Neu khong co dump_id, lay top dump gan nhat.
        """
        if dump_id:
            from urllib.parse import quote
            return await self.get(f"/sap/bc/adt/runtime/dumps/{quote(dump_id, safe='')}")
        return await self.get(
            "/sap/bc/adt/runtime/dumps",
            query={"maxResults": str(top)},
        )


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value
