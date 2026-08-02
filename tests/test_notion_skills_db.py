"""Tests for reference/scripts/notion_skills_db.py pin helpers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import notion_skills_db as nsd  # noqa: E402


def test_get_set_clear_pin(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    assert nsd.get_pinned_id() is None
    path = nsd.set_pinned_id("abcdef0123456789abcdef0123456789")
    assert path.is_file()
    assert nsd.get_pinned_id() == "abcdef0123456789abcdef0123456789"
    assert nsd.clear_pinned_id() is True
    assert nsd.get_pinned_id() is None


def test_env_overrides_file(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    nsd.set_pinned_id("fileid0123456789abcdef0123456789ab")
    monkeypatch.setenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", "envid0123456789abcdef0123456789ab")
    assert nsd.get_pinned_id() == "envid0123456789abcdef0123456789ab"


def test_set_accepts_notion_url(tmp_path, monkeypatch):
    monkeypatch.setenv("SAP_ABAP_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SAP_ABAP_AGENT_NOTION_SKILLS_DB", raising=False)
    url = (
        "https://www.notion.so/workspace/"
        "abcdef0123456789abcdef0123456789?v=deadbeef"
    )
    nsd.set_pinned_id(url)
    assert nsd.get_pinned_id() == "abcdef0123456789abcdef0123456789"
