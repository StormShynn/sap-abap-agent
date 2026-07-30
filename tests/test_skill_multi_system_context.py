"""Test cho skill sap-multi-system-context (Phase 4).

Skill doc: skills/sap-multi-system-context/SKILL.md
- Frontmatter phai co name, description, model, tools, when_to_use, argument-hint, effort
- name phai khop ten thu muc (sap-multi-system-context)
- description phai chua "routingHints" hoac "multi-system" de validate_plugin pick up
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "sap-multi-system-context"
SKILL_FILE = SKILL_DIR / "SKILL.md"


def _parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if km:
            fm[km.group(1)] = km.group(2).strip()
    return fm


def test_skill_directory_exists():
    assert SKILL_DIR.is_dir()


def test_skill_file_exists():
    assert SKILL_FILE.is_file()


def test_skill_frontmatter_required_fields():
    text = SKILL_FILE.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    for required in ("name", "description", "model", "tools", "when_to_use", "argument-hint", "effort"):
        assert required in fm, f"Thieu field bat buoc: {required}"


def test_skill_name_matches_directory():
    text = SKILL_FILE.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    assert fm.get("name") == "sap-multi-system-context"


def test_skill_model_is_sonnet():
    text = SKILL_FILE.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    assert fm.get("model") == "sonnet"


def test_skill_tools_limited_to_read_bash():
    text = SKILL_FILE.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    tools = fm.get("tools", "")
    assert "Read" in tools
    assert "Bash" in tools
    # Khong co Write/Edit (chi read + execute Bash cho multi-system lookups)
    assert "Write" not in tools
    assert "Edit" not in tools


def test_skill_description_mentions_routing_hints():
    text = SKILL_FILE.read_text(encoding="utf-8")
    # Description la multi-line YAML block; chi can check chuoi day du trong file
    assert "routingHints" in text, "Description/body nen de cap den routingHints"


def test_skill_body_mentions_5_editions():
    text = SKILL_FILE.read_text(encoding="utf-8")
    for edition in ("s4hc_(public)", "s4hc_(private)", "btp", "onprem", "rise_with_sap"):
        assert edition in text, f"Body thieu edition: {edition}"


def test_skill_body_mentions_3_backends():
    text = SKILL_FILE.read_text(encoding="utf-8")
    for backend in ("sap-connect", "sap-vsp", "sap-dict-bridge"):
        assert backend in text, f"Body thieu backend: {backend}"


def test_skill_mentions_cache_7_days():
    text = SKILL_FILE.read_text(encoding="utf-8")
    assert "7 ngay" in text or "7 days" in text, "Body can de cap TTL 7 ngay (consistent voi bootstrap-system-context)"


def test_skill_mentions_all_7_routing_hint_keys():
    text = SKILL_FILE.read_text(encoding="utf-8")
    expected_keys = (
        "supportsReadonlyClass", "supportsDebug", "supportsVspSlim",
        "supportsVspHealth", "supportsDictBridge", "preferredTransport",
        "preferredAnalysis",
    )
    for key in expected_keys:
        assert key in text, f"Body thieu routingHints key: {key}"
