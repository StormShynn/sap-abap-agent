"""Test integration: subprocess CLI doc env var SAP_BTP_EARLY_FINISH_FILE."""
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

# Tao file marker
fd, marker = tempfile.mkstemp(prefix="sap_early_test_", suffix=".path")
os.close(fd)
os.unlink(marker)

env = os.environ.copy()
env["SAP_BTP_EARLY_FINISH_FILE"] = marker

# Spawn 1 python subprocess chay mock _cmd_reauth
proc = subprocess.Popen(
    [sys.executable, "-c", """
import asyncio
import os, sys
from sap_btp_agent.cli.__init__ import _cmd_reauth
from unittest.mock import patch, MagicMock

# Mock config
fake_cfg = {
    'authMode': 'cookie',
    'reauthMode': 'auto',
    'btpUrl': 'https://example.com',
}

async def main():
    with patch('sap_btp_agent.cli.__init__.load_config', return_value=fake_cfg):
        await _cmd_reauth('test.s4hana.cloud.sap')

try:
    asyncio.run(main())
except Exception as err:
    print(f'SUBPROC EXC: {type(err).__name__}: {err}')
"""],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, env=env,
)

# Sau 2s, touch file marker de signal
def trigger_after():
    time.sleep(2.0)
    print("\n[TEST] touching file marker...")
    Path(marker).touch()
threading.Thread(target=trigger_after, daemon=True).start()

t0 = time.monotonic()
out, _ = proc.communicate(timeout=15)
elapsed = time.monotonic() - t0

print(f"subprocess exited after {elapsed:.1f}s")
print("--- output ---")
print(out)
