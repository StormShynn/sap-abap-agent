#!/usr/bin/env python3
"""SessionStart wrapper portable cho Claude Code hook.

Thay the 2 shell command cua `hooks.json` (SessionStart) dung `sed | python` -
vi du:
    f="${CLAUDE_PLUGIN_ROOT}/skills/sap-routing-discipline/SKILL.md"
    [ -f "$f" ] || exit 0
    sed -n '/^---$/,/^---$/!p' "$f" | python -c "import sys, json; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': sys.stdin.read()}}))"

Lenh tren:
  - Su dung `$f` va `sed` => KHONG chay duoc tren Windows PowerShell.
  - Parse thu cong frontmatter.

Wrapper nay:
  1. Lay path plugin root tu env CLAUDE_PLUGIN_ROOT (fallback __file__).
  2. Voi moi skill trong _SKILLS, doc body (bo frontmatter `---`).
  3. Emit 1 JSON object hop le cho hookSpecificOutput (AdditionalContext).
  4. Thoat 0 neu khong co gi (im lang, khong crash).

Logic Y NGUYEN voi lenh shell cu:
  - Lay body (skip phan giua 2 dau `---` dau tien)
  - Wrap trong JSON `hookSpecificOutput.additionalContext`
  - Thoat 0 neu file khong ton tai
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Skill files can thiet cho SessionStart.
_SKILLS = [
    "skills/sap-routing-discipline/SKILL.md",
    "skills/sap-ask-before-guessing/SKILL.md",
]


def _plugin_root() -> Path:
    """Tra ve plugin root (uu tien env CLAUDE_PLUGIN_ROOT)."""
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env_root:
        return Path(env_root)
    # Fallback: .../sap-abap-agent/ (hooks/ nam trong repo root).
    return Path(__file__).resolve().parent.parent


def _strip_frontmatter(text: str) -> str:
    """Bo block frontmatter YAML (giua 2 dau `---` dau tien).

    Tuong duong `sed -n '/^---$/,/^---$/!p'`:
      - In dong KHONG nam trong khoang [line_1 dau `---`, line_2 dau `---`].
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_frontmatter = False
    seen_first = False
    for line in lines:
        if line.strip() == "---":
            if not seen_first:
                # Bat dau frontmatter.
                in_frontmatter = True
                seen_first = True
                continue
            if in_frontmatter:
                # Ket thuc frontmatter.
                in_frontmatter = False
                continue
        if not in_frontmatter:
            out.append(line)
    return "".join(out)


def _load_skill_body(skill_relpath: str) -> str | None:
    """Doc file skill tu plugin root, tra ve body hoac None neu khong ton tai."""
    full_path = _plugin_root() / skill_relpath
    if not full_path.is_file():
        return None
    try:
        text = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    return _strip_frontmatter(text).strip()


def main() -> int:
    chunks: list[str] = []
    for relpath in _SKILLS:
        body = _load_skill_body(relpath)
        if not body:
            continue
        chunks.append(body)

    if not chunks:
        # Khong co gi de inject -> giu im lang (giong `[ -f "$f" ] || exit 0`).
        return 0

    additional = "\n\n---\n\n".join(chunks)
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional,
        }
    }
    # Giong format Python cua lenh shell (`print(json.dumps(...))`).
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
