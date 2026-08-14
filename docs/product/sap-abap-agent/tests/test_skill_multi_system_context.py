"""Test cho reference/process/sap-multi-system-context.md (Phase 4, relocated 2026-07-31).

Doc: reference/process/sap-multi-system-context.md
Chuyen tu skills/sap-multi-system-context/SKILL.md sang day (xem
docs/audits/2026-Q3-skill-consolidation-part2.md) - khong con auto-discover qua tu khoa,
chi duoc doc khi skill/agent khac chu dong tro toi bang ten. Test nay xac nhan noi dung cot
loi (routingHints, 5 edition, 3 backend, cache 7 ngay) van con nguyen sau khi doi vi tri, va
khong con ton tai o vi tri skill cu (regression guard cho viec di chuyen).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC_FILE = ROOT / "reference" / "process" / "sap-multi-system-context.md"
OLD_SKILL_DIR = ROOT / "skills" / "sap-multi-system-context"
ROUTING_FILE = ROOT / "skills" / "sap-ask-consultant" / "SKILL.md"


def test_doc_file_exists():
    assert DOC_FILE.is_file()


def test_old_skill_location_removed():
    assert not OLD_SKILL_DIR.exists(), (
        "skills/sap-multi-system-context/ van con ton tai - phai xoa sau khi noi dung da "
        "chuyen sang reference/process/ (tranh trung ten/trung noi dung)"
    )


def test_doc_mentions_routing_hints():
    text = DOC_FILE.read_text(encoding="utf-8")
    assert "routingHints" in text, "Noi dung nen de cap den routingHints"


def test_doc_mentions_5_editions():
    text = DOC_FILE.read_text(encoding="utf-8")
    for edition in ("s4hc_(public)", "s4hc_(private)", "btp", "onprem", "rise_with_sap"):
        assert edition in text, f"Thieu edition: {edition}"


def test_doc_mentions_3_backends():
    text = DOC_FILE.read_text(encoding="utf-8")
    for backend in ("sap-connect", "sap-vsp", "sap-dict-bridge"):
        assert backend in text, f"Thieu backend: {backend}"


def test_doc_mentions_cache_7_days():
    text = DOC_FILE.read_text(encoding="utf-8")
    assert "7 ngay" in text or "7 days" in text, "Can de cap TTL 7 ngay (consistent voi bootstrap-system-context)"


def test_doc_mentions_all_7_routing_hint_keys():
    text = DOC_FILE.read_text(encoding="utf-8")
    expected_keys = (
        "supportsReadonlyClass", "supportsDebug", "supportsVspSlim",
        "supportsVspHealth", "supportsDictBridge", "preferredTransport",
        "preferredAnalysis",
    )
    for key in expected_keys:
        assert key in text, f"Thieu routingHints key: {key}"


def test_sap_ask_consultant_references_new_path():
    """sap-ask-consultant la noi duy nhat 'goi' tai lieu nay trong quy trinh dispatch (Buoc 5.5)
    - xac nhan no tro dung ve vi tri moi, khong con noi ten skill cu da bi xoa."""
    text = ROUTING_FILE.read_text(encoding="utf-8")
    assert "reference/process/sap-multi-system-context.md" in text
