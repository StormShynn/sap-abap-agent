---
name: sap-btp-setup
description: Ho tro setup & xu ly su co ket noi SAP BTP qua MCP (multi-profile). Dung khi user muon ket noi SAP BTP, hoi ve BTP/ADT/ABAP system, OAuth2, hoac gap loi authentication khi dung sap_* tool.
effort: medium
model: haiku
---

# SAP BTP Setup Helper (multi-profile)

## Them project SAP moi (nhanh nhat)

Khi user co URL moi (VD: `https://project1.s4hana.cloud.sap`), chi can chay:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Wizard tu sinh profile id tu hostname URL, hoi phuong thuc xac thuc, roi hoi cac thong tin tuong ung, luu rieng vao folder user.

### Phuong thuc xac thuc (wizard hoi luc setup, chon 1-4)

| # | Mode | Khi nao dung |
|---|------|-------------|
| 1 | OAuth2 (client_credentials) | Mac dinh/khuyen dung. Da co client_id + client_secret tu Communication Arrangement (BTP cockpit) |
| 2 | Password (username/password) | Co tai khoan SAP dang nhap truc tiep, khong tao OAuth2 client |
| 3 | Bearer token | Da co access token san (VD: lay tu tool/he thong khac) |
| 4 | Cookie-based | Da dang nhap SAP GUI/Fiori/SSO san, muon tai su dung session cookie (`MYSAPSSO2`, `SAP_SESSIONID`, `sap-usercontext`) thay vi xin OAuth2 client rieng. Ho tro tu dong re-auth qua browser popup (hoac Playwright) khi session het han (401) |

Neu user hoi "sao khong thay/goi y cookie-based" -- day la **option 4**, khong duoc goi y mac dinh vi OAuth2 (option 1) la lua chon khuyen dung, nhung wizard van in day du ca 4 option moi lan chay `setup`.

Chon option 4 xong, wizard hoi tiep **lay cookie tu dau** (chon 1-3):

| # | Cach lay cookie | Ghi chu |
|---|-----------------|---------|
| 1 | File cookie Netscape format | User da export cookie ra file san |
| 2 | Paste tay | User tu F12 -> Application -> Cookies -> copy, roi paste vao terminal |
| 3 | **Auto** (mac dinh) | Tu mo browser cho user dang nhap user/pass nhu binh thuong, tu dong trich cookie sau khi login -- khong can F12. Can extra `playwright`: `pip install -e ".[playwright]"` + `playwright install chromium`. Neu chua cai, tu fallback ve option 2 (paste tay) kem canh bao, khong crash. |

Neu user noi "muon mo web nhap user/pass tu lay cookie" -- chinh la **option 3** o buoc nay.

## MCP server

`sap-btp-agent` goi khong co argument se chay MCP stdio server (`sap_btp_agent/server.py`), serve dung
7 tool `sap_*` qua JSON-RPC cho Claude Code / Claude Desktop. Da test end-to-end (initialize -> tools/list ->
tools/call) truoc khi cong bo. Neu user hoi vi sao tool `sap_*` khong xuat hien / khong goi duoc trong Claude,
kiem tra theo thu tu: (1) da `claude mcp add` dung chua, (2) da co profile nao chua (`sap-btp-agent profiles list`),
(3) loi cu the tu `sap_ping` -- thuong la do secret/cookie sai hon la do transport.

## Cau hinh folder

```
%USERPROFILE%\.sap-btp-agent\   (Windows)
~/.sap-btp-agent/               (macOS/Linux)
+-- profiles.json                <- registry (danh sach + active)
+-- profiles/
|   +-- project1.s4hana.cloud.sap/
|   |   +-- config.json          <- URL, tenant, client_id, region, service
|   |   +-- secrets.json         <- client_secret / token (MA HOA)
|   +-- project2.s4hana.cloud.sap/
|       +-- config.json
|       +-- secrets.json
+-- log/
+-- cache/
```

- Tren Windows: secrets ma hoa bang DPAPI (gan voi user account Windows).
- Tren macOS/Linux: AES-256-GCM, key derive tu hostname + username.

## Quan ly profile

```bash
sap-btp-agent profiles list
sap-btp-agent profiles use project1.s4hana.cloud.sap
sap-btp-agent profiles show
sap-btp-agent profiles remove project1.s4hana.cloud.sap
```

## Env

- `SAP_BTP_PROFILE=project1` -- khoa profile cho 1 lan chay (uu tien registry)
- `SAP_BTP_AGENT_HOME=/path` -- doi folder cau hinh (test, multi-tenant)

## Tool MCP

Moi tool deu co tham so `profile` (de trong = active):

- `sap_list_profiles` -- liet ke profile
- `sap_ping { profile }`
- `sap_list_packages { profile, parent }`
- `sap_search { profile, query, objectType }`
- `sap_read_source { profile, objectUri, objectType }`
- `sap_syntax_check { profile, objectUri, objectType }`
- `sap_activate { profile, objectUri, objectType }`

## Xu ly su co

- `401 Unauthorized`: client_secret sai / het han. Chay `sap-btp-agent setup <profile-id>` de cap nhat.
- `404 /oauth/token`: URL token sai. Vao `profiles/<id>/secrets.json`, sua `tokenUrl` (vd: doi `/oauth/token` thanh `/oauth2/token` neu dung IAS).
- `Khong giai ma duoc secret`: Doi may / hostname. Chay lai `setup <profile-id>`.
- `'sap-btp-agent' is not recognized as an internal or external command` (Windows, rat hay gap): PATH khong
  co folder chua entry point (thuong do pip cai vao user-scheme scripts dir, VD `%APPDATA%\Python\PythonXY\Scripts`,
  khong tu dong nam trong PATH). Bao user chay `python -m sap_btp_agent.doctor` -- lenh nay chay duoc du
  PATH sai, tu phat hien va in san lenh PowerShell de fix. Khong tu doan/sua PATH thay user neu chua chay doctor.
- Muon xoa het: `sap-btp-agent reset`.
- Muon kiem tra toan bo moi truong (PATH, pywin32, playwright...): `sap-btp-agent doctor` (hoac
  `python -m sap_btp_agent.doctor` neu PATH chua dung).
