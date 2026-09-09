"""Shared fixtures/paths for mcp-sap-connect tests.

Cac test file o day thuong dung sys.path.insert de import mcp_sap_connect,
nen ta them <repo>/reference/mcp-server/ vao sys.path ngay khi pytest khoi dong.
"""
import sys
from pathlib import Path

# Cho phep `import mcp_sap_connect` khi chay pytest tu root hoac tu tests/.
_MCP_SERVER_DIR = Path(__file__).resolve().parent.parent
if str(_MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_SERVER_DIR))


# Cac file duoi day la script test cu (di chuyen tu root), chay ngay khi
# IMPORT qua asyncio.run(...)/code o module-level (khong co ham `def test_*`
# nao pytest nhan dien duoc) - collect binh thuong se tu chay het side-effect
# (spawn subprocess, mo Tkinter GUI that...) ngay luc discovery, rat cham va
# khong an toan. Liet ke DICH DANH tung file (KHONG dung glob "test_*.py" -
# glob do vo tinh ignore LUON ca cac file test_*.py that su co ham test_* hop
# le, khien toan bo thu muc nay bi bo qua am tham moi khi chay
# `pytest tests/` thay vi chi định 1 file cu the).
#
# De CHAY that cac script cu nay, goi truc tiep:
#   python tests/test_auto4.py
collect_ignore = [
    "test_int2.py",
    "test_int3.py",
    "test_auto4.py",
    "test_auto5.py",
    "test_auto_real2.py",
    "test_gui_btn.py",
]
