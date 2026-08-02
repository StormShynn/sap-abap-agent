#!/usr/bin/env python3
"""Pin / doc id database Notion "SAP Skills" (tranh tao trung theo ten).

Pin file (mot dong, id page/collection):
  <agent-home>/notion-skills-db.id

Override env (uu tien hon file):
  SAP_ABAP_AGENT_NOTION_SKILLS_DB=<id>

CLI:
  python notion_skills_db.py get
  python notion_skills_db.py set <id>
  python notion_skills_db.py clear
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from agent_home import get_agent_home

PIN_NAME = "notion-skills-db.id"
ENV_KEY = "SAP_ABAP_AGENT_NOTION_SKILLS_DB"


def pin_path() -> Path:
    return get_agent_home() / PIN_NAME


def get_pinned_id() -> str | None:
    env = os.environ.get(ENV_KEY, "").strip()
    if env:
        return env
    path = pin_path()
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def set_pinned_id(database_id: str) -> Path:
    cleaned = database_id.strip()
    if not cleaned:
        raise ValueError("database id rong")
    # Cho phep URL Notion — lay doan id 32 hex cuoi neu co.
    if "notion.so" in cleaned or "-" in cleaned:
        token = cleaned.rstrip("/").split("/")[-1].split("?")[0]
        token = token.replace("-", "")
        if len(token) >= 32 and all(c in "0123456789abcdefABCDEF" for c in token[:32]):
            cleaned = token[:32]
    home = get_agent_home()
    home.mkdir(parents=True, exist_ok=True)
    path = home / PIN_NAME
    path.write_text(cleaned + "\n", encoding="utf-8")
    return path


def clear_pinned_id() -> bool:
    path = pin_path()
    if path.is_file():
        path.unlink()
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    cmd = args[0]
    if cmd == "get":
        pinned = get_pinned_id()
        if not pinned:
            print("", end="")
            return 1
        print(pinned)
        return 0
    if cmd == "set":
        if len(args) < 2:
            print("Usage: notion_skills_db.py set <id-or-url>", file=sys.stderr)
            return 2
        path = set_pinned_id(args[1])
        print(str(path))
        return 0
    if cmd == "clear":
        clear_pinned_id()
        return 0
    print(f"Unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
