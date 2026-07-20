import os
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

fd, marker = tempfile.mkstemp(prefix="sap_early_test_", suffix=".path")
os.close(fd)
os.unlink(marker)

testdir = tempfile.mkdtemp()
profiles_dir = os.path.join(testdir, "profiles", "test.s4hana.cloud.sap")
os.makedirs(profiles_dir)
for fn, content in [
    ("config.json", '{"authMode": "cookie", "reauthMode": "auto", "btpUrl": "https://example.com"}'),
    ("secrets.json", "{}"),
]:
    with open(os.path.join(profiles_dir, fn), "w", encoding="utf-8") as f:
        f.write(content)

env = os.environ.copy()
env["SAP_BTP_EARLY_FINISH_FILE"] = marker
env["SAP_BTP_APPDIR_OVERRIDE"] = testdir

# Test truc tiep: import va run async function, khong qua subprocess
# de verify logic file-marker
async def main():
    from sap_btp_agent.cli import _cmd_reauth

    mock_auth = MagicMock()
    mock_auth.init = AsyncMock()

    async def fake_reauth(ctx=None):
        print(f"[mock] reauth called, ctx keys: {list(ctx.keys()) if ctx else None}")
        # Lay event tu ctx, set no tu task khac
        ev = ctx.get("early_finish_event") if ctx else None
        if ev:
            print(f"[mock] waiting for event (set={ev.is_set()})...")
            await ev.wait()
            print("[mock] event SET! continuing.")
        return MagicMock(cookies={'SAP_SESSIONID_HL8_080': 'abc'}, access_token='', expires_at=0)
    mock_auth.reauth = fake_reauth
    mock_auth.save_cookies = AsyncMock()

    fake_cfg = {'authMode': 'cookie', 'reauthMode': 'auto', 'btpUrl': 'https://example.com'}

    with patch('sap_btp_agent.config.store.load_config', return_value=fake_cfg), \
         patch('sap_btp_agent.config.secrets.load_secrets', new=AsyncMock(return_value={'cookies': {}})), \
         patch('sap_btp_agent.config.secrets.update_secrets', new=AsyncMock(return_value={})), \
         patch('sap_btp_agent.cli.__init__.SapCookieAuth', return_value=mock_auth):

        # Patch sys.stdin de khong bi block o thread watcher (TTY check)
        import sys as _sys
        _sys.stdin = MagicMock()
        _sys.stdin.isatty = lambda: False  # de watcher khong start stdin thread

        # Set env
        os.environ['SAP_BTP_EARLY_FINISH_FILE'] = marker

        # Spawn task touch file marker sau 1s
        async def touch():
            await asyncio.sleep(1.0)
            print("\n[main] touching file marker...")
            Path(marker).touch()
        asyncio.create_task(touch())

        t0 = time.monotonic()
        await _cmd_reauth('test.s4hana.cloud.sap')
        elapsed = time.monotonic() - t0
        print(f"\n[main] _cmd_reauth done in {elapsed:.2f}s")

import asyncio  # noqa: E402

asyncio.run(main())
