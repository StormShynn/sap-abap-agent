#!/usr/bin/env python3
"""Pre-flight check may moi truoc khi onboard SAP ABAP Agent (team rollout).

Usage:
  python validate_team_setup.py
  python validate_team_setup.py --persona A   # ABAP Dev (default)
  python validate_team_setup.py --persona B   # Functional
  python validate_team_setup.py --persona C   # Key user (Claude plugin only)

Exit 0 = tat ca bat buoc PASS; exit 1 = thieu muc required.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass


DEFAULT_NOTION_DB = "9d54b58613ad485f8b8f19909adbb219"


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True


def _run(cmd: list[str]) -> tuple[bool, str]:
    try:
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        text = (out.stdout or out.stderr or "").strip()
        return out.returncode == 0, text.splitlines()[0] if text else f"exit {out.returncode}"
    except FileNotFoundError:
        return False, "command not found"
    except Exception as err:  # noqa: BLE001 — preflight fail-open detail
        return False, str(err)


def check_python() -> Check:
    ver = sys.version_info
    ok = ver >= (3, 10)
    return Check(
        "Python >= 3.10",
        ok,
        f"{ver.major}.{ver.minor}.{ver.micro}",
        required=True,
    )


def check_mcp_on_path() -> Check:
    path = shutil.which("mcp-sap-connect")
    if path:
        return Check("mcp-sap-connect on PATH", True, path, required=True)
    ok, detail = _run([sys.executable, "-m", "mcp_sap_connect", "--help"])
    if ok:
        return Check(
            "mcp-sap-connect module",
            True,
            "python -m mcp_sap_connect OK (add Scripts to PATH)",
            required=True,
        )
    return Check(
        "mcp-sap-connect on PATH",
        False,
        "pip install \"mcp-sap-connect[win-dpapi]\" rồi doctor",
        required=True,
    )


def check_doctor() -> Check:
    ok, detail = _run([sys.executable, "-m", "mcp_sap_connect.doctor"])
    if not ok:
        ok2, detail2 = _run(["mcp-sap-connect", "doctor"])
        ok, detail = ok2, detail2
    return Check("mcp-sap-connect doctor", ok, detail[:200], required=False)


def check_claude() -> Check:
    ok, detail = _run(["claude", "--version"])
    return Check(
        "Claude Code CLI (claude)",
        ok,
        detail if ok else "install Claude Code — cần cho plugin/hooks",
        required=True,
    )


def check_notion_learning() -> Check:
    """Resolve Notion SAP Skills id (default StormShynn shared = learning ready id)."""
    script = os.path.join(os.path.dirname(__file__), "notion_skills_db.py")
    if not os.path.isfile(script):
        return Check("Notion learning DB", False, "notion_skills_db.py missing", required=False)
    ok, detail = _run([sys.executable, script, "get", "--source"])
    if not (ok and detail.strip()):
        return Check(
            "Notion learning DB",
            False,
            "resolve failed — expect default StormShynn shared DB",
            required=False,
        )
    parts = detail.strip().split()
    db_id = parts[0] if parts else ""
    source = parts[1] if len(parts) > 1 else "?"
    short = (db_id[:12] + "…") if len(db_id) > 12 else db_id
    if source == "default" and db_id.replace("-", "") == DEFAULT_NOTION_DB:
        tip = f"{short} (default) — Accept Share + /mcp Notion OAuth để đọc/ghi skill"
    elif source in ("pin", "env"):
        tip = f"{short} ({source} override) — Share DB công ty + OAuth; clear để về default"
    else:
        tip = f"{short} ({source})"
    return Check("Notion learning DB", True, tip, required=False)


def check_cursor_pack_script() -> Check:
    script = os.path.join(os.path.dirname(__file__), "emit_cursor_mcp_pack.py")
    if os.path.isfile(script):
        return Check(
            "Cursor MCP pack script",
            True,
            "emit_cursor_mcp_pack.py (docs-only host)",
            required=False,
        )
    return Check("Cursor MCP pack script", False, "missing", required=False)


def run_checks(persona: str) -> list[Check]:
    persona = persona.upper()
    checks = [check_python()]
    if persona in ("A", "B"):
        checks.append(check_mcp_on_path())
        checks.append(check_doctor())
    if persona in ("A", "B", "C"):
        checks.append(check_claude())
        checks.append(check_notion_learning())
        checks.append(check_cursor_pack_script())
    return checks


def _print_learning_next_steps(checks: list[Check]) -> None:
    notion = next((c for c in checks if c.name == "Notion learning DB"), None)
    print("Learning-ready next (optional):")
    if notion and notion.ok:
        print(f"  • Notion: {notion.detail}")
    else:
        print(
            "  • Notion: python reference/scripts/notion_skills_db.py get --source"
        )
    print(
        "  • Cursor/VS Code only: python reference/scripts/emit_cursor_mcp_pack.py -o …"
    )
    print("  • Core MCP = sap-connect + sap-dict-bridge + cds-kb + mcp-sap-docs-btp")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--persona",
        default="A",
        choices=["A", "B", "C", "a", "b", "c"],
        help="A=ABAP Dev, B=Functional, C=Key user",
    )
    args = parser.parse_args(argv)
    checks = run_checks(args.persona)
    print(f"SAP ABAP Agent pre-flight (persona {args.persona.upper()})")
    print("-" * 56)
    failed_required = 0
    for c in checks:
        mark = "PASS" if c.ok else ("FAIL" if c.required else "WARN")
        if not c.ok and c.required:
            failed_required += 1
        req = "required" if c.required else "optional"
        print(f"[{mark}] {c.name} ({req}): {c.detail}")
    print("-" * 56)
    if failed_required:
        print(f"Result: NOT READY ({failed_required} required check(s) failed)")
        print("Xem docs/onboarding-guide.md + docs/rollout-guide.md")
        return 1
    print("Result: READY — tiếp tục onboarding-guide / rollout-guide")
    _print_learning_next_steps(checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
