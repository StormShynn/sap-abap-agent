#!/usr/bin/env python
"""
Setup GitHub Labels cho SAP ABAP Agent repo.

Tạo các label cần thiết cho auto-error-reporter:
  - auto-reported  🟣 — Issue tự động tạo bởi CI engine
  - auto-fix       🟢 — Fix tự động đính kèm

Không cần gh CLI — chỉ dùng Python std lib + GITHUB_TOKEN.
Chạy:  python reference/scripts/setup_labels.py

Yêu cầu:
  - GITHUB_TOKEN hoặc GH_TOKEN env var (personal access token)
  - Hoặc đã login gh CLI (nó sẽ tự lấy token từ keyring)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

REPO = "StormShynn/sap-abap-agent"

LABELS: list[dict[str, Any]] = [
    {
        "name": "auto-reported",
        "color": "5319e7",
        "description": "Issue được tự động tạo bởi error reporter (CI engine)",
    },
    {
        "name": "auto-fix",
        "color": "0e8a16",
        "description": "Fix được tự động phát hiện và đính kèm vào issue",
    },
]

API_URL = f"https://api.github.com/repos/{REPO}/labels"


def _get_token() -> str | None:
    """Lấy token: GITHUB_TOKEN → GH_TOKEN → gh auth token."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    # Fallback: thử lấy token từ gh CLI (nếu có)
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _create_label(token: str, label: dict[str, Any]) -> bool:
    """Tạo 1 label trên GitHub repo. Trả về True nếu thành công hoặc đã tồn tại."""
    data = json.dumps(label).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "sap-abap-agent-setup-labels",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_data = json.loads(resp.read().decode())
            print(f"  ✅ Created: {resp_data.get('name')} ({resp_data.get('color')})")
            return True
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            # Label đã tồn tại → update
            body = json.loads(exc.read().decode())
            if any("already_exists" in str(e.get("message", "")) for e in body.get("errors", [])):
                print(f"  ℹ️  Already exists: {label['name']} — updating...")
                return _update_label(token, label)
        print(f"  ❌ Failed to create '{label['name']}': {exc.code} {exc.reason[:100]}")
        return False
    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        return False


def _update_label(token: str, label: dict[str, Any]) -> bool:
    """Update label (nếu đã tồn tại nhưng cần sửa màu/description)."""
    url = f"{API_URL}/{label['name']}"
    data = json.dumps({
        "color": label["color"],
        "description": label["description"],
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "sap-abap-agent-setup-labels",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_data = json.loads(resp.read().decode())
            print(f"  ✅ Updated: {resp_data.get('name')} ({resp_data.get('color')})")
            return True
    except urllib.error.HTTPError as exc:
        print(f"  ❌ Failed to update '{label['name']}': {exc.code} {exc.reason[:100]}")
        return False


def main() -> None:
    print(f"🔧 Setting up GitHub labels for {REPO}...")
    print(f"   Labels: {', '.join(label['name'] for label in LABELS)}")
    print()

    token = _get_token()
    if not token:
        print("❌ Không tìm thấy GITHUB_TOKEN hoặc GH_TOKEN.")
        print("   Cách 1: export GITHUB_TOKEN=ghp_xxx")
        print("   Cách 2: gh auth login  (rồi chạy lại)")
        sys.exit(1)

    success = 0
    for label in LABELS:
        if _create_label(token, label):
            success += 1

    print()
    if success == len(LABELS):
        print(f"✅ All {success}/{len(LABELS)} labels ready!")
        sys.exit(0)
    else:
        print(f"⚠️  {success}/{len(LABELS)} labels created (check errors above)")
        sys.exit(1 if success == 0 else 0)


if __name__ == "__main__":
    main()
