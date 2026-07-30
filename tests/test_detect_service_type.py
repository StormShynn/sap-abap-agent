"""Test cho reference/scripts/detect_service_type.py.

File do co comment tu khai "Phai khop 100% voi
reference/mcp-server/mcp_sap_connect/config/store.py (SERVICE_TYPES /
SERVICE_TYPE_ALIASES)" - Phase 2 (them rise_with_sap) da vi pham dieu nay
(script van chi co 4 edition + thieu env var dung case MCP_SAP_CONNECT_HOME).
Test nay pin lai invariant do de khong lech nua trong tuong lai.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import detect_service_type as dst  # noqa: E402

from mcp_sap_connect.config import store  # noqa: E402


# ===== Invariant: phai khop 100% voi store.py ========================


def test_service_types_match_store_py():
    assert set(dst.SERVICE_TYPES) == set(store.SERVICE_TYPES)


def test_service_type_aliases_match_store_py():
    assert dst.SERVICE_TYPE_ALIASES == store.SERVICE_TYPE_ALIASES


def test_includes_rise_with_sap():
    assert "rise_with_sap" in dst.SERVICE_TYPES
    assert dst.SERVICE_TYPE_ALIASES.get("rise") == "rise_with_sap"


# ===== _get_app_dir: dung dung ten bien MCP_SAP_CONNECT_HOME ==========


def test_get_app_dir_respects_uppercase_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(tmp_path))
    assert dst._get_app_dir() == tmp_path.resolve()


def test_get_app_dir_ignores_lowercase_typo_env_var(monkeypatch, tmp_path):
    """Ten bien cu (bug da fix) khong duoc anh huong gi nua.

    Dung dict thuong (khong phai monkeypatch.setenv that) vi os.environ tren
    Windows case-insensitive - set "mcp_sap_connect_HOME" that se tinh cach
    Windows tu fold thanh khop voi "MCP_SAP_CONNECT_HOME", che mat regression
    nay. Dict thuong luon case-sensitive, phan anh dung hanh vi tren POSIX
    (Linux/macOS - noi package nay cung ho tro) ma khong phu thuoc OS chay test.
    """
    fake_environ = dict(dst.os.environ)  # giu cac bien that (vd USERPROFILE) de Path.home() van resolve duoc
    fake_environ.pop("MCP_SAP_CONNECT_HOME", None)
    fake_environ["mcp_sap_connect_HOME"] = str(tmp_path)
    monkeypatch.setattr(dst.os, "environ", fake_environ)
    assert dst._get_app_dir() != tmp_path.resolve()


# ===== detect(): rise_with_sap profile duoc nhan dung (source == "config") ==


def test_detect_recognizes_rise_with_sap_profile(monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_BTP_PROFILE", raising=False)
    (tmp_path / "profiles.json").write_text(json.dumps({"active": "p1"}), encoding="utf-8")
    profile_dir = tmp_path / "profiles" / "p1"
    profile_dir.mkdir(parents=True)
    (profile_dir / "config.json").write_text(json.dumps({"service": "rise_with_sap"}), encoding="utf-8")

    result = dst.detect()

    assert result["service"] == "rise_with_sap"
    assert result["source"] == "config"


def test_detect_resolves_rise_alias(monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_BTP_PROFILE", raising=False)
    (tmp_path / "profiles.json").write_text(json.dumps({"active": "p1"}), encoding="utf-8")
    profile_dir = tmp_path / "profiles" / "p1"
    profile_dir.mkdir(parents=True)
    (profile_dir / "config.json").write_text(json.dumps({"service": "rise"}), encoding="utf-8")

    result = dst.detect()

    assert result["service"] == "rise_with_sap"
    assert result["source"] == "config"
