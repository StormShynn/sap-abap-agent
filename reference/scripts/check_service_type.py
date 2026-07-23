#!/usr/bin/env python3
"""Check service type consistency in code + docs.

Service type taxonomy (2026-07):
  s4hc_(private) | s4hc_(public) | btp | onprem

Legacy enum values that should be migrated away:
  - "s4hc"  (now aliased to s4hc_(public) for backward-compat)
  - "btp"   (kept as a separate value; flag user-facing labels that
             collapse it with the old taxonomy, e.g. "s4hc / btp / onprem")

Scans:
  1. reference/mcp-server/sap_btp_agent/**/*.py
     reject hardcoded prompt literal "Service type (s4hc / btp / onprem)"
     or the half-migrated "(s4hc_(private) / s4hc_(public) / onprem)".
     Whitelist: store.py + cli/__init__.py + tools/registry.py
     (those DEFINE the migration).
  2. ALL user-facing markdown/html files in the repo (see DOC_DIRS).
     Flag any of these legacy patterns:
       - "Service type (s4hc / btp / onprem)"
       - "s4hc / btp" / "btp / onprem" / "s4hc / onprem" (with / or | or \\)
       - any mention of "s4hc" as a service-type ENUM VALUE (not as part
         of "sap-btp-agent", "s4hana.cloud.sap", or generic prose).

Run:
  python scripts/check_service_type.py

Exit codes:
  0 = no findings
  1 = findings (please fix)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# File extensions treated as "user-facing docs"
DOC_EXTS = {".md", ".html", ".txt"}

# Directories containing user-facing docs (recursive).
DOC_DIRS = [
    ROOT / "agents",
    ROOT / "skills",
    ROOT / "commands",
    ROOT / "hooks",
    ROOT / "reference" / "modules",
    ROOT / "reference" / ".vscode-extensions",
    ROOT / ".codex",
    ROOT / ".claude-plugin",
]

# Top-level docs to scan (root of repo).
ROOT_DOCS = [
    ROOT / "README.md",
    ROOT / "index.html",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / "CODE_OF_CONDUCT.md",
    ROOT / "SKILL_TEMPLATE.md",
]

# Files allowed to mention the legacy taxonomy (they DEFINE the migration:
# default values, aliases, docstrings explaining the change).
CODE_WHITELIST = {
    ROOT / "reference" / "mcp-server" / "sap_btp_agent" / "config" / "store.py",
    ROOT / "reference" / "mcp-server" / "sap_btp_agent" / "cli" / "__init__.py",
    ROOT / "reference" / "mcp-server" / "sap_btp_agent" / "tools" / "registry.py",
    Path(__file__).resolve(),  # this lint script documents the legacy forms
}

# Legacy prompt literals (must NOT appear anywhere user-facing).
OLD_PROMPT_LITERAL = "Service type (s4hc / btp / onprem)"
HALF_MIGRATED_PROMPT = re.compile(
    r"Service type \(s4hc_\(private\) / s4hc_\(public\) / onprem\)"
)

# Pair patterns with separators / | \\. Matches "s4hc / btp", "s4hc|btp",
# "s4hc \\ btp", etc. These are the legacy enum listings.
LEGACY_PAIR_PATTERN = re.compile(
    r"(?<!_)\bs4hc\b\s*[/|\\\\]\s*(btp|onprem)\b"
    r"\b(btp)\s*[/|\\\\]\s*(onprem)\b|"
    r"\b(s4hc)\s*[/|\\\\]\s*(s4hc|btp)\s*[/|\\\\]\s*(onprem)\b"
)

# Standalone "s4hc" word boundary (NOT as part of larger identifier).
# Skips matches inside "sap-btp-agent", "s4hana", "s4hc_(private)", etc.
STANDALONE_S4HC = re.compile(r"\b(?<![-_a-z])s4hc\b(?![-_(a-z])")

FAILURES: list[str] = []
WARNINGS: list[str] = []


def _add(fail: bool, message: str) -> None:
    (FAILURES if fail else WARNINGS).append(message)


def _iter_docs() -> list[Path]:
    files: list[Path] = []
    for path in ROOT_DOCS:
        if path.exists():
            files.append(path)
    for d in DOC_DIRS:
        if not d.exists():
            continue
        for ext in DOC_EXTS:
            files.extend(d.rglob(f"*{ext}"))
    # Skip this lint script itself
    return [p for p in files if p.resolve() not in CODE_WHITELIST]


def _check_code() -> None:
    target = ROOT / "reference" / "mcp-server" / "sap_btp_agent"
    if not target.exists():
        _add(False, f"Skip code scan: {target} khong ton tai")
        return

    patterns = [
        re.compile(re.escape(OLD_PROMPT_LITERAL)),
        HALF_MIGRATED_PROMPT,
    ]
    for py in target.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        if py.resolve() in CODE_WHITELIST:
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pat in patterns:
            for m in pat.finditer(text):
                rel = py.relative_to(ROOT)
                _add(
                    True,
                    f"{rel}: legacy service-type literal con sot: {m.group(0)!r}",
                )


def _check_docs() -> None:
    total = 0
    for path in _iter_docs():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(ROOT)

        if OLD_PROMPT_LITERAL in text:
            n = text.count(OLD_PROMPT_LITERAL)
            _add(True, f"{rel}: {n}x legacy prompt literal")

        for m in LEGACY_PAIR_PATTERN.finditer(text):
            _add(
                True,
                f"{rel}: legacy service-type enum listing: {m.group(0)!r}",
            )
            total += 1
            break  # 1 finding per file is enough; the fix is global


def main() -> int:
    _check_code()
    _check_docs()

    for w in WARNINGS:
        print(f"  warn: {w}")
    for f in FAILURES:
        print(f"  FAIL  {f}")

    if FAILURES:
        print(f"\\n{len(FAILURES)} loi service type can fix.")
        return 1
    print("OK - service type consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
