# SAP ABAP Agent — GUI (Tauri) v1.22.8

Native desktop GUI cho `mcp-sap-connect` (Rust + Tauri v2 + vanilla TypeScript).

**PATH-only** (Harness decision `0001-gui-path-only-no-sidecar`): installer **không**
embed Python. Cần `mcp-sap-connect` trên PATH (`pip install`). Rust chỉ orchestration —
auth/secrets vẫn ở Python, gọi qua `mcp-sap-connect <command> --json`.

**Auto-updater** (decision `0002-gui-auto-updater`): `tauri-plugin-updater` + minisign +
`update.json` trên rolling tag **`gui-latest`**.

Bản Python/Tkinter (`pip install mcp-sap-connect[gui]` → `mcp-sap-connect-gui`) là
**legacy** — vẫn chạy trong ≥2 minor sau GA native; khuyến nghị dùng installer này.

## End-user (Windows)

1. Cài CLI (một lần):

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

2. Cài GUI: ưu tiên **NSIS** từ Release `gui-v*` / `gui-latest`
   (workflow `.github/workflows/gui-release.yml`). MSI cần elevate (Error 1925).

3. Mở **SAP ABAP Agent** → nếu thiếu CLI, banner vàng → **Kiểm tra lại**.
   **ℹ About** → Check for updates → Download & install (sau khi CI đã publish `gui-latest`).

4. Add profile → Ping / Connect → MCP Servers.

## Yêu cầu (dev / build)

- Node.js 18+ và npm.
- Rust toolchain (`rustup`) + WebView2.
- `mcp-sap-connect` trên PATH.
- (Release) GitHub secrets `TAURI_SIGNING_PRIVATE_KEY` (+ optional password) —
  xem [`.signing/README.md`](.signing/README.md).

## Chạy dev

```bash
cd gui-native
npm install
npm run tauri dev
```

## Build production (Windows)

```bash
cd gui-native
npm install
# Local signed build (optional):
#   $env:TAURI_SIGNING_PRIVATE_KEY = Get-Content $env:TEMP\sap-abap-agent-gui-keys\sap-abap-agent-gui.key -Raw
npm run tauri build
```

Artifact:

- `src-tauri/target/release/bundle/nsis/*.exe` (+ `.sig` / `.nsis.zip` khi signed)
- `src-tauri/target/release/bundle/msi/*.msi`
- CI: `update.json` + rolling tag `gui-latest`
  - Updater URL ưu tiên signed **`.nsis.zip`**; nếu thiếu thì signed **`*-setup.exe`**
    (deterministic trong `scripts/generate-update-json.mjs`)

Publish: set secrets → `git tag gui-vX.Y.Z && git push origin gui-vX.Y.Z`.

## Tính năng

- **About / Auto-update:** Check → Download & Install → relaunch (`gui-latest/update.json`).
- **Runtime check (PATH-only):** banner khi thiếu `mcp-sap-connect`.
- Profile / License / Ping / Reauth / Connect / MCP Servers / tray.

## Kiến trúc thư mục

```text
gui-native/
+- scripts/generate-update-json.mjs
+- .signing/README.md
+- src/main.ts
+- src-tauri/
   +- src/lib.rs          # updater + process plugins
   +- src/mcp_cli.rs
   +- tauri.conf.json     # createUpdaterArtifacts + plugins.updater
```
