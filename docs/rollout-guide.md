# Rollout guide — nhiều user / team

Hướng dẫn cho team lead khi đưa **SAP ABAP Agent** tới N developer.
Chi tiết happy-path từng người: [`onboarding-guide.md`](onboarding-guide.md).

**Phiên bản tài liệu:** khớp plugin **1.22.8** (xem `.claude-plugin/plugin.json`).
Wheel MCP gần nhất trên Releases: `mcp-server-v1.22.0` (có thể lệch patch so với plugin).

---

## Mô hình triển khai (khuyến nghị)

| Nguyên tắc | Chi tiết |
|------------|----------|
| **1 người = 1 OS account** | Secrets/profiles nằm trong `%USERPROFILE%\.mcp-sap-connect` (Windows DPAPI theo user) hoặc `~/.mcp-sap-connect`. Cùng login Windows = **cùng vault SAP**. |
| **Không copy thư mục profile giữa máy** | Mỗi máy chạy `setup` / GUI Add profile riêng. |
| **Cách ly lab** | Đặt `MCP_SAP_CONNECT_HOME` trỏ tới thư mục riêng nếu nhiều người buộc dùng chung OS user (không khuyến nghị). |
| **Claude Code = full stack** | Skills + hooks + agents. Cursor / VS Code = **chỉ MCP** (không plugin/hooks). |

---

## Checklist rollout N seats

1. Mỗi máy: Python ≥ 3.10, `pip install "mcp-sap-connect[win-dpapi]"`, `python -m mcp_sap_connect.doctor`.
2. Windows GUI (tuỳ chọn): NSIS từ [gui-latest](https://github.com/StormShynn/sap-abap-agent/releases/tag/gui-latest) / tag `gui-v*` — **current-user**, không cần admin.
3. Claude Code (mỗi máy một lần):
   ```text
   /plugin marketplace add StormShynn/sap-abap-agent
   /plugin install sap-abap-agent
   ```
4. Đăng ký **MCP Core** trước (`sap-btp`, `sap-dict-bridge`, `cds-kb`, `mcp-sap-docs-btp`). Full research (ADT alt, sap-vsp, …) chỉ khi cần — Claude Code giới hạn số stdio MCP.
5. Onboarding theo persona trong [`onboarding-guide.md`](onboarding-guide.md).

---

## MCP: Core vs Full

| Preset | Servers (tóm tắt) | Khi nào |
|--------|-------------------|---------|
| **Core** | `sap-btp`, `sap-dict-bridge`, + remote docs/CDS | Mặc định mọi user |
| **Research / Full** | + `arc-1` hoặc `mcp-abap-adt`, `sap-vsp`, … | Dev cần ADT sâu / VSP — đăng ký thêm có kiểm soát |

GUI: **MCP Servers** → Preset Core / Preset Research. Chi tiết inventory: `reference/scripts/mcp_inventory.json`.

---

## Windows SmartScreen / Authenticode

Installer GUI hiện **có thể chưa ký Authenticode** (minisign updater vẫn tin cậy cho update trong app). User có thể thấy cảnh báo SmartScreen lần đầu — kỳ vọng cho đến khi org upload cert OV/EV (`WINDOWS_CERTIFICATE*`). Xem [`gui-native/.signing/README.md`](../gui-native/.signing/README.md).

---

## Không nằm trong phạm vi rollout này

- SSO / IdP tổ chức (mỗi user auth SAP/BTP riêng).
- Private marketplace nội bộ Claude (dùng public `StormShynn/sap-abap-agent` hoặc fork + `marketplace add` URL nội bộ).
- Rate-limit phía remote MCP (cds-kb, sap-docs) — phụ thuộc nhà cung cấp endpoint.

---

## Liên kết

- Bảo mật & chia sẻ secret: [`SECURITY.md`](../SECURITY.md)
- Hạn chế đã biết: [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md)
- Đóng góp / org pointer: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
