"""Tests for hooks/ Python wrappers.

Cac hook nay duoc goi tu hooks.json cua Claude Code:
  - session_start_skill.py  (SessionStart)
  - post_tool_select_star.py (PostToolUse / Edit|Write)

Test o day chi smoke test:
  - subprocess.run khong crash
  - Output JSON contract (session_start_skill) dung format
  - Stderr warning (post_tool_select_star) xuat hien khi file co SELECT *
  - Exits 0 (canh bao, khong block)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent
SESSION_HOOK = HOOKS_DIR / "session_start_skill.py"
SELECT_STAR_HOOK = HOOKS_DIR / "post_tool_select_star.py"


def _run_hook(script: Path, stdin_payload: str = "") -> subprocess.CompletedProcess:
    """Chay mot hook script voi stdin tuy chon. Tra ve CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(script)],
        input=stdin_payload,
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
    )


class TestSessionStartSkill:
    """Smoke test cho SessionStart hook wrapper."""

    def test_exists(self):
        assert SESSION_HOOK.is_file(), f"missing: {SESSION_HOOK}"

    def test_emits_valid_json(self):
        out = _run_hook(SESSION_HOOK)
        assert out.returncode == 0, f"exit {out.returncode}: {out.stderr}"
        # JSON contract: hookSpecificOutput.hookEventName + additionalContext
        data = json.loads(out.stdout)
        assert "hookSpecificOutput" in data
        hook_out = data["hookSpecificOutput"]
        assert hook_out["hookEventName"] == "SessionStart"
        assert isinstance(hook_out["additionalContext"], str)
        assert len(hook_out["additionalContext"]) > 0

    def test_includes_routing_discipline_skill(self):
        """SessionStart phai include body cua sap-routing-discipline (skill chinh)."""
        out = _run_hook(SESSION_HOOK)
        data = json.loads(out.stdout)
        context = data["hookSpecificOutput"]["additionalContext"]
        # Routing discipline co marker "# SAP Routing Discipline" o dau body
        assert "Routing Discipline" in context or "routing" in context.lower()
        # Hoac ask-before-guessing
        assert "guessing" in context.lower() or "Ask Before Guessing" in context

    def test_no_stderr_output(self):
        """Khong output gi ra stderr (hook chi emit JSON qua stdout)."""
        out = _run_hook(SESSION_HOOK)
        assert out.stderr == "", f"unexpected stderr: {out.stderr!r}"


class TestPostToolSelectStar:
    """Smoke test cho PostToolUse SELECT * warning hook."""

    def test_exists(self):
        assert SELECT_STAR_HOOK.is_file(), f"missing: {SELECT_STAR_HOOK}"

    def test_empty_stdin_exits_zero(self):
        out = _run_hook(SELECT_STAR_HOOK)
        assert out.returncode == 0

    def test_non_abap_file_no_warning(self):
        payload = json.dumps({"tool_input": {"file_path": "README.md"}})
        out = _run_hook(SELECT_STAR_HOOK, payload)
        assert out.returncode == 0
        assert "SELECT *" not in out.stderr
        assert out.stdout == ""

    def test_abap_file_no_select_star_no_warning(self):
        """File .abap KHONG co SELECT * -> khong canh bao."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".abap", delete=False, encoding="utf-8"
        ) as f:
            f.write("SELECT field1 field2 FROM ztest INTO TABLE lt_data.\n")
            tmp_path = f.name
        try:
            payload = json.dumps({"tool_input": {"file_path": tmp_path}})
            out = _run_hook(SELECT_STAR_HOOK, payload)
            assert out.returncode == 0
            assert "SELECT *" not in out.stderr
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_abap_file_with_select_star_warns(self):
        """File .abap co SELECT * -> in canh bao ra stderr, exit 0."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".abap", delete=False, encoding="utf-8"
        ) as f:
            f.write("SELECT * FROM ztest INTO TABLE lt_data.\n")
            tmp_path = f.name
        try:
            payload = json.dumps({"tool_input": {"file_path": tmp_path}})
            out = _run_hook(SELECT_STAR_HOOK, payload)
            assert out.returncode == 0, "hook should warn, not crash"
            assert "SELECT *" in out.stderr, f"missing warning in: {out.stderr!r}"
            assert "sap-abap-agent" in out.stderr
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_malformed_json_exits_zero(self):
        """JSON loi -> thoat 0 (khong crash hook)."""
        out = _run_hook(SELECT_STAR_HOOK, "{not-json")
        assert out.returncode == 0

    def test_hooks_json_schema(self):
        """File hooks.json phai hop le JSON va co cac event can thiet."""
        hooks_json = HOOKS_DIR / "hooks.json"
        assert hooks_json.is_file()
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
        assert "hooks" in data
        # SessionStart, PreToolUse, PostToolUse, Stop (RFC Claude Code hook events)
        for event in ["SessionStart", "PreToolUse", "PostToolUse", "Stop"]:
            assert event in data["hooks"], f"missing hook event: {event}"
