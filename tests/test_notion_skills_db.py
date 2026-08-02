"""Tests for reference/scripts/notion_skills_db.py resolve helpers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import notion_skills_db as nsd  # noqa: E402


def test_default_when_no_pin(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    assert nsd.get_pinned_id() is None
    assert nsd.get_database_id() == nsd.DEFAULT_DATABASE_ID
    assert nsd.resolve_database_id() == (nsd.DEFAULT_DATABASE_ID, "default")


def test_get_set_clear_pin(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    path = nsd.set_pinned_id("abcdef0123456789abcdef0123456789")
    assert path.is_file()
    assert nsd.get_pinned_id() == "abcdef0123456789abcdef0123456789"
    assert nsd.resolve_database_id() == ("abcdef0123456789abcdef0123456789", "pin")
    assert nsd.clear_pinned_id() is True
    assert nsd.get_pinned_id() is None
    assert nsd.get_database_id() == nsd.DEFAULT_DATABASE_ID


def test_env_overrides_file_and_default(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    nsd.set_pinned_id("fileid0123456789abcdef0123456789ab")
    monkeypatch.setenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", "envid0123456789abcdef0123456789ab")
    assert nsd.resolve_database_id() == ("envid0123456789abcdef0123456789ab", "env")


def test_set_accepts_notion_so_url(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    url = (
        "https://www.notion.so/workspace/"
        "abcdef0123456789abcdef0123456789?v=deadbeef"
    )
    nsd.set_pinned_id(url)
    assert nsd.get_pinned_id() == "abcdef0123456789abcdef0123456789"


def test_set_accepts_app_notion_com_url(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    url = (
        "https://app.notion.com/p/stormshynn/"
        "9d54b58613ad485f8b8f19909adbb219?v=154a2b18ed8f4d41ba9448c9bed75d4e"
    )
    nsd.set_pinned_id(url)
    assert nsd.get_pinned_id() == "9d54b58613ad485f8b8f19909adbb219"


def test_cli_get_source_default(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    assert nsd.main(["get", "--source"]) == 0
    out = capsys.readouterr().out.strip()
    assert out == f"{nsd.DEFAULT_DATABASE_ID}\tdefault"
