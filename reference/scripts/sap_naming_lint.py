#!/usr/bin/env python3
"""SAP ABAP naming lint — 3-layer CDS pattern.

Check tất cả file ABAP/CDS trong src/ theo docs/sap-knowledge/naming-conventions.md.

Naming rule (3-layer):
- ZTB*  transparent table
- ZI*   CDS interface view (base, technical)
- ZR*   CDS reuse view (root, associations)
- ZC*   CDS consumption view (projection, UI)
- ZE*   CDS extension view
- ZA*   CDS abstract entity
- Z*    behavior definition (ZC cho C, ZR cho R)
- ZBP*  behavior implementation (ABAP class)
- ZUI*  service binding / service definition
- ZCL_* ABAP class thường
- ZF_*  function module
- Độ dài tên: repository object ≤ 30 ký tự; database table (TABL / DDL `define table`) ≤ 16 ký tự
  (nguồn: ABAP Keyword Documentation – Names of Repository Objects, CLOUD)

Usage:
  python sap_naming_lint.py <src-dir> [--json]
"""
import json
import re
import sys
from pathlib import Path

# Map: file extension → expected prefix pattern
# Thứ tự quan trọng — check rule cụ thể trước rule generic.
RULES = [
    # Transparent table
    (r'\.tabl\.xml$',         [r'^ZTB[A-Z0-9_]+$'],                    'transparent table'),

    # CDS DDL: cùng extension cho table và view
    # Phân biệt: table dùng 'define table', view dùng 'define view'
    (r'\.ddls\.asddls$',      'CDS_DDL',                              'CDS DDL source (table or view)'),

    # Behavior definition
    (r'\.bdef\.asbdef$',      [r'^ZR[A-Z0-9_]+$', r'^ZC[A-Z0-9_]+$'],  'behavior definition (ZR for R, ZC for C)'),

    # ABAP class
    (r'\.clas\.abap$',        [r'^ZBP[A-Z0-9_]+$', r'^ZCL_[A-Z0-9_]+$', r'^LCL_[A-Z0-9_]+$'],
                                                                     'ABAP class (behavior impl / regular / test)'),

    # Service definition (ZUI = app/UI, ZAPI = machine-to-machine — xem service-naming-convention)
    (r'\.srvd\.[^.]+$',      [r'^ZUI[A-Z0-9_]+(_SD|_O[24])?$', r'^ZAPI[A-Z0-9_]+(_SD|_O[24])?$'],
                                                                     'service definition'),

    # Service binding (ZUI = app/UI, ZAPI = machine-to-machine)
    (r'\.srvb\.[^.]+$',      [r'^ZUI[A-Z0-9_]+_O[24]$', r'^ZAPI[A-Z0-9_]+_O[24]$'],
                                                                     'service binding OData V2/V4'),

    # Metadata extension
    (r'\.mde\.asmd$',         [r'^ZC[A-Z0-9_]+$'],                    'metadata extension (MDE for ZC consumption)'),
    (r'\.ddlx\.asddlxs$',     [r'^ZC[A-Z0-9_]+$'],                    'metadata extension (DDLX for ZC consumption)'),

    # DCL
    (r'\.dcls\.asdcls$',      [r'^ZR[A-Z0-9_]+$', r'^ZC[A-Z0-9_]+$'], 'DCL (data control language)'),

    # Function module
    (r'\.function\.xml$',     [r'^ZF_[A-Z0-9_]+$'],                   'function module'),
]

# Giới hạn độ dài tên (nguồn: ABAP Keyword Documentation – Names of Repository Objects, CLOUD):
#   "The length of names is restricted to 30 characters or less" (gồm namespace prefix)
#   "the names of database tables are restricted to 16 characters"
# → DB-physical object (transparent table / DDL `define table`) = 16, còn lại = 30.
MAX_NAME_LEN = 30
MAX_NAME_LEN_TABLE = 16


def max_name_len(path: Path, is_ddl_table: bool = False) -> int:
    """Trả max độ dài tên hợp lệ cho object theo loại file.

    - Database table (transparent/pool/cluster) hoặc DDL `define table` = 16
      (vì sinh ra physical DB object).
    - DDIC structure (TABCLASS=INTTAB, cũng serialize ra .tabl.xml) = 30.
    - Còn lại (data element, domain, table type, CDS view, class, service...) = 30.
    """
    if is_ddl_table:
        return MAX_NAME_LEN_TABLE
    if path.name.endswith('.tabl.xml'):
        try:
            txt = path.read_text(encoding='utf-8', errors='replace').upper()
        except Exception:
            txt = ''
        # Structure (INTTAB) không phải DB table → giới hạn repository chung (30).
        if 'INTTAB' in txt:
            return MAX_NAME_LEN
        return MAX_NAME_LEN_TABLE
    return MAX_NAME_LEN


def check_name(name: str, patterns: list) -> bool:
    if not patterns:
        return True
    return any(re.fullmatch(p, name) for p in patterns)


def detect_cds_kind(path: Path, stem: str) -> str:
    """Phân biệt ZI/ZR/ZC/ZE/ZA dựa vào content của CDS view."""
    try:
        text = path.read_text(encoding='utf-8', errors='replace').lower()
    except Exception:
        return 'unknown'
    if 'abstract entity' in text:
        return 'ZA (abstract)'
    if 'as projection on' in text:
        if 'provider contract' in text or 'provider' in text[:200]:
            return 'ZC (consumption/projection)'
        # projection on ZR hoặc ZI
        if f'as projection on {stem.lower()}' in text.replace('_', ''):
            return 'ZC (consumption/projection)'
        # Nếu projection on view khác thì có thể là ZC
        return 'ZC (consumption/projection)'
    if 'as select from' in text:
        return 'ZI (interface/base)'
    if 'as projection on' in text:
        return 'ZR (reuse) or ZC (consumption)'
    return 'unknown'


def lint_dir(src: Path) -> list:
    issues = []
    for path in src.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        for pattern, prefixes, label in RULES:
            if re.search(pattern, path.name):
                # Lấy tên object từ file name
                # File naming: zi_<object>.ddls.asddls → stem = zi_<object>
                stem_lower = path.name.split('.')[0]
                stem = stem_lower.upper()

                # Special check cho MDE/DDLX
                if path.name.endswith('.mde.asmd') or path.name.endswith('.ddlx.asddlxs'):
                    stem = path.name.split('.')[0].upper()

                # Check
                # Special handling cho CDS DDL
                is_table = False
                if prefixes == 'CDS_DDL':
                    try:
                        content = path.read_text(encoding='utf-8', errors='replace')
                    except Exception:
                        content = ''
                    is_table = 'define table' in content.lower()
                    if is_table:
                        actual_prefixes = [r'^ZTB[A-Z0-9_]+$']
                        actual_label = 'CDS DDL table'
                    else:
                        actual_prefixes = [r'^ZI[A-Z0-9_]+$', r'^ZR[A-Z0-9_]+$',
                                          r'^ZC[A-Z0-9_]+$', r'^ZE[A-Z0-9_]+$',
                                          r'^ZA[A-Z0-9_]+$']
                        actual_label = 'CDS view (interface/reuse/consumption/extension/abstract)'
                    if not check_name(stem, actual_prefixes):
                        issues.append({
                            'file': str(rel),
                            'object': stem,
                            'expected_prefix': actual_prefixes,
                            'type': actual_label,
                            'severity': 'ERROR',
                            'message': f'Object {stem} ({actual_label}) violates naming. Expected one of: {actual_prefixes}',
                        })
                else:
                    if not check_name(stem, prefixes):
                        issues.append({
                            'file': str(rel),
                            'object': stem,
                            'expected_prefix': prefixes,
                            'type': label,
                            'severity': 'ERROR',
                            'message': f'Object {stem} ({label}) violates naming. Expected one of: {prefixes}',
                        })
                limit = max_name_len(path, is_ddl_table=is_table)
                if len(stem) > limit:
                    issues.append({
                        'file': str(rel),
                        'object': stem,
                        'expected_prefix': prefixes if prefixes != 'CDS_DDL' else [],
                        'type': label,
                        'severity': 'ERROR',
                        'message': f'Object name {len(stem)} chars > max {limit} '
                                   f'({"database table" if limit == MAX_NAME_LEN_TABLE else "repository object"})',
                    })
                break
    return issues


def main():
    if len(sys.argv) < 2:
        print('Usage: sap_naming_lint.py <src-dir> [--json]', file=sys.stderr)
        sys.exit(2)
    src = Path(sys.argv[1])
    if not src.is_dir():
        print(f'Not a directory: {src}', file=sys.stderr)
        sys.exit(2)
    json_out = '--json' in sys.argv

    issues = lint_dir(src)
    if json_out:
        print(json.dumps({'issues': issues, 'count': len(issues)}, indent=2))
    else:
        if not issues:
            print(f'✅ Naming lint passed: {sum(1 for _ in src.rglob("*"))} files checked, 0 issues.')
            return 0
        print(f'❌ Naming lint FAILED: {len(issues)} issue(s)')
        print()
        for i, issue in enumerate(issues, 1):
            print(f'  {i}. {issue["file"]}')
            print(f'     Object: {issue["object"]}')
            print(f"     Type:   {issue['type']}")
            print(f"     {issue['message']}")
            print()
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
