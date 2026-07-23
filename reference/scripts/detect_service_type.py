#!/usr/bin/env python3
"""Xac dinh service type (edition) cua profile sap-btp-agent dang active - KHONG goi MCP.

Doc truc tiep profiles/<id>/config.json (field "service", vd s4hc_(private)/s4hc_(public)/
btp/onprem) thay vi goi tool sap_ping de suy ra edition - re hon (khong round-trip mang qua
he thong SAP that), khong phu thuoc he thong dang song hay khong, va an toan: config.json
KHONG chua secret (secret nam rieng o secrets.json - script nay khong dong vao file do).

Vi sao can file nay: cac skill (sap-ask-consultant, sap-extensibility, sap-clean-code,
sap-abap-sql...) tra loi khac nhau rat nhieu theo edition (vd Public Edition cam SELECT bang
chuan - phai qua CDS/API released; onprem/Private thi duoc SELECT truc tiep) nhung truoc gio
khong skill nao doc field "service" da co san trong config nay - mac dinh coi nhu Public
Edition. Script nay la buoc "do offline" dau tien de skill sap-service-type-context xac dinh
dung ngu canh truoc khi tra loi, tranh hoi lai user neu da co san.

Thu tu resolve profile active (dung y het
reference/mcp-server/sap_btp_agent/config/{paths,profile}.py - xem file do neu can doi chieu):
    1. --profile <id> (tham so dong lenh, ep cu the)
    2. Env SAP_BTP_PROFILE (uu tien cao nhat neu khong truyen --profile)
    3. registry profiles.json -> field "active"
    4. Khong co profile nao -> source = "not_configured"

Sau khi co profile id, doc profiles/<id>/config.json:
    - Co field "service" hop le (nam trong SERVICE_TYPES, sau khi alias) -> source = "config"
      (dang tin duoc, KHONG can hoi lai user)
    - File ton tai nhung thieu/rong/sai "service" -> source = "config_default" (day chi la gia
      tri fallback, CHUA chac user da tung xac nhan - nen hoi lai)
    - Khong tim thay profile dir / config.json -> source = "not_configured" (vd workflow
      abapgit-local thuan, hoac dung MCP ADT khac ngoai sap-btp-agent - phai hoi thang user)

Output: 1 khoi JSON ra stdout, vd:
    {
      "profile": "project1.s4hana.cloud.sap",
      "service": "s4hc_(public)",
      "source": "config",
      "configPath": "C:\\Users\\xxx\\.sap-btp-agent\\profiles\\project1.s4hana.cloud.sap\\config.json",
      "note": null
    }

Quy tac cho skill goi script nay (xem skills/sap-service-type-context/SKILL.md):
    - source == "config"           -> dung gia tri "service", KHONG hoi lai user.
    - source == "config_default"   -> hoi user xac nhan lai truoc khi dung.
    - source == "not_configured"   -> hoi thang user (taxonomy 4 nhanh), khong tu doan.

KHONG bao gio doc secrets.json duoi bat ky truong hop nao.

Dung tu SKILL.md:
    python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/detect_service_type.py"
    python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/detect_service_type.py" --profile project1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

APP_DIR_NAME = ".sap-btp-agent"

# Phai khop 100% voi reference/mcp-server/sap_btp_agent/config/store.py
# (SERVICE_TYPES / SERVICE_TYPE_ALIASES). Day la ban DOC-ONLY, khong import package
# sap_btp_agent de tranh phu thuoc package do phai pip-install/import duoc tu noi script
# nay chay (reference/scripts/ la stdlib-only, chay ad hoc qua Bash tool).
SERVICE_TYPES = ("s4hc_(private)", "s4hc_(public)", "btp", "onprem")
SERVICE_TYPE_ALIASES = {"s4hc": "s4hc_(public)"}


def _get_app_dir() -> Path:
    override = os.environ.get("SAP_BTP_AGENT_HOME", "").strip()
    if override:
        return Path(override).resolve()
    return Path.home() / APP_DIR_NAME


def _resolve_active_profile(explicit: str | None) -> tuple[str | None, str]:
    """Tra ve (profile_id hoac None, ly do/nguon resolve - chi de debug)."""
    if explicit:
        return explicit, "arg --profile"

    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    if env:
        return env, "env SAP_BTP_PROFILE"

    registry_file = _get_app_dir() / "profiles.json"
    if not registry_file.exists():
        return None, "khong co profiles.json (chua tung chay 'sap-btp-agent setup')"
    try:
        data = json.loads(registry_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        return None, f"loi doc profiles.json: {err}"

    active = data.get("active")
    if not active:
        return None, "profiles.json khong co profile active nao"
    return active, "profiles.json.active"


def detect(explicit_profile: str | None = None) -> dict[str, Any]:
    profile_id, resolved_from = _resolve_active_profile(explicit_profile)
    if not profile_id:
        return {
            "profile": None,
            "service": None,
            "source": "not_configured",
            "configPath": None,
            "note": f"Khong xac dinh duoc profile dang active ({resolved_from}).",
        }

    config_path = _get_app_dir() / "profiles" / profile_id / "config.json"
    if not config_path.exists():
        return {
            "profile": profile_id,
            "service": None,
            "source": "not_configured",
            "configPath": str(config_path),
            "note": "Profile co trong registry nhung khong tim thay config.json tuong ung.",
        }

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        return {
            "profile": profile_id,
            "service": None,
            "source": "not_configured",
            "configPath": str(config_path),
            "note": f"Loi doc config.json: {err}",
        }

    raw_service = str(config.get("service") or "").strip()
    if not raw_service:
        return {
            "profile": profile_id,
            "service": None,
            "source": "config_default",
            "configPath": str(config_path),
            "note": "config.json khong co field 'service' - chua tung duoc user xac nhan that.",
        }

    normalized = SERVICE_TYPE_ALIASES.get(raw_service, raw_service)
    if normalized not in SERVICE_TYPES:
        return {
            "profile": profile_id,
            "service": None,
            "source": "config_default",
            "configPath": str(config_path),
            "note": f"Gia tri 'service' khong hop le trong config.json: {raw_service!r}.",
        }

    return {
        "profile": profile_id,
        "service": normalized,
        "source": "config",
        "configPath": str(config_path),
        "note": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--profile", default=None, help="Ep 1 profile id cu the (mac dinh: profile active)")
    args = parser.parse_args()
    print(json.dumps(detect(args.profile), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
