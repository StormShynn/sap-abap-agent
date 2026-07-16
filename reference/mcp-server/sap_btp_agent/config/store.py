"""Load/save config (khong nhay cam) theo tung profile.

File: profiles/<id>/config.json
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .paths import get_profile_config_file, mirror_write_text
from .profile import ensure_app_dir, get_current_active



# ===== Service type taxonomy ============================================
# Schema moi (2026-07): phan biet ro giua cac bien the SAP
# - s4hc_(private) : S/4HANA Cloud Private Edition (single-tenant, SAP-managed)
# - s4hc_(public)  : S/4HANA Cloud Public Edition (multi-tenant SaaS)
# - btp            : SAP BTP ABAP Environment (Steampunk) - runtime rieng tren CF/Kyma
# - onprem         : On-premise / RISE with SAP on customer-managed infra
SERVICE_TYPES: tuple[str, ...] = (
    "s4hc_(private)",
    "s4hc_(public)",
    "btp",
    "onprem",
)
SERVICE_TYPE_DEFAULT = "s4hc_(public)"

# Tuong thich nguoc: gia tri schema cu ("s4hc" | "btp" | "onprem") -> schema moi
SERVICE_TYPE_ALIASES: dict[str, str] = {
    "s4hc": "s4hc_(public)",
}


def normalize_service_type(value: object) -> str:
    """Chuan hoa service type ve 1 trong SERVICE_TYPES.

    - "" / None -> SERVICE_TYPE_DEFAULT
    - gia tri cu (alias) -> gia tri moi tuong ung
    - gia tri moi -> gia tri moi (neu khong nam trong SERVICE_TYPES thi raise)
    """
    v = str(value or "").strip()
    if not v:
        return SERVICE_TYPE_DEFAULT
    v = SERVICE_TYPE_ALIASES.get(v, v)
    if v not in SERVICE_TYPES:
        raise ValueError(
            f"Service type khong hop le: {value!r}. "
            f"Chon mot trong: {', '.join(SERVICE_TYPES)}"
        )
    return v


def normalize_btp_url(value: object) -> str:
    """Dam bao btpUrl co scheme (https://) - SAP BTP/S4HANA luon dung HTTPS.

    Thieu scheme khien urllib.parse khong nhan dien duoc host (derive profile
    ID tu URL fail) va Playwright/httpx tu choi request voi loi kho hieu
    (VD "Cannot navigate to invalid URL"). Chuoi rong giu nguyen (chua setup).
    """
    v = str(value or "").strip()
    if not v or re.match(r"^https?://", v, re.IGNORECASE):
        return v
    return f"https://{v}"


DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "btpUrl": "",
    "tenant": "",
    "clientId": "",
    "authMode": "oauth2",  # oauth2 | password | bearer | cookie
    "scope": "",
    "region": "eu10",
    "service": SERVICE_TYPE_DEFAULT,   # s4hc_(private) | s4hc_(public) | btp | onprem
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
        # Tuong thich nguoc: tu chuan hoa service type cu ("s4hc"/"btp") ve schema moi
        if "service" in data:
            try:
                data["service"] = normalize_service_type(data["service"])
            except ValueError:
                data["service"] = SERVICE_TYPE_DEFAULT
        # Tu sua config cu thieu scheme (VD luu tu ban truoc khi co fix nay)
        if "btpUrl" in data:
            data["btpUrl"] = normalize_btp_url(data["btpUrl"])
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
    # Validate / chuan hoa service type (alias s4hc -> s4hc_(public), reject gia tri khong hop le)
    if "service" in merged:
        merged["service"] = normalize_service_type(merged["service"])
    if "btpUrl" in merged:
        merged["btpUrl"] = normalize_btp_url(merged["btpUrl"])
    content = json.dumps(merged, ensure_ascii=False, indent=2)
    file.write_text(content, encoding="utf-8")
    mirror_write_text(file, content)
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
