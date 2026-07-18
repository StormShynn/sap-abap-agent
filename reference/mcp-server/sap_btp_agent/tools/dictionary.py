"""
ADT Dictionary Bridge — Tao Domain, Data Element, Database Table, CDS View,
Service Definition, Service Binding, Interface, Package bang cookie auth tu
sap-btp-agent (SapClient).

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
  - Interface (INTF): source ABAP (INTERFACE <name> PUBLIC. ... ENDINTERFACE.)
  - Package (DEVC): KHONG co lock/PUT-source/unlock/activate - chi 1 POST,
    dung ngay (xem _create_package)

ADT Workflow day du (CDS/SRVD/INTF, port tu vibing-steampunk crud.go - xem
ghi chu tung ham): CREATE (POST object + package) -> lock -> PUT source ->
UNLOCK -> activate. Domain/DataElement gio CUNG da co buoc CREATE nay (them
2026-07-18, nguon marcellourbani/abap-adt-api - xem DDIC_CREATE_INFO) - truoc
do CHI lam duoc lock->PUT->unlock->activate (chi ghi de object da ton tai).

Nguon tham khao (da xac nhan hoat dong that qua test song hoac qua chinh
commit/test cua tac gia nguon):
  - github.com/StormShynn/vibing-steampunk (Go, cung tac gia du an nay) -
    pkg/adt/crud.go + devtools.go - CLAS/DDLS/SRVD/DDLX*/DCLS*/SRVB/TABL/INTF/DEVC.
  - github.com/marcellourbani/abap-adt-api (TS, thu vien khac, truong thanh) -
    src/api/objectcreator.ts - DDLX/DCLS/DOMA/DTEL/INTF/MSAG(chua kiem chung)/DEVC.
Endpoint/XML la doc source that, KHONG suy doan - xem comment tai tung noi
dung de biet dong/ham nguon.
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
    "ddlx": {
        # Nguon: github.com/marcellourbani/abap-adt-api src/api/objectcreator.ts
        # (doc truc tiep, DDLX/EX khong co trong vibing-steampunk - ho khong
        # ho tro loai nay). Metadata Extension - annotate view <cds_view> with { ... }
        "type_code": "DDLX/EX",
        "creation_path": "/sap/bc/adt/ddic/ddlx/sources",
        "root_name": "ddlx:ddlxSource",
        "namespace": 'xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources"',
    },
    "dcls": {
        # Nguon: marcellourbani/abap-adt-api objectcreator.ts (vibing-steampunk
        # khong ho tro loai nay). Access Control - define role <name> { grant
        # select on <entity> as authorization where ...; }
        "type_code": "DCLS/DL",
        "creation_path": "/sap/bc/adt/acm/dcl/sources",
        "root_name": "dcl:dclSource",
        "namespace": 'xmlns:dcl="http://www.sap.com/adt/acm/dclsources"',
    },
    "clas": {
        # Nguon: vibing-steampunk crud.go objectTypes["CLAS/OC"] (dong 245-249)
        # + GetObjectURL dong 894-895 - LUU Y: ten object dung UPPERCASE trong
        # URL (khac han DDLS/SRVD/DDLX/DCLS/Table deu lowercase).
        "type_code": "CLAS/OC",
        "creation_path": "/sap/bc/adt/oo/classes",
        "root_name": "class:abapClass",
        "namespace": 'xmlns:class="http://www.sap.com/adt/oo/classes"',
        "url_uppercase": True,
    },
    "intf": {
        # Nguon: hoi tu tu 2 thu vien doc lap (2026-07-18) - vibing-steampunk
        # crud.go ObjectTypeInterface (dong 250-254) VA marcellourbani/
        # abap-adt-api objectcreator.ts (dong 392-400), cung 1 schema. UPPERCASE
        # trong URL nhu Class (xac nhan tu crud.go GetObjectURL + tu 1 disruptive
        # test THAT tren tenant song cua abap-adt-api: disruptive.test.ts dong
        # 176-200 "Create and delete interface", ten literal UPPERCASE trong URL).
        # [Inference] Chuoi lock->PUT source->unlock->activate SAU create chua
        # duoc 1 test song nao chung minh rieng cho INTF (test tren chi lam
        # create->lock->delete) - suy tu cung code path voi CLAS/PROG (da xac
        # nhan dung {url}/source/main cho PROG cung file test).
        "type_code": "INTF/OI",
        "creation_path": "/sap/bc/adt/oo/interfaces",
        "root_name": "intf:abapInterface",
        "namespace": 'xmlns:intf="http://www.sap.com/adt/oo/interfaces"',
        "url_uppercase": True,
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
    (khong ton tai, loi mang, hoac response khong phai text).

    KHONG tu ep header Accept: application/xml - endpoint nay tra 406
    ExceptionResourceNotAcceptable neu ep qua chat (xac nhan qua test that
    2026-07-18, tenant project1: bo header nay di, de client tu dung default
    ADT "application/xml, */*", thi server moi chiu tra ve). Day chinh la
    nguyen nhan goc khien _package_is_local luon tra ve False truoc day -
    khong phai loi logic whitelist, ma la khong bao gio doc duoc XML de tra.
    """
    try:
        result = await client.get(
            f"/sap/bc/adt/packages/{package.lower()}",
            allow_404=True,
            is_json=False,
        )
    except Exception:
        return None
    return result if isinstance(result, str) else None


async def _package_superpackage(client: SapClient, package: str) -> str | None:
    """Lay ten superpackage (package cha) tu XML metadata cua 1 package.

    Format attribute "superPackage" (pak:superPackage adtcore:name="...")
    xac nhan DUNG qua GET that (tenant project1, 2026-07-18) - vd ZSD09_TEST
    tra ve superPackage name="YTEST_NGHIABHT". Neu regex khong khop, tra ve
    None (an toan hon - _package_is_local se roi vao nhanh CHAN).
    """
    xml_text = await _fetch_package_xml(client, package)
    if not xml_text:
        return None
    m = re.search(r'superPackage[^>]*\bname="([^"]+)"', xml_text)
    return m.group(1) if m else None


# Software Component (field pak:softwareComponent/@pak:name tren XML metadata
# cua 1 package) - KHAC HAN voi superPackage (package CHA trong cay phan
# cap): day la 1 truong PHAN LOAI rieng, ZLOCAL khong bao gio xuat hien nhu
# 1 gia tri "superPackage". Xac nhan qua GET that (2026-07-18, tenant
# project1): package ZSD09_TEST (superPackage that = YTEST_NGHIABHT) co
# <pak:softwareComponent pak:name="ZLOCAL" pak:description="Local
# Development" pak:typeDescription="Local customer developments (ABAP for
# cloud development)".../> - day moi la dung y nguoi dung khi noi "ZSD09_TEST
# la sub-package cua ZLOCAL". Chi nhung ten liet ke TUONG MINH o day moi
# duoc tin - KHONG suy rong sang software component/Z-package khac.
_LOCAL_SOFTWARE_COMPONENTS: set[str] = {"ZLOCAL"}


async def _package_software_component(client: SapClient, package: str) -> str | None:
    """Doc field pak:softwareComponent/@pak:name tu XML metadata cua 1
    package. Tra ve None neu khong doc duoc hoac gia tri rong."""
    xml_text = await _fetch_package_xml(client, package)
    if not xml_text:
        return None
    m = re.search(r'softwareComponent[^>]*\bname="([^"]*)"', xml_text)
    return m.group(1) if m and m.group(1) else None


async def _package_is_local(client: SapClient, package: str) -> bool:
    """True neu package nay la local ($ prefix), HOAC software component cua
    no nam trong _LOCAL_SOFTWARE_COMPONENTS, HOAC la sub-package (truc tiep
    hay qua nhieu cap) cua 1 package cha thoa 1 trong 2 dieu kien tren.

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
        swc = await _package_software_component(client, current)
        if swc in _LOCAL_SOFTWARE_COMPONENTS:
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
    thong dang thao tac la he thong khach hang THAT, khong phai sandbox).
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


# Ghi chu: lock/unlock/activate KHONG con la ham rieng le o day nua - da
# chuyen het vao SapClient.edit_session() (client.py). Ly do: 3 buoc nay (+
# create, + PUT source) BAT BUOC chay tren CUNG 1 phien HTTP stateful (giu
# nguyen httpx client + cookie 'sap-contextid' xuyen suot) thi SAP moi nhan
# dung lock - goi rieng le tung ham (nhu ban dau o day) van dung DUNG
# endpoint/format nhung se bi SAP tra loi nham "not locked"/"currently
# editing" vi moi request lai rơi vao 1 ket noi/application-server khac nhau.
# Da xac nhan qua test that voi ZSD09_TEST, 2026-07-17.


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

    # Them admin fields neu chua co - 5 field, dung ten khop chuan abapGit
    # that (xac nhan tu 1 file .tabl.xml serialize that cua khach hang, 2026-07-18):
    # local_last_changed_by/at (ETag muc instance) TACH RIENG voi
    # last_changed_at (tong the) - truoc day chi co 4 field va dung nham
    # ten "last_changed_by/at" cho cap LOCINST, khien CDS view viet theo
    # dung convention 5-field (vd "local_last_changed_by") activate loi
    # "column unknown" (xac nhan qua test that voi ZI_TEST_NOTE).
    has_admin = any(f.get("name", "").lower() in [
        "created_by", "created_at", "local_last_changed_by",
        "local_last_changed_at", "last_changed_at",
    ] for f in fields)
    if not has_admin:
        lines.append("  created_by             : abp_creation_user;")
        lines.append("  created_at             : abp_creation_tstmpl;")
        lines.append("  local_last_changed_by  : abp_locinst_lastchange_user;")
        lines.append("  local_last_changed_at  : abp_locinst_lastchange_tstmpl;")
        lines.append("  last_changed_at        : abp_lastchange_tstmpl;")

    lines.append("}")
    return "\n".join(lines) + "\n"


# ===== Dict CRUD methods ===========================================

# Schema CREATE (POST shell + gan package) cho DOMA/DTEL - nghien cuu tu
# marcellourbani/abap-adt-api (src/api/objectcreator.ts, "ctypes" registry
# dong 519-536, doc truc tiep 2026-07-18). Xac nhan qua chinh commit message
# cua tac gia nguon (561cb54c): "Domain (DOMA/DD): validate -> create OK".
# Day la buoc CREATE con thieu truoc day (chi lock/PUT/unlock/activate,
# khong tao moi duoc). PUT source SAU buoc create nay VAN dung DDL text
# ("define domain X {...}") nhu code cu - da xac nhan hoat dong that voi
# object DA TON TAI (test ZSD09_TEST, 2026-07-17). [Inference] Chuoi
# create+lock+PUT+unlock+activate NAY (ket hop create tu nguon A + PUT DDL
# text tu code cu, KHAC voi setDomainProperties/setDataElementProperties
# cua chinh nguon A dung structured-XML PUT rieng, khong phai DDL text) CHUA
# tu kiem chung tren 1 object HOAN TOAN moi (khac CLAS/DDLS/TABL/INTF da co
# bang chung song) - neu object moi bi loi o buoc PUT source, day la nghi
# van dau tien can xem lai.
DDIC_CREATE_INFO: dict[str, dict[str, str]] = {
    "domain": {
        "creation_path": "/sap/bc/adt/ddic/domains",
        "root_name": "domain:domain",
        "namespace": 'xmlns:domain="http://www.sap.com/dictionary/domain"',
        "type_code": "DOMA/DD",
    },
    "dataelement": {
        "creation_path": "/sap/bc/adt/ddic/dataelements",
        "root_name": "blue:wbobj",
        "namespace": 'xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel"',
        "type_code": "DTEL/DE",
    },
}


async def _create_ddic_object(
    client: SapClient,
    obj_type: str,       # "domain", "dataelement"
    obj_name: str,
    ddl_source: str,
    package: str,
    transport: str = "",
    responsible: str = "",
    label: str = "",
) -> dict[str, Any]:
    """
    ADT workflow: CREATE (POST shell + gan package) -> lock -> PUT source
    (DDL text) -> UNLOCK -> activate.

    Buoc CREATE (xem DDIC_CREATE_INFO) MOI duoc them (2026-07-18) - truoc day
    ham nay CHI lam duoc lock->PUT->unlock->activate (chi ghi de object DA
    TON TAI SAN, khong tao moi + khong gan package duoc). Neu buoc CREATE
    that bai (vd object da ton tai san - "already exists"), KHONG dung lai -
    van tiep tuc thu lock/PUT/unlock/activate nhu cu, giu nguyen kha nang
    ghi de object da ton tai (hanh vi cu, khong pha).

    Thu tu unlock TRUOC activate (khong phai sau) - dung thu tu da xac nhan
    hoat dong trong vibing-steampunk (crud.go CreateTable dong 1228-1234:
    "Unlock BEFORE activation").

    Returns dict voi ket qua.
    """
    ddic_type = DDIC_TYPE_MAP.get(obj_type)
    if not ddic_type:
        raise ValueError(f"Unknown DDIC type: {obj_type}")
    create_info = DDIC_CREATE_INFO.get(obj_type)

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

    lock_handle = None
    object_url = f"/sap/bc/adt/ddic/{obj_type}s/{obj_name.lower()}"

    # Ca chuoi create->lock->PUT->unlock->activate PHAI chay tren CUNG 1
    # edit_session (giu nguyen 1 httpx client + cookie 'sap-contextid' xuyen
    # suot) - thieu cai nay SAP se tra loi nham "not locked"/"currently
    # editing" du lock/unlock rieng le van bao "thanh cong" (xem
    # SapEditSession trong client.py).
    async with client.edit_session() as edit:
        # 0. Create shell + gan package (buoc MOI - xem DDIC_CREATE_INFO)
        if create_info:
            responsible_value = (responsible or "").strip() or "DDIC"
            create_xml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<{create_info["root_name"]} {create_info["namespace"]} xmlns:adtcore="http://www.sap.com/adt/core"\n'
                f'  adtcore:description="{_xml_escape(label or obj_name)}"\n'
                f'  adtcore:name="{obj_name}"\n'
                f'  adtcore:type="{create_info["type_code"]}"\n'
                f'  adtcore:language="EN"\n'
                f'  adtcore:masterLanguage="EN"\n'
                f'  adtcore:responsible="{responsible_value}">\n'
                f'  <adtcore:packageRef adtcore:name="{package}"/>\n'
                f'</{create_info["root_name"]}>'
            )
            try:
                await edit.create(create_info["creation_path"], create_xml, transport)
                result["create"] = "ok"
            except Exception as e:
                result["create_error"] = str(e)
                result["create_warning"] = (
                    "Buoc CREATE that bai - neu object nay DA TON TAI SAN, day co "
                    "the chi la loi 'already exists' vo hai (lock/PUT ben duoi se "
                    "ghi de source nhu binh thuong). Neu object THUC SU CHUA TON "
                    "TAI va van loi o day, schema CREATE (nguon marcellourbani/"
                    "abap-adt-api, chua kiem chung full tren object hoan toan moi) "
                    "co the khong khop tenant nay."
                )
                # KHONG return - van thu lock/PUT ben duoi (xem docstring).

        # 1. Lock
        try:
            lock_handle = await edit.lock(object_url)
            result["lock"] = "ok"
            result["lock_handle"] = lock_handle
        except Exception as e:
            result["status"] = "error"
            result["step"] = "lock"
            result["error"] = str(e)
            return result

        # 2. PUT source (DDL)
        try:
            await edit.put_source(f"{object_url}/source/main", ddl_source, lock_handle)
            result["source"] = "ok"
        except Exception as e:
            result["source_error"] = str(e)
            # Tiep tuc: van thu unlock + activate (object co the da co source cu)

        # 3. Unlock (TRUOC activate)
        try:
            await edit.unlock(object_url, lock_handle)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

        # 4. Activate
        try:
            act_resp = await edit.activate(object_url, obj_name.upper())
            result["activate"] = "ok"
            result["activate_detail"] = act_resp[:500]
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

    # Toan bo chuoi create->lock->PUT->unlock->activate PHAI chay tren CUNG 1
    # edit_session (giu nguyen httpx client + cookie 'sap-contextid' xuyen
    # suot) - xem SapEditSession trong client.py de biet ly do.
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
    async with client.edit_session() as edit:
        # 1. Create table object (gan package ngay trong XML nay)
        try:
            await edit.create(table_path, create_xml, transport,
                               content_type="application/vnd.sap.adt.tables.v2+xml")
            result["create"] = "ok"
        except Exception as e:
            result["status"] = "error"
            result["step"] = "create"
            result["error"] = str(e)
            return result

        # 2. Lock
        lock_handle = None
        try:
            lock_handle = await edit.lock(table_url)
            result["lock"] = "ok"
        except Exception as e:
            result["status"] = "partial"
            result["step"] = "lock"
            result["error"] = str(e)
            return result

        # 3. PUT source (Content-Type "text/plain" - KHONG "; charset=utf-8",
        # khac voi domain/dataelement - dung dung header vibing-steampunk dung)
        try:
            await edit.put_source(source_url, ddl_source, lock_handle,
                                   content_type="text/plain", transport=transport)
            result["source"] = "ok"
        except Exception as e:
            result["source_error"] = str(e)

        # 4. Unlock TRUOC activate
        try:
            await edit.unlock(table_url, lock_handle)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

        # 5. Activate
        try:
            act_resp = await edit.activate(table_url, obj_name.upper())
            result["activate"] = "ok"
            result["activate_detail"] = act_resp[:500]
        except Exception as e:
            result["activate_error"] = str(e)

    result["status"] = "success" if result.get("activate") == "ok" else (
        "partial" if result.get("source") == "ok" else "error"
    )
    return result


async def _create_package(
    client: SapClient,
    name: str,
    label: str,
    parent_package: str,
    software_component: str = "",
    transport_layer: str = "",
    responsible: str = "",
) -> dict[str, Any]:
    """Tao Package (DEVC) MOI - nguon: hoi tu tu 2 thu vien doc lap
    (2026-07-18) - marcellourbani/abap-adt-api (objectcreator.ts
    createBodyPackage(), dong 145-169) VA vibing-steampunk (crud.go
    buildCreateObjectBody(), dong 686-712) - cung 1 schema. Xac nhan CO 1
    disruptive test THAT tren tenant song cua abap-adt-api
    (disruptive.test.ts dong 333-360 "Create and delete a package").

    KHAC HAN moi loai khac trong file nay: KHONG co lock/PUT-source/unlock/
    activate - CHI 1 lenh POST duy nhat la xong, object dung ngay (xac nhan
    truc tiep tu test song noi tren - createObj() chi goi create + doc lai
    objectStructure, khong lock/source/activate gi ca).

    LUU Y quan trong ve tham so: "parent_package" o day la SUPERPACKAGE (package
    CHA cua package MOI nay trong cay phan cap) - KHONG PHAI noi package nay
    "nam trong" theo nghia cac ham khac trong file dung "package" (vi chinh
    no la 1 package, khong nam "trong" package nao ca). An toan: parent_package
    van phai la local (dung _check_transportable_edit nhu moi noi khac) -
    tranh tao package moi ngoai vung an toan.
    """
    result: dict[str, Any] = {"status": "unknown"}

    safety_err = await _check_transportable_edit(client, parent_package)
    if safety_err:
        result["status"] = "blocked"
        result["error"] = safety_err
        return result

    responsible_value = (responsible or "").strip() or "DDIC"
    swc = (software_component or "").strip() or "LOCAL"
    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<pak:package xmlns:pak="http://www.sap.com/adt/packages"\n'
        '             xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'             adtcore:description="{_xml_escape(label)}"\n'
        f'             adtcore:name="{name}"\n'
        '             adtcore:type="DEVC/K"\n'
        f'             adtcore:responsible="{responsible_value}">\n'
        '  <pak:attributes pak:packageType="development"/>\n'
        f'  <pak:superPackage adtcore:name="{parent_package}"/>\n'
        '  <pak:applicationComponent/>\n'
        '  <pak:transport>\n'
        f'    <pak:softwareComponent pak:name="{swc}"/>\n'
        f'    <pak:transportLayer pak:name="{transport_layer}"/>\n'
        '  </pak:transport>\n'
        '  <pak:translation/>\n'
        '  <pak:useAccesses/>\n'
        '  <pak:packageInterfaces/>\n'
        '  <pak:subPackages/>\n'
        '</pak:package>'
    )
    try:
        async with client.edit_session() as edit:
            resp = await edit.create("/sap/bc/adt/packages", create_xml, "")
        result["status"] = "success"
        result["create"] = "ok"
        result["detail"] = resp[:500]
    except Exception as e:
        result["status"] = "error"
        result["step"] = "create"
        result["error"] = str(e)
    return result


async def _create_bdef(
    client: SapClient,
    obj_name: str,
    label: str,
    package: str,
    transport: str,
    behavior_source: str,
    behavior_class: str = "",
    implementation_type: str = "Managed",
    responsible: str = "",
) -> dict[str, Any]:
    """Tao Behavior Definition (BDEF) MOI - schema hoi tu tu NHIEU thu vien
    doc lap (2026-07-18): marcellourbani/vscode_abap_remote_fs
    (BdefCreator.ts), jfilak/sapcli (behaviordefinition.py), fr0ster/
    mcp-abap-adt-clients (behaviorDefinition/create.ts) - CA 3 cung 1
    schema. LUU Y: marcellourbani/abap-adt-api (nguon chinh dung cho cac
    loai khac trong file nay) KHONG ho tro BDEF - chinh tac gia xac nhan
    trong issue #27 "not a simple task... not a priority".

    [Unverified] - QUAN TRONG: khong nguon nao trong so cac nguon tren xac
    nhan RIENG cho S/4HANA Cloud PUBLIC Edition (chi co bang chung tren he
    thong classic/private trial) - endpoint noi bo nay co the KHONG duoc
    released cho Public Edition. Day la lan dau tool nay thu tao BDEF - can
    theo doi ket qua that truoc khi tin tuyet doi.

    Khac cac loai khac trong file nay:
    1. Content-Type rieng "application/vnd.sap.adt.blues.v1+xml" (khong
       phai "application/*" nhu DDLS/SRVD/DDLX/DCLS/INTF).
    2. Can 1 block <adtcore:adtTemplate> khai bao implementation_type
       (Managed/Unmanaged/...) TRUOC packageRef trong XML tao.
    3. behavior_class la TUY CHON (khong bat buoc) - xac nhan qua doc 17 file
       BDEF that trong tests/__Du_an (2026-07-18): pattern "projection;" (BDEF
       chieu Consumption KHONG co "implementation in class") la THAT va PHO
       BIEN (vd ZC_ZCM01_PHIEUTHU001, ZC_QM_ZQM03, ZC_INT_BILLING deu khong co
       class implement). Neu CO behavior_class (PHAI DA TON TAI/activate
       truoc), activate PHAI gom CA BDEF lan class do trong CUNG 1 request
       (xem SapEditSession.activate_multi trong client.py) - thieu buoc nay
       activate co the fail hoac cho ket qua sai (xac nhan tu nhieu nguon).
       Neu KHONG co behavior_class, activate binh thuong nhu moi loai khac
       (chi 1 object).
    """
    result: dict[str, Any] = {
        "status": "unknown",
        "warning": (
            "[Unverified] Tao BDEF qua ADT REST chua duoc kiem chung tren "
            "S/4HANA Cloud Public Edition (chi co bang chung tren he thong "
            "classic/private trial trong nguon tham khao) - day la lan dau "
            "thu tren tenant nay, theo doi ky ket qua tra ve."
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

    responsible_value = (responsible or "").strip() or "DDIC"
    creation_path = "/sap/bc/adt/bo/behaviordefinitions"
    object_url = f"{creation_path}/{obj_name.lower()}"
    source_url = f"{object_url}/source/main"

    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'  adtcore:description="{_xml_escape(label)}"\n'
        f'  adtcore:name="{obj_name}"\n'
        '  adtcore:type="BDEF/BDO"\n'
        '  adtcore:language="EN"\n'
        '  adtcore:masterLanguage="EN"\n'
        f'  adtcore:responsible="{responsible_value}">\n'
        '  <adtcore:adtTemplate>\n'
        f'    <adtcore:adtProperty adtcore:key="implementation_type">{implementation_type}</adtcore:adtProperty>\n'
        '  </adtcore:adtTemplate>\n'
        f'  <adtcore:packageRef adtcore:name="{package}"/>\n'
        '</blue:blueSource>'
    )

    async with client.edit_session() as edit:
        try:
            await edit.create(creation_path, create_xml, transport,
                               content_type="application/vnd.sap.adt.blues.v1+xml")
            result["create"] = "ok"
        except Exception as e:
            result["status"] = "error"
            result["step"] = "create"
            result["error"] = str(e)
            return result

        lock_handle = None
        try:
            lock_handle = await edit.lock(object_url)
            result["lock"] = "ok"
        except Exception as e:
            result["status"] = "partial"
            result["step"] = "lock"
            result["error"] = str(e)
            return result

        try:
            await edit.put_source(source_url, behavior_source, lock_handle,
                                   content_type="text/plain", transport=transport)
            result["source"] = "ok"
        except Exception as e:
            result["source_error"] = str(e)

        try:
            await edit.unlock(object_url, lock_handle)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

        # Activate - gom CA class implement behavior neu CO (xem docstring;
        # BDEF chieu projection thuong KHONG co class, activate 1 minh la du)
        try:
            refs = [(object_url, obj_name.upper())]
            if behavior_class:
                behavior_class_url = f"/sap/bc/adt/oo/classes/{behavior_class.upper()}"
                refs.append((behavior_class_url, behavior_class.upper()))
            act_resp = await edit.activate_multi(refs)
            result["activate"] = "ok"
            result["activate_detail"] = act_resp[:500]
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

    # Hau het loai (DDLS/SRVD/DDLX/DCLS) dung LOWERCASE trong URL - rieng Class
    # dung UPPERCASE (xac nhan tu vibing-steampunk GetObjectURL, dong 894-895).
    url_name = obj_name.upper() if info.get("url_uppercase") else obj_name.lower()
    object_url = f"{info['creation_path']}/{url_name}"
    source_url = f"{object_url}/source/main"
    root = info["root_name"]
    extra_attr = info.get("extra_root_attr", "")

    # 1. Create object (gan package ngay trong XML nay)
    # Lich su debug tren project1: responsible="DDIC" khong du, van fail 400
    # "Check of condition failed" tai ddl:ddlSource(1). Thu them
    # masterLanguage="E" (lay tu .abapgit cua project - DDLANGUAGE: E) cung
    # KHONG du - lan test gan nhat doi sang loi khac han: "error occurred when
    # deserializing in the simple transformation program SDDIC_ST_ADT_DDLS"
    # (loi parse XML tang thap, khac han loi validate nghiep vu truoc).
    #
    # Doc truc tiep source github.com/marcellourbani/abap-adt-api (thu vien
    # TS khac, truong thanh, nguoi dung xac nhan dang dung) - src/api/
    # objectcreator.ts ham createBodySimple(): DDLS/SRVD/SRVB deu di qua ham
    # nay, LUON co CA HAI adtcore:language VA adtcore:masterLanguage, dung
    # ma 2 ky tu "EN" (KHONG PHAI "E" mot ky tu - "E" la ma rieng cua dinh
    # dang serialize .abapgit, khac schema voi ADT REST). Day la nguon khac,
    # doc lap voi vibing-steampunk, cung xac nhan pattern nay - ap dung ca 2
    # attribute, "EN", thay the hoan toan "E" truoc do.
    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<{root} {info["namespace"]} xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'  adtcore:description="{_xml_escape(label)}"\n'
        f'  adtcore:name="{obj_name}"\n'
        f'  adtcore:type="{info["type_code"]}"\n'
        f'  adtcore:language="EN"\n'
        f'  adtcore:masterLanguage="EN"\n'
        f'  adtcore:responsible="{responsible_value}"{extra_attr}>\n'
        f'  <adtcore:packageRef adtcore:name="{package}"/>\n'
        f'</{root}>'
    )
    # Toan bo chuoi create->lock->PUT->unlock->activate PHAI chay tren CUNG 1
    # edit_session (giu nguyen httpx client + cookie 'sap-contextid' xuyen
    # suot) - thieu cai nay SAP tra loi nham "not locked"/"currently editing"
    # du tung buoc rieng le van bao "thanh cong" (da xac nhan qua test that
    # voi ZSD09_TEST, 2026-07-17 - xem SapEditSession trong client.py).
    async with client.edit_session() as edit:
        try:
            await edit.create(info["creation_path"], create_xml, transport)
            result["create"] = "ok"
        except Exception as e:
            result["status"] = "error"
            result["step"] = "create"
            result["error"] = str(e)
            return result

        # 2. Lock
        lock_handle = None
        try:
            lock_handle = await edit.lock(object_url)
            result["lock"] = "ok"
        except Exception as e:
            result["status"] = "partial"
            result["step"] = "lock"
            result["error"] = str(e)
            return result

        # 3. PUT source
        try:
            await edit.put_source(source_url, ddl_source, lock_handle, transport=transport)
            result["source"] = "ok"
        except Exception as e:
            result["source_error"] = str(e)

        # 4. Unlock TRUOC activate
        try:
            await edit.unlock(object_url, lock_handle)
            result["unlock"] = "ok"
        except Exception as e:
            result["unlock_error"] = str(e)

        # 5. Activate
        try:
            act_resp = await edit.activate(object_url, obj_name.upper())
            result["activate"] = "ok"
            result["activate_detail"] = act_resp[:500]
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
    # adtcore:language/masterLanguage="EN" - cung pattern da xac nhan can cho
    # DDLS/SRVD (xem _create_standard_object), marcellourbani createBodyBinding()
    # cung di qua createBodySimple() nen SRVB can tuong tu.
    create_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<{info["root_name"]} {info["namespace"]} xmlns:adtcore="http://www.sap.com/adt/core"\n'
        f'  adtcore:description="{_xml_escape(label)}"\n'
        f'  adtcore:name="{obj_name}"\n'
        f'  adtcore:type="{info["type_code"]}"\n'
        f'  adtcore:language="EN"\n'
        f'  adtcore:masterLanguage="EN"\n'
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
    # create + activate tren CUNG 1 edit_session (xem SapEditSession) - du
    # SRVB khong lock/PUT source, van nen giu session/cookie nhat quan giua
    # 2 buoc nay.
    async with client.edit_session() as edit:
        try:
            await edit.create(info["creation_path"], create_xml, transport)
            result["create"] = "ok"
        except Exception as e:
            result["status"] = "error"
            result["step"] = "create"
            result["error"] = str(e)
            return result

        try:
            act_resp = await edit.activate(object_url, obj_name.upper())
            result["activate"] = "ok"
            result["activate_detail"] = act_resp[:500]
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
    binding_version: str = "V4",
) -> dict[str, Any]:
    """Publish Service Binding de thuc su expose thanh OData service - KHAC
    voi Activate (2 buoc rieng biet). Port tu vibing-steampunk crud.go dong
    1069-1108 (PublishServiceBinding/publishUnpublishServiceBinding).

    CHI ap dung that su cho OData V2. Xac nhan qua test that (2026-07-18,
    tenant project1): goi endpoint duoi day cho 1 binding V4 lam request
    TREO (ReadTimeout ~90s+, khong tra loi ro rang gi ca), khong phai loi
    tra ve binh thuong. Theo tai lieu SAP chinh thuc (help.sap.com/docs/
    abap-cloud, "Using Service Binding Editor for OData V4 Service"): voi
    V4, chinh buoc ACTIVATE (da lam trong sap_create_service_binding) la
    thu dang ky/expose service (qua /IWBEP/V4_ADMIN) - V4 KHONG CO khai
    niem "publish" rieng nhu V2. Vi vay: neu binding_version=V4, tra ve
    ngay 1 thong bao ro rang, KHONG goi endpoint nay (tranh treo lai)."""
    if (binding_version or "V4").strip().upper() == "V4":
        return {
            "status": "success",
            "publish": "not_needed",
            "info": (
                "Service Binding OData V4 khong co buoc publish rieng - "
                "activate (da lam luc tao binding qua sap_create_service_binding) "
                "chinh la thu dang ky/expose service qua /IWBEP/V4_ADMIN. "
                "Publish o day CHI danh cho OData V2 - goi cho V4 se TREO "
                "(xac nhan qua test that, tenant project1, 2026-07-18)."
            ),
        }
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
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    ddl = _build_domain_ddl(name, label, data_type, fixed_values)
    result = await _create_ddic_object(client, "domain", name, ddl, package, transport, responsible, label)
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
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    ddl = _build_data_element_ddl(name, label, data_type_or_domain)
    result = await _create_ddic_object(client, "dataelement", name, ddl, package, transport, responsible, label)
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


async def _handle_create_metadata_extension(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten metadata extension). VD: ZI_SD09_SALES_ORDERS_MDE"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({
            "error": "Thieu 'source' (DDL source: annotate view <cds_view> with { ... }). "
                     "Khong co generator tu dong, phai tu viet."
        })

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_standard_object(client, "ddlx", name, label, source, package, transport, responsible)
    return _to_json(result)


async def _handle_create_access_control(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten access control/DCL). VD: ZDC_SD09_TOPFRUIT"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({
            "error": "Thieu 'source' (DDL source: define role <name> { grant select on <entity> "
                     "as authorization where ...; }). Khong co generator tu dong, phai tu viet."
        })

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_standard_object(client, "dcls", name, label, source, package, transport, responsible)
    return _to_json(result)


async def _handle_create_class(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten class). VD: ZCL_SD09_TOPFRUIT_CALC"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({
            "error": "Thieu 'source' (source ABAP day du: CLASS <name> DEFINITION ... ENDCLASS. "
                     "CLASS <name> IMPLEMENTATION ... ENDCLASS.). Khong co generator tu dong."
        })

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_standard_object(client, "clas", name, label, source, package, transport, responsible)
    return _to_json(result)


async def _handle_create_interface(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten interface). VD: ZIF_SD09_TOPFRUIT"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({
            "error": "Thieu 'source' (source ABAP day du: INTERFACE <name> PUBLIC. ... "
                     "ENDINTERFACE.). Khong co generator tu dong."
        })

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_standard_object(client, "intf", name, label, source, package, transport, responsible)
    return _to_json(result)


async def _handle_create_package(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten package moi). VD: ZSD09_SUB"})

    parent_package = (args.get("parentPackage") or "").strip().upper()
    if not parent_package:
        return _to_json({
            "error": "Thieu 'parentPackage' (superpackage - package CHA cua package "
                     "moi nay, phai la local: $TMP/$*, hoac sub-package cua package "
                     "cha local, vd ZSD09_TEST)."
        })

    label = args.get("label", name)
    software_component = (args.get("softwareComponent") or "").strip().upper()
    transport_layer = (args.get("transportLayer") or "").strip().upper()
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_package(
        client, name, label, parent_package, software_component, transport_layer, responsible,
    )
    return _to_json(result)


async def _handle_create_bdef(args: dict[str, Any] | None) -> str:
    args = args or {}
    client = SapClient(_pick_profile(args))
    await client.init()

    name = args.get("name", "").upper().strip()
    if not name:
        return _to_json({"error": "Thieu 'name' (ten behavior definition). VD: ZR_SD09_TOPFRUIT"})

    source = args.get("source", "").strip()
    if not source:
        return _to_json({
            "error": "Thieu 'source' (BDEF source day du: managed implementation in "
                     "class <behaviorClass> unique; strict ( 2 ); define behavior for "
                     "<name> { ... }). Khong co generator tu dong."
        })

    # TUY CHON - "projection;" (BDEF chieu Consumption) thuong KHONG co class
    # implement, xac nhan qua doc file that trong tests/__Du_an (2026-07-18).
    # Neu CO truyen, class nay PHAI DA TON TAI/activate truoc (activate BDEF
    # se gom chung voi class do).
    behavior_class = args.get("behaviorClass", "").upper().strip()

    label = args.get("label", name)
    package = (args.get("package") or "$TMP").strip().upper()
    transport = (args.get("transport") or "").strip().upper()
    implementation_type = args.get("implementationType", "Managed")
    responsible = (args.get("responsible") or "").strip().upper()

    result = await _create_bdef(
        client, name, label, package, transport, source, behavior_class,
        implementation_type, responsible,
    )
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
    binding_version = args.get("bindingVersion", "V4")
    result = await _publish_service_binding(client, name, version, binding_version)
    return _to_json(result)


# ===== Tool Registration ===========================================

def build_dict_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "sap_create_domain",
            "description": (
                "Tao Domain ABAP Cloud MOI (define domain ...) qua ADT + gan package - port tu "
                "marcellourbani/abap-adt-api (schema CREATE them 2026-07-18). PUT source (DDL text) "
                "van la co che da xac nhan hoat dong that voi object da ton tai; chuoi create+PUT tren "
                "object HOAN TOAN moi chua tu kiem chung rieng - xem 'create_warning' trong ket qua "
                "neu buoc create loi."
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
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name"],
            },
            "handler": _handle_create_domain,
        },
        {
            "name": "sap_create_data_element",
            "description": (
                "Tao Data Element ABAP Cloud MOI (define data element ...) qua ADT + gan package - "
                "port tu marcellourbani/abap-adt-api (schema CREATE them 2026-07-18). PUT source (DDL "
                "text) van la co che da xac nhan hoat dong that voi object da ton tai; chuoi create+PUT "
                "tren object HOAN TOAN moi chua tu kiem chung rieng - xem 'create_warning' neu buoc "
                "create loi."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten data element. VD: ZDE_STATUS"},
                    "label": {"type": "string", "description": "Mo ta (EndUserText.label)."},
                    "type": {"type": "string", "description": "Kieu hoac domain. VD: zdom_status, abap.char(40), abap.int4. Mac dinh: abap.char(40)."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
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
            "name": "sap_create_metadata_extension",
            "description": (
                "Tao Metadata Extension (DDLX) MOI qua ADT + gan package - nguon: marcellourbani/"
                "abap-adt-api (vibing-steampunk khong ho tro loai nay). KHONG co generator DDL tu "
                "dong - ban phai tu viet 'source' dang 'annotate view <cds_view> with { ... }'."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten metadata extension. VD: ZI_SD09_SALES_ORDERS_MDE"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "source": {"type": "string", "description": "DDL source: annotate view <cds_view> with { ... }"},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_metadata_extension,
        },
        {
            "name": "sap_create_access_control",
            "description": (
                "Tao Access Control / DCL (DCLS) MOI qua ADT + gan package - nguon: marcellourbani/"
                "abap-adt-api. KHONG co generator - ban phai tu viet 'source' dang 'define role <name> "
                "{ grant select on <entity> as authorization where <field> = aspect pfcg_auth(...); }'."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten access control. VD: ZDC_SD09_TOPFRUIT"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "source": {"type": "string", "description": "DDL source: define role <name> { grant select on <entity> as authorization where ...; }"},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_access_control,
        },
        {
            "name": "sap_create_class",
            "description": (
                "Tao ABAP Class (CLAS) MOI qua ADT + gan package - port tu vibing-steampunk. Ban phai "
                "tu cung cap 'source' day du (ca CLASS ... DEFINITION va CLASS ... IMPLEMENTATION trong "
                "1 khoi source/main - CHI ho tro class don gian, chua ho tro them include rieng nhu "
                "testclasses/locals)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten class. VD: ZCL_SD09_TOPFRUIT_CALC"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "source": {"type": "string", "description": "Source ABAP day du: CLASS <name> DEFINITION ... ENDCLASS. CLASS <name> IMPLEMENTATION ... ENDCLASS."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_class,
        },
        {
            "name": "sap_create_interface",
            "description": (
                "Tao ABAP Interface (INTF) MOI qua ADT + gan package - schema hoi tu tu 2 nguon doc "
                "lap (vibing-steampunk + marcellourbani/abap-adt-api), xac nhan qua 1 disruptive test "
                "that (create+lock+delete). [Inference] Chuoi lock->PUT source->unlock->activate SAU "
                "create chua duoc test song rieng cho INTF (suy tu cung code path voi Class). Ban phai "
                "tu cung cap 'source' day du (INTERFACE <name> PUBLIC. ... ENDINTERFACE.)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten interface. VD: ZIF_SD09_TOPFRUIT"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "source": {"type": "string", "description": "Source ABAP day du: INTERFACE <name> PUBLIC. ... ENDINTERFACE."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem (adtcore:responsible). Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_interface,
        },
        {
            "name": "sap_create_package",
            "description": (
                "Tao Package (DEVC) MOI - schema hoi tu tu 2 nguon doc lap (vibing-steampunk + "
                "marcellourbani/abap-adt-api), xac nhan qua 1 disruptive test that tren tenant song. "
                "KHAC moi tool khac trong bo nay: KHONG co lock/PUT-source/unlock/activate, chi 1 lenh "
                "la xong. 'parentPackage' la SUPERPACKAGE (package CHA cua package moi nay trong cay "
                "phan cap) - PHAI la local ($TMP/$*, hoac sub-package cua package cha local)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten package moi. VD: ZSD09_SUB"},
                    "label": {"type": "string", "description": "Mo ta (EndUserText/description)."},
                    "parentPackage": {"type": "string", "description": "Superpackage - package CHA cua package moi nay (BAT BUOC), phai la local."},
                    "softwareComponent": {"type": "string", "description": "Ten software component. Mac dinh 'LOCAL' neu de trong."},
                    "transportLayer": {"type": "string", "description": "Transport layer. De trong neu package local."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem. Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "parentPackage"],
            },
            "handler": _handle_create_package,
        },
        {
            "name": "sap_create_bdef",
            "description": (
                "Tao RAP Behavior Definition (BDEF) MOI qua ADT + gan package - schema hoi tu tu nhieu "
                "nguon doc lap (marcellourbani/vscode_abap_remote_fs, jfilak/sapcli, fr0ster/"
                "mcp-abap-adt-clients - LUU Y marcellourbani/abap-adt-api dung cho cac loai khac trong "
                "bo nay KHONG ho tro BDEF). [Unverified - QUAN TRONG] chua co nguon nao xac nhan rieng "
                "cho S/4HANA Cloud Public Edition (chi co bang chung tren he thong classic/private "
                "trial) - day la lan dau thu tren tenant Public Edition, theo doi ket qua that. "
                "'behaviorClass' la TUY CHON: BDEF root (managed/unmanaged) thuong CO class implement "
                "(PHAI DA TON TAI/activate truoc - activate se gom chung voi class do); BDEF projection "
                "(chi co 'projection;' trong source, khong 'implementation in class') THUONG KHONG CO "
                "- xac nhan qua doc 17 file that trong tests/__Du_an, 2026-07-18 - de trong trong truong "
                "hop nay."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string"},
                    "name": {"type": "string", "description": "Ten behavior definition. VD: ZR_SD09_TOPFRUIT"},
                    "label": {"type": "string", "description": "Mo ta."},
                    "source": {"type": "string", "description": "BDEF source day du. Vd co class: 'managed implementation in class ZBP_R_X unique; strict ( 2 ); define behavior for ZR_X { create; update; delete; }'. Vd KHONG class (projection): 'projection; strict ( 2 ); define behavior for ZC_X { use create; use update; }'."},
                    "behaviorClass": {"type": "string", "description": "Ten class implement behavior - TUY CHON (de trong neu source la 'projection;' khong co class). Neu truyen, class PHAI DA TON TAI/activate truoc. VD: ZBP_R_SD09_TOPFRUIT"},
                    "implementationType": {"type": "string", "description": "Managed/Unmanaged/Abstract/Interface. Mac dinh 'Managed'."},
                    "package": {"type": "string", "description": "Package dich. Mac dinh $TMP."},
                    "transport": {"type": "string", "description": "Khong dung duoc hien tai - package khong phai $TMP/$* bi chan tuyet doi, xem 'package'."},
                    "responsible": {"type": "string", "description": "SAP username chiu trach nhiem. Mac dinh 'DDIC' neu de trong."},
                },
                "required": ["name", "source"],
            },
            "handler": _handle_create_bdef,
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
                    "bindingVersion": {"type": "string", "description": "V2 hoac V4 - loai binding nay (mac dinh V4). V4 KHONG can publish rieng (activate luc tao binding la du) - goi tool nay voi V4 chi tra ve thong bao, khong goi API that. Chi truyen 'V2' neu binding thuc su la OData V2 va can publish that."},
                },
                "required": ["name"],
            },
            "handler": _handle_publish_service_binding,
        },
    ]
