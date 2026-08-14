"""Xac dinh duong dan folder cau hinh trong user home.

Mac dinh (sau rename 1.14.0):
    Windows: %USERPROFILE%\\.mcp-sap-connect\\
    macOS/Linux: ~/.mcp-sap-connect/

Co the override qua MCP_SAP_CONNECT_HOME (uu tien) hoac MCP_SAP_CONNECT_HOME (backward-compat).

Migration tu 1.x:
    Neu ~/.mcp-sap-connect khong ton tai nhung ~/.sap-btp-agent co,
    tu dong move toan bo folder sang ~/.mcp-sap-connect (1 lan).
    Backup dat tai <parent>/.sap-btp-agent.bak/<timestamp>/ neu that bai
    giua chang de co the rollback bang tay.

Cau truc multi-profile:
    <appDir>/
    +- profiles.json             <- registry
    +- profiles/<id>/
    |   +- config.json           <- thong tin khong nhay cam
    |   +- secrets.json          <- secret da ma hoa
    +- log/
    +- cache/
    +- in/                       <- FS/tai lieu dau vao, khong commit git
    +- out/                      <- output sinh ra
    +- bin/                      <- vendor binaries (vd vsp), khong commit git
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

APP_DIR_NAME = ".mcp-sap-connect"
LEGACY_APP_DIR_NAME = ".sap-btp-agent"

_PROFILE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def get_legacy_app_dir() -> Path:
    return Path.home() / LEGACY_APP_DIR_NAME


def get_app_dir() -> Path:
    override_new = os.environ.get("MCP_SAP_CONNECT_HOME", "").strip()
    override_old = os.environ.get("MCP_SAP_CONNECT_HOME", "").strip()
    if override_new:
        return Path(override_new).resolve()
    if override_old:
        return Path(override_old).resolve()
    home = Path.home()
    if not home or str(home) == "":
        raise RuntimeError("Khong xac dinh duoc thu muc home.")
    new_dir = home / APP_DIR_NAME
    legacy_dir = home / LEGACY_APP_DIR_NAME
    if new_dir.exists():
        return new_dir
    if legacy_dir.exists():
        _migrate_legacy_app_dir(legacy_dir, new_dir)
        return new_dir
    return new_dir


def _migrate_legacy_app_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        sys.stderr.write(
            f"[mcp-sap-connect] Khong the migrate: {dst} da ton tai.\n"
            f"                    Giu nguyen {src} - vui long kiem tra thu cong.\n"
        )
        return
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        sys.stderr.write(
            f"[mcp-sap-connect] Migrated: {src} -> {dst}\n"
            f"                    (de xem profile cu: ls {dst}/profiles/)\n"
        )
    except Exception as err:
        try:
            backup = src.with_suffix(src.suffix + ".bak")
            if backup.exists():
                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                backup = src.parent / f"{src.name}.bak.{ts}"
            shutil.copytree(str(src), str(backup))
            sys.stderr.write(
                f"[mcp-sap-connect] Migration that bai ({err}).\n"
                f"                    Backup: {backup}\n"
                f"                    Re-run sau khi sua quyen, hoac copy thu cong:\n"
                f"                      cp -r {backup}/* {dst}/\n"
            )
        except Exception as backup_err:
            sys.stderr.write(
                f"[mcp-sap-connect] Migration + backup that bai:\n"
                f"  err: {err}\n  backup_err: {backup_err}\n"
                f"  Thu muc cu van nguyen tai: {src}\n"
            )


def get_active_profile_id() -> str | None:
    env_new = os.environ.get("MCP_SAP_CONNECT_PROFILE", "").strip()
    if env_new:
        return env_new
    env_old = os.environ.get("SAP_BTP_PROFILE", "").strip()
    return env_old or None


def _validate_profile_id(id_: str) -> None:
    if not id_ or not _PROFILE_ID_RE.match(id_) or len(id_) > 64:
        raise ValueError(
            f"Profile id khong hop le: {id_!r}. Chi cho phep chu, so, '.', '_', '-' (toi da 64 ky tu)."
        )


def get_profiles_dir() -> Path:
    return get_app_dir() / "profiles"


def get_profile_dir(id_: str) -> Path:
    _validate_profile_id(id_)
    return get_profiles_dir() / id_


def get_profile_config_file(id_: str) -> Path:
    return get_profile_dir(id_) / "config.json"


def get_profile_secrets_file(id_: str) -> Path:
    return get_profile_dir(id_) / "secrets.json"


def get_registry_file() -> Path:
    return get_app_dir() / "profiles.json"


def get_log_dir() -> Path:
    return get_app_dir() / "log"


def get_cache_dir() -> Path:
    return get_app_dir() / "cache"


def get_in_dir() -> Path:
    return get_app_dir() / "in"


def get_out_dir() -> Path:
    return get_app_dir() / "out"


def get_bin_dir() -> Path:
    return get_app_dir() / "bin"


def get_dev_mirror_dir() -> Path | None:
    override_new = os.environ.get("MCP_SAP_CONNECT_DEV_MIRROR", "").strip()
    if override_new:
        return Path(override_new).resolve()
    override_old = os.environ.get("MCP_SAP_CONNECT_DEV_MIRROR", "").strip()
    if override_old:
        return Path(override_old).resolve()
    return None


def dev_mirror_includes_secrets() -> bool:
    new_flag = os.environ.get("MCP_SAP_CONNECT_DEV_MIRROR_SECRETS", "").strip()
    if new_flag:
        return new_flag == "1"
    old_flag = os.environ.get("MCP_SAP_CONNECT_DEV_MIRROR_SECRETS", "").strip()
    return old_flag == "1"


def _mirror_target(real_file: Path) -> Path | None:
    mirror_root = get_dev_mirror_dir()
    if mirror_root is None:
        return None
    try:
        rel = real_file.relative_to(get_app_dir())
    except ValueError:
        return None
    return mirror_root / rel


def mirror_write_text(real_file: Path, content: str, *, sensitive: bool = False) -> None:
    if sensitive and not dev_mirror_includes_secrets():
        return
    target = _mirror_target(real_file)
    if target is None:
        return
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except Exception:
        pass


def mirror_write_bytes(real_file: Path, content: bytes) -> None:
    target = _mirror_target(real_file)
    if target is None:
        return
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    except Exception:
        pass
