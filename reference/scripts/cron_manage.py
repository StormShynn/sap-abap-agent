#!/usr/bin/env python3
"""Cron that co that cho `sap-daily-learner` - lay dung kien truc da doc truc tiep tu
Hermes Agent (github.com/NousResearch/hermes-agent, xem
website/docs/user-guide/features/cron.md): 1 tool "action-style" (khong tach rieng
schedule/list/remove), 1 file lock chong tick trung, 1 tick spawn 1 session Claude Code
moi cho tung job den han, ket qua duoc "deliver" roi.

Khac voi Hermes ban goc:
  - Hermes co gateway daemon that (`hermes gateway install`), tu poll moi 60 giay. Plugin
    nay KHONG co daemon - ban than lenh "tick" phai duoc goi tu ben ngoai (Windows Task
    Scheduler, xem install-daily-learner-cron.bat) theo chu ky vai phut - "tick" chi kiem
    tra jobs.json, khong tu lap vong cho.
  - Hermes deliver ket qua toi Telegram/Slack/... Plugin nay khong co tich hop nhan tin -
    "deliver" o day nghia la ghi 1 file .md vao <agent-home>/cron/pending/, roi
    SessionStart hook (hooks/cron_deliver.py) bom noi dung do vao phien chat Claude Code
    KE TIEP khi user mo len - giong tinh than "delivery" nhung tan dung co che injection
    co san cua Claude Code plugin thay vi tu xay kenh thong bao rieng.
  - Hermes chap nhan lich dang tu nhien/cron-expression/relative-delay linh hoat. O day chi
    ho tro 2 dang don gian ("daily@HH:MM", "every:<so-phut>m") - du cho use case daily tip,
    tranh over-engineer 1 trinh parse cron-expression day du khong ai dung toi.

**OPT-IN, MAC DINH TAT** (giong het triet ly `hooks/error_reporter.py::_is_enabled()`):
  moi lan tick that su goi `claude -p` deu ton chi phi API - KHONG duoc tu bat ngam. Bat
  bang 1 trong 2 cach:
    1. Env var SAP_ABAP_AGENT_CRON_ENABLED=1 (hoac true/yes/on)
    2. Tao file marker: <agent-home>/cron/ENABLED
  Cai dat Task Scheduler (install-daily-learner-cron.bat) CHI dat lich tick, KHONG tu bat
  co gate nay - 2 buoc tach biet co y, de nguoi dung con 1 diem xac nhan rieng truoc khi
  chi phi that bat dau phat sinh.

Storage (duoi <agent-home>/cron/, resolve qua agent_home.py):
  jobs.json          - danh sach job {id, prompt, schedule, enabled, next_run_at, last_run_at}
  .tick.lock         - file lock (giong _FileLock cua hooks/error_reporter.py) chong 2 tick
                       chay song song cung luc (VD user bam tay dung luc Task Scheduler kich)
  pending/<id>_<ts>.md - ket qua tick cho session chat ke tiep "nhan" (xem cron_deliver_hook.py)
  delivered/         - noi pending/ duoc di chuyen toi SAU KHI da bom vao 1 session - khong xoa
  cost_log.jsonl     - append-only, 1 dong/lan tick that su goi claude -p (cost_usd, ok/loi)

Usage:
  python cron_manage.py add    <agent-home> <job-id> "<prompt>" <schedule> [--disabled]
  python cron_manage.py list   <agent-home>
  python cron_manage.py enable/disable <agent-home> <job-id>
  python cron_manage.py remove <agent-home> <job-id>
  python cron_manage.py tick   <agent-home> [--force] [--dry-run]
                               [--max-turns 20] [--timeout-s 300] [--bare]
  python cron_manage.py status <agent-home>

Output: JSON ra stdout.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
CLAUDE_BIN = os.environ.get("SAP_ABAP_AGENT_CLAUDE_BIN", "claude")
DEFAULT_MAX_TURNS = 20
DEFAULT_TIMEOUT_S = 300


# ── Opt-in gate (giong het triet ly hooks/error_reporter.py::_is_enabled()) ─────────────

def _is_enabled(agent_home: Path) -> bool:
    env = os.environ.get("SAP_ABAP_AGENT_CRON_ENABLED", "").strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    return (agent_home / "cron" / "ENABLED").exists()


# ── File lock - copy nguyen ban tu hooks/error_reporter.py::_FileLock ───────────────────
# (giu 2 noi khac nhau vi hooks/ va reference/scripts/ la 2 script doc lap, khong import
# cheo nhau - xem quy uoc cac file reference/scripts/*.py khac trong repo nay)

class _FileLock:
    """Lock don gian, portable, khong dependency ngoai - open(O_CREAT|O_EXCL) lam mutex.
    Tu bo qua lock cu (stale) qua stale_after_s de tranh deadlock vinh vien neu tick truoc
    crash giua luc dang giu lock. Fail-open: het wait_s ma khong lay duoc lock thi van tiep
    tuc KHONG co lock (uu tien khong bao gio treo tick hon la chong trung hoan hao)."""

    def __init__(self, path: Path, stale_after_s: float = 120.0, wait_s: float = 30.0):
        self.path = path
        self.stale_after_s = stale_after_s
        self.wait_s = wait_s
        self._acquired = False

    def __enter__(self) -> _FileLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + self.wait_s
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > self.stale_after_s:
                        self.path.unlink(missing_ok=True)
                        continue
                except OSError:
                    pass
                if time.time() >= deadline:
                    return self
                time.sleep(0.2)
            except OSError:
                return self

    def __exit__(self, *exc: Any) -> None:
        if self._acquired:
            with contextlib.suppress(OSError):
                self.path.unlink(missing_ok=True)


# ── Paths ────────────────────────────────────────────────────────────────────────────

def _cron_dir(agent_home: Path) -> Path:
    return agent_home / "cron"


def _jobs_path(agent_home: Path) -> Path:
    return _cron_dir(agent_home) / "jobs.json"


def _lock_path(agent_home: Path) -> Path:
    return _cron_dir(agent_home) / ".tick.lock"


def _pending_dir(agent_home: Path) -> Path:
    return _cron_dir(agent_home) / "pending"


def _cost_log_path(agent_home: Path) -> Path:
    return _cron_dir(agent_home) / "cost_log.jsonl"


def _load_jobs(agent_home: Path) -> list:
    """Doc jobs.json. QUAN TRONG: neu file TON TAI nhung khong parse duoc (VD JSON hong),
    KHONG duoc nuot loi roi tra ve [] - vi ham nay thuong duoc goi truoc 1 buoc _save_jobs()
    sau do, va "tra ve [] roi luu lai" se XOA SACH job that su cua nguoi dung. Chi coi la
    "chua co job" khi file thuc su chua ton tai. Dung "utf-8-sig" (khong phai "utf-8" thuong)
    de tu boc BOM neu co - tai hien thuc te: PowerShell `Set-Content -Encoding utf8` ghi BOM
    mac dinh, tung lam hong jobs.json va bi hieu nham la rong trong 1 lan test."""
    path = _jobs_path(agent_home)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _save_jobs(agent_home: Path, jobs: list) -> None:
    path = _jobs_path(agent_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_cost_log(agent_home: Path, record: dict) -> None:
    path = _cost_log_path(agent_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── Schedule parsing (chi 2 dang don gian - xem docstring dau file) ────────────────────

def compute_next_run(schedule: str, now: datetime) -> datetime:
    if schedule.startswith("daily@"):
        hh, mm = schedule[len("daily@"):].split(":")
        target = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target
    if schedule.startswith("every:") and schedule.endswith("m"):
        minutes = int(schedule[len("every:"):-1])
        return now + timedelta(minutes=minutes)
    raise ValueError(
        f"Khong hieu schedule: {schedule!r} - ho tro 'daily@HH:MM' hoac 'every:<so-phut>m'"
    )


# ── Job CRUD ─────────────────────────────────────────────────────────────────────────

def add_job(agent_home: Path, job_id: str, prompt: str, schedule: str, *, enabled: bool = True) -> dict:
    jobs = _load_jobs(agent_home)
    if any(j["id"] == job_id for j in jobs):
        return {"action": "error", "error": f"job id '{job_id}' da ton tai - dung 'remove' truoc neu muon thay"}
    now = datetime.now()
    compute_next_run(schedule, now)  # validate schedule truoc khi luu
    job = {
        "id": job_id,
        "prompt": prompt,
        "schedule": schedule,
        "enabled": enabled,
        "created_at": now.isoformat(),
        "last_run_at": None,
        "next_run_at": compute_next_run(schedule, now).isoformat(),
    }
    jobs.append(job)
    _save_jobs(agent_home, jobs)
    return {"action": "added", "job": job}


def set_enabled(agent_home: Path, job_id: str, enabled: bool) -> dict:
    jobs = _load_jobs(agent_home)
    for j in jobs:
        if j["id"] == job_id:
            j["enabled"] = enabled
            if enabled:
                j["next_run_at"] = compute_next_run(j["schedule"], datetime.now()).isoformat()
            _save_jobs(agent_home, jobs)
            return {"action": "enabled" if enabled else "disabled", "job": j}
    return {"action": "error", "error": f"khong tim thay job id '{job_id}'"}


def remove_job(agent_home: Path, job_id: str) -> dict:
    jobs = _load_jobs(agent_home)
    remaining = [j for j in jobs if j["id"] != job_id]
    if len(remaining) == len(jobs):
        return {"action": "error", "error": f"khong tim thay job id '{job_id}'"}
    _save_jobs(agent_home, remaining)
    return {"action": "removed", "job_id": job_id}


def list_jobs(agent_home: Path) -> dict:
    return {"jobs": _load_jobs(agent_home)}


# ── Tick (spawn 1 session claude -p cho tung job den han) ──────────────────────────────

def _run_job_subprocess(prompt: str, *, bare: bool, max_turns: int, timeout_s: int) -> dict:
    cmd = [CLAUDE_BIN, "-p", prompt, "--plugin-dir", str(PLUGIN_ROOT),
           "--output-format", "json", "--max-turns", str(max_turns)]
    if bare:
        cmd.insert(1, "--bare")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timeout sau {timeout_s}s"}
    except FileNotFoundError:
        return {"ok": False, "error": (
            f"khong goi duoc lenh '{CLAUDE_BIN}' - Claude Code CLI co nam trong PATH cua "
            "tai khoan chay Task Scheduler khong? Neu khong, dat env var "
            "SAP_ABAP_AGENT_CLAUDE_BIN=<duong-dan-tuyet-doi-toi-claude.exe>."
        )}
    if proc.returncode != 0:
        return {"ok": False, "error": f"exit code {proc.returncode}: {proc.stderr.strip()[:500]}"}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "output khong phai JSON hop le", "raw": proc.stdout[:500]}
    return {
        "ok": True,
        "result": payload.get("result", ""),
        "cost_usd": payload.get("total_cost_usd"),
    }


def _deliver(agent_home: Path, job_id: str, now: datetime, outcome: dict) -> Path:
    pending_dir = _pending_dir(agent_home)
    pending_dir.mkdir(parents=True, exist_ok=True)
    ts = now.strftime("%Y%m%dT%H%M%S")
    path = pending_dir / f"{job_id}_{ts}.md"
    if outcome["ok"]:
        body = f"## Cron job `{job_id}` — {now.isoformat()}\n\n{outcome['result']}\n"
    else:
        body = (
            f"## ⚠️ Cron job `{job_id}` LOI — {now.isoformat()}\n\n"
            f"{outcome['error']}\n\n"
            "_(job van duoc tinh la da chay - se thu lai theo lich ke tiep, khong retry "
            "ngay lap tuc de tranh spam loi lien tuc neu nguyen nhan la cau hinh sai)_\n"
        )
    path.write_text(body, encoding="utf-8")
    return path


def tick(
    agent_home: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    bare: bool = False,
    max_turns: int = DEFAULT_MAX_TURNS,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> dict:
    if not force and not _is_enabled(agent_home):
        return {
            "status": "disabled",
            "note": (
                "Cron dang TAT (opt-in mac dinh). Bat bang env var "
                "SAP_ABAP_AGENT_CRON_ENABLED=1 hoac tao file "
                f"{agent_home / 'cron' / 'ENABLED'}"
            ),
        }

    with _FileLock(_lock_path(agent_home)):
        now = datetime.now()
        jobs = _load_jobs(agent_home)
        due = [j for j in jobs if j.get("enabled") and j.get("next_run_at", "") <= now.isoformat()]

        ran = []
        for job in due:
            if dry_run:
                ran.append({"id": job["id"], "would_run": True})
                continue

            outcome = _run_job_subprocess(job["prompt"], bare=bare, max_turns=max_turns, timeout_s=timeout_s)
            delivered_path = _deliver(agent_home, job["id"], now, outcome)

            job["last_run_at"] = now.isoformat()
            job["next_run_at"] = compute_next_run(job["schedule"], now).isoformat()

            _append_cost_log(agent_home, {
                "job_id": job["id"],
                "timestamp": now.isoformat(),
                "ok": outcome["ok"],
                "cost_usd": outcome.get("cost_usd"),
                "error": outcome.get("error"),
            })
            ran.append({
                "id": job["id"],
                "ok": outcome["ok"],
                "delivered_to": str(delivered_path),
                "cost_usd": outcome.get("cost_usd"),
                "next_run_at": job["next_run_at"],
            })

        if not dry_run and due:
            _save_jobs(agent_home, jobs)

        return {
            "status": "dry_run" if dry_run else "ticked",
            "total_jobs": len(jobs),
            "due_this_tick": len(due),
            "ran": ran,
        }


def status(agent_home: Path) -> dict:
    jobs = _load_jobs(agent_home)
    cost_path = _cost_log_path(agent_home)
    total_cost = 0.0
    tick_count = 0
    if cost_path.exists():
        for line in cost_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            tick_count += 1
            total_cost += rec.get("cost_usd") or 0.0
    return {
        "enabled": _is_enabled(agent_home),
        "jobs": jobs,
        "total_ticks_run": tick_count,
        "total_cost_usd": round(total_cost, 4),
    }


# ── CLI ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Cron thuc su cho sap-daily-learner (kien truc lay tu Hermes Agent).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("agent_home")
    p_add.add_argument("job_id")
    p_add.add_argument("prompt")
    p_add.add_argument("schedule", help="'daily@HH:MM' hoac 'every:<so-phut>m'")
    p_add.add_argument("--disabled", action="store_true")

    for name in ("list", "status"):
        p = sub.add_parser(name)
        p.add_argument("agent_home")

    for name in ("enable", "disable", "remove"):
        p = sub.add_parser(name)
        p.add_argument("agent_home")
        p.add_argument("job_id")

    p_tick = sub.add_parser("tick")
    p_tick.add_argument("agent_home")
    p_tick.add_argument("--force", action="store_true", help="Bo qua opt-in gate (dung khi test thu cong)")
    p_tick.add_argument("--dry-run", action="store_true")
    p_tick.add_argument("--bare", action="store_true", help="claude --bare (can ANTHROPIC_API_KEY, xem docstring)")
    p_tick.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    p_tick.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S)

    args = parser.parse_args()
    agent_home = Path(args.agent_home).resolve()

    try:
        if args.command == "add":
            result = add_job(agent_home, args.job_id, args.prompt, args.schedule, enabled=not args.disabled)
        elif args.command == "list":
            result = list_jobs(agent_home)
        elif args.command == "enable":
            result = set_enabled(agent_home, args.job_id, True)
        elif args.command == "disable":
            result = set_enabled(agent_home, args.job_id, False)
        elif args.command == "remove":
            result = remove_job(agent_home, args.job_id)
        elif args.command == "status":
            result = status(agent_home)
        else:
            result = tick(
                agent_home,
                force=args.force,
                dry_run=args.dry_run,
                bare=args.bare,
                max_turns=args.max_turns,
                timeout_s=args.timeout_s,
            )
    except ValueError as exc:
        result = {"action": "error", "error": str(exc)}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
