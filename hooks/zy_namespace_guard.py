#!/usr/bin/env python
"""PreToolUse guard: block MCP calls that would create/update/delete a DDIC/CDS/
RAP object whose name is NOT in the Z/Y customer namespace (or a registered
"/namespace/" prefix).

Covers the object-creation tools this repo documents/ships:
  - sap-dict-bridge (reference/mcp-server/sap_btp_agent/tools/dictionary.py):
    sap_create_domain, sap_create_data_element, sap_create_table
  - ADT MCP forks documented in skills/mcp-sap-adt/SKILL.md:
    CreateDomain, CreateDataElement, CreateTable, CreateStructure, CreateView,
    CreateBehaviorDef(inition), CreateMetadataExtension, CreateServiceDefinition
  - Same tools prefixed Update*/Delete* (modifying/deleting an existing object
    is just as unsafe on a non-Z/Y name as creating one).

Fails open on any error or ambiguity (unknown tool shape, no recognisable name
field, name field empty) - this guard only blocks when it is CONFIDENT a
DDIC-object create/update/delete call targets a non-customer namespace. See
skill sap-deployment-target / sap-clean-code for the instruction-level rule
this backs up technically.
"""
import json
import re
import sys

ACTION_RE = re.compile(r"(create|update|delete)", re.IGNORECASE)
OBJECT_KEYWORDS = (
    "domain",
    "dataelement",
    "data_element",
    "table",
    "structure",
    "view",
    "behaviordef",
    "behaviordefinition",
    "metadataextension",
    "servicedefinition",
)
NAME_FIELDS = ("name", "object_name", "objectName", "objName")
# Z/Y customer namespace, or a registered "/namespace/..." prefix.
ALLOWED_NAME_RE = re.compile(r"^(/\w+/|[ZzYy])")


def looks_like_ddic_object_call(tool_name):
    if not tool_name:
        return False
    lowered = tool_name.lower()
    if not ACTION_RE.search(lowered):
        return False
    return any(kw in lowered for kw in OBJECT_KEYWORDS)


def extract_object_name(tool_input):
    if not isinstance(tool_input, dict):
        return None
    for field in NAME_FIELDS:
        value = tool_input.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open - malformed input must never block a tool call

    try:
        tool_name = payload.get("tool_name", "") or ""
        tool_input = payload.get("tool_input", {}) or {}

        if not looks_like_ddic_object_call(tool_name):
            sys.exit(0)

        object_name = extract_object_name(tool_input)
        if not object_name:
            sys.exit(0)  # can't determine the target name - don't block blindly

        if ALLOWED_NAME_RE.match(object_name):
            sys.exit(0)

        reason = (
            "Chan tool '" + tool_name + "' vi object '" + object_name + "' KHONG thuoc namespace "
            "Z/Y (hoac /namespace/ da dang ky). ABAP Cloud KHONG cho phep tao/sua/xoa object "
            "chuan SAP - xem skill sap-deployment-target / sap-clean-code. Neu day la nham lan "
            "ten (vd thieu prefix Z), sua lai ten roi thu lai."
        )
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)
    except Exception:
        sys.exit(0)  # fail open - a bug in this guard must never block a real tool call


if __name__ == "__main__":
    main()
