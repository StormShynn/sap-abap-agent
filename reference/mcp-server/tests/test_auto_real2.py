import asyncio
import sys
import time
from unittest.mock import MagicMock, AsyncMock, patch

sys.modules["playwright"] = MagicMock()
sys.modules["playwright.async_api"] = MagicMock()
fake_pw_instance = MagicMock()
fake_pw_instance.start = AsyncMock(return_value=fake_pw_instance)
sys.modules["playwright.async_api"].async_playwright = MagicMock(
    return_value=fake_pw_instance
)

from sap_btp_agent.sap.auth import web_login_auto

async def real_sleep(ms):
    await asyncio.sleep(ms / 1000)

async def case_url_stable_real_timing():
    print("=== URL stable 3s (real sleep) ===")
    fb = MagicMock()
    fb.close = AsyncMock()
    fc = MagicMock()
    fc.cookies = AsyncMock(return_value=[
        {"name": "SAP_SESSIONID_HL8_080", "value": "abc"},
    ])
    fp = MagicMock()
    fp.url = "https://my440301.s4hana.cloud.sap/sap/bc/adt/"
    fp.wait_for_timeout = AsyncMock(side_effect=real_sleep)
    fc.new_page = AsyncMock(return_value=fp)
    fb.new_context = AsyncMock(return_value=fc)

    with patch("sap_btp_agent.sap.auth._launch_real_browser",
               new=AsyncMock(return_value=fb)), \
         patch("sap_btp_agent.sap.auth._verify_discovery_session",
               new=AsyncMock(return_value=False)):

        t0 = time.monotonic()
        try:
            await web_login_auto({
                "base_url": "https://my440301.s4hana.cloud.sap",
                "profile_id": "test",
            })
        except Exception as err:
            print(f"  raised: {type(err).__name__}: {err}")
        elapsed = time.monotonic() - t0
        print(f"  elapsed: {elapsed:.2f}s")
        assert 3.0 < elapsed < 6.0, f"Should be ~4.5s, got {elapsed:.1f}s"
        print(f"  CASE PASS - URL stable took {elapsed:.2f}s (was 30s before)")

asyncio.run(case_url_stable_real_timing())
