# Team troubleshooting — SAP ABAP Agent

FAQ khi **nhiều người** dùng chung plugin / cùng tenant. Lỗi 1 máy: bảng
[Lỗi thường gặp](onboarding-guide.md#lỗi-thường-gặp) trong onboarding.

---

## Notion — đồng nghiệp không thấy skill của tôi

| Nguyên nhân | Cách xử |
|-------------|---------|
| Chưa invite vào database | Owner: Notion Share → email đồng nghiệp; họ Accept trong browser |
| Chưa OAuth Notion trên máy họ | `/mcp` → `notion` → đăng nhập **tài khoản của họ** |
| DB id (default) | Plugin đã hardcode StormShynn shared — `notion_skills_db.py get --source` phải ra `default` (không bắt buộc `set`) |
| Muốn DB riêng công ty | `notion_skills_db.py set "<company-id-or-url>"` trên mọi máy; xem rollout “Company DB override” |
| Agent tạo DB “SAP Skills” rỗng | Dừng; `clear` nếu pin nhầm; dùng default hoặc pin đúng — **không** tạo trùng |

Chi tiết: `skills/sap-daily-learner/SKILL.md` mục 3b + README Notion.

---

## Profile / secret

| Hiện tượng | Cách xử |
|------------|---------|
| Đổi máy → không giải mã secret | Bình thường (DPAPI/keychain theo user+host). Setup lại; **không** copy `secrets.json` |
| Nhiều người cùng Windows login | Vault chung — **cấm** cho production team. Mỗi người 1 OS account hoặc `MCP_SAP_CONNECT_HOME` riêng |
| Muốn chia config không lộ secret | `python reference/scripts/team_profile_export.py <id> -o template.json` rồi gửi template; mỗi người `setup --from-file` |

---

## sap-vsp “hỏng” sau khi đổi profile

`sap-vsp` chỉ nhận credential lúc `mcp-setup`. Đổi active profile → CLI/GUI cảnh báo → chạy lại:

```powershell
mcp-sap-connect mcp-setup
# hoặc đăng ký lại sap-vsp trong GUI MCP Servers
```

Chỉ password auth mới auto-điền `SAP_ADT_USER`/`PASSWORD`. Cookie/OAuth: xem `KNOWN_LIMITATIONS.md`.

---

## Cursor user kỳ vọng skill/hooks Claude

Không có. Cursor = MCP only. Full routing/verification = Claude Code. Xem host matrix trong
`onboarding-guide.md`.

---

## MCP remote chậm / lỗi (cds-kb, sap-docs)

- Rate-limit / downtime nhà cung cấp SSE — thử lại; không phải vault local.
- Windows + supergateway: thử `supergateway.cmd` hoặc đường dẫn tuyệt đối (README).

---

## SmartScreen chặn GUI installer

Installer có thể chưa Authenticode (minisign updater vẫn OK trong app). Org: cert OV/EV +
secrets `WINDOWS_CERTIFICATE*` — `gui-native/.signing/README.md`. User: “More info → Run anyway”
nếu tin nguồn Release GitHub org.

---

## Pre-flight trước khi gọi support

```powershell
python reference/scripts/validate_team_setup.py --persona A
```

PASS required → gửi output + `mcp-sap-connect doctor` + persona khi mở issue nội bộ.
