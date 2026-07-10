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

Wizard tu sinh profile id tu hostname URL, hoi cac thong tin can thiet, luu rieng vao folder user.

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
- Muon xoa het: `sap-btp-agent reset`.
