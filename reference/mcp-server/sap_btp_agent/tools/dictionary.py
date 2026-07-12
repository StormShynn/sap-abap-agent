"""
ADT Dictionary Bridge — Tao Domain, Data Element, Database Table
bang cookie auth tu sap-btp-agent (SapClient).

Thay vi dung fr0ster/mcp-abap-adt (can basic auth), module nay goi truc tiep
ADT REST API thong qua SapClient da co cookie auth + auto re-auth (browser popup).

Dinh dang:
  - Domain:  define domain <name> { type <type>; value range: ... }
  - Data Element: define data element <name> { type <type|domain>; }
  - Table:   define table <name> { key client ...; key uuid ...; ... }

ADT Workflow (lock -> create/update source -> activate -> unlock):
  POST /sap/bc/adt/locks?type={type}&name={name}  -> lockHandle
  PUT  /sap/bc/adt/ddic/{type}/{name}/source/main  -> DDL source
  POST /sap/bc/adt/activation                       -> activate
  DELETE /sap/bc/adt/locks/{lockHandle}              -> unlock
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..config.profile import get_current_active
from ..sap.client import SapClient

DDIC_TYPE_MAP = {
    "domain": "DOMA",
    "dataelement": "DTEL",
    "table": "TABL",
}


def _pick_profile(args: dict[str, Any] | None) -> str | None:
    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    if env:
        return env
    if args and isinstance(args.get("profile"), str) and args["profile"].strip():
        return args["profile"].strip()
    return None


def _to_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ===== ADT XML Payload builders ====================================

def _build_domain_ddl(name: str, label: str, data_type: str,
                       fixed_values: list[dict[str, str]] | None = None) -> str:
    """Xay dung DDL source cho Domain: define domain <name> { ... }"""
    lines = []
    lines.append("@EndUserText.label : '" + label + "'")
    lines.append("define domain " + name + " {")
    lines.append("  type " + data_type + ";")
    if fixed_values:
        lines.append("  value range:")
        for i, fv in enumerate(fixed_values):
            comma = "," if i < len(fixed_values) - 1 else ";"
            val = fv.get("value", "")
            lbl = fv.get("label", "")
            lines.append("    '" + val + "' : '" + lbl + "'" + comma)
    lines.append("}")
    return "\n".join(lines) + "\n"


def _build_data_element_ddl(name: str, label: str, data_type_or_domain: str) -> str:
    """Xay dung DDL source cho Data Element: define data element <name> { ... }"""
    lines = []
    lines.append("@EndUserText.label : '" + label + "'")
    lines.append("@DataClassification.level : #BUSINESS_INFORMATION")
    lines.append("define data element " + name + " {")
    lines.append("  type " + data_type_or_domain + ";")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _build_table_ddl(name: str, label: str, fields: list[dict[str, str]]) -> str:
    """Xay dung DDL source cho Database Table: define table <name> { ... }"""
    lines = []
    lines.append("@EndUserText.label : '" + label + "'")
    lines.append("@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE")
    lines.append("@AbapCatalog.tableCategory : #TRANSPARENT")
    lines.append("@AbapCatalog.deliveryClass : #A")
    lines.append("@AbapCatalog.dataMaintenance : #RESTRICTED")
    lines.append("define table " + name + " {")

    for f in fields:
        f_name = f.get("name", "").strip()
        f_type = f.get("type", "")
        f_key = f.get("key", "false") == "true"
        f_not_null = f.get("notNull", "false") == "true"

        # "key" la nguon su that duy nhat cho tu khoa DDL — bo tien to "key "
        # neu ten da go san (tuong thich nguoc voi field mac dinh ben duoi),
        # roi tu quyet dinh co them lai dua vao f_key, tranh truong hop
        # key=true nhung ten khong co "key " bi sinh ra thanh field thuong.
        if f_name.lower().startswith("key "):
            f_name = f_name[4:].strip()

        col = "  key " + f_name if f_key else "  " + f_name
        col += " : " + f_type
        if f_key and f_not_null:
            col += " not null"
        col += ";"

        lines.append(col)

    # Them admin fields neu chua co
    has_admin = any(f.get("name", "").lower() in [
        "created_by", "created_at", "last_changed_by", "last_changed_at"
    ] for f in fields)
    if not has_admin:
        lines.append("  created_by          : abp_creation_user;")
        lines.append("  created_at          : abp_creation_tstmpl;")
        lines.append("  last_changed_by     : abp_locinst_lastchange_user;")
        lines.append("  last_changed_at     : abp_locinst_lastchange_tstmpl;")

    lines.append("}")
    return "\n".join(lines) + "\n"


# ===== Dict CRUD methods ===========================================

async def _create_ddic_object(
    client: SapClient,
    obj_type: str,       # "domain", "dataelement", "table"
    obj_name: str,
    ddl_source: str,
) -> dict[str, Any]:
    """
    ADT workflow: lock -> PUT source -> activate -> unlock.

    Returns dict voi ket qua.
    """
    ddic_type = DDIC_TYPE_MAP.get(obj_type)
    if not ddic_type:
        raise ValueError(f"Unknown DDIC type: {obj_type}")

    base_url = client._adt_base()
    result: dict[str, Any] = {"status": "unknown"}

    # 1. Lock object
    try:
        lock_resp = await client.post(
            f"/sap/bc/adt/locks?type={ddic_type}&name={obj_name.upper()}",
            headers={"x-csrf-token": "fetch"},
        )
        lock_handle = None
        if isinstance(lock_resp, dict):
            lock_handle = lock_resp.get("lockHandle") or lock_resp.get("handle")
        result["lock"] = "ok"
        result["lock_handle"] = lock_handle
    except Exception as e:
        return {"status": "error", "step": "lock", "error": str(e)}        # 2. PUT source (DDL)
    try:
        source_path = f"/sap/bc/adt/ddic/{obj_type}s/{obj_name.lower()}/source/main"
        source_resp = await client.put(
            source_path,
            body=ddl_source,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "x-csrf-token": "fetch",
            },
            is_json=False,
        )
        result["source"] = "ok"
    except Exception as e:
        result["source_error"] = str(e)
        # Tiep tuc activate (co the object da ton tai)

    # 3. Activate
    try:
        act_resp = await client.post(
            "/sap/bc/adt/activation",
            body={
                "objectUri": f"/sap/bc/adt/ddic/{obj_type}s/{obj_name.lower()}",
                "objectType": ddic_type,
                "transport": "",
            },
            headers={"x-csrf-token": "fetch"},
        )
        result["activate"] = "ok"
        if isinstance(act_resp, dict):
            result["activate_detail"] = act_resp.get("messages", act_resp)
    except Exception as e:
        result["activate_error"] = str(e)

    # 4. Unlock
    if lock_handle:
        try:
            unlock_resp = await client.delete(
                f"/sap/bc/adt/locks/{lock_handle}",
                is_json=False,
            )
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

    # Xac dinh status tong the
    if result.get("activate") == "ok":
        result["status"] = "success"
    elif result.get("source") == "ok":
        result["status"] = "partial"
    else:
        result["status"] = "error"

    return result


# ===== Tool Handlers ===============================================

async def _handle_create_domain(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten domain). VD: ZDOM_STATUS"})

    label = args.get("label", name)
    data_type = args.get("type", "abap.char( 1 )")
    fixed_values = args.get("fixedValues") or args.get("values")

    ddl = _build_domain_ddl(name, label, data_type, fixed_values)
    result = await _create_ddic_object(client, "domain", name, ddl)
    result["ddl"] = ddl
    return _to_json(result)


async def _handle_create_data_element(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten data element). VD: ZDE_STATUS"})

    label = args.get("label", name)
    data_type_or_domain = args.get("type", "abap.char( 40 )")

    ddl = _build_data_element_ddl(name, label, data_type_or_domain)
    result = await _create_ddic_object(client, "dataelement", name, ddl)
    result["ddl"] = ddl
    return _to_json(result)


async def _handle_create_table(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten table). VD: ZTB_HEADER"})

    label = args.get("label", name)
    fields = args.get("fields", [])

    if not fields:
        # Tao table mac dinh voi key + uuid + admin fields
        fields = [
            {"name": "key client", "type": "abap.clnt", "key": "true", "notNull": "true"},
            {"name": "key uuid", "type": "sysuuid_x16", "key": "true", "notNull": "true"},
        ]

    ddl = _build_table_ddl(name, label, fields)
    result = await _create_ddic_object(client, "table", name, ddl)
    result["ddl"] = ddl
    return _to_json(result)


# ===== Tool Registration ===========================================

def build_dict_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "sap_create_domain",
            "description": "Tao Domain ABAP Cloud (define domain ...). Dung cookie auth sap-btp-agent.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string", "description": "Profile id (de trong = active)."},
                    "name": {"type": "string", "description": "Ten domain. VD: ZDOM_STATUS"},
                    "label": {"type": "string", "description": "Mo ta (EndUserText.label)."},
                    "type": {"type": "string", "description": "Kieu du lieu. VD: abap.char(1), abap.int4, abap.dec(16,2). Mac dinh: abap.char(1)."},
                    "fixedValues": {
                        "type": "array",
                        "description": "Danh sach fixed values: [{\"value\":\"A\",\"label\":\"Active\"}, ...]",
                        "items": {
                            "type": "object",
                            "properties": {
                                "value": {"type": "string"},
                                "label": {"type": "string"},
                            },
                        },
                    },
                },
                "required": ["name"],
            },
            "handler": _handle_create_domain,
        },
        {
            "name": "sap_create_data_element",
            "description": "Tao Data Element ABAP Cloud (define data element ...). Dung cookie auth sap-btp-agent.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten data element. VD: ZDE_STATUS"},
                    "label": {"type": "string", "description": "Mo ta (EndUserText.label)."},
                    "type": {"type": "string", "description": "Kieu hoac domain. VD: zdom_status, abap.char(40), abap.int4. Mac dinh: abap.char(40)."},
                },
                "required": ["name"],
            },
            "handler": _handle_create_data_element,
        },
        {
            "name": "sap_create_table",
            "description": "Tao Database Table ABAP Cloud (define table ...). Dung cookie auth sap-btp-agent. Tu dong them admin fields (created_by, created_at...) neu thieu.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten table. VD: ZTB_HEADER"},
                    "label": {"type": "string", "description": "Mo ta table."},
                    "fields": {
                        "type": "array",
                        "description": "Danh sach field (de trong = key + uuid mac dinh).",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Ten field, co the co 'key' prefix. VD: 'key client', 'name', 'status'"},
                                "type": {"type": "string", "description": "Kieu. VD: abap.clnt, sysuuid_x16, zde_status, abap.char(100)"},
                                "key": {"type": "string", "description": "'true' neu la key field"},
                                "notNull": {"type": "string", "description": "'true' neu not null"},
                            },
                        },
                    },
                },
                "required": ["name"],
            },
            "handler": _handle_create_table,
        },
    ]
