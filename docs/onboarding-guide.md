---
title: Onboarding Guide
audience: end-user
version: 1.19.0
last_updated: 2026-08-01
---

# Hướng dẫn Onboarding — SAP ABAP Agent

Chọn **đúng 1 persona** bên dưới và làm lần lượt. Mỗi đường happy-path ≤ 15 phút.
Chi tiết sâu / tùy chọn nằm ở mục [Tùy chọn nâng cao](#tuy-chon-nang-cao) — bỏ qua lần đầu.

Yêu cầu chung: **Python ≥ 3.10**, tài khoản SAP (BTP / S/4HANA Cloud) nếu cần kết nối hệ thống.

---

## Persona A — ABAP Developer

Mục tiêu: kết nối hệ thống + dùng AI scaffold/review/test code ABAP Cloud.

### A1. Cài CLI (PATH-only)

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

Doctor phải báo `mcp-sap-connect` trên PATH (hoặc in lệnh sửa PATH). Mở **terminal mới** nếu vừa sửa PATH.

### A2. GUI Windows (khuyến nghị) hoặc chỉ CLI

- **GUI:** cài NSIS/MSI từ Release tag `gui-v1.19.0` (hoặc file local `gui-native/dist-bundle/`).
  Mở **SAP ABAP Agent** → nếu banner vàng: làm A1 rồi bấm **Kiểm tra lại**.
- **CLI only:** bỏ qua GUI, dùng lệnh ở A3.

### A3. Thêm profile SAP

GUI: **+ Add** → Setup from file / wizard.  
CLI:

```powershell
mcp-sap-connect setup https://<tenant>.s4hana.cloud.sap
# hoặc: mcp-sap-connect setup --from-file path\to\profile.json
mcp-sap-connect ping
mcp-sap-connect connect
```

`ping` = session còn sống (nhẹ). `connect` = đọc + CSRF/ghi.

### A4. Plugin + MCP core

Trong Claude Code:

```
/plugin marketplace add StormShynn/sap-abap-agent
/plugin install sap-abap-agent
```

Đăng ký MCP core (GUI panel **MCP Servers** → đăng ký `sap-btp` / `sap-dict-bridge`, hoặc):

```powershell
mcp-sap-connect mcp-setup
```

Preset **Core only:** `sap-btp` + `sap-dict-bridge`.  
Preset **Full research:** thêm `cds-kb` + `mcp-sap-docs-btp` (+ Notion nếu team dùng).

### A5. Thử ngay

Trong chat AI:

- `Liệt kê các profile SAP của tôi`
- `Tìm class bắt đầu bằng ZCL_`
- Đưa FS `.docx` → pipeline: analyze → technical spec → scaffold → ATC → unit test → finish

---

## Persona B — Functional Consultant

Mục tiêu: hỏi nghiệp vụ module (SD/FI/MM…) + tra CDS/docs — **không** scaffold ABAP.

### B1. Cài tối thiểu

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

Cài plugin Claude Code như A4. GUI tùy chọn (hữu ích nếu hay đổi profile / xem license).

### B2. Profile (nếu cần đọc hệ thống thật)

```powershell
mcp-sap-connect setup https://<tenant>.s4hana.cloud.sap
mcp-sap-connect ping
```

Không cần profile nếu chỉ hỏi kiến thức / tra docs remote.

### B3. MCP research (khuyến nghị)

Preset **Full research:** đăng ký `cds-kb` + `mcp-sap-docs-btp` (GUI **MCP Servers** hoặc `mcp-sap-connect mcp-setup`).

### B4. Thử ngay

- `Hỏi SD: cấu hình pricing cho sales order`
- `Tìm CDS view cho purchase order quá hạn`
- `Hỏi FI và CO: cost center với GL`

Routing tự dispatch consultant đúng module — không cần nhớ tên agent.

---

## Persona C — Key User

Mục tiêu: tra cứu / key-user extensibility — **không** cần ABAP CLI sâu.

### C1. Cài plugin

```
/plugin marketplace add StormShynn/sap-abap-agent
/plugin install sap-abap-agent
```

### C2. MCP (tối thiểu)

Chỉ cần research remote nếu muốn tra CDS/Help:

- `cds-kb`, `mcp-sap-docs-btp` qua GUI hoặc `mcp-setup`
- **Không bắt buộc** `mcp-sap-connect` / GUI nếu không kết nối tenant

### C3. Thử ngay

- `Key user: thêm custom field cho sales order như thế nào?`
- `Học SAP hôm nay` / `Quiz MM cho tôi` (daily learner — tùy chọn)

Skill chính: `sap-key-user-toolkit` + hỏi consultant module khi cần.

---

## Tùy chọn nâng cao

Bỏ qua lần đầu. Bật khi đã chạy happy-path ổn.

| Chủ đề | Ghi chú |
|--------|---------|
| Notion skill notes | `/mcp` → đăng nhập Notion; xem README mục Notion |
| Error reporting | Opt-in `SAP_ABAP_AGENT_ERROR_REPORTING=1` hoặc file `ENABLED` |
| Daily learner cron | Opt-in Task Scheduler — tốn API; xem skill `sap-daily-learner` |
| sap-vsp / ADT thay thế | `KNOWN_LIMITATIONS.md` + `docs/sap-mcp-recommendations.md` |
| Cursor / VS Code | MCP qua config stdio/SSE (supergateway); plugin hooks tối ưu Claude Code |
| Legacy Tkinter GUI | `pip install "mcp-sap-connect[gui]"` — không khuyến nghị cho user mới |

---

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|-----|------------|
| Banner GUI / `'mcp-sap-connect' is not recognized` | `python -m mcp_sap_connect.doctor` → sửa PATH → mở lại app/terminal |
| `401 Unauthorized` | `mcp-sap-connect reauth` hoặc setup lại profile |
| `Chua co profile nao` | `mcp-sap-connect setup <URL>` hoặc GUI **+ Add** |
| `Khong giai ma duoc secret` | Đổi máy → setup lại (DPAPI theo user/máy) |
| Skill không hiện | Restart Claude Code sau `/plugin install` |

---

## Cập nhật

```powershell
.\reference\scripts\update.ps1   # Windows
# bash reference/scripts/update.sh  # macOS/Linux
```

Marketplace Claude Code cũng nhắc khi có bản mới. GUI: Release `gui-v*` (workflow `gui-release.yml`).

## Tài liệu liên quan

- [`README.md`](../README.md) — tổng quan / reference
- [`gui-native/README.md`](../gui-native/README.md) — build & PATH-only GUI
- [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md) — hạn chế cố ý
- [`docs/sap-mcp-recommendations.md`](sap-mcp-recommendations.md) — MCP opt-in thêm
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — đóng góp
