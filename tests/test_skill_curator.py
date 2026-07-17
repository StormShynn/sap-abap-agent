"""Test cho reference/scripts/skill_curator.py (record-use + run lifecycle).

Tap trung vao:
  - record_use: bumb use_count + last_used
  - _days_since (pure function)
  - _backfill_untracked (them skill chua co trong index)
  - run_curator: gate interval, demote status, archive (move file - khong xoa that)
  - _state_path / _index_path (helper)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import skill_curator as sc  # noqa: E402


# ---------- Helper ----------

def _make_skill(memory_root: Path, name: str, days_old: int = 5) -> Path:
    """Tao 1 skill file va back-date mtime de test stale."""
    skills_dir = memory_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    p = skills_dir / name
    p.write_text(f"# skill {name}", encoding="utf-8")
    if days_old > 0:
        import time
        age = time.time() - days_old * 86400
        # uv metadata hack on Windows: set via os.utime
        import os
        os.utime(p, (age, age))
    return p


def _idx(memory_root: Path, entry: dict) -> None:
    """Ghi 1 entry vao index."""
    p = sc._index_path(memory_root)
    p.write_text(json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------- _days_since ----------

def test_days_since_same_day_returns_zero():
    today = date(2026, 7, 17)
    assert sc._days_since("2026-07-17", today) == 0


def test_days_since_positive():
    today = date(2026, 7, 17)
    assert sc._days_since("2026-07-01", today) == 16


# ---------- record_use ----------

def test_record_use_updates_existing(tmp_path):
    """Skill da co trong index -> bump use_count + last_used."""
    today = date.today().isoformat()
    _idx(tmp_path, {
        "skill": "mm-stock.md",
        "created": "2026-01-01",
        "last_used": "2026-01-01",
        "use_count": 3,
        "status": "active",
    })
    result = sc.record_use(tmp_path, "mm-stock.md")
    assert result["action"] == "updated"
    assert result["use_count"] == 4
    # Verify file updated
    entries = sc.load_index(tmp_path)
    assert entries[0]["last_used"] == today


def test_record_use_creates_new(tmp_path):
    """Skill chua co trong index -> tao moi."""
    _make_skill(tmp_path, "new-skill.md")
    result = sc.record_use(tmp_path, "new-skill.md")
    assert result["action"] == "created"
    assert result["use_count"] == 1
    entries = sc.load_index(tmp_path)
    assert entries[0]["skill"] == "new-skill.md"
    assert entries[0]["status"] == "active"


def test_record_use_revives_archived(tmp_path):
    """Skill archived/stale duoc khoi phuc ve active khi dung lai."""
    _idx(tmp_path, {
        "skill": "old-skill.md",
        "created": "2025-01-01",
        "last_used": "2025-01-01",
        "use_count": 1,
        "status": "archived",
    })
    sc.record_use(tmp_path, "old-skill.md")
    entries = sc.load_index(tmp_path)
    assert entries[0]["status"] == "active"


# ---------- _backfill_untracked ----------

def test_backfill_untracked_adds_missing(tmp_path):
    """Skill file co san nhung chua co entry trong index -> them vao."""
    today = date.today().isoformat()
    _make_skill(tmp_path, "orphan.md", days_old=0)
    entries = []
    out = sc._backfill_untracked(tmp_path, entries)
    assert any(e["skill"] == "orphan.md" for e in out)
    # use_count = 0 (honest), status = active
    e = next(e for e in out if e["skill"] == "orphan.md")
    assert e["use_count"] == 0
    assert e["status"] == "active"
    assert e["last_used"] in (today, date.today().isoformat())


def test_backfill_skips_already_tracked(tmp_path):
    """Skill da co trong index -> khong them."""
    _make_skill(tmp_path, "tracked.md")
    entries = [{"skill": "tracked.md", "use_count": 5, "status": "active", "created": "2026-01-01", "last_used": "2026-01-01"}]
    out = sc._backfill_untracked(tmp_path, entries)
    assert len(out) == 1
    assert out[0]["use_count"] == 5  # giu nguyen


# ---------- run_curator: gate interval ----------

def test_run_curator_skipped_due_to_interval(tmp_path):
    """Vua chay 1 ngay truoc -> skip (interval_days=7)."""
    today = date.today()
    sc._state_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    sc._state_path(tmp_path).write_text(
        json.dumps({"last_run": today.isoformat()}),
        encoding="utf-8",
    )
    result = sc.run_curator(tmp_path, force=False)
    assert result["status"] == "skipped_interval"
    assert result["days_since_last_run"] == 0


def test_run_curator_force_skips_interval(tmp_path):
    """force=True -> chay luon, khong can interval check."""
    today = date.today()
    sc._state_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    sc._state_path(tmp_path).write_text(
        json.dumps({"last_run": today.isoformat()}),
        encoding="utf-8",
    )
    result = sc.run_curator(tmp_path, force=True)
    assert result["status"] != "skipped_interval"


# ---------- run_curator: archive lifecycle ----------

def test_run_curator_archives_old_skill(tmp_path):
    """Skill khong dung 100 ngay (vuot archive_after_days=90) -> archive (move file)."""
    import time
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True)
    skill_path = skills_dir / "old-md.md"
    skill_path.write_text("# old", encoding="utf-8")
    # Backdate mtime 100 ngay
    age = time.time() - 100 * 86400
    import os
    os.utime(skill_path, (age, age))

    # Index da co entry da 100 ngay chua dung
    today = date.today()
    old = today.toordinal() - 100
    old_date = date.fromordinal(old).isoformat()
    _idx(tmp_path, {
        "skill": "old-md.md",
        "created": old_date,
        "last_used": old_date,
        "use_count": 1,
        "status": "active",
    })

    result = sc.run_curator(tmp_path, force=True, archive_after_days=90)
    assert result["status"] == "ran"
    assert result["archived_this_run"] >= 1

    # File da bi move vao .archive/, KHONG xoa that
    archive = skills_dir / ".archive" / "old-md.md"
    assert archive.exists(), "Skill phai duoc archive (move), KHONG xoa"
    assert not skill_path.exists(), "File goc da duoc chuyen di"


def test_run_curator_mark_stale(tmp_path):
    """Skill khong dung 35 ngay (vuot stale_after_days=30, < archive=90) -> stale."""
    import time
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True)
    skill_path = skills_dir / "mid-md.md"
    skill_path.write_text("# mid", encoding="utf-8")
    age = time.time() - 35 * 86400
    import os
    os.utime(skill_path, (age, age))

    today = date.today()
    old = today.toordinal() - 35
    _idx(tmp_path, {
        "skill": "mid-md.md",
        "created": date.fromordinal(old).isoformat(),
        "last_used": date.fromordinal(old).isoformat(),
        "use_count": 0,
        "status": "active",
    })

    result = sc.run_curator(tmp_path, force=True, stale_after_days=30)
    assert result["status"] == "ran"
    entries = sc.load_index(tmp_path)
    e = next(x for x in entries if x["skill"] == "mid-md.md")
    assert e["status"] == "stale"
    # File GOC van ton tai (stale, chua archive)
    assert skill_path.exists()


def test_run_curator_dry_run_does_not_archive(tmp_path):
    """--dry-run khong thay doi file."""
    import time
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True)
    skill_path = skills_dir / "old-dry.md"
    skill_path.write_text("# old", encoding="utf-8")
    age = time.time() - 100 * 86400
    import os
    os.utime(skill_path, (age, age))

    today = date.today()
    old_date = date.fromordinal(today.toordinal() - 100).isoformat()
    _idx(tmp_path, {
        "skill": "old-dry.md",
        "created": old_date,
        "last_used": old_date,
        "use_count": 0,
        "status": "active",
    })

    sc.run_curator(tmp_path, force=True, dry_run=True, archive_after_days=90)
    # File goc phai van ton tai
    assert skill_path.exists()
    # KHONG co archive dir
    archive_dir = skills_dir / ".archive"
    if archive_dir.exists():
        assert not (archive_dir / "old-dry.md").exists()


# ---------- _state_path / _index_path ----------

def test_helpers_paths():
    root = Path("/tmp/test-root")
    assert sc._state_path(root) == Path("/tmp/test-root/curator_state.json")
    assert sc._index_path(root) == Path("/tmp/test-root/skills_index.jsonl")
    assert sc._skills_dir(root) == Path("/tmp/test-root/skills")


# ---------- load_index handles BOM ----------

def test_load_index_handles_bom(tmp_path):
    """File index co BOM (do 1 tool ngoai ghi) van load duoc."""
    import codecs
    idx = tmp_path / sc.INDEX_FILENAME
    content = json.dumps({"skill": "x.md", "use_count": 1}) + "\n"
    with open(idx, "wb") as f:
        f.write(codecs.BOM_UTF8 + content.encode("utf-8"))
    entries = sc.load_index(tmp_path)
    assert len(entries) == 1
    assert entries[0]["skill"] == "x.md"
