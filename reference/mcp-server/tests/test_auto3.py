import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# Mock playwright module TRUOC khi import auth
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.async_api"] = MagicMock()
fake_pw_instance = MagicMock()
fake_pw_instance.start = AsyncMock(return_value=fake_pw_instance)
sys.modules["playwright.async_api"].async_playwright = MagicMock(
    return_value=fake_pw_instance
)

from sap_btp_agent.sap.auth import web_login_auto

def make_fake_browser():
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
    return fake_browser

async def case_1():
    """early_event set after 0.5s -> finish som."""
    print("=== CASE 1: early_event set after 0.5s ===")
    event = asyncio.Event()

    async def _set_after():
        await asyncio.sleep(0.5)
        event.set()
    asyncio.create_task(_set_after())

    fake_browser = make_fake_browser()
    with patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=fake_browser)), \
         patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=True)), \
         patch("sap_btp_agent.sap.auth.webbrowser"):

        import time
        t0 = time.monotonic()
        result = await web_login_auto({
            "base_url": "https://my440301.s4hana.cloud.sap",
            "profile_id": "test",
            "early_finish_event": event,
        })
        elapsed = time.monotonic() - t0
        print(f"  elapsed: {elapsed:.2f}s (target ~2-3s)")
        print(f"  cookies: {list(result.cookies.keys())}")
        assert elapsed < 5.0, f"Took {elapsed:.1f}s, expected <5s"
        assert "SAP_SESSIONID_HL8_080" in result.cookies
        print("  CASE 1 PASS")

async def case_2():
    """URL stable 3s, no event -> finish som ~3-5s."""
    print("=== CASE 2: URL stable 3s (no event) ===")
    fake_browser = make_fake_browser()
    # No session -> raise ReauthCancelled sau khi close browser
    with patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=fake_browser)), \
         patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=False)), \
         patch("sap_btp_agent.sap.auth.webbrowser"):

        import time
        t0 = time.monotonic()
        try:
            result = await web_login_auto({
                "base_url": "https://my440301.s4hana.cloud.sap",
                "profile_id": "test",
            })
            elapsed = time.monotonic() - t0
            print(f"  elapsed: {elapsed:.2f}s (target ~5-6s)")
            assert elapsed < 8.0
            print("  CASE 2 elapsed OK")
        except Exception as err:
            elapsed = time.monotonic() - t0
            print(f"  raised: {type(err).__name__} after {elapsed:.2f}s")
            assert elapsed < 8.0
            print(f"  CASE 2 raised OK ({type(err).__name__})")

async def main():
    await case_1()
    await case_2()
    print("=== ALL PASS ===")

asyncio.run(main())
