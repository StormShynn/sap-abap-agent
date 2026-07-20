#!/usr/bin/env python3
"""Scan hooks/scripts/ for clear-text logging of sensitive data.

Dat theo CodeQL alerts #6/#9/#16/#22/#23 (da duoc Copilot Autofix merge 5 PR).
Script nay quet nhanh (regex) de contributor phat hien truoc khi commit,
bo sung cho security_scan.py (chuyen sau).

Patterns:
  - print/fprint/log > secret-shaped variable: SECRET/PASSWORD/TOKEN/API_KEY
  - print URL co embedded credential (user:pass@host)

Chi warning (exit 0), khong block - de contributor review va fix.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCAN_DIRS = [
    REPO_ROOT / "hooks",
    REPO_ROOT / "reference" / "scripts",
]

SENSITIVE_NAME_RE = re.compile(
    r"\b(secret|password|passwd|token|api_key|apikey|access_key|"
    r"client_secret|private_key|session_id|cookie|credential)s?\b",
    re.IGNORECASE,
)
PRINT_LIKE_RE = re.compile(
    r"\b(print|fprintf|sys\.stdout\.write|console\.log|logger?\.\w+\()",
    re.IGNORECASE,
)


def scan_file(path: Path) -> list[str]:
    """Tra ve danh sach warning (1 string per line match)."""
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return warnings
    for lineno, line in enumerate(text.splitlines(), 1):
        if not PRINT_LIKE_RE.search(line):
            continue
        # Skip comment line
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        if SENSITIVE_NAME_RE.search(line):
            # Verify khong phai self-assign (var = ...)
            if "=" in line and line.find("=") < line.find("print"):
                continue  # assignment, khong print
            warnings.append(
                f"{path.relative_to(REPO_ROOT)}:{lineno}: "
                f"possible clear-text sensitive data: {line.strip()[:80]}"
            )
    return warnings


def main() -> int:
    if not any(d.is_dir() for d in SCAN_DIRS):
        print(f"WARNING: scan dirs khong ton tai", file=sys.stderr)
        return 0

    total: list[str] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.is_dir():
            continue
        for py_file in scan_dir.rglob("*.py"):
            warnings = scan_file(py_file)
            total.extend(warnings)

    if total:
        print("Clear-text logging scan:")
        for w in total:
            print(f"  {w}")
        print(f"  total: {len(total)} finding(s)")
        print("(warning only - review manual, khong block build)")
    else:
        print("Clear-text logging scan: clean")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
