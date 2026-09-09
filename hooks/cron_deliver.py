#!/usr/bin/env python
"""SessionStart hook - "deliver" ket qua cron job (xem reference/scripts/cron_manage.py)
vao phien chat Claude Code ke tiep khi user mo len - giong tinh than "delivery" cua Hermes
Agent (gui ve Telegram/Slack/...) nhung tan dung co che SessionStart injection co san cua
Claude Code plugin thay vi tu xay 1 kenh thong bao rieng.

Doc <agent-home>/cron/pending/*.md (ghi boi cron_manage.py khi tick chay 1 job den han),
neu co thi gop noi dung lam additionalContext, roi di chuyen file da doc sang
<agent-home>/cron/delivered/ (KHONG xoa - giu tinh than "khong xoa kien thuc" chung cua
plugin nay).

Fail-open (giong het triet ly hooks/error_reporter.py, hooks/verify_nudge.py): bat ky loi
nao (agent-home chua ton tai, file hong...) -> exit(0) im lang, KHONG bao gio chan session
khoi mo duoc.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
from pathlib import Path

AGENT_HOME = Path(os.environ.get("SAP_ABAP_AGENT_HOME", str(Path.home() / ".sap-abap-agent")))
PENDING_DIR = AGENT_HOME / "cron" / "pending"
DELIVERED_DIR = AGENT_HOME / "cron" / "delivered"
# Tran chan 1 chuoi tick loi lien tuc bom qua nhieu context vao 1 session moi - phan con
# lai se duoc deliver o lan mo session ke tiep, khong mat (van nam trong pending/).
MAX_CHARS = 4000


def main() -> int:
    try:
        if not PENDING_DIR.exists():
            return 0
        files = sorted(PENDING_DIR.glob("*.md"))
        if not files:
            return 0

        parts: list[str] = []
        delivered: list[Path] = []
        total = 0
        for f in files:
            text = f.read_text(encoding="utf-8", errors="replace")
            if total + len(text) > MAX_CHARS and parts:
                break
            parts.append(text)
            total += len(text)
            delivered.append(f)

        if not parts:
            return 0

        context = (
            "📬 Cron job (sap-daily-learner) co ket qua moi tu luc ban khong mo Claude Code:\n\n"
            + "\n---\n".join(parts)
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }))

        DELIVERED_DIR.mkdir(parents=True, exist_ok=True)
        for f in delivered:
            with contextlib.suppress(OSError):
                f.replace(DELIVERED_DIR / f.name)
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
