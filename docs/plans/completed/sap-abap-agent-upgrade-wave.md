# Execution Plan: SAP ABAP Agent upgrade wave (P0–P2)

Date: 2026-08-02

## Status

Completed

## Outcome

Green Validate/Security Scan; GUI version tracks plugin; signed `gui-latest`
channel shippable; docs/Dependabot/MCP UX/polish upgraded; plugin P2
edition-gates + routing clarity landed.

## Scope

In scope: CI fixes, GUI version sync + release assert, Dependabot, docs,
MCP unregister + presets, signing secrets + tag if key present, tray update
hint, GUI PR CI, SECURITY.md, plugin P2 high-value polish.

Out of scope: Authenticode cert purchase; multi-OS GUI; enabling GitHub Pages
(repo setting); full 43-module deep-split.

## Approach

1. Fix validate pytest install + bandit severity/line-continuation.
2. Bump GUI to track plugin; wire version-bump + gui-release assert.
3. Docs, Dependabot, MCP UX, P2 polish.
4. Set secrets + tag `gui-v*` when key available.

## Progress

- [x] CI Validate + Security Scan (pytest install; Bandit HIGH gate)
- [x] GUI bump + version-bump sync + gui-release assert
- [x] Docs / Dependabot / remote clarity
- [x] MCP unregister + presets + secret env prompt
- [x] Secrets + signed `gui-v1.22.2` / rolling `gui-latest` (`update.json` live)
- [x] P2 polish (gui-ci, quiet startup update check, SECURITY.md)
- [x] Plugin surface P0/P1: `zy_namespace_guard` on all `sap_create_*` +
  `sap_publish_service_binding`; hook tests; validate_plugin guard-coverage
- [x] Plugin P2: RAP/CDS/CDS-analytics Buoc-0 edition gates; architecture
  skill-vs-agent table; daily-learner Write/Edit scoped to `<agent-home>`;
  validate_plugin README skill-count warn; deep-split backlog copy updated
  (8 modules split; remainder documented backlog)

## Validation

- Local: `validate_plugin.py` pass; `pytest hooks/hook_tests/` pass; bandit
  HIGH exit 0
- Remote: `gui-release` success for `gui-v1.22.2`;
  https://github.com/StormShynn/sap-abap-agent/releases/tag/gui-latest
  ships `update.json` version `1.22.2`

## Notes

- `origin` URL still ends in `sap-abap-agent-backup.git` but GitHub redirects
  to canonical `StormShynn/sap-abap-agent`.
- Signing: set private key via `cmd /c gh secret set ... < keyfile` (no BOM);
  workflow uses literal empty `TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ""`.
- Module deep-split beyond the 8 already done remains backlog.
