"""HTTP client goi SAP BTP / S/4HANA API + ADT REST API cho ABAP.

Async, retry 429/5xx, auto-reconnect khi 401.
"""
from __future__ import annotations

import asyncio
import contextlib
import re
from typing import Any
from urllib.parse import urlencode

import httpx

from .auth import (
    ReauthHandler,
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
            return bool(self.cookie_auth.get_cookies())
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

        if (
            self._looks_unauthenticated(resp)
            and self.use_cookie_auth
            and self.config.get("autoReconnect", True)
            and await self._handle_cookie_reauth()
        ):
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
            with contextlib.suppress(Exception):
                await self.check_write_access()
                # best-effort - loi that su se lo dien o lan goi tool tiep theo

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
        quote(object_type, safe="")
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

    def edit_session(self) -> SapEditSession:
        """Mo 1 'phien edit' stateful cho chuoi create/lock/PUT source/unlock/
        activate 1 object ADT. Xem SapEditSession de biet ly do can thiet."""
        return SapEditSession(self)


class SapEditSession:
    """1 phien HTTP dung CHUNG 1 httpx.AsyncClient (giu nguyen cookie jar,
    dac biet cookie 'sap-contextid') xuyen suot ca chuoi create -> lock ->
    PUT source -> unlock -> activate cho 1 object ADT.

    LY DO CAN THIET (phat hien qua test that voi package ZSD09_TEST,
    2026-07-17): kien truc binh thuong cua SapClient (_fetch_with_retry) tao
    1 httpx.AsyncClient MOI cho MOI request rieng le - lam mat cookie
    'sap-contextid' ma SAP tra ve luc Lock (dung de "ghim" - pin - phien lam
    viec vao 1 application server instance CU THE, noi lock duoc giu trong
    bo nho). Thieu cookie nay, cac request PUT/unlock/activate tiep theo co
    the bi route sang server KHAC khong biet gi ve lock vua tao - SAP tra loi
    nham lan kieu 401 "not locked" / 403 "currently editing" du code da gui
    dung lockHandle va da unlock "thanh cong" (thanh cong tren 1 server khac,
    khong phai server dang giu lock that).

    Dung header X-sap-adt-sessiontype: stateful (port tu vibing-steampunk
    http.go, comment nguyen van: "Lock handles are session-specific - force
    stateful, issue #88") KET HOP voi 1 httpx.AsyncClient DUY NHAT (khong tao
    lai cho tung request, de httpx tu dong giu + gui lai moi cookie server
    tra ve - gom ca sap-contextid) - da xac nhan hoat dong that qua test song
    voi ZSD09_TEST (tao + activate thanh cong het toan bo chuoi).

    Dung nhu:
        async with client.edit_session() as edit:
            await edit.create(creation_path, create_xml, transport)
            lock_handle = await edit.lock(object_url)
            await edit.put_source(source_url, ddl_text, lock_handle)
            await edit.unlock(object_url, lock_handle)
            result_xml = await edit.activate(object_url, object_name)
    """

    def __init__(self, client: SapClient) -> None:
        self._client = client
        self._hc: httpx.AsyncClient | None = None
        self._csrf_token: str = ""
        self._authorization: str | None = None

    async def __aenter__(self) -> SapEditSession:
        await self._client.init()
        timeout_s = (self._client.config.get("timeoutMs") or 30000) / 1000

        if self._client.use_cookie_auth:
            cookies = self._client.cookie_auth.get_cookies()
        else:
            token = await self._client.auth.get_access_token()
            self._authorization = f"Bearer {token}"
            cookies = {}

        self._hc = httpx.AsyncClient(cookies=cookies, timeout=timeout_s)

        headers = {"Accept": "application/xml", "x-csrf-token": "fetch"}
        if self._authorization:
            headers["Authorization"] = self._authorization
        base = self._client._base()
        try:
            resp = await self._hc.get(f"{base}/sap/bc/adt/core/discovery", headers=headers)
        except Exception:
            await self._hc.aclose()
            raise
        self._csrf_token = resp.headers.get("x-csrf-token", "")
        if not self._csrf_token:
            await self._hc.aclose()
            raise RuntimeError("Khong lay duoc CSRF token cho edit session.")
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._hc:
            await self._hc.aclose()

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        h = {"x-csrf-token": self._csrf_token, "X-sap-adt-sessiontype": "stateful"}
        if self._authorization:
            h["Authorization"] = self._authorization
        if extra:
            h.update(extra)
        return h

    @staticmethod
    def _raise_if_error(resp: httpx.Response, action: str, object_url: str) -> None:
        if resp.status_code >= 400:
            raise RuntimeError(f"{action} {object_url} -> {resp.status_code}: {resp.text[:500]}")

    async def create(self, creation_path: str, body: str, transport: str = "",
                      content_type: str = "application/*") -> str:
        """POST tao object shell (truoc lock). creation_path la duong dan
        collection (vd "/sap/bc/adt/ddic/ddl/sources"), KHONG phai URL cua
        object cu the (object chua ton tai truoc buoc nay)."""
        base = self._client._base()
        params = {"corrNr": transport} if transport else None
        resp = await self._hc.post(
            f"{base}{creation_path}", params=params,
            content=body.encode("utf-8"),
            headers=self._headers({"Content-Type": content_type}),
        )
        self._raise_if_error(resp, "Create", creation_path)
        return resp.text

    async def lock(self, object_url: str) -> str:
        """Lock object (POST thang vao URL cua chinh object). Tra ve lock
        handle; raise neu that bai hoac khong tim thay LOCK_HANDLE."""
        base = self._client._base()
        resp = await self._hc.post(
            f"{base}{object_url}",
            params={"_action": "LOCK", "accessMode": "MODIFY"},
            headers=self._headers({
                "Accept": "application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result",
            }),
        )
        self._raise_if_error(resp, "Lock", object_url)
        m = re.search(r"<LOCK_HANDLE>([^<]*)</LOCK_HANDLE>", resp.text)
        if not m or not m.group(1):
            raise RuntimeError(f"Lock khong tra ve LOCK_HANDLE hop le: {resp.text[:300]}")
        return m.group(1)

    async def put_source(self, source_url: str, source: str, lock_handle: str,
                          content_type: str = "text/plain; charset=utf-8",
                          transport: str = "") -> None:
        base = self._client._base()
        params: dict[str, str] = {"lockHandle": lock_handle}
        if transport:
            params["corrNr"] = transport
        resp = await self._hc.put(
            f"{base}{source_url}", params=params,
            content=source.encode("utf-8"),
            headers=self._headers({"Content-Type": content_type}),
        )
        self._raise_if_error(resp, "PUT source", source_url)

    async def unlock(self, object_url: str, lock_handle: str) -> None:
        base = self._client._base()
        resp = await self._hc.post(
            f"{base}{object_url}",
            params={"_action": "UNLOCK", "lockHandle": lock_handle},
            headers=self._headers(),
        )
        self._raise_if_error(resp, "Unlock", object_url)

    async def activate(self, object_url: str, object_name: str) -> str:
        return await self.activate_multi([(object_url, object_name)])

    async def activate_multi(self, refs: list[tuple[str, str]]) -> str:
        """Activate NHIEU object cung luc trong 1 request (nhieu
        adtcore:objectReference trong cung 1 body) - can cho BDEF: xac nhan
        tu nhieu nguon doc lap (marcellourbani/vscode_abap_remote_fs,
        jfilak/sapcli, fr0ster/mcp-abap-adt-clients, 2026-07-18) rang
        activate 1 Behavior Definition phai gom CA class implement behavior
        no trong CUNG 1 request /sap/bc/adt/activation - thieu buoc nay
        activate co the fail hoac cho ket qua sai. refs: list[(object_url,
        object_name)], object dau tien nen la object chinh (dung cho thong
        bao loi neu co)."""
        base = self._client._base()
        refs_xml = "\n".join(
            f'  <adtcore:objectReference adtcore:uri="{url}" adtcore:name="{name}"/>'
            for url, name in refs
        )
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">\n'
            f'{refs_xml}\n'
            '</adtcore:objectReferences>'
        )
        resp = await self._hc.post(
            f"{base}/sap/bc/adt/activation",
            params={"method": "activate", "preauditRequested": "true"},
            content=body.encode("utf-8"),
            headers=self._headers({"Content-Type": "application/xml"}),
        )
        self._raise_if_error(resp, "Activate", refs[0][0] if refs else "")
        return resp.text


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value
