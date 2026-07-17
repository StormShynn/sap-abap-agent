"""Test bo sung cho check phuc tap trong reference/scripts/validate_plugin.py.

Bao gom:
  - check_duplicate_lines (4 test)
  - check_core_deep_size (3 test)
  - check_tool_count_drift (3 test)
  - check_routing_matrix_coverage (4 test)
  - _real_skill_count / _real_module_count (3 test)

Tat ca test dung tmp_path de fake ROOT, tranh doc thu muc that.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import validate_plugin as vp  # noqa: E402


def _make_fake_repo(tmp_path: Path) -> Path:
    """Tao cay thu muc toi thieu de check_* khong bi skip."""
    fake = tmp_path / "fake"
    (fake / "agents").mkdir(parents=True)
    (fake / "skills").mkdir()
    (fake / "reference" / "modules").mkdir(parents=True)
    return fake


# ---------- check_duplicate_lines ----------

def test_check_duplicate_lines_clean(tmp_path, monkeypatch):
    """File md khong co 2 dong lien tiep giong nhau -> khong FAIL."""
    fake = _make_fake_repo(tmp_path)
    md = fake / "agents" / "sap-test.md"
    md.write_text(
        "---\nname: x\n---\n\n"
        "line 1\nline 2 different\nline 3 also diff\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_duplicate_lines()
    assert not any("[dup-block]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_duplicate_lines_flags_long_dup(tmp_path, monkeypatch):
    """Hai dong lien tiep giong nhau >= 40 ky tu -> FAIL."""
    fake = _make_fake_repo(tmp_path)
    md = fake / "agents" / "sap-dup.md"
    long_dup = "x" * 60
    md.write_text(long_dup + "\n" + long_dup + "\n", encoding="utf-8")
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_duplicate_lines()
    assert any("[dup-block]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_duplicate_lines_short_dup_ignored(tmp_path, monkeypatch):
    """Dup ngan (< 40 ky tu) khong bi flag - muc dich tranh false-positive o text ngan."""
    fake = _make_fake_repo(tmp_path)
    md = fake / "agents" / "sap-short.md"
    short = "---"
    md.write_text(short + "\n" + short + "\n", encoding="utf-8")
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_duplicate_lines()
    assert not any("[dup-block]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_duplicate_lines_skips_git_in_out(tmp_path, monkeypatch):
    """File trong .git/ va in/ out/ duoc bo qua."""
    fake = _make_fake_repo(tmp_path)
    (fake / ".git").mkdir()
    (fake / "in").mkdir()
    (fake / "out").mkdir()

    long_dup = "x" * 60
    (fake / ".git" / "should_skip.md").write_text(long_dup + "\n" + long_dup, encoding="utf-8")
    (fake / "in" / "should_skip.md").write_text(long_dup + "\n" + long_dup, encoding="utf-8")
    (fake / "out" / "should_skip.md").write_text(long_dup + "\n" + long_dup, encoding="utf-8")

    # 1 file legit trong agents/ cung khong co dup
    (fake / "agents" / "sap-ok.md").write_text("clean line\n", encoding="utf-8")

    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_duplicate_lines()
    assert not any("[dup-block]" in f for f in vp.FAILURES), vp.FAILURES


# ---------- check_core_deep_size ----------

def test_check_core_deep_size_no_deep_no_fail(tmp_path, monkeypatch):
    """Module chi co SKILL.md (khong co deep/) -> khong FAIL."""
    fake = _make_fake_repo(tmp_path)
    mod = fake / "reference" / "modules" / "sap-x-cloud"
    mod.mkdir()
    (mod / "SKILL.md").write_text("a\n" * 100, encoding="utf-8")  # 100 dong, vuot limit
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_core_deep_size()
    # Khong co deep/ -> check skip
    assert not any("[core-size]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_core_deep_size_under_limit_ok(tmp_path, monkeypatch):
    """Module co deep/, SKILL.md < 30 dong -> OK."""
    fake = _make_fake_repo(tmp_path)
    mod = fake / "reference" / "modules" / "sap-x-cloud"
    (mod / "deep").mkdir(parents=True)
    (mod / "SKILL.md").write_text("\n".join(f"line {i}" for i in range(10)), encoding="utf-8")
    (mod / "deep" / "SKILL.md").write_text("deep content", encoding="utf-8")
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_core_deep_size()
    assert not any("[core-size]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_core_deep_size_over_limit_fails(tmp_path, monkeypatch):
    """Module co deep/, SKILL.md > 30 dong -> FAIL."""
    fake = _make_fake_repo(tmp_path)
    mod = fake / "reference" / "modules" / "sap-x-cloud"
    (mod / "deep").mkdir(parents=True)
    (mod / "SKILL.md").write_text("\n".join(f"line {i}" for i in range(35)), encoding="utf-8")
    (mod / "deep" / "SKILL.md").write_text("deep", encoding="utf-8")
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_core_deep_size()
    assert any("[core-size]" in f and "35 lines" in f for f in vp.FAILURES), vp.FAILURES


# ---------- check_tool_count_drift ----------

def _make_registry(fake: Path, count: int) -> None:
    """Tao registry.py gia voi N sap_* tool."""
    reg = fake / "reference" / "mcp-server" / "sap_btp_agent" / "tools" / "registry.py"
    reg.parent.mkdir(parents=True, exist_ok=True)
    lines = "\n".join(f'    {{"name": "sap_tool_{i}", "desc": "x"}},' for i in range(count))
    reg.write_text(f"TOOLS = [\n{lines}\n]\n", encoding="utf-8")


def test_check_tool_count_drift_no_registry_warns(tmp_path, monkeypatch):
    """Khong co registry.py -> WARN, khong FAIL."""
    fake = _make_fake_repo(tmp_path)
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_tool_count_drift()
    assert not any("[tool-drift]" in f for f in vp.FAILURES), vp.FAILURES
    assert any("[tool-drift]" in w for w in vp.WARNINGS), vp.WARNINGS


def test_check_tool_count_drift_match_ok(tmp_path, monkeypatch):
    """Doc claim 5 MCP tools, registry co 5 -> OK."""
    fake = _make_fake_repo(tmp_path)
    _make_registry(fake, 5)
    (fake / "README.md").write_text("Plugin with 5 MCP tools\n", encoding="utf-8")
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_tool_count_drift()
    assert not any("[tool-drift]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_tool_count_drift_mismatch_fails(tmp_path, monkeypatch):
    """Doc claim 5 MCP tools nhung registry co 7 -> FAIL."""
    fake = _make_fake_repo(tmp_path)
    _make_registry(fake, 7)
    (fake / "README.md").write_text("Plugin with 5 MCP tools available.\n", encoding="utf-8")
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_tool_count_drift()
    assert any("[tool-drift]" in f and "5" in f and "7" in f for f in vp.FAILURES), vp.FAILURES


# ---------- check_routing_matrix_coverage ----------

def _make_routing_file(fake: Path, agents: list[str]) -> Path:
    """Tao skills/sap-ask-consultant/SKILL.md voi routing matrix gia."""
    routing_dir = fake / "skills" / "sap-ask-consultant"
    routing_dir.mkdir(parents=True, exist_ok=True)
    content = "---\nname: routing\n---\n\n## Routing matrix\n\n"
    for a in agents:
        content += f"| module | `{a}` | k1 | k2 | k3 | 2 |\n"
    (routing_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return routing_dir / "SKILL.md"


def test_check_routing_matrix_coverage_no_file_warns(tmp_path, monkeypatch):
    """Khong co routing file -> WARN, khong FAIL."""
    fake = _make_fake_repo(tmp_path)
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_routing_matrix_coverage()
    assert not any("[routing]" in f for f in vp.FAILURES), vp.FAILURES
    assert any("[routing]" in w for w in vp.WARNINGS), vp.WARNINGS


def test_check_routing_matrix_coverage_missing_agent(tmp_path, monkeypatch):
    """Routing tham chieu agent khong ton tai -> FAIL."""
    fake = _make_fake_repo(tmp_path)
    _make_routing_file(fake, ["sap-fi-consultant-cloud", "sap-ghost-consultant-cloud"])
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_routing_matrix_coverage()
    # fi ton tai? khong - trong fake root. ca 2 deu bi flag
    assert any("sap-ghost-consultant-cloud" in f and "[routing]" in f for f in vp.FAILURES), vp.FAILURES


def test_check_routing_matrix_coverage_orphan_agent_warns(tmp_path, monkeypatch):
    """Agent ton tai nhung khong co trong routing matrix -> WARN (khong FAIL)."""
    fake = _make_fake_repo(tmp_path)
    _make_routing_file(fake, ["sap-fi-consultant-cloud"])
    # Tao agent file FI nhung routing chi tham chieu FI qua description (khong phai table)
    (fake / "agents" / "sap-fi-consultant-cloud.md").write_text(
        "---\nname: sap-fi-consultant-cloud\n---\n", encoding="utf-8"
    )
    # Tao 1 agent orphan (khong co trong routing)
    (fake / "agents" / "sap-mm-consultant-cloud.md").write_text(
        "---\nname: sap-mm-consultant-cloud\n---\n", encoding="utf-8"
    )
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_routing_matrix_coverage()
    # fi co trong routing, mm khong co -> mm la orphan WARN
    assert any("sap-mm-consultant-cloud" in w and "never mentioned" in w for w in vp.WARNINGS), vp.WARNINGS


def test_check_routing_matrix_coverage_all_match(tmp_path, monkeypatch):
    """Tat ca agent deu co trong routing matrix, khong co reference ao -> OK."""
    fake = _make_fake_repo(tmp_path)
    _make_routing_file(fake, ["sap-fi-consultant-cloud", "sap-mm-consultant-cloud"])
    (fake / "agents" / "sap-fi-consultant-cloud.md").write_text(
        "---\nname: sap-fi-consultant-cloud\n---\n", encoding="utf-8"
    )
    (fake / "agents" / "sap-mm-consultant-cloud.md").write_text(
        "---\nname: sap-mm-consultant-cloud\n---\n", encoding="utf-8"
    )
    monkeypatch.setattr(vp, "ROOT", fake)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_routing_matrix_coverage()
    assert not any("[routing]" in f for f in vp.FAILURES), vp.FAILURES
    assert not any("[routing]" in w for w in vp.WARNINGS), vp.WARNINGS


# ---------- _real_skill_count / _real_module_count ----------

def test_real_skill_count_excludes_user_skills_placeholder(tmp_path, monkeypatch):
    """sap-user-skills/ la placeholder, bi tru di khi dem."""
    fake = _make_fake_repo(tmp_path)
    (fake / "skills" / "sap-a").mkdir()
    (fake / "skills" / "sap-b").mkdir()
    (fake / "skills" / "sap-user-skills").mkdir()  # placeholder
    monkeypatch.setattr(vp, "ROOT", fake)
    assert vp._real_skill_count() == 2  # 3 dir - 1 placeholder


def test_real_skill_count_no_placeholder(tmp_path, monkeypatch):
    """Khong co sap-user-skills -> dem tat ca."""
    fake = _make_fake_repo(tmp_path)
    (fake / "skills" / "sap-a").mkdir()
    (fake / "skills" / "sap-b").mkdir()
    monkeypatch.setattr(vp, "ROOT", fake)
    assert vp._real_skill_count() == 2


def test_real_module_count_counts_all_dirs(tmp_path, monkeypatch):
    """Dem moi dir trong reference/modules/."""
    fake = _make_fake_repo(tmp_path)
    (fake / "reference" / "modules" / "sap-a-cloud").mkdir(parents=True)
    (fake / "reference" / "modules" / "sap-b-cloud").mkdir(parents=True)
    (fake / "reference" / "modules" / "cap-cloud").mkdir(parents=True)
    monkeypatch.setattr(vp, "ROOT", fake)
    assert vp._real_module_count() == 3
