#!/usr/bin/env python3
"""Skill lifecycle curator cho `memory/procedural/skills/` (dung boi `sap-daily-learner`) -
lay cam hung tu co che "Curator" cua Hermes Agent (github.com/NousResearch/hermes-agent,
xem website/docs/user-guide/features/curator.md): skill it dung dan chuyen
active -> stale -> archived, KHONG BAO GIO xoa that (archive luon khoi phuc duoc bang cach
di chuyen file tro lai tu .archive/).

Khac voi Hermes ban goc (co gateway daemon that, gate 1 lan curator chay theo CA
interval_hours (mac dinh 7 ngay) VA min_idle_hours (mac dinh 2 gio)): plugin nay khong co
tien trinh nen that - lenh "run" chi duoc goi opportunistic tu trong 1 luot chat (xem
skill sap-daily-learner muc 3d), nen chi gate theo interval_days, BO dieu kien idle (khong
the do "agent idle bao lau" khi khong co daemon chay lien tuc de theo doi).

Nguong mac dinh lay dung theo docs Hermes da doc: interval 7 ngay, stale sau 30 ngay khong
dung, archive sau 90 ngay khong dung.

Storage (duoi <memory-root> = <agent-home>/memory/procedural, resolve qua agent_home.py
giong het quy uoc cua lesson_card_add.py/lesson_card_retrieve.py - script nay KHONG tu
resolve agent-home, nguoi goi phai truyen memory-root da resolve):
  <memory-root>/skills_index.jsonl   - 1 dong/skill, rewrite toan bo file khi save (giong
    quy uoc lesson_card_retrieve.py), schema:
    {"skill": "<filename>.md", "created": "YYYY-MM-DD", "last_used": "YYYY-MM-DD",
     "use_count": N, "status": "active|stale|archived"}
  <memory-root>/curator_state.json   - {"last_run": "YYYY-MM-DD"} de gate interval giua
    2 lan chay "run".
  <memory-root>/skills/.archive/     - noi skill bi archive duoc di chuyen toi (khong xoa).

Usage:
  python skill_curator.py record-use <memory-root> <skill-filename.md>
  python skill_curator.py run <memory-root> [--dry-run] [--force]
                          [--interval-days 7] [--stale-after-days 30] [--archive-after-days 90]

Output: JSON ra stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

DEFAULT_INTERVAL_DAYS = 7
DEFAULT_STALE_AFTER_DAYS = 30
DEFAULT_ARCHIVE_AFTER_DAYS = 90

INDEX_FILENAME = "skills_index.jsonl"
STATE_FILENAME = "curator_state.json"


def _skills_dir(memory_root: Path) -> Path:
    return memory_root / "skills"


def _index_path(memory_root: Path) -> Path:
    return memory_root / INDEX_FILENAME


def _state_path(memory_root: Path) -> Path:
    return memory_root / STATE_FILENAME


def load_index(memory_root: Path) -> list:
    path = _index_path(memory_root)
    if not path.exists():
        return []
    entries = []
    # "utf-8-sig" tu boc BOM neu co (VD file tung bi ghi de boi 1 cong cu khac dung
    # PowerShell Set-Content -Encoding utf8, mac dinh kem BOM) - xem ghi chu tuong tu
    # trong cron_manage.py::_load_jobs.
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def save_index(memory_root: Path, entries: list) -> None:
    path = _index_path(memory_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def record_use(memory_root: Path, skill_filename: str) -> dict:
    """Bump use_count + last_used cho 1 skill vua duoc dung de tra loi (goi tu
    sap-ask-consultant Buoc 5 khi tim thay + dung 1 skill local co san, hoac tu
    sap-daily-learner khi tai su dung skill da co). Dung lai luon coi la con gia tri -
    neu dang "stale" hoac "archived" (vd nguoi dung tu tay khoi phuc tu .archive/) thi
    chuyen ve "active"."""
    entries = load_index(memory_root)
    today = date.today().isoformat()
    for entry in entries:
        if entry.get("skill") == skill_filename:
            entry["use_count"] = entry.get("use_count", 0) + 1
            entry["last_used"] = today
            if entry.get("status") in ("stale", "archived"):
                entry["status"] = "active"
            save_index(memory_root, entries)
            return {"action": "updated", "skill": skill_filename, "use_count": entry["use_count"]}

    entries.append({
        "skill": skill_filename,
        "created": today,
        "last_used": today,
        "use_count": 1,
        "status": "active",
    })
    save_index(memory_root, entries)
    return {"action": "created", "skill": skill_filename, "use_count": 1}


def _days_since(iso_date: str, today: date) -> int:
    return (today - date.fromisoformat(iso_date)).days


def _backfill_untracked(memory_root: Path, entries: list) -> list:
    """Skill co san truoc khi curator ton tai (hoac tao thu cong) se chua co trong index -
    them vao bang mtime cua file lam created/last_used, use_count=0 (khong the doan da
    dung bao nhieu lan truoc do - trung thuc con hon bia so)."""
    skills_dir = _skills_dir(memory_root)
    if not skills_dir.exists():
        return entries
    known = {e["skill"] for e in entries}
    for f in sorted(skills_dir.glob("*.md")):
        if f.name in known:
            continue
        mtime_date = date.fromtimestamp(f.stat().st_mtime).isoformat()
        entries.append({
            "skill": f.name,
            "created": mtime_date,
            "last_used": mtime_date,
            "use_count": 0,
            "status": "active",
        })
    return entries


def run_curator(
    memory_root: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    interval_days: int = DEFAULT_INTERVAL_DAYS,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    archive_after_days: int = DEFAULT_ARCHIVE_AFTER_DAYS,
) -> dict:
    today = date.today()
    state_path = _state_path(memory_root)
    last_run = None
    if state_path.exists():
        try:
            last_run = json.loads(state_path.read_text(encoding="utf-8-sig")).get("last_run")
        except (OSError, json.JSONDecodeError):
            last_run = None

    if not force and last_run:
        elapsed = _days_since(last_run, today)
        if elapsed < interval_days:
            return {
                "status": "skipped_interval",
                "last_run": last_run,
                "days_since_last_run": elapsed,
                "interval_days": interval_days,
            }

    entries = load_index(memory_root)
    entries = _backfill_untracked(memory_root, entries)

    skills_dir = _skills_dir(memory_root)
    archive_dir = skills_dir / ".archive"
    counts = {"active": 0, "stale": 0, "archived": 0, "archived_this_run": 0}

    for entry in entries:
        current_path = skills_dir / entry["skill"]

        if entry.get("status") == "archived":
            if current_path.exists():
                # Nguoi dung da tu tay khoi phuc file tu .archive/ - coi nhu con gia tri,
                # tinh lai tuoi ben duoi thay vi giu nguyen "archived".
                pass
            else:
                counts["archived"] += 1
                continue

        age = _days_since(entry["last_used"], today)

        if age >= archive_after_days:
            entry["status"] = "archived"
            counts["archived"] += 1
            counts["archived_this_run"] += 1
            if not dry_run and current_path.exists():
                archive_dir.mkdir(parents=True, exist_ok=True)
                current_path.replace(archive_dir / entry["skill"])
        elif age >= stale_after_days:
            entry["status"] = "stale"
            counts["stale"] += 1
        else:
            entry["status"] = "active"
            counts["active"] += 1

    if not dry_run:
        save_index(memory_root, entries)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"last_run": today.isoformat()}, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "ran" if not dry_run else "dry_run",
        "total_tracked": len(entries),
        **counts,
        "policy": {
            "interval_days": interval_days,
            "stale_after_days": stale_after_days,
            "archive_after_days": archive_after_days,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Skill lifecycle curator (active/stale/archived) cho memory/procedural/skills/."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_record = sub.add_parser("record-use", help="Ghi nhan 1 lan dung skill (bump use_count/last_used)")
    p_record.add_argument("memory_root")
    p_record.add_argument("skill_filename")

    p_run = sub.add_parser("run", help="Chay 1 luot curator: backfill + tinh stale/archive")
    p_run.add_argument("memory_root")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--force", action="store_true", help="Bo qua gate interval_days")
    p_run.add_argument("--interval-days", type=int, default=DEFAULT_INTERVAL_DAYS)
    p_run.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    p_run.add_argument("--archive-after-days", type=int, default=DEFAULT_ARCHIVE_AFTER_DAYS)

    args = parser.parse_args()
    memory_root = Path(args.memory_root).resolve()

    if args.command == "record-use":
        result = record_use(memory_root, args.skill_filename)
    else:
        result = run_curator(
            memory_root,
            force=args.force,
            dry_run=args.dry_run,
            interval_days=args.interval_days,
            stale_after_days=args.stale_after_days,
            archive_after_days=args.archive_after_days,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
