---
title: Onboarding Guide
audience: end-user
version: 1.21.0
last_updated: 2026-08-02
---

# Hướng dẫn Onboarding — SAP ABAP Agent

Chọn **đúng 1 persona** bên dưới và làm lần lượt. Mỗi đường happy-path ≤ 15 phút.
Chi tiết sâu nằm ở [Tùy chọn nâng cao](#tuy-chon-nang-cao) — bỏ qua lần đầu.

Yêu cầu chung: **Python ≥ 3.10**. Cần tenant SAP nếu muốn kết nối hệ thống thật.

---

## Persona A — ABAP Developer

Mục tiêu: kết nối hệ thống + scaffold / review / test ABAP Cloud.

### A1. Cài CLI (PATH-only)

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

Doctor phải báo `mcp-sap-connect` trên PATH (hoặc in lệnh sửa PATH). Mở **terminal mới** nếu vừa sửa PATH.

### A2. GUI Windows (khuyến nghị) hoặc chỉ CLI

- **GUI:** ưu tiên **NSIS** từ Release mới nhất tag `gui-v*` / rolling
  `gui-latest` (About → Check for updates sau khi đã cài). Bản local:
  `gui-native/dist-bundle/` nếu bạn tự build. MSI cần admin (Error 1925 nếu
  không elevate). Mở **SAP ABAP Agent** → nếu banner vàng: làm A1 rồi bấm
  **Kiểm tra lại**.
- **CLI only:** bỏ qua GUI, dùng lệnh ở A3.

### A3. Thêm profile SAP

GUI: **+ Add** → Setup from file / wizard.

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

Đăng ký MCP (GUI **MCP Servers**, hoặc CLI):

```powershell
mcp-sap-connect mcp-setup
# hoặc non-interactive:
mcp-sap-connect mcp-setup --register-json sap-btp
mcp-sap-connect mcp-setup --register-json sap-dict-bridge
```

| Preset | Servers |
|--------|---------|
| **Core only** | `sap-btp`, `sap-dict-bridge` |
| **Full research** | Core + `cds-kb` + `mcp-sap-docs-btp` (+ Notion nếu team dùng) |

### A5. Thử ngay

- `Liệt kê các profile SAP của tôi`
- `Tìm class bắt đầu bằng ZCL_`
- Đưa FS `.docx` → analyze → technical spec → scaffold → ATC → unit test → finish

---

## Persona B — Functional Consultant

Mục tiêu: hỏi nghiệp vụ module + tra CDS/docs — **không** scaffold ABAP.

### B1. Cài tối thiểu

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

Cài plugin như A4. GUI tùy chọn (đổi profile / license).

### B2. Profile (nếu cần đọc hệ thống thật)

```powershell
mcp-sap-connect setup https://<tenant>.s4hana.cloud.sap
mcp-sap-connect ping
```

Không cần profile nếu chỉ hỏi kiến thức / tra docs remote.

### B3. MCP research

Preset **Full research:** `cds-kb` + `mcp-sap-docs-btp` (GUI hoặc `mcp-setup`).

### B4. Thử ngay

- `Hỏi SD: cấu hình pricing cho sales order`
- `Tìm CDS view cho purchase order quá hạn`
- `Hỏi FI và CO: cost center với GL`

---

## Persona C — Key User

Mục tiêu: key-user extensibility / học — **không** bắt buộc CLI sâu.

### C1. Cài plugin

```
/plugin marketplace add StormShynn/sap-abap-agent
/plugin install sap-abap-agent
```

### C2. MCP (tối thiểu)

- Research: `cds-kb`, `mcp-sap-docs-btp` nếu muốn tra Help/CDS
- **Không bắt buộc** `mcp-sap-connect` / GUI nếu không nối tenant

### C3. Thử ngay

- `Key user: thêm custom field cho sales order như thế nào?`
- `Học SAP hôm nay` / `Quiz MM cho tôi`

Skill chính: `sap-key-user-toolkit` + consultant module khi cần.

---

## Tùy chọn nâng cao

| Chủ đề | Ghi chú |
|--------|---------|
| Notion skill notes | `/mcp` → OAuth Notion; xem README |
| Error reporting | Opt-in `SAP_ABAP_AGENT_ERROR_REPORTING=1` |
| Daily learner cron | Opt-in Task Scheduler — tốn API |
| sap-vsp / ADT thay thế | `KNOWN_LIMITATIONS.md`, `docs/sap-mcp-recommendations.md` |
| Cursor / VS Code | MCP stdio/SSE; hooks tối ưu Claude Code |
| Legacy Tkinter GUI | `pip install "mcp-sap-connect[gui]"` — không khuyến nghị user mới |

---

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|-----|------------|
| Banner GUI / `'mcp-sap-connect' is not recognized` | `python -m mcp_sap_connect.doctor` → sửa PATH → mở lại |
| `401 Unauthorized` | `mcp-sap-connect reauth` hoặc setup lại |
| `Chua co profile nao` | `mcp-sap-connect setup <URL>` hoặc GUI **+ Add** |
| `Khong giai ma duoc secret` | Đổi máy → setup lại (DPAPI theo user/máy) |
| MSI install fail (1603 / Error 1925) | MSI mặc định cần quyền admin (per-machine). Dùng **NSIS** `.exe` (current-user) hoặc chạy MSI elevated |
| Skill không hiện | Restart Claude Code sau `/plugin install` |

---

## Cập nhật

```powershell
.\reference\scripts\update.ps1
```

GUI: Release tag `gui-v*` (workflow `gui-release.yml`).

## Tài liệu liên quan

- [`README.md`](../README.md) — tổng quan / reference
- [`gui-native/README.md`](../gui-native/README.md) — PATH-only GUI
- [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md)
- [`docs/sap-mcp-recommendations.md`](sap-mcp-recommendations.md)
- [`CONTRIBUTING.md`](../CONTRIBUTING.md)
