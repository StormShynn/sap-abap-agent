"""Tests for reference/scripts/team_profile_export.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import team_profile_export as tpe  # noqa: E402


def test_redact_oauth2_never_leaks_secret():
    cfg = {
        "profileId": "demo",
        "btpUrl": "https://my123.s4hana.cloud.sap",
        "serviceType": "s4hc_(public)",
        "region": "eu10",
        "authMode": "oauth2",
        "clientId": "real-client",
        "clientSecret": "SUPER_SECRET",
    }
    out = tpe.redact_for_template(cfg)
    assert out["clientId"] == "real-client"
    assert out["clientSecret"] == "<CLIENT_SECRET>"
    assert "SUPER_SECRET" not in json.dumps(out)


def test_redact_password():
    out = tpe.redact_for_template(
        {
            "id": "p1",
            "url": "https://x.example",
            "authMode": "password",
            "username": "alice",
            "password": "hunter2",
        }
    )
    assert out["username"] == "alice"
    assert out["password"] == "<PASSWORD>"


def test_export_writes_file(tmp_path, monkeypatch):
    home = tmp_path / ".mcp-sap-connect"
    prof = home / "profiles" / "lab1"
    prof.mkdir(parents=True)
    (prof / "config.json").write_text(
        json.dumps(
            {
                "profileId": "lab1",
                "btpUrl": "https://lab.s4hana.cloud.sap",
                "authMode": "oauth2",
                "clientId": "cid",
                "clientSecret": "sekrit",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("MCP_SAP_CONNECT_HOME", str(home))
    out = tmp_path / "tmpl.json"
    assert tpe.main(["lab1", "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["clientSecret"] == "<CLIENT_SECRET>"
    assert "sekrit" not in out.read_text(encoding="utf-8")
