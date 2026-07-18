"""Wrapper chay sap-btp-agent qua subprocess va stream stdout/stderr.

Thiet ke de goi tu ca GUI (Tkinter) lan tray (pystray):

- start(args, on_line, on_done): chay subprocess, moi dong stdout/stderr goi
  on_line(text). Khi process ket thuc goi on_done(returncode).
- start_new_console(args, on_done): chay subprocess trong cua so CMD moi (dung
  cho wizard setup vi can nhap cookie/interactively).

Luu y quan trong:
- KHONG dung Popen trong main thread neu muon GUI khong bi dong bang.
- Doc stdout/sterr o worker thread, dong gian giao dien qua root.after().
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import threading
from typing import Callable, Optional


# Sap-btp-agent entry point (cung ten trong pyproject [project.scripts])
CLI_BIN = "sap-btp-agent"


def _resolve_executable() -> list[str]:
    """Tra ve command de chay CLI.

    - Windows: uu tien .exe (pip cai entry point) de khong bi console popup.
    - Moi truong dev: fallback ve `python -m sap_btp_agent.cli`.
    """
    import shutil
    found = shutil.which(CLI_BIN)
    if found:
        return [found]
    # Dev mode
    return [sys.executable, "-m", "sap_btp_agent.cli"]


def start(args: list[str], on_line: Callable[[str], None],
          on_done: Callable[[int], None], *, env_extra: Optional[dict] = None) -> "Job":
    """Chay subprocess, stream stdout/sterr -> on_line, khi xong goi on_done.

    Args:
        args: vi du ["reauth", "project1.s4hana.cloud.sap"] (KHONG ten CLI).
        on_line(text): callback moi dong output (newline da stripped).
        on_done(returncode): callback khi process ket thuc.
    """
    cmd = _resolve_executable() + list(args)
    creationflags = 0
    if os.name == "nt":
        # CREATE_NO_WINDOW = 0x08000000 - chan console popup tren Windows.
        creationflags = 0x08000000

    # Merge env (extra vars override parent)
    proc_env = None
    if env_extra:
        import os as _os
        proc_env = _os.environ.copy()
        proc_env.update(env_extra)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # gop stderr vao stdout cho don gian
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,  # line-buffered
        creationflags=creationflags,
        env=proc_env,
    )

    job = Job(proc, cmd)

    def reader():
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                on_line(line.rstrip("\n").rstrip("\r"))
            proc.stdout.close()
        except Exception as err:
            on_line(f"[reader error] {err}")
        finally:
            rc = proc.wait()
            on_done(rc)

    job._thread = threading.Thread(target=reader, daemon=True)
    job._thread.start()
    return job


def start_new_console(args: list[str], on_done: Optional[Callable[[int], None]] = None) -> "Job":
    """Chay subprocess trong cua so CMD moi (CREATE_NEW_CONSOLE).

    Dung cho wizard `setup` (nhap URL, OAuth, cookie paste...) - vi can
    interactive stdin/stdout truc tiep.
    """
    cmd = _resolve_executable() + list(args)
    creationflags = 0
    if os.name == "nt":
        # CREATE_NEW_CONSOLE = 0x00000010
        creationflags = 0x00000010

    proc = subprocess.Popen(cmd, creationflags=creationflags)
    job = Job(proc, cmd, new_console=True)

    if on_done is not None:
        def waiter():
            rc = proc.wait()
            on_done(rc)
        job._thread = threading.Thread(target=waiter, daemon=True)
        job._thread.start()
    return job


class Job:
    """Doi tuong bieu dien 1 tien trinh dang chay."""

    def __init__(self, proc: subprocess.Popen, cmd: list[str], new_console: bool = False):
        self.proc = proc
        self.cmd = cmd
        self.new_console = new_console
        self._thread: Optional[threading.Thread] = None

    @property
    def pid(self) -> int:
        return self.proc.pid

    @property
    def running(self) -> bool:
        return self.proc.poll() is None

    def cancel(self) -> None:
        """Terminate process (xu ly cross-platform)."""
        if not self.running:
            return
        try:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        except Exception:
            pass

    def __repr__(self) -> str:
        rc = self.proc.poll()
        state = f"rc={rc}" if rc is not None else "running"
        return f"<Job pid={self.pid} {state} cmd={shlex.join(self.cmd)}>"
