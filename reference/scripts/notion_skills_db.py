#!/usr/bin/env python3
"""Resolve id database Notion "SAP Skills" (default plugin + optional override).

Default (hardcode trong plugin — moi user dung chung de hoc skill notes):
  StormShynn shared DB 9d54b58613ad485f8b8f19909adbb219

Override (tuy chon — DB rieng cong ty / ca nhan):
  env SAP_ABAP_AGENT_NOTION_SKILLS_DB=<id>
  hoac pin file <agent-home>/notion-skills-db.id

Thu tu resolve: env → pin file → DEFAULT_DATABASE_ID

CLI:
  python notion_skills_db.py get [--source]
  python notion_skills_db.py default
  python notion_skills_db.py set <id-or-url>
  python notion_skills_db.py clear
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from agent_home import get_agent_home

PIN_NAME = "notion-skills-db.id"
ENV_KEY = "SAP_ABAP_AGENT_NOTION_SKILLS_DB"

# StormShynn shared "SAP Skills" — default cho moi ban cai plugin.
DEFAULT_DATABASE_ID = "9d54b58613ad485f8b8f19909adbb219"

_HEX32 = re.compile(r"[0-9a-fA-F]{32}")


def pin_path() -> Path:
    return get_agent_home() / PIN_NAME


def normalize_database_id(raw: str) -> str:
    """Lay 32-hex id tu raw id hoac URL Notion (notion.so / app.notion.com)."""
    cleaned = (raw or "").strip()
    if not cleaned:
        raise ValueError("database id rong")
    # Hex thuan (co the co dau - UUID style).
    compact = cleaned.replace("-", "")
    if len(compact) == 32 and all(c in "0123456789abcdefABCDEF" for c in compact):
        return compact.lower()
    # URL / path — tim doan 32 hex dau tien (thuong la id DB trong URL).
    match = _HEX32.search(cleaned.replace("-", ""))
    if match:
        return match.group(0).lower()
    # Fallback: token cuoi path (tuong thich cu).
    token = cleaned.rstrip("/").split("/")[-1].split("?")[0].replace("-", "")
    if len(token) >= 32 and all(c in "0123456789abcdefABCDEF" for c in token[:32]):
        return token[:32].lower()
    return cleaned


def get_pinned_id() -> str | None:
    """Chi env hoac pin file — KHONG gom default."""
    env = os.environ.get(ENV_KEY, "").strip()
    if env:
        return normalize_database_id(env)
    path = pin_path()
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    return normalize_database_id(text)


def resolve_database_id() -> tuple[str, str]:
    """Tra (id, source) voi source ∈ env|pin|default."""
    env = os.environ.get(ENV_KEY, "").strip()
    if env:
        return normalize_database_id(env), "env"
    path = pin_path()
    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return normalize_database_id(text), "pin"
    return DEFAULT_DATABASE_ID, "default"


def get_database_id() -> str:
    return resolve_database_id()[0]


def set_pinned_id(database_id: str) -> Path:
    cleaned = normalize_database_id(database_id)
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
        db_id, source = resolve_database_id()
        if "--source" in args[1:]:
            print(f"{db_id}\t{source}")
        else:
            print(db_id)
        return 0
    if cmd == "default":
        print(DEFAULT_DATABASE_ID)
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
