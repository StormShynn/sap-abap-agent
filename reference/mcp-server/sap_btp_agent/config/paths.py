"""Xac dinh duong dan folder cau hinh trong user home.

Mac dinh:
    Windows: %USERPROFILE%\\.sap-btp-agent\\
    macOS/Linux: ~/.sap-btp-agent/

Co the override qua SAP_BTP_AGENT_HOME.

Cau truc multi-profile:
    <appDir>/
    +- profiles.json             <- registry
    +- profiles/<id>/
    |   +- config.json           <- thong tin khong nhay cam
    |   +- secrets.json          <- secret da ma hoa
    +- log/
    +- cache/
"""
from __future__ import annotations

import os
import re
from pathlib import Path

APP_DIR_NAME = ".sap-btp-agent"

_PROFILE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def get_app_dir() -> Path:
    """Tra ve folder goc cua SAP BTP Agent. Tao neu chua co (lazy)."""
    override = os.environ.get("SAP_BTP_AGENT_HOME", "").strip()
    if override:
        return Path(override).resolve()
    home = Path.home()
    if not home or str(home) == "":
        raise RuntimeError("Khong xac dinh duoc thu muc home.")
    return home / APP_DIR_NAME


def get_active_profile_id() -> str | None:
    """Env SAP_BTP_PROFILE (uu tien cao nhat) hoac None."""
    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    return env or None


def _validate_profile_id(id_: str) -> None:
    if not id_ or not _PROFILE_ID_RE.match(id_) or len(id_) > 64:
        raise ValueError(
            f'Profile id khong hop le: "{id_}". '
            "Chi cho phep chu, so, '.', '_', '-' (toi da 64 ky tu)."
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
