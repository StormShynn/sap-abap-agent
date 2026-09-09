#!/usr/bin/env python3
"""PostToolUse hook - canh bao SELECT * trong file .abap vua edit.

Thay the shell pipeline cu (PostToolUse / Edit|Write):
    file=$(python -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', '') or '')"); if [ -n "$file" ] && [[ "$file" == *.abap ]] && grep -nE 'SELECT[[:space:]]+\\*' "$file" >/dev/null 2>&1; then echo "[sap-abap-agent] SELECT * found in $file - prefer explicit field lists." >&2; fi; exit 0

Lenh shell nay doc stdin JSON tu Claude Code (hook payload), lay `tool_input.file_path`,
kiem tra:
  1. File co ton tai.
  2. File co duoi `.abap`.
  3. Co chua pattern `SELECT *` (SELECT + space(s) + *).
Neu match: in canh bao ra stderr. Luon thoat 0 (canh bao, khong block).

Wrapper Python portable, cung logic Y NGUYEN.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_SELECT_STAR = re.compile(r"\bSELECT\s+\*", re.IGNORECASE)


def _read_hook_payload() -> dict | None:
    """Doc JSON payload tu stdin (Claude Code PostToolUse hook contract)."""
    try:
        raw = sys.stdin.read()
    except OSError:
        return None
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def main() -> int:
    payload = _read_hook_payload()
    if payload is None:
        # Khong co payload -> giu im lang (giong `[ -n "$file" ] && ...` fail an toan).
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    if not file_path:
        return 0

    path = Path(file_path)
    # Tuong duanh `[[ "$file" == *.abap ]]` - case-sensitive glob.
    if path.suffix.lower() != ".abap":
        return 0

    if not path.is_file():
        return 0

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    if _SELECT_STAR.search(text):
        # Tuong duong `echo "[sap-abap-agent] SELECT * found in $file ..." >&2`.
        print(
            f"[sap-abap-agent] SELECT * found in {file_path} - "
            "prefer explicit field lists.",
            file=sys.stderr,
        )
    # Luon exit 0 (giong `exit 0` cuoi lenh shell).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
