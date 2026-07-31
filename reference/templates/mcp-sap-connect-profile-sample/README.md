# Profile mau — tao profile SAP khong can tra loi wizard tung buoc

Copy 1 trong 4 file `.json` trong thu muc nay (theo dung phuong thuc xac thuc ban co), dien cac
gia tri `<...>`, roi chay:

```bash
mcp-sap-connect setup --from-file duong-dan-file-cua-ban.json
```

Lenh nay goi **dung logic luu tru/ma hoa** ma wizard tuong tac (`mcp-sap-connect setup <url>`)
dung — chi khac o cho khong hoi tung cau trong terminal. Field nao con placeholder (`<...>`,
`YOUR_...`) se bi tu choi voi thong bao ro rang, khong bao gio tao profile voi gia tri gia.

## Chon dung file mau theo phuong thuc xac thuc

| File | Phuong thuc | Dung khi |
|---|---|---|
| `profile.oauth2.json` | OAuth2 client_credentials | **Khuyen dung** — da co Communication Arrangement tren BTP Cockpit (client_id + client_secret) |
| `profile.password.json` | Username/Password | Co tai khoan SAP dang nhap truc tiep, chua tao OAuth2 client |
| `profile.bearer.json` | Bearer token | Da co access token san (vd tu he thong khac cap) |
| `profile.cookie.json` | Cookie-based | Da dang nhap SAP GUI/Fiori/SSO qua browser, muon tai dung session cookie |

## Field dung chung ca 4 file

| Field | Bat buoc | Mo ta |
|---|---|---|
| `profileId` | Khong | Ten profile. De trong -> tu sinh tu hostname cua `url` (vd `https://my123456.s4hana.cloud.sap` -> `my123456.s4hana.cloud.sap`) |
| `url` | **Co** | URL day du he thong SAP, co `https://` |
| `service` | Khong (mac dinh `s4hc_(public)`) | 1 trong 5 edition — xem bang duoi |
| `region` | Khong (mac dinh `eu10`) | Region SAP BTP (vd `eu10`, `us10`, `ap10`) |
| `tenant` | Khong | De trong = tu lay tu URL |
| `authMode` | **Co** | Phai khop dung ten file mau (`oauth2`/`password`/`bearer`/`cookie`) |

## 5 edition (`service`) — vi du gia tri

| `service` | Mo ta | Vi du URL |
|---|---|---|
| `s4hc_(public)` | S/4HANA Cloud Public Edition (multi-tenant SaaS) — **mac dinh** | `https://my123456.s4hana.cloud.sap` |
| `s4hc_(private)` | S/4HANA Cloud Private Edition (single-tenant, SAP-managed) | `https://vhcalXXXci.s4hana.ondemand.com` |
| `btp` | SAP BTP ABAP Environment (Steampunk) — runtime rieng tren CF/Kyma | `https://abap-xxxxx.abap.eu10.hana.ondemand.com` |
| `onprem` | On-premise (customer tu quan ly ha tang) | `https://s4hana.internal.company.com:44300` |
| `rise_with_sap` | RISE with SAP (SAP quan ly tren ha tang khach hang) | Tuy hop dong RISE, hoi tech lead du an |

Khong chac edition nao? Xem skill `reference/process/sap-service-type-context.md` hoac hoi
Basis/tech lead du an — chon sai edition co the lam cau tra loi cua Claude sai ngu canh (vd
gia dinh nham SELECT truc tiep bang chuan duoc phep hay khong).

## Vi du cu the theo tung auth mode

### OAuth2 (`profile.oauth2.json`)

```json
{
  "profileId": "myproject",
  "url": "https://my123456.s4hana.cloud.sap",
  "service": "s4hc_(public)",
  "region": "eu10",
  "authMode": "oauth2",
  "clientId": "sb-abcd1234-efgh-5678!b12345",
  "clientSecret": "aBcDeFgH1234567890==",
  "scope": "",
  "tenant": ""
}
```

`clientId`/`clientSecret` lay tu **SAP BTP Cockpit → Communication Management → Communication
Arrangements** (tao scenario phu hop, vd `SAP_COM_0659` cho ADT) hoac **Communication System +
Communication User**.

### Cookie-based (`profile.cookie.json`)

```json
{
  "profileId": "myproject",
  "url": "https://my123456.s4hana.cloud.sap",
  "service": "s4hc_(public)",
  "region": "eu10",
  "authMode": "cookie",
  "reauthMode": "manual",
  "cookies": {
    "MYSAPSSO2": "AbCd...(chuoi rat dai)...",
    "SAP_SESSIONID_ABC_100": "1234567890abcdef",
    "sap-usercontext": "sap-client=100"
  },
  "tenant": ""
}
```

Lay cookie: dang nhap he thong SAP tren browser -> F12 -> tab **Application** (Chrome/Edge) hoac
**Storage** (Firefox) -> **Cookies** -> copy tung cap ten/gia tri. Ten cookie thuong gap:
`MYSAPSSO2`, `SAP_SESSIONID_<SID>_<CLIENT>`, `sap-usercontext`.

## Sau khi chay `--from-file` thanh cong

```bash
mcp-sap-connect connect              # kiem tra ket noi
mcp-sap-connect profiles list        # xem lai profile vua tao
mcp-sap-connect mcp-setup            # dang ky MCP servers voi Claude Code (neu chua lam)
```

## Loi thuong gap

| Loi | Nguyen nhan | Xu ly |
|---|---|---|
| `❌ File thieu field 'url' hop le` | Con placeholder `<...>` hoac de trong | Dien URL that, co `https://` |
| `❌ Thieu hoac chua thay placeholder cho 'clientId'/'clientSecret'` | Chua dien hoac dien nham field khac auth mode dang chon | Kiem tra dung file mau khop `authMode` |
| `401 Unauthorized` sau khi `connect` | Credential sai/het han | Sua lai file, chay lai `--from-file` (ghi de an toan cung profile id), hoac `mcp-sap-connect setup <id>` de sua tay |
| `404 /oauth/token` | Sai token URL (thuong IAS dung `/oauth2/token`) | Kiem tra lai Communication Arrangement tren BTP Cockpit |

Xem chi tiet toan bo wizard tuong tac (neu muon tra loi tung buoc thay vi dung file) tai
`commands/sap-connect.md`.
