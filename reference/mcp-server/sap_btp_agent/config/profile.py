"""Quan ly registry (profiles.json) + CRUD cho tung profile.

Moi profile = 1 folder trong profiles/<id>/ chua config.json + secrets.json.
"""
from __future__ import annotations

import contextlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import (
    get_active_profile_id,
    get_app_dir,
    get_profile_dir,
    get_profiles_dir,
    get_registry_file,
    mirror_write_text,
)

REGISTRY_VERSION = 1


def ensure_app_dir() -> Path:
    """Dam bao folder goc + profiles/ ton tai. Tra ve path folder goc."""
    root = get_app_dir()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    get_profiles_dir().mkdir(parents=True, exist_ok=True, mode=0o700)
    return root


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_registry() -> dict[str, Any]:
    """Doc registry. Tra ve object mac dinh neu chua co."""
    ensure_app_dir()
    file = get_registry_file()
    if not file.exists():
        return {"version": REGISTRY_VERSION, "active": None, "profiles": {}}
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        if "profiles" not in data:
            data["profiles"] = {}
        return data
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Loi doc registry {file}: {err}") from err


def _save_registry(reg: dict[str, Any]) -> None:
    file = get_registry_file()
    content = json.dumps(reg, ensure_ascii=False, indent=2)
    file.write_text(content, encoding="utf-8")
    mirror_write_text(file, content)
    with contextlib.suppress(Exception):
        os_chmod(file, 0o600)


def is_valid_profile_id(id_: str) -> bool:
    return bool(
        id_
        and len(id_) <= 64
        and all(c.isalnum() or c in "._-" for c in id_)
    )


def derive_profile_id_from_url(url: str) -> str | None:
    """Sinh id tu URL. VD: https://project1.s4hana.cloud.sap/ -> project1.s4hana.cloud.sap"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host.startswith("www."):
            host = host[4:]
        return host or None
    except Exception:
        return None


def upsert_profile(
    id_: str,
    *,
    label: str | None = None,
    url: str | None = None,
) -> dict[str, Any]:
    """Dang ky hoac cap nhat 1 profile."""
    if not is_valid_profile_id(id_):
        raise ValueError(f'Profile id khong hop le: "{id_}"')
    reg = load_registry()
    now = _now_iso()
    existed = id_ in reg["profiles"]
    existing = reg["profiles"].get(id_, {})
    reg["profiles"][id_] = {
        "id": id_,
        "label": label or existing.get("label") or id_,
        "url": url or existing.get("url") or "",
        "addedAt": existing.get("addedAt") or now,
        "updatedAt": now,
    }
    if not reg.get("active"):
        reg["active"] = id_
    _save_registry(reg)
    return {
        "id": id_,
        "created": not existed,
        "profile": reg["profiles"][id_],
        "active": reg["active"],
    }


def set_active_profile(id_: str) -> str:
    reg = load_registry()
    if id_ not in reg["profiles"]:
        raise RuntimeError(f'Profile "{id_}" khong ton tai.')
    reg["active"] = id_
    _save_registry(reg)
    return id_


def get_current_active() -> str | None:
    """Profile active: uu tien env SAP_BTP_PROFILE -> registry.active."""
    env = get_active_profile_id()
    if env:
        return env
    return load_registry().get("active")


def remove_profile(id_: str) -> dict[str, Any]:
    reg = load_registry()
    if id_ not in reg["profiles"]:
        raise RuntimeError(f'Profile "{id_}" khong ton tai.')
    prof_dir = get_profile_dir(id_)
    if prof_dir.exists():
        shutil.rmtree(prof_dir, ignore_errors=True)
    del reg["profiles"][id_]
    if reg.get("active") == id_:
        remaining = sorted(reg["profiles"].keys())
        reg["active"] = remaining[0] if remaining else None
    _save_registry(reg)
    return {"removed": id_, "newActive": reg.get("active")}


def list_profiles() -> dict[str, Any]:
    reg = load_registry()
    items = sorted(reg["profiles"].values(), key=lambda p: p["id"])
    return {"active": reg.get("active"), "items": items}


def reset_all() -> None:
    """Xoa toan bo folder cau hinh (can than!)."""
    root = get_app_dir()
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    ensure_app_dir()


# Backwards compat helper (alias)
def os_chmod(path: Path, mode: int) -> None:
    import os
    os.chmod(path, mode)
