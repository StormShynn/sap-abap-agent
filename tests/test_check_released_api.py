"""Test cho reference/scripts/check_released_api.py - smoke test whitelist behavior."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import check_released_api as cra  # noqa: E402


def _write_abap(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_clean_code_passes(tmp_path):
    _write_abap(tmp_path, "zcl_clean.clas.abap", "DATA(lv_x) = 1.\nWRITE: / lv_x.\n")
    issues = cra.check_dir(tmp_path)
    assert issues == [], f"Expected no issues, got: {issues}"


def test_cl_gui_detected(tmp_path):
    _write_abap(
        tmp_path,
        "zcl_x.clas.abap",
        "DATA lo TYPE REF TO cl_gui_alv_grid.\n",
    )
    issues = cra.check_dir(tmp_path)
    assert any(i["severity"] == "ERROR" and "CL_GUI" in i["pattern"] for i in issues), issues


def test_call_transaction_detected(tmp_path):
    _write_abap(
        tmp_path,
        "zprog.prog.abap",
        "CALL TRANSACTION 'VA01'.\n",
    )
    issues = cra.check_dir(tmp_path)
    assert any("CALL TRANSACTION" in i["message"] for i in issues), issues


def test_authority_check_detected(tmp_path):
    _write_abap(
        tmp_path,
        "zauth.clas.abap",
        "AUTHORITY-CHECK OBJECT 'S_TCODE'.\n",
    )
    issues = cra.check_dir(tmp_path)
    assert any("AUTHORITY-CHECK" in i["pattern"] for i in issues), issues


def test_select_star_warn(tmp_path):
    _write_abap(
        tmp_path,
        "zs.prog.abap",
        "SELECT * FROM mara INTO TABLE lt_mara.\n",
    )
    issues = cra.check_dir(tmp_path)
    assert any(i["severity"] == "WARN" and "SELECT *" in i["message"] for i in issues), issues


def test_comment_lines_skipped(tmp_path):
    _write_abap(
        tmp_path,
        "zcomments.clas.abap",
        "* comment: CALL TRANSACTION 'VA01'\n"
        "\" comment: AUTHORITY-CHECK OBJECT 'S_TCODE'\n"
        "// comment: cl_gui_alv_grid create\n",
    )
    issues = cra.check_dir(tmp_path)
    assert issues == [], f"Expected comments skipped, got: {issues}"


def test_non_abap_files_skipped(tmp_path):
    _write_abap(tmp_path, "readme.md", "CALL TRANSACTION 'VA01'\n")
    _write_abap(tmp_path, "config.json", '{"k": "AUTHORITY-CHECK"}')
    issues = cra.check_dir(tmp_path)
    assert issues == [], f"Expected non-ABAP files skipped, got: {issues}"
