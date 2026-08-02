"""Test _claude_mcp_add() dung DUNG cu phap `claude mcp add` - xac nhan qua
chay lenh that 1 lan roi xoa lai (khong the lap lai trong CI vi can `claude`
that trong PATH), nen o day chi mock subprocess.run va kiem tra shape lenh:

- stdio: -e/--env PHAI dat TRUOC "--" (dat sau se thanh literal arg cho
  subprocess thay vi env var that).
- sse/http/ws: KHONG dung --env (variadic - dat truoc url se nuot mat url,
  dat sau thi claude im lang khong luu gi ca) - PHAI dung --header "K: V" SAU
  url (co che that de gui gia tri auth cho remote server qua HTTP header).
- KHONG bao gio dung flag --url (khong ton tai - URL la positional).
"""
from unittest.mock import MagicMock, patch

from mcp_sap_connect.cli import _claude_mcp_add


def _mock_result(returncode=0, stdout="", stderr=""):
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def test_stdio_env_before_separator():
    with patch("subprocess.run", return_value=_mock_result()) as mock_run:
        ok, detail = _claude_mcp_add(
            "claude", "sap-btp", "stdio",
            cmd="mcp-sap-connect", args=[], env={"FOO": "bar"},
        )
    assert ok is True
    assert detail == ""
    cli = mock_run.call_args.args[0]
    sep_idx = cli.index("--")
    env_idx = cli.index("--env")
    assert env_idx < sep_idx
    assert cli[env_idx + 1] == "FOO=bar"
    assert cli[sep_idx + 1] == "mcp-sap-connect"


def test_sse_header_after_url_not_env():
    with patch("subprocess.run", return_value=_mock_result()) as mock_run:
        ok, _ = _claude_mcp_add(
            "claude", "mcp-sap-docs-btp", "sse",
            url="https://example.com/sse", env={"SAP-API-HUB-KEY": "abc123"},
        )
    assert ok is True
    cli = mock_run.call_args.args[0]
    assert "--env" not in cli
    assert "--url" not in cli
    url_idx = cli.index("https://example.com/sse")
    header_idx = cli.index("--header")
    assert header_idx > url_idx
    assert cli[header_idx + 1] == "SAP-API-HUB-KEY: abc123"


def test_sse_no_env_no_header_flag():
    with patch("subprocess.run", return_value=_mock_result()) as mock_run:
        _claude_mcp_add("claude", "cds-kb", "sse", url="https://x.example/sse")
    cli = mock_run.call_args.args[0]
    assert "--header" not in cli
    assert "https://x.example/sse" in cli


def test_failure_returns_stderr_detail():
    with patch("subprocess.run", return_value=_mock_result(returncode=1, stderr="error: something bad")):
        ok, detail = _claude_mcp_add("claude", "x", "stdio", cmd="foo")
    assert ok is False
    assert "something bad" in detail
