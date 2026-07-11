"""Dang ky cac tool MCP cho SAP BTP Agent.

Moi tool nhan tham so `profile` (optional) de chuyen qua lai giua cac project
trong cung 1 phien Claude. Mac dinh lay tu active profile trong registry
hoac env SAP_BTP_PROFILE.
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..config.profile import get_current_active, list_profiles
from ..sap.client import SapClient


def _pick_profile(args: dict[str, Any] | None) -> str | None:
    """Uu tien: env SAP_BTP_PROFILE -> arg.profile -> None (SapClient tu lay active)."""
    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    if env:
        return env
    if args and isinstance(args.get("profile"), str) and args["profile"].strip():
        return args["profile"].strip()
    return None


def _to_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def build_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "sap_ping",
            "description": "Kiem tra ket noi SAP (lay token + goi 1 API nhe). Tra ve OK/FAIL + thong tin profile.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "string",
                        "description": "Profile id (de trong = active). VD: project1.s4hana.cloud.sap",
                    },
                },
            },
            "handler": _handle_ping,
        },
        {
            "name": "sap_list_profiles",
            "description": "Liet ke cac profile SAP da cau hinh (multi-tenant).",
            "inputSchema": {"type": "object", "properties": {}},
            "handler": _handle_list_profiles,
        },
        {
            "name": "sap_list_packages",
            "description": "Liet ke package ABAP trong repository. Mac dinh lay top-level.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string", "description": "Profile id (de trong = active)."},
                    "parent": {"type": "string", "description": "Ten package cha. De rong = top."},
                },
            },
            "handler": _handle_list_packages,
        },
        {
            "name": "sap_search",
            "description": "Tim object ABAP trong repository theo ten.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "query": {"type": "string", "description": "Chuoi tim kiem (VD: ZCL_)"},
                    "objectType": {"type": "string",
                                   "description": "Loc theo loai (CLAS, PROG, ...). De rong = tat ca."},
                },
                "required": ["query"],
            },
            "handler": _handle_search,
        },
        {
            "name": "sap_read_source",
            "description": "Doc source code ABAP (class, program, include...).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "objectUri": {"type": "string",
                                  "description": "URI ADT, VD: /sap/bc/adt/oo/classes/zcl_demo"},
                    "objectType": {"type": "string", "description": "Loai: CLAS, PROG, INCL, FUGR..."},
                },
                "required": ["objectUri", "objectType"],
            },
            "handler": _handle_read_source,
        },
        {
            "name": "sap_syntax_check",
            "description": "Chay syntax check cho 1 object (khong activate).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "objectUri": {"type": "string"},
                    "objectType": {"type": "string", "description": "CLAS, PROG, INCL..."},
                },
                "required": ["objectUri", "objectType"],
            },
            "handler": _handle_syntax_check,
        },
        {
            "name": "sap_activate",
            "description": "Activate object (transport local, khong qua CTS).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "objectUri": {"type": "string"},
                    "objectType": {"type": "string"},
                },
                "required": ["objectUri", "objectType"],
            },
            "handler": _handle_activate,
        },
        # ===== New tools ===========================================
        {
            "name": "sap_find_where_used",
            "description": "Tim noi su dung object ABAP (where-used list). Tra ve danh sach object co tham chieu den object chi dinh.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string", "description": "Profile id (de trong = active)."},
                    "objectName": {"type": "string", "description": "Ten object can tim (VD: ZCL_MY_CLASS, I_SalesDocument...)"},
                    "objectType": {"type": "string", "description": "Loai object (CLAS, PROG, TABL, DDLS...)"},
                },
                "required": ["objectName", "objectType"],
            },
            "handler": _handle_find_where_used,
        },
        {
            "name": "sap_execute_query",
            "description": "Truy van du lieu tu bang / CDS view (data preview). Tra ve top N dong.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "tableName": {"type": "string", "description": "Ten bang / CDS view (VD: I_SalesDocument, MARA, T000)"},
                    "objectType": {"type": "string", "description": "Loai object: TABL (bang), DDLS (CDS view), VIEW (view). Mac dinh TABL.", "default": "TABL"},
                    "top": {"type": "number", "description": "So dong toi da (mac dinh 50, toi da 500).", "default": 50},
                },
                "required": ["tableName"],
            },
            "handler": _handle_execute_query,
        },
        {
            "name": "sap_run_unit_tests",
            "description": "Chay ABAP Unit tests cho 1 class. Tra ve ket qua PASS/FAIL + chi tiet.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "objectUri": {"type": "string", "description": "URI ADT cua class (VD: /sap/bc/adt/oo/classes/zcl_demo)"},
                    "objectType": {"type": "string", "description": "Loai object (CLAS, PROG...)"},
                },
                "required": ["objectUri", "objectType"],
            },
            "handler": _handle_run_unit_tests,
        },
        {
            "name": "sap_get_system_info",
            "description": "Lay thong tin he thong SAP (version SAP_BASIS, release, database, kernel, tenant, region).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                },
            },
            "handler": _handle_get_system_info,
        },
        {
            "name": "sap_analyze_dump",
            "description": "Phan tich ST22 runtime dump. Neu khong co dump_id, lay top dump gan nhat.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "dumpId": {"type": "string", "description": "ID dump cu the (VD: DMP_20250101_123456). De trong = lay dump gan nhat."},
                    "top": {"type": "number", "description": "So dump gan nhat (mac dinh 20). Chi dung khi dumpId de trong.", "default": 20},
                },
            },
            "handler": _handle_analyze_dump,
        },
    ]


# ===== Handlers ====================================================
async def _handle_ping(args: dict[str, Any] | None) -> str:
    pid = _pick_profile(args)
    client = SapClient(pid)
    await client.init()
    try:
        me = await client.get(
            "/sap/bc/adt/repository/informationsystem/search",
            query={"operation": "quickSearch", "query": "ZZZZZZ_NO_MATCH_AAA", "maxResults": 1},
        )
    except Exception as err:
        me = {"error": str(err)}
    profile_id = client.profile_id or get_current_active()
    if isinstance(me, str):
        me = me[:200]
    return _to_json({
        "status": "ok",
        "profile": profile_id,
        "btpUrl": client.config.get("btpUrl"),
        "tenant": client.config.get("tenant"),
        "service": client.config.get("service"),
        "authMode": client.config.get("authMode"),
        "me": me,
    })


async def _handle_list_profiles(_args: dict[str, Any] | None) -> str:
    data = list_profiles()
    return _to_json(data)


async def _handle_list_packages(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.list_packages(args.get("parent") or "")
    return _to_json(data)


async def _handle_search(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.search_objects(args["query"], args.get("objectType") or "")
    return _to_json(data)


async def _handle_read_source(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    src = await client.read_source(args["objectUri"], args["objectType"])
    return src if isinstance(src, str) else _to_json(src)


async def _handle_syntax_check(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.syntax_check(args["objectUri"], args["objectType"])
    return _to_json(data)


async def _handle_activate(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.activate(args["objectUri"], args["objectType"])
    return _to_json(data)


# ===== New tools ===================================================

async def _handle_find_where_used(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.find_where_used(args["objectName"], args["objectType"])
    return _to_json(data)


async def _handle_execute_query(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    top = min(int(args.get("top", 50) or 50), 500)
    object_type = (args.get("objectType") or "TABL").strip()
    data = await client.execute_query(args["tableName"], object_type=object_type, top=top)
    return _to_json(data)


async def _handle_run_unit_tests(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.run_unit_tests(args["objectUri"], args["objectType"])
    return _to_json(data)


async def _handle_get_system_info(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    data = await client.get_system_info()
    return _to_json(data)


async def _handle_analyze_dump(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    dump_id = (args.get("dumpId") or "").strip()
    top = min(int(args.get("top", 20) or 20), 100)
    data = await client.analyze_dump(dump_id=dump_id or None, top=top)
    return _to_json(data)
