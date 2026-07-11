#!/usr/bin/env python3
"""
Convert file .docx/.xlsx/.xls sang Markdown (.md), phuc vu lam ngu canh cho AI
doc hieu tai lieu nghiep vu (FS/BP/...) va sinh code/xu ly logic ABAP.

Mac dinh doc/ghi trong thu muc local per-user "in/"/"out/" duoi
%USERPROFILE%\\.sap-btp-agent\\ (Windows) hoac ~/.sap-btp-agent/ (macOS/Linux) - CUNG cho voi
noi luu profile/secrets ket noi SAP BTP, KHONG nam trong git repo (tai lieu FS thuong la du
lieu nghiep vu/khach hang khong nen commit chung voi source code plugin).

Cach dung:
  python reference/scripts/office_to_md.py                          # convert het file trong in/ -> out/ (mac dinh)
  python reference/scripts/office_to_md.py /path/to/mydoc.docx      # convert 1 file, output vao out/ mac dinh
  python reference/scripts/office_to_md.py /path/to/mydoc.docx -o /path/khac  # chi dinh thu muc output khac

Anh nhung trong .docx (ke ca screenshot EMF) duoc trich xuat ra file that trong thu
muc "<ten-file>_assets/" ben canh file .md, thay vi bi cat bo thanh placeholder rong
nhu mac dinh cua thu vien markitdown. Luu y: anh dinh dang EMF/WMF (thuong la screenshot
dan tu clipboard Windows/Office) khong hien thi truc tiep duoc tren trinh xem Markdown
hay trinh duyet - can mo bang Word/PowerPoint (Save as Picture) hoac cong cu rieng de
doi sang PNG neu can xem truc quan.
"""

import argparse
import re
import sys
from pathlib import Path

import mammoth
import markdownify
import pandas as pd

try:
    from sap_btp_agent.config.paths import get_in_dir, get_out_dir

    DEFAULT_INPUT_DIR = get_in_dir()
    DEFAULT_OUTPUT_DIR = get_out_dir()
except ImportError:
    print(
        "[canh bao] Khong import duoc sap_btp_agent (chua cai `sap-btp-agent`?) - "
        "fallback ve thu muc in/ va out/ trong repo. Cai bang: pip install sap-btp-agent-mcp "
        "(xem reference/mcp-server/) de dung dung thu muc local chuan.",
        file=sys.stderr,
    )
    REPO_DIR = Path(__file__).resolve().parent.parent.parent
    DEFAULT_INPUT_DIR = REPO_DIR / "in"
    DEFAULT_OUTPUT_DIR = REPO_DIR / "out"

SUPPORTED_EXTENSIONS = {".docx", ".xlsx", ".xls"}

# EMF/WMF la dinh dang vector rieng cua Windows (Office hay dung khi paste screenshot).
_EXTENSION_FIXUPS = {"x-emf": "emf", "x-wmf": "wmf", "svg+xml": "svg", "jpeg": "jpg"}


def _clean_extension(content_type: str) -> str:
    ext = content_type.partition("/")[2].partition(";")[0].strip()
    return _EXTENSION_FIXUPS.get(ext, ext or "bin")


def convert_docx(input_path: Path, output_dir: Path):
    """Tra ve (duong dan file .md, so anh trich xuat duoc, danh sach canh bao)."""
    assets_dir = output_dir / f"{input_path.stem}_assets"
    counter = {"n": 0}

    def save_image(image):
        counter["n"] += 1
        ext = _clean_extension(image.content_type or "")
        filename = f"image{counter['n']:02d}.{ext}"
        assets_dir.mkdir(parents=True, exist_ok=True)
        with image.open() as src, open(assets_dir / filename, "wb") as dst:
            dst.write(src.read())
        return {"src": f"{assets_dir.name}/{filename}"}

    with input_path.open("rb") as f:
        result = mammoth.convert_to_html(
            f, convert_image=mammoth.images.img_element(save_image)
        )

    # Mammoth luon boc anh trong <p> (ke ca khi nam trong o bang: td > p > img).
    # Mac dinh markdownify coi noi dung o bang la "inline" va bo anh khong co alt
    # text (chi giu lai text rong) - phai khai bao "p" thi anh trong bang moi giu lai.
    md_text = markdownify.markdownify(
        result.value, heading_style=markdownify.ATX, keep_inline_images_in=["p"]
    )
    md_text = re.sub(r"\n{3,}", "\n\n", md_text).strip() + "\n"

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{input_path.stem}.md"
    out_path.write_text(md_text, encoding="utf-8")

    warnings = [m.message for m in result.messages if m.type == "warning"]
    return out_path, counter["n"], warnings


def convert_xlsx(input_path: Path, output_dir: Path):
    """Tra ve (duong dan file .md, so sheet). Moi sheet la 1 bang Markdown rieng."""
    # dtype=str: doc moi o nhu text goc, tranh pandas tu suy dien kieu so va lam mat
    # so 0 dung dau (vd ma Material SAP "00000001234567890" bi rut gon thanh so).
    engine = "xlrd" if input_path.suffix.lower() == ".xls" else "openpyxl"
    sheets = pd.read_excel(input_path, sheet_name=None, engine=engine, dtype=str)

    parts = []
    for sheet_name, df in sheets.items():
        parts.append(f"## {sheet_name}\n")
        html_table = df.to_html(index=False, na_rep="")
        parts.append(
            markdownify.markdownify(html_table, heading_style=markdownify.ATX).strip()
        )

    md_text = "\n\n".join(parts).strip() + "\n"

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{input_path.stem}.md"
    out_path.write_text(md_text, encoding="utf-8")
    return out_path, len(sheets)


def iter_input_files(inputs):
    files = []
    for p in inputs:
        if p.is_dir():
            for ext in SUPPORTED_EXTENSIONS:
                files.extend(sorted(p.glob(f"*{ext}")))
        elif p.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(p)
        else:
            print(f"Bo qua (dinh dang khong ho tro): {p}", file=sys.stderr)
    # Bo qua file lock tam cua Office (~$tenfile.docx)
    return [f for f in files if not f.name.startswith("~$")]


def main():
    parser = argparse.ArgumentParser(
        description="Convert .docx/.xlsx/.xls sang Markdown de lam ngu canh cho AI.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help=f"File hoac thu muc dau vao (mac dinh: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Thu muc output (mac dinh: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    inputs = args.inputs or [DEFAULT_INPUT_DIR]
    files = iter_input_files(inputs)

    if not files:
        print("Khong tim thay file .docx/.xlsx/.xls nao de convert.")
        return

    for f in files:
        print(f"Dang convert: {f}")
        try:
            if f.suffix.lower() == ".docx":
                out_path, n_images, warnings = convert_docx(f, args.output)
                print(f"  -> {out_path} ({n_images} anh trong {out_path.stem}_assets/)")
                for w in warnings:
                    print(f"  [canh bao] {w}")
            else:
                out_path, n_sheets = convert_xlsx(f, args.output)
                print(f"  -> {out_path} ({n_sheets} sheet)")
        except Exception as e:
            print(f"  [LOI] Khong convert duoc {f}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
