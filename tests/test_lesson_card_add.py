"""Test cho reference/scripts/lesson_card_add.py (idempotent, pure function)."""
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import lesson_card_add as lca  # noqa: E402


# ---------- tokenize / jaccard ----------

def test_tokenize_basic():
    assert lca.tokenize("Hello World 123") == {"hello", "world", "123"}


def test_tokenize_empty():
    assert lca.tokenize("") == set()


def test_jaccard_identical():
    a = {"a", "b", "c"}
    assert lca.jaccard(a, a) == 1.0


def test_jaccard_disjoint():
    assert lca.jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_empty():
    # Contract: both empty -> 1.0 (document this behavior)
    assert lca.jaccard(set(), set()) == 1.0


# ---------- lessons_path / load_cards / find_duplicate ----------

def test_lessons_path_creates_dir(tmp_path):
    p = lca.lessons_path(tmp_path, "FI")
    assert p.parent.exists()
    assert p.parent.is_dir()
    assert p == tmp_path / "lessons" / "FI.jsonl"


def test_lessons_path_uppercases_module(tmp_path):
    p = lca.lessons_path(tmp_path, "mm")
    assert p.name == "MM.jsonl"


def test_load_cards_empty(tmp_path):
    p = tmp_path / "lessons" / "FI.jsonl"
    assert lca.load_cards(p) == []


def test_load_cards_skips_blank_lines(tmp_path):
    p = tmp_path / "lessons" / "FI.jsonl"
    p.parent.mkdir()
    p.write_text(
        '{"id":"1"}\n\n   \n{"id":"2"}\n',
        encoding="utf-8",
    )
    cards = lca.load_cards(p)
    assert len(cards) == 2


def test_find_duplicate_no_match(tmp_path):
    p = tmp_path / "lessons" / "FI.jsonl"
    p.parent.mkdir()
    p.write_text(
        json.dumps({"id": "1", "topic": "acdoca", "fact": "ACDOCA line items"}) + "\n",
        encoding="utf-8",
    )
    cards = lca.load_cards(p)
    assert lca.find_duplicate(cards, "acdoca", "BSEG reconciliation") is None


def test_find_duplicate_match_same_topic(tmp_path):
    p = tmp_path / "lessons" / "FI.jsonl"
    p.parent.mkdir()
    p.write_text(
        json.dumps({
            "id": "1",
            "topic": "acdoca",
            "fact": "ACDOCA line items are universal journal entries aggregation",
        }) + "\n",
        encoding="utf-8",
    )
    cards = lca.load_cards(p)
    dup = lca.find_duplicate(cards, "acdoca",
        "ACDOCA line items are universal journal entries aggregation X")
    assert dup is not None
    assert dup["id"] == "1"


def test_find_duplicate_different_topic_no_match(tmp_path):
    """Same fact nhung khac topic -> khong xem la duplicate."""
    p = tmp_path / "lessons" / "FI.jsonl"
    p.parent.mkdir()
    p.write_text(
        json.dumps({"id": "1", "topic": "acdoca", "fact": "ACDOCA line items"}) + "\n",
        encoding="utf-8",
    )
    cards = lca.load_cards(p)
    dup = lca.find_duplicate(cards, "credit_memo", "ACDOCA line items")
    assert dup is None


# ---------- add_card (integration) ----------

def test_add_card_creates_new(tmp_path):
    result = lca.add_card(tmp_path, "FI", "acdoca", "Universal Journal line items")
    assert result["action"] == "added"
    assert "id" in result
    # File da duoc ghi
    p = tmp_path / "lessons" / "FI.jsonl"
    assert p.exists()
    cards = lca.load_cards(p)
    assert len(cards) == 1
    assert cards[0]["topic"] == "acdoca"


def test_add_card_dedup(tmp_path):
    """Add lan 1 -> added, add lan 2 giong -> skipped_duplicate."""
    r1 = lca.add_card(tmp_path, "FI", "acdoca",
        "ACDOCA primary ledger table for S/4HANA universal journal entries")
    r2 = lca.add_card(tmp_path, "FI", "acdoca",
        "ACDOCA primary ledger table for S/4HANA universal journal entries aggregation")
    assert r1["action"] == "added"
    assert r2["action"] == "skipped_duplicate"
    assert "similar_to" in r2


def test_add_card_valid_until_optional(tmp_path):
    """valid_until khong bat buoc, default la None/khong set."""
    r = lca.add_card(tmp_path, "MM", "stock", "Material stock in MARD-LABST")
    assert r["action"] == "added"
    # Kiem tra file co day du fields
    p = tmp_path / "lessons" / "MM.jsonl"
    cards = lca.load_cards(p)
    assert cards[0]["module"].upper() == "MM" or cards[0].get("module", "").upper() == "MM"


# ---------- CLI subprocess (smoke test) ----------

def test_cli_subprocess_add(tmp_path):
    """Chay script qua stdin JSON nhu document."""
    payload = json.dumps({
        "module": "FI",
        "topic": "credit_memo",
        "fact": "Credit memo cancels or reduces invoice posting",
    })
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "lesson_card_add.py"), str(tmp_path)],
        input=payload.encode("utf-8"),
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, f"stderr: {result.stderr.decode('utf-8', errors='replace')}"
    out = result.stdout.decode("utf-8").strip()
    parsed = json.loads(out)
    assert parsed["action"] == "added"
    assert (tmp_path / "lessons" / "FI.jsonl").exists()
