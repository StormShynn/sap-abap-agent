# 0002 GUI auto-updater (Tauri + minisign + update.json)

Date: 2026-08-01

## Status

Accepted

## Context

PATH-only GUI already ships NSIS/MSI. Users asked for auto-update like
`mcp-switch` (signed updater artifacts + `update.json`), not only “open
releases page”.

`releases/latest` on `sap-abap-agent` collides with `mcp-server-v*` tags, so
the updater channel must be GUI-specific.

## Decision

1. Enable `tauri-plugin-updater` + `tauri-plugin-process` on `gui-native`.
2. Set `bundle.createUpdaterArtifacts: true` and sign with minisign via
   `TAURI_SIGNING_PRIVATE_KEY` (+ optional password) in CI.
3. Publish `update.json` to rolling GitHub Release tag **`gui-latest`**, and
   also attach it to versioned `gui-v*` releases.
4. Endpoint in `tauri.conf.json`:
   `https://github.com/StormShynn/sap-abap-agent/releases/download/gui-latest/update.json`
5. About modal: Check → Download & Install → `relaunch()` (same UX as mcp-switch).
6. Keep NSIS as the updater install channel; MSI remains manual/current-user-admin tradeoff.

## Alternatives Considered

1. Manual GitHub API check only — rejected (user requested auto-updater).
2. `releases/latest/download/update.json` — rejected (tag collision).
3. Embed Python sidecar with updater — out of scope (decision 0001 PATH-only).

## Consequences

Positive:

- In-app update without opening browser when secrets + release exist.

Tradeoffs:

- Requires one-time key generation and GitHub secrets.
- Losing the private key breaks the update channel (must rotate pubkey + rebuild).

## Follow-Up

- Repo admin: set `TAURI_SIGNING_*` secrets (see `gui-native/.signing/README.md`).
- Push tag `gui-v*` after secrets exist to produce first signed release + `gui-latest`.
