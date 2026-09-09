"""Load/save config (khong nhay cam) theo tung profile.

File: profiles/<id>/config.json
"""
from __future__ import annotations

import contextlib
import json
import os
import re
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
    "rise_with_sap",
)
SERVICE_TYPE_DEFAULT = "s4hc_(public)"

# Tuong thich nguoc: gia tri schema cu ("s4hc" | "btp" | "onprem") -> schema moi
SERVICE_TYPE_ALIASES: dict[str, str] = {
    "s4hc": "s4hc_(public)",
    "rise": "rise_with_sap",
}

# Mo ta ngan cho moi service type (CLI hien thi trong setup wizard)
SERVICE_TYPE_DESCRIPTIONS: dict[str, str] = {
    "s4hc_(private)": "S/4HANA Cloud Private Edition (single-tenant, SAP-managed)",
    "s4hc_(public)":  "S/4HANA Cloud Public Edition (multi-tenant SaaS)",
    "btp":            "SAP BTP ABAP Environment (Steampunk) - runtime rieng tren CF/Kyma",
    "onprem":         "On-premise (customer-managed infrastructure)",
    "rise_with_sap":  "RISE with SAP (SAP-managed on customer infrastructure)",
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


def default_auth_mode_for_service(service: str) -> str:
    """Auth mode mac dinh theo service type.

    - s4hc_(public) / s4hc_(private) / rise_with_sap: cookie (browser SSO qua Playwright)
    - btp (Steampunk)        : oauth2 (client_credentials)
    - onprem                 : password (basic auth qua SAP router)
    User co the override trong config.json.
    """
    return {
        "s4hc_(public)":  "cookie",
        "s4hc_(private)": "cookie",
        "btp":            "oauth2",
        "onprem":         "password",
        "rise_with_sap":  "password",
    }.get(service, "oauth2")


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


# ===== routingHints schema (v2+) ============================================
# Moi profile co the khai bo kha nang backend. Phase 2 cua plan
# sap-multi-system-router se dung hint nay de `sap-multi-system-context`
# chon dung MCP server cho moi task. Tat ca field co default theo
# service type; user KHONG bat buoc dien.
ROUTING_HINT_KEYS: tuple[str, ...] = (
    "supportsReadonlyClass",
    "supportsDebug",
    "supportsVspSlim",
    "supportsVspHealth",
    "supportsDictBridge",
    "preferredTransport",
    "preferredAnalysis",
)


def _default_routing_hints(service: str) -> dict[str, Any]:
    """Default routing hints theo service type."""
    return {
        "supportsReadonlyClass": True,    # tat ca service deu ho tro doc class
        "supportsDebug":         service in ("onprem", "rise_with_sap", "s4hc_(private)"),
        "supportsVspSlim":       True,    # vsp co the phan tich dead code
        "supportsVspHealth":     True,    # vsp co the phan tich package health
        "supportsDictBridge":    service not in ("btp",),  # Steampunk khong cho DDIC
        "preferredTransport":    "sap-connect",
        "preferredAnalysis":     "sap-vsp",
    }


def normalize_routing_hints(value: object, service: str = SERVICE_TYPE_DEFAULT) -> dict[str, Any]:
    """Chuan hoa routing hints: reject unknown keys, fill missing keys theo service.

    Tra ve dict luon co day du 7 key. Raise ValueError neu:
      - value khong phai dict
      - co key khong nam trong ROUTING_HINT_KEYS
      - bool field khong phai bool
      - preferredTransport khong phai "sap-connect" / "sap-vsp"
      - preferredAnalysis khong phai "sap-vsp" / None
    """
    if value is None:
        return _default_routing_hints(service)
    if not isinstance(value, dict):
        raise ValueError(f"routingHints phai la dict, nhan duoc: {type(value).__name__}")
    unknown = set(value.keys()) - set(ROUTING_HINT_KEYS)
    if unknown:
        raise ValueError(f"routingHints co key khong ho tro: {sorted(unknown)}. Cho phep: {list(ROUTING_HINT_KEYS)}")
    defaults = _default_routing_hints(service)
    merged = {**defaults, **value}
    # Validate types
    for k in ("supportsReadonlyClass", "supportsDebug", "supportsVspSlim",
              "supportsVspHealth", "supportsDictBridge"):
        if not isinstance(merged[k], bool):
            raise ValueError(f"routingHints.{k} phai la bool, nhan duoc: {type(merged[k]).__name__}")
    if merged["preferredTransport"] not in ("sap-connect", "sap-vsp"):
        raise ValueError(
            f"routingHints.preferredTransport phai la 'sap-connect' hoac 'sap-vsp', nhan duoc: {merged['preferredTransport']!r}"
        )
    if merged["preferredAnalysis"] not in ("sap-vsp", None):
        raise ValueError(
            f"routingHints.preferredAnalysis phai la 'sap-vsp' hoac None, nhan duoc: {merged['preferredAnalysis']!r}"
        )
    return merged


def _upgrade_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Lazy upgrade: doc file v1 -> tra ve dict v2 (khong ghi dia)."""
    out = {**data}
    # Service type luon duoc chuan hoa
    if "service" in out:
        try:
            out["service"] = normalize_service_type(out["service"])
        except ValueError:
            out["service"] = SERVICE_TYPE_DEFAULT
    # routingHints: neu thieu thi dien default theo service
    out["routingHints"] = normalize_routing_hints(out.get("routingHints"), out.get("service", SERVICE_TYPE_DEFAULT))
    # version
    out["version"] = 2
    return out


DEFAULT_CONFIG: dict[str, Any] = {
    "version": 2,
    "btpUrl": "",
    "tenant": "",
    "clientId": "",
    "authMode": "cookie",  # default cho s4hc_(public); override trong save_config theo service type
    "scope": "",
    "routingHints": {  # schema v2 (Phase 2); filled by _default_routing_hints(service)
        "supportsReadonlyClass": True,
        "supportsDebug":         False,
        "supportsVspSlim":       True,
        "supportsVspHealth":     True,
        "supportsDictBridge":    True,
        "preferredTransport":    "sap-connect",
        "preferredAnalysis":     "sap-vsp",
    },
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
        raise RuntimeError("Chua co profile nao. Chay: mcp-sap-connect setup")
    ensure_app_dir()
    file = get_profile_config_file(pid)
    if not file.exists():
        return {**DEFAULT_CONFIG}
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Loi doc {file}: {err}") from err
    # Tu sua config cu thieu scheme (VD luu tu ban truoc khi co fix nay)
    if "btpUrl" in data:
        data["btpUrl"] = normalize_btp_url(data["btpUrl"])
    # Lazy upgrade v1 -> v2 neu can (khong ghi dia o read path)
    if int(data.get("version", 1)) < 2:
        data = _upgrade_v1_to_v2(data)
    return {**DEFAULT_CONFIG, **data}


def save_config(profile_id: str | None, partial: dict[str, Any]) -> dict[str, Any]:
    pid = profile_id or get_current_active()
    if not pid:
        raise RuntimeError("Chua co profile nao. Chay: mcp-sap-connect setup")
    ensure_app_dir()
    file = get_profile_config_file(pid)
    file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    current = load_config(pid) if file.exists() else {**DEFAULT_CONFIG}
    # Doc raw version tu file (load_config tra ve v2 ngay ca khi file v1 -> khong phan biet duoc)
    old_version = 1
    if file.exists():
        try:
            old_version = int(json.loads(file.read_text(encoding="utf-8")).get("version", 1))
        except (json.JSONDecodeError, ValueError):
            old_version = 1
    merged = {**current, **partial}
    # Service type
    if "service" in merged:
        merged["service"] = normalize_service_type(merged["service"])
    # btpUrl scheme
    if "btpUrl" in merged:
        merged["btpUrl"] = normalize_btp_url(merged["btpUrl"])
    # routingHints (validate + dien default neu thieu)
    merged["routingHints"] = normalize_routing_hints(
        merged.get("routingHints"), merged.get("service", SERVICE_TYPE_DEFAULT)
    )
    # Version: bump len v2 khi ghi (lazy upgrade)
    merged["version"] = 2
    # Backup neu file cu dang o v1 (lan dau tien save_config sau khi upgrade)
    backup_path = None
    if file.exists() and old_version < 2:
        backup_path = file.with_name(file.name + ".v1.bak")
        try:
            backup_path.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
            os.chmod(backup_path, 0o600)
        except Exception:
            backup_path = None
    content = json.dumps(merged, ensure_ascii=False, indent=2)
    file.write_text(content, encoding="utf-8")
    mirror_write_text(file, content)
    with contextlib.suppress(Exception):
        os.chmod(file, 0o600)
    return {"id": pid, "config": merged, "upgradedFromV1": backup_path is not None, "backupPath": str(backup_path) if backup_path else None}


def is_configured(profile_id: str | None = None) -> bool:
    try:
        cfg = load_config(profile_id)
        return bool(cfg.get("btpUrl") and cfg.get("clientId"))
    except Exception:
        return False
