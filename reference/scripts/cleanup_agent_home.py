#!/usr/bin/env python3
"""Don dep cache/log tich luy trong <agent-home> (va sync_skills.log cua plugin) - tranh phinh
thu muc local qua thoi gian.

Hai muc tieu doc lap:
  1. Cache cua skill `sap-context-tool-result-trim` (<agent-home>/cache/**, xem agent_home.py):
     xoa file cu hon N ngay (mac dinh 7 - dung dung policy da ghi trong SKILL.md), doc config
     tu `<agent-home>/cache/.retention` (JSON: {"days": N, "max_mb": N}) neu co. Sau khi xoa
     theo tuoi, neu tong dung luong con lai van vuot cap (mac dinh 500MB) thi xoa tiep tu file
     cu nhat cho den khi duoi cap.
  2. `sync_skills.log` (nam canh sync_skills.py trong repo plugin - KHONG phai <agent-home>, xem
     docstring sync_skills.py de biet ly do): giu lai cac dong log trong N ngay gan nhat, xoa
     dong cu hon.

KHONG dong vao: `memory/` (LEARNING_PROGRESS, knowledge_graph, lesson card - kien thuc lau dai,
khong phai log), `sessions/` (gan voi ticket dang lam - xem skill `sap-finish-ticket` de biet
khi nao don), `episodic/` (co policy rieng 30 ngay + archive-khong-xoa, xem `sap-daily-learner`),
`dev-mirror/` (ban sao config dang dung, xoa nham se mat dong bo voi %USERPROFILE%).

Usage:
  python reference/scripts/cleanup_agent_home.py                  # ap dung mac dinh/.retention
  python reference/scripts/cleanup_agent_home.py --dry-run         # xem se xoa gi, chua xoa that
  python reference/scripts/cleanup_agent_home.py --days 14         # doi so ngay giu lai
  python reference/scripts/cleanup_agent_home.py --max-cache-mb 200
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_home import get_agent_home  # noqa: E402

DEFAULT_DAYS = 7
DEFAULT_MAX_CACHE_MB = 500
_LOG_LINE_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\]")


def _load_retention_policy(cache_dir: Path) -> tuple[int, int]:
    """Doc <cache_dir>/.retention (JSON: {"days": N, "max_mb": N}) neu co, khong thi dung default.
    File hong/thieu key -> fallback tung phan, khong fail ca script (best-effort)."""
    days, max_mb = DEFAULT_DAYS, DEFAULT_MAX_CACHE_MB
    policy_file = cache_dir / ".retention"
    if policy_file.exists():
        try:
            data = json.loads(policy_file.read_text(encoding="utf-8"))
            days = int(data.get("days", days))
            max_mb = int(data.get("max_mb", max_mb))
        except Exception:
            pass
    return days, max_mb


def clean_cache(days: int | None = None, max_cache_mb: int | None = None, *, dry_run: bool = False) -> dict:
    """Xoa file trong <agent-home>/cache/ cu hon `days` ngay, roi ep tong dung luong duoi
    `max_cache_mb` (xoa tiep tu cu nhat neu can). Tra ve so file da xoa + dung luong giai phong."""
    cache_dir = get_agent_home() / "cache"
    if not cache_dir.exists():
        return {"dir": str(cache_dir), "deleted": 0, "freed_bytes": 0}

    policy_days, policy_max_mb = _load_retention_policy(cache_dir)
    days = policy_days if days is None else days
    max_cache_mb = policy_max_mb if max_cache_mb is None else max_cache_mb
    cutoff = time.time() - days * 86400

    deleted, freed = 0, 0
    kept: list[tuple[Path, float, int]] = []
    for f in cache_dir.rglob("*"):
        if not f.is_file() or f.name == ".retention":
            continue
        try:
            stat = f.stat()
        except OSError:
            continue
        if stat.st_mtime < cutoff:
            deleted += 1
            freed += stat.st_size
            if not dry_run:
                try:
                    f.unlink()
                except OSError:
                    deleted -= 1
                    freed -= stat.st_size
        else:
            kept.append((f, stat.st_mtime, stat.st_size))

    max_bytes = max_cache_mb * 1024 * 1024
    total_kept = sum(size for _, _, size in kept)
    if total_kept > max_bytes:
        kept.sort(key=lambda item: item[1])  # cu nhat truoc
        for f, _, size in kept:
            if total_kept <= max_bytes:
                break
            deleted += 1
            freed += size
            total_kept -= size
            if not dry_run:
                try:
                    f.unlink()
                except OSError:
                    deleted -= 1
                    freed -= size
                    total_kept += size

    return {
        "dir": str(cache_dir),
        "deleted": deleted,
        "freed_bytes": freed,
        "days": days,
        "max_cache_mb": max_cache_mb,
    }


def clean_sync_skills_log(days: int = DEFAULT_DAYS, *, dry_run: bool = False) -> dict:
    """sync_skills.log nam canh sync_skills.py (repo cua chinh plugin, KHONG phai <agent-home> -
    xem docstring sync_skills.py). Giu lai dong trong N ngay, ghi de file voi phan con lai."""
    repo_dir = Path(__file__).resolve().parent.parent.parent
    log_file = repo_dir / ".sap-abap-agent" / "sync_skills.log"
    if not log_file.exists():
        return {"file": str(log_file), "kept_lines": 0, "removed_lines": 0}

    cutoff_date = time.strftime("%Y-%m-%d", time.localtime(time.time() - days * 86400))
    lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()

    kept_lines, removed = [], 0
    for line in lines:
        m = _LOG_LINE_RE.match(line)
        if m and m.group(1) < cutoff_date:
            removed += 1
        else:
            kept_lines.append(line)

    if not dry_run and removed:
        content = "\n".join(kept_lines) + ("\n" if kept_lines else "")
        log_file.write_text(content, encoding="utf-8")

    return {"file": str(log_file), "kept_lines": len(kept_lines), "removed_lines": removed}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Don cache/log tich luy trong <agent-home> va sync_skills.log cua plugin."
    )
    parser.add_argument(
        "--days", type=int, default=None,
        help=f"So ngay giu lai (mac dinh {DEFAULT_DAYS}, hoac theo cache/.retention neu co)",
    )
    parser.add_argument(
        "--max-cache-mb", type=int, default=None,
        help=f"Dung luong cache toi da, MB (mac dinh {DEFAULT_MAX_CACHE_MB}, hoac theo .retention)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Chi xem se xoa gi, chua xoa that")
    args = parser.parse_args()

    cache_result = clean_cache(days=args.days, max_cache_mb=args.max_cache_mb, dry_run=args.dry_run)
    log_days = args.days if args.days is not None else DEFAULT_DAYS
    log_result = clean_sync_skills_log(days=log_days, dry_run=args.dry_run)

    prefix = "[DRY-RUN] " if args.dry_run else ""
    freed_mb = cache_result["freed_bytes"] / (1024 * 1024)
    print(
        f"{prefix}Cache ({cache_result['dir']}): xoa {cache_result['deleted']} file, "
        f"giai phong {freed_mb:.1f} MB "
        f"(policy: {cache_result.get('days', log_days)} ngay / "
        f"{cache_result.get('max_cache_mb', DEFAULT_MAX_CACHE_MB)} MB)"
    )
    print(
        f"{prefix}sync_skills.log ({log_result['file']}): "
        f"giu {log_result['kept_lines']} dong, xoa {log_result['removed_lines']} dong cu"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
