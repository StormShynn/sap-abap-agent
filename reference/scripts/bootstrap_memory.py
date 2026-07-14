#!/usr/bin/env python3
"""Khoi tao idempotent cho 3 tang memory (semantic/episodic/procedural) + cache cua
plugin sap-abap-agent.

Ly do can script nay: cac skill (sap-daily-learner, sap-bootstrap-system-context, ...) doc
LEARNING_PROGRESS.md + knowledge_graph.jsonl ngay dau session. Neu <agent-home>/memory/semantic
chua ton tai (lan dau dung plugin), cac skill nay in loi va dung. Script nay tao san toan
bo cay thu muc + file mac dinh, IDEMPOTENT (goi nhieu lan khong hong, KHONG ghi de file da
co noi dung cua user).

Vi tri luu: giong agent_home.py - mac dinh %USERPROFILE%\\.sap-abap-agent\\ (Windows) hoac
~/.sap-abap-agent/ (macOS/Linux); override qua SAP_ABAP_AGENT_HOME.
"""
from __future__ import annotations
import argparse, json, os, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_home import get_agent_home

DEFAULT_PROGRESS_FILENAME = "LEARNING_PROGRESS.md"
DEFAULT_KNOWLEDGE_GRAPH_FILENAME = "knowledge_graph.jsonl"
DEFAULT_EPISODIC_INDEX_FILENAME = "index.jsonl"
PROGRESS_MODULES = ["SD", "FI", "MM", "CO", "PP"]


def render_progress(today):
    lines = [
        "# SAP Learning Progress",
        "",
        "Last updated: " + today,
        "Session count: 0",
        "Total skills created: 0",
        "Memory tier loaded: semantic",
        "",
        "## Module Progress",
        "",
        "| Module | Level | Topics Mastered | Topics Pending | Last Activity |",
        "|--------|-------|----------------|----------------|---------------|",
    ]
    for m in PROGRESS_MODULES:
        lines.append("| " + m + " | beginner | 0 | 5 | never |")
    lines += [
        "",
        "## Recommended Next Module",
        "> **Moi bat dau? Hay hoc MM (Materials Management)** - module pho bien nhat, de tiep can voi quy trinh procurement hang ngay.",
        "",
        "## Auto-Created Skills",
        "*(chua co skill nao)*",
        "",
    ]
    return "\n".join(lines)


def _ensure_dir(path):
    if path.exists():
        return False
    path.mkdir(parents=True, exist_ok=True)
    return True


def _ensure_file(path, default_content, *, force=False):
    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError("Khong doc duoc {}: {}".format(path, exc)) from exc
        if existing.strip() and not force:
            return "kept"
        path.write_text(default_content, encoding="utf-8")
        return "overwritten" if existing.strip() else "created"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_content, encoding="utf-8")
    return "created"


def _resolve_under_home(home, subpath):
    """Resolve subpath inside <agent-home>; reject absolute or parent-escape paths."""
    candidate = (home / subpath).resolve()
    root = home.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path phai nam trong <agent-home>: {}".format(subpath)) from exc
    return candidate


def bootstrap(home=None, *, reset_progress=False, ensure_dirs=None, ensure_files=None):
    home = (home or get_agent_home()).resolve()
    created = []
    skipped = []
    overwritten = []
    dirs = [
        home / "memory" / "semantic" / "lessons",
        home / "memory" / "semantic" / "notes",
        home / "memory" / "episodic" / "archive",
        home / "memory" / "procedural" / "skills",
        home / "cache",
    ]
    for d in dirs:
        (created if _ensure_dir(d) else skipped).append(str(d))
    progress_path = home / "memory" / "semantic" / DEFAULT_PROGRESS_FILENAME
    pa = _ensure_file(progress_path, render_progress(date.today().isoformat()), force=reset_progress)
    if pa == "created":
        created.append(str(progress_path))
    elif pa == "overwritten":
        overwritten.append(str(progress_path))
    else:
        skipped.append(str(progress_path))
    kg_path = home / "memory" / "semantic" / DEFAULT_KNOWLEDGE_GRAPH_FILENAME
    ka = _ensure_file(kg_path, "")
    if ka == "created":
        created.append(str(kg_path))
    else:
        skipped.append(str(kg_path))
    index_path = home / "memory" / "episodic" / DEFAULT_EPISODIC_INDEX_FILENAME
    ia = _ensure_file(index_path, "")
    if ia == "created":
        created.append(str(index_path))
    else:
        skipped.append(str(index_path))

    for subpath in ensure_dirs or []:
        path = _resolve_under_home(home, subpath)
        (created if _ensure_dir(path) else skipped).append(str(path))

    for subpath, content in ensure_files or []:
        path = _resolve_under_home(home, subpath)
        action = _ensure_file(path, content)
        if action == "created":
            created.append(str(path))
        else:
            skipped.append(str(path))

    return {"home": str(home), "created": created, "skipped": skipped, "overwritten": overwritten}


def main():
    parser = argparse.ArgumentParser(
        description="Khoi tao idempotent cho 3 tang memory (semantic/episodic/procedural) + cache."
    )
    parser.add_argument("--reset-progress", action="store_true",
                        help="Ghi lai LEARNING_PROGRESS.md mac dinh (chi dung khi file bi hong/tron).")
    parser.add_argument("--home", default=None,
                        help="Override <agent-home> (mac dinh: $SAP_ABAP_AGENT_HOME hoac ~/.sap-abap-agent).")
    parser.add_argument("--ensure-dir", action="append", default=[], metavar="SUBPATH",
                        help="Tao them folder trong <agent-home> neu chua co; co the lap lai.")
    parser.add_argument("--ensure-file", action="append", default=[], metavar="SUBPATH[=CONTENT]",
                        help="Tao them file trong <agent-home> neu chua co; co the lap lai.")
    args = parser.parse_args()
    home_override = args.home or os.environ.get("SAP_ABAP_AGENT_HOME") or None
    try:
        home = Path(home_override).resolve() if home_override else get_agent_home()
        ensure_files = []
        for specification in args.ensure_file:
            subpath, separator, content = specification.partition("=")
            ensure_files.append((subpath, content if separator else ""))
        result = bootstrap(
            home=home,
            reset_progress=args.reset_progress,
            ensure_dirs=args.ensure_dir,
            ensure_files=ensure_files,
        )
    except Exception as exc:
        print("[bootstrap-memory] LOI: {}".format(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
