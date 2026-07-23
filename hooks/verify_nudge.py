#!/usr/bin/env python
"""Soft nudge: if code was edited but nothing was run (Bash) before Claude
stops, block once and point at sap-verification-before-completion.

Fails open on any error (never blocks a stop due to a bug in this script).
Self-limiting by construction: the sentinel is consumed (deleted) the moment
it is used to block, so the same pending edit can never trigger a second
block. Combined with the stop_hook_active check, this cannot loop.
"""
import contextlib
import json
import os
import re
import sys
import tempfile

CODE_FILE_RE = re.compile(r"\.(abap|asddls|asddlxs|asbdef|asdcls|clas\.abap)$", re.IGNORECASE)


def sentinel_path(session_id):
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", str(session_id) or "default")
    return os.path.join(tempfile.gettempdir(), "sap-abap-agent-verify-pending-" + safe_id)


def is_code_file(file_path):
    if not file_path:
        return False
    normalized = file_path.replace("\\", "/")
    if CODE_FILE_RE.search(normalized):
        return True
    return "/out/" in normalized and "/src/" in normalized


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open - malformed input must never block a stop

    session_id = payload.get("session_id", "default")
    path = sentinel_path(session_id)

    if mode == "mark-edit":
        file_path = (payload.get("tool_input") or {}).get("file_path", "")
        if is_code_file(file_path):
            try:
                with open(path, "w") as f:
                    f.write(file_path)
            except Exception:
                pass
        sys.exit(0)

    if mode == "mark-verified":
        with contextlib.suppress(Exception):
            os.remove(path)
        sys.exit(0)

    if mode == "check-stop":
        if payload.get("stop_hook_active"):
            sys.exit(0)  # defense in depth: never block twice in a row

        if not os.path.exists(path):
            sys.exit(0)

        try:
            with open(path) as f:
                pending_file = f.read().strip()
            os.remove(path)  # consume now: this pending edit can nudge at most once
        except Exception:
            sys.exit(0)  # fail open

        if not pending_file:
            sys.exit(0)

        reason = (
            "Da sua " + pending_file + " nhung chua thay lenh nao chay trong luot nay. "
            "Ap dung skill sap-verification-before-completion truoc khi bao xong: "
            "chay activate/test/script that va dan bang chung that vao cau tra loi."
        )
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
