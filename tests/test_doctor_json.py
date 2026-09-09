"""doctor --json surfaces path_ok / path_fix for GUI Copy PATH fix."""
from __future__ import annotations

import json

from mcp_sap_connect.doctor import collect_report, main


def test_collect_report_shape():
    report = collect_report()
    assert isinstance(report["all_ok"], bool)
    assert isinstance(report["path_ok"], bool)
    assert "scripts_dir" in report
    assert "path_fix" in report
    assert isinstance(report["checks"], list)
    assert report["checks"], "expected at least python/path/deps checks"
    for item in report["checks"]:
        assert "ok" in item and "message" in item
    if report["path_ok"]:
        assert report["path_fix"] is None
    elif report["scripts_dir"]:
        assert report["path_fix"]
        assert "PATH" in report["path_fix"]


def test_doctor_json_stdout(capsys):
    rc = main(["--json"])
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert "path_ok" in data
    assert "path_fix" in data
    assert "all_ok" in data
    assert rc in (0, 1)
    assert (rc == 0) == data["all_ok"]
