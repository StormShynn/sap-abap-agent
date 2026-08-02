# Rollout guide — nhiều user / team (công ty)

Hướng dẫn cho **team lead / Basis / champion** khi đưa SAP ABAP Agent tới N người.
Happy-path từng người: [`onboarding-guide.md`](onboarding-guide.md).  
Sự cố team: [`team-troubleshooting.md`](team-troubleshooting.md).

**Phiên bản tài liệu:** khớp plugin **1.22.8** (xem `.claude-plugin/plugin.json`).

---

## Mục tiêu “sản phẩm nội bộ”

Sau rollout, mỗi consultant/dev:

1. Có **Claude Code** + plugin + MCP Core trên máy riêng.
2. Kết nối đúng **tenant/profile** (secret không share file).
3. (Tuỳ team) Pin chung **Notion “SAP Skills”** — một DB, không tạo trùng.
4. Biết host: Claude = full; Cursor = MCP only.

---

## Mô hình triển khai (bắt buộc)

| Nguyên tắc | Chi tiết |
|------------|----------|
| **1 người = 1 OS account** | Vault: `%USERPROFILE%\.mcp-sap-connect` (DPAPI) / `~/.mcp-sap-connect`. Cùng login Windows = **cùng vault SAP**. |
| **Không copy thư mục profile giữa máy** | Mỗi máy `setup` / GUI Add riêng. |
| **Lab chung (escape hatch)** | `MCP_SAP_CONNECT_HOME` trỏ thư mục riêng / người — không khuyến nghị lâu dài. |
| **Claude Code = full stack** | Skills + hooks + agents. Cursor / VS Code = **chỉ MCP**. |
| **Notion team = pin DB** | `notion_skills_db.py set <id>` trên mọi máy sau khi Share. |

### Kịch bản nhanh

| Scenario | Làm gì |
|----------|--------|
| A — Nhiều máy, cùng tenant | Mỗi người setup + ping; export template không secret nếu cần thống nhất URL |
| B — VM lab nhiều user | Mỗi user Windows account riêng |
| C — Bắt buộc 1 OS user | `MCP_SAP_CONNECT_HOME` per person + kỷ luật tuyệt đối |
| D — Skill notes team | 1 Notion DB + Share + pin id trên mọi máy |

---

## Day-0 (team lead, 1 lần)

1. Chọn **edition** tenant (`s4hc_(public)` / BTP / …) — ghi vào wiki nội bộ.
2. Chuẩn bị **Communication Arrangement / user** đủ quyền ADT (không dùng chung 1 service key cho cả cty nếu policy cấm).
3. (Khuyến nghị) Tạo Notion database **SAP Skills**, Share cho team, lấy URL/id.
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

```text
/plugin marketplace add StormShynn/sap-abap-agent
/plugin install sap-abap-agent
```

Restart session Claude Code.

### 5. MCP Core

```powershell
mcp-sap-connect mcp-setup
# hoặc GUI → MCP Servers → Preset Core
```

| Preset | Servers | Khi nào |
|--------|---------|---------|
| **Core** | `sap-btp`, `sap-dict-bridge` (+ remote CDS/docs nếu cần) | Mặc định mọi user |
| **Full / Research** | + `sap-vsp`, ADT alt, … | Chỉ khi lead bật — tốn slot stdio |

### 6. Notion (nếu team dùng skill notes)

1. Accept Share trong browser.
2. `/mcp` → OAuth Notion (tài khoản cá nhân).
3. Pin:
   ```powershell
   python reference/scripts/notion_skills_db.py set "<database-id-or-url>"
   python reference/scripts/notion_skills_db.py get
   ```

### 7. Smoke

- `Liệt kê profile SAP của tôi`
- (Dev) tìm 1 class `Z*` / ping
- (Team Notion) hỏi topic đã có note — không tạo DB mới

---

## MCP: Core vs Full

GUI: **MCP Servers** → Preset. Inventory: `reference/scripts/mcp_inventory.json`.

Đổi active profile khi đã bật `sap-vsp` → chạy lại `mcp-setup` (CLI/GUI có cảnh báo).

---

## Windows SmartScreen / Authenticode

Installer GUI **có thể chưa ký Authenticode** (minisign updater vẫn tin cậy trong app).
Org muốn bỏ SmartScreen: cert OV/EV + GitHub secrets `WINDOWS_CERTIFICATE*` —
xem [`gui-native/.signing/README.md`](../gui-native/.signing/README.md).

---

## Việc team lead theo dõi hàng tuần

- [ ] Mọi seat `validate_team_setup.py` READY (spot-check người mới)
- [ ] Notion: một DB, không ai tạo “SAP Skills” rỗng song song (`notion_skills_db.py get` giống nhau)
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
| [`SECURITY.md`](../SECURITY.md) | Secret / không share vault |
| [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md) | MFA, vsp single-profile |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Đóng góp / org fork |
