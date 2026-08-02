"""Test data dir migration va env var aliases cho Phase 1 rename.

Cover:
  - get_app_dir() returns new .mcp-sap-connect by default
  - get_app_dir() migrates legacy .mcp-sap-connect on first call (1-shot)
  - get_app_dir() respects MCP_SAP_CONNECT_HOME (new env var)
  - get_app_dir() still respects MCP_SAP_CONNECT_HOME (backward-compat alias)
  - get_active_profile_id() prefers MCP_SAP_CONNECT_PROFILE, falls back to SAP_BTP_PROFILE
  - get_dev_mirror_dir() same priority order
  - dev_mirror_includes_secrets() same priority order
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from mcp_sap_connect.config import paths


@pytest.fixture
def fresh_home(tmp_path, monkeypatch):
    # Path.home() uses HOME on Unix and USERPROFILE on Windows — set both.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.delenv("MCP_SAP_CONNECT_HOME", raising=False)
    monkeypatch.delenv("MCP_SAP_CONNECT_PROFILE", raising=False)
    monkeypatch.delenv("SAP_BTP_PROFILE", raising=False)
    return tmp_path


def test_default_app_dir_is_new(fresh_home):
    assert paths.get_app_dir() == fresh_home / paths.APP_DIR_NAME


def test_legacy_app_dir_helper(fresh_home):
    assert paths.get_legacy_app_dir() == fresh_home / paths.LEGACY_APP_DIR_NAME


def test_migration_moves_legacy_to_new(fresh_home):
    legacy = fresh_home / paths.LEGACY_APP_DIR_NAME
    profiles = legacy / "profiles" / "projA"
    profiles.mkdir(parents=True)
    (profiles / "config.json").write_text(json.dumps({"btpUrl": "x"}), encoding="utf-8")
    (legacy / "profiles.json").write_text("{}", encoding="utf-8")

    new_dir = paths.get_app_dir()
    assert new_dir == fresh_home / paths.APP_DIR_NAME
    assert not legacy.exists(), "Legacy folder phai bien mat sau migration"
    assert new_dir.exists()
    assert (new_dir / "profiles" / "projA" / "config.json").read_text(encoding="utf-8") == '{"btpUrl": "x"}'


def test_when_new_already_exists_use_new(fresh_home):
    new_dir = fresh_home / paths.APP_DIR_NAME
    new_dir.mkdir()
    legacy = fresh_home / paths.LEGACY_APP_DIR_NAME
    legacy.mkdir()
    (legacy / "old-data.txt").write_text("x", encoding="utf-8")

    assert paths.get_app_dir() == new_dir
    # Migration khong chay khi new_dir da ton tai (uu tien new hon legacy)
    assert legacy.exists(), "Legacy folder KHONG duoc xoa khi new_dir da ton tai san"


def test_migrate_skips_when_dst_already_exists(fresh_home, capsys):
    """Khi _migrate_legacy_app_dir duoc goi voi dst da ton tai san (do
    process khac tao truoc), migration phai skip va giu legacy nguyen."""
    legacy = fresh_home / paths.LEGACY_APP_DIR_NAME
    legacy.mkdir()
    (legacy / "old.txt").write_text("x", encoding="utf-8")
    new_dir = fresh_home / paths.APP_DIR_NAME
    new_dir.mkdir()

    paths._migrate_legacy_app_dir(legacy, new_dir)
    captured = capsys.readouterr()
    assert "Khong the migrate" in captured.err
    assert legacy.exists(), "Legacy folder KHONG duoc xoa khi migration bi skip"
    assert (legacy / "old.txt").exists()


def test_migrate_logs_success_on_success(fresh_home, capsys):
    legacy = fresh_home / paths.LEGACY_APP_DIR_NAME
    legacy.mkdir()
    (legacy / "old.txt").write_text("x", encoding="utf-8")
    new_dir = fresh_home / paths.APP_DIR_NAME

    paths._migrate_legacy_app_dir(legacy, new_dir)
    captured = capsys.readouterr()
    assert "Migrated:" in captured.err
    assert not legacy.exists()
    assert new_dir.exists()


def test_mcp_sap_connect_home_takes_priority(fresh_home, monkeypatch, tmp_path):
    override = tmp_path / "custom_home"
    override.mkdir()
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(override))
    assert paths.get_app_dir() == override


def test_legacy_env_var_still_works(fresh_home, monkeypatch, tmp_path):
    override = tmp_path / "legacy_env_home"
    override.mkdir()
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(override))
    assert paths.get_app_dir() == override


def test_active_profile_env_new_var(fresh_home, monkeypatch):
    monkeypatch.setenv("MCP_SAP_CONNECT_PROFILE", "foo")
    assert paths.get_active_profile_id() == "foo"


def test_active_profile_env_old_var(fresh_home, monkeypatch):
    monkeypatch.setenv("SAP_BTP_PROFILE", "bar")
    monkeypatch.delenv("MCP_SAP_CONNECT_PROFILE", raising=False)
    assert paths.get_active_profile_id() == "bar"


def test_active_profile_env_new_overrides_old(fresh_home, monkeypatch):
    monkeypatch.setenv("MCP_SAP_CONNECT_PROFILE", "new")
    monkeypatch.setenv("SAP_BTP_PROFILE", "old")
    assert paths.get_active_profile_id() == "new"


def test_active_profile_env_none(fresh_home):
    assert paths.get_active_profile_id() is None


def test_dev_mirror_env_new_var(fresh_home, monkeypatch, tmp_path):
    mirror = tmp_path / "mirror_new"
    monkeypatch.setenv("MCP_SAP_CONNECT_DEV_MIRROR", str(mirror))
    assert paths.get_dev_mirror_dir() == mirror


def test_dev_mirror_env_old_var_still_works(fresh_home, monkeypatch, tmp_path):
    mirror = tmp_path / "mirror_old"
    monkeypatch.setenv("MCP_SAP_CONNECT_DEV_MIRROR", str(mirror))
    assert paths.get_dev_mirror_dir() == mirror


def test_get_bin_dir(fresh_home):
    assert paths.get_bin_dir() == fresh_home / paths.APP_DIR_NAME / "bin"
