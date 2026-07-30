"""Test cho reference/scripts/validate_plugin.py.

Cac ham duoc test (chon loc, tranh phu thuoc vao network/git):
  - parse_frontmatter(text)          # YAML frontmatter don gian
  - parse_inline_list(val)            # convert string list
  - check_agent_frontmatter()         # thuc thi voi fixture nho
  - check_python_syntax()             # py_compile smoke test
  - check_version_consistency()       # plugin.json vs CHANGELOG.md

Cac ham KHONG test o day (vi phu thuoc vao repo state thuc te):
  - check_core_deep_size, check_duplicate_lines, check_tool_count_drift,
    check_routing_matrix_coverage, check_index_html_counts (can filesystem that,
    co the gay nhieu false-positive khi test tren fixtures).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import validate_plugin as vp  # noqa: E402


# ---------- parse_frontmatter ----------

def test_parse_frontmatter_simple_fields():
    text = "---\nname: foo\ndescription: bar\nmodel: haiku\n---\nbody"
    fm = vp.parse_frontmatter(text)
    assert fm == {"name": "foo", "description": "bar", "model": "haiku"}


def test_parse_frontmatter_multiline_list():
    text = (
        "---\n"
        "name: foo\n"
        "skills:\n"
        "  - sap-sd-cloud\n"
        "  - sap-clean-code\n"
        "---\n"
    )
    fm = vp.parse_frontmatter(text)
    assert fm is not None
    # parser join items thanh "[item1, item2]" de parse_inline_list xu ly
    assert fm["skills"] == "[sap-sd-cloud, sap-clean-code]"


def test_parse_frontmatter_returns_none_for_missing():
    assert vp.parse_frontmatter("no frontmatter here") is None
    assert vp.parse_frontmatter("--\nname: foo\n") is None


def test_parse_frontmatter_handles_crlf():
    text = "---\r\nname: foo\r\ndescription: bar\r\n---\r\nbody"
    fm = vp.parse_frontmatter(text)
    assert fm is not None
    assert fm["name"] == "foo"


# ---------- parse_inline_list ----------

def test_parse_inline_list_bracketed():
    assert vp.parse_inline_list("[a, b, c]") == ["a", "b", "c"]


def test_parse_inline_list_unbracketed():
    assert vp.parse_inline_list("a, b ,c") == ["a", "b", "c"]


def test_parse_inline_list_strips_quotes():
    assert vp.parse_inline_list("[\"a\", 'b', c]") == ["a", "b", "c"]


def test_parse_inline_list_empty():
    assert vp.parse_inline_list("[]") == []
    assert vp.parse_inline_list("") == []


# ---------- check_agent_frontmatter (voi fixture) ----------

def test_check_agent_frontmatter_clean(tmp_path, monkeypatch):
    # Fake ROOT = tmp_path de khong doc repo that.
    fake_root = tmp_path / "fake"
    (fake_root / "agents").mkdir(parents=True)
    (fake_root / "skills").mkdir()
    (fake_root / "reference" / "modules").mkdir(parents=True)

    agent = fake_root / "agents" / "sap-test-cloud.md"
    agent.write_text(
        "---\n"
        "name: sap-test-cloud\n"
        "description: test agent\n"
        "model: haiku\n"
        "skills:\n"
        "  - sap-foo\n"
        "---\n"
        "body text\n",
        encoding="utf-8",
    )
    (fake_root / "skills" / "sap-foo" / "SKILL.md").parent.mkdir(parents=True)
    (fake_root / "skills" / "sap-foo" / "SKILL.md").write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_agent_frontmatter()
    # Clean fixture => khong co FAIL nao (co the co WARN tu skill-drift nhung khong mong doi)
    failures = [f for f in vp.FAILURES if "[frontmatter]" in f or "[skill-ref]" in f]
    assert failures == [], f"Unexpected failures: {failures}"


def test_check_agent_frontmatter_missing_required_field(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    (fake_root / "agents").mkdir(parents=True)
    (fake_root / "skills").mkdir()
    (fake_root / "reference" / "modules").mkdir(parents=True)

    # Thieu 'model:' - phai FAIL
    (fake_root / "agents" / "sap-bad.md").write_text(
        "---\nname: sap-bad\ndescription: x\n---\n", encoding="utf-8"
    )
    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_agent_frontmatter()
    assert any("[frontmatter]" in f and "missing 'model:'" in f for f in vp.FAILURES)


def test_check_agent_frontmatter_name_mismatch(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    (fake_root / "agents").mkdir(parents=True)
    (fake_root / "skills").mkdir()
    (fake_root / "reference" / "modules").mkdir(parents=True)

    # name khong khop filename
    (fake_root / "agents" / "sap-x.md").write_text(
        "---\nname: sap-y\ndescription: x\nmodel: haiku\n---\n", encoding="utf-8"
    )
    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_agent_frontmatter()
    assert any("name: 'sap-y' does not match filename" in f for f in vp.FAILURES)


def test_check_agent_frontmatter_declares_missing_skill(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    (fake_root / "agents").mkdir(parents=True)
    (fake_root / "skills").mkdir()
    (fake_root / "reference" / "modules").mkdir(parents=True)

    (fake_root / "agents" / "sap-test.md").write_text(
        "---\n"
        "name: sap-test\n"
        "description: x\n"
        "model: haiku\n"
        "skills:\n"
        "  - sap-not-exist\n"
        "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_agent_frontmatter()
    assert any("declares skills: [sap-not-exist]" in f for f in vp.FAILURES)


# ---------- check_python_syntax ----------

def test_check_python_syntax_clean_files(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    scripts_dir = fake_root / "reference" / "scripts"
    scripts_dir.mkdir(parents=True)
    (fake_root / "reference" / "mcp-server").mkdir(parents=True)

    (scripts_dir / "good.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (scripts_dir / "also_good.py").write_text("x = 1 + 2\n", encoding="utf-8")

    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_python_syntax()
    assert vp.FAILURES == [], f"Unexpected: {vp.FAILURES}"


def test_check_python_syntax_catches_syntax_error(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    scripts_dir = fake_root / "reference" / "scripts"
    scripts_dir.mkdir(parents=True)
    (fake_root / "reference" / "mcp-server").mkdir(parents=True)

    # File co syntax error ro rang
    (scripts_dir / "bad.py").write_text("def f(:\n    pass\n", encoding="utf-8")

    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_python_syntax()
    assert any("[py-syntax]" in f and "bad.py" in f for f in vp.FAILURES)


# ---------- check_version_consistency ----------

def test_check_version_consistency_match(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    (fake_root / ".claude-plugin").mkdir(parents=True)
    (fake_root / ".claude-plugin" / "plugin.json").write_text(
        '{"version": "1.2.3"}', encoding="utf-8"
    )
    (fake_root / "CHANGELOG.md").write_text(
        "## [v1.2.3] -- 2026-07-17\n\n### Added\n- foo\n", encoding="utf-8"
    )
    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_version_consistency()
    assert not any("version-drift" in w for w in vp.WARNINGS), vp.WARNINGS


def test_check_version_consistency_mismatch_warns(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    (fake_root / ".claude-plugin").mkdir(parents=True)
    (fake_root / ".claude-plugin" / "plugin.json").write_text(
        '{"version": "1.0.0"}', encoding="utf-8"
    )
    (fake_root / "CHANGELOG.md").write_text(
        "## [v2.0.0] -- 2026-07-17\n", encoding="utf-8"
    )
    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_version_consistency()
    assert any("version-drift" in w and "1.0.0" in w and "2.0.0" in w for w in vp.WARNINGS)


def test_check_version_consistency_missing_changelog_warns(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake"
    (fake_root / ".claude-plugin").mkdir(parents=True)
    (fake_root / ".claude-plugin" / "plugin.json").write_text(
        '{"version": "1.0.0"}', encoding="utf-8"
    )
    # khong tao CHANGELOG.md
    monkeypatch.setattr(vp, "ROOT", fake_root)
    vp.FAILURES.clear()
    vp.WARNINGS.clear()
    vp.check_version_consistency()
    # Khong FAIL, chi WARN neu thieu file
    assert not any("[version-drift]" in f for f in vp.FAILURES)
