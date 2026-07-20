"""Test web_login_auto voi mock playwright qua sys.modules."""
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Mock toan bo playwright module TRUOC khi import auth
fake_pw_module = MagicMock()
fake_pw_instance = MagicMock()
fake_pw_instance.start = AsyncMock(return_value=fake_pw_instance)
fake_pw_module.return_value.start.return_value = fake_pw_instance

sys.modules["playwright"] = MagicMock()
sys.modules["playwright.async_api"] = MagicMock()
sys.modules["playwright.async_api"].async_playwright = fake_pw_module

from sap_btp_agent.sap.auth import web_login_auto  # noqa: E402


async def case_1():
    """early_event set after 0.5s -> finish som."""
    print("=== CASE 1: early_event set after 0.5s ===")
    event = asyncio.Event()

    async def _set_after():
        await asyncio.sleep(0.5)
        event.set()
    asyncio.create_task(_set_after())

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
        print(f"  elapsed: {elapsed:.2f}s (expected ~2-3s)")
        print(f"  cookies: {list(result.cookies.keys())}")
        assert elapsed < 5.0, f"Should finish in <5s, took {elapsed:.1f}s"
        assert "SAP_SESSIONID_HL8_080" in result.cookies
        print("  CASE 1 PASS")

async def case_2():
    """URL stable 3s, no event, no session -> finish som ~3-5s."""
    print("=== CASE 2: URL stable 3s (no event, no session) ===")
    fake_browser = MagicMock()
    fake_browser.close = AsyncMock()
    fake_context = MagicMock()
    fake_context.cookies = AsyncMock(return_value=[
        {"name": "foo", "value": "v"},
    ])
    fake_page = MagicMock()
    fake_page.url = "https://my440301.s4hana.cloud.sap/sap/bc/adt/"
    fake_context.new_page = AsyncMock(return_value=fake_page)
    fake_browser.new_context = AsyncMock(return_value=fake_context)

    with patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=fake_browser)), \
         patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=False)), \
         patch("sap_btp_agent.sap.auth.webbrowser"):

        import time
        t0 = time.monotonic()
        try:
            await web_login_auto({
                "base_url": "https://my440301.s4hana.cloud.sap",
                "profile_id": "test",
            })
            elapsed = time.monotonic() - t0
            print(f"  elapsed: {elapsed:.2f}s (expected ~5-6s)")
            assert elapsed < 8.0
            print("  CASE 2 elapsed OK")
        except Exception as err:
            elapsed = time.monotonic() - t0
            print(f"  raised: {type(err).__name__}: {err}")
            print(f"  elapsed: {elapsed:.2f}s")
            assert elapsed < 8.0
            print("  CASE 2 raised as expected")

async def main():
    await case_1()
    await case_2()
    print("=== ALL PASS ===")

asyncio.run(main())
