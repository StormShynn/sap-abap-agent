#!/usr/bin/env python3
"""Verify consistency giua `docs/sap-knowledge/modules/` (knowledge base) va
`reference/modules/` (agent module skills).

Quy tac verify (khong fail build, chi warning):
  1. Moi file `docs/sap-knowledge/modules/<X>.md` nen co reference module
     tuong ung (`reference/modules/<module-cho-X>/`).
  2. Reference modules KHONG bat buoc co file knowledge-base (nhieu chi la
     cross-cutting nhu `sap-fiori-cloud`, `sap-bw-cloud`).

Thoat 0 neu co warning, 1 neu co loi parse. Chi canh bao, khong block.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KB_MODULES_DIR = REPO_ROOT / "docs" / "sap-knowledge" / "modules"
REF_MODULES_DIR = REPO_ROOT / "reference" / "modules"

# Mapping tu KB module code (SD, FI, ...) sang ten reference module
KB_TO_REF = {
    "SD": ["sap-sd-cloud"],
    "FI": ["sap-fi-cloud"],
    "MM": ["sap-mm-cloud"],
    "CO": ["sap-co-cloud"],
    "PP": ["sap-pp-cloud"],
    "QM": ["sap-qm-cloud"],
    "PM": ["sap-pm-cloud"],
    "WM": ["sap-wm-cloud"],
    "PS": ["sap-ps-cloud"],
    "HCM": ["sap-hcm-cloud"],
    "BW": ["sap-bw-cloud"],
    "LE": ["sap-tm-cloud", "sap-ewm-cloud"],  # LE = Logistics Execution, lien quan TM/EWM
}


def main() -> int:
    if not KB_MODULES_DIR.is_dir():
        print(f"WARNING: {KB_MODULES_DIR} khong ton tai - skip", file=sys.stderr)
        return 0

    if not REF_MODULES_DIR.is_dir():
        print(f"WARNING: {REF_MODULES_DIR} khong ton tai - skip", file=sys.stderr)
        return 0

    warnings: list[str] = []

    for kb_file in sorted(KB_MODULES_DIR.glob("*.md")):
        if kb_file.name.startswith("_") or kb_file.name == "README.md":
            continue
        stem = kb_file.stem  # 'SD', 'FI', ...
        if stem not in KB_TO_REF:
            warnings.append(f"  - {kb_file.name}: khong co mapping sang reference module")
            continue

        for ref_name in KB_TO_REF[stem]:
            ref_dir = REF_MODULES_DIR / ref_name
            if not ref_dir.is_dir():
                warnings.append(
                    f"  - {kb_file.name}: thieu reference module `{ref_name}/`"
                )

    if warnings:
        print("Modules consistency warnings:")
        for w in warnings:
            print(w)
        print("(warning only, khong block build)")
    else:
        print("Modules consistency: OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
