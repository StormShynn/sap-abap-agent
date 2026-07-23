"""Test integration: subprocess CLI doc env var SAP_BTP_EARLY_FINISH_FILE."""
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

fd, marker = tempfile.mkstemp(prefix="sap_early_test_", suffix=".path")
os.close(fd)
os.unlink(marker)

env = os.environ.copy()
env["SAP_BTP_EARLY_FINISH_FILE"] = marker

# Tao 1 profile gia de khong fail o load_config
testdir = tempfile.mkdtemp()
profiles_dir = os.path.join(testdir, "profiles", "test.s4hana.cloud.sap")
os.makedirs(profiles_dir)
with open(os.path.join(profiles_dir, "config.json"), "w", encoding="utf-8") as f:
    f.write('{"authMode": "cookie", "reauthMode": "auto", "btpUrl": "https://example.com"}')
with open(os.path.join(profiles_dir, "secrets.json"), "w", encoding="utf-8") as f:
    f.write("{}")

# Patch app_dir qua env (khong co cach set app_dir, nen dung HOME/USERPROFILE)
env["SAP_BTP_APPDIR_OVERRIDE"] = testdir

proc = subprocess.Popen(
    [sys.executable, "-c", """
import asyncio
import os, sys, json
from unittest.mock import patch, MagicMock

# Mock app_dir + secrets/load_config + SapCookieAuth
testdir = os.environ.get('SAP_BTP_APPDIR_OVERRIDE')

async def main():
    from sap_btp_agent.cli import _cmd_reauth

    # Mock toan bo I/O
    mock_auth = MagicMock()
    mock_auth.init = AsyncMock()
    async def fake_reauth(ctx=None):
        print("Reauth called with ctx:", ctx and list(ctx.keys()))
        return MagicMock(cookies={'SAP_SESSIONID_HL8_080': 'abc'}, access_token='', expires_at=0)
    mock_auth.reauth = fake_reauth
    mock_auth.save_cookies = AsyncMock()

    fake_cfg = {'authMode': 'cookie', 'reauthMode': 'auto', 'btpUrl': 'https://example.com'}
    with patch('sap_btp_agent.config.store.load_config', return_value=fake_cfg), \\
         patch('sap_btp_agent.cli.__init__.load_config', return_value=fake_cfg), \\
         patch('sap_btp_agent.sap.auth.load_secrets', new=AsyncMock(return_value={'cookies': {}})), \\
         patch('sap_btp_agent.sap.auth.update_secrets', new=AsyncMock(return_value={})), \\
         patch('sap_btp_agent.cli.__init__.SapCookieAuth', return_value=mock_auth):
        await _cmd_reauth('test.s4hana.cloud.sap')

try:
    asyncio.run(main())
except SystemExit:
    pass
except Exception as err:
    print(f'SUBPROC EXC: {type(err).__name__}: {err}')
"""],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, env=env,
)

def trigger_after():
    time.sleep(1.0)
    print("\n[TEST] touching file marker...")
    Path(marker).touch()
threading.Thread(target=trigger_after, daemon=True).start()

t0 = time.monotonic()
out, _ = proc.communicate(timeout=10)
elapsed = time.monotonic() - t0
print(f"\nsubprocess exited after {elapsed:.1f}s")
print("--- output ---")
print(out)
