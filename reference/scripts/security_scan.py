#!/usr/bin/env python3
"""Static security pattern scan for this repo's own code (MCP server + VS Code extension).

Stdlib-only. Not a full SAST tool — just the concrete vulnerability classes this
project has actually hit, adapted from ruflo-security-audit's pattern catalog:

    python scripts/security_scan.py

Exits 1 if any HIGH-confidence finding exists, 0 otherwise. MEDIUM findings are
printed but don't fail the build (higher false-positive rate, need a human look).

Patterns:
  - Shell/command injection: subprocess/os.system with shell=True + f-string or
    concatenation; TS exec()/execSync() or terminal.sendText() with a template
    literal that interpolates a variable.
  - Unencoded path-segment interpolation: an f-string building a URL/file path
    from a parameter, in a file where a sibling function already uses quote()/
    urllib for the same purpose (signals the encoding step was skipped, not that
    encoding is unnecessary).
  - Hardcoded secrets: high-entropy-looking literals assigned to key/token/secret/
    password-shaped variable names in source files (not docs).

Suppressing a finding already triaged as safe/mitigated: add a trailing
comment containing "security-scan: reviewed" (plus a short reason) on the
SAME line as the flagged code, e.g.:

    terminal.sendText(`...`);  // security-scan: reviewed, guarded by isSafeShellToken above

Suppressed findings still print (as SUPPRESSED, non-blocking) so they stay
auditable instead of silently disappearing - this is for "already fixed, the
static pattern just can't see the fix", not a way to make a real finding go
away unreviewed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HIGH: list[str] = []
MEDIUM: list[str] = []
SUPPRESSED: list[str] = []

SKIP_DIRS = {".git", "node_modules", "__pycache__", "in", "out", "dist"}
SUPPRESS_MARKER = "security-scan: reviewed"


def iter_files(*suffixes: str):
    for p in ROOT.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.suffix in suffixes:
            yield p


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def is_suppressed(text: str, pos: int) -> bool:
    line_start = text.rfind("\n", 0, pos) + 1
    line_end = text.find("\n", pos)
    if line_end == -1:
        line_end = len(text)
    return SUPPRESS_MARKER in text[line_start:line_end]


def report(bucket: list[str], suppressed_pos: tuple[str, int] | None, msg: str) -> None:
    """Append `msg` to `bucket`, unless `suppressed_pos` = (text, pos) is marked
    with SUPPRESS_MARKER on its line - then it goes to SUPPRESSED instead."""
    if suppressed_pos and is_suppressed(*suppressed_pos):
        SUPPRESSED.append(msg)
    else:
        bucket.append(msg)


def check_python_shell_injection() -> None:
    pattern = re.compile(
        r"(subprocess\.\w+|os\.system)\s*\([^)]*shell\s*=\s*True[^)]*\)", re.DOTALL
    )
    fstring_marker = re.compile(r"f[\"']|\.format\(|%\s*\(")
    for path in iter_files(".py"):
        text = read(path)
        for m in pattern.finditer(text):
            if fstring_marker.search(m.group(0)):
                report(HIGH, (text, m.start()),
                    f"{path.relative_to(ROOT)}:{line_no(text, m.start())}: "
                    f"shell=True with an interpolated string — use execFileSync/list-form "
                    f"args instead: {m.group(0)[:80]!r}"
                )


def check_ts_exec_injection() -> None:
    exec_pattern = re.compile(r"\b(exec|execSync|spawn)\s*\(\s*(`[^`]*\$\{[^`]*`)")
    sendtext_pattern = re.compile(r"\.sendText\s*\(\s*(`[^`]*\$\{[^`]*`)")
    for path in iter_files(".ts", ".js"):
        text = read(path)
        for m in exec_pattern.finditer(text):
            report(HIGH, (text, m.start()),
                f"{path.relative_to(ROOT)}:{line_no(text, m.start())}: "
                f"{m.group(1)}() called with an interpolated template literal — "
                f"an untrusted value here runs as shell syntax: {m.group(0)[:90]!r}"
            )
        for m in sendtext_pattern.finditer(text):
            report(HIGH, (text, m.start()),
                f"{path.relative_to(ROOT)}:{line_no(text, m.start())}: "
                f"terminal.sendText() with an interpolated template literal — quote/validate "
                f"the interpolated value first (breaks on spaces, and is shell-injectable if "
                f"the value comes from user/workspace config): {m.group(0)[:90]!r}"
            )


def check_unencoded_path_interpolation() -> None:
    quote_using_files: set[Path] = set()
    fstring_path = re.compile(r'f"[^"]*\{[a-zA-Z_][a-zA-Z0-9_]*\}[^"]*"')
    async_def = re.compile(r"async def (\w+)\([^)]*\)(?:\s*->\s*[^:\n]+)?:")
    for path in iter_files(".py"):
        text = read(path)
        if "quote(" in text:
            quote_using_files.add(path)

    for path in quote_using_files:
        text = read(path)
        for m in async_def.finditer(text):
            body_start = m.end()
            next_def = async_def.search(text, body_start)
            body_end = next_def.start() if next_def else len(text)
            body = text[body_start:body_end]
            if "quote(" in body:
                continue
            for fm in fstring_path.finditer(body):
                if "/" not in fm.group(0):
                    continue
                abs_pos = body_start + fm.start()
                report(MEDIUM, (text, abs_pos),
                    f"{path.relative_to(ROOT)}:{line_no(text, abs_pos)}: "
                    f"'{m.group(1)}' builds a path with an unencoded f-string "
                    f"({fm.group(0)[:70]!r}), but sibling methods in this file use quote() — "
                    f"confirm this parameter can't contain '/','?','#'"
                )


def check_hardcoded_secrets() -> None:
    pattern = re.compile(
        r'(?i)\b(api[_-]?key|secret|password|token|access[_-]?key)\b\s*[:=]\s*'
        r'["\']([A-Za-z0-9_\-/+]{20,})["\']'
    )
    placeholder = re.compile(r"(?i)your[_-]|xxx|placeholder|example|<.*>|\$\{|change[_-]?me")
    for path in iter_files(".py", ".ts", ".js", ".json"):
        text = read(path)
        for m in pattern.finditer(text):
            value = m.group(2)
            if placeholder.search(value):
                continue
            report(MEDIUM, (text, m.start()),
                f"{path.relative_to(ROOT)}:{line_no(text, m.start())}: "
                f"literal assigned to '{m.group(1)}'-shaped name — verify this isn't a real "
                f"secret committed to source: {m.group(0)[:60]!r}"
            )


def main() -> int:
    check_python_shell_injection()
    check_ts_exec_injection()
    check_unencoded_path_interpolation()
    check_hardcoded_secrets()

    if SUPPRESSED:
        print(f"--- {len(SUPPRESSED)} suppressed finding(s) (marked '{SUPPRESS_MARKER}', not blocking) ---")
        for s in SUPPRESSED:
            print(f"  SUPPRESSED  {s}")
        print()

    if MEDIUM:
        print(f"--- {len(MEDIUM)} medium-confidence finding(s) (review, non-blocking) ---")
        for m in MEDIUM:
            print(f"  MEDIUM  {m}")
        print()

    if HIGH:
        print(f"--- {len(HIGH)} high-confidence finding(s) ---")
        for h in HIGH:
            print(f"  HIGH  {h}")
        print(f"\nsecurity_scan.py: {len(HIGH)} high-confidence finding(s)")
        return 1

    print(f"security_scan.py: no high-confidence findings ({len(MEDIUM)} medium to review)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
