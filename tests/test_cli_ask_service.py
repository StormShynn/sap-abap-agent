"""Test _ask_service() cho Phase 2 cua plan sap-multi-system-router.

Cover:
  - Menu hien thi ca 5 service type kem mo ta (SERVICE_TYPE_DESCRIPTIONS phai duoc import dung)
  - Input hop le (gia tri moi + alias cu) duoc normalize dung
  - Input khong hop le -> retry voi menu day du (khong crash do bien khong ton tai)
"""
from __future__ import annotations

from unittest.mock import patch

from mcp_sap_connect.cli import _ask_service
from mcp_sap_connect.config.store import SERVICE_TYPES, SERVICE_TYPE_DESCRIPTIONS


def test_menu_lists_all_five_service_types_with_descriptions():
    with patch("mcp_sap_connect.cli.ask", return_value="s4hc_(public)") as m:
        _ask_service()
    prompt = m.call_args_list[0].args[0]
    for st in SERVICE_TYPES:
        assert st in prompt
        assert SERVICE_TYPE_DESCRIPTIONS[st] in prompt


def test_accepts_new_value_passthrough():
    with patch("mcp_sap_connect.cli.ask", return_value="rise_with_sap"):
        assert _ask_service() == "rise_with_sap"


def test_accepts_legacy_alias():
    with patch("mcp_sap_connect.cli.ask", return_value="rise"):
        assert _ask_service() == "rise_with_sap"


def test_invalid_input_reprompts_with_menu_and_recovers():
    with patch("mcp_sap_connect.cli.ask", side_effect=["bogus", "onprem"]) as m:
        assert _ask_service() == "onprem"
    retry_prompt = m.call_args_list[1].args[0]
    for st in SERVICE_TYPES:
        assert st in retry_prompt
