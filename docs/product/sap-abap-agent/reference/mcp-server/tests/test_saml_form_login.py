"""Test phan logic thuan (khong network/async) cua saml_form_login:
- _extract_form: parse form HTML dung.
- _canonical_host / _validate_form_action: chan exfiltrate SAMLResponse/
  credential ra host la, chan downgrade HTTPS->HTTP.

Day la phan quan trong nhat can test vi lien quan bao mat (khong phai toc
do). Khac cac file test_auto*/test_int* trong thu muc nay (asyncio.run(main())
o module scope) - file nay dung pytest binh thuong vi cac ham duoc test o
day deu la sync, khong can setup async runner rieng.
"""
import pytest

from mcp_sap_connect.sap.auth import (
    SamlLoginError,
    _canonical_host,
    _extract_form,
    _validate_form_action,
)


def test_extract_form_basic_login_form():
    html = """
    <html><body>
      <form action="/login/do" method="POST">
        <input type="hidden" name="csrf" value="abc123">
        <input type="text" name="j_username" value="">
        <input type="password" name="j_password" value="">
        <input type="submit" value="Log in">
      </form>
    </body></html>
    """
    form = _extract_form(html)
    assert form is not None
    assert form.action == "/login/do"
    assert form.method == "POST"
    assert form.fields == {"csrf": "abc123", "j_username": "", "j_password": ""}


def test_extract_form_no_form_returns_none():
    assert _extract_form("<html><body>no form here</body></html>") is None


def test_extract_form_excludes_button_and_image_inputs():
    html = """
    <form action="/x">
      <input type="hidden" name="keep" value="1">
      <input type="submit" name="drop_submit" value="go">
      <input type="button" name="drop_button" value="go">
      <input type="image" name="drop_image" value="go">
    </form>
    """
    form = _extract_form(html)
    assert form.fields == {"keep": "1"}


def test_canonical_host_strips_default_ports():
    assert _canonical_host("example.com:443", "https") == "example.com"
    assert _canonical_host("example.com:80", "http") == "example.com"
    assert _canonical_host("Example.COM", "https") == "example.com"
    # Non-default port kept as-is.
    assert _canonical_host("example.com:8443", "https") == "example.com:8443"


def test_validate_form_action_allows_same_host_relative():
    resolved = _validate_form_action(
        "https://ias.example.com/saml2/login", "/saml2/login/do", "sap.example.com"
    )
    assert resolved == "https://ias.example.com/saml2/login/do"


def test_validate_form_action_allows_sap_host_absolute():
    resolved = _validate_form_action(
        "https://ias.example.com/saml2/login",
        "https://sap.example.com/sap/saml2/sp/acs/080",
        "sap.example.com",
    )
    assert resolved == "https://sap.example.com/sap/saml2/sp/acs/080"


def test_validate_form_action_rejects_cross_host_exfiltration():
    with pytest.raises(SamlLoginError, match="host khac"):
        _validate_form_action(
            "https://ias.example.com/saml2/login",
            "https://attacker.evil/steal",
            "sap.example.com",
        )


def test_validate_form_action_rejects_https_downgrade():
    with pytest.raises(SamlLoginError, match="downgrade"):
        _validate_form_action(
            "https://ias.example.com/saml2/login",
            "http://ias.example.com/saml2/login/do",
            "sap.example.com",
        )
