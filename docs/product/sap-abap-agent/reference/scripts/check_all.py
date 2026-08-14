#!/usr/bin/env python3
"""Run all repo self-checks in one shot.

    python scripts/check_all.py            # validator + security scan + static site check
    python scripts/check_all.py --browser   # + headless-Chromium load of index.html
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(name: str, args: list[str]) -> bool:
    print(f"\n=== {name} ===")
    result = subprocess.run([sys.executable, *args], cwd=ROOT)
    return result.returncode == 0


def main() -> int:
    browser = "--browser" in sys.argv[1:]
    checks = [
        ("validate_plugin", ["scripts/validate_plugin.py"]),
        ("security_scan", ["scripts/security_scan.py"]),
        ("check_site", ["scripts/check_site.py", *(["--browser"] if browser else [])]),
    ]
    results = {name: run(name, args) for name, args in checks}

    print("\n=== summary ===")
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
