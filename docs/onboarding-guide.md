---
title: Onboarding Guide
audience: end-user
version: 1.0.0
last_updated: 2026-07-17
---

# Hướng dẫn Onboarding — SAP ABAP Agent

Tài liệu này hướng dẫn end-user (consultant / dev) cài đặt và bắt đầu dùng plugin **SAP ABAP Agent**
trên Claude Code. Nếu bạn là contributor (muốn sửa code plugin), xem `CONTRIBUTING.md` thay.

## 1. Cài plugin

### Cách A: từ marketplace Claude Code (khuyến nghị)

Trong Claude Code:

```
/plugin marketplace add StormShynn/sap-abap-agent
/plugin install sap-abap-agent
```

Sau đó khởi động lại Claude Code (hoặc mở tab mới).

### Cách B: dev mode từ local clone

```powershell
git clone https://github.com/StormShynn/sap-abap-agent
cd <your-project>
claude --plugin-dir ../sap-abap-agent
```

## 2. Cấu hình SAP BTP (lần đầu)

Trong Claude Code:

```
setup https://<your-tenant>.s4hana.cloud.sap
```

Wizard `sap-btp-setup` sẽ hỏi:

- **Client ID / Secret** (Service Key từ BTP Cockpit).
- **Token URL** (thường là `https://<tenant>.authentication.sap.hana.ondemand.com/oauth/token`).
- **Profile name** (vd: `dev`, `prod`, `sandbox`).
- **Folder lưu secret** (mặc định `%USERPROFILE%\.sap-btp-agent\<profile>\secrets.json`).

Sau khi setup, verify:

```
Liệt kê các profile SAP của tôi
```

→ gọi `sap_list_profiles`. Phải thấy profile vừa tạo.

## 3. Cài đặt Python (cho `sap-dict-bridge`)

MCP server `sap-dict-bridge` cần Python ≥ 3.10:

```powershell
python --version    # phai >= 3.10
pip install sap-btp-agent
```

## 4. (Tuỳ chọn) Bật MCP server bổ sung

Plugin mặc định bật 5 MCP: `sap-btp`, `sap-dict-bridge`, `cds-kb`, `mcp-sap-docs-btp`, `notion`.
Nếu muốn bật thêm (vd `mcp-abap-adt` cho on-prem), xem `docs/sap-mcp-recommendations.md`.

**Khuyến nghị**: bật `mcp-sap-notes` nếu hay tra SAP Notes — chỉ cần thêm entry vào `.mcp.json`
của project local (KHÔNG push lên git).

## 5. Dùng thử các tính năng chính

| Lệnh gợi ý                                  | Tính năng                                |
|----------------------------------------------|-------------------------------------------|
| "Liệt kê các profile SAP của tôi"           | Multi-profile BTP                         |
| "Tìm class bắt đầu bằng ZCL_ trong project" | `sap-btp` MCP + `sap_search`              |
| "Tạo table ZTB_TEST với field MANDT, MATNR"  | `sap-dict-bridge` + skill `sap-cloud-dictionary` |
| "Hỏi SD: cấu hình pricing cho sales order"   | `sap-sd-consultant-cloud`                  |
| "Tìm CDS view cho purchase order quá hạn"    | `cds-kb` MCP + `sap-docs-researcher`       |
| "Học SAP hôm nay"                            | `sap-daily-learner` (daily tip + path)     |
| "Quiz MM cho tôi"                            | `sap-daily-learner` (trắc nghiệm MM)      |
| "iFlow tích hợp S/4HANA với SuccessFactors"   | `sap-cpi-consultant-cloud` + SF            |

## 6. Daily Learner — setup (chỉ khi cần)

`sap-daily-learner` chạy local trong `%USERPROFILE%\.sap-abap-agent\` (Windows) hoặc
`~/.sap-abap-agent/` (macOS/Linux). Memory 3-tier (episodic / semantic / procedural) được
bootstrap bằng script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/bootstrap_memory.py"
```

Sau khi bootstrap, lần đầu gọi `sap-daily-learner` sẽ tự tạo `LEARNING_PROGRESS.md` + knowledge
graph + folder `memory/`.

**Cron opt-in**: nếu muốn tự động gửi daily tip, xem skill `sap-daily-learner` mục "Scheduling
cơ chế" — KHÔNG bật mặc định (tốn chi phí API).

## 7. Xử lý lỗi thường gặp

| Lỗi                                 | Cách xử lý                                                |
|--------------------------------------|------------------------------------------------------------|
| `401 Unauthorized`                   | Client_secret sai / hết hạn. Chạy `setup <profile-id>`.   |
| `404 /oauth/token`                   | Sửa `tokenUrl` trong profile.                              |
| `Khong giai ma duoc secret`          | Đổi máy. Chạy `setup <profile-id>` để tạo lại.            |
| `Chua co profile nao`                | Chạy `setup <URL>` để tạo profile đầu tiên.                |
| `'sap-btp-agent' is not recognized`  | PATH thiếu entry point. Chạy `python -m sap_btp_agent.doctor` để tự phát hiện. |
| Skill không hiển thị                 | Khởi động lại Claude Code sau khi cài plugin.             |

## 8. Cập nhật plugin

Khi có version mới, Claude Code marketplace tự động nhắc. Bạn có thể cập nhật thủ công:

```powershell
# Windows
.\reference\scripts\update.ps1

# macOS/Linux
bash reference/scripts/update.sh
```

Script tự động: pull code mới → tải wheel `.whl` mới nhất → `pip install --upgrade`.

## 9. Tài liệu liên quan

- `README.md` — tổng quan plugin.
- `docs/sap-mcp-recommendations.md` — khuyến nghị MCP server bổ sung.
- `CONTRIBUTING.md` — đóng góp cho plugin.
- `CHANGELOG.md` — lịch sử thay đổi.
