"""Tests for reference/scripts/validate_team_setup.py."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import validate_team_setup as vts  # noqa: E402


def test_check_python_passes_on_310_plus():
    c = vts.check_python()
    assert c.ok is True
    assert c.required is True


def test_run_checks_persona_c_skips_mcp_path():
    checks = vts.run_checks("C")
    names = [c.name for c in checks]
    assert "Python >= 3.10" in names
    assert "Claude Code CLI (claude)" in names
    assert not any(n.startswith("mcp-sap-connect on PATH") for n in names)


def test_main_returns_int():
    code = vts.main(["--persona", "C"])
    assert code in (0, 1)
