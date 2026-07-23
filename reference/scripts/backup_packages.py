#!/usr/bin/env python3
"""Backup source ABAP cho package Z* (va sub-package) + custom field/logic
YY1* qua ADT REST - lay cam hung tu co che serialize cua abapGit: dat ten file
theo kieu "<ten>.<loai>.<phan>", thu muc theo package hierarchy (xem
docs/sap-knowledge/abapgit-serialization-spec.md va nguon abapGit that,
docs.abapgit.org/user-guide/reference/folders-filenames.html).

KHAC voi abapGit that: day la 1 chieu DOC-RA-FILE don gian (khong sinh du XML
metadata co cau truc de abapGit that pull nguoc lai duoc) - muc tieu la co 1
ban backup doc duoc/diff duoc bang git, KHONG PHAI 1 repo abapGit day du
round-trip. Xem "known_limitations" trong manifest sinh ra sau moi lan chay.

Dung SapClient (reference/mcp-server/sap_btp_agent/sap/client.py) IMPORT TRUC
TIEP, khong qua giao thuc MCP - cung 1 pattern da dung trong
skills/sap-doc-to-md/SKILL.md (goi `python -c "from sap_btp_agent... "`). Ly
do: backup "full" 1 package co the co hang tram object - goi tool MCP tung
object mot (moi lan qua JSON-RPC + LLM doc lai ket qua) rat cham/ton token;
import thang SapClient cho phep 1 vong lap async goi truc tiep HTTP, chi in
ra 1 bao cao tom tat cuoi cung cho Claude/nguoi dung doc.

    python reference/scripts/backup_packages.py --packages ZFI_CUSTOM --inspect
    python reference/scripts/backup_packages.py --packages ZFI_CUSTOM,ZSD_EXT --dry-run
    python reference/scripts/backup_packages.py --packages ZFI_CUSTOM,ZSD_EXT --include-yy1

QUAN TRONG - doc truoc khi tin tuong ket qua full-scan (xem them SKILL.md cua
skill sap-package-backup, muc "Do tin cay theo loai object"):

  1. TYPE_MAP duoi day chia object theo 4 muc tin cay:
     - "verified": path da duoc sap_read_source/dictionary.py trong repo nay
       dung/test that (CLAS).
     - "high": suy tu chinh CHIEU TAO object da test that trong dictionary.py
       (INTF/DDLS/DDLX/DCLS/SRVD, cung GET path voi PUT dang dung) - chua tu
       verify rieng chieu DOC.
     - "medium": suy tu chieu tao NHUNG buoc tao ban than chua duoc xac nhan
       hoat dong tren S/4HANA Cloud Public Edition (BDEF - xem canh bao trong
       dictionary.py::_create_bdef), hoac loai DDIC ma abapGit that luu bang
       XML co cau truc (DD01V/DD04V/DD02V...) KHONG phai DDL text (DOMA/DTEL/
       TABL) - script van THU doc qua /source/main, loi thi bao ro trong
       manifest thay vi gia vo thanh cong.
     - "low": suy tu kien thuc ADT REST chung, KHONG tu 1 nguon da verify
       trong chinh repo nay (PROG).
  2. Cau truc XML/JSON tra ve tu nodestructure (list_packages)/quickSearch
     (sap_search) CHUA duoc test song trong phien viet script nay - ham
     parse_nodestructure()/parse_search_result() suy tu cau truc ADT pho bien
     (khop nhieu client ADT ma nguon khac), KHONG phai doc tu 1 response that
     cua he thong ban dang ket noi. CHAY --inspect TRUOC voi 1 package nho de
     kiem tra parser co doc dung khong - dung tin tuong ngay ket qua full-scan
     dau tien.
  3. "YY1" la tien to SAP sinh cho Custom Field qua app "Custom Fields and
     Logic" (Key User Extensibility). Script nay CHI tim duoc object co TADIR
     entry that su khop pattern ten (mac dinh "YY1", doi qua --yy1-pattern) VA
     co loai nam trong TYPE_MAP (thuong la class custom logic/CDS extend) -
     KHONG backup duoc metadata "business context" cua app do (nhan field, vi
     tri UI, scope) - phan nay nam trong repository rieng cua app Fiori, chua
     co API/tool nao trong MCP server nay doc duoc.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from sap_btp_agent.config.paths import get_out_dir
from sap_btp_agent.sap.client import SapClient

# ===== Object type dispatch (xem docstring muc 1 ve do tin cay) ===========

TYPE_MAP: dict[str, dict[str, object]] = {
    "CLAS": {
        "path": "/sap/bc/adt/oo/classes",
        "case": "upper",
        "ext": "clas.abap",
        "has_source": True,
        "confidence": "verified",
    },
    "INTF": {
        "path": "/sap/bc/adt/oo/interfaces",
        "case": "upper",
        "ext": "intf.abap",
        "has_source": True,
        "confidence": "high",
    },
    "DDLS": {
        "path": "/sap/bc/adt/ddic/ddl/sources",
        "case": "lower",
        "ext": "ddls.asddls",
        "has_source": True,
        "confidence": "high",
    },
    "DDLX": {
        "path": "/sap/bc/adt/ddic/ddlx/sources",
        "case": "lower",
        "ext": "ddlx.asddlxs",
        "has_source": True,
        "confidence": "high",
    },
    "DCLS": {
        "path": "/sap/bc/adt/acm/dcl/sources",
        "case": "lower",
        "ext": "dcls.asdcls",
        "has_source": True,
        "confidence": "high",
    },
    "SRVD": {
        "path": "/sap/bc/adt/ddic/srvd/sources",
        "case": "lower",
        "ext": "srvd.srvdsrv",
        "has_source": True,
        "confidence": "high",
    },
    "BDEF": {
        "path": "/sap/bc/adt/bo/behaviordefinitions",
        "case": "lower",
        "ext": "bdef.asbdef",
        "has_source": True,
        "confidence": "medium",
    },
    "DOMA": {
        "path": "/sap/bc/adt/ddic/domains",
        "case": "lower",
        "ext": "doma.abap",
        "has_source": True,
        "confidence": "medium",
    },
    "DTEL": {
        "path": "/sap/bc/adt/ddic/dataelements",
        "case": "lower",
        "ext": "dtel.abap",
        "has_source": True,
        "confidence": "medium",
    },
    "TABL": {
        "path": "/sap/bc/adt/ddic/tables",
        "case": "lower",
        "ext": "tabl.abap",
        "has_source": True,
        "confidence": "medium",
    },
    "SRVB": {
        "path": "/sap/bc/adt/businessservices/bindings",
        "case": "lower",
        "ext": "srvb.xml",
        "has_source": False,
        "confidence": "medium",
    },
    "PROG": {
        "path": "/sap/bc/adt/programs/programs",
        "case": "lower",
        "ext": "prog.abap",
        "has_source": True,
        "confidence": "low",
    },
}

DEVC_PATH = "/sap/bc/adt/packages"  # xac nhan qua dictionary.py::_fetch_package_xml (verified)

DEFAULT_MAX_DEPTH = 15
DEFAULT_CONCURRENCY = 4


def _pick_profile(explicit: str | None) -> str | None:
    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    return env or (explicit or "").strip() or None


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _short_type(raw_type: str) -> str:
    """ "CLAS/OC" -> "CLAS". Nodestructure/quickSearch co the tra ca dang ngan
    lan dang compound "TYPE/subtype" - chua xac dinh chac chan dang nao, xu
    ly ca 2 cho an toan."""
    return (raw_type or "").split("/")[0].strip().upper()


def _safe_name(name: str) -> str:
    cleaned = "".join(c for c in name if c.isalnum() or c in ("_", "-"))
    return cleaned or "_"


# ===== Parse response (xem docstring muc 2 - CHUA test song) ==============


def parse_nodestructure(raw: object) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Tra ve (objects, subpackages) tu ket qua list_packages().

    raw co the la dict/list (neu SAP tra JSON) hoac str (XML - nhieu kha nang
    hon, vi nodestructure la POST /sap/bc/adt/... va SapClient mac dinh gui
    Accept: application/xml cho moi request ADT - xem client.py::_request()).
    """
    if isinstance(raw, dict):
        nodes = raw.get("nodes")
        if nodes is None:
            nodes = raw.get("DATA", {}).get("TREE_CONTENT", [])
        objs: list[dict[str, str]] = []
        subs: list[dict[str, str]] = []
        for n in nodes if isinstance(nodes, list) else []:
            if not isinstance(n, dict):
                continue
            rec = {str(k).upper(): str(v) for k, v in n.items()}
            target = subs if _short_type(rec.get("OBJECT_TYPE", "")) == "DEVC" else objs
            target.append(rec)
        return objs, subs

    if not isinstance(raw, str) or not raw.strip():
        return [], []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return [], []

    objs = []
    subs = []
    for el in root.iter():
        if _local_tag(el.tag).upper() != "SEU_ADT_REPOSITORY_OBJ_NODE":
            continue
        rec = {_local_tag(c.tag).upper(): (c.text or "").strip() for c in el}
        if not rec.get("OBJECT_NAME"):
            continue
        target = subs if _short_type(rec.get("OBJECT_TYPE", "")) == "DEVC" else objs
        target.append(rec)
    return objs, subs


def parse_search_result(raw: object) -> list[dict[str, str]]:
    """Tuong tu parse_nodestructure - ho tro ca JSON lan XML, CHUA test song."""
    if isinstance(raw, dict):
        refs = raw.get("objectReferences") or raw.get("results") or []
        out = []
        for r in refs if isinstance(refs, list) else []:
            if not isinstance(r, dict):
                continue
            name = str(r.get("name") or r.get("OBJECT_NAME") or "")
            if not name:
                continue
            out.append(
                {
                    "OBJECT_NAME": name,
                    "OBJECT_TYPE": str(r.get("type") or r.get("OBJECT_TYPE") or ""),
                    "OBJECT_URI": str(r.get("uri") or r.get("OBJECT_URI") or ""),
                }
            )
        return out

    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    out = []
    for el in root.iter():
        tag = _local_tag(el.tag).lower()
        if tag not in ("objectreference", "object"):
            continue
        attrs = {_local_tag(k).lower(): v for k, v in el.attrib.items()}
        name = attrs.get("name", "")
        if name:
            out.append(
                {
                    "OBJECT_NAME": name,
                    "OBJECT_TYPE": attrs.get("type", ""),
                    "OBJECT_URI": attrs.get("uri", ""),
                }
            )
    return out


# ===== Goi ADT (qua SapClient truc tiep) ===================================


async def fetch_object_source(
    client: SapClient, obj_type: str, obj_name: str
) -> tuple[str | None, str | None]:
    info = TYPE_MAP.get(_short_type(obj_type))
    if not info:
        return None, "unsupported_type"
    name = obj_name.upper() if info["case"] == "upper" else obj_name.lower()
    base_url = f"{info['path']}/{name}"
    try:
        if info["has_source"]:
            text = await client.get(
                f"{base_url}/source/main", headers={"Accept": "text/plain"}, is_json=False
            )
        else:
            text = await client.get(base_url, is_json=False, allow_404=True)
    except Exception as err:
        return None, str(err)
    if text is None:
        return None, "not_found_404"
    return (text if isinstance(text, str) else json.dumps(text, ensure_ascii=False, indent=2)), None


async def fetch_package_meta(client: SapClient, package: str) -> tuple[str | None, str | None]:
    # KHONG tu ep header Accept - endpoint nay tra 406 neu ep qua chat, xem
    # dictionary.py::_fetch_package_xml (verified qua test that 2026-07-18).
    try:
        text = await client.get(f"{DEVC_PATH}/{package.lower()}", is_json=False, allow_404=True)
    except Exception as err:
        return None, str(err)
    if text is None:
        return None, "not_found_404"
    return (text if isinstance(text, str) else json.dumps(text, ensure_ascii=False, indent=2)), None


async def discover_by_name(
    client: SapClient, query: str, max_results: int = 500
) -> list[dict[str, str]]:
    # Goi truc tiep endpoint quickSearch (khong qua client.search_objects(),
    # vi ham do hardcode maxResults=50 - khong du de tim het object YY1* tren
    # 1 he thong that). Khong sua client.py - chi goi .get() cong khai voi
    # tham so rieng cua script nay.
    raw = await client.get(
        "/sap/bc/adt/repository/informationsystem/search",
        query={
            "operation": "quickSearch",
            "query": query,
            "objectType": "",
            "maxResults": str(max_results),
        },
    )
    return parse_search_result(raw)


async def walk_package(
    client: SapClient,
    package: str,
    depth: int,
    max_depth: int,
    seen: set[str],
    inventory: list[tuple[str, dict[str, str]]],
) -> list[str]:
    """De quy liet ke object + sub-package. Tra ve danh sach loi (khong raise)
    de 1 package con loi khong lam hong toan bo scan."""
    errors: list[str] = []
    if depth > max_depth:
        errors.append(
            f"{package}: dat --max-depth ({max_depth}), dung de quy - tang len neu can sau hon."
        )
        return errors
    if package in seen:
        return errors
    seen.add(package)

    try:
        raw = await client.list_packages(package)
    except Exception as err:
        errors.append(f"{package}: khong doc duoc nodestructure - {err}")
        return errors

    objs, subs = parse_nodestructure(raw)
    for o in objs:
        inventory.append((package, o))
    for s in subs:
        sub_name = s.get("OBJECT_NAME", "").strip()
        if sub_name:
            errors.extend(
                await walk_package(client, sub_name, depth + 1, max_depth, seen, inventory)
            )
    return errors


# ===== Orchestration ========================================================


@dataclass
class BackupResult:
    package: str
    name: str
    obj_type: str
    status: str  # "ok" | "error" | "skipped_unsupported_type"
    file: str | None = None
    error: str | None = None


KNOWN_LIMITATIONS = [
    "Cau truc XML nodestructure/quickSearch chua duoc test song - neu counts bat "
    "thuong (vd 0 object cho 1 package chac chan co object), chay lai voi --inspect "
    "va doi chieu file _inspect_*.raw.txt voi parse_nodestructure() trong script nay.",
    "YY1: chi tim duoc object co TADIR entry khop ten pattern VA loai nam trong "
    "TYPE_MAP - KHONG backup duoc metadata 'business context' cua app Custom Fields "
    "and Logic (nhan field, vi tri UI) - phan do can API/tool khac chua co trong MCP "
    "server nay.",
    "DOMA/DTEL/TABL/BDEF: doc qua /source/main voi do tin cay 'medium' - abapGit that "
    "luu cac loai nay bang XML co cau truc (DD01V/DD04V/DD02V...), khong phai DDL text "
    "thuan - file ghi ra day la BEST-EFFORT, kiem tra lai truoc khi coi la ban backup "
    "day du tuong duong abapGit that.",
    "MSAG (Message Class) va FUGR (Function Group/Module) khong co trong TYPE_MAP - "
    "chua xac dinh duoc endpoint ADT REST doc duoc (xem "
    "docs/sap-knowledge/abapgit-serialization-spec.md muc MSAG) - object loai nay se "
    "bi bao 'skipped_unsupported_type'.",
]


async def run_backup(args: argparse.Namespace) -> int:
    client = SapClient(_pick_profile(args.profile))
    await client.init()

    out_root = Path(args.out) if args.out else (get_out_dir() / "backups")
    label = _safe_name(args.label or "backup")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / f"{label}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]
    try:
        run_dir.resolve().relative_to(repo_root)
        print(
            f"[CANH BAO] Thu muc output ({run_dir}) nam TRONG repo plugin nay "
            f"({repo_root}) - du lieu Z*/YY1 backup co the la source code THAT cua "
            "khach hang, KHONG duoc commit vao git cua plugin nay. Dung --out tro ra "
            "ngoai repo, hoac tu dam bao path nay da .gitignore truoc khi tiep tuc.",
            file=sys.stderr,
        )
    except ValueError:
        pass  # ngoai repo - binh thuong, khong can canh bao

    packages = [p.strip() for p in (args.packages or "").split(",") if p.strip()]

    if args.inspect:
        if not packages:
            print(
                "Can it nhat 1 package cho --inspect (vd --packages ZFI_CUSTOM).", file=sys.stderr
            )
            return 2
        pkg = packages[0]
        raw = await client.list_packages(pkg)
        dump_file = run_dir / f"_inspect_{_safe_name(pkg)}.raw.txt"
        dump_file.write_text(
            raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        objs, subs = parse_nodestructure(raw)
        print(f"Da ghi raw response vao {dump_file}")
        print(
            f"Parser doc duoc: {len(objs)} object truc tiep, {len(subs)} sub-package trong '{pkg}'."
        )
        if not objs and not subs:
            print(
                "[CANH BAO] Parser khong doc duoc gi ca - co the format XML/JSON tra ve "
                "khac voi gia dinh trong parse_nodestructure(). Mo file raw o tren, doi "
                "chieu voi ham parse_nodestructure() trong script nay va tu dieu chinh "
                "truoc khi chay full-scan.",
                file=sys.stderr,
            )
        return 0

    if not packages and not args.include_yy1:
        print("Can --packages (vd ZFI_CUSTOM,ZSD_EXT) hoac --include-yy1.", file=sys.stderr)
        return 2

    inventory: list[tuple[str, dict[str, str]]] = []
    walk_errors: list[str] = []
    seen: set[str] = set()

    for root_pkg in packages:
        walk_errors.extend(await walk_package(client, root_pkg, 0, args.max_depth, seen, inventory))

    if args.include_yy1:
        yy1_hits = await discover_by_name(client, args.yy1_pattern)
        for h in yy1_hits:
            inventory.append(("_yy1_enhancements", h))

    print(f"Tim thay {len(inventory)} object (da duyet {len(seen)} package).")
    if args.dry_run:
        for pkg, o in inventory:
            print(
                f"  [{pkg}] {_short_type(o.get('OBJECT_TYPE', '')):6s}\t{o.get('OBJECT_NAME', '')}"
            )
        for e in walk_errors:
            print(f"  LOI duyet package: {e}", file=sys.stderr)
        return 0

    package_meta_status: dict[str, str] = {}
    for pkg in seen:
        text, err = await fetch_package_meta(client, pkg)
        package_meta_status[pkg] = "ok" if text else f"error: {err}"
        if text:
            pkg_dir = run_dir / _safe_name(pkg)
            pkg_dir.mkdir(parents=True, exist_ok=True)
            (pkg_dir / "package.devc.xml").write_text(text, encoding="utf-8")

    sem = asyncio.Semaphore(max(1, args.concurrency))
    results: list[BackupResult] = []

    async def _one(pkg: str, o: dict[str, str]) -> None:
        name = o.get("OBJECT_NAME", "").strip()
        obj_type = o.get("OBJECT_TYPE", "").strip()
        if not name:
            return
        async with sem:
            text, err = await fetch_object_source(client, obj_type, name)
        if text is not None:
            info = TYPE_MAP[_short_type(obj_type)]
            target_dir = run_dir / _safe_name(pkg)
            target_dir.mkdir(parents=True, exist_ok=True)
            base = _safe_name(name).lower()
            file_path = target_dir / f"{base}.{info['ext']}"
            file_path.write_text(text, encoding="utf-8")
            meta_path = target_dir / f"{base}.{_short_type(obj_type).lower()}.meta.json"
            meta_path.write_text(json.dumps(o, ensure_ascii=False, indent=2), encoding="utf-8")
            results.append(
                BackupResult(pkg, name, obj_type, "ok", file=str(file_path.relative_to(run_dir)))
            )
        else:
            status = "skipped_unsupported_type" if err == "unsupported_type" else "error"
            results.append(BackupResult(pkg, name, obj_type, status, error=err))

    await asyncio.gather(*(_one(pkg, o) for pkg, o in inventory))

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "profile": client.profile_id,
        "requested_packages": packages,
        "yy1_pattern": args.yy1_pattern if args.include_yy1 else None,
        "max_depth": args.max_depth,
        "packages_walked": sorted(seen),
        "package_meta_status": package_meta_status,
        "walk_errors": walk_errors,
        "counts": {
            "objects_found": len(inventory),
            "ok": sum(1 for r in results if r.status == "ok"),
            "error": sum(1 for r in results if r.status == "error"),
            "skipped_unsupported_type": sum(
                1 for r in results if r.status == "skipped_unsupported_type"
            ),
        },
        "objects": [vars(r) for r in results],
        "known_limitations": KNOWN_LIMITATIONS,
    }
    manifest_path = run_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = manifest["counts"]
    print(
        f"Xong: {counts['ok']} object backup OK, {counts['error']} loi, "
        f"{counts['skipped_unsupported_type']} bo qua (loai chua ho tro)."
    )
    print(f"Manifest: {manifest_path}")
    print(f"Output: {run_dir}")
    return 0 if counts["error"] == 0 else 1


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Backup source Z* packages + YY1 enhancements qua ADT REST."
    )
    p.add_argument(
        "--packages",
        default="",
        help="Danh sach package Z* goc, phan cach dau phay (vd ZFI_CUSTOM,ZSD_EXT).",
    )
    p.add_argument(
        "--include-yy1",
        action="store_true",
        help="Tim them object ten khop --yy1-pattern tren toan he thong (ngoai pham vi --packages).",
    )
    p.add_argument(
        "--yy1-pattern",
        default="YY1",
        help="Pattern ten cho quickSearch khi --include-yy1 (mac dinh 'YY1').",
    )
    p.add_argument("--profile", default="", help="Profile SAP (de trong = active).")
    p.add_argument(
        "--out", default="", help="Thu muc output (mac dinh: out dir cua sap-btp-agent/backups/)."
    )
    p.add_argument(
        "--label",
        default="backup",
        help="Nhan cho ten thu muc cua lan chay nay (mac dinh 'backup').",
    )
    p.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"Do sau toi da khi de quy sub-package (mac dinh {DEFAULT_MAX_DEPTH}).",
    )
    p.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"So request dong thoi toi da khi doc source (mac dinh {DEFAULT_CONCURRENCY}).",
    )
    p.add_argument(
        "--inspect",
        action="store_true",
        help="CHI dump raw nodestructure cua package dau tien trong --packages, khong ghi backup "
        "that. Chay buoc nay TRUOC lan full-scan dau tien.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Liet ke object se backup, KHONG goi read-source / KHONG ghi file.",
    )
    return p


def main() -> int:
    args = build_arg_parser().parse_args()
    return asyncio.run(run_backup(args))


if __name__ == "__main__":
    sys.exit(main())
