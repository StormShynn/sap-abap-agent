# SAP BTP MCP — sap-btp-agent cho VS Code

Tự động đăng ký MCP server `sap-btp-agent` vào VS Code — **không cần chạy `claude mcp add`** thủ công.

Kết nối SAP S/4HANA Cloud để đọc, tìm, syntax-check, activate ABAP ngay trong VS Code,
dùng với **GitHub Copilot**, **Claude Desktop**, **Cursor**, hoặc bất kỳ AI coding assistant
nào hỗ trợ MCP.

## Tính năng

- 🚀 **Tự động đăng ký** MCP server `sap-btp-agent` khi VS Code khởi động
- ⚙️ **Cấu hình linh hoạt**: command path, args, SAP BTP profile
- 🔌 **3 commands**: kiểm tra kết nối, mở cài đặt, chạy doctor
- 📋 **7 MCP tools** sau khi đăng ký:
  `sap_list_profiles`, `sap_ping`, `sap_list_packages`,
  `sap_search`, `sap_read_source`, `sap_syntax_check`, `sap_activate`

## Yêu cầu

- Python >= 3.10
- `sap-btp-agent` đã cài (chạy `pip install sap-abap-agent-mcp[win-dpapi]` trên Windows)
- Tài khoản SAP BTP / S/4HANA Cloud

## Cài đặt

1. Cài MCP Server (nếu chưa có):
   ```bash
   pip install https://github.com/StormShynn/sap-abap-agent/releases/download/mcp-server-v0.3.0/sap_abap_agent_mcp-0.3.0-py3-none-any.whl
   ```

2. Cài extension từ VSIX:
   ```bash
   code --install-extension sap-btp-mcp-0.1.0.vsix
   ```

3. Mở VS Code → extension tự động đăng ký MCP server
   (kiểm tra trong Chat: gõ `@mcp` xem có `sap-btp-agent` tools chưa)

## Cấu hình

| Setting | Default | Mô tả |
|---------|---------|-------|
| `sapBtpMcp.command` | `sap-btp-agent` | Đường dẫn hoặc tên lệnh |
| `sapBtpMcp.args` | `[]` | Đối số thêm (vd: `["--verbose"]`) |
| `sapBtpMcp.profile` | `""` | Profile SAP BTP mặc định |

## Commands

| Command | Gọi từ | Chức năng |
|---------|--------|-----------|
| `SAP BTP: Check Connection` | Command Palette | Test kết nối SAP BTP |
| `SAP BTP: Open Settings` | Command Palette | Mở cài đặt extension |
| `SAP BTP: Run Doctor` | Command Palette | Kiểm tra môi trường Python |

## Phát triển

```bash
cd .vscode-extensions/sap-btp-mcp
npm install
npm run compile     # Build TypeScript → dist/
npm run package     # Đóng gói .vsix
```

## License

MIT
