# SAP ABAP Agent — GUI (Tauri) v1.19.0

Native desktop GUI cho `mcp-sap-connect` (Rust + Tauri v2 + vanilla TypeScript).

**PATH-only** (Harness decision `0001-gui-path-only-no-sidecar`): installer **không**
embed Python. Cần `mcp-sap-connect` trên PATH (`pip install`). Rust chỉ orchestration —
auth/secrets vẫn ở Python, gọi qua `mcp-sap-connect <command> --json`.

Bản Python/Tkinter (`pip install mcp-sap-connect[gui]` → `mcp-sap-connect-gui`) là
**legacy** — vẫn chạy trong ≥2 minor sau GA native; khuyến nghị dùng installer này.

## End-user (Windows)

1. Cài CLI (một lần):

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

2. Cài GUI: chạy file **NSIS** hoặc **MSI** từ GitHub Release tag `gui-v1.19.0`
   (workflow `.github/workflows/gui-release.yml` khi push tag). Hoặc build local (mục dưới).

3. Mở **SAP ABAP Agent** → nếu thiếu CLI, banner vàng hiện lệnh pip/doctor →
   **Kiểm tra lại** sau khi cài.

4. Add profile → Ping / Connect → MCP Servers (đăng ký core với Claude Code).

## Yêu cầu (dev / build)

- Node.js 18+ và npm.
- Rust toolchain (`rustup`) + WebView2 (Windows 10/11 thường có sẵn).
- `mcp-sap-connect` trên PATH (hoặc `python -m mcp_sap_connect.cli` cho dev).
- `claude` CLI nếu dùng panel MCP Servers Setup.

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
npm run tauri build
```

Artifact (khi build thành công):

- `src-tauri/target/release/bundle/nsis/*.exe`
- `src-tauri/target/release/bundle/msi/*.msi`
- Binary: `src-tauri/target/release/gui-native.exe` (tên binary Cargo)
- Bản copy local (gitignored): `gui-native/dist-bundle/`

Proven local build (2026-08-01, exit 0):

- `SAP ABAP Agent_1.19.0_x64-setup.exe`
- `SAP ABAP Agent_1.19.0_x64_en-US.msi`

Publish: `git tag gui-v1.19.0 && git push origin gui-v1.19.0` → workflow `gui-release.yml`.

## Tính năng

- **Runtime check (PATH-only):** banner khi thiếu/hỏng `mcp-sap-connect`.
- **Quản lý profile** + license countdown + Ping / Reauth / Connect / Set Active / Remove.
- **+ Add:** setup wizard (console), setup `--from-file` (stream log), import JSON backup.
- **MCP Servers Setup:** đăng ký server còn thiếu qua `claude mcp add`.
- **System tray:** đóng cửa sổ = ẩn tray; Quit thật từ menu tray.

## Kiến trúc thư mục

```text
gui-native/
+- index.html
+- src/
|  +- main.ts
|  +- styles.css
+- src-tauri/
   +- src/
   |  +- lib.rs
   |  +- mcp_cli.rs      # check_runtime + profiles/license/mcp --json
   |  +- jobs.rs
   |  +- tray.rs
   +- tauri.conf.json    # version 1.18.0, targets nsis+msi
```
