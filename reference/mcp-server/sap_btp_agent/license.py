"""Kiem tra trang thai license/credentials (cookie, OAuth token, ...).

Cung cap cac ham get_*_status(profile_id) tra ve dict:
  {
    'has_credentials': bool,
    'type': 'cookie' | 'oauth2' | 'none',
    'expires_at': float | None,    # epoch seconds (UTC)
    'expires_in_human': str,       # vd "1h 23m", "expired 2h ago", "no session"
    'is_expired': bool,
    'is_warning': bool,            # < 1h con lai
    'last_saved': float | None,
    'extra': dict,                 # thong tin rieng (token endpoint, scope, ...)
  }

Su dung:
  from sap_btp_agent.license import get_cookie_status, format_expires_in_human
  print(get_cookie_status('project1.s4hana.cloud.sap'))
"""
from __future__ import annotations

import time
from typing import Any

from .config.profile import list_profiles
from .config.secrets import load_secrets

# Heuristic: SAP cookie session mac dinh 8h. Co the config trong config.json
# (sap_session_max_age_hours) de override.
DEFAULT_COOKIE_MAX_AGE_HOURS = 8.0
WARNING_THRESHOLD_S = 3600  # can < 1h -> warning


def _humanize_duration(seconds: float) -> str:
    """Chuyen giay thanh chuoi ngan gon: '1h 23m', '45m', '2d 3h', 'expired 5m ago'."""
    if seconds is None:
        return "unknown"
    if seconds < 0:
        # Da het han
        ago = -seconds
        if ago < 60:
            return f"expired {int(ago)}s ago"
        if ago < 3600:
            # hien thi giay de biet "vua moi het han" hay "gan day"
            m = int(ago / 60)
            s = int(ago % 60)
            return f"expired {m}m {s}s ago"
        if ago < 86400:
            return f"expired {ago / 3600:.1f}h ago"
        return f"expired {ago / 86400:.1f}d ago"

    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        # < 1h: hien thi "Xm Ys" de countdown muot (moi giay giam 1s)
        m = int(seconds / 60)
        s = int(seconds % 60)
        return f"{m}m {s}s"
    if seconds < 86400:
        h = int(seconds / 3600)
        m = int((seconds % 3600) / 60)
        return f"{h}h {m}m" if m else f"{h}h"
    d = int(seconds / 86400)
    h = int((seconds % 86400) / 3600)
    return f"{d}d {h}h" if h else f"{d}d"


def format_expires_in_human(expires_at: float | None) -> str:
    """Format epoch timestamp thanh chuoi ngan (relative to now)."""
    if expires_at is None:
        return "unknown"
    delta = expires_at - time.time()
    return _humanize_duration(delta)


def _get_cookie_max_age_hours(profile_id: str) -> float:
    """Doc config.json cua profile (neu co) -> cookieMaxAgeHours, fallback default."""
    try:
        from .config.store import load_config
        cfg = load_config(profile_id)
        return float(cfg.get("cookieMaxAgeHours", DEFAULT_COOKIE_MAX_AGE_HOURS))
    except Exception:
        return DEFAULT_COOKIE_MAX_AGE_HOURS


def _load_secrets_sync(profile_id: str) -> dict[str, Any]:
    """load_secrets la async; helper sync cho GUI/Tk thread.

    Neu dang o trong asyncio event loop (vd CLI async path), raise RuntimeError
    de caller su dung async path thay the.
    """
    import asyncio
    try:
        asyncio.get_running_loop()
        # Dang trong async context - caller phai await truc tiep
        raise RuntimeError("use async path")
    except RuntimeError as e:
        if "use async path" in str(e):
            raise
        # Khong co loop -> asyncio.run duoc
        return asyncio.run(load_secrets(profile_id))


def get_cookie_status(profile_id: str) -> dict[str, Any]:
    """Tra ve trang thai cookie cua profile.

    Neu chua luu expires_at -> uoc luong = last_saved + max_age_hours.
    """
    try:
        secrets = _load_secrets_sync(profile_id)
    except Exception:
        return {
            "has_credentials": False,
            "type": "none",
            "expires_at": None,
            "expires_in_human": "no secrets",
            "is_expired": True,
            "is_warning": False,
            "last_saved": None,
            "extra": {},
        }

    cookies = secrets.get("cookies") if isinstance(secrets, dict) else None
    if not cookies:
        return {
            "has_credentials": False,
            "type": "cookie",
            "expires_at": None,
            "expires_in_human": "no cookie saved",
            "is_expired": True,
            "is_warning": False,
            "last_saved": secrets.get("saved_at") if isinstance(secrets, dict) else None,
            "extra": {"session_cookies": []},
        }

    # Loc session-cookie
    from .sap.auth import _session_cookie_names
    sess = _session_cookie_names(cookies)

    # expires_at: uu tien secrets["cookie_expires_at"], fallback last_saved + max_age
    expires_at = secrets.get("cookie_expires_at") if isinstance(secrets, dict) else None
    last_saved = secrets.get("saved_at") if isinstance(secrets, dict) else None
    if expires_at is None:
        if last_saved:
            expires_at = float(last_saved) + _get_cookie_max_age_hours(profile_id) * 3600
        else:
            # Khong co gi de uoc luong -> gia su da luu trong 1h qua (best guess)
            expires_at = time.time() - 3600  # expired

    now = time.time()
    delta = expires_at - now
    is_expired = delta < 0
    is_warning = not is_expired and delta < WARNING_THRESHOLD_S

    return {
        "has_credentials": bool(sess),
        "type": "cookie",
        "expires_at": expires_at,
        "expires_in_human": _humanize_duration(delta),
        "is_expired": is_expired,
        "is_warning": is_warning,
        "last_saved": last_saved,
        "extra": {
            "session_cookies": sess,
            "total_cookies": len(cookies),
            "max_age_hours": _get_cookie_max_age_hours(profile_id),
        },
    }


def get_oauth_status(profile_id: str) -> dict[str, Any]:
    """Trang thai OAuth2 access_token (neu profile dung oauth2)."""
    try:
        secrets = _load_secrets_sync(profile_id)
    except Exception:
        secrets = {}

    token = secrets.get("access_token") if isinstance(secrets, dict) else None
    expires_at = secrets.get("token_expires_at") if isinstance(secrets, dict) else None
    last_saved = secrets.get("saved_at") if isinstance(secrets, dict) else None

    if not token:
        return {
            "has_credentials": False,
            "type": "oauth2",
            "expires_at": None,
            "expires_in_human": "no token",
            "is_expired": True,
            "is_warning": False,
            "last_saved": last_saved,
            "extra": {},
        }

    if expires_at is None:
        # Uoc luong OAuth access_token song 1h (SAP mac dinh)
        expires_at = (last_saved or time.time()) + 3600

    now = time.time()
    delta = expires_at - now
    is_expired = delta < 0
    is_warning = not is_expired and delta < WARNING_THRESHOLD_S

    return {
        "has_credentials": True,
        "type": "oauth2",
        "expires_at": expires_at,
        "expires_in_human": _humanize_duration(delta),
        "is_expired": is_expired,
        "is_warning": is_warning,
        "last_saved": last_saved,
        "extra": {
            "token_endpoint": (secrets or {}).get("token_endpoint"),
            "scope": (secrets or {}).get("scope"),
        },
    }


def get_profile_status(profile_id: str) -> dict[str, Any]:
    """Status tong hop cho 1 profile (auto-detect auth mode)."""
    try:
        from .config.store import load_config
        cfg = load_config(profile_id)
    except Exception:
        cfg = {}
    auth_mode = cfg.get("authMode", "oauth2")

    if auth_mode == "cookie":
        return get_cookie_status(profile_id)
    return get_oauth_status(profile_id)


def list_all_statuses() -> list[dict[str, Any]]:
    """Trang thai tat ca profiles + profile active."""
    data = list_profiles()
    items = data.get("items", [])
    active = data.get("active")

    result = []
    for p in items:
        s = get_profile_status(p["id"])
        result.append({
            "profile_id": p["id"],
            "label": p.get("label", p["id"]),
            "url": p.get("url", ""),
            "is_active": p["id"] == active,
            **s,
        })
    return result


def warning_profiles() -> list[dict[str, Any]]:
    """Loc ra profiles co credentials sap het han (< 1h) hoac da het."""
    return [s for s in list_all_statuses() if s.get("is_warning") or s.get("is_expired")]
