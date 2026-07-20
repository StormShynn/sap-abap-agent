import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.modules["playwright"] = MagicMock()
sys.modules["playwright.async_api"] = MagicMock()
fake_pw_instance = MagicMock()
fake_pw_instance.start = AsyncMock(return_value=fake_pw_instance)
sys.modules["playwright.async_api"].async_playwright = MagicMock(
    return_value=fake_pw_instance
)

from sap_btp_agent.sap.auth import web_login_auto  # noqa: E402


def make_fake_browser():
    fb = MagicMock()
    fb.close = AsyncMock()
    fc = MagicMock()
    fc.cookies = AsyncMock(return_value=[
        {"name": "sap-usercontext", "value": "ctx"},
        {"name": "SAP_SESSIONID_HL8_080", "value": "abc123"},
    ])
    fp = MagicMock()
    fp.url = "https://my440301.s4hana.cloud.sap/sap/bc/adt/"
    fp.wait_for_timeout = AsyncMock()  # QUAN TRONG: AsyncMock
    fc.new_page = AsyncMock(return_value=fp)
    fb.new_context = AsyncMock(return_value=fc)
    return fb

async def case_1():
    print("=== CASE 1: early_event set after 0.5s ===")
    event = asyncio.Event()
    async def _set():
        await asyncio.sleep(0.5)
        event.set()
    asyncio.create_task(_set())

    with patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=make_fake_browser())), \
         patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=True)):

        import time
        t0 = time.monotonic()
        result = await web_login_auto({
            "base_url": "https://my440301.s4hana.cloud.sap",
            "profile_id": "test",
            "early_finish_event": event,
        })
        elapsed = time.monotonic() - t0
        print(f"  elapsed: {elapsed:.2f}s (target ~2-3s)")
        assert elapsed < 5.0
        assert "SAP_SESSIONID_HL8_080" in result.cookies
        print("  CASE 1 PASS")

async def case_2():
    print("=== CASE 2: URL stable 3s (no event, no session) ===")
    with patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=make_fake_browser())), \
         patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=False)):

        import time
        t0 = time.monotonic()
        try:
            await web_login_auto({
                "base_url": "https://my440301.s4hana.cloud.sap",
                "profile_id": "test",
            })
        except Exception as err:
            print(f"  raised: {type(err).__name__}")
        elapsed = time.monotonic() - t0
        print(f"  elapsed: {elapsed:.2f}s (target ~5-6s)")
        assert elapsed < 8.0
        print("  CASE 2 PASS")

async def main():
    await case_1()
    await case_2()
    print("=== ALL PASS ===")

asyncio.run(main())
