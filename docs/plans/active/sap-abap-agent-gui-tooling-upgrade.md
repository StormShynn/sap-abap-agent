# Execution Plan: SAP ABAP Agent — GUI tooling upgrade wave

Date: 2026-08-02

## Status

Active

## Outcome

`gui-native/` (Tauri v2, Windows) gains a curated set of additional Tauri
plugins and UI polish so the desktop app feels native on Windows 11 and is
more reliable to debug, without changing the PATH-only distribution model
(decision 0001) or the updater channel (decision 0002).

This plan lives in the Harness workspace and only documents the wave. GUI code
is owned by the product repo `StormShynn/sap-abap-agent/gui-native/`; the
implementation executes there.

## Context

- GUI truth: `docs/product/sap-abap-agent/README.md` (GUI section),
  `gui-native/README.md` in product repo.
- Decisions: `docs/decisions/0001-gui-path-only-no-sidecar.md`,
  `docs/decisions/0002-gui-auto-updater.md`,
  `docs/decisions/0003-claude-code-skills-cursor-docs-only.md`.
- Prior waves: `docs/plans/completed/sap-abap-agent-abc-roadmap.md` (ship GUI),
  `docs/plans/completed/sap-abap-agent-upgrade-wave.md` (signed gui-latest).
- Current GUI capabilities (verified in product README): profile / reauth /
  connect / ping / MCP servers / license dashboard / system tray + tray
  license warning / in-app updater (minisign) / runtime PATH check.
- Research (2026-08-02): Tauri v2 official plugin ecosystem, custom titlebar
  + window effects, UI kits, DX tooling. GUI is on Tauri v2; exact frontend
  stack in `gui-native/` is not visible from this Harness workspace — confirm
  from product-repo source before choosing a UI kit.

## Scope

In scope (documented as prioritized waves):

1. **Lifecycle/robustness plugins (P1):**
   - `tauri-plugin-window-state` — remember window size/position.
   - `tauri-plugin-single-instance` — one GUI instance; reconcile with the
     existing "1 profile / instance" env-based model (`SAP_BTP_PROFILE`).
   - `tauri-plugin-dialog` — native file picker for "Add profile from file".
   - `tauri-plugin-store` — persist GUI settings (theme, last window, update
     check prefs) outside the CLI config.
2. **Desktop integration plugins (P2):**
   - `tauri-plugin-global-shortcut` — quick summon/hide hotkey.
   - `tauri-plugin-autostart` — optional run at login + minimize to tray.
   - `tauri-plugin-shell` — safe open of release page / `doctor` / pip hints.
   - `tauri-plugin-deep-link` — `sap-abap-agent://` deep links (open profile /
     tab from outside).
   - `tauri-plugin-os` — OS info in About/Support.
3. **Native Windows look (P3):**
   - Custom titlebar (`decorations: false` + `data-tauri-drag-region`) +
     Windows 11 Mica/Acrylic via `windowEffects` where supported.
   - UI kit pass (shadcn/ui or Fluent UI depending on confirmed frontend
     stack) + dark/light mode following OS theme (`window.theme()`).
4. **DX & reliability (P4):**
   - `tauri-plugin-log` + `tauri-plugin-devtools` (debug IPC real-time).
   - `tauri-action` in `gui-release.yml` (cached builds, artifact signing).
   - Rust panic hook (`std::panic::set_hook`) for graceful failure + local
     crash log.
   - Review `src-tauri/capabilities/` permissions after each plugin addition.

Out of scope (this wave):

- Authenticode code signing — pending IT requirement (see upgrade-wave plan).
- CrabNebula Cloud as update host — keep GitHub Releases `gui-latest`.
- Embedding Python sidecar — decision 0001 stays.
- macOS/Linux native GUI — Windows first.
- Tkinter GUI work — legacy, deprecation path unchanged.

## Approach

Smallest coherent sequence, each group independently verifiable:

1. **Phase 1 — P1 plugins.** Add the four lifecycle plugins, wire
   `window-state` + `store` + `single-instance` first, then `dialog` in the
   Add-profile flow. Verify single-instance does not break the documented
   multi-instance env model (test two instances with different
   `SAP_BTP_PROFILE`; if it conflicts, gate single-instance behind a setting).
2. **Phase 2 — P2 plugins.** Add global-shortcut, autostart (opt-in), shell
   (scoped commands only), deep-link (register scheme), os. Each with the
   matching capability permission entries.
3. **Phase 3 — P3 UI polish.** Custom titlebar + window effects behind a
   feature flag first (fallback to decorated window if WebView2/Windows
   version lacks support); then UI kit + OS theme sync.
4. **Phase 4 — P4 DX/reliability.** Logging + devtools (debug builds),
   tauri-action CI, panic hook.
5. Update `gui-native/README.md` + product README GUI section with new
   features and any new first-run behavior.
6. Bump GUI version, push `gui-v*` tag, assert `gui-latest` update channel
   still serves the signed `update.json`.

## Risks And Recovery

| Risk | Mitigation | Recovery |
|------|------------|----------|
| `single-instance` conflicts with multi-instance per-profile model | Gate behind a setting; default ON only after testing two instances | Revert the plugin init + capability; keep feature flag OFF |
| Custom titlebar/window-effects breaks on older WebView2 or non-Win11 | Feature-flag + runtime capability check | Fall back to default decorations |
| Adding plugins expands attack surface | Minimal capability scopes per plugin; review `capabilities/` each phase | Revoke permissions; remove plugin |
| `tauri-action`/CI changes break `gui-release.yml` | Test on a draft `gui-v*`-style tag branch before touching main | Revert workflow change |
| New UI kit churn / visual regression | Keep kit change isolated in one PR; screenshot before/after | Revert kit PR; keep previous styling |

## Progress

- [ ] Phase 1 — P1 lifecycle plugins (window-state, store, single-instance,
      dialog).
- [ ] Phase 2 — P2 desktop integration plugins (global-shortcut, autostart,
      shell, deep-link, os).
- [ ] Phase 3 — P3 native Windows look (custom titlebar + window effects, UI
      kit, OS theme sync).
- [ ] Phase 4 — P4 DX/reliability (log + devtools, tauri-action, panic hook).
- [ ] Docs sync (gui-native README + product README GUI section).
- [ ] Version bump + signed `gui-v*` release assert (`gui-latest` update.json).

## Decisions

- 2026-08-02: GUI upgrade wave documented in Harness workspace only; code
  changes execute in product repo `gui-native/`. Rationale: product repo is
  system of record for GUI code (matches decision 0003 split).
- 2026-08-02: Single-instance is opt-in pending multi-instance env-model
  test — do not silently change documented behavior.
- 2026-08-02: UI kit choice (shadcn/ui vs Fluent UI) deferred until the
  exact frontend stack in `gui-native/` is confirmed from source.

## Validation

- Focused proof: per-phase plugin init tests in `gui-native` (Rust unit +
  frontend smoke); capability files linted against plugin docs.
- Integration or end-to-end proof: `npm run tauri build` → NSIS install →
  launch → exercise each new surface (window state persists, hotkey toggles,
  deep-link opens profile tab, theme follows OS). Two-instance test for
  single-instance decision.
- Repository-required checks: `validate_plugin.py` if any plugin-surface docs
  change; existing GUI CI must stay green; `gui-latest` update.json still
  signed and served.

## Result

Complete after implementation. Record verified outcome, limitations (e.g.
Windows-version-dependent effects), and follow-up before moving this plan to
`docs/plans/completed/`.
