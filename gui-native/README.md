# SAP ABAP Agent — GUI (Tauri)

Native desktop GUI cho `mcp-sap-connect` (Rust + Tauri v2 + vanilla TypeScript), thay thế bản Python/Tkinter
cũ (`reference/mcp-server/mcp_sap_connect/gui/app.py`). Rust chỉ là lớp UI/orchestration — mọi logic thật
(xác thực SAP, mã hóa secrets, đọc/ghi profile registry, gọi `claude mcp add`) vẫn nằm trong Python
(`mcp_sap_connect`), gọi qua subprocess `mcp-sap-connect <command> --json` để tránh viết lại/đồng bộ lại
định dạng file riêng ở 2 ngôn ngữ.

## Yêu cầu

- Node.js 18+ và npm.
- Rust toolchain (`rustup`) + các dependency native của Tauri v2 cho Windows (WebView2 — có sẵn trên
  Windows 10/11 bản mới).
- `mcp-sap-connect` đã cài (`pip install mcp_sap_connect[win-dpapi]` hoặc editable install) và có trong
  PATH — GUI tự tìm binary này trước, fallback `python -m mcp_sap_connect.cli` cho môi trường dev.
- `claude` CLI (Claude Code) trong PATH nếu muốn dùng panel "MCP Servers Setup".

## Chạy dev

```bash
npm install
npm run tauri dev
```

Vite dev server + `cargo run` sẽ tự khởi động; sửa `src/*.ts`/`src/*.css`/`index.html` hot-reload ngay,
sửa file trong `src-tauri/src/` sẽ tự rebuild + khởi động lại app.

## Build production

```bash
npm run tauri build
```

Output nằm ở `src-tauri/target/release/`.

## Tính năng

- **Quản lý profile**: dropdown chọn profile (đọc `mcp-sap-connect profiles list --json`), hiện trạng thái
  license/cookie (còn hạn/sắp hết hạn/hết hạn) kèm đếm ngược cập nhật mỗi giây.
- **4 nút hành động chính**: Reauth (đăng nhập lại, SAML fast-path ưu tiên rồi fallback browser), Connect
  (test kết nối đọc + ghi), Set Active, Remove — log subprocess stream trực tiếp vào panel chính.
- **Nút "Đã đăng nhập xong"**: touch marker file (`SAP_BTP_EARLY_FINISH_FILE`) để nhánh browser-fallback
  kiểm tra session ngay thay vì chờ tự phát hiện/timeout 30s.
- **License Dashboard**: modal xem trạng thái hết hạn của TẤT CẢ profile cùng lúc, tự refresh 1s.
- **Menu "+ Add"**:
  - *Setup wizard (interactive)* — mở cửa sổ CMD mới chạy `mcp-sap-connect setup` (cần console thật để
    tương tác từng bước — không hoạt động nếu app tự nó không có console cha, ví dụ chạy dev qua script
    tự động hoá không gán TTY).
  - *Setup from file (--from-file)* — chọn file JSON đã điền, chạy `setup --from-file` streamed vào log
    chính (không mở console riêng — lệnh này non-interactive, console riêng sẽ đóng quá nhanh để đọc).
  - *Import from JSON backup* — đăng ký nhanh 1 profile từ file `config.json` backup (chỉ có `btpUrl`,
    không có secrets — phải copy `secrets.json` từ máy cũ thủ công vì đã mã hóa DPAPI theo user/máy).
- **MCP Servers Setup**: modal liệt kê toàn bộ MCP server mà `mcp-sap-connect mcp-setup` biết đăng ký, chia
  nhóm (core/remote/adt-alternative/special/manual), hiện đã đăng ký hay chưa (đọc `~/.claude.json`), nút
  "Đăng ký" per-server (hỏi env var cần thiết nếu có). Khác `mcp-switch` (dự án riêng, chỉ bật/tắt server
  đã cấu hình sẵn) — panel này CẤU HÌNH server còn thiếu.
- **System tray**: ẩn xuống tray khi đóng cửa sổ thay vì thoát hẳn; menu tray có Reauth/Connect profile
  active, mở License Dashboard, mở lại cửa sổ chính, Quit thật.

## Kiến trúc thư mục

```text
gui-native/
+- index.html            # markup toàn bộ UI (không dùng framework)
+- src/
|  +- main.ts             # toàn bộ logic frontend (state, event wiring, invoke() calls)
|  +- styles.css           # theme sáng/tối qua CSS variables + color-scheme
+- src-tauri/
   +- src/
   |  +- lib.rs            # wire plugin + invoke_handler + tray + window-close-to-tray
   |  +- mcp_cli.rs         # goi `mcp-sap-connect ... --json` (profiles/license/mcp-setup)
   |  +- jobs.rs            # quan ly subprocess streamed/console + early-finish marker file
   |  +- tray.rs            # system tray icon + menu
   +- capabilities/default.json  # ACL permissions cho dialog/notification/window
```
