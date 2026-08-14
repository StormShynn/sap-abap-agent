"""Tai va quan ly binary `vsp` (vibing-steampunk) - Go binary phan tich ABAP
sau (package health, dead code, debug adapter). Chay side-by-side voi
mcp-sap-connect qua MCP rieng (`sap-vsp`), KHONG fork/patch - luon tai
truc tiep tu upstream `oisee/vibing-steampunk`.

Nguon asset + SHA256: xac minh cheo ngay 2026-07-30 giua GitHub Releases API
(`digest` field cua tung asset) va `checksums.txt` do chinh release dinh kem -
ca 2 khop nhau 9/9 asset. Release v2.38.1 publish binary Go tran (KHONG phai
.tar.gz/.zip) cho tung platform, khong can buoc giai nen.
"""
from __future__ import annotations

import hashlib
import platform
import stat
import urllib.error
import urllib.request
from pathlib import Path

from .config.paths import get_bin_dir

VSP_VERSION = "2.38.1"
_RELEASE_BASE = f"https://github.com/oisee/vibing-steampunk/releases/download/v{VSP_VERSION}"

# platform_key -> (ten asset tren GitHub Release, SHA256 da xac minh)
_ASSETS: dict[str, tuple[str, str]] = {
    "darwin_amd64":  ("vsp-darwin-amd64",      "270ccabe2314efc8fa1a5936a861631980fe6fa573fce88f46fc3f5abada29a4"),
    "darwin_arm64":  ("vsp-darwin-arm64",      "a79b7ef73c419677840c7d6213707448e67241c1fec09a2862c26fe3bad6d9c4"),
    "linux_386":     ("vsp-linux-386",         "cfa9a916aa2bd89eaffec2a5c5cefc1a134365f9395775cfc1983e0d8a712e75"),
    "linux_amd64":   ("vsp-linux-amd64",       "39addbd62d0f26dd40d6bb3b0f0eae17ef57079d96b8306c8e3d7576f903a550"),
    "linux_arm":     ("vsp-linux-arm",         "1a38a893fdb6ca3c14109d278badd881ee0b1d993397f9a39755eca61375ccc3"),
    "linux_arm64":   ("vsp-linux-arm64",       "423362a8ef7b8013228c4f8204bdabd4cba53ee2184e992e4a78df4c174cd23a"),
    "windows_386":   ("vsp-windows-386.exe",   "1270d401c81b38a2fd2fd436d7dfb53761ffed76bc91b9c36d7e1c0b2e9f2121"),
    "windows_amd64": ("vsp-windows-amd64.exe", "02e1929e7e265e10c8979b27143c2badda668d0e5daa8dcce87227778dd9ac58"),
    "windows_arm64": ("vsp-windows-arm64.exe", "9d97510236c2d0cad8d24cb14e07c76f5d28439d125da4a5f9fc30d985dbaa11"),
}


class VspSetupError(RuntimeError):
    """Khong tai duoc / khong verify duoc vsp binary."""


def detect_platform_key(system: str | None = None, machine: str | None = None) -> str:
    """Map (platform.system(), platform.machine()) ve 1 key trong _ASSETS.

    Nhan tham so tuy chon de test khong phai monkeypatch module `platform`.
    Raise VspSetupError neu OS/kien truc hien tai khong nam trong asset upstream.
    """
    system = (system if system is not None else platform.system()).lower()
    machine = (machine if machine is not None else platform.machine()).lower()

    os_key = {"darwin": "darwin", "linux": "linux", "windows": "windows"}.get(system)
    if os_key is None:
        raise VspSetupError(f"He dieu hanh khong duoc vsp ho tro: {system!r}")

    if machine in ("x86_64", "amd64"):
        arch_key = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch_key = "arm64"
    elif machine in ("i386", "i686", "x86"):
        arch_key = "386"
    elif machine.startswith("arm") and os_key == "linux":
        arch_key = "arm"
    else:
        raise VspSetupError(f"Kien truc khong duoc vsp ho tro: {machine!r}")

    key = f"{os_key}_{arch_key}"
    if key not in _ASSETS:
        raise VspSetupError(f"Khong co vsp build cho {key}")
    return key


def binary_path() -> Path:
    """Duong dan dich (chua chac da ton tai) cua vsp trong <appDir>/bin/."""
    name = "vsp.exe" if platform.system().lower() == "windows" else "vsp"
    return get_bin_dir() / name


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = dest.parent / (dest.name + ".part")
    try:
        try:
            with urllib.request.urlopen(url, timeout=60) as resp, tmp.open("wb") as out:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            raise VspSetupError(f"Tai vsp that bai ({url}): {err}") from err
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def ensure_vsp(*, force: bool = False) -> Path:
    """Tra ve duong dan executable `vsp`, san sang chay.

    Idempotent: neu binary da ton tai va force=False, tra ve ngay (khong tai
    lai, khong verify lai - verify chi chay 1 lan luc tai). Neu chua co (hoac
    force=True): tai tu GitHub Release, verify SHA256, chmod +x (POSIX), roi
    tra ve path. Raise VspSetupError neu platform khong ho tro, mang loi, hoac
    SHA256 khong khop (binary bi hong hoac upstream doi asset ma chua cap
    nhat pin trong module nay).
    """
    dest = binary_path()
    if dest.exists() and not force:
        return dest

    key = detect_platform_key()
    asset_name, expected_sha256 = _ASSETS[key]
    url = f"{_RELEASE_BASE}/{asset_name}"

    _download(url, dest)

    actual_sha256 = _sha256_of(dest)
    if actual_sha256 != expected_sha256:
        dest.unlink(missing_ok=True)
        raise VspSetupError(
            f"SHA256 khong khop cho {asset_name} (vsp {VSP_VERSION}): "
            f"expect {expected_sha256}, nhan duoc {actual_sha256}. "
            f"Upstream co the da thay doi asset nay - KHONG dung binary vua tai, "
            f"bao loi de cap nhat pin trong setup_vsp.py."
        )

    if platform.system().lower() != "windows":
        mode = dest.stat().st_mode
        dest.chmod(mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    return dest
