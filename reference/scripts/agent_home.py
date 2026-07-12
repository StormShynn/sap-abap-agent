#!/usr/bin/env python3
"""Xac dinh thu muc luu state cua CHINH plugin Claude Code sap-abap-agent.

Day la ban tuong duong cua reference/mcp-server/sap_btp_agent/config/paths.py nhung danh
cho cac skill cua plugin nay (sap-daily-learner, sap-context-tool-result-trim,
sap-scaffold-context-summary, sap-analyze-function-spec, sap-handoff, sap-routing-discipline)
- khac voi sap_btp_agent (MCP server ket noi SAP BTP, dung %USERPROFILE%\\.sap-btp-agent\\).

Vi sao can file rieng: cac skill tren la markdown instruction (khong phai Python package cai
qua pip), duoc Claude Code chay ad hoc bang bash/python. Khi plugin duoc cai that (marketplace
hoac git clone o noi khac repo dang lam viec), thu muc lam viec hien tai (cwd) la project cua
END USER dang mo, KHONG phai thu muc cai plugin - nen KHONG the dung duong dan tuong doi kieu
"<workspace>/.sap-abap-agent/..." de luu state on dinh. Phai dung 1 thu muc co dinh theo may/
user, giong het cach paths.py da lam cho sap_btp_agent.

Mac dinh:
    Windows: %USERPROFILE%\\.sap-abap-agent\\
    macOS/Linux: ~/.sap-abap-agent/

Co the override qua SAP_ABAP_AGENT_HOME - vd khi dev/test plugin ngay trong repo nay, tro
thang vao <repo>/.sap-abap-agent de tien xem (cac thu muc con da co san trong .gitignore).

Dung tu SKILL.md (qua CLI, in duong dan tuyet doi + tu tao thu muc):
    python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory/semantic
    -> C:\\Users\\<user>\\.sap-abap-agent\\memory\\semantic

Dung tu script Python khac (import):
    from agent_home import get_agent_home, resolve
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = ".sap-abap-agent"


def get_agent_home() -> Path:
    """Tra ve folder goc luu state cua plugin (chua chac da ton tai - xem resolve())."""
    override = os.environ.get("SAP_ABAP_AGENT_HOME", "").strip()
    if override:
        return Path(override).resolve()
    home = Path.home()
    if not home or str(home) == "":
        raise RuntimeError("Khong xac dinh duoc thu muc home.")
    return home / APP_DIR_NAME


def resolve(subpath: str = "") -> Path:
    """Tra ve get_agent_home()/subpath (dang thu muc), tao neu chua co."""
    target = (get_agent_home() / subpath) if subpath else get_agent_home()
    target.mkdir(parents=True, exist_ok=True)
    return target


def main() -> int:
    subpath = sys.argv[1] if len(sys.argv) > 1 else ""
    print(str(resolve(subpath)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
