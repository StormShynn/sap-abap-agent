"""Test cho _setup_vsp_server() trong cli/__init__.py (Phase 3 cua plan
sap-multi-system-router): credential resolution theo authMode + goi
register_fn dung tham so.
"""
from __future__ import annotations

from mcp_sap_connect.cli import _setup_vsp_server
from mcp_sap_connect.setup_vsp import VspSetupError


def _fake_register():
    calls = []

    def register(name, transport, *, cmd=None, args=None, env=None):
        calls.append({"name": name, "transport": transport, "cmd": cmd, "args": args, "env": env})

    register.calls = calls
    return register


def test_registers_with_password_auth_credentials(monkeypatch):
    monkeypatch.delenv("MCP_SAP_CONNECT_VSP_BIN", raising=False)
    monkeypatch.setattr("mcp_sap_connect.cli.ensure_vsp", lambda: "/fake/bin/vsp")
    monkeypatch.setattr("mcp_sap_connect.cli.load_config", lambda: {
        "btpUrl": "https://onprem.example.com", "authMode": "password",
    })

    async def _fake_load_secrets(*a, **kw):
        return {"username": "bob", "password": "s3cr3t"}

    monkeypatch.setattr("mcp_sap_connect.cli.load_secrets", _fake_load_secrets)

    register = _fake_register()
    _setup_vsp_server(register)

    assert len(register.calls) == 1
    call = register.calls[0]
    assert call["name"] == "sap-vsp"
    assert call["cmd"] == "/fake/bin/vsp"
    assert call["args"] == ["mcp"]
    assert call["env"] == {
        "SAP_ADT_URL": "https://onprem.example.com",
        "SAP_ADT_USER": "bob",
        "SAP_ADT_PASSWORD": "s3cr3t",
    }


def test_registers_without_credentials_when_cookie_auth(monkeypatch):
    monkeypatch.delenv("MCP_SAP_CONNECT_VSP_BIN", raising=False)
    monkeypatch.setattr("mcp_sap_connect.cli.ensure_vsp", lambda: "/fake/bin/vsp")
    monkeypatch.setattr("mcp_sap_connect.cli.load_config", lambda: {
        "btpUrl": "https://public.example.com", "authMode": "cookie",
    })

    register = _fake_register()
    _setup_vsp_server(register)

    assert len(register.calls) == 1
    env = register.calls[0]["env"]
    assert env["SAP_ADT_URL"] == "https://public.example.com"
    assert "SAP_ADT_USER" not in env
    assert "SAP_ADT_PASSWORD" not in env


def test_uses_pinned_vsp_bin_env_var_skips_download(monkeypatch):
    monkeypatch.setenv("MCP_SAP_CONNECT_VSP_BIN", "/opt/vsp/vsp")

    def _fail_if_called():
        raise AssertionError("khong duoc goi ensure_vsp() khi da co MCP_SAP_CONNECT_VSP_BIN")

    monkeypatch.setattr("mcp_sap_connect.cli.ensure_vsp", _fail_if_called)
    monkeypatch.setattr("mcp_sap_connect.cli.load_config", lambda: {"btpUrl": "x", "authMode": "oauth2"})

    register = _fake_register()
    _setup_vsp_server(register)

    assert register.calls[0]["cmd"] == "/opt/vsp/vsp"


def test_skips_registration_when_ensure_vsp_fails(monkeypatch):
    monkeypatch.delenv("MCP_SAP_CONNECT_VSP_BIN", raising=False)

    def _raise():
        raise VspSetupError("network down")

    monkeypatch.setattr("mcp_sap_connect.cli.ensure_vsp", _raise)

    register = _fake_register()
    _setup_vsp_server(register)

    assert register.calls == []


def test_handles_missing_active_profile_gracefully(monkeypatch):
    monkeypatch.delenv("MCP_SAP_CONNECT_VSP_BIN", raising=False)
    monkeypatch.setattr("mcp_sap_connect.cli.ensure_vsp", lambda: "/fake/bin/vsp")

    def _raise(*a, **kw):
        raise RuntimeError("Chua co profile nao.")

    monkeypatch.setattr("mcp_sap_connect.cli.load_config", _raise)

    register = _fake_register()
    _setup_vsp_server(register)

    assert len(register.calls) == 1
    assert register.calls[0]["env"] == {"SAP_ADT_URL": ""}
