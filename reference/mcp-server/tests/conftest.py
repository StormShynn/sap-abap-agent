"""Shared fixtures/paths for sap-btp-agent tests.

Cac test file o day thuong dung sys.path.insert de import sap_btp_agent,
nen ta them <repo>/reference/mcp-server/ vao sys.path ngay khi pytest khoi dong.
"""
import sys
from pathlib import Path

# Cho phep `import sap_btp_agent` khi chay pytest tu root hoac tu tests/.
_MCP_SERVER_DIR = Path(__file__).resolve().parent.parent
if str(_MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_SERVER_DIR))


# Cac file test_* o day la script test cu (cu di chuyen tu root, co prefix _test_)
# chay ngay khi import qua asyncio.run(main()) o module-level - khong phai pytest
# function that. De khong lam fail pytest discovery (va giu logic goc),
# ta collect_ignore toan bo, va de pre-commit chi collect-only o day.
#
# De CHAY that cac test cu, nguoi dung co the goi truc tiep:
#   python tests/test_auto1.py
collect_ignore_glob = ["test_*.py"]
