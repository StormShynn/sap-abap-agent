"""Test _setup_from_file tra ve True/False dung (thay vi luon None) - GUI (qua
runner() -> sys.exit) dua vao gia tri nay de phan biet thanh cong/that bai, vi
tu khi doi start_new_console -> start_streamed, output console rieng khong con
de doc kip (chay xong qua nhanh), phai dua vao exit code + log trong app.

Moi test tu tro app dir ve 1 tmp_path rieng (MCP_SAP_CONNECT_HOME) de khong dung
cham toi profile that cua may dang chay test.
"""
import asyncio
import json

import pytest

from mcp_sap_connect.cli import _make_runner, _setup_from_file
from mcp_sap_connect.config.profile import list_profiles


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(tmp_path / "home"))


def test_missing_file_returns_false(tmp_path):
    result = _run(_setup_from_file(str(tmp_path / "khong_ton_tai.json")))
    assert result is False
    assert list_profiles()["items"] == []


def test_placeholder_url_returns_false(tmp_path):
    profile_file = tmp_path / "profile.cookie.json"
    profile_file.write_text(json.dumps({
        "url": "<https://YOUR_TENANT.s4hana.cloud.sap>",
        "authMode": "cookie",
        "reauthMode": "manual",
        "cookies": {"MYSAPSSO2": "<PASTE_COOKIE_VALUE>"},
    }), encoding="utf-8")

    result = _run(_setup_from_file(str(profile_file)))
    assert result is False
    assert list_profiles()["items"] == []


def test_valid_cookie_manual_returns_true_and_creates_profile(tmp_path):
    profile_file = tmp_path / "profile.cookie.json"
    profile_file.write_text(json.dumps({
        "profileId": "test_throwaway",
        "url": "https://test-throwaway.invalid.example",
        "service": "s4hc_(public)",
        "region": "eu10",
        "authMode": "cookie",
        "reauthMode": "manual",
        "cookies": {"MYSAPSSO2": "fake-not-real-value"},
    }), encoding="utf-8")

    result = _run(_setup_from_file(str(profile_file)))
    assert result is True

    items = {p["id"]: p for p in list_profiles()["items"]}
    assert "test_throwaway" in items
    assert items["test_throwaway"]["url"] == "https://test-throwaway.invalid.example"


def test_runner_exits_1_when_coro_returns_false():
    runner = _make_runner()

    async def rejected():
        return False

    with pytest.raises(SystemExit) as exc_info:
        runner(rejected)
    assert exc_info.value.code == 1


def test_runner_does_not_exit_when_coro_returns_none():
    runner = _make_runner()

    async def ok_none():
        return None

    runner(ok_none)  # khong raise SystemExit
