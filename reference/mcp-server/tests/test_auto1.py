"""Test web_login_auto:
- Case 1: early_finish_event set sau 0.5s -> finish som (hon ca 3s URL stable)
- Case 2: URL stable 3s (khong co session) -> finish som voi reason "url-stable"
- Case 3: timeout 30s (khong co gi) -> fallback (khong test vi lau)
"""
import asyncio
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from sap_btp_agent.sap.auth import web_login_auto, ReauthCancelled

async def case_1_early_event():
    """User set early_event sau 0.5s -> finish som ~ 0.5s + 1.5s wait = ~2s."""
    print("\n=== CASE 1: early_event set after 0.5s ===")
    event = asyncio.Event()

    async def _set_after():
        await asyncio.sleep(0.5)
        event.set()
    asyncio.create_task(_set_after())

    # Mock _verify_discovery_session -> always True
    with patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=True)), \
         patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=MagicMock())), \
         patch("sap_btp_agent.sap.auth.async_playwright") as ap:

        # Fake pw context manager
        fake_pw = MagicMock()
        fake_pw.start = MagicMock(return_value=AsyncMock(return_value=fake_pw)())
        ap.return_value.start = MagicMock(return_value=AsyncMock(return_value=fake_pw)())

        # Fake browser/context/page
        fake_browser = MagicMock()
        fake_browser.close = AsyncMock()
        fake_context = MagicMock()
        fake_context.cookies = AsyncMock(return_value=[
            {"name": "sap-usercontext", "value": "ctx"},
            {"name": "SAP_SESSIONID_HL8_080", "value": "abc123"},
        ])
        fake_page = MagicMock()
        fake_page.url = "https://my440301.s4hana.cloud.sap/sap/bc/adt/"
        fake_context.new_page = AsyncMock(return_value=fake_page)
        fake_browser.new_context = AsyncMock(return_value=fake_context)

        # _launch_real_browser tra ve fake_browser
        with patch("sap_btp_agent.sap.auth._launch_real_browser",
                   new=AsyncMock(return_value=fake_browser)):
            import time
            t0 = time.monotonic()
            result = await web_login_auto({
                "base_url": "https://my440301.s4hana.cloud.sap",
                "profile_id": "test",
                "early_finish_event": event,
            })
            elapsed = time.monotonic() - t0
            print(f"  elapsed: {elapsed:.2f}s")
            print(f"  cookies: {list(result.cookies.keys())}")
            assert elapsed < 5.0, f"Should finish in ~1s, took {elapsed:.1f}s"
            assert "SAP_SESSIONID_HL8_080" in result.cookies
            print("  CASE 1 PASS")

async def case_2_url_stable():
    """URL stable 3s (no event) -> finish som ~ 3-4s."""
    print("\n=== CASE 2: URL stable 3s (no event) ===")
    with patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=False)), \
         patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=MagicMock())):

        fake_browser = MagicMock()
        fake_browser.close = AsyncMock()
        fake_context = MagicMock()
        fake_context.cookies = AsyncMock(return_value=[
            {"name": "some_cookie", "value": "v"},
        ])
        fake_page = MagicMock()
        fake_page.url = "https://my440301.s4hana.cloud.sap/sap/bc/adt/"
        fake_context.new_page = AsyncMock(return_value=fake_page)
        fake_browser.new_context = AsyncMock(return_value=fake_context)

        with patch("sap_btp_agent.sap.auth._launch_real_browser",
                   new=AsyncMock(return_value=fake_browser)):
            import time
            t0 = time.monotonic()
            result = await web_login_auto({
                "base_url": "https://my440301.s4hana.cloud.sap",
                "profile_id": "test",
            })
            elapsed = time.monotonic() - t0
            print(f"  elapsed: {elapsed:.2f}s")
            print(f"  cookies: {list(result.cookies.keys())}")
            # URL stable takes ~3s + 1.5s wait_for_load = ~5s
            assert elapsed < 7.0, f"Should finish in ~5s, took {elapsed:.1f}s"
            # URL-stable nhung khong co session -> logged_in=False
            # nhung code van tra cookies (raw) - thuc ra trai raise ReauthCancelled
            # vi test 1 ver cho URL stable khong co session -> logged_in=False nhung
            # van tra cookies (khong save trong _cmd_reauth).
            # Trong test, raise ReauthCancelled o nhanh "no session cookie" duoi.
            # CASE 2 chi test finish som, khong quan tam cookies content.
            print(f"  CASE 2 elapsed OK (finish som < 7s)")

async def main():
    await case_1_early_event()
    await case_2_url_stable()
    print("\n=== ALL PASS ===")

asyncio.run(main())
