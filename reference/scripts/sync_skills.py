#!/usr/bin/env python3
r"""
🔄 Skill Sync Daemon — SAP ABAP Agent
======================================
Tu dong dong bo skills/agents moi nhat tu GitHub ve local.
Chay ngam background, ho tro ca Windows, macOS, Linux.

Cach dung:
  python reference/scripts/sync_skills.py                  # chay 1 lan
  python reference/scripts/sync_skills.py --daemon          # chay background (macOS/Linux)
  python reference/scripts/sync_skills.py --interval 300    # check moi 5 phut

Cai dat Task Scheduler (Windows):
  Task Scheduler > Tao task moi > Trigger: Every 30 min > Action: python D:\path\reference\scripts\sync_skills.py

Cai dat crontab (macOS/Linux):
  */5 * * * * cd /path/to/sap-abap-agent && python reference/scripts/sync_skills.py
"""

import argparse
import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path

# === CONFIG ===
REPO_DIR = Path(__file__).resolve().parent.parent.parent  # mac dinh: repo root (file nay nam o reference/scripts/)
DEFAULT_INTERVAL = 300  # 5 phut (giay)
LOG_FILE = REPO_DIR / ".sap-abap-agent" / "sync_skills.log"
LOCK_FILE = REPO_DIR / ".sap-abap-agent" / "sync_skills.lock"

# === UTILITIES ===

def log(msg: str):
    """Ghi log ra console va file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass  # Khong log duoc thi thoi


def is_already_running() -> bool:
    """Kiem tra co instance khac dang chay khong (stampede protection)."""
    try:
        if LOCK_FILE.exists():
            # Check PID that wrote the lock
            pid = int(LOCK_FILE.read_text().strip())
            if platform.system() == "Windows":
                # Windows: check via tasklist
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                    capture_output=True, text=True, timeout=5
                )
                if str(pid) in result.stdout:
                    return True
            else:
                # macOS/Linux: check via kill -0
                try:
                    os.kill(pid, 0)
                    return True
                except OSError:
                    pass
        # Write new lock
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCK_FILE.write_text(str(os.getpid()))
        return False
    except Exception:
        return False


def sync_skills() -> bool:
    """
    Chay git pull de lay skills moi nhat.
    Returns: True neu co cap nhat, False neu da up-to-date hoac loi.
    """
    try:
        # Kiem tra xem co git repo khong
        git_dir = REPO_DIR / ".git"
        if not git_dir.exists():
            log("⚠️ Khong tim thay .git — khong phai git repo. Bo qua.")
            return False

        # git fetch truoc de kiem tra nhanh
        log("🔍 Dang kiem tra cap nhat tren GitHub...")
        fetch = subprocess.run(
            ["git", "fetch", "origin", "main"],
            capture_output=True, text=True, timeout=30,
            cwd=REPO_DIR
        )
        if fetch.returncode != 0:
            log(f"⚠️ git fetch that bai: {fetch.stderr.strip()}")
            return False

        # Kiem tra xem co commit moi khong
        status = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True, timeout=10,
            cwd=REPO_DIR
        )
        new_commits = status.stdout.strip()
        if new_commits == "0":
            log("✅ Skills da la phien ban moi nhat.")
            return False

        log(f"📦 Phat hien {new_commits} commit moi. Dang cap nhat...")
        pull = subprocess.run(
            ["git", "pull", "--ff-only", "origin", "main"],
            capture_output=True, text=True, timeout=60,
            cwd=REPO_DIR
        )

        if pull.returncode == 0:
            # Dem so file thay doi
            changed = subprocess.run(
                ["git", "diff", "--name-only", "HEAD@{1}", "HEAD"],
                capture_output=True, text=True, timeout=10,
                cwd=REPO_DIR
            )
            files = [f for f in changed.stdout.strip().split("\n") if f]
            # Chi dem file quan trong (skills/ agents/ commands/ reference/)
            relevant = [f for f in files if f.startswith(("skills/", "agents/", "commands/", "reference/"))]

            log(f"✅ Cap nhat thanh cong! {len(relevant)} skills/agents moi.")
            for f in relevant[:10]:  # Chi show 10 file dau
                log(f"   📄 {f}")
            if len(relevant) > 10:
                log(f"   ... va {len(relevant) - 10} file khac.")
            return True
        else:
            log(f"⚠️ git pull that bai: {pull.stderr.strip()}")
            # Thu git rebase?
            if "merge" in pull.stderr.lower():
                log("💡 Hint: Ban co the co thay doi local. Chay 'git stash' truoc khi dong bo.")
            return False

    except subprocess.TimeoutExpired:
        log("⏰ Timeout: GitHub qua cham hoac mat mang.")
        return False
    except FileNotFoundError:
        log("❌ Khong tim thay 'git' trong PATH. Cai git truoc da.")
        return False
    except Exception as e:
        log(f"❌ Loi khong xac dinh: {e}")
        return False


def run_once():
    """Chay dong bo 1 lan."""
    if is_already_running():
        log("⚠️ Co instance sync khac dang chay. Thoat.")
        return
    try:
        sync_skills()
    finally:
        # Clean up lock file
        try:
            if LOCK_FILE.exists():
                LOCK_FILE.unlink()
        except Exception:
            pass


def run_daemon(interval: int):
    """Chay ngam background, check dinh ky."""
    if is_already_running():
        log(f"⚠️ Da co instance sync dang chay (PID: {LOCK_FILE.read_text().strip()}). Thoat.")
        return

    log("🔄 Skill Sync Daemon BAT DAU")
    log(f"📁 Repo: {REPO_DIR}")
    log(f"⏰ Interval: {interval}s ({interval // 60} phut)")
    log(f"📝 Log: {LOG_FILE}")
    log(f"🔒 Lock: {LOCK_FILE}")
    print("-" * 50)

    try:
        while True:
            sync_skills()
            print(f"💤 Ngu {interval}s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        log("🛑 Daemon dung boi nguoi dung.")
    finally:
        try:
            if LOCK_FILE.exists():
                LOCK_FILE.unlink()
        except Exception:
            pass
        log("👋 Daemon ket thuc.")


# === MAIN ===

def main():
    parser = argparse.ArgumentParser(
        description="🔄 Skill Sync Daemon — SAP ABAP Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Vi du:
  %(prog)s                          # chay 1 lan
  %(prog)s --daemon                 # chay background (macOS/Linux: nohup)
  %(prog)s --daemon --interval 600  # check moi 10 phut
  %(prog)s --dir /path/to/repo      # chi dinh thu muc repo

Cai dat Task Scheduler (Windows):
  Task Scheduler > Tao task > Trigger: moi 30 phut > Action: python reference/scripts/sync_skills.py

Cai dat crontab (macOS/Linux):
  */5 * * * * cd /path/to/sap-abap-agent && python reference/scripts/sync_skills.py
        """
    )
    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Chay background (mac dinh: chay 1 lan roi thoat)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Interval giua cac lan check (giay). Mac dinh: {DEFAULT_INTERVAL}s"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Duong dan den thu muc repo SAP ABAP Agent"
    )

    args = parser.parse_args()

    # Override REPO_DIR neu duoc chi dinh
    global REPO_DIR
    if args.dir:
        REPO_DIR = Path(args.dir).resolve()

    if args.daemon:
        run_daemon(args.interval)
    else:
        run_once()


if __name__ == "__main__":
    main()
