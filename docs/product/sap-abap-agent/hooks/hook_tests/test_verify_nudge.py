"""Tests for hooks/verify_nudge.py soft Stop gate helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

VERIFY_NUDGE = Path(__file__).resolve().parent.parent / "verify_nudge.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("verify_nudge", VERIFY_NUDGE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_clears_verify_pending_helper():
    mod = _load_mod()
    assert mod.clears_verify_pending("mcp__sap-connect__sap_activate")
    assert mod.clears_verify_pending("sap_run_unit_tests")
    assert mod.clears_verify_pending("sap_syntax_check")
    assert mod.clears_verify_pending("sap_ping")
    assert not mod.clears_verify_pending("mcp__sap-connect__sap_search")
    assert not mod.clears_verify_pending("sap_read_source")
    assert not mod.clears_verify_pending("")


def test_tool_name_from_payload():
    mod = _load_mod()
    assert mod.tool_name_from_payload({"tool_name": "sap_ping"}) == "sap_ping"
    assert mod.tool_name_from_payload({"toolName": "sap_activate"}) == "sap_activate"
    assert mod.tool_name_from_payload({"tool_input": {"name": "sap_syntax_check"}}) == (
        "sap_syntax_check"
    )
    assert mod.tool_name_from_payload({}) == ""
