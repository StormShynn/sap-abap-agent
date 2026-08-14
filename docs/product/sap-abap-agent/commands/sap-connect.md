---
description: Thiet lap / quan ly ket noi SAP BTP (multi-profile)
argument-hint: "[setup|connect|reset|profiles|where] [URL|profileId]"
---

Huong dan nguoi dung cai dat va quan ly cac profile SAP BTP.

## Setup project moi (nhanh)

Neu moi them 1 project SAP (VD: https://project1.s4hana.cloud.sap), chi can 1 lenh:

```bash
mcp-sap-connect setup https://project1.s4hana.cloud.sap
```

Wizard se tu sinh profile id tu URL (vd: `project1.s4hana.cloud.sap`), hoi phuong thuc xac thuc (chon 1-4):

1. OAuth2 client_id + client_secret -- mac dinh/khuyen dung
2. Username/password
3. Bearer token (nhap tay)
4. Cookie-based -- session cookie SAP; uu tien **SAML fast-path** (nhap user/pass, ~1-3s qua HTTP
   truc tiep, KHONG mo browser, khong dung duoc neu IAS co MFA), fallback **auto** (mo browser, ho
   tro ca MFA) neu SAML that bai hoac ban tu chon, hoac lay tu file/paste tay

Sau do hoi Region, service type (`s4hc_(private)` / `s4hc_(public)` / `btp` / `onprem`).

Thong tin duoc luu rieng trong `%USERPROFILE%\.mcp-sap-connect\profiles\<id>\` (Windows)
hoac `~/.mcp-sap-connect/profiles/<id>/` (macOS/Linux):

- `config.json` -- URL, tenant, client_id, region, service, auth mode (KHONG nhay cam)
- `secrets.json` -- client_secret / token da duoc MA HOA (DPAPI tren Windows, AES-256-GCM cho he khac)

## Quan ly nhieu profile

```bash
mcp-sap-connect profiles list          # liet ke tat ca profile
mcp-sap-connect profiles use project1   # chon profile active
mcp-sap-connect profiles show           # xem profile dang dung
mcp-sap-connect profiles remove project1
```

## Chuyen profile nhanh qua env

Dat `SAP_BTP_PROFILE=project1.s4hana.cloud.sap` truoc khi goi `mcp-sap-connect` de khoa profile do.

## Kiem tra ket noi

```bash
mcp-sap-connect connect
mcp-sap-connect connect project1.s4hana.cloud.sap
```

## Dang ky MCP servers voi Claude Code (1 lan duy nhat)

Sau khi setup profile, chay lenh nay de dang ky TOAN BO MCP servers:
```bash
mcp-sap-connect mcp-setup
```
Hoac setup wizard se tu hoi khi ban tao profile moi.

Cac server duoc dang ky tu dong (bat buoc):
- `sap-connect` — ket noi chinh den SAP BTP
- `sap-dict-bridge` — tao Domain/DataElement/Table
- `cds-kb` — tra cuu 7,355 CDS views
- `mcp-sap-docs-btp` — tra cuu SAP Help / API Hub

Cac server ADT alternative (tuy chon, can Node.js):
- `arc-1`, `mcp-abap-adt` — se hoi ban truoc khi dang ky

Cac server product-specific (can cai dat thu cong):
- `sap-notes`, `sap-gui`, `sf-mcp`, `sf-cdata`, `sap-concur`, `sap-fieldglass`

Sau khi cau hinh nhieu profile, Claude se co cac tool:

- `sap_list_profiles` -- liet ke profile
- `sap_ping { profile }` -- test 1 profile cu the
- `sap_list_packages`, `sap_search`, `sap_read_source`, `sap_syntax_check`, `sap_activate` -- deu co tham so `profile` (de trong = active)

**`profile` KHONG bat buoc la profileId chinh xac.** Neu user noi trong cau hoi tu nhien mot
URL, hostname/tenant subdomain, hoac tenant (Communication Arrangement) - Claude co the dua
nguyen gia tri do vao `profile`, KHONG can tu tra `sap_list_profiles` truoc de doi ra profileId
noi bo. Vi du user noi "connect toi project1.s4hana.cloud.sap" hoac "dung tenant abc-xyz" deu
duoc, khong can biet profileId thuc su la gi. Neu gia tri khong khop profile nao, hoac khop
nhieu profile cung luc (2 profile trung ten tenant chang han), tool se tra ve loi ro liet ke cac
profile hien co - **Claude PHAI hoi lai user de chon dung**, KHONG duoc tu doan/fallback ve
profile active (co the la 1 he thong SAP khac hoan toan voi cai user dinh noi toi).

## Loi thuong gap

- `401 Unauthorized`: client_secret sai hoac het han. Chay `mcp-sap-connect setup <id>` de cap nhat.
- `404 /oauth/token`: URL token sai. Vao `profiles/<id>/secrets.json` sua `tokenUrl`, hoac sua file qua wizard.
- `Khong giai ma duoc secret`: Doi may / hostname. Chay lai setup.
- `'mcp-sap-connect' is not recognized`: PATH thieu folder entry point. Chay `python -m mcp_sap_connect.doctor`.
