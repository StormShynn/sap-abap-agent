"""Unit tests for hooks/zy_namespace_guard.py (PreToolUse Z/Y namespace guard)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent
GUARD = HOOKS_DIR / "zy_namespace_guard.py"

# Every sap_create_* / name-bound publish tool from dictionary.py build_dict_tools().
DICT_BRIDGE_TOOLS = (
    "sap_create_domain",
    "sap_create_data_element",
    "sap_create_table",
    "sap_create_cds_view",
    "sap_create_service_definition",
    "sap_create_metadata_extension",
    "sap_create_access_control",
    "sap_create_class",
    "sap_create_interface",
    "sap_create_package",
    "sap_create_bdef",
    "sap_create_service_binding",
    "sap_publish_service_binding",
)


def _run_guard(payload: dict | str) -> subprocess.CompletedProcess:
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=15,
        encoding="utf-8",
    )


def _block_decision(stdout: str) -> dict | None:
    text = stdout.strip()
    if not text:
        return None
    return json.loads(text)


class TestGuardBasics:
    def test_exists(self):
        assert GUARD.is_file()

    def test_malformed_json_fails_open(self):
        out = _run_guard("{not-json")
        assert out.returncode == 0
        assert out.stdout.strip() == ""

    def test_unknown_tool_passes(self):
        out = _run_guard(
            {
                "tool_name": "sap_read_source",
                "tool_input": {"name": "MARA"},
            }
        )
        assert out.returncode == 0
        assert out.stdout.strip() == ""

    def test_missing_name_fails_open(self):
        out = _run_guard(
            {
                "tool_name": "sap_create_table",
                "tool_input": {"package": "$TMP"},
            }
        )
        assert out.returncode == 0
        assert out.stdout.strip() == ""


@pytest.mark.parametrize("tool", DICT_BRIDGE_TOOLS)
class TestDictBridgeCoverage:
    def test_blocks_standard_sap_name(self, tool: str):
        out = _run_guard(
            {
                "tool_name": tool,
                "tool_input": {"name": "MARA"},
            }
        )
        assert out.returncode == 0
        decision = _block_decision(out.stdout)
        assert decision is not None, f"{tool} should block MARA"
        assert decision["decision"] == "block"
        assert "MARA" in decision["reason"]

    def test_allows_z_prefix(self, tool: str):
        out = _run_guard(
            {
                "tool_name": tool,
                "tool_input": {"name": "ZTB_HEADER"},
            }
        )
        assert out.returncode == 0
        assert out.stdout.strip() == ""

    def test_allows_y_prefix(self, tool: str):
        out = _run_guard(
            {
                "tool_name": f"mcp__sap-dict-bridge__{tool}",
                "tool_input": {"name": "YCL_HELPER"},
            }
        )
        assert out.returncode == 0
        assert out.stdout.strip() == ""

    def test_allows_registered_namespace(self, tool: str):
        out = _run_guard(
            {
                "tool_name": tool,
                "tool_input": {"name": "/ACME/CL_HELPER"},
            }
        )
        assert out.returncode == 0
        assert out.stdout.strip() == ""


class TestNameFieldsAndAdt:
    def test_object_name_field(self):
        out = _run_guard(
            {
                "tool_name": "sap_create_class",
                "tool_input": {"object_name": "CL_SALV_TABLE"},
            }
        )
        decision = _block_decision(out.stdout)
        assert decision is not None
        assert decision["decision"] == "block"

    def test_adt_create_domain_blocked(self):
        out = _run_guard(
            {
                "tool_name": "CreateDomain",
                "tool_input": {"name": "DOM_STATUS"},
            }
        )
        decision = _block_decision(out.stdout)
        assert decision is not None
        assert decision["decision"] == "block"

    def test_adt_update_table_allows_z(self):
        out = _run_guard(
            {
                "tool_name": "UpdateTable",
                "tool_input": {"name": "ZTB_OK"},
            }
        )
        assert out.returncode == 0
        assert out.stdout.strip() == ""
