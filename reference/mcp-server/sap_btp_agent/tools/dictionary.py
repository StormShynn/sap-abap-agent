"""
ADT Dictionary Bridge — Tao Domain, Data Element, Database Table, CDS View,
Service Definition, Service Binding bang cookie auth tu sap-btp-agent (SapClient).

Thay vi dung fr0ster/mcp-abap-adt (can basic auth), module nay goi truc tiep
ADT REST API thong qua SapClient da co cookie auth + auto re-auth (browser popup).

Dinh dang:
  - Domain:  define domain <name> { type <type>; value range: ... }
  - Data Element: define data element <name> { type <type|domain>; }
  - Table:   define table <name> { key client ...; key uuid ...; ... }
  - CDS View (DDLS): DDL source (@AbapCatalog..., define view entity ...)
  - Service Definition (SRVD): DDL source (define service ...) - tu viet, khong
    co generator san (giong ben nguon tham khao - xem duoi)
  - Service Binding (SRVB): khong co source, toan bo khai bao nam trong XML tao

ADT Workflow day du (CDS/SRVD, port tu vibing-steampunk crud.go - xem ghi chu
tung ham): CREATE (POST object + package) -> lock -> PUT source -> UNLOCK
-> activate. Truoc day module nay THIEU han buoc CREATE (chi lam duoc
lock->PUT->activate->unlock), nen khong tao duoc object MOI + khong gan duoc
dung package - chi hoat dong voi object da ton tai san. Domain/DataElement
VAN CON thieu buoc CREATE nay (chua tim duoc XML schema chuan cho 2 loai do o
nguon tham khao - xem _handle_create_domain/_handle_create_data_element).

Nguon tham khao (cung tac gia, da xac nhan hoat dong that): doc truc tiep
github.com/StormShynn/vibing-steampunk (Go) pkg/adt/crud.go + devtools.go.
Endpoint/XML cho DDLS/SRVD/SRVB/Table la doc source that, KHONG suy doan -
xem comment tai tung noi dung de biet dong/ham nguon.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from ..config.profile import get_current_active
from ..sap.client import SapClient

DDIC_TYPE_MAP = {
    "domain": "DOMA",
    "dataelement": "DTEL",
    "table": "TABL",
}

# ===== Registry object "chuan" (Program/Class/DDLS/SRVD...) ================
# Nguon: vibing-steampunk pkg/adt/crud.go, map `objectTypes` (dong 234-291) -
# doc truc tiep, da xac nhan tung truong. domain/dataelement KHONG co trong
# registry nay vi KHONG ton tai trong repo nguon (ho khong ho tro 2 loai do).
STANDARD_OBJECT_TYPES: dict[str, dict[str, str]] = {
    "ddls": {
        "type_code": "DDLS/DF",
        "creation_path": "/sap/bc/adt/ddic/ddl/sources",
        "root_name": "ddl:ddlSource",
        "namespace": 'xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources"',
    },
    "srvd": {
        "type_code": "SRVD/SRV",
        "creation_path": "/sap/bc/adt/ddic/srvd/sources",
        "root_name": "srvd:srvdSource",
        "namespace": 'xmlns:srvd="http://www.sap.com/adt/ddic/srvdsources"',
        "extra_root_attr": ' srvd:srvdSourceType="S"',
    },
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


def _xml_escape(text: str) -> str:
    """Escape ky tu XML dac biet trong attribute value (& < > " ')."""
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


async def _fetch_package_xml(client: SapClient, package: str) -> str | None:
    """Doc XML metadata cua 1 package qua ADT. Tra ve None neu khong doc duoc
    (khong ton tai, loi mang, hoac response khong phai text)."""
    try:
        result = await client.get(
            f"/sap/bc/adt/packages/{package.lower()}",
            headers={"Accept": "application/xml"},
            allow_404=True,
            is_json=False,
        )
    except Exception:
        return None
    return result if isinstance(result, str) else None


async def _package_superpackage(client: SapClient, package: str) -> str | None:
    """Lay ten superpackage (package cha) tu XML metadata cua 1 package.

    [Unverified] Ten attribute "superPackage" suy tu XML TAO package (da xac
    nhan tu vibing-steampunk crud.go dong 692-693: <pack:superPackage
    adtcore:name="..."/>), nhung CHUA kiem chung day co dung la format ADT
    tra ve khi GET/doc (khac voi POST/tao) hay khong. Neu regex khong khop,
    tra ve None (an toan hon - _package_is_local se roi vao nhanh CHAN).
    """
    xml_text = await _fetch_package_xml(client, package)
    if not xml_text:
        return None
    m = re.search(r'superPackage[^>]*\bname="([^"]+)"', xml_text)
    return m.group(1) if m else None


async def _package_is_local(client: SapClient, package: str) -> bool:
    """True neu package nay la local ($ prefix) HOAC la sub-package (truc tiep
    hay qua nhieu cap) cua 1 package cha local - nguoi dung xac nhan truong
    hop nay xay ra that (vd "ZSD09_TEST la package con nam trong package cha
    LOCAL", 2026-07-17), nen chi check ten package tu than la khong du.

    Di nguoc chuoi superpackage toi da 10 buoc (tranh vong lap vo han neu du
    lieu la/loop). Loi/khong xac dinh duoc o buoc nao -> dung lai, tra ve False
    (an toan hon: coi nhu KHONG local, roi vao nhanh CHAN, thay vi false
    positive cho phep ghi nham).
    """
    seen: set[str] = set()
    current = package
    for _ in range(10):
        if current.startswith("$"):
            return True
        if current in seen:
            break
        seen.add(current)
        parent = await _package_superpackage(client, current)
        if not parent:
            break
        current = parent
    return False


async def _check_transportable_edit(client: SapClient, package: str) -> str | None:
    """CHAN TUYET DOI tao/sua object trong package khong "local" - "local" gio
    tinh ca sub-package cua 1 package cha local (xem _package_is_local), khong
    chi rieng ten bat dau bang "$".

    Theo yeu cau nguoi dung (2026-07-17): moi tool tao object trong module nay
    CHI duoc phep ghi vao package local - khong co co che opt-in/env var nao
    de vuot qua rao nay (khac ban dau port tu vibing-steampunk co cho
    SAP_BTP_AGENT_ALLOW_TRANSPORTABLE_EDITS lam co che bat lai - da bo, vi he
    thong dang thao tac la he thong that cua Nafoods, khong phai sandbox).
    Muon ghi vao package that (transportable) phai sua code nay tuong minh,
    khong duoc bat qua bien moi truong. Tra ve None neu OK (package local),
    hoac thong bao loi neu bi chan.
    """
    if await _package_is_local(client, package):
        return None
    return (
        f"Bi chan: chi cho phep tao object trong package local ($TMP/$*, hoac "
        f"sub-package cua 1 package cha local) - '{package}' khong xac dinh duoc "
        "la thuoc dien nay. Day la gioi han CO CHU DICH (khong co env var nao "
        "de bat qua) de tranh ghi nham vao he thong that."
    )


async def _package_exists(client: SapClient, package: str) -> bool:
    """Kiem tra package da ton tai truoc khi tao object trong do.

    Nguon: vibing-steampunk crud.go dong 595-604, comment nguyen van: "SAP ADT
    tao ENQUEUE lock NOI BO truoc khi validate request - neu package khong ton
    tai, SAP fail nhung de lai lock mo côi, chi xoa duoc qua transaction SM12".
    Check truoc giup tranh hoan toan tinh huong nay tren he thong that.
    """
    if package.startswith("$"):
        return True  # package local ($TMP...) luon ton tai san, khoi can check
    try:
        result = await client.get(f"/sap/bc/adt/packages/{package.lower()}", allow_404=True)
        return result is not None
    except Exception:
        # Khong chan tao chi vi check nay loi (vd endpoint khac ten tren 1 so
        # he thong) - de buoc create that quyet dinh, tranh false negative.
        return True


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
    obj_type: str,       # "domain", "dataelement"
    obj_name: str,
    ddl_source: str,
) -> dict[str, Any]:
    """
    ADT workflow: lock -> PUT source -> UNLOCK -> activate.

    CHUA co buoc "create object + gan package" (POST truoc lock) - domain/
    dataelement khong nam trong nguon tham khao vibing-steampunk (ho khong ho
    tro 2 loai nay) nen chua xac dinh duoc XML schema/namespace chuan de tao
    moi. Ham nay VI VAY chi hoat dong voi object DA TON TAI SAN (ghi de source),
    khong tao moi + khong gan package duoc - xem "warning" trong ket qua tra ve.

    Thu tu unlock TRUOC activate (khong phai sau) - sua theo dung thu tu da
    xac nhan hoat dong trong vibing-steampunk (crud.go CreateTable dong
    1228-1234: "Unlock BEFORE activation").

    Returns dict voi ket qua.
    """
    ddic_type = DDIC_TYPE_MAP.get(obj_type)
    if not ddic_type:
        raise ValueError(f"Unknown DDIC type: {obj_type}")

    result: dict[str, Any] = {
        "status": "unknown",
        "warning": (
            f"Tool nay CHUA co buoc tao object moi + gan package cho '{obj_type}' "
            "(gap chua tim duoc XML schema chuan tu nguon tham khao) - chi ghi de "
            "duoc source neu object DA TON TAI SAN trong he thong."
        ),
    }
    lock_handle = None

    # 1. Lock object
    try:
        lock_resp = await client.post(
            f"/sap/bc/adt/locks?type={ddic_type}&name={obj_name.upper()}",
            headers={"x-csrf-token": "fetch"},
        )
        if isinstance(lock_resp, dict):
            lock_handle = lock_resp.get("lockHandle") or lock_resp.get("handle")
        result["lock"] = "ok"
        result["lock_handle"] = lock_handle
    except Exception as e:
        result["status"] = "error"
        result["step"] = "lock"
        result["error"] = str(e)
        return result

    # 2. PUT source (DDL)
    try:
        source_path = f"/sap/bc/adt/ddic/{obj_type}s/{obj_name.lower()}/source/main"
        await client.put(
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
        # Tiep tuc: van thu unlock + activate (object co the da co source cu)

    # 3. Unlock (TRUOC activate)
    if lock_handle:
        try:
            await client.delete(f"/sap/bc/adt/locks/{lock_handle}", is_json=False)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

    # 4. Activate
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

    # Xac dinh status tong the
    if result.get("activate") == "ok":
        result["status"] = "success"
    elif result.get("source") == "ok":
        result["status"] = "partial"
    else:
        result["status"] = "error"

    return result


async def _create_table_object(
    client: SapClient,
    obj_name: str,
    label: str,
    ddl_source: str,
    package: str,
    transport: str,
) -> dict[str, Any]:
    """Tao Database Table MOI, dung endpoint/content-type RIENG cua Table
    (khac han DDLS/SRVD) - port nguyen ven tu vibing-steampunk crud.go
    CreateTable() dong 1150-1237 (doc source that, khong suy doan).

    Workflow: check safety+package -> CREATE (POST blue:blueSource) -> lock
    -> PUT source (Content-Type "text/plain", KHONG co ";charset=utf-8") ->
    UNLOCK -> activate. Day la diem KHAC voi _create_ddic_object: Table co
    buoc CREATE rieng (con domain/dataelement thi chua).
    """
    result: dict[str, Any] = {"status": "unknown"}

    safety_err = await _check_transportable_edit(client, package)
    if safety_err:
        result["status"] = "blocked"
        result["error"] = safety_err
        return result

    if not await _package_exists(client, package):
        result["status"] = "error"
        result["step"] = "package_check"
        result["error"] = (
            f"Package '{package}' khong ton tai - tao package truoc de tranh ADT "
            "de lai lock mo coi (chi xoa duoc qua SM12)."
        )
        return result

    table_path = "/sap/bc/adt/ddic/tables"
    table_url = f"{table_path}/{obj_name.lower()}"
    source_url = f"{table_url}/source/main"

    # 1. Create table object (gan package ngay trong XML nay)
    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"\n'
        '                 xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'                 adtcore:name="{obj_name}"\n'
        '                 adtcore:type="TABL/DT"\n'
        f'                 adtcore:description="{_xml_escape(label)}">\n'
        f'  <adtcore:packageRef adtcore:name="{package}"/>\n'
        '</blue:blueSource>'
    )
    try:
        await client.post(
            table_path,
            body=create_xml,
            query={"corrNr": transport} if transport else None,
            headers={
                "Content-Type": "application/vnd.sap.adt.tables.v2+xml",
                "Accept": "application/vnd.sap.adt.tables.v2+xml",
            },
            is_json=False,
        )
        result["create"] = "ok"
    except Exception as e:
        result["status"] = "error"
        result["step"] = "create"
        result["error"] = str(e)
        return result

    # 2. Lock
    lock_handle = None
    try:
        lock_resp = await client.post(
            f"/sap/bc/adt/locks?type=TABL&name={obj_name}",
            headers={"x-csrf-token": "fetch"},
        )
        if isinstance(lock_resp, dict):
            lock_handle = lock_resp.get("lockHandle") or lock_resp.get("handle")
        result["lock"] = "ok"
    except Exception as e:
        result["status"] = "partial"
        result["step"] = "lock"
        result["error"] = str(e)
        return result

    # 3. PUT source (Content-Type "text/plain" - KHONG "; charset=utf-8", khac
    # voi domain/dataelement - dung dung header vibing-steampunk dung)
    try:
        await client.put(
            source_url,
            body=ddl_source,
            query={"lockHandle": lock_handle, **({"corrNr": transport} if transport else {})},
            headers={"Content-Type": "text/plain", "x-csrf-token": "fetch"},
            is_json=False,
        )
        result["source"] = "ok"
    except Exception as e:
        result["source_error"] = str(e)

    # 4. Unlock TRUOC activate
    if lock_handle:
        try:
            await client.delete(f"/sap/bc/adt/locks/{lock_handle}", is_json=False)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

    # 5. Activate
    try:
        act_resp = await client.post(
            "/sap/bc/adt/activation",
            body={"objectUri": table_url, "objectType": "TABL", "transport": transport},
            headers={"x-csrf-token": "fetch"},
        )
        result["activate"] = "ok"
        if isinstance(act_resp, dict):
            result["activate_detail"] = act_resp.get("messages", act_resp)
    except Exception as e:
        result["activate_error"] = str(e)

    result["status"] = "success" if result.get("activate") == "ok" else (
        "partial" if result.get("source") == "ok" else "error"
    )
    return result


async def _create_standard_object(
    client: SapClient,
    type_key: str,        # key trong STANDARD_OBJECT_TYPES: "ddls" | "srvd"
    obj_name: str,
    label: str,
    ddl_source: str,
    package: str,
    transport: str,
    responsible: str = "",
) -> dict[str, Any]:
    """Tao object theo mau "chuan" (CDS View/Service Definition) - port tu
    vibing-steampunk crud.go: buildCreateObjectBody() nhanh standard (dong
    819-834) + CreateObject()/objectTypes map (dong 234-291, 558-667).

    Workflow: check safety+package -> CREATE (POST + packageRef) -> lock ->
    PUT source -> UNLOCK -> activate.
    """
    info = STANDARD_OBJECT_TYPES[type_key]
    result: dict[str, Any] = {"status": "unknown"}
    # Ban dau port sai: de trong ("") - vibing-steampunk (crud.go dong 613-616)
    # LUON dien mot username that (config hien tai, fallback "DDIC" neu khong
    # co) chu KHONG BAO GIO de trong. [Inference] day la nghi van chinh cho loi
    # 400 ExceptionInvalidData "Check of condition failed" gap phai lan dau -
    # SAP co the require adtcore:responsible la 1 user hop le, khong chap nhan
    # chuoi rong. Chua kiem chung 100% (chua test lai), nhung sua theo dung
    # pattern nguon tham khao la huong hop ly nhat.
    responsible_value = (responsible or "").strip() or "DDIC"

    safety_err = await _check_transportable_edit(client, package)
    if safety_err:
        result["status"] = "blocked"
        result["error"] = safety_err
        return result

    if not await _package_exists(client, package):
        result["status"] = "error"
        result["step"] = "package_check"
        result["error"] = (
            f"Package '{package}' khong ton tai - tao package truoc de tranh ADT "
            "de lai lock mo coi (chi xoa duoc qua SM12)."
        )
        return result

    name_lower = obj_name.lower()
    object_url = f"{info['creation_path']}/{name_lower}"
    source_url = f"{object_url}/source/main"
    root = info["root_name"]
    extra_attr = info.get("extra_root_attr", "")

    # 1. Create object (gan package ngay trong XML nay)
    # [Inference, 2026-07-17] Fallback responsible="DDIC" da RETEST that tren
    # my440301 (ca ZI_SD09_SALES_ORDERS day du lan 1 view toi gian chi 2
    # field) - VAN FAIL 400 "Check of condition failed" dung XML_PATH goc
    # ddl:ddlSource(1). Nghi van moi: thieu adtcore:masterLanguage - attribute
    # ADT thuong bat buoc khi tao moi DDLS/SRVD, thieu de gay dung loai loi
    # chung chung nay o root element. Gia tri "E" lay tu .abapgit cua chinh
    # project (master_language: "E"). CHUA kiem chung - can test lai.
    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<{root} {info["namespace"]} xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'  adtcore:description="{_xml_escape(label)}"\n'
        f'  adtcore:name="{obj_name}"\n'
        f'  adtcore:type="{info["type_code"]}"\n'
        f'  adtcore:masterLanguage="E"\n'
        f'  adtcore:responsible="{responsible_value}"{extra_attr}>\n'
        f'  <adtcore:packageRef adtcore:name="{package}"/>\n'
        f'</{root}>'
    )
    try:
        await client.post(
            info["creation_path"],
            body=create_xml,
            query={"corrNr": transport} if transport else None,
            headers={"Content-Type": "application/*", "x-csrf-token": "fetch"},
            is_json=False,
        )
        result["create"] = "ok"
    except Exception as e:
        result["status"] = "error"
        result["step"] = "create"
        result["error"] = str(e)
        return result

    # 2. Lock
    lock_handle = None
    ddic_type_bare = info["type_code"].split("/")[0]  # "DDLS/DF" -> "DDLS"
    try:
        lock_resp = await client.post(
            f"/sap/bc/adt/locks?type={ddic_type_bare}&name={obj_name}",
            headers={"x-csrf-token": "fetch"},
        )
        if isinstance(lock_resp, dict):
            lock_handle = lock_resp.get("lockHandle") or lock_resp.get("handle")
        result["lock"] = "ok"
    except Exception as e:
        result["status"] = "partial"
        result["step"] = "lock"
        result["error"] = str(e)
        return result

    # 3. PUT source
    try:
        await client.put(
            source_url,
            body=ddl_source,
            query={"lockHandle": lock_handle, **({"corrNr": transport} if transport else {})},
            headers={"Content-Type": "text/plain; charset=utf-8", "x-csrf-token": "fetch"},
            is_json=False,
        )
        result["source"] = "ok"
    except Exception as e:
        result["source_error"] = str(e)

    # 4. Unlock TRUOC activate
    if lock_handle:
        try:
            await client.delete(f"/sap/bc/adt/locks/{lock_handle}", is_json=False)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

    # 5. Activate
    try:
        act_resp = await client.post(
            "/sap/bc/adt/activation",
            body={"objectUri": object_url, "objectType": ddic_type_bare, "transport": transport},
            headers={"x-csrf-token": "fetch"},
        )
        result["activate"] = "ok"
        if isinstance(act_resp, dict):
            result["activate_detail"] = act_resp.get("messages", act_resp)
    except Exception as e:
        result["activate_error"] = str(e)

    result["status"] = "success" if result.get("activate") == "ok" else (
        "partial" if result.get("source") == "ok" else "error"
    )
    return result


async def _create_service_binding(
    client: SapClient,
    obj_name: str,
    label: str,
    package: str,
    transport: str,
    service_definition_name: str,
    binding_type: str = "ODATA",
    binding_version: str = "V2",
    binding_category: str = "0",
    responsible: str = "",
) -> dict[str, Any]:
    """Tao Service Binding (SRVB) - port tu vibing-steampunk crud.go dong
    756-797 (nhanh XML rieng cho SRVB) + objectTypes["SRVB"] (dong 286-290).

    KHAC voi DDLS/SRVD: khong co source rieng (toan bo khai bao nam trong XML
    tao nay) nen KHONG PUT source.

    [Unverified] Thu tu lock/activate cho SRVB KHONG xac dinh duoc tu nguon
    tham khao (ho khong co vi du end-to-end day du cho SRVB - buildObjectURL-
    WithParent trong workflows_deploy.go khong co case cho SRVB). Ham nay CHỈ
    lam Create -> Activate (bo qua lock, vi khong co gi de sua sau khi tao) -
    day la suy doan hop ly nhat co the, CHUA duoc kiem chung thuc te. Neu ADT
    tra loi "object chua duoc lock", can them buoc lock/unlock nhu cac ham tren.
    """
    info = STANDARD_OBJECT_TYPES_SRVB
    responsible_value = (responsible or "").strip() or "DDIC"
    result: dict[str, Any] = {
        "status": "unknown",
        "warning": (
            "[Unverified] Thu tu tao SRVB (co can lock truoc activate hay khong) "
            "chua duoc kiem chung tu nguon tham khao - neu loi 'not locked', bao lai."
        ),
    }

    safety_err = await _check_transportable_edit(client, package)
    if safety_err:
        result["status"] = "blocked"
        result["error"] = safety_err
        return result

    if not await _package_exists(client, package):
        result["status"] = "error"
        result["step"] = "package_check"
        result["error"] = f"Package '{package}' khong ton tai."
        return result

    object_url = f"{info['creation_path']}/{obj_name.lower()}"
    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<{info["root_name"]} {info["namespace"]} xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'  adtcore:description="{_xml_escape(label)}"\n'
        f'  adtcore:name="{obj_name}"\n'
        f'  adtcore:type="{info["type_code"]}"\n'
        f'  adtcore:responsible="{responsible_value}">\n'
        f'  <adtcore:packageRef adtcore:name="{package}"/>\n'
        f'  <srvb:services srvb:name="{service_definition_name}">\n'
        '    <srvb:content srvb:version="0001">\n'
        f'      <srvb:serviceDefinition adtcore:name="{service_definition_name}"/>\n'
        '    </srvb:content>\n'
        '  </srvb:services>\n'
        f'  <srvb:binding srvb:category="{binding_category}" srvb:type="{binding_type}" '
        f'srvb:version="{binding_version}">\n'
        '    <srvb:implementation adtcore:name=""/>\n'
        '  </srvb:binding>\n'
        f'</{info["root_name"]}>'
    )
    try:
        await client.post(
            info["creation_path"],
            body=create_xml,
            query={"corrNr": transport} if transport else None,
            headers={"Content-Type": "application/*", "x-csrf-token": "fetch"},
            is_json=False,
        )
        result["create"] = "ok"
    except Exception as e:
        result["status"] = "error"
        result["step"] = "create"
        result["error"] = str(e)
        return result

    try:
        act_resp = await client.post(
            "/sap/bc/adt/activation",
            body={"objectUri": object_url, "objectType": "SRVB", "transport": transport},
            headers={"x-csrf-token": "fetch"},
        )
        result["activate"] = "ok"
        if isinstance(act_resp, dict):
            result["activate_detail"] = act_resp.get("messages", act_resp)
    except Exception as e:
        result["activate_error"] = str(e)

    result["status"] = "success" if result.get("activate") == "ok" else (
        "partial" if result.get("create") == "ok" else "error"
    )
    return result


STANDARD_OBJECT_TYPES_SRVB = {
    "type_code": "SRVB/SVB",
    "creation_path": "/sap/bc/adt/businessservices/bindings",
    "root_name": "srvb:serviceBinding",
    "namespace": 'xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings"',
}


async def _publish_service_binding(
    client: SapClient, service_name: str, service_version: str = "0001",
) -> dict[str, Any]:
    """Publish Service Binding de thuc su expose thanh OData service - KHAC
    voi Activate (2 buoc rieng biet). Port tu vibing-steampunk crud.go dong
    1069-1108 (PublishServiceBinding/publishUnpublishServiceBinding)."""
    try:
        body = (
            '<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">\n'
            f'  <adtcore:objectReference adtcore:name="{service_name}"/>\n'
            '</adtcore:objectReferences>'
        )
        resp = await client.post(
            "/sap/bc/adt/businessservices/odatav2/publishjobs",
            body=body,
            query={"servicename": service_name, "serviceversion": service_version or "0001"},
            headers={"Content-Type": "application/*", "Accept": "application/*", "x-csrf-token": "fetch"},
            is_json=False,
        )
        return {"status": "success", "publish": "ok", "detail": resp if isinstance(resp, dict) else str(resp)[:500]}
    except Exception as e:
        return {"status": "error", "step": "publish", "error": str(e)}


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
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()

    if not fields:
        # Tao table mac dinh voi key + uuid + admin fields
        fields = [
            {"name": "key client", "type": "abap.clnt", "key": "true", "notNull": "true"},
            {"name": "key uuid", "type": "sysuuid_x16", "key": "true", "notNull": "true"},
        ]

    ddl = _build_table_ddl(name, label, fields)
    result = await _create_table_object(client, name, label, ddl, package, transport)
    result["ddl"] = ddl
    return _to_json(result)


async def _handle_create_cds_view(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten CDS view). VD: ZI_SD09_SALES_ORDERS"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({"error": "Thieu 'source' (DDL source day du cua CDS view: define view entity ...)"})

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_standard_object(client, "ddls", name, label, source, package, transport, responsible)
    return _to_json(result)


async def _handle_create_service_definition(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten service definition). VD: ZUI_SD09_SALES_ORDERS_SD"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({
            "error": "Thieu 'source' (DDL source: define service <name> { expose <cds view> as ...; }). "
                     "Khong co generator tu dong cho SRVD (giong ben nguon tham khao), phai tu viet."
        })

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_standard_object(client, "srvd", name, label, source, package, transport, responsible)
    return _to_json(result)


async def _handle_create_service_binding(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten service binding). VD: ZUI_SD09_SALES_ORDERS_O2"})

    service_definition_name = args.get("serviceDefinition", "").upper().strip()
    if not service_definition_name:
        return _to_json({"error": "Thieu 'serviceDefinition' (ten Service Definition da tao/activate truoc do)."})

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    binding_type = args.get("bindingType", "ODATA")
    binding_version = args.get("bindingVersion", "V2")
    binding_category = args.get("bindingCategory", "0")
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_service_binding(
        client, name, label, package, transport, service_definition_name,
        binding_type, binding_version, binding_category, responsible,
    )
    return _to_json(result)


async def _handle_publish_service_binding(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten service binding can publish)."})

    version = args.get("serviceVersion", "0001")
    result = await _publish_service_binding(client, name, version)
    return _to_json(result)


# ===== Tool Registration ===========================================

def build_dict_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "sap_create_domain",
            "description": (
                "Tao Domain ABAP Cloud (define domain ...). Dung cookie auth sap-btp-agent. "
                "[GIOI HAN] CHUA co buoc tao object moi + gan package - chi ghi de duoc source "
                "neu domain nay DA TON TAI SAN trong he thong (khong tu tao moi/khong chon package)."
            ),
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
            "description": (
                "Tao Data Element ABAP Cloud (define data element ...). Dung cookie auth sap-btp-agent. "
                "[GIOI HAN] CHUA co buoc tao object moi + gan package - chi ghi de duoc source "
                "neu data element nay DA TON TAI SAN trong he thong."
            ),
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
            "description": (
                "Tao Database Table ABAP Cloud MOI (define table ...), gan dung package. Dung cookie "
                "auth sap-btp-agent. Tu dong them admin fields (created_by, created_at...) neu thieu. "
                "CHI cho phep package local ($TMP/$*) - package that (transportable) bi CHAN TUYET DOI, khong co cach bat qua."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten table. VD: ZTB_HEADER"},
                    "label": {"type": "string", "description": "Mo ta table."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP (local, luon cho phep)."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
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
        {
            "name": "sap_create_cds_view",
            "description": (
                "Tao CDS View (DDLS) MOI qua ADT + gan package - port tu vibing-steampunk (da xac nhan "
                "hoat dong that). Ban PHAI tu cung cap 'source' day du (define view entity ... as select "
                "from ...). CHI cho phep package local ($TMP/$*) - package that bi CHAN TUYET DOI."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten CDS view. VD: ZI_SD09_SALES_ORDERS"},
                    "label": {"type": "string", "description": "Mo ta (adtcore:description)."},
                    "source": {"type": "string", "description": "DDL source day du cua CDS view."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_cds_view,
        },
        {
            "name": "sap_create_service_definition",
            "description": (
                "Tao Service Definition (SRVD) MOI qua ADT + gan package - port tu vibing-steampunk. "
                "KHONG co generator DDL tu dong (giong nguon tham khao) - ban phai tu viet 'source' dang "
                "'define service <name> { expose <cds_view> as ...; }'."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten service definition. VD: ZUI_SD09_SALES_ORDERS_SD"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "source": {"type": "string", "description": "DDL source: define service <name> { expose <view> as ...; }"},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_service_definition,
        },
        {
            "name": "sap_create_service_binding",
            "description": (
                "Tao Service Binding (SRVB) MOI de expose 1 Service Definition ra OData - port tu "
                "vibing-steampunk. [Unverified] thu tu lock/activate cho SRVB chua kiem chung thuc te "
                "(xem warning trong ket qua tra ve). Sau khi tao/activate, goi them "
                "sap_publish_service_binding de thuc su expose OData endpoint."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten service binding. VD: ZUI_SD09_SALES_ORDERS_O2"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "serviceDefinition": {"type": "string", "description": "Ten Service Definition da tao/activate truoc do."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "bindingType": {"type": "string", "description": "Mac dinh ODATA."},
                    "bindingVersion": {"type": "string", "description": "V2 hoac V4. Mac dinh V2."},
                    "bindingCategory": {"type": "string", "description": "'0' = Web API, '1' = UI. Mac dinh '0'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "serviceDefinition"],
            },
            "handler": _handle_create_service_binding,
        },
        {
            "name": "sap_publish_service_binding",
            "description": (
                "Publish 1 Service Binding da activate de thuc su expose thanh OData endpoint - buoc "
                "RIENG voi Activate (port tu vibing-steampunk PublishServiceBinding)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten service binding can publish."},
                    "serviceVersion": {"type": "string", "description": "Mac dinh '0001'."},
                },
                "required": ["name"],
            },
            "handler": _handle_publish_service_binding,
        },
    ]
