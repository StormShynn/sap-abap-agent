"""Test schema v2 + rise_with_sap cho Phase 2 cua plan sap-multi-system-router.

Cover:
  - SERVICE_TYPES co rise_with_sap (5 edition)
  - normalize_service_type: rise_with_sap, alias 'rise', reject unknown
  - default_auth_mode_for_service: cookie/oauth2/password theo service
  - normalize_routing_hints: defaults + validation (unknown key, wrong type, bad enum)
  - load_config: lazy upgrade v1 -> v2 (khong ghi dia o read path)
  - save_config: backup v1 file, bump version, them routingHints default
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from mcp_sap_connect.config import store
from mcp_sap_connect.config import paths


@pytest.fixture
def fresh_home(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(tmp_path / "app"))
    return tmp_path


# ===== SERVICE_TYPES taxonomy ======================================


def test_service_types_has_five_entries():
    assert len(store.SERVICE_TYPES) == 5


def test_service_types_includes_rise_with_sap():
    assert "rise_with_sap" in store.SERVICE_TYPES


def test_service_types_descriptions_cover_all():
    for st in store.SERVICE_TYPES:
        assert st in store.SERVICE_TYPE_DESCRIPTIONS
        assert len(store.SERVICE_TYPE_DESCRIPTIONS[st]) > 0


# ===== normalize_service_type =======================================


def test_normalize_rise_with_sap_passthrough():
    assert store.normalize_service_type("rise_with_sap") == "rise_with_sap"


def test_normalize_rise_alias():
    assert store.normalize_service_type("rise") == "rise_with_sap"


def test_normalize_unknown_raises():
    with pytest.raises(ValueError, match="Service type khong hop le"):
        store.normalize_service_type("foo_bar")


def test_normalize_empty_returns_default():
    assert store.normalize_service_type("") == store.SERVICE_TYPE_DEFAULT
    assert store.normalize_service_type(None) == store.SERVICE_TYPE_DEFAULT


def test_normalize_existing_alias_still_works():
    assert store.normalize_service_type("s4hc") == "s4hc_(public)"


# ===== default_auth_mode_for_service ================================


def test_default_auth_for_public():
    assert store.default_auth_mode_for_service("s4hc_(public)") == "cookie"


def test_default_auth_for_rise_with_sap():
    assert store.default_auth_mode_for_service("rise_with_sap") == "password"


def test_default_auth_for_btp():
    assert store.default_auth_mode_for_service("btp") == "oauth2"


def test_default_auth_for_onprem():
    assert store.default_auth_mode_for_service("onprem") == "password"


def test_default_auth_for_unknown_service():
    assert store.default_auth_mode_for_service("foo") == "oauth2"


# ===== normalize_routing_hints =====================================


def test_normalize_routing_hints_default_for_public():
    hints = store.normalize_routing_hints(None, "s4hc_(public)")
    assert hints["supportsReadonlyClass"] is True
    assert hints["supportsDebug"] is False  # public khong cho external debug
    assert hints["supportsVspSlim"] is True
    assert hints["supportsVspHealth"] is True
    assert hints["supportsDictBridge"] is True
    assert hints["preferredTransport"] == "sap-connect"
    assert hints["preferredAnalysis"] == "sap-vsp"


def test_normalize_routing_hints_default_for_rise():
    hints = store.normalize_routing_hints(None, "rise_with_sap")
    assert hints["supportsDebug"] is True  # rise cho phep external debug


def test_normalize_routing_hints_default_for_btp():
    hints = store.normalize_routing_hints(None, "btp")
    assert hints["supportsDictBridge"] is False  # Steampunk khong cho DDIC


def test_normalize_routing_hints_partial_override():
    hints = store.normalize_routing_hints({"supportsDebug": False}, "rise_with_sap")
    # override field duoc giu
    assert hints["supportsDebug"] is False
    # cac field khac van theo default cua rise (True)
    assert hints["supportsReadonlyClass"] is True


def test_normalize_routing_hints_rejects_unknown_key():
    with pytest.raises(ValueError, match="routingHints co key khong ho tro"):
        store.normalize_routing_hints({"foo": True}, "s4hc_(public)")


def test_normalize_routing_hints_rejects_non_bool():
    with pytest.raises(ValueError, match="supportsDebug phai la bool"):
        store.normalize_routing_hints({"supportsDebug": "yes"}, "s4hc_(public)")


def test_normalize_routing_hints_rejects_bad_transport():
    with pytest.raises(ValueError, match="preferredTransport phai la"):
        store.normalize_routing_hints({"preferredTransport": "sap-foo"}, "s4hc_(public)")


def test_normalize_routing_hints_rejects_bad_analysis():
    with pytest.raises(ValueError, match="preferredAnalysis phai la"):
        store.normalize_routing_hints({"preferredAnalysis": "other"}, "s4hc_(public)")


def test_normalize_routing_hints_accepts_null_analysis():
    hints = store.normalize_routing_hints({"preferredAnalysis": None}, "s4hc_(public)")
    assert hints["preferredAnalysis"] is None


# ===== load_config: lazy upgrade v1 -> v2 ==========================


def test_load_default_config_returns_v2(fresh_home):
    # Khong co file, tra ve DEFAULT_CONFIG (version=2, routingHints present)
    cfg = store.load_config("nonexistent")
    assert cfg["version"] == 2
    assert "routingHints" in cfg
    assert cfg["routingHints"]["preferredTransport"] == "sap-connect"


def test_load_v1_config_upgrades_to_v2(fresh_home, tmp_path):
    # Viet 1 file v1 cu
    app_dir = tmp_path / "app"
    profiles = app_dir / "profiles" / "legacy1"
    profiles.mkdir(parents=True)
    (profiles / "config.json").write_text(json.dumps({
        "version": 1,
        "btpUrl": "https://test.s4hana.cloud.sap",
        "service": "s4hc",  # alias cu
        "authMode": "cookie",
    }), encoding="utf-8")
    cfg = store.load_config("legacy1")
    # Doc path: tra ve version 2, service normalized, routingHints dien default
    assert cfg["version"] == 2
    assert cfg["service"] == "s4hc_(public)"  # alias resolved
    assert "routingHints" in cfg
    assert cfg["routingHints"]["supportsReadonlyClass"] is True
    # File tren dia CHUA duoc ghi (lazy upgrade, chi khi save_config moi ghi)
    raw = json.loads((profiles / "config.json").read_text(encoding="utf-8"))
    assert raw["version"] == 1, "Read path KHONG duoc ghi dia"


# ===== save_config: bump v1 -> v2 + backup =========================


def test_save_config_bumps_v1_to_v2_with_backup(fresh_home, tmp_path):
    app_dir = tmp_path / "app"
    profiles = app_dir / "profiles" / "upg1"
    profiles.mkdir(parents=True)
    (profiles / "config.json").write_text(json.dumps({
        "version": 1,
        "btpUrl": "https://test.s4hana.cloud.sap",
        "service": "s4hc",
    }), encoding="utf-8")
    result = store.save_config("upg1", {"clientId": "test-client"})
    assert result["config"]["version"] == 2
    assert result["config"]["service"] == "s4hc_(public)"
    assert "routingHints" in result["config"]
    assert result["upgradedFromV1"] is True
    assert result["backupPath"] is not None
    backup = Path(result["backupPath"])
    assert backup.exists()
    backup_data = json.loads(backup.read_text(encoding="utf-8"))
    assert backup_data["version"] == 1  # backup giu ban goc


def test_save_config_does_not_backup_when_already_v2(fresh_home, tmp_path):
    app_dir = tmp_path / "app"
    profiles = app_dir / "profiles" / "v2only"
    profiles.mkdir(parents=True)
    (profiles / "config.json").write_text(json.dumps({
        "version": 2,
        "btpUrl": "https://test.s4hana.cloud.sap",
        "service": "rise_with_sap",
        "routingHints": store._default_routing_hints("rise_with_sap"),
    }), encoding="utf-8")
    result = store.save_config("v2only", {"clientId": "c2"})
    assert result["upgradedFromV1"] is False
    assert result["backupPath"] is None


def test_save_config_validates_service_and_hints(fresh_home, tmp_path):
    app_dir = tmp_path / "app"
    profiles = app_dir / "profiles" / "val1"
    profiles.mkdir(parents=True)
    (profiles / "config.json").write_text(json.dumps({
        "version": 1, "btpUrl": "x", "service": "s4hc",
    }), encoding="utf-8")
    # Bad service phai raise
    with pytest.raises(ValueError, match="Service type khong hop le"):
        store.save_config("val1", {"service": "totally-invalid"})
    # Bad routingHints phai raise
    with pytest.raises(ValueError, match="routingHints co key khong ho tro"):
        store.save_config("val1", {"routingHints": {"unknown_field": True}})
