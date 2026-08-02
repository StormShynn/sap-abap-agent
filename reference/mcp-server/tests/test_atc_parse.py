"""Unit tests for ATC worklist XML parsing (no live tenant)."""
from __future__ import annotations

from mcp_sap_connect.sap.client import _parse_atc_worklist_xml


SAMPLE = """<?xml version="1.0"?>
<worklist id="WL1" timestamp="2026-08-02T00:00:00Z">
  <objects>
    <object name="ZCL_DEMO" uri="/sap/bc/adt/oo/classes/zcl_demo">
      <findings>
        <finding priority="1" checkTitle="Clean Core"
          messageTitle="Unreleased API" messageId="1"
          location="/sap/bc/adt/oo/classes/zcl_demo#start=10,1"
          uri="/sap/bc/adt/atc/findings/1"/>
        <finding priority="3" checkTitle="Style"
          messageTitle="Long method" messageId="2"
          location="/sap/bc/adt/oo/classes/zcl_demo#start=20,1"
          uri="/sap/bc/adt/atc/findings/2"/>
      </findings>
    </object>
  </objects>
</worklist>
"""


def test_parse_atc_fail_on_priority_1():
    data = _parse_atc_worklist_xml(
        SAMPLE,
        worklist_id="WL1",
        check_variant="DEFAULT",
        object_uri="/sap/bc/adt/oo/classes/zcl_demo",
    )
    assert data["status"] == "FAIL"
    assert data["errorCount"] == 1
    assert data["warningCount"] == 1
    assert data["findingCount"] == 2
    assert data["findings"][0]["messageTitle"] == "Unreleased API"


def test_parse_atc_pass_when_empty():
    data = _parse_atc_worklist_xml(
        "<worklist id='x'/>",
        worklist_id="x",
        check_variant="DEFAULT",
        object_uri="/sap/bc/adt/oo/classes/zcl_demo",
    )
    assert data["status"] == "PASS"
    assert data["errorCount"] == 0
