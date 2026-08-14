#!/usr/bin/env python3
"""SessionStart hook: phat hien lan dau dung plugin (chua co profile SAP nao cau hinh),
goi y Claude chu dong hoi user ve `/sap-setup` thay vi im lang cho user tu biet go lenh.

Chi kiem tra OFFLINE (khong goi MCP, khong dong mang) - doc thu muc profiles cua
mcp-sap-connect qua `mcp_sap_connect.config.paths.get_profiles_dir()` (neu package da cai vao
Python dang chay hook nay). Neu package CHUA cai (ImportError) hoac thu muc profiles rong ->
coi la lan dau, bom 1 doan goi y ngan vao context cua phien. Neu da co it nhat 1 profile -> im
lang (exit 0, khong output) de KHONG lam phien user cu moi lan mo phien.

Luu y: day la heuristic best-effort (co the sai neu user co nhieu Python interpreter va
mcp-sap-connect cai o 1 ban khac voi `python` dang chay hook nay) - vi vay noi dung goi y luon
noi Claude CHI hoi 1 lan, khong hoi lai neu user tu choi trong cung phien.
"""
from __future__ import annotations

import json
import sys


def _has_any_profile() -> bool:
    try:
        from mcp_sap_connect.config.paths import get_profiles_dir
    except ImportError:
        return False  # package chua cai vao Python nay -> chac chan chua tung setup qua day

    try:
        profiles_dir = get_profiles_dir()
        return profiles_dir.is_dir() and any(profiles_dir.iterdir())
    except OSError:
        # Khong doc duoc thu muc (quyen/duong dan la) -> an toan hon la coi nhu chua setup,
        # de Claude hoi 1 lan thay vi im lang sai neu thuc su chua setup.
        return False


def main() -> int:
    if _has_any_profile():
        return 0  # da setup roi (co it nhat 1 profile) -> im lang, khong lam phien user cu

    message = (
        "[sap-abap-agent] Chua phat hien profile SAP nao duoc cau hinh tren may nay (hoac "
        "package mcp-sap-connect chua cai vao Python dang dung). Neu day co ve la lan dau user "
        "dung plugin nay: CHU DONG hoi ngay dau phien (dung 1 lan, KHONG hoi lai trong cung "
        "phien neu user tu choi hoac dang ban viec khac) — \"Co ve day la lan dau ban dung "
        "plugin sap-abap-agent tren may nay - ban co muon toi chay /sap-setup de cai dat (pip "
        "install mcp-sap-connect, tao profile SAP dau tien, dang ky MCP servers voi Claude "
        "Code) khong?\". Day chi la goi y offline (co the sai neu mcp-sap-connect da cai o 1 "
        "Python khac) - neu user noi da setup roi, tin loi user, khong tranh cai."
    )
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
