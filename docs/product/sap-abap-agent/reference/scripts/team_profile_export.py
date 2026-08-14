#!/usr/bin/env python3
"""Xuat profile mau an toan (redact secret) de chia se noi bo team.

KHONG bao gio ghi password/clientSecret/cookie/token ra file export.

Usage:
  python team_profile_export.py <profile-id> --out team-template.json
  python team_profile_export.py <profile-id>   # stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Reuse mcp_sap_connect store when available; fallback to raw paths.
SECRET_KEYS = {
    "clientSecret",
    "password",
    "samlPassword",
    "samlBootstrapPassword",
    "bearerToken",
    "accessToken",
    "refreshToken",
    "cookies",
    "cookieHeader",
}


def _profiles_root() -> Path:
    override = Path(os_environ_home())
    return override / "profiles"


def os_environ_home() -> Path:
    import os

    env = os.environ.get("MCP_SAP_CONNECT_HOME", "").strip()
    if env:
        return Path(env)
    return Path.home() / ".mcp-sap-connect"


def load_config(profile_id: str) -> dict:
    cfg_path = _profiles_root() / profile_id / "config.json"
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Khong thay config: {cfg_path}")
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def redact_for_template(cfg: dict) -> dict:
    """Build setup --from-file shaped template with placeholders for secrets."""
    auth = (cfg.get("authMode") or cfg.get("auth_mode") or "oauth2").lower()
    url = cfg.get("btpUrl") or cfg.get("url") or "<https://YOUR_TENANT.s4hana.cloud.sap>"
    out: dict = {
        "profileId": cfg.get("id") or cfg.get("profileId") or "<profile-id>",
        "url": url,
        "service": cfg.get("serviceType") or cfg.get("service") or "s4hc_(public)",
        "region": cfg.get("region") or "eu10",
        "authMode": auth,
    }
    if auth == "oauth2":
        out["clientId"] = cfg.get("clientId") or "<CLIENT_ID>"
        out["clientSecret"] = "<CLIENT_SECRET>"
    elif auth == "password":
        out["username"] = cfg.get("username") or "<USERNAME>"
        out["password"] = "<PASSWORD>"
    elif auth == "bearer":
        out["bearerToken"] = "<BEARER_TOKEN>"
    elif auth == "cookie":
        out["cookies"] = "<PASTE_COOKIE_OR_USE_WIZARD>"
        if cfg.get("samlBootstrapUsername") or cfg.get("samlUsername"):
            out["samlBootstrapUsername"] = "<IAS_USERNAME_OPTIONAL>"
            out["samlBootstrapPassword"] = "<IAS_PASSWORD_OPTIONAL>"
    # Strip any leaked secret-like keys
    for k in list(out.keys()):
        if k in SECRET_KEYS and not str(out[k]).startswith("<"):
            out[k] = f"<{k.upper()}>"
    out["_comment"] = (
        "Template an toan — dien placeholder roi: "
        "mcp-sap-connect setup --from-file this.json. "
        "KHONG commit file da dien secret."
    )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile_id", help="Profile id dang co tren may (profiles list)")
    parser.add_argument("--out", "-o", help="Ghi JSON ra file (mac dinh stdout)")
    args = parser.parse_args(argv)
    try:
        cfg = load_config(args.profile_id)
        template = redact_for_template(cfg)
    except Exception as err:  # noqa: BLE001
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    text = json.dumps(template, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
