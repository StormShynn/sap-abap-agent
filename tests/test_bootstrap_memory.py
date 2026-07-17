"""Test cho reference/scripts/bootstrap_memory.py (idempotent memory init).

Test focus:
  - render_progress(today): pure function, deterministic output
  - _ensure_dir(path): idempotent
  - _ensure_file(path, content, force=False): created/kept/overwritten logic
  - _resolve_under_home(home, subpath): path traversal protection (reject absolute + parent-escape)
  - main(): end-to-end CLI with tmp_path as SAP_ABAP_AGENT_HOME override
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import bootstrap_memory as bm  # noqa: E402


# ---------- render_progress ----------

def test_render_progress_includes_modules():
    out = bm.render_progress("2026-07-17")
    for m in bm.PROGRESS_MODULES:
        assert f"| {m} |" in out, f"Missing module row for {m}"


def test_render_progress_includes_today_date():
    out = bm.render_progress("2026-07-17")
    assert "Last updated: 2026-07-17" in out


def test_render_progress_contains_header():
    out = bm.render_progress("2026-07-17")
    assert out.startswith("# SAP Learning Progress")
    assert "## Module Progress" in out
    assert "## Recommended Next Module" in out


def test_render_progress_module_count():
    """Tat ca modules trong PROGRESS_MODULES deu co row."""
    out = bm.render_progress("2026-07-17")
    rows = [l for l in out.splitlines() if l.startswith("| ") and "|" in l[2:]]
    # 1 header row + N module rows = N+1 rows co '|'
    assert len(rows) == 1 + len(bm.PROGRESS_MODULES)


# ---------- _ensure_dir ----------

def test_ensure_dir_creates(tmp_path):
    p = tmp_path / "a" / "b" / "c"
    assert bm._ensure_dir(p) is True  # created
    assert p.is_dir()


def test_ensure_dir_idempotent(tmp_path):
    p = tmp_path / "x"
    p.mkdir()
    assert bm._ensure_dir(p) is False  # already exists
    assert p.is_dir()


# ---------- _ensure_file ----------

def test_ensure_file_creates_when_missing(tmp_path):
    p = tmp_path / "new.md"
    result = bm._ensure_file(p, "default content")
    assert result == "created"
    assert p.read_text(encoding="utf-8") == "default content"


def test_ensure_file_kept_when_nonempty(tmp_path):
    p = tmp_path / "existing.md"
    p.write_text("user data here", encoding="utf-8")
    result = bm._ensure_file(p, "default content")
    assert result == "kept"
    assert p.read_text(encoding="utf-8") == "user data here"


def test_ensure_file_overwrite_empty(tmp_path):
    """File empty -> ghi de default (van return created)."""
    p = tmp_path / "empty.md"
    p.write_text("", encoding="utf-8")
    result = bm._ensure_file(p, "default content")
    # existing.strip() = "" falsy -> treated as created
    assert result == "created"
    assert p.read_text(encoding="utf-8") == "default content"


def test_ensure_file_force_overwrite(tmp_path):
    p = tmp_path / "existing.md"
    p.write_text("user data", encoding="utf-8")
    result = bm._ensure_file(p, "default content", force=True)
    assert result == "overwritten"
    assert p.read_text(encoding="utf-8") == "default content"


# ---------- _resolve_under_home ----------

def test_resolve_under_home_simple(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    out = bm._resolve_under_home(home, "memory/semantic")
    assert out == (home / "memory" / "semantic").resolve()


def test_resolve_under_home_rejects_absolute(tmp_path):
    """Absolute path ben ngoai home phai bi reject."""
    import pytest
    home = tmp_path / "home"
    home.mkdir()
    with pytest.raises(ValueError):
        bm._resolve_under_home(home, "/etc/passwd")


def test_resolve_under_home_rejects_parent_escape(tmp_path):
    """Path chua '../' de escape ra ngoai home phai bi reject."""
    import pytest
    home = tmp_path / "home"
    home.mkdir()
    with pytest.raises(ValueError):
        bm._resolve_under_home(home, "../escape/secret")


def test_resolve_under_home_does_not_resolve_outside(tmp_path):
    """Du absolute hay tuong doi, neu resolved path khong thuoc home -> reject."""
    import pytest
    home = tmp_path / "home"
    home.mkdir()
    with pytest.raises(ValueError):
        bm._resolve_under_home(home, "../../../Windows/System32")


# ---------- main() end-to-end (via subprocess + SAP_ABAP_AGENT_HOME override) ----------


def test_main_via_cli_subprocess(tmp_path):
    """Smoke test: chay CLI script voi SAP_ABAP_AGENT_HOME override."""
    home = tmp_path / "agent-home"
    home.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "bootstrap_memory.py")],
        env={
            **__import__("os").environ,
            "SAP_ABAP_AGENT_HOME": str(home),
        },
        capture_output=True,
        timeout=10,
    )
    # Script co the in ra stdout (descriptive), exit 0
    assert result.returncode == 0, f"stderr: {result.stderr.decode('utf-8', errors='replace')}"

    # Verify LEARNING_PROGRESS.md da duoc tao
    progress = home / "memory" / "semantic" / "LEARNING_PROGRESS.md"
    assert progress.exists(), "LEARNING_PROGRESS.md phai duoc tao"
    text = progress.read_text(encoding="utf-8")
    assert "Last updated:" in text
    assert "SD |" in text or "| SD " in text


def test_main_idempotent(tmp_path):
    """Chay 2 lan lien tiep -> khong gay loi, khong mat data user."""
    home = tmp_path / "agent-home"
    home.mkdir()

    env = {**__import__("os").environ, "SAP_ABAP_AGENT_HOME": str(home)}

    r1 = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "bootstrap_memory.py")],
        env=env, capture_output=True, timeout=10,
    )
    assert r1.returncode == 0

    # User sua LEARNING_PROGRESS.md
    progress = home / "memory" / "semantic" / "LEARNING_PROGRESS.md"
    progress.write_text("# Custom user content\n", encoding="utf-8")

    # Chay lai lan 2
    r2 = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "bootstrap_memory.py")],
        env=env, capture_output=True, timeout=10,
    )
    assert r2.returncode == 0

    # User data KHONG bi ghi de
    assert progress.read_text(encoding="utf-8") == "# Custom user content\n"
