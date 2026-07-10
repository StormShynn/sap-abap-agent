---
description: Thiet lap / quan ly ket noi SAP BTP (multi-profile)
argument-hint: "[setup|connect|reset|profiles|where] [URL|profileId]"
---

Huong dan nguoi dung cai dat va quan ly cac profile SAP BTP.

## Setup project moi (nhanh)

Neu moi them 1 project SAP (VD: https://project1.s4hana.cloud.sap), chi can 1 lenh:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Wizard se tu sinh profile id tu URL (vd: `project1.s4hana.cloud.sap`), hoi phuong thuc xac thuc (chon 1-4):

1. OAuth2 client_id + client_secret -- mac dinh/khuyen dung
2. Username/password
3. Bearer token (nhap tay)
4. Cookie-based -- session cookie SAP; lay cookie tu file, paste tay, hoac **auto** (tu mo browser dang nhap, can extra `playwright`)

Sau do hoi Region, service type.

Thong tin duoc luu rieng trong `%USERPROFILE%\.sap-btp-agent\profiles\<id>\` (Windows)
hoac `~/.sap-btp-agent/profiles/<id>/` (macOS/Linux):

- `config.json` -- URL, tenant, client_id, region, service, auth mode (KHONG nhay cam)
- `secrets.json` -- client_secret / token da duoc MA HOA (DPAPI tren Windows, AES-256-GCM cho he khac)

## Quan ly nhieu profile

```bash
sap-btp-agent profiles list          # liet ke tat ca profile
sap-btp-agent profiles use project1   # chon profile active
sap-btp-agent profiles show           # xem profile dang dung
sap-btp-agent profiles remove project1
```

## Chuyen profile nhanh qua env

Dat `SAP_BTP_PROFILE=project1.s4hana.cloud.sap` truoc khi goi `sap-btp-agent` de khoa profile do.

## Kiem tra ket noi

```bash
sap-btp-agent connect
sap-btp-agent connect project1.s4hana.cloud.sap
```

## Dang ky MCP server voi Claude Code

Dung lenh `claude mcp add` (Claude Code khong con dung file `mcp_servers.json`):

```bash
claude mcp add --transport stdio sap-btp -- sap-btp-agent
```

Sau khi cau hinh nhieu profile, Claude se co cac tool:

- `sap_list_profiles` -- liet ke profile
- `sap_ping { profile }` -- test 1 profile cu the
- `sap_list_packages`, `sap_search`, `sap_read_source`, `sap_syntax_check`, `sap_activate` -- deu co tham so `profile` (de trong = active)

## Loi thuong gap

- `401 Unauthorized`: client_secret sai hoac het han. Chay `sap-btp-agent setup <id>` de cap nhat.
- `404 /oauth/token`: URL token sai. Vao `profiles/<id>/secrets.json` sua `tokenUrl`, hoac sua file qua wizard.
- `Khong giai ma duoc secret`: Doi may / hostname. Chay lai setup.
- `'sap-btp-agent' is not recognized`: PATH thieu folder entry point. Chay `python -m sap_btp_agent.doctor`.
