# Rollout guide — nhiều user / team (công ty)

Hướng dẫn cho **team lead / Basis / champion** khi đưa SAP ABAP Agent tới N người.
Happy-path từng người: [`onboarding-guide.md`](onboarding-guide.md).  
Sự cố team: [`team-troubleshooting.md`](team-troubleshooting.md).

**Phiên bản tài liệu:** khớp plugin **1.23.1** (xem `.claude-plugin/plugin.json`).

---

## Mục tiêu “sản phẩm nội bộ”

Sau rollout, mỗi consultant/dev:

1. Có **Claude Code** + plugin + MCP Core trên máy riêng.
2. Kết nối đúng **tenant/profile** (secret không share file).
3. Notion: **default** dùng StormShynn shared “SAP Skills”
   (`9d54b58613ad485f8b8f19909adbb219`); công ty có thể override DB riêng.
4. Biết host: Claude = full; Cursor = MCP only.

---

## Mô hình triển khai (bắt buộc)

| Nguyên tắc | Chi tiết |
|------------|----------|
| **1 người = 1 OS account** | Vault: `%USERPROFILE%\.mcp-sap-connect` (DPAPI) / `~/.mcp-sap-connect`. Cùng login Windows = **cùng vault SAP**. |
| **Không copy thư mục profile giữa máy** | Mỗi máy `setup` / GUI Add riêng. |
| **Lab chung (escape hatch)** | `MCP_SAP_CONNECT_HOME` trỏ thư mục riêng / người — không khuyến nghị lâu dài. |
| **Claude Code = full stack** | Skills + hooks + agents. Cursor / VS Code = **chỉ MCP**. |
| **Notion default = StormShynn shared** | Id hardcode trong `notion_skills_db.py`; override bằng `set`/env nếu cần DB riêng. |

### Kịch bản nhanh

| Scenario | Làm gì |
|----------|--------|
| A — Nhiều máy, cùng tenant | Mỗi người setup + ping; export template không secret nếu cần thống nhất URL |
| B — VM lab nhiều user | Mỗi user Windows account riêng |
| C — Bắt buộc 1 OS user | `MCP_SAP_CONNECT_HOME` per person + kỷ luật tuyệt đối |
| D — Skill notes (mặc định) | OAuth Notion + Accept Share StormShynn DB — không cần `set` |
| E — Skill notes DB riêng cty | `notion_skills_db.py set <company-db-id>` trên mọi máy |

---

## Day-0 (team lead, 1 lần)

1. Chọn **edition** tenant (`s4hc_(public)` / BTP / …) — ghi vào wiki nội bộ.
2. Chuẩn bị **Communication Arrangement / user** đủ quyền ADT (không dùng chung 1 service key cho cả cty nếu policy cấm).
3. Notion: dùng **default StormShynn shared DB** (Share link cho seat mới). Chỉ tạo DB riêng
   nếu policy công ty yêu cầu kho skill nội bộ — rồi `set` id trên mọi máy.
4. Export template an toàn từ máy pilot (không secret):
   ```powershell
   python reference/scripts/team_profile_export.py <pilot-profile-id> -o team-s4-template.json
   ```
   Đưa `team-s4-template.json` vào wiki nội bộ (chỉ placeholder). Mẫu sẵn:
   `reference/templates/mcp-sap-connect-profile-sample/`.
5. Gửi link: onboarding-guide + rollout này + Notion invite.

---

## Checklist mỗi seat (≤ 20 phút)

### 0. Pre-flight

```powershell
cd path\to\sap-abap-agent   # hoặc clone / plugin path
python reference/scripts/validate_team_setup.py --persona A
```

`A` = ABAP Dev, `B` = Functional, `C` = Key user. Required phải PASS.

### 1. CLI + doctor

```powershell
pip install "mcp-sap-connect[win-dpapi]"
python -m mcp_sap_connect.doctor
```

### 2. GUI (Windows, tuỳ chọn)

NSIS từ [gui-latest](https://github.com/StormShynn/sap-abap-agent/releases/tag/gui-latest) /
tag `gui-v*` — current-user. SmartScreen: xem mục Authenticode bên dưới.

### 3. Profile SAP

- Từ template team: điền secret **local** → `mcp-sap-connect setup --from-file team-s4-template.json`
- Hoặc wizard: `mcp-sap-connect setup https://<tenant>...`
- Xác nhận: `mcp-sap-connect ping` rồi `connect`

### 4. Claude Code plugin

**Option A — script (ít typo):**

```powershell
powershell -ExecutionPolicy Bypass -File reference\scripts\claude_plugin_install.ps1
```

**Option B — tay trong Claude Code:**

```text
/plugin marketplace add StormShynn/sap-abap-agent
/plugin install sap-abap-agent
```

Restart session Claude Code.

### 5. MCP Core

```powershell
mcp-sap-connect mcp-setup
# hoặc GUI → MCP Servers → «Đăng ký MCP bắt buộc» / Cài Core
```

| Preset | Servers | Khi nào |
|--------|---------|---------|
| **Core (bắt buộc)** | `sap-btp`, `sap-dict-bridge`, `cds-kb`, `mcp-sap-docs-btp` | Mặc định mọi user — GUI nhắc khi thiếu |
| **Full / Research** | + `sap-vsp`, ADT alt, … | Chỉ khi lead bật — tốn slot stdio |

### 6. Notion (skill notes — mặc định shared)

1. Accept Share StormShynn “SAP Skills” trong browser (lead gửi link).
2. `/mcp` → OAuth Notion (tài khoản cá nhân).
3. Xác nhận default (không bắt buộc `set`):
   ```powershell
   python reference/scripts/notion_skills_db.py get --source
   # expect: 9d54b58613ad485f8b8f19909adbb219    default
   ```
4. (Tuỳ chọn) DB riêng công ty — xem [Company DB override](#company-db-override) bên dưới.

### 7. Cursor / VS Code seat (MCP only)

```powershell
python reference/scripts/emit_cursor_mcp_pack.py -o %USERPROFILE%\.cursor\mcp.json
```

Không cài plugin Claude — chỉ Core MCP. Xem `reference/templates/cursor-mcp-core/`.

### 8. Smoke

- `Liệt kê profile SAP của tôi`
- (Dev) tìm 1 class `Z*` / ping
- (Team Notion) hỏi topic đã có note — không tạo DB mới
- CDS: search 1 view qua `cds-kb` (xác nhận URL `kit-production`)

---

## Company DB override

Khi policy **không** cho phép dùng StormShynn shared DB:

1. Tạo Notion database **SAP Skills** (schema như `sap-daily-learner` mục 3b).
2. Share cho mọi seat (browser).
3. Trên **mỗi máy**:
   ```powershell
   python reference/scripts/notion_skills_db.py set "<company-db-id-or-url>"
   python reference/scripts/notion_skills_db.py get --source
   # expect: <id>    pin
   ```
4. Quay về shared StormShynn: `notion_skills_db.py clear`.
5. Pre-flight: `validate_team_setup.py` sẽ báo `(pin override)`.

---

## MCP: Core vs Full

GUI: **MCP Servers** → Preset. Inventory: `reference/scripts/mcp_inventory.json`.

Đổi active profile khi đã bật `sap-vsp` → chạy lại `mcp-setup` (CLI/GUI có cảnh báo).

---

## Windows SmartScreen / Authenticode

Installer GUI **có thể chưa ký Authenticode** (minisign updater vẫn tin cậy trong app).
Org muốn bỏ SmartScreen: xem [`org-authenticode-setup.md`](org-authenticode-setup.md)
(+ chi tiết CI: [`gui-native/.signing/README.md`](../gui-native/.signing/README.md)).

---

## Việc team lead theo dõi hàng tuần

- [ ] Mọi seat `validate_team_setup.py` READY (spot-check người mới)
- [ ] Notion: seat mới `get --source` = `default` (hoặc cùng pin company nếu override)
- [ ] **Promote loop:** trong Notion “SAP Skills”, lọc `Lan dung lai` cao / chưa `Da promote`
      → champion review → đề xuất đưa vào `reference/modules/` (hoặc skill local promote)
- [ ] Không ai commit `.mcp-sap-connect/` / secrets
- [ ] Plugin/wheel theo version wiki (badge README / Releases)
- [ ] Sự cố lặp → bổ sung [`team-troubleshooting.md`](team-troubleshooting.md)

---

## Ngoài phạm vi

- SSO/IdP org cho SAP (mỗi user auth riêng).
- Private Claude marketplace (fork + `marketplace add` URL nội bộ nếu cần).
- Rate-limit remote MCP (cds-kb, sap-docs).
- Port skills/hooks sang Cursor (quyết định: Claude-only).

---

## Liên kết

| Doc | Mục đích |
|-----|----------|
| [`onboarding-guide.md`](onboarding-guide.md) | Happy-path 3 persona + host matrix |
| [`team-troubleshooting.md`](team-troubleshooting.md) | FAQ đa user |
| [`org-authenticode-setup.md`](org-authenticode-setup.md) | Cert Windows cho GUI (org admin) |
| [`SECURITY.md`](../SECURITY.md) | Secret / không share vault |
| [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md) | MFA, vsp single-profile |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Đóng góp / org fork |
