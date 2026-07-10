"""Load/save config (khong nhay cam) theo tung profile.

File: profiles/<id>/config.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .paths import get_profile_config_file
from .profile import ensure_app_dir, get_current_active

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "btpUrl": "",
    "tenant": "",
    "clientId": "",
    "authMode": "oauth2",  # oauth2 | password | bearer | cookie
    "scope": "",
    "region": "eu10",
    "service": "s4hc",     # s4hc | btp | onprem
    "adtEnabled": True,
    "autoReconnect": True,
    "timeoutMs": 30000,
    "reauthMode": "manual",  # manual (paste cookie) | auto (playwright) - chi cho cookie auth
}


def load_config(profile_id: str | None = None) -> dict[str, Any]:
    pid = profile_id or get_current_active()
    if not pid:
        raise RuntimeError("Chua co profile nao. Chay: sap-btp-agent setup")
    ensure_app_dir()
    file = get_profile_config_file(pid)
    if not file.exists():
        return {**DEFAULT_CONFIG}
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **data}
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Loi doc {file}: {err}") from err


def save_config(profile_id: str | None, partial: dict[str, Any]) -> dict[str, Any]:
    pid = profile_id or get_current_active()
    if not pid:
        raise RuntimeError("Chua co profile nao. Chay: sap-btp-agent setup")
    ensure_app_dir()
    file = get_profile_config_file(pid)
    file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    current = load_config(pid) if file.exists() else {**DEFAULT_CONFIG}
    merged = {**current, **partial, "version": 1}
    file.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(file, 0o600)
    except Exception:
        pass
    return {"id": pid, "config": merged}


def is_configured(profile_id: str | None = None) -> bool:
    try:
        cfg = load_config(profile_id)
        return bool(cfg.get("btpUrl") and cfg.get("clientId"))
    except Exception:
        return False
