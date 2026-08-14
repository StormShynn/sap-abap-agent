"""Doctor: kiem tra moi truong Python + cac dependency hay bi thieu/an trong lang.

Chay duoc TRUOC KHI mcp-sap-connect nam tren PATH (vi day la diem hay gay nham lan nhat):
    python -m mcp_sap_connect.doctor

Sau khi da cai xong va tren PATH, cung goi duoc qua:
    mcp-sap-connect doctor
    mcp-sap-connect doctor --json   # machine-readable (GUI Copy PATH fix)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import sysconfig
from pathlib import Path


def _check_python_version() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 10)
    return ok, f"Python {sys.version.split()[0]} ({'OK' if ok else 'can >= 3.10'})"


def _entry_point_name() -> str:
    return "mcp-sap-connect.exe" if os.name == "nt" else "mcp-sap-connect"


def _find_entry_point_dir() -> Path | None:
    """Tim folder chua script mcp-sap-connect, thu ca default scheme va user scheme.

    pip co the cai vao user-scheme scripts dir (VD: %APPDATA%\\Python\\PythonXY\\Scripts
    tren Windows) neu khong co quyen viet vao Python goc -- day chinh la nguyen nhan
    loi "khong nhan dien lenh" hay gap nhat.
    """
    exe_name = _entry_point_name()
    user_scheme = "nt_user" if os.name == "nt" else "posix_user"
    seen: set[str] = set()
    for scheme in (None, user_scheme):
        try:
            d = sysconfig.get_path("scripts", scheme=scheme) if scheme else sysconfig.get_path("scripts")
        except Exception:
            continue
        if not d or d in seen:
            continue
        seen.add(d)
        if (Path(d) / exe_name).exists():
            return Path(d)
    return None


def _path_fix_script(scripts_dir: Path) -> str:
    """Chuoi fix PATH de copy (PowerShell User PATH tren Windows, export tren Unix)."""
    if os.name == "nt":
        return (
            f"$f = '{scripts_dir}'\n"
            "$cur = [Environment]::GetEnvironmentVariable('PATH','User')\n"
            "[Environment]::SetEnvironmentVariable('PATH', $cur.TrimEnd(';') + ';' + $f, 'User')"
        )
    return f'export PATH="{scripts_dir}:$PATH"'


def _check_path() -> tuple[bool, str, Path | None, str | None]:
    """Tra (path_ok, message, scripts_dir, path_fix).

    path_fix chi co khi binary da cai nhung folder Scripts khong nam tren PATH.
    """
    on_path = shutil.which("mcp-sap-connect")
    if on_path:
        return True, f"mcp-sap-connect tren PATH: {on_path}", None, None

    found_dir = _find_entry_point_dir()
    if found_dir is None:
        return (
            False,
            "Khong tim thay mcp-sap-connect o dau ca -- kiem tra lai 'pip install -e .' da chay thanh cong chua.",
            None,
            None,
        )

    path_fix = _path_fix_script(found_dir)
    msg = f"mcp-sap-connect CO duoc cai, nhung folder chua no KHONG nam trong PATH:\n      {found_dir}\n"
    if os.name == "nt":
        msg += (
            "    Fix (PowerShell, khong can quyen Admin):\n"
            f"      $f = '{found_dir}'\n"
            "      $cur = [Environment]::GetEnvironmentVariable('PATH','User')\n"
            "      [Environment]::SetEnvironmentVariable('PATH', $cur.TrimEnd(';') + ';' + $f, 'User')\n"
            "    Sau do MO TERMINAL MOI (cua so dang mo se khong tu nhan)."
        )
    else:
        msg += (
            f'    Fix: them vao ~/.bashrc hoac ~/.zshrc:\n      export PATH="{found_dir}:$PATH"\n'
            "    Sau do: source ~/.bashrc (hoac mo terminal moi)."
        )
    return False, msg, found_dir, path_fix


def _check_module(name: str, label: str, *, required: bool) -> tuple[bool, str]:
    found = importlib.util.find_spec(name) is not None
    if found:
        return True, f"{label}: OK"
    return (not required), f"{label}: {'THIEU (bat buoc)' if required else 'chua cai (optional)'}"


def _cleanup_orphan_mcp_processes() -> tuple[bool, str]:
    """Tim + tu dong dong tien trinh mcp-sap-connect.exe bi orphan (process
    Claude Code/terminal cha da tat nhung MCP server con van con song).

    Chi Windows: day la nguyen nhan hay gap nhat khien `pip install --upgrade`
    fail voi loi "file dang duoc su dung boi tien trinh khac" - file .exe bi
    lock boi bat ky tien trinh mcp-sap-connect.exe nao con song, ke ca orphan.
    Chi dong tien trinh KHONG con process cha (an toan tuyet doi - khong the
    lam gian doan session nao dang dung, vi theo dinh nghia khong con ai
    tham chieu no nua). KHONG dong tien trinh van co process cha con song.
    """
    if os.name != "nt":
        return True, "Cleanup orphan MCP process: bo qua (chi ap dung Windows)"

    import subprocess

    ps_script = (
        "$all = Get-CimInstance Win32_Process; "
        "$targets = $all | Where-Object { $_.Name -eq 'mcp-sap-connect.exe' }; "
        "$alivePids = $all.ProcessId; "
        "$orphans = $targets | Where-Object { $_.ParentProcessId -notin $alivePids }; "
        "$orphans | Select-Object -ExpandProperty ProcessId | ConvertTo-Json"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True, text=True, timeout=15,
        )
    except Exception as err:
        return True, f"Cleanup orphan MCP process: khong chay duoc PowerShell de kiem tra ({err})"

    raw = (result.stdout or "").strip()
    if not raw:
        return True, "Cleanup orphan MCP process: khong co tien trinh orphan"

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return True, "Cleanup orphan MCP process: khong parse duoc ket qua PowerShell (bo qua)"

    pids = [parsed] if isinstance(parsed, int) else list(parsed)
    if not pids:
        return True, "Cleanup orphan MCP process: khong co tien trinh orphan"

    killed = []
    for pid in pids:
        try:
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid), "/T"],
                capture_output=True, text=True, timeout=10,
            )
            killed.append(str(pid))
        except Exception:
            pass

    if killed:
        return True, (
            f"Cleanup orphan MCP process: da tu dong dong {len(killed)} tien trinh "
            f"mcp-sap-connect.exe bi orphan (PID {', '.join(killed)}) - se khong con lock file "
            f".exe cho lan 'pip install --upgrade' sau"
        )
    return True, "Cleanup orphan MCP process: phat hien orphan nhung khong dong duoc - thu taskkill thu cong"


def _check_playwright_browsers() -> tuple[bool, str]:
    if importlib.util.find_spec("playwright") is None:
        return True, "Playwright + chromium: chua cai (option 3 'auto mo browser' se fallback ve paste tay)"

    cache_dir = (
        Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
        if os.name == "nt"
        else Path.home() / ".cache" / "ms-playwright"
    )
    if cache_dir.exists() and any(p.name.startswith("chromium") for p in cache_dir.iterdir()):
        return True, f"Playwright chromium: OK ({cache_dir})"
    return False, "Playwright da cai nhung CHUA co chromium binary. Chay: playwright install chromium"


def collect_report() -> dict:
    """Chay tat ca check, tra dict dung cho --json / GUI."""
    path_ok, path_msg, scripts_dir, path_fix = _check_path()
    checks: list[tuple[bool, str]] = [
        _check_python_version(),
        (path_ok, path_msg),
        _check_module("mcp", "MCP SDK", required=True),
        _check_module("httpx", "httpx", required=True),
        _check_module("cryptography", "cryptography", required=True),
    ]
    if os.name == "nt":
        checks.append(_check_module("win32crypt", "pywin32 (DPAPI cho secrets)", required=False))
        checks.append(_cleanup_orphan_mcp_processes())
    checks.append(_check_playwright_browsers())

    all_ok = all(ok for ok, _ in checks)
    return {
        "all_ok": all_ok,
        "path_ok": path_ok,
        "scripts_dir": str(scripts_dir) if scripts_dir else None,
        "path_fix": path_fix,
        "checks": [{"ok": ok, "message": msg} for ok, msg in checks],
    }


def _print_human(report: dict) -> None:
    print()
    print("=" * 60)
    print("  SAP ABAP Agent -- Doctor (kiem tra moi truong)")
    print("=" * 60)
    print()

    for item in report["checks"]:
        icon = "  OK  " if item["ok"] else "  !!  "
        print(f"{icon}{item['message']}")

    print()
    if report["all_ok"]:
        print("  Moi thu deu OK. Chay: mcp-sap-connect setup <URL>")
    else:
        print("  Co van de can xu ly o cac dong '!!' phia tren truoc khi dung mcp-sap-connect.")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcp-sap-connect doctor")
    parser.add_argument(
        "--json",
        action="store_true",
        help="In ket qua JSON (path_ok, scripts_dir, path_fix, checks) cho GUI",
    )
    args = parser.parse_args(argv)

    report = collect_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        _print_human(report)
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
