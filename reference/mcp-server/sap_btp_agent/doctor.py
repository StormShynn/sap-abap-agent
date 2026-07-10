"""Doctor: kiem tra moi truong Python + cac dependency hay bi thieu/an trong lang.

Chay duoc TRUOC KHI sap-btp-agent nam tren PATH (vi day la diem hay gay nham lan nhat):
    python -m sap_btp_agent.doctor

Sau khi da cai xong va tren PATH, cung goi duoc qua:
    sap-btp-agent doctor
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import sysconfig
from pathlib import Path


def _check_python_version() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 10)
    return ok, f"Python {sys.version.split()[0]} ({'OK' if ok else 'can >= 3.10'})"


def _entry_point_name() -> str:
    return "sap-btp-agent.exe" if os.name == "nt" else "sap-btp-agent"


def _find_entry_point_dir() -> Path | None:
    """Tim folder chua script sap-btp-agent, thu ca default scheme va user scheme.

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


def _check_path() -> tuple[bool, str]:
    on_path = shutil.which("sap-btp-agent")
    if on_path:
        return True, f"sap-btp-agent tren PATH: {on_path}"

    found_dir = _find_entry_point_dir()
    if found_dir is None:
        return False, "Khong tim thay sap-btp-agent o dau ca -- kiem tra lai 'pip install -e .' da chay thanh cong chua."

    msg = f"sap-btp-agent CO duoc cai, nhung folder chua no KHONG nam trong PATH:\n      {found_dir}\n"
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
    return False, msg


def _check_module(name: str, label: str, *, required: bool) -> tuple[bool, str]:
    found = importlib.util.find_spec(name) is not None
    if found:
        return True, f"{label}: OK"
    return (not required), f"{label}: {'THIEU (bat buoc)' if required else 'chua cai (optional)'}"


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


def main() -> None:
    print()
    print("=" * 60)
    print("  SAP ABAP Agent -- Doctor (kiem tra moi truong)")
    print("=" * 60)
    print()

    checks: list[tuple[bool, str]] = [
        _check_python_version(),
        _check_path(),
        _check_module("mcp", "MCP SDK", required=True),
        _check_module("httpx", "httpx", required=True),
        _check_module("cryptography", "cryptography", required=True),
    ]
    if os.name == "nt":
        checks.append(_check_module("win32crypt", "pywin32 (DPAPI cho secrets)", required=False))
    checks.append(_check_playwright_browsers())

    all_ok = True
    for ok, msg in checks:
        icon = "  OK  " if ok else "  !!  "
        print(f"{icon}{msg}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("  Moi thu deu OK. Chay: sap-btp-agent setup <URL>")
    else:
        print("  Co van de can xu ly o cac dong '!!' phia tren truoc khi dung sap-btp-agent.")
    print()


if __name__ == "__main__":
    main()
