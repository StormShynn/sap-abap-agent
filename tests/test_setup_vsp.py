"""Test cho Phase 3 cua plan sap-multi-system-router: reference/mcp-server/
mcp_sap_connect/setup_vsp.py (auto-download binary `vsp` tu vibing-steampunk).

Khong goi network that: mock urllib.request.urlopen bang response gia.
SHA256 pin thuc (trong _ASSETS) khong duoc dung de verify trong test tai/
verify - test tu tinh SHA256 cua content gia roi patch _ASSETS, de test doc
lap voi gia tri pin that (se doi khi upstream ra version moi).
"""
from __future__ import annotations

import hashlib

import pytest

from mcp_sap_connect import setup_vsp


# ===== detect_platform_key =========================================


def test_detect_linux_amd64():
    assert setup_vsp.detect_platform_key("Linux", "x86_64") == "linux_amd64"


def test_detect_darwin_arm64():
    assert setup_vsp.detect_platform_key("Darwin", "arm64") == "darwin_arm64"


def test_detect_windows_amd64():
    assert setup_vsp.detect_platform_key("Windows", "AMD64") == "windows_amd64"


def test_detect_linux_arm_32bit():
    assert setup_vsp.detect_platform_key("Linux", "armv7l") == "linux_arm"


def test_detect_linux_aarch64_alias():
    assert setup_vsp.detect_platform_key("Linux", "aarch64") == "linux_arm64"


def test_detect_windows_386():
    assert setup_vsp.detect_platform_key("Windows", "x86") == "windows_386"


def test_detect_unsupported_os_raises():
    with pytest.raises(setup_vsp.VspSetupError, match="He dieu hanh"):
        setup_vsp.detect_platform_key("FreeBSD", "x86_64")


def test_detect_unsupported_arch_raises():
    with pytest.raises(setup_vsp.VspSetupError, match="Kien truc"):
        setup_vsp.detect_platform_key("Linux", "riscv64")


# ===== _ASSETS pin table sanity ====================================


def test_all_nine_platforms_covered():
    assert len(setup_vsp._ASSETS) == 9


def test_all_pinned_sha256_are_valid_64char_hex():
    import re
    for platform_key, (asset_name, sha256) in setup_vsp._ASSETS.items():
        assert re.fullmatch(r"[0-9a-f]{64}", sha256), f"{platform_key}/{asset_name}: bad sha256 {sha256!r}"


def test_all_asset_names_unique():
    names = [name for name, _ in setup_vsp._ASSETS.values()]
    assert len(names) == len(set(names))


# ===== binary_path ===================================================


def test_binary_path_windows_has_exe_suffix(tmp_path, monkeypatch):
    monkeypatch.setattr(setup_vsp, "get_bin_dir", lambda: tmp_path)
    monkeypatch.setattr(setup_vsp.platform, "system", lambda: "Windows")
    assert setup_vsp.binary_path() == tmp_path / "vsp.exe"


def test_binary_path_posix_no_suffix(tmp_path, monkeypatch):
    monkeypatch.setattr(setup_vsp, "get_bin_dir", lambda: tmp_path)
    monkeypatch.setattr(setup_vsp.platform, "system", lambda: "Linux")
    assert setup_vsp.binary_path() == tmp_path / "vsp"


# ===== ensure_vsp: download + verify + idempotency ==================


class _FakeResponse:
    def __init__(self, data: bytes):
        self._chunks = [data]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, size):
        if not self._chunks:
            return b""
        return self._chunks.pop(0)


@pytest.fixture
def fake_binary_env(tmp_path, monkeypatch):
    """Isolate ensure_vsp: fake bin dir, fake asset table with content we control."""
    bin_dir = tmp_path / "bin"
    monkeypatch.setattr(setup_vsp, "get_bin_dir", lambda: bin_dir)
    monkeypatch.setattr(setup_vsp.platform, "system", lambda: "Linux")
    monkeypatch.setattr(setup_vsp.platform, "machine", lambda: "x86_64")
    content = b"#!/bin/sh\necho fake-vsp-binary\n"
    real_sha256 = hashlib.sha256(content).hexdigest()
    monkeypatch.setitem(setup_vsp._ASSETS, "linux_amd64", ("vsp-linux-amd64", real_sha256))
    return bin_dir, content, real_sha256


def test_ensure_vsp_downloads_and_verifies(fake_binary_env, monkeypatch):
    bin_dir, content, _ = fake_binary_env
    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", lambda url, timeout: _FakeResponse(content))

    path = setup_vsp.ensure_vsp()

    assert path == bin_dir / "vsp"
    assert path.read_bytes() == content


def test_ensure_vsp_chmods_executable_on_posix_mocked_platform(fake_binary_env, monkeypatch):
    """platform.system() la mocked "Linux" (khong phai OS thuc cua may chay
    test) - chi assert chmod() DUOC GOI voi cac bit exec, khong assert ket
    qua stat() sau do (semantics chmod +x tren Windows filesystem thuc khac
    POSIX du platform.system() bao gi)."""
    bin_dir, content, _ = fake_binary_env
    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", lambda url, timeout: _FakeResponse(content))
    calls = []
    original_chmod = type(bin_dir).chmod

    def _tracking_chmod(self, mode, *a, **kw):
        calls.append(mode)
        return original_chmod(self, mode, *a, **kw)

    monkeypatch.setattr(type(bin_dir), "chmod", _tracking_chmod)

    setup_vsp.ensure_vsp()

    assert len(calls) == 1
    assert calls[0] & (setup_vsp.stat.S_IEXEC | setup_vsp.stat.S_IXGRP | setup_vsp.stat.S_IXOTH)


def test_ensure_vsp_skips_chmod_when_mocked_platform_is_windows(fake_binary_env, monkeypatch):
    bin_dir, content, _ = fake_binary_env
    monkeypatch.setattr(setup_vsp.platform, "system", lambda: "Windows")
    monkeypatch.setitem(setup_vsp._ASSETS, "windows_amd64", ("vsp-windows-amd64.exe", hashlib.sha256(content).hexdigest()))
    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", lambda url, timeout: _FakeResponse(content))
    calls = []
    monkeypatch.setattr(type(bin_dir), "chmod", lambda self, *a, **kw: calls.append(a))

    path = setup_vsp.ensure_vsp()

    assert path.name == "vsp.exe"
    assert calls == []


def test_ensure_vsp_idempotent_no_redownload(fake_binary_env, monkeypatch):
    bin_dir, content, _ = fake_binary_env
    calls = {"n": 0}

    def _urlopen(url, timeout):
        calls["n"] += 1
        return _FakeResponse(content)

    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", _urlopen)

    first = setup_vsp.ensure_vsp()
    second = setup_vsp.ensure_vsp()

    assert first == second
    assert calls["n"] == 1


def test_ensure_vsp_force_redownloads(fake_binary_env, monkeypatch):
    bin_dir, content, _ = fake_binary_env
    calls = {"n": 0}

    def _urlopen(url, timeout):
        calls["n"] += 1
        return _FakeResponse(content)

    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", _urlopen)

    setup_vsp.ensure_vsp()
    setup_vsp.ensure_vsp(force=True)

    assert calls["n"] == 2


def test_ensure_vsp_raises_and_cleans_up_on_sha256_mismatch(fake_binary_env, monkeypatch):
    bin_dir, content, _ = fake_binary_env
    corrupted = content + b"tampered"
    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", lambda url, timeout: _FakeResponse(corrupted))

    with pytest.raises(setup_vsp.VspSetupError, match="SHA256 khong khop"):
        setup_vsp.ensure_vsp()

    assert not (bin_dir / "vsp").exists()


def test_ensure_vsp_wraps_network_error(fake_binary_env, monkeypatch):
    import urllib.error

    def _raise(url, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", _raise)

    with pytest.raises(setup_vsp.VspSetupError, match="Tai vsp that bai"):
        setup_vsp.ensure_vsp()


def test_ensure_vsp_unsupported_platform_raises_before_download(tmp_path, monkeypatch):
    monkeypatch.setattr(setup_vsp, "get_bin_dir", lambda: tmp_path / "bin")
    monkeypatch.setattr(setup_vsp.platform, "system", lambda: "FreeBSD")
    monkeypatch.setattr(setup_vsp.platform, "machine", lambda: "x86_64")

    def _fail_if_called(url, timeout):
        raise AssertionError("khong duoc goi network khi platform khong ho tro")

    monkeypatch.setattr(setup_vsp.urllib.request, "urlopen", _fail_if_called)

    with pytest.raises(setup_vsp.VspSetupError, match="He dieu hanh"):
        setup_vsp.ensure_vsp()
