"""Test cho Phase 4 step 3 cua plan sap-multi-system-router.

Moi agents/sap-*-consultant-cloud.md phai co 1 dong "Backend capability" tro
ve skill `sap-multi-system-context`, de agent/nguoi doc biet kiem tra
routingHints truoc khi gia dinh backend nao dung duoc tren edition hien tai.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
AGENT_FILES = sorted(AGENTS_DIR.glob("sap-*-consultant-cloud.md"))


def test_found_all_consultant_cloud_agents():
    assert len(AGENT_FILES) == 25


def test_every_agent_mentions_backend_capability():
    missing = [
        p.name for p in AGENT_FILES
        if "Backend capability" not in p.read_text(encoding="utf-8")
    ]
    assert not missing, f"Agents thieu dong 'Backend capability': {missing}"


def test_every_backend_capability_line_points_to_multi_system_context_skill():
    missing = [
        p.name for p in AGENT_FILES
        if "sap-multi-system-context" not in p.read_text(encoding="utf-8")
    ]
    assert not missing, f"Agents co 'Backend capability' nhung khong tro ve sap-multi-system-context: {missing}"
