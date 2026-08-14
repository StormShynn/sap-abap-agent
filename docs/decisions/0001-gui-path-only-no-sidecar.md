# 0001 GUI Windows PATH-only (no Python sidecar)

Date: 2026-08-01

## Status

Accepted

## Context

Phase B of `docs/plans/active/sap-abap-agent-abc-roadmap.md` ships a native
Tauri GUI (`gui-native/`). Two distribution models were open: embed a Python
runtime + `mcp-sap-connect` wheel inside the MSI, or require the CLI on PATH
and keep the installer as UI-only orchestration.

Embedding duplicates secret-store assumptions, increases artifact size and
code-signing surface, and risks version skew between GUI and CLI. The GUI
already resolves `mcp-sap-connect` then falls back to
`python -m mcp_sap_connect.cli`.

## Decision

**PATH-only for GUI GA (v1.18.x):** the Windows installer does **not** embed
Python or the wheel. Users install `mcp-sap-connect` via pip (or editable
dev install) so the binary is on PATH. The GUI probes CLI availability on
startup and shows install/PATH fix hints when missing.

GUI semver matches the product release for the same ship window (currently
`1.19.0` after CI bump). Release tag for the installer artifact: `gui-v1.19.0`.

Tkinter GUI (`pip install mcp-sap-connect[gui]`) remains supported as
**legacy** for at least two minor releases after native GUI GA, then docs
stop recommending it.

## Alternatives Considered

1. Embed Python sidecar + wheel in MSI — rejected for v1 (size, signing,
   dual update path). May revisit as a later decision.
2. GUI-only without any CLI dependency — rejected; would rewrite auth/secrets
   in Rust and create format drift.

## Consequences

Positive:

- Single source of truth for SAP auth/secrets (Python package).
- Smaller, simpler installer; doctor/PATH fixes reuse existing CLI tooling.

Tradeoffs:

- First-run still needs one pip install (or PATH fix) before GUI works.
- Users with multiple Pythons can still hit PATH confusion — mitigated by
  in-app runtime banner + `mcp-sap-connect doctor`.

## Follow-Up

- In-app `check_runtime` banner (Phase B).
- Document MSI/NSIS download + pip prerequisite in `gui-native/README.md`
  and product README GUI section.
- Optional later: embed sidecar — requires a new decision superseding this one.
